#!/usr/bin/env python3
"""
Multi-XDR Response Engine
Motor de respuestas coordinadas para múltiples plataformas XDR
Orquesta respuestas automáticas basadas en análisis HRM + contexto empresarial
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

from xdr_mcp_coordinators import (
    XDRMCPCoordinator, XDRPlatform, XDRResponse, ExportPriority,
    create_xdr_mcp_coordinator
)

class ResponseAction(Enum):
    BLOCK_IP = "block_ip"
    QUARANTINE_HOST = "quarantine_host"
    DISABLE_USER = "disable_user"
    ISOLATE_ENDPOINT = "isolate_endpoint"
    BLOCK_DOMAIN = "block_domain"
    ALERT_ESCALATE = "alert_escalate"
    FORENSIC_COLLECT = "forensic_collect"
    THREAT_HUNT = "threat_hunt"
    NOTIFICATION_SEND = "notification_send"

class ResponseUrgency(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5

@dataclass
class ResponseTask:
    """Tarea de respuesta automatizada"""
    task_id: str
    action: ResponseAction
    target_platforms: List[XDRPlatform]
    urgency: ResponseUrgency
    parameters: Dict[str, Any]
    business_context: Dict[str, Any]
    hrm_justification: Dict[str, Any]
    created_at: datetime
    timeout_seconds: int = 300
    requires_approval: bool = False
    status: str = "pending"
    results: List[Dict] = None

    def __post_init__(self):
        if self.results is None:
            self.results = []

@dataclass
class CoordinatedResponse:
    """Respuesta coordinada multi-XDR"""
    response_id: str
    trigger_event: Dict[str, Any]
    hrm_analysis: Dict[str, Any]
    business_context: Dict[str, Any]
    response_tasks: List[ResponseTask]
    coordination_strategy: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    overall_status: str = "initializing"
    success_rate: float = 0.0
    execution_summary: Dict[str, Any] = None

    def __post_init__(self):
        if self.execution_summary is None:
            self.execution_summary = {}

class MultiXDRResponseEngine:
    """Motor de respuestas coordinadas multi-XDR"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("MultiXDRResponseEngine")

        # Coordinador XDR
        self.xdr_coordinator = create_xdr_mcp_coordinator(config.get("xdr_config", {}))

        # Configuración de respuestas automáticas
        self.response_config = config.get("response_config", self._default_response_config())

        # Estado del motor
        self.active_responses = {}
        self.completed_responses = []
        self.response_history = []

        # Workers para procesamiento
        self.is_running = False
        self.response_workers = []

    def _default_response_config(self) -> Dict:
        """Configuración por defecto de respuestas"""
        return {
            "auto_response_enabled": True,
            "approval_required_for": ["QUARANTINE_HOST", "DISABLE_USER"],
            "max_concurrent_responses": 10,
            "response_timeout_seconds": 300,
            "escalation_thresholds": {
                "critical_asset": "EMERGENCY",
                "high_confidence": "CRITICAL",
                "compliance_required": "HIGH"
            },
            "platform_capabilities": {
                "crowdstrike": [
                    "BLOCK_IP", "QUARANTINE_HOST", "ISOLATE_ENDPOINT",
                    "FORENSIC_COLLECT", "THREAT_HUNT"
                ],
                "sentinel": [
                    "ALERT_ESCALATE", "THREAT_HUNT", "NOTIFICATION_SEND",
                    "FORENSIC_COLLECT"
                ],
                "cisco_umbrella": [
                    "BLOCK_DOMAIN", "BLOCK_IP", "ALERT_ESCALATE"
                ]
            }
        }

    async def start_response_engine(self):
        """Iniciar motor de respuestas"""
        self.logger.info("Starting Multi-XDR Response Engine")
        self.is_running = True

        # Iniciar coordinador XDR
        await self.xdr_coordinator.start_coordination()

        # Iniciar workers de respuesta
        num_workers = self.config.get("num_response_workers", 3)
        for i in range(num_workers):
            worker = asyncio.create_task(self._response_worker(f"response-worker-{i}"))
            self.response_workers.append(worker)

        self.logger.info(f"Started {num_workers} response workers")

    async def stop_response_engine(self):
        """Detener motor de respuestas"""
        self.logger.info("Stopping Multi-XDR Response Engine")
        self.is_running = False

        # Detener workers
        for worker in self.response_workers:
            worker.cancel()

        await asyncio.gather(*self.response_workers, return_exceptions=True)

        # Detener coordinador XDR
        await self.xdr_coordinator.stop_coordination()

        self.logger.info("Multi-XDR Response Engine stopped")

    async def coordinate_threat_response(self, threat_event: Dict, hrm_analysis: Dict,
                                       business_context: Dict) -> CoordinatedResponse:
        """Coordinar respuesta automática a amenaza"""

        response_id = f"response_{datetime.now().timestamp()}_{hashlib.md5(str(threat_event.get('event_id', '')).encode()).hexdigest()[:8]}"

        self.logger.info(f"Initiating coordinated response: {response_id}")

        # 1. Análizar necesidad de respuesta automática
        response_necessity = self._analyze_response_necessity(
            hrm_analysis, business_context
        )

        if not response_necessity["requires_response"]:
            self.logger.info(f"No automated response required for {response_id}")
            return CoordinatedResponse(
                response_id=response_id,
                trigger_event=threat_event,
                hrm_analysis=hrm_analysis,
                business_context=business_context,
                response_tasks=[],
                coordination_strategy="no_response",
                created_at=datetime.now(),
                overall_status="completed",
                success_rate=1.0
            )

        # 2. Generar tareas de respuesta basadas en HRM + contexto
        response_tasks = await self._generate_response_tasks(
            threat_event, hrm_analysis, business_context, response_necessity
        )

        # 3. Determinar estrategia de coordinación
        coordination_strategy = self._determine_coordination_strategy(
            response_tasks, business_context
        )

        # 4. Crear respuesta coordinada
        coordinated_response = CoordinatedResponse(
            response_id=response_id,
            trigger_event=threat_event,
            hrm_analysis=hrm_analysis,
            business_context=business_context,
            response_tasks=response_tasks,
            coordination_strategy=coordination_strategy,
            created_at=datetime.now(),
            overall_status="executing"
        )

        # 5. Registrar y ejecutar
        self.active_responses[response_id] = coordinated_response

        # 6. Ejecutar respuesta coordinada
        await self._execute_coordinated_response(coordinated_response)

        return coordinated_response

    def _analyze_response_necessity(self, hrm_analysis: Dict, business_context: Dict) -> Dict:
        """Analizar si se requiere respuesta automática"""
        threat_level = hrm_analysis.get("hrm_analysis", {}).get("final_assessment", {}).get("threat_level", "MEDIUM")
        confidence = hrm_analysis.get("hrm_analysis", {}).get("final_assessment", {}).get("confidence", 0.5)
        false_positive_score = hrm_analysis.get("hrm_analysis", {}).get("analysis_modules", {}).get("ml_false_positive", {}).get("score", 0.5)

        asset_criticality = business_context.get("asset_criticality", "medium")
        business_unit = business_context.get("business_unit", "unknown")
        compliance_frameworks = business_context.get("compliance_frameworks", [])

        # Lógica de decisión para respuesta automática
        requires_response = False
        response_reasoning = []

        # Criterios basados en amenaza
        if threat_level == "CRITICAL" and confidence > 0.85:
            requires_response = True
            response_reasoning.append("Critical threat with high confidence")

        elif threat_level == "HIGH" and confidence > 0.75 and false_positive_score < 0.3:
            requires_response = True
            response_reasoning.append("High threat with high confidence and low false positive probability")

        # Criterios basados en contexto empresarial
        if asset_criticality == "critical":
            requires_response = True
            response_reasoning.append("Critical asset involved")

        if business_unit in ["finance", "healthcare"] and threat_level in ["HIGH", "CRITICAL"]:
            requires_response = True
            response_reasoning.append("Critical business unit affected")

        # Criterios de compliance
        if any(framework in ["SOX", "HIPAA", "PCI-DSS"] for framework in compliance_frameworks):
            if threat_level in ["HIGH", "CRITICAL"]:
                requires_response = True
                response_reasoning.append("Compliance-regulated environment requires response")

        # Override por configuración
        if not self.response_config.get("auto_response_enabled", True):
            requires_response = False
            response_reasoning = ["Automated response disabled in configuration"]

        return {
            "requires_response": requires_response,
            "reasoning": response_reasoning,
            "threat_factors": {
                "level": threat_level,
                "confidence": confidence,
                "false_positive_score": false_positive_score
            },
            "business_factors": {
                "asset_criticality": asset_criticality,
                "business_unit": business_unit,
                "compliance": compliance_frameworks
            }
        }

    async def _generate_response_tasks(self, threat_event: Dict, hrm_analysis: Dict,
                                     business_context: Dict, response_necessity: Dict) -> List[ResponseTask]:
        """Generar tareas de respuesta basadas en análisis"""

        tasks = []
        threat_level = hrm_analysis.get("hrm_analysis", {}).get("final_assessment", {}).get("threat_level", "MEDIUM")
        confidence = hrm_analysis.get("hrm_analysis", {}).get("final_assessment", {}).get("confidence", 0.5)

        # Determinar urgencia general
        urgency = self._calculate_response_urgency(hrm_analysis, business_context)

        # Extraer indicadores de amenaza
        source_ip = threat_event.get("source_ip")
        target_host = threat_event.get("target_host")
        affected_user = threat_event.get("affected_user")
        suspicious_domain = threat_event.get("domain")

        # Generar tareas específicas según tipo de amenaza y contexto

        # 1. Bloqueo de IP maliciosa
        if source_ip and confidence > 0.7:
            platforms = self._select_platforms_for_action(ResponseAction.BLOCK_IP)
            if platforms:
                task = ResponseTask(
                    task_id=f"block_ip_{source_ip}_{datetime.now().timestamp()}",
                    action=ResponseAction.BLOCK_IP,
                    target_platforms=platforms,
                    urgency=urgency,
                    parameters={
                        "ip_address": source_ip,
                        "duration_hours": self._calculate_block_duration(threat_level),
                        "reason": f"SmartCompute HRM detected {threat_level} threat"
                    },
                    business_context=business_context,
                    hrm_justification={
                        "threat_level": threat_level,
                        "confidence": confidence,
                        "analysis_modules": hrm_analysis.get("hrm_analysis", {}).get("analysis_modules", {})
                    },
                    created_at=datetime.now()
                )
                tasks.append(task)

        # 2. Cuarentena de endpoint
        if target_host and threat_level in ["CRITICAL", "HIGH"] and confidence > 0.8:
            platforms = self._select_platforms_for_action(ResponseAction.QUARANTINE_HOST)
            if platforms:
                task = ResponseTask(
                    task_id=f"quarantine_{target_host}_{datetime.now().timestamp()}",
                    action=ResponseAction.QUARANTINE_HOST,
                    target_platforms=platforms,
                    urgency=urgency,
                    parameters={
                        "hostname": target_host,
                        "isolation_level": "full" if threat_level == "CRITICAL" else "partial"
                    },
                    business_context=business_context,
                    hrm_justification={
                        "threat_level": threat_level,
                        "confidence": confidence
                    },
                    created_at=datetime.now(),
                    requires_approval=True  # Requiere aprobación para cuarentena
                )
                tasks.append(task)

        # 3. Bloqueo de dominio sospechoso
        if suspicious_domain and confidence > 0.6:
            platforms = self._select_platforms_for_action(ResponseAction.BLOCK_DOMAIN)
            if platforms:
                task = ResponseTask(
                    task_id=f"block_domain_{suspicious_domain}_{datetime.now().timestamp()}",
                    action=ResponseAction.BLOCK_DOMAIN,
                    target_platforms=platforms,
                    urgency=urgency,
                    parameters={
                        "domain": suspicious_domain,
                        "block_subdomains": True
                    },
                    business_context=business_context,
                    hrm_justification={
                        "threat_level": threat_level,
                        "confidence": confidence
                    },
                    created_at=datetime.now()
                )
                tasks.append(task)

        # 4. Escalación de alerta para amenazas críticas
        if threat_level == "CRITICAL" or business_context.get("asset_criticality") == "critical":
            platforms = self._select_platforms_for_action(ResponseAction.ALERT_ESCALATE)
            if platforms:
                task = ResponseTask(
                    task_id=f"escalate_alert_{datetime.now().timestamp()}",
                    action=ResponseAction.ALERT_ESCALATE,
                    target_platforms=platforms,
                    urgency=ResponseUrgency.CRITICAL,
                    parameters={
                        "escalation_level": "P1_CRITICAL",
                        "notify_channels": ["email", "sms", "slack"],
                        "stakeholders": self._get_escalation_stakeholders(business_context)
                    },
                    business_context=business_context,
                    hrm_justification={
                        "threat_level": threat_level,
                        "confidence": confidence
                    },
                    created_at=datetime.now()
                )
                tasks.append(task)

        # 5. Recolección forense para análisis posterior
        if threat_level in ["CRITICAL", "HIGH"] and confidence > 0.75:
            platforms = self._select_platforms_for_action(ResponseAction.FORENSIC_COLLECT)
            if platforms:
                task = ResponseTask(
                    task_id=f"forensic_collect_{datetime.now().timestamp()}",
                    action=ResponseAction.FORENSIC_COLLECT,
                    target_platforms=platforms,
                    urgency=urgency,
                    parameters={
                        "collection_scope": "targeted" if threat_level == "HIGH" else "comprehensive",
                        "preserve_evidence": True,
                        "include_network_logs": True,
                        "include_process_dumps": True
                    },
                    business_context=business_context,
                    hrm_justification={
                        "threat_level": threat_level,
                        "confidence": confidence
                    },
                    created_at=datetime.now()
                )
                tasks.append(task)

        # 6. Threat Hunting proactivo
        threat_intel = hrm_analysis.get("hrm_analysis", {}).get("analysis_modules", {}).get("threat_intelligence", {})
        if threat_intel.get("category") in ["apt", "advanced_persistent_threat"] and confidence > 0.7:
            platforms = self._select_platforms_for_action(ResponseAction.THREAT_HUNT)
            if platforms:
                task = ResponseTask(
                    task_id=f"threat_hunt_{datetime.now().timestamp()}",
                    action=ResponseAction.THREAT_HUNT,
                    target_platforms=platforms,
                    urgency=ResponseUrgency.HIGH,
                    parameters={
                        "hunt_scope": "organization_wide",
                        "iocs": self._extract_iocs_from_analysis(hrm_analysis),
                        "hunt_duration_days": 7,
                        "focus_areas": ["lateral_movement", "data_exfiltration", "persistence"]
                    },
                    business_context=business_context,
                    hrm_justification={
                        "threat_category": threat_intel.get("category"),
                        "confidence": confidence
                    },
                    created_at=datetime.now()
                )
                tasks.append(task)

        return tasks

    def _calculate_response_urgency(self, hrm_analysis: Dict, business_context: Dict) -> ResponseUrgency:
        """Calcular urgencia de respuesta"""
        threat_level = hrm_analysis.get("hrm_analysis", {}).get("final_assessment", {}).get("threat_level", "MEDIUM")
        confidence = hrm_analysis.get("hrm_analysis", {}).get("final_assessment", {}).get("confidence", 0.5)
        asset_criticality = business_context.get("asset_criticality", "medium")

        # Lógica de urgencia
        if threat_level == "CRITICAL" and confidence > 0.9:
            return ResponseUrgency.EMERGENCY
        elif threat_level == "CRITICAL" or (threat_level == "HIGH" and confidence > 0.8):
            return ResponseUrgency.CRITICAL
        elif threat_level == "HIGH" or asset_criticality == "critical":
            return ResponseUrgency.HIGH
        elif threat_level == "MEDIUM" or asset_criticality == "high":
            return ResponseUrgency.MEDIUM
        else:
            return ResponseUrgency.LOW

    def _select_platforms_for_action(self, action: ResponseAction) -> List[XDRPlatform]:
        """Seleccionar plataformas capaces de ejecutar acción"""
        platform_capabilities = self.response_config["platform_capabilities"]
        selected_platforms = []

        for platform_name, capabilities in platform_capabilities.items():
            if action.value.upper() in capabilities:
                try:
                    platform_enum = XDRPlatform(platform_name)
                    # Verificar que el coordinador tiene esta plataforma configurada
                    if platform_enum in self.xdr_coordinator.coordinators:
                        selected_platforms.append(platform_enum)
                except ValueError:
                    continue

        return selected_platforms

    def _calculate_block_duration(self, threat_level: str) -> int:
        """Calcular duración de bloqueo en horas"""
        duration_map = {
            "CRITICAL": 72,   # 3 días
            "HIGH": 48,       # 2 días
            "MEDIUM": 24,     # 1 día
            "LOW": 12         # 12 horas
        }
        return duration_map.get(threat_level, 24)

    def _get_escalation_stakeholders(self, business_context: Dict) -> List[str]:
        """Obtener stakeholders para escalación"""
        stakeholders = ["security_team@company.com"]

        business_unit = business_context.get("business_unit", "unknown")
        if business_unit == "finance":
            stakeholders.extend(["cfo@company.com", "finance_security@company.com"])
        elif business_unit == "healthcare":
            stakeholders.extend(["compliance@company.com", "privacy_officer@company.com"])

        compliance = business_context.get("compliance_frameworks", [])
        if "SOX" in compliance:
            stakeholders.append("sox_compliance@company.com")
        if "HIPAA" in compliance:
            stakeholders.append("hipaa_officer@company.com")

        return stakeholders

    def _extract_iocs_from_analysis(self, hrm_analysis: Dict) -> List[Dict]:
        """Extraer IOCs del análisis HRM"""
        iocs = []

        threat_intel = hrm_analysis.get("hrm_analysis", {}).get("analysis_modules", {}).get("threat_intelligence", {})
        indicators = threat_intel.get("indicators", [])

        for indicator in indicators:
            ioc = {
                "type": indicator.get("type", "unknown"),
                "value": indicator.get("value", ""),
                "confidence": indicator.get("confidence", 0.5),
                "description": f"Detected by SmartCompute HRM: {indicator.get('description', '')}"
            }
            iocs.append(ioc)

        return iocs

    def _determine_coordination_strategy(self, response_tasks: List[ResponseTask],
                                       business_context: Dict) -> str:
        """Determinar estrategia de coordinación"""
        if not response_tasks:
            return "no_response"

        # Analizar urgencia y dependencias
        max_urgency = max(task.urgency.value for task in response_tasks)
        has_approval_required = any(task.requires_approval for task in response_tasks)

        if max_urgency >= ResponseUrgency.CRITICAL.value:
            if has_approval_required:
                return "critical_with_approval"
            else:
                return "critical_immediate"
        elif max_urgency >= ResponseUrgency.HIGH.value:
            return "high_priority_parallel"
        else:
            return "standard_sequential"

    async def _execute_coordinated_response(self, coordinated_response: CoordinatedResponse):
        """Ejecutar respuesta coordinada"""
        response_id = coordinated_response.response_id
        self.logger.info(f"Executing coordinated response: {response_id}")

        try:
            coordinated_response.overall_status = "executing"

            # Ejecutar según estrategia de coordinación
            if coordinated_response.coordination_strategy == "critical_immediate":
                await self._execute_parallel_immediate(coordinated_response)

            elif coordinated_response.coordination_strategy == "critical_with_approval":
                await self._execute_with_approval_flow(coordinated_response)

            elif coordinated_response.coordination_strategy == "high_priority_parallel":
                await self._execute_parallel_prioritized(coordinated_response)

            elif coordinated_response.coordination_strategy == "standard_sequential":
                await self._execute_sequential(coordinated_response)

            # Calcular éxito general
            successful_tasks = sum(1 for task in coordinated_response.response_tasks
                                 if task.status == "completed")
            total_tasks = len(coordinated_response.response_tasks)
            coordinated_response.success_rate = successful_tasks / max(total_tasks, 1)

            # Completar respuesta
            coordinated_response.completed_at = datetime.now()
            coordinated_response.overall_status = "completed"

            # Generar resumen de ejecución
            coordinated_response.execution_summary = self._generate_execution_summary(
                coordinated_response
            )

            # Mover a completadas
            if response_id in self.active_responses:
                del self.active_responses[response_id]
            self.completed_responses.append(coordinated_response)

            self.logger.info(f"Coordinated response completed: {response_id} "
                           f"(Success rate: {coordinated_response.success_rate:.2%})")

        except Exception as e:
            self.logger.error(f"Error executing coordinated response {response_id}: {str(e)}")
            coordinated_response.overall_status = "failed"
            coordinated_response.execution_summary = {
                "error": str(e),
                "failed_at": datetime.now().isoformat()
            }

    async def _execute_parallel_immediate(self, coordinated_response: CoordinatedResponse):
        """Ejecutar tareas en paralelo inmediatamente (crítico)"""
        tasks_coroutines = []

        for task in coordinated_response.response_tasks:
            if not task.requires_approval:
                coroutine = self._execute_single_task(task)
                tasks_coroutines.append(coroutine)

        # Ejecutar todas en paralelo
        await asyncio.gather(*tasks_coroutines, return_exceptions=True)

        # Tareas que requieren aprobación se marcan como pendientes
        for task in coordinated_response.response_tasks:
            if task.requires_approval:
                task.status = "pending_approval"

    async def _execute_with_approval_flow(self, coordinated_response: CoordinatedResponse):
        """Ejecutar con flujo de aprobación"""
        # Ejecutar tareas que no requieren aprobación inmediatamente
        immediate_tasks = [task for task in coordinated_response.response_tasks
                          if not task.requires_approval]
        approval_tasks = [task for task in coordinated_response.response_tasks
                         if task.requires_approval]

        # Paralelo para tareas inmediatas
        immediate_coroutines = [self._execute_single_task(task) for task in immediate_tasks]
        await asyncio.gather(*immediate_coroutines, return_exceptions=True)

        # Simular flujo de aprobación (en producción integrar con sistema real)
        for task in approval_tasks:
            approval_granted = await self._simulate_approval_process(task)
            if approval_granted:
                await self._execute_single_task(task)
            else:
                task.status = "approval_denied"

    async def _execute_parallel_prioritized(self, coordinated_response: CoordinatedResponse):
        """Ejecutar en paralelo con priorización"""
        # Ordenar por urgencia
        sorted_tasks = sorted(coordinated_response.response_tasks,
                            key=lambda t: t.urgency.value, reverse=True)

        # Ejecutar en lotes por urgencia
        current_urgency = None
        current_batch = []

        for task in sorted_tasks:
            if task.urgency != current_urgency:
                # Ejecutar lote anterior
                if current_batch:
                    batch_coroutines = [self._execute_single_task(task) for task in current_batch]
                    await asyncio.gather(*batch_coroutines, return_exceptions=True)

                current_urgency = task.urgency
                current_batch = [task]
            else:
                current_batch.append(task)

        # Ejecutar último lote
        if current_batch:
            batch_coroutines = [self._execute_single_task(task) for task in current_batch]
            await asyncio.gather(*batch_coroutines, return_exceptions=True)

    async def _execute_sequential(self, coordinated_response: CoordinatedResponse):
        """Ejecutar secuencialmente (estándar)"""
        for task in coordinated_response.response_tasks:
            await self._execute_single_task(task)

    async def _execute_single_task(self, task: ResponseTask):
        """Ejecutar tarea individual de respuesta"""
        self.logger.info(f"Executing response task: {task.task_id} ({task.action.value})")

        try:
            task.status = "executing"
            start_time = datetime.now()

            # Ejecutar según tipo de acción
            if task.action == ResponseAction.BLOCK_IP:
                result = await self._execute_block_ip(task)

            elif task.action == ResponseAction.QUARANTINE_HOST:
                result = await self._execute_quarantine_host(task)

            elif task.action == ResponseAction.BLOCK_DOMAIN:
                result = await self._execute_block_domain(task)

            elif task.action == ResponseAction.ALERT_ESCALATE:
                result = await self._execute_alert_escalation(task)

            elif task.action == ResponseAction.FORENSIC_COLLECT:
                result = await self._execute_forensic_collection(task)

            elif task.action == ResponseAction.THREAT_HUNT:
                result = await self._execute_threat_hunt(task)

            else:
                result = {"success": False, "error": f"Unsupported action: {task.action}"}

            # Actualizar resultado
            execution_time = (datetime.now() - start_time).total_seconds()
            task.results.append({
                "timestamp": start_time.isoformat(),
                "execution_time_seconds": execution_time,
                "result": result
            })

            task.status = "completed" if result.get("success") else "failed"

            self.logger.info(f"Task {task.task_id} {'completed' if result.get('success') else 'failed'} "
                           f"in {execution_time:.2f}s")

        except Exception as e:
            task.status = "error"
            task.results.append({
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            })
            self.logger.error(f"Error executing task {task.task_id}: {str(e)}")

    async def _execute_block_ip(self, task: ResponseTask) -> Dict:
        """Ejecutar bloqueo de IP"""
        ip_address = task.parameters.get("ip_address")
        duration_hours = task.parameters.get("duration_hours", 24)

        results = []
        for platform in task.target_platforms:
            if platform == XDRPlatform.CROWDSTRIKE:
                # Simular bloqueo en CrowdStrike
                result = {
                    "platform": "crowdstrike",
                    "action": "ip_block",
                    "ip": ip_address,
                    "duration": f"{duration_hours}h",
                    "block_id": f"cs_block_{hashlib.md5(ip_address.encode()).hexdigest()[:8]}",
                    "success": True
                }
                results.append(result)

            elif platform == XDRPlatform.CISCO_UMBRELLA:
                # Simular bloqueo en Cisco Umbrella
                result = {
                    "platform": "cisco_umbrella",
                    "action": "ip_block",
                    "ip": ip_address,
                    "policy_applied": "SmartCompute_AutoBlock",
                    "success": True
                }
                results.append(result)

        return {
            "success": all(r.get("success", False) for r in results),
            "platform_results": results,
            "blocked_ip": ip_address,
            "duration_hours": duration_hours
        }

    async def _execute_quarantine_host(self, task: ResponseTask) -> Dict:
        """Ejecutar cuarentena de host"""
        hostname = task.parameters.get("hostname")
        isolation_level = task.parameters.get("isolation_level", "partial")

        # Simular cuarentena en CrowdStrike
        if XDRPlatform.CROWDSTRIKE in task.target_platforms:
            result = {
                "platform": "crowdstrike",
                "action": "host_quarantine",
                "hostname": hostname,
                "isolation_level": isolation_level,
                "quarantine_id": f"cs_quarantine_{hashlib.md5(hostname.encode()).hexdigest()[:8]}",
                "success": True
            }

            return {
                "success": True,
                "platform_results": [result],
                "quarantined_host": hostname
            }

        return {"success": False, "error": "No capable platforms configured"}

    async def _execute_block_domain(self, task: ResponseTask) -> Dict:
        """Ejecutar bloqueo de dominio"""
        domain = task.parameters.get("domain")
        block_subdomains = task.parameters.get("block_subdomains", True)

        # Simular bloqueo en Cisco Umbrella
        if XDRPlatform.CISCO_UMBRELLA in task.target_platforms:
            result = {
                "platform": "cisco_umbrella",
                "action": "domain_block",
                "domain": domain,
                "include_subdomains": block_subdomains,
                "policy_id": f"umbrella_block_{hashlib.md5(domain.encode()).hexdigest()[:8]}",
                "success": True
            }

            return {
                "success": True,
                "platform_results": [result],
                "blocked_domain": domain
            }

        return {"success": False, "error": "No capable platforms configured"}

    async def _execute_alert_escalation(self, task: ResponseTask) -> Dict:
        """Ejecutar escalación de alerta"""
        escalation_level = task.parameters.get("escalation_level", "P2_HIGH")
        notify_channels = task.parameters.get("notify_channels", ["email"])
        stakeholders = task.parameters.get("stakeholders", [])

        # Simular escalación
        notifications_sent = []
        for channel in notify_channels:
            for stakeholder in stakeholders:
                notification = {
                    "channel": channel,
                    "recipient": stakeholder,
                    "escalation_level": escalation_level,
                    "sent_at": datetime.now().isoformat(),
                    "success": True
                }
                notifications_sent.append(notification)

        return {
            "success": True,
            "escalation_level": escalation_level,
            "notifications_sent": notifications_sent,
            "total_notifications": len(notifications_sent)
        }

    async def _execute_forensic_collection(self, task: ResponseTask) -> Dict:
        """Ejecutar recolección forense"""
        collection_scope = task.parameters.get("collection_scope", "targeted")

        # Simular recolección forense
        collected_artifacts = [
            "system_memory_dump",
            "network_connection_logs",
            "process_execution_history",
            "file_system_changes"
        ]

        if collection_scope == "comprehensive":
            collected_artifacts.extend([
                "registry_changes",
                "event_logs_complete",
                "network_packet_captures"
            ])

        return {
            "success": True,
            "collection_scope": collection_scope,
            "artifacts_collected": collected_artifacts,
            "collection_id": f"forensic_{datetime.now().timestamp()}",
            "storage_location": f"s3://forensic-bucket/smartcompute/{task.task_id}/"
        }

    async def _execute_threat_hunt(self, task: ResponseTask) -> Dict:
        """Ejecutar threat hunting"""
        hunt_scope = task.parameters.get("hunt_scope", "targeted")
        iocs = task.parameters.get("iocs", [])
        hunt_duration_days = task.parameters.get("hunt_duration_days", 7)

        # Simular threat hunt
        hunt_results = {
            "hunt_id": f"hunt_{datetime.now().timestamp()}",
            "scope": hunt_scope,
            "iocs_searched": len(iocs),
            "duration_days": hunt_duration_days,
            "matches_found": len(iocs) * 2,  # Simular algunos matches
            "false_positives": 1,
            "confirmed_threats": len(iocs),
            "additional_iocs_discovered": ["192.168.1.99", "suspicious.domain.com"],
            "hunt_status": "completed"
        }

        return {
            "success": True,
            "hunt_results": hunt_results
        }

    async def _simulate_approval_process(self, task: ResponseTask) -> bool:
        """Simular proceso de aprobación"""
        # En producción, esto integraría con sistema real de aprobaciones
        self.logger.info(f"Simulating approval process for task: {task.task_id}")

        # Simular tiempo de aprobación
        await asyncio.sleep(1)

        # Simular aprobación automática para demo (90% aprobado)
        import random
        return random.random() > 0.1

    def _generate_execution_summary(self, coordinated_response: CoordinatedResponse) -> Dict:
        """Generar resumen de ejecución"""
        total_tasks = len(coordinated_response.response_tasks)
        completed_tasks = sum(1 for task in coordinated_response.response_tasks
                             if task.status == "completed")
        failed_tasks = sum(1 for task in coordinated_response.response_tasks
                          if task.status in ["failed", "error"])

        execution_time = 0
        if coordinated_response.completed_at and coordinated_response.created_at:
            execution_time = (coordinated_response.completed_at -
                            coordinated_response.created_at).total_seconds()

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "success_rate": coordinated_response.success_rate,
            "execution_time_seconds": execution_time,
            "coordination_strategy": coordinated_response.coordination_strategy,
            "platforms_used": list(set(
                platform.value for task in coordinated_response.response_tasks
                for platform in task.target_platforms
            )),
            "actions_executed": list(set(
                task.action.value for task in coordinated_response.response_tasks
            ))
        }

    async def _response_worker(self, worker_name: str):
        """Worker para procesamiento de respuestas (reservado para futuro uso)"""
        self.logger.debug(f"Response worker started: {worker_name}")

        while self.is_running:
            await asyncio.sleep(1)  # Placeholder

        self.logger.debug(f"Response worker stopped: {worker_name}")

    async def get_engine_status(self) -> Dict:
        """Obtener estado del motor de respuestas"""
        return {
            "engine_status": "running" if self.is_running else "stopped",
            "active_responses": len(self.active_responses),
            "completed_responses": len(self.completed_responses),
            "total_responses_processed": len(self.completed_responses) + len(self.response_history),
            "xdr_coordinator_status": await self.xdr_coordinator.get_coordination_status(),
            "recent_responses": [
                {
                    "response_id": response.response_id,
                    "trigger_event_id": response.trigger_event.get("event_id"),
                    "success_rate": response.success_rate,
                    "coordination_strategy": response.coordination_strategy,
                    "total_tasks": len(response.response_tasks),
                    "execution_time_seconds": response.execution_summary.get("execution_time_seconds", 0)
                }
                for response in self.completed_responses[-5:]  # Últimas 5
            ]
        }

