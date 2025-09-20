#!/usr/bin/env python3
"""
SmartCompute Enterprise - Live System Analysis
==============================================

Análisis en tiempo real del sistema local con interfaz web interactiva.
Monitorea el sistema durante 3 minutos y presenta los resultados en tiempo real.

Copyright (c) 2024 SmartCompute. All rights reserved.
"""

import asyncio
import json
import logging
import psutil
import time
import threading
import webbrowser
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import statistics
import socket
import subprocess
import os
from collections import deque, defaultdict
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse


class LiveSystemAnalyzer:
    """
    Analizador en tiempo real del sistema local con SmartCompute Enterprise
    """

    def __init__(self):
        self.logger = self._setup_logging()

        # Configuración del análisis
        self.analysis_duration = 180  # 3 minutos
        self.update_interval = 1.0   # 1 segundo
        self.start_time = None
        self.is_running = False

        # Datos de monitoreo
        self.system_metrics = deque(maxlen=200)
        self.threat_analysis = deque(maxlen=100)
        self.network_activity = deque(maxlen=150)
        self.process_analysis = deque(maxlen=100)
        self.security_events = deque(maxlen=50)

        # Estado actual del sistema
        self.current_state = {
            'timestamp': datetime.now(),
            'cpu_percent': 0.0,
            'memory_percent': 0.0,
            'disk_io': {'read': 0, 'write': 0},
            'network_io': {'sent': 0, 'recv': 0},
            'active_connections': 0,
            'running_processes': 0,
            'security_score': 85,
            'threat_level': 'LOW',
            'analysis_progress': 0.0
        }

        # Contadores de amenazas simuladas
        self.threat_counters = {
            'suspicious_processes': 0,
            'unusual_network': 0,
            'high_resource_usage': 0,
            'security_alerts': 0,
            'performance_issues': 0
        }

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger('SmartCompute.LiveAnalysis')

    async def start_analysis(self):
        """Iniciar análisis en tiempo real"""
        self.start_time = datetime.now()
        self.is_running = True

        self.logger.info("🚀 Iniciando análisis SmartCompute Enterprise en tiempo real")
        print("🔍 SmartCompute Enterprise - Análisis Local en Tiempo Real")
        print("=" * 60)
        print(f"⏰ Duración: {self.analysis_duration} segundos (3 minutos)")
        print(f"🔄 Actualización cada: {self.update_interval} segundos")
        print(f"🌐 Interfaz web: http://localhost:8888")
        print("=" * 60)

        # Crear tareas asíncronas
        tasks = [
            asyncio.create_task(self._monitor_system_metrics()),
            asyncio.create_task(self._analyze_processes()),
            asyncio.create_task(self._monitor_network_activity()),
            asyncio.create_task(self._detect_security_threats()),
            asyncio.create_task(self._perform_threat_analysis()),
            asyncio.create_task(self._update_progress())
        ]

        # Ejecutar análisis durante el tiempo especificado
        try:
            await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=self.analysis_duration
            )
        except asyncio.TimeoutError:
            self.logger.info("✅ Análisis completado - tiempo límite alcanzado")

        self.is_running = False
        await self._generate_final_report()

    async def _monitor_system_metrics(self):
        """Monitorear métricas del sistema"""
        while self.is_running:
            try:
                # CPU y memoria
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory = psutil.virtual_memory()

                # I/O de disco
                disk_io = psutil.disk_io_counters()
                disk_io_data = {
                    'read': disk_io.read_bytes if disk_io else 0,
                    'write': disk_io.write_bytes if disk_io else 0
                }

                # I/O de red
                net_io = psutil.net_io_counters()
                net_io_data = {
                    'sent': net_io.bytes_sent if net_io else 0,
                    'recv': net_io.bytes_recv if net_io else 0
                }

                # Conexiones de red
                connections = len(psutil.net_connections())
                processes = len(psutil.pids())

                # Actualizar estado actual
                self.current_state.update({
                    'timestamp': datetime.now(),
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'disk_io': disk_io_data,
                    'network_io': net_io_data,
                    'active_connections': connections,
                    'running_processes': processes
                })

                # Agregar a historial
                self.system_metrics.append({
                    'timestamp': datetime.now().isoformat(),
                    'cpu': cpu_percent,
                    'memory': memory.percent,
                    'disk_read': disk_io_data['read'],
                    'disk_write': disk_io_data['write'],
                    'net_sent': net_io_data['sent'],
                    'net_recv': net_io_data['recv'],
                    'connections': connections,
                    'processes': processes
                })

                await asyncio.sleep(self.update_interval)

            except Exception as e:
                self.logger.error(f"Error monitoreando sistema: {e}")
                await asyncio.sleep(1)

    async def _analyze_processes(self):
        """Analizar procesos en ejecución"""
        while self.is_running:
            try:
                suspicious_processes = []
                high_cpu_processes = []
                high_memory_processes = []

                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                    try:
                        info = proc.info

                        # Detectar procesos con alto uso de CPU
                        if info['cpu_percent'] and info['cpu_percent'] > 80:
                            high_cpu_processes.append({
                                'pid': info['pid'],
                                'name': info['name'],
                                'cpu': info['cpu_percent']
                            })

                        # Detectar procesos con alta memoria
                        if info['memory_percent'] and info['memory_percent'] > 10:
                            high_memory_processes.append({
                                'pid': info['pid'],
                                'name': info['name'],
                                'memory': info['memory_percent']
                            })

                        # Simular detección de procesos sospechosos
                        if self._is_suspicious_process(info['name']):
                            suspicious_processes.append({
                                'pid': info['pid'],
                                'name': info['name'],
                                'reason': 'Nombre sospechoso'
                            })

                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue

                # Actualizar contadores
                if high_cpu_processes:
                    self.threat_counters['high_resource_usage'] += 1

                if suspicious_processes:
                    self.threat_counters['suspicious_processes'] += len(suspicious_processes)

                # Agregar al análisis
                self.process_analysis.append({
                    'timestamp': datetime.now().isoformat(),
                    'suspicious_count': len(suspicious_processes),
                    'high_cpu_count': len(high_cpu_processes),
                    'high_memory_count': len(high_memory_processes),
                    'suspicious_processes': suspicious_processes[:5],  # Top 5
                    'high_cpu_processes': high_cpu_processes[:5],
                    'high_memory_processes': high_memory_processes[:5]
                })

                await asyncio.sleep(5)  # Analizar cada 5 segundos

            except Exception as e:
                self.logger.error(f"Error analizando procesos: {e}")
                await asyncio.sleep(5)

    def _is_suspicious_process(self, process_name: str) -> bool:
        """Detectar nombres de procesos sospechosos (simulado)"""
        suspicious_names = [
            'miner', 'bitcoin', 'crypto', 'hack', 'trojan',
            'keylog', 'backdoor', 'rat', 'botnet', 'malware'
        ]
        return any(name in process_name.lower() for name in suspicious_names)

    async def _monitor_network_activity(self):
        """Monitorear actividad de red"""
        while self.is_running:
            try:
                connections = psutil.net_connections()

                # Analizar conexiones
                listening_ports = []
                established_connections = []
                suspicious_connections = []

                for conn in connections:
                    if conn.status == psutil.CONN_LISTEN and conn.laddr:
                        listening_ports.append({
                            'port': conn.laddr.port,
                            'protocol': 'TCP' if conn.type == socket.SOCK_STREAM else 'UDP'
                        })

                    elif conn.status == psutil.CONN_ESTABLISHED and conn.raddr:
                        established_connections.append({
                            'local_port': conn.laddr.port if conn.laddr else 0,
                            'remote_ip': conn.raddr.ip,
                            'remote_port': conn.raddr.port
                        })

                        # Simular detección de conexiones sospechosas
                        if self._is_suspicious_ip(conn.raddr.ip):
                            suspicious_connections.append({
                                'remote_ip': conn.raddr.ip,
                                'remote_port': conn.raddr.port,
                                'reason': 'IP sospechosa'
                            })

                # Actualizar contadores
                if suspicious_connections:
                    self.threat_counters['unusual_network'] += len(suspicious_connections)

                # Agregar al monitoreo
                self.network_activity.append({
                    'timestamp': datetime.now().isoformat(),
                    'total_connections': len(connections),
                    'listening_ports': len(listening_ports),
                    'established_connections': len(established_connections),
                    'suspicious_connections': len(suspicious_connections),
                    'top_listening_ports': listening_ports[:10],
                    'suspicious_ips': suspicious_connections[:5]
                })

                await asyncio.sleep(3)  # Cada 3 segundos

            except Exception as e:
                self.logger.error(f"Error monitoreando red: {e}")
                await asyncio.sleep(3)

    def _is_suspicious_ip(self, ip: str) -> bool:
        """Detectar IPs sospechosas (simulado)"""
        # Simulamos algunos rangos "sospechosos" para demo
        suspicious_ranges = ['192.168.100.', '10.0.0.', '172.16.0.']
        return any(ip.startswith(range_ip) for range_ip in suspicious_ranges)

    async def _detect_security_threats(self):
        """Detectar amenazas de seguridad"""
        while self.is_running:
            try:
                threats_detected = []

                # Analizar métricas actuales
                cpu = self.current_state['cpu_percent']
                memory = self.current_state['memory_percent']
                connections = self.current_state['active_connections']

                # Detectar uso anómalo de recursos
                if cpu > 90:
                    threats_detected.append({
                        'type': 'HIGH_CPU_USAGE',
                        'severity': 'MEDIUM',
                        'description': f'Uso de CPU extremadamente alto: {cpu:.1f}%',
                        'recommendation': 'Verificar procesos consumiendo CPU'
                    })

                if memory > 85:
                    threats_detected.append({
                        'type': 'HIGH_MEMORY_USAGE',
                        'severity': 'MEDIUM',
                        'description': f'Uso de memoria alto: {memory:.1f}%',
                        'recommendation': 'Revisar procesos con alta memoria'
                    })

                # Detectar conexiones anómalas
                if connections > 100:
                    threats_detected.append({
                        'type': 'EXCESSIVE_CONNECTIONS',
                        'severity': 'HIGH',
                        'description': f'Número inusual de conexiones: {connections}',
                        'recommendation': 'Investigar actividad de red'
                    })

                # Simular detección de amenazas adicionales
                if time.time() % 30 < 1:  # Cada 30 segundos aprox
                    threats_detected.append({
                        'type': 'SUSPICIOUS_ACTIVITY',
                        'severity': 'LOW',
                        'description': 'Patrón de comportamiento inusual detectado',
                        'recommendation': 'Monitoreo continuo recomendado'
                    })

                # Actualizar contadores y eventos
                if threats_detected:
                    self.threat_counters['security_alerts'] += len(threats_detected)

                    for threat in threats_detected:
                        self.security_events.append({
                            'timestamp': datetime.now().isoformat(),
                            'type': threat['type'],
                            'severity': threat['severity'],
                            'description': threat['description'],
                            'recommendation': threat['recommendation']
                        })

                # Calcular score de seguridad
                total_threats = sum(self.threat_counters.values())
                security_score = max(50, 95 - (total_threats * 2))

                if security_score >= 90:
                    threat_level = 'LOW'
                elif security_score >= 75:
                    threat_level = 'MEDIUM'
                else:
                    threat_level = 'HIGH'

                self.current_state.update({
                    'security_score': security_score,
                    'threat_level': threat_level
                })

                await asyncio.sleep(2)  # Cada 2 segundos

            except Exception as e:
                self.logger.error(f"Error detectando amenazas: {e}")
                await asyncio.sleep(2)

    async def _perform_threat_analysis(self):
        """Realizar análisis de amenazas con IA simulada"""
        while self.is_running:
            try:
                # Simular análisis HRM/IA
                analysis_results = {
                    'timestamp': datetime.now().isoformat(),
                    'ai_confidence': 85 + (time.time() % 10),  # 85-95%
                    'threat_patterns': [],
                    'behavioral_anomalies': [],
                    'risk_assessment': 'LOW',
                    'recommendations': []
                }

                # Simular detección de patrones
                if self.current_state['cpu_percent'] > 70:
                    analysis_results['threat_patterns'].append({
                        'pattern': 'HIGH_RESOURCE_CONSUMPTION',
                        'confidence': 0.78,
                        'description': 'Patrón de alto consumo de recursos detectado'
                    })

                if len(self.network_activity) > 0 and self.network_activity[-1]['total_connections'] > 50:
                    analysis_results['threat_patterns'].append({
                        'pattern': 'NETWORK_ACTIVITY_SPIKE',
                        'confidence': 0.65,
                        'description': 'Incremento inusual en actividad de red'
                    })

                # Evaluación de riesgo
                total_threats = sum(self.threat_counters.values())
                if total_threats > 10:
                    analysis_results['risk_assessment'] = 'HIGH'
                elif total_threats > 5:
                    analysis_results['risk_assessment'] = 'MEDIUM'

                # Recomendaciones
                if self.current_state['cpu_percent'] > 80:
                    analysis_results['recommendations'].append(
                        'Considerar optimización de procesos de alto consumo'
                    )

                if self.current_state['memory_percent'] > 80:
                    analysis_results['recommendations'].append(
                        'Revisar aplicaciones con alta utilización de memoria'
                    )

                self.threat_analysis.append(analysis_results)

                await asyncio.sleep(10)  # Análisis cada 10 segundos

            except Exception as e:
                self.logger.error(f"Error en análisis de amenazas: {e}")
                await asyncio.sleep(10)

    async def _update_progress(self):
        """Actualizar progreso del análisis"""
        while self.is_running:
            if self.start_time:
                elapsed = (datetime.now() - self.start_time).total_seconds()
                progress = min(100.0, (elapsed / self.analysis_duration) * 100)
                self.current_state['analysis_progress'] = progress

                if progress >= 100:
                    break

            await asyncio.sleep(1)

    async def _generate_final_report(self):
        """Generar reporte final"""
        end_time = datetime.now()
        duration = end_time - self.start_time

        final_report = {
            'analysis_summary': {
                'start_time': self.start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': duration.total_seconds(),
                'total_metrics_collected': len(self.system_metrics),
                'threat_events_detected': len(self.security_events),
                'final_security_score': self.current_state['security_score'],
                'final_threat_level': self.current_state['threat_level']
            },
            'threat_summary': dict(self.threat_counters),
            'performance_summary': {
                'avg_cpu': statistics.mean([m['cpu'] for m in self.system_metrics]) if self.system_metrics else 0,
                'avg_memory': statistics.mean([m['memory'] for m in self.system_metrics]) if self.system_metrics else 0,
                'max_connections': max([m['connections'] for m in self.system_metrics]) if self.system_metrics else 0,
                'avg_processes': statistics.mean([m['processes'] for m in self.system_metrics]) if self.system_metrics else 0
            }
        }

        # Guardar reporte
        report_file = Path('/tmp/smartcompute_live_analysis_report.json')
        with open(report_file, 'w') as f:
            json.dump(final_report, f, indent=2)

        self.logger.info(f"📄 Reporte final guardado: {report_file}")
        print(f"\n📄 Análisis completado - Reporte: {report_file}")

    def get_current_data(self) -> Dict[str, Any]:
        """Obtener datos actuales para la interfaz web"""
        return {
            'current_state': self.current_state,
            'system_metrics': list(self.system_metrics)[-20:],  # Últimos 20 puntos
            'network_activity': list(self.network_activity)[-10:],
            'process_analysis': list(self.process_analysis)[-5:],
            'security_events': list(self.security_events)[-10:],
            'threat_analysis': list(self.threat_analysis)[-3:],
            'threat_counters': self.threat_counters,
            'is_running': self.is_running
        }


