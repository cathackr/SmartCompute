#!/usr/bin/env python3
"""
SmartCompute Secure Download Manager
Sistema de descarga post-pago con tokens únicos y expiración

Features:
- Tokens únicos con firma HMAC
- Expiración automática de enlaces
- Logging de todas las descargas
- Protección contra acceso no autorizado
- Integración con sistema de licencias

Autor: SmartCompute Team
Versión: 2.0.0 Production
Fecha: 2025-09-20
"""

import os
import json
import hashlib
import hmac
import secrets
import time
import zipfile
import tempfile
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging
from pathlib import Path

class SecureDownloadManager:
    """Gestor de descargas seguras post-pago"""

    def __init__(self, download_secret: str = None):
        self.download_secret = download_secret or os.environ.get('DOWNLOAD_TOKEN_SECRET', secrets.token_hex(32))
        # Usar directorio local para demo
        self.base_path = Path('/home/gatux/smartcompute/secure-files')
        self.temp_path = Path('/tmp/smartcompute-downloads')

        # Crear directorios si no existen
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.temp_path.mkdir(parents=True, exist_ok=True)

        # Configurar logging
        self.setup_logging()

    def setup_logging(self):
        """Configurar logging de descargas"""
        log_dir = Path('/home/gatux/smartcompute/logs')
        log_dir.mkdir(exist_ok=True)

        self.logger = logging.getLogger('download_manager')
        handler = logging.FileHandler(log_dir / 'downloads.log')
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def create_license_package(self, license_type: str, customer_email: str) -> str:
        """Crear paquete de licencia personalizado"""

        self.logger.info(f"Creating license package for {customer_email}, type: {license_type}")

        # Crear directorio temporal para el paquete
        package_id = secrets.token_hex(16)
        package_dir = self.temp_path / f"package_{package_id}"
        package_dir.mkdir(exist_ok=True)

        try:
            # Copiar archivos base según tipo de licencia
            if license_type == 'enterprise':
                self._create_enterprise_package(package_dir, customer_email)
            elif license_type == 'industrial':
                self._create_industrial_package(package_dir, customer_email)
            else:
                raise ValueError(f"Tipo de licencia inválido: {license_type}")

            # Crear archivo ZIP
            zip_path = self.base_path / f"{license_type}_{package_id}.zip"
            self._create_zip_package(package_dir, zip_path)

            # Limpiar directorio temporal
            import shutil
            shutil.rmtree(package_dir)

            self.logger.info(f"License package created: {zip_path}")
            return str(zip_path)

        except Exception as e:
            # Limpiar en caso de error
            import shutil
            if package_dir.exists():
                shutil.rmtree(package_dir)
            raise e

    def _create_enterprise_package(self, package_dir: Path, customer_email: str):
        """Crear paquete Enterprise"""

        # Crear estructura de directorios
        (package_dir / 'smartcompute-enterprise').mkdir()
        (package_dir / 'smartcompute-enterprise' / 'bin').mkdir()
        (package_dir / 'smartcompute-enterprise' / 'config').mkdir()
        (package_dir / 'smartcompute-enterprise' / 'docs').mkdir()
        (package_dir / 'smartcompute-enterprise' / 'licenses').mkdir()

        # Copiar archivos Enterprise
        enterprise_files = [
            'smartcompute_enterprise_gui.py',
            'enterprise/smartcompute_live_analysis.py',
            'enterprise/mle_star_engine.py',
            'enterprise/hrm_mle_collaborative_bridge.py',
            'enterprise/smartcompute_user_auth_system.py'
        ]

        for file_path in enterprise_files:
            src_path = Path('/home/gatux/smartcompute') / file_path
            if src_path.exists():
                dst_path = package_dir / 'smartcompute-enterprise' / 'bin' / src_path.name
                import shutil
                shutil.copy2(src_path, dst_path)

        # Crear licencia personalizada
        license_key = self._generate_license_key('enterprise', customer_email)
        license_file = package_dir / 'smartcompute-enterprise' / 'licenses' / 'enterprise.lic'

        with open(license_file, 'w') as f:
            f.write(f"""# SmartCompute Enterprise License
# Customer: {customer_email}
# License Type: Enterprise
# Agents: Up to 100
# Issued: {datetime.now().isoformat()}
# Expires: {(datetime.now() + timedelta(days=365)).isoformat()}

LICENSE_KEY={license_key}
LICENSE_TYPE=enterprise
MAX_AGENTS=100
CUSTOMER_EMAIL={customer_email}
ISSUED_DATE={datetime.now().isoformat()}
EXPIRES_DATE={(datetime.now() + timedelta(days=365)).isoformat()}
""")

        # Crear archivo de configuración
        config_file = package_dir / 'smartcompute-enterprise' / 'config' / 'enterprise.yaml'
        with open(config_file, 'w') as f:
            f.write(f"""# SmartCompute Enterprise Configuration
version: "2.0.0"
license_type: "enterprise"
customer: "{customer_email}"

features:
  max_agents: 100
  advanced_ml: true
  siem_integration: true
  xdr_integration: true
  enterprise_dashboard: true
  priority_support: true

security:
  license_validation: true
  api_authentication: true
  encrypted_communications: true

integrations:
  enabled:
    - "siem"
    - "xdr"
    - "threat_intelligence"
    - "incident_response"
    - "compliance_reporting"

dashboard:
  enterprise_features: true
  custom_branding: true
  advanced_analytics: true
""")

        # Crear documentación
        readme_file = package_dir / 'smartcompute-enterprise' / 'README.md'
        with open(readme_file, 'w') as f:
            f.write(f"""# SmartCompute Enterprise v2.0.0

Licencia Enterprise para {customer_email}

## 🚀 Instalación Rápida

```bash
cd smartcompute-enterprise
chmod +x install_enterprise.sh
./install_enterprise.sh
```

## 📋 Características Enterprise

- ✅ Hasta 100 agentes simultáneos
- ✅ Análisis ML avanzado
- ✅ Integración SIEM/XDR
- ✅ Dashboard empresarial
- ✅ Soporte prioritario
- ✅ Compliance automático

## 🔧 Configuración

1. Verificar licencia: `python3 bin/smartcompute_enterprise_gui.py --check-license`
2. Iniciar sistema: `python3 bin/smartcompute_enterprise_gui.py`
3. Acceder dashboard: http://localhost:8080

## 📞 Soporte

- Email: enterprise-support@smartcompute.io
- Slack: #smartcompute-enterprise
- Documentación: https://docs.smartcompute.io/enterprise

---
© 2025 SmartCompute - Enterprise License
""")

    def _create_industrial_package(self, package_dir: Path, customer_email: str):
        """Crear paquete Industrial"""

        # Crear estructura de directorios
        (package_dir / 'smartcompute-industrial').mkdir()
        (package_dir / 'smartcompute-industrial' / 'bin').mkdir()
        (package_dir / 'smartcompute-industrial' / 'config').mkdir()
        (package_dir / 'smartcompute-industrial' / 'docs').mkdir()
        (package_dir / 'smartcompute-industrial' / 'licenses').mkdir()
        (package_dir / 'smartcompute-industrial' / 'protocols').mkdir()

        # Copiar archivos Industrial (incluye todos los Enterprise + Industrial)
        industrial_files = [
            'smartcompute_industrial_gui.py',
            'industrial_protocols_engine.py',
            'industrial_systems_integrator.py',
            'industrial_vulnerability_manager.py',
            'industrial_standards_compliance.py',
            'smartcompute_enterprise_gui.py',  # Industrial incluye Enterprise
            'enterprise/smartcompute_live_analysis.py',
            'enterprise/mle_star_engine.py'
        ]

        for file_path in industrial_files:
            src_path = Path('/home/gatux/smartcompute') / file_path
            if src_path.exists():
                dst_path = package_dir / 'smartcompute-industrial' / 'bin' / src_path.name
                import shutil
                shutil.copy2(src_path, dst_path)

        # Crear licencia Industrial
        license_key = self._generate_license_key('industrial', customer_email)
        license_file = package_dir / 'smartcompute-industrial' / 'licenses' / 'industrial.lic'

        with open(license_file, 'w') as f:
            f.write(f"""# SmartCompute Industrial License
# Customer: {customer_email}
# License Type: Industrial
# Agents: Unlimited
# Issued: {datetime.now().isoformat()}
# Expires: {(datetime.now() + timedelta(days=365)).isoformat()}

LICENSE_KEY={license_key}
LICENSE_TYPE=industrial
MAX_AGENTS=unlimited
CUSTOMER_EMAIL={customer_email}
ISSUED_DATE={datetime.now().isoformat()}
EXPIRES_DATE={(datetime.now() + timedelta(days=365)).isoformat()}

# Industrial Features
INDUSTRIAL_PROTOCOLS=true
CRITICAL_INFRASTRUCTURE=true
ISA_IEC_62443_COMPLIANCE=true
NERC_CIP_COMPLIANCE=true
SCADA_INTEGRATION=true
""")

        # Crear configuración Industrial
        config_file = package_dir / 'smartcompute-industrial' / 'config' / 'industrial.yaml'
        with open(config_file, 'w') as f:
            f.write(f"""# SmartCompute Industrial Configuration
version: "2.0.0"
license_type: "industrial"
customer: "{customer_email}"

features:
  max_agents: unlimited
  advanced_ml: true
  siem_integration: true
  xdr_integration: true
  enterprise_dashboard: true
  industrial_protocols: true
  critical_infrastructure: true
  priority_support: true
  dedicated_tam: true

security:
  license_validation: true
  api_authentication: true
  encrypted_communications: true
  industrial_grade_security: true

protocols:
  modbus: true
  profinet: true
  opc_ua: true
  dnp3: true
  iec_61850: true

compliance:
  isa_iec_62443: true
  nerc_cip: true
  nist_framework: true

integrations:
  enabled:
    - "siem"
    - "xdr"
    - "threat_intelligence"
    - "incident_response"
    - "compliance_reporting"
    - "scada_systems"
    - "industrial_networks"
    - "critical_infrastructure"

dashboard:
  industrial_features: true
  protocol_monitoring: true
  infrastructure_view: true
  compliance_tracking: true
""")

    def _generate_license_key(self, license_type: str, customer_email: str) -> str:
        """Generar clave de licencia única"""

        # Datos para la clave
        license_data = {
            'type': license_type,
            'email': customer_email,
            'issued': int(time.time()),
            'expires': int(time.time()) + (365 * 24 * 3600),  # 1 año
            'nonce': secrets.token_hex(8)
        }

        # Crear firma HMAC
        data_string = json.dumps(license_data, separators=(',', ':'))
        signature = hmac.new(
            self.download_secret.encode(),
            data_string.encode(),
            hashlib.sha256
        ).hexdigest()

        # Combinar datos y firma
        import base64
        license_key = base64.b64encode(
            f"{data_string}.{signature}".encode()
        ).decode()

        return license_key

    def _create_zip_package(self, source_dir: Path, zip_path: Path):
        """Crear archivo ZIP del paquete"""

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in source_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(source_dir)
                    zipf.write(file_path, arcname)

    def generate_download_token(self, license_type: str, customer_email: str, package_path: str) -> str:
        """Generar token de descarga único"""

        # Datos del token
        token_data = {
            'license': license_type,
            'email': customer_email,
            'package': package_path,
            'issued_at': int(time.time()),
            'expires_at': int(time.time()) + 86400 * 7,  # 7 días
            'nonce': secrets.token_hex(16)
        }

        # Crear firma HMAC
        data_string = json.dumps(token_data, separators=(',', ':'))
        signature = hmac.new(
            self.download_secret.encode(),
            data_string.encode(),
            hashlib.sha256
        ).hexdigest()

        # Crear token
        import base64
        token = base64.b64encode(
            f"{data_string}.{signature}".encode()
        ).decode()

        self.logger.info(f"Download token generated for {customer_email}, expires in 7 days")
        return token

    def validate_download_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validar token de descarga"""

        try:
            import base64
            decoded = base64.b64decode(token.encode()).decode()
            data_string, signature = decoded.rsplit('.', 1)

            # Verificar firma HMAC
            expected_signature = hmac.new(
                self.download_secret.encode(),
                data_string.encode(),
                hashlib.sha256
            ).hexdigest()

            if not hmac.compare_digest(signature, expected_signature):
                self.logger.warning("Invalid download token signature")
                return None

            # Parsear datos
            token_data = json.loads(data_string)

            # Verificar expiración
            if token_data['expires_at'] < int(time.time()):
                self.logger.warning(f"Expired download token for {token_data.get('email')}")
                return None

            # Verificar que el archivo existe
            package_path = Path(token_data['package'])
            if not package_path.exists():
                self.logger.error(f"Package file not found: {package_path}")
                return None

            return token_data

        except Exception as e:
            self.logger.error(f"Token validation error: {str(e)}")
            return None

    def process_download(self, token: str, client_ip: str) -> Optional[Dict[str, Any]]:
        """Procesar descarga con token"""

        token_data = self.validate_download_token(token)
        if not token_data:
            return None

        package_path = Path(token_data['package'])

        # Log de descarga
        self.logger.info(f"Download initiated: {token_data['email']} | {token_data['license']} | {client_ip}")

        # Generar URL de descarga temporal
        download_id = secrets.token_hex(16)

        return {
            'download_id': download_id,
            'package_path': str(package_path),
            'license_type': token_data['license'],
            'customer_email': token_data['email'],
            'expires_in': token_data['expires_at'] - int(time.time()),
            'file_size': package_path.stat().st_size if package_path.exists() else 0
        }

    def cleanup_expired_packages(self):
        """Limpiar paquetes expirados"""

        self.logger.info("Starting cleanup of expired packages")

        # Limpiar archivos más antiguos de 30 días
        cutoff_time = time.time() - (30 * 24 * 3600)
        removed_count = 0

        for file_path in self.base_path.glob('*.zip'):
            if file_path.stat().st_mtime < cutoff_time:
                file_path.unlink()
                removed_count += 1
                self.logger.info(f"Removed expired package: {file_path.name}")

        # Limpiar directorio temporal
        for temp_dir in self.temp_path.glob('package_*'):
            if temp_dir.is_dir() and temp_dir.stat().st_mtime < cutoff_time:
                import shutil
                shutil.rmtree(temp_dir)
                removed_count += 1

        self.logger.info(f"Cleanup completed: {removed_count} items removed")

def demo_download_system():
    """Demo del sistema de descarga"""
    print("💾 SmartCompute Secure Download Manager Demo")
    print("=" * 60)

    # Crear instancia del manager
    manager = SecureDownloadManager()

    # Simular creación de paquete Enterprise
    print("📦 Creando paquete Enterprise...")
    try:
        package_path = manager.create_license_package('enterprise', 'demo@example.com')
        print(f"✅ Paquete creado: {package_path}")

        # Generar token de descarga
        token = manager.generate_download_token('enterprise', 'demo@example.com', package_path)
        print(f"🔑 Token generado: {token[:32]}...")

        # Simular descarga
        download_info = manager.process_download(token, '192.168.1.100')
        if download_info:
            print("📥 Descarga autorizada:")
            print(f"   ID: {download_info['download_id']}")
            print(f"   Tamaño: {download_info['file_size']:,} bytes")
            print(f"   Expira en: {download_info['expires_in']} segundos")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

    print("\n🧹 Ejecutando limpieza...")
    manager.cleanup_expired_packages()

    print("\n✅ Demo completado")

if __name__ == "__main__":
    demo_download_system()