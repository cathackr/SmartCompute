#!/usr/bin/env python3
import json
import time
import hashlib
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class ThreatIndicator:
    ioc_type: str
    value: str
    confidence: float
    source: str
    first_seen: str
    last_seen: str
    threat_types: List[str]
    malware_families: List[str]

@dataclass
class ThreatActor:
    name: str
    aliases: List[str]
    techniques: List[str]  # MITRE ATT&CK
    target_sectors: List[str]
    confidence: float

class ThreatIntelligenceEngine:
    """Motor de Threat Intelligence integrado"""

    def __init__(self):
        self.ioc_database = {}
        self.threat_actors = {}
        self.mitre_techniques = {}
        self.load_threat_data()

    def load_threat_data(self):
        """Cargar datos de threat intelligence (simulado)"""

        # IOCs simulados
        self.ioc_database = {
            "hashes": {
                "md5": {
                    "a1b2c3d4e5f6g7h8i9j0": ThreatIndicator(
                        ioc_type="md5",
                        value="a1b2c3d4e5f6g7h8i9j0",
                        confidence=0.9,
                        source="VirusTotal",
                        first_seen="2025-08-15",
                        last_seen="2025-09-10",
                        threat_types=["Trojan", "Process Injection"],
                        malware_families=["Cobalt Strike"]
                    )
                }
            },
            "domains": {
                "malicious-c2.com": ThreatIndicator(
                    ioc_type="domain",
                    value="malicious-c2.com",
                    confidence=0.95,
                    source="Cyber Threat Intelligence",
                    first_seen="2025-07-20",
                    last_seen="2025-09-14",
                    threat_types=["C2", "Command and Control"],
                    malware_families=["APT29"]
                )
            },
            "ips": {
                "203.0.113.45": ThreatIndicator(
                    ioc_type="ip",
                    value="203.0.113.45",
                    confidence=0.8,
                    source="OSINT",
                    first_seen="2025-08-01",
                    last_seen="2025-09-12",
                    threat_types=["Scanning", "Reconnaissance"],
                    malware_families=[]
                )
            }
        }

        # Threat Actors simulados
        self.threat_actors = {
            "APT29": ThreatActor(
                name="APT29",
                aliases=["Cozy Bear", "The Dukes"],
                techniques=["T1055", "T1055.002", "T1059.001", "T1071.001"],
                target_sectors=["Government", "Healthcare", "Technology"],
                confidence=0.9
            ),
            "Cobalt Strike Users": ThreatActor(
                name="Cobalt Strike Users",
                aliases=["CS Teams"],
                techniques=["T1055.002", "T1055.012", "T1134"],
                target_sectors=["Finance", "Healthcare", "Government"],
                confidence=0.7
            )
        }

        # Técnicas MITRE ATT&CK
        self.mitre_techniques = {
            "T1055": {
                "name": "Process Injection",
                "description": "Adversaries may inject code into processes",
                "tactics": ["Defense Evasion", "Privilege Escalation"],
                "sub_techniques": ["T1055.001", "T1055.002", "T1055.012"]
            },
            "T1055.002": {
                "name": "Portable Executable Injection",
                "description": "Adversaries may inject portable executables (PE) into processes",
                "tactics": ["Defense Evasion", "Privilege Escalation"],
                "detection": ["Process monitoring", "API call monitoring"]
            },
            "T1055.012": {
                "name": "Process Hollowing",
                "description": "Adversaries may inject malicious code into suspended and hollowed processes",
                "tactics": ["Defense Evasion", "Privilege Escalation"],
                "detection": ["Process creation monitoring", "Memory analysis"]
            }
        }

    def enrich_with_threat_intel(self, event_data: Dict) -> Dict:
        """Enriquecer evento con threat intelligence"""

        threat_intel = {
            "ioc_matches": [],
            "technique_analysis": {},
            "threat_actor_attribution": [],
            "risk_assessment": {},
            "contextual_indicators": []
        }

        # Analizar IOCs
        threat_intel["ioc_matches"] = self._check_iocs(event_data)

        # Analizar técnicas MITRE
        threat_intel["technique_analysis"] = self._analyze_mitre_techniques(event_data)

        # Atribuir threat actors
        threat_intel["threat_actor_attribution"] = self._attribute_threat_actors(
            threat_intel["technique_analysis"]
        )

        # Evaluar riesgo
        threat_intel["risk_assessment"] = self._assess_threat_risk(threat_intel)

        # Indicadores contextuales
        threat_intel["contextual_indicators"] = self._find_contextual_indicators(event_data)

        return threat_intel

    def _check_iocs(self, event_data: Dict) -> List[Dict]:
        """Verificar IOCs en el evento"""
        matches = []

        # Extraer elementos verificables del evento
        process_path = event_data.get("process_path", "")
        description = event_data.get("description", "")
        raw_payload = event_data.get("raw_payload", "")

        # Simular hash del proceso
        if process_path:
            simulated_hash = hashlib.md5(process_path.encode()).hexdigest()[:20]

            # Verificar si coincide con IOCs conocidos (simulado)
            if simulated_hash in ["a1b2c3d4e5f6g7h8i9j0"]:  # Hash malicioso simulado
                ioc = self.ioc_database["hashes"]["md5"][simulated_hash]
                matches.append({
                    "ioc_type": "process_hash",
                    "matched_value": simulated_hash,
                    "confidence": ioc.confidence,
                    "threat_types": ioc.threat_types,
                    "source": ioc.source
                })

        # Verificar patterns en descripción/payload
        combined_text = f"{description} {raw_payload}".lower()

        # Buscar indicadores de técnicas conocidas
        technique_indicators = {
            "createremotethread": ["T1055.002"],
            "process hollowing": ["T1055.012"],
            "dll injection": ["T1055.001"],
            "cobalt strike": ["Cobalt Strike"]
        }

        for indicator, associated_threats in technique_indicators.items():
            if indicator in combined_text:
                matches.append({
                    "ioc_type": "technique_indicator",
                    "matched_value": indicator,
                    "confidence": 0.7,
                    "associated_threats": associated_threats,
                    "source": "Pattern Matching"
                })

        return matches

    def _analyze_mitre_techniques(self, event_data: Dict) -> Dict:
        """Analizar técnicas MITRE ATT&CK"""
        analysis = {
            "identified_techniques": [],
            "tactic_coverage": [],
            "kill_chain_stage": None
        }

        description = event_data.get("description", "").lower()

        # Mapear observaciones a técnicas MITRE
        if "createremotethread" in description:
            technique = self.mitre_techniques.get("T1055.002", {})
            analysis["identified_techniques"].append({
                "technique_id": "T1055.002",
                "technique_name": technique.get("name", "Unknown"),
                "confidence": 0.8,
                "evidence": "CreateRemoteThread API call observed"
            })

            # Agregar táctica padre
            parent_technique = self.mitre_techniques.get("T1055", {})
            analysis["identified_techniques"].append({
                "technique_id": "T1055",
                "technique_name": parent_technique.get("name", "Unknown"),
                "confidence": 0.9,
                "evidence": "Process injection behavior detected"
            })

            analysis["tactic_coverage"] = ["Defense Evasion", "Privilege Escalation"]
            analysis["kill_chain_stage"] = "Actions on Objectives"

        return analysis

    def _attribute_threat_actors(self, technique_analysis: Dict) -> List[Dict]:
        """Atribuir threat actors basado en técnicas"""
        attributions = []

        identified_techniques = [
            t["technique_id"] for t in technique_analysis.get("identified_techniques", [])
        ]

        for actor_name, actor in self.threat_actors.items():
            # Calcular overlap de técnicas
            technique_overlap = set(identified_techniques) & set(actor.techniques)
            overlap_score = len(technique_overlap) / max(len(actor.techniques), 1)

            if overlap_score > 0.3:  # Threshold de similaridad
                attributions.append({
                    "threat_actor": actor_name,
                    "aliases": actor.aliases,
                    "confidence": overlap_score * actor.confidence,
                    "matching_techniques": list(technique_overlap),
                    "target_sectors": actor.target_sectors
                })

        # Ordenar por confianza
        attributions.sort(key=lambda x: x["confidence"], reverse=True)
        return attributions[:3]  # Top 3

    def _assess_threat_risk(self, threat_intel: Dict) -> Dict:
        """Evaluar riesgo de amenaza"""
        risk_score = 0.0
        risk_factors = []

        # Puntuar basado en IOCs
        ioc_matches = threat_intel.get("ioc_matches", [])
        for match in ioc_matches:
            risk_score += match.get("confidence", 0) * 2
            risk_factors.append(f"IOC match: {match['ioc_type']}")

        # Puntuar basado en técnicas
        techniques = threat_intel.get("technique_analysis", {}).get("identified_techniques", [])
        for technique in techniques:
            risk_score += technique.get("confidence", 0) * 1.5
            risk_factors.append(f"MITRE technique: {technique['technique_id']}")

        # Puntuar basado en atribución de threat actors
        attributions = threat_intel.get("threat_actor_attribution", [])
        for attribution in attributions:
            risk_score += attribution.get("confidence", 0) * 3
            risk_factors.append(f"Threat actor attribution: {attribution['threat_actor']}")

        # Normalizar score
        normalized_score = min(risk_score / 10.0, 1.0)

        return {
            "threat_score": normalized_score,
            "risk_level": self._categorize_risk(normalized_score),
            "risk_factors": risk_factors,
            "recommendation": self._generate_threat_recommendation(normalized_score)
        }

    def _categorize_risk(self, score: float) -> str:
        """Categorizar nivel de riesgo"""
        if score >= 0.8:
            return "CRITICAL"
        elif score >= 0.6:
            return "HIGH"
        elif score >= 0.4:
            return "MEDIUM"
        else:
            return "LOW"

    def _generate_threat_recommendation(self, score: float) -> str:
        """Generar recomendación basada en threat intel"""
        if score >= 0.8:
            return "IMMEDIATE_ACTION: Known threat actor technique detected - initiate incident response"
        elif score >= 0.6:
            return "HIGH_PRIORITY: Likely malicious activity - escalate to security team"
        elif score >= 0.4:
            return "INVESTIGATE: Suspicious patterns detected - requires analysis"
        else:
            return "MONITOR: Low threat confidence - continue monitoring"

    def _find_contextual_indicators(self, event_data: Dict) -> List[str]:
        """Encontrar indicadores contextuales"""
        indicators = []

        timestamp = event_data.get("timestamp", "")
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                # Actividad fuera de horario laboral
                if dt.hour < 8 or dt.hour > 18:
                    indicators.append("off_hours_activity")
            except:
                pass

        # Proceso target común para ataques
        process_path = event_data.get("process_path", "").lower()
        if "chrome.exe" in process_path:
            indicators.append("browser_targeting")

        # Severidad crítica
        severity = event_data.get("severity", "")
        if severity == "CRITICAL":
            indicators.append("critical_severity_event")

        return indicators

