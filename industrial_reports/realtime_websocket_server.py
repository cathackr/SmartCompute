#!/usr/bin/env python3
"""
SmartCompute Real-Time WebSocket Server
Servidor WebSocket para streaming de datos industriales en tiempo real
"""

import asyncio
import json
import logging
import os
import signal
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Set, Any, Optional
from dataclasses import dataclass, asdict
import math

# Fallback para librerías opcionales
try:
    import numpy as np
except ImportError:
    # Implementación básica de funciones numpy necesarias
    class np:
        @staticmethod
        def random():
            class random:
                @staticmethod
                def uniform(low, high):
                    import random as r
                    return r.uniform(low, high)

                @staticmethod
                def normal(mean, std):
                    import random as r
                    return r.gauss(mean, std)

                @staticmethod
                def poisson(lam):
                    import random as r
                    # Aproximación simple de Poisson
                    return int(r.expovariate(1.0/lam)) if lam > 0 else 0

                @staticmethod
                def random():
                    import random as r
                    return r.random()
            return random()

        @staticmethod
        def sin(x):
            return math.sin(x)

        @staticmethod
        def pi():
            return math.pi

        @staticmethod
        def mean(values):
            return sum(values) / len(values) if values else 0

    np.pi = math.pi

try:
    import websockets
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False
    print("⚠️ websockets not available, using HTTP fallback")

try:
    import uvloop
    HAS_UVLOOP = True
except ImportError:
    HAS_UVLOOP = False

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('SmartCompute-WebSocket')

# Agregar el directorio padre al path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from enterprise.mle_star_engine import MLESTAREngine
    from smartcompute_industrial_monitor import IndustrialMonitor
    HAS_MLE_INTEGRATION = True
except ImportError:
    HAS_MLE_INTEGRATION = False
    logger.warning("MLE-STAR integration not available, using simulation mode")

@dataclass
class WebSocketMessage:
    """Estructura de mensajes WebSocket"""
    type: str
    timestamp: str
    data: Dict[str, Any]
    client_id: Optional[str] = None

