#!/usr/bin/env python3
"""
SmartCompute Industrial - Network Intelligence Analyzer
Multi-protocol network analysis for industrial environments
"""

import asyncio
import socket
import struct
import time
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import json
import ipaddress
import subprocess
import re

from scapy.all import sniff, Ether, IP, TCP, UDP, ICMP, ARP
from scapy.layers.inet import traceroute


class ProtocolType(Enum):
    """Supported protocol types"""
    MODBUS_TCP = "modbus_tcp"
    PROFINET = "profinet" 
    ETHERNET_IP = "ethernet_ip"
    OPCUA = "opcua"
    BACNET = "bacnet"
    SNMP = "snmp"
    HTTP = "http"
    HTTPS = "https"
    SSH = "ssh"
    TELNET = "telnet"


class DeviceType(Enum):
    """Network device types"""
    PLC = "plc"
    HMI = "hmi"
    SWITCH = "switch"
    ROUTER = "router"
    FIREWALL = "firewall"
    ACCESS_POINT = "access_point"
    SERVER = "server"
    WORKSTATION = "workstation"
    UNKNOWN = "unknown"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class NetworkDevice:
    """Network device information"""
    ip_address: str
    mac_address: str
    hostname: str = ""
    device_type: DeviceType = DeviceType.UNKNOWN
    vendor: str = ""
    open_ports: List[int] = None
    protocols: List[ProtocolType] = None
    last_seen: datetime = None
    response_time: float = 0.0
    vlan_id: Optional[int] = None
    subnet: str = ""
    
    def __post_init__(self):
        if self.open_ports is None:
            self.open_ports = []
        if self.protocols is None:
            self.protocols = []
        if self.last_seen is None:
            self.last_seen = datetime.now()


@dataclass
class NetworkAlert:
    """Network alert information"""
    timestamp: datetime
    severity: AlertSeverity
    alert_type: str
    device_ip: str
    message: str
    details: Dict[str, Any]
    resolved: bool = False


@dataclass
class NetworkPerformanceMetrics:
    """Network performance metrics"""
    timestamp: datetime
    device_ip: str
    latency_ms: float
    packet_loss_pct: float
    bandwidth_utilization_pct: float
    connection_count: int
    error_count: int
    retransmission_count: int


class IndustrialProtocolAnalyzer:
    """Analyzer for industrial protocols"""
    
    @staticmethod
    def analyze_modbus_tcp(packet_data: bytes) -> Optional[Dict[str, Any]]:
        """Analyze Modbus TCP packet"""
        try:
            if len(packet_data) < 12:  # Minimum Modbus TCP length
                return None
            
            # Modbus TCP Header: Transaction ID (2) + Protocol ID (2) + Length (2) + Unit ID (1) + Function Code (1)
            transaction_id = struct.unpack(">H", packet_data[0:2])[0]
            protocol_id = struct.unpack(">H", packet_data[2:4])[0]
            length = struct.unpack(">H", packet_data[4:6])[0]
            unit_id = packet_data[6]
            function_code = packet_data[7]
            
            if protocol_id != 0:  # Modbus TCP protocol identifier
                return None
            
            function_names = {
                1: "Read Coils", 2: "Read Discrete Inputs", 3: "Read Holding Registers",
                4: "Read Input Registers", 5: "Write Single Coil", 6: "Write Single Register",
                15: "Write Multiple Coils", 16: "Write Multiple Registers"
            }
            
            return {
                "protocol": "Modbus TCP",
                "transaction_id": transaction_id,
                "unit_id": unit_id,
                "function_code": function_code,
                "function_name": function_names.get(function_code, f"Unknown ({function_code})"),
                "length": length,
                "is_response": function_code & 0x80 != 0
            }
            
        except Exception as e:
            logging.debug(f"Error analyzing Modbus TCP packet: {e}")
            return None
    
    @staticmethod
    def analyze_profinet(packet_data: bytes) -> Optional[Dict[str, Any]]:
        """Analyze PROFINET packet"""
        try:
            # PROFINET uses Ethernet Type 0x8892 for Real-Time (RT) or 0x8100 for VLAN
            # This is a simplified analysis
            if len(packet_data) < 20:
                return None
            
            # Basic PROFINET frame analysis
            return {
                "protocol": "PROFINET",
                "frame_type": "RT",  # Real-Time
                "cycle_counter": struct.unpack(">H", packet_data[0:2])[0] if len(packet_data) >= 2 else 0,
                "data_status": packet_data[2] if len(packet_data) > 2 else 0
            }
            
        except Exception as e:
            logging.debug(f"Error analyzing PROFINET packet: {e}")
            return None
    
    @staticmethod 
    def analyze_ethernet_ip(packet_data: bytes) -> Optional[Dict[str, Any]]:
        """Analyze EtherNet/IP packet"""
        try:
            if len(packet_data) < 24:  # Minimum EIP header length
                return None
            
            # EtherNet/IP Header
            command = struct.unpack("<H", packet_data[0:2])[0]
            length = struct.unpack("<H", packet_data[2:4])[0]
            session_handle = struct.unpack("<L", packet_data[4:8])[0]
            status = struct.unpack("<L", packet_data[8:12])[0]
            
            command_names = {
                0x0065: "RegisterSession", 0x0066: "UnRegisterSession",
                0x006F: "SendRRData", 0x0070: "SendUnitData"
            }
            
            return {
                "protocol": "EtherNet/IP",
                "command": command,
                "command_name": command_names.get(command, f"Unknown ({command:04X})"),
                "length": length,
                "session_handle": session_handle,
                "status": status
            }
            
        except Exception as e:
            logging.debug(f"Error analyzing EtherNet/IP packet: {e}")
            return None


