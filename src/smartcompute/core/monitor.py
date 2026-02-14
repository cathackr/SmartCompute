#!/usr/bin/env python3
"""
SmartCompute - Monitor de Procesos Detallado
============================================

Monitor avanzado que captura información detallada de procesos en tiempo real:
- CPU y memoria por proceso
- Rutas de archivos y directorios
- Puertos de red y protocolos
- PIDs y información de conexiones
"""

import asyncio
import json
import logging
import os
import socket
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import psutil
import subprocess
import re
import glob


@dataclass
class ProcessInfo:
    """Información detallada de un proceso"""
    pid: int
    name: str
    cmdline: List[str]
    exe: str
    cwd: str
    cpu_percent: float
    memory_percent: float
    memory_mb: int
    status: str
    create_time: float
    num_threads: int
    connections: List[Dict[str, Any]]
    open_files: List[str]
    environment: Dict[str, str]
    parent_pid: Optional[int]
    username: str


@dataclass
class Layer12Connection:
    """Información de conexión directa de Capa 1 y 2"""
    mac_address: str
    manufacturer: str
    firmware_version: str
    ip_requested: str
    dhcp_active: bool
    vlan_id: Optional[int]
    vxlan_vni: Optional[int]
    link_type: str  # trunk, access, hybrid
    cable_category: str
    interface_name: str
    port_speed: str
    duplex_mode: str
    mtu_size: int
    link_state: str
    last_seen: float
    packet_count: int
    byte_count: int


@dataclass
class NetworkConnection:
    """Información de conexión de red"""
    pid: int
    process_name: str
    local_address: str
    local_port: int
    remote_address: str
    remote_port: int
    protocol: str
    status: str
    family: str
    # Información avanzada de red
    network_adapter: str
    channel: Optional[int]
    frequency: Optional[str]
    connection_time: Optional[float]
    physical_port: str
    encryption_type: str
    transmission_speed: str
    bytes_sent: int
    bytes_received: int
    interface_name: str