class RealTimeDataStreamer:
    """Generador de datos industriales en tiempo real"""

    def __init__(self):
        self.sensors_baseline = {
            'temperature_reactor': 70.0,
            'pressure_hydraulic': 20.0,
            'flow_water': 35.0,
            'voltage_motor_a': 220.0,
            'current_pump': 8.0,
            'vibration_axis': 5.0,
            'speed_motor': 1600.0,
            'humidity_ambient': 50.0
        }

        self.plcs_baseline = {
            'PLC_001': {
                'cpu_load': 45.0,
                'memory_usage': 60.0,
                'network_latency': 12.0,
                'error_count': 0
            },
            'PLC_002': {
                'cpu_load': 38.0,
                'memory_usage': 55.0,
                'network_latency': 8.0,
                'error_count': 0
            }
        }

        self.protocols_baseline = {
            'modbus_tcp': {
                'connections_per_second': 90.0,
                'latency_ms': 10.0,
                'error_rate': 0.1,
                'throughput_mbps': 35.0
            },
            'profinet': {
                'connections_per_second': 75.0,
                'latency_ms': 8.0,
                'error_rate': 0.05,
                'throughput_mbps': 45.0
            },
            'opc_ua': {
                'connections_per_second': 15.0,
                'latency_ms': 35.0,
                'error_rate': 0.3,
                'throughput_mbps': 20.0
            }
        }

    def generate_sensors_data(self) -> Dict[str, float]:
        """Genera datos de sensores con variación temporal realista"""
        current_time = datetime.now()
        data = {}

        for sensor_name, baseline in self.sensors_baseline.items():
            # Diferentes patrones para cada sensor
            if 'temperature' in sensor_name:
                # Variación diurna + ruido
                daily_variation = 10 * np.sin(current_time.hour * np.pi / 12)
                noise = np.random.normal(0, 2)
                value = baseline + daily_variation + noise
                value = max(15, min(85, value))  # Límites físicos

            elif 'pressure' in sensor_name:
                # Variación cíclica rápida
                cycle_variation = 5 * np.sin(current_time.minute * np.pi / 15)
                noise = np.random.normal(0, 1)
                value = baseline + cycle_variation + noise
                value = max(0, min(50, value))

            elif 'flow' in sensor_name:
                # Variación operacional
                operational_variation = 10 * np.sin(current_time.minute * np.pi / 30)
                noise = np.random.normal(0, 2)
                value = baseline + operational_variation + noise
                value = max(10, min(100, value))

            elif 'voltage' in sensor_name:
                # Fluctuaciones de red
                grid_variation = 15 * np.sin(current_time.second * np.pi / 30)
                noise = np.random.normal(0, 3)
                value = baseline + grid_variation + noise
                value = max(200, min(240, value))

            elif 'current' in sensor_name:
                # Carga variable
                load_variation = 4 * np.sin(current_time.minute * np.pi / 20)
                noise = np.random.normal(0, 0.5)
                value = baseline + load_variation + noise
                value = max(5, min(15, value))

            elif 'vibration' in sensor_name:
                # Vibración mecánica
                mechanical_variation = 2 * np.sin(current_time.second * np.pi / 10)
                noise = np.random.normal(0, 0.3)
                value = baseline + mechanical_variation + noise
                value = max(0, min(10, value))

            elif 'speed' in sensor_name:
                # Velocidad del motor
                speed_variation = 200 * np.sin(current_time.minute * np.pi / 45)
                noise = np.random.normal(0, 20)
                value = baseline + speed_variation + noise
                value = max(1000, min(3000, value))

            else:  # humidity, etc.
                # Variación estándar
                value = baseline + np.random.normal(0, baseline * 0.1)
                value = max(0, min(100, value))

            data[sensor_name] = round(value, 2)

        return data

    def generate_plcs_data(self) -> Dict[str, Dict[str, Any]]:
        """Genera datos de PLCs con variación realista"""
        data = {}

        for plc_name, baseline in self.plcs_baseline.items():
            plc_data = {}

            # CPU Load con variación operacional
            cpu_base = baseline['cpu_load']
            cpu_variation = 15 * np.sin(datetime.now().minute * np.pi / 20)
            cpu_noise = np.random.normal(0, 5)
            plc_data['cpu_load'] = max(5, min(95, cpu_base + cpu_variation + cpu_noise))

            # Memory Usage
            mem_base = baseline['memory_usage']
            mem_variation = 10 * np.sin(datetime.now().minute * np.pi / 30)
            mem_noise = np.random.normal(0, 3)
            plc_data['memory_usage'] = max(10, min(90, mem_base + mem_variation + mem_noise))

            # Network Latency
            net_base = baseline['network_latency']
            net_variation = 5 * np.sin(datetime.now().second * np.pi / 15)
            net_noise = np.random.normal(0, 2)
            plc_data['network_latency'] = max(1, min(100, net_base + net_variation + net_noise))

            # Error Count (eventos Poisson)
            plc_data['error_count'] = baseline['error_count'] + np.random.poisson(0.1)

            # Estado y metadatos
            plc_data['status'] = 'online' if plc_data['cpu_load'] < 90 else 'warning'
            plc_data['uptime_hours'] = baseline.get('uptime_hours', 1000) + 0.017  # +1 minuto
            plc_data['firmware_version'] = 'V32.011' if '001' in plc_name else 'V2.8.1'

            # Redondear valores
            for key in ['cpu_load', 'memory_usage', 'network_latency', 'uptime_hours']:
                if key in plc_data:
                    plc_data[key] = round(plc_data[key], 2)

            data[plc_name] = plc_data

        return data

    def generate_protocols_data(self) -> Dict[str, Dict[str, Any]]:
        """Genera datos de protocolos industriales"""
        data = {}

        for proto_name, baseline in self.protocols_baseline.items():
            proto_data = {}

            # Connections per second
            conn_base = baseline['connections_per_second']
            conn_variation = conn_base * 0.2 * np.sin(datetime.now().minute * np.pi / 25)
            conn_noise = np.random.normal(0, conn_base * 0.05)
            proto_data['connections_per_second'] = max(1, conn_base + conn_variation + conn_noise)

            # Latency
            lat_base = baseline['latency_ms']
            lat_variation = lat_base * 0.3 * np.sin(datetime.now().second * np.pi / 20)
            lat_noise = np.random.normal(0, lat_base * 0.1)
            proto_data['latency_ms'] = max(1, lat_base + lat_variation + lat_noise)

            # Error rate
            error_base = baseline['error_rate']
            error_variation = error_base * 0.5 * np.random.random()
            proto_data['error_rate'] = max(0, min(2.0, error_base + error_variation))

            # Throughput
            through_base = baseline['throughput_mbps']
            through_variation = through_base * 0.2 * np.sin(datetime.now().minute * np.pi / 15)
            through_noise = np.random.normal(0, through_base * 0.05)
            proto_data['throughput_mbps'] = max(1, through_base + through_variation + through_noise)

            # Estado
            if proto_data['latency_ms'] > 50 or proto_data['error_rate'] > 1.0:
                proto_data['status'] = 'warning'
            elif proto_data['latency_ms'] > 100 or proto_data['error_rate'] > 2.0:
                proto_data['status'] = 'critical'
            else:
                proto_data['status'] = 'online'

            # Redondear valores
            for key in ['connections_per_second', 'latency_ms', 'error_rate', 'throughput_mbps']:
                proto_data[key] = round(proto_data[key], 2)

            data[proto_name] = proto_data

        return data

    def generate_alerts(self, sensors: Dict[str, float], plcs: Dict[str, Dict], protocols: Dict[str, Dict]) -> list:
        """Genera alertas basadas en condiciones del sistema"""
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
                    'value': value,
                    'threshold': 80
                })
            elif 'pressure' in sensor_name and value > 45:
                alerts.append({
                    'level': 'warning',
                    'source': sensor_name,
                    'message': f'Presión alta: {value} bar',
                    'timestamp': current_time.isoformat(),
                    'value': value,
                    'threshold': 45
                })
            elif 'voltage' in sensor_name and (value < 205 or value > 235):
                alerts.append({
                    'level': 'warning',
                    'source': sensor_name,
                    'message': f'Voltaje fuera de rango: {value}V',
                    'timestamp': current_time.isoformat(),
                    'value': value,
                    'threshold': '205-235V'
                })

        # Alertas de PLCs
        for plc_name, plc_data in plcs.items():
            if plc_data['cpu_load'] > 85:
                alerts.append({
                    'level': 'critical',
                    'source': plc_name,
                    'message': f'CPU alta: {plc_data["cpu_load"]}%',
                    'timestamp': current_time.isoformat(),
                    'value': plc_data['cpu_load'],
                    'threshold': 85
                })
            elif plc_data['memory_usage'] > 80:
                alerts.append({
                    'level': 'warning',
                    'source': plc_name,
                    'message': f'Memoria alta: {plc_data["memory_usage"]}%',
                    'timestamp': current_time.isoformat(),
                    'value': plc_data['memory_usage'],
                    'threshold': 80
                })

        # Alertas de protocolos
        for proto_name, proto_data in protocols.items():
            if proto_data['latency_ms'] > 60:
                alerts.append({
                    'level': 'warning',
                    'source': proto_name,
                    'message': f'Latencia alta: {proto_data["latency_ms"]}ms',
                    'timestamp': current_time.isoformat(),
                    'value': proto_data['latency_ms'],
                    'threshold': 60
                })

        return alerts

