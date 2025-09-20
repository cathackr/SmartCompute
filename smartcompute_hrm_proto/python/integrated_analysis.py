#!/usr/bin/env python3
"""
Análisis integrado que combina todos los módulos implementados
"""
import json
from advanced_detector import AdvancedProcessInjectionDetector
from behavioral_analyzer import BehavioralAnalyzer
from simple_ml_analyzer import SimpleFalsePositiveAnalyzer
from threat_intelligence import ThreatIntelligenceEngine
from incident_response import AutomatedIncidentResponse

def run_integrated_analysis(event_data):
    """Ejecutar análisis completo e integrado"""
    print("🔍 Iniciando análisis integrado SmartCompute HRM...")

    results = {
        "event_id": event_data.get("event_id", "unknown"),
        "timestamp": event_data.get("timestamp"),
        "analysis_modules": {},
        "final_assessment": {}
    }

    # 1. Detección avanzada de process injection
    print("\n1️⃣ Ejecutando detección avanzada...")
    detector = AdvancedProcessInjectionDetector()
    advanced_analysis = detector.analyze_injection(event_data)
    results["analysis_modules"]["advanced_detection"] = advanced_analysis

    # 2. Análisis comportamental
    print("2️⃣ Ejecutando análisis comportamental...")
    behavioral_analyzer = BehavioralAnalyzer()
    behavioral_analysis = behavioral_analyzer.analyze_behavioral_context(event_data)
    results["analysis_modules"]["behavioral_analysis"] = behavioral_analysis

    # 3. Análisis ML para falsos positivos
    print("3️⃣ Ejecutando análisis ML anti-falsos positivos...")
    ml_analyzer = SimpleFalsePositiveAnalyzer()
    ml_analysis = ml_analyzer.calculate_false_positive_score(event_data, behavioral_analysis)
    results["analysis_modules"]["ml_false_positive"] = ml_analysis

    # 4. Threat Intelligence
    print("4️⃣ Ejecutando análisis de threat intelligence...")
    threat_intel_engine = ThreatIntelligenceEngine()
    threat_intel = threat_intel_engine.enrich_with_threat_intel(event_data)
    results["analysis_modules"]["threat_intelligence"] = threat_intel

    # 5. Evaluación final integrada
    print("5️⃣ Generando evaluación final...")
    final_assessment = generate_final_assessment(results["analysis_modules"])
    results["final_assessment"] = final_assessment

    # 6. Respuesta automática si es necesario
    if final_assessment["requires_response"]:
        print("6️⃣ Ejecutando respuesta automática...")
        response_system = AutomatedIncidentResponse()
        incident_response = response_system.process_incident(advanced_analysis, event_data)
        results["incident_response"] = incident_response

    return results

def generate_final_assessment(analysis_modules):
    """Generar evaluación final integrando todos los análisis"""

    # Extraer scores clave
    risk_score = analysis_modules["advanced_detection"]["risk_score"]
    behavioral_score = analysis_modules["behavioral_analysis"]["behavioral_score"]
    fp_probability = analysis_modules["ml_false_positive"]["false_positive_probability"]
    threat_score = analysis_modules["threat_intelligence"]["risk_assessment"]["threat_score"]

    # Calcular score final ponderado
    # Si hay alta probabilidad de falso positivo, reducir significativamente el riesgo
    if fp_probability > 0.7:
        adjusted_risk = risk_score * (1 - fp_probability) * 0.3  # Reducción drástica
        confidence_level = "HIGH_FALSE_POSITIVE"
    elif fp_probability > 0.4:
        adjusted_risk = risk_score * (1 - fp_probability) * 0.6  # Reducción moderada
        confidence_level = "POSSIBLE_FALSE_POSITIVE"
    else:
        # Combinar scores normalmente
        weights = {
            "technical": 0.3,
            "behavioral": 0.2,
            "threat_intel": 0.5
        }
        adjusted_risk = (
            risk_score * weights["technical"] +
            behavioral_score * weights["behavioral"] +
            threat_score * 10 * weights["threat_intel"]  # threat_score está normalizado 0-1
        )
        confidence_level = "LEGITIMATE_THREAT"

    # Determinar nivel de riesgo final
    if adjusted_risk >= 7.0:
        risk_level = "CRITICAL"
        requires_response = True
    elif adjusted_risk >= 5.0:
        risk_level = "HIGH"
        requires_response = True
    elif adjusted_risk >= 3.0:
        risk_level = "MEDIUM"
        requires_response = False
    else:
        risk_level = "LOW"
        requires_response = False

    # Generar recomendación final
    recommendation = generate_integrated_recommendation(
        confidence_level, risk_level, fp_probability, analysis_modules
    )

    return {
        "final_risk_score": adjusted_risk,
        "risk_level": risk_level,
        "confidence_level": confidence_level,
        "false_positive_probability": fp_probability,
        "requires_response": requires_response,
        "recommendation": recommendation,
        "summary": generate_executive_summary(analysis_modules, adjusted_risk, confidence_level)
    }

