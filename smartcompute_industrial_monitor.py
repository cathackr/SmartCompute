#!/usr/bin/env python3
"""
SmartCompute Industrial - Monitor de Sistemas Industriales
=========================================================

Monitor avanzado para entornos industriales con detección de:
- Protocolos industriales (Modbus, EtherNet/IP, PROFINET, etc.)
- PLCs y sus especificaciones
- Sensores en tiempo real
- Estados de interruptores manuales
- Mensajes SCADA y logs
- Recomendaciones ISA/IEC
"""

import json
import struct
import socket
import threading
import time
import psutil
import subprocess
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import asyncio
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class IndustrialProtocol:
    """Información de protocolo industrial detectado"""
    name: str
    port: int
    description: str
    detected: bool = False
    traffic_count: int = 0
    last_seen: str = ""

@dataclass
class PLCDevice:
    """Información de dispositivo PLC"""
    ip_address: str
    mac_address: str
    manufacturer: str
    model: str
    firmware_version: str
    protocol: str
    status: str
    last_communication: str
    error_count: int = 0
    rack_slot: str = ""

@dataclass
class IndustrialSensor:
    """Sensor industrial en tiempo real"""
    id: str
    name: str
    type: str  # temperature, humidity, pressure, voltage, current, etc.
    value: float
    unit: str
    timestamp: str
    status: str  # normal, warning, critical, offline
    min_threshold: float = 0.0
    max_threshold: float = 100.0
    location: str = ""

@dataclass
class ManualSwitch:
    """Interruptor manual industrial"""
    id: str
    name: str
    type: str  # emergency_stop, selector, pushbutton, etc.
    state: str  # on, off, pressed, released
    location: str
    last_changed: str
    maintenance_due: bool = False

@dataclass
class SCADAMessage:
    """Mensaje del sistema SCADA"""
    timestamp: str
    source: str
    destination: str
    message_type: str
    content: str
    priority: str  # low, medium, high, critical
    acknowledged: bool = False