class SecurityDeviceIntegrator:
    """Integration with security devices (Cisco, Fortigate, Palo Alto, etc.)"""
    
    def __init__(self):
        self.device_configs = {}
        self.supported_vendors = {
            "cisco": {"snmp_community": "public", "api_port": 443},
            "fortinet": {"api_port": 443, "api_path": "/api/v2"},
            "paloalto": {"api_port": 443, "api_path": "/api"},
            "checkpoint": {"api_port": 443, "api_path": "/web_api"},
            "opengear": {"api_port": 443, "api_path": "/api"}
        }
    
    def add_security_device(self, ip: str, vendor: str, credentials: Dict[str, str]):
        """Add security device for monitoring"""
        if vendor.lower() in self.supported_vendors:
            self.device_configs[ip] = {
                "vendor": vendor.lower(),
                "credentials": credentials,
                "config": self.supported_vendors[vendor.lower()]
            }
            logging.info(f"Added {vendor} security device: {ip}")
    
    async def get_firewall_rules(self, device_ip: str) -> List[Dict[str, Any]]:
        """Get firewall rules from security device"""
        if device_ip not in self.device_configs:
            return []
        
        device = self.device_configs[device_ip]
        vendor = device["vendor"]
        
        # Mock implementation - in production would use vendor APIs
        mock_rules = [
            {
                "rule_id": 1,
                "name": "Allow Industrial Network",
                "source": "192.168.100.0/24",
                "destination": "192.168.200.0/24", 
                "service": "modbus-tcp",
                "action": "allow",
                "enabled": True
            },
            {
                "rule_id": 2,
                "name": "Block Internet Access",
                "source": "192.168.200.0/24",
                "destination": "any",
                "service": "any",
                "action": "deny",
                "enabled": True
            }
        ]
        
        logging.debug(f"Retrieved {len(mock_rules)} firewall rules from {vendor} device {device_ip}")
        return mock_rules
    
    async def get_threat_intelligence(self, device_ip: str) -> Dict[str, Any]:
        """Get threat intelligence from security device"""
        if device_ip not in self.device_configs:
            return {}
        
        # Mock threat intelligence data
        return {
            "threats_detected_24h": 12,
            "blocked_connections": 45,
            "suspicious_ips": ["10.0.1.50", "192.168.1.100"],
            "malware_signatures": 3,
            "last_update": datetime.now().isoformat()
        }


