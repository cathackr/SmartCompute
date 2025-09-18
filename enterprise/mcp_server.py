#!/usr/bin/env python3
"""
MCP Server para SmartCompute Enterprise
Servidor MCP que expone funcionalidades HRM como servicios estándar
Compatible con especificación MCP 2024-11-05
"""

import asyncio
import json
import logging
import sys
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import websockets
from websockets.server import WebSocketServerProtocol
from dataclasses import asdict
import argparse

from mcp_hrm_bridge import create_mcp_hrm_bridge, MCPRequest, MCPResponse
from mcp_enterprise_orchestrator import create_mcp_enterprise_orchestrator

class MCPServer:
    """
    Servidor MCP para SmartCompute Enterprise
    Implementa el protocolo MCP estándar con extensiones para SmartCompute
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        self.logger = self._setup_logging()

        # Componentes principales
        self.mcp_bridge = create_mcp_hrm_bridge()
        self.orchestrator = create_mcp_enterprise_orchestrator()

        # Estado del servidor
        self.active_connections = set()
        self.server_info = {
            "name": "SmartCompute Enterprise MCP Server",
            "version": "1.0.0",
            "protocol_version": "2024-11-05",
            "capabilities": self._get_server_capabilities(),
            "started_at": datetime.now().isoformat()
        }

    def _default_config(self) -> Dict:
        """Configuración por defecto del servidor MCP"""
        return {
            "host": "localhost",
            "port": 8080,
            "max_connections": 100,
            "enable_orchestrator": True,
            "log_level": "INFO",
            "websocket_config": {
                "ping_interval": 30,
                "ping_timeout": 10,
                "close_timeout": 10
            },
            "security": {
                "require_authentication": False,  # Para desarrollo
                "allowed_origins": ["*"],  # Para desarrollo
                "rate_limiting": {
                    "enabled": True,
                    "requests_per_minute": 60
                }
            }
        }

    def _setup_logging(self) -> logging.Logger:
        """Configurar logging del servidor"""
        logger = logging.getLogger("MCPServer")
        logger.setLevel(getattr(logging, self.config.get("log_level", "INFO")))

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _get_server_capabilities(self) -> Dict:
        """Obtener capacidades del servidor MCP"""
        return {
            "experimental": {},
            "logging": {},
            "prompts": {
                "listChanged": True
            },
            "resources": {
                "subscribe": True,
                "listChanged": True
            },
            "tools": {
                "listChanged": True
            },
            "smartcompute_extensions": {
                "threat_analysis": True,
                "enterprise_orchestration": True,
                "hrm_integration": True,
                "auto_scaling": True,
                "multi_region_dr": True
            }
        }

    async def start_server(self):
        """Iniciar servidor MCP"""
        self.logger.info(f"Starting MCP Server on {self.config['host']}:{self.config['port']}")

        # Iniciar orquestador si está habilitado
        if self.config.get("enable_orchestrator", True):
            await self.orchestrator.start_orchestration()
            self.logger.info("Enterprise Orchestrator started")

        # Configurar servidor WebSocket
        server = await websockets.serve(
            self._handle_connection,
            self.config["host"],
            self.config["port"],
            ping_interval=self.config["websocket_config"]["ping_interval"],
            ping_timeout=self.config["websocket_config"]["ping_timeout"],
            close_timeout=self.config["websocket_config"]["close_timeout"]
        )

        self.server = server
        self.logger.info(f"MCP Server started successfully on ws://{self.config['host']}:{self.config['port']}")

        # Mantener servidor activo
        await server.wait_closed()

    async def stop_server(self):
        """Detener servidor MCP"""
        self.logger.info("Stopping MCP Server")

        # Cerrar conexiones activas
        if self.active_connections:
            self.logger.info(f"Closing {len(self.active_connections)} active connections")
            await asyncio.gather(
                *[conn.close() for conn in self.active_connections],
                return_exceptions=True
            )

        # Detener orquestador
        if hasattr(self, 'orchestrator'):
            await self.orchestrator.stop_orchestration()
            self.logger.info("Enterprise Orchestrator stopped")

        # Detener servidor
        if hasattr(self, 'server'):
            self.server.close()
            await self.server.wait_closed()

        self.logger.info("MCP Server stopped")

    async def _handle_connection(self, websocket: WebSocketServerProtocol, path: str):
        """Manejar nueva conexión WebSocket"""
        client_info = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        self.logger.info(f"New connection from {client_info}")

        # Verificar límite de conexiones
        if len(self.active_connections) >= self.config["max_connections"]:
            await websocket.close(code=1013, reason="Server overloaded")
            self.logger.warning(f"Connection from {client_info} rejected: max connections reached")
            return

        # Registrar conexión
        self.active_connections.add(websocket)

        try:
            # Enviar información del servidor al conectar
            server_info_msg = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {
                    "server_info": self.server_info,
                    "capabilities": self.server_info["capabilities"]
                }
            }
            await websocket.send(json.dumps(server_info_msg))

            # Procesar mensajes
            async for message in websocket:
                try:
                    await self._process_message(websocket, message, client_info)
                except Exception as e:
                    self.logger.error(f"Error processing message from {client_info}: {str(e)}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32603,
                            "message": "Internal error",
                            "data": str(e)
                        },
                        "id": None
                    }
                    await websocket.send(json.dumps(error_response))

        except websockets.exceptions.ConnectionClosed:
            self.logger.info(f"Connection closed: {client_info}")
        except Exception as e:
            self.logger.error(f"Connection error with {client_info}: {str(e)}")
        finally:
            # Limpiar conexión
            self.active_connections.discard(websocket)
            self.logger.debug(f"Connection cleanup completed for {client_info}")

    async def _process_message(self, websocket: WebSocketServerProtocol, message: str, client_info: str):
        """Procesar mensaje MCP"""
        try:
            data = json.loads(message)
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON from {client_info}: {str(e)}")
            error_response = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32700,
                    "message": "Parse error"
                },
                "id": None
            }
            await websocket.send(json.dumps(error_response))
            return

        # Validar estructura básica MCP
        if not self._validate_mcp_message(data):
            error_response = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32600,
                    "message": "Invalid Request"
                },
                "id": data.get("id")
            }
            await websocket.send(json.dumps(error_response))
            return

        # Enrutar mensaje según tipo
        if data.get("method"):
            # Es una solicitud o notificación
            await self._handle_request_or_notification(websocket, data, client_info)
        else:
            # Es una respuesta (no esperado en servidor típico)
            self.logger.warning(f"Received unexpected response from {client_info}: {data}")

    def _validate_mcp_message(self, data: Dict) -> bool:
        """Validar estructura básica de mensaje MCP"""
        if not isinstance(data, dict):
            return False

        if data.get("jsonrpc") != "2.0":
            return False

        # Debe tener method (request/notification) o result/error (response)
        has_method = "method" in data
        has_result_or_error = "result" in data or "error" in data

        return has_method or has_result_or_error

    async def _handle_request_or_notification(self, websocket: WebSocketServerProtocol,
                                            data: Dict, client_info: str):
        """Manejar solicitud o notificación MCP"""
        method = data.get("method", "")
        params = data.get("params", {})
        request_id = data.get("id")

        self.logger.debug(f"Processing {method} from {client_info} [ID: {request_id}]")

        response = None

        try:
            # Enrutar según método MCP
            if method.startswith("smartcompute/"):
                # Métodos SmartCompute - usar bridge HRM
                mcp_request = MCPRequest(
                    method=method,
                    params=params,
                    id=request_id
                )
                response = await self.mcp_bridge.handle_mcp_request(mcp_request)

            elif method.startswith("orchestrator/"):
                # Métodos del orquestador Enterprise
                response = await self._handle_orchestrator_method(method, params, request_id)

            elif method == "initialize":
                # Inicialización MCP estándar
                response = await self._handle_initialize(params, request_id)

            elif method == "notifications/initialized":
                # Notificación de inicialización (no requiere respuesta)
                self.logger.debug(f"Client {client_info} initialized")
                return

            elif method in ["tools/list", "tools/call"]:
                # Herramientas MCP estándar
                response = await self._handle_tools(method, params, request_id)

            elif method in ["resources/list", "resources/read"]:
                # Recursos MCP estándar
                response = await self._handle_resources(method, params, request_id)

            elif method in ["prompts/list", "prompts/get"]:
                # Prompts MCP estándar
                response = await self._handle_prompts(method, params, request_id)

            else:
                # Método no soportado
                response = MCPResponse(
                    error={
                        "code": -32601,
                        "message": f"Method not found: {method}",
                        "data": {"available_namespaces": ["smartcompute/", "orchestrator/"]}
                    },
                    id=request_id
                )

            # Enviar respuesta (solo para requests, no notifications)
            if request_id is not None and response:
                response_data = asdict(response)
                await websocket.send(json.dumps(response_data))

        except Exception as e:
            self.logger.error(f"Error handling {method} from {client_info}: {str(e)}")

            if request_id is not None:  # Solo responder a requests
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32603,
                        "message": "Internal error",
                        "data": str(e)
                    },
                    "id": request_id
                }
                await websocket.send(json.dumps(error_response))

    async def _handle_orchestrator_method(self, method: str, params: Dict, request_id: str) -> MCPResponse:
        """Manejar métodos específicos del orquestador"""
        if method == "orchestrator/process_threat":
            # Procesar amenaza empresarial
            threat_event = params.get("threat_event", {})
            business_context = params.get("business_context", {})

            result = await self.orchestrator.process_enterprise_threat(
                threat_event, business_context
            )

            return MCPResponse(result=result, id=request_id)

        elif method == "orchestrator/status":
            # Obtener estado del orquestador
            result = await self.orchestrator.get_orchestrator_status()
            return MCPResponse(result=result, id=request_id)

        elif method == "orchestrator/scaling_history":
            # Obtener historial de escalado
            result = {
                "scaling_history": self.orchestrator.scaling_history[-20:],  # Últimas 20 acciones
                "total_count": len(self.orchestrator.scaling_history)
            }
            return MCPResponse(result=result, id=request_id)

        else:
            return MCPResponse(
                error={
                    "code": -32601,
                    "message": f"Orchestrator method not found: {method}"
                },
                id=request_id
            )

    async def _handle_initialize(self, params: Dict, request_id: str) -> MCPResponse:
        """Manejar inicialización MCP estándar"""
        client_info = params.get("clientInfo", {})
        protocol_version = params.get("protocolVersion", "unknown")

        self.logger.info(f"Client initializing: {client_info.get('name', 'unknown')} v{client_info.get('version', 'unknown')}")

        result = {
            "protocolVersion": "2024-11-05",
            "capabilities": self.server_info["capabilities"],
            "serverInfo": {
                "name": self.server_info["name"],
                "version": self.server_info["version"]
            }
        }

        return MCPResponse(result=result, id=request_id)

    async def _handle_tools(self, method: str, params: Dict, request_id: str) -> MCPResponse:
        """Manejar herramientas MCP"""
        if method == "tools/list":
            # Listar herramientas disponibles
            tools = [
                {
                    "name": "analyze_threat",
                    "description": "Analyze security threat using SmartCompute HRM",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "event": {"type": "object", "description": "Threat event data"},
                            "business_context": {"type": "object", "description": "Business context"}
                        },
                        "required": ["event"]
                    }
                },
                {
                    "name": "enterprise_orchestration",
                    "description": "Execute enterprise orchestration with auto-scaling and DR",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "threat_event": {"type": "object"},
                            "business_context": {"type": "object"}
                        },
                        "required": ["threat_event", "business_context"]
                    }
                }
            ]

            return MCPResponse(result={"tools": tools}, id=request_id)

        elif method == "tools/call":
            # Ejecutar herramienta
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            if tool_name == "analyze_threat":
                mcp_request = MCPRequest(
                    method="smartcompute/analyze_threat",
                    params=arguments
                )
                bridge_response = await self.mcp_bridge.handle_mcp_request(mcp_request)

                return MCPResponse(
                    result={
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(bridge_response.result, indent=2)
                            }
                        ]
                    },
                    id=request_id
                )

            elif tool_name == "enterprise_orchestration":
                result = await self.orchestrator.process_enterprise_threat(
                    arguments.get("threat_event", {}),
                    arguments.get("business_context", {})
                )

                return MCPResponse(
                    result={
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, indent=2)
                            }
                        ]
                    },
                    id=request_id
                )

            else:
                return MCPResponse(
                    error={
                        "code": -32602,
                        "message": f"Unknown tool: {tool_name}"
                    },
                    id=request_id
                )

    async def _handle_resources(self, method: str, params: Dict, request_id: str) -> MCPResponse:
        """Manejar recursos MCP"""
        if method == "resources/list":
            # Listar recursos disponibles
            resources = [
                {
                    "uri": "smartcompute://threats/recent",
                    "name": "Recent Threats",
                    "description": "Recent threat analysis results",
                    "mimeType": "application/json"
                },
                {
                    "uri": "smartcompute://orchestrator/status",
                    "name": "Orchestrator Status",
                    "description": "Current orchestrator status and metrics",
                    "mimeType": "application/json"
                },
                {
                    "uri": "smartcompute://nodes/health",
                    "name": "Node Health",
                    "description": "Health status of all enterprise nodes",
                    "mimeType": "application/json"
                }
            ]

            return MCPResponse(result={"resources": resources}, id=request_id)

        elif method == "resources/read":
            # Leer recurso específico
            uri = params.get("uri", "")

            if uri == "smartcompute://orchestrator/status":
                status = await self.orchestrator.get_orchestrator_status()
                return MCPResponse(
                    result={
                        "contents": [
                            {
                                "uri": uri,
                                "mimeType": "application/json",
                                "text": json.dumps(status, indent=2)
                            }
                        ]
                    },
                    id=request_id
                )
            else:
                return MCPResponse(
                    error={
                        "code": -32602,
                        "message": f"Unknown resource: {uri}"
                    },
                    id=request_id
                )

    async def _handle_prompts(self, method: str, params: Dict, request_id: str) -> MCPResponse:
        """Manejar prompts MCP"""
        if method == "prompts/list":
            # Listar prompts disponibles
            prompts = [
                {
                    "name": "analyze_enterprise_threat",
                    "description": "Analyze enterprise threat with business context",
                    "arguments": [
                        {
                            "name": "threat_data",
                            "description": "Threat event data in JSON format",
                            "required": True
                        },
                        {
                            "name": "business_unit",
                            "description": "Business unit affected",
                            "required": False
                        }
                    ]
                }
            ]

            return MCPResponse(result={"prompts": prompts}, id=request_id)

        elif method == "prompts/get":
            # Obtener prompt específico
            prompt_name = params.get("name")
            arguments = params.get("arguments", {})

            if prompt_name == "analyze_enterprise_threat":
                prompt_text = f"""
