"""
Offline RSA-based license validator.

License token format::

    base64(json_payload).base64(rsa_signature)

The public key is embedded here so validation works without any
network calls.  The private key lives in ``tools/admin/`` and is
never distributed.
"""

from __future__ import annotations

import base64
import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

# Tier hierarchy (higher index = more features)
TIER_HIERARCHY = ["starter", "enterprise", "industrial"]

# Default license directory
LICENSE_DIR = Path.home() / ".smartcompute"
LICENSE_FILE = LICENSE_DIR / "license.json"

# ── Embedded RSA public key (PEM) ──────────────────────────────
# Replace with YOUR production public key before shipping.
# Generate a keypair with:
#   python -m smartcompute.licensing.keys generate-keypair
_PUBLIC_KEY_PEM = """\
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0Z3VS5JJcds3xfn/ygWe
PLACEHOLDER_REPLACE_WITH_REAL_KEY_BEFORE_RELEASE
-----END PUBLIC KEY-----
"""


@dataclass
class LicenseInfo:
    """Parsed and validated license payload."""

    license_id: str
    tier: str
    email: str
    org: str
    issued_at: str
    expires_at: str
    max_nodes: int = 1
    hardware_id: str = ""
    features: List[str] = field(default_factory=list)

    # Set after validation
    valid: bool = False
    error: Optional[str] = None

    @property
    def is_expired(self) -> bool:
        try:
            exp = datetime.fromisoformat(self.expires_at)
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            return datetime.now(timezone.utc) > exp
        except (ValueError, TypeError):
            return True

    @property
    def tier_level(self) -> int:
        """Numeric tier level (0=starter, 1=enterprise, 2=industrial)."""
        try:
            return TIER_HIERARCHY.index(self.tier.lower())
        except ValueError:
            return 0


class LicenseValidator:
    """Validates SmartCompute license tokens offline using RSA signatures."""

    def __init__(self, public_key_pem: Optional[str] = None):
        self._public_key_pem = public_key_pem or _PUBLIC_KEY_PEM
        self._cached_license: Optional[LicenseInfo] = None

    # ── Public API ──────────────────────────────────────────────

    def validate_token(self, token: str) -> LicenseInfo:
        """Validate a ``payload.signature`` token and return license info.

        Parameters
        ----------
        token : str
            The full license token (``base64(payload).base64(sig)``).

        Returns
        -------
        LicenseInfo
            Always returns an object; check ``.valid`` and ``.error``.
        """
        try:
            payload_b64, sig_b64 = token.strip().split(".", 1)
        except ValueError:
            return self._invalid("Invalid token format (expected payload.signature)")

        try:
            payload_bytes = base64.urlsafe_b64decode(payload_b64 + "==")
            payload = json.loads(payload_bytes)
        except Exception:
            return self._invalid("Cannot decode token payload")

        # Build LicenseInfo from payload
        info = LicenseInfo(
            license_id=payload.get("license_id", ""),
            tier=payload.get("tier", "starter"),
            email=payload.get("email", ""),
            org=payload.get("org", ""),
            issued_at=payload.get("issued_at", ""),
            expires_at=payload.get("expires_at", ""),
            max_nodes=payload.get("max_nodes", 1),
            hardware_id=payload.get("hardware_id", ""),
            features=payload.get("features", []),
        )

        # Verify RSA signature
        try:
            sig_bytes = base64.urlsafe_b64decode(sig_b64 + "==")
            self._verify_signature(payload_bytes, sig_bytes)
        except ImportError:
            info.error = "cryptography package required for license validation"
            return info
        except Exception as exc:
            info.error = f"Signature verification failed: {exc}"
            return info

        # Check expiration
        if info.is_expired:
            info.error = "License has expired"
            return info

        # Check hardware binding (if set)
        if info.hardware_id:
            from smartcompute.licensing.hardware_id import get_hardware_id

            if info.hardware_id != get_hardware_id():
                info.error = "License is bound to a different machine"
                return info

        info.valid = True
        self._cached_license = info
        return info

    def activate(self, token: str) -> LicenseInfo:
        """Validate *token* and persist it to ``~/.smartcompute/license.json``."""
        info = self.validate_token(token)
        if not info.valid:
            return info

        LICENSE_DIR.mkdir(parents=True, exist_ok=True)
        LICENSE_FILE.write_text(json.dumps({"token": token}, indent=2))
        logger.info("License activated for %s (%s tier)", info.org, info.tier)
        return info

    def get_current_license(self) -> LicenseInfo:
        """Load and validate the persisted license, falling back to Starter."""
        if self._cached_license and self._cached_license.valid:
            return self._cached_license

        if LICENSE_FILE.exists():
            try:
                data = json.loads(LICENSE_FILE.read_text())
                token = data.get("token", "")
                if token:
                    info = self.validate_token(token)
                    if info.valid:
                        return info
                    logger.warning("Stored license invalid: %s", info.error)
            except Exception as exc:
                logger.warning("Cannot read license file: %s", exc)

        # Fall back to Starter (free tier)
        return LicenseInfo(
            license_id="starter-free",
            tier="starter",
            email="",
            org="",
            issued_at="",
            expires_at="2099-12-31T23:59:59",
            valid=True,
        )

    def get_current_tier(self) -> str:
        """Shortcut: return the validated tier name."""
        return self.get_current_license().tier.lower()

    def has_tier(self, required_tier: str) -> bool:
        """Check whether the active license meets *required_tier*."""
        current = self.get_current_license()
        if not current.valid:
            return False
        try:
            required_level = TIER_HIERARCHY.index(required_tier.lower())
        except ValueError:
            return False
        return current.tier_level >= required_level

    # ── Internals ───────────────────────────────────────────────

    def _verify_signature(self, payload_bytes: bytes, sig_bytes: bytes) -> None:
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding

        public_key = serialization.load_pem_public_key(
            self._public_key_pem.encode()
        )
        public_key.verify(
            sig_bytes,
            payload_bytes,
            padding.PKCS1v15(),
            hashes.SHA256(),
        )

    @staticmethod
    def _invalid(error: str) -> LicenseInfo:
        return LicenseInfo(
            license_id="",
            tier="starter",
            email="",
            org="",
            issued_at="",
            expires_at="",
            error=error,
        )
