#!/usr/bin/env python3
import json
import time
import threading
from queue import Queue, Empty
from typing import Dict, List, Callable
from datetime import datetime
import logging

class EventStream:
    """Simulador de stream de eventos distribuido"""

    def __init__(self, stream_name: str):
        self.stream_name = stream_name
        self.queue = Queue()
        self.subscribers = []
        self.is_active = False
        self.thread = None

    def publish(self, event: Dict):
        """Publicar evento al stream"""
        enriched_event = {
            **event,
            "stream_metadata": {
                "stream_name": self.stream_name,
                "published_at": datetime.now().isoformat(),
                "event_id": f"{self.stream_name}_{int(time.time() * 1000)}"
            }
        }
        self.queue.put(enriched_event)

    def subscribe(self, callback: Callable[[Dict], None]):
        """Suscribirse al stream"""
        self.subscribers.append(callback)

    def start(self):
        """Iniciar procesamiento del stream"""
        self.is_active = True
        self.thread = threading.Thread(target=self._process_stream, daemon=True)
        self.thread.start()

    def stop(self):
        """Detener procesamiento del stream"""
        self.is_active = False
        if self.thread:
            self.thread.join()

    def _process_stream(self):
        """Procesar eventos del stream"""
        while self.is_active:
            try:
                event = self.queue.get(timeout=1)
                for callback in self.subscribers:
                    try:
                        callback(event)
                    except Exception as e:
                        logging.error(f"Error in subscriber callback: {e}")
            except Empty:
                continue

