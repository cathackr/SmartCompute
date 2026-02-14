"""
Shared test fixtures for SmartCompute.

Provides:
- RSA keypair for license testing
- Temporary license directory
- Helper to generate test license tokens
"""

from __future__ import annotations

import base64
import json
import os
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Generator
from unittest.mock import patch
import uuid

import pytest


# ── RSA keypair fixture (only if cryptography is installed) ─────


@pytest.fixture(scope="session")
def rsa_keypair():
    """Generate a 2048-bit RSA keypair for the entire test session."""
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    priv_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()

    pub_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()

    return priv_pem, pub_pem


@pytest.fixture
def license_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Provide a temporary license directory and patch LICENSE_FILE."""
    lic_dir = tmp_path / ".smartcompute"
    lic_dir.mkdir()
    lic_file = lic_dir / "license.json"

    with patch("smartcompute.licensing.validator.LICENSE_DIR", lic_dir), \
         patch("smartcompute.licensing.validator.LICENSE_FILE", lic_file):
        yield lic_dir


def _make_token(
    priv_pem: str,
    tier: str = "enterprise",
    email: str = "test@example.com",
    org: str = "TestCorp",
    days: int = 365,
    hardware_id: str = "",
    features: list[str] | None = None,
    extra_payload: dict | None = None,
) -> str:
    """Create a signed license token for tests."""
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding

    private_key = serialization.load_pem_private_key(priv_pem.encode(), password=None)

    now = datetime.now(timezone.utc)
    payload = {
        "license_id": str(uuid.uuid4()),
        "tier": tier,
        "email": email,
        "org": org,
        "issued_at": now.isoformat(),
        "expires_at": (now + timedelta(days=days)).isoformat(),
        "max_nodes": 1,
        "hardware_id": hardware_id,
        "features": features or [],
    }
    if extra_payload:
        payload.update(extra_payload)

    payload_bytes = json.dumps(payload, separators=(",", ":")).encode()
    payload_b64 = base64.urlsafe_b64encode(payload_bytes).rstrip(b"=").decode()

    signature = private_key.sign(
        payload_bytes,
        padding.PKCS1v15(),
        hashes.SHA256(),
    )
    sig_b64 = base64.urlsafe_b64encode(signature).rstrip(b"=").decode()

    return f"{payload_b64}.{sig_b64}"


@pytest.fixture
def make_token(rsa_keypair):
    """Factory fixture: call ``make_token(tier="enterprise", ...)``."""
    priv_pem, _ = rsa_keypair

    def _factory(**kwargs):
        return _make_token(priv_pem, **kwargs)

    return _factory
