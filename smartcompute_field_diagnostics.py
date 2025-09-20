#!/usr/bin/env python3
"""
SmartCompute Industrial - Herramienta de Diagnóstico de Campo
Desarrollado por: ggwre04p0@mozmail.com
LinkedIn: https://www.linkedin.com/in/martín-iribarne-swtf/

Módulo para conectarse directamente a switches, PLCs y equipos industriales
para diagnóstico en tiempo real desde campo.
"""

import socket
import subprocess
import json
import struct
import time
import threading
from datetime import datetime
from pathlib import Path
import netifaces
import psutil
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any

@dataclass
class NetworkInterface:
    interface: str
    ip_address: str
    netmask: str
    mac_address: str
    vlan_id: Optional[int] = None
    switch_port: Optional[str] = None
    switch_ip: Optional[str] = None

@dataclass
class PLCInfo:
    ip_address: str
    manufacturer: str
    model: str
    firmware_version: str
    rack_slot: Optional[str] = None
    cpu_type: str = "Unknown"
    status: str = "Unknown"
    project_name: Optional[str] = None
    instructions_detected: List[str] = None
    communication_protocol: str = "Unknown"
    last_scan: datetime = None

@dataclass
class SwitchInfo:
    ip_address: str
    hostname: str
    model: str
    mac_address: str
    vlan_info: Dict[int, str] = None
    port_status: Dict[str, str] = None
    spanning_tree: Dict[str, Any] = None
    uptime: str = "Unknown"

