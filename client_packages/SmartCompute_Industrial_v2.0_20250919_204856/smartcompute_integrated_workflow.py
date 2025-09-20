#!/usr/bin/env python3
"""
SmartCompute Industrial - Workflow Integrado Completo
Desarrollado por: ggwre04p0@mozmail.com
LinkedIn: https://www.linkedin.com/in/martín-iribarne-swtf/

Sistema completo que integra todas las funcionalidades:
- Autenticación segura con 2FA y GPS
- Análisis visual con IA
- Flujo de aprobaciones
- Aprendizaje continuo
- Interacción inteligente operador-IA
"""

import json
import time
import asyncio
import subprocess
from datetime import datetime
from pathlib import Path
from dataclasses import asdict
from typing import Dict, List, Optional, Any, Tuple

# Importar módulos desarrollados
try:
    from smartcompute_secure_interaction import SmartComputeSecureInteraction, VisualAnalysisRequest
    from smartcompute_visual_ai import SmartComputeVisualAI
    from smartcompute_ai_learning import SmartComputeAILearning, InterventionRecord
    from smartcompute_field_diagnostics import SmartComputeFieldDiagnostics
    from hrm_integration import HRMIndustrialReasoning, IndustrialProblem
except ImportError as e:
    print(f"⚠️ Advertencia: Algunos módulos no disponibles: {e}")

