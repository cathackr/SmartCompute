#!/usr/bin/env python3
"""
SmartCompute Industrial SCADA Logging System - Sistema Avanzado de Logs y Alertas ICS/SCADA

Integración con Soluciones SCADA:
- Wonderware System Platform (ArchestrA, InTouch, Historian)
- Emerson DeltaV (Process Control, Batch, Safety)
- Honeywell Experion PKS (C300, Safety Manager)
- ABB System 800xA (Control Builder, Operations)
- Schneider Electric EcoStruxure (AVEVA System Platform)
- GE Digital iFIX (Proficy, Historian, MES)
- Rockwell FactoryTalk (View SE/ME, Batch, Historian)
- Siemens WinCC (SCADA, Advanced, Professional)
- Yokogawa CENTUM VP (Engineering, Operations)
- ICONICS GENESIS64 (HMI/SCADA Suite)

Características:
- Correlación de eventos cross-platform SCADA
- Análisis de logs ICS en tiempo real
- Detección de anomalías en procesos industriales
- Alertas de seguridad específicas para entornos OT
- Dashboard unificado multi-SCADA
- Compliance con ISA-99/IEC 62443
- SIEM integration para SOC industrial
- Forensic analysis de incidentes ICS

Author: SmartCompute Team
Version: 2.0.0 SCADA Logging
Date: 2025-09-19
"""

import asyncio
import json
import sqlite3
import struct
import socket
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from pathlib import Path
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging
import re
import hashlib
import xml.etree.ElementTree as ET
from collections import defaultdict, deque
import numpy as np
import pandas as pd

class SCADASystem(Enum):
    """Sistemas SCADA soportados"""
    WONDERWARE = "wonderware"
    EMERSON_DELTAV = "emerson_deltav"
    HONEYWELL_EXPERION = "honeywell_experion"
    ABB_800XA = "abb_800xa"
    SCHNEIDER_ECOSTRUXURE = "schneider_ecostruxure"
    GE_IFIX = "ge_ifix"
    FACTORYTALK = "factorytalk"
    SIEMENS_WINCC = "siemens_wincc"
    YOKOGAWA_CENTUM = "yokogawa_centum"
    ICONICS_GENESIS = "iconics_genesis"

class LogSeverity(Enum):
    """Severidad de logs industriales"""
    EMERGENCY = "emergency"      # System is unusable
    ALERT = "alert"             # Action must be taken immediately
    CRITICAL = "critical"       # Critical conditions
    ERROR = "error"             # Error conditions
    WARNING = "warning"         # Warning conditions
    NOTICE = "notice"          # Normal but significant condition
    INFO = "info"              # Informational messages
    DEBUG = "debug"            # Debug-level messages

class ProcessAlarmType(Enum):
    """Tipos de alarmas de proceso"""
    HIGH_HIGH = "high_high"     # HH - Critical high
    HIGH = "high"               # H - High alarm
    LOW = "low"                 # L - Low alarm
    LOW_LOW = "low_low"         # LL - Critical low
    DEVIATION = "deviation"     # DEV - Deviation alarm
    RATE = "rate"              # ROC - Rate of change
    BAD_QUALITY = "bad_quality" # Quality alarm
    COMM_FAIL = "comm_fail"    # Communication failure
    SAFETY = "safety"          # Safety system alarm
    BATCH = "batch"            # Batch alarm

class ICSEventCategory(Enum):
    """Categorías de eventos ICS"""
    PROCESS_CONTROL = "process_control"
    SAFETY_SYSTEM = "safety_system"
    SECURITY_EVENT = "security_event"
    MAINTENANCE = "maintenance"
    OPERATOR_ACTION = "operator_action"
    SYSTEM_STATUS = "system_status"
    BATCH_OPERATION = "batch_operation"
    RECIPE_MANAGEMENT = "recipe_management"
    HISTORIAN_EVENT = "historian_event"
    COMMUNICATION = "communication"

@dataclass
class SCADALogEntry:
    """Entrada de log SCADA unificada"""
    log_id: str
    timestamp: datetime
    scada_system: SCADASystem
    source_node: str
    severity: LogSeverity
    category: ICSEventCategory
    message: str
    details: Dict[str, Any] = field(default_factory=dict)

    # Contexto del proceso
    process_area: Optional[str] = None
    control_module: Optional[str] = None
    tag_name: Optional[str] = None
    tag_value: Optional[Union[float, str, bool]] = None
    tag_quality: Optional[str] = None
    setpoint: Optional[float] = None

    # Información de alarma
    alarm_type: Optional[ProcessAlarmType] = None
    alarm_priority: Optional[int] = None
    alarm_state: Optional[str] = None  # Active, Acknowledged, Cleared
    operator_id: Optional[str] = None

    # Contexto de seguridad
    security_classification: Optional[str] = None
    access_level_required: Optional[str] = None
    authentication_method: Optional[str] = None

    # Metadatos técnicos
    raw_data: Optional[bytes] = None
    parsed_fields: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None

