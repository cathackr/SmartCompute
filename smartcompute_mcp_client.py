#!/usr/bin/env python3
"""
SmartCompute MCP Client
======================

Cliente MCP para conectar SmartCompute Enterprise e Industrial
al servidor central para gestión de datos y incidentes.
"""

import asyncio
import json
import ssl
import socket
import aiohttp
import websockets
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import platform
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SmartComputeMCPClient:
    """Cliente MCP para SmartCompute"""

    def __init__(self, client_type: str = "enterprise", config_file: str = "client_config.json"):
        self.client_type = client_type  # enterprise, industrial
        self.client_id = self._generate_client_id()
        self.hostname = platform.node()
        self.ip_address = self._get_local_ip()
        self.version = "1.0.0"

        # Configuración del servidor
        self.config = self._load_config(config_file)
        self.server_url = self.config.get('server_url', 'https://localhost:8443')
        self.api_key = self.config.get('api_key', '')

        # Estado de conexión
        self.token = None
        self.connected = False
        self.websocket = None

        # Session HTTP
        self.session = None

    def _generate_client_id(self) -> str:
        """Generar ID único del cliente"""
        hostname = platform.node()
        mac = hex(uuid.getnode())[2:]
        return f"{self.client_type}_{hostname}_{mac}"

    def _get_local_ip(self) -> str:
        """Obtener IP local"""
        try:
            # Conectar a Google DNS para obtener IP local
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Cargar configuración del cliente"""
        default_config = {
            'server_url': 'https://localhost:8443',
            'api_key': 'smartcompute-enterprise-key-2025',
            'ssl_verify': False,  # En producción cambiar a True
            'reconnect_attempts': 5,
            'reconnect_delay': 10,
            'heartbeat_interval': 30
        }

        if Path(config_file).exists():
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Error loading config: {e}, using defaults")

        return default_config

    async def initialize_session(self):
        """Inicializar sesión HTTP"""
        connector = aiohttp.TCPConnector(
            ssl=False if not self.config['ssl_verify'] else None
        )
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=30)
        )

    async def register_with_server(self) -> bool:
        """Registrar cliente con el servidor central"""
        if not self.session:
            await self.initialize_session()

        try:
            registration_data = {
                'client_id': self.client_id,
                'client_type': self.client_type,
                'hostname': self.hostname,
                'ip_address': self.ip_address,
                'version': self.version,
                'platform': platform.platform(),
                'python_version': platform.python_version()
            }

            headers = {}
            if self.api_key:
                headers['X-API-Key'] = self.api_key

            async with self.session.post(
                f"{self.server_url}/api/register",
                json=registration_data,
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.token = data.get('token')
                    self.connected = True
                    logger.info(f"Successfully registered with server: {self.client_id}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"Registration failed: {response.status} - {error_text}")
                    return False

        except Exception as e:
            logger.error(f"Error during registration: {e}")
            return False

    async def submit_analysis(self, analysis_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Enviar análisis al servidor central"""
        if not self.connected or not self.token:
            logger.warning("Client not connected to server")
            return None

        try:
            payload = {
                'analysis_type': self.client_type,
                'timestamp': datetime.utcnow().isoformat(),
                'data': analysis_data,
                'severity': self._determine_severity(analysis_data)
            }

            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }

            async with self.session.post(
                f"{self.server_url}/api/analysis",
                json=payload,
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Analysis submitted successfully: {result.get('analysis_id')}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to submit analysis: {response.status} - {error_text}")
                    return None

        except Exception as e:
            logger.error(f"Error submitting analysis: {e}")
            return None

    def _determine_severity(self, analysis_data: Dict[str, Any]) -> str:
        """Determinar severidad del análisis"""
        # Para Enterprise
        if self.client_type == "enterprise":
            alerts = analysis_data.get('alerts', [])
            critical_alerts = [a for a in alerts if a.get('severity') == 'high']

            if len(critical_alerts) > 5:
                return 'critical'
            elif len(critical_alerts) > 0:
                return 'high'
            elif len(alerts) > 10:
                return 'medium'
            else:
                return 'low'

        # Para Industrial
        elif self.client_type == "industrial":
            alerts = analysis_data.get('alerts', [])
            emergency_stops = [a for a in alerts if 'emergency_stop' in a.get('id', '')]
            sensor_critical = [a for a in alerts if a.get('severity') == 'critical']

            if emergency_stops or len(sensor_critical) > 0:
                return 'critical'
            elif len(alerts) > 3:
                return 'high'
            elif len(alerts) > 0:
                return 'medium'
            else:
                return 'low'

        return 'medium'

    async def connect_websocket(self):
        """Conectar WebSocket para notificaciones en tiempo real"""
        if not self.connected:
            logger.warning("Not connected to server, cannot establish WebSocket")
            return

        try:
            ws_url = self.server_url.replace('http://', 'ws://').replace('https://', 'wss://') + '/ws'

            # Configurar SSL si es necesario
            ssl_context = None
            if ws_url.startswith('wss://') and not self.config['ssl_verify']:
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE

            self.websocket = await websockets.connect(
                ws_url,
                ssl=ssl_context,
                extra_headers={'Authorization': f'Bearer {self.token}'}
            )

            logger.info("WebSocket connection established")

            # Manejar mensajes entrantes
            async for message in self.websocket:
                await self._handle_websocket_message(json.loads(message))

        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            self.websocket = None

    async def _handle_websocket_message(self, message: Dict[str, Any]):
        """Manejar mensajes del WebSocket"""
        msg_type = message.get('type')

        if msg_type == 'incident_update':
            incident = message.get('incident')
            logger.info(f"Incident update received: {incident.get('incident_id')} - {incident.get('status')}")
            # Aquí se puede agregar lógica para notificaciones locales

        elif msg_type == 'pong':
            logger.debug("Pong received")

        else:
            logger.debug(f"Unknown message type: {msg_type}")

    async def start_heartbeat(self):
        """Iniciar heartbeat para mantener conexión"""
        while self.connected and self.websocket:
            try:
                await self.websocket.send(json.dumps({'type': 'ping'}))
                await asyncio.sleep(self.config['heartbeat_interval'])
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
                break

    async def get_incidents(self) -> Optional[List[Dict[str, Any]]]:
        """Obtener lista de incidentes"""
        if not self.connected or not self.token:
            return None

        try:
            headers = {'Authorization': f'Bearer {self.token}'}

            async with self.session.get(
                f"{self.server_url}/api/incidents",
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('incidents', [])
                else:
                    logger.error(f"Failed to get incidents: {response.status}")
                    return None

        except Exception as e:
            logger.error(f"Error getting incidents: {e}")
            return None

    async def close(self):
        """Cerrar conexiones"""
        self.connected = False

        if self.websocket:
            await self.websocket.close()

        if self.session:
            await self.session.close()

        logger.info("MCP Client closed")

# Funciones de integración específicas

async def integrate_with_enterprise_analysis():
    """Integrar con SmartCompute Enterprise"""
    client = SmartComputeMCPClient(client_type="enterprise")

    try:
        await client.initialize_session()

        if await client.register_with_server():
            logger.info("Enterprise client registered successfully")

            # Ejecutar análisis enterprise
            from run_enterprise_analysis import SmartComputeEnterpriseAnalyzer

            analyzer = SmartComputeEnterpriseAnalyzer()
            analysis_result = await analyzer.run_complete_analysis()

            # Enviar al servidor central
            submission_result = await client.submit_analysis(analysis_result)

            if submission_result:
                incident_id = submission_result.get('incident_id')
                if incident_id:
                    logger.warning(f"Incident created: {incident_id}")

            # Conectar WebSocket para notificaciones
            await client.connect_websocket()

            # Mantener conexión activa
            await client.start_heartbeat()

        else:
            logger.error("Failed to register enterprise client")

    except Exception as e:
        logger.error(f"Enterprise integration error: {e}")
    finally:
        await client.close()

async def integrate_with_industrial_analysis():
    """Integrar con SmartCompute Industrial"""
    client = SmartComputeMCPClient(client_type="industrial")

    try:
        await client.initialize_session()

        if await client.register_with_server():
            logger.info("Industrial client registered successfully")

            # Ejecutar análisis industrial
            from smartcompute_industrial_monitor import SmartComputeIndustrialMonitor

            monitor = SmartComputeIndustrialMonitor()
            analysis_result = monitor.analyze_industrial_system()

            # Enviar al servidor central
            submission_result = await client.submit_analysis(analysis_result)

            if submission_result:
                incident_id = submission_result.get('incident_id')
                if incident_id:
                    logger.warning(f"Industrial incident created: {incident_id}")

            # Conectar WebSocket para notificaciones
            await client.connect_websocket()

            # Mantener conexión activa
            await client.start_heartbeat()

        else:
            logger.error("Failed to register industrial client")

    except Exception as e:
        logger.error(f"Industrial integration error: {e}")
    finally:
        await client.close()

async def main():
    """Función principal para testing"""
    import sys

    if len(sys.argv) < 2:
        print("Uso: python smartcompute_mcp_client.py [enterprise|industrial]")
        return

    client_type = sys.argv[1]

    if client_type == "enterprise":
        await integrate_with_enterprise_analysis()
    elif client_type == "industrial":
        await integrate_with_industrial_analysis()
    else:
        print("Tipo de cliente no válido. Use 'enterprise' o 'industrial'")

if __name__ == "__main__":
    asyncio.run(main())