#!/usr/bin/env python3
"""
SmartCompute Response System
¡Sistema de respuesta automático a anomalías detectadas!

Tu concepto: Detección + Acción = Producto completo
Ethical Hacker approach: Respuesta inteligente y segura
"""

import os
import sys
import subprocess
import psutil
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple
import threading

class ThreatResponse:
    """Sistema de respuesta automática a amenazas detectadas"""
    
    def __init__(self):
        self.response_config = self.load_response_config()
        self.quarantine_dir = os.path.expanduser("~/smartcompute_quarantine")
        self.create_quarantine_dir()
        
    def load_response_config(self) -> Dict:
        """Carga configuración de respuestas"""
        default_config = {
            "auto_response_enabled": True,
            "severity_thresholds": {
                "low": {"auto_action": "log", "user_prompt": True},
                "medium": {"auto_action": "investigate", "user_prompt": True},
                "high": {"auto_action": "contain", "user_prompt": True},
                "critical": {"auto_action": "isolate", "user_prompt": False}
            },
            "allowed_auto_actions": ["log", "investigate", "contain", "isolate"],
            "user_preferences": {
                "notification_method": "console",  # console, email, desktop
                "auto_quarantine": False,
                "auto_network_isolation": False,
                "create_forensic_snapshot": True
            }
        }
        
        config_file = "smartcompute_response_config.json"
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except:
                pass
        
        return default_config
    
    def create_quarantine_dir(self):
        """Crea directorio de cuarentena si no existe"""
        if not os.path.exists(self.quarantine_dir):
            os.makedirs(self.quarantine_dir)
            print(f"📁 Directorio de cuarentena creado: {self.quarantine_dir}")

class IncidentAnalyzer:
    """Analiza anomalías detectadas y determina tipo de amenaza"""
    
    def classify_threat(self, anomaly_result: Dict) -> Dict:
        """Clasifica el tipo de amenaza basándose en anomalías"""
        threat_info = {
            "threat_type": "unknown",
            "confidence": 0,
            "indicators": [],
            "recommended_actions": []
        }
        
        anomalies = anomaly_result.get('anomalies', {})
        
        # Crypto Mining Detection
        if 'gpu_anomaly' in anomalies and 'cpu_anomaly' in anomalies:
            gpu_severity = anomalies['gpu_anomaly'].get('severity', 'low')
            cpu_severity = anomalies['cpu_anomaly'].get('severity', 'low')
            
            if gpu_severity in ['high', 'medium'] and cpu_severity in ['high', 'medium']:
                threat_info.update({
                    "threat_type": "crypto_mining",
                    "confidence": 85,
                    "indicators": [
                        "High GPU utilization anomaly",
                        "Concurrent CPU spike",
                        "Pattern consistent with mining"
                    ],
                    "recommended_actions": [
                        "identify_mining_processes",
                        "terminate_suspicious_processes",
                        "check_network_connections",
                        "scan_for_mining_malware"
                    ]
                })
        
        # Process Spawning / Botnet Activity
        elif 'process_anomaly' in anomalies:
            proc_details = anomalies['process_anomaly']
            if proc_details.get('severity') == 'high':
                threat_info.update({
                    "threat_type": "process_spawning",
                    "confidence": 75,
                    "indicators": [
                        "Unusual number of processes",
                        "Potential botnet activity",
                        "Suspicious process creation"
                    ],
                    "recommended_actions": [
                        "list_suspicious_processes",
                        "analyze_process_tree",
                        "check_network_connections",
                        "create_process_dump"
                    ]
                })
        
        # Memory-based Attack
        elif 'memory_anomaly' in anomalies:
            mem_details = anomalies['memory_anomaly']
            if mem_details.get('zscore', 0) > 3.0:
                threat_info.update({
                    "threat_type": "memory_attack",
                    "confidence": 70,
                    "indicators": [
                        "Abnormal memory consumption",
                        "Potential data exfiltration",
                        "Memory-resident malware"
                    ],
                    "recommended_actions": [
                        "analyze_memory_usage",
                        "identify_memory_hogs",
                        "check_for_memory_leaks",
                        "create_memory_dump"
                    ]
                })
        
        # Generic High Anomaly
        elif anomaly_result.get('score', 0) >= 50:
            threat_info.update({
                "threat_type": "generic_anomaly",
                "confidence": 60,
                "indicators": [
                    "Multiple system anomalies detected",
                    "Behavior deviation from baseline"
                ],
                "recommended_actions": [
                    "full_system_analysis",
                    "check_running_processes",
                    "analyze_network_activity"
                ]
            })
        
        return threat_info