class LocalThreatAnalyzer:
    """Local threat pattern analysis (no external connections)"""
    
    def __init__(self):
        self.threat_patterns = {}
        self.learning_enabled = True
        
    def analyze_local_patterns(self, network_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze network patterns locally for anomalies"""
        
        # Local pattern analysis without external connections
        analysis = {
            "unusual_traffic_patterns": [],
            "potential_security_issues": [],
            "optimization_suggestions": [],
            "administrative_recommendations": []
        }
        
        # Example local analysis
        if network_data.get("high_modbus_frequency", 0) > 100:
            analysis["administrative_recommendations"].append({
                "type": "performance_optimization",
                "message": "Consider reducing Modbus polling frequency",
                "impact": "Reduce network congestion",
                "action_required": "Administrator should review PLC polling settings"
            })
        
        return analysis
    
    def learn_from_patterns(self, pattern_data: Dict[str, Any]):
        """Learn from observed network patterns (local only)"""
        if not self.learning_enabled:
            return
            
        # Store patterns locally for future analysis
        pattern_key = f"{pattern_data.get('type', 'unknown')}_{int(time.time())}"
        self.threat_patterns[pattern_key] = {
            "timestamp": datetime.now().isoformat(),
            "pattern": pattern_data,
            "learned_locally": True
        }
        
        # Keep only recent patterns (last 30 days)
        cutoff_time = datetime.now() - timedelta(days=30)
        self.threat_patterns = {
            k: v for k, v in self.threat_patterns.items()
            if datetime.fromisoformat(v["timestamp"]) > cutoff_time
        }


class NetworkIntelligenceAnalyzer:
    """Main network intelligence analyzer"""
    
    def __init__(self, interface: str = None):
        self.interface = interface
        self.discovered_devices: Dict[str, NetworkDevice] = {}
        self.alerts: List[NetworkAlert] = []
        self.performance_metrics: List[NetworkPerformanceMetrics] = []
        self.protocol_analyzer = IndustrialProtocolAnalyzer()
        self.security_integrator = SecurityDeviceIntegrator()
        self.threat_analyzer = LocalThreatAnalyzer()
        self.monitoring_active = False
        
        # Network conflict detection
        self.ip_conflicts: Dict[str, List[str]] = {}  # IP -> [MAC addresses]
        self.vlan_assignments: Dict[int, List[str]] = {}  # VLAN -> [IPs]
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    async def start_monitoring(self):
        """Start network monitoring"""
        self.monitoring_active = True
        self.logger.info("🚀 Starting Network Intelligence Analyzer")
        
        # Start background tasks
        tasks = [
            asyncio.create_task(self.network_discovery()),
            asyncio.create_task(self.performance_monitoring()),
            asyncio.create_task(self.conflict_detection()),
            asyncio.create_task(self.packet_analysis())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            self.logger.error(f"Error in monitoring tasks: {e}")
        finally:
            self.monitoring_active = False
    
    async def network_discovery(self):
        """Discover network devices"""
        while self.monitoring_active:
            try:
                # Get network interfaces and subnets
                subnets = await self.get_local_subnets()
                
                for subnet in subnets:
                    await self.scan_subnet(subnet)
                
                # Clean up old devices (not seen in 5 minutes)
                cutoff_time = datetime.now() - timedelta(minutes=5)
                devices_to_remove = [
                    ip for ip, device in self.discovered_devices.items()
                    if device.last_seen < cutoff_time
                ]
                
                for ip in devices_to_remove:
                    del self.discovered_devices[ip]
                    self.logger.info(f"Removed stale device: {ip}")
                
                await asyncio.sleep(60)  # Discover every minute
                
            except Exception as e:
                self.logger.error(f"Error in network discovery: {e}")
                await asyncio.sleep(60)
    
    async def get_local_subnets(self) -> List[str]:
        """Get local network subnets"""
        try:
            result = subprocess.run(
                ["ip", "route", "show", "scope", "link"],
                capture_output=True, text=True, timeout=10
            )
            
            subnets = []
            for line in result.stdout.split('\n'):
                if 'dev' in line and '/' in line:
                    # Extract subnet from route line
                    parts = line.split()
                    if len(parts) > 0 and '/' in parts[0]:
                        subnet = parts[0]
                        # Validate subnet format
                        try:
                            ipaddress.ip_network(subnet, strict=False)
                            subnets.append(subnet)
                        except:
                            pass
            
            return subnets[:5]  # Limit to first 5 subnets
            
        except Exception as e:
            self.logger.debug(f"Error getting subnets: {e}")
            # Fallback to common private subnets
            return ["192.168.1.0/24", "192.168.0.0/24", "10.0.0.0/24"]
    
    async def scan_subnet(self, subnet: str):
        """Scan subnet for devices"""
        try:
            network = ipaddress.ip_network(subnet, strict=False)
            # Limit scan to first 50 IPs for performance
            hosts_to_scan = list(network.hosts())[:50]
            
            for host_ip in hosts_to_scan:
                ip_str = str(host_ip)
                
                # Quick ping check
                ping_result = subprocess.run(
                    ["ping", "-c", "1", "-W", "1", ip_str],
                    capture_output=True, timeout=2
                )
                
                if ping_result.returncode == 0:
                    # Device is alive, get more info
                    device = await self.analyze_device(ip_str)
                    if device:
                        self.discovered_devices[ip_str] = device
                
                await asyncio.sleep(0.1)  # Small delay to avoid flooding
                
        except Exception as e:
            self.logger.debug(f"Error scanning subnet {subnet}: {e}")
    
    async def analyze_device(self, ip: str) -> Optional[NetworkDevice]:
        """Analyze individual device"""
        try:
            # Get MAC address
            mac_address = await self.get_mac_address(ip)
            if not mac_address:
                mac_address = "unknown"
            
            # Get hostname
            hostname = await self.get_hostname(ip)
            
            # Port scan for common industrial ports
            open_ports = await self.port_scan(ip)
            
            # Determine device type and protocols
            device_type, protocols = self.classify_device(open_ports)
            
            # Get vendor from MAC
            vendor = self.get_vendor_from_mac(mac_address)
            
            # Measure response time
            response_time = await self.measure_response_time(ip)
            
            device = NetworkDevice(
                ip_address=ip,
                mac_address=mac_address,
                hostname=hostname,
                device_type=device_type,
                vendor=vendor,
                open_ports=open_ports,
                protocols=protocols,
                response_time=response_time,
                subnet=self.get_subnet_for_ip(ip)
            )
            
            self.logger.debug(f"Analyzed device {ip}: {device_type.value}, {len(open_ports)} ports")
            return device
            
        except Exception as e:
            self.logger.debug(f"Error analyzing device {ip}: {e}")
            return None
    
    async def get_mac_address(self, ip: str) -> Optional[str]:
        """Get MAC address for IP"""
        try:
            # Use ARP to get MAC address
            result = subprocess.run(
                ["arp", "-n", ip],
                capture_output=True, text=True, timeout=2
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if ip in line and ':' in line:
                        # Extract MAC address
                        parts = line.split()
                        for part in parts:
                            if ':' in part and len(part) == 17:
                                return part.lower()
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Error getting MAC for {ip}: {e}")
            return None
    
    async def get_hostname(self, ip: str) -> str:
        """Get hostname for IP"""
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            return hostname
        except:
            return ""
    
    async def port_scan(self, ip: str) -> List[int]:
        """Scan common industrial and network ports"""
        common_ports = [
            22,    # SSH
            23,    # Telnet
            53,    # DNS
            80,    # HTTP
            443,   # HTTPS
            502,   # Modbus TCP
            102,   # S7
            44818, # EtherNet/IP
            4840,  # OPC UA
            161,   # SNMP
            47808, # BACnet
            20000, # DNP3
            2404,  # IEC 104
            789,   # RedLion
            9600,  # OMRON FINS
        ]
        
        open_ports = []
        
        for port in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                result = sock.connect_ex((ip, port))
                sock.close()
                
                if result == 0:
                    open_ports.append(port)
                    
            except:
                pass
        
        return open_ports
    
    def classify_device(self, open_ports: List[int]) -> Tuple[DeviceType, List[ProtocolType]]:
        """Classify device type based on open ports"""
        protocols = []
        
        # Detect protocols
        if 502 in open_ports:
            protocols.append(ProtocolType.MODBUS_TCP)
        if 44818 in open_ports:
            protocols.append(ProtocolType.ETHERNET_IP)
        if 4840 in open_ports:
            protocols.append(ProtocolType.OPCUA)
        if 47808 in open_ports:
            protocols.append(ProtocolType.BACNET)
        if 161 in open_ports:
            protocols.append(ProtocolType.SNMP)
        if 80 in open_ports:
            protocols.append(ProtocolType.HTTP)
        if 443 in open_ports:
            protocols.append(ProtocolType.HTTPS)
        
        # Classify device type
        if any(p in [ProtocolType.MODBUS_TCP, ProtocolType.ETHERNET_IP] for p in protocols):
            device_type = DeviceType.PLC
        elif ProtocolType.OPCUA in protocols:
            device_type = DeviceType.SERVER
        elif 161 in open_ports and (80 in open_ports or 443 in open_ports):
            device_type = DeviceType.SWITCH
        elif 22 in open_ports and 23 in open_ports:
            device_type = DeviceType.ROUTER
        else:
            device_type = DeviceType.UNKNOWN
        
        return device_type, protocols
    
    def get_vendor_from_mac(self, mac: str) -> str:
        """Get vendor from MAC address OUI"""
        if not mac or mac == "unknown":
            return ""
        
        # Common OUI prefixes for industrial devices
        oui_vendors = {
            "00:50:c2": "IEEE 1394",
            "00:0f:fe": "Cisco",
            "00:1b:21": "Intel",
            "00:15:17": "Siemens",
            "00:80:f4": "Schneider Electric",
            "00:a0:45": "Rockwell Automation",
            "00:c0:f2": "Kingston",
            "08:00:30": "Network Research Corporation"
        }
        
        oui = mac[:8].lower()
        return oui_vendors.get(oui, "")
    
    async def measure_response_time(self, ip: str) -> float:
        """Measure network response time"""
        try:
            start_time = time.time()
            ping_result = subprocess.run(
                ["ping", "-c", "1", "-W", "1", ip],
                capture_output=True, timeout=2
            )
            end_time = time.time()
            
            if ping_result.returncode == 0:
                # Parse ping output for actual time
                output = ping_result.stdout.decode()
                time_match = re.search(r'time=(\d+\.?\d*)', output)
                if time_match:
                    return float(time_match.group(1))
                else:
                    return (end_time - start_time) * 1000
            else:
                return -1.0  # No response
                
        except Exception as e:
            self.logger.debug(f"Error measuring response time for {ip}: {e}")
            return -1.0
    
    def get_subnet_for_ip(self, ip: str) -> str:
        """Get subnet for IP address"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            if ip_obj.is_private:
                # Common private subnets
                if str(ip_obj).startswith("192.168."):
                    return f"192.168.{str(ip_obj).split('.')[2]}.0/24"
                elif str(ip_obj).startswith("10."):
                    return "10.0.0.0/8"
                elif str(ip_obj).startswith("172."):
                    return "172.16.0.0/12"
            
            return "unknown"
        except:
            return "unknown"
    
    async def performance_monitoring(self):
        """Monitor network performance"""
        while self.monitoring_active:
            try:
                for ip, device in self.discovered_devices.items():
                    # Measure current performance
                    metrics = await self.collect_performance_metrics(ip, device)
                    if metrics:
                        self.performance_metrics.append(metrics)
                        
                        # Check for performance issues
                        await self.analyze_performance_issues(metrics)
                
                # Keep only last 1000 metrics
                if len(self.performance_metrics) > 1000:
                    self.performance_metrics = self.performance_metrics[-1000:]
                
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in performance monitoring: {e}")
                await asyncio.sleep(30)
    
    async def collect_performance_metrics(self, ip: str, device: NetworkDevice) -> Optional[NetworkPerformanceMetrics]:
        """Collect performance metrics for device"""
        try:
            # Measure latency
            latency = await self.measure_response_time(ip)
            if latency < 0:
                return None
            
            # Mock other metrics - in production would use SNMP/API calls
            packet_loss = 0.0
            bandwidth_util = min(100.0, max(0.0, 20.0 + len(device.open_ports) * 5.0))
            connection_count = len(device.open_ports) * 2
            error_count = 0
            retrans_count = 0
            
            return NetworkPerformanceMetrics(
                timestamp=datetime.now(),
                device_ip=ip,
                latency_ms=latency,
                packet_loss_pct=packet_loss,
                bandwidth_utilization_pct=bandwidth_util,
                connection_count=connection_count,
                error_count=error_count,
                retransmission_count=retrans_count
            )
            
        except Exception as e:
            self.logger.debug(f"Error collecting metrics for {ip}: {e}")
            return None
    
    async def analyze_performance_issues(self, metrics: NetworkPerformanceMetrics):
        """Analyze performance metrics for issues"""
        alerts_to_create = []
        
        # High latency
        if metrics.latency_ms > 100:
            alerts_to_create.append({
                "severity": AlertSeverity.HIGH if metrics.latency_ms > 200 else AlertSeverity.MEDIUM,
                "alert_type": "high_latency",
                "message": f"High network latency detected: {metrics.latency_ms:.1f}ms",
                "details": {"latency_ms": metrics.latency_ms, "threshold": 100}
            })
        
        # High bandwidth utilization
        if metrics.bandwidth_utilization_pct > 80:
            alerts_to_create.append({
                "severity": AlertSeverity.HIGH,
                "alert_type": "high_bandwidth_utilization",
                "message": f"High bandwidth utilization: {metrics.bandwidth_utilization_pct:.1f}%",
                "details": {"utilization_pct": metrics.bandwidth_utilization_pct}
            })
        
        # Create alerts
        for alert_data in alerts_to_create:
            alert = NetworkAlert(
                timestamp=datetime.now(),
                severity=alert_data["severity"],
                alert_type=alert_data["alert_type"],
                device_ip=metrics.device_ip,
                message=alert_data["message"],
                details=alert_data["details"]
            )
            self.alerts.append(alert)
            
            # Analyze locally for learning purposes (no external sharing)
            if alert.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
                self.threat_analyzer.learn_from_patterns({
                    "type": alert.alert_type,
                    "device_ip": alert.device_ip,
                    "severity": alert.severity.value,
                    "timestamp": alert.timestamp.isoformat(),
                    "context": "network_performance_alert"
                })
    
    async def conflict_detection(self):
        """Detect IP, VLAN, and MAC conflicts"""
        while self.monitoring_active:
            try:
                # Detect IP conflicts (same IP, different MACs)
                ip_to_macs = {}
                mac_to_ips = {}
                
                for device in self.discovered_devices.values():
                    ip = device.ip_address
                    mac = device.mac_address
                    
                    if mac and mac != "unknown":
                        if ip not in ip_to_macs:
                            ip_to_macs[ip] = []
                        ip_to_macs[ip].append(mac)
                        
                        if mac not in mac_to_ips:
                            mac_to_ips[mac] = []
                        mac_to_ips[mac].append(ip)
                
                # Check for conflicts
                for ip, macs in ip_to_macs.items():
                    if len(set(macs)) > 1:  # Multiple unique MACs for same IP
                        self.create_conflict_alert(
                            "ip_conflict",
                            f"IP conflict detected: {ip} used by multiple devices",
                            {"ip": ip, "mac_addresses": list(set(macs))}
                        )
                
                for mac, ips in mac_to_ips.items():
                    if len(set(ips)) > 1:  # Multiple IPs for same MAC
                        self.create_conflict_alert(
                            "mac_conflict", 
                            f"MAC conflict detected: {mac} has multiple IPs",
                            {"mac_address": mac, "ip_addresses": list(set(ips))}
                        )
                
                await asyncio.sleep(120)  # Check every 2 minutes
                
            except Exception as e:
                self.logger.error(f"Error in conflict detection: {e}")
                await asyncio.sleep(120)
    
    def create_conflict_alert(self, alert_type: str, message: str, details: Dict[str, Any]):
        """Create network conflict alert with administrative recommendation"""
        
        # Add administrative guidance to the alert
        admin_message = f"{message} - ACCIÓN REQUERIDA: El administrador debe verificar la configuración de red"
        
        alert = NetworkAlert(
            timestamp=datetime.now(),
            severity=AlertSeverity.HIGH,
            alert_type=alert_type,
            device_ip=details.get("ip", "multiple"),
            message=admin_message,
            details={
                **details,
                "requires_admin_action": True,
                "suggested_action": self._get_conflict_resolution_suggestion(alert_type, details),
                "automated_action": "none - monitoring only"
            }
        )
        self.alerts.append(alert)
        self.logger.warning(f"Network conflict detected (admin action required): {message}")
    
    def _get_conflict_resolution_suggestion(self, alert_type: str, details: Dict[str, Any]) -> str:
        """Get suggested resolution for network conflicts"""
        suggestions = {
            "ip_conflict": "Revisar configuración DHCP o asignar IPs estáticas únicas",
            "mac_conflict": "Verificar dispositivos duplicados o problemas de switch",
            "vlan_conflict": "Revisar configuración de VLANs en switches",
            "port_conflict": "Verificar configuración de puertos de switch"
        }
        
        return suggestions.get(alert_type, "Contactar administrador de red para investigación")
    
    async def packet_analysis(self):
        """Analyze network packets for protocol insights"""
        # This would normally use packet capture, but for demo we'll simulate
        while self.monitoring_active:
            try:
                # Simulate protocol analysis
                await asyncio.sleep(60)
                
            except Exception as e:
                self.logger.error(f"Error in packet analysis: {e}")
                await asyncio.sleep(60)
    
    def get_network_topology(self) -> Dict[str, Any]:
        """Get network topology information"""
        topology = {
            "devices": [],
            "subnets": {},
            "connections": [],
            "summary": {
                "total_devices": len(self.discovered_devices),
                "device_types": {},
                "protocols": {},
                "alerts": len([a for a in self.alerts if not a.resolved])
            }
        }
        
        # Count device types and protocols
        for device in self.discovered_devices.values():
            device_type = device.device_type.value
            topology["summary"]["device_types"][device_type] = \
                topology["summary"]["device_types"].get(device_type, 0) + 1
            
            for protocol in device.protocols:
                protocol_name = protocol.value
                topology["summary"]["protocols"][protocol_name] = \
                    topology["summary"]["protocols"].get(protocol_name, 0) + 1
            
            # Add device to topology
            topology["devices"].append({
                "ip": device.ip_address,
                "mac": device.mac_address,
                "hostname": device.hostname,
                "type": device.device_type.value,
                "vendor": device.vendor,
                "protocols": [p.value for p in device.protocols],
                "response_time": device.response_time,
                "subnet": device.subnet
            })
        
        return topology
    
    def get_security_summary(self) -> Dict[str, Any]:
        """Get network security summary"""
        return {
            "total_devices": len(self.discovered_devices),
            "active_alerts": len([a for a in self.alerts if not a.resolved]),
            "critical_alerts": len([a for a in self.alerts if a.severity == AlertSeverity.CRITICAL and not a.resolved]),
            "industrial_devices": len([d for d in self.discovered_devices.values() 
                                    if d.device_type in [DeviceType.PLC, DeviceType.HMI]]),
            "open_industrial_ports": len([d for d in self.discovered_devices.values() 
                                        if any(p in [502, 44818, 4840] for p in d.open_ports)]),
            "recent_alerts": [asdict(a) for a in self.alerts[-10:]]
        }
    
    async def stop_monitoring(self):
        """Stop network monitoring"""
        self.monitoring_active = False
        self.logger.info("🛑 Network Intelligence Analyzer stopped")