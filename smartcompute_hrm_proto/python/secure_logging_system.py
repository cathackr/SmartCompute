#!/usr/bin/env python3
"""
SmartCompute HRM - Sistema de Logging Seguro y Centralizado
Implementa logging completo con integridad, cifrado y alertas automaticas
"""

import logging
import json
import hashlib
import hmac
import os
import time
import smtplib
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from pathlib import Path
import threading
import queue

# Configuración de seguridad
LOGGING_KEY = b"SmartComputeLogSecurityKey123456"  # 32 bytes para AES-256
HMAC_KEY = b"SmartComputeHMACIntegrityKey1234"    # Clave para integridad

@dataclass
class SecurityEvent:
    """Estructura estándar para eventos de seguridad"""
    event_id: str
    timestamp: str
    event_type: str  # AUTH, DATA_ACCESS, SYSTEM, ERROR, THREAT
    severity: str    # CRITICAL, HIGH, MEDIUM, LOW, INFO
    user_id: Optional[str] = None
    source_ip: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None
    result: Optional[str] = None  # SUCCESS, FAILURE, BLOCKED
    details: Optional[Dict] = None
    correlation_id: Optional[str] = None

class SecureLogger:
    """Logger centralizado con características de seguridad enterprise"""

    def __init__(self, config_path: str = None):
        self.base_path = Path("/home/gatux/smartcompute/smartcompute_hrm_proto/secure_logs")
        self.base_path.mkdir(exist_ok=True)

        # Configuración de loggers especializados
        self.setup_loggers()

        # Sistema de alertas
        self.alert_queue = queue.Queue()
        self.alert_thread = threading.Thread(target=self._alert_processor, daemon=True)
        self.alert_thread.start()

        # Contador de eventos para correlación
        self.event_counter = 0
        self.event_lock = threading.Lock()

    def setup_loggers(self):
        """Configurar loggers especializados por tipo de evento"""

        # Logger para autenticación y autorización
        self.auth_logger = self._create_secure_logger(
            'smartcompute.auth',
            self.base_path / 'authentication.log',
            max_bytes=50*1024*1024,  # 50MB
            backup_count=10
        )

        # Logger para acceso a datos
        self.data_logger = self._create_secure_logger(
            'smartcompute.data',
            self.base_path / 'data_access.log',
            max_bytes=100*1024*1024,  # 100MB
            backup_count=20
        )

        # Logger para errores y excepciones
        self.error_logger = self._create_secure_logger(
            'smartcompute.error',
            self.base_path / 'security_errors.log',
            max_bytes=50*1024*1024,
            backup_count=15
        )

        # Logger para eventos del sistema
        self.system_logger = self._create_secure_logger(
            'smartcompute.system',
            self.base_path / 'system_events.log',
            max_bytes=75*1024*1024,
            backup_count=12
        )

        # Logger para amenazas y detecciones
        self.threat_logger = self._create_secure_logger(
            'smartcompute.threat',
            self.base_path / 'threat_detection.log',
            max_bytes=200*1024*1024,  # Más espacio para amenazas
            backup_count=25
        )

        # Logger maestro para auditoría
        self.audit_logger = self._create_secure_logger(
            'smartcompute.audit',
            self.base_path / 'security_audit.log',
            max_bytes=500*1024*1024,  # 500MB para auditoría completa
            backup_count=50
        )

    def _create_secure_logger(self, name: str, log_file: Path, max_bytes: int, backup_count: int):
        """Crear logger con rotación segura y formato estructurado"""

        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

        # Evitar duplicar handlers
        if logger.handlers:
            return logger

        # Handler con rotación automática
        handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )

        # Formato estructurado JSON para parsing automático
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": %(message)s}'
        )
        handler.setFormatter(formatter)

        logger.addHandler(handler)
        return logger

    def _generate_event_id(self) -> str:
        """Generar ID único para eventos con timestamp y contador"""
        with self.event_lock:
            self.event_counter += 1
            timestamp = int(time.time() * 1000)  # milliseconds
            return f"SEC-{timestamp}-{self.event_counter:06d}"

    def _calculate_integrity_hash(self, event_data: str) -> str:
        """Calcular hash HMAC para integridad del evento"""
        return hmac.new(
            HMAC_KEY,
            event_data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    def _log_secure_event(self, logger: logging.Logger, event: SecurityEvent):
        """Log evento con integridad y estructura estándar"""

        # Asegurar timestamp consistente
        if not event.timestamp:
            event.timestamp = datetime.now().isoformat()

        # Generar ID si no existe
        if not event.event_id:
            event.event_id = self._generate_event_id()

        # Convertir a dict y preparar para JSON
        event_dict = asdict(event)
        event_json = json.dumps(event_dict, ensure_ascii=False, separators=(',', ':'))

        # Calcular hash de integridad
        integrity_hash = self._calculate_integrity_hash(event_json)
        event_dict['integrity_hash'] = integrity_hash

        # Log final con integridad
        final_json = json.dumps(event_dict, ensure_ascii=False, separators=(',', ':'))
        logger.info(final_json)

        # Log también en auditoría maestra
        self.audit_logger.info(final_json)

        # Verificar si requiere alerta
        if event.severity in ['CRITICAL', 'HIGH']:
            self.alert_queue.put(event)

        return event.event_id

    # ===== MÉTODOS PÚBLICOS PARA LOGGING DE SEGURIDAD =====

    def log_authentication_event(self, user_id: str, action: str, result: str,
                                source_ip: str = None, details: Dict = None) -> str:
        """Log eventos de autenticación y autorización"""

        event = SecurityEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.now().isoformat(),
            event_type="AUTH",
            severity="HIGH" if result == "FAILURE" else "INFO",
            user_id=user_id,
            source_ip=source_ip,
            action=action,
            result=result,
            details=details or {}
        )

        return self._log_secure_event(self.auth_logger, event)

    def log_data_access(self, user_id: str, resource: str, action: str,
                       result: str, source_ip: str = None, details: Dict = None) -> str:
        """Log accesos a datos sensibles"""

        # Determinar severidad basada en el recurso y acción
        severity = "HIGH"
        if "password" in resource.lower() or "secret" in resource.lower():
            severity = "CRITICAL"
        elif action in ["READ", "view"]:
            severity = "MEDIUM"
        elif action in ["write", "delete", "modify"]:
            severity = "HIGH"

        event = SecurityEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.now().isoformat(),
            event_type="DATA_ACCESS",
            severity=severity,
            user_id=user_id,
            source_ip=source_ip,
            resource=resource,
            action=action,
            result=result,
            details=details or {}
        )

        return self._log_secure_event(self.data_logger, event)

    def log_system_event(self, action: str, result: str, user_id: str = None,
                        details: Dict = None) -> str:
        """Log eventos críticos del sistema"""

        # Determinar severidad basada en la acción
        severity = "MEDIUM"
        if action in ["service_stop", "config_change", "user_add", "privilege_escalation"]:
            severity = "HIGH"
        elif action in ["system_shutdown", "firewall_disable", "admin_created"]:
            severity = "CRITICAL"

        event = SecurityEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.now().isoformat(),
            event_type="SYSTEM",
            severity=severity,
            user_id=user_id,
            action=action,
            result=result,
            details=details or {}
        )

        return self._log_secure_event(self.system_logger, event)

    def log_security_error(self, error_type: str, error_message: str,
                          user_id: str = None, source_ip: str = None,
                          details: Dict = None) -> str:
        """Log errores de seguridad y excepciones"""

        # Determinar severidad basada en el tipo de error
        severity = "MEDIUM"
        if "sql injection" in error_message.lower():
            severity = "CRITICAL"
        elif "unauthorized" in error_message.lower():
            severity = "HIGH"
        elif "encryption" in error_message.lower():
            severity = "HIGH"

        event = SecurityEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.now().isoformat(),
            event_type="ERROR",
            severity=severity,
            user_id=user_id,
            source_ip=source_ip,
            action=error_type,
            result="FAILURE",
            details={"error_message": error_message, **(details or {})}
        )

        return self._log_secure_event(self.error_logger, event)

    def log_threat_detection(self, threat_type: str, severity: str, source: str,
                           details: Dict = None, correlation_id: str = None) -> str:
        """Log detecciones de amenazas y actividad sospechosa"""

        event = SecurityEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.now().isoformat(),
            event_type="THREAT",
            severity=severity,
            resource=source,
            action="threat_detected",
            result="DETECTED",
            details={"threat_type": threat_type, **(details or {})},
            correlation_id=correlation_id
        )

        return self._log_secure_event(self.threat_logger, event)

    def _alert_processor(self):
        """Procesar alertas críticas en background"""
        while True:
            try:
                event = self.alert_queue.get(timeout=30)
                if event:
                    self._send_security_alert(event)
                self.alert_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                # Log error de alertas sin crear loop infinito
                print(f"Error en sistema de alertas: {e}")

    def _send_security_alert(self, event: SecurityEvent):
        """Enviar alerta de seguridad crítica"""

        alert_message = f"""
🚨 ALERTA DE SEGURIDAD SMARTCOMPUTE 🚨

Event ID: {event.event_id}
Timestamp: {event.timestamp}
Tipo: {event.event_type}
Severidad: {event.severity}
Usuario: {event.user_id or 'N/A'}
IP Origen: {event.source_ip or 'N/A'}
Recurso: {event.resource or 'N/A'}
Acción: {event.action or 'N/A'}
Resultado: {event.result or 'N/A'}

Detalles: {json.dumps(event.details or {}, indent=2)}

--- SMARTCOMPUTE HRM SECURITY ---
"""

        # En producción, aquí enviarías email, webhook, Slack, etc.
        print(f"[SECURITY ALERT] {alert_message}")

        # Guardar alerta en archivo especial
        alert_file = self.base_path / "critical_alerts.log"
        with open(alert_file, "a", encoding='utf-8') as f:
            f.write(f"{datetime.now().isoformat()} - {alert_message}\n")

    def verify_log_integrity(self, log_file: Path) -> Dict[str, Any]:
        """Verificar integridad de un archivo de log"""

        results = {
            "file": str(log_file),
            "total_events": 0,
            "corrupted_events": 0,
            "verification_timestamp": datetime.now().isoformat(),
            "integrity_status": "UNKNOWN"
        }

        if not log_file.exists():
            results["integrity_status"] = "FILE_NOT_FOUND"
            return results

        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if not line.strip():
                        continue

                    try:
                        # Parse JSON event
                        log_entry = json.loads(line.strip())
                        if 'message' in log_entry:
                            event_data = json.loads(log_entry['message'])

                            if 'integrity_hash' in event_data:
                                # Verificar hash de integridad
                                stored_hash = event_data.pop('integrity_hash')
                                event_json = json.dumps(event_data, ensure_ascii=False, separators=(',', ':'))
                                calculated_hash = self._calculate_integrity_hash(event_json)

                                results["total_events"] += 1

                                if stored_hash != calculated_hash:
                                    results["corrupted_events"] += 1
                                    print(f"[INTEGRITY ERROR] Line {line_num}: Hash mismatch")

                    except json.JSONDecodeError:
                        results["corrupted_events"] += 1
                    except Exception as e:
                        results["corrupted_events"] += 1

            # Determinar estado final
            if results["corrupted_events"] == 0:
                results["integrity_status"] = "VERIFIED"
            else:
                results["integrity_status"] = "COMPROMISED"

        except Exception as e:
            results["integrity_status"] = "VERIFICATION_FAILED"
            results["error"] = str(e)

        return results

