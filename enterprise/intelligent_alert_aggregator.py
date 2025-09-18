#!/usr/bin/env python3
"""
SmartCompute Enterprise - Intelligent Alert Aggregation System

Sistema inteligente de agregación de alertas que:
- Deduplica alertas similares usando técnicas de ML
- Agrupa alertas relacionadas por contexto de negocio
- Aplica filtros de ruido inteligentes
- Crea resúmenes ejecutivos de amenazas
- Gestiona escalación automática basada en umbrales
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
import difflib
import re
from enum import Enum

# Import SIEM components
from siem_intelligence_coordinator import SIEMAlert, ThreatCorrelation, AlertSeverity
from threat_correlation_engine import AdvancedThreatCorrelationEngine

class AggregationStrategy(Enum):
    SIMILARITY = "similarity"
    BUSINESS_CONTEXT = "business_context"
    TEMPORAL = "temporal"
    IOC_BASED = "ioc_based"
    NOISE_REDUCTION = "noise_reduction"

class AlertPriority(Enum):
    NOISE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5

@dataclass
class AlertCluster:
    """Cluster de alertas relacionadas"""
    cluster_id: str
    primary_alert: SIEMAlert
    related_alerts: List[SIEMAlert]
    aggregation_strategy: AggregationStrategy
    similarity_score: float
    cluster_priority: AlertPriority
    business_context: Dict[str, Any]
    summary: str
    recommended_actions: List[str]
    auto_escalated: bool = False
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

@dataclass
class NoiseFilter:
    """Filtro de ruido para alertas"""
    filter_name: str
    description: str
    patterns: List[str]
    platforms: List[str]
    time_window_minutes: int
    max_frequency: int
    enabled: bool = True

@dataclass
class ExecutiveSummary:
    """Resumen ejecutivo de amenazas"""
    summary_id: str
    time_period: str
    total_alerts: int
    critical_threats: int
    clusters_created: int
    noise_filtered: int
    top_threats: List[str]
    business_impact_summary: str
    recommended_executive_actions: List[str]
    compliance_alerts: int
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

class IntelligentAlertAggregator:
    """Sistema inteligente de agregación de alertas"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("IntelligentAlertAggregator")

        # Aggregation parameters
        self.similarity_threshold = config.get("similarity_threshold", 0.8)
        self.temporal_window_minutes = config.get("temporal_window_minutes", 60)
        self.max_cluster_size = config.get("max_cluster_size", 50)

        # Business context mapping
        self.business_units = config.get("business_units", {
            "finance": {"criticality": "high", "compliance": ["SOX", "PCI-DSS"]},
            "hr": {"criticality": "medium", "compliance": ["GDPR", "HIPAA"]},
            "engineering": {"criticality": "high", "compliance": ["IP_PROTECTION"]},
            "executive": {"criticality": "critical", "compliance": ["ALL"]},
            "operations": {"criticality": "medium", "compliance": ["ISO27001"]}
        })

        # Load noise filters
        self.noise_filters = self._load_noise_filters()

        # Clustering state
        self.active_clusters: Dict[str, AlertCluster] = {}
        self.noise_statistics = defaultdict(int)

    def _load_noise_filters(self) -> List[NoiseFilter]:
        """Cargar filtros de ruido predefinidos"""
        filters = [
            NoiseFilter(
                filter_name="failed_login_noise",
                description="Filter excessive failed login attempts from same source",
                patterns=["failed login", "authentication failed", "invalid credentials"],
                platforms=["splunk", "qradar", "elastic"],
                time_window_minutes=15,
                max_frequency=10
            ),
            NoiseFilter(
                filter_name="network_scan_noise",
                description="Filter repetitive network scanning alerts",
                patterns=["port scan", "network scan", "reconnaissance"],
                platforms=["qradar", "elastic"],
                time_window_minutes=30,
                max_frequency=20
            ),
            NoiseFilter(
                filter_name="automated_tool_noise",
                description="Filter alerts from legitimate security tools",
                patterns=["security scanner", "vulnerability assessment", "nessus", "qualys"],
                platforms=["splunk", "qradar", "elastic"],
                time_window_minutes=60,
                max_frequency=50
            ),
            NoiseFilter(
                filter_name="system_maintenance_noise",
                description="Filter maintenance-related alerts",
                patterns=["maintenance", "backup", "system update", "scheduled task"],
                platforms=["splunk", "elastic"],
                time_window_minutes=120,
                max_frequency=30
            ),
            NoiseFilter(
                filter_name="dns_query_noise",
                description="Filter excessive DNS query alerts",
                patterns=["dns query", "domain lookup", "nxdomain"],
                platforms=["qradar", "umbrella"],
                time_window_minutes=10,
                max_frequency=100
            )
        ]

        return filters

    async def aggregate_alerts(self, alerts: List[SIEMAlert]) -> Tuple[List[AlertCluster], List[SIEMAlert]]:
        """Agregar alertas usando múltiples estrategias"""
        self.logger.info(f"🔄 Starting intelligent alert aggregation for {len(alerts)} alerts")

        # Step 1: Apply noise filters
        filtered_alerts, noise_alerts = await self._apply_noise_filters(alerts)
        self.logger.info(f"📊 Noise filtering: {len(filtered_alerts)} kept, {len(noise_alerts)} filtered")

        # Step 2: Create clusters using different strategies
        clusters = []

        # Similarity-based clustering
        similarity_clusters = await self._cluster_by_similarity(filtered_alerts)
        clusters.extend(similarity_clusters)

        # Business context clustering
        business_clusters = await self._cluster_by_business_context(filtered_alerts)
        clusters.extend(business_clusters)

        # Temporal clustering
        temporal_clusters = await self._cluster_by_temporal_patterns(filtered_alerts)
        clusters.extend(temporal_clusters)

        # IOC-based clustering
        ioc_clusters = await self._cluster_by_iocs(filtered_alerts)
        clusters.extend(ioc_clusters)

        # Step 3: Merge overlapping clusters
        final_clusters = await self._merge_overlapping_clusters(clusters)

        # Step 4: Prioritize clusters
        prioritized_clusters = await self._prioritize_clusters(final_clusters)

        # Step 5: Apply auto-escalation rules
        escalated_clusters = await self._apply_auto_escalation(prioritized_clusters)

        self.logger.info(f"✅ Aggregation completed: {len(escalated_clusters)} clusters created")

        return escalated_clusters, noise_alerts

    async def _apply_noise_filters(self, alerts: List[SIEMAlert]) -> Tuple[List[SIEMAlert], List[SIEMAlert]]:
        """Aplicar filtros de ruido"""
        kept_alerts = []
        noise_alerts = []

        # Group alerts by filter patterns for frequency analysis
        pattern_groups = defaultdict(list)

        for alert in alerts:
            alert_text = f"{alert.title} {alert.description}".lower()
            matched_filter = None

            for noise_filter in self.noise_filters:
                if not noise_filter.enabled:
                    continue

                # Check if alert matches filter patterns
                for pattern in noise_filter.patterns:
                    if pattern.lower() in alert_text:
                        # Check if platform matches
                        if alert.platform.value in noise_filter.platforms:
                            matched_filter = noise_filter
                            break
                if matched_filter:
                    break

            if matched_filter:
                filter_key = f"{matched_filter.filter_name}_{alert.platform.value}"
                pattern_groups[filter_key].append((alert, matched_filter))
            else:
                kept_alerts.append(alert)

        # Apply frequency-based filtering
        for filter_key, alert_filter_pairs in pattern_groups.items():
            if not alert_filter_pairs:
                continue

            alerts_in_group = [pair[0] for pair in alert_filter_pairs]
            filter_config = alert_filter_pairs[0][1]

            # Sort by timestamp
            alerts_in_group.sort(key=lambda a: a.timestamp)

            # Apply time window filtering
            current_window_alerts = []

            for alert in alerts_in_group:
                # Remove old alerts from current window
                window_start = alert.timestamp - timedelta(minutes=filter_config.time_window_minutes)
                current_window_alerts = [
                    a for a in current_window_alerts
                    if a.timestamp >= window_start
                ]

                current_window_alerts.append(alert)

                # Check if frequency exceeds threshold
                if len(current_window_alerts) <= filter_config.max_frequency:
                    kept_alerts.append(alert)
                else:
                    noise_alerts.append(alert)
                    self.noise_statistics[filter_config.filter_name] += 1

        return kept_alerts, noise_alerts

    async def _cluster_by_similarity(self, alerts: List[SIEMAlert]) -> List[AlertCluster]:
        """Clusterizar alertas por similitud usando ML"""
        self.logger.debug("🔍 Clustering by similarity")

        clusters = []
        processed_alerts = set()

        for i, alert in enumerate(alerts):
            if alert.alert_id in processed_alerts:
                continue

            similar_alerts = []

            for j, other_alert in enumerate(alerts[i+1:], i+1):
                if other_alert.alert_id in processed_alerts:
                    continue

                similarity = await self._calculate_alert_similarity(alert, other_alert)

                if similarity >= self.similarity_threshold:
                    similar_alerts.append(other_alert)
                    processed_alerts.add(other_alert.alert_id)

            if similar_alerts:
                # Create cluster with primary alert and similar alerts
                cluster = AlertCluster(
                    cluster_id=f"similarity_{hashlib.md5(alert.alert_id.encode()).hexdigest()[:8]}",
                    primary_alert=alert,
                    related_alerts=similar_alerts,
                    aggregation_strategy=AggregationStrategy.SIMILARITY,
                    similarity_score=statistics.mean([
                        await self._calculate_alert_similarity(alert, sa) for sa in similar_alerts
                    ]),
                    cluster_priority=self._determine_cluster_priority([alert] + similar_alerts),
                    business_context=await self._extract_business_context([alert] + similar_alerts),
                    summary=await self._generate_cluster_summary([alert] + similar_alerts),
                    recommended_actions=await self._generate_cluster_actions([alert] + similar_alerts)
                )
                clusters.append(cluster)
                processed_alerts.add(alert.alert_id)

        return clusters

    async def _calculate_alert_similarity(self, alert1: SIEMAlert, alert2: SIEMAlert) -> float:
        """Calcular similitud entre dos alertas"""
        similarities = []

        # Title similarity
        title_similarity = difflib.SequenceMatcher(None, alert1.title, alert2.title).ratio()
        similarities.append(title_similarity * 0.3)

        # Description similarity
        desc_similarity = difflib.SequenceMatcher(None, alert1.description, alert2.description).ratio()
        similarities.append(desc_similarity * 0.2)

        # Rule name similarity
        if alert1.rule_name and alert2.rule_name:
            rule_similarity = difflib.SequenceMatcher(None, alert1.rule_name, alert2.rule_name).ratio()
            similarities.append(rule_similarity * 0.25)

        # Platform similarity
        platform_similarity = 1.0 if alert1.platform == alert2.platform else 0.0
        similarities.append(platform_similarity * 0.1)

        # Severity similarity
        severity_diff = abs(alert1.severity.value - alert2.severity.value)
        severity_similarity = max(0, 1 - (severity_diff / 4))  # Max diff is 4
        similarities.append(severity_similarity * 0.1)

        # Tag similarity
        if alert1.tags and alert2.tags:
            common_tags = set(alert1.tags) & set(alert2.tags)
            all_tags = set(alert1.tags) | set(alert2.tags)
            tag_similarity = len(common_tags) / len(all_tags) if all_tags else 0
            similarities.append(tag_similarity * 0.05)

        return sum(similarities)

    async def _cluster_by_business_context(self, alerts: List[SIEMAlert]) -> List[AlertCluster]:
        """Clusterizar alertas por contexto de negocio"""
        self.logger.debug("🏢 Clustering by business context")

        clusters = []

        # Group alerts by business unit (extracted from various fields)
        business_groups = defaultdict(list)

        for alert in alerts:
            business_unit = await self._extract_business_unit(alert)
            if business_unit:
                business_groups[business_unit].append(alert)

        # Create clusters for each business unit if significant
        for business_unit, unit_alerts in business_groups.items():
            if len(unit_alerts) >= 3:  # Minimum alerts for business cluster

                # Sort by severity and timestamp
                unit_alerts.sort(key=lambda a: (a.severity.value, a.timestamp), reverse=True)

                primary_alert = unit_alerts[0]
                related_alerts = unit_alerts[1:]

                cluster = AlertCluster(
                    cluster_id=f"business_{business_unit}_{int(datetime.now().timestamp())}",
                    primary_alert=primary_alert,
                    related_alerts=related_alerts,
                    aggregation_strategy=AggregationStrategy.BUSINESS_CONTEXT,
                    similarity_score=0.8,  # High for business context
                    cluster_priority=self._determine_cluster_priority(unit_alerts),
                    business_context={
                        "business_unit": business_unit,
                        "unit_config": self.business_units.get(business_unit, {}),
                        "alert_count": len(unit_alerts)
                    },
                    summary=f"Business unit alert cluster: {business_unit} ({len(unit_alerts)} alerts)",
                    recommended_actions=[
                        f"Notify {business_unit} security team",
                        f"Assess business impact on {business_unit} operations",
                        "Coordinate with business unit leadership"
                    ]
                )
                clusters.append(cluster)

        return clusters

    async def _extract_business_unit(self, alert: SIEMAlert) -> Optional[str]:
        """Extraer unidad de negocio de la alerta"""
        # Check various fields for business unit indicators
        search_text = f"{alert.title} {alert.description}".lower()

        if alert.host:
            search_text += f" {alert.host}".lower()

        if alert.user:
            search_text += f" {alert.user}".lower()

        # Map keywords to business units
        unit_keywords = {
            "finance": ["finance", "accounting", "treasury", "billing", "payment", "financial"],
            "hr": ["hr", "human resources", "personnel", "employee", "payroll", "recruitment"],
            "engineering": ["dev", "development", "engineering", "tech", "software", "code"],
            "executive": ["executive", "ceo", "cto", "cfo", "board", "leadership", "c-level"],
            "operations": ["ops", "operations", "infrastructure", "datacenter", "production"]
        }

        for unit, keywords in unit_keywords.items():
            for keyword in keywords:
                if keyword in search_text:
                    return unit

        # Check IP ranges (simplified)
        if alert.source_ip:
            if alert.source_ip.startswith("192.168.1."):
                return "finance"
            elif alert.source_ip.startswith("192.168.2."):
                return "hr"
            elif alert.source_ip.startswith("192.168.3."):
                return "engineering"
            elif alert.source_ip.startswith("10.0.1."):
                return "executive"

        return None

    async def _cluster_by_temporal_patterns(self, alerts: List[SIEMAlert]) -> List[AlertCluster]:
        """Clusterizar alertas por patrones temporales"""
        self.logger.debug("⏰ Clustering by temporal patterns")

        clusters = []

        # Group alerts by time windows
        time_windows = defaultdict(list)
        window_size = timedelta(minutes=self.temporal_window_minutes)

        for alert in alerts:
            # Calculate window start (round down to window boundary)
            window_start = alert.timestamp.replace(second=0, microsecond=0)
            window_minutes = (window_start.minute // self.temporal_window_minutes) * self.temporal_window_minutes
            window_start = window_start.replace(minute=window_minutes)

            time_windows[window_start].append(alert)

        # Create clusters for windows with significant activity
        for window_start, window_alerts in time_windows.items():
            if len(window_alerts) >= 5:  # Minimum for temporal cluster

                # Sort by severity
                window_alerts.sort(key=lambda a: a.severity.value, reverse=True)

                primary_alert = window_alerts[0]
                related_alerts = window_alerts[1:]

                cluster = AlertCluster(
                    cluster_id=f"temporal_{int(window_start.timestamp())}",
                    primary_alert=primary_alert,
                    related_alerts=related_alerts,
                    aggregation_strategy=AggregationStrategy.TEMPORAL,
                    similarity_score=0.7,
                    cluster_priority=self._determine_cluster_priority(window_alerts),
                    business_context={
                        "time_window": window_start.isoformat(),
                        "window_duration_minutes": self.temporal_window_minutes,
                        "alert_burst": len(window_alerts) >= 10
                    },
                    summary=f"Temporal alert burst: {len(window_alerts)} alerts in {self.temporal_window_minutes} minutes",
                    recommended_actions=[
                        "Investigate temporal correlation of alerts",
                        "Check for system-wide events or attacks",
                        "Analyze timeline for attack progression"
                    ]
                )
                clusters.append(cluster)

        return clusters

    async def _cluster_by_iocs(self, alerts: List[SIEMAlert]) -> List[AlertCluster]:
        """Clusterizar alertas por IOCs compartidos"""
        self.logger.debug("🔗 Clustering by shared IOCs")

        clusters = []
        ioc_groups = defaultdict(list)

        # Group alerts by shared IOCs
        for alert in alerts:
            alert_iocs = self._extract_simple_iocs(alert)
            for ioc in alert_iocs:
                ioc_groups[ioc].append(alert)

        # Create clusters for IOCs with multiple alerts
        for ioc, ioc_alerts in ioc_groups.items():
            if len(ioc_alerts) >= 2:

                # Remove duplicates
                unique_alerts = []
                seen_ids = set()
                for alert in ioc_alerts:
                    if alert.alert_id not in seen_ids:
                        unique_alerts.append(alert)
                        seen_ids.add(alert.alert_id)

                if len(unique_alerts) >= 2:
                    unique_alerts.sort(key=lambda a: a.severity.value, reverse=True)

                    primary_alert = unique_alerts[0]
                    related_alerts = unique_alerts[1:]

                    cluster = AlertCluster(
                        cluster_id=f"ioc_{hashlib.md5(ioc.encode()).hexdigest()[:8]}",
                        primary_alert=primary_alert,
                        related_alerts=related_alerts,
                        aggregation_strategy=AggregationStrategy.IOC_BASED,
                        similarity_score=0.9,  # High for shared IOCs
                        cluster_priority=self._determine_cluster_priority(unique_alerts),
                        business_context={
                            "shared_ioc": ioc,
                            "ioc_frequency": len(unique_alerts)
                        },
                        summary=f"Shared IOC cluster: {ioc} ({len(unique_alerts)} alerts)",
                        recommended_actions=[
                            f"Investigate shared IOC: {ioc}",
                            "Check IOC reputation and threat intelligence",
                            "Consider blocking IOC if confirmed malicious"
                        ]
                    )
                    clusters.append(cluster)

        return clusters

    def _extract_simple_iocs(self, alert: SIEMAlert) -> List[str]:
        """Extraer IOCs simples de la alerta"""
        iocs = []

        if alert.source_ip:
            iocs.append(alert.source_ip)
        if alert.dest_ip:
            iocs.append(alert.dest_ip)
        if alert.user:
            iocs.append(alert.user)
        if alert.host:
            iocs.append(alert.host)

        return iocs

    def _determine_cluster_priority(self, alerts: List[SIEMAlert]) -> AlertPriority:
        """Determinar prioridad del cluster"""
        if not alerts:
            return AlertPriority.LOW

        max_severity = max(alert.severity.value for alert in alerts)
        alert_count = len(alerts)

        # Priority based on severity and count
        if max_severity >= 4 and alert_count >= 5:  # Critical severity with many alerts
            return AlertPriority.EMERGENCY
        elif max_severity >= 4:  # Critical severity
            return AlertPriority.CRITICAL
        elif max_severity >= 3 and alert_count >= 3:  # High severity with multiple alerts
            return AlertPriority.CRITICAL
        elif max_severity >= 3:  # High severity
            return AlertPriority.HIGH
        elif alert_count >= 10:  # Many alerts regardless of severity
            return AlertPriority.HIGH
        elif max_severity >= 2:  # Medium severity
            return AlertPriority.MEDIUM
        else:
            return AlertPriority.LOW

    async def _extract_business_context(self, alerts: List[SIEMAlert]) -> Dict[str, Any]:
        """Extraer contexto de negocio del cluster"""
        business_units = set()
        compliance_frameworks = set()
        criticality_levels = set()

        for alert in alerts:
            # Extract business unit
            unit = await self._extract_business_unit(alert)
            if unit:
                business_units.add(unit)
                unit_config = self.business_units.get(unit, {})
                criticality_levels.add(unit_config.get("criticality", "unknown"))
                compliance_frameworks.update(unit_config.get("compliance", []))

        return {
            "business_units": list(business_units),
            "compliance_frameworks": list(compliance_frameworks),
            "criticality_levels": list(criticality_levels),
            "platforms_involved": list(set(alert.platform.value for alert in alerts))
        }

    async def _generate_cluster_summary(self, alerts: List[SIEMAlert]) -> str:
        """Generar resumen del cluster"""
        if not alerts:
            return "Empty cluster"

        alert_count = len(alerts)
        platforms = set(alert.platform.value for alert in alerts)
        max_severity = max((alert.severity for alert in alerts), key=lambda s: s.value)

        # Common patterns in titles
        titles = [alert.title for alert in alerts]
        common_words = self._find_common_words(titles)

        summary_parts = [
            f"{alert_count} alerts",
            f"platforms: {', '.join(platforms)}",
            f"max severity: {max_severity.name}"
        ]

        if common_words:
            summary_parts.append(f"common theme: {', '.join(common_words[:3])}")

        return " | ".join(summary_parts)

    def _find_common_words(self, texts: List[str]) -> List[str]:
        """Encontrar palabras comunes en textos"""
        if not texts:
            return []

        # Extract words from all texts
        all_words = []
        for text in texts:
            words = re.findall(r'\b\w+\b', text.lower())
            all_words.extend(words)

        # Filter out common stop words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        meaningful_words = [word for word in all_words if word not in stop_words and len(word) > 3]

        # Count frequency
        word_counts = Counter(meaningful_words)

        # Return most common words that appear in multiple texts
        common_words = []
        for word, count in word_counts.most_common(10):
            if count >= 2:  # Appears at least twice
                common_words.append(word)

        return common_words

    async def _generate_cluster_actions(self, alerts: List[SIEMAlert]) -> List[str]:
        """Generar acciones recomendadas para el cluster"""
        actions = []

        # Basic investigation actions
        actions.append(f"Investigate cluster of {len(alerts)} related alerts")

        # Platform-specific actions
        platforms = set(alert.platform.value for alert in alerts)
        if len(platforms) > 1:
            actions.append("Coordinate investigation across multiple SIEM platforms")

        # Severity-based actions
        max_severity = max((alert.severity for alert in alerts), key=lambda s: s.value)
        if max_severity.value >= 4:
            actions.append("Immediate escalation required for critical threats")
            actions.append("Notify SOC manager and incident response team")

        # IOC-related actions
        iocs = set()
        for alert in alerts:
            iocs.update(self._extract_simple_iocs(alert))

        if iocs:
            actions.append("Analyze shared IOCs for threat intelligence")

        # Business context actions
        business_units = set()
        for alert in alerts:
            unit = await self._extract_business_unit(alert)
            if unit:
                business_units.add(unit)

        if business_units:
            actions.append(f"Notify affected business units: {', '.join(business_units)}")

        return actions[:6]  # Limit to 6 actions

    async def _merge_overlapping_clusters(self, clusters: List[AlertCluster]) -> List[AlertCluster]:
        """Fusionar clusters superpuestos"""
        if not clusters:
            return []

        merged_clusters = []
        processed_cluster_ids = set()

        for cluster in clusters:
            if cluster.cluster_id in processed_cluster_ids:
                continue

            # Find overlapping clusters
            overlapping_clusters = [cluster]
            cluster_alert_ids = set(alert.alert_id for alert in ([cluster.primary_alert] + cluster.related_alerts))

            for other_cluster in clusters:
                if (other_cluster.cluster_id != cluster.cluster_id and
                    other_cluster.cluster_id not in processed_cluster_ids):

                    other_alert_ids = set(alert.alert_id for alert in ([other_cluster.primary_alert] + other_cluster.related_alerts))

                    # Check for overlap
                    overlap = len(cluster_alert_ids & other_alert_ids)
                    if overlap > 0:
                        overlapping_clusters.append(other_cluster)
                        processed_cluster_ids.add(other_cluster.cluster_id)

            # Merge overlapping clusters
            if len(overlapping_clusters) > 1:
                merged_cluster = await self._merge_cluster_group(overlapping_clusters)
                merged_clusters.append(merged_cluster)
            else:
                merged_clusters.append(cluster)

            processed_cluster_ids.add(cluster.cluster_id)

        return merged_clusters

    async def _merge_cluster_group(self, clusters: List[AlertCluster]) -> AlertCluster:
        """Fusionar grupo de clusters"""
        # Combine all alerts
        all_alerts = []
        seen_alert_ids = set()

        for cluster in clusters:
            for alert in [cluster.primary_alert] + cluster.related_alerts:
                if alert.alert_id not in seen_alert_ids:
                    all_alerts.append(alert)
                    seen_alert_ids.add(alert.alert_id)

        # Sort by severity to determine primary alert
        all_alerts.sort(key=lambda a: a.severity.value, reverse=True)
        primary_alert = all_alerts[0]
        related_alerts = all_alerts[1:]

        # Merge business contexts
        merged_business_context = {}
        for cluster in clusters:
            merged_business_context.update(cluster.business_context)

        # Combine recommended actions
        all_actions = []
        for cluster in clusters:
            all_actions.extend(cluster.recommended_actions)
        unique_actions = list(dict.fromkeys(all_actions))  # Remove duplicates

        # Calculate merged priority
        max_priority = max((cluster.cluster_priority for cluster in clusters), key=lambda p: p.value)

        merged_cluster = AlertCluster(
            cluster_id=f"merged_{int(datetime.now().timestamp())}_{len(clusters)}",
            primary_alert=primary_alert,
            related_alerts=related_alerts,
            aggregation_strategy=AggregationStrategy.SIMILARITY,  # Default
            similarity_score=statistics.mean([c.similarity_score for c in clusters]),
            cluster_priority=max_priority,
            business_context=merged_business_context,
            summary=f"Merged cluster: {len(all_alerts)} alerts from {len(clusters)} sources",
            recommended_actions=unique_actions[:8]  # Limit actions
        )

        return merged_cluster

    async def _prioritize_clusters(self, clusters: List[AlertCluster]) -> List[AlertCluster]:
        """Priorizar clusters por importancia"""
        # Sort clusters by priority and other factors
        def cluster_score(cluster):
            priority_score = cluster.cluster_priority.value * 100

            # Business context bonus
            business_bonus = 0
            if cluster.business_context.get("business_units"):
                for unit in cluster.business_context["business_units"]:
                    unit_config = self.business_units.get(unit, {})
                    if unit_config.get("criticality") == "critical":
                        business_bonus += 50
                    elif unit_config.get("criticality") == "high":
                        business_bonus += 30

            # Alert count bonus
            alert_count = len(cluster.related_alerts) + 1
            count_bonus = min(50, alert_count * 2)

            # Similarity bonus
            similarity_bonus = cluster.similarity_score * 20

            return priority_score + business_bonus + count_bonus + similarity_bonus

        prioritized = sorted(clusters, key=cluster_score, reverse=True)
        return prioritized

    async def _apply_auto_escalation(self, clusters: List[AlertCluster]) -> List[AlertCluster]:
        """Aplicar reglas de escalación automática"""
        escalated_clusters = []

        for cluster in clusters:
            # Auto-escalation rules
            should_escalate = False
            escalation_reasons = []

            # Rule 1: Critical priority clusters
            if cluster.cluster_priority.value >= AlertPriority.CRITICAL.value:
                should_escalate = True
                escalation_reasons.append("Critical priority threshold exceeded")

            # Rule 2: Executive business unit involvement
            if "executive" in cluster.business_context.get("business_units", []):
                should_escalate = True
                escalation_reasons.append("Executive business unit affected")

            # Rule 3: Multiple compliance frameworks
            compliance = cluster.business_context.get("compliance_frameworks", [])
            if len(compliance) >= 2:
                should_escalate = True
                escalation_reasons.append("Multiple compliance frameworks affected")

            # Rule 4: Large cluster size
            total_alerts = len(cluster.related_alerts) + 1
            if total_alerts >= 15:
                should_escalate = True
                escalation_reasons.append(f"Large cluster size ({total_alerts} alerts)")

            # Apply escalation
            if should_escalate:
                cluster.auto_escalated = True
                escalation_actions = [
                    "AUTO-ESCALATED: Immediate attention required",
                    f"Escalation reasons: {', '.join(escalation_reasons)}"
                ]
                cluster.recommended_actions = escalation_actions + cluster.recommended_actions

            escalated_clusters.append(cluster)

        return escalated_clusters

    async def generate_executive_summary(self, clusters: List[AlertCluster],
                                       noise_alerts: List[SIEMAlert],
                                       time_period: str = "24h") -> ExecutiveSummary:
        """Generar resumen ejecutivo"""
        total_alerts = sum(len(c.related_alerts) + 1 for c in clusters) + len(noise_alerts)
        critical_threats = sum(1 for c in clusters if c.cluster_priority.value >= AlertPriority.CRITICAL.value)

        # Top threats summary
        top_threats = []
        for cluster in clusters[:5]:  # Top 5 clusters
            threat_desc = f"{cluster.aggregation_strategy.value}: {cluster.summary}"
            top_threats.append(threat_desc)

        # Business impact analysis
        affected_units = set()
        compliance_alerts = 0

        for cluster in clusters:
            business_units = cluster.business_context.get("business_units", [])
            affected_units.update(business_units)

            if cluster.business_context.get("compliance_frameworks"):
                compliance_alerts += 1

        business_impact = f"Affected business units: {', '.join(affected_units) if affected_units else 'None identified'}"

        # Executive actions
        executive_actions = [
            f"Review {critical_threats} critical threat clusters",
            f"Coordinate response for {len(affected_units)} affected business units",
            f"Address {compliance_alerts} compliance-related incidents"
        ]

        if any(c.auto_escalated for c in clusters):
            executive_actions.append("Review auto-escalated incidents requiring immediate attention")

        summary = ExecutiveSummary(
            summary_id=f"exec_summary_{int(datetime.now().timestamp())}",
            time_period=time_period,
            total_alerts=total_alerts,
            critical_threats=critical_threats,
            clusters_created=len(clusters),
            noise_filtered=len(noise_alerts),
            top_threats=top_threats,
            business_impact_summary=business_impact,
            recommended_executive_actions=executive_actions,
            compliance_alerts=compliance_alerts
        )

        return summary

async def demo_intelligent_aggregation():
    """Demostración del sistema de agregación inteligente"""
    print("\n🤖 SmartCompute Enterprise - Intelligent Alert Aggregation Demo")
    print("=" * 75)

    # Initialize aggregator
    config = {
        "similarity_threshold": 0.8,
        "temporal_window_minutes": 60,
        "max_cluster_size": 50
    }

    aggregator = IntelligentAlertAggregator(config)

    # Get sample alerts from SIEM coordinator
    from siem_intelligence_coordinator import demo_siem_intelligence_coordination

    print("📡 Collecting sample SIEM alerts for aggregation...")
    sample_correlations = await demo_siem_intelligence_coordination()

    # Extract all alerts
    all_alerts = []
    for correlation in sample_correlations:
        all_alerts.extend(correlation.alerts)

    print(f"\n🔄 Processing {len(all_alerts)} alerts through intelligent aggregation...")

    # Run aggregation
    clusters, noise_alerts = await aggregator.aggregate_alerts(all_alerts)

    # Generate executive summary
    exec_summary = await aggregator.generate_executive_summary(clusters, noise_alerts)

    # Display results
    print(f"\n📊 INTELLIGENT AGGREGATION RESULTS")
    print("=" * 50)
    print(f"Original Alerts: {len(all_alerts)}")
    print(f"Clusters Created: {len(clusters)}")
    print(f"Noise Filtered: {len(noise_alerts)}")
    print(f"Reduction Ratio: {(1 - len(clusters) / len(all_alerts)) * 100:.1f}%")

    print(f"\n🎯 TOP ALERT CLUSTERS")
    print("=" * 30)

    for i, cluster in enumerate(clusters[:5], 1):
        print(f"\n{i}. Cluster: {cluster.cluster_id}")
        print(f"   Strategy: {cluster.aggregation_strategy.value}")
        print(f"   Priority: {cluster.cluster_priority.name}")
        print(f"   Alerts: {len(cluster.related_alerts) + 1}")
        print(f"   Similarity: {cluster.similarity_score:.2f}")
        print(f"   Auto-Escalated: {'YES' if cluster.auto_escalated else 'NO'}")
        print(f"   Summary: {cluster.summary}")

        if cluster.business_context.get("business_units"):
            print(f"   Business Units: {', '.join(cluster.business_context['business_units'])}")

    print(f"\n📋 EXECUTIVE SUMMARY")
    print("=" * 25)
    print(f"Time Period: {exec_summary.time_period}")
    print(f"Critical Threats: {exec_summary.critical_threats}")
    print(f"Compliance Alerts: {exec_summary.compliance_alerts}")
    print(f"Business Impact: {exec_summary.business_impact_summary}")

    print(f"\nTop Executive Actions:")
    for action in exec_summary.recommended_executive_actions:
        print(f"  - {action}")

    print(f"\n✅ Intelligent alert aggregation completed successfully!")

    return clusters, exec_summary

if __name__ == "__main__":
    # Run demo
    results = asyncio.run(demo_intelligent_aggregation())