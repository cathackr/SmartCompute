#!/usr/bin/env python3
"""
SmartCompute Enterprise - Advanced Threat Correlation Engine

Motor de correlación avanzado que utiliza múltiples técnicas:
- Análisis temporal de patrones
- Correlación geográfica por IP
- Análisis de TTPs (Tactics, Techniques, Procedures)
- Machine Learning para detección de anomalías
- Correlación basada en IOCs (Indicators of Compromise)
"""

import asyncio
import json
import logging
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import hashlib
import ipaddress
import re
import math

# Import SIEM components
from siem_intelligence_coordinator import SIEMAlert, ThreatCorrelation, AlertSeverity, CorrelationStatus

@dataclass
class AttackPattern:
    """Patrón de ataque identificado"""
    pattern_id: str
    name: str
    description: str
    mitre_tactics: List[str]
    mitre_techniques: List[str]
    indicators: List[str]
    confidence_threshold: float
    time_window_minutes: int

@dataclass
class IOCPattern:
    """Patrón de Indicator of Compromise"""
    ioc_type: str  # ip, domain, hash, user, etc.
    value: str
    confidence: float
    first_seen: datetime
    last_seen: datetime
    platforms: Set[str]
    related_alerts: List[str]

@dataclass
class GeographicCorrelation:
    """Correlación geográfica de amenazas"""
    source_locations: List[str]
    target_locations: List[str]
    suspicious_patterns: List[str]
    risk_score: float
    geographic_distance: float