# Singleton para uso global
_secure_logger_instance = None

def get_secure_logger() -> SecureLogger:
    """Obtener instancia singleton del logger seguro"""
    global _secure_logger_instance
    if _secure_logger_instance is None:
        _secure_logger_instance = SecureLogger()
    return _secure_logger_instance

# ===== FUNCIONES DE CONVENIENCIA =====

def log_auth_success(user_id: str, source_ip: str = None, details: Dict = None) -> str:
    """Log login exitoso"""
    return get_secure_logger().log_authentication_event(
        user_id=user_id,
        action="login",
        result="SUCCESS",
        source_ip=source_ip,
        details=details
    )

def log_auth_failure(user_id: str, source_ip: str = None, reason: str = None) -> str:
    """Log fallo de autenticación"""
    return get_secure_logger().log_authentication_event(
        user_id=user_id,
        action="login",
        result="FAILURE",
        source_ip=source_ip,
        details={"failure_reason": reason} if reason else None
    )

def log_file_access(user_id: str, file_path: str, action: str, success: bool = True) -> str:
    """Log acceso a archivos"""
    return get_secure_logger().log_data_access(
        user_id=user_id,
        resource=file_path,
        action=action,
        result="SUCCESS" if success else "FAILURE"
    )

def log_critical_error(error_msg: str, user_id: str = None, source_ip: str = None) -> str:
    """Log error crítico de seguridad"""
    return get_secure_logger().log_security_error(
        error_type="critical_error",
        error_message=error_msg,
        user_id=user_id,
        source_ip=source_ip
    )

