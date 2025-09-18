#!/usr/bin/env python3
"""
SmartCompute Incident Management Dashboard
=========================================

Dashboard web para gestión de incidentes y monitoreo en tiempo real
del servidor central SmartCompute.
"""

import asyncio
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from aiohttp import web, WSMsgType
import aiohttp_jinja2
import jinja2
import logging

logger = logging.getLogger(__name__)

class IncidentManagementDashboard:
    """Dashboard para gestión de incidentes"""

    def __init__(self, server_db_path: str = "smartcompute_central.db"):
        self.db_path = server_db_path
        self.websocket_connections = set()

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del dashboard"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Estadísticas generales
            cursor.execute("SELECT COUNT(*) FROM incidents")
            total_incidents = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM incidents WHERE status = 'open'")
            open_incidents = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM incidents WHERE severity = 'critical'")
            critical_incidents = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM clients WHERE status = 'online'")
            online_clients = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM analyses WHERE created_at >= datetime('now', '-24 hours')")
            analyses_24h = cursor.fetchone()[0]

            # Incidentes por severidad
            cursor.execute("""
                SELECT severity, COUNT(*) as count
                FROM incidents
                WHERE status IN ('open', 'investigating')
                GROUP BY severity
            """)
            incidents_by_severity = dict(cursor.fetchall())

            # Incidentes recientes
            cursor.execute("""
                SELECT incident_id, title, severity, status, created_at
                FROM incidents
                ORDER BY created_at DESC
                LIMIT 10
            """)
            recent_incidents = [
                {
                    'incident_id': row[0],
                    'title': row[1],
                    'severity': row[2],
                    'status': row[3],
                    'created_at': row[4]
                }
                for row in cursor.fetchall()
            ]

            # Clientes conectados
            cursor.execute("""
                SELECT client_id, client_type, hostname, last_seen, status
                FROM clients
                ORDER BY last_seen DESC
            """)
            clients = [
                {
                    'client_id': row[0],
                    'client_type': row[1],
                    'hostname': row[2],
                    'last_seen': row[3],
                    'status': row[4]
                }
                for row in cursor.fetchall()
            ]

            return {
                'total_incidents': total_incidents,
                'open_incidents': open_incidents,
                'critical_incidents': critical_incidents,
                'online_clients': online_clients,
                'analyses_24h': analyses_24h,
                'incidents_by_severity': incidents_by_severity,
                'recent_incidents': recent_incidents,
                'clients': clients
            }

        finally:
            conn.close()

    def get_incident_details(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """Obtener detalles de un incidente específico"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT incident_id, title, description, severity, status,
                       created_at, updated_at, assigned_to, resolution_steps, metadata_encrypted
                FROM incidents
                WHERE incident_id = ?
            """, (incident_id,))

            row = cursor.fetchone()
            if not row:
                return None

            return {
                'incident_id': row[0],
                'title': row[1],
                'description': row[2],
                'severity': row[3],
                'status': row[4],
                'created_at': row[5],
                'updated_at': row[6],
                'assigned_to': row[7],
                'resolution_steps': row[8],
                'metadata': row[9]  # Cifrado, se puede descifrar si es necesario
            }

        finally:
            conn.close()

    def update_incident_status(self, incident_id: str, status: str, assigned_to: str = None) -> bool:
        """Actualizar estado de incidente"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            updated_at = datetime.utcnow().isoformat()

            if assigned_to:
                cursor.execute("""
                    UPDATE incidents
                    SET status = ?, assigned_to = ?, updated_at = ?
                    WHERE incident_id = ?
                """, (status, assigned_to, updated_at, incident_id))
            else:
                cursor.execute("""
                    UPDATE incidents
                    SET status = ?, updated_at = ?
                    WHERE incident_id = ?
                """, (status, updated_at, incident_id))

            conn.commit()
            return cursor.rowcount > 0

        except Exception as e:
            logger.error(f"Error updating incident: {e}")
            return False
        finally:
            conn.close()

    async def handle_dashboard(self, request):
        """Handler para dashboard principal"""
        stats = self.get_dashboard_stats()
        return aiohttp_jinja2.render_template('dashboard.html', request, stats)

    async def handle_api_stats(self, request):
        """API endpoint para estadísticas"""
        stats = self.get_dashboard_stats()
        return web.json_response(stats)

    async def handle_api_incident_update(self, request):
        """API endpoint para actualizar incidente"""
        try:
            data = await request.json()
            incident_id = data.get('incident_id')
            status = data.get('status')
            assigned_to = data.get('assigned_to')

            if not incident_id or not status:
                return web.json_response({'error': 'Missing required fields'}, status=400)

            success = self.update_incident_status(incident_id, status, assigned_to)

            if success:
                # Broadcast update to WebSocket clients
                await self.broadcast_incident_update({
                    'incident_id': incident_id,
                    'status': status,
                    'assigned_to': assigned_to,
                    'updated_at': datetime.utcnow().isoformat()
                })

                return web.json_response({'success': True})
            else:
                return web.json_response({'error': 'Failed to update incident'}, status=500)

        except Exception as e:
            logger.error(f"Error in incident update: {e}")
            return web.json_response({'error': str(e)}, status=500)

    async def handle_websocket_dashboard(self, request):
        """Handler para WebSocket del dashboard"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        self.websocket_connections.add(ws)
        logger.info("Dashboard WebSocket client connected")

        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    # Manejar mensajes del dashboard
                    if data.get('type') == 'get_stats':
                        stats = self.get_dashboard_stats()
                        await ws.send(json.dumps({
                            'type': 'stats_update',
                            'data': stats
                        }))
                elif msg.type == WSMsgType.ERROR:
                    logger.error(f'WebSocket error: {ws.exception()}')
        except Exception as e:
            logger.error(f"Dashboard WebSocket error: {e}")
        finally:
            self.websocket_connections.discard(ws)
            logger.info("Dashboard WebSocket client disconnected")

        return ws

    async def broadcast_incident_update(self, update_data: Dict[str, Any]):
        """Broadcast incident update to dashboard clients"""
        if self.websocket_connections:
            message = {
                'type': 'incident_update',
                'data': update_data,
                'timestamp': datetime.utcnow().isoformat()
            }

            disconnected = set()
            for ws in self.websocket_connections:
                try:
                    await ws.send(json.dumps(message))
                except:
                    disconnected.add(ws)

            self.websocket_connections -= disconnected

    def create_dashboard_html(self) -> str:
        """Crear HTML del dashboard"""
        return """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SmartCompute - Incident Management Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }

        .dashboard-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            text-align: center;
        }

        .header h1 {
            color: #1e3c72;
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
            text-align: center;
        }

        .stat-card h3 {
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }

        .stat-card.critical h3 {
            color: #dc3545;
        }

        .stat-card.warning h3 {
            color: #fd7e14;
        }

        .stat-card.success h3 {
            color: #28a745;
        }

        .stat-card.info h3 {
            color: #007bff;
        }

        .incidents-section, .clients-section {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
        }

        .section-title {
            font-size: 1.8em;
            color: #1e3c72;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #e9ecef;
        }

        .incident-item, .client-item {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .incident-item.critical {
            border-left: 4px solid #dc3545;
            background: #fff5f5;
        }

        .incident-item.high {
            border-left: 4px solid #fd7e14;
            background: #fff8f0;
        }

        .incident-item.medium {
            border-left: 4px solid #ffc107;
            background: #fffbf0;
        }

        .incident-item.low {
            border-left: 4px solid #6c757d;
            background: #f8f9fa;
        }

        .severity-badge {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        }

        .severity-critical {
            background: #dc3545;
            color: white;
        }

        .severity-high {
            background: #fd7e14;
            color: white;
        }

        .severity-medium {
            background: #ffc107;
            color: #212529;
        }

        .severity-low {
            background: #6c757d;
            color: white;
        }

        .status-badge {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
        }

        .status-open {
            background: #dc3545;
            color: white;
        }

        .status-investigating {
            background: #ffc107;
            color: #212529;
        }

        .status-resolved {
            background: #28a745;
            color: white;
        }

        .client-status {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
        }

        .client-online {
            background: #28a745;
        }

        .client-offline {
            background: #dc3545;
        }

        .auto-refresh {
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(255, 255, 255, 0.9);
            padding: 10px 20px;
            border-radius: 25px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }

        .loading {
            opacity: 0.6;
            pointer-events: none;
        }

        @media (max-width: 768px) {
            .dashboard-container {
                padding: 10px;
            }

            .stats-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="dashboard-container">
        <div class="header">
            <h1>🚨 SmartCompute Incident Management</h1>
            <p>Dashboard de Gestión de Incidentes y Monitoreo en Tiempo Real</p>
        </div>

        <div class="auto-refresh">
            <span id="refresh-status">🔄 Auto-refresh activo</span>
        </div>

        <div class="stats-grid" id="stats-grid">
            <!-- Stats cards will be populated by JavaScript -->
        </div>

        <div class="incidents-section">
            <h2 class="section-title">📋 Incidentes Recientes</h2>
            <div id="incidents-list">
                <!-- Incidents will be populated by JavaScript -->
            </div>
        </div>

        <div class="clients-section">
            <h2 class="section-title">💻 Clientes Conectados</h2>
            <div id="clients-list">
                <!-- Clients will be populated by JavaScript -->
            </div>
        </div>
    </div>

    <script>
        class IncidentDashboard {
            constructor() {
                this.websocket = null;
                this.refreshInterval = 30000; // 30 segundos
                this.init();
            }

            async init() {
                await this.loadStats();
                this.connectWebSocket();
                this.startAutoRefresh();
            }

            async loadStats() {
                try {
                    document.getElementById('refresh-status').textContent = '🔄 Actualizando...';

                    const response = await fetch('/api/stats');
                    const stats = await response.json();

                    this.updateStatsGrid(stats);
                    this.updateIncidentsList(stats.recent_incidents);
                    this.updateClientsList(stats.clients);

                    document.getElementById('refresh-status').textContent = '✅ Actualizado';
                    setTimeout(() => {
                        document.getElementById('refresh-status').textContent = '🔄 Auto-refresh activo';
                    }, 2000);

                } catch (error) {
                    console.error('Error loading stats:', error);
                    document.getElementById('refresh-status').textContent = '❌ Error de conexión';
                }
            }

            updateStatsGrid(stats) {
                const grid = document.getElementById('stats-grid');
                grid.innerHTML = `
                    <div class="stat-card info">
                        <h3>${stats.total_incidents}</h3>
                        <p>Total Incidentes</p>
                    </div>
                    <div class="stat-card critical">
                        <h3>${stats.open_incidents}</h3>
                        <p>Incidentes Abiertos</p>
                    </div>
                    <div class="stat-card warning">
                        <h3>${stats.critical_incidents}</h3>
                        <p>Críticos</p>
                    </div>
                    <div class="stat-card success">
                        <h3>${stats.online_clients}</h3>
                        <p>Clientes Online</p>
                    </div>
                    <div class="stat-card info">
                        <h3>${stats.analyses_24h}</h3>
                        <p>Análisis (24h)</p>
                    </div>
                `;
            }

            updateIncidentsList(incidents) {
                const list = document.getElementById('incidents-list');
                if (!incidents || incidents.length === 0) {
                    list.innerHTML = '<p>No hay incidentes recientes</p>';
                    return;
                }

                list.innerHTML = incidents.map(incident => `
                    <div class="incident-item ${incident.severity}">
                        <div>
                            <strong>${incident.incident_id}</strong>
                            <p>${incident.title}</p>
                            <small>${new Date(incident.created_at).toLocaleString()}</small>
                        </div>
                        <div>
                            <span class="severity-badge severity-${incident.severity}">${incident.severity}</span>
                            <span class="status-badge status-${incident.status}">${incident.status}</span>
                        </div>
                    </div>
                `).join('');
            }

            updateClientsList(clients) {
                const list = document.getElementById('clients-list');
                if (!clients || clients.length === 0) {
                    list.innerHTML = '<p>No hay clientes conectados</p>';
                    return;
                }

                list.innerHTML = clients.map(client => `
                    <div class="client-item">
                        <div>
                            <span class="client-status client-${client.status}"></span>
                            <strong>${client.hostname}</strong>
                            <span class="severity-badge severity-${client.client_type === 'enterprise' ? 'info' : 'medium'}">
                                ${client.client_type}
                            </span>
                        </div>
                        <div>
                            <small>Last seen: ${new Date(client.last_seen).toLocaleString()}</small>
                        </div>
                    </div>
                `).join('');
            }

            connectWebSocket() {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const wsUrl = `${protocol}//${window.location.host}/ws/dashboard`;

                this.websocket = new WebSocket(wsUrl);

                this.websocket.onopen = () => {
                    console.log('WebSocket connected');
                    // Solicitar stats iniciales
                    this.websocket.send(JSON.stringify({type: 'get_stats'}));
                };

                this.websocket.onmessage = (event) => {
                    const message = JSON.parse(event.data);
                    this.handleWebSocketMessage(message);
                };

                this.websocket.onclose = () => {
                    console.log('WebSocket disconnected, attempting to reconnect...');
                    setTimeout(() => this.connectWebSocket(), 5000);
                };

                this.websocket.onerror = (error) => {
                    console.error('WebSocket error:', error);
                };
            }

            handleWebSocketMessage(message) {
                switch (message.type) {
                    case 'stats_update':
                        this.updateStatsGrid(message.data);
                        this.updateIncidentsList(message.data.recent_incidents);
                        this.updateClientsList(message.data.clients);
                        break;
                    case 'incident_update':
                        // Reload stats when incident is updated
                        this.loadStats();
                        break;
                }
            }

            startAutoRefresh() {
                setInterval(() => {
                    this.loadStats();
                }, this.refreshInterval);
            }
        }

        // Initialize dashboard when page loads
        document.addEventListener('DOMContentLoaded', () => {
            new IncidentDashboard();
        });
    </script>
</body>
</html>
        """

    def create_app(self):
        """Crear aplicación web para dashboard"""
        app = web.Application()

        # Configurar Jinja2 templates
        aiohttp_jinja2.setup(
            app,
            loader=jinja2.DictLoader({
                'dashboard.html': self.create_dashboard_html()
            })
        )

        # Rutas
        app.router.add_get('/', self.handle_dashboard)
        app.router.add_get('/api/stats', self.handle_api_stats)
        app.router.add_post('/api/incident/update', self.handle_api_incident_update)
        app.router.add_get('/ws/dashboard', self.handle_websocket_dashboard)

        return app

    async def start_dashboard(self, host: str = '0.0.0.0', port: int = 8081):
        """Iniciar servidor del dashboard"""
        app = self.create_app()

        runner = web.AppRunner(app)
        await runner.setup()

        site = web.TCPSite(runner, host, port)
        await site.start()

        logger.info(f"Incident Management Dashboard started on http://{host}:{port}")
        return runner

async def main():
    """Función principal para ejecutar dashboard independiente"""
    dashboard = IncidentManagementDashboard()
    runner = await dashboard.start_dashboard()

    logger.info("Dashboard is running")
    logger.info("Press Ctrl+C to stop")

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down dashboard...")
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())