# Factory function
def create_multi_xdr_response_engine(config: Optional[Dict] = None) -> MultiXDRResponseEngine:
    """Factory para crear motor de respuestas multi-XDR"""
    if config is None:
        config = {
            "xdr_config": {
                "crowdstrike": {"enabled": True},
                "sentinel": {"enabled": True},
                "cisco_umbrella": {"enabled": True}
            },
            "response_config": {
                "auto_response_enabled": True,
                "max_concurrent_responses": 10
            },
            "num_response_workers": 3
        }

    return MultiXDRResponseEngine(config)

# Ejemplo de uso
if __name__ == "__main__":
    async def test_multi_xdr_response():
        # Crear motor de respuestas
        response_engine = create_multi_xdr_response_engine()
        await response_engine.start_response_engine()

        # Evento de amenaza de prueba
        test_threat = {
            "event_id": "multi_xdr_test_001",
            "event_type": "advanced_persistent_threat",
            "source_ip": "10.0.0.50",
            "target_host": "finance-server-01",
            "affected_user": "admin@company.com",
            "domain": "malicious.example.com"
        }

        # Análisis HRM simulado
        test_hrm_analysis = {
            "hrm_analysis": {
                "final_assessment": {
                    "threat_level": "CRITICAL",
                    "confidence": 0.95
                },
                "analysis_modules": {
                    "threat_intelligence": {
                        "category": "apt",
                        "indicators": [
                            {"type": "ip", "value": "10.0.0.50", "confidence": 0.9}
                        ]
                    },
                    "behavioral_analysis": {"confidence": 0.88},
                    "ml_false_positive": {"score": 0.05}
                }
            }
        }

        # Contexto empresarial
        test_business_context = {
            "business_unit": "finance",
            "asset_criticality": "critical",
            "compliance_frameworks": ["SOX", "PCI-DSS"],
            "risk_tolerance": "very_low"
        }

        # Ejecutar respuesta coordinada
        coordinated_response = await response_engine.coordinate_threat_response(
            test_threat, test_hrm_analysis, test_business_context
        )

        print("Multi-XDR Coordinated Response Results:")
        print(f"Response ID: {coordinated_response.response_id}")
        print(f"Strategy: {coordinated_response.coordination_strategy}")
        print(f"Total Tasks: {len(coordinated_response.response_tasks)}")
        print(f"Success Rate: {coordinated_response.success_rate:.2%}")

        print("\nExecuted Tasks:")
        for task in coordinated_response.response_tasks:
            print(f"- {task.action.value}: {task.status} "
                  f"(Platforms: {[p.value for p in task.target_platforms]})")

        # Estado del motor
        status = await response_engine.get_engine_status()
        print(f"\nEngine Status:")
        print(json.dumps(status, indent=2))

        await response_engine.stop_response_engine()

    # Ejecutar test
    asyncio.run(test_multi_xdr_response())