class WebInterface(BaseHTTPRequestHandler):
    """Servidor web para interfaz en tiempo real"""

    analyzer = None  # Will be set externally

    def do_GET(self):
        """Manejar peticiones GET"""
        parsed_path = urllib.parse.urlparse(self.path)

        if parsed_path.path == '/':
            self._serve_dashboard()
        elif parsed_path.path == '/api/data':
            self._serve_api_data()
        elif parsed_path.path == '/api/status':
            self._serve_status()
        else:
            self._serve_404()

    def _serve_dashboard(self):
        """Servir dashboard principal"""
        html_content = self._generate_dashboard_html()

        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))

    def _serve_api_data(self):
        """Servir datos de API"""
        if self.analyzer:
            data = self.analyzer.get_current_data()
        else:
            data = {'error': 'Analyzer not available'}

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode('utf-8'))

    def _serve_status(self):
        """Servir estado del sistema"""
        status = {
            'status': 'running' if (self.analyzer and self.analyzer.is_running) else 'stopped',
            'timestamp': datetime.now().isoformat()
        }

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(status).encode('utf-8'))

    def _serve_404(self):
        """Servir error 404"""
        self.send_response(404)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'<h1>404 Not Found</h1>')

    def _generate_dashboard_html(self) -> str:
        """Generar HTML del dashboard"""
        return """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SmartCompute Enterprise - Análisis en Tiempo Real</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #2c3e50, #34495e);
            color: white;
            min-height: 100vh;
            overflow-x: hidden;
        }

        .header {
            background: rgba(0,0,0,0.3);
            padding: 20px;
            text-align: center;
            border-bottom: 2px solid #3498db;
        }

        .header h1 {
            font-size: 2em;
            margin-bottom: 10px;
            color: #ecf0f1;
        }

        .status-bar {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 30px;
            margin-top: 15px;
        }

        .status-item {
            background: rgba(255,255,255,0.1);
            padding: 10px 20px;
            border-radius: 20px;
            border: 2px solid transparent;
            transition: all 0.3s ease;
        }

        .status-running { border-color: #27ae60; }
        .status-stopped { border-color: #e74c3c; }

        .container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            padding: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }

        .card {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
            transition: transform 0.3s ease;
        }

        .card:hover {
            transform: translateY(-5px);
        }

        .card h3 {
            color: #3498db;
            margin-bottom: 15px;
            font-size: 1.2em;
            border-bottom: 2px solid #3498db;
            padding-bottom: 5px;
        }

        .metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 15px;
            margin: 15px 0;
        }

        .metric {
            background: rgba(0,0,0,0.3);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }

        .metric-value {
            font-size: 1.8em;
            font-weight: bold;
            color: #2ecc71;
            margin-bottom: 5px;
        }

        .metric-label {
            font-size: 0.9em;
            color: #bdc3c7;
        }

        .progress-bar {
            width: 100%;
            height: 20px;
            background: rgba(0,0,0,0.3);
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #27ae60, #2ecc71);
            border-radius: 10px;
            transition: width 0.3s ease;
        }

        .threat-level {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
        }

        .threat-low { background: #27ae60; }
        .threat-medium { background: #f39c12; }
        .threat-high { background: #e74c3c; }

        .event-list {
            max-height: 200px;
            overflow-y: auto;
            background: rgba(0,0,0,0.2);
            border-radius: 10px;
            padding: 10px;
        }

        .event-item {
            margin: 8px 0;
            padding: 8px;
            background: rgba(255,255,255,0.05);
            border-radius: 5px;
            font-size: 0.9em;
        }

        .timestamp {
            color: #7f8c8d;
            font-size: 0.8em;
        }

        .full-width {
            grid-column: 1 / -1;
        }

        .chart-container {
            height: 200px;
            background: rgba(0,0,0,0.2);
            border-radius: 10px;
            padding: 10px;
            margin: 15px 0;
            position: relative;
            overflow: hidden;
        }

        .loading {
            text-align: center;
            padding: 50px;
            font-size: 1.2em;
            color: #95a5a6;
        }

        @keyframes pulse {
            0% { opacity: 0.6; }
            50% { opacity: 1; }
            100% { opacity: 0.6; }
        }

        .pulse {
            animation: pulse 2s infinite;
        }

        .security-score {
            text-align: center;
            padding: 20px;
        }

        .security-score-value {
            font-size: 3em;
            font-weight: bold;
            margin: 10px 0;
        }

        .score-excellent { color: #27ae60; }
        .score-good { color: #3498db; }
        .score-warning { color: #f39c12; }
        .score-critical { color: #e74c3c; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 SmartCompute Enterprise</h1>
        <p>Análisis de Sistema Local en Tiempo Real</p>

        <div class="status-bar">
            <div class="status-item" id="status">
                <span id="status-text">Iniciando...</span>
            </div>
            <div class="status-item">
                <span>⏱️ Tiempo: <span id="elapsed-time">00:00</span> / 03:00</span>
            </div>
            <div class="status-item">
                <span>🔄 Progreso: <span id="progress-text">0%</span></span>
            </div>
        </div>

        <div class="progress-bar">
            <div class="progress-fill" id="progress-bar" style="width: 0%"></div>
        </div>
    </div>

    <div class="container">
        <!-- Métricas del Sistema -->
        <div class="card">
            <h3>📊 Métricas del Sistema</h3>
            <div class="metric-grid">
                <div class="metric">
                    <div class="metric-value" id="cpu-value">0%</div>
                    <div class="metric-label">CPU</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="memory-value">0%</div>
                    <div class="metric-label">Memoria</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="connections-value">0</div>
                    <div class="metric-label">Conexiones</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="processes-value">0</div>
                    <div class="metric-label">Procesos</div>
                </div>
            </div>
            <div class="chart-container" id="cpu-chart">
                <div class="loading">Cargando gráfico de CPU...</div>
            </div>
        </div>

        <!-- Análisis de Seguridad -->
        <div class="card">
            <h3>🔒 Análisis de Seguridad</h3>
            <div class="security-score">
                <div class="security-score-value score-excellent" id="security-score">85</div>
                <div>Puntuación de Seguridad</div>
                <div class="threat-level threat-low" id="threat-level">BAJO</div>
            </div>

            <div class="metric-grid">
                <div class="metric">
                    <div class="metric-value" id="threats-suspicious">0</div>
                    <div class="metric-label">Procesos Sospechosos</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="threats-network">0</div>
                    <div class="metric-label">Red Inusual</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="threats-resources">0</div>
                    <div class="metric-label">Alto Recurso</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="threats-alerts">0</div>
                    <div class="metric-label">Alertas</div>
                </div>
            </div>
        </div>

        <!-- Actividad de Red -->
        <div class="card">
            <h3>🌐 Actividad de Red</h3>
            <div class="metric-grid">
                <div class="metric">
                    <div class="metric-value" id="net-connections">0</div>
                    <div class="metric-label">Conexiones Activas</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="net-listening">0</div>
                    <div class="metric-label">Puertos Escuchando</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="net-established">0</div>
                    <div class="metric-label">Establecidas</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="net-suspicious">0</div>
                    <div class="metric-label">Sospechosas</div>
                </div>
            </div>

            <div id="network-details" class="event-list">
                <div class="loading pulse">Monitoreando actividad de red...</div>
            </div>
        </div>

        <!-- Análisis de Procesos -->
        <div class="card">
            <h3>⚙️ Análisis de Procesos</h3>
            <div id="process-analysis" class="event-list">
                <div class="loading pulse">Analizando procesos del sistema...</div>
            </div>
        </div>

        <!-- Eventos de Seguridad -->
        <div class="card full-width">
            <h3>🚨 Eventos de Seguridad en Tiempo Real</h3>
            <div id="security-events" class="event-list">
                <div class="loading pulse">Monitoreando eventos de seguridad...</div>
            </div>
        </div>

        <!-- Análisis de Amenazas IA -->
        <div class="card full-width">
            <h3>🧠 Análisis de Amenazas con IA (SmartCompute HRM)</h3>
            <div id="threat-analysis" class="event-list">
                <div class="loading pulse">Analizando patrones con inteligencia artificial...</div>
            </div>
        </div>
    </div>

    <script>
        let startTime = Date.now();
        let analysisData = {};

        // Actualizar cada segundo
        setInterval(updateDashboard, 1000);

        function updateDashboard() {
            fetch('/api/data')
                .then(response => response.json())
                .then(data => {
                    analysisData = data;
                    updateStatus();
                    updateMetrics();
                    updateSecurity();
                    updateNetwork();
                    updateProcesses();
                    updateSecurityEvents();
                    updateThreatAnalysis();
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        }

        function updateStatus() {
            const status = analysisData.current_state;
            if (!status) return;

            // Status
            const statusEl = document.getElementById('status');
            const statusText = document.getElementById('status-text');

            if (analysisData.is_running) {
                statusEl.className = 'status-item status-running';
                statusText.textContent = '🟢 Análisis Activo';
            } else {
                statusEl.className = 'status-item status-stopped';
                statusText.textContent = '🔴 Análisis Completado';
            }

            // Time
            const elapsed = Math.floor((Date.now() - startTime) / 1000);
            const minutes = Math.floor(elapsed / 60);
            const seconds = elapsed % 60;
            document.getElementById('elapsed-time').textContent =
                `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;

            // Progress
            const progress = Math.min(100, status.analysis_progress || 0);
            document.getElementById('progress-text').textContent = `${progress.toFixed(1)}%`;
            document.getElementById('progress-bar').style.width = `${progress}%`;
        }

        function updateMetrics() {
            const state = analysisData.current_state;
            if (!state) return;

            document.getElementById('cpu-value').textContent = `${state.cpu_percent.toFixed(1)}%`;
            document.getElementById('memory-value').textContent = `${state.memory_percent.toFixed(1)}%`;
            document.getElementById('connections-value').textContent = state.active_connections;
            document.getElementById('processes-value').textContent = state.running_processes;
        }

        function updateSecurity() {
            const state = analysisData.current_state;
            const threats = analysisData.threat_counters;
            if (!state || !threats) return;

            // Security score
            const score = state.security_score;
            const scoreEl = document.getElementById('security-score');
            scoreEl.textContent = score;

            // Score color
            scoreEl.className = 'security-score-value ';
            if (score >= 90) scoreEl.className += 'score-excellent';
            else if (score >= 75) scoreEl.className += 'score-good';
            else if (score >= 60) scoreEl.className += 'score-warning';
            else scoreEl.className += 'score-critical';

            // Threat level
            const threatEl = document.getElementById('threat-level');
            threatEl.textContent = state.threat_level;
            threatEl.className = `threat-level threat-${state.threat_level.toLowerCase()}`;

            // Threat counters
            document.getElementById('threats-suspicious').textContent = threats.suspicious_processes || 0;
            document.getElementById('threats-network').textContent = threats.unusual_network || 0;
            document.getElementById('threats-resources').textContent = threats.high_resource_usage || 0;
            document.getElementById('threats-alerts').textContent = threats.security_alerts || 0;
        }

        function updateNetwork() {
            const network = analysisData.network_activity;
            if (!network || network.length === 0) return;

            const latest = network[network.length - 1];

            document.getElementById('net-connections').textContent = latest.total_connections;
            document.getElementById('net-listening').textContent = latest.listening_ports;
            document.getElementById('net-established').textContent = latest.established_connections;
            document.getElementById('net-suspicious').textContent = latest.suspicious_connections;

            // Network details
            let detailsHtml = '';
            if (latest.suspicious_ips && latest.suspicious_ips.length > 0) {
                detailsHtml += '<h4>🚨 IPs Sospechosas:</h4>';
                latest.suspicious_ips.forEach(ip => {
                    detailsHtml += `<div class="event-item">
                        <strong>${ip.remote_ip}:${ip.remote_port}</strong> - ${ip.reason}
                        <div class="timestamp">${new Date().toLocaleTimeString()}</div>
                    </div>`;
                });
            } else {
                detailsHtml = '<div class="event-item">✅ No se detectaron conexiones sospechosas</div>';
            }

            document.getElementById('network-details').innerHTML = detailsHtml;
        }

        function updateProcesses() {
            const processes = analysisData.process_analysis;
            if (!processes || processes.length === 0) return;

            const latest = processes[processes.length - 1];
            let html = '';

            if (latest.suspicious_processes && latest.suspicious_processes.length > 0) {
                html += '<h4>⚠️ Procesos Sospechosos:</h4>';
                latest.suspicious_processes.forEach(proc => {
                    html += `<div class="event-item">
                        <strong>PID ${proc.pid}: ${proc.name}</strong> - ${proc.reason}
                    </div>`;
                });
            }

            if (latest.high_cpu_processes && latest.high_cpu_processes.length > 0) {
                html += '<h4>🔥 Alto Uso CPU:</h4>';
                latest.high_cpu_processes.forEach(proc => {
                    html += `<div class="event-item">
                        <strong>${proc.name}</strong> - ${proc.cpu.toFixed(1)}% CPU
                    </div>`;
                });
            }

            if (latest.high_memory_processes && latest.high_memory_processes.length > 0) {
                html += '<h4>🧠 Alta Memoria:</h4>';
                latest.high_memory_processes.forEach(proc => {
                    html += `<div class="event-item">
                        <strong>${proc.name}</strong> - ${proc.memory.toFixed(1)}% Memoria
                    </div>`;
                });
            }

            if (!html) {
                html = '<div class="event-item">✅ Todos los procesos funcionan normalmente</div>';
            }

            document.getElementById('process-analysis').innerHTML = html;
        }

        function updateSecurityEvents() {
            const events = analysisData.security_events;
            if (!events) return;

            let html = '';
            const recentEvents = events.slice(-10);

            if (recentEvents.length === 0) {
                html = '<div class="event-item">✅ No se han detectado eventos de seguridad</div>';
            } else {
                recentEvents.reverse().forEach(event => {
                    const time = new Date(event.timestamp).toLocaleTimeString();
                    const severityClass = `threat-${event.severity.toLowerCase()}`;

                    html += `<div class="event-item">
                        <div><span class="threat-level ${severityClass}">${event.severity}</span>
                        <strong>${event.type}</strong></div>
                        <div>${event.description}</div>
                        <div style="font-size: 0.8em; margin-top: 5px;">💡 ${event.recommendation}</div>
                        <div class="timestamp">${time}</div>
                    </div>`;
                });
            }

            document.getElementById('security-events').innerHTML = html;
        }

        function updateThreatAnalysis() {
            const analysis = analysisData.threat_analysis;
            if (!analysis) return;

            let html = '';
            const recent = analysis.slice(-3);

            if (recent.length === 0) {
                html = '<div class="event-item pulse">🧠 Iniciando análisis con IA...</div>';
            } else {
                recent.reverse().forEach(item => {
                    const time = new Date(item.timestamp).toLocaleTimeString();

                    html += `<div class="event-item">
                        <div><strong>🤖 Análisis IA</strong> - Confianza: ${item.ai_confidence.toFixed(1)}%</div>
                        <div><strong>Evaluación de Riesgo:</strong>
                        <span class="threat-level threat-${item.risk_assessment.toLowerCase()}">${item.risk_assessment}</span></div>
                    `;

                    if (item.threat_patterns && item.threat_patterns.length > 0) {
                        html += '<div><strong>Patrones Detectados:</strong></div>';
                        item.threat_patterns.forEach(pattern => {
                            html += `<div style="margin-left: 15px;">
                                • ${pattern.description} (${(pattern.confidence * 100).toFixed(0)}% confianza)
                            </div>`;
                        });
                    }

                    if (item.recommendations && item.recommendations.length > 0) {
                        html += '<div><strong>Recomendaciones:</strong></div>';
                        item.recommendations.forEach(rec => {
                            html += `<div style="margin-left: 15px;">💡 ${rec}</div>`;
                        });
                    }

                    html += `<div class="timestamp">${time}</div></div>`;
                });
            }

            document.getElementById('threat-analysis').innerHTML = html;
        }

        // Inicializar
        updateDashboard();
    </script>
</body>
</html>"""

    def log_message(self, format, *args):
        """Suprimir logs del servidor HTTP"""
        pass