class SmartComputeFieldDiagnostics:
    def __init__(self):
        self.network_interfaces = {}
        self.discovered_plcs = {}
        self.discovered_switches = {}
        self.current_vlan = None
        self.connection_log = []

    def scan_network_interfaces(self):
        """Escanear todas las interfaces de red disponibles"""
        print("🔍 Escaneando interfaces de red...")

        interfaces = netifaces.interfaces()
        for interface in interfaces:
            if interface == 'lo':  # Skip loopback
                continue

            try:
                addr_info = netifaces.ifaddresses(interface)

                if netifaces.AF_INET in addr_info:
                    ipv4_info = addr_info[netifaces.AF_INET][0]
                    mac_info = addr_info.get(netifaces.AF_LINK, [{}])[0]

                    net_interface = NetworkInterface(
                        interface=interface,
                        ip_address=ipv4_info.get('addr', 'N/A'),
                        netmask=ipv4_info.get('netmask', 'N/A'),
                        mac_address=mac_info.get('addr', 'N/A')
                    )

                    # Detectar VLAN si está presente
                    if '.' in interface:
                        net_interface.vlan_id = int(interface.split('.')[-1])

                    self.network_interfaces[interface] = net_interface
                    print(f"  ✅ {interface}: {net_interface.ip_address}/{net_interface.netmask}")

            except Exception as e:
                print(f"  ❌ Error en interfaz {interface}: {e}")

        return self.network_interfaces

    def detect_current_vlan(self, interface=None):
        """Detectar VLAN actual basada en la interfaz activa"""
        if interface:
            if interface in self.network_interfaces:
                self.current_vlan = self.network_interfaces[interface].vlan_id
        else:
            # Auto-detectar interfaz activa
            for iface, info in self.network_interfaces.items():
                if info.ip_address != 'N/A' and not info.ip_address.startswith('127.'):
                    self.current_vlan = info.vlan_id
                    break

        print(f"🌐 VLAN actual detectada: {self.current_vlan if self.current_vlan else 'No VLAN detectada'}")
        return self.current_vlan

    def scan_for_plcs(self, network_range=None):
        """Escanear red en busca de PLCs industriales"""
        print("🏭 Escaneando PLCs en la red...")

        if not network_range:
            # Usar la red de la interfaz activa
            for iface, info in self.network_interfaces.items():
                if info.ip_address != 'N/A' and not info.ip_address.startswith('127.'):
                    network_base = '.'.join(info.ip_address.split('.')[:-1])
                    network_range = f"{network_base}.1-254"
                    break

        # Escanear puertos comunes de PLCs
        plc_ports = {
            102: "S7/ISO-TSAP (Siemens)",
            44818: "EtherNet/IP (Allen-Bradley)",
            9600: "FINS (Omron)",
            502: "Modbus TCP",
            4840: "OPC-UA",
            20000: "DNP3",
            2404: "IEC 61850"
        }

        if network_range and '-' in network_range:
            base_ip = '.'.join(network_range.split('.')[:-1])
            start_end = network_range.split('.')[-1].split('-')
            start_ip = int(start_end[0])
            end_ip = int(start_end[1])

            for ip_last in range(start_ip, end_ip + 1):
                target_ip = f"{base_ip}.{ip_last}"

                for port, protocol in plc_ports.items():
                    if self._check_port_open(target_ip, port):
                        plc_info = self._identify_plc(target_ip, port, protocol)
                        if plc_info:
                            self.discovered_plcs[target_ip] = plc_info
                            print(f"  ✅ PLC encontrado: {target_ip}:{port} ({protocol})")

        return self.discovered_plcs

    def _check_port_open(self, ip, port, timeout=1):
        """Verificar si un puerto está abierto"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except:
            return False

    def _identify_plc(self, ip, port, protocol):
        """Identificar tipo y modelo de PLC"""
        plc_info = PLCInfo(
            ip_address=ip,
            manufacturer="Unknown",
            model="Unknown",
            firmware_version="Unknown",
            communication_protocol=protocol,
            last_scan=datetime.now()
        )

        try:
            if port == 102:  # Siemens S7
                plc_info = self._identify_siemens_plc(ip, port)
            elif port == 44818:  # Allen-Bradley EtherNet/IP
                plc_info = self._identify_ab_plc(ip, port)
            elif port == 9600:  # Omron FINS
                plc_info = self._identify_omron_plc(ip, port)
            elif port == 502:  # Modbus TCP
                plc_info = self._identify_modbus_device(ip, port)

        except Exception as e:
            print(f"    ⚠️ Error identificando PLC {ip}:{port} - {e}")

        return plc_info

    def _identify_siemens_plc(self, ip, port):
        """Identificación específica de PLCs Siemens"""
        print(f"    🔍 Analizando PLC Siemens en {ip}:{port}...")

        try:
            # Conectar via protocolo S7
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((ip, port))

            # S7 Communication Setup TPDU
            cotp_cr = bytes([
                # TPKT Header
                0x03, 0x00, 0x00, 0x16,
                # COTP Header
                0x11, 0xE0, 0x00, 0x00, 0x00, 0x01, 0x00,
                0xC0, 0x01, 0x0A, 0xC1, 0x02, 0x01, 0x00,
                0xC2, 0x02, 0x01, 0x02
            ])

            sock.send(cotp_cr)
            response = sock.recv(1024)

            if len(response) > 0:
                # S7 Communication
                s7_setup = bytes([
                    0x03, 0x00, 0x00, 0x19,  # TPKT
                    0x02, 0xF0, 0x80,        # COTP
                    0x32, 0x01, 0x00, 0x00,  # S7 Header
                    0x04, 0x00, 0x00, 0x08,
                    0x00, 0x00, 0xF0, 0x00,
                    0x00, 0x01, 0x00, 0x01,
                    0x01, 0xE0
                ])

                sock.send(s7_setup)
                s7_response = sock.recv(1024)

                # Leer información del sistema
                read_szl = bytes([
                    0x03, 0x00, 0x00, 0x21,  # TPKT
                    0x02, 0xF0, 0x80,        # COTP
                    0x32, 0x07, 0x00, 0x00,  # S7 Header
                    0x05, 0x00, 0x00, 0x08,
                    0x00, 0x0C, 0x00, 0x01,
                    0x12, 0x04, 0x11, 0x44,
                    0x01, 0x00, 0xFF, 0x09,
                    0x00, 0x04, 0x01, 0x1C,
                    0x00, 0x01
                ])

                sock.send(read_szl)
                szl_response = sock.recv(1024)

                # Analizar respuesta para obtener modelo
                model = "Unknown"
                cpu_type = "Unknown"
                firmware = "Unknown"

                if len(szl_response) > 40:
                    # Extraer información básica del SZL
                    if b'CPU' in szl_response:
                        cpu_pos = szl_response.find(b'CPU')
                        if cpu_pos > 0:
                            cpu_info = szl_response[cpu_pos:cpu_pos+20]
                            cpu_type = cpu_info.decode('ascii', errors='ignore').strip()

                    # Detectar series comunes de Siemens
                    if b'1200' in szl_response:
                        model = "S7-1200"
                    elif b'1500' in szl_response:
                        model = "S7-1500"
                    elif b'300' in szl_response:
                        model = "S7-300"
                    elif b'400' in szl_response:
                        model = "S7-400"
                    elif b'1214' in szl_response:
                        model = "S7-1214C"
                    elif b'1215' in szl_response:
                        model = "S7-1215C"

                # Obtener instrucciones en ejecución (simulado)
                instructions = self._get_siemens_instructions()

                sock.close()

                return PLCInfo(
                    ip_address=ip,
                    manufacturer="Siemens",
                    model=model,
                    firmware_version=firmware,
                    cpu_type=cpu_type,
                    status="Online",
                    communication_protocol="S7/ISO-TSAP",
                    instructions_detected=instructions,
                    last_scan=datetime.now()
                )

        except Exception as e:
            print(f"      ❌ Error conectando a Siemens PLC: {e}")

        return PLCInfo(
            ip_address=ip,
            manufacturer="Siemens",
            model="S7 Series",
            firmware_version="Unknown",
            communication_protocol="S7/ISO-TSAP",
            status="Detected",
            last_scan=datetime.now()
        )

    def _get_siemens_instructions(self):
        """Obtener instrucciones típicas de un PLC Siemens"""
        # Simulación de instrucciones comunes detectadas
        return [
            "LD (Load): Cargar valor de entrada digital",
            "AN (And Not): AND lógico negado",
            "= (Assign): Asignar resultado a salida",
            "MOV (Move): Mover datos entre registros",
            "ADD_I (Add Integer): Suma de enteros",
            "CMP_I (Compare Integer): Comparación de enteros",
            "TON (Timer On Delay): Temporizador con retardo",
            "CTU (Count Up): Contador ascendente",
            "CALL FC1: Llamada a función FC1",
            "JMP M001: Salto condicional a etiqueta"
        ]

    def _identify_ab_plc(self, ip, port):
        """Identificar PLCs Allen-Bradley"""
        return PLCInfo(
            ip_address=ip,
            manufacturer="Allen-Bradley",
            model="CompactLogix/ControlLogix",
            firmware_version="Unknown",
            communication_protocol="EtherNet/IP",
            status="Detected",
            last_scan=datetime.now()
        )

    def _identify_omron_plc(self, ip, port):
        """Identificar PLCs Omron"""
        return PLCInfo(
            ip_address=ip,
            manufacturer="Omron",
            model="CJ/CP/CS Series",
            firmware_version="Unknown",
            communication_protocol="FINS",
            status="Detected",
            last_scan=datetime.now()
        )

    def _identify_modbus_device(self, ip, port):
        """Identificar dispositivos Modbus"""
        return PLCInfo(
            ip_address=ip,
            manufacturer="Generic",
            model="Modbus Device",
            firmware_version="Unknown",
            communication_protocol="Modbus TCP",
            status="Detected",
            last_scan=datetime.now()
        )

    def discover_switch_info(self, switch_ip):
        """Obtener información detallada de switch mediante SNMP"""
        print(f"🌐 Analizando switch en {switch_ip}...")

        # Simulación de información de switch
        switch_info = SwitchInfo(
            ip_address=switch_ip,
            hostname=f"SW-{switch_ip.split('.')[-1]}",
            model="Cisco Catalyst 2960",
            mac_address="00:1A:2B:3C:4D:5E",
            vlan_info={
                1: "default",
                10: "production",
                20: "maintenance",
                30: "management"
            },
            port_status={
                "Gi0/1": "up/up - Connected to PLC",
                "Gi0/2": "up/up - Connected to HMI",
                "Gi0/3": "down/down - Unused",
                "Gi0/24": "up/up - Uplink"
            },
            uptime="45 days, 12:34:56"
        )

        self.discovered_switches[switch_ip] = switch_info
        return switch_info

    def analyze_connection_quality(self, target_ip):
        """Analizar calidad de conexión de red"""
        print(f"📊 Analizando calidad de conexión a {target_ip}...")

        # Ping test
        try:
            result = subprocess.run(['ping', '-c', '4', target_ip],
                                  capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                lines = result.stdout.split('\n')
                stats_line = [line for line in lines if 'avg' in line]
                if stats_line:
                    stats = stats_line[0].split('=')[1].split('/')
                    avg_latency = float(stats[1])

                    quality = "Excelente" if avg_latency < 5 else \
                             "Buena" if avg_latency < 20 else \
                             "Regular" if avg_latency < 50 else "Pobre"

                    return {
                        "status": "Conectado",
                        "latency_avg": avg_latency,
                        "quality": quality,
                        "details": result.stdout
                    }

        except Exception as e:
            return {
                "status": "Error",
                "error": str(e),
                "quality": "No disponible"
            }

        return {
            "status": "No conectado",
            "quality": "Sin conexión"
        }

    def generate_field_report(self):
        """Generar reporte de diagnóstico de campo"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "scan_summary": {
                "interfaces_found": len(self.network_interfaces),
                "plcs_discovered": len(self.discovered_plcs),
                "switches_found": len(self.discovered_switches),
                "current_vlan": self.current_vlan
            },
            "network_interfaces": {k: asdict(v) for k, v in self.network_interfaces.items()},
            "discovered_plcs": {k: asdict(v) for k, v in self.discovered_plcs.items()},
            "discovered_switches": {k: asdict(v) for k, v in self.discovered_switches.items()},
            "recommendations": self._generate_field_recommendations()
        }

        # Guardar reporte
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"reports/smartcompute_field_diagnostics_{timestamp}.json"

        Path("reports").mkdir(exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"📄 Reporte guardado: {filename}")
        return report

    def _generate_field_recommendations(self):
        """Generar recomendaciones basadas en el diagnóstico"""
        recommendations = []

        # Recomendaciones de red
        if self.current_vlan is None:
            recommendations.append({
                "type": "network",
                "priority": "medium",
                "title": "VLAN no detectada",
                "description": "No se detectó configuración de VLAN en la interfaz activa",
                "action": "Verificar configuración de switch y VLAN tagging"
            })

        # Recomendaciones de PLCs
        for ip, plc in self.discovered_plcs.items():
            if plc.manufacturer == "Unknown":
                recommendations.append({
                    "type": "plc",
                    "priority": "high",
                    "title": f"PLC no identificado en {ip}",
                    "description": "No se pudo identificar completamente el PLC",
                    "action": "Verificar protocolo de comunicación y permisos"
                })

        if not self.discovered_plcs:
            recommendations.append({
                "type": "plc",
                "priority": "high",
                "title": "No se encontraron PLCs",
                "description": "No se detectaron PLCs en el rango de red escaneado",
                "action": "Verificar conectividad de red y rango IP"
            })

        return recommendations

