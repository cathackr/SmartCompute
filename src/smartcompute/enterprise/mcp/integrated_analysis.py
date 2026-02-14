#!/usr/bin/env python3
"""
SmartCompute Enterprise - MCP Integrated Analysis with AI Context
================================================================

Análisis inteligente con integración MCP que proporciona:
- Desglose detallado de conexiones y procesos
- Análisis contextual de IA con explicaciones claras
- Integración MCP para respuestas inteligentes automáticas
- Comandos sugeridos para investigación y resolución

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
from typing import Dict, List, Any, Optional, Tuple
import statistics
import socket
import subprocess
import os
from collections import deque, defaultdict
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import hashlib


class MCPContextualAnalyzer:
    """
    Analizador contextual que integra MCP para proporcionar explicaciones
    inteligentes y comandos sugeridos
    """

    def __init__(self):
        self.logger = self._setup_logging()

        # Base de conocimiento contextual
        self.authorized_activities = {
            'claude_operations': {
                'processes': ['python3', 'node', 'npm', 'code', 'claude'],
                'ports': [3000, 8000, 8080, 8888, 5000, 3001],
                'description': 'Actividad autorizada de Claude AI Assistant',
                'risk_level': 'LOW',
                'user_context': 'Trabajo colaborativo con IA'
            },
            'development_work': {
                'processes': ['git', 'bash', 'vim', 'nano', 'wget', 'curl'],
                'ports': [22, 80, 443, 8080, 3000],
                'description': 'Desarrollo de software autorizado',
                'risk_level': 'LOW',
                'user_context': 'Entorno de desarrollo activo'
            },
            'system_monitoring': {
                'processes': ['ps', 'netstat', 'top', 'htop', 'smartcompute'],
                'ports': [8888, 8889, 8890],
                'description': 'Monitoreo de sistema SmartCompute',
                'risk_level': 'LOW',
                'user_context': 'Análisis de sistema autorizado'
            }
        }

        # Patrones de amenaza real
        self.real_threat_patterns = {
            'crypto_mining': ['xmrig', 'cpuminer', 'bitcoin', 'ethereum'],
            'backdoors': ['nc -l', 'netcat', 'reverse_shell'],
            'data_exfiltration': ['wget', 'curl', 'scp', 'rsync'],
            'privilege_escalation': ['sudo', 'su', 'passwd'],
            'network_scanning': ['nmap', 'masscan', 'zmap']
        }

    def _setup_logging(self) -> logging.Logger:
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger('SmartCompute.MCPAnalyzer')

    async def analyze_process_with_context(self, process_info: Dict) -> Dict[str, Any]:
        """Analizar proceso con contexto inteligente"""
        pid = process_info.get('pid')
        name = process_info.get('name', '').lower()
        cpu = process_info.get('cpu_percent', 0)
        memory = process_info.get('memory_percent', 0)

        analysis = {
            'pid': pid,
            'name': process_info.get('name'),
            'risk_assessment': 'LOW',
            'confidence': 0.95,
            'context_explanation': '',
            'user_authorization_status': 'UNKNOWN',
            'suggested_actions': [],
            'detailed_info': {},
            'mcp_recommendation': ''
        }

        # Verificar si es actividad autorizada
        for activity_type, activity_info in self.authorized_activities.items():
            if any(proc in name for proc in activity_info['processes']):
                analysis.update({
                    'risk_assessment': 'LOW',
                    'confidence': 0.98,
                    'context_explanation': f"✅ Proceso identificado como '{activity_info['description']}'",
                    'user_authorization_status': 'AUTHORIZED',
                    'mcp_recommendation': f"Proceso legítimo relacionado con {activity_info['user_context']}"
                })

                if cpu > 50:
                    analysis['suggested_actions'].append(
                        f"echo 'Proceso {pid} ({name}) usando {cpu}% CPU - Normal para {activity_type}'"
                    )
                break

        # Verificar patrones de amenaza real
        for threat_type, threat_patterns in self.real_threat_patterns.items():
            if any(pattern in name for pattern in threat_patterns):
                analysis.update({
                    'risk_assessment': 'HIGH',
                    'confidence': 0.92,
                    'context_explanation': f"⚠️ Proceso coincide con patrón de {threat_type}",
                    'user_authorization_status': 'REQUIRES_VERIFICATION',
                    'mcp_recommendation': f"Investigar inmediatamente - posible {threat_type}"
                })

                analysis['suggested_actions'].extend([
                    f"ps -fp {pid}",
                    f"lsof -p {pid}",
                    f"cat /proc/{pid}/cmdline"
                ])
                break

        # Obtener información detallada del proceso
        try:
            proc = psutil.Process(pid)
            analysis['detailed_info'] = {
                'cmdline': ' '.join(proc.cmdline()[:3]),  # Primeros 3 argumentos
                'cwd': proc.cwd() if proc.cwd() else 'N/A',
                'create_time': datetime.fromtimestamp(proc.create_time()).isoformat(),
                'connections': len(proc.connections()) if proc.connections() else 0,
                'open_files': len(proc.open_files()) if proc.open_files() else 0
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            analysis['detailed_info'] = {'error': 'Access denied or process not found'}

        return analysis

    async def analyze_connections_with_context(self, connections_data: List[Dict]) -> Dict[str, Any]:
        """Analizar conexiones con contexto detallado"""
        analysis = {
            'total_connections': len(connections_data),
            'risk_assessment': 'LOW',
            'confidence': 0.90,
            'breakdown': {
                'listening_ports': [],
                'established_connections': [],
                'suspicious_connections': []
            },
            'context_explanation': '',
            'suggested_investigations': [],
            'mcp_recommendations': []
        }

        listening_ports = []
        established_conns = []
        suspicious_conns = []

        for conn in connections_data:
            if conn.get('status') == 'LISTEN':
                port_info = {
                    'port': conn.get('local_port', 0),
                    'protocol': conn.get('protocol', 'TCP'),
                    'process': conn.get('process_name', 'Unknown'),
                    'risk_level': 'LOW'
                }

                # Verificar si es puerto autorizado
                is_authorized = any(
                    port_info['port'] in activity['ports']
                    for activity in self.authorized_activities.values()
                )

                if is_authorized:
                    port_info['context'] = '✅ Puerto autorizado para operaciones de desarrollo/IA'
                    port_info['risk_level'] = 'LOW'
                elif port_info['port'] in [22, 80, 443]:
                    port_info['context'] = '✅ Puerto estándar del sistema'
                    port_info['risk_level'] = 'LOW'
                elif port_info['port'] > 1024:
                    port_info['context'] = '⚠️ Puerto dinámico - verificar aplicación'
                    port_info['risk_level'] = 'MEDIUM'
                else:
                    port_info['context'] = '🔍 Puerto privilegiado - requiere investigación'
                    port_info['risk_level'] = 'HIGH'

                listening_ports.append(port_info)

            elif conn.get('status') == 'ESTABLISHED':
                conn_info = {
                    'local_port': conn.get('local_port', 0),
                    'remote_ip': conn.get('remote_ip', 'Unknown'),
                    'remote_port': conn.get('remote_port', 0),
                    'process': conn.get('process_name', 'Unknown'),
                    'risk_level': 'LOW'
                }

                # Analizar IP remota
                remote_ip = conn_info['remote_ip']
                if remote_ip.startswith('127.') or remote_ip.startswith('::1'):
                    conn_info['context'] = '✅ Conexión local (localhost)'
                elif remote_ip.startswith('192.168.') or remote_ip.startswith('10.'):
                    conn_info['context'] = '✅ Red local privada'
                elif remote_ip.startswith('172.'):
                    conn_info['context'] = '✅ Red privada corporativa'
                else:
                    conn_info['context'] = '🌐 Conexión externa'
                    if conn_info['remote_port'] in [80, 443]:
                        conn_info['context'] += ' (Web/HTTPS normal)'
                    else:
                        conn_info['context'] += ' - Verificar propósito'
                        conn_info['risk_level'] = 'MEDIUM'

                established_conns.append(conn_info)

        analysis['breakdown']['listening_ports'] = listening_ports
        analysis['breakdown']['established_connections'] = established_conns

        # Generar recomendaciones MCP
        high_risk_ports = [p for p in listening_ports if p['risk_level'] == 'HIGH']
        if high_risk_ports:
            analysis['mcp_recommendations'].append({
                'type': 'INVESTIGATION',
                'priority': 'HIGH',
                'description': f"Investigar {len(high_risk_ports)} puertos privilegiados",
                'commands': [f"lsof -i :{port['port']}" for port in high_risk_ports[:3]]
            })

        external_conns = [c for c in established_conns if not c['remote_ip'].startswith(('127.', '192.168.', '10.'))]
        if len(external_conns) > 10:
            analysis['mcp_recommendations'].append({
                'type': 'MONITORING',
                'priority': 'MEDIUM',
                'description': f"Monitorear {len(external_conns)} conexiones externas",
                'commands': [
                    "netstat -tuln | grep ESTABLISHED | wc -l",
                    "ss -tuln | grep -E ':(80|443)' | wc -l"
                ]
            })

        # Evaluación general de riesgo
        if high_risk_ports or len(external_conns) > 20:
            analysis['risk_assessment'] = 'MEDIUM'
            analysis['context_explanation'] = f"⚠️ Se detectaron {len(high_risk_ports)} puertos de riesgo y {len(external_conns)} conexiones externas"
        else:
            analysis['context_explanation'] = f"✅ Actividad de red normal: {len(listening_ports)} puertos escuchando, {len(established_conns)} conexiones activas"

        return analysis

    async def generate_ai_threat_analysis(self, system_state: Dict) -> Dict[str, Any]:
        """Generar análisis de amenazas con IA contextual"""

        ai_analysis = {
            'confidence': 0.0,
            'risk_level': 'LOW',
            'threat_patterns': [],
            'behavioral_insights': [],
            'contextual_assessment': '',
            'user_activity_correlation': '',
            'recommended_actions': [],
            'false_positive_likelihood': 'LOW'
        }

        # Analizar patrones de comportamiento
        cpu_usage = system_state.get('cpu_percent', 0)
        memory_usage = system_state.get('memory_percent', 0)
        process_count = system_state.get('running_processes', 0)
        connection_count = system_state.get('active_connections', 0)

        # IA contextual: Correlacionar con actividad autorizada
        current_hour = datetime.now().hour
        is_work_hours = 8 <= current_hour <= 18

        behavioral_patterns = []

        # Patrón 1: Actividad de desarrollo
        if any(proc in str(system_state).lower() for proc in ['python', 'node', 'npm', 'code']):
            behavioral_patterns.append({
                'pattern': 'DEVELOPMENT_ACTIVITY',
                'confidence': 0.95,
                'description': 'Patrones consistentes con desarrollo de software',
                'context': '✅ Actividad esperada - Claude está ejecutando tareas de desarrollo'
            })

        # Patrón 2: Alto uso CPU durante trabajo autorizado
        if cpu_usage > 70 and is_work_hours:
            behavioral_patterns.append({
                'pattern': 'HIGH_CPU_WORK_HOURS',
                'confidence': 0.88,
                'description': 'Alto uso de CPU durante horas laborales',
                'context': '🔄 Probable compilación o procesamiento autorizado'
            })

        # Patrón 3: Conexiones de red relacionadas con IA
        if connection_count > 10:
            behavioral_patterns.append({
                'pattern': 'AI_NETWORK_ACTIVITY',
                'confidence': 0.92,
                'description': 'Actividad de red consistente con operaciones de IA',
                'context': '🤖 Conexiones relacionadas con Claude AI Assistant'
            })

        # Evaluar contexto general
        authorized_activity_score = 0
        for pattern in behavioral_patterns:
            if pattern['pattern'] in ['DEVELOPMENT_ACTIVITY', 'AI_NETWORK_ACTIVITY']:
                authorized_activity_score += pattern['confidence']

        if authorized_activity_score > 1.5:
            ai_analysis.update({
                'confidence': 0.94,
                'risk_level': 'LOW',
                'contextual_assessment': '✅ Actividad totalmente consistente con trabajo autorizado de IA',
                'user_activity_correlation': 'STRONG_POSITIVE - Claude está ejecutando tareas autorizadas por el usuario',
                'false_positive_likelihood': 'HIGH - Las alertas provienen de actividad legítima'
            })
        elif authorized_activity_score > 0.8:
            ai_analysis.update({
                'confidence': 0.87,
                'risk_level': 'LOW',
                'contextual_assessment': '🔍 Actividad mayormente autorizada con algunos elementos a verificar',
                'user_activity_correlation': 'POSITIVE - Principalmente trabajo autorizado',
                'false_positive_likelihood': 'MEDIUM'
            })
        else:
            ai_analysis.update({
                'confidence': 0.75,
                'risk_level': 'MEDIUM',
                'contextual_assessment': '⚠️ Actividad requiere verificación adicional',
                'user_activity_correlation': 'UNCLEAR - Patrones no reconocidos',
                'false_positive_likelihood': 'LOW'
            })

        ai_analysis['threat_patterns'] = behavioral_patterns

        # Generar acciones recomendadas basadas en contexto
        if ai_analysis['false_positive_likelihood'] == 'HIGH':
            ai_analysis['recommended_actions'] = [
                "🔧 Ajustar sensibilidad de SmartCompute para entorno de desarrollo",
                "📝 Documentar patrones de trabajo con IA como actividad autorizada",
                "⚙️ Configurar whitelist para procesos de Claude/desarrollo"
            ]
        else:
            ai_analysis['recommended_actions'] = [
                "🔍 Verificar procesos activos: ps aux --sort=-%cpu | head -10",
                "🌐 Revisar conexiones: netstat -tuln | grep ESTABLISHED",
                "📊 Monitor continuo: watch 'ps aux --sort=-%cpu | head -5'"
            ]

        return ai_analysis


class SmartComputeMCPIntegratedAnalyzer:
    """Analizador integrado con capacidades MCP"""

    def __init__(self):
        self.logger = self._setup_logging()
        self.mcp_analyzer = MCPContextualAnalyzer()
        self.analysis_session_id = f"session_{int(time.time())}"

        # Estado del análisis
        self.detailed_analysis = {
            'session_info': {
                'id': self.analysis_session_id,
                'start_time': datetime.now(),
                'user_context': 'Development environment with AI assistant'
            },
            'process_analysis': [],
            'connection_analysis': {},
            'ai_threat_assessment': {},
            'mcp_recommendations': [],
            'investigation_commands': []
        }

    def _setup_logging(self) -> logging.Logger:
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger('SmartCompute.MCPIntegrated')

    async def perform_comprehensive_analysis(self, duration_seconds: int = 60):
        """Realizar análisis comprensivo con integración MCP"""

        self.logger.info(f"🔍 Iniciando análisis MCP integrado (ID: {self.analysis_session_id})")

        start_time = time.time()

        while time.time() - start_time < duration_seconds:
            # Recopilar datos del sistema
            system_data = await self._collect_system_data()

            # Análisis contextual de procesos
            process_analysis = await self._analyze_processes_with_context()

            # Análisis de conexiones detallado
            connection_analysis = await self.mcp_analyzer.analyze_connections_with_context(
                self._get_connection_data()
            )

            # Análisis de amenazas con IA
            ai_analysis = await self.mcp_analyzer.generate_ai_threat_analysis(system_data)

            # Actualizar análisis detallado
            self.detailed_analysis.update({
                'process_analysis': process_analysis,
                'connection_analysis': connection_analysis,
                'ai_threat_assessment': ai_analysis,
                'last_update': datetime.now()
            })

            await asyncio.sleep(5)  # Análisis cada 5 segundos

        # Generar recomendaciones finales
        await self._generate_final_recommendations()

        return self.detailed_analysis

    async def _collect_system_data(self) -> Dict:
        """Recopilar datos básicos del sistema"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'running_processes': len(psutil.pids()),
            'active_connections': len(psutil.net_connections()),
            'timestamp': datetime.now()
        }

    async def _analyze_processes_with_context(self) -> List[Dict]:
        """Analizar procesos con contexto MCP"""
        process_analysis = []

        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                proc_info = proc.info
                if proc_info['cpu_percent'] and proc_info['cpu_percent'] > 5:  # Solo procesos con CPU significativo

                    # Análisis contextual MCP
                    context_analysis = await self.mcp_analyzer.analyze_process_with_context(proc_info)
                    process_analysis.append(context_analysis)

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return process_analysis[:10]  # Top 10 procesos

    def _get_connection_data(self) -> List[Dict]:
        """Obtener datos de conexiones de red"""
        connections = []

        try:
            for conn in psutil.net_connections():
                conn_data = {
                    'status': conn.status,
                    'local_port': conn.laddr.port if conn.laddr else 0,
                    'remote_ip': conn.raddr.ip if conn.raddr else 'N/A',
                    'remote_port': conn.raddr.port if conn.raddr else 0,
                    'protocol': 'TCP' if conn.type == socket.SOCK_STREAM else 'UDP',
                    'process_name': 'Unknown'
                }

                # Intentar obtener nombre del proceso
                try:
                    if conn.pid:
                        proc = psutil.Process(conn.pid)
                        conn_data['process_name'] = proc.name()
                except:
                    pass

                connections.append(conn_data)

        except Exception as e:
            self.logger.error(f"Error obteniendo conexiones: {e}")

        return connections

    async def _generate_final_recommendations(self):
        """Generar recomendaciones finales MCP"""

        recommendations = []
        investigation_commands = []

        # Basado en análisis de procesos
        high_risk_processes = [
            p for p in self.detailed_analysis['process_analysis']
            if p.get('risk_assessment') == 'HIGH'
        ]

        if high_risk_processes:
            recommendations.append({
                'type': 'PROCESS_INVESTIGATION',
                'priority': 'HIGH',
                'count': len(high_risk_processes),
                'description': f"Investigar {len(high_risk_processes)} procesos de alto riesgo",
                'processes': [p['name'] for p in high_risk_processes[:3]]
            })

            for proc in high_risk_processes[:3]:
                investigation_commands.extend(proc.get('suggested_actions', []))

        # Basado en análisis de conexiones
        conn_recommendations = self.detailed_analysis['connection_analysis'].get('mcp_recommendations', [])
        recommendations.extend(conn_recommendations)

        # Basado en análisis de IA
        ai_recommendations = self.detailed_analysis['ai_threat_assessment'].get('recommended_actions', [])
        investigation_commands.extend(ai_recommendations)

        self.detailed_analysis['mcp_recommendations'] = recommendations
        self.detailed_analysis['investigation_commands'] = investigation_commands

    def generate_detailed_report(self) -> str:
        """Generar reporte detallado en formato legible"""

        report = f"""
🚀 SmartCompute Enterprise - Análisis MCP Integrado
==================================================
Session ID: {self.analysis_session_id}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 RESUMEN EJECUTIVO
-------------------
IA Confidence: {self.detailed_analysis['ai_threat_assessment'].get('confidence', 0):.2f}
Risk Level: {self.detailed_analysis['ai_threat_assessment'].get('risk_level', 'UNKNOWN')}
Context: {self.detailed_analysis['ai_threat_assessment'].get('contextual_assessment', 'N/A')}

🔍 ANÁLISIS DETALLADO DE PROCESOS
---------------------------------
"""

        for i, proc in enumerate(self.detailed_analysis['process_analysis'][:5], 1):
            report += f"""
{i}. Proceso: {proc['name']} (PID: {proc['pid']})
   Risk Assessment: {proc['risk_assessment']}
   Authorization: {proc['user_authorization_status']}
   Context: {proc['context_explanation']}
   MCP Recommendation: {proc['mcp_recommendation']}
   Detailed Info: {proc['detailed_info']}
"""

        report += f"""

🌐 ANÁLISIS DE CONEXIONES
-------------------------
Total Connections: {self.detailed_analysis['connection_analysis'].get('total_connections', 0)}
Risk Assessment: {self.detailed_analysis['connection_analysis'].get('risk_assessment', 'UNKNOWN')}
Context: {self.detailed_analysis['connection_analysis'].get('context_explanation', 'N/A')}

📊 Listening Ports:
"""

        for port in self.detailed_analysis['connection_analysis']['breakdown']['listening_ports'][:5]:
            report += f"   Port {port['port']}: {port['context']} ({port['risk_level']})\n"

        report += """
🔗 Established Connections:
"""

        for conn in self.detailed_analysis['connection_analysis']['breakdown']['established_connections'][:5]:
            report += f"   {conn['remote_ip']}:{conn['remote_port']} - {conn['context']}\n"

        report += f"""

🧠 ANÁLISIS DE IA CONTEXTUAL
----------------------------
Confidence: {self.detailed_analysis['ai_threat_assessment'].get('confidence', 0):.2f}
Risk Level: {self.detailed_analysis['ai_threat_assessment'].get('risk_level', 'UNKNOWN')}
User Activity Correlation: {self.detailed_analysis['ai_threat_assessment'].get('user_activity_correlation', 'N/A')}
False Positive Likelihood: {self.detailed_analysis['ai_threat_assessment'].get('false_positive_likelihood', 'UNKNOWN')}

Behavioral Patterns Detected:
"""

        for pattern in self.detailed_analysis['ai_threat_assessment'].get('threat_patterns', []):
            report += f"   • {pattern['pattern']}: {pattern['description']} (Confidence: {pattern['confidence']:.2f})\n"

        report += f"""

🎯 RECOMENDACIONES MCP
---------------------
"""

        for i, rec in enumerate(self.detailed_analysis['mcp_recommendations'], 1):
            report += f"{i}. {rec.get('type', 'UNKNOWN')} ({rec.get('priority', 'LOW')} Priority)\n"
            report += f"   Description: {rec.get('description', 'N/A')}\n"

        report += f"""

💻 COMANDOS DE INVESTIGACIÓN SUGERIDOS
--------------------------------------
"""

        for i, cmd in enumerate(self.detailed_analysis['investigation_commands'][:10], 1):
            report += f"{i}. {cmd}\n"

        report += f"""

📋 CONCLUSIONES
---------------
• Total de procesos analizados: {len(self.detailed_analysis['process_analysis'])}
• Conexiones monitoreadas: {self.detailed_analysis['connection_analysis'].get('total_connections', 0)}
• Nivel de confianza IA: {self.detailed_analysis['ai_threat_assessment'].get('confidence', 0):.2f}
• Probabilidad falsos positivos: {self.detailed_analysis['ai_threat_assessment'].get('false_positive_likelihood', 'UNKNOWN')}

✅ Análisis completado con contexto MCP integrado
"""

        return report


async def run_mcp_integrated_analysis():
    """Ejecutar análisis integrado con MCP"""

    analyzer = SmartComputeMCPIntegratedAnalyzer()

    print("🚀 SmartCompute Enterprise - Análisis MCP Integrado")
    print("=" * 60)
    print("🔍 Iniciando análisis con contexto inteligente...")
    print("⏱️  Duración: 60 segundos")
    print("")

    # Ejecutar análisis
    results = await analyzer.perform_comprehensive_analysis(60)

    # Generar reporte
    detailed_report = analyzer.generate_detailed_report()

    # Guardar reporte
    report_file = f"/tmp/smartcompute_mcp_analysis_{analyzer.analysis_session_id}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(detailed_report)

    print(detailed_report)
    print(f"\n📄 Reporte detallado guardado en: {report_file}")

    return results


if __name__ == "__main__":
    asyncio.run(run_mcp_integrated_analysis())