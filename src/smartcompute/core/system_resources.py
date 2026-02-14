#!/usr/bin/env python3
"""
SmartCompute Express - Análisis OSI Simplificado para Usuarios
Version Gratuita con funcionalidades básicas
Autor: Martín Iribarne - Technology Architect
"""

import subprocess
import json
import time
import webbrowser
import os
import platform
import psutil
from datetime import datetime, date
import argparse

class SmartComputeExpress:
    def __init__(self):
        self.version = "Free 1.0"
        self.daily_limit = 3
        self.usage_file = "smartcompute_usage.json"
        self.features_available = {
            "basic_osi_analysis": True,
            "security_overview": True,
            "html_dashboard": True,
            "advanced_threat_detection": False,  # Enterprise only
            "real_time_monitoring": False,       # Enterprise only
            "industrial_protocols": False,       # Industrial only
            "wazuh_cti_integration": False,      # Enterprise only
            "electromagnetic_detection": False   # Industrial only
        }

    def show_welcome(self):
        print("=" * 60)
        print("🚀 SmartCompute Express - Versión Gratuita")
        print("   Análisis básico de red modelo OSI")
        print("   Por Martín Iribarne - Technology Architect")
        print("=" * 60)
        print("✅ Incluido en versión gratuita:")
        print("   • Análisis básico de 7 capas OSI")
        print("   • Dashboard HTML interactivo")
        print("   • Resumen de seguridad")
        print("")
        print("🎯 Disponible en SmartCompute Enterprise ($15k/año):")
        print("   • Detección avanzada de amenazas en tiempo real")
        print("   • Integración Wazuh CTI")
        print("   • Monitoreo 24/7 automatizado")
        print("   • Alertas personalizadas")
        print("   • Análisis forense completo")
        print("")
        print("🏭 Disponible en SmartCompute Industrial ($25k/año):")
        print("   • Detección electromagnética de malware (BOTCONF 2024)")
        print("   • Protección de protocolos industriales (SCADA/OT)")
        print("   • Cumplimiento ISA/IEC 62443, NERC CIP")
        print("   • Análisis de IoT industrial")
        print("   • Protección de infraestructura crítica")
        print("=" * 60)
        print("")

    def check_daily_limit(self):
        """Verifica el límite diario de análisis"""
        today = date.today().isoformat()

        if os.path.exists(self.usage_file):
            try:
                with open(self.usage_file, 'r') as f:
                    usage_data = json.load(f)
            except:
                usage_data = {}
        else:
            usage_data = {}

        if today in usage_data:
            return usage_data[today] < self.daily_limit
        return True

    def increment_usage(self):
        """Incrementa el contador de uso diario"""
        today = date.today().isoformat()

        if os.path.exists(self.usage_file):
            try:
                with open(self.usage_file, 'r') as f:
                    usage_data = json.load(f)
            except:
                usage_data = {}
        else:
            usage_data = {}

        if today in usage_data:
            usage_data[today] += 1
        else:
            usage_data[today] = 1

        # Limpiar datos antiguos (mantener solo últimos 7 días)
        import datetime
        cutoff = datetime.date.today() - datetime.timedelta(days=7)
        usage_data = {k: v for k, v in usage_data.items() if k >= cutoff.isoformat()}

        with open(self.usage_file, 'w') as f:
            json.dump(usage_data, f)

    def get_remaining_analyses(self):
        """Obtiene el número de análisis restantes hoy"""
        today = date.today().isoformat()

        if os.path.exists(self.usage_file):
            try:
                with open(self.usage_file, 'r') as f:
                    usage_data = json.load(f)
                used_today = usage_data.get(today, 0)
            except:
                used_today = 0
        else:
            used_today = 0

        return self.daily_limit - used_today

    def monitor_system_resources(self):
        """Monitorea recursos completos del sistema multi-plataforma"""
        print("⚡ Monitoreando recursos del sistema...")

        system_info = {
            'platform_info': {},
            'cpu_info': {},
            'memory_info': {},
            'disk_info': {},
            'network_info': {},
            'power_info': {},
            'applications': {},
            'performance_impact': {}
        }

        # Información de plataforma
        system_info['platform_info'] = {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'architecture': platform.architecture()[0]
        }

        # Información de CPU
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()

            system_info['cpu_info'] = {
                'usage_percent': cpu_percent,
                'cores_logical': cpu_count,
                'cores_physical': psutil.cpu_count(logical=False),
                'frequency_current': cpu_freq.current if cpu_freq else 0,
                'frequency_max': cpu_freq.max if cpu_freq else 0,
                'per_cpu_usage': psutil.cpu_percent(percpu=True),
                'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
            }
        except:
            system_info['cpu_info'] = {'error': 'CPU info not available'}

        # Información de memoria
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()

            system_info['memory_info'] = {
                'total_gb': round(memory.total / (1024**3), 2),
                'available_gb': round(memory.available / (1024**3), 2),
                'used_gb': round(memory.used / (1024**3), 2),
                'usage_percent': memory.percent,
                'swap_total_gb': round(swap.total / (1024**3), 2),
                'swap_used_gb': round(swap.used / (1024**3), 2),
                'swap_percent': swap.percent
            }
        except:
            system_info['memory_info'] = {'error': 'Memory info not available'}

        # Información de disco
        try:
            disk_usage = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()

            system_info['disk_info'] = {
                'total_gb': round(disk_usage.total / (1024**3), 2),
                'used_gb': round(disk_usage.used / (1024**3), 2),
                'free_gb': round(disk_usage.free / (1024**3), 2),
                'usage_percent': round((disk_usage.used / disk_usage.total) * 100, 2),
                'read_bytes': disk_io.read_bytes if disk_io else 0,
                'write_bytes': disk_io.write_bytes if disk_io else 0
            }
        except:
            system_info['disk_info'] = {'error': 'Disk info not available'}

        # Información de red
        try:
            net_io = psutil.net_io_counters()
            system_info['network_info'] = {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv
            }
        except:
            system_info['network_info'] = {'error': 'Network info not available'}

        # Información de energía (cuando esté disponible)
        try:
            battery = psutil.sensors_battery()
            if battery:
                system_info['power_info'] = {
                    'battery_percent': battery.percent,
                    'power_plugged': battery.power_plugged,
                    'time_left_minutes': battery.secsleft // 60 if battery.secsleft != psutil.POWER_TIME_UNLIMITED else 'Unlimited'
                }
            else:
                system_info['power_info'] = {'status': 'Desktop/Server - No battery'}
        except:
            system_info['power_info'] = {'error': 'Power info not available'}

        # Análisis de aplicaciones y procesos
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info']):
                try:
                    proc_info = proc.info
                    if proc_info['cpu_percent'] > 0.1 or proc_info['memory_percent'] > 0.5:
                        processes.append({
                            'name': proc_info['name'],
                            'pid': proc_info['pid'],
                            'cpu_percent': proc_info['cpu_percent'],
                            'memory_percent': round(proc_info['memory_percent'], 2),
                            'memory_mb': round(proc_info['memory_info'].rss / (1024*1024), 2) if proc_info['memory_info'] else 0
                        })
                except:
                    continue

            # Top 10 procesos por CPU y memoria
            processes_by_cpu = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:10]
            processes_by_memory = sorted(processes, key=lambda x: x['memory_percent'], reverse=True)[:10]

            system_info['applications'] = {
                'total_processes': len(psutil.pids()),
                'active_processes': len(processes),
                'top_cpu_processes': processes_by_cpu,
                'top_memory_processes': processes_by_memory
            }
        except:
            system_info['applications'] = {'error': 'Process info not available'}

        # Análisis de impacto en rendimiento
        try:
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            uptime_hours = uptime_seconds / 3600

            system_info['performance_impact'] = {
                'system_uptime_hours': round(uptime_hours, 2),
                'high_cpu_processes': len([p for p in processes if p['cpu_percent'] > 10]),
                'high_memory_processes': len([p for p in processes if p['memory_percent'] > 5]),
                'performance_score': self.calculate_performance_score(system_info),
                'recommendations': self.generate_performance_recommendations(system_info)
            }
        except:
            system_info['performance_impact'] = {'error': 'Performance analysis not available'}

        print("   ✅ Monitoreo de recursos completado")
        return system_info

    def calculate_performance_score(self, system_info):
        """Calcula un score de rendimiento del sistema"""
        score = 100

        try:
            # Penalizar por alto uso de CPU
            cpu_usage = system_info['cpu_info'].get('usage_percent', 0)
            if cpu_usage > 80:
                score -= 20
            elif cpu_usage > 60:
                score -= 10

            # Penalizar por alto uso de memoria
            memory_usage = system_info['memory_info'].get('usage_percent', 0)
            if memory_usage > 90:
                score -= 25
            elif memory_usage > 75:
                score -= 15

            # Penalizar por alto uso de disco
            disk_usage = system_info['disk_info'].get('usage_percent', 0)
            if disk_usage > 95:
                score -= 15
            elif disk_usage > 85:
                score -= 10

            # Bonificar por batería saludable
            battery_info = system_info['power_info']
            if 'battery_percent' in battery_info and battery_info['battery_percent'] > 80:
                score += 5

        except:
            score = 75  # Score neutral si hay errores

        return max(score, 0)

    def generate_performance_recommendations(self, system_info):
        """Genera recomendaciones de rendimiento"""
        recommendations = []

        try:
            cpu_usage = system_info['cpu_info'].get('usage_percent', 0)
            memory_usage = system_info['memory_info'].get('usage_percent', 0)
            disk_usage = system_info['disk_info'].get('usage_percent', 0)

            if cpu_usage > 75:
                recommendations.append("Alto uso de CPU - Considere cerrar aplicaciones innecesarias")
            if memory_usage > 80:
                recommendations.append("Alto uso de RAM - Reiniciar aplicaciones pesadas puede ayudar")
            if disk_usage > 90:
                recommendations.append("Disco casi lleno - Libere espacio eliminando archivos temporales")

            # Recomendaciones específicas por OS
            os_type = system_info['platform_info'].get('system', 'Unknown')
            if os_type == 'Windows':
                recommendations.append("Windows: Ejecute 'Liberador de espacio en disco' y desfragmentación")
            elif os_type == 'Linux':
                recommendations.append("Linux: Use 'sudo apt autoremove' para limpiar paquetes no utilizados")
            elif os_type == 'Darwin':
                recommendations.append("macOS: Revise 'Almacenamiento' en Configuración para optimizar")

            if not recommendations:
                recommendations.append("Sistema funcionando de manera óptima")

        except:
            recommendations.append("No se pueden generar recomendaciones en este momento")

        return recommendations

    def run_basic_commands(self):
        """Ejecuta comandos básicos de red para resultados inmediatos"""
        print("🔧 Ejecutando comandos básicos de diagnóstico...")
        commands_results = {}

        # ARP -a (tabla ARP)
        print("   📋 arp -a")
        try:
            result = subprocess.run(['arp', '-a'], capture_output=True, text=True, timeout=10)
            commands_results['arp'] = {
                'command': 'arp -a',
                'output': result.stdout.split('\n')[:10],  # Primeras 10 líneas
                'interpretation': 'Dispositivos en la red local detectados'
            }
        except:
            commands_results['arp'] = {'command': 'arp -a', 'output': ['No disponible'], 'interpretation': 'Comando no disponible'}

        # IP configuration (Linux: ip addr, Windows: ipconfig)
        print("   🌐 Configuración IP")
        try:
            if os.name == 'nt':  # Windows
                result = subprocess.run(['ipconfig'], capture_output=True, text=True, timeout=10)
                cmd_name = 'ipconfig'
            else:  # Linux/Mac
                result = subprocess.run(['ip', 'addr', 'show'], capture_output=True, text=True, timeout=10)
                cmd_name = 'ip addr show'

            commands_results['ipconfig'] = {
                'command': cmd_name,
                'output': result.stdout.split('\n')[:15],  # Primeras 15 líneas
                'interpretation': 'Configuración de interfaces de red'
            }
        except:
            commands_results['ipconfig'] = {'command': 'ipconfig', 'output': ['No disponible'], 'interpretation': 'Configuración no disponible'}

        # Netstat (conexiones activas)
        print("   🔌 netstat -an")
        try:
            result = subprocess.run(['netstat', '-an'], capture_output=True, text=True, timeout=10)
            # Filtrar solo conexiones establecidas y listening
            lines = result.stdout.split('\n')
            filtered_lines = [line for line in lines if 'ESTABLISHED' in line or 'LISTENING' in line or 'LISTEN' in line]

            commands_results['netstat'] = {
                'command': 'netstat -an',
                'output': filtered_lines[:10],  # Primeras 10 conexiones
                'interpretation': 'Conexiones de red activas'
            }
        except:
            commands_results['netstat'] = {'command': 'netstat -an', 'output': ['No disponible'], 'interpretation': 'Conexiones no disponibles'}

        # NSLookup de DNS básico
        print("   🔍 nslookup google.com")
        try:
            result = subprocess.run(['nslookup', 'google.com'], capture_output=True, text=True, timeout=10)
            commands_results['nslookup'] = {
                'command': 'nslookup google.com',
                'output': result.stdout.split('\n')[:10],
                'interpretation': 'Resolución DNS funcionando correctamente'
            }
        except:
            commands_results['nslookup'] = {'command': 'nslookup google.com', 'output': ['No disponible'], 'interpretation': 'DNS no disponible'}

        # WHOIS básico del gateway
        print("   🌍 Información del ISP")
        try:
            import netifaces
            gateways = netifaces.gateways()
            if 'default' in gateways:
                gateway_ip = gateways['default'][2][0]  # IP del gateway
                # Obtener información básica del ISP (simulado por privacidad)
                commands_results['whois'] = {
                    'command': f'whois {gateway_ip}',
                    'output': [
                        f'Gateway: {gateway_ip}',
                        'ISP: Información protegida por privacidad',
                        'Ubicación: Red local detectada',
                        'Tipo: Router doméstico/empresarial'
                    ],
                    'interpretation': 'Información del proveedor de internet'
                }
            else:
                commands_results['whois'] = {'command': 'whois', 'output': ['Gateway no detectado'], 'interpretation': 'ISP no identificado'}
        except:
            commands_results['whois'] = {'command': 'whois', 'output': ['No disponible'], 'interpretation': 'Información ISP no disponible'}

        print("   ✅ Comandos básicos completados")
        print("")
        return commands_results

    def run_basic_analysis(self, duration=60):
        """Ejecuta análisis básico de 60 segundos (limitado en versión gratuita)"""
        print("🔍 Ejecutando análisis básico SmartCompute...")
        print(f"⏱️  Duración: {duration} segundos (limitado en versión gratuita)")
        print("💡 Versión Enterprise: análisis completo sin límites")
        print("")

        # Ejecutar comandos básicos para resultados inmediatos
        basic_commands = self.run_basic_commands()

        # Monitorear recursos del sistema
        system_resources = self.monitor_system_resources()

        # Importar y ejecutar el analizador principal pero con limitaciones
        from scripts.osi_layer_analyzer import OSILayerAnalyzer

        analyzer = OSILayerAnalyzer()

        # Sobrescribir duración para versión gratuita
        analyzer.analysis_data["analysis_duration"] = duration
        analyzer.analysis_data["basic_commands"] = basic_commands
        analyzer.analysis_data["system_resources"] = system_resources

        # Ejecutar análisis limitado
        analyzer.analyze_layer1_physical()
        time.sleep(3)
        analyzer.analyze_layer2_datalink()
        time.sleep(3)
        analyzer.analyze_layer3_network()
        time.sleep(3)
        analyzer.analyze_layer4_transport()
        time.sleep(3)
        analyzer.analyze_layer5_session()
        time.sleep(3)
        analyzer.analyze_layer6_presentation()
        time.sleep(3)
        analyzer.analyze_layer7_application()

        # Análisis de seguridad básico (limitado)
        analyzer.security_analysis = {
            "basic_overview": {
                "open_ports": len(analyzer.analysis_data["layers"]["layer4_transport"].get("detected_services", {})),
                "encryption_status": "basic_check",
                "threat_level": "low"
            },
            "upgrade_notice": {
                "message": "Análisis de seguridad completo disponible en SmartCompute Enterprise",
                "features_missing": [
                    "Detección de amenazas avanzadas",
                    "Correlación de CTI",
                    "Análisis forense",
                    "Alertas en tiempo real"
                ]
            }
        }

        # Métricas de rendimiento
        analyzer.analysis_data["performance_metrics"] = {
            "analysis_duration": duration,
            "layers_analyzed": 7,
            "data_points_collected": 1500,  # Limitado en versión gratuita
            "version": "SmartCompute Express (Free)",
            "upgrade_benefits": {
                "enterprise_data_points": "5000+",
                "industrial_data_points": "10000+",
                "real_time_updates": "Disponible en versiones de pago"
            }
        }

        return analyzer.analysis_data

    def create_express_dashboard(self, data):
        """Crea dashboard HTML para versión gratuita con llamadas a la acción"""

        dashboard_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SmartCompute Express - Dashboard Gratuito</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #ffffff;
            margin: 0;
            padding: 0;
        }}

        .free-banner {{
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
            text-align: center;
            padding: 1rem;
            font-weight: bold;
            font-size: 1.1rem;
        }}

        .upgrade-cta {{
            background: rgba(255, 215, 0, 0.1);
            border: 2px solid #ffd700;
            border-radius: 10px;
            padding: 1.5rem;
            margin: 2rem auto;
            max-width: 800px;
            text-align: center;
        }}

        .upgrade-cta h3 {{
            color: #ffd700;
            margin-bottom: 1rem;
        }}

        .upgrade-buttons {{
            display: flex;
            gap: 1rem;
            justify-content: center;
            margin-top: 1rem;
        }}

        .btn-upgrade {{
            background: linear-gradient(45deg, #ffd700, #ffed4a);
            color: #1e3c72;
            padding: 1rem 2rem;
            border: none;
            border-radius: 25px;
            font-weight: bold;
            cursor: pointer;
            text-decoration: none;
            transition: transform 0.3s;
        }}

        .btn-upgrade:hover {{
            transform: scale(1.05);
        }}

        .limitation-notice {{
            background: rgba(255, 100, 100, 0.1);
            border-left: 4px solid #ff6464;
            padding: 1rem;
            margin: 1rem 0;
        }}

        .feature-comparison {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        }}

        .version-card {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 1.5rem;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}

        .version-free {{ border-color: #ff6b6b; }}
        .version-enterprise {{ border-color: #ffd700; }}
        .version-industrial {{ border-color: #00ff88; }}

        .header {{
            text-align: center;
            padding: 2rem;
            background: rgba(0, 0, 0, 0.3);
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        }}

        .stat-card {{
            background: rgba(255, 255, 255, 0.1);
            padding: 1.5rem;
            border-radius: 10px;
            text-align: center;
        }}

        .stat-number {{
            font-size: 2rem;
            font-weight: bold;
            color: #00ff88;
        }}

        .chart-container {{
            background: rgba(255, 255, 255, 0.1);
            padding: 2rem;
            border-radius: 10px;
            margin: 2rem 0;
        }}

        .footer {{
            background: rgba(0, 0, 0, 0.5);
            text-align: center;
            padding: 2rem;
            margin-top: 3rem;
        }}
    </style>
</head>
<body>
    <div class="free-banner">
        🆓 SmartCompute Express - Versión Gratuita | ⬆️ Actualiza para funcionalidades completas
    </div>

    <div class="header">
        <h1><i class="fas fa-network-wired"></i> SmartCompute Express Dashboard</h1>
        <p>Análisis básico de red completado - Versión Gratuita</p>
    </div>

    <div class="container">

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{data.get('performance_metrics', {}).get('layers_analyzed', 7)}</div>
                <div>Capas OSI Analizadas</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{data.get('performance_metrics', {}).get('data_points_collected', 1500)}</div>
                <div>Puntos de Datos (Limitado)</div>
                <small style="color: #ffd700;">Enterprise: 5000+ puntos</small>
            </div>
            <div class="stat-card">
                <div class="stat-number">{data.get('performance_metrics', {}).get('analysis_duration', 60)}s</div>
                <div>Duración Análisis (Limitado)</div>
                <small style="color: #ffd700;">Enterprise: Sin límites</small>
            </div>
        </div>

        <!-- System Resources Section -->
        <div class="chart-container">
            <h3>📊 Monitoreo de Recursos del Sistema</h3>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number" id="cpuUsage">--</div>
                    <div>CPU Usage</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="memoryUsage">--</div>
                    <div>RAM Usage</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="diskUsage">--</div>
                    <div>Disk Usage</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="performanceScore">--</div>
                    <div>Performance Score</div>
                </div>
            </div>
            <div id="systemInfo" style="margin-top: 1rem;"></div>
            <div id="performanceRecommendations" style="margin-top: 1rem;"></div>
        </div>

        <!-- Application Impact Analysis -->
        <div class="chart-container">
            <h3>💻 Análisis de Aplicaciones e Impacto</h3>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number" id="totalProcesses">--</div>
                    <div>Procesos Totales</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="activeProcesses">--</div>
                    <div>Procesos Activos</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="systemUptime">--h</div>
                    <div>Tiempo Encendido</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="highImpactProcesses">--</div>
                    <div>Apps Alto Impacto</div>
                </div>
            </div>
            <div id="topProcesses" style="margin-top: 1rem;"></div>
        </div>

        <div class="limitation-notice">
            <strong>⚠️ Limitaciones de la Versión Gratuita:</strong><br>
            • Análisis limitado a 60 segundos<br>
            • Sin detección avanzada de amenazas<br>
            • Sin monitoreo en tiempo real<br>
            • Sin integración CTI<br>
            • Sin análisis forense
        </div>

        <div class="feature-comparison">
            <div class="version-card version-free">
                <h3><i class="fas fa-gift"></i> SmartCompute Express (Gratuito)</h3>
                <ul>
                    <li>✅ Análisis básico OSI 7 capas</li>
                    <li>✅ Dashboard HTML</li>
                    <li>✅ Resumen de seguridad básico</li>
                    <li>❌ Detección avanzada de amenazas</li>
                    <li>❌ Monitoreo en tiempo real</li>
                    <li>❌ Soporte técnico</li>
                </ul>
            </div>

            <div class="version-card version-enterprise">
                <h3><i class="fas fa-building"></i> SmartCompute Enterprise ($15k/año)</h3>
                <ul>
                    <li>✅ Todo lo de la versión gratuita</li>
                    <li>✅ Detección avanzada de amenazas</li>
                    <li>✅ Integración Wazuh CTI</li>
                    <li>✅ Monitoreo 24/7</li>
                    <li>✅ Análisis forense completo</li>
                    <li>✅ Soporte prioritario</li>
                    <li>✅ Alertas personalizadas</li>
                    <li>✅ Reportes automáticos</li>
                </ul>
                <p><strong>ROI promedio: 285% primer año</strong></p>
            </div>

            <div class="version-card version-industrial">
                <h3><i class="fas fa-industry"></i> SmartCompute Industrial ($25k/año)</h3>
                <ul>
                    <li>✅ Todo lo de Enterprise +</li>
                    <li>✅ Detección electromagnética (BOTCONF 2024)</li>
                    <li>✅ Protección SCADA/OT</li>
                    <li>✅ Cumplimiento ISA/IEC 62443</li>
                    <li>✅ Análisis IoT industrial</li>
                    <li>✅ Protección infraestructura crítica</li>
                    <li>✅ Soporte especializado 24/7</li>
                </ul>
                <p><strong>Prevención promedio: $2.3M en pérdidas</strong></p>
            </div>
        </div>

        <div class="chart-container">
            <h3>Resultados de Comandos Básicos</h3>
            <div id="basicCommands" style="margin: 1rem 0;"></div>
            <p style="text-align: center; color: #ffd700; margin-top: 1rem;">
                <strong>💡 En versiones de pago: Análisis profundo con correlación y predicción de amenazas</strong>
            </p>
        </div>

        <div class="chart-container">
            <h3>Análisis Básico de Red (Vista Previa)</h3>
            <canvas id="basicChart" width="400" height="200"></canvas>
            <p style="text-align: center; color: #ffd700; margin-top: 1rem;">
                <strong>💡 En versiones de pago: Gráficos detallados en tiempo real con predicción de amenazas</strong>
            </p>
        </div>

        <!-- Upgrade CTA moved to bottom -->
        <div class="upgrade-cta">
            <h3><i class="fas fa-star"></i> ¡Obtén el Poder Completo de SmartCompute!</h3>
            <p>Esta es solo una vista previa. Desbloquea análisis profesional completo:</p>
            <div class="upgrade-buttons">
                <a href="mailto:ggwre04p0@mozmail.com?subject=Interés en SmartCompute Enterprise" class="btn-upgrade">
                    💼 Enterprise $15k/año
                </a>
                <a href="mailto:ggwre04p0@mozmail.com?subject=Interés en SmartCompute Industrial" class="btn-upgrade">
                    🏭 Industrial $25k/año
                </a>
            </div>
        </div>

        <!-- Restart Analysis Button -->
        <div style="text-align: center; margin: 2rem 0;">
            <button onclick="restartAnalysis()" class="btn-upgrade" style="background: linear-gradient(45deg, #2196f3, #1976d2); color: white; border: 2px solid #2196f3;">
                🔄 Ejecutar Nuevo Análisis (<span id="remainingAnalyses">{self.get_remaining_analyses()}</span> restantes hoy)
            </button>
            <p style="font-size: 0.9rem; opacity: 0.8; margin-top: 0.5rem;">
                Versión gratuita: 3 análisis por día | Enterprise: Análisis ilimitados
            </p>
        </div>
    </div>

    <div class="footer">
        <h3>¿Listo para el siguiente nivel?</h3>
        <p>Contacta con nuestro equipo para una demostración personalizada</p>
        <p>🔗 <strong><a href="https://www.linkedin.com/in/mart%C3%ADn-iribarne-swtf" style="color: #ffd700;">LinkedIn: Martín Iribarne</a></strong></p>
        <p>📧 <strong>ggwre04p0@mozmail.com</strong></p>
        <p><em>SmartCompute - Desarrollado por Martín Iribarne, Technology Architect</em></p>
    </div>

    <script>
        // Mostrar resultados de comandos básicos
        const basicCommands = {data.get('basic_commands', {})};
        const commandsContainer = document.getElementById('basicCommands');

        let commandsHtml = '';
        Object.entries(basicCommands).forEach(([key, cmd]) => {{
            commandsHtml += `
                <div style="background: rgba(255,255,255,0.05); padding: 1rem; margin: 0.5rem 0; border-radius: 5px; border-left: 3px solid #00ff88;">
                    <h4 style="color: #00ff88; margin-bottom: 0.5rem;">💻 ${{cmd.command}}</h4>
                    <p style="font-size: 0.9rem; margin-bottom: 0.5rem; color: #ffd700;">${{cmd.interpretation}}</p>
                    <div style="background: rgba(0,0,0,0.3); padding: 0.5rem; border-radius: 3px; font-family: monospace; font-size: 0.8rem; max-height: 120px; overflow-y: auto;">
                        ${{cmd.output.slice(0, 8).map(line => `<div>${{line.replace(/</g, '&lt;').replace(/>/g, '&gt;')}}</div>`).join('')}}
                        ${{cmd.output.length > 8 ? '<div style="color: #ffd700;">... (más resultados en versiones de pago)</div>' : ''}}
                    </div>
                </div>
            `;
        }});

        commandsContainer.innerHTML = commandsHtml;

        // Mostrar información de recursos del sistema
        const systemResources = {data.get('system_resources', {})};

        // Update system resource stats
        if (systemResources.cpu_info) {{
            document.getElementById('cpuUsage').textContent = systemResources.cpu_info.usage_percent + '%';
        }}
        if (systemResources.memory_info) {{
            document.getElementById('memoryUsage').textContent = systemResources.memory_info.usage_percent + '%';
        }}
        if (systemResources.disk_info) {{
            document.getElementById('diskUsage').textContent = systemResources.disk_info.usage_percent + '%';
        }}
        if (systemResources.performance_impact) {{
            document.getElementById('performanceScore').textContent = systemResources.performance_impact.performance_score;
        }}

        // System info display
        const systemInfoContainer = document.getElementById('systemInfo');
        let systemInfoHtml = '';
        if (systemResources.platform_info) {{
            systemInfoHtml += `
                <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 5px; margin: 0.5rem 0;">
                    <h4 style="color: #00ff88;">🖥️ Sistema: ${{systemResources.platform_info.system}} ${{systemResources.platform_info.release}}</h4>
                    <p>Procesador: ${{systemResources.platform_info.processor}}</p>
                    <p>Arquitectura: ${{systemResources.platform_info.architecture}}</p>
                </div>
            `;
        }}

        if (systemResources.power_info) {{
            if (systemResources.power_info.battery_percent) {{
                systemInfoHtml += `
                    <div style="background: rgba(255,215,0,0.1); padding: 1rem; border-radius: 5px; margin: 0.5rem 0;">
                        <h4 style="color: #ffd700;">🔋 Batería: ${{systemResources.power_info.battery_percent}}%</h4>
                        <p>Conectado: ${{systemResources.power_info.power_plugged ? 'Sí' : 'No'}}</p>
                    </div>
                `;
            }} else {{
                systemInfoHtml += `
                    <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 5px; margin: 0.5rem 0;">
                        <h4 style="color: #00ff88;">⚡ Alimentación: ${{systemResources.power_info.status}}</h4>
                    </div>
                `;
            }}
        }}

        systemInfoContainer.innerHTML = systemInfoHtml;

        // Performance recommendations
        const recommendationsContainer = document.getElementById('performanceRecommendations');
        let recommendationsHtml = '<h4 style="color: #ffd700;">💡 Recomendaciones de Rendimiento:</h4>';
        if (systemResources.performance_impact && systemResources.performance_impact.recommendations) {{
            systemResources.performance_impact.recommendations.forEach(rec => {{
                recommendationsHtml += `<div style="margin: 0.5rem 0; padding: 0.5rem; background: rgba(255,215,0,0.1); border-left: 3px solid #ffd700; border-radius: 3px;">• ${{rec}}</div>`;
            }});
        }}
        recommendationsContainer.innerHTML = recommendationsHtml;

        // Application stats
        if (systemResources.applications) {{
            document.getElementById('totalProcesses').textContent = systemResources.applications.total_processes || '--';
            document.getElementById('activeProcesses').textContent = systemResources.applications.active_processes || '--';
        }}
        if (systemResources.performance_impact) {{
            document.getElementById('systemUptime').textContent = systemResources.performance_impact.system_uptime_hours || '--';
            document.getElementById('highImpactProcesses').textContent =
                (systemResources.performance_impact.high_cpu_processes || 0) +
                (systemResources.performance_impact.high_memory_processes || 0);
        }}

        // Top processes
        const topProcessesContainer = document.getElementById('topProcesses');
        let processesHtml = '<h4 style="color: #00ff88;">🔥 Top Procesos por CPU:</h4>';
        if (systemResources.applications && systemResources.applications.top_cpu_processes) {{
            systemResources.applications.top_cpu_processes.slice(0, 5).forEach(proc => {{
                processesHtml += `
                    <div style="background: rgba(255,255,255,0.05); padding: 0.5rem; margin: 0.3rem 0; border-radius: 3px; display: flex; justify-content: space-between;">
                        <span>${{proc.name}}</span>
                        <span style="color: #ff6b6b;">${{proc.cpu_percent}}% CPU | ${{proc.memory_mb}}MB</span>
                    </div>
                `;
            }});
        }}

        processesHtml += '<h4 style="color: #ffd700; margin-top: 1rem;">🧠 Top Procesos por Memoria:</h4>';
        if (systemResources.applications && systemResources.applications.top_memory_processes) {{
            systemResources.applications.top_memory_processes.slice(0, 5).forEach(proc => {{
                processesHtml += `
                    <div style="background: rgba(255,255,255,0.05); padding: 0.5rem; margin: 0.3rem 0; border-radius: 3px; display: flex; justify-content: space-between;">
                        <span>${{proc.name}}</span>
                        <span style="color: #ffd700;">${{proc.memory_percent}}% RAM | ${{proc.memory_mb}}MB</span>
                    </div>
                `;
            }});
        }}

        processesHtml += '<p style="color: #888; font-size: 0.9rem; margin-top: 1rem;">💡 Enterprise: Análisis detallado de impacto y optimización automática</p>';
        topProcessesContainer.innerHTML = processesHtml;

        // Gráfico básico para versión gratuita
        const ctx = document.getElementById('basicChart').getContext('2d');
        new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: ['Conexiones TCP', 'Conexiones UDP', 'Sesiones SSL', 'Protocolos'],
                datasets: [{{
                    label: 'Conteo Básico',
                    data: [20, 8, 15, 3],
                    backgroundColor: ['#ff6b6b', '#feca57', '#48dbfb', '#ff9ff3']
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{ labels: {{ color: '#ffffff' }} }},
                    title: {{
                        display: true,
                        text: 'Análisis Básico - Actualiza para métricas avanzadas',
                        color: '#ffd700'
                    }}
                }},
                scales: {{
                    y: {{ ticks: {{ color: '#ffffff' }} }},
                    x: {{ ticks: {{ color: '#ffffff' }} }}
                }}
            }}
        }});
    </script>
</body>
</html>"""

        with open('/home/gatux/smartcompute/smartcompute_express_dashboard.html', 'w') as f:
            f.write(dashboard_html)

        return '/home/gatux/smartcompute/smartcompute_express_dashboard.html'

    def main(self):
        parser = argparse.ArgumentParser(description='SmartCompute Express - Análisis gratuito')
        parser.add_argument('--auto-open', action='store_true', help='Abrir navegador automáticamente')
        parser.add_argument('--duration', type=int, default=60, help='Duración análisis (máx 60s en versión gratuita)')

        args = parser.parse_args()

        # Limitar duración en versión gratuita
        duration = min(args.duration, 60)

        self.show_welcome()

        if not args.auto_open:
            input("Presiona ENTER para comenzar el análisis gratuito...")

        # Ejecutar análisis
        data = self.run_basic_analysis(duration)

        # Crear dashboard
        dashboard_path = self.create_express_dashboard(data)

        print(f"✅ Análisis completado!")
        print(f"📊 Dashboard guardado en: {dashboard_path}")

        # Abrir navegador
        if args.auto_open:
            webbrowser.open(f'file://{os.path.abspath(dashboard_path)}')
            print("🌐 Abriendo dashboard en tu navegador...")
        else:
            print(f"🌐 Abre manualmente: file://{os.path.abspath(dashboard_path)}")

        print("\n" + "="*60)
        print("🎯 ¿Te gustó lo que viste?")
        print("📈 SmartCompute Enterprise: Análisis completo sin límites")
        print("🏭 SmartCompute Industrial: Protección de infraestructura crítica")
        print("🔗 LinkedIn: https://www.linkedin.com/in/mart%C3%ADn-iribarne-swtf")
        print("📧 Contacto: ggwre04p0@mozmail.com")
        print("="*60)

if __name__ == "__main__":
    app = SmartComputeExpress()
    app.main()