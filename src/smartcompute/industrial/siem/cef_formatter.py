#!/usr/bin/env python3
"""
SmartCompute SIEM Integration - CEF Formatter
Genera eventos en formato CEF (Common Event Format) para integración con SIEMs
Compatible con: Splunk, QRadar, ArcSight, LogRhythm
"""

import time
import json
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum

class CEFSeverity(Enum):
    """Niveles de severidad CEF estándar"""
    LOW = 0
    MEDIUM = 5
    HIGH = 8
    CRITICAL = 10

class SmartComputeCEFFormatter:
    """Formateador de eventos SmartCompute a formato CEF para SIEMs"""
    
    def __init__(self, vendor="SmartCompute", product="PerformanceMonitor", version="1.0"):
        self.vendor = vendor
        self.product = product  
        self.version = version
        self.device_host = "smartcompute-sensor"
        
    def format_anomaly_event(self, anomaly_data: Dict[str, Any]) -> str:
        """
        Convierte una anomalía detectada por SmartCompute a formato CEF
        
        Args:
            anomaly_data: Datos de la anomalía detectada
            
        Returns:
            String en formato CEF listo para enviar al SIEM
        """
        
        # Extraer información clave
        severity = self._calculate_cef_severity(anomaly_data.get('risk_score', 0))
        signature_id = f"SC_{anomaly_data.get('anomaly_type', 'UNKNOWN').upper()}"
        event_name = f"SmartCompute {anomaly_data.get('anomaly_type', 'Anomaly')} Detection"
        
        # CEF Header: CEF:Version|Device Vendor|Device Product|Device Version|Signature ID|Name|Severity|
        cef_header = f"CEF:0|{self.vendor}|{self.product}|{self.version}|{signature_id}|{event_name}|{severity.value}"
        
        # CEF Extensions - Campos adicionales con datos de SmartCompute
        extensions = []
        
        # Información temporal
        if 'timestamp' in anomaly_data:
            extensions.append(f"rt={int(anomaly_data['timestamp'] * 1000)}")  # Tiempo en ms
        else:
            extensions.append(f"rt={int(time.time() * 1000)}")
            
        # Información del host/dispositivo
        if 'source_host' in anomaly_data:
            extensions.append(f"dhost={anomaly_data['source_host']}")
        else:
            extensions.append(f"dhost={self.device_host}")
            
        # Datos específicos de SmartCompute
        if 'cpu_usage' in anomaly_data:
            extensions.append(f"cs1={anomaly_data['cpu_usage']}")
            extensions.append("cs1Label=CPU_Usage_Percent")
            
        if 'memory_usage' in anomaly_data:
            extensions.append(f"cs2={anomaly_data['memory_usage']}")  
            extensions.append("cs2Label=Memory_Usage_Percent")
            
        if 'performance_impact' in anomaly_data:
            extensions.append(f"cs3={anomaly_data['performance_impact']}")
            extensions.append("cs3Label=Performance_Impact_Score")
            
        # Risk Score de SmartCompute
        if 'risk_score' in anomaly_data:
            extensions.append(f"cs4={anomaly_data['risk_score']}")
            extensions.append("cs4Label=SmartCompute_Risk_Score")
            
        # Detalles del método de detección
        if 'detection_method' in anomaly_data:
            extensions.append(f"cs5={anomaly_data['detection_method']}")
            extensions.append("cs5Label=Detection_Method")
            
        # Mensaje descriptivo
        msg = anomaly_data.get('description', f"Anomaly detected: {anomaly_data.get('anomaly_type', 'Unknown')}")
        extensions.append(f'msg={msg}')
        
        # IP si está disponible
        if 'source_ip' in anomaly_data:
            extensions.append(f"src={anomaly_data['source_ip']}")
            
        # Puerto si está disponible  
        if 'source_port' in anomaly_data:
            extensions.append(f"spt={anomaly_data['source_port']}")
            
        # Protocolo si está disponible
        if 'protocol' in anomaly_data:
            extensions.append(f"proto={anomaly_data['protocol']}")
            
        # Categoría de amenaza
        if 'threat_category' in anomaly_data:
            extensions.append(f"cat={anomaly_data['threat_category']}")
        else:
            extensions.append("cat=Performance Anomaly")
            
        # Ensamblar evento CEF completo
        cef_extensions = " ".join(extensions)
        cef_event = f"{cef_header}|{cef_extensions}"
        
        return cef_event
    
    def format_performance_event(self, perf_data: Dict[str, Any]) -> str:
        """
        Convierte métricas de performance a formato CEF para correlación SIEM
        """
        
        severity = CEFSeverity.LOW  # Performance events son típicamente informativos
        signature_id = "SC_PERFORMANCE_METRIC"
        event_name = "SmartCompute Performance Baseline"
        
        cef_header = f"CEF:0|{self.vendor}|{self.product}|{self.version}|{signature_id}|{event_name}|{severity.value}"
        
        extensions = []
        extensions.append(f"rt={int(time.time() * 1000)}")
        extensions.append(f"dhost={perf_data.get('hostname', self.device_host)}")
        
        # Métricas de SmartCompute como campos personalizados
        if 'execution_time' in perf_data:
            extensions.append(f"cs1={perf_data['execution_time']}")
            extensions.append("cs1Label=Execution_Time_Seconds")
            
        if 'method_used' in perf_data:
            extensions.append(f"cs2={perf_data['method_used']}")
            extensions.append("cs2Label=Optimization_Method")
            
        if 'precision_achieved' in perf_data:
            extensions.append(f"cs3={perf_data['precision_achieved']}")
            extensions.append("cs3Label=Precision_Percentage")
            
        if 'speedup' in perf_data:
            extensions.append(f"cs4={perf_data['speedup']}")
            extensions.append("cs4Label=Performance_Speedup")
            
        msg = f"Performance baseline: {perf_data.get('method_used', 'unknown')} method"
        extensions.append(f'msg={msg}')
        extensions.append("cat=Performance Baseline")
        
        cef_extensions = " ".join(extensions)
        return f"{cef_header}|{cef_extensions}"
    
    def _calculate_cef_severity(self, risk_score: float) -> CEFSeverity:
        """Convierte SmartCompute risk score a severidad CEF"""
        if risk_score >= 0.9:
            return CEFSeverity.CRITICAL
        elif risk_score >= 0.7:
            return CEFSeverity.HIGH  
        elif risk_score >= 0.4:
            return CEFSeverity.MEDIUM
        else:
            return CEFSeverity.LOW
    
    def create_sample_events(self) -> list:
        """Genera eventos de ejemplo para testing"""
        
        sample_anomaly = {
            'timestamp': time.time(),
            'anomaly_type': 'cpu_spike',
            'source_host': 'web-server-01',
            'source_ip': '192.168.1.100',
            'cpu_usage': 95.5,
            'memory_usage': 78.2,
            'risk_score': 0.85,
            'detection_method': 'statistical_analysis',
            'performance_impact': 0.72,
            'description': 'Unusual CPU spike detected - potential DoS attack or resource exhaustion',
            'threat_category': 'Resource Exhaustion'
        }
        
        sample_performance = {
            'hostname': 'compute-node-02',
            'execution_time': 0.0245,
            'method_used': 'Multi-thread (Rápido)',
            'precision_achieved': 0.987,
            'speedup': 3.2
        }
        
        events = []
        events.append(self.format_anomaly_event(sample_anomaly))
        events.append(self.format_performance_event(sample_performance))
        
        return events

def demo_cef_formatting():
    """Demo de formateo CEF"""
    print("🔧 SmartCompute CEF Formatter Demo")
    print("=" * 50)
    
    formatter = SmartComputeCEFFormatter()
    sample_events = formatter.create_sample_events()
    
    for i, event in enumerate(sample_events, 1):
        print(f"\n📤 Evento CEF #{i}:")
        print("-" * 40)
        print(event)
        print(f"📏 Longitud: {len(event)} caracteres")
    
    print(f"\n✅ {len(sample_events)} eventos generados")
    print("📡 Listos para enviar a cualquier SIEM compatible con CEF")
    print("🎯 Formatos soportados: Splunk, QRadar, ArcSight, LogRhythm")

if __name__ == "__main__":
    demo_cef_formatting()