class SmartComputeProcessMonitor:
    """Monitor avanzado de procesos para SmartCompute"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.monitoring = False
        self.processes_cache = {}
        self.network_cache = {}
        self.network_interfaces = {}
        self.connection_times = {}
        self.layer12_cache = {}
        self.mac_vendor_db = {}
        self._initialize_network_interfaces()
        self._load_mac_vendor_database()

    async def get_detailed_process_info(self, filter_keywords: List[str] = None) -> List[ProcessInfo]:
        """Obtiene información detallada de procesos"""
        processes = []
        filter_keywords = filter_keywords or ['smartcompute', 'python', 'node', 'nginx', 'apache', 'mysql']

        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    # Filtrar procesos relevantes
                    if self._should_monitor_process(proc, filter_keywords):
                        process_info = await self._get_process_details(proc)
                        if process_info:
                            processes.append(process_info)

                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue

        except Exception as e:
            self.logger.error(f"Error getting process info: {e}")

        return processes

    def _should_monitor_process(self, proc, filter_keywords: List[str]) -> bool:
        """Determina si un proceso debe ser monitorizado"""
        try:
            proc_info = proc.info
            name = proc_info.get('name', '').lower()
            cmdline = ' '.join(proc_info.get('cmdline', [])).lower()

            # Siempre incluir procesos de SmartCompute
            if 'smartcompute' in name or 'smartcompute' in cmdline:
                return True

            # Incluir procesos que coincidan con palabras clave
            for keyword in filter_keywords:
                if keyword.lower() in name or keyword.lower() in cmdline:
                    return True

            # Incluir procesos con alto uso de recursos
            try:
                cpu_percent = proc.cpu_percent()
                memory_percent = proc.memory_percent()
                if cpu_percent > 5.0 or memory_percent > 2.0:
                    return True
            except:
                pass

            return False

        except Exception:
            return False

    async def _get_process_details(self, proc) -> Optional[ProcessInfo]:
        """Obtiene detalles completos de un proceso"""
        try:
            # Información básica del proceso
            with proc.oneshot():
                pid = proc.pid
                name = proc.name()
                cmdline = proc.cmdline()

                try:
                    exe = proc.exe()
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    exe = "N/A"

                try:
                    cwd = proc.cwd()
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    cwd = "N/A"

                # Métricas de recursos
                cpu_percent = proc.cpu_percent()
                memory_info = proc.memory_info()
                memory_percent = proc.memory_percent()
                memory_mb = memory_info.rss / 1024 / 1024

                # Estado y tiempo
                status = proc.status()
                create_time = proc.create_time()
                num_threads = proc.num_threads()

                try:
                    parent_pid = proc.ppid()
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    parent_pid = None

                try:
                    username = proc.username()
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    username = "N/A"

                # Conexiones de red
                connections = await self._get_process_connections(proc)

                # Archivos abiertos
                open_files = await self._get_process_files(proc)

                # Variables de entorno (limitadas por seguridad)
                environment = await self._get_process_environment(proc)

                return ProcessInfo(
                    pid=pid,
                    name=name,
                    cmdline=cmdline,
                    exe=exe,
                    cwd=cwd,
                    cpu_percent=cpu_percent,
                    memory_percent=memory_percent,
                    memory_mb=int(memory_mb),
                    status=status,
                    create_time=create_time,
                    num_threads=num_threads,
                    connections=connections,
                    open_files=open_files,
                    environment=environment,
                    parent_pid=parent_pid,
                    username=username
                )

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return None
        except Exception as e:
            self.logger.error(f"Error getting details for process {proc.pid}: {e}")
            return None

    async def _get_process_connections(self, proc) -> List[Dict[str, Any]]:
        """Obtiene conexiones de red del proceso"""
        connections = []
        try:
            for conn in proc.connections(kind='inet'):
                connection_info = {
                    'family': 'IPv4' if conn.family == socket.AF_INET else 'IPv6',
                    'type': 'TCP' if conn.type == socket.SOCK_STREAM else 'UDP',
                    'local_address': conn.laddr.ip if conn.laddr else 'N/A',
                    'local_port': conn.laddr.port if conn.laddr else 0,
                    'remote_address': conn.raddr.ip if conn.raddr else 'N/A',
                    'remote_port': conn.raddr.port if conn.raddr else 0,
                    'status': conn.status if hasattr(conn, 'status') else 'N/A'
                }
                connections.append(connection_info)

        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass
        except Exception as e:
            self.logger.debug(f"Error getting connections for PID {proc.pid}: {e}")

        return connections

    async def _get_process_files(self, proc) -> List[str]:
        """Obtiene archivos abiertos por el proceso"""
        files = []
        try:
            open_files = proc.open_files()
            for file_info in open_files[:10]:  # Limitar a 10 archivos por performance
                files.append(file_info.path)

        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass
        except Exception as e:
            self.logger.debug(f"Error getting files for PID {proc.pid}: {e}")

        return files

    async def _get_process_environment(self, proc) -> Dict[str, str]:
        """Obtiene variables de entorno relevantes del proceso"""
        env_vars = {}
        try:
            full_env = proc.environ()

            # Solo variables relevantes por seguridad
            relevant_vars = [
                'PATH', 'HOME', 'USER', 'PWD', 'SHELL', 'LANG',
                'PYTHONPATH', 'NODE_ENV', 'PORT', 'HOST',
                'DATABASE_URL', 'REDIS_URL'  # Comunes pero cuidado con secretos
            ]

            for var in relevant_vars:
                if var in full_env:
                    value = full_env[var]
                    # Ofuscar valores sensibles
                    if any(sensitive in var.lower() for sensitive in ['password', 'secret', 'key', 'token']):
                        value = '***HIDDEN***'
                    elif len(value) > 100:
                        value = value[:97] + '...'

                    env_vars[var] = value

        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass
        except Exception as e:
            self.logger.debug(f"Error getting environment for PID {proc.pid}: {e}")

        return env_vars

    def _initialize_network_interfaces(self):
        """Inicializa información de interfaces de red"""
        try:
            # Obtener información de interfaces de red
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_if_stats()

            for iface_name, addrs in interfaces.items():
                iface_info = {
                    'name': iface_name,
                    'addresses': [],
                    'speed': 0,
                    'mtu': 0,
                    'is_up': False,
                    'duplex': 'unknown',
                    'adapter_type': 'unknown',
                    'physical_port': 'N/A'
                }

                # Obtener direcciones
                for addr in addrs:
                    iface_info['addresses'].append({
                        'family': addr.family.name if hasattr(addr.family, 'name') else str(addr.family),
                        'address': addr.address,
                        'netmask': getattr(addr, 'netmask', None),
                        'broadcast': getattr(addr, 'broadcast', None)
                    })

                # Obtener estadísticas
                if iface_name in stats:
                    stat = stats[iface_name]
                    iface_info.update({
                        'speed': stat.speed,
                        'mtu': stat.mtu,
                        'is_up': stat.isup,
                        'duplex': stat.duplex.name if hasattr(stat.duplex, 'name') else str(stat.duplex)
                    })

                # Detectar tipo de adaptador
                iface_info['adapter_type'] = self._detect_adapter_type(iface_name)
                iface_info['physical_port'] = self._detect_physical_port(iface_name)

                self.network_interfaces[iface_name] = iface_info

        except Exception as e:
            self.logger.debug(f"Error initializing network interfaces: {e}")

    def _detect_adapter_type(self, iface_name: str) -> str:
        """Detecta el tipo de adaptador de red"""
        try:
            iface_lower = iface_name.lower()

            # Ethernet
            if any(prefix in iface_lower for prefix in ['eth', 'enp', 'eno', 'ens']):
                return 'Ethernet'

            # WiFi
            elif any(prefix in iface_lower for prefix in ['wlan', 'wlp', 'wifi', 'wlo']):
                return 'WiFi/Wireless'

            # Loopback
            elif 'lo' in iface_lower:
                return 'Loopback'

            # VPN/Tunnel
            elif any(prefix in iface_lower for prefix in ['tun', 'tap', 'vpn', 'ppp']):
                return 'VPN/Tunnel'

            # Docker/Container
            elif any(prefix in iface_lower for prefix in ['docker', 'br-', 'veth']):
                return 'Container/Virtual'

            # Bluetooth
            elif 'bnep' in iface_lower or 'bt' in iface_lower:
                return 'Bluetooth'

            else:
                return 'Other/Unknown'

        except Exception:
            return 'Unknown'

    def _detect_physical_port(self, iface_name: str) -> str:
        """Detecta información del puerto físico"""
        try:
            # Intentar obtener información del puerto desde sysfs
            sys_path = f"/sys/class/net/{iface_name}"

            if os.path.exists(sys_path):
                # Verificar si es un dispositivo PCI
                device_path = os.path.join(sys_path, "device")
                if os.path.exists(device_path):
                    try:
                        real_path = os.path.realpath(device_path)
                        if 'pci' in real_path:
                            pci_addr = real_path.split('/')[-1]
                            return f"PCI: {pci_addr}"
                    except:
                        pass

                # Verificar si es USB
                if 'usb' in str(os.path.realpath(device_path)):
                    return "USB"

            # Fallback basado en el nombre
            iface_lower = iface_name.lower()
            if any(prefix in iface_lower for prefix in ['eth', 'enp']):
                return "Integrated Ethernet"
            elif any(prefix in iface_lower for prefix in ['wlan', 'wlp']):
                return "Integrated WiFi"
            elif 'lo' in iface_lower:
                return "Virtual (Loopback)"
            else:
                return "Virtual/Software"

        except Exception:
            return "Unknown"

    def _get_wireless_info(self, iface_name: str) -> Dict[str, Any]:
        """Obtiene información específica de conexiones inalámbricas"""
        wireless_info = {
            'channel': None,
            'frequency': None,
            'encryption': 'Unknown',
            'signal_strength': None,
            'ssid': None
        }

        try:
            # Intentar obtener información con iwconfig
            result = subprocess.run(['iwconfig', iface_name],
                                  capture_output=True, text=True, timeout=5)

            if result.returncode == 0:
                output = result.stdout

                # Extraer frecuencia
                freq_match = re.search(r'Frequency:(\d+\.?\d*)\s*GHz', output)
                if freq_match:
                    freq_ghz = float(freq_match.group(1))
                    wireless_info['frequency'] = f"{freq_ghz} GHz"

                    # Estimar canal basado en frecuencia
                    if 2.4 <= freq_ghz <= 2.5:
                        channel = int((freq_ghz - 2.412) / 0.005) + 1
                        wireless_info['channel'] = channel
                    elif 5.0 <= freq_ghz <= 6.0:
                        wireless_info['channel'] = int((freq_ghz - 5.0) * 200)

                # Extraer tipo de encriptación
                if 'Encryption key:on' in output:
                    if 'IEEE 802.11' in output:
                        wireless_info['encryption'] = 'WPA/WPA2'
                    else:
                        wireless_info['encryption'] = 'WEP'
                elif 'Encryption key:off' in output:
                    wireless_info['encryption'] = 'Open'

                # Extraer SSID
                ssid_match = re.search(r'ESSID:"([^"]*)"', output)
                if ssid_match:
                    wireless_info['ssid'] = ssid_match.group(1)

        except Exception as e:
            self.logger.debug(f"Error getting wireless info for {iface_name}: {e}")

        return wireless_info

    def _get_interface_for_connection(self, local_addr: str, remote_addr: str) -> str:
        """Determina la interfaz de red utilizada para una conexión"""
        try:
            # Usar el comando route para determinar la interfaz
            if remote_addr and remote_addr != 'N/A':
                result = subprocess.run(['ip', 'route', 'get', remote_addr],
                                      capture_output=True, text=True, timeout=3)

                if result.returncode == 0:
                    # Extraer el nombre de la interfaz
                    match = re.search(r'dev\s+(\w+)', result.stdout)
                    if match:
                        return match.group(1)

            # Fallback: usar la interfaz por defecto para direcciones locales
            if local_addr:
                for iface_name, iface_info in self.network_interfaces.items():
                    for addr_info in iface_info['addresses']:
                        if addr_info['address'] == local_addr:
                            return iface_name

            return 'unknown'

        except Exception:
            return 'unknown'

    def _get_connection_stats(self, pid: int, local_port: int) -> Dict[str, int]:
        """Obtiene estadísticas de transmisión de datos para una conexión"""
        try:
            # Obtener estadísticas de red del proceso
            proc = psutil.Process(pid)

            # Intentar obtener estadísticas de la interfaz
            net_io = psutil.net_io_counters(pernic=True)

            # Para conexiones específicas, es difícil obtener estadísticas exactas
            # Devolvemos estadísticas generales del sistema
            total_io = psutil.net_io_counters()

            return {
                'bytes_sent': total_io.bytes_sent // 1024,  # En KB
                'bytes_received': total_io.bytes_recv // 1024,  # En KB
            }

        except Exception:
            return {
                'bytes_sent': 0,
                'bytes_received': 0
            }

    def _load_mac_vendor_database(self):
        """Carga base de datos de fabricantes MAC"""
        # Base de datos básica de OUIs más comunes
        self.mac_vendor_db = {
            '00:00:0c': 'Cisco Systems',
            '00:01:42': 'Parallels Inc',
            '00:03:93': 'Apple Inc',
            '00:04:20': 'Hitachi Ltd',
            '00:05:02': 'Apple Inc',
            '00:0a:27': 'Apple Inc',
            '00:0c:29': 'VMware Inc',
            '00:0f:4b': 'Realtek Semiconductor',
            '00:11:25': 'Intel Corporate',
            '00:13:72': 'Dell Inc',
            '00:15:5d': 'Microsoft Corporation',
            '00:16:3e': 'Xensource Inc',
            '00:17:fa': 'Broadcom Corporation',
            '00:1b:21': 'Intel Corporate',
            '00:1c:23': 'Cisco Systems',
            '00:1c:25': 'Broadcom Corporation',
            '00:1e:68': 'Cisco Systems',
            '00:21:70': 'Cisco Systems',
            '00:22:48': 'Cisco Systems',
            '00:23:ea': 'Cisco Systems',
            '00:25:90': 'Cisco Systems',
            '00:50:56': 'VMware Inc',
            '08:00:27': 'Oracle VirtualBox',
            '0c:54:15': 'Apple Inc',
            '10:dd:b1': 'Apple Inc',
            '14:10:9f': 'Apple Inc',
            '18:03:73': 'Dell Inc',
            '20:c9:d0': 'Apple Inc',
            '28:cf:e9': 'Apple Inc',
            '3c:07:54': 'Apple Inc',
            '40:a8:f0': 'Apple Inc',
            '52:54:00': 'QEMU Virtual NIC',
            '60:03:08': 'Apple Inc',
            '68:5b:35': 'Apple Inc',
            '70:56:81': 'Apple Inc',
            '78:4f:43': 'Apple Inc',
            '84:38:35': 'Apple Inc',
            '88:63:df': 'Apple Inc',
            '8c:85:90': 'Apple Inc',
            '90:72:40': 'Apple Inc',
            '94:e6:f7': 'Apple Inc',
            'a4:83:e7': 'Apple Inc',
            'ac:87:a3': 'Apple Inc',
            'b8:09:8a': 'Apple Inc',
            'b8:e8:56': 'Apple Inc',
            'c8:2a:14': 'Apple Inc',
            'd0:25:44': 'Apple Inc',
            'd4:9a:20': 'Apple Inc',
            'dc:a9:04': 'Apple Inc',
            'e0:ac:cb': 'Apple Inc',
            'e4:ce:8f': 'Apple Inc',
            'e8:06:88': 'Apple Inc',
            'ec:f4:bb': 'Apple Inc',
            'f0:18:98': 'Apple Inc',
            'f4:5c:89': 'Apple Inc',
            'f8:1e:df': 'Apple Inc',
            'fc:25:3f': 'Apple Inc'
        }

    def _get_mac_manufacturer(self, mac_address: str) -> str:
        """Obtiene el fabricante basado en la dirección MAC"""
        try:
            if not mac_address or mac_address == 'N/A':
                return 'Unknown'

            # Normalizar MAC
            mac_clean = mac_address.lower().replace('-', ':').replace('.', ':')
            oui = ':'.join(mac_clean.split(':')[:3])

            return self.mac_vendor_db.get(oui, 'Unknown Manufacturer')

        except Exception:
            return 'Unknown'

    def _detect_cable_category(self, interface_name: str, speed: int) -> str:
        """Detecta la categoría de cable basada en velocidad y tipo"""
        try:
            # Para interfaces Ethernet, inferir categoría por velocidad
            if speed >= 10000:  # 10 Gbps+
                return 'Cat 6A/7'
            elif speed >= 1000:  # 1 Gbps
                return 'Cat 5e/6'
            elif speed >= 100:  # 100 Mbps
                return 'Cat 5'
            elif speed >= 10:  # 10 Mbps
                return 'Cat 3'
            else:
                # Para interfaces WiFi o virtuales
                iface_lower = interface_name.lower()
                if any(wifi in iface_lower for wifi in ['wlan', 'wifi', 'wlp']):
                    return 'Wireless'
                elif any(virt in iface_lower for virt in ['lo', 'tun', 'tap', 'docker', 'br-']):
                    return 'Virtual'
                else:
                    return 'Unknown'

        except Exception:
            return 'Unknown'

    def _get_vlan_info(self, interface_name: str) -> Dict[str, Any]:
        """Obtiene información de VLAN para una interfaz"""
        vlan_info = {
            'vlan_id': None,
            'vxlan_vni': None,
            'link_type': 'access'
        }

        try:
            # Verificar si la interfaz tiene VLAN tag en el nombre
            if '.' in interface_name:
                parts = interface_name.split('.')
                if len(parts) == 2 and parts[1].isdigit():
                    vlan_info['vlan_id'] = int(parts[1])

            # Intentar obtener información de VLAN desde /proc/net/vlan/
            vlan_config_path = f"/proc/net/vlan/{interface_name}"
            if os.path.exists(vlan_config_path):
                try:
                    with open(vlan_config_path, 'r') as f:
                        content = f.read()
                        # Extraer VLAN ID
                        vlan_match = re.search(r'VID:\s*(\d+)', content)
                        if vlan_match:
                            vlan_info['vlan_id'] = int(vlan_match.group(1))
                except:
                    pass

            # Verificar configuración de bridge para detectar trunking
            try:
                bridge_cmd = subprocess.run(['bridge', 'vlan', 'show', 'dev', interface_name],
                                          capture_output=True, text=True, timeout=3)
                if bridge_cmd.returncode == 0:
                    output = bridge_cmd.stdout
                    if 'PVID' in output:
                        vlan_info['link_type'] = 'access'
                    elif len(re.findall(r'\d+', output)) > 1:
                        vlan_info['link_type'] = 'trunk'
            except:
                pass

            # Verificar VXLAN
            try:
                ip_cmd = subprocess.run(['ip', 'link', 'show', interface_name],
                                      capture_output=True, text=True, timeout=3)
                if ip_cmd.returncode == 0:
                    output = ip_cmd.stdout
                    vxlan_match = re.search(r'vxlan.*id\s+(\d+)', output)
                    if vxlan_match:
                        vlan_info['vxlan_vni'] = int(vxlan_match.group(1))
            except:
                pass

        except Exception as e:
            self.logger.debug(f"Error getting VLAN info for {interface_name}: {e}")

        return vlan_info

    def _get_dhcp_status(self, interface_name: str, ip_address: str) -> Dict[str, Any]:
        """Detecta si una IP fue asignada por DHCP"""
        dhcp_info = {
            'dhcp_active': False,
            'ip_requested': ip_address,
            'lease_time': None,
            'dhcp_server': None
        }

        try:
            # Verificar leases de DHCP en ubicaciones comunes
            dhcp_lease_files = [
                '/var/lib/dhcp/dhclient.leases',
                '/var/lib/dhclient/dhclient.leases',
                f'/var/lib/dhcp/dhclient.{interface_name}.leases',
                '/etc/dhcp/dhclient.leases'
            ]

            for lease_file in dhcp_lease_files:
                if os.path.exists(lease_file):
                    try:
                        with open(lease_file, 'r') as f:
                            content = f.read()

                        # Buscar lease para esta IP
                        lease_pattern = rf'lease\s+{re.escape(ip_address)}\s*\{{([^}}]*)\}}'
                        lease_match = re.search(lease_pattern, content, re.DOTALL)

                        if lease_match:
                            lease_block = lease_match.group(1)
                            dhcp_info['dhcp_active'] = True

                            # Extraer servidor DHCP
                            server_match = re.search(r'dhcp-server-identifier\s+([\d.]+)', lease_block)
                            if server_match:
                                dhcp_info['dhcp_server'] = server_match.group(1)

                            break

                    except Exception:
                        continue

            # Verificar NetworkManager para información DHCP
            try:
                nm_cmd = subprocess.run(['nmcli', 'device', 'show', interface_name],
                                      capture_output=True, text=True, timeout=5)
                if nm_cmd.returncode == 0:
                    output = nm_cmd.stdout
                    if 'DHCP4.OPTION' in output:
                        dhcp_info['dhcp_active'] = True
            except:
                pass

        except Exception as e:
            self.logger.debug(f"Error checking DHCP status for {interface_name}: {e}")

        return dhcp_info

    def _get_firmware_info(self, interface_name: str) -> str:
        """Obtiene información de firmware para una interfaz"""
        try:
            # Intentar obtener información con ethtool
            ethtool_cmd = subprocess.run(['ethtool', '-i', interface_name],
                                       capture_output=True, text=True, timeout=5)

            if ethtool_cmd.returncode == 0:
                output = ethtool_cmd.stdout

                # Extraer versión de firmware
                fw_match = re.search(r'firmware-version:\s*(.+)', output)
                if fw_match:
                    return fw_match.group(1).strip()

                # Extraer versión de driver como fallback
                driver_match = re.search(r'version:\s*(.+)', output)
                if driver_match:
                    return f"Driver: {driver_match.group(1).strip()}"

            # Fallback: información del módulo del kernel
            try:
                modinfo_cmd = subprocess.run(['modinfo', interface_name],
                                           capture_output=True, text=True, timeout=3)
                if modinfo_cmd.returncode == 0:
                    output = modinfo_cmd.stdout
                    version_match = re.search(r'version:\s*(.+)', output)
                    if version_match:
                        return f"Module: {version_match.group(1).strip()}"
            except:
                pass

            return 'Unknown'

        except Exception:
            return 'Unknown'

    async def get_layer12_connections(self) -> List[Layer12Connection]:
        """Obtiene conexiones directas de Capa 1 y 2"""
        connections = []

        try:
            # Obtener tabla ARP para detectar dispositivos conectados
            arp_table = {}
            try:
                arp_cmd = subprocess.run(['arp', '-a'], capture_output=True, text=True, timeout=5)
                if arp_cmd.returncode == 0:
                    for line in arp_cmd.stdout.split('\n'):
                        # Formato: hostname (ip) at mac [ether] on interface
                        arp_match = re.search(r'\(([\d.]+)\)\s+at\s+([a-fA-F0-9:]{17})', line)
                        if arp_match:
                            ip_addr = arp_match.group(1)
                            mac_addr = arp_match.group(2)

                            # Extraer interfaz
                            iface_match = re.search(r'on\s+(\w+)', line)
                            interface = iface_match.group(1) if iface_match else 'unknown'

                            arp_table[mac_addr] = {
                                'ip': ip_addr,
                                'interface': interface
                            }
            except Exception as e:
                self.logger.debug(f"Error reading ARP table: {e}")

            # Procesar cada interfaz de red
            for iface_name, iface_info in self.network_interfaces.items():
                try:
                    # Obtener MAC de la interfaz
                    iface_mac = None
                    for addr_info in iface_info['addresses']:
                        if addr_info['family'] == 'AF_PACKET' or 'packet' in str(addr_info['family']).lower():
                            iface_mac = addr_info['address']
                            break

                    if not iface_mac or iface_mac == '00:00:00:00:00:00':
                        continue

                    # Información básica de la interfaz
                    manufacturer = self._get_mac_manufacturer(iface_mac)
                    firmware = self._get_firmware_info(iface_name)

                    # Obtener IP de la interfaz
                    ip_address = 'N/A'
                    for addr_info in iface_info['addresses']:
                        if addr_info['family'] == 'AF_INET' or 'inet' in str(addr_info['family']).lower():
                            if addr_info['address'] != '127.0.0.1':
                                ip_address = addr_info['address']
                                break

                    # Información DHCP
                    dhcp_info = self._get_dhcp_status(iface_name, ip_address)

                    # Información VLAN
                    vlan_info = self._get_vlan_info(iface_name)

                    # Categoría de cable
                    cable_cat = self._detect_cable_category(iface_name, iface_info.get('speed', 0))

                    # Estadísticas de la interfaz
                    try:
                        net_io = psutil.net_io_counters(pernic=True)
                        iface_stats = net_io.get(iface_name)
                        packet_count = iface_stats.packets_sent + iface_stats.packets_recv if iface_stats else 0
                        byte_count = iface_stats.bytes_sent + iface_stats.bytes_recv if iface_stats else 0
                    except:
                        packet_count = 0
                        byte_count = 0

                    # Crear conexión de capa 1/2
                    layer12_conn = Layer12Connection(
                        mac_address=iface_mac,
                        manufacturer=manufacturer,
                        firmware_version=firmware,
                        ip_requested=ip_address,
                        dhcp_active=dhcp_info['dhcp_active'],
                        vlan_id=vlan_info['vlan_id'],
                        vxlan_vni=vlan_info['vxlan_vni'],
                        link_type=vlan_info['link_type'],
                        cable_category=cable_cat,
                        interface_name=iface_name,
                        port_speed=f"{iface_info.get('speed', 0)} Mbps" if iface_info.get('speed', 0) > 0 else 'Unknown',
                        duplex_mode=iface_info.get('duplex', 'unknown'),
                        mtu_size=iface_info.get('mtu', 0),
                        link_state='UP' if iface_info.get('is_up') else 'DOWN',
                        last_seen=time.time(),
                        packet_count=packet_count,
                        byte_count=byte_count
                    )

                    connections.append(layer12_conn)

                except Exception as e:
                    self.logger.debug(f"Error processing interface {iface_name}: {e}")
                    continue

            # Agregar dispositivos detectados en ARP que no son interfaces locales
            local_macs = {conn.mac_address for conn in connections}

            for mac_addr, arp_info in arp_table.items():
                if mac_addr not in local_macs:
                    try:
                        manufacturer = self._get_mac_manufacturer(mac_addr)

                        # Crear entrada para dispositivo remoto detectado
                        remote_conn = Layer12Connection(
                            mac_address=mac_addr,
                            manufacturer=manufacturer,
                            firmware_version='Remote Device',
                            ip_requested=arp_info['ip'],
                            dhcp_active=True,  # Asumido para dispositivos remotos
                            vlan_id=None,
                            vxlan_vni=None,
                            link_type='access',
                            cable_category='Remote',
                            interface_name=arp_info['interface'],
                            port_speed='Unknown',
                            duplex_mode='unknown',
                            mtu_size=0,
                            link_state='DETECTED',
                            last_seen=time.time(),
                            packet_count=0,
                            byte_count=0
                        )

                        connections.append(remote_conn)

                    except Exception as e:
                        self.logger.debug(f"Error processing ARP entry {mac_addr}: {e}")
                        continue

        except Exception as e:
            self.logger.error(f"Error getting Layer 1/2 connections: {e}")

        return connections

    async def get_network_overview(self) -> List[NetworkConnection]:
        """Obtiene vista general de conexiones de red"""
        connections = []

        try:
            # Obtener todas las conexiones de red del sistema
            all_connections = psutil.net_connections(kind='inet')

            for conn in all_connections:
                try:
                    if conn.pid:
                        try:
                            proc = psutil.Process(conn.pid)
                            process_name = proc.name()
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            process_name = "Unknown"
                    else:
                        process_name = "System"

                    # Información básica de la conexión
                    local_addr = conn.laddr.ip if conn.laddr else 'N/A'
                    remote_addr = conn.raddr.ip if conn.raddr else 'N/A'
                    local_port = conn.laddr.port if conn.laddr else 0
                    remote_port = conn.raddr.port if conn.raddr else 0

                    # Determinar interfaz de red
                    interface_name = self._get_interface_for_connection(local_addr, remote_addr)

                    # Obtener información del adaptador
                    adapter_info = self.network_interfaces.get(interface_name, {})
                    adapter_type = adapter_info.get('adapter_type', 'Unknown')
                    physical_port = adapter_info.get('physical_port', 'N/A')

                    # Obtener velocidad de transmisión
                    speed = adapter_info.get('speed', 0)
                    if speed > 0:
                        if speed >= 1000:
                            transmission_speed = f"{speed//1000} Gbps"
                        else:
                            transmission_speed = f"{speed} Mbps"
                    else:
                        transmission_speed = "Unknown"

                    # Información inalámbrica (si aplica)
                    wireless_info = {}
                    channel = None
                    frequency = None
                    encryption_type = "N/A"

                    if 'wifi' in adapter_type.lower() or 'wireless' in adapter_type.lower():
                        wireless_info = self._get_wireless_info(interface_name)
                        channel = wireless_info.get('channel')
                        frequency = wireless_info.get('frequency')
                        encryption_type = wireless_info.get('encryption', 'Unknown')

                    # Estadísticas de transmisión
                    stats = self._get_connection_stats(conn.pid if conn.pid else 0, local_port)

                    # Tiempo de conexión (estimado)
                    connection_time = None
                    if conn.pid:
                        try:
                            proc = psutil.Process(conn.pid)
                            connection_time = time.time() - proc.create_time()
                        except:
                            connection_time = None

                    network_conn = NetworkConnection(
                        pid=conn.pid if conn.pid else 0,
                        process_name=process_name,
                        local_address=local_addr,
                        local_port=local_port,
                        remote_address=remote_addr,
                        remote_port=remote_port,
                        protocol='TCP' if conn.type == socket.SOCK_STREAM else 'UDP',
                        status=conn.status if hasattr(conn, 'status') else 'N/A',
                        family='IPv4' if conn.family == socket.AF_INET else 'IPv6',
                        # Información avanzada
                        network_adapter=adapter_type,
                        channel=channel,
                        frequency=frequency,
                        connection_time=connection_time,
                        physical_port=physical_port,
                        encryption_type=encryption_type,
                        transmission_speed=transmission_speed,
                        bytes_sent=stats['bytes_sent'],
                        bytes_received=stats['bytes_received'],
                        interface_name=interface_name
                    )

                    connections.append(network_conn)

                except Exception as e:
                    self.logger.debug(f"Error processing connection: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"Error getting network connections: {e}")

        return connections

    async def get_system_resources_detailed(self) -> Dict[str, Any]:
        """Obtiene información detallada de recursos del sistema"""
        try:
            # CPU detallado
            cpu_info = {
                'percent': psutil.cpu_percent(interval=1),
                'count_logical': psutil.cpu_count(logical=True),
                'count_physical': psutil.cpu_count(logical=False),
                'per_cpu': psutil.cpu_percent(interval=1, percpu=True),
                'freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
                'load_avg': os.getloadavg() if hasattr(os, 'getloadavg') else None
            }

            # Memoria detallada
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            memory_info = {
                'virtual': memory._asdict(),
                'swap': swap._asdict(),
                'available_gb': memory.available / 1024 / 1024 / 1024,
                'used_gb': memory.used / 1024 / 1024 / 1024,
                'total_gb': memory.total / 1024 / 1024 / 1024
            }

            # Disco detallado
            disk_info = {}
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info[partition.mountpoint] = {
                        'device': partition.device,
                        'fstype': partition.fstype,
                        'total_gb': usage.total / 1024 / 1024 / 1024,
                        'used_gb': usage.used / 1024 / 1024 / 1024,
                        'free_gb': usage.free / 1024 / 1024 / 1024,
                        'percent': (usage.used / usage.total * 100) if usage.total > 0 else 0
                    }
                except (PermissionError, OSError):
                    continue

            # Red detallada
            net_io = psutil.net_io_counters()
            net_info = {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
                'errin': net_io.errin,
                'errout': net_io.errout,
                'dropin': net_io.dropin,
                'dropout': net_io.dropout
            }

            return {
                'cpu': cpu_info,
                'memory': memory_info,
                'disk': disk_info,
                'network': net_info,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error getting system resources: {e}")
            return {}

    async def generate_process_report(self, filter_keywords: List[str] = None) -> Dict[str, Any]:
        """Genera reporte completo de procesos"""
        print("🔍 Generando reporte detallado de procesos...")

        start_time = time.time()

        # Obtener información de procesos
        processes = await self.get_detailed_process_info(filter_keywords)

        # Obtener conexiones de red
        network_connections = await self.get_network_overview()

        # Obtener recursos del sistema
        system_resources = await self.get_system_resources_detailed()

        # Estadísticas generales
        total_processes = len(psutil.pids())
        monitored_processes = len(processes)

        # Procesos con mayor uso de recursos
        top_cpu_processes = sorted(processes, key=lambda p: p.cpu_percent, reverse=True)[:10]
        top_memory_processes = sorted(processes, key=lambda p: p.memory_mb, reverse=True)[:10]

        # Puertos en uso
        listening_ports = [conn for conn in network_connections
                          if conn.status == 'LISTEN' and conn.local_port > 0]

        # Agrupar por protocolo
        tcp_connections = [conn for conn in network_connections if conn.protocol == 'TCP']
        udp_connections = [conn for conn in network_connections if conn.protocol == 'UDP']

        generation_time = time.time() - start_time

        report = {
            'timestamp': datetime.now().isoformat(),
            'generation_time_seconds': round(generation_time, 2),
            'summary': {
                'total_processes': total_processes,
                'monitored_processes': monitored_processes,
                'network_connections': len(network_connections),
                'listening_ports': len(listening_ports),
                'tcp_connections': len(tcp_connections),
                'udp_connections': len(udp_connections)
            },
            'processes': [asdict(p) for p in processes],
            'top_cpu': [asdict(p) for p in top_cpu_processes],
            'top_memory': [asdict(p) for p in top_memory_processes],
            'network_connections': [asdict(conn) for conn in network_connections],
            'listening_ports': [asdict(port) for port in listening_ports],
            'system_resources': system_resources
        }

        print(f"✅ Reporte generado en {generation_time:.1f}s")
        print(f"   📊 Procesos monitorizados: {monitored_processes}/{total_processes}")
        print(f"   🌐 Conexiones de red: {len(network_connections)}")
        print(f"   🔌 Puertos en escucha: {len(listening_ports)}")

        return report

    def save_report(self, report: Dict[str, Any], output_path: str = None) -> str:
        """Guarda el reporte en formato JSON"""
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"/home/gatux/smartcompute/reports/process_monitor_{timestamp}.json"

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        return output_path


# Función de demostración
async def demo_process_monitor():
    """Demostración del monitor de procesos"""
    print("🔍 SmartCompute Process Monitor Demo")
    print("=" * 50)

    monitor = SmartComputeProcessMonitor()

    # Generar reporte con filtros específicos
    filter_keywords = ['python', 'node', 'smartcompute', 'chrome', 'firefox']

    report = await monitor.generate_process_report(filter_keywords)

    # Guardar reporte
    report_path = monitor.save_report(report)
    print(f"\n💾 Reporte guardado: {report_path}")

    # Mostrar algunos resultados destacados
    print("\n🏆 TOP 5 Procesos por CPU:")
    for i, proc in enumerate(report['top_cpu'][:5], 1):
        print(f"   {i}. {proc['name']} (PID {proc['pid']}) - {proc['cpu_percent']:.1f}% CPU")

    print("\n🧠 TOP 5 Procesos por Memoria:")
    for i, proc in enumerate(report['top_memory'][:5], 1):
        print(f"   {i}. {proc['name']} (PID {proc['pid']}) - {proc['memory_mb']:.1f} MB")

    print("\n🔌 Puertos en Escucha:")
    for port in report['listening_ports'][:10]:
        print(f"   {port['local_port']} ({port['protocol']}) - {port['process_name']} (PID {port['pid']})")


if __name__ == "__main__":
    asyncio.run(demo_process_monitor())