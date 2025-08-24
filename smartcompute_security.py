#!/usr/bin/env python3
"""
SmartCompute Security - Performance Anomaly Detection
¡Tu concepto revolucionario de detección basada en performance!

Combina optimización CPU/GPU con detección de anomalías de seguridad
Ethical Hacker approach: No-intrusive, behavior-based detection
"""

import numpy as np
import time
import json
import os
import psutil
import threading
from datetime import datetime, timedelta
from collections import deque
from typing import Dict, List, Tuple, Any
import hashlib

class SecurityBaseline:
    """Establece y mantiene baseline de performance normal del sistema"""
    
    def __init__(self):
        self.baseline_file = "smartcompute_baseline.json"
        self.baseline_data = self.load_baseline()
        self.collection_window = deque(maxlen=100)  # Últimas 100 mediciones
        
    def load_baseline(self) -> Dict:
        if os.path.exists(self.baseline_file):
            with open(self.baseline_file, 'r') as f:
                return json.load(f)
        return {
            'cpu_patterns': {},
            'gpu_patterns': {},
            'system_patterns': {},
            'established': False,
            'created_at': time.time(),
            'measurements': 0
        }
    
    def save_baseline(self):
        with open(self.baseline_file, 'w') as f:
            json.dump(self.baseline_data, f, indent=2)
    
    def collect_system_metrics(self) -> Dict:
        """Recolecta métricas completas del sistema"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_freq = psutil.cpu_freq()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network I/O
            net_io = psutil.net_io_counters()
            
            # Process count y threads
            process_count = len(psutil.pids())
            
            metrics = {
                'timestamp': time.time(),
                'cpu_percent': cpu_percent,
                'cpu_freq': cpu_freq.current if cpu_freq else 0,
                'memory_percent': memory.percent,
                'memory_used': memory.used,
                'disk_percent': disk.percent,
                'network_bytes_sent': net_io.bytes_sent,
                'network_bytes_recv': net_io.bytes_recv,
                'process_count': process_count,
                'load_avg': os.getloadavg()[0] if hasattr(os, 'getloadavg') else 0
            }
            
            # GPU metrics si está disponible
            try:
                import cupy as cp
                device = cp.cuda.Device(0)
                mem_info = device.mem_info
                metrics.update({
                    'gpu_memory_used': mem_info[0],
                    'gpu_memory_total': mem_info[1],
                    'gpu_memory_percent': (mem_info[0] / mem_info[1]) * 100
                })
            except:
                metrics.update({
                    'gpu_memory_used': 0,
                    'gpu_memory_total': 0,
                    'gpu_memory_percent': 0
                })
            
            return metrics
            
        except Exception as e:
            print(f"Error collecting metrics: {e}")
            return {}
    
    def establish_baseline(self, duration_minutes: int = 5):
        """Establece baseline durante periodo de actividad normal"""
        print(f"🔒 Estableciendo baseline de seguridad ({duration_minutes} minutos)")
        print("   ⚠️  Usar sistema NORMALMENTE durante este tiempo")
        print("   ⚠️  NO ejecutar software sospechoso")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        measurements = []
        
        while time.time() < end_time:
            metrics = self.collect_system_metrics()
            if metrics:
                measurements.append(metrics)
                remaining = int(end_time - time.time())
                print(f"   📊 Recolectando... {remaining}s restantes")
            time.sleep(5)  # Cada 5 segundos
        
        # Calcular estadísticas baseline
        if measurements:
            self.baseline_data = self.calculate_baseline_stats(measurements)
            self.baseline_data['established'] = True
            self.baseline_data['measurements'] = len(measurements)
            self.save_baseline()
            
            print(f"✅ Baseline establecido con {len(measurements)} mediciones")
            print(f"📊 CPU promedio: {self.baseline_data['cpu_patterns']['mean']:.1f}%")
            print(f"🧠 Memoria promedio: {self.baseline_data['system_patterns']['memory_mean']:.1f}%")
            print(f"💾 Baseline guardado en: {self.baseline_file}")
        else:
            print("❌ Error: No se pudieron recolectar mediciones")
    
    def calculate_baseline_stats(self, measurements: List[Dict]) -> Dict:
        """Calcula estadísticas baseline de las mediciones"""
        # Extraer arrays de cada métrica
        cpu_data = [m['cpu_percent'] for m in measurements if m.get('cpu_percent')]
        memory_data = [m['memory_percent'] for m in measurements if m.get('memory_percent')]
        gpu_memory_data = [m['gpu_memory_percent'] for m in measurements if m.get('gpu_memory_percent')]
        process_data = [m['process_count'] for m in measurements if m.get('process_count')]
        load_data = [m['load_avg'] for m in measurements if m.get('load_avg')]
        
        return {
            'cpu_patterns': {
                'mean': float(np.mean(cpu_data)) if cpu_data else 0,
                'std': float(np.std(cpu_data)) if cpu_data else 0,
                'min': float(np.min(cpu_data)) if cpu_data else 0,
                'max': float(np.max(cpu_data)) if cpu_data else 0,
                'percentile_95': float(np.percentile(cpu_data, 95)) if cpu_data else 0
            },
            'gpu_patterns': {
                'memory_mean': float(np.mean(gpu_memory_data)) if gpu_memory_data else 0,
                'memory_std': float(np.std(gpu_memory_data)) if gpu_memory_data else 0,
                'memory_max': float(np.max(gpu_memory_data)) if gpu_memory_data else 0
            },
            'system_patterns': {
                'memory_mean': float(np.mean(memory_data)) if memory_data else 0,
                'memory_std': float(np.std(memory_data)) if memory_data else 0,
                'process_mean': float(np.mean(process_data)) if process_data else 0,
                'process_std': float(np.std(process_data)) if process_data else 0,
                'load_mean': float(np.mean(load_data)) if load_data else 0,
                'load_std': float(np.std(load_data)) if load_data else 0
            },
            'established': True,
            'created_at': time.time(),
            'measurements': len(measurements)
        }

class AnomalyDetector:
    """Detecta anomalías de seguridad basándose en patrones de performance"""
    
    def __init__(self, baseline: SecurityBaseline):
        self.baseline = baseline
        self.alerts = []
        self.monitoring = False
        
    def calculate_anomaly_score(self, current_metrics: Dict) -> Dict:
        """Calcula score de anomalía comparando con baseline"""
        if not self.baseline.baseline_data['established']:
            return {'score': 0, 'details': 'Baseline no establecido'}
        
        baseline = self.baseline.baseline_data
        anomalies = {}
        total_score = 0
        
        # CPU Anomaly Detection
        if 'cpu_percent' in current_metrics:
            cpu_current = current_metrics['cpu_percent']
            cpu_baseline = baseline['cpu_patterns']['mean']
            cpu_std = baseline['cpu_patterns']['std']
            
            # Z-score para detectar desviaciones
            if cpu_std > 0:
                cpu_zscore = abs(cpu_current - cpu_baseline) / cpu_std
                if cpu_zscore > 2.5:  # Más de 2.5 desviaciones estándar
                    anomalies['cpu_anomaly'] = {
                        'current': cpu_current,
                        'baseline': cpu_baseline,
                        'zscore': cpu_zscore,
                        'severity': 'high' if cpu_zscore > 3.5 else 'medium'
                    }
                    total_score += min(cpu_zscore * 10, 50)
        
        # GPU Memory Anomaly Detection
        if 'gpu_memory_percent' in current_metrics:
            gpu_current = current_metrics['gpu_memory_percent']
            gpu_baseline = baseline['gpu_patterns']['memory_mean']
            gpu_std = baseline['gpu_patterns']['memory_std']
            
            if gpu_std > 0:
                gpu_zscore = abs(gpu_current - gpu_baseline) / gpu_std
                if gpu_zscore > 2.0:  # GPU más sensible
                    anomalies['gpu_anomaly'] = {
                        'current': gpu_current,
                        'baseline': gpu_baseline,
                        'zscore': gpu_zscore,
                        'severity': 'high' if gpu_zscore > 3.0 else 'medium'
                    }
                    total_score += min(gpu_zscore * 15, 60)
        
        # Process Count Anomaly
        if 'process_count' in current_metrics:
            proc_current = current_metrics['process_count']
            proc_baseline = baseline['system_patterns']['process_mean']
            proc_std = baseline['system_patterns']['process_std']
            
            if proc_std > 0:
                proc_zscore = abs(proc_current - proc_baseline) / proc_std
                if proc_zscore > 2.0:
                    anomalies['process_anomaly'] = {
                        'current': proc_current,
                        'baseline': proc_baseline,
                        'zscore': proc_zscore,
                        'severity': 'medium' if proc_zscore < 3.0 else 'high'
                    }
                    total_score += min(proc_zscore * 8, 40)
        
        # Memory Anomaly Detection
        if 'memory_percent' in current_metrics:
            mem_current = current_metrics['memory_percent']
            mem_baseline = baseline['system_patterns']['memory_mean']
            mem_std = baseline['system_patterns']['memory_std']
            
            if mem_std > 0:
                mem_zscore = abs(mem_current - mem_baseline) / mem_std
                if mem_zscore > 2.5:
                    anomalies['memory_anomaly'] = {
                        'current': mem_current,
                        'baseline': mem_baseline,
                        'zscore': mem_zscore,
                        'severity': 'high' if mem_zscore > 4.0 else 'medium'
                    }
                    total_score += min(mem_zscore * 12, 48)
        
        return {
            'score': min(total_score, 100),  # Cap at 100
            'anomalies': anomalies,
            'timestamp': time.time(),
            'severity': self.get_severity_level(total_score)
        }
    
    def get_severity_level(self, score: float) -> str:
        """Convierte score numérico a nivel de severidad"""
        if score >= 70:
            return 'critical'
        elif score >= 50:
            return 'high'
        elif score >= 25:
            return 'medium'
        elif score >= 10:
            return 'low'
        else:
            return 'normal'
    
    def generate_alert(self, anomaly_result: Dict):
        """Genera alerta de seguridad basada en anomalías"""
        if anomaly_result['score'] >= 25:  # Solo alertar scores significativos
            alert = {
                'timestamp': datetime.now().isoformat(),
                'score': anomaly_result['score'],
                'severity': anomaly_result['severity'],
                'anomalies': anomaly_result['anomalies'],
                'recommendations': self.get_recommendations(anomaly_result)
            }
            
            self.alerts.append(alert)
            return alert
        
        return None
    
    def get_recommendations(self, anomaly_result: Dict) -> List[str]:
        """Genera recomendaciones basadas en anomalías detectadas"""
        recommendations = []
        
        for anomaly_type, details in anomaly_result['anomalies'].items():
            if anomaly_type == 'cpu_anomaly':
                recommendations.append("🔍 Revisar procesos con alto uso de CPU")
                recommendations.append("⚠️  Posible crypto mining o botnet activity")
                
            elif anomaly_type == 'gpu_anomaly':
                recommendations.append("🎮 Verificar uso anómalo de GPU")
                recommendations.append("💰 Posible cryptocurrency mining malware")
                
            elif anomaly_type == 'process_anomaly':
                recommendations.append("📊 Revisar procesos ejecutándose")
                recommendations.append("🦠 Posible malware spawning processes")
                
            elif anomaly_type == 'memory_anomaly':
                recommendations.append("🧠 Analizar uso de memoria inusual")
                recommendations.append("💾 Posible memory leak o data exfiltration")
        
        if anomaly_result['severity'] in ['high', 'critical']:
            recommendations.append("🚨 ACCIÓN INMEDIATA: Ejecutar antivirus completo")
            recommendations.append("🔒 Considerar desconectar de red temporalmente")
        
        return recommendations

class SmartComputeSecure:
    """SmartCompute con capacidades de seguridad integradas"""
    
    def __init__(self, security_enabled: bool = True):
        # Core SmartCompute (tu código original)
        self.cpu_cores = os.cpu_count()
        self.gpu_available = self.check_gpu()
        
        # Security Module (nuevo)
        self.security_enabled = security_enabled
        if security_enabled:
            self.baseline = SecurityBaseline()
            self.anomaly_detector = AnomalyDetector(self.baseline)
            self.security_monitoring = False
        
        print(f"🚀 SmartCompute Secure iniciado")
        print(f"⚙️  CPU: {self.cpu_cores} cores")
        print(f"🎮 GPU: {'Disponible' if self.gpu_available else 'No disponible'}")
        print(f"🔒 Security: {'Habilitado' if security_enabled else 'Deshabilitado'}")
    
    def check_gpu(self) -> bool:
        try:
            import cupy as cp
            cp.array([1, 2, 3])
            return True
        except:
            return False
    
    def establish_security_baseline(self, duration_minutes: int = 5):
        """Establece baseline de seguridad"""
        if not self.security_enabled:
            print("❌ Security module no habilitado")
            return
        
        self.baseline.establish_baseline(duration_minutes)
    
    def start_security_monitoring(self):
        """Inicia monitoreo continuo de seguridad"""
        if not self.security_enabled:
            print("❌ Security module no habilitado")
            return
        
        if not self.baseline.baseline_data['established']:
            print("⚠️  Baseline no establecido. Ejecuta establish_security_baseline() primero")
            return
        
        self.security_monitoring = True
        self.monitor_thread = threading.Thread(target=self._security_monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("🔒 Monitoreo de seguridad INICIADO")
        print("   📊 Análisis cada 30 segundos")
        print("   🚨 Alertas automáticas para anomalías")
    
    def stop_security_monitoring(self):
        """Detiene monitoreo de seguridad"""
        self.security_monitoring = False
        print("🔒 Monitoreo de seguridad DETENIDO")
    
    def _security_monitor_loop(self):
        """Loop de monitoreo continuo (thread separado)"""
        while self.security_monitoring:
            try:
                # Recolectar métricas actuales
                current_metrics = self.baseline.collect_system_metrics()
                
                if current_metrics:
                    # Analizar anomalías
                    anomaly_result = self.anomaly_detector.calculate_anomaly_score(current_metrics)
                    
                    # Generar alertas si es necesario
                    alert = self.anomaly_detector.generate_alert(anomaly_result)
                    
                    if alert:
                        self._print_security_alert(alert)
                
                time.sleep(30)  # Monitorear cada 30 segundos
                
            except Exception as e:
                print(f"Error en monitoreo: {e}")
                time.sleep(30)
    
    def _print_security_alert(self, alert: Dict):
        """Imprime alerta de seguridad formateada"""
        print("\n" + "="*60)
        print(f"🚨 ALERTA DE SEGURIDAD - {alert['severity'].upper()}")
        print("="*60)
        print(f"⏰ Tiempo: {alert['timestamp']}")
        print(f"📊 Score: {alert['score']:.1f}/100")
        
        for anomaly_type, details in alert['anomalies'].items():
            print(f"\n🔍 {anomaly_type.upper()}:")
            print(f"   Actual: {details['current']:.1f}")
            print(f"   Baseline: {details['baseline']:.1f}")
            print(f"   Severidad: {details['severity']}")
        
        print(f"\n💡 RECOMENDACIONES:")
        for rec in alert['recommendations']:
            print(f"   {rec}")
        
        print("="*60 + "\n")
    
    def get_security_status(self) -> Dict:
        """Obtiene estado actual de seguridad"""
        if not self.security_enabled:
            return {'security_enabled': False}
        
        return {
            'security_enabled': True,
            'baseline_established': self.baseline.baseline_data['established'],
            'monitoring_active': self.security_monitoring,
            'total_alerts': len(self.anomaly_detector.alerts),
            'recent_alerts': len([a for a in self.anomaly_detector.alerts 
                                if time.time() - time.mktime(time.strptime(a['timestamp'][:19], 
                                "%Y-%m-%dT%H:%M:%S")) < 3600])  # Últimas 24 horas
        }
    
    def security_demo(self):
        """Demo del sistema de seguridad"""
        print("🔒 SmartCompute Security Demo")
        print("="*50)
        
        if not self.security_enabled:
            print("❌ Security no habilitado")
            return
        
        if not self.baseline.baseline_data['established']:
            print("📊 Estableciendo baseline rápido (30 segundos)...")
            print("   ⚠️  Mantén actividad normal del sistema")
            
            # Baseline rápido para demo
            measurements = []
            for i in range(6):  # 6 mediciones de 5 segundos cada una
                metrics = self.baseline.collect_system_metrics()
                if metrics:
                    measurements.append(metrics)
                print(f"   Medición {i+1}/6...")
                time.sleep(5)
            
            if measurements:
                self.baseline.baseline_data = self.baseline.calculate_baseline_stats(measurements)
                self.baseline.save_baseline()
                print("✅ Baseline establecido para demo")
        
        # Mostrar status actual
        print(f"\n📊 ANÁLISIS ACTUAL:")
        current_metrics = self.baseline.collect_system_metrics()
        if current_metrics:
            anomaly_result = self.anomaly_detector.calculate_anomaly_score(current_metrics)
            
            print(f"   Score de anomalía: {anomaly_result['score']:.1f}/100")
            print(f"   Nivel de severidad: {anomaly_result['severity']}")
            print(f"   CPU: {current_metrics['cpu_percent']:.1f}%")
            print(f"   Memoria: {current_metrics['memory_percent']:.1f}%")
            print(f"   GPU Memoria: {current_metrics['gpu_memory_percent']:.1f}%")
            
            if anomaly_result['score'] > 10:
                print(f"\n⚠️  ANOMALÍAS DETECTADAS:")
                for anomaly_type, details in anomaly_result['anomalies'].items():
                    print(f"   {anomaly_type}: {details['severity']}")
            else:
                print(f"\n✅ Sistema funcionando dentro de parámetros normales")
        
        print("\n💡 Para monitoreo continuo: start_security_monitoring()")

def demo_smartcompute_security():
    """Demo completo del sistema de seguridad"""
    print("="*70)
    print("🔒 SMARTCOMPUTE SECURITY - TU CONCEPTO REVOLUCIONARIO")
    print("💡 Performance-Based Anomaly Detection")
    print("🎯 Ethical Hacker Approach: Non-intrusive Security")
    print("="*70)
    
    # Crear instancia con security habilitado
    sc = SmartComputeSecure(security_enabled=True)
    
    print(f"\n🔍 ¿Qué opción quieres probar?")
    print(f"1️⃣  Demo rápido (análisis actual)")
    print(f"2️⃣  Establecer baseline completo (5 minutos)")
    print(f"3️⃣  Iniciar monitoreo continuo")
    print(f"4️⃣  Ver estado de seguridad")
    
    try:
        choice = input("\nElige opción (1-4): ").strip()
        
        if choice == '1':
            sc.security_demo()
        elif choice == '2':
            sc.establish_security_baseline(5)
        elif choice == '3':
            sc.start_security_monitoring()
            print("Presiona Ctrl+C para detener...")
            while True:
                time.sleep(1)
        elif choice == '4':
            status = sc.get_security_status()
            print(f"\n📊 ESTADO DE SEGURIDAD:")
            for key, value in status.items():
                print(f"   {key}: {value}")
        else:
            sc.security_demo()
            
    except KeyboardInterrupt:
        print(f"\n👋 SmartCompute Security finalizado")
        sc.stop_security_monitoring()

if __name__ == "__main__":
    demo_smartcompute_security()