def main():
    # Crear motor de threat intelligence
    threat_intel_engine = ThreatIntelligenceEngine()

    # Cargar evento
    with open("../redacted_output.json", "r") as f:
        data = json.load(f)

    if "findings" in data:
        for finding in data["findings"]:
            print(f"\n=== Threat Intelligence Analysis for Event {finding.get('event_id', 'Unknown')} ===")

            # Enriquecer con threat intelligence
            threat_intel = threat_intel_engine.enrich_with_threat_intel(finding)

            print(f"Threat Score: {threat_intel['risk_assessment']['threat_score']:.3f}")
            print(f"Risk Level: {threat_intel['risk_assessment']['risk_level']}")
            print(f"Recommendation: {threat_intel['risk_assessment']['recommendation']}")

            print("\nIOC Matches:")
            for match in threat_intel["ioc_matches"]:
                print(f"  • {match['ioc_type']}: {match['matched_value']} (confidence: {match['confidence']:.2f})")

            print("\nMITRE Techniques:")
            for technique in threat_intel["technique_analysis"]["identified_techniques"]:
                print(f"  • {technique['technique_id']}: {technique['technique_name']} (confidence: {technique['confidence']:.2f})")

            print("\nThreat Actor Attribution:")
            for attribution in threat_intel["threat_actor_attribution"]:
                print(f"  • {attribution['threat_actor']} (confidence: {attribution['confidence']:.2f})")

            # Guardar análisis completo
            output_file = f"../plans/threat_intel_analysis_{finding.get('event_id', 'unknown')}.json"
            with open(output_file, "w") as f:
                json.dump(threat_intel, f, indent=2)
            print(f"\nThreat intelligence analysis saved to: {output_file}")

if __name__ == "__main__":
    main()