#!/usr/bin/env python3
"""
Business Context XDR Router
Router inteligente que dirige amenazas a plataformas XDR basado en contexto empresarial
Integra análisis HRM con lógica de negocio para optimizar respuestas
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

from xdr_mcp_coordinators import XDRPlatform, ExportPriority
from multi_xdr_response_engine import ResponseAction, ResponseUrgency

class BusinessUnit(Enum):
    FINANCE = "finance"
    HEALTHCARE = "healthcare"
    TECHNOLOGY = "technology"
    MANUFACTURING = "manufacturing"
    RETAIL = "retail"
    EDUCATION = "education"
    GOVERNMENT = "government"
    UNKNOWN = "unknown"

class ComplianceFramework(Enum):
    SOX = "sox"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    GDPR = "gdpr"
    ISO27001 = "iso27001"
    NIST = "nist"
    FISMA = "fisma"
    NERC_CIP = "nerc_cip"

class AssetCriticality(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class BusinessContextProfile:
    """Perfil de contexto empresarial"""
    business_unit: BusinessUnit
    compliance_frameworks: List[ComplianceFramework]
    asset_criticality: AssetCriticality
    risk_tolerance: str  # very_low, low, medium, high
    geographical_region: str
    business_hours_active: bool
    data_classification: str  # public, internal, confidential, restricted
    regulatory_requirements: List[str]

@dataclass
class XDRRoutingDecision:
    """Decisión de enrutamiento XDR"""
    decision_id: str
    primary_platforms: List[XDRPlatform]
    secondary_platforms: List[XDRPlatform]
    routing_strategy: str
    business_justification: str
    compliance_requirements: List[str]
    export_priority: ExportPriority
    response_urgency: ResponseUrgency
    estimated_cost: float
    sla_requirements: Dict[str, Any]
    audit_trail_required: bool

class BusinessContextXDRRouter:
    """Router inteligente basado en contexto empresarial"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("BusinessContextXDRRouter")

        # Cargar perfiles de contexto empresarial
        self.business_profiles = self._load_business_profiles()

        # Matriz de capacidades por plataforma y contexto
        self.platform_capabilities_matrix = self._build_capabilities_matrix()

        # Reglas de enrutamiento por compliance
        self.compliance_routing_rules = self._load_compliance_rules()

        # Métricas de routing
        self.routing_metrics = {
            "total_decisions": 0,
            "decisions_by_business_unit": {},
            "decisions_by_compliance": {},
            "platform_utilization": {},
            "average_decision_time_ms": 0
        }

    def _load_business_profiles(self) -> Dict[BusinessUnit, Dict]:
        """Cargar perfiles de unidades de negocio"""
        return {
            BusinessUnit.FINANCE: {
                "critical_systems": ["trading_systems", "payment_processing", "core_banking"],
                "peak_hours": {"start": 6, "end": 18},
                "risk_tolerance": "very_low",
                "mandatory_compliance": [ComplianceFramework.SOX, ComplianceFramework.PCI_DSS],
                "preferred_xdr": [XDRPlatform.CROWDSTRIKE, XDRPlatform.SENTINEL],
                "sla_requirements": {
                    "detection_time_minutes": 5,
                    "response_time_minutes": 15,
                    "availability_percentage": 99.9
                },
                "audit_retention_years": 7,
                "notification_stakeholders": ["cfo", "compliance_officer", "security_team"]
            },

            BusinessUnit.HEALTHCARE: {
                "critical_systems": ["ehr_systems", "medical_devices", "patient_portals"],
                "peak_hours": {"start": 0, "end": 24},  # 24/7
                "risk_tolerance": "very_low",
                "mandatory_compliance": [ComplianceFramework.HIPAA, ComplianceFramework.GDPR],
                "preferred_xdr": [XDRPlatform.SENTINEL, XDRPlatform.CROWDSTRIKE],
                "sla_requirements": {
                    "detection_time_minutes": 3,
                    "response_time_minutes": 10,
                    "availability_percentage": 99.95
                },
                "audit_retention_years": 6,
                "notification_stakeholders": ["cmo", "privacy_officer", "hipaa_officer", "security_team"]
            },

            BusinessUnit.TECHNOLOGY: {
                "critical_systems": ["development_environments", "ci_cd_pipelines", "cloud_infrastructure"],
                "peak_hours": {"start": 8, "end": 20},
                "risk_tolerance": "medium",
                "mandatory_compliance": [ComplianceFramework.ISO27001],
                "preferred_xdr": [XDRPlatform.CROWDSTRIKE],
                "sla_requirements": {
                    "detection_time_minutes": 10,
                    "response_time_minutes": 30,
                    "availability_percentage": 99.5
                },
                "audit_retention_years": 3,
                "notification_stakeholders": ["cto", "devops_team", "security_team"]
            },

            BusinessUnit.MANUFACTURING: {
                "critical_systems": ["scada_systems", "plc_controllers", "manufacturing_execution_systems"],
                "peak_hours": {"start": 6, "end": 22},
                "risk_tolerance": "low",
                "mandatory_compliance": [ComplianceFramework.NERC_CIP, ComplianceFramework.ISO27001],
                "preferred_xdr": [XDRPlatform.SENTINEL, XDRPlatform.CISCO_UMBRELLA],
                "sla_requirements": {
                    "detection_time_minutes": 5,
                    "response_time_minutes": 20,
                    "availability_percentage": 99.8
                },
                "audit_retention_years": 5,
                "notification_stakeholders": ["operations_manager", "plant_security", "it_security"]
            },

            BusinessUnit.UNKNOWN: {
                "critical_systems": [],
                "peak_hours": {"start": 8, "end": 18},
                "risk_tolerance": "medium",
                "mandatory_compliance": [],
                "preferred_xdr": [XDRPlatform.CROWDSTRIKE],
                "sla_requirements": {
                    "detection_time_minutes": 15,
                    "response_time_minutes": 60,
                    "availability_percentage": 99.0
                },
                "audit_retention_years": 1,
                "notification_stakeholders": ["security_team"]
            }
        }

    def _build_capabilities_matrix(self) -> Dict:
        """Construir matriz de capacidades por plataforma y contexto"""
        return {
            XDRPlatform.CROWDSTRIKE: {
                "best_for_business_units": [BusinessUnit.FINANCE, BusinessUnit.TECHNOLOGY],
                "compliance_strengths": [ComplianceFramework.SOX, ComplianceFramework.PCI_DSS],
                "threat_specializations": ["endpoint_protection", "behavioral_analysis", "threat_hunting"],
                "response_capabilities": ["quarantine", "process_termination", "memory_analysis"],
                "cost_per_event": 2.50,
                "average_response_time_minutes": 8,
                "data_retention_days": 90
            },

            XDRPlatform.SENTINEL: {
                "best_for_business_units": [BusinessUnit.HEALTHCARE, BusinessUnit.GOVERNMENT],
                "compliance_strengths": [ComplianceFramework.HIPAA, ComplianceFramework.FISMA, ComplianceFramework.GDPR],
                "threat_specializations": ["cloud_security", "identity_protection", "compliance_monitoring"],
                "response_capabilities": ["user_disable", "conditional_access", "threat_intelligence"],
                "cost_per_event": 1.80,
                "average_response_time_minutes": 12,
                "data_retention_days": 365
            },

            XDRPlatform.CISCO_UMBRELLA: {
                "best_for_business_units": [BusinessUnit.MANUFACTURING, BusinessUnit.RETAIL],
                "compliance_strengths": [ComplianceFramework.NERC_CIP, ComplianceFramework.NIST],
                "threat_specializations": ["dns_security", "web_filtering", "network_visibility"],
                "response_capabilities": ["dns_block", "category_block", "policy_enforcement"],
                "cost_per_event": 0.75,
                "average_response_time_minutes": 3,
                "data_retention_days": 30
            }
        }

    def _load_compliance_rules(self) -> Dict:
        """Cargar reglas de enrutamiento por compliance"""
        return {
            ComplianceFramework.SOX: {
                "required_platforms": [XDRPlatform.SENTINEL],  # Para auditoría
                "audit_requirements": {
                    "detailed_logging": True,
                    "retention_years": 7,
                    "immutable_logs": True
                },
                "notification_requirements": ["compliance_officer", "external_auditor"],
                "response_time_sla_minutes": 15
            },

            ComplianceFramework.HIPAA: {
                "required_platforms": [XDRPlatform.SENTINEL],
                "audit_requirements": {
                    "detailed_logging": True,
                    "retention_years": 6,
                    "encryption_required": True,
                    "access_logging": True
                },
                "notification_requirements": ["privacy_officer", "compliance_team"],
                "breach_notification_hours": 72,
                "response_time_sla_minutes": 10
            },

            ComplianceFramework.PCI_DSS: {
                "required_platforms": [XDRPlatform.CROWDSTRIKE],
                "audit_requirements": {
                    "detailed_logging": True,
                    "retention_years": 3,
                    "network_monitoring": True
                },
                "notification_requirements": ["compliance_officer", "payment_processor"],
                "response_time_sla_minutes": 15
            },

            ComplianceFramework.GDPR: {
                "required_platforms": [XDRPlatform.SENTINEL],
                "audit_requirements": {
                    "detailed_logging": True,
                    "retention_years": 3,
                    "data_subject_rights": True
                },
                "notification_requirements": ["dpo", "supervisory_authority"],
                "breach_notification_hours": 72,
                "response_time_sla_minutes": 20
            },

            ComplianceFramework.NERC_CIP: {
                "required_platforms": [XDRPlatform.SENTINEL, XDRPlatform.CISCO_UMBRELLA],
                "audit_requirements": {
                    "detailed_logging": True,
                    "retention_years": 5,
                    "critical_infrastructure_focus": True
                },
                "notification_requirements": ["nerc_compliance", "operations_center"],
                "response_time_sla_minutes": 15
            }
        }

    async def route_threat_to_xdr(self, threat_event: Dict, hrm_analysis: Dict,
                                 business_context: Dict) -> XDRRoutingDecision:
        """Enrutar amenaza a plataformas XDR basado en contexto empresarial"""

        start_time = datetime.now()
        decision_id = f"routing_{start_time.timestamp()}_{hashlib.md5(str(threat_event.get('event_id', '')).encode()).hexdigest()[:8]}"

        self.logger.info(f"Starting XDR routing decision: {decision_id}")

        try:
            # 1. Analizar contexto empresarial
            business_profile = await self._analyze_business_context(business_context)

            # 2. Evaluar requisitos de compliance
            compliance_requirements = self._evaluate_compliance_requirements(business_profile)

            # 3. Calcular criticidad y urgencia
            criticality_assessment = self._assess_threat_criticality(
                hrm_analysis, business_profile
            )

            # 4. Seleccionar plataformas primarias y secundarias
            primary_platforms, secondary_platforms = await self._select_optimal_platforms(
                business_profile, compliance_requirements, criticality_assessment
            )

            # 5. Determinar estrategia de enrutamiento
            routing_strategy = self._determine_routing_strategy(
                criticality_assessment, business_profile, compliance_requirements
            )

            # 6. Calcular prioridad de exportación y urgencia de respuesta
            export_priority = self._calculate_export_priority(criticality_assessment)
            response_urgency = self._calculate_response_urgency(criticality_assessment)

            # 7. Estimar costos
            estimated_cost = self._estimate_routing_cost(primary_platforms, secondary_platforms)

            # 8. Determinar requisitos de SLA
            sla_requirements = self._determine_sla_requirements(business_profile, compliance_requirements)

            # 9. Verificar si se requiere audit trail
            audit_trail_required = self._check_audit_requirements(compliance_requirements)

            # 10. Crear decisión de enrutamiento
            routing_decision = XDRRoutingDecision(
                decision_id=decision_id,
                primary_platforms=primary_platforms,
                secondary_platforms=secondary_platforms,
                routing_strategy=routing_strategy,
                business_justification=self._generate_business_justification(
                    business_profile, criticality_assessment
                ),
                compliance_requirements=[req.name for req in compliance_requirements],
                export_priority=export_priority,
                response_urgency=response_urgency,
                estimated_cost=estimated_cost,
                sla_requirements=sla_requirements,
                audit_trail_required=audit_trail_required
            )

            # 11. Actualizar métricas
            decision_time = (datetime.now() - start_time).total_seconds() * 1000
            self._update_routing_metrics(routing_decision, decision_time, business_profile)

            self.logger.info(f"XDR routing decision completed: {decision_id} "
                           f"(Primary: {[p.value for p in primary_platforms]}, "
                           f"Strategy: {routing_strategy})")

            return routing_decision

        except Exception as e:
            self.logger.error(f"Error in XDR routing decision {decision_id}: {str(e)}")
            # Fallback a routing básico
            return await self._fallback_routing_decision(decision_id, threat_event, hrm_analysis)

    async def _analyze_business_context(self, business_context: Dict) -> BusinessContextProfile:
        """Analizar y enriquecer contexto empresarial"""

        # Extraer información básica
        business_unit_str = business_context.get("business_unit", "unknown")
        try:
            business_unit = BusinessUnit(business_unit_str.lower())
        except ValueError:
            business_unit = BusinessUnit.UNKNOWN

        # Parsear frameworks de compliance
        compliance_frameworks = []
        for framework_str in business_context.get("compliance_frameworks", []):
            try:
                framework = ComplianceFramework(framework_str.lower())
                compliance_frameworks.append(framework)
            except ValueError:
                self.logger.warning(f"Unknown compliance framework: {framework_str}")

        # Parsear criticidad de activos
        asset_criticality_str = business_context.get("asset_criticality", "medium")
        try:
            asset_criticality = AssetCriticality(asset_criticality_str.lower())
        except ValueError:
            asset_criticality = AssetCriticality.MEDIUM

        # Determinar si están en horario empresarial
        current_hour = datetime.now().hour
        business_profile = self.business_profiles.get(business_unit, {})
        peak_hours = business_profile.get("peak_hours", {"start": 8, "end": 18})
        business_hours_active = peak_hours["start"] <= current_hour <= peak_hours["end"]

        return BusinessContextProfile(
            business_unit=business_unit,
            compliance_frameworks=compliance_frameworks,
            asset_criticality=asset_criticality,
            risk_tolerance=business_context.get("risk_tolerance", "medium"),
            geographical_region=business_context.get("geographical_region", "unknown"),
            business_hours_active=business_hours_active,
            data_classification=business_context.get("data_classification", "internal"),
            regulatory_requirements=business_context.get("regulatory_requirements", [])
        )

    def _evaluate_compliance_requirements(self, business_profile: BusinessContextProfile) -> List[ComplianceFramework]:
        """Evaluar requisitos de compliance activos"""
        active_frameworks = list(business_profile.compliance_frameworks)

        # Añadir frameworks obligatorios por unidad de negocio
        unit_profile = self.business_profiles.get(business_profile.business_unit, {})
        mandatory_compliance = unit_profile.get("mandatory_compliance", [])
        for framework in mandatory_compliance:
            if framework not in active_frameworks:
                active_frameworks.append(framework)

        return active_frameworks

    def _assess_threat_criticality(self, hrm_analysis: Dict,
                                  business_profile: BusinessContextProfile) -> Dict:
        """Evaluar criticidad de amenaza considerando contexto empresarial"""

        # Análisis básico HRM
        threat_level = hrm_analysis.get("hrm_analysis", {}).get("final_assessment", {}).get("threat_level", "MEDIUM")
        confidence = hrm_analysis.get("hrm_analysis", {}).get("final_assessment", {}).get("confidence", 0.5)
        false_positive_score = hrm_analysis.get("hrm_analysis", {}).get("analysis_modules", {}).get("ml_false_positive", {}).get("score", 0.5)

        # Factores de contexto empresarial
        business_multiplier = 1.0

        # Multiplicador por criticidad de activo
        if business_profile.asset_criticality == AssetCriticality.CRITICAL:
            business_multiplier += 0.5
        elif business_profile.asset_criticality == AssetCriticality.HIGH:
            business_multiplier += 0.3

        # Multiplicador por unidad de negocio crítica
        if business_profile.business_unit in [BusinessUnit.FINANCE, BusinessUnit.HEALTHCARE]:
            business_multiplier += 0.3

        # Multiplicador por horario empresarial
        if business_profile.business_hours_active:
            business_multiplier += 0.2

        # Multiplicador por compliance crítico
        critical_compliance = [ComplianceFramework.HIPAA, ComplianceFramework.SOX, ComplianceFramework.NERC_CIP]
        if any(framework in critical_compliance for framework in business_profile.compliance_frameworks):
            business_multiplier += 0.4

        # Calcular score final
        base_score = self._threat_level_to_score(threat_level) * confidence * (1 - false_positive_score)
        final_score = min(base_score * business_multiplier, 1.0)

        return {
            "base_threat_level": threat_level,
            "base_confidence": confidence,
            "false_positive_score": false_positive_score,
            "business_multiplier": business_multiplier,
            "final_criticality_score": final_score,
            "adjusted_threat_level": self._score_to_threat_level(final_score),
            "business_impact_factors": {
                "asset_criticality": business_profile.asset_criticality.value,
                "business_unit": business_profile.business_unit.value,
                "business_hours_active": business_profile.business_hours_active,
                "compliance_critical": any(framework in critical_compliance
                                         for framework in business_profile.compliance_frameworks)
            }
        }

    async def _select_optimal_platforms(self, business_profile: BusinessContextProfile,
                                       compliance_requirements: List[ComplianceFramework],
                                       criticality_assessment: Dict) -> Tuple[List[XDRPlatform], List[XDRPlatform]]:
        """Seleccionar plataformas primarias y secundarias óptimas"""

        # Obtener plataformas preferidas por unidad de negocio
        unit_profile = self.business_profiles.get(business_profile.business_unit, {})
        preferred_platforms = unit_profile.get("preferred_xdr", [])

        # Plataformas requeridas por compliance
        required_platforms = []
        for framework in compliance_requirements:
            compliance_rules = self.compliance_routing_rules.get(framework, {})
            framework_required = compliance_rules.get("required_platforms", [])
            required_platforms.extend(framework_required)

        # Eliminar duplicados manteniendo orden
        required_platforms = list(dict.fromkeys(required_platforms))

        # Selección basada en criticidad
        final_criticality_score = criticality_assessment["final_criticality_score"]

        primary_platforms = []
        secondary_platforms = []

        if final_criticality_score >= 0.9:  # Crítico extremo
            # Usar todas las plataformas disponibles
            primary_platforms = list(required_platforms)
            for platform in preferred_platforms:
                if platform not in primary_platforms:
                    primary_platforms.append(platform)

            # Si no hay suficientes, añadir todas disponibles
            all_platforms = [XDRPlatform.CROWDSTRIKE, XDRPlatform.SENTINEL, XDRPlatform.CISCO_UMBRELLA]
            for platform in all_platforms:
                if platform not in primary_platforms:
                    secondary_platforms.append(platform)

        elif final_criticality_score >= 0.7:  # Alto
            # Usar plataformas requeridas + preferidas
            primary_platforms = list(required_platforms)
            for platform in preferred_platforms[:2]:  # Top 2 preferidas
                if platform not in primary_platforms:
                    primary_platforms.append(platform)

            # Resto como secundarias
            for platform in preferred_platforms[2:]:
                if platform not in primary_platforms:
                    secondary_platforms.append(platform)

        elif final_criticality_score >= 0.5:  # Medio
            # Solo plataformas requeridas + 1 preferida
            primary_platforms = list(required_platforms)
            if preferred_platforms and preferred_platforms[0] not in primary_platforms:
                primary_platforms.append(preferred_platforms[0])

            # Resto como secundarias
            for platform in preferred_platforms[1:]:
                if platform not in primary_platforms:
                    secondary_platforms.append(platform)

        else:  # Bajo
            # Solo plataformas absolutamente requeridas
            primary_platforms = list(required_platforms)
            secondary_platforms = [p for p in preferred_platforms if p not in primary_platforms]

        # Asegurar que tenemos al menos una plataforma primaria
        if not primary_platforms:
            if preferred_platforms:
                primary_platforms.append(preferred_platforms[0])
            else:
                primary_platforms.append(XDRPlatform.CROWDSTRIKE)  # Default

        return primary_platforms, secondary_platforms

    def _determine_routing_strategy(self, criticality_assessment: Dict,
                                   business_profile: BusinessContextProfile,
                                   compliance_requirements: List[ComplianceFramework]) -> str:
        """Determinar estrategia de enrutamiento"""

        final_score = criticality_assessment["final_criticality_score"]
        business_hours = business_profile.business_hours_active
        has_compliance = len(compliance_requirements) > 0

        if final_score >= 0.9:
            return "emergency_broadcast"  # A todas las plataformas inmediatamente

        elif final_score >= 0.7:
            if has_compliance:
                return "compliance_priority_parallel"  # Compliance primero, luego paralelo
            else:
                return "high_priority_parallel"  # Paralelo a plataformas primarias

        elif final_score >= 0.5:
            if business_hours and business_profile.business_unit in [BusinessUnit.FINANCE, BusinessUnit.HEALTHCARE]:
                return "business_hours_priority"  # Prioridad durante horas de negocio
            else:
                return "standard_sequential"  # Secuencial estándar

        else:
            return "low_priority_deferred"  # Diferido a baja prioridad

    def _calculate_export_priority(self, criticality_assessment: Dict) -> ExportPriority:
        """Calcular prioridad de exportación"""
        final_score = criticality_assessment["final_criticality_score"]

        if final_score >= 0.9:
            return ExportPriority.EMERGENCY
        elif final_score >= 0.8:
            return ExportPriority.CRITICAL
        elif final_score >= 0.6:
            return ExportPriority.HIGH
        elif final_score >= 0.4:
            return ExportPriority.MEDIUM
        else:
            return ExportPriority.LOW

    def _calculate_response_urgency(self, criticality_assessment: Dict) -> ResponseUrgency:
        """Calcular urgencia de respuesta"""
        final_score = criticality_assessment["final_criticality_score"]

        if final_score >= 0.95:
            return ResponseUrgency.EMERGENCY
        elif final_score >= 0.8:
            return ResponseUrgency.CRITICAL
        elif final_score >= 0.6:
            return ResponseUrgency.HIGH
        elif final_score >= 0.4:
            return ResponseUrgency.MEDIUM
        else:
            return ResponseUrgency.LOW

    def _estimate_routing_cost(self, primary_platforms: List[XDRPlatform],
                              secondary_platforms: List[XDRPlatform]) -> float:
        """Estimar costo de enrutamiento"""
        total_cost = 0.0

        all_platforms = primary_platforms + secondary_platforms
        for platform in all_platforms:
            platform_info = self.platform_capabilities_matrix.get(platform, {})
            cost_per_event = platform_info.get("cost_per_event", 1.0)
            total_cost += cost_per_event

        return total_cost

    def _determine_sla_requirements(self, business_profile: BusinessContextProfile,
                                   compliance_requirements: List[ComplianceFramework]) -> Dict:
        """Determinar requisitos de SLA"""

        # SLA base por unidad de negocio
        unit_profile = self.business_profiles.get(business_profile.business_unit, {})
        base_sla = unit_profile.get("sla_requirements", {})

        # Ajustar por compliance más restrictivo
        most_restrictive_sla = dict(base_sla)

        for framework in compliance_requirements:
            compliance_rules = self.compliance_routing_rules.get(framework, {})
            framework_sla_minutes = compliance_rules.get("response_time_sla_minutes")

            if framework_sla_minutes:
                current_sla = most_restrictive_sla.get("response_time_minutes", 60)
                if framework_sla_minutes < current_sla:
                    most_restrictive_sla["response_time_minutes"] = framework_sla_minutes

        return most_restrictive_sla

    def _check_audit_requirements(self, compliance_requirements: List[ComplianceFramework]) -> bool:
        """Verificar si se requiere audit trail detallado"""
        audit_required_frameworks = [
            ComplianceFramework.SOX,
            ComplianceFramework.HIPAA,
            ComplianceFramework.PCI_DSS,
            ComplianceFramework.FISMA
        ]

        return any(framework in audit_required_frameworks for framework in compliance_requirements)

    def _generate_business_justification(self, business_profile: BusinessContextProfile,
                                        criticality_assessment: Dict) -> str:
        """Generar justificación empresarial de la decisión"""

        justifications = []

        # Justificación por unidad de negocio
        if business_profile.business_unit == BusinessUnit.FINANCE:
            justifications.append("Financial services require immediate threat response due to regulatory oversight")
        elif business_profile.business_unit == BusinessUnit.HEALTHCARE:
            justifications.append("Healthcare data protection mandates rapid incident response")
        elif business_profile.business_unit == BusinessUnit.MANUFACTURING:
            justifications.append("Manufacturing systems require specialized OT/IT security coordination")

        # Justificación por criticidad de activo
        if business_profile.asset_criticality == AssetCriticality.CRITICAL:
            justifications.append("Critical asset classification demands highest priority response")

        # Justificación por compliance
        for framework in business_profile.compliance_frameworks:
            if framework == ComplianceFramework.SOX:
                justifications.append("SOX compliance requires detailed audit trail and rapid response")
            elif framework == ComplianceFramework.HIPAA:
                justifications.append("HIPAA breach notification requirements drive urgent response")
            elif framework == ComplianceFramework.PCI_DSS:
                justifications.append("PCI-DSS mandates immediate containment of payment system threats")

        # Justificación por horario empresarial
        if business_profile.business_hours_active:
            justifications.append("Business hours operations require immediate security response")

        # Justificación por criticidad ajustada
        final_score = criticality_assessment["final_criticality_score"]
        if final_score >= 0.9:
            justifications.append("Extreme threat criticality with business context amplification")
        elif final_score >= 0.7:
            justifications.append("High threat criticality enhanced by business risk factors")

        return "; ".join(justifications) if justifications else "Standard threat response protocol"

    def _threat_level_to_score(self, threat_level: str) -> float:
        """Convertir nivel de amenaza a score numérico"""
        mapping = {
            "CRITICAL": 0.9,
            "HIGH": 0.7,
            "MEDIUM": 0.5,
            "LOW": 0.3
        }
        return mapping.get(threat_level, 0.5)

    def _score_to_threat_level(self, score: float) -> str:
        """Convertir score numérico a nivel de amenaza"""
        if score >= 0.8:
            return "CRITICAL"
        elif score >= 0.6:
            return "HIGH"
        elif score >= 0.4:
            return "MEDIUM"
        else:
            return "LOW"

    async def _fallback_routing_decision(self, decision_id: str, threat_event: Dict,
                                        hrm_analysis: Dict) -> XDRRoutingDecision:
        """Decisión de routing de fallback en caso de error"""
        self.logger.warning(f"Using fallback routing for decision: {decision_id}")

        return XDRRoutingDecision(
            decision_id=decision_id,
            primary_platforms=[XDRPlatform.CROWDSTRIKE],  # Default safe choice
            secondary_platforms=[],
            routing_strategy="fallback_basic",
            business_justification="Fallback routing due to context analysis error",
            compliance_requirements=[],
            export_priority=ExportPriority.MEDIUM,
            response_urgency=ResponseUrgency.MEDIUM,
            estimated_cost=2.50,
            sla_requirements={"response_time_minutes": 30},
            audit_trail_required=False
        )

    def _update_routing_metrics(self, routing_decision: XDRRoutingDecision,
                               decision_time_ms: float, business_profile: BusinessContextProfile):
        """Actualizar métricas de routing"""
        self.routing_metrics["total_decisions"] += 1

        # Métricas por unidad de negocio
        unit_key = business_profile.business_unit.value
        if unit_key not in self.routing_metrics["decisions_by_business_unit"]:
            self.routing_metrics["decisions_by_business_unit"][unit_key] = 0
        self.routing_metrics["decisions_by_business_unit"][unit_key] += 1

        # Métricas por compliance
        for framework in business_profile.compliance_frameworks:
            framework_key = framework.value
            if framework_key not in self.routing_metrics["decisions_by_compliance"]:
                self.routing_metrics["decisions_by_compliance"][framework_key] = 0
            self.routing_metrics["decisions_by_compliance"][framework_key] += 1

        # Métricas de utilización de plataforma
        all_platforms = routing_decision.primary_platforms + routing_decision.secondary_platforms
        for platform in all_platforms:
            platform_key = platform.value
            if platform_key not in self.routing_metrics["platform_utilization"]:
                self.routing_metrics["platform_utilization"][platform_key] = 0
            self.routing_metrics["platform_utilization"][platform_key] += 1

        # Tiempo promedio de decisión
        current_avg = self.routing_metrics["average_decision_time_ms"]
        total_decisions = self.routing_metrics["total_decisions"]
        new_avg = ((current_avg * (total_decisions - 1)) + decision_time_ms) / total_decisions
        self.routing_metrics["average_decision_time_ms"] = new_avg

    async def get_routing_analytics(self) -> Dict:
        """Obtener analytics de enrutamiento"""
        return {
            "routing_metrics": self.routing_metrics,
            "business_unit_preferences": {
                unit.value: profile.get("preferred_xdr", [])
                for unit, profile in self.business_profiles.items()
            },
            "compliance_platform_matrix": {
                framework.value: rules.get("required_platforms", [])
                for framework, rules in self.compliance_routing_rules.items()
            },
            "platform_capabilities_summary": {
                platform.value: {
                    "best_for": info.get("best_for_business_units", []),
                    "compliance_strengths": info.get("compliance_strengths", []),
                    "cost_per_event": info.get("cost_per_event", 0),
                    "avg_response_time": info.get("average_response_time_minutes", 0)
                }
                for platform, info in self.platform_capabilities_matrix.items()
            }
        }

    async def simulate_routing_scenarios(self, scenarios: List[Dict]) -> List[Dict]:
        """Simular escenarios de routing para análisis"""
        results = []

        for i, scenario in enumerate(scenarios):
            self.logger.info(f"Simulating routing scenario {i+1}/{len(scenarios)}")

            threat_event = scenario.get("threat_event", {})
            hrm_analysis = scenario.get("hrm_analysis", {})
            business_context = scenario.get("business_context", {})

            routing_decision = await self.route_threat_to_xdr(
                threat_event, hrm_analysis, business_context
            )

            result = {
                "scenario_id": i + 1,
                "scenario_name": scenario.get("name", f"Scenario {i+1}"),
                "input": scenario,
                "routing_decision": asdict(routing_decision),
                "cost_impact": routing_decision.estimated_cost,
                "platforms_selected": [p.value for p in routing_decision.primary_platforms],
                "sla_requirements": routing_decision.sla_requirements
            }
            results.append(result)

        return results