class SmartComputeWebSocketServer:
    """Servidor WebSocket para datos industriales en tiempo real"""

    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.data_streamer = RealTimeDataStreamer()
        self.running = False
        self.update_interval = 2.0  # Actualizar cada 2 segundos

    async def register_client(self, websocket: websockets.WebSocketServerProtocol):
        """Registra un nuevo cliente WebSocket"""
        self.clients.add(websocket)
        client_info = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        logger.info(f"Cliente conectado: {client_info} (Total: {len(self.clients)})")

        # Enviar datos iniciales al cliente
        await self.send_initial_data(websocket)

    async def unregister_client(self, websocket: websockets.WebSocketServerProtocol):
        """Desregistra un cliente WebSocket"""
        self.clients.discard(websocket)
        client_info = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        logger.info(f"Cliente desconectado: {client_info} (Total: {len(self.clients)})")

    async def send_initial_data(self, websocket: websockets.WebSocketServerProtocol):
        """Envía datos iniciales a un cliente recién conectado"""
        try:
            # Configuración inicial
            config_message = WebSocketMessage(
                type="config",
                timestamp=datetime.now().isoformat(),
                data={
                    "update_interval": self.update_interval,
                    "server_version": "2.0.0",
                    "features": ["real_time_sensors", "plc_monitoring", "protocol_analysis", "alerts"]
                }
            )

            await websocket.send(json.dumps(asdict(config_message)))

            # Datos iniciales del sistema
            await self.broadcast_data([websocket])

        except websockets.exceptions.ConnectionClosed:
            pass

    async def handle_client_message(self, websocket: websockets.WebSocketServerProtocol, message: str):
        """Maneja mensajes recibidos de clientes"""
        try:
            data = json.loads(message)
            msg_type = data.get('type', 'unknown')

            if msg_type == 'subscribe':
                # Cliente solicita suscribirse a tipos específicos de datos
                await self.handle_subscription(websocket, data)
            elif msg_type == 'get_historical':
                # Cliente solicita datos históricos
                await self.handle_historical_request(websocket, data)
            elif msg_type == 'control_command':
                # Cliente envía comando de control
                await self.handle_control_command(websocket, data)
            else:
                logger.warning(f"Tipo de mensaje desconocido: {msg_type}")

        except json.JSONDecodeError:
            logger.error(f"Mensaje JSON inválido recibido: {message}")
        except Exception as e:
            logger.error(f"Error procesando mensaje: {e}")

    async def handle_subscription(self, websocket: websockets.WebSocketServerProtocol, data: Dict):
        """Maneja suscripciones de clientes"""
        # Implementar lógica de suscripción específica
        response = WebSocketMessage(
            type="subscription_ack",
            timestamp=datetime.now().isoformat(),
            data={"status": "subscribed", "topics": data.get('topics', [])}
        )
        await websocket.send(json.dumps(asdict(response)))

    async def handle_historical_request(self, websocket: websockets.WebSocketServerProtocol, data: Dict):
        """Maneja solicitudes de datos históricos"""
        # Simular datos históricos
        historical_data = {
            "sensors": [
                {"timestamp": (datetime.now() - timedelta(minutes=i)).isoformat(),
                 "values": self.data_streamer.generate_sensors_data()}
                for i in range(60, 0, -5)  # Últimos 60 minutos, cada 5 minutos
            ]
        }

        response = WebSocketMessage(
            type="historical_data",
            timestamp=datetime.now().isoformat(),
            data=historical_data
        )
        await websocket.send(json.dumps(asdict(response)))

    async def handle_control_command(self, websocket: websockets.WebSocketServerProtocol, data: Dict):
        """Maneja comandos de control del sistema"""
        command = data.get('command', '')

        if command == 'update_interval':
            new_interval = data.get('value', self.update_interval)
            if 1.0 <= new_interval <= 10.0:
                self.update_interval = new_interval
                logger.info(f"Intervalo de actualización cambiado a {new_interval}s")

                response = WebSocketMessage(
                    type="command_response",
                    timestamp=datetime.now().isoformat(),
                    data={"status": "success", "command": command, "new_value": new_interval}
                )
            else:
                response = WebSocketMessage(
                    type="command_response",
                    timestamp=datetime.now().isoformat(),
                    data={"status": "error", "command": command, "error": "Invalid interval"}
                )

            await websocket.send(json.dumps(asdict(response)))

    async def broadcast_data(self, clients: Optional[Set] = None):
        """Transmite datos a todos los clientes conectados"""
        if not clients:
            clients = self.clients.copy()

        if not clients:
            return

        try:
            # Generar datos en tiempo real
            sensors = self.data_streamer.generate_sensors_data()
            plcs = self.data_streamer.generate_plcs_data()
            protocols = self.data_streamer.generate_protocols_data()
            alerts = self.data_streamer.generate_alerts(sensors, plcs, protocols)

            # Calcular métricas derivadas
            efficiency = np.mean([
                100 - abs(sensors.get('temperature_reactor', 70) - 70) * 2,
                100 - abs(sensors.get('pressure_hydraulic', 20) - 20) * 3,
                min(100, sensors.get('flow_water', 35) * 2)
            ])

            # Crear mensaje de datos
            data_message = WebSocketMessage(
                type="real_time_data",
                timestamp=datetime.now().isoformat(),
                data={
                    "sensors": sensors,
                    "plcs": plcs,
                    "protocols": protocols,
                    "alerts": alerts,
                    "metrics": {
                        "efficiency": round(efficiency, 1),
                        "total_alerts": len(alerts),
                        "systems_online": len([p for p in plcs.values() if p['status'] == 'online']) +
                                         len([p for p in protocols.values() if p['status'] == 'online']),
                        "total_systems": len(plcs) + len(protocols)
                    }
                }
            )

            # Enviar a todos los clientes
            message_json = json.dumps(asdict(data_message))

            # Usar asyncio.gather para envío paralelo
            if clients:
                await asyncio.gather(
                    *[client.send(message_json) for client in clients],
                    return_exceptions=True
                )

        except Exception as e:
            logger.error(f"Error broadcasting data: {e}")

    async def client_handler(self, websocket: websockets.WebSocketServerProtocol, path: str):
        """Maneja conexiones de clientes WebSocket"""
        await self.register_client(websocket)

        try:
            async for message in websocket:
                await self.handle_client_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            logger.error(f"Error en client_handler: {e}")
        finally:
            await self.unregister_client(websocket)

    async def data_broadcaster(self):
        """Tarea en background para transmisión periódica de datos"""
        while self.running:
            try:
                await self.broadcast_data()
                await asyncio.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Error en data_broadcaster: {e}")
                await asyncio.sleep(1)

    async def start_server(self):
        """Inicia el servidor WebSocket"""
        self.running = True

        logger.info(f"Iniciando SmartCompute WebSocket Server en {self.host}:{self.port}")

        # Iniciar servidor WebSocket
        server = await websockets.serve(
            self.client_handler,
            self.host,
            self.port,
            ping_interval=20,
            ping_timeout=10,
            max_size=10**6,
            max_queue=32
        )

        # Iniciar broadcaster de datos
        broadcaster_task = asyncio.create_task(self.data_broadcaster())

        logger.info(f"✅ Servidor WebSocket activo en ws://{self.host}:{self.port}")
        logger.info("💡 Conecte su dashboard para recibir datos en tiempo real")

        try:
            # Esperar hasta que se cancele
            await server.wait_closed()
        except asyncio.CancelledError:
            pass
        finally:
            broadcaster_task.cancel()
            try:
                await broadcaster_task
            except asyncio.CancelledError:
                pass

    def stop_server(self):
        """Detiene el servidor"""
        self.running = False
        logger.info("🛑 Deteniendo servidor WebSocket...")

async def main():
    """Función principal del servidor"""
    # Configurar uvloop para mejor rendimiento si está disponible
    if HAS_UVLOOP and sys.platform != 'win32':
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    # Configuración del servidor
    HOST = os.getenv('SMARTCOMPUTE_WS_HOST', 'localhost')
    PORT = int(os.getenv('SMARTCOMPUTE_WS_PORT', '8765'))

    server = SmartComputeWebSocketServer(HOST, PORT)

    # Manejo de señales para cierre limpio
    def signal_handler():
        logger.info("Señal de interrupción recibida")
        server.stop_server()

    if sys.platform != 'win32':
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, signal_handler)

    try:
        await server.start_server()
    except KeyboardInterrupt:
        signal_handler()
    except Exception as e:
        logger.error(f"Error crítico en el servidor: {e}")
        raise

if __name__ == "__main__":
    print("🏭 SmartCompute WebSocket Server")
    print("=" * 50)
    print("Servidor de streaming en tiempo real para datos industriales")
    print("Presione Ctrl+C para detener")
    print()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Servidor detenido por el usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)