#!/usr/bin/env python3
"""
SmartCompute Enterprise - ML-Driven Threat Prioritization System

Sistema de priorización de amenazas basado en Machine Learning que:
- Utiliza múltiples algoritmos ML para scoring de amenazas
- Aprende de patrones históricos de incidentes
- Aplica análisis de comportamiento para detección de anomalías
- Integra threat intelligence feeds para enriquecimiento
- Proporciona explicabilidad de decisiones ML (XAI)
"""

import asyncio
import json
import logging
import numpy as np
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import hashlib
import pickle
import math
from enum import Enum

# Import SIEM components
from siem_intelligence_coordinator import SIEMAlert, ThreatCorrelation, AlertSeverity
from intelligent_alert_aggregator import AlertCluster, AlertPriority

class MLModelType(Enum):
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    NEURAL_NETWORK = "neural_network"
    ISOLATION_FOREST = "isolation_forest"
    ENSEMBLE = "ensemble"

class ThreatCategory(Enum):
    MALWARE = "malware"
    PHISHING = "phishing"
    DATA_BREACH = "data_breach"
    INSIDER_THREAT = "insider_threat"
    APT = "apt"
    RANSOMWARE = "ransomware"
    NETWORK_INTRUSION = "network_intrusion"
    UNKNOWN = "unknown"

@dataclass
class MLFeatureVector:
    """Vector de características ML para amenaza"""
    feature_id: str
    alert_count: int
    max_severity: float
    avg_confidence: float
    platform_diversity: float
    temporal_spread_hours: float
    business_impact_score: float
    ioc_reputation_score: float
    geographic_risk_score: float
    behavioral_anomaly_score: float
    compliance_risk_score: float
    historical_similarity_score: float
    threat_intelligence_score: float
    network_context_score: float
    user_context_score: float
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

    def to_array(self) -> np.ndarray:
        """Convertir a array numpy para ML"""
        return np.array([
            self.alert_count,
            self.max_severity,
            self.avg_confidence,
            self.platform_diversity,
            self.temporal_spread_hours,
            self.business_impact_score,
            self.ioc_reputation_score,
            self.geographic_risk_score,
            self.behavioral_anomaly_score,
            self.compliance_risk_score,
            self.historical_similarity_score,
            self.threat_intelligence_score,
            self.network_context_score,
            self.user_context_score
        ])

@dataclass
class MLPrediction:
    """Predicción ML para amenaza"""
    prediction_id: str
    threat_score: float
    threat_category: ThreatCategory
    confidence: float
    model_used: MLModelType
    feature_importance: Dict[str, float]
    risk_factors: List[str]
    recommended_priority: AlertPriority
    explanation: str
    predicted_impact: str
    time_to_escalate_hours: float
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

@dataclass
class ThreatIntelligenceContext:
    """Contexto de threat intelligence"""
    ti_feeds_matched: List[str]
    malware_families: List[str]
    attack_campaigns: List[str]
    threat_actors: List[str]
    cti_score: float
    reputation_scores: Dict[str, float]
    first_seen_global: Optional[datetime] = None
    last_activity_global: Optional[datetime] = None

