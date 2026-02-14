#!/usr/bin/env python3
"""
OSI Layer Analyzer for SmartCompute Express
Análisis detallado de las 7 capas del modelo OSI
"""

import psutil
import socket
import subprocess
import json
import time
from datetime import datetime
import platform

class OSILayerAnalyzer:
    """Analizador completo de las 7 capas del modelo OSI"""

    def __init__(self):
        self.system_info = {
            'os': platform.system(),
            'version': platform.version(),
            'architecture': platform.architecture()[0],
            'hostname': socket.gethostname()
        }

        # Inicializar estructura de datos de análisis
        self.analysis_data = {
            "layers": {},
            "system_info": self.system_info,
            "timestamp": datetime.now().isoformat()
        }

    def analyze_all_layers(self, duration=30):
        """Analizar todas las capas OSI durante el tiempo especificado"""
        print("🔍 Analizando modelo OSI completo...")

        analysis_data = {
            'timestamp': datetime.now().isoformat(),
            'duration': duration,
            'system_info': self.system_info,
            'layers': {}
        }

        # Capa 1: Física
        print("   📡 Capa 1 - Física: Analizando interfaces físicas...")
        analysis_data['layers']['physical'] = self.analyze_physical_layer()

        # Capa 2: Enlace de datos
        print("   🔗 Capa 2 - Enlace: Analizando protocolos de enlace...")
        analysis_data['layers']['datalink'] = self.analyze_datalink_layer()

        # Capa 3: Red
        print("   🌐 Capa 3 - Red: Analizando enrutamiento IP...")
        analysis_data['layers']['network'] = self.analyze_network_layer()

        # Capa 4: Transporte
        print("   🚚 Capa 4 - Transporte: Analizando TCP/UDP...")
        analysis_data['layers']['transport'] = self.analyze_transport_layer()

        # Capa 5: Sesión
        print("   🤝 Capa 5 - Sesión: Analizando sesiones activas...")
        analysis_data['layers']['session'] = self.analyze_session_layer()

        # Capa 6: Presentación
        print("   📄 Capa 6 - Presentación: Analizando protocolos...")
        analysis_data['layers']['presentation'] = self.analyze_presentation_layer()

        # Capa 7: Aplicación
        print("   💻 Capa 7 - Aplicación: Analizando aplicaciones...")
        analysis_data['layers']['application'] = self.analyze_application_layer()

        return analysis_data

    def analyze_physical_layer(self):
        """Capa 1: Análisis de la capa física"""
        try:
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_if_stats()

            physical_data = {
                'interfaces': {},
                'total_interfaces': len(interfaces),
                'active_interfaces': 0,
                'bandwidth_info': {}
            }

            for interface, addresses in interfaces.items():
                if interface in stats:
                    interface_stat = stats[interface]
                    physical_data['interfaces'][interface] = {
                        'is_up': interface_stat.isup,
                        'duplex': str(interface_stat.duplex),
                        'speed': interface_stat.speed,  # Mbps
                        'mtu': interface_stat.mtu,
                        'addresses': []
                    }

                    if interface_stat.isup:
                        physical_data['active_interfaces'] += 1

                    # Información de bandwidth
                    if interface_stat.speed > 0:
                        physical_data['bandwidth_info'][interface] = {
                            'speed_mbps': interface_stat.speed,
                            'theoretical_max_bps': interface_stat.speed * 1024 * 1024
                        }

                    for addr in addresses:
                        physical_data['interfaces'][interface]['addresses'].append({
                            'family': str(addr.family),
                            'address': addr.address,
                            'netmask': addr.netmask,
                            'broadcast': addr.broadcast
                        })

            return physical_data

        except Exception as e:
            return {'error': str(e), 'layer': 'physical'}

    def analyze_datalink_layer(self):
        """Capa 2: Análisis de enlace de datos"""
        try:
            # ARP table analysis
            arp_result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
            arp_entries = []

            if arp_result.returncode == 0:
                for line in arp_result.stdout.split('\n'):
                    if line.strip() and '(' in line:
                        arp_entries.append(line.strip())

            # Network I/O counters
            net_io = psutil.net_io_counters(pernic=True)

            datalink_data = {
                'arp_table': {
                    'total_entries': len(arp_entries),
                    'entries': arp_entries[:10]  # Primeros 10 para el dashboard
                },
                'frame_statistics': {},
                'mac_addresses': {}
            }

            # Estadísticas de frames por interfaz
            for interface, counters in net_io.items():
                datalink_data['frame_statistics'][interface] = {
                    'packets_sent': counters.packets_sent,
                    'packets_recv': counters.packets_recv,
                    'errors_in': counters.errin,
                    'errors_out': counters.errout,
                    'drops_in': counters.dropin,
                    'drops_out': counters.dropout
                }

            return datalink_data

        except Exception as e:
            return {'error': str(e), 'layer': 'datalink'}

    def analyze_network_layer(self):
        """Capa 3: Análisis de la capa de red"""
        try:
            # Routing table
            if platform.system() == "Linux":
                route_cmd = ['ip', 'route']
            else:
                route_cmd = ['route', '-n']

            route_result = subprocess.run(route_cmd, capture_output=True, text=True)
            routes = []

            if route_result.returncode == 0:
                for line in route_result.stdout.split('\n'):
                    if line.strip():
                        routes.append(line.strip())

            # IP statistics
            net_io = psutil.net_io_counters()

            network_data = {
                'routing_table': {
                    'total_routes': len(routes),
                    'routes': routes[:15]  # Primeras 15 rutas
                },
                'ip_statistics': {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                    'packets_sent': net_io.packets_sent,
                    'packets_recv': net_io.packets_recv
                },
                'dns_servers': self.get_dns_servers(),
                'default_gateway': self.get_default_gateway()
            }

            return network_data

        except Exception as e:
            return {'error': str(e), 'layer': 'network'}

    def analyze_transport_layer(self):
        """Capa 4: Análisis de la capa de transporte"""
        try:
            # Conexiones TCP/UDP activas
            connections = psutil.net_connections()

            tcp_connections = [conn for conn in connections if conn.type == socket.SOCK_STREAM]
            udp_connections = [conn for conn in connections if conn.type == socket.SOCK_DGRAM]

            # Puertos más utilizados
            port_usage = {}
            for conn in connections:
                if conn.laddr:
                    port = conn.laddr.port
                    port_usage[port] = port_usage.get(port, 0) + 1

            # Top 10 puertos
            top_ports = sorted(port_usage.items(), key=lambda x: x[1], reverse=True)[:10]

            transport_data = {
                'tcp_connections': {
                    'total': len(tcp_connections),
                    'by_status': {},
                    'connections': []
                },
                'udp_connections': {
                    'total': len(udp_connections),
                    'connections': []
                },
                'port_analysis': {
                    'total_ports_in_use': len(port_usage),
                    'top_ports': top_ports
                }
            }

            # TCP por estado
            for conn in tcp_connections[:20]:  # Primeras 20 conexiones TCP
                status = conn.status if hasattr(conn, 'status') else 'UNKNOWN'
                transport_data['tcp_connections']['by_status'][status] = \
                    transport_data['tcp_connections']['by_status'].get(status, 0) + 1

                conn_info = {
                    'local_addr': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A",
                    'remote_addr': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A",
                    'status': status,
                    'pid': conn.pid
                }
                transport_data['tcp_connections']['connections'].append(conn_info)

            # UDP connections
            for conn in udp_connections[:15]:  # Primeras 15 conexiones UDP
                conn_info = {
                    'local_addr': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A",
                    'pid': conn.pid
                }
                transport_data['udp_connections']['connections'].append(conn_info)

            return transport_data

        except Exception as e:
            return {'error': str(e), 'layer': 'transport'}

    def analyze_session_layer(self):
        """Capa 5: Análisis de la capa de sesión"""
        try:
            # Sesiones de red activas por proceso
            processes = []

            for proc in psutil.process_iter(['pid', 'name', 'connections']):
                try:
                    proc_info = proc.info
                    if proc_info['connections']:
                        session_info = {
                            'pid': proc_info['pid'],
                            'name': proc_info['name'],
                            'connection_count': len(proc_info['connections']),
                            'connections': []
                        }

                        # Detalles de las primeras 5 conexiones del proceso
                        for conn in proc_info['connections'][:5]:
                            conn_detail = {
                                'type': 'TCP' if conn.type == socket.SOCK_STREAM else 'UDP',
                                'local': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A",
                                'remote': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A",
                                'status': conn.status if hasattr(conn, 'status') else 'N/A'
                            }
                            session_info['connections'].append(conn_detail)

                        processes.append(session_info)

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Ordenar por número de conexiones
            processes.sort(key=lambda x: x['connection_count'], reverse=True)

            session_data = {
                'active_sessions': len(processes),
                'processes_with_network': processes[:15],  # Top 15 procesos
                'session_summary': {
                    'total_processes_with_network': len(processes),
                    'total_connections': sum(p['connection_count'] for p in processes)
                }
            }

            return session_data

        except Exception as e:
            return {'error': str(e), 'layer': 'session'}

    def analyze_presentation_layer(self):
        """Capa 6: Análisis de la capa de presentación"""
        try:
            # Análisis de protocolos de presentación comunes
            presentation_data = {
                'ssl_tls_connections': 0,
                'http_connections': 0,
                'https_connections': 0,
                'ssh_connections': 0,
                'protocol_analysis': {},
                'encryption_status': {}
            }

            connections = psutil.net_connections()

            for conn in connections:
                if conn.laddr:
                    port = conn.laddr.port

                    # Identificar protocolos comunes por puerto
                    if port == 443:  # HTTPS/TLS
                        presentation_data['https_connections'] += 1
                        presentation_data['ssl_tls_connections'] += 1
                    elif port == 80:  # HTTP
                        presentation_data['http_connections'] += 1
                    elif port == 22:  # SSH
                        presentation_data['ssh_connections'] += 1

                    # Conteo por protocolo
                    protocol_name = self.get_protocol_name(port)
                    if protocol_name:
                        presentation_data['protocol_analysis'][protocol_name] = \
                            presentation_data['protocol_analysis'].get(protocol_name, 0) + 1

            # Estado de encriptación estimado
            total_connections = len(connections)
            encrypted = presentation_data['ssl_tls_connections'] + presentation_data['ssh_connections']

            if total_connections > 0:
                presentation_data['encryption_status'] = {
                    'encrypted_percentage': (encrypted / total_connections) * 100,
                    'total_connections': total_connections,
                    'encrypted_connections': encrypted,
                    'unencrypted_connections': total_connections - encrypted
                }

            return presentation_data

        except Exception as e:
            return {'error': str(e), 'layer': 'presentation'}

    def analyze_application_layer(self):
        """Capa 7: Análisis de la capa de aplicación"""
        try:
            # Análisis de aplicaciones y procesos con conexiones de red
            applications = []

            for proc in psutil.process_iter(['pid', 'name', 'exe', 'connections', 'memory_info', 'cpu_percent']):
                try:
                    proc_info = proc.info
                    if proc_info['connections']:
                        # Clasificar por tipo de aplicación
                        app_category = self.classify_application(proc_info['name'])

                        app_info = {
                            'pid': proc_info['pid'],
                            'name': proc_info['name'],
                            'exe': proc_info['exe'] if proc_info['exe'] else "N/A",
                            'category': app_category,
                            'connection_count': len(proc_info['connections']),
                            'memory_mb': round(proc_info['memory_info'].rss / 1024 / 1024, 2),
                            'cpu_percent': proc_info['cpu_percent'],
                            'ports_used': [],
                            'protocols': set()
                        }

                        # Analizar puertos y protocolos usados
                        for conn in proc_info['connections']:
                            if conn.laddr:
                                app_info['ports_used'].append(conn.laddr.port)
                                protocol_name = self.get_protocol_name(conn.laddr.port)
                                if protocol_name:
                                    app_info['protocols'].add(protocol_name)

                        app_info['protocols'] = list(app_info['protocols'])
                        app_info['unique_ports'] = len(set(app_info['ports_used']))

                        applications.append(app_info)

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Ordenar por uso de recursos
            applications.sort(key=lambda x: (x['connection_count'], x['memory_mb']), reverse=True)

            # Estadísticas por categoría
            category_stats = {}
            for app in applications:
                category = app['category']
                if category not in category_stats:
                    category_stats[category] = {
                        'count': 0,
                        'total_connections': 0,
                        'total_memory_mb': 0,
                        'applications': []
                    }

                category_stats[category]['count'] += 1
                category_stats[category]['total_connections'] += app['connection_count']
                category_stats[category]['total_memory_mb'] += app['memory_mb']
                category_stats[category]['applications'].append(app['name'])

            application_data = {
                'total_network_applications': len(applications),
                'top_applications': applications[:20],  # Top 20 aplicaciones
                'category_breakdown': category_stats,
                'resource_summary': {
                    'total_memory_mb': sum(app['memory_mb'] for app in applications),
                    'total_connections': sum(app['connection_count'] for app in applications),
                    'average_connections_per_app': sum(app['connection_count'] for app in applications) / len(applications) if applications else 0
                }
            }

            return application_data

        except Exception as e:
            return {'error': str(e), 'layer': 'application'}

    def get_protocol_name(self, port):
        """Obtener nombre del protocolo basado en el puerto"""
        common_ports = {
            20: 'FTP-DATA', 21: 'FTP', 22: 'SSH', 23: 'TELNET', 25: 'SMTP',
            53: 'DNS', 67: 'DHCP', 68: 'DHCP', 80: 'HTTP', 110: 'POP3',
            143: 'IMAP', 443: 'HTTPS', 993: 'IMAPS', 995: 'POP3S',
            587: 'SMTP-TLS', 465: 'SMTPS', 3389: 'RDP', 5432: 'PostgreSQL',
            3306: 'MySQL', 27017: 'MongoDB', 6379: 'Redis', 8080: 'HTTP-ALT'
        }
        return common_ports.get(port)

    def classify_application(self, app_name):
        """Clasificar aplicación por categoría"""
        app_name_lower = app_name.lower()

        if any(x in app_name_lower for x in ['chrome', 'firefox', 'safari', 'edge', 'browser']):
            return 'Web Browser'
        elif any(x in app_name_lower for x in ['ssh', 'putty', 'terminal']):
            return 'Remote Access'
        elif any(x in app_name_lower for x in ['python', 'node', 'java', 'dotnet']):
            return 'Development'
        elif any(x in app_name_lower for x in ['docker', 'kubernetes', 'systemd']):
            return 'System/Container'
        elif any(x in app_name_lower for x in ['mysql', 'postgres', 'mongo', 'redis']):
            return 'Database'
        elif any(x in app_name_lower for x in ['apache', 'nginx', 'httpd']):
            return 'Web Server'
        else:
            return 'Other'

    def get_dns_servers(self):
        """Obtener servidores DNS configurados"""
        try:
            if platform.system() == "Linux":
                with open('/etc/resolv.conf', 'r') as f:
                    dns_servers = []
                    for line in f:
                        if line.startswith('nameserver'):
                            dns_servers.append(line.split()[1])
                    return dns_servers
            return []
        except:
            return []

    def get_default_gateway(self):
        """Obtener gateway por defecto"""
        try:
            if platform.system() == "Linux":
                result = subprocess.run(['ip', 'route', 'show', 'default'],
                                      capture_output=True, text=True)
                if result.returncode == 0 and result.stdout:
                    return result.stdout.strip().split()[2] if len(result.stdout.strip().split()) > 2 else None
            return None
        except:
            return None

    # Métodos individuales por capa para compatibilidad con smartcompute_express.py
    def analyze_layer1_physical(self):
        """Compatibilidad: Análisis capa física"""
        self.analysis_data["layers"]["layer1_physical"] = self.analyze_physical_layer()

    def analyze_layer2_datalink(self):
        """Compatibilidad: Análisis capa enlace"""
        self.analysis_data["layers"]["layer2_datalink"] = self.analyze_datalink_layer()

    def analyze_layer3_network(self):
        """Compatibilidad: Análisis capa red"""
        self.analysis_data["layers"]["layer3_network"] = self.analyze_network_layer()

    def analyze_layer4_transport(self):
        """Compatibilidad: Análisis capa transporte"""
        self.analysis_data["layers"]["layer4_transport"] = self.analyze_transport_layer()

    def analyze_layer5_session(self):
        """Compatibilidad: Análisis capa sesión"""
        self.analysis_data["layers"]["layer5_session"] = self.analyze_session_layer()

    def analyze_layer6_presentation(self):
        """Compatibilidad: Análisis capa presentación"""
        self.analysis_data["layers"]["layer6_presentation"] = self.analyze_presentation_layer()

    def analyze_layer7_application(self):
        """Compatibilidad: Análisis capa aplicación"""
        self.analysis_data["layers"]["layer7_application"] = self.analyze_application_layer()