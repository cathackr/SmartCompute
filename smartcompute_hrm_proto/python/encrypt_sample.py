#!/usr/bin/env python3
# encrypt_sample.py
# Genera un sample JSON y lo cifra con envelope encryption (AES-GCM + RSA public key)
import os, json, base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import secrets
import sys

PUBKEY_PATH = os.path.join(os.path.dirname(__file__), "..", "keys", "public_key.pem")
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "sample", "scan_sample.json.enc")

sample = {
    "scan_id": "scan123",
    "timestamp": "2025-09-15T10:23:00Z",
    "findings": [
        {
            "severity": "CRITICAL",
            "event_id": 8,
            "description": "CreateRemoteThread observed targeting chrome.exe",
            "process_path": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "raw_payload": "CreateRemoteThread to process pid=456 using CreateRemoteThread..."
        }
    ],
    "source_meta": {
        "host": "admin-workstation-1.local",
        "ip": "192.168.100.55",
        "user": "admin@example.com"
    }
}

def load_pubkey(p):
    with open(p, "rb") as f:
        return serialization.load_pem_public_key(f.read())

def envelope_encrypt(plaintext_bytes, pubkey):
    # generate random data key
    data_key = secrets.token_bytes(32)  # AES-256
    aesgcm = AESGCM(data_key)
    nonce = secrets.token_bytes(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext_bytes, None)
    # encrypt data_key with RSA public key (OAEP)
    enc_data_key = pubkey.encrypt(
        data_key,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )
    return {
        "enc_key_b64": base64.b64encode(enc_data_key).decode(),
        "nonce_b64": base64.b64encode(nonce).decode(),
        "ciphertext_b64": base64.b64encode(ciphertext).decode()
    }

def main():
    pubkey = load_pubkey(PUBKEY_PATH)
    plaintext = json.dumps(sample).encode()
    wrapped = envelope_encrypt(plaintext, pubkey)
    with open(OUT_PATH, "w") as f:
        json.dump(wrapped, f)
    print("Sample encrypted written to:", OUT_PATH)

if __name__ == '__main__':
    main()
