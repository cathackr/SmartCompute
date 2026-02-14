"""
Tests for the SmartCompute licensing system.

Covers: token generation, validation, expiration, invalid signatures,
hardware binding, tier hierarchy, decorators, and persistence.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

from smartcompute.licensing.validator import LicenseValidator, LicenseInfo, TIER_HIERARCHY
from smartcompute.licensing.decorators import requires_tier, TierRequiredError
from smartcompute.licensing.hardware_id import get_hardware_id


# ── Hardware ID ─────────────────────────────────────────────────


class TestHardwareId:
    def test_returns_hex_string(self):
        hw_id = get_hardware_id()
        assert isinstance(hw_id, str)
        assert len(hw_id) == 64  # SHA-256 hex digest

    def test_is_deterministic(self):
        assert get_hardware_id() == get_hardware_id()


# ── LicenseInfo ─────────────────────────────────────────────────


class TestLicenseInfo:
    def test_tier_level_starter(self):
        info = LicenseInfo(
            license_id="x", tier="starter", email="", org="",
            issued_at="", expires_at="2099-01-01",
        )
        assert info.tier_level == 0

    def test_tier_level_enterprise(self):
        info = LicenseInfo(
            license_id="x", tier="enterprise", email="", org="",
            issued_at="", expires_at="2099-01-01",
        )
        assert info.tier_level == 1

    def test_tier_level_industrial(self):
        info = LicenseInfo(
            license_id="x", tier="industrial", email="", org="",
            issued_at="", expires_at="2099-01-01",
        )
        assert info.tier_level == 2

    def test_is_expired_future(self):
        info = LicenseInfo(
            license_id="x", tier="starter", email="", org="",
            issued_at="", expires_at="2099-12-31T23:59:59",
        )
        assert not info.is_expired

    def test_is_expired_past(self):
        info = LicenseInfo(
            license_id="x", tier="starter", email="", org="",
            issued_at="", expires_at="2020-01-01T00:00:00",
        )
        assert info.is_expired


# ── Token validation ────────────────────────────────────────────


class TestLicenseValidator:
    def test_valid_enterprise_token(self, rsa_keypair, make_token, license_dir):
        _, pub_pem = rsa_keypair
        token = make_token(tier="enterprise", org="Acme")
        validator = LicenseValidator(public_key_pem=pub_pem)
        info = validator.validate_token(token)

        assert info.valid is True
        assert info.tier == "enterprise"
        assert info.org == "Acme"
        assert info.error is None

    def test_valid_industrial_token(self, rsa_keypair, make_token, license_dir):
        _, pub_pem = rsa_keypair
        token = make_token(tier="industrial")
        validator = LicenseValidator(public_key_pem=pub_pem)
        info = validator.validate_token(token)

        assert info.valid is True
        assert info.tier == "industrial"

    def test_invalid_format(self, rsa_keypair, license_dir):
        _, pub_pem = rsa_keypair
        validator = LicenseValidator(public_key_pem=pub_pem)
        info = validator.validate_token("not-a-valid-token")

        assert info.valid is False
        assert "format" in info.error.lower()

    def test_tampered_payload(self, rsa_keypair, make_token, license_dir):
        """Modifying the payload should fail signature verification."""
        import base64
        _, pub_pem = rsa_keypair
        token = make_token(tier="enterprise")
        payload_b64, sig_b64 = token.split(".", 1)

        # Decode, modify, re-encode
        payload_bytes = base64.urlsafe_b64decode(payload_b64 + "==")
        payload = json.loads(payload_bytes)
        payload["tier"] = "industrial"  # tamper!
        tampered = base64.urlsafe_b64encode(
            json.dumps(payload, separators=(",", ":")).encode()
        ).rstrip(b"=").decode()

        validator = LicenseValidator(public_key_pem=pub_pem)
        info = validator.validate_token(f"{tampered}.{sig_b64}")

        assert info.valid is False
        assert "signature" in info.error.lower() or "verification" in info.error.lower()

    def test_expired_token(self, rsa_keypair, make_token, license_dir):
        _, pub_pem = rsa_keypair
        token = make_token(days=-1)  # already expired
        validator = LicenseValidator(public_key_pem=pub_pem)
        info = validator.validate_token(token)

        assert info.valid is False
        assert "expired" in info.error.lower()

    def test_hardware_binding_matches(self, rsa_keypair, make_token, license_dir):
        _, pub_pem = rsa_keypair
        hw_id = get_hardware_id()
        token = make_token(hardware_id=hw_id)
        validator = LicenseValidator(public_key_pem=pub_pem)
        info = validator.validate_token(token)

        assert info.valid is True

    def test_hardware_binding_mismatch(self, rsa_keypair, make_token, license_dir):
        _, pub_pem = rsa_keypair
        token = make_token(hardware_id="wrong_hardware_id_abc123")
        validator = LicenseValidator(public_key_pem=pub_pem)
        info = validator.validate_token(token)

        assert info.valid is False
        assert "machine" in info.error.lower()

    def test_activate_persists(self, rsa_keypair, make_token, license_dir):
        _, pub_pem = rsa_keypair
        token = make_token(tier="enterprise", org="PersistCorp")
        validator = LicenseValidator(public_key_pem=pub_pem)
        info = validator.activate(token)

        assert info.valid is True

        # Now read it back with a fresh validator
        validator2 = LicenseValidator(public_key_pem=pub_pem)
        current = validator2.get_current_license()
        assert current.valid is True
        assert current.tier == "enterprise"
        assert current.org == "PersistCorp"

    def test_fallback_to_starter(self, rsa_keypair, license_dir):
        _, pub_pem = rsa_keypair
        validator = LicenseValidator(public_key_pem=pub_pem)
        info = validator.get_current_license()

        assert info.valid is True
        assert info.tier == "starter"

    def test_has_tier_hierarchy(self, rsa_keypair, make_token, license_dir):
        _, pub_pem = rsa_keypair
        token = make_token(tier="industrial")
        validator = LicenseValidator(public_key_pem=pub_pem)
        validator.validate_token(token)

        assert validator.has_tier("starter") is True
        assert validator.has_tier("enterprise") is True
        assert validator.has_tier("industrial") is True

    def test_enterprise_cannot_access_industrial(self, rsa_keypair, make_token, license_dir):
        _, pub_pem = rsa_keypair
        token = make_token(tier="enterprise")
        validator = LicenseValidator(public_key_pem=pub_pem)
        validator.validate_token(token)

        assert validator.has_tier("starter") is True
        assert validator.has_tier("enterprise") is True
        assert validator.has_tier("industrial") is False


# ── Decorators ──────────────────────────────────────────────────


class TestRequiresTier:
    def test_decorator_allows_matching_tier(self, rsa_keypair, make_token, license_dir):
        _, pub_pem = rsa_keypair
        token = make_token(tier="enterprise")

        # Patch the module-level validator
        from smartcompute.licensing import decorators
        validator = LicenseValidator(public_key_pem=pub_pem)
        validator.validate_token(token)

        with patch.object(decorators, "_validator", validator):
            @requires_tier("enterprise")
            def my_func():
                return "ok"

            assert my_func() == "ok"

    def test_decorator_blocks_lower_tier(self, rsa_keypair, license_dir):
        _, pub_pem = rsa_keypair
        from smartcompute.licensing import decorators
        validator = LicenseValidator(public_key_pem=pub_pem)
        # No token loaded → starter

        with patch.object(decorators, "_validator", validator):
            @requires_tier("enterprise")
            def my_func():
                return "ok"

            with pytest.raises(TierRequiredError) as exc_info:
                my_func()

            assert "enterprise" in str(exc_info.value)
            assert "starter" in str(exc_info.value)

    def test_decorator_preserves_function_name(self):
        @requires_tier("enterprise")
        def important_function():
            """Important docstring."""
            pass

        assert important_function.__name__ == "important_function"
        assert important_function.__doc__ == "Important docstring."
        assert important_function._required_tier == "enterprise"

    def test_invalid_tier_raises_value_error(self):
        with pytest.raises(ValueError, match="Unknown tier"):
            @requires_tier("nonexistent")
            def bad_func():
                pass


# ── Tier hierarchy constant ─────────────────────────────────────


class TestTierHierarchy:
    def test_order(self):
        assert TIER_HIERARCHY == ["starter", "enterprise", "industrial"]

    def test_starter_is_lowest(self):
        assert TIER_HIERARCHY.index("starter") == 0

    def test_industrial_is_highest(self):
        assert TIER_HIERARCHY.index("industrial") == 2