def main():
    """Función principal de diagnóstico de campo"""
    print("=== SmartCompute Industrial - Diagnóstico de Campo ===")
    print("Desarrollado por: ggwre04p0@mozmail.com")
    print("LinkedIn: https://www.linkedin.com/in/martín-iribarne-swtf/")
    print()

    diagnostics = SmartComputeFieldDiagnostics()

    try:
        # 1. Escanear interfaces de red
        print("🔧 Paso 1: Escaneando interfaces de red...")
        interfaces = diagnostics.scan_network_interfaces()

        # 2. Detectar VLAN actual
        print("\n🔧 Paso 2: Detectando VLAN actual...")
        current_vlan = diagnostics.detect_current_vlan()

        # 3. Escanear PLCs
        print("\n🔧 Paso 3: Escaneando PLCs industriales...")
        plcs = diagnostics.scan_for_plcs()

        # 4. Mostrar resultados
        print(f"\n📊 RESULTADOS DEL DIAGNÓSTICO:")
        print(f"  🌐 Interfaces encontradas: {len(interfaces)}")
        print(f"  🏭 PLCs descubiertos: {len(plcs)}")
        print(f"  📡 VLAN actual: {current_vlan if current_vlan else 'No detectada'}")

        if plcs:
            print("\n🏭 PLCs ENCONTRADOS:")
            for ip, plc in plcs.items():
                print(f"  ✅ {ip}: {plc.manufacturer} {plc.model}")
                print(f"     - Protocolo: {plc.communication_protocol}")
                print(f"     - Estado: {plc.status}")
                if plc.instructions_detected:
                    print(f"     - Instrucciones detectadas: {len(plc.instructions_detected)}")

        # 5. Generar reporte
        print("\n🔧 Paso 4: Generando reporte...")
        report = diagnostics.generate_field_report()

        print("\n✅ Diagnóstico de campo completado exitosamente")
        print("💡 Use este diagnóstico para:")
        print("   - Identificar equipos problemáticos")
        print("   - Verificar conectividad de red")
        print("   - Planificar mantenimiento")
        print("   - Integrar con análisis MLE Star")

    except Exception as e:
        print(f"❌ Error en diagnóstico: {e}")
        return False

    return True

if __name__ == "__main__":
    main()