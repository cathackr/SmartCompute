#!/usr/bin/env python3
"""
SmartCompute Enterprise - Admin Authorization Workflow
=====================================================

Sistema de autorización de administrador para cambios críticos de seguridad:
- Workflow de aprobación para implementaciones de alto riesgo
- Notificaciones en tiempo real a administradores
- Análisis de riesgo automatizado
- Historial de decisiones de autorización
- Integración con sistemas de aprendizaje HRM y experimentación MITRE

Copyright (c) 2024 SmartCompute. All rights reserved.
"""

import asyncio
import json
import logging
import smtplib
import ssl
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import uuid
import yaml

# Importaciones opcionales de email
try:
    from email.mime.text import MimeText
    from email.mime.multipart import MimeMultipart
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False
    # Clases dummy para evitar errores
    class MimeText:
        def __init__(self, *args, **kwargs): pass
    class MimeMultipart:
        def __init__(self, *args, **kwargs): pass


class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    ESCALATED = "escalated"


class RiskLevel(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class ChangeType(Enum):
    SECURITY_POLICY = "security_policy"
    SYSTEM_CONFIG = "system_config"
    SECURITY_SOLUTION = "security_solution"
    NETWORK_CHANGE = "network_change"
    ACCESS_CONTROL = "access_control"
    EMERGENCY_RESPONSE = "emergency_response"


@dataclass
class AdminUser:
    """Usuario administrador"""
    admin_id: str
    username: str
    email: str
    phone: Optional[str]
    role: str
    authorization_level: int  # 1-5, 5 being highest
    notification_preferences: Dict[str, bool]
    active: bool
    last_login: Optional[datetime]


@dataclass
class ApprovalRequest:
    """Solicitud de aprobación"""
    request_id: str
    title: str
    description: str
    change_type: ChangeType
    risk_level: RiskLevel
    requested_by: str
    requested_at: datetime
    expires_at: datetime
    status: ApprovalStatus

    # Datos técnicos
    technical_details: Dict[str, Any]
    affected_systems: List[str]
    rollback_plan: str
    testing_results: Dict[str, Any]

    # Aprobación
    required_approvers: int
    approver_ids: List[str]
    approvals: List[Dict[str, Any]]
    rejections: List[Dict[str, Any]]

    # Metadata
    tags: List[str]
    related_requests: List[str]
    escalation_history: List[Dict[str, Any]]


@dataclass
class ApprovalDecision:
    """Decisión de aprobación"""
    decision_id: str
    request_id: str
    admin_id: str
    decision: str  # approved, rejected
    timestamp: datetime
    justification: str
    conditions: List[str]  # Condiciones para la aprobación
    follow_up_required: bool


class SmartComputeAdminAuthorization:
    """Sistema de autorización de administrador para SmartCompute"""

    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = str(Path.home() / "smartcompute" / "admin_auth_config.yaml")

        self.config_path = Path(config_path)
        self.data_path = self.config_path.parent / "admin_auth_data"
        self.data_path.mkdir(parents=True, exist_ok=True)

        # Configurar logging
        self.logger = logging.getLogger(__name__)

        # Archivos de datos
        self.admins_file = self.data_path / "admins.json"
        self.requests_file = self.data_path / "approval_requests.json"
        self.decisions_file = self.data_path / "approval_decisions.json"

        # Cargar configuración y datos
        self.config = self._load_config()
        self.admins = self._load_admins()
        self.requests = self._load_requests()
        self.decisions = self._load_decisions()

        # Callbacks para notificaciones
        self.notification_callbacks: List[Callable] = []

    def _load_config(self) -> Dict[str, Any]:
        """Carga configuración del sistema"""
        default_config = {
            "approval_timeouts": {
                "low": 24 * 60,      # 24 horas en minutos
                "medium": 8 * 60,    # 8 horas
                "high": 4 * 60,      # 4 horas
                "critical": 2 * 60   # 2 horas
            },
            "required_approvers": {
                "low": 1,
                "medium": 1,
                "high": 2,
                "critical": 3
            },
            "auto_escalation": {
                "enabled": True,
                "timeout_minutes": 60
            },
            "notifications": {
                "email": {
                    "enabled": True,
                    "smtp_server": "localhost",
                    "smtp_port": 587,
                    "use_tls": True,
                    "from_email": "smartcompute@company.com"
                },
                "slack": {
                    "enabled": False,
                    "webhook_url": ""
                }
            },
            "emergency_contacts": [
                {
                    "name": "Emergency Security Team",
                    "email": "security-emergency@company.com",
                    "phone": "+1-555-0123"
                }
            ]
        }

        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    user_config = yaml.safe_load(f)
                    default_config.update(user_config)
            except Exception as e:
                self.logger.error(f"Error loading config: {e}")

        return default_config

    def _load_admins(self) -> List[AdminUser]:
        """Carga lista de administradores"""
        if self.admins_file.exists():
            try:
                with open(self.admins_file, 'r') as f:
                    data = json.load(f)
                    return [self._dict_to_admin(item) for item in data]
            except Exception as e:
                self.logger.error(f"Error loading admins: {e}")

        # Crear admin por defecto si no existe
        default_admin = AdminUser(
            admin_id=str(uuid.uuid4()),
            username="admin",
            email="admin@localhost",
            phone=None,
            role="system_administrator",
            authorization_level=5,
            notification_preferences={
                "email": True,
                "sms": False,
                "slack": False
            },
            active=True,
            last_login=None
        )

        return [default_admin]

    def _load_requests(self) -> List[ApprovalRequest]:
        """Carga solicitudes de aprobación"""
        if self.requests_file.exists():
            try:
                with open(self.requests_file, 'r') as f:
                    data = json.load(f)
                    return [self._dict_to_request(item) for item in data]
            except Exception as e:
                self.logger.error(f"Error loading requests: {e}")
        return []

    def _load_decisions(self) -> List[ApprovalDecision]:
        """Carga decisiones de aprobación"""
        if self.decisions_file.exists():
            try:
                with open(self.decisions_file, 'r') as f:
                    data = json.load(f)
                    return [self._dict_to_decision(item) for item in data]
            except Exception as e:
                self.logger.error(f"Error loading decisions: {e}")
        return []

    async def submit_approval_request(self,
                                    title: str,
                                    description: str,
                                    change_type: ChangeType,
                                    risk_level: RiskLevel,
                                    requested_by: str,
                                    technical_details: Dict[str, Any],
                                    affected_systems: List[str],
                                    rollback_plan: str,
                                    testing_results: Dict[str, Any] = None) -> str:
        """Envía una solicitud de aprobación"""

        # Calcular timeout basado en nivel de riesgo
        timeout_minutes = self.config["approval_timeouts"][risk_level.name.lower()]
        expires_at = datetime.now() + timedelta(minutes=timeout_minutes)

        # Determinar número requerido de aprobadores
        required_approvers = self.config["required_approvers"][risk_level.name.lower()]

        # Seleccionar aprobadores elegibles
        eligible_approvers = self._get_eligible_approvers(risk_level, change_type)

        request = ApprovalRequest(
            request_id=str(uuid.uuid4()),
            title=title,
            description=description,
            change_type=change_type,
            risk_level=risk_level,
            requested_by=requested_by,
            requested_at=datetime.now(),
            expires_at=expires_at,
            status=ApprovalStatus.PENDING,
            technical_details=technical_details or {},
            affected_systems=affected_systems,
            rollback_plan=rollback_plan,
            testing_results=testing_results or {},
            required_approvers=required_approvers,
            approver_ids=[admin.admin_id for admin in eligible_approvers[:required_approvers * 2]],  # Más opciones
            approvals=[],
            rejections=[],
            tags=self._generate_tags(title, description, change_type),
            related_requests=[],
            escalation_history=[]
        )

        self.requests.append(request)
        self._save_requests()

        # Enviar notificaciones
        await self._notify_approvers(request)

        # Programar escalamiento automático si está habilitado
        if self.config["auto_escalation"]["enabled"]:
            await self._schedule_auto_escalation(request)

        self.logger.info(f"Approval request submitted: {request.request_id} - {title}")
        return request.request_id

    def _get_eligible_approvers(self, risk_level: RiskLevel, change_type: ChangeType) -> List[AdminUser]:
        """Obtiene lista de aprobadores elegibles"""
        min_auth_level = {
            RiskLevel.LOW: 2,
            RiskLevel.MEDIUM: 3,
            RiskLevel.HIGH: 4,
            RiskLevel.CRITICAL: 5
        }

        eligible = []
        for admin in self.admins:
            if (admin.active and
                admin.authorization_level >= min_auth_level[risk_level]):
                eligible.append(admin)

        # Ordenar por nivel de autorización (más alto primero)
        eligible.sort(key=lambda x: x.authorization_level, reverse=True)
        return eligible

    def _generate_tags(self, title: str, description: str, change_type: ChangeType) -> List[str]:
        """Genera tags automáticos para la solicitud"""
        tags = [change_type.value]

        # Tags basados en palabras clave
        keywords_map = {
            "production": ["production"],
            "emergency": ["emergency", "urgent"],
            "security": ["security", "vulnerability"],
            "network": ["network", "firewall"],
            "database": ["database", "sql"],
            "authentication": ["auth", "login", "password"],
            "encryption": ["encrypt", "ssl", "tls"],
            "backup": ["backup", "restore"],
            "monitoring": ["monitor", "alert", "log"]
        }

        text = (title + " " + description).lower()
        for tag, keywords in keywords_map.items():
            if any(keyword in text for keyword in keywords):
                tags.append(tag)

        return list(set(tags))

    async def approve_request(self,
                            request_id: str,
                            admin_id: str,
                            justification: str,
                            conditions: List[str] = None) -> bool:
        """Aprueba una solicitud"""

        request = self._get_request(request_id)
        if not request:
            return False

        if request.status != ApprovalStatus.PENDING:
            return False

        # Verificar que el admin puede aprobar
        if admin_id not in request.approver_ids:
            return False

        # Verificar que no haya aprobado ya
        if any(approval["admin_id"] == admin_id for approval in request.approvals):
            return False

        # Crear decisión
        decision = ApprovalDecision(
            decision_id=str(uuid.uuid4()),
            request_id=request_id,
            admin_id=admin_id,
            decision="approved",
            timestamp=datetime.now(),
            justification=justification,
            conditions=conditions or [],
            follow_up_required=len(conditions or []) > 0
        )

        # Agregar aprobación
        request.approvals.append({
            "admin_id": admin_id,
            "timestamp": decision.timestamp.isoformat(),
            "justification": justification,
            "conditions": conditions or []
        })

        self.decisions.append(decision)

        # Verificar si tiene suficientes aprobaciones
        if len(request.approvals) >= request.required_approvers:
            request.status = ApprovalStatus.APPROVED
            await self._notify_approval_complete(request)

        self._save_requests()
        self._save_decisions()

        self.logger.info(f"Request approved: {request_id} by {admin_id}")
        return True

    async def reject_request(self,
                           request_id: str,
                           admin_id: str,
                           justification: str) -> bool:
        """Rechaza una solicitud"""

        request = self._get_request(request_id)
        if not request:
            return False

        if request.status != ApprovalStatus.PENDING:
            return False

        # Verificar que el admin puede rechazar
        if admin_id not in request.approver_ids:
            return False

        # Crear decisión
        decision = ApprovalDecision(
            decision_id=str(uuid.uuid4()),
            request_id=request_id,
            admin_id=admin_id,
            decision="rejected",
            timestamp=datetime.now(),
            justification=justification,
            conditions=[],
            follow_up_required=False
        )

        # Agregar rechazo
        request.rejections.append({
            "admin_id": admin_id,
            "timestamp": decision.timestamp.isoformat(),
            "justification": justification
        })

        request.status = ApprovalStatus.REJECTED
        self.decisions.append(decision)

        await self._notify_rejection(request, decision)

        self._save_requests()
        self._save_decisions()

        self.logger.info(f"Request rejected: {request_id} by {admin_id}")
        return True

    async def escalate_request(self, request_id: str, reason: str) -> bool:
        """Escala una solicitud a nivel superior"""

        request = self._get_request(request_id)
        if not request:
            return False

        # Obtener aprobadores de nivel superior
        higher_level_admins = [
            admin for admin in self.admins
            if admin.active and admin.authorization_level == 5
        ]

        if not higher_level_admins:
            return False

        # Agregar a historial de escalación
        escalation = {
            "timestamp": datetime.now().isoformat(),
            "reason": reason,
            "escalated_to": [admin.admin_id for admin in higher_level_admins]
        }

        request.escalation_history.append(escalation)
        request.status = ApprovalStatus.ESCALATED

        # Actualizar aprobadores
        request.approver_ids = [admin.admin_id for admin in higher_level_admins]

        # Extender timeout para escalaciones
        request.expires_at = datetime.now() + timedelta(hours=2)

        await self._notify_escalation(request, escalation)

        self._save_requests()
        self.logger.info(f"Request escalated: {request_id}")
        return True

    async def _schedule_auto_escalation(self, request: ApprovalRequest):
        """Programa escalación automática"""
        timeout_minutes = self.config["auto_escalation"]["timeout_minutes"]

        async def auto_escalate():
            await asyncio.sleep(timeout_minutes * 60)

            # Verificar si aún está pendiente
            current_request = self._get_request(request.request_id)
            if current_request and current_request.status == ApprovalStatus.PENDING:
                await self.escalate_request(
                    request.request_id,
                    f"Auto-escalated after {timeout_minutes} minutes without response"
                )

        # Ejecutar en background
        asyncio.create_task(auto_escalate())

    async def _notify_approvers(self, request: ApprovalRequest):
        """Notifica a los aprobadores"""
        for admin_id in request.approver_ids:
            admin = self._get_admin(admin_id)
            if admin and admin.active:
                await self._send_notification(admin, "approval_request", {
                    "request": request,
                    "admin": admin
                })

    async def _notify_approval_complete(self, request: ApprovalRequest):
        """Notifica cuando se completa una aprobación"""
        requester = request.requested_by
        await self._send_notification_to_user(requester, "approval_granted", {
            "request": request
        })

    async def _notify_rejection(self, request: ApprovalRequest, decision: ApprovalDecision):
        """Notifica cuando se rechaza una solicitud"""
        requester = request.requested_by
        await self._send_notification_to_user(requester, "approval_rejected", {
            "request": request,
            "decision": decision
        })

    async def _notify_escalation(self, request: ApprovalRequest, escalation: Dict[str, Any]):
        """Notifica sobre escalación"""
        for admin_id in escalation["escalated_to"]:
            admin = self._get_admin(admin_id)
            if admin and admin.active:
                await self._send_notification(admin, "request_escalated", {
                    "request": request,
                    "escalation": escalation,
                    "admin": admin
                })

    async def _send_notification(self, admin: AdminUser, notification_type: str, data: Dict[str, Any]):
        """Envía notificación a un administrador"""
        try:
            # Email notification
            if (admin.notification_preferences.get("email", False) and
                self.config["notifications"]["email"]["enabled"]):
                await self._send_email_notification(admin, notification_type, data)

            # Callbacks personalizados
            for callback in self.notification_callbacks:
                try:
                    await callback(admin, notification_type, data)
                except Exception as e:
                    self.logger.error(f"Notification callback failed: {e}")

        except Exception as e:
            self.logger.error(f"Failed to send notification to {admin.admin_id}: {e}")

    async def _send_notification_to_user(self, user_id: str, notification_type: str, data: Dict[str, Any]):
        """Envía notificación a un usuario (no admin)"""
        # En implementación real, esto buscaría el usuario en base de datos
        self.logger.info(f"Notification sent to user {user_id}: {notification_type}")

    async def _send_email_notification(self, admin: AdminUser, notification_type: str, data: Dict[str, Any]):
        """Envía notificación por email"""
        try:
            if not EMAIL_AVAILABLE:
                self.logger.info(f"Email notification simulated for {admin.email} (email libs not available)")
                return

            email_config = self.config["notifications"]["email"]

            subject, body = self._generate_email_content(notification_type, data)

            msg = MimeMultipart()
            msg["From"] = email_config["from_email"]
            msg["To"] = admin.email
            msg["Subject"] = subject

            msg.attach(MimeText(body, "html"))

            # Enviar email (simulado - en producción usar servidor SMTP real)
            self.logger.info(f"Email sent to {admin.email}: {subject}")

        except Exception as e:
            self.logger.error(f"Failed to send email to {admin.email}: {e}")

    def _generate_email_content(self, notification_type: str, data: Dict[str, Any]) -> tuple[str, str]:
        """Genera contenido del email"""
        request = data.get("request")
        admin = data.get("admin")

        templates = {
            "approval_request": {
                "subject": f"🔐 Approval Required: {request.title}",
                "body": f"""
                <h2>SmartCompute - Approval Request</h2>
                <p>Hello {admin.username},</p>
                <p>A new approval request requires your attention:</p>

                <div style="background: #f5f5f5; padding: 15px; margin: 10px 0;">
                    <h3>{request.title}</h3>
                    <p><strong>Risk Level:</strong> {request.risk_level.name}</p>
                    <p><strong>Change Type:</strong> {request.change_type.value}</p>
                    <p><strong>Requested by:</strong> {request.requested_by}</p>
                    <p><strong>Expires:</strong> {request.expires_at.strftime('%Y-%m-%d %H:%M')}</p>
                </div>

                <p><strong>Description:</strong></p>
                <p>{request.description}</p>

                <p><strong>Affected Systems:</strong> {', '.join(request.affected_systems)}</p>

                <p>Please review and approve/reject this request promptly.</p>
                """
            },
            "request_escalated": {
                "subject": f"🚨 Escalated Request: {request.title}",
                "body": f"""
                <h2>SmartCompute - Escalated Request</h2>
                <p>Hello {admin.username},</p>
                <p>A request has been escalated to your level:</p>

                <div style="background: #fff3cd; padding: 15px; margin: 10px 0;">
                    <h3>{request.title}</h3>
                    <p><strong>Risk Level:</strong> {request.risk_level.name}</p>
                    <p><strong>Escalation Reason:</strong> {data['escalation']['reason']}</p>
                </div>

                <p>This requires immediate attention due to escalation.</p>
                """
            }
        }

        template = templates.get(notification_type, {
            "subject": "SmartCompute Notification",
            "body": f"<p>Notification: {notification_type}</p>"
        })

        return template["subject"], template["body"]

    def get_pending_requests(self, admin_id: str = None) -> List[ApprovalRequest]:
        """Obtiene solicitudes pendientes"""
        pending = [req for req in self.requests if req.status == ApprovalStatus.PENDING]

        if admin_id:
            pending = [req for req in pending if admin_id in req.approver_ids]

        return pending

    def get_request_status(self, request_id: str) -> Dict[str, Any]:
        """Obtiene estado de una solicitud"""
        request = self._get_request(request_id)
        if not request:
            return {"error": "Request not found"}

        return {
            "request_id": request.request_id,
            "title": request.title,
            "status": request.status.value,
            "risk_level": request.risk_level.name,
            "requested_by": request.requested_by,
            "requested_at": request.requested_at.isoformat(),
            "expires_at": request.expires_at.isoformat(),
            "approvals_received": len(request.approvals),
            "approvals_required": request.required_approvers,
            "can_proceed": len(request.approvals) >= request.required_approvers,
            "rejections": len(request.rejections),
            "escalation_count": len(request.escalation_history)
        }

    def add_notification_callback(self, callback: Callable):
        """Agrega callback para notificaciones"""
        self.notification_callbacks.append(callback)

    def register_admin(self,
                      username: str,
                      email: str,
                      role: str,
                      authorization_level: int,
                      phone: str = None) -> str:
        """Registra un nuevo administrador"""

        admin = AdminUser(
            admin_id=str(uuid.uuid4()),
            username=username,
            email=email,
            phone=phone,
            role=role,
            authorization_level=authorization_level,
            notification_preferences={
                "email": True,
                "sms": False,
                "slack": False
            },
            active=True,
            last_login=None
        )

        self.admins.append(admin)
        self._save_admins()

        self.logger.info(f"Admin registered: {username} ({admin.admin_id})")
        return admin.admin_id

    # Métodos de utilidad
    def _get_request(self, request_id: str) -> Optional[ApprovalRequest]:
        """Obtiene solicitud por ID"""
        return next((req for req in self.requests if req.request_id == request_id), None)

    def _get_admin(self, admin_id: str) -> Optional[AdminUser]:
        """Obtiene admin por ID"""
        return next((admin for admin in self.admins if admin.admin_id == admin_id), None)

    # Métodos de persistencia
    def _save_admins(self):
        """Guarda administradores"""
        try:
            data = [self._admin_to_dict(admin) for admin in self.admins]
            with open(self.admins_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Error saving admins: {e}")

    def _save_requests(self):
        """Guarda solicitudes"""
        try:
            data = [self._request_to_dict(req) for req in self.requests]
            with open(self.requests_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Error saving requests: {e}")

    def _save_decisions(self):
        """Guarda decisiones"""
        try:
            data = [self._decision_to_dict(decision) for decision in self.decisions]
            with open(self.decisions_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Error saving decisions: {e}")

    # Métodos de conversión
    def _admin_to_dict(self, admin: AdminUser) -> Dict[str, Any]:
        result = asdict(admin)
        return result

    def _dict_to_admin(self, data: Dict[str, Any]) -> AdminUser:
        if data.get("last_login"):
            data["last_login"] = datetime.fromisoformat(data["last_login"])
        return AdminUser(**data)

    def _request_to_dict(self, request: ApprovalRequest) -> Dict[str, Any]:
        result = asdict(request)
        result["change_type"] = request.change_type.value
        result["risk_level"] = request.risk_level.value
        result["status"] = request.status.value
        return result

    def _dict_to_request(self, data: Dict[str, Any]) -> ApprovalRequest:
        data["change_type"] = ChangeType(data["change_type"])
        data["risk_level"] = RiskLevel(data["risk_level"])
        data["status"] = ApprovalStatus(data["status"])
        data["requested_at"] = datetime.fromisoformat(data["requested_at"])
        data["expires_at"] = datetime.fromisoformat(data["expires_at"])
        return ApprovalRequest(**data)

    def _decision_to_dict(self, decision: ApprovalDecision) -> Dict[str, Any]:
        return asdict(decision)

    def _dict_to_decision(self, data: Dict[str, Any]) -> ApprovalDecision:
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return ApprovalDecision(**data)


# Ejemplo de uso
async def demo_admin_authorization():
    """Demostración del sistema de autorización"""

    print("🔐 SmartCompute Admin Authorization Demo")
    print("=" * 50)

    # Inicializar sistema
    auth_system = SmartComputeAdminAuthorization()

    # Registrar admin adicional
    admin_id = auth_system.register_admin(
        username="security_admin",
        email="security@company.com",
        role="security_administrator",
        authorization_level=4,
        phone="+1-555-0100"
    )

    print(f"✅ Admin registrado: {admin_id}")

    # Enviar solicitud de aprobación
    request_id = await auth_system.submit_approval_request(
        title="Implement Advanced Brute Force Protection",
        description="Deploy machine learning-based brute force protection with automatic IP blocking",
        change_type=ChangeType.SECURITY_SOLUTION,
        risk_level=RiskLevel.HIGH,
        requested_by="hrm_learning_system",
        technical_details={
            "solution_type": "ml_brute_force_protection",
            "mitre_techniques": ["T1110"],
            "implementation_complexity": 7
        },
        affected_systems=["authentication_service", "load_balancer"],
        rollback_plan="Disable ML protection and revert to basic rate limiting",
        testing_results={
            "sandbox_success": True,
            "security_score": 92.5,
            "performance_impact": "minimal"
        }
    )

    print(f"✅ Solicitud enviada: {request_id}")

    # Verificar estado
    status = auth_system.get_request_status(request_id)
    print(f"✅ Estado: {status['status']}")
    print(f"   Aprobaciones necesarias: {status['approvals_required']}")

    # Simular aprobación
    admins = auth_system.admins
    if admins:
        admin = admins[0]
        approved = await auth_system.approve_request(
            request_id=request_id,
            admin_id=admin.admin_id,
            justification="Solution addresses critical security gap with acceptable risk",
            conditions=["Monitor for 24h after deployment", "Prepare immediate rollback if issues"]
        )

        print(f"✅ Aprobación: {'Exitosa' if approved else 'Falló'}")

    # Verificar estado final
    final_status = auth_system.get_request_status(request_id)
    print(f"✅ Estado final: {final_status['status']}")
    print(f"   Puede proceder: {final_status['can_proceed']}")

    # Mostrar solicitudes pendientes
    pending = auth_system.get_pending_requests()
    print(f"✅ Solicitudes pendientes: {len(pending)}")


if __name__ == "__main__":
    asyncio.run(demo_admin_authorization())