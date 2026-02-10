#!/usr/bin/env python3
"""
SmartCompute Industrial - Sistema de Interacción Segura con IA
Desarrollado por: ggwre04p0@mozmail.com
LinkedIn: https://www.linkedin.com/in/martín-iribarne-swtf/

Sistema de autenticación segura con 2FA, geolocalización y análisis visual
para interacción inteligente entre operadores y IA en campo.
"""

import json
import time
import hashlib
import secrets
import base64
import qrcode
import cv2
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Tuple
import io
import pyotp
import jwt
from cryptography.fernet import Fernet
import requests
from PIL import Image, ExifTags
import subprocess
import threading
import socketserver
import http.server

@dataclass
class OperatorCredentials:
    operator_id: str
    full_name: str
    department: str
    authorization_level: int  # 1-5 (1=básico, 5=supervisión)
    phone_number: str
    email: str
    totp_secret: str
    ssh_public_key: str
    authorized_locations: List[str]
    active: bool = True
    last_login: Optional[datetime] = None
    failed_attempts: int = 0

@dataclass
class SecureSession:
    session_id: str
    operator_id: str
    start_time: datetime
    location_gps: Tuple[float, float]
    location_name: str
    device_fingerprint: str
    vpn_authenticated: bool
    totp_verified: bool
    session_token: str
    expires_at: datetime
    actions_performed: List[Dict[str, Any]] = None

@dataclass
class VisualAnalysisRequest:
    request_id: str
    session_id: str
    operator_id: str
    image_path: str
    gps_coordinates: Tuple[float, float]
    timestamp: datetime
    problem_description: str
    equipment_suspected: Optional[str] = None
    urgency_level: str = "medium"

@dataclass
class AIRecommendation:
    recommendation_id: str
    request_id: str
    analysis_type: str
    confidence_score: float
    visual_findings: List[str]
    recommended_actions: List[Dict[str, Any]]
    risk_assessment: Dict[str, str]
    approval_required: bool
    approval_level_needed: int
    estimated_downtime: Optional[str] = None
    safety_considerations: List[str] = None