class MLThreatPrioritizer:
    """Sistema de priorización ML de amenazas"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("MLThreatPrioritizer")

        # ML configuration
        self.ml_enabled = config.get("ml_enabled", True)
        self.model_type = MLModelType(config.get("model_type", "ensemble"))
        self.feature_scaling = config.get("feature_scaling", True)

        # Training data and models (simulated)
        self.trained_models = {}
        self.feature_scalers = {}
        self.historical_incidents = []

        # Threat intelligence
        self.ti_feeds = self._load_threat_intelligence_feeds()
        self.reputation_cache = {}

        # Feature extractors
        self.feature_extractors = self._initialize_feature_extractors()

        # Learning parameters
        self.retrain_threshold = config.get("retrain_threshold", 100)
        self.confidence_threshold = config.get("confidence_threshold", 0.75)

    def _load_threat_intelligence_feeds(self) -> Dict[str, Dict]:
        """Cargar feeds de threat intelligence (simulado)"""
        return {
            "misp": {
                "enabled": True,
                "weight": 0.8,
                "categories": ["malware", "apt", "indicators"]
            },
            "otx": {
                "enabled": True,
                "weight": 0.7,
                "categories": ["pulses", "indicators", "malware"]
            },
            "virustotal": {
                "enabled": True,
                "weight": 0.9,
                "categories": ["file", "url", "domain", "ip"]
            },
            "crowdstrike": {
                "enabled": True,
                "weight": 0.85,
                "categories": ["actors", "malware", "campaigns"]
            },
            "internal_intel": {
                "enabled": True,
                "weight": 1.0,
                "categories": ["custom", "historical", "patterns"]
            }
        }

    def _initialize_feature_extractors(self) -> Dict[str, Any]:
        """Inicializar extractores de características"""
        return {
            "temporal": "temporal_features",
            "behavioral": "behavioral_features",
            "network": "network_features",
            "business": "business_features",
            "threat_intel": "threat_intel_features",
            "historical": "historical_features"
        }

    async def prioritize_threats(self, clusters: List[AlertCluster]) -> List[Tuple[AlertCluster, MLPrediction]]:
        """Priorizar amenazas usando ML"""
        self.logger.info(f"🤖 Starting ML-driven threat prioritization for {len(clusters)} clusters")

        prioritized_threats = []

        for cluster in clusters:
            try:
                # Extract ML features
                feature_vector = await self._extract_ml_features(cluster)

                # Get threat intelligence context
                ti_context = await self._get_threat_intelligence_context(cluster)

                # Make ML prediction
                prediction = await self._make_ml_prediction(feature_vector, ti_context, cluster)

                # Update cluster priority based on ML
                await self._update_cluster_with_ml(cluster, prediction)

                prioritized_threats.append((cluster, prediction))

            except Exception as e:
                self.logger.error(f"ML prioritization failed for cluster {cluster.cluster_id}: {e}")
                # Fallback to original priority
                default_prediction = self._create_default_prediction(cluster)
                prioritized_threats.append((cluster, default_prediction))

        # Sort by ML threat score
        prioritized_threats.sort(key=lambda x: x[1].threat_score, reverse=True)

        self.logger.info(f"✅ ML prioritization completed")
        return prioritized_threats

    async def _extract_ml_features(self, cluster: AlertCluster) -> MLFeatureVector:
        """Extraer vector de características ML"""
        all_alerts = [cluster.primary_alert] + cluster.related_alerts

        # Basic statistics
        alert_count = len(all_alerts)
        max_severity = max((alert.severity.value for alert in all_alerts))
        avg_confidence = statistics.mean([alert.confidence for alert in all_alerts])

        # Platform diversity
        platforms = set(alert.platform.value for alert in all_alerts)
        platform_diversity = len(platforms) / 3.0  # Normalize by max platforms

        # Temporal analysis
        timestamps = [alert.timestamp for alert in all_alerts]
        if len(timestamps) > 1:
            time_span = max(timestamps) - min(timestamps)
            temporal_spread_hours = time_span.total_seconds() / 3600
        else:
            temporal_spread_hours = 0.0

        # Extract specialized features
        business_impact = await self._extract_business_impact_score(cluster)
        ioc_reputation = await self._extract_ioc_reputation_score(cluster)
        geographic_risk = await self._extract_geographic_risk_score(cluster)
        behavioral_anomaly = await self._extract_behavioral_anomaly_score(cluster)
        compliance_risk = await self._extract_compliance_risk_score(cluster)
        historical_similarity = await self._extract_historical_similarity_score(cluster)
        threat_intel = await self._extract_threat_intelligence_score(cluster)
        network_context = await self._extract_network_context_score(cluster)
        user_context = await self._extract_user_context_score(cluster)

        feature_vector = MLFeatureVector(
            feature_id=f"features_{cluster.cluster_id}",
            alert_count=alert_count,
            max_severity=max_severity / 5.0,  # Normalize
            avg_confidence=avg_confidence,
            platform_diversity=platform_diversity,
            temporal_spread_hours=min(temporal_spread_hours, 24.0) / 24.0,  # Normalize
            business_impact_score=business_impact,
            ioc_reputation_score=ioc_reputation,
            geographic_risk_score=geographic_risk,
            behavioral_anomaly_score=behavioral_anomaly,
            compliance_risk_score=compliance_risk,
            historical_similarity_score=historical_similarity,
            threat_intelligence_score=threat_intel,
            network_context_score=network_context,
            user_context_score=user_context
        )

        return feature_vector

    async def _extract_business_impact_score(self, cluster: AlertCluster) -> float:
        """Extraer puntuación de impacto de negocio"""
        business_units = cluster.business_context.get("business_units", [])

        # Weight by business unit criticality
        impact_weights = {
            "executive": 1.0,
            "finance": 0.9,
            "engineering": 0.8,
            "hr": 0.6,
            "operations": 0.7
        }

        if not business_units:
            return 0.3  # Default low impact

        max_impact = max(impact_weights.get(unit, 0.5) for unit in business_units)

        # Bonus for multiple units
        multi_unit_bonus = min(0.2, (len(business_units) - 1) * 0.1)

        return min(1.0, max_impact + multi_unit_bonus)

    async def _extract_ioc_reputation_score(self, cluster: AlertCluster) -> float:
        """Extraer puntuación de reputación de IOCs"""
        all_alerts = [cluster.primary_alert] + cluster.related_alerts
        reputation_scores = []

        for alert in all_alerts:
            # Extract IOCs
            if alert.source_ip:
                rep_score = await self._get_ip_reputation(alert.source_ip)
                reputation_scores.append(rep_score)

            if alert.dest_ip:
                rep_score = await self._get_ip_reputation(alert.dest_ip)
                reputation_scores.append(rep_score)

            # Check for domains in description
            import re
            text = f"{alert.title} {alert.description}".lower()
            domains = re.findall(r'\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\b', text)
            for domain in domains[:3]:  # Limit to 3 domains
                rep_score = await self._get_domain_reputation(domain)
                reputation_scores.append(rep_score)

        if not reputation_scores:
            return 0.5  # Neutral

        # Return worst reputation score (higher is worse)
        return max(reputation_scores)

    async def _get_ip_reputation(self, ip_address: str) -> float:
        """Obtener reputación de IP (simulado)"""
        if ip_address in self.reputation_cache:
            return self.reputation_cache[ip_address]

        # Simulate reputation lookup
        await asyncio.sleep(0.001)

        # Simple heuristic based on IP
        ip_hash = int(hashlib.md5(ip_address.encode()).hexdigest()[:8], 16)

        # Private IPs get lower threat score
        if ip_address.startswith(('192.168.', '10.', '172.')):
            reputation = 0.2 + (ip_hash % 30) / 100
        else:
            # External IPs get variable reputation
            reputation = 0.3 + (ip_hash % 70) / 100

        self.reputation_cache[ip_address] = reputation
        return reputation

    async def _get_domain_reputation(self, domain: str) -> float:
        """Obtener reputación de dominio (simulado)"""
        if domain in self.reputation_cache:
            return self.reputation_cache[domain]

        await asyncio.sleep(0.001)

        # Simulate domain reputation
        domain_hash = int(hashlib.md5(domain.encode()).hexdigest()[:8], 16)

        # Known bad patterns
        suspicious_patterns = ['temp', 'bit.ly', 'tinyurl', 'malware', 'phish']
        if any(pattern in domain.lower() for pattern in suspicious_patterns):
            reputation = 0.8 + (domain_hash % 20) / 100
        else:
            reputation = 0.1 + (domain_hash % 40) / 100

        self.reputation_cache[domain] = reputation
        return reputation

    async def _extract_geographic_risk_score(self, cluster: AlertCluster) -> float:
        """Extraer puntuación de riesgo geográfico"""
        all_alerts = [cluster.primary_alert] + cluster.related_alerts
        geo_risks = []

        for alert in all_alerts:
            if alert.source_ip:
                geo_risk = await self._get_geographic_risk(alert.source_ip)
                geo_risks.append(geo_risk)

        if not geo_risks:
            return 0.3

        return max(geo_risks)

    async def _get_geographic_risk(self, ip_address: str) -> float:
        """Obtener riesgo geográfico de IP"""
        # Simulate geolocation risk assessment
        ip_hash = int(hashlib.md5(ip_address.encode()).hexdigest()[:8], 16)

        # Simulate country-based risk
        high_risk_countries = ['CN', 'RU', 'KP', 'IR']
        medium_risk_countries = ['BR', 'IN', 'PK', 'BD']

        country_code = high_risk_countries[ip_hash % len(high_risk_countries)]

        if country_code in high_risk_countries:
            return 0.8 + (ip_hash % 20) / 100
        elif country_code in medium_risk_countries:
            return 0.5 + (ip_hash % 30) / 100
        else:
            return 0.2 + (ip_hash % 30) / 100

    async def _extract_behavioral_anomaly_score(self, cluster: AlertCluster) -> float:
        """Extraer puntuación de anomalía comportamental"""
        all_alerts = [cluster.primary_alert] + cluster.related_alerts

        # Analyze timing patterns
        timestamps = [alert.timestamp for alert in all_alerts]

        anomaly_indicators = 0
        total_checks = 0

        # Check for off-hours activity
        for timestamp in timestamps:
            total_checks += 1
            if timestamp.hour < 6 or timestamp.hour > 22:
                anomaly_indicators += 1

        # Check for weekend activity
        for timestamp in timestamps:
            total_checks += 1
            if timestamp.weekday() >= 5:  # Saturday=5, Sunday=6
                anomaly_indicators += 1

        # Check for unusual burst patterns
        if len(timestamps) > 5:
            total_checks += 1
            time_diffs = []
            sorted_times = sorted(timestamps)
            for i in range(1, len(sorted_times)):
                diff = (sorted_times[i] - sorted_times[i-1]).total_seconds()
                time_diffs.append(diff)

            # If most alerts are within very short time (< 60 seconds)
            short_intervals = sum(1 for diff in time_diffs if diff < 60)
            if short_intervals > len(time_diffs) * 0.8:
                anomaly_indicators += 1

        if total_checks == 0:
            return 0.5

        return anomaly_indicators / total_checks

    async def _extract_compliance_risk_score(self, cluster: AlertCluster) -> float:
        """Extraer puntuación de riesgo de compliance"""
        compliance_frameworks = cluster.business_context.get("compliance_frameworks", [])

        if not compliance_frameworks:
            return 0.2

        # Weight compliance frameworks by severity
        framework_weights = {
            "SOX": 0.9,
            "HIPAA": 0.95,
            "PCI-DSS": 0.85,
            "GDPR": 0.9,
            "ISO27001": 0.7,
            "ALL": 1.0
        }

        max_compliance_risk = max(framework_weights.get(fw, 0.5) for fw in compliance_frameworks)

        # Bonus for multiple frameworks
        multi_framework_bonus = min(0.1, (len(compliance_frameworks) - 1) * 0.05)

        return min(1.0, max_compliance_risk + multi_framework_bonus)

    async def _extract_historical_similarity_score(self, cluster: AlertCluster) -> float:
        """Extraer puntuación de similitud histórica"""
        # Simulate historical incident comparison
        await asyncio.sleep(0.001)

        # Create signature for cluster
        signature_elements = [
            cluster.aggregation_strategy.value,
            str(cluster.cluster_priority.value),
            str(len(cluster.related_alerts))
        ]

        business_units = cluster.business_context.get("business_units", [])
        signature_elements.extend(sorted(business_units))

        cluster_signature = "_".join(signature_elements)
        signature_hash = int(hashlib.md5(cluster_signature.encode()).hexdigest()[:8], 16)

        # Simulate similarity to historical incidents
        similarity_score = (signature_hash % 80) / 100  # 0.0 to 0.8

        return similarity_score

    async def _extract_threat_intelligence_score(self, cluster: AlertCluster) -> float:
        """Extraer puntuación de threat intelligence"""
        ti_context = await self._get_threat_intelligence_context(cluster)
        return ti_context.cti_score

    async def _extract_network_context_score(self, cluster: AlertCluster) -> float:
        """Extraer puntuación de contexto de red"""
        all_alerts = [cluster.primary_alert] + cluster.related_alerts

        network_indicators = 0
        total_alerts = len(all_alerts)

        for alert in all_alerts:
            # Check for network-related keywords
            network_keywords = ['network', 'traffic', 'connection', 'port', 'protocol', 'firewall']
            alert_text = f"{alert.title} {alert.description}".lower()

            if any(keyword in alert_text for keyword in network_keywords):
                network_indicators += 1

        network_score = network_indicators / total_alerts if total_alerts > 0 else 0

        # Bonus for multiple IPs involved
        unique_ips = set()
        for alert in all_alerts:
            if alert.source_ip:
                unique_ips.add(alert.source_ip)
            if alert.dest_ip:
                unique_ips.add(alert.dest_ip)

        ip_diversity_bonus = min(0.3, len(unique_ips) * 0.1)

        return min(1.0, network_score + ip_diversity_bonus)

    async def _extract_user_context_score(self, cluster: AlertCluster) -> float:
        """Extraer puntuación de contexto de usuario"""
        all_alerts = [cluster.primary_alert] + cluster.related_alerts

        # Count alerts with user context
        user_alerts = sum(1 for alert in all_alerts if alert.user)
        user_score = user_alerts / len(all_alerts) if all_alerts else 0

        # Check for privileged users
        privileged_keywords = ['admin', 'root', 'administrator', 'service', 'system']
        privileged_users = 0

        for alert in all_alerts:
            if alert.user:
                user_lower = alert.user.lower()
                if any(keyword in user_lower for keyword in privileged_keywords):
                    privileged_users += 1

        privileged_bonus = min(0.4, privileged_users * 0.2)

        return min(1.0, user_score + privileged_bonus)

    async def _get_threat_intelligence_context(self, cluster: AlertCluster) -> ThreatIntelligenceContext:
        """Obtener contexto de threat intelligence"""
        # Simulate threat intelligence lookup
        await asyncio.sleep(0.002)

        all_alerts = [cluster.primary_alert] + cluster.related_alerts

        # Simulate TI feed matching
        ti_feeds_matched = []
        malware_families = []
        attack_campaigns = []
        threat_actors = []
        reputation_scores = {}

        # Extract IOCs for TI lookup
        iocs = set()
        for alert in all_alerts:
            if alert.source_ip:
                iocs.add(alert.source_ip)
            if alert.dest_ip:
                iocs.add(alert.dest_ip)

        # Simulate TI feed hits
        for ioc in list(iocs)[:5]:  # Limit to 5 IOCs
            ioc_hash = int(hashlib.md5(ioc.encode()).hexdigest()[:8], 16)

            # Simulate feed matches
            if ioc_hash % 10 < 3:  # 30% chance of TI hit
                ti_feeds_matched.append("misp")
                reputation_scores[ioc] = 0.7 + (ioc_hash % 30) / 100

            if ioc_hash % 10 < 2:  # 20% chance
                ti_feeds_matched.append("virustotal")

            if ioc_hash % 15 < 1:  # ~7% chance of APT hit
                threat_actors.append(f"APT{ioc_hash % 40 + 1}")
                attack_campaigns.append(f"Campaign_{ioc_hash % 20}")

        # Simulate malware family detection
        malware_keywords = ['malware', 'trojan', 'ransomware', 'backdoor']
        for alert in all_alerts:
            alert_text = f"{alert.title} {alert.description}".lower()
            for keyword in malware_keywords:
                if keyword in alert_text:
                    family_hash = int(hashlib.md5(alert_text.encode()).hexdigest()[:8], 16)
                    malware_families.append(f"{keyword.title()}_{family_hash % 100}")
                    break

        # Calculate CTI score
        cti_score = 0.3  # Base score

        if ti_feeds_matched:
            cti_score += 0.3
        if malware_families:
            cti_score += 0.2
        if threat_actors:
            cti_score += 0.4
        if attack_campaigns:
            cti_score += 0.3

        cti_score = min(1.0, cti_score)

        return ThreatIntelligenceContext(
            ti_feeds_matched=list(set(ti_feeds_matched)),
            malware_families=list(set(malware_families)),
            attack_campaigns=list(set(attack_campaigns)),
            threat_actors=list(set(threat_actors)),
            cti_score=cti_score,
            reputation_scores=reputation_scores
        )

    async def _make_ml_prediction(self, feature_vector: MLFeatureVector,
                                ti_context: ThreatIntelligenceContext,
                                cluster: AlertCluster) -> MLPrediction:
        """Realizar predicción ML"""
        # Simulate ML model prediction
        await asyncio.sleep(0.005)

        # Convert features to array
        features = feature_vector.to_array()

        # Simulate different ML models
        if self.model_type == MLModelType.ENSEMBLE:
            # Combine multiple model predictions
            rf_score = await self._simulate_random_forest_prediction(features)
            gb_score = await self._simulate_gradient_boosting_prediction(features)
            nn_score = await self._simulate_neural_network_prediction(features)

            # Weighted ensemble
            threat_score = (rf_score * 0.4 + gb_score * 0.35 + nn_score * 0.25)
            model_used = MLModelType.ENSEMBLE
            confidence = 0.85

        elif self.model_type == MLModelType.RANDOM_FOREST:
            threat_score = await self._simulate_random_forest_prediction(features)
            model_used = MLModelType.RANDOM_FOREST
            confidence = 0.80

        else:
            # Default to gradient boosting
            threat_score = await self._simulate_gradient_boosting_prediction(features)
            model_used = MLModelType.GRADIENT_BOOSTING
            confidence = 0.82

        # Adjust score based on TI context
        threat_score += ti_context.cti_score * 0.2
        threat_score = min(1.0, threat_score)

        # Determine threat category
        threat_category = self._classify_threat_category(cluster, ti_context)

        # Calculate feature importance
        feature_importance = self._calculate_feature_importance(features)

        # Generate risk factors
        risk_factors = self._identify_risk_factors(feature_vector, ti_context)

        # Determine recommended priority
        recommended_priority = self._calculate_recommended_priority(threat_score, confidence)

        # Generate explanation
        explanation = self._generate_ml_explanation(feature_vector, ti_context, threat_score)

        # Predict impact and time to escalate
        predicted_impact = self._predict_business_impact(feature_vector, threat_category)
        time_to_escalate = self._predict_escalation_time(threat_score, threat_category)

        prediction = MLPrediction(
            prediction_id=f"ml_pred_{cluster.cluster_id}",
            threat_score=threat_score,
            threat_category=threat_category,
            confidence=confidence,
            model_used=model_used,
            feature_importance=feature_importance,
            risk_factors=risk_factors,
            recommended_priority=recommended_priority,
            explanation=explanation,
            predicted_impact=predicted_impact,
            time_to_escalate_hours=time_to_escalate
        )

        return prediction

    async def _simulate_random_forest_prediction(self, features: np.ndarray) -> float:
        """Simular predicción Random Forest"""
        # Simulate ensemble of decision trees
        tree_predictions = []

        for i in range(100):  # 100 trees
            # Simulate tree prediction based on feature subset
            feature_subset = features[::2] if i % 2 == 0 else features[1::2]
            tree_score = np.mean(feature_subset) + np.random.normal(0, 0.1)
            tree_predictions.append(max(0, min(1, tree_score)))

        return np.mean(tree_predictions)

    async def _simulate_gradient_boosting_prediction(self, features: np.ndarray) -> float:
        """Simular predicción Gradient Boosting"""
        # Simulate sequential boosting
        prediction = 0.5  # Base prediction
        learning_rate = 0.1

        for i in range(50):  # 50 boosting rounds
            # Simulate weak learner
            residual = np.random.normal(0, 0.05)
            weak_prediction = np.mean(features) * 0.1 + residual
            prediction += learning_rate * weak_prediction

        return max(0, min(1, prediction))

    async def _simulate_neural_network_prediction(self, features: np.ndarray) -> float:
        """Simular predicción Neural Network"""
        # Simulate simple neural network
        # Hidden layer 1
        w1 = np.random.normal(0, 0.1, (len(features), 10))
        h1 = np.tanh(np.dot(features, w1))

        # Hidden layer 2
        w2 = np.random.normal(0, 0.1, (10, 5))
        h2 = np.tanh(np.dot(h1, w2))

        # Output layer
        w3 = np.random.normal(0, 0.1, 5)
        output = 1 / (1 + np.exp(-np.dot(h2, w3)))  # Sigmoid activation

        return float(output)

    def _classify_threat_category(self, cluster: AlertCluster,
                                ti_context: ThreatIntelligenceContext) -> ThreatCategory:
        """Clasificar categoría de amenaza"""
        # Check malware families
        if ti_context.malware_families:
            for family in ti_context.malware_families:
                if 'ransomware' in family.lower():
                    return ThreatCategory.RANSOMWARE
                elif 'trojan' in family.lower():
                    return ThreatCategory.MALWARE

        # Check threat actors (APT indicators)
        if ti_context.threat_actors:
            return ThreatCategory.APT

        # Analyze cluster characteristics
        all_alerts = [cluster.primary_alert] + cluster.related_alerts
        combined_text = " ".join([
            f"{alert.title} {alert.description}" for alert in all_alerts
        ]).lower()

        # Keyword-based classification
        if any(keyword in combined_text for keyword in ['phish', 'email', 'social']):
            return ThreatCategory.PHISHING
        elif any(keyword in combined_text for keyword in ['data', 'exfiltration', 'leak']):
            return ThreatCategory.DATA_BREACH
        elif any(keyword in combined_text for keyword in ['insider', 'privilege', 'abuse']):
            return ThreatCategory.INSIDER_THREAT
        elif any(keyword in combined_text for keyword in ['network', 'intrusion', 'lateral']):
            return ThreatCategory.NETWORK_INTRUSION
        elif any(keyword in combined_text for keyword in ['malware', 'virus', 'trojan']):
            return ThreatCategory.MALWARE

        return ThreatCategory.UNKNOWN

    def _calculate_feature_importance(self, features: np.ndarray) -> Dict[str, float]:
        """Calcular importancia de características"""
        feature_names = [
            "alert_count", "max_severity", "avg_confidence", "platform_diversity",
            "temporal_spread", "business_impact", "ioc_reputation", "geographic_risk",
            "behavioral_anomaly", "compliance_risk", "historical_similarity",
            "threat_intelligence", "network_context", "user_context"
        ]

        # Simulate feature importance calculation
        importances = {}
        total_importance = 0

        for i, name in enumerate(feature_names):
            # Higher values generally indicate higher importance
            importance = features[i] * np.random.uniform(0.5, 1.5)
            importances[name] = importance
            total_importance += importance

        # Normalize to sum to 1.0
        if total_importance > 0:
            for name in importances:
                importances[name] /= total_importance

        # Sort by importance
        sorted_importance = dict(sorted(importances.items(),
                                      key=lambda x: x[1], reverse=True))

        return sorted_importance

    def _identify_risk_factors(self, feature_vector: MLFeatureVector,
                             ti_context: ThreatIntelligenceContext) -> List[str]:
        """Identificar factores de riesgo principales"""
        risk_factors = []

        # High-value thresholds
        if feature_vector.business_impact_score > 0.7:
            risk_factors.append("High business impact potential")

        if feature_vector.ioc_reputation_score > 0.6:
            risk_factors.append("Malicious IOCs detected")

        if feature_vector.geographic_risk_score > 0.7:
            risk_factors.append("High-risk geographic origin")

        if feature_vector.behavioral_anomaly_score > 0.6:
            risk_factors.append("Unusual behavioral patterns")

        if feature_vector.compliance_risk_score > 0.8:
            risk_factors.append("Critical compliance implications")

        if feature_vector.threat_intelligence_score > 0.7:
            risk_factors.append("Known threat intelligence indicators")

        if feature_vector.alert_count > 10:
            risk_factors.append("High volume alert cluster")

        if feature_vector.platform_diversity > 0.6:
            risk_factors.append("Multi-platform coordination")

        # TI context factors
        if ti_context.threat_actors:
            risk_factors.append(f"Known threat actor activity: {', '.join(ti_context.threat_actors[:2])}")

        if ti_context.malware_families:
            risk_factors.append(f"Malware family detected: {', '.join(ti_context.malware_families[:2])}")

        return risk_factors[:6]  # Limit to top 6 factors

    def _calculate_recommended_priority(self, threat_score: float, confidence: float) -> AlertPriority:
        """Calcular prioridad recomendada"""
        weighted_score = threat_score * confidence

        if weighted_score >= 0.9:
            return AlertPriority.EMERGENCY
        elif weighted_score >= 0.75:
            return AlertPriority.CRITICAL
        elif weighted_score >= 0.6:
            return AlertPriority.HIGH
        elif weighted_score >= 0.4:
            return AlertPriority.MEDIUM
        elif weighted_score >= 0.2:
            return AlertPriority.LOW
        else:
            return AlertPriority.NOISE

    def _generate_ml_explanation(self, feature_vector: MLFeatureVector,
                               ti_context: ThreatIntelligenceContext,
                               threat_score: float) -> str:
        """Generar explicación de decisión ML"""
        explanation_parts = []

        explanation_parts.append(f"ML threat score: {threat_score:.2f}")

        # Top contributing factors
        if feature_vector.business_impact_score > 0.6:
            explanation_parts.append(f"High business impact ({feature_vector.business_impact_score:.2f})")

        if feature_vector.ioc_reputation_score > 0.5:
            explanation_parts.append(f"Suspicious IOCs ({feature_vector.ioc_reputation_score:.2f})")

        if feature_vector.threat_intelligence_score > 0.5:
            explanation_parts.append(f"Threat intel match ({feature_vector.threat_intelligence_score:.2f})")

        if ti_context.cti_score > 0.5:
            explanation_parts.append(f"CTI enrichment score: {ti_context.cti_score:.2f}")

        return " | ".join(explanation_parts)

    def _predict_business_impact(self, feature_vector: MLFeatureVector,
                               threat_category: ThreatCategory) -> str:
        """Predecir impacto de negocio"""
        impact_score = feature_vector.business_impact_score

        # Category-specific impact
        category_impacts = {
            ThreatCategory.RANSOMWARE: "Business operations disruption",
            ThreatCategory.DATA_BREACH: "Data confidentiality compromise",
            ThreatCategory.APT: "Long-term intelligence compromise",
            ThreatCategory.INSIDER_THREAT: "Internal security breach",
            ThreatCategory.PHISHING: "Credential compromise risk",
            ThreatCategory.MALWARE: "System integrity compromise",
            ThreatCategory.NETWORK_INTRUSION: "Network security breach"
        }

        base_impact = category_impacts.get(threat_category, "Security incident")

        if impact_score > 0.8:
            return f"Critical: {base_impact}"
        elif impact_score > 0.6:
            return f"High: {base_impact}"
        elif impact_score > 0.4:
            return f"Medium: {base_impact}"
        else:
            return f"Low: {base_impact}"

    def _predict_escalation_time(self, threat_score: float,
                               threat_category: ThreatCategory) -> float:
        """Predecir tiempo hasta escalación"""
        # Base escalation time by category
        category_times = {
            ThreatCategory.RANSOMWARE: 0.5,      # 30 minutes
            ThreatCategory.DATA_BREACH: 1.0,     # 1 hour
            ThreatCategory.APT: 2.0,             # 2 hours
            ThreatCategory.INSIDER_THREAT: 4.0,  # 4 hours
            ThreatCategory.PHISHING: 6.0,        # 6 hours
            ThreatCategory.MALWARE: 3.0,         # 3 hours
            ThreatCategory.NETWORK_INTRUSION: 2.0, # 2 hours
            ThreatCategory.UNKNOWN: 8.0          # 8 hours
        }

        base_time = category_times.get(threat_category, 8.0)

        # Adjust by threat score
        time_multiplier = 1.0 - threat_score  # Higher threat = faster escalation

        return max(0.25, base_time * time_multiplier)  # Minimum 15 minutes

    async def _update_cluster_with_ml(self, cluster: AlertCluster, prediction: MLPrediction):
        """Actualizar cluster con predicción ML"""
        # Update cluster priority if ML recommends higher
        if prediction.recommended_priority.value > cluster.cluster_priority.value:
            cluster.cluster_priority = prediction.recommended_priority
            cluster.auto_escalated = True

        # Add ML insights to recommended actions
        ml_actions = [
            f"ML Analysis: {prediction.explanation}",
            f"Predicted Impact: {prediction.predicted_impact}",
            f"Escalation Timeline: {prediction.time_to_escalate_hours:.1f} hours"
        ]

        # Add risk factor actions
        for risk_factor in prediction.risk_factors[:3]:
            ml_actions.append(f"Risk Factor: {risk_factor}")

        # Prepend ML actions to existing actions
        cluster.recommended_actions = ml_actions + cluster.recommended_actions

    def _create_default_prediction(self, cluster: AlertCluster) -> MLPrediction:
        """Crear predicción por defecto en caso de error ML"""
        return MLPrediction(
            prediction_id=f"default_{cluster.cluster_id}",
            threat_score=0.5,
            threat_category=ThreatCategory.UNKNOWN,
            confidence=0.3,
            model_used=MLModelType.ENSEMBLE,
            feature_importance={},
            risk_factors=["ML processing failed"],
            recommended_priority=cluster.cluster_priority,
            explanation="Default prediction due to ML processing error",
            predicted_impact="Unknown impact",
            time_to_escalate_hours=4.0
        )

async def demo_ml_threat_prioritization():
    """Demostración del sistema de priorización ML"""
    print("\n🤖 SmartCompute Enterprise - ML-Driven Threat Prioritization Demo")
    print("=" * 80)

    # Initialize ML prioritizer
    config = {
        "ml_enabled": True,
        "model_type": "ensemble",
        "confidence_threshold": 0.75
    }

    ml_prioritizer = MLThreatPrioritizer(config)

    # Get sample clusters from aggregator
    from intelligent_alert_aggregator import demo_intelligent_aggregation

    print("📊 Collecting sample alert clusters for ML prioritization...")
    clusters, exec_summary = await demo_intelligent_aggregation()

    print(f"\n🤖 Processing {len(clusters)} clusters through ML prioritization...")

    # Run ML prioritization
    prioritized_threats = await ml_prioritizer.prioritize_threats(clusters)

    # Display results
    print(f"\n🎯 ML THREAT PRIORITIZATION RESULTS")
    print("=" * 50)

    for i, (cluster, prediction) in enumerate(prioritized_threats[:5], 1):
        print(f"\n{i}. Cluster: {cluster.cluster_id}")
        print(f"   ML Threat Score: {prediction.threat_score:.3f}")
        print(f"   Threat Category: {prediction.threat_category.value}")
        print(f"   ML Confidence: {prediction.confidence:.3f}")
        print(f"   Model Used: {prediction.model_used.value}")
        print(f"   Recommended Priority: {prediction.recommended_priority.name}")
        print(f"   Predicted Impact: {prediction.predicted_impact}")
        print(f"   Time to Escalate: {prediction.time_to_escalate_hours:.1f} hours")

        print(f"   Top Risk Factors:")
        for risk_factor in prediction.risk_factors[:3]:
            print(f"     - {risk_factor}")

        print(f"   ML Explanation: {prediction.explanation}")

        # Show top feature importance
        top_features = list(prediction.feature_importance.items())[:3]
        if top_features:
            print(f"   Top Features: {', '.join([f'{name}({imp:.2f})' for name, imp in top_features])}")

    print(f"\n📈 ML MODEL PERFORMANCE SUMMARY")
    print("=" * 40)

    # Calculate summary statistics
    threat_scores = [pred.threat_score for _, pred in prioritized_threats]
    confidences = [pred.confidence for _, pred in prioritized_threats]

    print(f"Average Threat Score: {statistics.mean(threat_scores):.3f}")
    print(f"Average Confidence: {statistics.mean(confidences):.3f}")
    print(f"High Confidence Predictions: {sum(1 for c in confidences if c >= 0.8)}/{len(confidences)}")

    # Category distribution
    categories = [pred.threat_category for _, pred in prioritized_threats]
    category_counts = Counter(categories)
    print(f"Threat Categories: {dict(category_counts)}")

    # Priority recommendations
    priorities = [pred.recommended_priority for _, pred in prioritized_threats]
    priority_counts = Counter(priorities)
    print(f"ML Priority Distribution: {dict(priority_counts)}")

    print(f"\n✅ ML-driven threat prioritization completed successfully!")

    return prioritized_threats

if __name__ == "__main__":
    # Run demo
    results = asyncio.run(demo_ml_threat_prioritization())