class AdvancedThreatCorrelationEngine:
    """Motor avanzado de correlación de amenazas"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("AdvancedThreatCorrelationEngine")

        # Load attack patterns and IOC databases
        self.attack_patterns = self._load_attack_patterns()
        self.ioc_database: Dict[str, IOCPattern] = {}
        self.temporal_cache: Dict[str, List[SIEMAlert]] = defaultdict(list)

        # Machine Learning components (simulated)
        self.ml_enabled = config.get("ml_enabled", True)
        self.ml_threshold = config.get("ml_threshold", 0.7)

        # Correlation parameters
        self.max_time_window = config.get("max_time_window_hours", 24)
        self.min_correlation_confidence = config.get("min_correlation_confidence", 0.6)

    def _load_attack_patterns(self) -> Dict[str, AttackPattern]:
        """Cargar patrones de ataque basados en MITRE ATT&CK"""
        patterns = {}

        # Define common attack patterns
        pattern_definitions = [
            {
                "pattern_id": "apt_lateral_movement",
                "name": "APT Lateral Movement",
                "description": "Advanced Persistent Threat lateral movement pattern",
                "mitre_tactics": ["lateral-movement", "credential-access", "discovery"],
                "mitre_techniques": ["T1021", "T1078", "T1087", "T1135"],
                "indicators": ["multiple_hosts", "credential_access", "network_discovery"],
                "confidence_threshold": 0.8,
                "time_window_minutes": 360  # 6 hours
            },
            {
                "pattern_id": "ransomware_deployment",
                "name": "Ransomware Deployment",
                "description": "Ransomware deployment and encryption pattern",
                "mitre_tactics": ["initial-access", "execution", "impact"],
                "mitre_techniques": ["T1566", "T1204", "T1486", "T1490"],
                "indicators": ["file_encryption", "ransom_note", "process_injection"],
                "confidence_threshold": 0.9,
                "time_window_minutes": 120  # 2 hours
            },
            {
                "pattern_id": "data_exfiltration_campaign",
                "name": "Data Exfiltration Campaign",
                "description": "Multi-stage data exfiltration campaign",
                "mitre_tactics": ["collection", "exfiltration", "command-and-control"],
                "mitre_techniques": ["T1005", "T1041", "T1071", "T1567"],
                "indicators": ["data_collection", "external_communication", "large_transfers"],
                "confidence_threshold": 0.75,
                "time_window_minutes": 480  # 8 hours
            },
            {
                "pattern_id": "insider_threat_pattern",
                "name": "Insider Threat Activity",
                "description": "Malicious insider threat behavior pattern",
                "mitre_tactics": ["credential-access", "collection", "exfiltration"],
                "mitre_techniques": ["T1078", "T1005", "T1052", "T1020"],
                "indicators": ["off_hours_access", "unusual_data_access", "privilege_abuse"],
                "confidence_threshold": 0.7,
                "time_window_minutes": 720  # 12 hours
            },
            {
                "pattern_id": "supply_chain_compromise",
                "name": "Supply Chain Compromise",
                "description": "Supply chain attack pattern detection",
                "mitre_tactics": ["initial-access", "persistence", "defense-evasion"],
                "mitre_techniques": ["T1195", "T1543", "T1055", "T1027"],
                "indicators": ["software_update", "trusted_process_abuse", "code_signing"],
                "confidence_threshold": 0.85,
                "time_window_minutes": 1440  # 24 hours
            }
        ]

        for pattern_def in pattern_definitions:
            pattern = AttackPattern(**pattern_def)
            patterns[pattern.pattern_id] = pattern

        return patterns

    async def correlate_advanced_threats(self, alerts: List[SIEMAlert]) -> List[ThreatCorrelation]:
        """Motor principal de correlación avanzada"""
        self.logger.info(f"🔬 Starting advanced threat correlation for {len(alerts)} alerts")

        # Update IOC database
        await self._update_ioc_database(alerts)

        # Multiple correlation techniques
        correlation_results = []

        # 1. Temporal Pattern Analysis
        temporal_correlations = await self._correlate_temporal_patterns(alerts)
        correlation_results.extend(temporal_correlations)

        # 2. IOC-based Correlation
        ioc_correlations = await self._correlate_by_iocs(alerts)
        correlation_results.extend(ioc_correlations)

        # 3. MITRE ATT&CK Pattern Detection
        attack_pattern_correlations = await self._correlate_attack_patterns(alerts)
        correlation_results.extend(attack_pattern_correlations)

        # 4. Geographic Correlation
        geographic_correlations = await self._correlate_geographic_patterns(alerts)
        correlation_results.extend(geographic_correlations)

        # 5. Machine Learning Anomaly Detection
        if self.ml_enabled:
            ml_correlations = await self._correlate_ml_anomalies(alerts)
            correlation_results.extend(ml_correlations)

        # Merge and deduplicate correlations
        final_correlations = await self._merge_correlations(correlation_results)

        self.logger.info(f"🎯 Advanced correlation completed: {len(final_correlations)} correlations found")
        return final_correlations

    async def _update_ioc_database(self, alerts: List[SIEMAlert]):
        """Actualizar base de datos de IOCs"""
        for alert in alerts:
            # Extract IOCs from alerts
            iocs = self._extract_iocs_from_alert(alert)

            for ioc_type, value in iocs:
                ioc_key = f"{ioc_type}:{value}"

                if ioc_key in self.ioc_database:
                    # Update existing IOC
                    ioc = self.ioc_database[ioc_key]
                    ioc.last_seen = alert.timestamp
                    ioc.platforms.add(alert.platform.value)
                    ioc.related_alerts.append(alert.alert_id)
                    # Increase confidence if seen multiple times
                    ioc.confidence = min(1.0, ioc.confidence + 0.1)
                else:
                    # Create new IOC
                    ioc = IOCPattern(
                        ioc_type=ioc_type,
                        value=value,
                        confidence=0.5,
                        first_seen=alert.timestamp,
                        last_seen=alert.timestamp,
                        platforms={alert.platform.value},
                        related_alerts=[alert.alert_id]
                    )
                    self.ioc_database[ioc_key] = ioc

    def _extract_iocs_from_alert(self, alert: SIEMAlert) -> List[Tuple[str, str]]:
        """Extraer IOCs de una alerta"""
        iocs = []

        # IP addresses
        if alert.source_ip:
            iocs.append(("ip", alert.source_ip))
        if alert.dest_ip:
            iocs.append(("ip", alert.dest_ip))

        # User accounts
        if alert.user:
            iocs.append(("user", alert.user))

        # Hostnames
        if alert.host:
            iocs.append(("hostname", alert.host))

        # Extract from description and title
        text_content = f"{alert.title} {alert.description}".lower()

        # Email patterns
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text_content)
        for email in emails:
            iocs.append(("email", email))

        # Domain patterns
        domain_pattern = r'\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\b'
        domains = re.findall(domain_pattern, text_content)
        for domain in domains:
            if '.' in domain and not domain.startswith('192.168') and not domain.startswith('10.'):
                iocs.append(("domain", domain))

        # File hash patterns (MD5, SHA1, SHA256)
        hash_patterns = [
            (r'\b[a-f0-9]{32}\b', "md5"),
            (r'\b[a-f0-9]{40}\b', "sha1"),
            (r'\b[a-f0-9]{64}\b', "sha256")
        ]

        for pattern, hash_type in hash_patterns:
            hashes = re.findall(pattern, text_content)
            for hash_value in hashes:
                iocs.append((hash_type, hash_value))

        return iocs

    async def _correlate_temporal_patterns(self, alerts: List[SIEMAlert]) -> List[ThreatCorrelation]:
        """Correlación basada en patrones temporales"""
        self.logger.debug("🕐 Analyzing temporal patterns")

        correlations = []

        # Group alerts by time windows
        time_windows = {}
        window_size = timedelta(minutes=30)

        for alert in alerts:
            window_start = alert.timestamp.replace(minute=0, second=0, microsecond=0)
            # Round to nearest 30-minute window
            if alert.timestamp.minute >= 30:
                window_start = window_start.replace(minute=30)

            if window_start not in time_windows:
                time_windows[window_start] = []
            time_windows[window_start].append(alert)

        # Analyze each time window for patterns
        for window_start, window_alerts in time_windows.items():
            if len(window_alerts) < 3:  # Need at least 3 alerts for pattern
                continue

            # Check for burst patterns (many alerts in short time)
            if len(window_alerts) >= 5:
                correlation = await self._create_burst_correlation(window_alerts, window_start)
                if correlation:
                    correlations.append(correlation)

            # Check for escalation patterns (severity increasing over time)
            escalation_correlation = await self._detect_escalation_pattern(window_alerts, window_start)
            if escalation_correlation:
                correlations.append(escalation_correlation)

        return correlations

    async def _create_burst_correlation(self, alerts: List[SIEMAlert], window_start: datetime) -> Optional[ThreatCorrelation]:
        """Crear correlación para ráfaga de alertas"""
        if len(alerts) < 5:
            return None

        # Calculate burst characteristics
        platforms = set(alert.platform for alert in alerts)
        avg_severity = statistics.mean([alert.severity.value for alert in alerts])
        unique_sources = set(alert.source_ip for alert in alerts if alert.source_ip)

        # Higher threat score for multi-platform bursts
        threat_score = 60 + (len(platforms) * 10) + (len(alerts) * 2)
        threat_score = min(100, threat_score)

        correlation = ThreatCorrelation(
            correlation_id=f"temporal_burst_{int(window_start.timestamp())}",
            alerts=alerts,
            threat_score=threat_score,
            threat_category="temporal_burst",
            attack_pattern="alert_flooding",
            business_impact="medium" if threat_score < 80 else "high",
            confidence=0.7,
            recommended_actions=[
                f"Investigate {len(alerts)} alerts in 30-minute window",
                "Check for coordinated attack or system malfunction",
                "Analyze common elements across burst alerts"
            ]
        )

        return correlation

    async def _detect_escalation_pattern(self, alerts: List[SIEMAlert], window_start: datetime) -> Optional[ThreatCorrelation]:
        """Detectar patrón de escalación de amenazas"""
        if len(alerts) < 3:
            return None

        # Sort alerts by timestamp
        sorted_alerts = sorted(alerts, key=lambda a: a.timestamp)

        # Check if severity is generally increasing
        severities = [alert.severity.value for alert in sorted_alerts]

        # Calculate if there's an escalation trend
        is_escalating = True
        for i in range(1, len(severities)):
            if severities[i] < severities[i-1]:
                is_escalating = False
                break

        if not is_escalating:
            return None

        # Check if escalation is significant
        severity_increase = severities[-1] - severities[0]
        if severity_increase < 2:  # Need at least 2-level increase
            return None

        threat_score = 70 + (severity_increase * 10)

        correlation = ThreatCorrelation(
            correlation_id=f"escalation_{int(window_start.timestamp())}",
            alerts=sorted_alerts,
            threat_score=min(100, threat_score),
            threat_category="threat_escalation",
            attack_pattern="severity_escalation",
            business_impact="high",
            confidence=0.75,
            recommended_actions=[
                "Immediate investigation of escalating threat",
                "Check if attack is progressing through stages",
                "Implement emergency response procedures"
            ]
        )

        return correlation

    async def _correlate_by_iocs(self, alerts: List[SIEMAlert]) -> List[ThreatCorrelation]:
        """Correlación basada en IOCs compartidos"""
        self.logger.debug("🔍 Analyzing IOC-based correlations")

        correlations = []
        ioc_alert_groups = defaultdict(list)

        # Group alerts by shared IOCs
        for alert in alerts:
            alert_iocs = self._extract_iocs_from_alert(alert)
            for ioc_type, value in alert_iocs:
                ioc_key = f"{ioc_type}:{value}"
                ioc_alert_groups[ioc_key].append(alert)

        # Create correlations for IOCs with multiple alerts
        for ioc_key, ioc_alerts in ioc_alert_groups.items():
            if len(ioc_alerts) < 2:
                continue

            ioc_type, ioc_value = ioc_key.split(":", 1)

            # Calculate threat score based on IOC type and frequency
            base_score = self._calculate_ioc_threat_score(ioc_type, ioc_value, len(ioc_alerts))

            # Check if IOC is known malicious
            if ioc_key in self.ioc_database:
                ioc_pattern = self.ioc_database[ioc_key]
                base_score += (ioc_pattern.confidence * 30)

            correlation = ThreatCorrelation(
                correlation_id=f"ioc_{hashlib.md5(ioc_key.encode()).hexdigest()[:8]}",
                alerts=ioc_alerts,
                threat_score=min(100, base_score),
                threat_category="ioc_correlation",
                attack_pattern=f"shared_{ioc_type}",
                business_impact="medium",
                confidence=0.8,
                recommended_actions=[
                    f"Investigate shared {ioc_type}: {ioc_value}",
                    f"Block {ioc_type} if confirmed malicious",
                    "Check for additional IOCs in same campaign"
                ]
            )

            correlations.append(correlation)

        return correlations

    def _calculate_ioc_threat_score(self, ioc_type: str, ioc_value: str, frequency: int) -> float:
        """Calcular puntuación de amenaza para IOC"""
        base_scores = {
            "ip": 40,
            "domain": 35,
            "email": 30,
            "user": 45,
            "hostname": 25,
            "md5": 60,
            "sha1": 60,
            "sha256": 60
        }

        base_score = base_scores.get(ioc_type, 30)

        # Frequency bonus
        frequency_bonus = min(30, frequency * 5)

        # IP-specific analysis
        if ioc_type == "ip":
            try:
                ip = ipaddress.ip_address(ioc_value)
                if ip.is_private:
                    base_score -= 20  # Private IPs less threatening externally
                elif ip.is_reserved:
                    base_score -= 10
            except:
                pass

        return base_score + frequency_bonus

    async def _correlate_attack_patterns(self, alerts: List[SIEMAlert]) -> List[ThreatCorrelation]:
        """Correlación basada en patrones de ataque MITRE ATT&CK"""
        self.logger.debug("⚔️ Analyzing MITRE ATT&CK patterns")

        correlations = []

        for pattern_id, attack_pattern in self.attack_patterns.items():
            pattern_alerts = await self._match_attack_pattern(alerts, attack_pattern)

            if len(pattern_alerts) >= 2:  # Need at least 2 alerts for pattern
                # Calculate confidence based on pattern matching
                confidence = self._calculate_pattern_confidence(pattern_alerts, attack_pattern)

                if confidence >= attack_pattern.confidence_threshold:
                    threat_score = 80 + (len(pattern_alerts) * 5)

                    correlation = ThreatCorrelation(
                        correlation_id=f"mitre_{pattern_id}_{int(datetime.now().timestamp())}",
                        alerts=pattern_alerts,
                        threat_score=min(100, threat_score),
                        threat_category="mitre_attack_pattern",
                        attack_pattern=pattern_id,
                        business_impact="high",
                        confidence=confidence,
                        recommended_actions=[
                            f"MITRE ATT&CK pattern detected: {attack_pattern.name}",
                            f"Tactics: {', '.join(attack_pattern.mitre_tactics)}",
                            f"Techniques: {', '.join(attack_pattern.mitre_techniques)}",
                            "Implement MITRE-based response procedures"
                        ]
                    )

                    correlations.append(correlation)

        return correlations

    async def _match_attack_pattern(self, alerts: List[SIEMAlert], pattern: AttackPattern) -> List[SIEMAlert]:
        """Encontrar alertas que coinciden con patrón de ataque"""
        matching_alerts = []

        # Filter alerts within time window
        if alerts:
            latest_time = max(alert.timestamp for alert in alerts)
            time_threshold = latest_time - timedelta(minutes=pattern.time_window_minutes)

            for alert in alerts:
                if alert.timestamp >= time_threshold:
                    # Check if alert matches pattern indicators
                    if self._alert_matches_pattern(alert, pattern):
                        matching_alerts.append(alert)

        return matching_alerts

    def _alert_matches_pattern(self, alert: SIEMAlert, pattern: AttackPattern) -> bool:
        """Verificar si alerta coincide con patrón"""
        alert_text = f"{alert.title} {alert.description} {' '.join(alert.tags)}".lower()

        # Check for pattern indicators in alert text
        matches = 0
        for indicator in pattern.indicators:
            if indicator.lower() in alert_text:
                matches += 1

        # Require at least 30% of indicators to match
        return matches >= (len(pattern.indicators) * 0.3)

    def _calculate_pattern_confidence(self, alerts: List[SIEMAlert], pattern: AttackPattern) -> float:
        """Calcular confianza de coincidencia de patrón"""
        total_indicators = len(pattern.indicators)
        if total_indicators == 0:
            return 0.0

        matched_indicators = set()

        for alert in alerts:
            alert_text = f"{alert.title} {alert.description} {' '.join(alert.tags)}".lower()
            for indicator in pattern.indicators:
                if indicator.lower() in alert_text:
                    matched_indicators.add(indicator)

        base_confidence = len(matched_indicators) / total_indicators

        # Bonus for multiple alerts
        alert_bonus = min(0.2, (len(alerts) - 1) * 0.05)

        # Bonus for multiple platforms
        platforms = set(alert.platform for alert in alerts)
        platform_bonus = min(0.1, (len(platforms) - 1) * 0.05)

        return min(1.0, base_confidence + alert_bonus + platform_bonus)

    async def _correlate_geographic_patterns(self, alerts: List[SIEMAlert]) -> List[ThreatCorrelation]:
        """Correlación basada en patrones geográficos"""
        self.logger.debug("🌍 Analyzing geographic patterns")

        correlations = []

        # Group alerts by source IP geolocation (simulated)
        geo_groups = defaultdict(list)

        for alert in alerts:
            if alert.source_ip:
                # Simulate geolocation lookup
                geo_info = await self._get_ip_geolocation(alert.source_ip)
                if geo_info:
                    geo_key = f"{geo_info['country']}_{geo_info['region']}"
                    geo_groups[geo_key].append(alert)

        # Analyze geographic patterns
        for geo_key, geo_alerts in geo_groups.items():
            if len(geo_alerts) < 3:
                continue

            # Check for suspicious geographic patterns
            correlation = await self._analyze_geographic_correlation(geo_key, geo_alerts)
            if correlation:
                correlations.append(correlation)

        return correlations

    async def _get_ip_geolocation(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """Obtener geolocalización de IP (simulado)"""
        # Simulate geolocation lookup
        await asyncio.sleep(0.001)

        try:
            ip = ipaddress.ip_address(ip_address)
            if ip.is_private:
                return {
                    "country": "Private",
                    "region": "Internal",
                    "city": "LocalNetwork",
                    "latitude": 0.0,
                    "longitude": 0.0
                }
        except:
            pass

        # Simulate external IP geolocation
        hash_val = int(hashlib.md5(ip_address.encode()).hexdigest()[:8], 16)
        countries = ["US", "CN", "RU", "DE", "GB", "FR", "CA", "JP"]
        country = countries[hash_val % len(countries)]

        return {
            "country": country,
            "region": f"Region_{hash_val % 10}",
            "city": f"City_{hash_val % 100}",
            "latitude": (hash_val % 180) - 90,
            "longitude": (hash_val % 360) - 180
        }

    async def _analyze_geographic_correlation(self, geo_key: str, alerts: List[SIEMAlert]) -> Optional[ThreatCorrelation]:
        """Analizar correlación geográfica"""
        country, region = geo_key.split("_", 1)

        # Check for suspicious patterns
        suspicious_countries = ["CN", "RU", "KP", "IR"]
        is_suspicious_location = country in suspicious_countries

        # Calculate geographic threat score
        base_score = 50
        if is_suspicious_location:
            base_score += 30

        # Frequency bonus
        frequency_bonus = min(20, len(alerts) * 3)
        threat_score = base_score + frequency_bonus

        # Check for coordinated timing
        time_span = max(alert.timestamp for alert in alerts) - min(alert.timestamp for alert in alerts)
        if time_span.total_seconds() < 3600:  # Within 1 hour
            threat_score += 15

        if threat_score < 70:  # Only create correlation if significant
            return None

        correlation = ThreatCorrelation(
            correlation_id=f"geo_{geo_key}_{int(datetime.now().timestamp())}",
            alerts=alerts,
            threat_score=min(100, threat_score),
            threat_category="geographic_correlation",
            attack_pattern="geo_coordinated",
            business_impact="medium",
            confidence=0.6,
            recommended_actions=[
                f"Investigate {len(alerts)} alerts from {country}/{region}",
                f"Consider geo-blocking {country} if confirmed malicious",
                "Analyze attack coordination from geographic region"
            ]
        )

        return correlation

    async def _correlate_ml_anomalies(self, alerts: List[SIEMAlert]) -> List[ThreatCorrelation]:
        """Correlación usando detección de anomalías ML (simulado)"""
        self.logger.debug("🤖 Analyzing ML-based anomalies")

        correlations = []

        # Simulate ML anomaly detection
        ml_features = await self._extract_ml_features(alerts)
        anomalies = await self._detect_ml_anomalies(ml_features)

        for anomaly in anomalies:
            if anomaly["confidence"] >= self.ml_threshold:
                anomaly_alerts = [alerts[i] for i in anomaly["alert_indices"]]

                correlation = ThreatCorrelation(
                    correlation_id=f"ml_anomaly_{anomaly['anomaly_id']}",
                    alerts=anomaly_alerts,
                    threat_score=anomaly["threat_score"],
                    threat_category="ml_anomaly",
                    attack_pattern=anomaly["pattern_type"],
                    business_impact="medium",
                    confidence=anomaly["confidence"],
                    recommended_actions=[
                        f"ML-detected anomaly: {anomaly['description']}",
                        "Investigate alerts flagged by ML algorithm",
                        "Validate ML findings with manual analysis"
                    ]
                )

                correlations.append(correlation)

        return correlations

    async def _extract_ml_features(self, alerts: List[SIEMAlert]) -> List[Dict[str, Any]]:
        """Extraer características para ML"""
        features = []

        for i, alert in enumerate(alerts):
            feature_vector = {
                "alert_index": i,
                "severity": alert.severity.value,
                "platform": hash(alert.platform.value) % 100,
                "hour": alert.timestamp.hour,
                "day_of_week": alert.timestamp.weekday(),
                "title_length": len(alert.title),
                "description_length": len(alert.description),
                "has_source_ip": 1 if alert.source_ip else 0,
                "has_dest_ip": 1 if alert.dest_ip else 0,
                "has_user": 1 if alert.user else 0,
                "tag_count": len(alert.tags),
                "confidence": alert.confidence
            }
            features.append(feature_vector)

        return features

    async def _detect_ml_anomalies(self, features: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detectar anomalías usando ML simulado"""
        anomalies = []

        # Simulate ML anomaly detection algorithm
        for i, feature in enumerate(features):
            # Calculate anomaly score based on feature deviations
            anomaly_score = 0.0

            # Check for unusual timing
            if feature["hour"] < 6 or feature["hour"] > 22:  # Off hours
                anomaly_score += 0.3

            # Check for high severity
            if feature["severity"] >= 4:
                anomaly_score += 0.4

            # Check for unusual length patterns
            if feature["title_length"] > 100 or feature["description_length"] > 500:
                anomaly_score += 0.2

            # Check for weekend activity
            if feature["day_of_week"] >= 5:  # Weekend
                anomaly_score += 0.1

            # Random component to simulate ML uncertainty
            import random
            random.seed(i)  # Deterministic for testing
            anomaly_score += random.uniform(-0.2, 0.2)

            if anomaly_score >= 0.7:  # Threshold for anomaly
                anomaly = {
                    "anomaly_id": f"ml_anom_{i:03d}",
                    "alert_indices": [i],
                    "confidence": min(1.0, anomaly_score),
                    "threat_score": min(100, anomaly_score * 120),
                    "pattern_type": "behavioral_anomaly",
                    "description": f"ML-detected anomaly in alert pattern (score: {anomaly_score:.2f})"
                }
                anomalies.append(anomaly)

        return anomalies

    async def _merge_correlations(self, correlations: List[ThreatCorrelation]) -> List[ThreatCorrelation]:
        """Fusionar y deduplicar correlaciones"""
        if not correlations:
            return []

        # Group correlations by overlapping alerts
        merged_groups = []

        for correlation in correlations:
            merged = False
            correlation_alert_ids = set(alert.alert_id for alert in correlation.alerts)

            for group in merged_groups:
                group_alert_ids = set()
                for group_correlation in group:
                    group_alert_ids.update(alert.alert_id for alert in group_correlation.alerts)

                # Check for overlap
                overlap = len(correlation_alert_ids & group_alert_ids)
                if overlap > 0:
                    group.append(correlation)
                    merged = True
                    break

            if not merged:
                merged_groups.append([correlation])

        # Create final merged correlations
        final_correlations = []

        for group in merged_groups:
            if len(group) == 1:
                final_correlations.append(group[0])
            else:
                # Merge multiple correlations into one
                merged_correlation = await self._merge_correlation_group(group)
                final_correlations.append(merged_correlation)

        # Sort by threat score
        final_correlations.sort(key=lambda c: c.threat_score * c.confidence, reverse=True)

        return final_correlations

    async def _merge_correlation_group(self, correlations: List[ThreatCorrelation]) -> ThreatCorrelation:
        """Fusionar grupo de correlaciones"""
        # Combine all alerts
        all_alerts = []
        seen_alert_ids = set()

        for correlation in correlations:
            for alert in correlation.alerts:
                if alert.alert_id not in seen_alert_ids:
                    all_alerts.append(alert)
                    seen_alert_ids.add(alert.alert_id)

        # Calculate merged threat score
        max_threat_score = max(c.threat_score for c in correlations)
        avg_confidence = statistics.mean([c.confidence for c in correlations])

        # Combine categories and patterns
        categories = [c.threat_category for c in correlations]
        patterns = [c.attack_pattern for c in correlations if c.attack_pattern]

        # Combine recommended actions
        all_actions = []
        for correlation in correlations:
            all_actions.extend(correlation.recommended_actions)
        unique_actions = list(dict.fromkeys(all_actions))  # Remove duplicates

        merged_correlation = ThreatCorrelation(
            correlation_id=f"merged_{int(datetime.now().timestamp())}_{len(correlations)}",
            alerts=all_alerts,
            threat_score=min(100, max_threat_score + 10),  # Bonus for multiple correlations
            threat_category="multi_correlation",
            attack_pattern=f"combined_{'+'.join(patterns[:3])}",
            business_impact="high",
            confidence=min(1.0, avg_confidence + 0.1),
            recommended_actions=unique_actions[:10],  # Limit to 10 actions
            status=CorrelationStatus.CORRELATED
        )

        return merged_correlation

