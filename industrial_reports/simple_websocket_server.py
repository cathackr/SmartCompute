#!/usr/bin/env python3
"""
Simple WebSocket Server for SmartCompute Industrial
Servidor WebSocket simplificado sin dependencias externas
"""

import asyncio
import json
import http.server
import socketserver
import threading
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any
import math
import random

# Configurar logging básico
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('SmartCompute-Simple')

class IndustrialDataGenerator:
    """Generador de datos industriales simulados"""

    def __init__(self):
        self.base_values = {
            'temperature_reactor': 70.0,
            'pressure_hydraulic': 20.0,
            'flow_water': 35.0,
            'voltage_motor_a': 220.0,
            'current_pump': 8.0,
            'vibration_axis': 5.0,
            'speed_motor': 1600.0,
            'humidity_ambient': 50.0
        }

    def generate_sensors(self) -> Dict[str, float]:
        """Genera datos de sensores realistas"""
        current_time = datetime.now()
        data = {}

        for sensor_name, baseline in self.base_values.items():
            if 'temperature' in sensor_name:
                # Variación diurna + ruido
                daily_var = 10 * math.sin(current_time.hour * math.pi / 12)
                noise = random.gauss(0, 2)
                value = baseline + daily_var + noise
                value = max(15, min(85, value))

            elif 'pressure' in sensor_name:
                # Variación cíclica
                cycle_var = 5 * math.sin(current_time.minute * math.pi / 15)
                noise = random.gauss(0, 1)
                value = baseline + cycle_var + noise
                value = max(0, min(50, value))

            elif 'flow' in sensor_name:
                # Variación operacional
                op_var = 10 * math.sin(current_time.minute * math.pi / 30)
                noise = random.gauss(0, 2)
                value = baseline + op_var + noise
                value = max(10, min(100, value))

            elif 'voltage' in sensor_name:
                # Fluctuaciones de red
                grid_var = 15 * math.sin(current_time.second * math.pi / 30)
                noise = random.gauss(0, 3)
                value = baseline + grid_var + noise
                value = max(200, min(240, value))

            else:
                # Variación estándar
                value = baseline + random.gauss(0, baseline * 0.1)
                value = max(0, value)

            data[sensor_name] = round(value, 2)

        return data

    def generate_plcs(self) -> Dict[str, Dict[str, Any]]:
        """Genera datos de PLCs"""
        return {
            'PLC_001': {
                'status': 'online',
                'cpu_load': max(5, min(95, 45 + random.gauss(0, 15))),
                'memory_usage': max(10, min(90, 60 + random.gauss(0, 10))),
                'network_latency': max(1, min(100, 12 + random.gauss(0, 5))),
                'error_count': max(0, random.randint(0, 2)),
                'firmware_version': 'V32.011'
            },
            'PLC_002': {
                'status': 'online',
                'cpu_load': max(5, min(95, 38 + random.gauss(0, 12))),
                'memory_usage': max(10, min(90, 55 + random.gauss(0, 8))),
                'network_latency': max(1, min(100, 8 + random.gauss(0, 3))),
                'error_count': max(0, random.randint(0, 1)),
                'firmware_version': 'V2.8.1'
            }
        }

    def generate_protocols(self) -> Dict[str, Dict[str, Any]]:
        """Genera datos de protocolos"""
        protocols = {
            'modbus_tcp': {
                'connections_per_second': max(1, 90 + random.gauss(0, 10)),
                'latency_ms': max(1, 10 + random.gauss(0, 3)),
                'error_rate': max(0, 0.1 + random.random() * 0.3),
                'throughput_mbps': max(1, 35 + random.gauss(0, 10))
            },
            'profinet': {
                'connections_per_second': max(1, 75 + random.gauss(0, 8)),
                'latency_ms': max(1, 8 + random.gauss(0, 2)),
                'error_rate': max(0, 0.05 + random.random() * 0.2),
                'throughput_mbps': max(1, 45 + random.gauss(0, 12))
            },
            'opc_ua': {
                'connections_per_second': max(1, 15 + random.gauss(0, 5)),
                'latency_ms': max(1, 35 + random.gauss(0, 15)),
                'error_rate': max(0, 0.3 + random.random() * 0.5),
                'throughput_mbps': max(1, 20 + random.gauss(0, 8))
            }
        }

        # Agregar estado basado en métricas
        for proto_name, proto_data in protocols.items():
            if proto_data['latency_ms'] > 50 or proto_data['error_rate'] > 1.0:
                proto_data['status'] = 'warning'
            elif proto_data['latency_ms'] > 100 or proto_data['error_rate'] > 2.0:
                proto_data['status'] = 'critical'
            else:
                proto_data['status'] = 'online'

            # Redondear valores
            for key in ['connections_per_second', 'latency_ms', 'error_rate', 'throughput_mbps']:
                proto_data[key] = round(proto_data[key], 2)

        return protocols

    def generate_alerts(self, sensors: Dict, plcs: Dict, protocols: Dict) -> list:
        """Genera alertas basadas en las condiciones del sistema"""
        alerts = []
        current_time = datetime.now()

        # Alertas de sensores
        for sensor_name, value in sensors.items():
            if 'temperature' in sensor_name and value > 80:
                alerts.append({
                    'level': 'critical',
                    'source': sensor_name,
                    'message': f'Temperatura crítica: {value}°C',
                    'timestamp': current_time.isoformat(),
                    'value': value
                })
            elif 'pressure' in sensor_name and value > 45:
                alerts.append({
                    'level': 'warning',
                    'source': sensor_name,
                    'message': f'Presión alta: {value} bar',
                    'timestamp': current_time.isoformat(),
                    'value': value
                })

        # Alertas de PLCs
        for plc_name, plc_data in plcs.items():
            if plc_data['cpu_load'] > 85:
                alerts.append({
                    'level': 'critical',
                    'source': plc_name,
                    'message': f'CPU alta: {plc_data["cpu_load"]:.1f}%',
                    'timestamp': current_time.isoformat(),
                    'value': plc_data['cpu_load']
                })

        # Alertas de protocolos
        for proto_name, proto_data in protocols.items():
            if proto_data['latency_ms'] > 60:
                alerts.append({
                    'level': 'warning',
                    'source': proto_name,
                    'message': f'Latencia alta: {proto_data["latency_ms"]}ms',
                    'timestamp': current_time.isoformat(),
                    'value': proto_data['latency_ms']
                })

        return alerts

