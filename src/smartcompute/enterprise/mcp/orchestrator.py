#!/usr/bin/env python3
"""
MCP Enterprise Orchestrator
Orquestador inteligente para SmartCompute Enterprise usando MCP + HRM
Coordina auto-scaling, load balancing y multi-región DR
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import uuid

from mcp_hrm_bridge import create_mcp_hrm_bridge, MCPRequest, MCPResponse

class ScalingAction(Enum):
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    MAINTAIN = "maintain"
    EMERGENCY_SCALE = "emergency_scale"

class RegionHealth(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    RECOVERING = "recovering"

@dataclass
class EnterpriseNode:
    """Nodo de procesamiento Enterprise"""
    node_id: str
    region: str
    node_type: str  # "standard", "threat_analysis", "ml_processing", "compliance"
    current_load: float
    max_capacity: int
    specialized_capabilities: List[str]
    health_status: RegionHealth
    last_heartbeat: datetime

@dataclass
class ScalingDecision:
    """Decisión de escalado inteligente"""
    action: ScalingAction
    target_instances: int
    reason: str
    confidence: float
    estimated_cost: float
    business_impact: str
    execution_priority: int

@dataclass
class LoadBalancingDecision:
    """Decisión de balanceeo de carga inteligente"""
    target_node: str
    routing_reason: str
    expected_performance: Dict[str, Any]
    fallback_nodes: List[str]
    business_context_weight: float

class MCPEnterpriseOrchestrator:
    """
    Orquestador Enterprise que integra MCP con HRM para:
    - Auto-scaling inteligente basado en contexto de amenaza
    - Load balancing por tipo de análisis
    - Disaster Recovery multi-región
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        self.logger = self._setup_logging()

        # Componentes core
        self.mcp_bridge = create_mcp_hrm_bridge()
        self.enterprise_nodes = {}
        self.region_health = {}
        self.scaling_history = []
        self.performance_metrics = {}

        # Estado del orquestador
        self.is_running = False
        self.monitoring_tasks = []

        # Inicializar nodos Enterprise
        self._initialize_enterprise_nodes()

    def _default_config(self) -> Dict:
        """Configuración por defecto del orquestador"""
        return {
            "regions": {
                "us-east-1": {"primary": True, "capacity": 10},
                "eu-west-1": {"primary": False, "capacity": 8},
                "ap-southeast-1": {"primary": False, "capacity": 6}
            },
            "node_types": {
                "standard": {"min_instances": 2, "max_instances": 10},
                "threat_analysis": {"min_instances": 1, "max_instances": 5},
                "ml_processing": {"min_instances": 1, "max_instances": 8},
                "compliance": {"min_instances": 1, "max_instances": 3}
            },
            "scaling_thresholds": {
                "cpu_threshold": 70.0,
                "memory_threshold": 80.0,
                "threat_queue_threshold": 50,
                "response_time_threshold": 500  # ms
            },
            "business_hours": {
                "start": 8, "end": 18,
                "timezone": "UTC"
            },
            "disaster_recovery": {
                "rto_minutes": 15,  # Recovery Time Objective
                "rpo_minutes": 1,   # Recovery Point Objective
                "auto_failover": True
            }
        }

    def _setup_logging(self) -> logging.Logger:
        """Setup logging para el orquestador"""
        logger = logging.getLogger("MCPEnterpriseOrchestrator")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _initialize_enterprise_nodes(self):
        """Inicializar nodos Enterprise por región"""
        for region, region_config in self.config["regions"].items():
            self.region_health[region] = RegionHealth.HEALTHY
            self.enterprise_nodes[region] = []

            # Crear nodos por tipo
            for node_type, type_config in self.config["node_types"].items():
                for i in range(type_config["min_instances"]):
                    node = EnterpriseNode(
                        node_id=f"{region}-{node_type}-{i:03d}",
                        region=region,
                        node_type=node_type,
                        current_load=0.0,
                        max_capacity=region_config["capacity"],
                        specialized_capabilities=self._get_node_capabilities(node_type),
                        health_status=RegionHealth.HEALTHY,
                        last_heartbeat=datetime.now()
                    )
                    self.enterprise_nodes[region].append(node)

    def _get_node_capabilities(self, node_type: str) -> List[str]:
        """Obtener capacidades especializadas por tipo de nodo"""
        capabilities_map = {
            "standard": ["general_analysis", "basic_threat_detection"],
            "threat_analysis": ["advanced_threat_detection", "behavioral_analysis", "apt_detection"],
            "ml_processing": ["false_positive_reduction", "pattern_recognition", "predictive_analysis"],
            "compliance": ["audit_trail", "compliance_reporting", "data_retention"]
        }
        return capabilities_map.get(node_type, [])

    async def start_orchestration(self):
        """Iniciar orquestación Enterprise"""
        self.logger.info("Starting MCP Enterprise Orchestrator")
        self.is_running = True

        # Iniciar tareas de monitoreo
        self.monitoring_tasks = [
            asyncio.create_task(self._monitor_node_health()),
            asyncio.create_task(self._monitor_scaling_requirements()),
            asyncio.create_task(self._monitor_region_performance()),
            asyncio.create_task(self._cleanup_expired_data())
        ]

        self.logger.info("Enterprise Orchestrator started successfully")

    async def stop_orchestration(self):
        """Detener orquestación"""
        self.logger.info("Stopping MCP Enterprise Orchestrator")
        self.is_running = False

        # Cancelar tareas de monitoreo
        for task in self.monitoring_tasks:
            task.cancel()

        await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)
        self.logger.info("Enterprise Orchestrator stopped")

    async def process_enterprise_threat(self, threat_event: Dict, business_context: Dict) -> Dict:
        """
        Procesamiento Enterprise de amenaza usando MCP + HRM
        """
        self.logger.info(f"Processing enterprise threat: {threat_event.get('event_id', 'unknown')}")

        # 1. Análisis HRM vía MCP
        analysis_request = MCPRequest(
            method="smartcompute/analyze_threat",
            params={
                "event": threat_event,
                "business_context": business_context,
                "options": {"enterprise_mode": True}
            }
        )

        analysis_response = await self.mcp_bridge.handle_mcp_request(analysis_request)
        if analysis_response.error:
            raise Exception(f"HRM analysis failed: {analysis_response.error}")

        hrm_analysis = analysis_response.result

        # 2. Decisión de enrutamiento inteligente
        routing_decision = await self._make_intelligent_routing_decision(
            hrm_analysis, business_context
        )

        # 3. Decisión de escalado si es necesario
        scaling_decision = await self._make_scaling_decision(
            hrm_analysis, business_context
        )

        # 4. Ejecutar coordinadamente
        execution_result = await self._execute_coordinated_response(
            threat_event, hrm_analysis, routing_decision, scaling_decision
        )

        return {
            "orchestration_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "threat_analysis": hrm_analysis,
            "routing_decision": asdict(routing_decision),
            "scaling_decision": asdict(scaling_decision),
            "execution_result": execution_result,
            "business_impact_assessment": self._assess_business_impact(
                hrm_analysis, business_context
            )
        }

    async def _make_intelligent_routing_decision(self, hrm_analysis: Dict, business_context: Dict) -> LoadBalancingDecision:
        """
        Decisión inteligente de enrutamiento basada en HRM + contexto empresarial
        """
        threat_level = hrm_analysis.get("hrm_analysis", {}).get("final_assessment", {}).get("threat_level", "MEDIUM")
        threat_category = hrm_analysis.get("hrm_analysis", {}).get("analysis_modules", {}).get("threat_intelligence", {}).get("category", "unknown")
        business_unit = business_context.get("business_unit", "unknown")

        # Determinar tipo de nodo especializado necesario
        preferred_node_type = self._determine_preferred_node_type(threat_level, threat_category)

        # Encontrar mejor nodo disponible
        best_node = await self._find_optimal_node(preferred_node_type, business_context)

        # Nodos de fallback
        fallback_nodes = await self._find_fallback_nodes(preferred_node_type, best_node)

        return LoadBalancingDecision(
            target_node=best_node.node_id,
            routing_reason=f"Optimal for {threat_category} threats in {business_unit}",
            expected_performance={
                "estimated_processing_time": self._estimate_processing_time(best_node, hrm_analysis),
                "confidence_level": 0.85,
                "resource_utilization": best_node.current_load
            },
            fallback_nodes=[node.node_id for node in fallback_nodes],
            business_context_weight=self._calculate_business_weight(business_context)
        )

    def _determine_preferred_node_type(self, threat_level: str, threat_category: str) -> str:
        """Determinar tipo de nodo preferido basado en amenaza"""
        if threat_level == "CRITICAL":
            return "threat_analysis"
        elif threat_category in ["apt", "advanced_persistent_threat", "zero_day"]:
            return "threat_analysis"
        elif threat_category in ["false_positive", "benign", "low_confidence"]:
            return "ml_processing"
        elif threat_category in ["compliance_violation", "audit_required"]:
            return "compliance"
        else:
            return "standard"

    async def _find_optimal_node(self, preferred_type: str, business_context: Dict) -> EnterpriseNode:
        """Encontrar nodo óptimo considerando carga y contexto empresarial"""
        business_unit = business_context.get("business_unit", "unknown")
        compliance_requirements = business_context.get("compliance_frameworks", [])

        candidate_nodes = []

        # Recopilar nodos candidatos de todas las regiones saludables
        for region, health in self.region_health.items():
            if health == RegionHealth.HEALTHY:
                for node in self.enterprise_nodes[region]:
                    if node.node_type == preferred_type and node.health_status == RegionHealth.HEALTHY:
                        candidate_nodes.append(node)

        if not candidate_nodes:
            # Fallback a nodos standard
            for region, health in self.region_health.items():
                if health == RegionHealth.HEALTHY:
                    for node in self.enterprise_nodes[region]:
                        if node.node_type == "standard" and node.health_status == RegionHealth.HEALTHY:
                            candidate_nodes.append(node)

        if not candidate_nodes:
            raise Exception("No healthy nodes available")

        # Scoring para seleccionar mejor nodo
        best_node = None
        best_score = -1

        for node in candidate_nodes:
            score = self._calculate_node_score(node, business_context)
            if score > best_score:
                best_score = score
                best_node = node

        return best_node

    def _calculate_node_score(self, node: EnterpriseNode, business_context: Dict) -> float:
        """Calcular score de nodo considerando múltiples factores"""
        score = 0.0

        # Factor de carga (peso 40%)
        load_score = (1.0 - node.current_load) * 0.4
        score += load_score

        # Factor de capacidad (peso 20%)
        capacity_score = (node.max_capacity / 10.0) * 0.2  # Normalizar a 10
        score += capacity_score

        # Factor de especialización (peso 30%)
        business_unit = business_context.get("business_unit", "unknown")
        if business_unit == "finance" and "compliance" in node.specialized_capabilities:
            score += 0.3
        elif business_unit == "healthcare" and "audit_trail" in node.specialized_capabilities:
            score += 0.3
        elif "advanced_threat_detection" in node.specialized_capabilities:
            score += 0.2

        # Factor de latencia geográfica (peso 10%)
        # Preferir nodos en región primaria
        if node.region == "us-east-1":  # Región primaria
            score += 0.1

        return min(score, 1.0)  # Normalizar a 1.0

    async def _find_fallback_nodes(self, preferred_type: str, primary_node: EnterpriseNode) -> List[EnterpriseNode]:
        """Encontrar nodos de fallback"""
        fallback_nodes = []

        for region, health in self.region_health.items():
            if health in [RegionHealth.HEALTHY, RegionHealth.DEGRADED]:
                for node in self.enterprise_nodes[region]:
                    if (node.node_id != primary_node.node_id and
                        node.health_status == RegionHealth.HEALTHY and
                        node.current_load < 0.8):  # Menos del 80% de carga
                        fallback_nodes.append(node)

        # Ordenar por score y tomar los mejores 3
        fallback_nodes.sort(key=lambda n: (1.0 - n.current_load), reverse=True)
        return fallback_nodes[:3]

    async def _make_scaling_decision(self, hrm_analysis: Dict, business_context: Dict) -> ScalingDecision:
        """
        Decisión de escalado inteligente basada en HRM
        """
        threat_level = hrm_analysis.get("hrm_analysis", {}).get("final_assessment", {}).get("threat_level", "MEDIUM")
        confidence = hrm_analysis.get("hrm_analysis", {}).get("final_assessment", {}).get("confidence", 0.5)
        false_positive_score = hrm_analysis.get("hrm_analysis", {}).get("analysis_modules", {}).get("ml_false_positive", {}).get("score", 0.5)

        business_impact = business_context.get("asset_criticality", "medium")
        compliance_frameworks = business_context.get("compliance_frameworks", [])

        # Evaluar necesidad de escalado
        current_load = await self._get_average_cluster_load()
        threat_queue_size = await self._get_threat_queue_size()

        if threat_level == "CRITICAL" and confidence > 0.85:
            return ScalingDecision(
                action=ScalingAction.EMERGENCY_SCALE,
                target_instances=5,
                reason="Critical threat with high confidence detected",
                confidence=0.95,
                estimated_cost=250.0,  # USD per hour
                business_impact="HIGH - Immediate response required",
                execution_priority=1
            )

        elif (threat_level == "HIGH" and confidence > 0.70) or threat_queue_size > 100:
            return ScalingDecision(
                action=ScalingAction.SCALE_UP,
                target_instances=2,
                reason="High threat level or queue backlog detected",
                confidence=0.80,
                estimated_cost=100.0,
                business_impact="MEDIUM - Performance optimization",
                execution_priority=2
            )

        elif current_load < 0.3 and threat_queue_size < 10:
            return ScalingDecision(
                action=ScalingAction.SCALE_DOWN,
                target_instances=-1,
                reason="Low utilization detected - cost optimization",
                confidence=0.75,
                estimated_cost=-50.0,  # Negative = savings
                business_impact="LOW - Cost optimization",
                execution_priority=5
            )

        else:
            return ScalingDecision(
                action=ScalingAction.MAINTAIN,
                target_instances=0,
                reason="Current capacity sufficient",
                confidence=0.70,
                estimated_cost=0.0,
                business_impact="NEUTRAL - Stable operation",
                execution_priority=10
            )

    async def _execute_coordinated_response(self, threat_event: Dict, hrm_analysis: Dict,
                                          routing_decision: LoadBalancingDecision,
                                          scaling_decision: ScalingDecision) -> Dict:
        """
        Ejecutar respuesta coordinada Enterprise
        """
        execution_results = {
            "routing_executed": False,
            "scaling_executed": False,
            "xdr_export_executed": False,
            "siem_export_executed": False,
            "notifications_sent": False
        }

        try:
            # 1. Ejecutar enrutamiento
            if routing_decision.target_node:
                await self._route_to_node(threat_event, routing_decision.target_node)
                execution_results["routing_executed"] = True
                self.logger.info(f"Routed threat to node: {routing_decision.target_node}")

            # 2. Ejecutar escalado si es necesario
            if scaling_decision.action != ScalingAction.MAINTAIN:
                await self._execute_scaling(scaling_decision)
                execution_results["scaling_executed"] = True
                self.logger.info(f"Executed scaling action: {scaling_decision.action}")

            # 3. Exportar a XDR si es amenaza crítica
            threat_level = hrm_analysis.get("hrm_analysis", {}).get("final_assessment", {}).get("threat_level")
            if threat_level in ["CRITICAL", "HIGH"]:
                await self._export_to_xdr_systems(threat_event, hrm_analysis)
                execution_results["xdr_export_executed"] = True

            # 4. Exportar a SIEM para auditoría
            await self._export_to_siem_systems(threat_event, hrm_analysis)
            execution_results["siem_export_executed"] = True

            # 5. Notificaciones empresariales
            if scaling_decision.execution_priority <= 2:  # Alta prioridad
                await self._send_enterprise_notifications(threat_event, hrm_analysis)
                execution_results["notifications_sent"] = True

        except Exception as e:
            self.logger.error(f"Error in coordinated response execution: {str(e)}")
            execution_results["error"] = str(e)

        return execution_results

    async def _route_to_node(self, threat_event: Dict, target_node_id: str):
        """Enrutar evento a nodo específico"""
        # Simular enrutamiento (implementación real conectaría con el nodo)
        self.logger.debug(f"Routing event {threat_event.get('event_id')} to node {target_node_id}")

        # Actualizar carga del nodo
        for region_nodes in self.enterprise_nodes.values():
            for node in region_nodes:
                if node.node_id == target_node_id:
                    node.current_load = min(node.current_load + 0.1, 1.0)
                    break

    async def _execute_scaling(self, scaling_decision: ScalingDecision):
        """Ejecutar decisión de escalado"""
        self.logger.info(f"Executing scaling: {scaling_decision.action} with {scaling_decision.target_instances} instances")

        # Registrar en historial
        self.scaling_history.append({
            "timestamp": datetime.now().isoformat(),
            "action": scaling_decision.action.value,
            "instances": scaling_decision.target_instances,
            "reason": scaling_decision.reason,
            "estimated_cost": scaling_decision.estimated_cost
        })

        # Simular escalado (implementación real conectaría con cloud provider)
        await asyncio.sleep(0.1)

    async def _export_to_xdr_systems(self, threat_event: Dict, hrm_analysis: Dict):
        """Exportar a sistemas XDR Enterprise existentes"""
        self.logger.debug("Exporting to XDR systems: CrowdStrike, Sentinel, Cisco Umbrella")
        # Implementación conectaría con exporters existentes
        await asyncio.sleep(0.1)

    async def _export_to_siem_systems(self, threat_event: Dict, hrm_analysis: Dict):
        """Exportar a sistemas SIEM Enterprise existentes"""
        self.logger.debug("Exporting to SIEM systems: Wazuh, Splunk, Elastic")
        # Implementación conectaría con conectores SIEM existentes
        await asyncio.sleep(0.1)

    async def _send_enterprise_notifications(self, threat_event: Dict, hrm_analysis: Dict):
        """Enviar notificaciones empresariales"""
        self.logger.debug("Sending enterprise notifications: Email, Slack, SMS")
        # Implementación conectaría con sistemas de notificación
        await asyncio.sleep(0.1)

    # Métodos de monitoreo continuo

    async def _monitor_node_health(self):
        """Monitoreo continuo de salud de nodos"""
        while self.is_running:
            try:
                for region, nodes in self.enterprise_nodes.items():
                    healthy_nodes = sum(1 for node in nodes if node.health_status == RegionHealth.HEALTHY)
                    total_nodes = len(nodes)

                    if healthy_nodes / total_nodes < 0.5:
                        self.region_health[region] = RegionHealth.DEGRADED
                        self.logger.warning(f"Region {region} degraded: {healthy_nodes}/{total_nodes} nodes healthy")
                    else:
                        self.region_health[region] = RegionHealth.HEALTHY

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                self.logger.error(f"Error in node health monitoring: {str(e)}")
                await asyncio.sleep(60)

    async def _monitor_scaling_requirements(self):
        """Monitoreo de requisitos de escalado"""
        while self.is_running:
            try:
                avg_load = await self._get_average_cluster_load()
                queue_size = await self._get_threat_queue_size()

                if avg_load > 0.8 or queue_size > 50:
                    self.logger.info(f"Scaling may be needed: load={avg_load:.2f}, queue={queue_size}")

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                self.logger.error(f"Error in scaling monitoring: {str(e)}")
                await asyncio.sleep(120)

    async def _monitor_region_performance(self):
        """Monitoreo de rendimiento por región"""
        while self.is_running:
            try:
                for region in self.config["regions"].keys():
                    # Simular métricas de rendimiento
                    region_metrics = {
                        "average_response_time": 150 + (hash(region + str(datetime.now().minute)) % 100),
                        "error_rate": max(0, (hash(region + str(datetime.now().second)) % 10) / 100),
                        "throughput": 100 + (hash(region + str(datetime.now().hour)) % 50)
                    }

                    self.performance_metrics[region] = region_metrics

                await asyncio.sleep(120)  # Check every 2 minutes

            except Exception as e:
                self.logger.error(f"Error in performance monitoring: {str(e)}")
                await asyncio.sleep(180)

    async def _cleanup_expired_data(self):
        """Limpieza de datos expirados"""
        while self.is_running:
            try:
                # Limpiar historial de escalado antiguo (más de 24 horas)
                cutoff_time = datetime.now() - timedelta(hours=24)
                self.scaling_history = [
                    entry for entry in self.scaling_history
                    if datetime.fromisoformat(entry["timestamp"]) > cutoff_time
                ]

                await asyncio.sleep(3600)  # Cleanup every hour

            except Exception as e:
                self.logger.error(f"Error in data cleanup: {str(e)}")
                await asyncio.sleep(3600)

    # Métodos de utilidad

    async def _get_average_cluster_load(self) -> float:
        """Obtener carga promedio del cluster"""
        total_load = 0
        total_nodes = 0

        for region_nodes in self.enterprise_nodes.values():
            for node in region_nodes:
                if node.health_status == RegionHealth.HEALTHY:
                    total_load += node.current_load
                    total_nodes += 1

        return total_load / max(total_nodes, 1)

    async def _get_threat_queue_size(self) -> int:
        """Simular tamaño de cola de amenazas"""
        # En implementación real, esto consultaría el sistema de colas
        return hash(str(datetime.now().minute)) % 100

    def _estimate_processing_time(self, node: EnterpriseNode, hrm_analysis: Dict) -> int:
        """Estimar tiempo de procesamiento en milisegundos"""
        base_time = 200  # 200ms base
        load_multiplier = 1 + node.current_load
        complexity_multiplier = 1.0

        # Ajustar por complejidad de análisis
        threat_level = hrm_analysis.get("hrm_analysis", {}).get("final_assessment", {}).get("threat_level", "MEDIUM")
        if threat_level == "CRITICAL":
            complexity_multiplier = 1.5
        elif threat_level == "HIGH":
            complexity_multiplier = 1.3

        return int(base_time * load_multiplier * complexity_multiplier)

    def _calculate_business_weight(self, business_context: Dict) -> float:
        """Calcular peso de contexto empresarial"""
        weight = 0.5  # Base weight

        asset_criticality = business_context.get("asset_criticality", "medium")
        if asset_criticality == "critical":
            weight += 0.3
        elif asset_criticality == "high":
            weight += 0.2

        compliance_frameworks = business_context.get("compliance_frameworks", [])
        if any(framework in ["SOX", "HIPAA", "PCI-DSS"] for framework in compliance_frameworks):
            weight += 0.2

        return min(weight, 1.0)

    def _assess_business_impact(self, hrm_analysis: Dict, business_context: Dict) -> Dict:
        """Evaluar impacto empresarial"""
        threat_level = hrm_analysis.get("hrm_analysis", {}).get("final_assessment", {}).get("threat_level", "MEDIUM")
        business_unit = business_context.get("business_unit", "unknown")
        asset_criticality = business_context.get("asset_criticality", "medium")

        impact_score = 0

        # Factor de nivel de amenaza
        if threat_level == "CRITICAL":
            impact_score += 40
        elif threat_level == "HIGH":
            impact_score += 25
        elif threat_level == "MEDIUM":
            impact_score += 15

        # Factor de criticidad de activo
        if asset_criticality == "critical":
            impact_score += 30
        elif asset_criticality == "high":
            impact_score += 20
        elif asset_criticality == "medium":
            impact_score += 10

        # Factor de unidad de negocio
        if business_unit in ["finance", "healthcare"]:
            impact_score += 20
        elif business_unit == "technology":
            impact_score += 15
        else:
            impact_score += 10

        # Determinar nivel de impacto
        if impact_score >= 80:
            impact_level = "CRITICAL"
        elif impact_score >= 60:
            impact_level = "HIGH"
        elif impact_score >= 40:
            impact_level = "MEDIUM"
        else:
            impact_level = "LOW"

        return {
            "impact_level": impact_level,
            "impact_score": impact_score,
            "business_factors": {
                "threat_contribution": threat_level,
                "asset_contribution": asset_criticality,
                "business_unit_contribution": business_unit
            },
            "estimated_financial_impact": self._estimate_financial_impact(impact_level),
            "recommended_response_time": self._get_recommended_response_time(impact_level)
        }

    def _estimate_financial_impact(self, impact_level: str) -> Dict:
        """Estimar impacto financiero"""
        impact_ranges = {
            "CRITICAL": {"min": 100000, "max": 1000000, "currency": "USD"},
            "HIGH": {"min": 25000, "max": 100000, "currency": "USD"},
            "MEDIUM": {"min": 5000, "max": 25000, "currency": "USD"},
            "LOW": {"min": 1000, "max": 5000, "currency": "USD"}
        }

        return impact_ranges.get(impact_level, {"min": 0, "max": 1000, "currency": "USD"})

    def _get_recommended_response_time(self, impact_level: str) -> str:
        """Obtener tiempo de respuesta recomendado"""
        response_times = {
            "CRITICAL": "< 15 minutes",
            "HIGH": "< 1 hour",
            "MEDIUM": "< 4 hours",
            "LOW": "< 24 hours"
        }

        return response_times.get(impact_level, "< 24 hours")

    async def get_orchestrator_status(self) -> Dict:
        """Obtener estado completo del orquestador"""
        return {
            "orchestrator_status": "running" if self.is_running else "stopped",
            "timestamp": datetime.now().isoformat(),
            "regions": {
                region: {
                    "health": health.value,
                    "nodes": len(nodes),
                    "healthy_nodes": sum(1 for node in nodes if node.health_status == RegionHealth.HEALTHY),
                    "average_load": sum(node.current_load for node in nodes) / len(nodes) if nodes else 0
                }
                for region, (health, nodes) in zip(self.region_health.items(), self.enterprise_nodes.values())
            },
            "performance_metrics": self.performance_metrics,
            "scaling_history_count": len(self.scaling_history),
            "recent_scaling_actions": self.scaling_history[-5:] if self.scaling_history else [],
            "cluster_average_load": await self._get_average_cluster_load(),
            "estimated_threat_queue_size": await self._get_threat_queue_size()
        }

