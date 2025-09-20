#!/usr/bin/env bash
set -euo pipefail

# setup_prototype.sh
# Ejecuta: chmod +x setup_prototype.sh && ./setup_prototype.sh
# Crea un prototipo del pipeline: sample encryptor, preprocessor (decrypt+redact),
# hrm_train_stub (produce plans cifrados), y Node.js server que desencripta on-demand.

ROOTDIR="smartcompute_hrm_proto"
rm -rf "$ROOTDIR"
mkdir -p "$ROOTDIR"/{keys,sample,training-ready,plans,logs,python,node}
cd "$ROOTDIR"

echo "Creando README..."
cat > README_RUN.txt <<'EOF'
INSTRUCCIONES RÁPIDAS (prototipo local)
1) Generar dependencias Python y Node:
   - Python: python3 -m venv venv && source venv/bin/activate
             pip install -r python/requirements.txt
   - Node: cd node && npm install

2) Generar par de claves RSA (ya creado por el script).
   (keys/private_key.pem, keys/public_key.pem)

3) Generar sample cifrado (ya creado por el script).
   (sample/scan_sample.json.enc)

4) Ejecutar preprocessor para desencriptar + redactar -> training-ready/
   source venv/bin/activate
   python3 python/preprocessor.py --input sample/scan_sample.json.enc --out_dir training-ready

