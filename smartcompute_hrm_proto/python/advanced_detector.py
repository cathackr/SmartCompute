#!/usr/bin/env python3
import json
import re
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class InjectionPattern:
    technique: str
    indicators: List[str]
    severity: str
    mitre_id: str

class AdvancedProcessInjectionDetector:
    def __init__(self):
        self.patterns = [
            InjectionPattern(
                technique="CreateRemoteThread",
                indicators=["CreateRemoteThread", "WriteProcessMemory", "VirtualAllocEx"],
                severity="HIGH",
                mitre_id="T1055.002"
            ),
            InjectionPattern(
                technique="Process Hollowing",
                indicators=["NtUnmapViewOfSection", "CreateProcess.*SUSPENDED", "SetThreadContext"],
                severity="CRITICAL",
                mitre_id="T1055.012"
            ),
            InjectionPattern(
                technique="DLL Injection",
                indicators=["LoadLibrary", "GetProcAddress", "CreateRemoteThread"],
                severity="MEDIUM",
                mitre_id="T1055.001"
            ),
            InjectionPattern(
                technique="PE Injection",
                indicators=["VirtualAllocEx", "WriteProcessMemory", "CreateRemoteThread"],
                severity="HIGH",
                mitre_id="T1055.002"
            )
        ]

        self.trusted_processes = [
            "svchost.exe", "winlogon.exe", "csrss.exe", "lsass.exe"
        ]

        self.suspicious_targets = [
            "chrome.exe", "firefox.exe", "iexplore.exe", "powershell.exe", "cmd.exe"
        ]

    def analyze_injection(self, event_data: Dict) -> Dict:
        results = {
            "detected_techniques": [],
            "risk_score": 0,
            "context_analysis": {},
            "recommended_actions": []
        }

        description = event_data.get("description", "").lower()
        process_path = event_data.get("process_path", "").lower()
        raw_payload = event_data.get("raw_payload", "").lower()

        # Detectar técnicas específicas
        for pattern in self.patterns:
            matches = sum(1 for indicator in pattern.indicators
                         if re.search(indicator.lower(), description + " " + raw_payload))

            if matches >= 1:
                technique_result = {
                    "technique": pattern.technique,
                    "mitre_id": pattern.mitre_id,
                    "severity": pattern.severity,
                    "confidence": min(matches / len(pattern.indicators), 1.0),
                    "indicators_found": matches
                }
                results["detected_techniques"].append(technique_result)

                # Calcular score de riesgo
                severity_scores = {"LOW": 1, "MEDIUM": 3, "HIGH": 5, "CRITICAL": 8}
                results["risk_score"] += severity_scores.get(pattern.severity, 0) * technique_result["confidence"]

        # Análisis contextual
        results["context_analysis"] = self._analyze_context(process_path, event_data)

        # Generar recomendaciones
        results["recommended_actions"] = self._generate_recommendations(results, event_data)

        return results

    def _analyze_context(self, process_path: str, event_data: Dict) -> Dict:
        context = {
            "target_process": None,
            "is_suspicious_target": False,
            "is_trusted_source": False,
            "timestamp_analysis": None
        }

        # Extraer proceso target
        for target in self.suspicious_targets:
            if target in process_path:
                context["target_process"] = target
                context["is_suspicious_target"] = True
                break

        # Verificar si el proceso fuente es confiable
        for trusted in self.trusted_processes:
            if trusted in process_path:
                context["is_trusted_source"] = True
                break

        # Análisis temporal (horario sospechoso)
        timestamp = event_data.get("timestamp", "")
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                hour = dt.hour
                if hour < 6 or hour > 22:  # Fuera de horario laboral
                    context["timestamp_analysis"] = "suspicious_hours"
                else:
                    context["timestamp_analysis"] = "business_hours"
            except:
                context["timestamp_analysis"] = "invalid_timestamp"

        return context

    def _generate_recommendations(self, analysis_results: Dict, event_data: Dict) -> List[str]:
        recommendations = []

        risk_score = analysis_results.get("risk_score", 0)
        context = analysis_results.get("context_analysis", {})

        if risk_score >= 5:
            recommendations.extend([
                "IMMEDIATE: Isolate affected host from network",
                "Collect full memory dump for forensic analysis",
                "Block suspicious process execution"
            ])

        if context.get("is_suspicious_target"):
            recommendations.append("Monitor browser/shell processes for anomalous behavior")

        if context.get("timestamp_analysis") == "suspicious_hours":
            recommendations.append("Investigate why process injection occurred outside business hours")

        if not context.get("is_trusted_source"):
            recommendations.extend([
                "Analyze parent process chain",
                "Check process digital signatures"
            ])

        # Recomendaciones específicas por técnica
        for technique in analysis_results.get("detected_techniques", []):
            if technique["technique"] == "CreateRemoteThread":
                recommendations.append("Enable advanced EDR monitoring for CreateRemoteThread API calls")
            elif technique["technique"] == "Process Hollowing":
                recommendations.append("CRITICAL: Likely advanced malware - engage incident response team")

        return recommendations

def main():
    detector = AdvancedProcessInjectionDetector()

    # Cargar evento de muestra
    with open("../redacted_output.json", "r") as f:
        data = json.load(f)

    if "findings" in data:
        for finding in data["findings"]:
            print(f"\n=== Analyzing Event {finding.get('event_id', 'Unknown')} ===")
            analysis = detector.analyze_injection(finding)

            print(f"Risk Score: {analysis['risk_score']:.1f}/10")
            print(f"Detected Techniques: {len(analysis['detected_techniques'])}")

            for technique in analysis["detected_techniques"]:
                print(f"  - {technique['technique']} (MITRE: {technique['mitre_id']}) "
                      f"Confidence: {technique['confidence']:.2f}")

            print("\nRecommended Actions:")
            for action in analysis["recommended_actions"]:
                print(f"  • {action}")

            # Guardar análisis detallado
            output_file = f"../plans/injection_analysis_{finding.get('event_id', 'unknown')}.json"
            with open(output_file, "w") as f:
                json.dump(analysis, f, indent=2)
            print(f"\nDetailed analysis saved to: {output_file}")

if __name__ == "__main__":
    main()