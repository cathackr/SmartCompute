#!/usr/bin/env python3
"""
SmartCompute HRM - Analizador Enterprise e Industrial
Adaptaciones específicas para entornos corporativos y de manufactura
"""
import json
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

@dataclass
class EnterpriseContext:
    business_unit: str
    compliance_frameworks: List[str]
    risk_tolerance: str
    asset_criticality: str
    user_privileges: str

@dataclass
class IndustrialContext:
    plant_zone: str  # DMZ, Control Network, Safety Network
    protocol_type: str  # Modbus, DNP3, OPC-UA, etc.
    production_impact: str  # CRITICAL, HIGH, MEDIUM, LOW
    safety_classification: str  # SIL1, SIL2, SIL3, SIL4
    operational_mode: str  # PRODUCTION, MAINTENANCE, SHUTDOWN

class EnterpriseIndustrialHRM:
    """HRM especializado para Enterprise e Industrial"""

    def __init__(self):
        self.enterprise_profiles = self._load_enterprise_profiles()
        self.industrial_profiles = self._load_industrial_profiles()
        self.compliance_requirements = self._load_compliance_requirements()

    def _load_enterprise_profiles(self) -> Dict:
        return {
            "finance": {
                "critical_processes": ["trading", "payment_processing", "risk_management"],
                "compliance": ["SOX", "PCI-DSS", "GDPR"],
                "response_priority": "immediate",
                "business_hours": {"start": 6, "end": 20},
                "escalation_threshold": 3.0
            },
            "healthcare": {
                "critical_processes": ["patient_care", "medical_devices", "phi_systems"],
                "compliance": ["HIPAA", "FDA", "HITECH"],
                "response_priority": "critical",
                "business_hours": {"start": 0, "end": 24},  # 24/7
                "escalation_threshold": 2.0
            },
            "technology": {
                "critical_processes": ["development", "production", "customer_data"],
                "compliance": ["SOC2", "ISO27001", "GDPR"],
                "response_priority": "high",
                "business_hours": {"start": 8, "end": 18},
                "escalation_threshold": 4.0
            }
        }

    def _load_industrial_profiles(self) -> Dict:
        return {
            "power_generation": {
                "critical_systems": ["turbine_control", "protection_relays", "load_dispatch"],
                "protocols": ["DNP3", "IEC 61850", "Modbus"],
                "safety_requirements": "SIL3",
                "production_priority": "absolute",
                "response_constraints": ["no_auto_shutdown", "ops_approval_required"]
            },
            "oil_gas": {
                "critical_systems": ["pipeline_control", "safety_shutdown", "leak_detection"],
                "protocols": ["Modbus", "HART", "Foundation Fieldbus"],
                "safety_requirements": "SIL4",
                "production_priority": "critical",
                "response_constraints": ["safety_first", "environmental_protection"]
            },
            "manufacturing": {
                "critical_systems": ["production_line", "quality_control", "inventory"],
                "protocols": ["OPC-UA", "Ethernet/IP", "Profinet"],
                "safety_requirements": "SIL2",
                "production_priority": "high",
                "response_constraints": ["minimize_downtime", "quality_preservation"]
            },
            "water_treatment": {
                "critical_systems": ["chemical_dosing", "filtration", "distribution"],
                "protocols": ["Modbus", "DNP3", "BACnet"],
                "safety_requirements": "SIL3",
                "production_priority": "critical",
                "response_constraints": ["public_health_priority", "regulatory_compliance"]
            }
        }

    def _load_compliance_requirements(self) -> Dict:
        return {
            "SOX": {
                "data_retention": "7_years",
                "audit_requirements": ["financial_controls", "access_logging"],
                "response_timeframe": "24_hours"
            },
            "HIPAA": {
                "data_protection": "PHI_encryption",
                "breach_notification": "72_hours",
                "audit_requirements": ["access_logs", "data_flow_tracking"]
            },
            "NERC_CIP": {
                "critical_infrastructure": True,
                "response_timeframe": "immediate",
                "reporting_requirements": ["government_notification", "industry_sharing"]
            },
            "IEC62443": {
                "industrial_security": True,
                "zone_segmentation": "required",
                "safety_integration": "mandatory"
            }
        }

    def analyze_enterprise_context(self, event_data: Dict, business_context: EnterpriseContext) -> Dict:
        """Análisis específico para entornos empresariales"""

        analysis = {
            "business_impact": {},
            "compliance_implications": {},
            "escalation_requirements": {},
            "customized_response": {}
        }

        # Evaluar impacto de negocio
        business_profile = self.enterprise_profiles.get(business_context.business_unit.lower(), {})

        # Determinar criticidad basada en el contexto empresarial
        if business_context.asset_criticality == "executive_system":
            impact_multiplier = 3.0
        elif business_context.asset_criticality == "customer_facing":
            impact_multiplier = 2.5
        elif business_context.asset_criticality == "internal_operations":
            impact_multiplier = 1.5
        else:
            impact_multiplier = 1.0

        analysis["business_impact"] = {
            "severity_multiplier": impact_multiplier,
            "affected_processes": business_profile.get("critical_processes", []),
            "estimated_cost_per_hour": self._calculate_business_cost(business_context),
            "reputation_risk": "high" if impact_multiplier > 2.0 else "medium"
        }

        # Evaluar implicaciones de compliance
        compliance_issues = []
        for framework in business_context.compliance_frameworks:
            if framework in self.compliance_requirements:
                req = self.compliance_requirements[framework]
                compliance_issues.append({
                    "framework": framework,
                    "notification_deadline": req.get("response_timeframe", "unknown"),
                    "audit_impact": "high" if "audit_requirements" in req else "low"
                })

        analysis["compliance_implications"] = compliance_issues

        # Determinar escalación automática
        base_risk = event_data.get("severity", "MEDIUM")
        escalation_threshold = business_profile.get("escalation_threshold", 3.0)

        analysis["escalation_requirements"] = {
            "auto_escalate": impact_multiplier >= escalation_threshold,
            "notification_list": self._get_enterprise_contacts(business_context),
            "escalation_timeline": "immediate" if impact_multiplier > 2.5 else "standard"
        }

        return analysis

    def analyze_industrial_context(self, event_data: Dict, industrial_context: IndustrialContext) -> Dict:
        """Análisis específico para entornos industriales (OT/ICS)"""

        analysis = {
            "safety_assessment": {},
            "production_impact": {},
            "protocol_analysis": {},
            "response_constraints": {}
        }

        # Perfil industrial específico
        plant_profile = self.industrial_profiles.get(industrial_context.plant_zone.lower(), {})

        # Evaluación de seguridad (Safety)
        safety_level = industrial_context.safety_classification
        analysis["safety_assessment"] = {
            "sil_level": safety_level,
            "safety_critical": safety_level in ["SIL3", "SIL4"],
            "human_safety_risk": "critical" if safety_level == "SIL4" else "high",
            "environmental_risk": self._assess_environmental_risk(industrial_context)
        }

        # Impacto en producción
        production_risk = {
            "CRITICAL": 5.0,
            "HIGH": 3.0,
            "MEDIUM": 2.0,
            "LOW": 1.0
        }.get(industrial_context.production_impact, 1.0)

        analysis["production_impact"] = {
            "severity": industrial_context.production_impact,
            "estimated_downtime_cost": production_risk * 100000,  # $100k base per hour
            "affected_systems": plant_profile.get("critical_systems", []),
            "cascade_risk": "high" if production_risk >= 3.0 else "medium"
        }

        # Análisis de protocolo
        protocol_info = self._analyze_industrial_protocol(industrial_context.protocol_type)
        analysis["protocol_analysis"] = protocol_info

        # Restricciones de respuesta específicas para OT
        analysis["response_constraints"] = {
            "auto_shutdown_allowed": False,  # Nunca en entornos industriales
            "human_approval_required": True,
            "safety_system_priority": True,
            "change_window_required": industrial_context.operational_mode == "PRODUCTION",
            "specialized_team": "OT_security_team"
        }

        return analysis

    def _calculate_business_cost(self, context: EnterpriseContext) -> float:
        """Calcular costo estimado por hora de downtime"""
        base_costs = {
            "finance": 500000,  # $500k/hour
            "healthcare": 200000,  # $200k/hour
            "technology": 100000,  # $100k/hour
            "manufacturing": 75000,  # $75k/hour
        }

        base = base_costs.get(context.business_unit.lower(), 50000)

        # Multiplicadores por criticidad
        if context.asset_criticality == "executive_system":
            return base * 3
        elif context.asset_criticality == "customer_facing":
            return base * 2
        else:
            return base

    def _assess_environmental_risk(self, context: IndustrialContext) -> str:
        """Evaluar riesgo ambiental"""
        high_risk_zones = ["oil_gas", "chemical", "nuclear", "water_treatment"]
        return "critical" if context.plant_zone.lower() in high_risk_zones else "medium"

    def _analyze_industrial_protocol(self, protocol: str) -> Dict:
        """Analizar vulnerabilidades específicas del protocolo industrial"""
        protocol_info = {
            "Modbus": {
                "security_level": "low",
                "encryption": "none",
                "authentication": "none",
                "common_attacks": ["unauthorized_commands", "data_manipulation"]
            },
            "DNP3": {
                "security_level": "medium",
                "encryption": "optional",
                "authentication": "challenge_response",
                "common_attacks": ["replay_attacks", "sequence_manipulation"]
            },
            "OPC-UA": {
                "security_level": "high",
                "encryption": "standard",
                "authentication": "certificates",
                "common_attacks": ["certificate_attacks", "endpoint_exploitation"]
            },
            "IEC 61850": {
                "security_level": "medium",
                "encryption": "limited",
                "authentication": "basic",
                "common_attacks": ["goose_manipulation", "mms_attacks"]
            }
        }

        return protocol_info.get(protocol, {"security_level": "unknown"})

    def _get_enterprise_contacts(self, context: EnterpriseContext) -> List[str]:
        """Obtener lista de contactos para escalación empresarial"""
        contacts = ["security_team@company.com"]

        if context.user_privileges == "executive":
            contacts.extend(["ciso@company.com", "ceo@company.com"])
        elif context.business_unit.lower() == "finance":
            contacts.extend(["cfo@company.com", "risk_management@company.com"])
        elif context.business_unit.lower() == "healthcare":
            contacts.extend(["compliance@company.com", "privacy_officer@company.com"])

        return contacts

    def generate_sector_specific_recommendations(self,
                                               event_data: Dict,
                                               enterprise_context: Optional[EnterpriseContext] = None,
                                               industrial_context: Optional[IndustrialContext] = None) -> Dict:
        """Generar recomendaciones específicas por sector"""

        recommendations = {
            "immediate_actions": [],
            "compliance_actions": [],
            "business_continuity": [],
            "long_term_improvements": []
        }

        if enterprise_context:
            ent_analysis = self.analyze_enterprise_context(event_data, enterprise_context)

            # Acciones inmediatas empresariales
            if ent_analysis["business_impact"]["severity_multiplier"] > 2.0:
                recommendations["immediate_actions"].extend([
                    "Activate business continuity plan",
                    "Notify executive leadership within 30 minutes",
                    "Assess customer data exposure"
                ])

            # Acciones de compliance
            for compliance in ent_analysis["compliance_implications"]:
                recommendations["compliance_actions"].append(
                    f"Initiate {compliance['framework']} incident reporting within {compliance['notification_deadline']}"
                )

        if industrial_context:
            ind_analysis = self.analyze_industrial_context(event_data, industrial_context)

            # Acciones inmediatas industriales
            if ind_analysis["safety_assessment"]["safety_critical"]:
                recommendations["immediate_actions"].extend([
                    "Notify safety officer immediately",
                    "Verify safety systems operational status",
                    "Consider manual operation mode if needed"
                ])

            # Continuidad de negocio industrial
            if ind_analysis["production_impact"]["cascade_risk"] == "high":
                recommendations["business_continuity"].extend([
                    "Activate alternate production lines",
                    "Implement manual control procedures",
                    "Coordinate with supply chain team"
                ])

        return recommendations

