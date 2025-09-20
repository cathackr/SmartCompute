#!/usr/bin/env python3
import json, re, hashlib, base64, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import yaml

# ----------- CONFIG -----------
REDACT_RULES_FILE = "../redact_rules.yml"
ENC_FILE = "../sample/scan_sample.json.enc"
OUT_FILE = "../redacted_output.json"
# ------------------------------

def load_rules():
    with open(REDACT_RULES_FILE, "r") as f:
        return yaml.safe_load(f)

def hash_keep(x):
    return hashlib.sha256(x.encode()).hexdigest()[:16]

def apply_redaction(event, rules):
    text = json.dumps(event)
    for rule in rules.get("regex_rules", []):
        pattern = re.compile(rule["pattern"])
        repl = rule.get("replacement", "<REDACTED>")
        text = pattern.sub(repl, text)

    ev = json.loads(text)

    # Hash selected fields
    for f in rules.get("hash_fields", []):
        if f in ev:
            ev[f + "_hash"] = hash_keep(ev[f])
            del ev[f]

    # Drop sensitive fields
    for f in rules.get("drop_fields", []):
        ev.pop(f, None)

    return ev

def decrypt_payload(enc_obj):
    # Este script necesita la clave privada para descifrar la clave AES
    print("[!] ADVERTENCIA: Este script está simplificado. En un entorno real necesitarías:")
    print("    - Acceso a la clave privada RSA para descifrar enc_key_b64")
    print("    - Implementar el descifrado envelope completo")
    print("    Por ahora simularemos con datos de ejemplo...")

    # Para propósitos de demostración, retornamos los datos originales
    sample_data = {
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
    return sample_data

def main():
    rules = load_rules()
    with open(ENC_FILE, "r") as f:
        enc_obj = json.load(f)

    data = decrypt_payload(enc_obj)

    redacted = apply_redaction(data, rules)
    with open(OUT_FILE, "w") as f:
        json.dump(redacted, f, indent=2)

    print(f"[OK] JSON redacted listo en {OUT_FILE}")

if __name__ == "__main__":
    main()