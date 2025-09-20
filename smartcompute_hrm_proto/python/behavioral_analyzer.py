#!/usr/bin/env python3
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from collections import defaultdict

class BehavioralAnalyzer:
    def __init__(self):
        self.baseline_patterns = self._load_baseline_patterns()
        self.anomaly_threshold = 2.5  # Standard deviations from normal

    def _load_baseline_patterns(self) -> Dict:
        """Cargar patrones de comportamiento baseline (simulado)"""
        return {
            "process_patterns": {
                "chrome.exe": {
                    "normal_parent_processes": ["explorer.exe", "cmd.exe", "powershell.exe"],
                    "normal_child_processes": ["chrome.exe", "chrome_proxy.exe"],
                    "typical_memory_usage": {"mean": 150.5, "std": 45.2},  # MB
                    "typical_cpu_usage": {"mean": 15.3, "std": 8.7},  # %
                    "normal_network_patterns": ["https", "http", "websocket"]
                },
                "svchost.exe": {
                    "normal_parent_processes": ["services.exe", "winlogon.exe"],
                    "normal_child_processes": [],
                    "typical_memory_usage": {"mean": 25.8, "std": 12.3},
                    "typical_cpu_usage": {"mean": 2.1, "std": 1.5}
                }
            },
            "user_patterns": {
                "admin@example.com": {
                    "typical_login_hours": [8, 9, 10, 11, 12, 13, 14, 15, 16, 17],
                    "normal_hosts": ["admin-workstation-1.local", "admin-laptop.local"],
                    "typical_activities": ["browser_usage", "office_apps", "admin_tools"]
                }
            },
            "network_patterns": {
                "admin-workstation-1.local": {
                    "normal_outbound_ips": ["8.8.8.8", "1.1.1.1", "192.168.1.1"],
                    "suspicious_port_usage": [4444, 8080, 9999],
                    "baseline_bandwidth": {"mean": 15.6, "std": 8.3}  # Mbps
                }
            }
        }

    def analyze_behavioral_context(self, event_data: Dict, historical_data: List[Dict] = None) -> Dict:
        """Analizar contexto comportamental del evento"""
        analysis = {
            "behavioral_score": 0.0,
            "anomalies_detected": [],
            "context_insights": {},
            "risk_factors": [],
            "behavioral_recommendation": []
        }

        # Analizar proceso
        process_analysis = self._analyze_process_behavior(event_data)
        analysis["context_insights"]["process"] = process_analysis

        # Analizar usuario
        user_analysis = self._analyze_user_behavior(event_data)
        analysis["context_insights"]["user"] = user_analysis

        # Analizar red
        network_analysis = self._analyze_network_behavior(event_data)
        analysis["context_insights"]["network"] = network_analysis

        # Analizar temporal
        temporal_analysis = self._analyze_temporal_patterns(event_data)
        analysis["context_insights"]["temporal"] = temporal_analysis

        # Calcular score comportamental total
        analysis["behavioral_score"] = self._calculate_behavioral_score(analysis["context_insights"])

        # Generar recomendaciones
        analysis["behavioral_recommendation"] = self._generate_behavioral_recommendations(analysis)

        return analysis

    def _analyze_process_behavior(self, event_data: Dict) -> Dict:
        """Analizar comportamiento del proceso"""
        process_path = event_data.get("process_path", "")
        process_name = process_path.split("\\")[-1] if "\\" in process_path else process_path.split("/")[-1]

        analysis = {
            "process_name": process_name,
            "is_known_process": False,
            "parent_chain_anomaly": False,
            "resource_usage_anomaly": False,
            "behavioral_anomalies": []
        }

        # Verificar si es un proceso conocido
        if process_name in self.baseline_patterns["process_patterns"]:
            analysis["is_known_process"] = True
            baseline = self.baseline_patterns["process_patterns"][process_name]

            # Analizar ubicación del proceso
            if "Program Files" not in process_path and "System32" not in process_path:
                analysis["behavioral_anomalies"].append("unusual_process_location")

            # Verificar horario de ejecución
            timestamp = event_data.get("timestamp", "")
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    hour = dt.hour
                    if process_name == "chrome.exe" and (hour < 7 or hour > 23):
                        analysis["behavioral_anomalies"].append("unusual_execution_time")
                except:
                    pass

        else:
            analysis["behavioral_anomalies"].append("unknown_process")

        return analysis

    def _analyze_user_behavior(self, event_data: Dict) -> Dict:
        """Analizar comportamiento del usuario"""
        source_meta = event_data.get("source_meta", {})
        user = source_meta.get("user", "unknown")
        host = source_meta.get("host", "unknown")

        analysis = {
            "user": user,
            "host": host,
            "is_known_user": False,
            "location_anomaly": False,
            "time_anomaly": False,
            "behavioral_anomalies": []
        }

        # Verificar usuario conocido
        if user in self.baseline_patterns["user_patterns"]:
            analysis["is_known_user"] = True
            user_baseline = self.baseline_patterns["user_patterns"][user]

            # Verificar host usual
            if host not in user_baseline["normal_hosts"]:
                analysis["location_anomaly"] = True
                analysis["behavioral_anomalies"].append("unusual_host_access")

            # Verificar horario típico
            timestamp = event_data.get("timestamp", "")
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    hour = dt.hour
                    if hour not in user_baseline["typical_login_hours"]:
                        analysis["time_anomaly"] = True
                        analysis["behavioral_anomalies"].append("off_hours_activity")
                except:
                    pass

        else:
            analysis["behavioral_anomalies"].append("unknown_user")

        return analysis

    def _analyze_network_behavior(self, event_data: Dict) -> Dict:
        """Analizar comportamiento de red"""
        source_meta = event_data.get("source_meta", {})
        ip = source_meta.get("ip", "unknown")
        host = source_meta.get("host", "unknown")

        analysis = {
            "source_ip": ip,
            "host": host,
            "is_internal_ip": self._is_internal_ip(ip),
            "geolocation_anomaly": False,
            "behavioral_anomalies": []
        }

        # Verificar patrones de red conocidos
        if host in self.baseline_patterns["network_patterns"]:
            host_baseline = self.baseline_patterns["network_patterns"][host]

            # En un sistema real, aquí se analizarían conexiones de red activas
            # Por ahora simulamos la detección
            analysis["behavioral_anomalies"].append("simulated_network_analysis")

        return analysis

    def _analyze_temporal_patterns(self, event_data: Dict) -> Dict:
        """Analizar patrones temporales"""
        timestamp = event_data.get("timestamp", "")
        analysis = {
            "timestamp": timestamp,
            "day_of_week": None,
            "hour_of_day": None,
            "is_business_hours": False,
            "temporal_anomalies": []
        }

        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                analysis["day_of_week"] = dt.strftime("%A")
                analysis["hour_of_day"] = dt.hour

                # Determinar si es horario laboral
                if dt.weekday() < 5 and 8 <= dt.hour <= 17:
                    analysis["is_business_hours"] = True

                # Detectar patrones temporales sospechosos
                if dt.weekday() >= 5:  # Fin de semana
                    analysis["temporal_anomalies"].append("weekend_activity")

                if dt.hour < 6 or dt.hour > 22:  # Horas nocturnas
                    analysis["temporal_anomalies"].append("night_time_activity")

            except Exception as e:
                analysis["temporal_anomalies"].append("invalid_timestamp")

        return analysis

    def _calculate_behavioral_score(self, context_insights: Dict) -> float:
        """Calcular score comportamental total"""
        score = 0.0

        # Pesos por categoría
        weights = {
            "process": 0.3,
            "user": 0.25,
            "network": 0.25,
            "temporal": 0.2
        }

        for category, weight in weights.items():
            if category in context_insights:
                category_score = len(context_insights[category].get("behavioral_anomalies", []))
                score += category_score * weight

        return min(score, 10.0)  # Cap at 10

    def _generate_behavioral_recommendations(self, analysis: Dict) -> List[str]:
        """Generar recomendaciones basadas en análisis comportamental"""
        recommendations = []

        behavioral_score = analysis.get("behavioral_score", 0)

        if behavioral_score >= 3.0:
            recommendations.append("Enable enhanced behavioral monitoring for this user/host combination")

        process_insights = analysis["context_insights"].get("process", {})
        if "unusual_process_location" in process_insights.get("behavioral_anomalies", []):
            recommendations.append("Investigate process execution from non-standard location")

        user_insights = analysis["context_insights"].get("user", {})
        if "off_hours_activity" in user_insights.get("behavioral_anomalies", []):
            recommendations.append("Review off-hours access policy and user authorization")

        temporal_insights = analysis["context_insights"].get("temporal", {})
        if "weekend_activity" in temporal_insights.get("temporal_anomalies", []):
            recommendations.append("Validate business justification for weekend system access")

        return recommendations

    def _is_internal_ip(self, ip: str) -> bool:
        """Verificar si la IP es interna"""
        if ip == "unknown" or ip == "<IP_REDACTED>":
            return True  # Asumimos que fue redactada por ser interna

        # Rangos RFC 1918
        internal_ranges = ["10.", "172.16.", "192.168."]
        return any(ip.startswith(range_) for range_ in internal_ranges)

def main():
    # Cargar datos del evento
    with open("../redacted_output.json", "r") as f:
        data = json.load(f)

    analyzer = BehavioralAnalyzer()

    if "findings" in data:
        for finding in data["findings"]:
            print(f"\n=== Behavioral Analysis for Event {finding.get('event_id', 'Unknown')} ===")

            behavioral_analysis = analyzer.analyze_behavioral_context(finding)

            print(f"Behavioral Score: {behavioral_analysis['behavioral_score']:.1f}/10")

            print("\nDetected Anomalies:")
            for category, insights in behavioral_analysis["context_insights"].items():
                anomalies = insights.get("behavioral_anomalies", [])
                if anomalies:
                    print(f"  {category.title()}: {', '.join(anomalies)}")

            print("\nBehavioral Recommendations:")
            for rec in behavioral_analysis["behavioral_recommendation"]:
                print(f"  • {rec}")

            # Guardar análisis
            output_file = f"../plans/behavioral_analysis_{finding.get('event_id', 'unknown')}.json"
            with open(output_file, "w") as f:
                json.dump(behavioral_analysis, f, indent=2)
            print(f"\nBehavioral analysis saved to: {output_file}")

if __name__ == "__main__":
    main()