#!/usr/bin/env python3
"""
SmartCompute Splunk Integration
Conector para enviar eventos SmartCompute directamente a Splunk via HTTP Event Collector (HEC)
"""

import requests
import json
import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
try:
    from .cef_formatter import SmartComputeCEFFormatter
except ImportError:
    from cef_formatter import SmartComputeCEFFormatter

class SplunkConnector:
    """Conector para integración con Splunk HTTP Event Collector"""
    
    def __init__(self, splunk_host: str, hec_token: str, index: str = "smartcompute", 
                 source: str = "smartcompute", sourcetype: str = "cef", use_ssl: bool = True,
                 verify_ssl: bool = True, hec_port: int = 8088):
        """
        Inicializar conector Splunk
        
        Args:
            splunk_host: Hostname/IP del servidor Splunk
            hec_token: Token del HTTP Event Collector  
            index: Índice Splunk donde enviar eventos
            source: Campo source para eventos
            sourcetype: Sourcetype para parsing (cef recomendado)
            use_ssl: Usar HTTPS
            verify_ssl: Verificar certificados SSL
            hec_port: Puerto HEC (default 8088)
        """
        self.splunk_host = splunk_host
        self.hec_token = hec_token
        self.index = index
        self.source = source
        self.sourcetype = sourcetype
        self.hec_port = hec_port
        
        # Configurar URL base
        protocol = "https" if use_ssl else "http"
        self.hec_url = f"{protocol}://{splunk_host}:{hec_port}/services/collector/event"
        self.raw_hec_url = f"{protocol}://{splunk_host}:{hec_port}/services/collector/raw"
        
        # Configurar headers
        self.headers = {
            "Authorization": f"Splunk {hec_token}",
            "Content-Type": "application/json"
        }
        
        # Configurar sesión HTTP
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        if not verify_ssl:
            self.session.verify = False
            requests.packages.urllib3.disable_warnings()
            
        # Inicializar formateador CEF
        self.cef_formatter = SmartComputeCEFFormatter()
        
        # Logger
        self.logger = logging.getLogger(__name__)
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Probar conectividad con Splunk HEC
        
        Returns:
            Dict con resultado del test
        """
        try:
            test_event = {
                "time": int(time.time()),
                "index": self.index,
                "source": self.source,
                "sourcetype": "smartcompute_test",
                "event": {
                    "message": "SmartCompute connection test",
                    "test_timestamp": datetime.now().isoformat(),
                    "connector_version": "1.0"
                }
            }
            
            response = self.session.post(self.hec_url, json=test_event, timeout=10)
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "message": "Connection successful",
                    "splunk_response": response.json(),
                    "latency_ms": int(response.elapsed.total_seconds() * 1000)
                }
            else:
                return {
                    "status": "error", 
                    "message": f"HTTP {response.status_code}: {response.text}",
                    "status_code": response.status_code
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"Connection error: {str(e)}",
                "exception_type": type(e).__name__
            }
    
    def send_anomaly_event(self, anomaly_data: Dict[str, Any], use_cef: bool = True) -> Dict[str, Any]:
        """
        Enviar evento de anomalía a Splunk
        
        Args:
            anomaly_data: Datos de la anomalía detectada por SmartCompute
            use_cef: Si True, usa formato CEF; si False, JSON estructurado
            
        Returns:
            Dict con resultado del envío
        """
        try:
            if use_cef:
                # Formatear como CEF y enviar como raw event
                cef_event = self.cef_formatter.format_anomaly_event(anomaly_data)
                return self._send_raw_event(cef_event)
            else:
                # Enviar como evento JSON estructurado
                splunk_event = {
                    "time": int(anomaly_data.get('timestamp', time.time())),
                    "index": self.index,
                    "source": self.source, 
                    "sourcetype": "smartcompute_anomaly",
                    "event": {
                        "event_type": "anomaly_detection",
                        "anomaly_type": anomaly_data.get('anomaly_type', 'unknown'),
                        "risk_score": anomaly_data.get('risk_score', 0),
                        "source_host": anomaly_data.get('source_host', 'unknown'),
                        "cpu_usage": anomaly_data.get('cpu_usage'),
                        "memory_usage": anomaly_data.get('memory_usage'),
                        "performance_impact": anomaly_data.get('performance_impact'),
                        "detection_method": anomaly_data.get('detection_method'),
                        "description": anomaly_data.get('description'),
                        "smartcompute_version": "1.0"
                    }
                }
                return self._send_json_event(splunk_event)
                
        except Exception as e:
            self.logger.error(f"Error sending anomaly event: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to send event: {str(e)}"
            }
    
    def send_performance_event(self, perf_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enviar métricas de performance como baseline"""
        try:
            splunk_event = {
                "time": int(time.time()),
                "index": self.index,
                "source": self.source,
                "sourcetype": "smartcompute_performance", 
                "event": {
                    "event_type": "performance_baseline",
                    "hostname": perf_data.get('hostname', 'unknown'),
                    "execution_time": perf_data.get('execution_time'),
                    "method_used": perf_data.get('method_used'),
                    "precision_achieved": perf_data.get('precision_achieved'),
                    "speedup": perf_data.get('speedup'),
                    "cpu_cores": perf_data.get('cpu_cores'),
                    "operation_type": perf_data.get('operation_type', 'matrix_multiplication'),
                    "smartcompute_version": "1.0"
                }
            }
            
            return self._send_json_event(splunk_event)
            
        except Exception as e:
            self.logger.error(f"Error sending performance event: {str(e)}")
            return {
                "status": "error", 
                "message": f"Failed to send performance event: {str(e)}"
            }
    
    def send_batch_events(self, events: List[Dict[str, Any]], event_type: str = "mixed") -> Dict[str, Any]:
        """
        Enviar múltiples eventos en batch para mejor rendimiento
        
        Args:
            events: Lista de eventos a enviar
            event_type: Tipo de eventos ('anomaly', 'performance', 'mixed')
        """
        try:
            batch_events = []
            
            for event_data in events:
                if event_type == "anomaly" or event_data.get('event_type') == 'anomaly':
                    splunk_event = {
                        "time": int(event_data.get('timestamp', time.time())),
                        "index": self.index,
                        "source": self.source,
                        "sourcetype": "smartcompute_anomaly",
                        "event": event_data
                    }
                else:
                    splunk_event = {
                        "time": int(time.time()),
                        "index": self.index,
                        "source": self.source,
                        "sourcetype": "smartcompute_performance",
                        "event": event_data
                    }
                
                batch_events.append(splunk_event)
            
            # Enviar como batch (múltiples eventos en una request)
            batch_payload = "\n".join([json.dumps(event) for event in batch_events])
            
            response = self.session.post(
                self.hec_url,
                data=batch_payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "events_sent": len(batch_events),
                    "splunk_response": response.json(),
                    "latency_ms": int(response.elapsed.total_seconds() * 1000)
                }
            else:
                return {
                    "status": "error",
                    "message": f"Batch send failed: HTTP {response.status_code}",
                    "response_text": response.text
                }
                
        except Exception as e:
            self.logger.error(f"Error sending batch events: {str(e)}")
            return {
                "status": "error",
                "message": f"Batch send failed: {str(e)}"
            }
    
    def _send_json_event(self, splunk_event: Dict[str, Any]) -> Dict[str, Any]:
        """Enviar evento JSON a Splunk HEC"""
        response = self.session.post(self.hec_url, json=splunk_event, timeout=10)
        
        if response.status_code == 200:
            return {
                "status": "success",
                "splunk_response": response.json(),
                "latency_ms": int(response.elapsed.total_seconds() * 1000)
            }
        else:
            return {
                "status": "error",
                "message": f"HTTP {response.status_code}: {response.text}",
                "status_code": response.status_code
            }
    
    def _send_raw_event(self, raw_event: str) -> Dict[str, Any]:
        """Enviar evento raw (CEF) a Splunk HEC"""
        response = self.session.post(
            self.raw_hec_url,
            data=raw_event,
            headers={
                "Authorization": f"Splunk {self.hec_token}",
                "Content-Type": "text/plain"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            return {
                "status": "success", 
                "format": "CEF",
                "latency_ms": int(response.elapsed.total_seconds() * 1000)
            }
        else:
            return {
                "status": "error",
                "message": f"CEF send failed: HTTP {response.status_code}",
                "response_text": response.text
            }
    
    def create_splunk_dashboard_config(self) -> str:
        """
        Genera configuración XML para dashboard Splunk de SmartCompute
        """
        dashboard_xml = '''<form>
  <label>SmartCompute Security Dashboard</label>
  <fieldset submitButton="true">
    <input type="time" token="time_picker">
      <label>Time Range</label>
      <default>
        <earliest>-1h@h</earliest>
        <latest>now</latest>
      </default>
    </input>
  </fieldset>
  
  <row>
    <panel>
      <title>Anomalies by Risk Score</title>
      <chart>
        <search>
          <query>index=smartcompute sourcetype=smartcompute_anomaly 
                | eval risk_level=case(risk_score>=0.9,"Critical",risk_score>=0.7,"High",risk_score>=0.4,"Medium",1=1,"Low") 
                | stats count by risk_level</query>
          <earliest>$time_picker.earliest$</earliest>
          <latest>$time_picker.latest$</latest>
        </search>
        <option name="charting.chart">pie</option>
      </chart>
    </panel>
    
    <panel>
      <title>Performance Trends</title>
      <chart>
        <search>
          <query>index=smartcompute sourcetype=smartcompute_performance 
                | timechart avg(speedup) as "Average Speedup" avg(precision_achieved) as "Average Precision"</query>
          <earliest>$time_picker.earliest$</earliest>
          <latest>$time_picker.latest$</latest>
        </search>
        <option name="charting.chart">line</option>
      </chart>
    </panel>
  </row>
  
  <row>
    <panel>
      <title>Top Anomaly Sources</title>
      <table>
        <search>
          <query>index=smartcompute sourcetype=smartcompute_anomaly 
                | stats count avg(risk_score) as avg_risk by source_host 
                | sort -count</query>
          <earliest>$time_picker.earliest$</earliest>
          <latest>$time_picker.latest$</latest>
        </search>
      </table>
    </panel>
  </row>
</form>'''
        
        return dashboard_xml

def demo_splunk_integration():
    """Demo de integración con Splunk"""
    print("🔗 SmartCompute Splunk Integration Demo")
    print("=" * 50)
    
    # NOTA: Usar credenciales de demo/testing
    print("⚠️  Configure estas variables para su entorno:")
    print("   SPLUNK_HOST = 'your-splunk.com'")
    print("   HEC_TOKEN = 'your-hec-token'")
    print("   INDEX = 'smartcompute'")
    
    # Simular configuración (no funcional sin credenciales reales)
    connector = SplunkConnector(
        splunk_host="demo-splunk.local",
        hec_token="demo-token-12345",
        index="smartcompute"
    )
    
    # Generar eventos de ejemplo
    sample_anomaly = {
        'timestamp': time.time(),
        'anomaly_type': 'resource_exhaustion',
        'source_host': 'web-server-01', 
        'cpu_usage': 98.5,
        'memory_usage': 89.2,
        'risk_score': 0.92,
        'detection_method': 'ml_statistical_analysis',
        'description': 'Critical resource exhaustion detected - immediate action required'
    }
    
    print("\n📤 Evento de ejemplo (formato JSON):")
    print(json.dumps(sample_anomaly, indent=2))
    
    print("\n📤 Evento de ejemplo (formato CEF):")
    cef_event = connector.cef_formatter.format_anomaly_event(sample_anomaly)
    print(cef_event)
    
    print(f"\n📊 Dashboard XML generado:")
    print("💾 Guárdelo como 'smartcompute_dashboard.xml' en Splunk")
    
    print(f"\n🔍 Búsquedas útiles en Splunk:")
    print("   index=smartcompute | stats count by anomaly_type")
    print("   index=smartcompute risk_score>0.8 | sort -_time")
    print("   index=smartcompute | eval response_time=execution_time*1000 | timechart avg(response_time)")

if __name__ == "__main__":
    demo_splunk_integration()