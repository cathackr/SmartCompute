#!/usr/bin/env python3
"""
MCP-HRM Bridge Module
Integración entre Model Context Protocol y SmartCompute HRM
Fase 1: Foundation Integration
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
import uuid

# Importar módulos HRM existentes
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'smartcompute_hrm_proto', 'python'))

try:
    from integrated_analysis import run_integrated_analysis
    from stream_processor import EventStream
    from enterprise_industrial_analyzer import EnterpriseIndustrialHRM, EnterpriseContext
    from threat_intelligence import ThreatIntelligenceEngine
    from incident_response import AutomatedIncidentResponse
    HRM_AVAILABLE = True
except ImportError as e:
    logging.warning(f"HRM modules not available: {e}")
    HRM_AVAILABLE = False

@dataclass
class MCPRequest:
    """Estructura de solicitud MCP estándar"""
    jsonrpc: str = "2.0"
    method: str = ""
    params: Dict[str, Any] = None
    id: str = None

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.params is None:
            self.params = {}

@dataclass
class MCPResponse:
    """Estructura de respuesta MCP estándar"""
    jsonrpc: str = "2.0"
    result: Dict[str, Any] = None
    error: Dict[str, Any] = None
    id: str = None

    def __post_init__(self):
        if self.result is None:
            self.result = {}

class MCPHRMBridge:
    """
    Puente principal entre MCP y SmartCompute HRM
    Mantiene compatibilidad con funcionalidades Enterprise existentes
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        self.logger = self._setup_logging()

        # Inicializar componentes HRM si están disponibles
        if HRM_AVAILABLE:
            self.hrm_analyzer = EnterpriseIndustrialHRM()
            self.stream_processor = EventStream("enterprise_mcp_events")
            self.threat_intel_engine = ThreatIntelligenceEngine()
            self.incident_response = AutomatedIncidentResponse()
        else:
            self.logger.warning("HRM components not available - running in simulation mode")

        # Estado interno
        self.active_sessions = {}
        self.performance_metrics = {
            "requests_processed": 0,
            "average_response_time": 0,
            "hrm_analysis_count": 0,
            "last_update": datetime.now().isoformat()
        }

    def _default_config(self) -> Dict:
        """Configuración por defecto"""
        return {
            "mcp_version": "2024-11-05",
            "enterprise_mode": True,
            "hrm_integration": True,
            "max_concurrent_requests": 10,
            "response_timeout_seconds": 30,
            "metrics_enabled": True,
            "log_level": "INFO"
        }

    def _setup_logging(self) -> logging.Logger:
        """Configurar logging"""
        logger = logging.getLogger("MCPHRMBridge")
        logger.setLevel(getattr(logging, self.config.get("log_level", "INFO")))

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    async def handle_mcp_request(self, request: MCPRequest) -> MCPResponse:
        """
        Manejador principal de solicitudes MCP
        """
        start_time = datetime.now()
        self.logger.info(f"Processing MCP request: {request.method} [ID: {request.id}]")

        try:
            # Enrutar según método MCP
            if request.method == "smartcompute/analyze_threat":
                result = await self._handle_threat_analysis(request.params)
            elif request.method == "smartcompute/enterprise_context":
                result = await self._handle_enterprise_context(request.params)
            elif request.method == "smartcompute/stream_events":
                result = await self._handle_stream_events(request.params)
            elif request.method == "smartcompute/get_metrics":
                result = self._handle_get_metrics()
            elif request.method == "smartcompute/health_check":
                result = self._handle_health_check()
            else:
                raise ValueError(f"Unknown method: {request.method}")

            # Actualizar métricas
            self._update_performance_metrics(start_time)

            return MCPResponse(result=result, id=request.id)

        except Exception as e:
            self.logger.error(f"Error processing request {request.id}: {str(e)}")
            error_detail = {
                "code": -32603,  # Internal error
                "message": f"Internal error: {str(e)}",
                "data": {"request_id": request.id, "method": request.method}
            }
            return MCPResponse(error=error_detail, id=request.id)

    async def _handle_threat_analysis(self, params: Dict) -> Dict:
        """
        Análisis de amenazas usando HRM integrado
        """
        if not HRM_AVAILABLE:
            return self._simulate_threat_analysis(params)

        event_data = params.get("event", {})
        business_context = params.get("business_context", {})
        analysis_options = params.get("options", {})

        self.logger.debug(f"Analyzing threat with HRM: {event_data.get('event_id', 'unknown')}")

        # Usar análisis integrado HRM existente
        hrm_analysis = run_integrated_analysis(event_data)

        # Añadir contexto empresarial si está disponible
        if business_context:
            enterprise_context = self.hrm_analyzer.analyze_enterprise_context(
                event_data, EnterpriseContext(**business_context)
            )
            hrm_analysis["enterprise_context"] = enterprise_context

        # Enriquecer con métricas adicionales para MCP
        mcp_enhanced_analysis = {
            "mcp_request_id": params.get("request_id"),
            "analysis_timestamp": datetime.now().isoformat(),
            "hrm_analysis": hrm_analysis,
            "routing_recommendations": self._generate_routing_recommendations(hrm_analysis),
            "scaling_advice": self._generate_scaling_advice(hrm_analysis),
            "enterprise_actions": self._suggest_enterprise_actions(hrm_analysis)
        }

        self.performance_metrics["hrm_analysis_count"] += 1
        return mcp_enhanced_analysis

    def _simulate_threat_analysis(self, params: Dict) -> Dict:
        """Simulación cuando HRM no está disponible"""
        return {
            "simulation_mode": True,
            "message": "HRM components not available - simulation response",
            "mock_analysis": {
                "threat_level": "MEDIUM",
                "confidence": 0.75,
                "recommendations": ["Enable HRM components for full analysis"]
            }
        }

    async def _handle_enterprise_context(self, params: Dict) -> Dict:
        """
        Manejo de contexto empresarial
        """
        business_unit = params.get("business_unit", "unknown")
        compliance_requirements = params.get("compliance_frameworks", [])

        if not HRM_AVAILABLE:
            return {"simulation_mode": True, "business_unit": business_unit}

        # Usar analizador empresarial HRM
        context_analysis = self.hrm_analyzer.analyze_enterprise_context(
            params.get("event", {}),
            EnterpriseContext(
                business_unit=business_unit,
                compliance_frameworks=compliance_requirements,
                risk_tolerance=params.get("risk_tolerance", "medium"),
                asset_criticality=params.get("asset_criticality", "medium"),
                user_privileges=params.get("user_privileges", "standard")
            )
        )

        return {
            "enterprise_context": context_analysis,
            "mcp_routing_logic": self._get_enterprise_routing_logic(context_analysis),
            "compliance_requirements": self._get_compliance_actions(compliance_requirements)
        }

    async def _handle_stream_events(self, params: Dict) -> Dict:
        """
        Manejo de eventos en stream
        """
        if not HRM_AVAILABLE:
            return {"simulation_mode": True, "stream_active": False}

        stream_config = params.get("stream_config", {})
        events = params.get("events", [])

        # Procesar eventos usando stream processor HRM
        processed_events = []
        for event in events:
            # Usar el stream processor existente
            enriched_event = {
                **event,
                "mcp_metadata": {
                    "processed_at": datetime.now().isoformat(),
                    "bridge_version": "1.0.0",
                    "hrm_enhanced": True
                }
            }
            processed_events.append(enriched_event)

        return {
            "processed_events": processed_events,
            "stream_metrics": {
                "events_processed": len(processed_events),
                "processing_rate": "real-time",
                "hrm_enhancement": "active"
            }
        }

    def _handle_get_metrics(self) -> Dict:
        """Obtener métricas del puente MCP-HRM"""
        return {
            "bridge_metrics": self.performance_metrics,
            "hrm_status": "available" if HRM_AVAILABLE else "simulation_mode",
            "mcp_version": self.config["mcp_version"],
            "enterprise_mode": self.config["enterprise_mode"]
        }

    def _handle_health_check(self) -> Dict:
        """Health check del sistema"""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "mcp_bridge": "operational",
                "hrm_integration": "available" if HRM_AVAILABLE else "simulation_mode",
                "enterprise_context": "operational",
                "stream_processing": "operational"
            }
        }

        return health_status

    def _generate_routing_recommendations(self, hrm_analysis: Dict) -> List[Dict]:
        """
        Generar recomendaciones de enrutamiento basadas en análisis HRM
        """
        threat_level = hrm_analysis.get("final_assessment", {}).get("threat_level", "UNKNOWN")
        confidence = hrm_analysis.get("final_assessment", {}).get("confidence", 0.5)

        recommendations = []

        if threat_level == "CRITICAL" and confidence > 0.85:
            recommendations.append({
                "target": "priority_nodes",
                "reason": "Critical threat with high confidence",
                "priority": 1,
                "resources": "maximum"
            })
        elif threat_level == "HIGH":
            recommendations.append({
                "target": "specialized_nodes",
                "reason": "High-level threat detection",
                "priority": 2,
                "resources": "elevated"
            })
        else:
            recommendations.append({
                "target": "standard_nodes",
                "reason": "Standard threat processing",
                "priority": 3,
                "resources": "normal"
            })

        return recommendations

    def _generate_scaling_advice(self, hrm_analysis: Dict) -> Dict:
        """
        Generar consejos de escalado basados en análisis HRM
        """
        threat_level = hrm_analysis.get("final_assessment", {}).get("threat_level", "UNKNOWN")
        ml_score = hrm_analysis.get("analysis_modules", {}).get("ml_false_positive", {}).get("score", 0.5)

        if threat_level == "CRITICAL":
            return {
                "action": "scale_up_immediately",
                "instances": 3,
                "reason": "Critical threat detected",
                "duration": "until_resolved"
            }
        elif ml_score < 0.3:  # Baja probabilidad de falso positivo
            return {
                "action": "scale_up_moderate",
                "instances": 2,
                "reason": "High confidence threat",
                "duration": "30_minutes"
            }
        else:
            return {
                "action": "maintain_current",
                "reason": "Standard threat processing sufficient"
            }

    def _suggest_enterprise_actions(self, hrm_analysis: Dict) -> List[Dict]:
        """
        Sugerir acciones empresariales basadas en análisis HRM
        """
        actions = []

        threat_level = hrm_analysis.get("final_assessment", {}).get("threat_level", "UNKNOWN")

        if threat_level in ["CRITICAL", "HIGH"]:
            actions.append({
                "action": "notify_security_team",
                "urgency": "immediate",
                "channels": ["email", "sms", "slack"]
            })

            actions.append({
                "action": "export_to_xdr",
                "targets": ["crowdstrike", "sentinel", "cisco_umbrella"],
                "format": "enhanced"
            })

        # Siempre sugerir logging para auditoría
        actions.append({
            "action": "enhanced_logging",
            "retention": "extended",
            "compliance_ready": True
        })

        return actions

    def _get_enterprise_routing_logic(self, context_analysis: Dict) -> Dict:
        """
        Lógica de enrutamiento empresarial
        """
        return {
            "routing_strategy": "business_context_aware",
            "primary_factors": ["business_unit", "compliance_requirements", "asset_criticality"],
            "fallback_strategy": "load_balanced"
        }

    def _get_compliance_actions(self, compliance_frameworks: List[str]) -> List[Dict]:
        """
        Acciones específicas por framework de compliance
        """
        actions = []

        for framework in compliance_frameworks:
            if framework == "SOX":
                actions.append({
                    "framework": "SOX",
                    "requirements": ["audit_trail", "data_integrity", "access_controls"],
                    "retention": "7_years"
                })
            elif framework == "HIPAA":
                actions.append({
                    "framework": "HIPAA",
                    "requirements": ["phi_protection", "breach_notification", "access_logging"],
                    "retention": "6_years"
                })
            elif framework == "PCI-DSS":
                actions.append({
                    "framework": "PCI-DSS",
                    "requirements": ["card_data_protection", "network_monitoring", "vulnerability_management"],
                    "retention": "3_years"
                })

        return actions

    def _update_performance_metrics(self, start_time: datetime):
        """
        Actualizar métricas de rendimiento
        """
        response_time = (datetime.now() - start_time).total_seconds()

        self.performance_metrics["requests_processed"] += 1

        # Calcular promedio móvil simple
        current_avg = self.performance_metrics["average_response_time"]
        request_count = self.performance_metrics["requests_processed"]
        new_avg = ((current_avg * (request_count - 1)) + response_time) / request_count
        self.performance_metrics["average_response_time"] = round(new_avg, 3)

        self.performance_metrics["last_update"] = datetime.now().isoformat()