class DistributedSecurityAnalyzer:
    """Analizador de seguridad distribuido con streams"""

    def __init__(self):
        self.streams = {
            "raw_events": EventStream("raw_events"),
            "processed_events": EventStream("processed_events"),
            "alerts": EventStream("alerts"),
            "incidents": EventStream("incidents")
        }

        self.processors = {}
        self.correlation_window = {}  # Para correlación temporal
        self.setup_logging()
        self.setup_processors()

    def setup_logging(self):
        """Configurar logging distribuido"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s',
            handlers=[
                logging.FileHandler('../logs/distributed_analyzer.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('DistributedAnalyzer')

    def setup_processors(self):
        """Configurar procesadores de eventos"""

        # Procesador de enriquecimiento
        self.processors['enrichment'] = self.enrichment_processor

        # Procesador de correlación
        self.processors['correlation'] = self.correlation_processor

        # Procesador de análisis ML
        self.processors['ml_analysis'] = self.ml_analysis_processor

        # Procesador de respuesta automática
        self.processors['auto_response'] = self.auto_response_processor

        # Configurar suscripciones
        self.streams["raw_events"].subscribe(self.processors['enrichment'])
        self.streams["processed_events"].subscribe(self.processors['correlation'])
        self.streams["processed_events"].subscribe(self.processors['ml_analysis'])
        self.streams["alerts"].subscribe(self.processors['auto_response'])

    def start_processing(self):
        """Iniciar todos los streams"""
        self.logger.info("Starting distributed security analyzer...")
        for stream_name, stream in self.streams.items():
            stream.start()
            self.logger.info(f"Started stream: {stream_name}")

    def stop_processing(self):
        """Detener todos los streams"""
        self.logger.info("Stopping distributed security analyzer...")
        for stream_name, stream in self.streams.items():
            stream.stop()
            self.logger.info(f"Stopped stream: {stream_name}")

    def enrichment_processor(self, event: Dict):
        """Procesador de enriquecimiento de eventos"""
        try:
            self.logger.info(f"Enriching event: {event.get('stream_metadata', {}).get('event_id', 'unknown')}")

            # Simular enriquecimiento con datos contextuales
            enriched_event = {
                **event,
                "enrichment": {
                    "geo_location": self._enrich_geolocation(event),
                    "threat_intel": self._enrich_threat_intel(event),
                    "asset_info": self._enrich_asset_info(event),
                    "user_context": self._enrich_user_context(event)
                },
                "processing_stage": "enriched"
            }

            # Publicar al siguiente stream
            self.streams["processed_events"].publish(enriched_event)

        except Exception as e:
            self.logger.error(f"Error in enrichment processor: {e}")

    def correlation_processor(self, event: Dict):
        """Procesador de correlación de eventos"""
        try:
            event_id = event.get('stream_metadata', {}).get('event_id', 'unknown')
            self.logger.info(f"Correlating event: {event_id}")

            # Mantener ventana de correlación
            current_time = time.time()
            source_host = event.get('source_meta', {}).get('host', 'unknown')

            # Limpiar eventos antiguos (ventana de 5 minutos)
            window_key = f"{source_host}_correlation"
            if window_key not in self.correlation_window:
                self.correlation_window[window_key] = []

            # Remover eventos antiguos
            self.correlation_window[window_key] = [
                e for e in self.correlation_window[window_key]
                if current_time - e['timestamp'] < 300  # 5 minutos
            ]

            # Agregar evento actual
            correlation_event = {
                'event': event,
                'timestamp': current_time
            }
            self.correlation_window[window_key].append(correlation_event)

            # Buscar patrones de correlación
            correlation_result = self._find_correlations(window_key)

            if correlation_result['correlated_events'] > 1:
                # Crear alerta correlacionada
                correlated_alert = {
                    **event,
                    "correlation": correlation_result,
                    "alert_type": "correlated_activity",
                    "processing_stage": "correlated"
                }
                self.streams["alerts"].publish(correlated_alert)

        except Exception as e:
            self.logger.error(f"Error in correlation processor: {e}")

    def ml_analysis_processor(self, event: Dict):
        """Procesador de análisis ML"""
        try:
            event_id = event.get('stream_metadata', {}).get('event_id', 'unknown')
            self.logger.info(f"ML analyzing event: {event_id}")

            # Simular análisis ML (en producción usaría modelos reales)
            ml_result = {
                "false_positive_probability": 0.15,  # Simulado
                "threat_score": 7.8,
                "confidence": "HIGH",
                "model_version": "v2.1.0"
            }

            # Si el score de amenaza es alto, crear alerta
            if ml_result["threat_score"] > 6.0:
                ml_alert = {
                    **event,
                    "ml_analysis": ml_result,
                    "alert_type": "ml_detection",
                    "processing_stage": "ml_analyzed"
                }
                self.streams["alerts"].publish(ml_alert)

        except Exception as e:
            self.logger.error(f"Error in ML processor: {e}")

    def auto_response_processor(self, event: Dict):
        """Procesador de respuesta automática"""
        try:
            event_id = event.get('stream_metadata', {}).get('event_id', 'unknown')
            alert_type = event.get('alert_type', 'unknown')
            self.logger.info(f"Processing auto-response for alert: {event_id} ({alert_type})")

            # Determinar tipo de respuesta
            response_actions = self._determine_response_actions(event)

            if response_actions:
                incident = {
                    **event,
                    "response_actions": response_actions,
                    "incident_id": f"INC-{int(time.time())}",
                    "processing_stage": "incident_created"
                }
                self.streams["incidents"].publish(incident)

                # Simular ejecución de respuestas
                self._execute_response_actions(response_actions, event)

        except Exception as e:
            self.logger.error(f"Error in auto-response processor: {e}")

    def _enrich_geolocation(self, event: Dict) -> Dict:
        """Enriquecer con información geográfica"""
        ip = event.get('source_meta', {}).get('ip', 'unknown')
        return {
            "source_ip": ip,
            "country": "Unknown" if ip == "<IP_REDACTED>" else "Simulated_Country",
            "is_internal": True,
            "risk_score": 1.0
        }

    def _enrich_threat_intel(self, event: Dict) -> Dict:
        """Enriquecer con threat intelligence"""
        return {
            "known_malware_families": [],
            "ioc_matches": [],
            "threat_actor_attribution": None,
            "campaign_correlation": None
        }

    def _enrich_asset_info(self, event: Dict) -> Dict:
        """Enriquecer con información de assets"""
        host = event.get('source_meta', {}).get('host', 'unknown')
        return {
            "asset_criticality": "HIGH" if "admin" in host else "MEDIUM",
            "os_version": "Windows 10",
            "security_tools": ["Windows Defender", "SmartCompute EDR"],
            "patch_level": "Up to date"
        }

    def _enrich_user_context(self, event: Dict) -> Dict:
        """Enriquecer con contexto de usuario"""
        user = event.get('source_meta', {}).get('user', 'unknown')
        return {
            "user_role": "Administrator" if "admin" in user else "Standard User",
            "risk_score": 3.0,
            "recent_activities": ["Login", "File access", "Process execution"],
            "behavioral_baseline": "Normal"
        }

    def _find_correlations(self, window_key: str) -> Dict:
        """Buscar correlaciones en la ventana temporal"""
        events = self.correlation_window.get(window_key, [])

        correlation_result = {
            "correlated_events": len(events),
            "pattern_type": None,
            "confidence": 0.0
        }

        if len(events) >= 3:
            # Detectar patrón de múltiples inyecciones
            injection_events = [
                e for e in events
                if "createremotethread" in e['event'].get('description', '').lower()
            ]

            if len(injection_events) >= 2:
                correlation_result.update({
                    "pattern_type": "repeated_injection_attempts",
                    "confidence": 0.8,
                    "details": f"Detected {len(injection_events)} injection attempts"
                })

        return correlation_result

    def _determine_response_actions(self, event: Dict) -> List[Dict]:
        """Determinar acciones de respuesta automática"""
        actions = []

        alert_type = event.get('alert_type', '')
        correlation = event.get('correlation', {})
        ml_analysis = event.get('ml_analysis', {})

        # Respuesta para eventos correlacionados
        if alert_type == "correlated_activity":
            actions.append({
                "action": "isolate_host",
                "priority": "HIGH",
                "reason": "Multiple correlated suspicious activities detected"
            })

        # Respuesta para detecciones ML
        if alert_type == "ml_detection" and ml_analysis.get('threat_score', 0) > 7.0:
            actions.append({
                "action": "collect_forensics",
                "priority": "MEDIUM",
                "reason": "High-confidence ML threat detection"
            })

        return actions

    def _execute_response_actions(self, actions: List[Dict], event: Dict):
        """Ejecutar acciones de respuesta (simulado)"""
        for action in actions:
            self.logger.info(f"Executing response action: {action['action']} - {action['reason']}")

    def ingest_event(self, event: Dict):
        """Punto de entrada para nuevos eventos"""
        self.streams["raw_events"].publish(event)

def main():
    # Crear analizador distribuido
    analyzer = DistributedSecurityAnalyzer()

    # Iniciar procesamiento
    analyzer.start_processing()

    try:
        # Cargar evento de muestra
        with open("../redacted_output.json", "r") as f:
            data = json.load(f)

        print("=== Testing Distributed Security Analyzer ===")

        # Simular múltiples eventos para demostrar correlación
        base_event = data["findings"][0] if "findings" in data else {}

        events_to_simulate = [
            {**base_event, "event_id": 1, "description": "CreateRemoteThread observed targeting chrome.exe"},
            {**base_event, "event_id": 2, "description": "DLL injection detected in chrome.exe"},
            {**base_event, "event_id": 3, "description": "CreateRemoteThread observed targeting chrome.exe again"},
        ]

        for i, event in enumerate(events_to_simulate):
            print(f"\nIngesting event {i+1}...")
            analyzer.ingest_event(event)
            time.sleep(2)  # Esperar un poco entre eventos

        # Dejar que el sistema procese
        print("\nProcessing events...")
        time.sleep(5)

        print("\nDistributed analysis completed!")
        print("Check ../logs/distributed_analyzer.log for detailed logs")

    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        analyzer.stop_processing()

if __name__ == "__main__":
    main()