def generate_integrated_recommendation(confidence_level, risk_level, fp_probability, analysis_modules):
    """Generar recomendación integrada"""

    if confidence_level == "HIGH_FALSE_POSITIVE":
        return {
            "action": "SUPPRESS_ALERT",
            "reasoning": f"85%+ probabilidad de falso positivo. Evento típico de Chrome con CreateRemoteThread para extensiones.",
            "next_steps": [
                "Suprimir alerta o reducir prioridad",
                "Actualizar reglas de detección para reducir ruido",
                "Monitorear patrones similares para refinamiento"
            ]
        }

    elif confidence_level == "POSSIBLE_FALSE_POSITIVE":
        return {
            "action": "REVIEW_REQUIRED",
            "reasoning": "Probabilidad moderada de falso positivo. Requiere revisión analista.",
            "next_steps": [
                "Revisión manual por analista de seguridad",
                "Validar contexto adicional antes de escalación",
                "Documentar decisión para mejora de modelos"
            ]
        }

    else:  # LEGITIMATE_THREAT
        threat_actors = analysis_modules["threat_intelligence"]["threat_actor_attribution"]
        if threat_actors:
            top_actor = threat_actors[0]["threat_actor"]
            return {
                "action": "IMMEDIATE_INVESTIGATION",
                "reasoning": f"Amenaza legítima detectada con posible atribución a {top_actor}",
                "next_steps": [
                    "Iniciar investigación inmediata",
                    "Aislar host afectado",
                    "Recolectar evidencia forense",
                    "Notificar a equipo de respuesta a incidentes"
                ]
            }
        else:
            return {
                "action": "STANDARD_INVESTIGATION",
                "reasoning": "Amenaza legítima detectada - seguir protocolos estándar",
                "next_steps": [
                    "Investigación estándar por equipo SOC",
                    "Monitoreo enhancido del host",
                    "Revisión de logs adicionales"
                ]
            }

def generate_executive_summary(analysis_modules, risk_score, confidence_level):
    """Generar resumen ejecutivo"""

    techniques = analysis_modules["advanced_detection"]["detected_techniques"]
    technique_names = [t["technique"] for t in techniques]

    fp_prob = analysis_modules["ml_false_positive"]["false_positive_probability"]
    threat_actors = analysis_modules["threat_intelligence"]["threat_actor_attribution"]

    summary = f"Detección de {', '.join(technique_names)} en proceso Chrome. "

    if confidence_level == "HIGH_FALSE_POSITIVE":
        summary += f"⚠️ FALSO POSITIVO (probabilidad: {fp_prob:.1%}) - Actividad legítima de extensiones Chrome."
    elif confidence_level == "POSSIBLE_FALSE_POSITIVE":
        summary += f"⚠️ POSIBLE FALSO POSITIVO (probabilidad: {fp_prob:.1%}) - Requiere validación."
    else:
        summary += f"🚨 AMENAZA LEGÍTIMA (score: {risk_score:.1f}/10)"
        if threat_actors:
            summary += f" - Posible atribución: {threat_actors[0]['threat_actor']}"

    return summary

def main():
    import sys

    # Permitir especificar archivo de prueba
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
    else:
        test_file = "../redacted_output.json"

    # Cargar evento de muestra
    with open(test_file, "r") as f:
        data = json.load(f)

    if "findings" in data and data["findings"]:
        event = data["findings"][0]

        print("=" * 60)
        print("🤖 SMARTCOMPUTE HRM - ANÁLISIS INTEGRADO")
        print("=" * 60)

        # Ejecutar análisis completo
        results = run_integrated_analysis(event)

        # Mostrar resultados
        print("\n" + "=" * 60)
        print("📊 RESULTADOS FINALES")
        print("=" * 60)

        final = results["final_assessment"]
        print(f"📋 Resumen: {final['summary']}")
        print(f"🎯 Score Final: {final['final_risk_score']:.1f}/10")
        print(f"⚠️  Nivel de Riesgo: {final['risk_level']}")
        print(f"🔍 Confianza: {final['confidence_level']}")
        print(f"🤖 Prob. Falso Positivo: {final['false_positive_probability']:.1%}")

        print(f"\n📝 Recomendación: {final['recommendation']['action']}")
        print(f"💭 Razonamiento: {final['recommendation']['reasoning']}")

        print("\n🔧 Próximos pasos:")
        for i, step in enumerate(final['recommendation']['next_steps'], 1):
            print(f"   {i}. {step}")

        if "incident_response" in results:
            print(f"\n🚨 Respuesta Automática: {len(results['incident_response']['actions_executed'])} acciones ejecutadas")

        # Guardar resultado completo
        output_file = f"../plans/integrated_analysis_{event.get('event_id', 'unknown')}.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Análisis completo guardado en: {output_file}")

        print("\n" + "=" * 60)
        print("✅ ANÁLISIS INTEGRADO COMPLETADO")
        print("=" * 60)

if __name__ == "__main__":
    main()