# Factory function
def create_business_context_xdr_router(config: Optional[Dict] = None) -> BusinessContextXDRRouter:
    """Factory para crear router de contexto empresarial XDR"""
    if config is None:
        config = {
            "enable_cost_optimization": True,
            "enable_compliance_enforcement": True,
            "default_fallback_platform": "crowdstrike"
        }

    return BusinessContextXDRRouter(config)

# Ejemplo de uso
if __name__ == "__main__":
    async def test_business_context_routing():
        # Crear router
        router = create_business_context_xdr_router()

        # Escenario 1: Finanzas con SOX
        finance_threat = {
            "event_id": "finance_test_001",
            "event_type": "insider_threat",
            "source_system": "trading_platform"
        }

        finance_hrm_analysis = {
            "hrm_analysis": {
                "final_assessment": {
                    "threat_level": "HIGH",
                    "confidence": 0.85
                },
                "analysis_modules": {
                    "ml_false_positive": {"score": 0.15}
                }
            }
        }

        finance_context = {
            "business_unit": "finance",
            "asset_criticality": "critical",
            "compliance_frameworks": ["sox", "pci_dss"],
            "risk_tolerance": "very_low"
        }

        finance_decision = await router.route_threat_to_xdr(
            finance_threat, finance_hrm_analysis, finance_context
        )

        print("Finance Scenario Results:")
        print(f"- Primary Platforms: {[p.value for p in finance_decision.primary_platforms]}")
        print(f"- Routing Strategy: {finance_decision.routing_strategy}")
        print(f"- Export Priority: {finance_decision.export_priority.name}")
        print(f"- Estimated Cost: ${finance_decision.estimated_cost:.2f}")
        print(f"- SLA Response Time: {finance_decision.sla_requirements.get('response_time_minutes')} minutes")
        print(f"- Business Justification: {finance_decision.business_justification}")

        print("\n" + "="*50 + "\n")

        # Escenario 2: Healthcare con HIPAA
        healthcare_threat = {
            "event_id": "healthcare_test_001",
            "event_type": "data_breach",
            "source_system": "ehr_system"
        }

        healthcare_hrm_analysis = {
            "hrm_analysis": {
                "final_assessment": {
                    "threat_level": "CRITICAL",
                    "confidence": 0.92
                },
                "analysis_modules": {
                    "ml_false_positive": {"score": 0.08}
                }
            }
        }

        healthcare_context = {
            "business_unit": "healthcare",
            "asset_criticality": "critical",
            "compliance_frameworks": ["hipaa", "gdpr"],
            "risk_tolerance": "very_low",
            "data_classification": "restricted"
        }

        healthcare_decision = await router.route_threat_to_xdr(
            healthcare_threat, healthcare_hrm_analysis, healthcare_context
        )

        print("Healthcare Scenario Results:")
        print(f"- Primary Platforms: {[p.value for p in healthcare_decision.primary_platforms]}")
        print(f"- Routing Strategy: {healthcare_decision.routing_strategy}")
        print(f"- Export Priority: {healthcare_decision.export_priority.name}")
        print(f"- Estimated Cost: ${healthcare_decision.estimated_cost:.2f}")
        print(f"- SLA Response Time: {healthcare_decision.sla_requirements.get('response_time_minutes')} minutes")
        print(f"- Audit Trail Required: {healthcare_decision.audit_trail_required}")
        print(f"- Business Justification: {healthcare_decision.business_justification}")

        # Analytics
        analytics = await router.get_routing_analytics()
        print(f"\nRouting Analytics:")
        print(json.dumps(analytics, indent=2))

    # Ejecutar test
    asyncio.run(test_business_context_routing())