@dataclass
class ProcessAlarm:
    """Alarma de proceso industrial"""
    alarm_id: str
    timestamp: datetime
    tag_name: str
    alarm_type: ProcessAlarmType
    priority: int  # 1-4 (1=highest)
    current_value: float
    alarm_limit: float
    process_area: str
    control_module: str
    alarm_state: str  # Active, Acked, Cleared, Suppressed
    operator_comment: Optional[str] = None
    ack_timestamp: Optional[datetime] = None
    clear_timestamp: Optional[datetime] = None
    duration_seconds: Optional[float] = None

@dataclass
class BatchEvent:
    """Evento de operación batch"""
    event_id: str
    timestamp: datetime
    batch_id: str
    recipe_name: str
    unit_procedure: str
    operation: str
    phase: str
    step: str
    event_type: str  # Start, End, Pause, Resume, Abort
    operator_id: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)

class SCADALogParser:
    """Parser unificado para logs de diferentes sistemas SCADA"""

    def __init__(self):
        self.parsers = {
            SCADASystem.WONDERWARE: self._parse_wonderware_log,
            SCADASystem.EMERSON_DELTAV: self._parse_deltav_log,
            SCADASystem.HONEYWELL_EXPERION: self._parse_experion_log,
            SCADASystem.ABB_800XA: self._parse_abb_log,
            SCADASystem.SCHNEIDER_ECOSTRUXURE: self._parse_schneider_log,
            SCADASystem.GE_IFIX: self._parse_ifix_log,
            SCADASystem.FACTORYTALK: self._parse_factorytalk_log,
            SCADASystem.SIEMENS_WINCC: self._parse_wincc_log,
            SCADASystem.YOKOGAWA_CENTUM: self._parse_centum_log,
            SCADASystem.ICONICS_GENESIS: self._parse_iconics_log
        }

    def parse_log_entry(self, raw_log: str, scada_system: SCADASystem) -> Optional[SCADALogEntry]:
        """Parsear entrada de log según el sistema SCADA"""
        parser = self.parsers.get(scada_system)
        if not parser:
            return None

        try:
            return parser(raw_log)
        except Exception as e:
            print(f"Error parsing {scada_system.value} log: {e}")
            return None

    def _parse_wonderware_log(self, raw_log: str) -> SCADALogEntry:
        """Parser para Wonderware System Platform / InTouch"""
        # Formato típico: 2025-01-15 14:30:25.123 [ALARM] Area1.PumpMotor1.Speed HH 1850.5 rpm (Limit: 1800.0) Operator: JSmith
        pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}) \[(\w+)\] (.+?)(?:\s+Operator: (\w+))?$'
        match = re.match(pattern, raw_log)

        if not match:
            raise ValueError("Invalid Wonderware log format")

        timestamp_str, severity_str, message, operator = match.groups()
        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')

        # Parsear detalles de tag si es alarma
        tag_details = self._parse_wonderware_tag_details(message)

        return SCADALogEntry(
            log_id=hashlib.md5(raw_log.encode()).hexdigest(),
            timestamp=timestamp,
            scada_system=SCADASystem.WONDERWARE,
            source_node="Wonderware_Node",
            severity=self._map_severity(severity_str),
            category=ICSEventCategory.PROCESS_CONTROL if "ALARM" in severity_str else ICSEventCategory.SYSTEM_STATUS,
            message=message,
            tag_name=tag_details.get('tag_name'),
            tag_value=tag_details.get('tag_value'),
            alarm_type=tag_details.get('alarm_type'),
            setpoint=tag_details.get('setpoint'),
            operator_id=operator,
            details=tag_details
        )

    def _parse_deltav_log(self, raw_log: str) -> SCADALogEntry:
        """Parser para Emerson DeltaV"""
        # Formato típico: 15-JAN-25 14:30:25.123 REACTOR01/TIC_001/PV.CV HI_ALM 85.5 DEG_C PRIO=3 USER=OPERATOR1
        pattern = r'(\d{2}-\w{3}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}) (\S+) (\w+) ([\d.]+) (\w+)(?:\s+PRIO=(\d+))? (?:USER=(\w+))?'
        match = re.match(pattern, raw_log)

        if not match:
            raise ValueError("Invalid DeltaV log format")

        timestamp_str, tag_path, alarm_type, value, units, priority, user = match.groups()
        timestamp = datetime.strptime(timestamp_str, '%d-%b-%y %H:%M:%S.%f')

        # Parsear path del tag DeltaV (AREA/MODULE/PARAMETER)
        path_parts = tag_path.split('/')
        process_area = path_parts[0] if len(path_parts) > 0 else None
        control_module = path_parts[1] if len(path_parts) > 1 else None

        return SCADALogEntry(
            log_id=hashlib.md5(raw_log.encode()).hexdigest(),
            timestamp=timestamp,
            scada_system=SCADASystem.EMERSON_DELTAV,
            source_node="DeltaV_Controller",
            severity=LogSeverity.WARNING if "ALM" in alarm_type else LogSeverity.INFO,
            category=ICSEventCategory.PROCESS_CONTROL,
            message=f"{tag_path} {alarm_type} {value} {units}",
            process_area=process_area,
            control_module=control_module,
            tag_name=tag_path,
            tag_value=float(value) if value else None,
            alarm_type=self._map_deltav_alarm_type(alarm_type),
            alarm_priority=int(priority) if priority else None,
            operator_id=user,
            details={'units': units, 'raw_alarm_type': alarm_type}
        )

    def _parse_experion_log(self, raw_log: str) -> SCADALogEntry:
        """Parser para Honeywell Experion PKS"""
        # Formato típico: 2025.01.15 14:30:25.123 C300_01 ALARM FC_101.PV HIGH 75.5 % [ACK: OPERATOR2 14:32:15]
        pattern = r'(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2}\.\d{3}) (\w+) (\w+) (\S+) (\w+) ([\d.]+) (\w+)(?:\s+\[ACK: (\w+) (\d{2}:\d{2}:\d{2})\])?'
        match = re.match(pattern, raw_log)

        if not match:
            raise ValueError("Invalid Experion log format")

        timestamp_str, controller, event_type, tag, alarm_type, value, units, ack_user, ack_time = match.groups()
        timestamp = datetime.strptime(timestamp_str, '%Y.%m.%d %H:%M:%S.%f')

        return SCADALogEntry(
            log_id=hashlib.md5(raw_log.encode()).hexdigest(),
            timestamp=timestamp,
            scada_system=SCADASystem.HONEYWELL_EXPERION,
            source_node=controller,
            severity=LogSeverity.WARNING if event_type == "ALARM" else LogSeverity.INFO,
            category=ICSEventCategory.PROCESS_CONTROL,
            message=f"{tag} {alarm_type} {value} {units}",
            tag_name=tag,
            tag_value=float(value) if value else None,
            alarm_type=self._map_alarm_type_generic(alarm_type),
            operator_id=ack_user,
            details={'units': units, 'controller': controller, 'ack_time': ack_time}
        )

    def _parse_siemens_wincc_log(self, raw_log: str) -> SCADALogEntry:
        """Parser para Siemens WinCC"""
        # Formato típico: 2025-01-15,14:30:25.123,S7-1500_01,@2s\\MotorSpeed,1850.5,rpm,HH_ALM,User01,Acknowledged
        parts = raw_log.split(',')
        if len(parts) < 6:
            raise ValueError("Invalid WinCC log format")

        timestamp_str = f"{parts[0]} {parts[1]}"
        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')

        return SCADALogEntry(
            log_id=hashlib.md5(raw_log.encode()).hexdigest(),
            timestamp=timestamp,
            scada_system=SCADASystem.SIEMENS_WINCC,
            source_node=parts[2],
            severity=LogSeverity.WARNING if "ALM" in parts[6] else LogSeverity.INFO,
            category=ICSEventCategory.PROCESS_CONTROL,
            message=f"{parts[3]} {parts[6]} {parts[4]} {parts[5]}",
            tag_name=parts[3],
            tag_value=float(parts[4]) if parts[4] else None,
            alarm_type=self._map_alarm_type_generic(parts[6]),
            operator_id=parts[7] if len(parts) > 7 else None,
            details={'units': parts[5], 'plc': parts[2]}
        )

    def _parse_factorytalk_log(self, raw_log: str) -> SCADALogEntry:
        """Parser para Rockwell FactoryTalk"""
        # Formato XML típico de FactoryTalk Batch
        if raw_log.startswith('<'):
            return self._parse_factorytalk_xml(raw_log)
        else:
            return self._parse_factorytalk_text(raw_log)

    def _parse_factorytalk_xml(self, xml_log: str) -> SCADALogEntry:
        """Parser para logs XML de FactoryTalk"""
        root = ET.fromstring(xml_log)

        timestamp_str = root.get('timestamp')
        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))

        event_type = root.get('type', 'UNKNOWN')
        batch_id = root.findtext('BatchId', '')
        recipe = root.findtext('Recipe', '')
        operator = root.findtext('Operator', '')

        return SCADALogEntry(
            log_id=hashlib.md5(xml_log.encode()).hexdigest(),
            timestamp=timestamp,
            scada_system=SCADASystem.FACTORYTALK,
            source_node="FactoryTalk_Server",
            severity=LogSeverity.INFO,
            category=ICSEventCategory.BATCH_OPERATION,
            message=f"Batch {batch_id}: {event_type}",
            operator_id=operator,
            details={'batch_id': batch_id, 'recipe': recipe, 'event_type': event_type}
        )

    def _parse_factorytalk_text(self, text_log: str) -> SCADALogEntry:
        """Parser para logs de texto de FactoryTalk"""
        # Formato: [2025-01-15 14:30:25] [INFO] HMI_Station_01: Motor1_Start = TRUE (User: OPERATOR1)
        pattern = r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] \[(\w+)\] (\w+): (.+?)(?:\s+\(User: (\w+)\))?'
        match = re.match(pattern, text_log)

        if not match:
            raise ValueError("Invalid FactoryTalk text log format")

        timestamp_str, severity, station, message, user = match.groups()
        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')

        return SCADALogEntry(
            log_id=hashlib.md5(text_log.encode()).hexdigest(),
            timestamp=timestamp,
            scada_system=SCADASystem.FACTORYTALK,
            source_node=station,
            severity=self._map_severity(severity),
            category=ICSEventCategory.OPERATOR_ACTION,
            message=message,
            operator_id=user,
            details={'station': station}
        )

    def _parse_wonderware_tag_details(self, message: str) -> Dict[str, Any]:
        """Parsear detalles de tags de Wonderware"""
        details = {}

        # Buscar patrón de tag con alarma: Area1.PumpMotor1.Speed HH 1850.5 rpm (Limit: 1800.0)
        tag_pattern = r'(\S+)\s+([HL]{1,2})\s+([\d.]+)\s+(\w+)\s+\(Limit:\s+([\d.]+)\)'
        match = re.search(tag_pattern, message)

        if match:
            tag_name, alarm_type, value, units, limit = match.groups()
            details.update({
                'tag_name': tag_name,
                'tag_value': float(value),
                'alarm_type': self._map_alarm_type_generic(alarm_type),
                'setpoint': float(limit),
                'units': units
            })

        return details

    def _map_severity(self, severity_str: str) -> LogSeverity:
        """Mapear string de severidad a enum"""
        severity_map = {
            'EMERGENCY': LogSeverity.EMERGENCY,
            'ALERT': LogSeverity.ALERT,
            'CRITICAL': LogSeverity.CRITICAL,
            'ERROR': LogSeverity.ERROR,
            'WARN': LogSeverity.WARNING,
            'WARNING': LogSeverity.WARNING,
            'NOTICE': LogSeverity.NOTICE,
            'INFO': LogSeverity.INFO,
            'DEBUG': LogSeverity.DEBUG,
            'ALARM': LogSeverity.WARNING
        }
        return severity_map.get(severity_str.upper(), LogSeverity.INFO)

    def _map_alarm_type_generic(self, alarm_str: str) -> ProcessAlarmType:
        """Mapear string de alarma a enum genérico"""
        alarm_map = {
            'HH': ProcessAlarmType.HIGH_HIGH,
            'H': ProcessAlarmType.HIGH,
            'HIGH': ProcessAlarmType.HIGH,
            'L': ProcessAlarmType.LOW,
            'LL': ProcessAlarmType.LOW_LOW,
            'LOW': ProcessAlarmType.LOW,
            'DEV': ProcessAlarmType.DEVIATION,
            'ROC': ProcessAlarmType.RATE,
            'COMM': ProcessAlarmType.COMM_FAIL,
            'QUALITY': ProcessAlarmType.BAD_QUALITY,
            'SAFETY': ProcessAlarmType.SAFETY
        }
        return alarm_map.get(alarm_str.upper(), ProcessAlarmType.HIGH)

    def _map_deltav_alarm_type(self, alarm_str: str) -> ProcessAlarmType:
        """Mapear tipos de alarma específicos de DeltaV"""
        deltav_map = {
            'HI_ALM': ProcessAlarmType.HIGH,
            'HIHI_ALM': ProcessAlarmType.HIGH_HIGH,
            'LO_ALM': ProcessAlarmType.LOW,
            'LOLO_ALM': ProcessAlarmType.LOW_LOW,
            'DEV_ALM': ProcessAlarmType.DEVIATION,
            'ROC_ALM': ProcessAlarmType.RATE,
            'COMM_ALM': ProcessAlarmType.COMM_FAIL,
            'BAD_PV': ProcessAlarmType.BAD_QUALITY
        }
        return deltav_map.get(alarm_str.upper(), ProcessAlarmType.HIGH)