async def demo_advanced_correlation():
    """Demostración del motor de correlación avanzado"""
    print("\n🔬 SmartCompute Enterprise - Advanced Threat Correlation Demo")
    print("=" * 70)

    # Initialize correlation engine
    config = {
        "ml_enabled": True,
        "ml_threshold": 0.7,
        "max_time_window_hours": 24,
        "min_correlation_confidence": 0.6
    }

    correlation_engine = AdvancedThreatCorrelationEngine(config)

    # Import and use sample alerts from SIEM coordinator
    from siem_intelligence_coordinator import demo_siem_intelligence_coordination

    print("📡 Collecting sample SIEM alerts...")
    sample_correlations = await demo_siem_intelligence_coordination()

    # Extract all alerts from correlations
    all_alerts = []
    for correlation in sample_correlations:
        all_alerts.extend(correlation.alerts)

    print(f"\n🔍 Running advanced correlation on {len(all_alerts)} alerts...")

    # Run advanced correlation
    advanced_correlations = await correlation_engine.correlate_advanced_threats(all_alerts)

    # Display results
    print(f"\n🎯 ADVANCED CORRELATION RESULTS")
    print("=" * 45)

    for i, correlation in enumerate(advanced_correlations, 1):
        print(f"\n{i}. Advanced Correlation: {correlation.correlation_id}")
        print(f"   Category: {correlation.threat_category}")
        print(f"   Attack Pattern: {correlation.attack_pattern}")
        print(f"   Threat Score: {correlation.threat_score:.1f}")
        print(f"   Confidence: {correlation.confidence:.3f}")
        print(f"   Business Impact: {correlation.business_impact}")
        print(f"   Alerts: {len(correlation.alerts)}")
        print(f"   Platforms: {', '.join(set(alert.platform.value for alert in correlation.alerts))}")

        if correlation.recommended_actions:
            print("   Advanced Actions:")
            for action in correlation.recommended_actions[:3]:  # Show first 3
                print(f"     - {action}")

    print(f"\n✅ Advanced threat correlation completed!")
    print(f"📊 Summary: {len(advanced_correlations)} advanced correlations generated")

    return advanced_correlations

if __name__ == "__main__":
    # Run demo
    results = asyncio.run(demo_advanced_correlation())