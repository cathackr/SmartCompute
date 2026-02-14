#!/usr/bin/env python3
"""
SmartCompute Industrial - Sistema de Exportación de Reportes con Autorización Granular
Autor: SmartCompute Industrial Team
Fecha: 2024-09-19

Sistema avanzado de exportación de reportes industriales con control de acceso granular,
cifrado de datos sensibles, y formatos múltiples incluyendo PDF, Excel, CSV y JSON.
Integra con sistemas de autenticación empresarial y cumple normativas industriales.
"""

import asyncio
import os
import json
import csv
import sqlite3
import hashlib
import hmac
import secrets
import zipfile
import tempfile
import io
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field, asdict
from enum import Enum, auto
from pathlib import Path
import logging
from contextlib import asynccontextmanager
# import aiofiles
# import aiohttp
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
# import pandas as pd
# from fpdf import FPDF
# import openpyxl
# from openpyxl.styles import Font, PatternFill, Border, Side
# from openpyxl.utils.dataframe import dataframe_to_rows
# import matplotlib.pyplot as plt
# import seaborn as sns
# from jinja2 import Template

# Configuración de logging seguro
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/gatux/smartcompute/logs/industrial_reports_exporter.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ReportType(Enum):
    """Tipos de reportes disponibles en el sistema industrial"""
    VULNERABILITY_ASSESSMENT = "vulnerability_assessment"
    SCADA_LOGS_ANALYSIS = "scada_logs_analysis"
    NETWORK_TOPOLOGY = "network_topology"
    PROCESS_VARIABLES = "process_variables"
    SECURITY_INCIDENTS = "security_incidents"
    COMPLIANCE_AUDIT = "compliance_audit"
    RISK_ANALYSIS = "risk_analysis"
    PERFORMANCE_METRICS = "performance_metrics"
    ALARM_SUMMARY = "alarm_summary"
    MAINTENANCE_SCHEDULE = "maintenance_schedule"

class ReportFormat(Enum):
    """Formatos de exportación soportados"""
    PDF = "pdf"
    EXCEL = "xlsx"
    CSV = "csv"
    JSON = "json"
    HTML = "html"
    XML = "xml"

class AccessLevel(Enum):
    """Niveles de acceso para reportes industriales"""
    PUBLIC = auto()          # Información general
    RESTRICTED = auto()      # Personal autorizado
    CONFIDENTIAL = auto()    # Supervisores y gerentes
    SECRET = auto()          # Alta gerencia y seguridad
    TOP_SECRET = auto()      # Solo directores ejecutivos

class DataSensitivity(Enum):
    """Clasificación de sensibilidad de datos"""
    UNCLASSIFIED = auto()
    INTERNAL_USE = auto()
    CONFIDENTIAL = auto()
    HIGHLY_CONFIDENTIAL = auto()
    RESTRICTED = auto()

@dataclass
class ReportPermission:
    """Permisos granulares para exportación de reportes"""
    report_type: ReportType
    user_id: str
    role: str
    access_level: AccessLevel
    allowed_formats: List[ReportFormat]
    data_filters: Dict[str, Any] = field(default_factory=dict)
    expiration_date: Optional[datetime] = None
    ip_restrictions: List[str] = field(default_factory=list)
    time_restrictions: Dict[str, str] = field(default_factory=dict)  # {"start": "08:00", "end": "18:00"}
    max_exports_per_day: int = 10
    require_approval: bool = False
    watermark_required: bool = True

@dataclass
class ReportMetadata:
    """Metadatos de reporte para auditoría"""
    report_id: str
    report_type: ReportType
    format: ReportFormat
    created_by: str
    created_at: datetime
    file_size: int
    checksum: str
    sensitivity: DataSensitivity
    access_level: AccessLevel
    export_restrictions: Dict[str, Any] = field(default_factory=dict)
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class ExportRequest:
    """Solicitud de exportación de reporte"""
    request_id: str
    user_id: str
    report_type: ReportType
    format: ReportFormat
    operator_encryption_key: str  # Clave que genera el operador para cifrado
    parameters: Dict[str, Any] = field(default_factory=dict)
    date_range: Optional[Tuple[datetime, datetime]] = None
    filters: Dict[str, Any] = field(default_factory=dict)
    requested_at: datetime = field(default_factory=datetime.now)
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None

