#!/usr/bin/env python3
"""
SmartCompute Enterprise - Compliance-Aware Incident Workflows

Sistema de workflows de incidentes consciente de compliance que:
- Automatiza respuestas según marcos regulatorios (SOX, HIPAA, PCI-DSS, GDPR)
- Gestiona notificaciones obligatorias y plazos regulatorios
- Implementa cadenas de custodia para evidencia digital
- Automatiza reportes de compliance y auditoría
- Coordina con equipos legales y de compliance
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
from collections import defaultdict
from enum import Enum
import uuid

# Import previous components
from siem_intelligence_coordinator import SIEMAlert, ThreatCorrelation, AlertSeverity
from intelligent_alert_aggregator import AlertCluster, AlertPriority
from ml_threat_prioritization import MLPrediction, ThreatCategory

class ComplianceFramework(Enum):
    SOX = "sox"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    GDPR = "gdpr"
    ISO27001 = "iso27001"
    NIST = "nist"
    CCPA = "ccpa"
    FISMA = "fisma"

class IncidentSeverity(Enum):
    INFORMATIONAL = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    CATASTROPHIC = 5

class WorkflowStatus(Enum):
    INITIATED = "initiated"
    IN_PROGRESS = "in_progress"
    PENDING_APPROVAL = "pending_approval"
    ESCALATED = "escalated"
    UNDER_INVESTIGATION = "under_investigation"
    EVIDENCE_COLLECTION = "evidence_collection"
    LEGAL_REVIEW = "legal_review"
    REGULATORY_REPORTING = "regulatory_reporting"
    REMEDIATION = "remediation"
    CLOSED = "closed"
    ARCHIVED = "archived"

@dataclass
class ComplianceRequirement:
    """Requisito de compliance específico"""
    requirement_id: str
    framework: ComplianceFramework
    title: str
    description: str
    notification_deadline_hours: int
    reporting_deadline_hours: int
    evidence_retention_days: int
    required_stakeholders: List[str]
    regulatory_body: Optional[str] = None
    penalties: Optional[str] = None
    automation_level: float = 0.8  # 0.0 = manual, 1.0 = fully automated

@dataclass
class EvidenceItem:
    """Item de evidencia digital"""
    evidence_id: str
    incident_id: str
    evidence_type: str  # logs, files, network_captures, screenshots, etc.
    source: str
    collection_timestamp: datetime
    hash_sha256: str
    chain_of_custody: List[Dict[str, Any]]
    preservation_status: str
    legal_hold: bool = False
    retention_until: Optional[datetime] = None

@dataclass
class IncidentWorkflow:
    """Workflow de incidente con compliance"""
    incident_id: str
    title: str
    description: str
    severity: IncidentSeverity
    status: WorkflowStatus
    applicable_frameworks: List[ComplianceFramework]
    business_units_affected: List[str]
    data_types_involved: List[str]

    # Stakeholders and notifications
    assigned_analyst: Optional[str] = None
    compliance_officer: Optional[str] = None
    legal_counsel: Optional[str] = None
    privacy_officer: Optional[str] = None

    # Timeline and deadlines
    created_at: datetime = None
    first_response_deadline: Optional[datetime] = None
    notification_deadline: Optional[datetime] = None
    reporting_deadline: Optional[datetime] = None

    # Evidence and documentation
    evidence_items: List[EvidenceItem] = None
    regulatory_notifications: List[Dict[str, Any]] = None
    compliance_reports: List[Dict[str, Any]] = None

    # Source data
    related_clusters: List[str] = None
    ml_predictions: List[str] = None

    # Workflow history
    workflow_history: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.evidence_items is None:
            self.evidence_items = []
        if self.regulatory_notifications is None:
            self.regulatory_notifications = []
        if self.compliance_reports is None:
            self.compliance_reports = []
        if self.related_clusters is None:
            self.related_clusters = []
        if self.ml_predictions is None:
            self.ml_predictions = []
        if self.workflow_history is None:
            self.workflow_history = []

@dataclass
class NotificationTemplate:
    """Template para notificaciones regulatorias"""
    template_id: str
    framework: ComplianceFramework
    notification_type: str
    template_content: str
    required_fields: List[str]
    delivery_method: str  # email, portal, certified_mail, etc.
    follow_up_required: bool = False

class ComplianceIncidentManager:
    """Gestor de workflows de incidentes consciente de compliance"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("ComplianceIncidentManager")

        # Load compliance frameworks and requirements
        self.compliance_requirements = self._load_compliance_requirements()
        self.notification_templates = self._load_notification_templates()

        # Workflow state
        self.active_workflows: Dict[str, IncidentWorkflow] = {}
        self.evidence_repository: Dict[str, EvidenceItem] = {}

        # Organizational configuration
        self.organization_info = config.get("organization", {
            "name": "SmartCompute Enterprise",
            "dpo_email": "dpo@smartcompute.com",
            "ciso_email": "ciso@smartcompute.com",
            "legal_email": "legal@smartcompute.com",
            "compliance_email": "compliance@smartcompute.com"
        })

        # Automation settings
        self.automation_enabled = config.get("automation_enabled", True)
        self.auto_evidence_collection = config.get("auto_evidence_collection", True)
        self.auto_notifications = config.get("auto_notifications", False)

    def _load_compliance_requirements(self) -> Dict[ComplianceFramework, List[ComplianceRequirement]]:
        """Cargar requisitos de compliance por framework"""
        requirements = {}

        # SOX (Sarbanes-Oxley Act)
        requirements[ComplianceFramework.SOX] = [
            ComplianceRequirement(
                requirement_id="SOX_404",
                framework=ComplianceFramework.SOX,
                title="Internal Controls Over Financial Reporting",
                description="Document and test internal controls for financial data",
                notification_deadline_hours=24,
                reporting_deadline_hours=72,
                evidence_retention_days=2555,  # 7 years
                required_stakeholders=["cfo", "compliance_officer", "external_auditor"],
                regulatory_body="SEC",
                penalties="Criminal charges, fines up to $5M"
            ),
            ComplianceRequirement(
                requirement_id="SOX_302",
                framework=ComplianceFramework.SOX,
                title="Corporate Responsibility for Financial Reports",
                description="CEO/CFO certification of financial controls",
                notification_deadline_hours=12,
                reporting_deadline_hours=48,
                evidence_retention_days=2555,
                required_stakeholders=["ceo", "cfo", "compliance_officer"],
                regulatory_body="SEC",
                penalties="Up to 20 years imprisonment"
            )
        ]

        # HIPAA (Health Insurance Portability and Accountability Act)
        requirements[ComplianceFramework.HIPAA] = [
            ComplianceRequirement(
                requirement_id="HIPAA_BREACH",
                framework=ComplianceFramework.HIPAA,
                title="Breach Notification Rule",
                description="Notification of PHI breaches affecting 500+ individuals",
                notification_deadline_hours=72,  # 72 hours to notify
                reporting_deadline_hours=1440,  # 60 days for full report
                evidence_retention_days=2190,  # 6 years
                required_stakeholders=["privacy_officer", "compliance_officer", "legal_counsel"],
                regulatory_body="HHS OCR",
                penalties="Up to $1.5M per incident"
            ),
            ComplianceRequirement(
                requirement_id="HIPAA_SECURITY",
                framework=ComplianceFramework.HIPAA,
                title="Security Rule Compliance",
                description="Safeguarding of electronic PHI",
                notification_deadline_hours=24,
                reporting_deadline_hours=168,  # 7 days
                evidence_retention_days=2190,
                required_stakeholders=["security_officer", "privacy_officer"],
                regulatory_body="HHS OCR",
                penalties="Up to $50,000 per violation"
            )
        ]

        # PCI-DSS (Payment Card Industry Data Security Standard)
        requirements[ComplianceFramework.PCI_DSS] = [
            ComplianceRequirement(
                requirement_id="PCI_INCIDENT",
                framework=ComplianceFramework.PCI_DSS,
                title="Security Incident Response",
                description="Response to cardholder data security incidents",
                notification_deadline_hours=24,
                reporting_deadline_hours=72,
                evidence_retention_days=365,
                required_stakeholders=["security_officer", "compliance_officer"],
                regulatory_body="Card Brands",
                penalties="Fines up to $100,000 per month"
            )
        ]

        # GDPR (General Data Protection Regulation)
        requirements[ComplianceFramework.GDPR] = [
            ComplianceRequirement(
                requirement_id="GDPR_BREACH",
                framework=ComplianceFramework.GDPR,
                title="Personal Data Breach Notification",
                description="Notification of personal data breaches",
                notification_deadline_hours=72,
                reporting_deadline_hours=720,  # 30 days for detailed report
                evidence_retention_days=2555,  # 7 years for evidence
                required_stakeholders=["dpo", "legal_counsel", "privacy_officer"],
                regulatory_body="Data Protection Authority",
                penalties="Up to 4% of annual global turnover"
            )
        ]

        return requirements

    def _load_notification_templates(self) -> Dict[str, NotificationTemplate]:
        """Cargar templates de notificación"""
        templates = {}

        # SOX notification template
        templates["sox_incident"] = NotificationTemplate(
            template_id="sox_incident",
            framework=ComplianceFramework.SOX,
            notification_type="incident_report",
            template_content="""
CONFIDENTIAL - SOX Incident Notification

Incident ID: {incident_id}
Date/Time: {incident_date}
Severity: {severity}

Description:
{description}

Financial Systems Affected:
{affected_systems}

Potential Impact on Financial Reporting:
{financial_impact}

Immediate Actions Taken:
{immediate_actions}

Next Steps:
{next_steps}

Contact: {compliance_officer}
""",
            required_fields=["incident_id", "incident_date", "severity", "description",
                           "affected_systems", "financial_impact", "immediate_actions",
                           "next_steps", "compliance_officer"],
            delivery_method="secure_email"
        )

        # HIPAA breach notification template
        templates["hipaa_breach"] = NotificationTemplate(
            template_id="hipaa_breach",
            framework=ComplianceFramework.HIPAA,
            notification_type="breach_notification",
            template_content="""
HIPAA Breach Notification - CONFIDENTIAL

Incident ID: {incident_id}
Date of Discovery: {discovery_date}
Estimated Date of Breach: {breach_date}

Description of Breach:
{description}

PHI Involved:
{phi_types}

Number of Individuals Affected: {affected_count}

Risk Assessment:
{risk_assessment}

Mitigation Actions:
{mitigation_actions}

Contact Information:
Privacy Officer: {privacy_officer}
Legal Counsel: {legal_counsel}
""",
            required_fields=["incident_id", "discovery_date", "breach_date", "description",
                           "phi_types", "affected_count", "risk_assessment",
                           "mitigation_actions", "privacy_officer", "legal_counsel"],
            delivery_method="certified_mail",
            follow_up_required=True
        )

        return templates

    async def create_compliance_workflow(self, clusters: List[AlertCluster],
                                       ml_predictions: List[MLPrediction]) -> IncidentWorkflow:
        """Crear workflow de incidente consciente de compliance"""
        self.logger.info(f"🏛️ Creating compliance-aware incident workflow for {len(clusters)} clusters")

        # Analyze compliance implications
        applicable_frameworks = await self._analyze_compliance_frameworks(clusters)

        # Determine incident severity
        incident_severity = await self._calculate_incident_severity(clusters, ml_predictions)

        # Extract business context
        business_context = await self._extract_business_context(clusters)

        # Create incident workflow
        incident_id = f"INC_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

        workflow = IncidentWorkflow(
            incident_id=incident_id,
            title=await self._generate_incident_title(clusters, ml_predictions),
            description=await self._generate_incident_description(clusters, ml_predictions),
            severity=incident_severity,
            status=WorkflowStatus.INITIATED,
            applicable_frameworks=applicable_frameworks,
            business_units_affected=business_context["business_units"],
            data_types_involved=business_context["data_types"],
            related_clusters=[cluster.cluster_id for cluster in clusters],
            ml_predictions=[pred.prediction_id for pred in ml_predictions]
        )

        # Set compliance deadlines
        await self._set_compliance_deadlines(workflow)

        # Assign stakeholders
        await self._assign_stakeholders(workflow)

        # Initialize evidence collection
        if self.auto_evidence_collection:
            await self._initiate_evidence_collection(workflow, clusters)

        # Add to active workflows
        self.active_workflows[incident_id] = workflow

        # Log workflow creation
        await self._log_workflow_event(workflow, "workflow_created",
                                     "Compliance incident workflow initiated")

        self.logger.info(f"✅ Compliance workflow {incident_id} created successfully")
        return workflow

    async def _analyze_compliance_frameworks(self, clusters: List[AlertCluster]) -> List[ComplianceFramework]:
        """Analizar frameworks de compliance aplicables"""
        applicable_frameworks = set()

        for cluster in clusters:
            # Check business context
            business_units = cluster.business_context.get("business_units", [])
            compliance_frameworks = cluster.business_context.get("compliance_frameworks", [])

            # Map business units to frameworks
            unit_framework_mapping = {
                "finance": [ComplianceFramework.SOX],
                "healthcare": [ComplianceFramework.HIPAA],
                "payments": [ComplianceFramework.PCI_DSS],
                "hr": [ComplianceFramework.GDPR],
                "executive": [ComplianceFramework.SOX, ComplianceFramework.GDPR]
            }

            for unit in business_units:
                if unit in unit_framework_mapping:
                    applicable_frameworks.update(unit_framework_mapping[unit])

            # Direct framework mapping
            framework_mapping = {
                "SOX": ComplianceFramework.SOX,
                "HIPAA": ComplianceFramework.HIPAA,
                "PCI-DSS": ComplianceFramework.PCI_DSS,
                "GDPR": ComplianceFramework.GDPR,
                "ISO27001": ComplianceFramework.ISO27001
            }

            for fw in compliance_frameworks:
                if fw in framework_mapping:
                    applicable_frameworks.add(framework_mapping[fw])

            # Analyze alert content for compliance indicators
            all_alerts = [cluster.primary_alert] + cluster.related_alerts
            for alert in all_alerts:
                alert_text = f"{alert.title} {alert.description}".lower()

                # Look for compliance-related keywords
                if any(keyword in alert_text for keyword in ['financial', 'payment', 'sox']):
                    applicable_frameworks.add(ComplianceFramework.SOX)
                if any(keyword in alert_text for keyword in ['health', 'medical', 'phi', 'hipaa']):
                    applicable_frameworks.add(ComplianceFramework.HIPAA)
                if any(keyword in alert_text for keyword in ['card', 'payment', 'pci']):
                    applicable_frameworks.add(ComplianceFramework.PCI_DSS)
                if any(keyword in alert_text for keyword in ['personal', 'privacy', 'gdpr']):
                    applicable_frameworks.add(ComplianceFramework.GDPR)

        return list(applicable_frameworks)

    async def _calculate_incident_severity(self, clusters: List[AlertCluster],
                                         ml_predictions: List[MLPrediction]) -> IncidentSeverity:
        """Calcular severidad del incidente"""
        # Get highest cluster priority
        max_cluster_priority = max((cluster.cluster_priority.value for cluster in clusters), default=0)

        # Get highest ML threat score
        max_ml_score = max((pred.threat_score for pred in ml_predictions), default=0.0)

        # Consider business impact
        business_critical = any(
            "executive" in cluster.business_context.get("business_units", []) or
            "finance" in cluster.business_context.get("business_units", [])
            for cluster in clusters
        )

        # Calculate composite severity
        if max_ml_score >= 0.9 and business_critical:
            return IncidentSeverity.CATASTROPHIC
        elif max_ml_score >= 0.8 or max_cluster_priority >= 4:
            return IncidentSeverity.CRITICAL
        elif max_ml_score >= 0.7 or max_cluster_priority >= 3:
            return IncidentSeverity.HIGH
        elif max_ml_score >= 0.5 or max_cluster_priority >= 2:
            return IncidentSeverity.MEDIUM
        elif max_ml_score >= 0.3:
            return IncidentSeverity.LOW
        else:
            return IncidentSeverity.INFORMATIONAL

    async def _extract_business_context(self, clusters: List[AlertCluster]) -> Dict[str, Any]:
        """Extraer contexto de negocio de los clusters"""
        business_units = set()
        data_types = set()

        for cluster in clusters:
            # Extract business units
            cluster_units = cluster.business_context.get("business_units", [])
            business_units.update(cluster_units)

            # Infer data types from content
            all_alerts = [cluster.primary_alert] + cluster.related_alerts
            for alert in all_alerts:
                alert_text = f"{alert.title} {alert.description}".lower()

                # Data type identification
                if any(keyword in alert_text for keyword in ['financial', 'accounting', 'payment']):
                    data_types.add("financial_data")
                if any(keyword in alert_text for keyword in ['health', 'medical', 'patient']):
                    data_types.add("health_information")
                if any(keyword in alert_text for keyword in ['personal', 'customer', 'employee']):
                    data_types.add("personal_data")
                if any(keyword in alert_text for keyword in ['card', 'credit', 'payment']):
                    data_types.add("payment_data")
                if any(keyword in alert_text for keyword in ['intellectual', 'proprietary', 'trade']):
                    data_types.add("intellectual_property")

        return {
            "business_units": list(business_units),
            "data_types": list(data_types)
        }

    async def _generate_incident_title(self, clusters: List[AlertCluster],
                                     ml_predictions: List[MLPrediction]) -> str:
        """Generar título del incidente"""
        # Get primary threat category
        if ml_predictions:
            primary_category = ml_predictions[0].threat_category.value
        else:
            primary_category = "security_incident"

        # Get affected business units
        business_units = set()
        for cluster in clusters:
            cluster_units = cluster.business_context.get("business_units", [])
            business_units.update(cluster_units)

        business_context = f" affecting {', '.join(list(business_units)[:2])}" if business_units else ""

        # Count total alerts
        total_alerts = sum(len(cluster.related_alerts) + 1 for cluster in clusters)

        return f"Security Incident: {primary_category.replace('_', ' ').title()}{business_context} ({total_alerts} alerts)"

    async def _generate_incident_description(self, clusters: List[AlertCluster],
                                           ml_predictions: List[MLPrediction]) -> str:
        """Generar descripción del incidente"""
        description_parts = []

        # Summary statistics
        total_alerts = sum(len(cluster.related_alerts) + 1 for cluster in clusters)
        platforms = set()
        for cluster in clusters:
            all_alerts = [cluster.primary_alert] + cluster.related_alerts
            for alert in all_alerts:
                platforms.add(alert.platform.value)

        description_parts.append(f"Security incident involving {total_alerts} alerts across {len(platforms)} SIEM platforms.")

        # ML analysis summary
        if ml_predictions:
            avg_threat_score = sum(pred.threat_score for pred in ml_predictions) / len(ml_predictions)
            threat_categories = [pred.threat_category.value for pred in ml_predictions]
            description_parts.append(f"ML analysis indicates average threat score of {avg_threat_score:.2f} with categories: {', '.join(set(threat_categories))}.")

        # Business impact
        business_units = set()
        for cluster in clusters:
            cluster_units = cluster.business_context.get("business_units", [])
            business_units.update(cluster_units)

        if business_units:
            description_parts.append(f"Potentially affecting business units: {', '.join(business_units)}.")

        # Timeline
        description_parts.append(f"Incident detected and workflow initiated at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}.")

        return " ".join(description_parts)

    async def _set_compliance_deadlines(self, workflow: IncidentWorkflow):
        """Establecer plazos de compliance"""
        # Get strictest deadlines from applicable frameworks
        min_notification_hours = 999999
        min_reporting_hours = 999999

        for framework in workflow.applicable_frameworks:
            if framework in self.compliance_requirements:
                for requirement in self.compliance_requirements[framework]:
                    min_notification_hours = min(min_notification_hours, requirement.notification_deadline_hours)
                    min_reporting_hours = min(min_reporting_hours, requirement.reporting_deadline_hours)

        # Set deadlines
        if min_notification_hours < 999999:
            workflow.notification_deadline = workflow.created_at + timedelta(hours=min_notification_hours)

        if min_reporting_hours < 999999:
            workflow.reporting_deadline = workflow.created_at + timedelta(hours=min_reporting_hours)

        # Set first response deadline (always within 4 hours for security incidents)
        workflow.first_response_deadline = workflow.created_at + timedelta(hours=4)

    async def _assign_stakeholders(self, workflow: IncidentWorkflow):
        """Asignar stakeholders según compliance"""
        # Default assignments
        workflow.assigned_analyst = "security_analyst_001"

        # Framework-specific assignments
        for framework in workflow.applicable_frameworks:
            if framework == ComplianceFramework.SOX:
                workflow.compliance_officer = "sox_compliance_officer"
                workflow.legal_counsel = "securities_attorney"
            elif framework == ComplianceFramework.HIPAA:
                workflow.privacy_officer = "hipaa_privacy_officer"
                workflow.compliance_officer = "healthcare_compliance"
            elif framework == ComplianceFramework.GDPR:
                workflow.privacy_officer = "gdpr_dpo"
                workflow.legal_counsel = "privacy_attorney"
            elif framework == ComplianceFramework.PCI_DSS:
                workflow.compliance_officer = "pci_compliance_officer"

        # Default fallbacks
        if not workflow.compliance_officer:
            workflow.compliance_officer = "chief_compliance_officer"
        if not workflow.legal_counsel:
            workflow.legal_counsel = "general_counsel"

    async def _initiate_evidence_collection(self, workflow: IncidentWorkflow, clusters: List[AlertCluster]):
        """Iniciar recolección de evidencia"""
        self.logger.info(f"🔍 Initiating evidence collection for incident {workflow.incident_id}")

        for cluster in clusters:
            all_alerts = [cluster.primary_alert] + cluster.related_alerts

            for alert in all_alerts:
                # Collect alert logs as evidence
                evidence_item = EvidenceItem(
                    evidence_id=f"LOG_{alert.alert_id}",
                    incident_id=workflow.incident_id,
                    evidence_type="siem_alert",
                    source=alert.platform.value,
                    collection_timestamp=datetime.utcnow(),
                    hash_sha256=self._calculate_evidence_hash(alert),
                    chain_of_custody=[{
                        "action": "automated_collection",
                        "timestamp": datetime.utcnow().isoformat(),
                        "actor": "smartcompute_compliance_system",
                        "location": "enterprise_evidence_repository"
                    }],
                    preservation_status="preserved"
                )

                # Set legal hold for compliance frameworks
                if any(fw in [ComplianceFramework.SOX, ComplianceFramework.HIPAA]
                       for fw in workflow.applicable_frameworks):
                    evidence_item.legal_hold = True

                # Set retention period
                max_retention_days = 0
                for framework in workflow.applicable_frameworks:
                    if framework in self.compliance_requirements:
                        for requirement in self.compliance_requirements[framework]:
                            max_retention_days = max(max_retention_days, requirement.evidence_retention_days)

                if max_retention_days > 0:
                    evidence_item.retention_until = datetime.utcnow() + timedelta(days=max_retention_days)

                workflow.evidence_items.append(evidence_item)
                self.evidence_repository[evidence_item.evidence_id] = evidence_item

        self.logger.info(f"📦 Collected {len(workflow.evidence_items)} evidence items")

    def _calculate_evidence_hash(self, alert: SIEMAlert) -> str:
        """Calcular hash de evidencia para integridad"""
        import hashlib

        # Create deterministic string representation
        alert_data = {
            "alert_id": alert.alert_id,
            "platform": alert.platform.value,
            "title": alert.title,
            "description": alert.description,
            "timestamp": alert.timestamp.isoformat(),
            "severity": alert.severity.value
        }

        alert_json = json.dumps(alert_data, sort_keys=True)
        return hashlib.sha256(alert_json.encode()).hexdigest()

    async def _log_workflow_event(self, workflow: IncidentWorkflow, event_type: str, description: str):
        """Registrar evento en el workflow"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "description": description,
            "status": workflow.status.value,
            "actor": "system"
        }
        workflow.workflow_history.append(event)

    async def process_compliance_notifications(self, workflow: IncidentWorkflow) -> List[Dict[str, Any]]:
        """Procesar notificaciones de compliance"""
        self.logger.info(f"📧 Processing compliance notifications for {workflow.incident_id}")

        notifications = []

        for framework in workflow.applicable_frameworks:
            # Check if notification is required
            if workflow.severity.value >= IncidentSeverity.HIGH.value:

                # Create framework-specific notification
                notification = await self._create_compliance_notification(workflow, framework)

                if self.auto_notifications:
                    # Auto-send notification (simulated)
                    await self._send_notification(notification)
                    notification["status"] = "sent"
                else:
                    notification["status"] = "pending_approval"

                notifications.append(notification)
                workflow.regulatory_notifications.append(notification)

        await self._log_workflow_event(workflow, "notifications_processed",
                                     f"Processed {len(notifications)} compliance notifications")

        return notifications

    async def _create_compliance_notification(self, workflow: IncidentWorkflow,
                                            framework: ComplianceFramework) -> Dict[str, Any]:
        """Crear notificación específica de framework"""

        # Get appropriate template
        template_key = f"{framework.value}_incident"
        if template_key in self.notification_templates:
            template = self.notification_templates[template_key]
        else:
            # Generic template
            template = self._create_generic_template(framework)

        # Populate template fields
        notification_content = template.template_content.format(
            incident_id=workflow.incident_id,
            incident_date=workflow.created_at.strftime('%Y-%m-%d %H:%M:%S UTC'),
            severity=workflow.severity.name,
            description=workflow.description,
            affected_systems=', '.join(workflow.business_units_affected),
            financial_impact="Under assessment",
            immediate_actions="Incident response team activated",
            next_steps="Investigation and containment in progress",
            compliance_officer=workflow.compliance_officer or "TBD",
            discovery_date=workflow.created_at.strftime('%Y-%m-%d'),
            breach_date="Under investigation",
            phi_types=', '.join(workflow.data_types_involved),
            affected_count="Under assessment",
            risk_assessment="Initial assessment in progress",
            mitigation_actions="Standard incident response procedures",
            privacy_officer=workflow.privacy_officer or "TBD",
            legal_counsel=workflow.legal_counsel or "TBD"
        )

        notification = {
            "notification_id": f"NOTIFY_{workflow.incident_id}_{framework.value}",
            "incident_id": workflow.incident_id,
            "framework": framework.value,
            "notification_type": template.notification_type,
            "content": notification_content,
            "created_at": datetime.utcnow().isoformat(),
            "deadline": workflow.notification_deadline.isoformat() if workflow.notification_deadline else None,
            "delivery_method": template.delivery_method,
            "recipients": self._get_notification_recipients(framework),
            "status": "created"
        }

        return notification

    def _create_generic_template(self, framework: ComplianceFramework) -> NotificationTemplate:
        """Crear template genérico"""
        return NotificationTemplate(
            template_id=f"generic_{framework.value}",
            framework=framework,
            notification_type="incident_notification",
            template_content="""
{framework} Compliance Incident Notification

