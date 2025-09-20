#!/usr/bin/env python3
"""
SmartCompute Enterprise - Security Recommendations Engine
=========================================================

Motor de recomendaciones de seguridad basado en OWASP, NIST e ISO 27001
para análisis de infraestructura SmartCompute Enterprise.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class SecurityFramework(Enum):
    """Frameworks de seguridad soportados"""
    OWASP = "OWASP"
    NIST = "NIST"
    ISO27001 = "ISO 27001"


class RiskLevel(Enum):
    """Niveles de riesgo"""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFO = "Info"


class RecommendationCategory(Enum):
    """Categorías de recomendaciones"""
    NETWORK_SECURITY = "Network Security"
    ACCESS_CONTROL = "Access Control"
    DATA_PROTECTION = "Data Protection"
    INCIDENT_RESPONSE = "Incident Response"
    VULNERABILITY_MANAGEMENT = "Vulnerability Management"
    CONFIGURATION_MANAGEMENT = "Configuration Management"
    MONITORING_LOGGING = "Monitoring & Logging"
    COMPLIANCE = "Compliance"


@dataclass
class SecurityRecommendation:
    """Recomendación de seguridad"""
    id: str
    title: str
    description: str
    framework: SecurityFramework
    category: RecommendationCategory
    risk_level: RiskLevel
    impact: str
    implementation_effort: str
    compliance_references: List[str]
    technical_details: str
    remediation_steps: List[str]
    priority_score: int
    affected_assets: List[str]


class SmartComputeSecurityRecommendationsEngine:
    """Motor de recomendaciones de seguridad para SmartCompute Enterprise"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.recommendations_db = self._initialize_recommendations_database()

    def _initialize_recommendations_database(self) -> Dict[str, SecurityRecommendation]:
        """Inicializa la base de datos de recomendaciones de seguridad"""
        recommendations = {}

        # OWASP Top 10 y Security Best Practices
        owasp_recommendations = [
            SecurityRecommendation(
                id="OWASP-A01-2021",
                title="Implementar Control de Acceso Robusto",
                description="Fortalecer mecanismos de autenticación y autorización para prevenir acceso no autorizado",
                framework=SecurityFramework.OWASP,
                category=RecommendationCategory.ACCESS_CONTROL,
                risk_level=RiskLevel.HIGH,
                impact="Previene acceso no autorizado a sistemas críticos",
                implementation_effort="Medium",
                compliance_references=["OWASP Top 10 2021 A01", "ISO 27001 A.9.1", "NIST SP 800-53 AC-2"],
                technical_details="Implementar autenticación multifactor, principio de menor privilegio y revisión periódica de accesos",
                remediation_steps=[
                    "Implementar autenticación de dos factores (2FA/MFA)",
                    "Aplicar principio de menor privilegio",
                    "Configurar timeouts de sesión apropiados",
                    "Implementar revisión periódica de cuentas de usuario",
                    "Usar contraseñas fuertes y políticas de rotación"
                ],
                priority_score=90,
                affected_assets=["User accounts", "Administrative interfaces", "API endpoints"]
            ),
            SecurityRecommendation(
                id="OWASP-A02-2021",
                title="Corregir Fallas Criptográficas",
                description="Implementar cifrado adecuado para datos en tránsito y en reposo",
                framework=SecurityFramework.OWASP,
                category=RecommendationCategory.DATA_PROTECTION,
                risk_level=RiskLevel.HIGH,
                impact="Protege datos sensibles de exposición y manipulación",
                implementation_effort="Medium",
                compliance_references=["OWASP Top 10 2021 A02", "ISO 27001 A.10.1", "NIST SP 800-53 SC-8"],
                technical_details="Usar algoritmos de cifrado modernos, gestión segura de claves y TLS 1.3",
                remediation_steps=[
                    "Implementar cifrado AES-256 para datos en reposo",
                    "Usar TLS 1.3 para todas las comunicaciones",
                    "Implementar gestión segura de claves criptográficas",
                    "Deshabilitar protocolos y cifrados obsoletos",
                    "Implementar Perfect Forward Secrecy (PFS)"
                ],
                priority_score=85,
                affected_assets=["Database", "Network communications", "File storage", "API connections"]
            ),
            SecurityRecommendation(
                id="OWASP-A03-2021",
                title="Validar y Sanitizar Entradas",
                description="Implementar validación robusta de todas las entradas del usuario",
                framework=SecurityFramework.OWASP,
                category=RecommendationCategory.VULNERABILITY_MANAGEMENT,
                risk_level=RiskLevel.HIGH,
                impact="Previene inyección de código y ataques de manipulación de datos",
                implementation_effort="High",
                compliance_references=["OWASP Top 10 2021 A03", "ISO 27001 A.14.2", "NIST SP 800-53 SI-10"],
                technical_details="Validación del lado servidor, sanitización de entradas, uso de consultas parametrizadas",
                remediation_steps=[
                    "Implementar validación de entrada en el servidor",
                    "Usar consultas SQL parametrizadas",
                    "Sanitizar todas las entradas del usuario",
                    "Implementar listas blancas de entrada",
                    "Usar frameworks con protección anti-inyección integrada"
                ],
                priority_score=80,
                affected_assets=["Web applications", "APIs", "Database interfaces", "User input forms"]
            ),
            SecurityRecommendation(
                id="OWASP-A06-2021",
                title="Fortalecer Configuración de Seguridad",
                description="Implementar configuraciones seguras y eliminar componentes innecesarios",
                framework=SecurityFramework.OWASP,
                category=RecommendationCategory.CONFIGURATION_MANAGEMENT,
                risk_level=RiskLevel.MEDIUM,
                impact="Reduce superficie de ataque y fortalece postura de seguridad",
                implementation_effort="Medium",
                compliance_references=["OWASP Top 10 2021 A06", "ISO 27001 A.12.6", "NIST SP 800-53 CM-6"],
                technical_details="Hardening de sistemas, deshabilitación de servicios innecesarios, configuración segura por defecto",
                remediation_steps=[
                    "Aplicar hardening de sistemas operativos",
                    "Deshabilitar servicios y puertos innecesarios",
                    "Configurar headers de seguridad HTTP",
                    "Implementar configuración segura por defecto",
                    "Realizar auditorías regulares de configuración"
                ],
                priority_score=70,
                affected_assets=["Operating systems", "Web servers", "Network devices", "Applications"]
            ),
            SecurityRecommendation(
                id="OWASP-A09-2021",
                title="Implementar Logging y Monitoreo de Seguridad",
                description="Establecer logging comprehensivo y monitoreo en tiempo real",
                framework=SecurityFramework.OWASP,
                category=RecommendationCategory.MONITORING_LOGGING,
                risk_level=RiskLevel.MEDIUM,
                impact="Mejora detección de incidentes y capacidad de respuesta",
                implementation_effort="High",
                compliance_references=["OWASP Top 10 2021 A09", "ISO 27001 A.12.4", "NIST SP 800-53 AU-2"],
                technical_details="SIEM, logs centralizados, alertas automáticas, retención de logs",
                remediation_steps=[
                    "Implementar solución SIEM centralizada",
                    "Configurar logging de eventos de seguridad",
                    "Establecer alertas automáticas para eventos críticos",
                    "Implementar retención apropiada de logs",
                    "Realizar análisis regular de logs de seguridad"
                ],
                priority_score=75,
                affected_assets=["All systems", "Network infrastructure", "Applications", "Security tools"]
            )
        ]

        # NIST Cybersecurity Framework
        nist_recommendations = [
            SecurityRecommendation(
                id="NIST-ID-AM-1",
                title="Inventario de Activos de Hardware",
                description="Mantener inventario actualizado de todos los dispositivos de hardware",
                framework=SecurityFramework.NIST,
                category=RecommendationCategory.CONFIGURATION_MANAGEMENT,
                risk_level=RiskLevel.MEDIUM,
                impact="Mejora visibilidad y control de activos organizacionales",
                implementation_effort="Medium",
                compliance_references=["NIST CSF ID.AM-1", "ISO 27001 A.8.1", "CIS Control 1"],
                technical_details="Implementar herramientas de descubrimiento automático y registro de activos",
                remediation_steps=[
                    "Implementar herramienta de gestión de activos",
                    "Realizar escaneo automático de red",
                    "Mantener base de datos de activos actualizada",
                    "Clasificar activos por criticidad",
                    "Establecer proceso de alta/baja de activos"
                ],
                priority_score=65,
                affected_assets=["Network devices", "Servers", "Workstations", "IoT devices"]
            ),
            SecurityRecommendation(
                id="NIST-ID-AM-2",
                title="Inventario de Activos de Software",
                description="Mantener inventario actualizado de todo el software instalado",
                framework=SecurityFramework.NIST,
                category=RecommendationCategory.CONFIGURATION_MANAGEMENT,
                risk_level=RiskLevel.MEDIUM,
                impact="Facilita gestión de vulnerabilidades y licencias de software",
                implementation_effort="Medium",
                compliance_references=["NIST CSF ID.AM-2", "ISO 27001 A.8.1", "CIS Control 2"],
                technical_details="Usar herramientas de inventario de software y gestión de licencias",
                remediation_steps=[
                    "Implementar herramientas de inventario de software",
                    "Escanear regularmente software instalado",
                    "Mantener lista de software autorizado",
                    "Identificar software no autorizado",
                    "Gestionar licencias y actualizaciones"
                ],
                priority_score=60,
                affected_assets=["All systems", "Applications", "Operating systems", "Firmware"]
            ),
            SecurityRecommendation(
                id="NIST-PR-AC-1",
                title="Gestión de Identidades y Credenciales",
                description="Implementar gestión centralizada de identidades y credenciales",
                framework=SecurityFramework.NIST,
                category=RecommendationCategory.ACCESS_CONTROL,
                risk_level=RiskLevel.HIGH,
                impact="Fortalece control de acceso y reduce riesgo de credenciales comprometidas",
                implementation_effort="High",
                compliance_references=["NIST CSF PR.AC-1", "ISO 27001 A.9.2", "NIST SP 800-63"],
                technical_details="Implementar solución IAM con SSO, MFA y gestión de ciclo de vida de identidades",
                remediation_steps=[
                    "Implementar solución de Identity Management (IAM)",
                    "Configurar Single Sign-On (SSO)",
                    "Implementar autenticación multifactor",
                    "Establecer políticas de contraseñas fuertes",
                    "Automatizar provisioning/deprovisioning de cuentas"
                ],
                priority_score=88,
                affected_assets=["User accounts", "Service accounts", "Administrative accounts", "API keys"]
            ),
            SecurityRecommendation(
                id="NIST-DE-CM-1",
                title="Monitoreo Continuo de Red",
                description="Implementar monitoreo continuo de actividad de red",
                framework=SecurityFramework.NIST,
                category=RecommendationCategory.MONITORING_LOGGING,
                risk_level=RiskLevel.MEDIUM,
                impact="Mejora detección temprana de actividades maliciosas",
                implementation_effort="High",
                compliance_references=["NIST CSF DE.CM-1", "ISO 27001 A.12.4", "NIST SP 800-94"],
                technical_details="Implementar IDS/IPS, análisis de tráfico de red y detección de anomalías",
                remediation_steps=[
                    "Implementar sistema IDS/IPS en puntos críticos",
                    "Configurar monitoreo de tráfico de red",
                    "Establecer baselines de tráfico normal",
                    "Implementar detección de anomalías",
                    "Configurar alertas automatizadas"
                ],
                priority_score=72,
                affected_assets=["Network infrastructure", "Firewalls", "Switches", "Routers"]
            )
        ]

        # ISO 27001 Controls
        iso27001_recommendations = [
            SecurityRecommendation(
                id="ISO27001-A.8.1.1",
                title="Inventario de Activos de Información",
                description="Mantener inventario preciso de todos los activos de información",
                framework=SecurityFramework.ISO27001,
                category=RecommendationCategory.CONFIGURATION_MANAGEMENT,
                risk_level=RiskLevel.MEDIUM,
                impact="Asegura protección adecuada de activos críticos de información",
                implementation_effort="Medium",
                compliance_references=["ISO 27001 A.8.1.1", "NIST CSF ID.AM-5"],
                technical_details="Clasificar y etiquetar activos según su valor y criticidad para el negocio",
                remediation_steps=[
                    "Identificar y catalogar todos los activos de información",
                    "Asignar propietarios responsables de cada activo",
                    "Clasificar activos según criticidad",
                    "Establecer procedimientos de manejo de activos",
                    "Revisar inventario periódicamente"
                ],
                priority_score=68,
                affected_assets=["Databases", "Documents", "Intellectual property", "Personal data"]
            ),
            SecurityRecommendation(
                id="ISO27001-A.9.1.2",
                title="Control de Acceso a Redes y Servicios",
                description="Implementar controles rigurosos de acceso a servicios de red",
                framework=SecurityFramework.ISO27001,
                category=RecommendationCategory.NETWORK_SECURITY,
                risk_level=RiskLevel.HIGH,
                impact="Previene acceso no autorizado a recursos de red críticos",
                implementation_effort="Medium",
                compliance_references=["ISO 27001 A.9.1.2", "NIST SP 800-53 AC-3"],
                technical_details="Segmentación de red, ACLs, VLANs y controles de acceso basados en roles",
                remediation_steps=[
                    "Implementar segmentación de red",
                    "Configurar firewalls con reglas restrictivas",
                    "Usar VLANs para separar tráfico",
                    "Implementar NAC (Network Access Control)",
                    "Monitorear accesos a servicios críticos"
                ],
                priority_score=82,
                affected_assets=["Network services", "Servers", "Databases", "Critical applications"]
            ),
            SecurityRecommendation(
                id="ISO27001-A.12.4.1",
                title="Registro de Eventos (Event Logging)",
                description="Implementar logging comprehensivo de eventos de seguridad",
                framework=SecurityFramework.ISO27001,
                category=RecommendationCategory.MONITORING_LOGGING,
                risk_level=RiskLevel.MEDIUM,
                impact="Facilita detección de incidentes y análisis forense",
                implementation_effort="High",
                compliance_references=["ISO 27001 A.12.4.1", "NIST SP 800-53 AU-2"],
                technical_details="Logging centralizado, protección de logs, retención apropiada y análisis automatizado",
                remediation_steps=[
                    "Configurar logging en todos los sistemas críticos",
                    "Centralizar logs en servidor seguro",
                    "Implementar protección de integridad de logs",
                    "Establecer políticas de retención",
                    "Configurar análisis automatizado de logs"
                ],
                priority_score=75,
                affected_assets=["All systems", "Security devices", "Applications", "Network equipment"]
            ),
            SecurityRecommendation(
                id="ISO27001-A.13.1.1",
                title="Controles de Red",
                description="Implementar controles de seguridad en redes",
                framework=SecurityFramework.ISO27001,
                category=RecommendationCategory.NETWORK_SECURITY,
                risk_level=RiskLevel.HIGH,
                impact="Protege integridad y confidencialidad de comunicaciones de red",
                implementation_effort="High",
                compliance_references=["ISO 27001 A.13.1.1", "NIST SP 800-53 SC-7"],
                technical_details="Firewalls, IPS, segmentación de red, cifrado de comunicaciones",
                remediation_steps=[
                    "Implementar firewalls de nueva generación",
                    "Configurar IPS en puntos críticos",
                    "Implementar segmentación de red",
                    "Usar cifrado para comunicaciones críticas",
                    "Monitorear tráfico de red continuamente"
                ],
                priority_score=85,
                affected_assets=["Network infrastructure", "Communication channels", "Remote connections"]
            ),
            SecurityRecommendation(
                id="ISO27001-A.16.1.1",
                title="Responsabilidades y Procedimientos de Gestión de Incidentes",
                description="Establecer procedimientos formales de gestión de incidentes de seguridad",
                framework=SecurityFramework.ISO27001,
                category=RecommendationCategory.INCIDENT_RESPONSE,
                risk_level=RiskLevel.MEDIUM,
                impact="Mejora capacidad de respuesta y recuperación ante incidentes",
                implementation_effort="Medium",
                compliance_references=["ISO 27001 A.16.1.1", "NIST SP 800-61"],
                technical_details="Plan de respuesta a incidentes, equipo CSIRT, procedimientos de comunicación",
                remediation_steps=[
                    "Desarrollar plan de respuesta a incidentes",
                    "Formar equipo de respuesta (CSIRT)",
                    "Establecer procedimientos de comunicación",
                    "Implementar herramientas de gestión de incidentes",
                    "Realizar ejercicios de simulación regulares"
                ],
                priority_score=70,
                affected_assets=["All organizational assets", "Business processes", "Reputation"]
            )
        ]

        # Agregar todas las recomendaciones al diccionario
        all_recommendations = owasp_recommendations + nist_recommendations + iso27001_recommendations

        for rec in all_recommendations:
            recommendations[rec.id] = rec

        return recommendations

    def analyze_system_security(self, system_metrics: Dict[str, Any]) -> List[SecurityRecommendation]:
        """Analiza las métricas del sistema y genera recomendaciones contextuales"""
        applicable_recommendations = []

        try:
            # Analizar métricas del sistema
            system_info = system_metrics.get('system', {})
            security_info = system_metrics.get('security', {})
            enterprise_modules = system_metrics.get('enterprise_modules', {})
            network_details = system_info.get('network_details', [])
            layer12_details = system_info.get('layer12_details', [])

            # Análisis de red y conectividad
            if len(network_details) > 20:
                # Red compleja, recomendar monitoreo avanzado
                applicable_recommendations.extend([
                    self.recommendations_db['NIST-DE-CM-1'],
                    self.recommendations_db['ISO27001-A.13.1.1']
                ])

            # Análisis de conexiones de capa 1/2
            if layer12_details:
                dhcp_active_count = sum(1 for conn in layer12_details if conn.get('dhcp_active'))
                if dhcp_active_count > 0:
                    # DHCP detectado, recomendar controles de red
                    applicable_recommendations.append(self.recommendations_db['ISO27001-A.9.1.2'])

                # Verificar VLANs
                vlan_count = sum(1 for conn in layer12_details if conn.get('vlan_id'))
                if vlan_count == 0:
                    # Sin VLANs, recomendar segmentación
                    applicable_recommendations.append(self.recommendations_db['ISO27001-A.13.1.1'])

            # Análisis de módulos de seguridad
            security_modules_ok = sum(1 for data in security_info.values()
                                    if isinstance(data, dict) and not data.get('error'))

            if security_modules_ok < len(security_info):
                # Módulos de seguridad con errores
                applicable_recommendations.extend([
                    self.recommendations_db['OWASP-A06-2021'],
                    self.recommendations_db['OWASP-A01-2021']
                ])

            # Análisis de logging y monitoreo
            if not security_info.get('logging_configured'):
                applicable_recommendations.extend([
                    self.recommendations_db['OWASP-A09-2021'],
                    self.recommendations_db['ISO27001-A.12.4.1']
                ])

            # Recomendaciones base siempre aplicables
            base_recommendations = [
                self.recommendations_db['OWASP-A01-2021'],
                self.recommendations_db['OWASP-A02-2021'],
                self.recommendations_db['NIST-ID-AM-1'],
                self.recommendations_db['NIST-PR-AC-1'],
                self.recommendations_db['ISO27001-A.8.1.1'],
                self.recommendations_db['ISO27001-A.16.1.1']
            ]

            applicable_recommendations.extend(base_recommendations)

            # Eliminar duplicados y ordenar por prioridad
            seen_ids = set()
            unique_recommendations = []
            for rec in applicable_recommendations:
                if rec.id not in seen_ids:
                    unique_recommendations.append(rec)
                    seen_ids.add(rec.id)

            # Ordenar por score de prioridad (descendente)
            unique_recommendations.sort(key=lambda x: x.priority_score, reverse=True)

            return unique_recommendations[:12]  # Top 12 recomendaciones

        except Exception as e:
            self.logger.error(f"Error analyzing system security: {e}")
            return []

    def generate_security_summary(self, recommendations: List[SecurityRecommendation]) -> Dict[str, Any]:
        """Genera resumen de las recomendaciones de seguridad"""
        try:
            # Estadísticas por framework
            framework_stats = {}
            for framework in SecurityFramework:
                count = sum(1 for rec in recommendations if rec.framework == framework)
                framework_stats[framework.value] = count

            # Estadísticas por nivel de riesgo
            risk_stats = {}
            for risk in RiskLevel:
                count = sum(1 for rec in recommendations if rec.risk_level == risk)
                risk_stats[risk.value] = count

            # Estadísticas por categoría
            category_stats = {}
            for category in RecommendationCategory:
                count = sum(1 for rec in recommendations if rec.category == category)
                category_stats[category.value] = count

            # Score de seguridad general
            total_score = sum(rec.priority_score for rec in recommendations)
            avg_priority = total_score / len(recommendations) if recommendations else 0

            # Determinar nivel de seguridad general
            if avg_priority >= 80:
                security_level = "CRÍTICO - Acción Inmediata Requerida"
                security_color = "danger"
            elif avg_priority >= 70:
                security_level = "ALTO - Atención Prioritaria"
                security_color = "warning"
            elif avg_priority >= 60:
                security_level = "MEDIO - Mejoras Recomendadas"
                security_color = "info"
            else:
                security_level = "BAJO - Monitoreo Regular"
                security_color = "success"

            return {
                'total_recommendations': len(recommendations),
                'framework_distribution': framework_stats,
                'risk_distribution': risk_stats,
                'category_distribution': category_stats,
                'average_priority': round(avg_priority, 2),
                'security_level': security_level,
                'security_color': security_color,
                'top_priority_recommendations': recommendations[:5],
                'generated_at': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error generating security summary: {e}")
            return {}

    def export_recommendations(self, recommendations: List[SecurityRecommendation],
                             output_format: str = 'json') -> str:
        """Exporta recomendaciones en formato especificado"""
        try:
            if output_format.lower() == 'json':
                return json.dumps([asdict(rec) for rec in recommendations],
                                indent=2, default=str)
            else:
                raise ValueError(f"Formato no soportado: {output_format}")

        except Exception as e:
            self.logger.error(f"Error exporting recommendations: {e}")
            return ""


# Función de demostración
def demo_security_recommendations():
    """Demostración del motor de recomendaciones de seguridad"""
    print("🛡️ SmartCompute Security Recommendations Engine Demo")
    print("=" * 60)

    engine = SmartComputeSecurityRecommendationsEngine()

    # Simular métricas del sistema
    sample_metrics = {
        'system': {
            'network_details': [{'connection': f'conn_{i}'} for i in range(25)],
            'layer12_details': [
                {'dhcp_active': True, 'vlan_id': None},
                {'dhcp_active': False, 'vlan_id': 100}
            ]
        },
        'security': {
            'module1': {'error': False},
            'module2': {'error': True}
        }
    }

    # Generar recomendaciones
    recommendations = engine.analyze_system_security(sample_metrics)
    summary = engine.generate_security_summary(recommendations)

    print(f"📊 Recomendaciones Generadas: {summary['total_recommendations']}")
    print(f"🎯 Nivel de Seguridad: {summary['security_level']}")
    print(f"📈 Prioridad Promedio: {summary['average_priority']}")

    print("\n🏆 Top 5 Recomendaciones Prioritarias:")
    for i, rec in enumerate(summary['top_priority_recommendations'], 1):
        print(f"   {i}. [{rec.framework.value}] {rec.title}")
        print(f"      Risk: {rec.risk_level.value} | Priority: {rec.priority_score}")

    print(f"\n📋 Distribución por Framework:")
    for framework, count in summary['framework_distribution'].items():
        print(f"   {framework}: {count} recomendaciones")


if __name__ == "__main__":
    demo_security_recommendations()