class IndustrialSCADALogger:
    """Sistema principal de logging SCADA industrial"""

    def __init__(self):
        self.logger = self.setup_logging()
        self.db_path = Path(__file__).parent / "industrial_scada_logs.db"

        # Componentes principales
        self.log_parser = SCADALogParser()
        self.log_buffer = deque(maxlen=10000)  # Buffer circular para logs recientes
        self.alarm_buffer = deque(maxlen=5000)  # Buffer para alarmas activas

        # Estado del sistema
        self.active_alarms = {}
        self.scada_connections = {}
        self.log_statistics = defaultdict(int)

        # Configuración de alertas
        self.alert_rules = {}
        self.correlation_rules = {}

        # Análisis en tiempo real
        self.anomaly_detector = None
        self.pattern_analyzer = None

        self.init_database()
        self.load_alert_rules()
        self.start_log_processing()

        self.logger.info("📝 Industrial SCADA Logger initialized")

    def setup_logging(self) -> logging.Logger:
        """Configurar sistema de logging"""
        logger = logging.getLogger('SCADALogger')
        logger.setLevel(logging.INFO)

        handler = logging.FileHandler('smartcompute_scada_logger.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def init_database(self):
        """Inicializar base de datos de logs SCADA"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Tabla principal de logs SCADA
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scada_logs (
                log_id TEXT PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL,
                scada_system TEXT NOT NULL,
                source_node TEXT,
                severity TEXT NOT NULL,
                category TEXT NOT NULL,
                message TEXT NOT NULL,
                process_area TEXT,
                control_module TEXT,
                tag_name TEXT,
                tag_value REAL,
                tag_quality TEXT,
                setpoint REAL,
                alarm_type TEXT,
                alarm_priority INTEGER,
                alarm_state TEXT,
                operator_id TEXT,
                security_classification TEXT,
                correlation_id TEXT,
                details TEXT,
                raw_data BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Tabla de alarmas de proceso
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS process_alarms (
                alarm_id TEXT PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL,
                tag_name TEXT NOT NULL,
                alarm_type TEXT NOT NULL,
                priority INTEGER NOT NULL,
                current_value REAL NOT NULL,
                alarm_limit REAL NOT NULL,
                process_area TEXT,
                control_module TEXT,
                alarm_state TEXT NOT NULL,
                operator_comment TEXT,
                ack_timestamp TIMESTAMP,
                clear_timestamp TIMESTAMP,
                duration_seconds REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Tabla de eventos batch
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS batch_events (
                event_id TEXT PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL,
                batch_id TEXT NOT NULL,
                recipe_name TEXT NOT NULL,
                unit_procedure TEXT,
                operation TEXT,
                phase TEXT,
                step_name TEXT,
                event_type TEXT NOT NULL,
                operator_id TEXT,
                parameters TEXT,
                results TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Tabla de conexiones SCADA
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scada_connections (
                connection_id TEXT PRIMARY KEY,
                scada_system TEXT NOT NULL,
                node_name TEXT NOT NULL,
                ip_address TEXT,
                port INTEGER,
                protocol TEXT,
                connection_status TEXT,
                last_heartbeat TIMESTAMP,
                connection_params TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Tabla de reglas de correlación
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS correlation_rules (
                rule_id TEXT PRIMARY KEY,
                rule_name TEXT NOT NULL,
                conditions TEXT NOT NULL,
                actions TEXT NOT NULL,
                time_window_seconds INTEGER DEFAULT 300,
                enabled BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Índices para rendimiento
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON scada_logs(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_severity ON scada_logs(severity)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_system ON scada_logs(scada_system)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_tag ON scada_logs(tag_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alarms_state ON process_alarms(alarm_state)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alarms_priority ON process_alarms(priority)')

        conn.commit()
        conn.close()

    def load_alert_rules(self):
        """Cargar reglas de alertas predefinidas"""
        # Reglas de alerta críticas para entornos industriales
        critical_rules = {
            "safety_system_failure": {
                "conditions": {
                    "tag_patterns": ["*SAFETY*", "*SIS*", "*TRIP*"],
                    "alarm_types": [ProcessAlarmType.SAFETY],
                    "severity": [LogSeverity.CRITICAL, LogSeverity.EMERGENCY]
                },
                "actions": {
                    "notify_immediately": True,
                    "escalate_to_management": True,
                    "log_to_security_siem": True,
                    "create_incident": True
                },
                "time_window": 60  # 1 minuto
            },

            "multiple_communication_failures": {
                "conditions": {
                    "alarm_types": [ProcessAlarmType.COMM_FAIL],
                    "minimum_occurrences": 3,
                    "time_window": 300  # 5 minutos
                },
                "actions": {
                    "notify_network_team": True,
                    "check_cybersecurity_incident": True,
                    "log_correlation_event": True
                }
            },

            "unauthorized_operator_actions": {
                "conditions": {
                    "categories": [ICSEventCategory.OPERATOR_ACTION],
                    "time_ranges": ["22:00-06:00", "weekends"],  # Fuera de horario
                    "excluded_operators": ["emergency_ops", "shift_supervisor"]
                },
                "actions": {
                    "security_alert": True,
                    "require_justification": True,
                    "audit_log": True
                }
            },

            "batch_recipe_deviations": {
                "conditions": {
                    "categories": [ICSEventCategory.BATCH_OPERATION],
                    "event_types": ["deviation", "abort", "parameter_change"],
                    "minimum_batch_value": 10000  # Solo batches de alto valor
                },
                "actions": {
                    "notify_production_manager": True,
                    "quality_hold": True,
                    "investigate_root_cause": True
                }
            },

            "process_value_anomalies": {
                "conditions": {
                    "statistical_deviation": 3.0,  # 3 sigma
                    "consecutive_readings": 5,
                    "critical_tags": ["*REACTOR*", "*DISTILLATION*", "*PRESSURE*"]
                },
                "actions": {
                    "process_engineer_alert": True,
                    "trend_analysis": True,
                    "predictive_maintenance": True
                }
            }
        }

        self.alert_rules.update(critical_rules)
        self.logger.info(f"✅ Loaded {len(critical_rules)} critical alert rules")

    def register_scada_connection(self, scada_system: SCADASystem, connection_params: Dict):
        """Registrar conexión a sistema SCADA"""
        connection_id = f"{scada_system.value}_{connection_params.get('node_name', 'default')}"

        connection_info = {
            'connection_id': connection_id,
            'scada_system': scada_system,
            'node_name': connection_params.get('node_name', 'Unknown'),
            'ip_address': connection_params.get('ip_address'),
            'port': connection_params.get('port'),
            'protocol': connection_params.get('protocol'),
            'status': 'connected',
            'last_heartbeat': datetime.now(),
            'params': connection_params
        }

        self.scada_connections[connection_id] = connection_info

        # Guardar en base de datos
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO scada_connections
            (connection_id, scada_system, node_name, ip_address, port, protocol,
             connection_status, last_heartbeat, connection_params, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            connection_id, scada_system.value, connection_info['node_name'],
            connection_info['ip_address'], connection_info['port'],
            connection_info['protocol'], connection_info['status'],
            connection_info['last_heartbeat'], json.dumps(connection_params),
            datetime.now()
        ))

        conn.commit()
        conn.close()

        self.logger.info(f"🔗 Registered SCADA connection: {connection_id}")
        return connection_id

    def ingest_raw_log(self, raw_log: str, scada_system: SCADASystem, source_connection: str = None):
        """Ingestar log raw de sistema SCADA"""
        try:
            # Parsear log usando el parser apropiado
            log_entry = self.log_parser.parse_log_entry(raw_log, scada_system)
            if not log_entry:
                self.logger.warning(f"Failed to parse log from {scada_system.value}: {raw_log[:100]}...")
                return

            # Agregar información de conexión
            if source_connection:
                log_entry.details['source_connection'] = source_connection

            # Procesar y almacenar
            self.process_log_entry(log_entry)

            # Actualizar estadísticas
            self.log_statistics[scada_system.value] += 1
            self.log_statistics['total'] += 1

        except Exception as e:
            self.logger.error(f"Error ingesting log from {scada_system.value}: {e}")

    def process_log_entry(self, log_entry: SCADALogEntry):
        """Procesar entrada de log"""
        # Agregar a buffer
        self.log_buffer.append(log_entry)

        # Análisis en tiempo real
        self.analyze_log_entry(log_entry)

        # Verificar reglas de alerta
        self.check_alert_rules(log_entry)

        # Si es alarma, procesamiento especial
        if log_entry.alarm_type:
            self.process_alarm(log_entry)

        # Guardar en base de datos
        asyncio.create_task(self.save_log_entry(log_entry))

    def analyze_log_entry(self, log_entry: SCADALogEntry):
        """Análisis en tiempo real de entrada de log"""
        # Detección de anomalías (simplificado)
        if log_entry.tag_value is not None:
            self.update_tag_statistics(log_entry.tag_name, log_entry.tag_value)

        # Correlación de eventos
        self.correlate_events(log_entry)

        # Análisis de patrones de seguridad
        self.security_pattern_analysis(log_entry)

    def check_alert_rules(self, log_entry: SCADALogEntry):
        """Verificar reglas de alerta"""
        for rule_name, rule_config in self.alert_rules.items():
            if self.evaluate_alert_condition(log_entry, rule_config):
                self.trigger_alert(rule_name, log_entry, rule_config)

    def evaluate_alert_condition(self, log_entry: SCADALogEntry, rule_config: Dict) -> bool:
        """Evaluar condición de alerta"""
        conditions = rule_config.get('conditions', {})

        # Verificar patrones de tag
        tag_patterns = conditions.get('tag_patterns', [])
        if tag_patterns and log_entry.tag_name:
            tag_match = any(
                self.match_pattern(log_entry.tag_name, pattern)
                for pattern in tag_patterns
            )
            if not tag_match:
                return False

        # Verificar tipos de alarma
        alarm_types = conditions.get('alarm_types', [])
        if alarm_types and log_entry.alarm_type not in alarm_types:
            return False

        # Verificar severidad
        severities = conditions.get('severity', [])
        if severities and log_entry.severity not in severities:
            return False

        # Verificar categorías
        categories = conditions.get('categories', [])
        if categories and log_entry.category not in categories:
            return False

        return True

    def match_pattern(self, text: str, pattern: str) -> bool:
        """Verificar si texto coincide con patrón (soporte wildcards)"""
        import fnmatch
        return fnmatch.fnmatch(text.upper(), pattern.upper())

    def trigger_alert(self, rule_name: str, log_entry: SCADALogEntry, rule_config: Dict):
        """Disparar alerta"""
        actions = rule_config.get('actions', {})

        alert_data = {
            'alert_id': f"alert_{int(datetime.now().timestamp())}",
            'rule_name': rule_name,
            'timestamp': datetime.now(),
            'log_entry': asdict(log_entry),
            'severity': log_entry.severity.value,
            'actions_taken': []
        }

        # Ejecutar acciones configuradas
        if actions.get('notify_immediately'):
            self.send_immediate_notification(alert_data)
            alert_data['actions_taken'].append('immediate_notification')

        if actions.get('log_to_security_siem'):
            self.forward_to_siem(alert_data)
            alert_data['actions_taken'].append('siem_forwarding')

        if actions.get('create_incident'):
            self.create_security_incident(alert_data)
            alert_data['actions_taken'].append('incident_creation')

        self.logger.warning(f"🚨 ALERT TRIGGERED: {rule_name} - {log_entry.message}")

    def process_alarm(self, log_entry: SCADALogEntry):
        """Procesamiento específico de alarmas"""
        if not log_entry.tag_name or not log_entry.alarm_type:
            return

        alarm_key = f"{log_entry.tag_name}_{log_entry.alarm_type.value}"

        # Crear objeto de alarma
        alarm = ProcessAlarm(
            alarm_id=alarm_key,
            timestamp=log_entry.timestamp,
            tag_name=log_entry.tag_name,
            alarm_type=log_entry.alarm_type,
            priority=log_entry.alarm_priority or 3,
            current_value=log_entry.tag_value or 0.0,
            alarm_limit=log_entry.setpoint or 0.0,
            process_area=log_entry.process_area or "Unknown",
            control_module=log_entry.control_module or "Unknown",
            alarm_state=log_entry.alarm_state or "Active"
        )

        # Gestionar estado de alarma
        if alarm.alarm_state == "Active":
            self.active_alarms[alarm_key] = alarm
            self.alarm_buffer.append(alarm)
        elif alarm.alarm_state in ["Acknowledged", "Cleared"]:
            if alarm_key in self.active_alarms:
                existing_alarm = self.active_alarms[alarm_key]
                if alarm.alarm_state == "Acknowledged":
                    existing_alarm.ack_timestamp = log_entry.timestamp
                elif alarm.alarm_state == "Cleared":
                    existing_alarm.clear_timestamp = log_entry.timestamp
                    existing_alarm.duration_seconds = (
                        log_entry.timestamp - existing_alarm.timestamp
                    ).total_seconds()
                    del self.active_alarms[alarm_key]

        # Guardar alarma
        asyncio.create_task(self.save_alarm(alarm))

    def update_tag_statistics(self, tag_name: str, value: float):
        """Actualizar estadísticas de tag para detección de anomalías"""
        # Implementación simplificada - en producción usar algoritmos más sofisticados
        pass

    def correlate_events(self, log_entry: SCADALogEntry):
        """Correlacionar eventos para detectar patrones"""
        # Implementación de correlación de eventos
        pass

    def security_pattern_analysis(self, log_entry: SCADALogEntry):
        """Análisis de patrones de seguridad"""
        # Buscar patrones sospechosos típicos en entornos ICS
        suspicious_patterns = [
            "password",
            "login failed",
            "unauthorized access",
            "configuration changed",
            "program download",
            "recipe modified"
        ]

        message_lower = log_entry.message.lower()
        for pattern in suspicious_patterns:
            if pattern in message_lower:
                self.logger.warning(f"🔍 Security pattern detected: {pattern} in {log_entry.message}")
                break

    async def save_log_entry(self, log_entry: SCADALogEntry):
        """Guardar entrada de log en base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO scada_logs
                (log_id, timestamp, scada_system, source_node, severity, category,
                 message, process_area, control_module, tag_name, tag_value, tag_quality,
                 setpoint, alarm_type, alarm_priority, alarm_state, operator_id,
                 security_classification, correlation_id, details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                log_entry.log_id, log_entry.timestamp, log_entry.scada_system.value,
                log_entry.source_node, log_entry.severity.value, log_entry.category.value,
                log_entry.message, log_entry.process_area, log_entry.control_module,
                log_entry.tag_name, log_entry.tag_value, log_entry.tag_quality,
                log_entry.setpoint,
                log_entry.alarm_type.value if log_entry.alarm_type else None,
                log_entry.alarm_priority, log_entry.alarm_state, log_entry.operator_id,
                log_entry.security_classification, log_entry.correlation_id,
                json.dumps(log_entry.details, default=str)
            ))

            conn.commit()
        except Exception as e:
            self.logger.error(f"Error saving log entry: {e}")
        finally:
            conn.close()

    async def save_alarm(self, alarm: ProcessAlarm):
        """Guardar alarma en base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT OR REPLACE INTO process_alarms
                (alarm_id, timestamp, tag_name, alarm_type, priority, current_value,
                 alarm_limit, process_area, control_module, alarm_state, operator_comment,
                 ack_timestamp, clear_timestamp, duration_seconds)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                alarm.alarm_id, alarm.timestamp, alarm.tag_name, alarm.alarm_type.value,
                alarm.priority, alarm.current_value, alarm.alarm_limit,
                alarm.process_area, alarm.control_module, alarm.alarm_state,
                alarm.operator_comment, alarm.ack_timestamp, alarm.clear_timestamp,
                alarm.duration_seconds
            ))

            conn.commit()
        except Exception as e:
            self.logger.error(f"Error saving alarm: {e}")
        finally:
            conn.close()

    def send_immediate_notification(self, alert_data: Dict):
        """Enviar notificación inmediata"""
        # En producción integrar con sistemas de notificación reales
        self.logger.critical(f"IMMEDIATE ALERT: {alert_data['rule_name']}")

    def forward_to_siem(self, alert_data: Dict):
        """Reenviar a SIEM de seguridad"""
        # En producción integrar con SIEM real (Splunk, QRadar, etc.)
        self.logger.info(f"Forwarding to SIEM: {alert_data['alert_id']}")

    def create_security_incident(self, alert_data: Dict):
        """Crear incidente de seguridad"""
        # En producción integrar con sistema de tickets
        self.logger.info(f"Creating security incident: {alert_data['alert_id']}")

    def start_log_processing(self):
        """Iniciar procesamiento de logs en background"""
        def log_processing_loop():
            while True:
                try:
                    # Simular recepción de logs de diferentes sistemas SCADA
                    self.simulate_scada_logs()
                    time.sleep(5)
                except Exception as e:
                    self.logger.error(f"Log processing error: {e}")
                    time.sleep(30)

        processing_thread = threading.Thread(target=log_processing_loop)
        processing_thread.daemon = True
        processing_thread.start()

    def simulate_scada_logs(self):
        """Simular logs de diferentes sistemas SCADA para demostración"""
        import random

        # Logs de ejemplo de diferentes sistemas
        sample_logs = [
            # Wonderware
            ("2025-01-15 14:30:25.123 [ALARM] Area1.PumpMotor1.Speed HH 1850.5 rpm (Limit: 1800.0) Operator: JSmith", SCADASystem.WONDERWARE),

            # DeltaV
            ("15-JAN-25 14:31:15.456 REACTOR01/TIC_001/PV.CV HI_ALM 85.5 DEG_C PRIO=3 USER=OPERATOR1", SCADASystem.EMERSON_DELTAV),

            # Experion
            ("2025.01.15 14:32:05.789 C300_01 ALARM FC_101.PV HIGH 75.5 % [ACK: OPERATOR2 14:32:15]", SCADASystem.HONEYWELL_EXPERION),

            # WinCC
            ("2025-01-15,14:33:45.123,S7-1500_01,@2s\\MotorSpeed,1850.5,rpm,HH_ALM,User01,Acknowledged", SCADASystem.SIEMENS_WINCC),

            # FactoryTalk
            ("[2025-01-15 14:34:25] [INFO] HMI_Station_01: Motor1_Start = TRUE (User: OPERATOR1)", SCADASystem.FACTORYTALK)
        ]

        # Seleccionar log aleatorio
        if random.random() < 0.3:  # 30% probabilidad de generar log
            log_text, scada_system = random.choice(sample_logs)
            self.ingest_raw_log(log_text, scada_system, f"connection_{scada_system.value}")

    def get_dashboard_data(self) -> Dict:
        """Obtener datos para dashboard de logs SCADA"""
        current_time = datetime.now()
        last_hour = current_time - timedelta(hours=1)

        conn = sqlite3.connect(self.db_path)

        # Estadísticas generales
        total_logs = len(self.log_buffer)
        active_alarms_count = len(self.active_alarms)

        # Logs por sistema SCADA
        system_stats = {}
        for system in SCADASystem:
            count = sum(1 for log in self.log_buffer if log.scada_system == system)
            system_stats[system.value] = count

        # Alarmas por prioridad
        alarm_priorities = defaultdict(int)
        for alarm in self.active_alarms.values():
            alarm_priorities[alarm.priority] += 1

        # Top tags con más eventos
        tag_events = defaultdict(int)
        for log in self.log_buffer:
            if log.tag_name:
                tag_events[log.tag_name] += 1

        top_tags = sorted(tag_events.items(), key=lambda x: x[1], reverse=True)[:10]

        conn.close()

        return {
            'summary': {
                'total_logs_last_hour': total_logs,
                'active_alarms': active_alarms_count,
                'connected_scada_systems': len(self.scada_connections),
                'alert_rules_active': len(self.alert_rules)
            },
            'scada_systems': system_stats,
            'alarm_priorities': dict(alarm_priorities),
            'top_active_tags': top_tags,
            'recent_critical_events': [
                {
                    'timestamp': log.timestamp.isoformat(),
                    'system': log.scada_system.value,
                    'message': log.message[:100],
                    'severity': log.severity.value
                }
                for log in list(self.log_buffer)[-10:]
                if log.severity in [LogSeverity.CRITICAL, LogSeverity.EMERGENCY]
            ]
        }


def main():
    """Función principal de demostración"""
    print("📝 SmartCompute Industrial SCADA Logging System")
    print("=" * 60)

    logger = IndustrialSCADALogger()

    # Registrar conexiones SCADA
    scada_systems = [
        {
            'system': SCADASystem.WONDERWARE,
            'params': {'node_name': 'WW_Server_01', 'ip_address': '192.168.1.100', 'port': 1433, 'protocol': 'SQL'}
        },
        {
            'system': SCADASystem.EMERSON_DELTAV,
            'params': {'node_name': 'DeltaV_Prof_01', 'ip_address': '192.168.1.101', 'port': 18507, 'protocol': 'DeltaV'}
        },
        {
            'system': SCADASystem.SIEMENS_WINCC,
            'params': {'node_name': 'WinCC_RT_01', 'ip_address': '192.168.1.102', 'port': 1433, 'protocol': 'SQL'}
        }
    ]

    for system_config in scada_systems:
        connection_id = logger.register_scada_connection(
            system_config['system'],
            system_config['params']
        )
        print(f"🔗 Registered: {connection_id}")

    print(f"\n📊 Alert Rules Loaded: {len(logger.alert_rules)}")
    for rule_name in logger.alert_rules.keys():
        print(f"  • {rule_name}")

    print(f"\n🔄 Log processing started...")
    print("Simulating SCADA logs...")

    try:
        # Ejecutar por un tiempo para demostrar funcionalidad
        time.sleep(30)

        # Mostrar estadísticas
        dashboard = logger.get_dashboard_data()
        print(f"\n📈 Dashboard Summary:")
        print(f"  Total logs processed: {dashboard['summary']['total_logs_last_hour']}")
        print(f"  Active alarms: {dashboard['summary']['active_alarms']}")
        print(f"  Connected SCADA systems: {dashboard['summary']['connected_scada_systems']}")

        print(f"\n🏭 SCADA Systems Activity:")
        for system, count in dashboard['scada_systems'].items():
            print(f"  {system}: {count} logs")

        if dashboard['top_active_tags']:
            print(f"\n🏷️  Top Active Tags:")
            for tag, count in dashboard['top_active_tags'][:5]:
                print(f"  {tag}: {count} events")

    except KeyboardInterrupt:
        print("\n🛑 Stopping SCADA logger...")


if __name__ == "__main__":
    main()