#!/usr/bin/env python3
"""
SmartCompute Security Monitor
Sistema de monitoreo de seguridad en tiempo real
"""

import os
import sys
import time
import json
import hashlib
import datetime
import logging
import psutil
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from threading import Thread
import subprocess

@dataclass
class SecurityEvent:
    """Evento de seguridad detectado"""
    timestamp: datetime.datetime
    event_type: str
    severity: str  # low, medium, high, critical
    description: str
    source_ip: Optional[str] = None
    affected_service: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class SmartComputeSecurityMonitor:
    """Monitor de seguridad para SmartCompute"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.events: List[SecurityEvent] = []
        self.is_monitoring = False
        self.known_file_hashes = {}
        self.last_process_check = datetime.datetime.now()
        
        # Configuración desde variables de entorno
        self.alert_webhook = os.getenv("SECURITY_WEBHOOK_URL", "")
        self.slack_token = os.getenv("SLACK_BOT_TOKEN", "")
        self.email_alerts = os.getenv("SECURITY_EMAIL_ALERTS", "").split(",")
        
        # Servicios a monitorear
        self.monitored_services = {
            "smartcompute_dashboard": {"port": 8000, "path": "/health"},
            "smartcompute_unified": {"port": 8001, "path": "/health"},  
            "smartcompute_network": {"port": 8002, "path": "/api/health"},
            "smartcompute_payment": {"port": 8003, "path": "/health"}
        }
        
        # Archivos críticos a monitorear
        self.critical_files = [
            ".env",
            "secret.key", 
            "smartcompute_industrial/secret.key",
            "SmartCompute-Industrial/payments/payment_integration.py",
            "nginx/smartcompute-secure.conf"
        ]
        
        self.logger.info("🔒 SmartCompute Security Monitor iniciado")

    def _setup_logging(self) -> logging.Logger:
        """Configurar logging de seguridad"""
        # Crear directorio de logs de seguridad
        log_dir = Path("security/logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar logger
        logger = logging.getLogger("SmartCompute-Security")
        logger.setLevel(logging.INFO)
        
        # Handler para archivo
        file_handler = logging.FileHandler(log_dir / "security_events.log")
        file_handler.setLevel(logging.INFO)
        
        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger

    def calculate_file_hash(self, file_path: str) -> str:
        """Calcular hash SHA256 de archivo"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except (FileNotFoundError, PermissionError):
            return ""

    def check_file_integrity(self):
        """Verificar integridad de archivos críticos"""
        for file_path in self.critical_files:
            if os.path.exists(file_path):
                current_hash = self.calculate_file_hash(file_path)
                
                if file_path not in self.known_file_hashes:
                    # Primera vez - establecer baseline
                    self.known_file_hashes[file_path] = current_hash
                    self.logger.info(f"🔐 Baseline establecido para {file_path}")
                    
                elif self.known_file_hashes[file_path] != current_hash:
                    # ¡Archivo modificado!
                    event = SecurityEvent(
                        timestamp=datetime.datetime.now(),
                        event_type="file_integrity_violation",
                        severity="high",
                        description=f"Archivo crítico modificado: {file_path}",
                        details={"file_path": file_path, "old_hash": self.known_file_hashes[file_path], "new_hash": current_hash}
                    )
                    self._handle_security_event(event)
                    self.known_file_hashes[file_path] = current_hash

    def check_service_health(self):
        """Verificar salud de servicios SmartCompute"""
        for service_name, config in self.monitored_services.items():
            try:
                url = f"http://127.0.0.1:{config['port']}{config['path']}"
                response = requests.get(url, timeout=5)
                
                if response.status_code != 200:
                    event = SecurityEvent(
                        timestamp=datetime.datetime.now(),
                        event_type="service_health_failure", 
                        severity="medium",
                        description=f"Servicio {service_name} reporta fallo (HTTP {response.status_code})",
                        affected_service=service_name,
                        details={"status_code": response.status_code, "url": url}
                    )
                    self._handle_security_event(event)
                    
            except requests.exceptions.RequestException as e:
                event = SecurityEvent(
                    timestamp=datetime.datetime.now(),
                    event_type="service_unavailable",
                    severity="high", 
                    description=f"Servicio {service_name} no disponible",
                    affected_service=service_name,
                    details={"error": str(e)}
                )
                self._handle_security_event(event)

    def check_suspicious_processes(self):
        """Detectar procesos sospechosos"""
        suspicious_keywords = ['xmr', 'mining', 'miner', 'cryptonight', 'stratum']
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent']):
            try:
                proc_info = proc.info
                cmdline_str = ' '.join(proc_info.get('cmdline', []))
                
                # Verificar keywords sospechosos
                for keyword in suspicious_keywords:
                    if keyword in proc_info['name'].lower() or keyword in cmdline_str.lower():
                        event = SecurityEvent(
                            timestamp=datetime.datetime.now(),
                            event_type="suspicious_process",
                            severity="critical",
                            description=f"Proceso sospechoso detectado: {proc_info['name']}",
                            details={"pid": proc_info['pid'], "cmdline": cmdline_str, "keyword": keyword}
                        )
                        self._handle_security_event(event)
                        
                # Verificar alto uso de CPU
                if proc_info.get('cpu_percent', 0) > 90:
                    event = SecurityEvent(
                        timestamp=datetime.datetime.now(),
                        event_type="high_cpu_usage",
                        severity="medium",
                        description=f"Proceso con alto uso de CPU: {proc_info['name']} ({proc_info['cpu_percent']}%)",
                        details={"pid": proc_info['pid'], "cpu_percent": proc_info['cpu_percent']}
                    )
                    self._handle_security_event(event)
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    def check_network_connections(self):
        """Verificar conexiones de red sospechosas"""
        try:
            connections = psutil.net_connections(kind='inet')
            
            for conn in connections:
                # Verificar conexiones en puertos críticos desde IPs externas
                if conn.laddr and conn.laddr.port in [8000, 8001, 8002, 8003]:
                    if conn.raddr and not conn.raddr.ip.startswith('127.0.0.'):
                        event = SecurityEvent(
                            timestamp=datetime.datetime.now(),
                            event_type="external_connection_to_internal_port",
                            severity="critical",
                            description=f"Conexión externa a puerto interno {conn.laddr.port}",
                            source_ip=conn.raddr.ip,
                            details={"local_port": conn.laddr.port, "remote_ip": conn.raddr.ip, "remote_port": conn.raddr.port}
                        )
                        self._handle_security_event(event)
                        
        except psutil.AccessDenied:
            pass

    def _handle_security_event(self, event: SecurityEvent):
        """Manejar evento de seguridad detectado"""
        self.events.append(event)
        
        # Log del evento
        self.logger.warning(f"🚨 {event.severity.upper()}: {event.description}")
        
        # Enviar alertas según severidad
        if event.severity in ['high', 'critical']:
            self._send_alert(event)

    def _send_alert(self, event: SecurityEvent):
        """Enviar alerta de seguridad crítica"""
        alert_message = f"""
🚨 ALERTA DE SEGURIDAD SMARTCOMPUTE

Severidad: {event.severity.upper()}
Evento: {event.event_type}
Descripción: {event.description}
Timestamp: {event.timestamp}
Servicio: {event.affected_service or 'N/A'}
IP Origen: {event.source_ip or 'N/A'}

Detalles: {json.dumps(event.details, indent=2) if event.details else 'N/A'}
        """.strip()
        
        # Webhook
        if self.alert_webhook:
            try:
                requests.post(self.alert_webhook, json={"text": alert_message}, timeout=10)
            except Exception as e:
                self.logger.error(f"Error enviando webhook: {e}")
        
        # Log crítico
        self.logger.critical(alert_message)

    def start_monitoring(self):
        """Iniciar monitoreo continuo"""
        self.is_monitoring = True
        self.logger.info("🔒 Iniciando monitoreo de seguridad...")
        
        while self.is_monitoring:
            try:
                # Verificaciones cada 30 segundos
                self.check_file_integrity()
                self.check_service_health()
                self.check_network_connections()
                
                # Verificaciones cada 2 minutos
                if (datetime.datetime.now() - self.last_process_check).seconds >= 120:
                    self.check_suspicious_processes()
                    self.last_process_check = datetime.datetime.now()
                
                time.sleep(30)
                
            except KeyboardInterrupt:
                self.logger.info("🛑 Monitoreo detenido por usuario")
                break
            except Exception as e:
                self.logger.error(f"Error en monitoreo: {e}")
                time.sleep(60)  # Espera más tiempo en caso de error

    def stop_monitoring(self):
        """Detener monitoreo"""
        self.is_monitoring = False
        
    def get_security_report(self) -> Dict[str, Any]:
        """Generar reporte de seguridad"""
        now = datetime.datetime.now()
        last_24h = now - datetime.timedelta(hours=24)
        
        recent_events = [e for e in self.events if e.timestamp >= last_24h]
        
        return {
            "report_timestamp": now.isoformat(),
            "monitoring_active": self.is_monitoring,
            "total_events": len(self.events),
            "events_last_24h": len(recent_events),
            "events_by_severity": {
                "critical": len([e for e in recent_events if e.severity == "critical"]),
                "high": len([e for e in recent_events if e.severity == "high"]),
                "medium": len([e for e in recent_events if e.severity == "medium"]),
                "low": len([e for e in recent_events if e.severity == "low"])
            },
            "services_monitored": list(self.monitored_services.keys()),
            "files_monitored": len(self.critical_files),
            "recent_events": [
                {
                    "timestamp": e.timestamp.isoformat(),
                    "type": e.event_type,
                    "severity": e.severity,
                    "description": e.description
                }
                for e in recent_events[-10:]  # Últimos 10 eventos
            ]
        }

def main():
    """Función principal"""
    if len(sys.argv) > 1 and sys.argv[1] == "--report":
        # Generar reporte
        monitor = SmartComputeSecurityMonitor()
        report = monitor.get_security_report()
        print(json.dumps(report, indent=2))
        return
        
    # Iniciar monitoreo
    monitor = SmartComputeSecurityMonitor()
    
    try:
        monitor.start_monitoring()
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo monitor de seguridad...")
        monitor.stop_monitoring()

if __name__ == "__main__":
    main()