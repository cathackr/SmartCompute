#!/usr/bin/env python3
import json
import math
from typing import Dict, List
from datetime import datetime

class SimpleFalsePositiveAnalyzer:
    """Analizador simple de falsos positivos sin dependencias ML externas"""

    def __init__(self):
        self.legitimate_patterns = {
            "chrome_extensions": {
                "process_patterns": ["chrome.exe", "chrome_proxy.exe"],
                "location_patterns": ["program files", "google", "chrome"],
                "description_patterns": ["extension", "plugin", "renderer"]
            },
            "system_processes": {
                "process_patterns": ["svchost.exe", "winlogon.exe", "csrss.exe"],
                "location_patterns": ["system32", "syswow64", "windows"],
                "description_patterns": ["system", "service", "legitimate"]
            },
            "business_hours": {
                "hours": list(range(8, 18)),  # 8 AM - 6 PM
                "weekdays": list(range(0, 5))  # Lunes a Viernes
            }
        }

    def calculate_false_positive_score(self, event_data: Dict, behavioral_analysis: Dict = None) -> Dict:
        """Calcular score de falso positivo usando heurísticas simples"""

        fp_score = 0.0
        evidence = []

        # Analizar proceso
        process_score, process_evidence = self._analyze_process_legitimacy(event_data)
        fp_score += process_score
        evidence.extend(process_evidence)

        # Analizar tiempo
        temporal_score, temporal_evidence = self._analyze_temporal_legitimacy(event_data)
        fp_score += temporal_score
        evidence.extend(temporal_evidence)

        # Analizar descripción
        description_score, desc_evidence = self._analyze_description_legitimacy(event_data)
        fp_score += description_score
        evidence.extend(desc_evidence)

        # Analizar contexto comportamental
        if behavioral_analysis:
            behavioral_score, behavioral_evidence = self._analyze_behavioral_context(behavioral_analysis)
            fp_score += behavioral_score
            evidence.extend(behavioral_evidence)

        # Normalizar score (0-1, donde 1 = muy probable falso positivo)
        normalized_score = min(fp_score / 10.0, 1.0)

        return {
            "false_positive_probability": normalized_score,
            "confidence_level": self._calculate_confidence(len(evidence)),
            "evidence": evidence,
            "recommendation": self._generate_recommendation(normalized_score),
            "detailed_scores": {
                "process_legitimacy": process_score,
                "temporal_legitimacy": temporal_score,
                "description_legitimacy": description_score,
                "behavioral_legitimacy": behavioral_score if behavioral_analysis else 0.0
            }
        }

    def _analyze_process_legitimacy(self, event_data: Dict) -> tuple:
        """Analizar legitimidad del proceso"""
        score = 0.0
        evidence = []

        process_path = event_data.get("process_path", "").lower()

        # Verificar si es chrome en ubicación legítima
        if "chrome.exe" in process_path and "program files" in process_path:
            score += 3.0
            evidence.append("chrome_in_legitimate_location")

        # Verificar si es proceso del sistema en ubicación correcta
        for pattern in self.legitimate_patterns["system_processes"]["process_patterns"]:
            if pattern in process_path and any(loc in process_path for loc in
                                             self.legitimate_patterns["system_processes"]["location_patterns"]):
                score += 2.5
                evidence.append(f"system_process_{pattern}_in_system_location")

        # Penalizar procesos en ubicaciones sospechosas
        suspicious_locations = ["temp", "appdata", "downloads", "public"]
        for location in suspicious_locations:
            if location in process_path:
                score -= 2.0
                evidence.append(f"suspicious_location_{location}")

        return score, evidence

    def _analyze_temporal_legitimacy(self, event_data: Dict) -> tuple:
        """Analizar legitimidad temporal"""
        score = 0.0
        evidence = []

        timestamp = event_data.get("timestamp", "")
        if not timestamp:
            return score, evidence

        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))

            # Horario laboral es más legítimo
            if dt.hour in self.legitimate_patterns["business_hours"]["hours"]:
                score += 1.5
                evidence.append("business_hours_activity")
            else:
                score -= 1.0
                evidence.append("off_hours_activity")

            # Días laborales son más legítimos
            if dt.weekday() in self.legitimate_patterns["business_hours"]["weekdays"]:
                score += 1.0
                evidence.append("weekday_activity")
            else:
                score -= 0.5
                evidence.append("weekend_activity")

        except Exception:
            evidence.append("invalid_timestamp")

        return score, evidence

    def _analyze_description_legitimacy(self, event_data: Dict) -> tuple:
        """Analizar legitimidad de la descripción"""
        score = 0.0
        evidence = []

        description = event_data.get("description", "").lower()
        raw_payload = event_data.get("raw_payload", "").lower()
        combined_text = f"{description} {raw_payload}"

        # Patrones que indican actividad legítima
        legitimate_keywords = [
            "extension", "plugin", "renderer", "service", "system",
            "legitimate", "normal", "expected", "chrome", "browser"
        ]

        # Patrones que indican actividad sospechosa
        suspicious_keywords = [
            "malware", "virus", "trojan", "backdoor", "exploit",
            "shellcode", "payload", "injection", "suspicious"
        ]

        # Calcular score basado en keywords
        legitimate_count = sum(1 for keyword in legitimate_keywords if keyword in combined_text)
        suspicious_count = sum(1 for keyword in suspicious_keywords if keyword in combined_text)

        score += legitimate_count * 0.5
        score -= suspicious_count * 1.0

        if legitimate_count > 0:
            evidence.append(f"legitimate_keywords_found_{legitimate_count}")
        if suspicious_count > 0:
            evidence.append(f"suspicious_keywords_found_{suspicious_count}")

        # Verificar si la descripción menciona CreateRemoteThread en chrome
        if "createremotethread" in combined_text and "chrome" in combined_text:
            score += 2.0
            evidence.append("chrome_createremotethread_pattern")

        return score, evidence

    def _analyze_behavioral_context(self, behavioral_analysis: Dict) -> tuple:
        """Analizar contexto comportamental"""
        score = 0.0
        evidence = []

        behavioral_score = behavioral_analysis.get("behavioral_score", 0.0)

        # Score comportamental bajo indica mayor legitimidad
        if behavioral_score < 2.0:
            score += 2.0
            evidence.append("low_behavioral_anomaly")
        elif behavioral_score > 5.0:
            score -= 1.5
            evidence.append("high_behavioral_anomaly")

        # Verificar insights específicos
        context_insights = behavioral_analysis.get("context_insights", {})

        # Usuario conocido es más legítimo
        user_insights = context_insights.get("user", {})
        if user_insights.get("is_known_user", False):
            score += 1.0
            evidence.append("known_user")

        # Proceso conocido es más legítimo
        process_insights = context_insights.get("process", {})
        if process_insights.get("is_known_process", False):
            score += 1.0
            evidence.append("known_process")

        return score, evidence

    def _calculate_confidence(self, evidence_count: int) -> str:
        """Calcular nivel de confianza basado en cantidad de evidencia"""
        if evidence_count >= 5:
            return "HIGH"
        elif evidence_count >= 3:
            return "MEDIUM"
        else:
            return "LOW"

    def _generate_recommendation(self, fp_probability: float) -> str:
        """Generar recomendación basada en probabilidad de falso positivo"""
        if fp_probability >= 0.7:
            return "LIKELY_FALSE_POSITIVE: Consider suppressing or lowering priority"
        elif fp_probability >= 0.4:
            return "POSSIBLE_FALSE_POSITIVE: Review context before escalation"
        elif fp_probability <= 0.2:
            return "LIKELY_LEGITIMATE_THREAT: Proceed with standard investigation"
        else:
            return "UNCERTAIN: Requires additional analysis"