def start_web_server(analyzer: LiveSystemAnalyzer, port: int = 8888):
    """Iniciar servidor web"""
    WebInterface.analyzer = analyzer

    try:
        server = HTTPServer(('localhost', port), WebInterface)
        print(f"🌐 Servidor web iniciado en http://localhost:{port}")

        # Abrir navegador
        try:
            webbrowser.open(f'http://localhost:{port}')
        except:
            print("⚠️  No se pudo abrir el navegador automáticamente")

        # Ejecutar servidor en thread separado
        server_thread = threading.Thread(target=server.serve_forever, daemon=True)
        server_thread.start()

        return server

    except OSError as e:
        if e.errno == 98:  # Address already in use
            print(f"⚠️  Puerto {port} ya está en uso, intentando puerto {port + 1}")
            return start_web_server(analyzer, port + 1)
        else:
            raise


async def main():
    """Función principal"""
    print("🚀 SmartCompute Enterprise - Análisis Local en Tiempo Real")
    print("=" * 60)

    # Crear analizador
    analyzer = LiveSystemAnalyzer()

    # Iniciar servidor web
    server = start_web_server(analyzer)

    try:
        # Iniciar análisis
        await analyzer.start_analysis()

        print("\n✅ Análisis completado!")
        print("🌐 La interfaz web seguirá disponible por unos minutos más")
        print("📄 Presiona Ctrl+C para cerrar")

        # Mantener servidor activo por un tiempo adicional
        await asyncio.sleep(60)  # 1 minuto adicional

    except KeyboardInterrupt:
        print("\n🛑 Análisis interrumpido por el usuario")

    finally:
        if server:
            server.shutdown()
        print("👋 Análisis finalizado")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Programa terminado")
    except Exception as e:
        print(f"❌ Error: {e}")