class SmartComputeSecureInteraction:
    """
    Sistema principal de interacción segura entre operadores y IA
    """

    def __init__(self):
        self.operators_db = {}
        self.active_sessions = {}
        self.visual_analysis_queue = []
        self.ai_recommendations = {}
        self.approval_workflows = {}

        # Configuración de seguridad
        self.jwt_secret = secrets.token_urlsafe(32)
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)

        # Configuración GPS/Geofencing
        self.authorized_locations = {
            "planta_principal": {"lat": -34.603700, "lng": -58.381600, "radius": 100},
            "almacen_a": {"lat": -34.603700, "lng": -58.381600, "radius": 50},
            "oficina_mantenimiento": {"lat": -34.603700, "lng": -58.381600, "radius": 30}
        }

        # Configuración de IA visual
        self.visual_ai_models = {
            "plc_diagnostics": {"confidence_threshold": 0.85},
            "equipment_inspection": {"confidence_threshold": 0.80},
            "safety_analysis": {"confidence_threshold": 0.90}
        }

        # Inicializar datos de ejemplo
        self._initialize_demo_data()

    def _initialize_demo_data(self):
        """Inicializar datos de demostración"""
        # Crear operador de ejemplo
        totp_secret = pyotp.random_base32()

        demo_operator = OperatorCredentials(
            operator_id="OP001",
            full_name="Juan Carlos Técnico",
            department="Mantenimiento Industrial",
            authorization_level=3,
            phone_number="+54911234567",
            email="ggwre04p0@mozmail.com",
            totp_secret=totp_secret,
            ssh_public_key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQAB...",
            authorized_locations=["planta_principal", "almacen_a"]
        )

        self.operators_db["OP001"] = demo_operator
        print(f"🔐 Operador demo creado: {demo_operator.full_name}")
        print(f"📱 Secreto TOTP: {totp_secret}")

    def generate_qr_for_2fa(self, operator_id: str) -> str:
        """Generar código QR para configuración 2FA"""
        if operator_id not in self.operators_db:
            raise ValueError("Operador no encontrado")

        operator = self.operators_db[operator_id]

        # Crear URI para TOTP
        totp_uri = pyotp.totp.TOTP(operator.totp_secret).provisioning_uri(
            name=operator.email,
            issuer_name="SmartCompute Industrial"
        )

        # Generar QR
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)

        qr_image = qr.make_image(fill_color="black", back_color="white")

        # Guardar QR
        qr_path = f"reports/2fa_qr_{operator_id}.png"
        qr_image.save(qr_path)

        print(f"📱 Código QR 2FA generado: {qr_path}")
        return qr_path

    def authenticate_operator(self, operator_id: str, totp_code: str,
                            gps_coords: Tuple[float, float],
                            device_info: str) -> SecureSession:
        """Autenticar operador con 2FA y geolocalización"""

        if operator_id not in self.operators_db:
            raise ValueError("Operador no encontrado")

        operator = self.operators_db[operator_id]

        if not operator.active:
            raise ValueError("Operador desactivado")

        # Verificar TOTP
        totp = pyotp.TOTP(operator.totp_secret)
        if not totp.verify(totp_code, valid_window=1):
            operator.failed_attempts += 1
            raise ValueError("Código 2FA inválido")

        # Verificar geolocalización
        location_name = self._verify_geolocation(gps_coords, operator.authorized_locations)
        if not location_name:
            raise ValueError("Ubicación no autorizada")

        # Crear sesión segura
        session_id = secrets.token_urlsafe(32)
        session_token = self._generate_session_token(operator_id, session_id)

        session = SecureSession(
            session_id=session_id,
            operator_id=operator_id,
            start_time=datetime.now(),
            location_gps=gps_coords,
            location_name=location_name,
            device_fingerprint=self._generate_device_fingerprint(device_info),
            vpn_authenticated=True,  # Simular VPN verificada
            totp_verified=True,
            session_token=session_token,
            expires_at=datetime.now() + timedelta(hours=8),
            actions_performed=[]
        )

        self.active_sessions[session_id] = session
        operator.last_login = datetime.now()
        operator.failed_attempts = 0

        print(f"✅ Operador autenticado: {operator.full_name}")
        print(f"📍 Ubicación: {location_name}")
        print(f"🔑 Sesión: {session_id[:8]}...")

        return session

    def submit_visual_analysis_request(self, session_id: str, image_path: str,
                                     problem_description: str,
                                     equipment_suspected: str = None,
                                     urgency: str = "medium") -> str:
        """Enviar solicitud de análisis visual"""

        if session_id not in self.active_sessions:
            raise ValueError("Sesión no válida")

        session = self.active_sessions[session_id]

        if datetime.now() > session.expires_at:
            raise ValueError("Sesión expirada")

        # Verificar que la imagen existe
        if not Path(image_path).exists():
            raise ValueError("Imagen no encontrada")

        # Extraer GPS de imagen si disponible
        image_gps = self._extract_gps_from_image(image_path)
        if not image_gps:
            image_gps = session.location_gps

        # Crear solicitud
        request_id = f"VAR-{int(time.time())}-{secrets.token_hex(4)}"

        visual_request = VisualAnalysisRequest(
            request_id=request_id,
            session_id=session_id,
            operator_id=session.operator_id,
            image_path=image_path,
            gps_coordinates=image_gps,
            timestamp=datetime.now(),
            problem_description=problem_description,
            equipment_suspected=equipment_suspected,
            urgency_level=urgency
        )

        self.visual_analysis_queue.append(visual_request)

        # Registrar acción en sesión
        session.actions_performed.append({
            "action": "visual_analysis_request",
            "request_id": request_id,
            "timestamp": datetime.now(),
            "description": problem_description
        })

        print(f"📸 Solicitud de análisis visual enviada: {request_id}")
        print(f"🔍 Problema: {problem_description}")

        # Procesar análisis
        self._process_visual_analysis(visual_request)

        return request_id

    def _process_visual_analysis(self, request: VisualAnalysisRequest):
        """Procesar análisis visual con IA (simulado)"""
        print(f"🤖 Procesando análisis visual: {request.request_id}")

        # Simular análisis de imagen
        time.sleep(2)  # Simular procesamiento

        # Análisis simulado basado en problema descrito
        visual_findings = self._simulate_visual_analysis(request)

        # Generar recomendaciones
        recommended_actions = self._generate_action_recommendations(request, visual_findings)

        # Determinar si requiere aprobación
        approval_required, approval_level = self._determine_approval_requirements(
            recommended_actions, request.urgency_level
        )

        recommendation = AIRecommendation(
            recommendation_id=f"REC-{request.request_id}",
            request_id=request.request_id,
            analysis_type="visual_diagnostic",
            confidence_score=0.87,
            visual_findings=visual_findings,
            recommended_actions=recommended_actions,
            risk_assessment={
                "safety": "medio",
                "operational": "alto",
                "financial": "bajo"
            },
            approval_required=approval_required,
            approval_level_needed=approval_level,
            estimated_downtime="15-30 minutos",
            safety_considerations=[
                "Aplicar LOTO antes de cualquier intervención",
                "Verificar ausencia de tensión",
                "Usar EPP requerido"
            ]
        )

        self.ai_recommendations[request.request_id] = recommendation

        # Iniciar flujo de aprobación si es necesario
        if approval_required:
            self._initiate_approval_workflow(recommendation)

        print(f"✅ Análisis completado con {recommendation.confidence_score:.0%} confianza")
        print(f"⚠️ Aprobación requerida: {'Sí' if approval_required else 'No'}")

        return recommendation

    def _simulate_visual_analysis(self, request: VisualAnalysisRequest) -> List[str]:
        """Simular análisis visual basado en descripción del problema"""
        problem_lower = request.problem_description.lower()

        findings = []

        if "plc" in problem_lower and "comunicación" in problem_lower:
            findings.extend([
                "LED de estado en PLC muestra patrón de error",
                "Cable de comunicación Ethernet conectado correctamente",
                "Pantalla HMI muestra timeout de comunicación",
                "Switch industrial con LED de actividad normal"
            ])

        if "sensor" in problem_lower:
            findings.extend([
                "Sensor aparenta conexión física correcta",
                "Cable sensor sin daños visibles",
                "LED indicador del sensor intermitente"
            ])

        if "motor" in problem_lower:
            findings.extend([
                "Motor sin signos de sobrecalentamiento",
                "Ventilador de refrigeración funcionando",
                "Vibración anormal detectada en análisis"
            ])

        if not findings:
            findings = [
                "Equipo visualmente en buen estado",
                "Conexiones eléctricas aparentemente correctas",
                "Sin signos evidentes de daño físico"
            ]

        return findings

    def _generate_action_recommendations(self, request: VisualAnalysisRequest,
                                       findings: List[str]) -> List[Dict[str, Any]]:
        """Generar recomendaciones de acción basadas en análisis"""

        actions = []

        if "plc" in request.problem_description.lower():
            actions.extend([
                {
                    "action": "Verificar configuración IP del PLC",
                    "priority": "alta",
                    "estimated_time": "10 minutos",
                    "tools_required": ["Laptop con TIA Portal", "Cable Ethernet"],
                    "safety_level": "bajo"
                },
                {
                    "action": "Reiniciar PLC en modo seguro",
                    "priority": "media",
                    "estimated_time": "5 minutos",
                    "tools_required": ["Acceso físico al PLC"],
                    "safety_level": "medio"
                }
            ])

        if "LED de error" in " ".join(findings):
            actions.append({
                "action": "Consultar manual de códigos de error del equipo",
                "priority": "alta",
                "estimated_time": "15 minutos",
                "tools_required": ["Manual técnico", "Código de error específico"],
                "safety_level": "bajo"
            })

        # Acción genérica de documentación
        actions.append({
            "action": "Documentar hallazgos y crear reporte de incidencia",
            "priority": "baja",
            "estimated_time": "10 minutos",
            "tools_required": ["Sistema SmartCompute"],
            "safety_level": "bajo"
        })

        return actions

    def _determine_approval_requirements(self, actions: List[Dict[str, Any]],
                                       urgency: str) -> Tuple[bool, int]:
        """Determinar si las acciones requieren aprobación"""

        max_safety_level = max([
            2 if action["safety_level"] == "alto" else
            1 if action["safety_level"] == "medio" else 0
            for action in actions
        ])

        high_priority_actions = sum(1 for action in actions if action["priority"] == "alta")

        # Requerir aprobación si:
        # - Hay acciones de alto riesgo
        # - Múltiples acciones de alta prioridad
        # - Urgencia alta con acciones complejas

        if max_safety_level >= 2:
            return True, 4  # Supervisor requerido
        elif high_priority_actions >= 2 and urgency == "alta":
            return True, 3  # Técnico senior requerido
        elif urgency == "alta":
            return True, 2  # Autorización básica requerida
        else:
            return False, 1  # No requiere aprobación

    def _initiate_approval_workflow(self, recommendation: AIRecommendation):
        """Iniciar flujo de aprobación"""
        workflow_id = f"WF-{recommendation.recommendation_id}"

        workflow = {
            "workflow_id": workflow_id,
            "recommendation_id": recommendation.recommendation_id,
            "approval_level_needed": recommendation.approval_level_needed,
            "status": "pending_approval",
            "created_at": datetime.now(),
            "notifications_sent": [],
            "approvers": self._get_available_approvers(recommendation.approval_level_needed)
        }

        self.approval_workflows[workflow_id] = workflow

        # Simular notificaciones
        self._send_approval_notifications(workflow)

        print(f"📋 Flujo de aprobación iniciado: {workflow_id}")
        print(f"👥 Nivel de aprobación requerido: {recommendation.approval_level_needed}")

    def _send_approval_notifications(self, workflow: Dict[str, Any]):
        """Enviar notificaciones de aprobación (simulado)"""

        for approver in workflow["approvers"]:
            notification = {
                "to": approver["email"],
                "subject": f"Aprobación Requerida - SmartCompute {workflow['workflow_id']}",
                "message": f"""
                Se requiere su aprobación para acciones de mantenimiento.

                Workflow: {workflow['workflow_id']}
                Nivel requerido: {workflow['approval_level_needed']}
                Fecha: {workflow['created_at']}

                Por favor acceda al sistema para revisar y aprobar.
                """,
                "sent_at": datetime.now()
            }

            workflow["notifications_sent"].append(notification)
            print(f"📧 Notificación enviada a: {approver['name']}")

    def _get_available_approvers(self, level_needed: int) -> List[Dict[str, str]]:
        """Obtener lista de aprobadores disponibles"""

        # Simulación de aprobadores por nivel
        approvers_db = {
            2: [{"name": "Carlos Supervisor", "email": "carlos.supervisor@empresa.com"}],
            3: [{"name": "Ana Jefe Mantenimiento", "email": "ana.jefe@empresa.com"}],
            4: [{"name": "Roberto Director", "email": "roberto.director@empresa.com"}],
            5: [{"name": "María Gerente Planta", "email": "maria.gerente@empresa.com"}]
        }

        available = []
        for level in range(level_needed, 6):
            available.extend(approvers_db.get(level, []))

        return available[:3]  # Máximo 3 aprobadores

    def get_recommendation_status(self, request_id: str) -> Dict[str, Any]:
        """Obtener estado de recomendación"""

        if request_id not in self.ai_recommendations:
            return {"error": "Solicitud no encontrada"}

        recommendation = self.ai_recommendations[request_id]

        status = {
            "request_id": request_id,
            "recommendation": asdict(recommendation),
            "status": "ready" if not recommendation.approval_required else "pending_approval",
            "can_execute": not recommendation.approval_required
        }

        # Agregar información de workflow si existe
        workflow = next((wf for wf in self.approval_workflows.values()
                        if wf["recommendation_id"] == recommendation.recommendation_id), None)

        if workflow:
            status["approval_workflow"] = workflow

        return status

    def execute_approved_actions(self, request_id: str, session_id: str) -> Dict[str, Any]:
        """Ejecutar acciones aprobadas"""

        if session_id not in self.active_sessions:
            raise ValueError("Sesión no válida")

        if request_id not in self.ai_recommendations:
            raise ValueError("Recomendación no encontrada")

        recommendation = self.ai_recommendations[request_id]

        if recommendation.approval_required:
            # Verificar que esté aprobado
            workflow = next((wf for wf in self.approval_workflows.values()
                           if wf["recommendation_id"] == recommendation.recommendation_id), None)

            if not workflow or workflow["status"] != "approved":
                raise ValueError("Acción no aprobada")

        # Simular ejecución de acciones
        execution_results = []

        for i, action in enumerate(recommendation.recommended_actions):
            print(f"⚙️ Ejecutando: {action['action']}")
            time.sleep(1)  # Simular tiempo de ejecución

            execution_results.append({
                "action": action["action"],
                "status": "completed",
                "timestamp": datetime.now(),
                "notes": f"Acción completada exitosamente"
            })

        # Registrar en sesión
        session = self.active_sessions[session_id]
        session.actions_performed.append({
            "action": "execute_recommendations",
            "request_id": request_id,
            "timestamp": datetime.now(),
            "results": execution_results
        })

        print(f"✅ Todas las acciones ejecutadas para {request_id}")

        return {
            "request_id": request_id,
            "execution_status": "completed",
            "actions_executed": len(execution_results),
            "results": execution_results
        }

    def _verify_geolocation(self, gps_coords: Tuple[float, float],
                          authorized_locations: List[str]) -> Optional[str]:
        """Verificar que la ubicación GPS esté autorizada"""

        lat, lng = gps_coords

        for location_name in authorized_locations:
            if location_name in self.authorized_locations:
                location_data = self.authorized_locations[location_name]

                # Calcular distancia (aproximada)
                lat_diff = abs(lat - location_data["lat"])
                lng_diff = abs(lng - location_data["lng"])
                distance_approx = ((lat_diff ** 2 + lng_diff ** 2) ** 0.5) * 111000  # Metros aprox

                if distance_approx <= location_data["radius"]:
                    return location_name

        return None

    def _generate_device_fingerprint(self, device_info: str) -> str:
        """Generar huella digital del dispositivo"""
        return hashlib.sha256(device_info.encode()).hexdigest()[:16]

    def _generate_session_token(self, operator_id: str, session_id: str) -> str:
        """Generar token JWT para la sesión"""
        payload = {
            "operator_id": operator_id,
            "session_id": session_id,
            "issued_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=8)).isoformat()
        }

        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")

    def _extract_gps_from_image(self, image_path: str) -> Optional[Tuple[float, float]]:
        """Extraer coordenadas GPS de metadatos de imagen"""
        try:
            image = Image.open(image_path)
            exif = image._getexif()

            if exif is not None:
                for tag, value in exif.items():
                    tag_name = ExifTags.TAGS.get(tag, tag)
                    if tag_name == "GPSInfo":
                        # Aquí iría la lógica de extracción de GPS real
                        # Por ahora retornar coordenadas simuladas
                        return (-34.6037, -58.3816)

        except Exception as e:
            print(f"⚠️ Error extrayendo GPS de imagen: {e}")

        return None