class SmartComputeIntegratedWorkflow:
    """
    Sistema integrado completo de SmartCompute Industrial
    """

    def __init__(self):
        self.secure_system = None
        self.visual_ai = None
        self.learning_system = None
        self.field_diagnostics = None
        self.hrm_system = None
        self.node_server_process = None

        # Estado del workflow
        self.current_session = None
        self.active_requests = {}
        self.intervention_history = []

        self.initialize_systems()

    def initialize_systems(self):
        """Inicializar todos los subsistemas"""
        print("🚀 Inicializando SmartCompute Industrial...")

        try:
            # Sistema de autenticación segura
            self.secure_system = SmartComputeSecureInteraction()
            print("  ✅ Sistema de autenticación segura")

            # IA de análisis visual
            self.visual_ai = SmartComputeVisualAI()
            print("  ✅ IA de análisis visual")

            # Sistema de aprendizaje continuo
            self.learning_system = SmartComputeAILearning()
            print("  ✅ Sistema de aprendizaje continuo")

            # Diagnóstico de campo
            self.field_diagnostics = SmartComputeFieldDiagnostics()
            print("  ✅ Diagnóstico de campo")

            # Sistema HRM
            self.hrm_system = HRMIndustrialReasoning()
            print("  ✅ Sistema HRM")

            # Iniciar servidor Node.js
            self.start_node_server()

            print("✅ Todos los sistemas inicializados correctamente")

        except Exception as e:
            print(f"❌ Error inicializando sistemas: {e}")
            print("⚠️ Continuando en modo simulación")

    def start_node_server(self):
        """Iniciar servidor Node.js para aprobaciones"""
        try:
            # Verificar si Node.js está disponible
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                print("⚠️ Node.js no disponible - servidor de aprobaciones deshabilitado")
                return

            print("🚀 Iniciando servidor Node.js...")
            self.node_server_process = subprocess.Popen(
                ['node', 'smartcompute_approval_workflow.js'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Esperar un momento para que se inicie
            time.sleep(2)

            if self.node_server_process.poll() is None:
                print("  ✅ Servidor Node.js en funcionamiento (puerto 3000)")
            else:
                print("  ⚠️ Error iniciando servidor Node.js")

        except Exception as e:
            print(f"  ⚠️ No se pudo iniciar servidor Node.js: {e}")

    def authenticate_and_start_session(self, operator_id: str, totp_code: str,
                                     gps_coords: Tuple[float, float],
                                     device_info: str) -> Dict[str, Any]:
        """Autenticar operador e iniciar sesión segura"""

        print(f"🔐 Autenticando operador: {operator_id}")

        try:
            # Autenticar con sistema seguro
            session = self.secure_system.authenticate_operator(
                operator_id, totp_code, gps_coords, device_info
            )

            self.current_session = session

            print(f"✅ Sesión iniciada: {session.session_id}")
            print(f"📍 Ubicación: {session.location_name}")

            return {
                "success": True,
                "session_id": session.session_id,
                "location": session.location_name,
                "expires_at": session.expires_at.isoformat()
            }

        except Exception as e:
            print(f"❌ Error de autenticación: {e}")
            return {"success": False, "error": str(e)}

    def process_field_problem_with_photo(self, image_path: str, problem_description: str,
                                       equipment_suspected: str = None,
                                       urgency: str = "medium") -> Dict[str, Any]:
        """Procesar problema de campo con foto usando workflow completo"""

        if not self.current_session:
            return {"error": "No hay sesión activa"}

        print(f"📸 Procesando problema con foto: {problem_description}")

        try:
            # 1. Enviar solicitud de análisis visual
            request_id = self.secure_system.submit_visual_analysis_request(
                self.current_session.session_id,
                image_path,
                problem_description,
                equipment_suspected,
                urgency
            )

            # 2. Ejecutar análisis visual con IA
            visual_diagnostic = self.visual_ai.analyze_image(image_path, equipment_suspected)

            # 3. Crear imagen anotada
            annotated_image = self.visual_ai.create_annotated_image(visual_diagnostic)

            # 4. Analizar problema con HRM
            problem = IndustrialProblem(
                problem_id=f"FIELD-{int(time.time())}",
                category=self._categorize_problem_type(problem_description),
                description=problem_description,
                symptoms=visual_diagnostic.status_indicators,
                context={
                    "visual_analysis": asdict(visual_diagnostic),
                    "session_id": self.current_session.session_id,
                    "location": self.current_session.location_name
                },
                priority=urgency,
                location=self.current_session.location_name,
                equipment_involved=[equipment_suspected] if equipment_suspected else [],
                timestamp=datetime.now()
            )

            hrm_solution = self.hrm_system.analyze_industrial_problem(problem)

            # 5. Combinar análisis visual y HRM para recomendaciones mejoradas
            combined_recommendations = self._combine_visual_and_hrm_analysis(
                visual_diagnostic, hrm_solution
            )

            # 6. Aplicar aprendizaje previo para mejorar recomendaciones
            if self.learning_system:
                improved_recommendations = self.learning_system.generate_improved_recommendations(
                    problem_description,
                    {"equipment_type": equipment_suspected, "urgency": urgency}
                )
                combined_recommendations.extend(improved_recommendations)

            # 7. Determinar si requiere aprobación
            approval_required = self._requires_approval(combined_recommendations, urgency)

            result = {
                "request_id": request_id,
                "visual_analysis": asdict(visual_diagnostic),
                "hrm_solution": asdict(hrm_solution),
                "combined_recommendations": combined_recommendations,
                "approval_required": approval_required,
                "annotated_image": annotated_image,
                "confidence_score": (visual_diagnostic.confidence_overall + hrm_solution.confidence_score) / 2
            }

            # 8. Si requiere aprobación, crear workflow
            if approval_required:
                workflow_result = self._create_approval_workflow(result)
                result["approval_workflow"] = workflow_result

            # 9. Guardar en historial para aprendizaje
            self.active_requests[request_id] = result

            print(f"✅ Análisis completado - Confianza: {result['confidence_score']:.1%}")
            print(f"⚠️ Requiere aprobación: {'Sí' if approval_required else 'No'}")

            return result

        except Exception as e:
            print(f"❌ Error procesando problema: {e}")
            return {"error": str(e)}

    def execute_approved_actions(self, request_id: str) -> Dict[str, Any]:
        """Ejecutar acciones aprobadas y registrar intervención"""

        if request_id not in self.active_requests:
            return {"error": "Solicitud no encontrada"}

        request_data = self.active_requests[request_id]

        print(f"⚙️ Ejecutando acciones para solicitud: {request_id}")

        try:
            # 1. Verificar aprobación si es necesaria
            if request_data.get("approval_required"):
                status = self.secure_system.get_recommendation_status(request_id)
                if not status.get("can_execute"):
                    return {"error": "Acciones no aprobadas aún"}

            # 2. Ejecutar acciones
            execution_start = time.time()

            executed_actions = []
            for rec in request_data["combined_recommendations"][:3]:  # Top 3 recomendaciones
                print(f"  🔧 Ejecutando: {rec.get('action', rec.get('title', 'Acción'))}")

                # Simular ejecución
                time.sleep(1)

                executed_actions.append({
                    "action": rec.get('action', rec.get('title', 'Acción')),
                    "status": "completed",
                    "timestamp": datetime.now(),
                    "result": "Ejecutado exitosamente"
                })

            execution_time = (time.time() - execution_start) / 60  # minutos

            # 3. Simular resultado (en producción sería real)
            outcome = "successful" if len(executed_actions) >= 2 else "partial"

            # 4. Crear registro de intervención para aprendizaje
            intervention = InterventionRecord(
                intervention_id=f"INT-{request_id}",
                session_id=self.current_session.session_id,
                operator_id=self.current_session.operator_id,
                timestamp=datetime.now(),
                problem_description=request_data["visual_analysis"]["image_path"],
                ai_recommendations=request_data["combined_recommendations"],
                actions_taken=executed_actions,
                outcome=outcome,
                resolution_time=execution_time
            )

            # 5. Registrar en sistema de aprendizaje
            if self.learning_system:
                self.learning_system.record_intervention(intervention)

            # 6. Guardar en historial
            self.intervention_history.append(intervention)

            result = {
                "request_id": request_id,
                "execution_status": "completed",
                "outcome": outcome,
                "actions_executed": len(executed_actions),
                "execution_time_minutes": execution_time,
                "actions": executed_actions,
                "intervention_id": intervention.intervention_id
            }

            print(f"✅ Acciones ejecutadas exitosamente en {execution_time:.1f} minutos")

            return result

        except Exception as e:
            print(f"❌ Error ejecutando acciones: {e}")
            return {"error": str(e)}

    def add_intervention_feedback(self, intervention_id: str, feedback_score: float,
                                comments: str = "") -> Dict[str, Any]:
        """Agregar feedback sobre una intervención"""

        print(f"💬 Agregando feedback para intervención: {intervention_id}")

        try:
            # Buscar intervención
            intervention = None
            for inter in self.intervention_history:
                if inter.intervention_id == intervention_id:
                    intervention = inter
                    break

            if not intervention:
                return {"error": "Intervención no encontrada"}

            # Agregar feedback al sistema de aprendizaje
            if self.learning_system:
                self.learning_system.add_feedback(intervention_id, feedback_score, comments)

            # Actualizar intervención
            intervention.feedback_score = feedback_score
            intervention.lesson_learned = comments

            print(f"✅ Feedback agregado: {feedback_score}/5 - {comments}")

            return {
                "success": True,
                "intervention_id": intervention_id,
                "feedback_score": feedback_score
            }

        except Exception as e:
            print(f"❌ Error agregando feedback: {e}")
            return {"error": str(e)}

    def get_session_summary(self) -> Dict[str, Any]:
        """Obtener resumen de la sesión actual"""

        if not self.current_session:
            return {"error": "No hay sesión activa"}

        # Calcular estadísticas
        total_requests = len(self.active_requests)
        completed_interventions = len(self.intervention_history)

        successful_interventions = sum(
            1 for inter in self.intervention_history
            if inter.outcome == "successful"
        )

        avg_resolution_time = 0
        if self.intervention_history:
            valid_times = [i.resolution_time for i in self.intervention_history if i.resolution_time]
            if valid_times:
                avg_resolution_time = sum(valid_times) / len(valid_times)

        # Obtener resumen de aprendizaje
        learning_summary = {}
        if self.learning_system:
            learning_summary = self.learning_system.get_learning_summary()

        session_duration = (datetime.now() - self.current_session.start_time).total_seconds() / 3600

        return {
            "session_info": {
                "session_id": self.current_session.session_id,
                "operator_id": self.current_session.operator_id,
                "location": self.current_session.location_name,
                "duration_hours": round(session_duration, 1),
                "start_time": self.current_session.start_time.isoformat()
            },
            "activity_summary": {
                "total_requests": total_requests,
                "completed_interventions": completed_interventions,
                "success_rate": successful_interventions / completed_interventions if completed_interventions > 0 else 0,
                "avg_resolution_time_minutes": round(avg_resolution_time, 1)
            },
            "learning_summary": learning_summary,
            "systems_status": {
                "secure_auth": bool(self.secure_system),
                "visual_ai": bool(self.visual_ai),
                "hrm_system": bool(self.hrm_system),
                "learning_system": bool(self.learning_system),
                "node_server": self.node_server_process is not None and self.node_server_process.poll() is None
            }
        }

    def close_session(self) -> Dict[str, Any]:
        """Cerrar sesión actual"""

        if not self.current_session:
            return {"error": "No hay sesión activa"}

        session_summary = self.get_session_summary()

        # Generar reporte final
        report_path = self._generate_session_report(session_summary)

        # Limpiar estado
        self.current_session = None
        self.active_requests.clear()

        print(f"📋 Sesión cerrada - Reporte: {report_path}")

        return {
            "success": True,
            "session_summary": session_summary,
            "report_path": report_path
        }

    def shutdown_system(self):
        """Cerrar sistema completo"""

        print("🛑 Cerrando SmartCompute Industrial...")

        # Cerrar sesión si está activa
        if self.current_session:
            self.close_session()

        # Cerrar servidor Node.js
        if self.node_server_process:
            self.node_server_process.terminate()
            self.node_server_process.wait()
            print("  ✅ Servidor Node.js cerrado")

        print("✅ Sistema cerrado correctamente")

    # Métodos auxiliares
    def _categorize_problem_type(self, description: str) -> str:
        """Categorizar tipo de problema"""
        desc_lower = description.lower()

        if any(word in desc_lower for word in ["plc", "controlador"]):
            return "plc_issue"
        elif any(word in desc_lower for word in ["sensor", "medición"]):
            return "sensor_issue"
        elif any(word in desc_lower for word in ["comunicación", "red"]):
            return "communication_issue"
        else:
            return "general_issue"

    def _combine_visual_and_hrm_analysis(self, visual_diagnostic, hrm_solution) -> List[Dict[str, Any]]:
        """Combinar análisis visual y HRM"""

        combined = []

        # Agregar recomendaciones visuales
        for rec in visual_diagnostic.recommended_actions:
            combined.append({
                "action": rec,
                "source": "visual_ai",
                "priority": "media",
                "confidence": visual_diagnostic.confidence_overall
            })

        # Agregar recomendaciones HRM
        for rec in hrm_solution.recommended_actions:
            combined.append({
                "action": rec,
                "source": "hrm",
                "priority": "alta",
                "confidence": hrm_solution.confidence_score
            })

        # Eliminar duplicados
        seen = set()
        unique_combined = []
        for rec in combined:
            if rec["action"] not in seen:
                seen.add(rec["action"])
                unique_combined.append(rec)

        return unique_combined

    def _requires_approval(self, recommendations: List[Dict[str, Any]], urgency: str) -> bool:
        """Determinar si requiere aprobación"""

        # Lógica simplificada
        high_priority_count = sum(1 for rec in recommendations if rec.get("priority") == "alta")

        if urgency == "alta" and high_priority_count >= 2:
            return True

        # Verificar si hay acciones de riesgo
        risk_keywords = ["reiniciar", "reemplazar", "desconectar", "modificar"]
        for rec in recommendations:
            if any(keyword in rec["action"].lower() for keyword in risk_keywords):
                return True

        return False

    def _create_approval_workflow(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crear workflow de aprobación en Node.js"""

        try:
            import requests

            workflow_data = {
                "requestId": request_data["request_id"],
                "operatorId": self.current_session.operator_id,
                "title": "Aprobación de Acciones de Campo",
                "description": "Solicitud de aprobación para acciones identificadas por IA",
                "actions": request_data["combined_recommendations"],
                "requiredLevel": 3,
                "urgency": "medium",
                "riskAssessment": {
                    "operational": "medio",
                    "safety": "bajo",
                    "financial": "bajo"
                }
            }

            response = requests.post(
                "http://localhost:3000/api/workflows",
                json=workflow_data,
                timeout=5
            )

            if response.status_code == 200:
                return response.json()
            else:
                print(f"⚠️ Error creando workflow: {response.status_code}")
                return {"error": "Error creando workflow"}

        except Exception as e:
            print(f"⚠️ Servidor Node.js no disponible: {e}")
            return {"error": "Servidor de aprobaciones no disponible"}

    def _generate_session_report(self, session_summary: Dict[str, Any]) -> str:
        """Generar reporte de sesión"""

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = f"reports/session_report_{self.current_session.session_id}_{timestamp}.json"

        Path("reports").mkdir(exist_ok=True)

        report_data = {
            "session_summary": session_summary,
            "intervention_history": [asdict(inter) for inter in self.intervention_history],
            "active_requests": self.active_requests,
            "generated_at": datetime.now().isoformat()
        }

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str)

        return report_path

def demonstrate_complete_workflow():
    """Demostrar workflow completo integrado"""

    print("=== SmartCompute Industrial - Workflow Integrado Completo ===")
    print("Desarrollado por: ggwre04p0@mozmail.com")
    print("LinkedIn: https://www.linkedin.com/in/martín-iribarne-swtf/")
    print()

    # Inicializar sistema completo
    workflow_system = SmartComputeIntegratedWorkflow()

    try:
        # Escenario completo: Operador llega a planta con problema
        print("📱 ESCENARIO: Operador recibe llamada de emergencia")
        print("   - PLC principal no responde")
        print("   - Producción detenida")
        print("   - Operador se dirige con smartphone al sitio")
        print()

        # 1. Autenticación segura
        print("🔐 PASO 1: Autenticación segura del operador")

        # Generar código 2FA de demo
        import pyotp
        demo_totp = pyotp.TOTP("JBSWY3DPEHPK3PXP")  # Secreto fijo para demo
        current_code = demo_totp.now()

        auth_result = workflow_system.authenticate_and_start_session(
            "OP001",
            current_code,
            (-34.6037, -58.3816),  # GPS Buenos Aires
            "smartphone-android-v12"
        )

        if not auth_result["success"]:
            print(f"❌ Fallo autenticación: {auth_result['error']}")
            return

        print(f"✅ Autenticado en: {auth_result['location']}")

        # 2. Captura y análisis de foto
        print("\n📸 PASO 2: Captura de foto del problema")

        # Crear imagen de demo
        demo_image_path = "reports/demo_problem_photo.jpg"
        Path("reports").mkdir(exist_ok=True)

        # Crear imagen simulada (en realidad sería de cámara)
        from PIL import Image
        demo_image = Image.new('RGB', (640, 480), color=(100, 100, 100))
        demo_image.save(demo_image_path)

        # Procesar problema con workflow completo
        analysis_result = workflow_system.process_field_problem_with_photo(
            demo_image_path,
            "PLC Siemens S7-1214C no responde a comandos desde HMI, LED rojo parpadeando",
            "PLC Siemens S7-1214C",
            "alta"
        )

        if "error" in analysis_result:
            print(f"❌ Error en análisis: {analysis_result['error']}")
            return

        print(f"✅ Análisis completado - Confianza: {analysis_result['confidence_score']:.1%}")
        print(f"   📋 Recomendaciones: {len(analysis_result['combined_recommendations'])}")
        print(f"   ⚠️ Requiere aprobación: {'Sí' if analysis_result['approval_required'] else 'No'}")

        # 3. Mostrar recomendaciones principales
        print("\n🤖 PASO 3: Recomendaciones de IA integrada")
        for i, rec in enumerate(analysis_result["combined_recommendations"][:3], 1):
            source = rec.get("source", "unknown")
            confidence = rec.get("confidence", 0) * 100
            print(f"   {i}. {rec['action']} ({source.upper()}, {confidence:.0f}%)")

        # 4. Ejecutar acciones (simular aprobación automática para demo)
        print("\n⚙️ PASO 4: Ejecución de acciones recomendadas")

        execution_result = workflow_system.execute_approved_actions(analysis_result["request_id"])

        if "error" in execution_result:
            print(f"❌ Error ejecutando: {execution_result['error']}")
        else:
            print(f"✅ Acciones ejecutadas en {execution_result['execution_time_minutes']:.1f} min")
            print(f"   📈 Resultado: {execution_result['outcome']}")

        # 5. Agregar feedback
        print("\n💬 PASO 5: Feedback del operador")

        feedback_result = workflow_system.add_intervention_feedback(
            execution_result["intervention_id"],
            5.0,
            "Problema resuelto exitosamente. Análisis muy preciso."
        )

        if feedback_result["success"]:
            print("✅ Feedback registrado para aprendizaje continuo")

        # 6. Resumen de sesión
        print("\n📊 PASO 6: Resumen de sesión")
        session_summary = workflow_system.get_session_summary()

        print(f"   ⏱️ Duración: {session_summary['session_info']['duration_hours']} horas")
        print(f"   📝 Intervenciones: {session_summary['activity_summary']['completed_interventions']}")
        print(f"   ✅ Tasa éxito: {session_summary['activity_summary']['success_rate']:.1%}")

        # 7. Cerrar sesión
        print("\n📋 PASO 7: Cerrando sesión")
        close_result = workflow_system.close_session()

        if close_result["success"]:
            print(f"✅ Sesión cerrada - Reporte: {close_result['report_path']}")

        print("\n🎯 WORKFLOW INTEGRADO COMPLETADO")
        print("\n💡 FUNCIONALIDADES DEMOSTRADAS:")
        print("  ✅ Autenticación 2FA + GPS")
        print("  ✅ Análisis visual con IA")
        print("  ✅ Razonamiento HRM")
        print("  ✅ Recomendaciones mejoradas")
        print("  ✅ Sistema de aprobaciones")
        print("  ✅ Ejecución supervisada")
        print("  ✅ Aprendizaje continuo")
        print("  ✅ Trazabilidad completa")

    except Exception as e:
        print(f"❌ Error en demostración: {e}")

    finally:
        # Limpiar
        workflow_system.shutdown_system()

def main():
    """Función principal"""
    demonstrate_complete_workflow()

if __name__ == "__main__":
    main()