#!/usr/bin/env python3
"""
agent_runner_secure.py

Prototipo seguro para ejecutar MLE-Star-Agent localmente:
- Solo lectura sobre SmartCompute
- Genera reporte JSON
- Cifra el reporte con AES-GCM
- Añade resumen GPT-friendly
"""
import subprocess, os, json, datetime
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# ----------------- CONFIG -----------------
AGENT_DIR = "MLE-Star-Agent"       # Path local al agente
TARGET_REPO = "SmartCompute"       # Path local al repo SmartCompute
REPORTS_DIR = "reports"            # Directorio donde guardar reportes
AES_KEY = b"32bytessecurekeyforaes256!!!!!!!!!"  # 32 bytes clave AES para prototipo
# -----------------------------------------

os.makedirs(REPORTS_DIR, exist_ok=True)

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
raw_report_path = os.path.join(REPORTS_DIR, f"report_{timestamp}.json")
enc_report_path = raw_report_path + ".enc"

# --------- 1. Ejecutar MLE-Star-Agent ----------
cmd = ["python3", os.path.join(AGENT_DIR, "run_agent.py"),
       "--repo", TARGET_REPO,
       "--output", raw_report_path,
       "--read-only"]

print(f"[INFO] Ejecutando MLE-Star-Agent en {TARGET_REPO}...")
subprocess.run(cmd, check=True)
print(f"[OK] Reporte sin procesar generado en {raw_report_path}")

# --------- 2. Cargar y procesar reporte ----------
with open(raw_report_path, "r") as f:
    report = json.load(f)

# --------- 3. Crear resumen GPT-friendly ----------
summary_lines = []
for idx, item in enumerate(report.get("recommendations", [])):
    rec_type = item.get("type", "unknown")
    rec_msg = item.get("message", "")
    summary_lines.append(f"{idx+1}. [{rec_type}] {rec_msg}")

summary_text = "\n".join(summary_lines)
report["gpt_summary"] = summary_text

# --------- 4. Guardar JSON actualizado ----------
with open(raw_report_path, "w") as f:
    json.dump(report, f, indent=2)
print(f"[OK] Reporte con resumen GPT agregado en {raw_report_path}")

# --------- 5. Cifrar reporte en AES-GCM ----------
with open(raw_report_path, "rb") as f:
    data_bytes = f.read()

nonce = os.urandom(12)
aesgcm = AESGCM(AES_KEY)
ciphertext = aesgcm.encrypt(nonce, data_bytes, None)

with open(enc_report_path, "wb") as f:
    f.write(nonce + ciphertext)

print(f"[OK] Reporte cifrado listo en {enc_report_path}")
print("[INFO] Mantén segura la clave AES para poder desencriptar y analizar con GPT")