def main():
    """Función principal de demostración"""
    print("=== SmartCompute Industrial - Sistema de Interacción Segura ===")
    print("Desarrollado por: ggwre04p0@mozmail.com")
    print("LinkedIn: https://www.linkedin.com/in/martín-iribarne-swtf/")
    print()

    # Inicializar sistema
    secure_system = SmartComputeSecureInteraction()

    # Generar código QR 2FA para demo
    qr_path = secure_system.generate_qr_for_2fa("OP001")

    # Simular autenticación
    print("\n🔐 DEMO: Proceso de Autenticación Segura")
    try:
        # Coordenadas de planta principal
        gps_coords = (-34.6037, -58.3816)

        # Generar código TOTP para demo
        operator = secure_system.operators_db["OP001"]
        totp = pyotp.TOTP(operator.totp_secret)
        current_totp = totp.now()

        print(f"📱 Código 2FA actual: {current_totp}")

        # Autenticar
        session = secure_system.authenticate_operator(
            "OP001",
            current_totp,
            gps_coords,
            "SmartPhone-Android-V12"
        )

        # Simular envío de foto y análisis
        print("\n📸 DEMO: Análisis Visual de Problema")

        # Crear imagen de demo (simulada)
        demo_image_path = "reports/demo_plc_problem.jpg"
        Path("reports").mkdir(exist_ok=True)

        # Crear imagen simple para demo
        demo_image = Image.new('RGB', (640, 480), color=(100, 100, 100))
        demo_image.save(demo_image_path)

        # Enviar solicitud de análisis
        request_id = secure_system.submit_visual_analysis_request(
            session.session_id,
            demo_image_path,
            "PLC Siemens no se comunica con HMI, LED de error parpadeando",
            "PLC S7-1214C",
            "alta"
        )

        # Obtener estado de recomendación
        print("\n📋 DEMO: Estado de Recomendación")
        status = secure_system.get_recommendation_status(request_id)

        print(f"Estado: {status['status']}")
        print(f"Puede ejecutar: {status['can_execute']}")

        if status['can_execute']:
            # Ejecutar acciones
            print("\n⚙️ DEMO: Ejecución de Acciones")
            execution_result = secure_system.execute_approved_actions(
                request_id,
                session.session_id
            )
            print(f"Acciones ejecutadas: {execution_result['actions_executed']}")
        else:
            print("⏳ Esperando aprobación...")

        print("\n✅ DEMO COMPLETADO")
        print("\n🎯 Funcionalidades Demostradas:")
        print("  ✅ Autenticación 2FA con TOTP")
        print("  ✅ Verificación de geolocalización")
        print("  ✅ Análisis visual con IA")
        print("  ✅ Sistema de aprobaciones")
        print("  ✅ Ejecución segura de acciones")
        print("  ✅ Trazabilidad completa")

    except Exception as e:
        print(f"❌ Error en demo: {e}")

if __name__ == "__main__":
    main()