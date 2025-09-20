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