Incident ID: {incident_id}
Date: {incident_date}
Severity: {severity}

Description: {description}

Contact: {compliance_officer}
""",
            required_fields=["incident_id", "incident_date", "severity", "description", "compliance_officer"],
            delivery_method="email"
        )

    def _get_notification_recipients(self, framework: ComplianceFramework) -> List[str]:
        """Obtener destinatarios de notificación"""
        org_info = self.organization_info

        framework_recipients = {
            ComplianceFramework.SOX: [org_info.get("ciso_email"), org_info.get("compliance_email")],
            ComplianceFramework.HIPAA: [org_info.get("dpo_email"), org_info.get("legal_email")],
            ComplianceFramework.PCI_DSS: [org_info.get("compliance_email"), org_info.get("ciso_email")],
            ComplianceFramework.GDPR: [org_info.get("dpo_email"), org_info.get("legal_email")]
        }

        return framework_recipients.get(framework, [org_info.get("compliance_email")])

    async def _send_notification(self, notification: Dict[str, Any]):
        """Enviar notificación (simulado)"""
        await asyncio.sleep(0.1)  # Simulate sending time
        self.logger.info(f"📤 Sent {notification['framework']} notification {notification['notification_id']}")

    async def generate_compliance_report(self, workflow: IncidentWorkflow) -> Dict[str, Any]:
        """Generar reporte de compliance"""
        self.logger.info(f"📊 Generating compliance report for {workflow.incident_id}")

        report = {
            "report_id": f"RPT_{workflow.incident_id}",
            "incident_id": workflow.incident_id,
            "generated_at": datetime.utcnow().isoformat(),
            "incident_summary": {
                "title": workflow.title,
                "severity": workflow.severity.name,
                "status": workflow.status.value,
                "created_at": workflow.created_at.isoformat(),
                "affected_business_units": workflow.business_units_affected,
                "data_types_involved": workflow.data_types_involved
            },
            "compliance_analysis": {
                "applicable_frameworks": [fw.value for fw in workflow.applicable_frameworks],
                "notification_deadlines_met": await self._check_deadline_compliance(workflow),
                "evidence_collection_status": "automated",
                "chain_of_custody_maintained": True
            },
            "timeline": workflow.workflow_history,
            "evidence_summary": {
                "total_items": len(workflow.evidence_items),
                "legal_hold_items": sum(1 for item in workflow.evidence_items if item.legal_hold),
                "retention_periods": self._get_retention_summary(workflow.evidence_items)
            },
            "notifications_sent": len(workflow.regulatory_notifications),
            "stakeholders_assigned": {
                "analyst": workflow.assigned_analyst,
                "compliance_officer": workflow.compliance_officer,
                "legal_counsel": workflow.legal_counsel,
                "privacy_officer": workflow.privacy_officer
            }
        }

        workflow.compliance_reports.append(report)
        return report

    async def _check_deadline_compliance(self, workflow: IncidentWorkflow) -> Dict[str, bool]:
        """Verificar cumplimiento de plazos"""
        current_time = datetime.utcnow()

        compliance_status = {}

        if workflow.first_response_deadline:
            compliance_status["first_response"] = current_time <= workflow.first_response_deadline

        if workflow.notification_deadline:
            compliance_status["notification"] = current_time <= workflow.notification_deadline

        if workflow.reporting_deadline:
            compliance_status["reporting"] = current_time <= workflow.reporting_deadline

        return compliance_status

    def _get_retention_summary(self, evidence_items: List[EvidenceItem]) -> Dict[str, int]:
        """Obtener resumen de períodos de retención"""
        retention_summary = defaultdict(int)

        for item in evidence_items:
            if item.retention_until:
                days_remaining = (item.retention_until - datetime.utcnow()).days
                if days_remaining > 2190:  # > 6 years
                    retention_summary["long_term"] += 1
                elif days_remaining > 365:  # > 1 year
                    retention_summary["medium_term"] += 1
                else:
                    retention_summary["short_term"] += 1
            else:
                retention_summary["indefinite"] += 1

        return dict(retention_summary)

async def demo_compliance_workflows():
    """Demostración del sistema de workflows de compliance"""
    print("\n🏛️ SmartCompute Enterprise - Compliance-Aware Incident Workflows Demo")
    print("=" * 85)

    # Initialize compliance manager
    config = {
        "automation_enabled": True,
        "auto_evidence_collection": True,
        "auto_notifications": False  # Require approval for demo
    }

    compliance_manager = ComplianceIncidentManager(config)

    # Get sample data from previous components
    from ml_threat_prioritization import demo_ml_threat_prioritization

    print("🤖 Collecting sample threat data for compliance workflow...")
    prioritized_threats = await demo_ml_threat_prioritization()

    # Extract clusters and predictions
    clusters = [threat[0] for threat in prioritized_threats[:3]]  # Top 3 threats
    ml_predictions = [threat[1] for threat in prioritized_threats[:3]]

    print(f"\n🏛️ Creating compliance workflow for {len(clusters)} high-priority threat clusters...")

    # Create compliance workflow
    workflow = await compliance_manager.create_compliance_workflow(clusters, ml_predictions)

    # Process notifications
    notifications = await compliance_manager.process_compliance_notifications(workflow)

    # Generate compliance report
    compliance_report = await compliance_manager.generate_compliance_report(workflow)

    # Display results
    print(f"\n📋 COMPLIANCE WORKFLOW CREATED")
    print("=" * 40)
    print(f"Incident ID: {workflow.incident_id}")
    print(f"Title: {workflow.title}")
    print(f"Severity: {workflow.severity.name}")
    print(f"Status: {workflow.status.value}")
    print(f"Applicable Frameworks: {', '.join([fw.value.upper() for fw in workflow.applicable_frameworks])}")
    print(f"Business Units Affected: {', '.join(workflow.business_units_affected)}")
    print(f"Data Types Involved: {', '.join(workflow.data_types_involved)}")

    print(f"\n⏰ COMPLIANCE DEADLINES")
    print("=" * 25)
    if workflow.first_response_deadline:
        print(f"First Response: {workflow.first_response_deadline.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    if workflow.notification_deadline:
        print(f"Notification: {workflow.notification_deadline.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    if workflow.reporting_deadline:
        print(f"Reporting: {workflow.reporting_deadline.strftime('%Y-%m-%d %H:%M:%S UTC')}")

    print(f"\n👥 STAKEHOLDER ASSIGNMENTS")
    print("=" * 30)
    print(f"Assigned Analyst: {workflow.assigned_analyst}")
    print(f"Compliance Officer: {workflow.compliance_officer}")
    print(f"Legal Counsel: {workflow.legal_counsel}")
    if workflow.privacy_officer:
        print(f"Privacy Officer: {workflow.privacy_officer}")

    print(f"\n🔍 EVIDENCE COLLECTION")
    print("=" * 25)
    print(f"Total Evidence Items: {len(workflow.evidence_items)}")
    legal_hold_count = sum(1 for item in workflow.evidence_items if item.legal_hold)
    print(f"Items Under Legal Hold: {legal_hold_count}")

    if workflow.evidence_items:
        print(f"Evidence Types: {', '.join(set(item.evidence_type for item in workflow.evidence_items))}")

    print(f"\n📧 COMPLIANCE NOTIFICATIONS")
    print("=" * 30)
    print(f"Notifications Created: {len(notifications)}")
    for notification in notifications:
        print(f"  - {notification['framework'].upper()}: {notification['status']}")

    print(f"\n📊 COMPLIANCE REPORT SUMMARY")
    print("=" * 35)
    print(f"Report ID: {compliance_report['report_id']}")
    print(f"Evidence Items Collected: {compliance_report['evidence_summary']['total_items']}")
    print(f"Frameworks Assessed: {len(compliance_report['compliance_analysis']['applicable_frameworks'])}")
    print(f"Timeline Events: {len(compliance_report['timeline'])}")

    deadline_compliance = compliance_report['compliance_analysis']['notification_deadlines_met']
    print(f"Deadline Compliance: {', '.join([f'{k}: ✅' if v else f'{k}: ❌' for k, v in deadline_compliance.items()])}")

    print(f"\n✅ Compliance-aware incident workflow completed successfully!")
    print(f"📈 Workflow demonstrates automated compliance management with:")
    print(f"  - Regulatory framework identification")
    print(f"  - Automated evidence collection and preservation")
    print(f"  - Stakeholder assignment based on compliance requirements")
    print(f"  - Deadline tracking and notification management")
    print(f"  - Comprehensive audit trail and reporting")

    return workflow, compliance_report

if __name__ == "__main__":
    # Run demo
    results = asyncio.run(demo_compliance_workflows())