def main():
    analyzer = EnterpriseIndustrialHRM()

    # Ejemplo Enterprise - Sector Financiero
    print("=" * 60)
    print("🏢 ANÁLISIS SMARTCOMPUTE HRM - SECTOR FINANCIERO")
    print("=" * 60)

    enterprise_ctx = EnterpriseContext(
        business_unit="finance",
        compliance_frameworks=["SOX", "PCI-DSS"],
        risk_tolerance="low",
        asset_criticality="customer_facing",
        user_privileges="standard"
    )

    # Evento simulado
    financial_event = {
        "event_id": "FIN-001",
        "severity": "HIGH",
        "description": "Suspicious database access pattern detected",
        "affected_system": "trading_platform",
        "timestamp": "2025-09-15T14:30:00Z"
    }

    enterprise_analysis = analyzer.analyze_enterprise_context(financial_event, enterprise_ctx)
    enterprise_recommendations = analyzer.generate_sector_specific_recommendations(
        financial_event, enterprise_context=enterprise_ctx
    )

    print(f"💰 Costo estimado/hora: ${enterprise_analysis['business_impact']['estimated_cost_per_hour']:,}")
    print(f"📊 Riesgo reputacional: {enterprise_analysis['business_impact']['reputation_risk']}")
    print(f"⚡ Escalación automática: {enterprise_analysis['escalation_requirements']['auto_escalate']}")

    print("\n📋 Recomendaciones Enterprise:")
    for action in enterprise_recommendations["immediate_actions"]:
        print(f"  • {action}")

    # Ejemplo Industrial - Planta de Energía
    print("\n" + "=" * 60)
    print("🏭 ANÁLISIS SMARTCOMPUTE HRM - SECTOR ENERGÉTICO")
    print("=" * 60)

    industrial_ctx = IndustrialContext(
        plant_zone="power_generation",
        protocol_type="DNP3",
        production_impact="CRITICAL",
        safety_classification="SIL3",
        operational_mode="PRODUCTION"
    )

    # Evento simulado
    power_event = {
        "event_id": "PWR-001",
        "severity": "CRITICAL",
        "description": "Unauthorized DNP3 commands detected",
        "affected_system": "turbine_control",
        "timestamp": "2025-09-15T14:30:00Z"
    }

    industrial_analysis = analyzer.analyze_industrial_context(power_event, industrial_ctx)
    industrial_recommendations = analyzer.generate_sector_specific_recommendations(
        power_event, industrial_context=industrial_ctx
    )

    print(f"⚡ Nivel de seguridad: {industrial_analysis['safety_assessment']['sil_level']}")
    print(f"🏭 Costo downtime estimado: ${industrial_analysis['production_impact']['estimated_downtime_cost']:,}")
    print(f"🔒 Shutdown automático permitido: {industrial_analysis['response_constraints']['auto_shutdown_allowed']}")
    print(f"📡 Protocolo: {industrial_ctx.protocol_type}")

    print("\n📋 Recomendaciones Industriales:")
    for action in industrial_recommendations["immediate_actions"]:
        print(f"  • {action}")

    print("\n" + "=" * 60)
    print("✅ ANÁLISIS SECTORIAL COMPLETADO")
    print("=" * 60)

if __name__ == "__main__":
    main()