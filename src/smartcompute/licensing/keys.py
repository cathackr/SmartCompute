"""
RSA keypair generation helper.

This module is shipped inside the package but the admin tool
(``tools/admin/license_generator.py``) is the one that actually
calls it.  End-users never need this.

Usage::

    python -m smartcompute.licensing.keys generate-keypair

Writes ``private_key.pem`` and ``public_key.pem`` to the current
directory.  Keep private_key.pem **secret**.
"""

from __future__ import annotations

import sys


def generate_keypair(out_dir: str = ".") -> tuple[str, str]:
    """Generate a 2048-bit RSA keypair and write PEM files.

    Returns (private_path, public_path).
    """
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    priv_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    pub_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    from pathlib import Path

    out = Path(out_dir)
    priv_path = out / "private_key.pem"
    pub_path = out / "public_key.pem"
    priv_path.write_bytes(priv_pem)
    pub_path.write_bytes(pub_pem)

    return str(priv_path), str(pub_path)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "generate-keypair":
        priv, pub = generate_keypair()
        print(f"Private key: {priv}")
        print(f"Public key:  {pub}")
        print("IMPORTANT: Keep private_key.pem SECRET. Never commit it.")
    else:
        print("Usage: python -m smartcompute.licensing.keys generate-keypair")
        sys.exit(1)