5) Ejecutar hrm trainer stub (produce plans/*.json.enc)
   python3 python/hrm_train_stub.py --input_dir training-ready --out_dir plans

6) Levantar server Node.js (orquestador/chat)
   cd node
   node server.js
   # POST a http://localhost:3000/chat con JSON:
   # { "scanId":"scan123","question":"¿Qué hago?","useHRM": true, "adminToken":"admintoken" }
   # Rpta: quickResponse + hrmPlan (si existe)

Notas de seguridad:
- Esto es un prototipo. En producción:
  * Cambiar RSA por KMS/Vault (envelope encryption).
  * No almacenar claves privadas sin HSM.
  * Añadir RBAC real y audit logs en DB.
  * No loguear datos sensibles.
EOF

echo "Generando claves RSA (mock KMS)..."
# Generate 2048-bit RSA keypair (for prototype only)
openssl genpkey -algorithm RSA -out keys/private_key.pem -pkeyopt rsa_keygen_bits:2048
openssl rsa -in keys/private_key.pem -pubout -out keys/public_key.pem

echo "Escribiendo requirements Python..."
cat > python/requirements.txt <<'PYREQ'
cryptography>=39.0.0
PyYAML>=6.0
requests>=2.0
python-dotenv>=1.0.0
PYREQ

echo "Creando redact_rules.yml..."
cat > redact_rules.yml <<'YML'
# redact_rules.yml
# Regex rules and fields to redact or hash
sensitive_fields:
  - payment_info
  - user_token
  - raw_payload
redactions:
  ip_regex: '\b(?:\d{1,3}\.){3}\d{1,3}\b'
  email_regex: '[\\w\\.-]+@[\\w\\.-]+'
  aws_key_regex: 'AKIA[0-9A-Z]{16}'
  credit_card_regex: '\b(?:\d[ -]*?){13,16}\b'
  jwt_regex: 'eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*'
YML

echo "Creando encrypt_sample.py (genera sample cifrado)..."
cat > python/encrypt_sample.py <<'PYENCRYPT'
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
PYENCRYPT

echo "Creando preprocessor.py (decrypt + redact)..."
cat > python/preprocessor.py <<'PYPRE'
#!/usr/bin/env python3
"""
preprocessor.py
- Lee archivo .enc (JSON with enc_key_b64, nonce_b64, ciphertext_b64)
- Usa private RSA key (keys/private_key.pem) para descifrar data key
- Descifra AES-GCM payload en memoria
- Aplica redaction rules (redact_rules.yml)
- Guarda JSON 'training-ready' en out_dir with filename <scan_id>.json (safe)
Usage:
  python3 preprocessor.py --input sample/scan_sample.json.enc --out_dir ../training-ready
"""
import argparse, os, json, base64, re, hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import yaml

HERE = os.path.dirname(__file__)
PRIVATE_KEY_PATH = os.path.join(HERE, "..", "keys", "private_key.pem")
REDACT_RULES_PATH = os.path.join(HERE, "..", "redact_rules.yml")

def load_private_key(path):
    with open(path, "rb") as f:
        return load_pem_private_key(f.read(), password=None)

def decrypt_envelope(enc_file_path, privkey):
    with open(enc_file_path, "r") as f:
        wrapper = json.load(f)
    enc_key = base64.b64decode(wrapper['enc_key_b64'])
    nonce = base64.b64decode(wrapper['nonce_b64'])
    ciphertext = base64.b64decode(wrapper['ciphertext_b64'])
    # decrypt data key
    data_key = privkey.decrypt(
        enc_key,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )
    aesgcm = AESGCM(data_key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext

def load_redact_rules(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def hash_keep(val):
    return hashlib.sha256(val.encode()).hexdigest()[:16]

def redact_json(obj, rules):
    # Simplified redaction: redact IPs, emails, aws keys, cc numbers and hash process_path
    txt = json.dumps(obj)
    redactions = rules.get("redactions", {})
    if "ip_regex" in redactions:
        txt = re.sub(redactions["ip_regex"], "<IP_REDACTED>", txt)
    if "email_regex" in redactions:
        txt = re.sub(redactions["email_regex"], "<EMAIL_REDACTED>", txt)
    if "aws_key_regex" in redactions:
        txt = re.sub(redactions["aws_key_regex"], "<AWSKEY_REDACTED>", txt)
    if "credit_card_regex" in redactions:
        txt = re.sub(redactions["credit_card_regex"], "<CC_REDACTED>", txt)
    if "jwt_regex" in redactions:
        txt = re.sub(redactions["jwt_regex"], "<JWT_REDACTED>", txt)
    j = json.loads(txt)
    # hash certain sensitive fields if present
    if isinstance(j.get("findings"), list):
        for f in j["findings"]:
            if "process_path" in f:
                f["process_hash"] = hash_keep(f["process_path"])
                del f["process_path"]
            if "raw_payload" in f:
                f["redacted_text"] = (f["raw_payload"][:300])  # keep short excerpt
                del f["raw_payload"]
    # redact source_meta
    if "source_meta" in j:
        if "ip" in j["source_meta"]:
            j["source_meta"]["ip"] = "<IP_REDACTED>"
        if "user" in j["source_meta"]:
            j["source_meta"]["user_hash"] = hash_keep(j["source_meta"]["user"])
            del j["source_meta"]["user"]
    return j

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--out_dir", required=True)
    args = parser.parse_args()
    privkey = load_private_key(PRIVATE_KEY_PATH)
    plaintext = decrypt_envelope(args.input, privkey)
    rules = load_redact_rules(REDACT_RULES_PATH)
    j = json.loads(plaintext)
    redacted = redact_json(j, rules)
    os.makedirs(args.out_dir, exist_ok=True)
    out_path = os.path.join(args.out_dir, f"{redacted.get('scan_id','scan_unknown')}.json")
    # safe write
    tmp = out_path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(redacted, f, indent=2)
    os.rename(tmp, out_path)
    print("Training-ready JSON written to:", out_path)

if __name__ == "__main__":
    main()
PYPRE
# ensure file is executable
chmod +x python/preprocessor.py

echo "Creando hrm_train_stub.py (genera plans cifrados basados en training-ready)..."
cat > python/hrm_train_stub.py <<'PYHRM'
#!/usr/bin/env python3
"""
hrm_train_stub.py
- Lee training-ready JSONs y genera un "plan jerárquico" simulado
- Encripta cada plan con envelope encryption (AES-GCM + RSA public key) y escribe plans/<scan_id>.json.enc
Usage:
  python3 hrm_train_stub.py --input_dir training-ready --out_dir plans
"""
import os, argparse, json, base64, secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

HERE = os.path.dirname(__file__)
PUBKEY_PATH = os.path.join(HERE, "..", "keys", "public_key.pem")

def load_pubkey(p):
    with open(p, "rb") as f:
        return load_pem_public_key(f.read())

def create_plan_from_findings(data):
    # Simulated HRM: prioritizes CRITICAL findings
    findings = data.get("findings", [])
    steps = []
    if any(f.get("severity","").upper()=="CRITICAL" for f in findings):
        steps.append({"step":"Isolate host from network", "priority":"High"})
        steps.append({"step":"Collect Sysmon and memory dump", "priority":"High"})
        steps.append({"step":"Hash suspicious binaries and upload for analysis", "priority":"Medium"})
    else:
        steps.append({"step":"Investigate events and monitor", "priority":"Medium"})
    plan = {
        "scan_id": data.get("scan_id"),
        "generated_at": "2025-09-15T11:00:00Z",
        "plan": steps,
        "notes":"This is a simulated HRM-generated plan (stub)."
    }
    return plan

def envelope_encrypt(plaintext_bytes, pubkey):
    data_key = secrets.token_bytes(32)
    aesgcm = AESGCM(data_key)
    nonce = secrets.token_bytes(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext_bytes, None)
    enc_data_key = pubkey.encrypt(
        data_key,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )
    return {"enc_key_b64": base64.b64encode(enc_data_key).decode(),
            "nonce_b64": base64.b64encode(nonce).decode(),
            "ciphertext_b64": base64.b64encode(ciphertext).decode()}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", required=True)
    parser.add_argument("--out_dir", required=True)
    args = parser.parse_args()
    pubkey = load_pubkey(PUBKEY_PATH)
    os.makedirs(args.out_dir, exist_ok=True)
    for fname in os.listdir(args.input_dir):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(args.input_dir, fname)
        with open(path, "r") as f:
            j = json.load(f)
        plan = create_plan_from_findings(j)
        plaintext = json.dumps(plan).encode()
        wrapped = envelope_encrypt(plaintext, pubkey)
        outpath = os.path.join(args.out_dir, fname.replace(".json", ".json.enc"))
        with open(outpath, "w") as f:
            json.dump(wrapped, f)
        print("Wrote encrypted plan:", outpath)

if __name__ == "__main__":
    main()
PYHRM
chmod +x python/hrm_train_stub.py

echo "Creando node server (server.js) y package.json..."
cat > node/package.json <<'PKG'
{
  "name": "smartcompute-hrm-orchestrator",
  "version": "0.1.0",
  "main": "server.js",
  "dependencies": {
    "express": "^4.18.2",
    "body-parser": "^1.20.2",
    "morgan": "^1.10.0"
  }
}
PKG

cat > node/server.js <<'NODEJS'
/*
 node/server.js
 - Express server with /chat endpoint.
 - If useHRM=true and adminToken matches, tries to decrypt plans/<scanId>.json.enc
 - Decrypts in-memory using RSA private key (mock KMS).
 Usage:
   node server.js
*/
const express = require('express');
const fs = require('fs').promises;
const path = require('path');
const crypto = require('crypto');
const bodyParser = require('body-parser');
const morgan = require('morgan');

const KEYS_DIR = path.join(__dirname, '..', 'keys');
const PLANS_DIR = path.join(__dirname, '..', 'plans');
const PRIVATE_KEY_PATH = path.join(KEYS_DIR, 'private_key.pem');
// Simulated admin token for prototype (in production use real AuthN/AuthZ)
const ADMIN_TOKEN = "admintoken";

async function decryptPlanFile(encFilePath) {
  const fileContents = await fs.readFile(encFilePath, 'utf8');
  const wrapper = JSON.parse(fileContents);
  const encKey = Buffer.from(wrapper.enc_key_b64, 'base64');
  const nonce = Buffer.from(wrapper.nonce_b64, 'base64');
  const ciphertext = Buffer.from(wrapper.ciphertext_b64, 'base64');

  // load private key
  const privPem = await fs.readFile(PRIVATE_KEY_PATH, 'utf8');
  const privateKey = {
    key: privPem,
    padding: crypto.constants.RSA_PKCS1_OAEP_PADDING,
    oaepHash: "sha256"
  };
  // decrypt data key
  const dataKey = crypto.privateDecrypt(privateKey, encKey); // Buffer
  // decrypt AES-GCM (256)
  const decipher = crypto.createDecipheriv('aes-256-gcm', dataKey, nonce);
  // Node's aes-gcm expects auth tag appended to ciphertext (cryptography's AESGCM already appends)
  // If tag is not present separately, it is included at end of ciphertext; but our encryption included tag; works.
  let decrypted = decipher.update(ciphertext);
  decrypted = Buffer.concat([decrypted, decipher.final()]);
  return JSON.parse(decrypted.toString());
}

async function main() {
  const app = express();
  app.use(morgan('dev'));
  app.use(bodyParser.json());

  app.post('/chat', async (req, res) => {
    try {
      const { scanId, question, useHRM, adminToken } = req.body || {};
      // quick response simulation
      const quickResponse = {
        summary: "Sugerencia inmediata: revisar procesos con EventID 8 y aislar si son CRITICAL.",
        confidence: "medium"
      };
      let hrmPlan = { status: "not_requested" };
      if (useHRM) {
        if (adminToken !== ADMIN_TOKEN) {
          return res.status(403).json({ error: "Forbidden: invalid admin token" });
        }
        const encPath = path.join(PLANS_DIR, `${scanId}.json.enc`);
        try {
          await fs.access(encPath);
        } catch (e) {
          return res.json({ quickResponse, hrmPlan: { status: "pending", message: "HRM plan not yet generated." } });
        }
        // decrypt on-demand (in-memory)
        const plan = await decryptPlanFile(encPath);
        hrmPlan = { status: "ready", plan };
      }
      return res.json({ quickResponse, hrmPlan });
    } catch (err) {
      console.error("Error /chat:", err);
      return res.status(500).json({ error: "internal error" });
    }
  });

  const port = process.env.PORT || 3000;
  app.listen(port, () => {
    console.log("Orchestrator listening on port", port);
    console.log("POST /chat {scanId, question, useHRM, adminToken}");
  });
}

main().catch(e => console.error(e));
NODEJS

echo "Creando archivo .gitignore..."
cat > .gitignore <<'GI'
keys/
*.pem
sample/*.enc
plans/*.json.enc
training-ready/
venv/
node_modules/
GI

echo "Instalando dependencias Node.js (puede tardar si npm descarga paquetes)..."
cd node
npm install --silent
cd ..

echo "Instalando dependencias Python en entorno virtual (opcional pero recomendado)..."
python3 -m venv venv
source venv/bin/activate
pip install -r python/requirements.txt
deactivate

echo "Generando sample cifrado (ejecutando encrypt_sample.py)..."
python3 python/encrypt_sample.py

echo "Creando .env demo para server (no obligatorio)..."
cat > node/.env <<'ENV'
# Demo only - in prod use vault / KMS and don't store tokens in plaintext
ADMIN_TOKEN=admintoken
ENV

echo "Proyecto creado en: $PWD"
echo
cat README_RUN.txt

echo "HECHO. Resumen de comandos útiles:"
echo "  source venv/bin/activate"
echo "  python3 python/preprocessor.py --input sample/scan_sample.json.enc --out_dir training-ready"
echo "  python3 python/hrm_train_stub.py --input_dir training-ready --out_dir plans"
echo "  cd node && node server.js"
echo
echo "POST example (curl):"
echo "curl -X POST http://localhost:3000/chat -H 'Content-Type: application/json' -d '{\"scanId\":\"scan123\",\"question\":\"¿Qué hago?\",\"useHRM\":true,\"adminToken\":\"admintoken\"}'"