# Factory function
def create_mcp_enterprise_orchestrator(config: Optional[Dict] = None) -> MCPEnterpriseOrchestrator:
    """
    Factory function para crear instancia del orquestador Enterprise
    """
    return MCPEnterpriseOrchestrator(config)

# Ejemplo de uso básico
if __name__ == "__main__":
    async def test_orchestrator():
        orchestrator = create_mcp_enterprise_orchestrator()

        # Iniciar orquestación
        await orchestrator.start_orchestration()

        # Test de procesamiento de amenaza empresarial
        test_threat = {
            "event_id": "enterprise_test_001",
            "timestamp": datetime.now().isoformat(),
            "event_type": "advanced_persistent_threat",
            "source_ip": "10.0.1.50",
            "target_system": "financial_db_server",
            "severity": "high"
        }

        test_business_context = {
            "business_unit": "finance",
            "compliance_frameworks": ["SOX", "PCI-DSS"],
            "asset_criticality": "critical",
            "risk_tolerance": "low",
            "user_privileges": "admin"
        }

        # Procesar amenaza
        result = await orchestrator.process_enterprise_threat(test_threat, test_business_context)
        print("Enterprise Threat Processing Result:")
        print(json.dumps(result, indent=2))

        # Obtener estado del orquestador
        status = await orchestrator.get_orchestrator_status()
        print("\nOrchestrator Status:")
        print(json.dumps(status, indent=2))

        # Esperar un poco para ver el monitoreo en acción
        await asyncio.sleep(5)

        # Detener orquestación
        await orchestrator.stop_orchestration()

    # Ejecutar test
    asyncio.run(test_orchestrator())