def main():
    analyzer = SimpleFalsePositiveAnalyzer()

    # Cargar datos del evento
    with open("../redacted_output.json", "r") as f:
        data = json.load(f)

    # Cargar análisis comportamental si existe
    try:
        with open("../plans/behavioral_analysis_8.json", "r") as f:
            behavioral_analysis = json.load(f)
    except:
        behavioral_analysis = None

    if "findings" in data:
        for finding in data["findings"]:
            print(f"\n=== Simple ML Analysis for Event {finding.get('event_id', 'Unknown')} ===")

            # Calcular score de falso positivo
            fp_analysis = analyzer.calculate_false_positive_score(finding, behavioral_analysis)

            print(f"False Positive Probability: {fp_analysis['false_positive_probability']:.3f}")
            print(f"Confidence Level: {fp_analysis['confidence_level']}")
            print(f"Recommendation: {fp_analysis['recommendation']}")

            print("\nEvidence Found:")
            for evidence in fp_analysis['evidence']:
                print(f"  • {evidence}")

            print("\nDetailed Scores:")
            for score_type, score_value in fp_analysis['detailed_scores'].items():
                print(f"  {score_type}: {score_value:.2f}")

            # Guardar análisis
            output_file = f"../plans/simple_ml_analysis_{finding.get('event_id', 'unknown')}.json"
            with open(output_file, "w") as f:
                json.dump(fp_analysis, f, indent=2)
            print(f"\nSimple ML analysis saved to: {output_file}")

if __name__ == "__main__":
    main()