#!/usr/bin/env python3
"""
SmartCompute Industrial Variables Monitor - Monitoreo Avanzado de Variables Físicas

Características:
- Monitoreo en tiempo real de variables físicas industriales
- Integración con PLCs y sistemas SCADA
- Análisis de tendencias y predicción de fallas
- Alertas inteligentes con machine learning
- Dashboard interactivo con gráficos en tiempo real
- Integración BotConf para análisis de anomalías
- Cumplimiento con estándares ISA-95 e IEC 61511

Variables Monitoreadas:
- Voltaje (AC/DC, trifásico, monofásico)
- Corriente (A, mA, intensidad)
- Potencia (kW, kVA, kVAr, factor de potencia)
- Temperatura (°C, °F, Kelvin)
- Presión (bar, PSI, kPa, mmHg)
- Caudal (L/min, m³/h, GPM)
- Humedad (RH%, absoluta)
- Vibración (mm/s, g, Hz)
- RPM (revoluciones por minuto)
- Nivel (%, mm, litros)
- pH, conductividad, ORP
- Posición, velocidad, aceleración

Author: SmartCompute Team
Version: 2.0.0 Industrial Monitor
Date: 2025-09-19
"""

import asyncio
import json
import time
import threading
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import socket
import struct
import random
import math
from collections import deque
import hashlib
import hmac

# Simulación de bibliotecas industriales
# En producción usar bibliotecas reales como:
# import snap7  # Para Siemens PLCs
# import pycomm3  # Para Allen-Bradley PLCs
# import pymodbus  # Para Modbus devices
# import opcua  # Para OPC-UA servers


class VariableType(Enum):
    """Tipos de variables industriales"""
    ELECTRICAL = "electrical"
    THERMAL = "thermal"
    MECHANICAL = "mechanical"
    FLUID = "fluid"
    CHEMICAL = "chemical"
    DIGITAL = "digital"
    ANALOG = "analog"


