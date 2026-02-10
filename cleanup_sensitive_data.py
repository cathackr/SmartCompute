#!/usr/bin/env python3
"""
SmartCompute Industrial - Limpieza de Datos Sensibles
Desarrollado por: ggwre04p0@mozmail.com
LinkedIn: https://www.linkedin.com/in/martín-iribarne-swtf/

Script para remover información sensible antes de commit
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime

def clean_sensitive_data():
    """Limpiar datos sensibles del repositorio"""

    print("🧹 ======== LIMPIEZA DE DATOS SENSIBLES ========")
    print("🔒 Removiendo información confidencial de pruebas")
    print("📧 Desarrollado por: ggwre04p0@mozmail.com")
    print("🔗 LinkedIn: https://www.linkedin.com/in/martín-iribarne-swtf/")
    print()

    # Directorios y archivos a limpiar/excluir
    sensitive_patterns = [
        # Archivos de datos de prueba
        "reports/production_session_*.json",
        "reports/hrm_analysis_*.json",
        "reports/photo_analysis_session_*.json",

        # Archivos de demostración con datos reales
        "smartcompute_production_demo.py",
        "smartcompute_complete_demo.py",
        "smartcompute_field_integration.py",
        "interactive_photo_analysis_demo.py",
        "photo_analysis_full_demo.py",

        # Directorios de datos sensibles
        "admin_auth_data/",
        "hrm_test/",
        "vault_test/",
        "nodejs_test/",
        "mitre_test/",

        # Archivos temporales y logs
        "*.log",
        "*.tmp",
        "__pycache__/",
        "node_modules/",

        # Archivos de configuración con secretos reales
        "config_real.ini",
        "operators_real.json",
        "secrets.json"
    ]

    # Crear directorio para archivos seguros
    safe_dir = Path("clean_repository")
    safe_dir.mkdir(exist_ok=True)

    # Archivos core seguros para incluir
    safe_files = [
        # Módulos principales (limpios)
        "smartcompute_secure_interaction.py",
        "smartcompute_field_diagnostics.py",
        "smartcompute_visual_ai.py",
        "hrm_integration.py",
        "smartcompute_ai_learning.py",
        "mle_star_analysis_engine.py",
        "smartcompute_approval_workflow.js",
        "package.json",
        "smartcompute_mobile_field_interface.py",
        "generate_hybrid_flow_analytics_dashboard.py",
        "smartcompute_integrated_workflow.py",

        # Documentación
        "DEPLOYMENT_PACKAGE.md",
        "SMARTCOMPUTE_GUI_USER_GUIDE.md",
        "COMPETITIVE_ANALYSIS_ENTERPRISE_SECURITY.md",
        "SMARTCOMPUTE_INDUSTRIAL_USER_GUIDE.md",

        # Scripts de utilidad
        "create_client_package.py",
        "cleanup_sensitive_data.py",

        # Archivos de configuración de ejemplo (sin secretos)
        "config_example.ini",
        "operators_example.json",
        "authorized_locations_example.json"
    ]

    print("📂 Creando estructura limpia...")

    # Copiar archivos seguros
    copied_files = 0
    for file_name in safe_files:
        file_path = Path(file_name)
        if file_path.exists():
            # Verificar si es archivo de configuración con secretos
            if file_name.endswith('.py'):
                clean_python_file(file_path, safe_dir / file_name)
            else:
                shutil.copy2(file_path, safe_dir / file_name)
            copied_files += 1
            print(f"  ✅ {file_name}")
        else:
            print(f"  ⚠️ No encontrado: {file_name}")

    # Crear archivos de configuración de ejemplo limpios
    create_clean_config_examples(safe_dir)

    # Crear README de seguridad
    create_security_readme(safe_dir)

    # Crear estructura de directorios necesaria
    (safe_dir / "reports").mkdir(exist_ok=True)
    (safe_dir / "logs").mkdir(exist_ok=True)
    (safe_dir / "config").mkdir(exist_ok=True)
    (safe_dir / "data").mkdir(exist_ok=True)

    # Crear .gitignore seguro
    create_secure_gitignore(safe_dir)

    print(f"\n✅ ======== LIMPIEZA COMPLETADA ========")
    print(f"📦 Archivos seguros copiados: {copied_files}")
    print(f"📁 Directorio limpio: {safe_dir}")
    print(f"🔒 Datos sensibles excluidos")
    print(f"📋 Configuración de ejemplo creada")
    print(f"🛡️ Prácticas de seguridad documentadas")

    return safe_dir

def clean_python_file(input_path, output_path):
    """Limpiar archivo Python de datos sensibles"""

    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remover o reemplazar datos sensibles
    replacements = [
        # Códigos y tokens de ejemplo
        (r'totp_code = "\d{6}"', 'totp_code = "123456"  # Ejemplo, cambiar en producción  # Ejemplo, cambiar en producción'),
        (r'session_token = "JWT-\d+"', 'session_token = "JWT-EXAMPLE"'),
        (r'"session_id": "SES-EXAMPLE"]*"', '"session_id": "SES-EXAMPLE"'),

        # Coordenadas GPS de ejemplo
        (r'lat = -34.603700  # Coordenada de ejemplo  # Coordenada de ejemplo'),
        (r'lng = -58.381600  # Coordenada de ejemplo  # Coordenada de ejemplo'),

        # Remover secretos reales si existen
        (r'jwt_secret = "CHANGE_IN_PRODUCTION"]*"', 'jwt_secret = "CHANGE_IN_PRODUCTION"'),
        (r'encryption_key = "GENERATE_NEW_KEY"]*"', 'encryption_key = "GENERATE_NEW_KEY"'),
    ]

    for pattern, replacement in replacements:
        import re
        content = re.sub(pattern, replacement, content)

    # Escribir archivo limpio
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

def create_clean_config_examples(safe_dir):
    """Crear archivos de configuración de ejemplo limpios"""

    # config_example.ini
    config_example = """[security]