Analyze this enterprise security threat using SmartCompute HRM:

Threat Data: {arguments.get('threat_data', 'Not provided')}
Business Unit: {arguments.get('business_unit', 'Unknown')}

Please provide:
1. Threat severity assessment
2. Business impact analysis
3. Recommended response actions
4. Escalation requirements
5. Compliance considerations
"""
                return MCPResponse(
                    result={
                        "description": "Enterprise threat analysis prompt",
                        "messages": [
                            {
                                "role": "user",
                                "content": {
                                    "type": "text",
                                    "text": prompt_text
                                }
                            }
                        ]
                    },
                    id=request_id
                )

    async def get_server_stats(self) -> Dict:
        """Obtener estadísticas del servidor"""
        return {
            "active_connections": len(self.active_connections),
            "server_info": self.server_info,
            "orchestrator_running": self.orchestrator.is_running if hasattr(self.orchestrator, 'is_running') else False,
            "uptime_seconds": (datetime.now() - datetime.fromisoformat(self.server_info["started_at"])).total_seconds()
        }

def main():
    """Función principal para ejecutar el servidor MCP"""
    parser = argparse.ArgumentParser(description="SmartCompute Enterprise MCP Server")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    parser.add_argument("--max-connections", type=int, default=100, help="Maximum concurrent connections")
    parser.add_argument("--disable-orchestrator", action="store_true", help="Disable enterprise orchestrator")

    args = parser.parse_args()

    # Crear configuración
    config = {
        "host": args.host,
        "port": args.port,
        "log_level": args.log_level,
        "max_connections": args.max_connections,
        "enable_orchestrator": not args.disable_orchestrator
    }

    # Crear y ejecutar servidor
    server = MCPServer(config)

    async def run_server():
        try:
            await server.start_server()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            await server.stop_server()
        except Exception as e:
            server.logger.error(f"Server error: {str(e)}")
            await server.stop_server()
            sys.exit(1)

    # Ejecutar servidor
    asyncio.run(run_server())

if __name__ == "__main__":
    main()