class HTTPServerWithCORS(http.server.SimpleHTTPRequestHandler):
    """Servidor HTTP con soporte CORS para servir archivos estáticos"""

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

class SmartComputeSimpleServer:
    """Servidor simple para streaming de datos industriales"""

    def __init__(self, host='localhost', http_port=8080, data_port=8081):
        self.host = host
        self.http_port = http_port
        self.data_port = data_port
        self.data_generator = IndustrialDataGenerator()
        self.running = False
        self.output_dir = Path(__file__).parent

    async def start_data_feed(self):
        """Inicia el feed de datos JSON"""
        logger.info(f"🚀 Iniciando feed de datos en puerto {self.data_port}")

        while self.running:
            try:
                # Generar datos actuales
                sensors = self.data_generator.generate_sensors()
                plcs = self.data_generator.generate_plcs()
                protocols = self.data_generator.generate_protocols()
                alerts = self.data_generator.generate_alerts(sensors, plcs, protocols)

                # Calcular métricas
                efficiency = sum([
                    100 - abs(sensors.get('temperature_reactor', 70) - 70) * 2,
                    100 - abs(sensors.get('pressure_hydraulic', 20) - 20) * 3,
                    min(100, sensors.get('flow_water', 35) * 2)
                ]) / 3

                # Crear estructura de datos con BotConf 2024
                data_feed = {
                    'timestamp': datetime.now().isoformat(),
                    'sensors': sensors,
                    'plcs': plcs,
                    'protocols': protocols,
                    'alerts': alerts,
                    'metrics': {
                        'efficiency': round(efficiency, 1),
                        'total_alerts': len(alerts),
                        'systems_online': len([p for p in plcs.values() if p['status'] == 'online']) +
                                         len([p for p in protocols.values() if p['status'] == 'online']),
                        'total_systems': len(plcs) + len(protocols),
                        'uptime_percentage': round(99.5 + random.uniform(-1, 0.5), 1)
                    },
                    'botconf_2024': {
                        'electromagnetic_analysis': {
                            'confidence_score': round(92 + random.uniform(0, 6), 1),
                            'rf_bands': {
                                'low_0_30mhz': round(-45 + random.uniform(0, 6), 1),
                                'mid_30_300mhz': round(-40 + random.uniform(0, 8), 1),
                                'high_300_3000mhz': round(-47 + random.uniform(0, 4), 1)
                            },
                            'signatures_detected': {
                                'iot_devices': 3,
                                'plc_communications': 2,
                                'anomalous_patterns': random.randint(0, 2)
                            },
                            'statistics': {
                                'total_scans': 2847 + random.randint(0, 10),
                                'threats_detected': random.randint(0, 5),
                                'false_positive_rate': round(0.1 + random.uniform(0, 0.3), 1),
                                'avg_response_time': round(0.6 + random.uniform(0, 0.4), 1)
                            }
                        },
                        'research_info': {
                            'paper_title': 'Electromagnetic-based Malware Detection for IoT Devices',
                            'conference': 'BOTCONF 2024',
                            'authors': ['Duy-Phuc Pham', 'Damien Marion', 'Annelie Heuser'],
                            'implementation_by': 'Martín Iribarne (CEH)',
                            'commercial_adaptation': True
                        }
                    }
                }

                # Guardar archivo JSON
                json_path = self.output_dir / 'live_data.json'
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(data_feed, f, indent=2)

                logger.info(f"📡 Datos actualizados - Eficiencia: {efficiency:.1f}% - Alertas: {len(alerts)}")

                # Esperar 2 segundos antes de la siguiente actualización
                await asyncio.sleep(2)

            except Exception as e:
                logger.error(f"Error en data feed: {e}")
                await asyncio.sleep(1)

    def start_http_server(self):
        """Inicia el servidor HTTP para servir archivos estáticos"""
        os.chdir(self.output_dir)

        handler = HTTPServerWithCORS
        httpd = socketserver.TCPServer((self.host, self.http_port), handler)

        logger.info(f"🌐 Servidor HTTP iniciado en http://{self.host}:{self.http_port}")
        httpd.serve_forever()

    async def start(self):
        """Inicia todos los servicios"""
        self.running = True

        logger.info("🏭 SmartCompute Simple Server")
        logger.info("=" * 50)

        # Iniciar servidor HTTP en hilo separado
        http_thread = threading.Thread(
            target=self.start_http_server,
            daemon=True
        )
        http_thread.start()

        # Iniciar feed de datos
        await self.start_data_feed()

    def stop(self):
        """Detiene el servidor"""
        self.running = False
        logger.info("🛑 Deteniendo servidor...")

async def main():
    """Función principal"""
    # Configuración del servidor
    HOST = os.getenv('SMARTCOMPUTE_HOST', 'localhost')
    HTTP_PORT = int(os.getenv('SMARTCOMPUTE_HTTP_PORT', '8080'))
    DATA_PORT = int(os.getenv('SMARTCOMPUTE_DATA_PORT', '8081'))

    server = SmartComputeSimpleServer(HOST, HTTP_PORT, DATA_PORT)

    try:
        await server.start()
    except KeyboardInterrupt:
        server.stop()
        logger.info("👋 Servidor detenido por el usuario")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    print("🏭 SmartCompute Simple Server")
    print("Servidor HTTP + Feed JSON para datos industriales")
    print("Presione Ctrl+C para detener")
    print()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Servidor detenido")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)