class IndustrialReportsExporter:
    """Sistema de exportación de reportes industriales con autorización granular"""

    def __init__(self, db_path: str = "/home/gatux/smartcompute/data/reports.db"):
        self.db_path = db_path
        self.encryption_key = self._generate_encryption_key()
        self.aes_gcm = AESGCM(self.encryption_key)
        self.pending_approvals: Dict[str, ExportRequest] = {}
        self._initialize_database()

    def _generate_encryption_key(self) -> bytes:
        """Genera clave de cifrado para reportes sensibles"""
        password_env = os.getenv('REPORTS_ENCRYPTION_PASSWORD')

        if not password_env:
            logging.error("❌ REPORTS_ENCRYPTION_PASSWORD no configurado!")
            logging.error("⚠️  Los reportes industriales contienen información sensible y DEBEN estar cifrados.")
            logging.error("💡 Configure REPORTS_ENCRYPTION_PASSWORD en .env con una contraseña fuerte (mínimo 32 caracteres)")
            raise ValueError(
                "REPORTS_ENCRYPTION_PASSWORD es requerido para cifrado de reportes industriales. "
                "Configure esta variable en .env antes de continuar."
            )

        password = password_env.encode()

        # Usar salt desde variable de entorno o generar uno aleatorio (no hardcodeado)
        salt_env = os.getenv('REPORTS_ENCRYPTION_SALT')
        if salt_env:
            salt = salt_env.encode()
        else:
            # Generar salt aleatorio y advertir que debe guardarse
            import secrets
            salt = secrets.token_bytes(32)
            salt_hex = salt.hex()
            logging.warning("⚠️  REPORTS_ENCRYPTION_SALT no configurado. Se generó uno aleatorio.")
            logging.warning(f"💾 Guarde este salt en .env: REPORTS_ENCRYPTION_SALT={salt_hex}")
            logging.warning("⚠️  Sin este salt, los reportes cifrados previamente NO podrán descifrarse!")

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=150000
        )
        return kdf.derive(password)

    def _initialize_database(self):
        """Inicializa base de datos de reportes y permisos"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Tabla de permisos de reportes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS report_permissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    report_type TEXT NOT NULL,
                    access_level INTEGER NOT NULL,
                    allowed_formats TEXT NOT NULL,
                    data_filters TEXT,
                    expiration_date TIMESTAMP,
                    ip_restrictions TEXT,
                    time_restrictions TEXT,
                    max_exports_per_day INTEGER DEFAULT 10,
                    require_approval BOOLEAN DEFAULT 0,
                    watermark_required BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Tabla de metadatos de reportes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS report_metadata (
                    report_id TEXT PRIMARY KEY,
                    report_type TEXT NOT NULL,
                    format TEXT NOT NULL,
                    created_by TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    file_size INTEGER NOT NULL,
                    checksum TEXT NOT NULL,
                    sensitivity INTEGER NOT NULL,
                    access_level INTEGER NOT NULL,
                    file_path TEXT NOT NULL,
                    export_restrictions TEXT,
                    audit_trail TEXT
                )
            ''')

            # Tabla de solicitudes de exportación
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS export_requests (
                    request_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    report_type TEXT NOT NULL,
                    format TEXT NOT NULL,
                    parameters TEXT,
                    date_range TEXT,
                    filters TEXT,
                    requested_at TIMESTAMP NOT NULL,
                    status TEXT DEFAULT 'pending',
                    approved_by TEXT,
                    approved_at TIMESTAMP
                )
            ''')

            # Tabla de auditoría de accesos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS access_audit (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    report_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    success BOOLEAN NOT NULL
                )
            ''')

            conn.commit()

        # Insertar permisos predeterminados para roles industriales
        self._insert_default_permissions()

        logger.info("Base de datos de reportes industriales inicializada correctamente")

    def _insert_default_permissions(self):
        """Inserta permisos predeterminados para roles industriales"""
        default_permissions = [
            # Administrador Industrial - Acceso completo
            {
                'user_id': 'admin_industrial',
                'role': 'industrial_administrator',
                'report_type': ReportType.VULNERABILITY_ASSESSMENT.value,
                'access_level': AccessLevel.TOP_SECRET.value,
                'allowed_formats': [f.value for f in ReportFormat],
                'max_exports_per_day': 50,
                'require_approval': False
            },
            # Operador Industrial - Acceso limitado
            {
                'user_id': 'operator_industrial',
                'role': 'industrial_operator',
                'report_type': ReportType.PROCESS_VARIABLES.value,
                'access_level': AccessLevel.RESTRICTED.value,
                'allowed_formats': [ReportFormat.PDF.value, ReportFormat.CSV.value],
                'max_exports_per_day': 10,
                'require_approval': True
            },
            # Supervisor de Seguridad
            {
                'user_id': 'security_supervisor',
                'role': 'security_supervisor',
                'report_type': ReportType.SECURITY_INCIDENTS.value,
                'access_level': AccessLevel.SECRET.value,
                'allowed_formats': [ReportFormat.PDF.value, ReportFormat.EXCEL.value],
                'max_exports_per_day': 25,
                'require_approval': False
            },
            # Ingeniero de Mantenimiento
            {
                'user_id': 'maintenance_engineer',
                'role': 'maintenance_engineer',
                'report_type': ReportType.MAINTENANCE_SCHEDULE.value,
                'access_level': AccessLevel.CONFIDENTIAL.value,
                'allowed_formats': [ReportFormat.PDF.value, ReportFormat.EXCEL.value, ReportFormat.CSV.value],
                'max_exports_per_day': 15,
                'require_approval': False
            }
        ]

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            for perm in default_permissions:
                cursor.execute('''
                    INSERT OR IGNORE INTO report_permissions
                    (user_id, role, report_type, access_level, allowed_formats,
                     max_exports_per_day, require_approval)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    perm['user_id'], perm['role'], perm['report_type'],
                    perm['access_level'], json.dumps(perm['allowed_formats']),
                    perm['max_exports_per_day'], perm['require_approval']
                ))

            conn.commit()

    async def check_permissions(self, user_id: str, report_type: ReportType,
                              format: ReportFormat, ip_address: str = None) -> bool:
        """Verifica permisos granulares para exportación de reportes"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Obtener permisos del usuario
                cursor.execute('''
                    SELECT * FROM report_permissions
                    WHERE user_id = ? AND report_type = ?
                ''', (user_id, report_type.value))

                perm_data = cursor.fetchone()
                if not perm_data:
                    logger.warning(f"Sin permisos para usuario {user_id} y reporte {report_type.value}")
                    return False

                # Verificar formato permitido
                allowed_formats = json.loads(perm_data[5])  # allowed_formats column
                if format.value not in allowed_formats:
                    logger.warning(f"Formato {format.value} no permitido para usuario {user_id}")
                    return False

                # Verificar expiración
                expiration_date = perm_data[7]  # expiration_date column
                if expiration_date:
                    exp_date = datetime.fromisoformat(expiration_date)
                    if datetime.now() > exp_date:
                        logger.warning(f"Permisos expirados para usuario {user_id}")
                        return False

                # Verificar restricciones de IP
                ip_restrictions = perm_data[8]  # ip_restrictions column
                if ip_restrictions and ip_address:
                    allowed_ips = json.loads(ip_restrictions)
                    if ip_address not in allowed_ips:
                        logger.warning(f"IP {ip_address} no autorizada para usuario {user_id}")
                        return False

                # Verificar restricciones de tiempo
                time_restrictions = perm_data[9]  # time_restrictions column
                if time_restrictions:
                    time_limits = json.loads(time_restrictions)
                    current_time = datetime.now().strftime("%H:%M")
                    if not (time_limits.get('start', '00:00') <= current_time <= time_limits.get('end', '23:59')):
                        logger.warning(f"Fuera del horario permitido para usuario {user_id}")
                        return False

                # Verificar límite diario de exportaciones
                cursor.execute('''
                    SELECT COUNT(*) FROM access_audit
                    WHERE user_id = ? AND DATE(timestamp) = DATE('now') AND success = 1
                ''', (user_id,))

                daily_exports = cursor.fetchone()[0]
                max_daily = perm_data[10]  # max_exports_per_day column

                if daily_exports >= max_daily:
                    logger.warning(f"Límite diario de exportaciones excedido para usuario {user_id}")
                    return False

                return True

        except Exception as e:
            logger.error(f"Error verificando permisos: {str(e)}")
            return False

    def _apply_watermark(self, content: bytes, format: ReportFormat,
                        user_id: str, timestamp: str) -> bytes:
        """Aplica marca de agua a reportes sensibles"""
        watermark_text = f"SmartCompute Industrial | Usuario: {user_id} | Fecha: {timestamp} | CONFIDENCIAL"

        if format == ReportFormat.PDF:
            # Para PDF, agregar watermark en cada página
            # Implementación simplificada
            return content
        elif format == ReportFormat.EXCEL:
            # Para Excel, agregar hoja con información de watermark
            return content
        else:
            # Para otros formatos, agregar header/footer con información
            return content

    async def generate_vulnerability_report(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Genera reporte de evaluación de vulnerabilidades"""
        # Datos simulados de vulnerabilidades industriales
        vulnerabilities = [
            {
                'id': 'VULN-001',
                'title': 'Buffer Overflow en Controlador SIMATIC S7-1200',
                'severity': 'CRITICAL',
                'cvss_score': 9.8,
                'location': 'Planta Principal - Zona A',
                'affected_asset': 'PLC-SIMATIC-001',
                'description': 'Vulnerabilidad de desbordamiento de buffer en firmware v4.2',
                'impact': 'Compromiso total del controlador, posible parada de producción',
                'remediation': 'Actualizar firmware a versión 4.4.3 o superior',
                'discovered_date': '2024-09-15',
                'status': 'Open'
            },
            {
                'id': 'VULN-002',
                'title': 'Autenticación débil en HMI WinCC',
                'severity': 'HIGH',
                'cvss_score': 8.1,
                'location': 'Sala de Control Central',
                'affected_asset': 'HMI-WINCC-001',
                'description': 'Contraseña por defecto en interfaz de operador',
                'impact': 'Acceso no autorizado a controles de proceso',
                'remediation': 'Cambiar contraseña por defecto y habilitar 2FA',
                'discovered_date': '2024-09-16',
                'status': 'In Progress'
            },
            {
                'id': 'VULN-003',
                'title': 'Protocolo Modbus sin cifrado',
                'severity': 'MEDIUM',
                'cvss_score': 6.5,
                'location': 'Red Industrial VLAN-100',
                'affected_asset': 'MODBUS-RTU-NETWORK',
                'description': 'Comunicaciones Modbus sin cifrado entre dispositivos',
                'impact': 'Intercepción de datos de proceso y comandos',
                'remediation': 'Implementar Modbus/TCP con TLS o migrar a OPC-UA',
                'discovered_date': '2024-09-17',
                'status': 'Open'
            }
        ]

        # Aplicar filtros
        if 'severity' in filters:
            vulnerabilities = [v for v in vulnerabilities if v['severity'] == filters['severity']]

        if 'location' in filters:
            vulnerabilities = [v for v in vulnerabilities if filters['location'] in v['location']]

        # Estadísticas
        severity_stats = {}
        for vuln in vulnerabilities:
            sev = vuln['severity']
            severity_stats[sev] = severity_stats.get(sev, 0) + 1

        return {
            'title': 'Reporte de Evaluación de Vulnerabilidades Industriales',
            'generated_at': datetime.now().isoformat(),
            'total_vulnerabilities': len(vulnerabilities),
            'severity_distribution': severity_stats,
            'vulnerabilities': vulnerabilities,
            'summary': {
                'critical_count': severity_stats.get('CRITICAL', 0),
                'high_count': severity_stats.get('HIGH', 0),
                'medium_count': severity_stats.get('MEDIUM', 0),
                'low_count': severity_stats.get('LOW', 0)
            }
        }

    async def generate_scada_logs_report(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Genera reporte de análisis de logs SCADA"""
        # Datos simulados de logs SCADA
        log_entries = [
            {
                'timestamp': '2024-09-19 08:15:23',
                'system': 'Wonderware InTouch',
                'level': 'ALARM',
                'message': 'Temperatura del reactor R-101 excede límite superior (85°C)',
                'tag': 'AI_R101_TEMP',
                'value': '87.3',
                'operator': 'OP001'
            },
            {
                'timestamp': '2024-09-19 08:20:15',
                'system': 'DeltaV DCS',
                'level': 'WARNING',
                'message': 'Presión en línea de vapor fluctuando',
                'tag': 'PI_STEAM_001',
                'value': '8.2',
                'operator': 'OP002'
            },
            {
                'timestamp': '2024-09-19 09:05:42',
                'system': 'Experion PKS',
                'level': 'INFO',
                'message': 'Batch B-2024-001 completado exitosamente',
                'tag': 'BATCH_STATUS',
                'value': 'COMPLETED',
                'operator': 'OP001'
            }
        ]

        # Estadísticas de logs
        level_stats = {}
        system_stats = {}

        for entry in log_entries:
            level = entry['level']
            system = entry['system']

            level_stats[level] = level_stats.get(level, 0) + 1
            system_stats[system] = system_stats.get(system, 0) + 1

        return {
            'title': 'Reporte de Análisis de Logs SCADA',
            'generated_at': datetime.now().isoformat(),
            'total_entries': len(log_entries),
            'level_distribution': level_stats,
            'system_distribution': system_stats,
            'log_entries': log_entries,
            'analysis': {
                'alarm_count': level_stats.get('ALARM', 0),
                'warning_count': level_stats.get('WARNING', 0),
                'info_count': level_stats.get('INFO', 0),
                'most_active_system': max(system_stats.items(), key=lambda x: x[1])[0] if system_stats else 'N/A'
            }
        }

    def _generate_pdf_report(self, data: Dict[str, Any], report_type: ReportType) -> bytes:
        """Genera reporte en formato PDF (versión simplificada)"""
        # Generar contenido de texto estructurado para PDF
        content = f"""SmartCompute Industrial - Reporte Confidencial

{data['title']}

Generado: {data['generated_at']}

"""

        if report_type == ReportType.VULNERABILITY_ASSESSMENT:
            summary = data['summary']
            content += f"""Resumen Ejecutivo:
Total de Vulnerabilidades: {data['total_vulnerabilities']}
Críticas: {summary['critical_count']}
Altas: {summary['high_count']}
Medias: {summary['medium_count']}

Vulnerabilidades Identificadas:

"""
            for vuln in data['vulnerabilities']:
                content += f"""{vuln['id']}: {vuln['title']}
Severidad: {vuln['severity']} | CVSS: {vuln['cvss_score']}
Ubicación: {vuln['location']}
Descripción: {vuln['description']}

"""

        return content.encode('utf-8')

    def _encrypt_report_content(self, content: bytes, operator_key: str) -> Tuple[bytes, bytes]:
        """Cifra el contenido del reporte con clave del operador"""
        # Derivar clave de cifrado desde la clave del operador
        salt = secrets.token_bytes(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000
        )
        encryption_key = kdf.derive(operator_key.encode('utf-8'))

        # Cifrar contenido con AES-GCM
        nonce = secrets.token_bytes(12)
        aesgcm = AESGCM(encryption_key)
        encrypted_content = aesgcm.encrypt(nonce, content, None)

        # Combinar salt, nonce y contenido cifrado
        encrypted_package = salt + nonce + encrypted_content

        return encrypted_package, salt

    def _generate_excel_report(self, data: Dict[str, Any], report_type: ReportType) -> bytes:
        """Genera reporte en formato Excel (versión simplificada como CSV estructurado)"""
        output = io.StringIO()

        # Encabezado del reporte
        output.write(f"SmartCompute Industrial - Reporte Excel\n")
        output.write(f"{data['title']}\n")
        output.write(f"Generado: {data['generated_at']}\n\n")

        if report_type == ReportType.VULNERABILITY_ASSESSMENT:
            # Hoja de estadísticas
            output.write("=== RESUMEN ESTADISTICAS ===\n")
            output.write("Severidad,Cantidad\n")
            for severity, count in data['severity_distribution'].items():
                output.write(f"{severity},{count}\n")

            output.write("\n=== VULNERABILIDADES DETALLADAS ===\n")
            output.write("ID,Título,Severidad,CVSS,Ubicación,Asset Afectado,Estado,Descripción\n")

            for vuln in data['vulnerabilities']:
                # Escapar comas en la descripción
                desc_clean = vuln['description'].replace(',', ';')
                output.write(f"{vuln['id']},{vuln['title']},{vuln['severity']},{vuln['cvss_score']},{vuln['location']},{vuln['affected_asset']},{vuln['status']},{desc_clean}\n")

        elif report_type == ReportType.SCADA_LOGS_ANALYSIS:
            # Hoja de estadísticas de logs
            output.write("=== ESTADISTICAS LOGS ===\n")
            output.write("Nivel,Cantidad\n")
            for level, count in data['level_distribution'].items():
                output.write(f"{level},{count}\n")

            output.write("\n=== LOGS SCADA DETALLADOS ===\n")
            output.write("Timestamp,Sistema,Nivel,Mensaje,Tag,Valor,Operador\n")

            for entry in data['log_entries']:
                # Escapar comas en el mensaje
                msg_clean = entry['message'].replace(',', ';')
                output.write(f"{entry['timestamp']},{entry['system']},{entry['level']},{msg_clean},{entry['tag']},{entry['value']},{entry['operator']}\n")

        return output.getvalue().encode('utf-8')

    def _generate_csv_report(self, data: Dict[str, Any], report_type: ReportType) -> bytes:
        """Genera reporte en formato CSV"""
        output = io.StringIO()

        if report_type == ReportType.VULNERABILITY_ASSESSMENT:
            writer = csv.DictWriter(output, fieldnames=[
                'id', 'title', 'severity', 'cvss_score', 'location',
                'affected_asset', 'description', 'status'
            ])
            writer.writeheader()

            for vuln in data['vulnerabilities']:
                writer.writerow({
                    'id': vuln['id'],
                    'title': vuln['title'],
                    'severity': vuln['severity'],
                    'cvss_score': vuln['cvss_score'],
                    'location': vuln['location'],
                    'affected_asset': vuln['affected_asset'],
                    'description': vuln['description'],
                    'status': vuln['status']
                })

        elif report_type == ReportType.SCADA_LOGS_ANALYSIS:
            writer = csv.DictWriter(output, fieldnames=[
                'timestamp', 'system', 'level', 'message', 'tag', 'value', 'operator'
            ])
            writer.writeheader()

            for entry in data['log_entries']:
                writer.writerow(entry)

        return output.getvalue().encode('utf-8')

    def _generate_json_report(self, data: Dict[str, Any], report_type: ReportType) -> bytes:
        """Genera reporte en formato JSON"""
        return json.dumps(data, indent=2, ensure_ascii=False).encode('utf-8')

    async def export_report(self, request: ExportRequest, user_ip: str = None) -> Optional[str]:
        """Exporta reporte con autorización granular"""
        try:
            # Verificar permisos
            has_permission = await self.check_permissions(
                request.user_id, request.report_type, request.format, user_ip
            )

            if not has_permission:
                logger.warning(f"Permiso denegado para exportación: {request.user_id} - {request.report_type.value}")
                return None

            # Verificar si requiere aprobación
            if await self._requires_approval(request.user_id, request.report_type):
                self.pending_approvals[request.request_id] = request
                logger.info(f"Solicitud {request.request_id} pendiente de aprobación")
                return "PENDING_APPROVAL"

            # Generar datos del reporte
            if request.report_type == ReportType.VULNERABILITY_ASSESSMENT:
                report_data = await self.generate_vulnerability_report(request.filters)
            elif request.report_type == ReportType.SCADA_LOGS_ANALYSIS:
                report_data = await self.generate_scada_logs_report(request.filters)
            else:
                logger.error(f"Tipo de reporte no soportado: {request.report_type}")
                return None

            # Generar archivo según formato
            if request.format == ReportFormat.PDF:
                content = self._generate_pdf_report(report_data, request.report_type)
            elif request.format == ReportFormat.EXCEL:
                content = self._generate_excel_report(report_data, request.report_type)
            elif request.format == ReportFormat.CSV:
                content = self._generate_csv_report(report_data, request.report_type)
            elif request.format == ReportFormat.JSON:
                content = self._generate_json_report(report_data, request.report_type)
            else:
                logger.error(f"Formato no soportado: {request.format}")
                return None

            # Aplicar marca de agua si es requerida
            watermark_required = await self._check_watermark_required(request.user_id, request.report_type)
            if watermark_required:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                content = self._apply_watermark(content, request.format, request.user_id, timestamp)

            # CIFRAR SIEMPRE el contenido con la clave del operador
            encrypted_content, salt = self._encrypt_report_content(content, request.operator_encryption_key)

            # Crear metadata de cifrado
            encryption_info = {
                'encrypted': True,
                'algorithm': 'AES-GCM',
                'key_derivation': 'PBKDF2-SHA256',
                'iterations': 100000,
                'salt': salt.hex(),
                'encrypted_by': request.user_id,
                'encrypted_at': datetime.now().isoformat()
            }

            # Calcular checksum del contenido original y cifrado
            original_checksum = hashlib.sha256(content).hexdigest()
            encrypted_checksum = hashlib.sha256(encrypted_content).hexdigest()

            # Guardar archivo cifrado
            file_extension = request.format.value
            filename = f"report_{request.report_type.value}_{request.request_id}.{file_extension}.encrypted"
            file_path = f"/home/gatux/smartcompute/reports/{filename}"

            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Escribir archivo cifrado con metadata
            with open(file_path, 'wb') as f:
                # Escribir metadata de cifrado como header
                metadata_json = json.dumps(encryption_info).encode('utf-8')
                metadata_size = len(metadata_json)

                # Estructura: [4 bytes tamaño metadata][metadata JSON][contenido cifrado]
                f.write(metadata_size.to_bytes(4, byteorder='big'))
                f.write(metadata_json)
                f.write(encrypted_content)

            # Crear archivo de instrucciones de descifrado
            instructions_file = f"{file_path}.instructions.txt"
            with open(instructions_file, 'w', encoding='utf-8') as f:
                f.write(f"""SmartCompute Industrial - Instrucciones de Descifrado
================================================================

Archivo: {filename}
Formato Original: {request.format.value.upper()}
Cifrado por: {request.user_id}
Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

IMPORTANTE: Este archivo está CIFRADO con la clave proporcionada por el operador.

Para descifrar:
1. Use la clave de descifrado que proporcionó durante la exportación
2. Algoritmo: AES-GCM con PBKDF2-SHA256
3. Iteraciones: 100,000
4. Salt incluido en el archivo

Checksums de verificación:
- Contenido original: {original_checksum}
- Contenido cifrado: {encrypted_checksum}

ADVERTENCIA: Mantenga la clave de descifrado en lugar seguro.
Sin la clave, el archivo NO PUEDE ser recuperado.
""")

            # Guardar metadatos incluyendo información de cifrado
            metadata = ReportMetadata(
                report_id=request.request_id,
                report_type=request.report_type,
                format=request.format,
                created_by=request.user_id,
                created_at=datetime.now(),
                file_size=len(encrypted_content),  # Tamaño del archivo cifrado
                checksum=encrypted_checksum,       # Checksum del archivo cifrado
                sensitivity=DataSensitivity.HIGHLY_CONFIDENTIAL,  # Elevado por cifrado
                access_level=AccessLevel.SECRET,   # Elevado por cifrado
                export_restrictions={'encrypted': True, 'original_checksum': original_checksum}
            )

            await self._save_report_metadata(metadata, file_path)

            # Registrar acceso en auditoría
            await self._log_access_audit(request.user_id, request.request_id, "EXPORT", user_ip, True)

            logger.info(f"Reporte CIFRADO exportado exitosamente: {filename}")
            logger.info(f"Instrucciones de descifrado: {instructions_file}")
            logger.info(f"IMPORTANTE: Archivo cifrado con clave del operador - Sin clave NO se puede recuperar")
            return file_path

        except Exception as e:
            logger.error(f"Error exportando reporte: {str(e)}")
            await self._log_access_audit(request.user_id, request.request_id, "EXPORT_ERROR", user_ip, False)
            return None

    async def _requires_approval(self, user_id: str, report_type: ReportType) -> bool:
        """Verifica si la solicitud requiere aprobación"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT require_approval FROM report_permissions
                WHERE user_id = ? AND report_type = ?
            ''', (user_id, report_type.value))

            result = cursor.fetchone()
            return result[0] if result else True

    async def _check_watermark_required(self, user_id: str, report_type: ReportType) -> bool:
        """Verifica si se requiere marca de agua"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT watermark_required FROM report_permissions
                WHERE user_id = ? AND report_type = ?
            ''', (user_id, report_type.value))

            result = cursor.fetchone()
            return result[0] if result else True

    async def _save_report_metadata(self, metadata: ReportMetadata, file_path: str):
        """Guarda metadatos del reporte"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO report_metadata
                (report_id, report_type, format, created_by, created_at, file_size,
                 checksum, sensitivity, access_level, file_path, audit_trail)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metadata.report_id, metadata.report_type.value, metadata.format.value,
                metadata.created_by, metadata.created_at, metadata.file_size,
                metadata.checksum, metadata.sensitivity.value, metadata.access_level.value,
                file_path, json.dumps([])
            ))

            conn.commit()

    async def _log_access_audit(self, user_id: str, report_id: str, action: str,
                               ip_address: str, success: bool):
        """Registra auditoría de acceso"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO access_audit
                (user_id, report_id, action, ip_address, success)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, report_id, action, ip_address, success))

            conn.commit()

    async def approve_export_request(self, request_id: str, approver_id: str) -> bool:
        """Aprueba solicitud de exportación pendiente"""
        if request_id not in self.pending_approvals:
            logger.warning(f"Solicitud {request_id} no encontrada en pendientes")
            return False

        request = self.pending_approvals[request_id]
        request.approved_by = approver_id
        request.approved_at = datetime.now()

        # Actualizar base de datos
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE export_requests
                SET status = 'approved', approved_by = ?, approved_at = ?
                WHERE request_id = ?
            ''', (approver_id, request.approved_at, request_id))

            conn.commit()

        # Procesar exportación
        file_path = await self.export_report(request)

        # Remover de pendientes
        del self.pending_approvals[request_id]

        logger.info(f"Solicitud {request_id} aprobada por {approver_id}")
        return file_path is not None

    async def get_export_statistics(self, user_id: str = None) -> Dict[str, Any]:
        """Obtiene estadísticas de exportaciones"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Estadísticas generales
            stats = {}

            # Total de reportes generados
            cursor.execute('SELECT COUNT(*) FROM report_metadata')
            stats['total_reports'] = cursor.fetchone()[0]

            # Reportes por tipo
            cursor.execute('''
                SELECT report_type, COUNT(*)
                FROM report_metadata
                GROUP BY report_type
            ''')
            stats['reports_by_type'] = dict(cursor.fetchall())

            # Reportes por formato
            cursor.execute('''
                SELECT format, COUNT(*)
                FROM report_metadata
                GROUP BY format
            ''')
            stats['reports_by_format'] = dict(cursor.fetchall())

            # Exportaciones por usuario (si se especifica)
            if user_id:
                cursor.execute('''
                    SELECT COUNT(*) FROM report_metadata
                    WHERE created_by = ?
                ''', (user_id,))
                stats['user_reports'] = cursor.fetchone()[0]

                cursor.execute('''
                    SELECT COUNT(*) FROM access_audit
                    WHERE user_id = ? AND DATE(timestamp) = DATE('now')
                ''', (user_id,))
                stats['user_daily_exports'] = cursor.fetchone()[0]

            # Solicitudes pendientes
            stats['pending_approvals'] = len(self.pending_approvals)

            return stats

async def main():
    """Función principal para demostración del sistema de exportación de reportes"""
    print("=== SmartCompute Industrial - Sistema de Exportación de Reportes ===")

    exporter = IndustrialReportsExporter()

    # Ejemplo de solicitud de exportación de vulnerabilidades con cifrado
    operator_key = input("Ingrese clave de cifrado para reporte de vulnerabilidades: ") or "ClaveSegura2024!"

    vuln_request = ExportRequest(
        request_id=f"REQ-{secrets.token_hex(6).upper()}",
        user_id="admin_industrial",
        report_type=ReportType.VULNERABILITY_ASSESSMENT,
        format=ReportFormat.PDF,
        operator_encryption_key=operator_key,
        filters={'severity': 'CRITICAL'}
    )

    print(f"\n1. Exportando reporte de vulnerabilidades...")
    vuln_report_path = await exporter.export_report(vuln_request, "192.168.1.100")

    if vuln_report_path and vuln_report_path != "PENDING_APPROVAL":
        print(f"✓ Reporte de vulnerabilidades generado: {vuln_report_path}")
    else:
        print("✗ Error generando reporte de vulnerabilidades")

    # Ejemplo de solicitud de exportación de logs SCADA con cifrado
    scada_key = input("Ingrese clave de cifrado para reporte SCADA: ") or "ScadaSecure2024!"

    scada_request = ExportRequest(
        request_id=f"REQ-{secrets.token_hex(6).upper()}",
        user_id="security_supervisor",
        report_type=ReportType.SCADA_LOGS_ANALYSIS,
        format=ReportFormat.EXCEL,
        operator_encryption_key=scada_key,
        filters={}
    )

    print(f"\n2. Exportando reporte de logs SCADA...")
    scada_report_path = await exporter.export_report(scada_request, "192.168.1.101")

    if scada_report_path and scada_report_path != "PENDING_APPROVAL":
        print(f"✓ Reporte de logs SCADA generado: {scada_report_path}")
    else:
        print("✗ Error generando reporte de logs SCADA")

    # Obtener estadísticas
    print(f"\n3. Estadísticas del sistema...")
    stats = await exporter.get_export_statistics()
    print(f"Total de reportes: {stats['total_reports']}")
    print(f"Reportes por tipo: {stats['reports_by_type']}")
    print(f"Reportes por formato: {stats['reports_by_format']}")
    print(f"Solicitudes pendientes: {stats['pending_approvals']}")

    print(f"\n✓ Sistema de exportación de reportes inicializado correctamente")
    print(f"  - Base de datos: /home/gatux/smartcompute/data/reports.db")
    print(f"  - Directorio de reportes: /home/gatux/smartcompute/reports/")
    print(f"  - Logs: /home/gatux/smartcompute/logs/industrial_reports_exporter.log")

if __name__ == "__main__":
    asyncio.run(main())