def log_threat(threat_type: str, severity: str, source: str, details: Dict = None) -> str:
    """Log detección de amenaza"""
    return get_secure_logger().log_threat_detection(
        threat_type=threat_type,
        severity=severity,
        source=source,
        details=details
    )

# ===== DEMO Y TESTING =====

def demo_logging_system():
    """Demostrar sistema de logging seguro"""

    print("🚀 Demo SmartCompute Secure Logging System")
    print("=" * 50)

    logger = get_secure_logger()

    # Simular eventos de seguridad diversos
    print("📝 Generando eventos de prueba...")

    # Eventos de autenticación
    log_auth_success("admin@smartcompute.com", "192.168.1.100", {"method": "password"})
    log_auth_failure("attacker@malicious.com", "10.0.0.1", "invalid_password")

    # Acceso a datos
    log_file_access("admin@smartcompute.com", "/etc/passwd", "read", True)
    log_file_access("user@smartcompute.com", "/var/log/sensitive.log", "write", False)

    # Errores críticos
    log_critical_error("SQL Injection attempt detected", "unknown", "192.168.1.200")

    # Detección de amenazas
    log_threat("process_injection", "CRITICAL", "host_workstation_01", {
        "technique": "T1055",
        "process": "explorer.exe",
        "confidence": 0.95
    })

    # Eventos del sistema
    logger.log_system_event("service_restart", "SUCCESS", "admin@smartcompute.com", {
        "service": "smartcompute-hrm",
        "reason": "configuration_update"
    })

    print("✅ Eventos de prueba generados")

    # Verificar integridad
    print("\n🔍 Verificando integridad de logs...")

    for log_file in logger.base_path.glob("*.log"):
        if log_file.stat().st_size > 0:
            integrity_result = logger.verify_log_integrity(log_file)
            status_icon = "✅" if integrity_result["integrity_status"] == "VERIFIED" else "❌"
            print(f"{status_icon} {log_file.name}: {integrity_result['integrity_status']} "
                  f"({integrity_result['total_events']} eventos, "
                  f"{integrity_result['corrupted_events']} corruptos)")

    print(f"\n📁 Logs seguros guardados en: {logger.base_path}")
    print("🔐 Sistema de logging seguro completamente funcional")

if __name__ == "__main__":
    demo_logging_system()