# ⚠️ CAMBIAR ESTOS VALORES EN PRODUCCIÓN
jwt_secret = GENERATE_SECURE_JWT_SECRET_256_BITS
encryption_key = GENERATE_AES_256_ENCRYPTION_KEY
session_timeout_hours = 8
max_failed_attempts = 3

[database]
db_path = ./data/smartcompute.db
backup_interval_hours = 24
max_history_days = 90

[network]
api_port = 3000
websocket_port = 3001
max_connections = 100
enable_ssl = true

[logging]
log_level = INFO
log_file = ./logs/smartcompute.log
max_log_size_mb = 100
backup_count = 10

[ai]
visual_confidence_threshold = 0.85
hrm_confidence_threshold = 0.80
learning_enabled = true
auto_update_models = true

[notifications]
email_enabled = true
sms_enabled = false
slack_enabled = false
"""

    with open(safe_dir / "config_example.ini", 'w') as f:
        f.write(config_example)

    # operators_example.json
    operators_example = {
        "operators": {
            "OP001": {
                "name": "Operador Ejemplo",
                "role": "technician",
                "level": 2,
                "certifications": ["electrical", "mechanical"],
                "phone": "+54911111111",
                "email": "operador@empresa.com",
                "totp_secret": "GENERATE_UNIQUE_SECRET_PER_OPERATOR",
                "authorized_locations": ["planta_principal"]
            }
        },
        "roles": {
            "technician": {"level": 1, "permissions": ["analyze", "execute_low_risk"]},
            "supervisor": {"level": 2, "permissions": ["analyze", "execute_medium_risk", "approve"]},
            "manager": {"level": 3, "permissions": ["all"]}
        }
    }

    with open(safe_dir / "operators_example.json", 'w') as f:
        json.dump(operators_example, f, indent=2)

    # authorized_locations_example.json
    locations_example = {
        "planta_principal": {
            "name": "Planta Principal",
            "lat": -34.603700,
            "lng": -58.381600,
            "radius_meters": 100,
            "authorized_operators": ["OP001", "OP002"],
            "emergency_contact": "+54911234567",
            "safety_requirements": ["safety_equipment", "authorized_personnel"]
        }
    }

    with open(safe_dir / "authorized_locations_example.json", 'w') as f:
        json.dump(locations_example, f, indent=2)

def create_security_readme(safe_dir):
    """Crear README de seguridad"""

    security_readme = """# 🔒 CONFIGURACIÓN SEGURA - SMARTCOMPUTE INDUSTRIAL

## ⚠️ ADVERTENCIAS CRÍTICAS DE SEGURIDAD

### 🚨 ANTES DE LA PRIMERA EJECUCIÓN:

1. **CAMBIAR TODAS LAS CLAVES DE EJEMPLO**
   ```bash
   # Generar clave JWT segura
   openssl rand -hex 32

   # Generar clave de encriptación AES-256
   openssl rand -hex 32

   # Generar secreto TOTP único por operador
   python3 -c "import pyotp; print(pyotp.random_base32())"
   ```

2. **CONFIGURAR UBICACIONES GPS REALES**
   - Usar coordenadas exactas de tu planta
   - Ajustar radio de seguridad apropiado
   - Verificar precisión GPS en el sitio

3. **CONFIGURAR OPERADORES REALES**
   - Crear cuentas individuales por técnico
   - Asignar niveles apropiados
   - Configurar 2FA único por persona

### 🛡️ PRÁCTICAS OBLIGATORIAS:

- ✅ Usar HTTPS en producción
- ✅ Configurar firewall restrictivo
- ✅ Habilitar logs de auditoría
- ✅ Backup automático de configuración
- ✅ Monitoreo de accesos

### ❌ NUNCA HACER:

- ❌ Usar configuración de ejemplo en producción
- ❌ Compartir secretos TOTP entre operadores
- ❌ Deshabilitar verificación GPS
- ❌ Ejecutar con permisos de root
- ❌ Conectar directamente a internet

## 📋 CHECKLIST DE SEGURIDAD:

- [ ] Claves únicas generadas
- [ ] GPS configurado y verificado
- [ ] Operadores con 2FA habilitado
- [ ] Firewall configurado
- [ ] SSL/TLS habilitado
- [ ] Logs de auditoría activos
- [ ] Backup automático configurado
- [ ] Personal entrenado en procedimientos

**📞 Soporte de seguridad:** ggwre04p0@mozmail.com
"""

    with open(safe_dir / "SECURITY_README.md", 'w') as f:
        f.write(security_readme)

def create_secure_gitignore(safe_dir):
    """Crear .gitignore seguro"""

    gitignore_content = """# SmartCompute Industrial - Archivos excluidos por seguridad

# Datos sensibles
*.log
*.key
*.pem
config_real.ini
operators_real.json
secrets.json

# Datos de producción
/data/
/reports/*.json
production_session_*
hrm_analysis_*

# Credenciales y tokens
auth_data/
vault_test/
admin_auth_data/

# Archivos temporales
*.tmp
*.temp
__pycache__/
node_modules/
.env

# Archivos de prueba con datos reales
*_demo.py
*_test.py
test_*

# Backups locales
*.bak
*.backup

# Directorios de desarrollo
hrm_test/
mitre_test/
nodejs_test/
vault_test/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Sistema
.DS_Store
Thumbs.db
"""

    with open(safe_dir / ".gitignore", 'w') as f:
        f.write(gitignore_content)

if __name__ == "__main__":
    clean_sensitive_data()