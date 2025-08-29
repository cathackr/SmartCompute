#!/usr/bin/env python3
"""
SmartCompute Self-Protection System
Protects the monitoring system against attacks and manipulations
"""

import hashlib
import hmac
import time
import os
import threading
import json
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import psutil


class SystemIntegrityMonitor:
    """
    Monitors the integrity of SmartCompute itself
    Prevents tampering and detects manipulation attempts
    """
    
    def __init__(self, config_path: str = "smartcompute_config.json"):
        self.config_path = config_path
        self.integrity_key = self._generate_integrity_key()
        self.process_whitelist = set()
        self.file_checksums = {}
        self.last_integrity_check = None
        self.suspicious_activities = []
        self.protection_active = True
        
        # Initialize protection
        self._initialize_protection()
    
    def _generate_integrity_key(self) -> bytes:
        """Generate cryptographic key for integrity checks"""
        # Use system-specific entropy
        system_info = f"{os.uname()}{psutil.boot_time()}"
        salt = hashlib.sha256(system_info.encode()).digest()
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        return base64.urlsafe_b64encode(kdf.derive(b"smartcompute_integrity"))
    
    def _initialize_protection(self) -> None:
        """Initialize self-protection mechanisms"""
        # Calculate checksums of critical files
        critical_files = [
            'app/core/smart_compute.py',
            'app/core/portable_system.py',
            'app/services/monitoring.py',
            'app/api/main.py'
        ]
        
        for file_path in critical_files:
            if os.path.exists(file_path):
                self.file_checksums[file_path] = self._calculate_file_checksum(file_path)
        
        # Whitelist current process and parent
        current_pid = os.getpid()
        parent_pid = os.getppid()
        
        self.process_whitelist.add(current_pid)
        self.process_whitelist.add(parent_pid)
        
        print(f"🛡️ Self-protection initialized for PID {current_pid}")
    
    def _calculate_file_checksum(self, file_path: str) -> str:
        """Calculate SHA-256 checksum of a file"""
        hash_sha256 = hashlib.sha256()
        
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            print(f"⚠️ Could not calculate checksum for {file_path}: {e}")
            return ""
    
    def verify_system_integrity(self) -> Dict[str, Any]:
        """Verify that SmartCompute files haven't been tampered with"""
        integrity_status = {
            'status': 'clean',
            'modified_files': [],
            'new_files': [],
            'missing_files': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # Check existing files
        for file_path, original_checksum in self.file_checksums.items():
            if not os.path.exists(file_path):
                integrity_status['missing_files'].append(file_path)
                integrity_status['status'] = 'compromised'
                continue
            
            current_checksum = self._calculate_file_checksum(file_path)
            if current_checksum != original_checksum:
                integrity_status['modified_files'].append({
                    'file': file_path,
                    'original': original_checksum[:16],
                    'current': current_checksum[:16]
                })
                integrity_status['status'] = 'modified'
        
        self.last_integrity_check = datetime.now()
        
        if integrity_status['status'] != 'clean':
            self._log_security_event('integrity_check_failed', integrity_status)
        
        return integrity_status
    
    def monitor_suspicious_processes(self) -> List[Dict[str, Any]]:
        """Monitor for processes that might be tampering with SmartCompute"""
        suspicious_processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
                try:
                    proc_info = proc.info
                    
                    # Skip whitelisted processes
                    if proc_info['pid'] in self.process_whitelist:
                        continue
                    
                    # Check for suspicious activities
                    is_suspicious = False
                    reasons = []
                    
                    # Check if process is accessing SmartCompute files
                    try:
                        open_files = proc.open_files()
                        for f in open_files:
                            if 'smartcompute' in f.path.lower() or 'app/' in f.path:
                                is_suspicious = True
                                reasons.append(f"accessing_file:{f.path}")
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                    
                    # Check command line for suspicious patterns
                    cmdline = ' '.join(proc_info['cmdline'] or [])
                    suspicious_patterns = ['inject', 'patch', 'hook', 'debug', 'trace']
                    
                    for pattern in suspicious_patterns:
                        if pattern in cmdline.lower():
                            is_suspicious = True
                            reasons.append(f"suspicious_cmdline:{pattern}")
                    
                    # Check for processes with high privilege that appeared recently
                    if proc_info['create_time'] > time.time() - 300:  # Last 5 minutes
                        try:
                            if proc.username() == 'root':
                                is_suspicious = True
                                reasons.append("recent_high_privilege")
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                    
                    if is_suspicious:
                        suspicious_processes.append({
                            'pid': proc_info['pid'],
                            'name': proc_info['name'],
                            'cmdline': cmdline[:100],
                            'reasons': reasons,
                            'create_time': proc_info['create_time']
                        })
                
                except (psutil.NoSuchProcess, psutil.ZombieProcess):
                    continue
                    
        except Exception as e:
            print(f"⚠️ Error monitoring processes: {e}")
        
        if suspicious_processes:
            self._log_security_event('suspicious_processes_detected', {
                'count': len(suspicious_processes),
                'processes': suspicious_processes[:5]  # Log first 5
            })
        
        return suspicious_processes
    
    def check_network_integrity(self) -> Dict[str, Any]:
        """Check for suspicious network connections"""
        network_status = {
            'status': 'clean',
            'suspicious_connections': [],
            'unexpected_listeners': []
        }
        
        try:
            # Check for unexpected listening ports
            expected_ports = {8000, 8080}  # SmartCompute API ports
            
            for conn in psutil.net_connections(kind='inet'):
                if conn.status == 'LISTEN':
                    port = conn.laddr.port
                    
                    # Check if it's an unexpected listener
                    if port not in expected_ports and conn.pid not in self.process_whitelist:
                        try:
                            proc = psutil.Process(conn.pid)
                            if 'smartcompute' in proc.name().lower():
                                network_status['unexpected_listeners'].append({
                                    'port': port,
                                    'pid': conn.pid,
                                    'process': proc.name()
                                })
                                network_status['status'] = 'suspicious'
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                
                # Check for suspicious outbound connections
                elif conn.status == 'ESTABLISHED' and conn.pid in self.process_whitelist:
                    # SmartCompute processes shouldn't make unexpected outbound connections
                    if conn.raddr and conn.raddr.ip not in ['127.0.0.1', '::1']:
                        network_status['suspicious_connections'].append({
                            'local': f"{conn.laddr.ip}:{conn.laddr.port}",
                            'remote': f"{conn.raddr.ip}:{conn.raddr.port}",
                            'pid': conn.pid
                        })
                        network_status['status'] = 'suspicious'
        
        except Exception as e:
            print(f"⚠️ Error checking network integrity: {e}")
            network_status['status'] = 'error'
        
        if network_status['status'] != 'clean':
            self._log_security_event('network_integrity_issue', network_status)
        
        return network_status
    
    def _log_security_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """Log security events"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'type': event_type,
            'details': details,
            'severity': self._assess_severity(event_type)
        }
        
        self.suspicious_activities.append(event)
        
        # Keep only last 100 events
        if len(self.suspicious_activities) > 100:
            self.suspicious_activities = self.suspicious_activities[-100:]
        
        # Alert on critical events
        if event['severity'] == 'critical':
            print(f"🚨 CRITICAL SECURITY EVENT: {event_type}")
            print(f"   Details: {details}")
    
    def _assess_severity(self, event_type: str) -> str:
        """Assess severity of security event"""
        critical_events = ['integrity_check_failed', 'code_injection_detected']
        high_events = ['suspicious_processes_detected', 'network_integrity_issue']
        
        if event_type in critical_events:
            return 'critical'
        elif event_type in high_events:
            return 'high'
        else:
            return 'medium'
    
    def run_security_scan(self) -> Dict[str, Any]:
        """Run comprehensive security scan"""
        print("🔍 Running security scan...")
        
        scan_results = {
            'scan_timestamp': datetime.now().isoformat(),
            'integrity_check': self.verify_system_integrity(),
            'process_monitoring': self.monitor_suspicious_processes(),
            'network_check': self.check_network_integrity(),
            'overall_status': 'clean'
        }
        
        # Determine overall status
        if (scan_results['integrity_check']['status'] == 'compromised' or 
            scan_results['network_check']['status'] == 'suspicious'):
            scan_results['overall_status'] = 'compromised'
        elif (scan_results['integrity_check']['status'] == 'modified' or 
              len(scan_results['process_monitoring']) > 0):
            scan_results['overall_status'] = 'suspicious'
        
        return scan_results
    
    def enable_continuous_protection(self, check_interval: int = 300) -> None:
        """Enable continuous security monitoring"""
        def protection_loop():
            while self.protection_active:
                try:
                    scan_results = self.run_security_scan()
                    
                    if scan_results['overall_status'] != 'clean':
                        print(f"⚠️ Security scan found issues: {scan_results['overall_status']}")
                    
                    time.sleep(check_interval)
                    
                except Exception as e:
                    print(f"⚠️ Error in protection loop: {e}")
                    time.sleep(60)  # Wait before retrying
        
        protection_thread = threading.Thread(target=protection_loop, daemon=True)
        protection_thread.start()
        print(f"🛡️ Continuous protection enabled (check every {check_interval}s)")
    
    def disable_protection(self) -> None:
        """Disable continuous protection"""
        self.protection_active = False
        print("🛡️ Self-protection disabled")
    
    def get_security_summary(self) -> Dict[str, Any]:
        """Get summary of security status"""
        recent_events = [e for e in self.suspicious_activities 
                        if datetime.fromisoformat(e['timestamp']) > datetime.now() - timedelta(hours=24)]
        
        return {
            'protection_active': self.protection_active,
            'last_integrity_check': self.last_integrity_check.isoformat() if self.last_integrity_check else None,
            'recent_events_24h': len(recent_events),
            'critical_events_24h': len([e for e in recent_events if e['severity'] == 'critical']),
            'files_monitored': len(self.file_checksums),
            'whitelisted_processes': len(self.process_whitelist)
        }


class SecureConfigManager:
    """
    Secure configuration management with encryption
    """
    
    def __init__(self, config_file: str = "smartcompute_secure.conf"):
        self.config_file = config_file
        self.cipher_suite = self._initialize_encryption()
    
    def _initialize_encryption(self) -> Fernet:
        """Initialize encryption for configuration"""
        # Generate key from system characteristics
        key_material = f"{os.uname()}{psutil.boot_time()}".encode()
        digest = hashes.Hash(hashes.SHA256())
        digest.update(key_material)
        key = base64.urlsafe_b64encode(digest.finalize())
        
        return Fernet(key)
    
    def save_secure_config(self, config: Dict[str, Any]) -> None:
        """Save configuration with encryption"""
        config_json = json.dumps(config).encode()
        encrypted_config = self.cipher_suite.encrypt(config_json)
        
        with open(self.config_file, 'wb') as f:
            f.write(encrypted_config)
    
    def load_secure_config(self) -> Optional[Dict[str, Any]]:
        """Load and decrypt configuration"""
        try:
            with open(self.config_file, 'rb') as f:
                encrypted_config = f.read()
            
            decrypted_config = self.cipher_suite.decrypt(encrypted_config)
            return json.loads(decrypted_config.decode())
        
        except Exception:
            return None


if __name__ == "__main__":
    # Demo self-protection system
    protector = SystemIntegrityMonitor()
    scan_results = protector.run_security_scan()
    
    print("Security Scan Results:")
    print(f"Overall Status: {scan_results['overall_status']}")
    print(f"Integrity: {scan_results['integrity_check']['status']}")
    print(f"Network: {scan_results['network_check']['status']}")
    print(f"Suspicious Processes: {len(scan_results['process_monitoring'])}")