class ActionExecutor:
    """Ejecuta acciones de respuesta automática"""
    
    def __init__(self, quarantine_dir: str):
        self.quarantine_dir = quarantine_dir
        
    def identify_mining_processes(self) -> List[Dict]:
        """Identifica procesos potenciales de crypto mining"""
        suspicious_processes = []
        mining_keywords = ['miner', 'mining', 'xmr', 'btc', 'eth', 'cryptonight', 'stratum']
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'cmdline']):
                try:
                    process_info = proc.info
                    name = process_info.get('name', '').lower()
                    cmdline = ' '.join(process_info.get('cmdline', [])).lower()
                    
                    # Check for mining keywords
                    for keyword in mining_keywords:
                        if keyword in name or keyword in cmdline:
                            suspicious_processes.append({
                                'pid': process_info['pid'],
                                'name': process_info['name'],
                                'cpu_percent': process_info['cpu_percent'],
                                'memory_percent': process_info['memory_percent'],
                                'cmdline': cmdline,
                                'reason': f'Contains keyword: {keyword}'
                            })
                            break
                    
                    # Check for high resource usage
                    if (process_info.get('cpu_percent', 0) > 80 or 
                        process_info.get('memory_percent', 0) > 50):
                        suspicious_processes.append({
                            'pid': process_info['pid'],
                            'name': process_info['name'],
                            'cpu_percent': process_info['cpu_percent'],
                            'memory_percent': process_info['memory_percent'],
                            'cmdline': cmdline,
                            'reason': 'High resource usage'
                        })
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except Exception as e:
            print(f"Error identificando procesos: {e}")
            
        return suspicious_processes
    
    def list_suspicious_processes(self) -> List[Dict]:
        """Lista procesos sospechosos generales"""
        suspicious_processes = []
        
        try:
            # Get processes sorted by resource usage
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'create_time']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
            
            # Get top 10 CPU consumers
            for proc in processes[:10]:
                if proc.get('cpu_percent', 0) > 10:  # More than 10% CPU
                    suspicious_processes.append({
                        'pid': proc['pid'],
                        'name': proc['name'],
                        'cpu_percent': proc['cpu_percent'],
                        'memory_percent': proc['memory_percent'],
                        'reason': 'High CPU usage'
                    })
                    
        except Exception as e:
            print(f"Error listando procesos: {e}")
            
        return suspicious_processes
    
    def check_network_connections(self) -> List[Dict]:
        """Verifica conexiones de red sospechosas"""
        suspicious_connections = []
        
        try:
            connections = psutil.net_connections(kind='inet')
            
            for conn in connections:
                if conn.status == psutil.CONN_ESTABLISHED and conn.raddr:
                    remote_ip = conn.raddr.ip
                    
                    # Check for suspicious patterns
                    is_suspicious = False
                    reason = ""
                    
                    # Non-standard ports
                    if conn.raddr.port in [4444, 8080, 9999, 1337, 31337]:
                        is_suspicious = True
                        reason = f"Suspicious port {conn.raddr.port}"
                    
                    # Private/internal IPs connecting outbound on unusual ports
                    if not self._is_local_ip(remote_ip) and conn.raddr.port > 10000:
                        is_suspicious = True
                        reason = f"High port outbound connection"
                    
                    if is_suspicious:
                        try:
                            process = psutil.Process(conn.pid) if conn.pid else None
                            suspicious_connections.append({
                                'local_addr': f"{conn.laddr.ip}:{conn.laddr.port}",
                                'remote_addr': f"{remote_ip}:{conn.raddr.port}",
                                'status': conn.status,
                                'pid': conn.pid,
                                'process_name': process.name() if process else 'Unknown',
                                'reason': reason
                            })
                        except:
                            suspicious_connections.append({
                                'local_addr': f"{conn.laddr.ip}:{conn.laddr.port}",
                                'remote_addr': f"{remote_ip}:{conn.raddr.port}",
                                'status': conn.status,
                                'pid': conn.pid,
                                'process_name': 'Unknown',
                                'reason': reason
                            })
                            
        except Exception as e:
            print(f"Error verificando conexiones: {e}")
            
        return suspicious_connections
    
    def _is_local_ip(self, ip: str) -> bool:
        """Verifica si una IP es local/privada"""
        local_ranges = [
            '127.', '10.', '192.168.', '172.16.', '172.17.', '172.18.',
            '172.19.', '172.20.', '172.21.', '172.22.', '172.23.',
            '172.24.', '172.25.', '172.26.', '172.27.', '172.28.',
            '172.29.', '172.30.', '172.31.'
        ]
        return any(ip.startswith(prefix) for prefix in local_ranges)
    
    def create_forensic_snapshot(self, anomaly_result: Dict, threat_info: Dict) -> str:
        """Crea snapshot forense del estado actual"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_file = os.path.join(self.quarantine_dir, f"forensic_snapshot_{timestamp}.json")
        
        try:
            # Collect system state
            snapshot_data = {
                'timestamp': timestamp,
                'anomaly_result': anomaly_result,
                'threat_info': threat_info,
                'system_info': {
                    'cpu_count': psutil.cpu_count(),
                    'memory_total': psutil.virtual_memory().total,
                    'boot_time': psutil.boot_time(),
                    'users': [user._asdict() for user in psutil.users()]
                },
                'running_processes': [],
                'network_connections': [],
                'system_load': {
                    'cpu_percent': psutil.cpu_percent(interval=1),
                    'memory': psutil.virtual_memory()._asdict(),
                    'disk': psutil.disk_usage('/')._asdict()
                }
            }
            
            # Get running processes
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'cmdline']):
                try:
                    snapshot_data['running_processes'].append(proc.info)
                except:
                    continue
            
            # Get network connections
            for conn in psutil.net_connections():
                try:
                    snapshot_data['network_connections'].append({
                        'laddr': conn.laddr._asdict() if conn.laddr else None,
                        'raddr': conn.raddr._asdict() if conn.raddr else None,
                        'status': conn.status,
                        'pid': conn.pid
                    })
                except:
                    continue
            
            # Save snapshot
            with open(snapshot_file, 'w') as f:
                json.dump(snapshot_data, f, indent=2, default=str)
                
            print(f"📸 Snapshot forense creado: {snapshot_file}")
            return snapshot_file
            
        except Exception as e:
            print(f"Error creando snapshot: {e}")
            return ""

class ResponseOrchestrator:
    """Orquesta la respuesta completa a incidentes de seguridad"""
    
    def __init__(self):
        self.threat_response = ThreatResponse()
        self.incident_analyzer = IncidentAnalyzer()
        self.action_executor = ActionExecutor(self.threat_response.quarantine_dir)
    
    def handle_security_incident(self, anomaly_result: Dict) -> Dict:
        """Maneja un incidente de seguridad completo"""
        print(f"\n{'='*70}")
        print(f"🚨 INCIDENTE DE SEGURIDAD DETECTADO")
        print(f"{'='*70}")
        
        # 1. Clasificar amenaza
        threat_info = self.incident_analyzer.classify_threat(anomaly_result)
        
        print(f"🔍 ANÁLISIS DE AMENAZA:")
        print(f"   Tipo: {threat_info['threat_type']}")
        print(f"   Confianza: {threat_info['confidence']}%")
        print(f"   Indicadores:")
        for indicator in threat_info['indicators']:
            print(f"     • {indicator}")
        
        # 2. Crear snapshot forense
        if self.threat_response.response_config['user_preferences']['create_forensic_snapshot']:
            snapshot_file = self.action_executor.create_forensic_snapshot(anomaly_result, threat_info)
        
        # 3. Ejecutar análisis específico
        analysis_results = self._execute_analysis_actions(threat_info['recommended_actions'])
        
        # 4. Presentar opciones al usuario
        response_options = self._generate_response_options(threat_info, analysis_results)
        
        # 5. Ejecutar respuesta
        if anomaly_result.get('severity') == 'critical':
            print(f"\n⚠️  RESPUESTA AUTOMÁTICA (SEVERIDAD CRÍTICA)")
            selected_actions = response_options['automatic_actions']
        else:
            print(f"\n🔧 OPCIONES DE RESPUESTA DISPONIBLES:")
            for i, option in enumerate(response_options['user_options'], 1):
                print(f"   {i}️⃣  {option['name']}: {option['description']}")
            
            print(f"   A️⃣  Ejecutar todas las acciones recomendadas")
            print(f"   I️⃣  Ignorar (solo registrar)")
            print(f"   Q️⃣  Cuarentena automática")
            print(f"   E️⃣  Análisis extendido")
            
            try:
                choice = input(f"\n🎯 Selecciona acción (1-{len(response_options['user_options'])}/A/I/Q/E): ").strip().upper()
                selected_actions = self._process_user_choice(choice, response_options)
            except KeyboardInterrupt:
                print(f"\n👋 Cancelado por usuario")
                selected_actions = ['log_incident']
        
        # 6. Ejecutar acciones seleccionadas
        execution_results = self._execute_response_actions(selected_actions, threat_info, analysis_results)
        
        # 7. Generar reporte
        incident_report = {
            'timestamp': datetime.now().isoformat(),
            'anomaly_result': anomaly_result,
            'threat_info': threat_info,
            'analysis_results': analysis_results,
            'actions_executed': selected_actions,
            'execution_results': execution_results,
            'snapshot_file': snapshot_file if 'snapshot_file' in locals() else None
        }
        
        self._save_incident_report(incident_report)
        
        print(f"\n✅ INCIDENTE PROCESADO")
        print(f"📊 Acciones ejecutadas: {len(selected_actions)}")
        print(f"📁 Reporte guardado en: smartcompute_incidents.json")
        print(f"{'='*70}")
        
        return incident_report
    
    def _execute_analysis_actions(self, recommended_actions: List[str]) -> Dict:
        """Ejecuta acciones de análisis recomendadas"""
        results = {}
        
        for action in recommended_actions:
            try:
                if action == 'identify_mining_processes':
                    results[action] = self.action_executor.identify_mining_processes()
                elif action == 'list_suspicious_processes':
                    results[action] = self.action_executor.list_suspicious_processes()
                elif action == 'check_network_connections':
                    results[action] = self.action_executor.check_network_connections()
                # Agregar más acciones según necesidad
                    
            except Exception as e:
                results[action] = {'error': str(e)}
                
        return results
    
    def _generate_response_options(self, threat_info: Dict, analysis_results: Dict) -> Dict:
        """Genera opciones de respuesta basándose en el análisis"""
        user_options = []
        automatic_actions = ['log_incident']
        
        if threat_info['threat_type'] == 'crypto_mining':
            user_options.extend([
                {
                    'name': 'Terminar procesos sospechosos',
                    'description': 'Finalizar procesos identificados como minería',
                    'action': 'terminate_mining_processes',
                    'risk': 'medium'
                },
                {
                    'name': 'Bloquear conexiones',
                    'description': 'Bloquear conexiones de red sospechosas',
                    'action': 'block_suspicious_connections',
                    'risk': 'low'
                }
            ])
            
        elif threat_info['threat_type'] == 'process_spawning':
            user_options.extend([
                {
                    'name': 'Analizar árbol de procesos',
                    'description': 'Investigar procesos padre e hijos',
                    'action': 'analyze_process_tree',
                    'risk': 'low'
                },
                {
                    'name': 'Cuarentena procesos',
                    'description': 'Mover ejecutables sospechosos a cuarentena',
                    'action': 'quarantine_processes',
                    'risk': 'high'
                }
            ])
        
        # Opciones comunes
        user_options.extend([
            {
                'name': 'Escaneo antivirus',
                'description': 'Ejecutar escaneo completo del sistema',
                'action': 'run_antivirus_scan',
                'risk': 'low'
            },
            {
                'name': 'Aislar sistema',
                'description': 'Desconectar de la red temporalmente',
                'action': 'isolate_network',
                'risk': 'high'
            }
        ])
        
        return {
            'user_options': user_options,
            'automatic_actions': automatic_actions
        }
    
    def _process_user_choice(self, choice: str, response_options: Dict) -> List[str]:
        """Procesa la elección del usuario"""
        if choice == 'A':
            return [opt['action'] for opt in response_options['user_options']]
        elif choice == 'I':
            return ['log_incident']
        elif choice == 'Q':
            return ['quarantine_processes', 'log_incident']
        elif choice == 'E':
            return ['extended_analysis', 'log_incident']
        elif choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(response_options['user_options']):
                return [response_options['user_options'][index]['action']]
        
        return ['log_incident']
    
    def _execute_response_actions(self, actions: List[str], threat_info: Dict, analysis_results: Dict) -> Dict:
        """Ejecuta las acciones de respuesta seleccionadas"""
        results = {}
        
        for action in actions:
            try:
                print(f"   🔧 Ejecutando: {action}")
                
                if action == 'log_incident':
                    results[action] = {'status': 'logged', 'message': 'Incidente registrado'}
                    
                elif action == 'terminate_mining_processes':
                    terminated = []
                    if 'identify_mining_processes' in analysis_results:
                        for proc in analysis_results['identify_mining_processes'][:3]:  # Solo primeros 3
                            try:
                                psutil.Process(proc['pid']).terminate()
                                terminated.append(proc['pid'])
                            except:
                                pass
                    results[action] = {'terminated_pids': terminated}
                
                elif action == 'run_antivirus_scan':
                    # Simular - en implementación real ejecutaría antivirus
                    results[action] = {
                        'status': 'scheduled',
                        'message': 'Escaneo antivirus programado'
                    }
                
                elif action == 'isolate_network':
                    # Simular - en implementación real desconectaría red
                    results[action] = {
                        'status': 'simulated',
                        'message': 'Aislamiento de red simulado'
                    }
                
                else:
                    results[action] = {'status': 'not_implemented'}
                    
                time.sleep(1)  # Simular tiempo de ejecución
                
            except Exception as e:
                results[action] = {'error': str(e)}
        
        return results
    
    def _save_incident_report(self, report: Dict):
        """Guarda reporte del incidente"""
        incidents_file = "smartcompute_incidents.json"
        
        try:
            if os.path.exists(incidents_file):
                with open(incidents_file, 'r') as f:
                    incidents = json.load(f)
            else:
                incidents = []
            
            incidents.append(report)
            
            with open(incidents_file, 'w') as f:
                json.dump(incidents, f, indent=2, default=str)
                
        except Exception as e:
            print(f"Error guardando reporte: {e}")

def demo_response_system():
    """Demo del sistema de respuesta a incidentes"""
    print("="*70)
    print("🚨 SMARTCOMPUTE RESPONSE SYSTEM - DEMO")
    print("💡 Automated Incident Response")
    print("🎯 Ethical Hacker Approach: Intelligent Response")
    print("="*70)
    
    # Simular anomalía detectada
    simulated_anomaly = {
        'score': 85.0,
        'severity': 'high',
        'anomalies': {
            'gpu_anomaly': {
                'current': 99.5,
                'baseline': 30.2,
                'zscore': 4.2,
                'severity': 'high'
            },
            'cpu_anomaly': {
                'current': 95.8,
                'baseline': 15.1,
                'zscore': 3.8,
                'severity': 'high'
            }
        },
        'timestamp': time.time()
    }
    
    # Crear orquestador y manejar incidente
    orchestrator = ResponseOrchestrator()
    incident_report = orchestrator.handle_security_incident(simulated_anomaly)
    
    return incident_report

if __name__ == "__main__":
    demo_response_system()