class SmartComputeIndustrialMonitor:
    """Monitor principal para sistemas industriales"""

    def __init__(self):
        self.protocols = self._initialize_protocols()
        self.plcs: List[PLCDevice] = []
        self.sensors: List[IndustrialSensor] = []
        self.switches: List[ManualSwitch] = []
        self.scada_messages: List[SCADAMessage] = []
        self.monitoring_active = False

        # Contadores de rendimiento
        self.stats = {
            'protocols_detected': 0,
            'plcs_discovered': 0,
            'sensors_active': 0,
            'messages_processed': 0,
            'errors_detected': 0,
            'start_time': datetime.now().isoformat()
        }

    def _initialize_protocols(self) -> Dict[str, IndustrialProtocol]:
        """Inicializar protocolos industriales conocidos"""
        protocols = {
            'modbus_tcp': IndustrialProtocol(
                name="Modbus TCP",
                port=502,
                description="Protocolo Modbus sobre TCP/IP"
            ),
            'ethernet_ip': IndustrialProtocol(
                name="EtherNet/IP",
                port=44818,
                description="Protocolo EtherNet/IP (Allen-Bradley)"
            ),
            'profinet': IndustrialProtocol(
                name="PROFINET",
                port=102,
                description="Protocolo PROFINET (Siemens)"
            ),
            'opcua': IndustrialProtocol(
                name="OPC UA",
                port=4840,
                description="OPC Unified Architecture"
            ),
            'dnp3': IndustrialProtocol(
                name="DNP3",
                port=20000,
                description="Distributed Network Protocol 3"
            ),
            'bacnet': IndustrialProtocol(
                name="BACnet",
                port=47808,
                description="Building Automation and Control Networks"
            ),
            's7comm': IndustrialProtocol(
                name="S7comm",
                port=102,
                description="Siemens S7 Communication"
            ),
            'fins': IndustrialProtocol(
                name="FINS",
                port=9600,
                description="Factory Interface Network Service (Omron)"
            )
        }
        return protocols

    async def scan_industrial_protocols(self) -> Dict[str, Any]:
        """Escanear protocolos industriales activos"""
        logger.info("Iniciando escaneo de protocolos industriales...")

        # Obtener conexiones de red activas
        connections = psutil.net_connections(kind='inet')
        protocol_results = {}

        for proto_id, protocol in self.protocols.items():
            protocol.detected = False
            protocol.traffic_count = 0

            # Buscar conexiones en el puerto del protocolo
            for conn in connections:
                if conn.laddr and conn.laddr.port == protocol.port:
                    protocol.detected = True
                    protocol.traffic_count += 1
                    protocol.last_seen = datetime.now().isoformat()
                    self.stats['protocols_detected'] += 1

            protocol_results[proto_id] = asdict(protocol)

        # Escaneo adicional de puertos industriales comunes
        await self._deep_scan_industrial_ports()

        return protocol_results

    async def _deep_scan_industrial_ports(self):
        """Escaneo profundo de puertos industriales"""
        industrial_ports = [502, 102, 4840, 20000, 47808, 44818, 9600, 1962, 2404]

        for port in industrial_ports:
            try:
                # Escaneo TCP
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('127.0.0.1', port))
                if result == 0:
                    logger.info(f"Puerto industrial {port} activo localmente")
                sock.close()

                # Escaneo de red local
                await self._scan_network_range(port)

            except Exception as e:
                logger.debug(f"Error escaneando puerto {port}: {e}")

    async def _scan_network_range(self, port: int):
        """Escanear rango de red local para un puerto específico"""
        try:
            # Obtener IP de la red local
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            network = '.'.join(local_ip.split('.')[:-1]) + '.'

            tasks = []
            for i in range(1, 255):
                target_ip = f"{network}{i}"
                tasks.append(self._check_industrial_device(target_ip, port))

            await asyncio.gather(*tasks, return_exceptions=True)

        except Exception as e:
            logger.debug(f"Error en escaneo de red: {e}")

    async def _check_industrial_device(self, ip: str, port: int):
        """Verificar si hay un dispositivo industrial en IP:Puerto"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((ip, port))

            if result == 0:
                # Intentar identificar el dispositivo
                device_info = await self._identify_plc_device(ip, port)
                if device_info:
                    self.plcs.append(device_info)
                    self.stats['plcs_discovered'] += 1

            sock.close()

        except Exception as e:
            logger.debug(f"Error verificando {ip}:{port}: {e}")

    async def _identify_plc_device(self, ip: str, port: int) -> Optional[PLCDevice]:
        """Identificar dispositivo PLC específico"""
        try:
            # Obtener MAC address si es posible
            mac_address = self._get_mac_address(ip)

            # Identificar fabricante por puerto y patrones
            manufacturer, model = self._identify_manufacturer_model(port)

            # Intentar obtener versión de firmware (simulado)
            firmware_version = await self._get_firmware_version(ip, port)

            plc = PLCDevice(
                ip_address=ip,
                mac_address=mac_address or "Unknown",
                manufacturer=manufacturer,
                model=model,
                firmware_version=firmware_version,
                protocol=self._get_protocol_by_port(port),
                status="Online",
                last_communication=datetime.now().isoformat(),
                rack_slot="0/1"  # Ejemplo
            )

            logger.info(f"PLC detectado: {manufacturer} {model} en {ip}:{port}")
            return plc

        except Exception as e:
            logger.debug(f"Error identificando PLC en {ip}:{port}: {e}")
            return None

    def _get_mac_address(self, ip: str) -> Optional[str]:
        """Obtener MAC address de una IP"""
        try:
            # Usar ARP para obtener MAC
            result = subprocess.run(['arp', '-n', ip],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if ip in line:
                        parts = line.split()
                        if len(parts) >= 3:
                            mac = parts[2]
                            if ':' in mac and len(mac) == 17:
                                return mac.upper()
        except:
            pass
        return None

    def _identify_manufacturer_model(self, port: int) -> Tuple[str, str]:
        """Identificar fabricante y modelo por puerto"""
        port_mappings = {
            502: ("Generic", "Modbus Device"),
            44818: ("Rockwell Automation", "CompactLogix/ControlLogix"),
            102: ("Siemens", "S7-1200/1500"),
            4840: ("Generic", "OPC UA Server"),
            20000: ("Generic", "DNP3 Device"),
            47808: ("Generic", "BACnet Device"),
            9600: ("Omron", "CJ/CS/CP Series")
        }
        return port_mappings.get(port, ("Unknown", "Unknown"))

    def _get_protocol_by_port(self, port: int) -> str:
        """Obtener protocolo por puerto"""
        protocol_map = {
            502: "Modbus TCP",
            44818: "EtherNet/IP",
            102: "PROFINET/S7comm",
            4840: "OPC UA",
            20000: "DNP3",
            47808: "BACnet",
            9600: "FINS"
        }
        return protocol_map.get(port, "Unknown")

    async def _get_firmware_version(self, ip: str, port: int) -> str:
        """Obtener versión de firmware (simulado para este ejemplo)"""
        # En un entorno real, esto haría consultas específicas del protocolo
        versions = ["V2.8.1", "V3.1.4", "V4.0.2", "V1.7.3", "V5.2.1"]
        import random
        return random.choice(versions)

    def simulate_sensor_data(self) -> List[IndustrialSensor]:
        """Simular datos de sensores industriales en tiempo real"""
        import random

        sensor_templates = [
            ("TEMP_001", "Temperatura Reactor", "temperature", "°C", 15.0, 85.0),
            ("HUM_002", "Humedad Ambiente", "humidity", "%", 30.0, 80.0),
            ("PRES_003", "Presión Hidráulica", "pressure", "bar", 0.0, 50.0),
            ("VOLT_004", "Voltaje Motor A", "voltage", "V", 200.0, 240.0),
            ("CURR_005", "Corriente Bomba", "current", "A", 5.0, 15.0),
            ("FLOW_006", "Flujo Agua", "flow", "L/min", 10.0, 100.0),
            ("VIB_007", "Vibración Eje", "vibration", "mm/s", 0.0, 10.0),
            ("RPM_008", "Velocidad Motor", "speed", "RPM", 1000, 3000)
        ]

        sensors = []
        for sensor_id, name, sensor_type, unit, min_val, max_val in sensor_templates:
            # Generar valor aleatorio dentro del rango
            value = round(random.uniform(min_val, max_val), 2)

            # Determinar status basado en umbrales
            if value < min_val * 1.1 or value > max_val * 0.9:
                status = "warning" if random.random() > 0.3 else "critical"
            else:
                status = "normal"

            sensor = IndustrialSensor(
                id=sensor_id,
                name=name,
                type=sensor_type,
                value=value,
                unit=unit,
                timestamp=datetime.now().isoformat(),
                status=status,
                min_threshold=min_val,
                max_threshold=max_val,
                location=f"Línea {random.randint(1,5)}"
            )
            sensors.append(sensor)

        self.sensors = sensors
        self.stats['sensors_active'] = len(sensors)
        return sensors

    def simulate_manual_switches(self) -> List[ManualSwitch]:
        """Simular estados de interruptores manuales"""
        import random

        switch_templates = [
            ("ES_001", "Parada Emergencia Línea 1", "emergency_stop"),
            ("SEL_002", "Selector Modo Auto/Manual", "selector"),
            ("PB_003", "Botón Reset Alarmas", "pushbutton"),
            ("SW_004", "Interruptor Principal", "main_switch"),
            ("ES_005", "Parada Emergencia Línea 2", "emergency_stop"),
            ("PB_006", "Botón Inicio Ciclo", "pushbutton")
        ]

        switches = []
        for switch_id, name, switch_type in switch_templates:
            # Estados aleatorios realistas
            if switch_type == "emergency_stop":
                state = "released" if random.random() > 0.05 else "pressed"
            elif switch_type == "selector":
                state = random.choice(["auto", "manual", "off"])
            else:
                state = "on" if random.random() > 0.3 else "off"

            switch = ManualSwitch(
                id=switch_id,
                name=name,
                type=switch_type,
                state=state,
                location=f"Panel {random.randint(1,3)}",
                last_changed=datetime.now().isoformat(),
                maintenance_due=random.random() < 0.1
            )
            switches.append(switch)

        self.switches = switches
        return switches

    def simulate_scada_messages(self) -> List[SCADAMessage]:
        """Simular mensajes del sistema SCADA"""
        import random

        message_templates = [
            ("HMI_001", "PLC_001", "alarm", "Temperatura alta en reactor", "high"),
            ("PLC_002", "SCADA_SRV", "status", "Bomba B iniciada correctamente", "low"),
            ("SENSOR_003", "HMI_001", "data", "Lectura presión: 25.4 bar", "medium"),
            ("PLC_001", "MAINTENANCE", "error", "Fallo comunicación módulo I/O", "critical"),
            ("OPERATOR", "PLC_002", "command", "Cambio a modo manual solicitado", "medium"),
            ("SAFETY_SYS", "ALL", "emergency", "Sistema de seguridad activado", "critical")
        ]

        messages = []
        for _ in range(random.randint(5, 15)):
            source, dest, msg_type, content, priority = random.choice(message_templates)

            message = SCADAMessage(
                timestamp=datetime.now().isoformat(),
                source=source,
                destination=dest,
                message_type=msg_type,
                content=content,
                priority=priority,
                acknowledged=random.random() > 0.4
            )
            messages.append(message)

        self.scada_messages = messages
        self.stats['messages_processed'] = len(messages)
        return messages

    def analyze_industrial_system(self) -> Dict[str, Any]:
        """Análisis completo del sistema industrial"""
        logger.info("Iniciando análisis completo del sistema industrial...")

        analysis = {
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': 0,
            'protocols': {},
            'plcs': [],
            'sensors': [],
            'switches': [],
            'scada_messages': [],
            'statistics': self.stats,
            'alerts': [],
            'recommendations': []
        }

        start_time = time.time()

        try:
            # Escanear protocolos (simulado para demo)
            analysis['protocols'] = {
                proto_id: asdict(proto) for proto_id, proto in self.protocols.items()
            }

            # Simular detección de algunos protocolos
            import random
            detected_protocols = random.sample(list(self.protocols.keys()), 3)
            for proto_id in detected_protocols:
                self.protocols[proto_id].detected = True
                self.protocols[proto_id].traffic_count = random.randint(10, 100)
                self.protocols[proto_id].last_seen = datetime.now().isoformat()
                analysis['protocols'][proto_id] = asdict(self.protocols[proto_id])

            # Simular PLCs detectados
            self._simulate_detected_plcs()
            analysis['plcs'] = [asdict(plc) for plc in self.plcs]

            # Generar datos de sensores
            analysis['sensors'] = [asdict(sensor) for sensor in self.simulate_sensor_data()]

            # Estados de interruptores
            analysis['switches'] = [asdict(switch) for switch in self.simulate_manual_switches()]

            # Mensajes SCADA
            analysis['scada_messages'] = [asdict(msg) for msg in self.simulate_scada_messages()]

            # Generar alertas
            analysis['alerts'] = self._generate_industrial_alerts()

            # Generar recomendaciones ISA/IEC
            analysis['recommendations'] = self._generate_isa_iec_recommendations()

            analysis['duration_seconds'] = round(time.time() - start_time, 2)

            logger.info(f"Análisis completado en {analysis['duration_seconds']} segundos")

        except Exception as e:
            logger.error(f"Error durante análisis: {e}")
            analysis['error'] = str(e)

        return analysis

    def _simulate_detected_plcs(self):
        """Simular PLCs detectados"""
        plc_examples = [
            PLCDevice(
                ip_address="192.168.1.100",
                mac_address="00:1B:1B:12:34:56",
                manufacturer="Allen-Bradley",
                model="CompactLogix 5380",
                firmware_version="V32.011",
                protocol="EtherNet/IP",
                status="Online",
                last_communication=datetime.now().isoformat(),
                rack_slot="0/1"
            ),
            PLCDevice(
                ip_address="192.168.1.101",
                mac_address="00:0F:25:78:9A:BC",
                manufacturer="Siemens",
                model="S7-1515-2 PN",
                firmware_version="V2.8.1",
                protocol="PROFINET",
                status="Online",
                last_communication=datetime.now().isoformat(),
                rack_slot="0/2"
            )
        ]
        self.plcs.extend(plc_examples)
        self.stats['plcs_discovered'] = len(self.plcs)

    def _generate_industrial_alerts(self) -> List[Dict[str, Any]]:
        """Generar alertas del sistema industrial"""
        alerts = []

        # Alertas de sensores críticos
        for sensor in self.sensors:
            if sensor.status == "critical":
                alerts.append({
                    'id': f"SENSOR_ALERT_{sensor.id}",
                    'type': 'sensor_critical',
                    'severity': 'high',
                    'message': f"Sensor {sensor.name} en estado crítico: {sensor.value} {sensor.unit}",
                    'source': sensor.id,
                    'timestamp': datetime.now().isoformat(),
                    'acknowledged': False
                })

        # Alertas de comunicación PLC
        for plc in self.plcs:
            if plc.error_count > 0:
                alerts.append({
                    'id': f"PLC_COMM_{plc.ip_address.replace('.', '_')}",
                    'type': 'communication_error',
                    'severity': 'medium',
                    'message': f"Errores de comunicación detectados en PLC {plc.model}",
                    'source': plc.ip_address,
                    'timestamp': datetime.now().isoformat(),
                    'acknowledged': False
                })

        # Alertas de seguridad
        emergency_stops = [sw for sw in self.switches if sw.type == "emergency_stop" and sw.state == "pressed"]
        for es in emergency_stops:
            alerts.append({
                'id': f"EMERGENCY_STOP_{es.id}",
                'type': 'safety_system',
                'severity': 'critical',
                'message': f"Parada de emergencia activada: {es.name}",
                'source': es.id,
                'timestamp': datetime.now().isoformat(),
                'acknowledged': False
            })

        self.stats['errors_detected'] = len(alerts)
        return alerts

    def _generate_isa_iec_recommendations(self) -> List[Dict[str, Any]]:
        """Generar recomendaciones basadas en estándares ISA/IEC"""
        recommendations = []

        # ISA-95 (Enterprise-Control System Integration)
        recommendations.append({
            'standard': 'ISA-95',
            'title': 'Integración Sistema de Control Empresarial',
            'category': 'integration',
            'priority': 'high',
            'description': 'Implementar arquitectura ISA-95 para mejor integración entre niveles',
            'technical_details': [
                'Definir claramente los niveles 0-4 de la pirámide de automatización',
                'Implementar interfaces estándar entre MES y sistemas de control',
                'Establecer modelos de datos consistentes para intercambio de información'
            ],
            'recommendations': [
                'Configurar gateway OPC UA para comunicación entre niveles',
                'Implementar base de datos histórica centralizada',
                'Definir workflows de producción estándar'
            ],
            'applicable_to': ['PLC Systems', 'SCADA', 'MES Integration']
        })

        # IEC 61511 (Functional Safety)
        recommendations.append({
            'standard': 'IEC 61511',
            'title': 'Safety Instrumented Systems (SIS)',
            'category': 'safety',
            'priority': 'critical',
            'description': 'Implementar sistemas instrumentados de seguridad según IEC 61511',
            'technical_details': [
                'Realizar análisis SIL (Safety Integrity Level) para funciones críticas',
                'Implementar arquitectura 2oo3 para sistemas críticos',
                'Establecer procedimientos de prueba periódica automática'
            ],
            'recommendations': [
                'Configurar sistemas de parada de emergencia independientes',
                'Implementar diagnósticos automáticos de seguridad',
                'Establecer bypass controlado con autorización'
            ],
            'applicable_to': ['Emergency Stop Systems', 'Safety PLCs', 'Process Interlocks']
        })

        # IEC 62443 (Industrial Communication Networks - Cybersecurity)
        recommendations.append({
            'standard': 'IEC 62443',
            'title': 'Ciberseguridad en Redes Industriales',
            'category': 'cybersecurity',
            'priority': 'high',
            'description': 'Implementar medidas de ciberseguridad según IEC 62443',
            'technical_details': [
                'Establecer zonas y conductos de seguridad (Security Zones & Conduits)',
                'Implementar autenticación y autorización robusta',
                'Configurar monitoreo continuo de amenazas'
            ],
            'recommendations': [
                'Segmentar redes industriales con firewalls especializados',
                'Implementar autenticación de dos factores para acceso a PLCs',
                'Configurar logging y monitoreo de eventos de seguridad'
            ],
            'applicable_to': ['Network Infrastructure', 'PLC Access', 'SCADA Systems']
        })

        # ISA-101 (Human Machine Interface)
        recommendations.append({
            'standard': 'ISA-101',
            'title': 'Interfaz Humano-Máquina',
            'category': 'hmi',
            'priority': 'medium',
            'description': 'Optimizar interfaces de usuario según principios ISA-101',
            'technical_details': [
                'Implementar jerarquía de pantallas según filosofía de operación',
                'Usar colores y símbolos estándar para indicación de estados',
                'Minimizar sobrecarga de información en pantallas críticas'
            ],
            'recommendations': [
                'Rediseñar pantallas SCADA con navegación intuitiva',
                'Implementar sistema de alarmas por prioridad',
                'Configurar pantallas de visión general (overview) efectivas'
            ],
            'applicable_to': ['SCADA Interface', 'HMI Panels', 'Operator Workstations']
        })

        # IEC 61850 (Communication Protocols for Intelligent Electronic Devices)
        if any(proto.name in ["IEC 61850", "GOOSE"] for proto in self.protocols.values()):
            recommendations.append({
                'standard': 'IEC 61850',
                'title': 'Comunicaciones para Dispositivos Electrónicos Inteligentes',
                'category': 'communication',
                'priority': 'medium',
                'description': 'Optimizar comunicaciones IEC 61850 para subestaciones',
                'technical_details': [
                    'Configurar GOOSE messaging para comunicación rápida',
                    'Implementar sincronización temporal precisa (IEEE 1588)',
                    'Establecer modelos de datos IED estándar'
                ],
                'recommendations': [
                    'Configurar redundancia de comunicaciones críticas',
                    'Implementar monitoreo de calidad de energía',
                    'Establecer configuración centralizada SCL'
                ],
                'applicable_to': ['Power Systems', 'Substations', 'Smart Grid']
            })

        return recommendations

def main():
    """Función principal para ejecutar análisis industrial"""
    monitor = SmartComputeIndustrialMonitor()

    print("🏭 SmartCompute Industrial - Análisis de Sistemas Industriales")
    print("=" * 60)

    # Ejecutar análisis completo
    analysis = monitor.analyze_industrial_system()

    # Guardar resultados
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"smartcompute_industrial_analysis_{timestamp}.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Análisis completado y guardado en: {output_file}")
    print(f"📊 Estadísticas:")
    print(f"   - Protocolos detectados: {analysis['statistics']['protocols_detected']}")
    print(f"   - PLCs descubiertos: {analysis['statistics']['plcs_discovered']}")
    print(f"   - Sensores activos: {analysis['statistics']['sensors_active']}")
    print(f"   - Mensajes procesados: {analysis['statistics']['messages_processed']}")
    print(f"   - Alertas generadas: {analysis['statistics']['errors_detected']}")
    print(f"   - Duración del análisis: {analysis['duration_seconds']} segundos")

    return output_file

if __name__ == "__main__":
    main()