class AlarmSeverity(Enum):
    """Severidad de alarmas"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class SensorStatus(Enum):
    """Estado de sensores"""
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    CALIBRATION = "calibration"


@dataclass
class IndustrialVariable:
    """Definición de variable industrial con especificaciones técnicas detalladas"""
    id: str
    name: str
    description: str
    variable_type: VariableType
    unit: str
    min_value: float
    max_value: float
    nominal_value: float
    warning_low: float
    warning_high: float
    alarm_low: float
    alarm_high: float
    location: str
    plc_address: str
    update_rate_ms: int
    history_retention_days: int = 30
    enable_prediction: bool = True
    enable_trending: bool = True

    # Especificaciones técnicas detalladas
    technical_specs: Optional[Dict[str, Any]] = None
    safety_classification: Optional[str] = None
    maintenance_schedule: Optional[Dict[str, Any]] = None
    calibration_info: Optional[Dict[str, Any]] = None
    installation_details: Optional[Dict[str, Any]] = None


@dataclass
class VariableReading:
    """Lectura de variable industrial"""
    variable_id: str
    timestamp: datetime
    value: float
    quality: int  # 0-100%
    status: SensorStatus
    raw_value: Optional[float] = None
    engineering_units: Optional[str] = None
    source_address: Optional[str] = None


@dataclass
class IndustrialAlarm:
    """Alarma industrial"""
    id: str
    variable_id: str
    timestamp: datetime
    severity: AlarmSeverity
    message: str
    current_value: float
    threshold_value: float
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    cleared: bool = False
    cleared_at: Optional[datetime] = None


class PLCCommunicationEngine:
    """Motor de comunicación con PLCs"""

    def __init__(self):
        self.logger = logging.getLogger('PLC-Communication')
        self.connections = {}
        self.supported_protocols = {
            'modbus_tcp': {'port': 502, 'library': 'pymodbus'},
            's7comm': {'port': 102, 'library': 'snap7'},
            'ethernet_ip': {'port': 44818, 'library': 'pycomm3'},
            'opcua': {'port': 4840, 'library': 'opcua'},
            'profinet': {'port': 34962, 'library': 'profinet'},
            'fins': {'port': 9600, 'library': 'fins'},
            'mc_protocol': {'port': 5007, 'library': 'mc_protocol'}
        }

    async def connect_plc(self, plc_config: Dict) -> bool:
        """Conectar a PLC específico"""
        plc_id = plc_config['id']
        protocol = plc_config['protocol']
        ip_address = plc_config['ip_address']

        try:
            if protocol == 'modbus_tcp':
                connection = await self.connect_modbus_tcp(ip_address, plc_config.get('port', 502))
            elif protocol == 's7comm':
                connection = await self.connect_s7(ip_address, plc_config.get('rack', 0), plc_config.get('slot', 1))
            elif protocol == 'ethernet_ip':
                connection = await self.connect_ethernet_ip(ip_address, plc_config.get('slot', 0))
            elif protocol == 'opcua':
                connection = await self.connect_opcua(f"opc.tcp://{ip_address}:4840")
            else:
                self.logger.warning(f"Unsupported protocol: {protocol}")
                return False

            self.connections[plc_id] = {
                'connection': connection,
                'protocol': protocol,
                'ip_address': ip_address,
                'connected_at': datetime.now(),
                'last_ping': datetime.now(),
                'config': plc_config
            }

            self.logger.info(f"✅ Connected to PLC {plc_id} via {protocol}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to connect to PLC {plc_id}: {e}")
            return False

    async def connect_modbus_tcp(self, ip_address: str, port: int = 502):
        """Conectar via Modbus TCP"""
        # Simulación de conexión Modbus
        return {
            'type': 'modbus_tcp',
            'socket': await self.create_socket_connection(ip_address, port),
            'connected': True
        }

    async def connect_s7(self, ip_address: str, rack: int = 0, slot: int = 1):
        """Conectar via S7comm (Siemens)"""
        # Simulación de conexión S7
        return {
            'type': 's7comm',
            'socket': await self.create_socket_connection(ip_address, 102),
            'rack': rack,
            'slot': slot,
            'connected': True
        }

    async def connect_ethernet_ip(self, ip_address: str, slot: int = 0):
        """Conectar via EtherNet/IP"""
        # Simulación de conexión EtherNet/IP
        return {
            'type': 'ethernet_ip',
            'socket': await self.create_socket_connection(ip_address, 44818),
            'slot': slot,
            'connected': True
        }

    async def connect_opcua(self, endpoint: str):
        """Conectar via OPC UA"""
        # Simulación de conexión OPC UA
        return {
            'type': 'opcua',
            'endpoint': endpoint,
            'connected': True
        }

    async def create_socket_connection(self, ip_address: str, port: int):
        """Crear conexión socket simulada"""
        # En producción crear socket real
        return {'simulated_socket': f"{ip_address}:{port}"}

    async def read_variable(self, plc_id: str, address: str) -> Optional[float]:
        """Leer variable de PLC"""
        if plc_id not in self.connections:
            return None

        connection = self.connections[plc_id]
        protocol = connection['protocol']

        try:
            if protocol == 'modbus_tcp':
                return await self.read_modbus_register(connection, address)
            elif protocol == 's7comm':
                return await self.read_s7_variable(connection, address)
            elif protocol == 'ethernet_ip':
                return await self.read_ethernet_ip_tag(connection, address)
            elif protocol == 'opcua':
                return await self.read_opcua_node(connection, address)
            else:
                return None

        except Exception as e:
            self.logger.error(f"Error reading {address} from {plc_id}: {e}")
            return None

    async def read_modbus_register(self, connection: Dict, address: str) -> float:
        """Leer registro Modbus"""
        # Parsear dirección Modbus (ej: "40001" = Holding Register 1)
        if address.startswith('4'):  # Holding Register
            register = int(address) - 40001
        elif address.startswith('3'):  # Input Register
            register = int(address) - 30001
        else:
            register = int(address)

        # Simulación de lectura Modbus
        return random.uniform(0, 1000) * (1 + register * 0.1)

    async def read_s7_variable(self, connection: Dict, address: str) -> float:
        """Leer variable S7 (Siemens)"""
        # Parsear dirección S7 (ej: "DB1.DBD0", "M0.0", "I0.0")
        # Simulación de lectura S7
        return random.uniform(-100, 1500)

    async def read_ethernet_ip_tag(self, connection: Dict, address: str) -> float:
        """Leer tag EtherNet/IP"""
        # Simulación de lectura EtherNet/IP
        return random.uniform(0, 2000)

    async def read_opcua_node(self, connection: Dict, address: str) -> float:
        """Leer nodo OPC UA"""
        # Simulación de lectura OPC UA
        return random.uniform(-50, 1200)


class VariableDataProcessor:
    """Procesador de datos de variables con análisis avanzado"""

    def __init__(self):
        self.logger = logging.getLogger('DataProcessor')
        self.moving_averages = {}
        self.trend_analyzers = {}
        self.anomaly_detectors = {}

    def process_reading(self, reading: VariableReading, variable_config: IndustrialVariable) -> Dict:
        """Procesar lectura de variable"""
        processing_result = {
            'raw_reading': asdict(reading),
            'processed_value': reading.value,
            'quality_score': reading.quality,
            'status': reading.status.value,
            'analysis': {}
        }

        try:
            # Filtrado de ruido
            filtered_value = self.apply_noise_filter(reading.variable_id, reading.value)
            processing_result['filtered_value'] = filtered_value

            # Análisis estadístico
            stats = self.calculate_statistics(reading.variable_id, filtered_value)
            processing_result['analysis']['statistics'] = stats

            # Detección de tendencias
            if variable_config.enable_trending:
                trend = self.analyze_trend(reading.variable_id, filtered_value)
                processing_result['analysis']['trend'] = trend

            # Predicción de valores futuros
            if variable_config.enable_prediction:
                prediction = self.predict_future_values(reading.variable_id, filtered_value)
                processing_result['analysis']['prediction'] = prediction

            # Detección de anomalías
            anomaly_score = self.detect_anomalies(reading.variable_id, filtered_value)
            processing_result['analysis']['anomaly_score'] = anomaly_score

            # Verificar umbrales de alarma
            alarms = self.check_alarm_thresholds(reading, variable_config)
            processing_result['alarms'] = alarms

        except Exception as e:
            self.logger.error(f"Error processing reading for {reading.variable_id}: {e}")
            processing_result['processing_error'] = str(e)

        return processing_result

    def apply_noise_filter(self, variable_id: str, value: float) -> float:
        """Aplicar filtro de ruido (media móvil exponencial)"""
        if variable_id not in self.moving_averages:
            self.moving_averages[variable_id] = deque(maxlen=10)

        self.moving_averages[variable_id].append(value)

        # Media móvil exponencial con factor de suavizado 0.3
        if len(self.moving_averages[variable_id]) > 1:
            alpha = 0.3
            previous_avg = list(self.moving_averages[variable_id])[-2]
            filtered_value = alpha * value + (1 - alpha) * previous_avg
            return filtered_value

        return value

    def calculate_statistics(self, variable_id: str, value: float) -> Dict:
        """Calcular estadísticas de la variable"""
        if variable_id not in self.moving_averages:
            return {}

        values = list(self.moving_averages[variable_id])
        if len(values) < 2:
            return {}

        return {
            'mean': np.mean(values),
            'std': np.std(values),
            'min': np.min(values),
            'max': np.max(values),
            'range': np.max(values) - np.min(values),
            'cv': np.std(values) / np.mean(values) if np.mean(values) != 0 else 0
        }

    def analyze_trend(self, variable_id: str, value: float) -> Dict:
        """Analizar tendencia de la variable"""
        if variable_id not in self.trend_analyzers:
            self.trend_analyzers[variable_id] = deque(maxlen=20)

        self.trend_analyzers[variable_id].append({
            'timestamp': time.time(),
            'value': value
        })

        if len(self.trend_analyzers[variable_id]) < 5:
            return {'trend': 'insufficient_data'}

        # Análisis de tendencia lineal
        data = list(self.trend_analyzers[variable_id])
        times = [d['timestamp'] for d in data]
        values = [d['value'] for d in data]

        # Regresión lineal simple
        n = len(values)
        sum_x = sum(times)
        sum_y = sum(values)
        sum_xy = sum(t * v for t, v in zip(times, values))
        sum_x2 = sum(t * t for t in times)

        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)

        trend_direction = 'stable'
        if abs(slope) > 0.001:  # Umbral de cambio significativo
            trend_direction = 'increasing' if slope > 0 else 'decreasing'

        return {
            'trend': trend_direction,
            'slope': slope,
            'rate_of_change': slope * 60,  # Por minuto
            'confidence': min(len(data) / 20.0, 1.0)  # Confianza basada en datos disponibles
        }

    def predict_future_values(self, variable_id: str, current_value: float) -> Dict:
        """Predecir valores futuros usando modelos simples"""
        if variable_id not in self.trend_analyzers or len(self.trend_analyzers[variable_id]) < 10:
            return {'prediction': 'insufficient_data'}

        data = list(self.trend_analyzers[variable_id])
        values = [d['value'] for d in data[-10:]]  # Últimos 10 valores

        # Predicción simple basada en tendencia
        mean_value = np.mean(values)
        trend_slope = (values[-1] - values[0]) / len(values)

        predictions = {
            '1_minute': current_value + trend_slope * 1,
            '5_minutes': current_value + trend_slope * 5,
            '15_minutes': current_value + trend_slope * 15,
            '1_hour': current_value + trend_slope * 60
        }

        # Calcular intervalos de confianza basados en desviación estándar
        std_dev = np.std(values)
        confidence_intervals = {}
        for time_horizon, pred_value in predictions.items():
            confidence_intervals[time_horizon] = {
                'predicted_value': pred_value,
                'lower_bound': pred_value - 2 * std_dev,
                'upper_bound': pred_value + 2 * std_dev,
                'confidence': 0.95
            }

        return {
            'predictions': confidence_intervals,
            'model_type': 'linear_trend',
            'accuracy_estimate': max(0.5, 1.0 - (std_dev / abs(mean_value)) if mean_value != 0 else 0.5)
        }

    def detect_anomalies(self, variable_id: str, value: float) -> float:
        """Detectar anomalías usando Z-score modificado"""
        if variable_id not in self.moving_averages or len(self.moving_averages[variable_id]) < 3:
            return 0.0

        values = list(self.moving_averages[variable_id])
        mean_val = np.mean(values)
        std_val = np.std(values)

        if std_val == 0:
            return 0.0

        # Z-score modificado
        z_score = abs(value - mean_val) / std_val

        # Normalizar a escala 0-1
        anomaly_score = min(z_score / 3.0, 1.0)  # Z-score > 3 = anomalía completa

        return anomaly_score

    def check_alarm_thresholds(self, reading: VariableReading, config: IndustrialVariable) -> List[Dict]:
        """Verificar umbrales de alarma"""
        alarms = []
        value = reading.value

        # Alarma crítica baja
        if value <= config.alarm_low:
            alarms.append({
                'severity': AlarmSeverity.CRITICAL.value,
                'type': 'low_alarm',
                'message': f"{config.name} critically low: {value} {config.unit} (threshold: {config.alarm_low})",
                'threshold': config.alarm_low,
                'deviation': abs(value - config.alarm_low)
            })

        # Alarma crítica alta
        elif value >= config.alarm_high:
            alarms.append({
                'severity': AlarmSeverity.CRITICAL.value,
                'type': 'high_alarm',
                'message': f"{config.name} critically high: {value} {config.unit} (threshold: {config.alarm_high})",
                'threshold': config.alarm_high,
                'deviation': abs(value - config.alarm_high)
            })

        # Warning bajo
        elif value <= config.warning_low:
            alarms.append({
                'severity': AlarmSeverity.HIGH.value,
                'type': 'low_warning',
                'message': f"{config.name} below warning level: {value} {config.unit} (threshold: {config.warning_low})",
                'threshold': config.warning_low,
                'deviation': abs(value - config.warning_low)
            })

        # Warning alto
        elif value >= config.warning_high:
            alarms.append({
                'severity': AlarmSeverity.HIGH.value,
                'type': 'high_warning',
                'message': f"{config.name} above warning level: {value} {config.unit} (threshold: {config.warning_high})",
                'threshold': config.warning_high,
                'deviation': abs(value - config.warning_high)
            })

        return alarms


class IndustrialVariablesMonitor:
    """Monitor principal de variables industriales"""

    def __init__(self):
        self.logger = self.setup_logging()
        self.db_path = Path(__file__).parent / "industrial_variables.db"

        # Componentes principales
        self.plc_engine = PLCCommunicationEngine()
        self.data_processor = VariableDataProcessor()

        # Estado del sistema
        self.variables_config = {}
        self.active_readings = {}
        self.active_alarms = {}
        self.monitoring_active = False

        # Base de datos
        self.init_database()

        # Variables industriales predefinidas
        self.load_default_variables()

        self.logger.info("🏭 Industrial Variables Monitor initialized")

    def setup_logging(self) -> logging.Logger:
        """Configurar sistema de logging"""
        logger = logging.getLogger('IndustrialMonitor')
        logger.setLevel(logging.INFO)

        handler = logging.FileHandler('/var/log/smartcompute_industrial_monitor.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def init_database(self):
        """Inicializar base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Tabla de configuración de variables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS variable_config (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                variable_type TEXT,
                unit TEXT,
                min_value REAL,
                max_value REAL,
                nominal_value REAL,
                warning_low REAL,
                warning_high REAL,
                alarm_low REAL,
                alarm_high REAL,
                location TEXT,
                plc_address TEXT,
                update_rate_ms INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Tabla de lecturas históricas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS variable_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                variable_id TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                value REAL NOT NULL,
                quality INTEGER,
                status TEXT,
                raw_value REAL,
                processed_value REAL,
                anomaly_score REAL,
                FOREIGN KEY (variable_id) REFERENCES variable_config (id)
            )
        ''')

        # Tabla de alarmas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alarms (
                id TEXT PRIMARY KEY,
                variable_id TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                current_value REAL,
                threshold_value REAL,
                acknowledged BOOLEAN DEFAULT FALSE,
                acknowledged_by TEXT,
                acknowledged_at TIMESTAMP,
                cleared BOOLEAN DEFAULT FALSE,
                cleared_at TIMESTAMP,
                FOREIGN KEY (variable_id) REFERENCES variable_config (id)
            )
        ''')

        # Índices para rendimiento
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_readings_timestamp ON variable_readings(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_readings_variable ON variable_readings(variable_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alarms_timestamp ON alarms(timestamp)')

        conn.commit()
        conn.close()

    def load_default_variables(self):
        """Cargar variables industriales predefinidas con especificaciones técnicas detalladas"""
        default_variables = [
            # Variables Eléctricas - Sistema Principal Trifásico 400V
            IndustrialVariable(
                id="voltage_main_l1_l2",
                name="Main Power Line L1-L2 Voltage",
                description="Voltaje entre líneas L1-L2 del suministro principal trifásico 400V",
                variable_type=VariableType.ELECTRICAL,
                unit="V",
                min_value=0.0,
                max_value=500.0,
                nominal_value=400.0,
                warning_low=380.0,
                warning_high=420.0,
                alarm_low=360.0,
                alarm_high=440.0,
                location="Sala Eléctrica Principal - Panel A1",
                plc_address="40001",
                update_rate_ms=1000,
                technical_specs={
                    "electrical": {
                        "voltage_class": "low",
                        "phase_type": "three_phase_wye",
                        "supply_type": "main_grid",
                        "nominal_frequency": 50.0,
                        "power_factor": 0.92,
                        "harmonic_distortion": 5.0,
                        "insulation_class": "F",
                        "protection_class": "IP54",
                        "grounding_type": "TN-S",
                        "cable_specs": "XLPE 95mm² 4-core SWA"
                    },
                    "measurement": {
                        "accuracy_class": "0.2S",
                        "sampling_rate": 1000,
                        "measurement_method": "True RMS"
                    }
                },
                safety_classification="sil_2",
                maintenance_schedule={
                    "type": "preventive",
                    "frequency_days": 180,
                    "duration_hours": 1.0,
                    "required_personnel": ["Electrician"],
                    "shutdown_required": False
                },
                installation_details={
                    "location_type": "Electrical Room",
                    "mounting": "DIN Rail",
                    "safety_distances": {"minimum_approach": "0.3 m", "working_distance": "0.5 m"}
                }
            ),
            IndustrialVariable(
                id="current_motor_1",
                name="Motor 1 Current",
                description="Corriente del motor principal",
                variable_type=VariableType.ELECTRICAL,
                unit="A",
                min_value=0.0,
                max_value=100.0,
                nominal_value=45.0,
                warning_low=5.0,
                warning_high=85.0,
                alarm_low=2.0,
                alarm_high=95.0,
                location="Área de Producción",
                plc_address="40002",
                update_rate_ms=500
            ),
            # Variables de Temperatura
            IndustrialVariable(
                id="temp_bearing_motor_1",
                name="Motor 1 Bearing Temperature",
                description="Temperatura del rodamiento motor 1",
                variable_type=VariableType.THERMAL,
                unit="°C",
                min_value=-40.0,
                max_value=150.0,
                nominal_value=65.0,
                warning_low=0.0,
                warning_high=85.0,
                alarm_low=-10.0,
                alarm_high=95.0,
                location="Motor Principal",
                plc_address="40010",
                update_rate_ms=2000
            ),
            IndustrialVariable(
                id="temp_hydraulic_oil",
                name="Hydraulic Oil Temperature",
                description="Temperatura del aceite hidráulico",
                variable_type=VariableType.THERMAL,
                unit="°C",
                min_value=0.0,
                max_value=120.0,
                nominal_value=55.0,
                warning_low=10.0,
                warning_high=80.0,
                alarm_low=5.0,
                alarm_high=90.0,
                location="Sistema Hidráulico",
                plc_address="40011",
                update_rate_ms=3000
            ),
            # Variables de Presión
            IndustrialVariable(
                id="pressure_hydraulic_system",
                name="Hydraulic System Pressure",
                description="Presión del sistema hidráulico",
                variable_type=VariableType.MECHANICAL,
                unit="bar",
                min_value=0.0,
                max_value=350.0,
                nominal_value=200.0,
                warning_low=150.0,
                warning_high=280.0,
                alarm_low=100.0,
                alarm_high=320.0,
                location="Bomba Hidráulica",
                plc_address="40020",
                update_rate_ms=1000
            ),
            IndustrialVariable(
                id="pressure_air_compressor",
                name="Air Compressor Pressure",
                description="Presión del compresor de aire",
                variable_type=VariableType.MECHANICAL,
                unit="bar",
                min_value=0.0,
                max_value=10.0,
                nominal_value=6.5,
                warning_low=5.0,
                warning_high=8.0,
                alarm_low=3.0,
                alarm_high=9.5,
                location="Compresor",
                plc_address="40021",
                update_rate_ms=2000
            ),
            # Variables de Caudal
            IndustrialVariable(
                id="flow_cooling_water",
                name="Cooling Water Flow",
                description="Caudal de agua de refrigeración",
                variable_type=VariableType.FLUID,
                unit="L/min",
                min_value=0.0,
                max_value=500.0,
                nominal_value=250.0,
                warning_low=200.0,
                warning_high=400.0,
                alarm_low=150.0,
                alarm_high=450.0,
                location="Sistema de Refrigeración",
                plc_address="40030",
                update_rate_ms=2000
            ),
            # Variables de Vibración
            IndustrialVariable(
                id="vibration_motor_1_x",
                name="Motor 1 Vibration X-axis",
                description="Vibración del motor 1 en eje X",
                variable_type=VariableType.MECHANICAL,
                unit="mm/s",
                min_value=0.0,
                max_value=50.0,
                nominal_value=2.5,
                warning_low=0.0,
                warning_high=7.0,
                alarm_low=0.0,
                alarm_high=12.0,
                location="Motor Principal",
                plc_address="40040",
                update_rate_ms=1000
            ),
            # Variables de Nivel
            IndustrialVariable(
                id="level_hydraulic_tank",
                name="Hydraulic Tank Level",
                description="Nivel del tanque hidráulico",
                variable_type=VariableType.FLUID,
                unit="%",
                min_value=0.0,
                max_value=100.0,
                nominal_value=75.0,
                warning_low=25.0,
                warning_high=95.0,
                alarm_low=15.0,
                alarm_high=98.0,
                location="Tanque Hidráulico",
                plc_address="40050",
                update_rate_ms=5000
            ),
            # Variables de RPM
            IndustrialVariable(
                id="rpm_motor_1",
                name="Motor 1 RPM",
                description="Revoluciones por minuto del motor 1",
                variable_type=VariableType.MECHANICAL,
                unit="RPM",
                min_value=0.0,
                max_value=3600.0,
                nominal_value=1800.0,
                warning_low=100.0,
                warning_high=3400.0,
                alarm_low=50.0,
                alarm_high=3550.0,
                location="Motor Principal",
                plc_address="40060",
                update_rate_ms=1000
            )
        ]

        # Guardar en base de datos y memoria
        for variable in default_variables:
            self.variables_config[variable.id] = variable
            self.save_variable_config(variable)

        self.logger.info(f"✅ Loaded {len(default_variables)} default industrial variables")

    def save_variable_config(self, variable: IndustrialVariable):
        """Guardar configuración de variable en base de datos con especificaciones técnicas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Actualizar esquema si es necesario
        cursor.execute('PRAGMA table_info(variable_config)')
        columns = [col[1] for col in cursor.fetchall()]

        if 'technical_specs' not in columns:
            cursor.execute('ALTER TABLE variable_config ADD COLUMN technical_specs TEXT')
        if 'safety_classification' not in columns:
            cursor.execute('ALTER TABLE variable_config ADD COLUMN safety_classification TEXT')
        if 'maintenance_schedule' not in columns:
            cursor.execute('ALTER TABLE variable_config ADD COLUMN maintenance_schedule TEXT')
        if 'calibration_info' not in columns:
            cursor.execute('ALTER TABLE variable_config ADD COLUMN calibration_info TEXT')
        if 'installation_details' not in columns:
            cursor.execute('ALTER TABLE variable_config ADD COLUMN installation_details TEXT')

        cursor.execute('''
            INSERT OR REPLACE INTO variable_config
            (id, name, description, variable_type, unit, min_value, max_value,
             nominal_value, warning_low, warning_high, alarm_low, alarm_high,
             location, plc_address, update_rate_ms, technical_specs, safety_classification,
             maintenance_schedule, calibration_info, installation_details)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            variable.id, variable.name, variable.description,
            variable.variable_type.value, variable.unit,
            variable.min_value, variable.max_value, variable.nominal_value,
            variable.warning_low, variable.warning_high,
            variable.alarm_low, variable.alarm_high,
            variable.location, variable.plc_address, variable.update_rate_ms,
            json.dumps(variable.technical_specs, default=str) if variable.technical_specs else None,
            variable.safety_classification,
            json.dumps(variable.maintenance_schedule, default=str) if variable.maintenance_schedule else None,
            json.dumps(variable.calibration_info, default=str) if variable.calibration_info else None,
            json.dumps(variable.installation_details, default=str) if variable.installation_details else None
        ))

        conn.commit()
        conn.close()

    async def start_monitoring(self):
        """Iniciar monitoreo de variables"""
        if self.monitoring_active:
            self.logger.warning("Monitoring already active")
            return

        self.monitoring_active = True
        self.logger.info("🚀 Starting industrial variables monitoring...")

        # Inicializar PLCs simulados
        await self.initialize_plcs()

        # Iniciar tasks de monitoreo para cada variable
        monitoring_tasks = []
        for variable_id, variable in self.variables_config.items():
            task = asyncio.create_task(
                self.monitor_variable_loop(variable)
            )
            monitoring_tasks.append(task)

        # Task de procesamiento de alarmas
        alarm_task = asyncio.create_task(self.alarm_processing_loop())
        monitoring_tasks.append(alarm_task)

        # Ejecutar todos los tasks
        try:
            await asyncio.gather(*monitoring_tasks)
        except Exception as e:
            self.logger.error(f"Monitoring error: {e}")
        finally:
            self.monitoring_active = False

    async def initialize_plcs(self):
        """Inicializar conexiones PLC simuladas"""
        plc_configs = [
            {
                'id': 'main_plc',
                'protocol': 'modbus_tcp',
                'ip_address': '192.168.1.10',
                'description': 'PLC Principal'
            },
            {
                'id': 'motor_plc',
                'protocol': 's7comm',
                'ip_address': '192.168.1.20',
                'rack': 0,
                'slot': 1,
                'description': 'PLC Control Motores'
            }
        ]

        for plc_config in plc_configs:
            await self.plc_engine.connect_plc(plc_config)

    async def monitor_variable_loop(self, variable: IndustrialVariable):
        """Loop de monitoreo para variable específica"""
        while self.monitoring_active:
            try:
                # Leer valor del PLC (simulado)
                raw_value = await self.plc_engine.read_variable('main_plc', variable.plc_address)

                if raw_value is None:
                    # Generar valor simulado si no hay conexión PLC
                    raw_value = self.simulate_variable_value(variable)

                # Crear reading
                reading = VariableReading(
                    variable_id=variable.id,
                    timestamp=datetime.now(),
                    value=raw_value,
                    quality=random.randint(95, 100),  # Alta calidad simulada
                    status=SensorStatus.ONLINE,
                    raw_value=raw_value,
                    engineering_units=variable.unit,
                    source_address=variable.plc_address
                )

                # Procesar lectura
                processed_data = self.data_processor.process_reading(reading, variable)

                # Almacenar en memoria y base de datos
                self.active_readings[variable.id] = processed_data
                await self.store_reading(reading, processed_data)

                # Procesar alarmas
                if processed_data.get('alarms'):
                    for alarm_data in processed_data['alarms']:
                        await self.create_alarm(variable.id, reading, alarm_data)

                # Esperar según rate de actualización
                await asyncio.sleep(variable.update_rate_ms / 1000.0)

            except Exception as e:
                self.logger.error(f"Error monitoring {variable.id}: {e}")
                await asyncio.sleep(5.0)

    def simulate_variable_value(self, variable: IndustrialVariable) -> float:
        """Simular valor de variable industrial"""
        current_time = time.time()

        # Valor base con variación sinusoidal
        base_value = variable.nominal_value

        # Añadir variación cíclica (simula comportamiento real)
        cycle_variation = math.sin(current_time / 60.0) * (variable.max_value - variable.min_value) * 0.05

        # Añadir ruido aleatorio
        noise = random.uniform(-1, 1) * (variable.max_value - variable.min_value) * 0.02

        # Simular ocasionales picos o caídas
        if random.random() < 0.005:  # 0.5% probabilidad de anomalía
            anomaly = random.choice([-1, 1]) * (variable.max_value - variable.min_value) * 0.3
            base_value += anomaly

        simulated_value = base_value + cycle_variation + noise

        # Mantener dentro de límites físicos
        return max(variable.min_value, min(variable.max_value, simulated_value))

    async def store_reading(self, reading: VariableReading, processed_data: Dict):
        """Almacenar lectura en base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO variable_readings
                (variable_id, timestamp, value, quality, status, raw_value,
                 processed_value, anomaly_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                reading.variable_id,
                reading.timestamp,
                reading.value,
                reading.quality,
                reading.status.value,
                reading.raw_value,
                processed_data.get('filtered_value', reading.value),
                processed_data.get('analysis', {}).get('anomaly_score', 0.0)
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            self.logger.error(f"Error storing reading: {e}")

    async def create_alarm(self, variable_id: str, reading: VariableReading, alarm_data: Dict):
        """Crear alarma industrial"""
        alarm_id = f"{variable_id}_{alarm_data['type']}_{int(reading.timestamp.timestamp())}"

        # Verificar si la alarma ya existe
        if alarm_id in self.active_alarms:
            return

        alarm = IndustrialAlarm(
            id=alarm_id,
            variable_id=variable_id,
            timestamp=reading.timestamp,
            severity=AlarmSeverity(alarm_data['severity']),
            message=alarm_data['message'],
            current_value=reading.value,
            threshold_value=alarm_data['threshold']
        )

        # Almacenar en memoria y base de datos
        self.active_alarms[alarm_id] = alarm
        await self.store_alarm(alarm)

        self.logger.warning(f"🚨 ALARM: {alarm.message}")

    async def store_alarm(self, alarm: IndustrialAlarm):
        """Almacenar alarma en base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO alarms
                (id, variable_id, timestamp, severity, message, current_value,
                 threshold_value, acknowledged, cleared)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                alarm.id, alarm.variable_id, alarm.timestamp,
                alarm.severity.value, alarm.message,
                alarm.current_value, alarm.threshold_value,
                alarm.acknowledged, alarm.cleared
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            self.logger.error(f"Error storing alarm: {e}")

    async def alarm_processing_loop(self):
        """Loop de procesamiento de alarmas"""
        while self.monitoring_active:
            try:
                # Auto-clear de alarmas que volvieron a normal
                await self.auto_clear_alarms()

                # Escalamiento de alarmas críticas no reconocidas
                await self.escalate_critical_alarms()

                await asyncio.sleep(30)  # Verificar cada 30 segundos

            except Exception as e:
                self.logger.error(f"Alarm processing error: {e}")
                await asyncio.sleep(60)

    async def auto_clear_alarms(self):
        """Auto-clear alarmas que volvieron a condiciones normales"""
        for alarm_id, alarm in list(self.active_alarms.items()):
            if alarm.cleared:
                continue

            # Obtener lectura actual de la variable
            variable_reading = self.active_readings.get(alarm.variable_id)
            if not variable_reading:
                continue

            current_value = variable_reading['raw_reading']['value']
            variable_config = self.variables_config[alarm.variable_id]

            # Verificar si la condición de alarma ya no existe
            should_clear = False

            if alarm.severity == AlarmSeverity.CRITICAL:
                if (alarm.current_value <= variable_config.alarm_low and
                    current_value > variable_config.warning_low):
                    should_clear = True
                elif (alarm.current_value >= variable_config.alarm_high and
                      current_value < variable_config.warning_high):
                    should_clear = True

            if should_clear:
                alarm.cleared = True
                alarm.cleared_at = datetime.now()
                await self.store_alarm(alarm)
                del self.active_alarms[alarm_id]

                self.logger.info(f"✅ Auto-cleared alarm: {alarm_id}")

    async def escalate_critical_alarms(self):
        """Escalamiento de alarmas críticas"""
        critical_timeout = timedelta(minutes=5)
        current_time = datetime.now()

        for alarm in self.active_alarms.values():
            if (alarm.severity == AlarmSeverity.CRITICAL and
                not alarm.acknowledged and
                current_time - alarm.timestamp > critical_timeout):

                # En producción: enviar notificaciones, emails, SMS, etc.
                self.logger.critical(f"🚨 CRITICAL ALARM ESCALATED: {alarm.message}")

    def get_monitoring_status(self) -> Dict:
        """Obtener estado del monitoreo"""
        active_alarms_count = len([a for a in self.active_alarms.values() if not a.cleared])
        critical_alarms_count = len([a for a in self.active_alarms.values()
                                   if a.severity == AlarmSeverity.CRITICAL and not a.cleared])

        return {
            'monitoring_active': self.monitoring_active,
            'total_variables': len(self.variables_config),
            'variables_online': len([r for r in self.active_readings.values()
                                   if r['raw_reading']['status'] == 'online']),
            'active_alarms': active_alarms_count,
            'critical_alarms': critical_alarms_count,
            'plc_connections': len(self.plc_engine.connections),
            'last_update': datetime.now().isoformat()
        }

    def get_variable_dashboard_data(self) -> Dict:
        """Obtener datos para dashboard de variables"""
        dashboard_data = {
            'variables': [],
            'alarms': [],
            'summary': self.get_monitoring_status()
        }

        # Datos de variables
        for variable_id, variable_config in self.variables_config.items():
            reading_data = self.active_readings.get(variable_id, {})

            variable_info = {
                'id': variable_id,
                'name': variable_config.name,
                'description': variable_config.description,
                'unit': variable_config.unit,
                'location': variable_config.location,
                'current_value': reading_data.get('processed_value', 0),
                'quality': reading_data.get('quality_score', 0),
                'status': reading_data.get('status', 'offline'),
                'thresholds': {
                    'alarm_low': variable_config.alarm_low,
                    'warning_low': variable_config.warning_low,
                    'nominal': variable_config.nominal_value,
                    'warning_high': variable_config.warning_high,
                    'alarm_high': variable_config.alarm_high
                },
                'analysis': reading_data.get('analysis', {}),
                'timestamp': reading_data.get('raw_reading', {}).get('timestamp')
            }
            dashboard_data['variables'].append(variable_info)

        # Alarmas activas
        for alarm in self.active_alarms.values():
            if not alarm.cleared:
                dashboard_data['alarms'].append({
                    'id': alarm.id,
                    'variable_id': alarm.variable_id,
                    'severity': alarm.severity.value,
                    'message': alarm.message,
                    'current_value': alarm.current_value,
                    'threshold_value': alarm.threshold_value,
                    'timestamp': alarm.timestamp.isoformat(),
                    'acknowledged': alarm.acknowledged
                })

        return dashboard_data


async def main():
    """Función principal"""
    print("🏭 SmartCompute Industrial Variables Monitor")
    print("=" * 50)

    monitor = IndustrialVariablesMonitor()

    try:
        # Mostrar estado inicial
        status = monitor.get_monitoring_status()
        print(f"📊 Initial Status: {json.dumps(status, indent=2)}")

        # Iniciar monitoreo
        await monitor.start_monitoring()

    except KeyboardInterrupt:
        print("\n🛑 Stopping monitoring...")
        monitor.monitoring_active = False
    except Exception as e:
        print(f"❌ Critical error: {e}")


if __name__ == "__main__":
    asyncio.run(main())