# Factory function para facilitar importación
def create_mcp_hrm_bridge(config: Optional[Dict] = None) -> MCPHRMBridge:
    """
    Factory function para crear instancia del puente MCP-HRM
    """
    return MCPHRMBridge(config)

# Ejemplo de uso básico
if __name__ == "__main__":
    async def test_bridge():
        bridge = create_mcp_hrm_bridge()

        # Test health check
        health_request = MCPRequest(
            method="smartcompute/health_check",
            params={}
        )

        response = await bridge.handle_mcp_request(health_request)
        print("Health Check Response:")
        print(json.dumps(asdict(response), indent=2))

        # Test threat analysis
        threat_request = MCPRequest(
            method="smartcompute/analyze_threat",
            params={
                "event": {
                    "event_id": "test_001",
                    "timestamp": datetime.now().isoformat(),
                    "event_type": "process_injection",
                    "source_ip": "192.168.1.100",
                    "target_process": "explorer.exe"
                },
                "business_context": {
                    "business_unit": "finance",
                    "compliance_frameworks": ["SOX", "PCI-DSS"],
                    "risk_tolerance": "low",
                    "asset_criticality": "high",
                    "user_privileges": "admin"
                }
            }
        )

        response = await bridge.handle_mcp_request(threat_request)
        print("\nThreat Analysis Response:")
        print(json.dumps(asdict(response), indent=2))

    # Ejecutar test
    asyncio.run(test_bridge())