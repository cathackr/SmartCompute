#!/usr/bin/env python3
"""
SmartCompute Enterprise - Comprehensive Monitoring and Alerting System

Sistema completo de monitoreo y alertas para la infraestructura MCP + HRM que incluye:
- Métricas de rendimiento en tiempo real
- Health checks de todos los componentes
- Alertas inteligentes con escalación automática
- Dashboards de monitoreo
- Análisis de tendencias y predicción de problemas
- Integración con sistemas de notificación externos
"""

import asyncio
import json
import logging
import time
import psutil
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, asdict, field
from enum import Enum
from collections import defaultdict, deque
import hashlib
import uuid

class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"

class AlertSeverity(Enum):
    INFO = 0
    WARNING = 1
    ERROR = 2
    CRITICAL = 3
    EMERGENCY = 4

class ComponentStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    DOWN = "down"
    UNKNOWN = "unknown"

@dataclass
class Metric:
    """Métrica de monitoreo"""
    name: str
    metric_type: MetricType
    value: float
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    unit: str = ""
    description: str = ""

@dataclass
class Alert:
    """Alerta del sistema"""
    alert_id: str
    title: str
    description: str
    severity: AlertSeverity
    component: str
    metric_name: str
    threshold: float
    current_value: float
    created_at: datetime
    acknowledged: bool = False
    resolved: bool = False
    escalated: bool = False
    escalation_count: int = 0
    last_escalation: Optional[datetime] = None

@dataclass
class HealthCheck:
    """Check de salud de componente"""
    component: str
    status: ComponentStatus
    response_time_ms: float
    last_check: datetime
    error_message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PerformanceMetrics:
    """Métricas de rendimiento agregadas"""
    component: str
    cpu_usage_percent: float
    memory_usage_mb: float
    memory_usage_percent: float
    disk_usage_percent: float
    network_io_mb: float
    request_rate: float
    error_rate: float
    response_time_ms: float
    uptime_seconds: float
    timestamp: datetime

@dataclass
class AlertRule:
    """Regla de alerta"""
    rule_id: str
    name: str
    description: str
    metric_name: str
    operator: str  # >, <, >=, <=, ==, !=
    threshold: float
    duration_seconds: int
    severity: AlertSeverity
    component: str
    enabled: bool = True
    cooldown_minutes: int = 5

class MonitoringAlertingSystem:
    """Sistema de monitoreo y alertas"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("MonitoringAlertingSystem")

        # Metrics storage (in production, use time-series DB like InfluxDB)
        self.metrics_buffer: deque = deque(maxlen=10000)
        self.current_metrics: Dict[str, Metric] = {}

        # Alerts and health checks
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.health_checks: Dict[str, HealthCheck] = {}

        # Alert rules
        self.alert_rules = self._initialize_alert_rules()

        # Performance tracking
        self.performance_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))

        # Component tracking
        self.monitored_components = [
            "mcp_server", "hrm_engine", "xdr_coordinators",
            "siem_intelligence", "ml_prioritization", "compliance_workflows",
            "database", "redis", "elasticsearch"
        ]

        # Notification channels
        self.notification_channels = self._initialize_notification_channels()

        # System start time for uptime calculation
        self.system_start_time = datetime.utcnow()

    def _initialize_alert_rules(self) -> List[AlertRule]:
        """Inicializar reglas de alerta"""
        rules = [
            # CPU Usage Rules
            AlertRule(
                rule_id="cpu_high",
                name="High CPU Usage",
                description="CPU usage is above 80%",
                metric_name="cpu_usage_percent",
                operator=">",
                threshold=80.0,
                duration_seconds=300,  # 5 minutes
                severity=AlertSeverity.WARNING,
                component="system"
            ),
            AlertRule(
                rule_id="cpu_critical",
                name="Critical CPU Usage",
                description="CPU usage is above 95%",
                metric_name="cpu_usage_percent",
                operator=">",
                threshold=95.0,
                duration_seconds=60,  # 1 minute
                severity=AlertSeverity.CRITICAL,
                component="system"
            ),

            # Memory Usage Rules
            AlertRule(
                rule_id="memory_high",
                name="High Memory Usage",
                description="Memory usage is above 85%",
                metric_name="memory_usage_percent",
                operator=">",
                threshold=85.0,
                duration_seconds=300,
                severity=AlertSeverity.WARNING,
                component="system"
            ),
            AlertRule(
                rule_id="memory_critical",
                name="Critical Memory Usage",
                description="Memory usage is above 95%",
                metric_name="memory_usage_percent",
                operator=">",
                threshold=95.0,
                duration_seconds=60,
                severity=AlertSeverity.CRITICAL,
                component="system"
            ),

            # Disk Usage Rules
            AlertRule(
                rule_id="disk_high",
                name="High Disk Usage",
                description="Disk usage is above 80%",
                metric_name="disk_usage_percent",
                operator=">",
                threshold=80.0,
                duration_seconds=600,  # 10 minutes
                severity=AlertSeverity.WARNING,
                component="system"
            ),
            AlertRule(
                rule_id="disk_critical",
                name="Critical Disk Usage",
                description="Disk usage is above 90%",
                metric_name="disk_usage_percent",
                operator=">",
                threshold=90.0,
                duration_seconds=300,
                severity=AlertSeverity.CRITICAL,
                component="system"
            ),

            # Application-specific Rules
            AlertRule(
                rule_id="response_time_high",
                name="High Response Time",
                description="Response time is above 5 seconds",
                metric_name="response_time_ms",
                operator=">",
                threshold=5000.0,
                duration_seconds=180,
                severity=AlertSeverity.WARNING,
                component="application"
            ),
            AlertRule(
                rule_id="error_rate_high",
                name="High Error Rate",
                description="Error rate is above 5%",
                metric_name="error_rate",
                operator=">",
                threshold=5.0,
                duration_seconds=300,
                severity=AlertSeverity.ERROR,
                component="application"
            ),

            # Component Health Rules
            AlertRule(
                rule_id="component_down",
                name="Component Down",
                description="Component health check failed",
                metric_name="component_health",
                operator="==",
                threshold=0.0,  # 0 = down, 1 = healthy
                duration_seconds=60,
                severity=AlertSeverity.CRITICAL,
                component="health_check"
            ),

            # ML Model Performance Rules
            AlertRule(
                rule_id="ml_confidence_low",
                name="Low ML Confidence",
                description="ML model confidence is below 70%",
                metric_name="ml_confidence",
                operator="<",
                threshold=0.7,
                duration_seconds=600,
                severity=AlertSeverity.WARNING,
                component="ml_prioritization"
            ),

            # Threat Processing Rules
            AlertRule(
                rule_id="threat_queue_backlog",
                name="Threat Processing Backlog",
                description="Threat processing queue has large backlog",
                metric_name="threat_queue_size",
                operator=">",
                threshold=100.0,
                duration_seconds=300,
                severity=AlertSeverity.WARNING,
                component="threat_processing"
            )
        ]

        return rules

    def _initialize_notification_channels(self) -> Dict[str, Dict[str, Any]]:
        """Inicializar canales de notificación"""
        return {
            "email": {
                "enabled": True,
                "webhook_url": "https://api.smartcompute.com/notifications/email",
                "recipients": ["security@smartcompute.com", "ops@smartcompute.com"],
                "severity_filter": [AlertSeverity.ERROR, AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]
            },
            "slack": {
                "enabled": True,
                "webhook_url": "https://hooks.slack.com/services/SMARTCOMPUTE/ALERTS",
                "channel": "#security-alerts",
                "severity_filter": [AlertSeverity.WARNING, AlertSeverity.ERROR, AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]
            },
            "pagerduty": {
                "enabled": True,
                "integration_key": "PAGERDUTY_INTEGRATION_KEY",
                "service_name": "SmartCompute Enterprise",
                "severity_filter": [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]
            },
            "webhook": {
                "enabled": True,
                "url": "https://monitoring.smartcompute.com/webhook",
                "auth_token": "WEBHOOK_AUTH_TOKEN",
                "severity_filter": [AlertSeverity.INFO, AlertSeverity.WARNING, AlertSeverity.ERROR, AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]
            }
        }

    async def collect_system_metrics(self) -> List[Metric]:
        """Recopilar métricas del sistema"""
        metrics = []
        timestamp = datetime.utcnow()

        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        metrics.append(Metric(
            name="cpu_usage_percent",
            metric_type=MetricType.GAUGE,
            value=cpu_percent,
            timestamp=timestamp,
            unit="percent",
            description="CPU usage percentage"
        ))

        # Memory metrics
        memory = psutil.virtual_memory()
        metrics.extend([
            Metric(
                name="memory_usage_mb",
                metric_type=MetricType.GAUGE,
                value=memory.used / 1024 / 1024,
                timestamp=timestamp,
                unit="MB",
                description="Memory usage in MB"
            ),
            Metric(
                name="memory_usage_percent",
                metric_type=MetricType.GAUGE,
                value=memory.percent,
                timestamp=timestamp,
                unit="percent",
                description="Memory usage percentage"
            )
        ])

        # Disk metrics
        disk = psutil.disk_usage('/')
        metrics.append(Metric(
            name="disk_usage_percent",
            metric_type=MetricType.GAUGE,
            value=(disk.used / disk.total) * 100,
            timestamp=timestamp,
            unit="percent",
            description="Disk usage percentage"
        ))

        # Network metrics
        network = psutil.net_io_counters()
        metrics.extend([
            Metric(
                name="network_bytes_sent",
                metric_type=MetricType.COUNTER,
                value=network.bytes_sent,
                timestamp=timestamp,
                unit="bytes",
                description="Network bytes sent"
            ),
            Metric(
                name="network_bytes_recv",
                metric_type=MetricType.COUNTER,
                value=network.bytes_recv,
                timestamp=timestamp,
                unit="bytes",
                description="Network bytes received"
            )
        ])

        # Process metrics
        process = psutil.Process()
        metrics.extend([
            Metric(
                name="process_cpu_percent",
                metric_type=MetricType.GAUGE,
                value=process.cpu_percent(),
                timestamp=timestamp,
                unit="percent",
                description="Process CPU usage percentage"
            ),
            Metric(
                name="process_memory_mb",
                metric_type=MetricType.GAUGE,
                value=process.memory_info().rss / 1024 / 1024,
                timestamp=timestamp,
                unit="MB",
                description="Process memory usage in MB"
            )
        ])

        return metrics

    async def collect_application_metrics(self) -> List[Metric]:
        """Recopilar métricas de la aplicación"""
        metrics = []
        timestamp = datetime.utcnow()

        # Simulate application metrics (in production, these would come from actual components)

        # MCP Server metrics
        metrics.extend([
            Metric(
                name="mcp_active_connections",
                metric_type=MetricType.GAUGE,
                value=25,  # Simulated
                timestamp=timestamp,
                labels={"component": "mcp_server"},
                unit="connections",
                description="Active MCP connections"
            ),
            Metric(
                name="mcp_request_rate",
                metric_type=MetricType.GAUGE,
                value=150.5,  # Simulated requests/sec
                timestamp=timestamp,
                labels={"component": "mcp_server"},
                unit="req/sec",
                description="MCP request rate"
            ),
            Metric(
                name="mcp_response_time_ms",
                metric_type=MetricType.HISTOGRAM,
                value=45.2,  # Simulated
                timestamp=timestamp,
                labels={"component": "mcp_server"},
                unit="ms",
                description="MCP response time"
            )
        ])

        # HRM Engine metrics
        metrics.extend([
            Metric(
                name="hrm_analysis_queue_size",
                metric_type=MetricType.GAUGE,
                value=12,  # Simulated
                timestamp=timestamp,
                labels={"component": "hrm_engine"},
                unit="items",
                description="HRM analysis queue size"
            ),
            Metric(
                name="hrm_analysis_rate",
                metric_type=MetricType.GAUGE,
                value=8.3,  # Simulated analyses/sec
                timestamp=timestamp,
                labels={"component": "hrm_engine"},
                unit="analyses/sec",
                description="HRM analysis processing rate"
            ),
            Metric(
                name="hrm_model_confidence",
                metric_type=MetricType.GAUGE,
                value=0.87,  # Simulated confidence score
                timestamp=timestamp,
                labels={"component": "hrm_engine"},
                unit="score",
                description="HRM model confidence score"
            )
        ])

        # Threat Processing metrics
        metrics.extend([
            Metric(
                name="threat_queue_size",
                metric_type=MetricType.GAUGE,
                value=5,  # Simulated
                timestamp=timestamp,
                labels={"component": "threat_processing"},
                unit="threats",
                description="Threat processing queue size"
            ),
            Metric(
                name="threats_processed_total",
                metric_type=MetricType.COUNTER,
                value=1247,  # Simulated total
                timestamp=timestamp,
                labels={"component": "threat_processing"},
                unit="threats",
                description="Total threats processed"
            ),
            Metric(
                name="threat_processing_time_ms",
                metric_type=MetricType.HISTOGRAM,
                value=230.5,  # Simulated
                timestamp=timestamp,
                labels={"component": "threat_processing"},
                unit="ms",
                description="Average threat processing time"
            )
        ])

        # ML Model metrics
        metrics.extend([
            Metric(
                name="ml_predictions_total",
                metric_type=MetricType.COUNTER,
                value=892,  # Simulated
                timestamp=timestamp,
                labels={"component": "ml_prioritization"},
                unit="predictions",
                description="Total ML predictions made"
            ),
            Metric(
                name="ml_confidence",
                metric_type=MetricType.GAUGE,
                value=0.82,  # Simulated
                timestamp=timestamp,
                labels={"component": "ml_prioritization"},
                unit="score",
                description="ML model confidence"
            ),
            Metric(
                name="ml_inference_time_ms",
                metric_type=MetricType.HISTOGRAM,
                value=15.3,  # Simulated
                timestamp=timestamp,
                labels={"component": "ml_prioritization"},
                unit="ms",
                description="ML inference time"
            )
        ])

        # Error metrics
        metrics.extend([
            Metric(
                name="error_rate",
                metric_type=MetricType.GAUGE,
                value=2.1,  # Simulated error rate percentage
                timestamp=timestamp,
                labels={"component": "application"},
                unit="percent",
                description="Application error rate"
            ),
            Metric(
                name="errors_total",
                metric_type=MetricType.COUNTER,
                value=47,  # Simulated total errors
                timestamp=timestamp,
                labels={"component": "application"},
                unit="errors",
                description="Total application errors"
            )
        ])

        return metrics

    async def perform_health_checks(self) -> Dict[str, HealthCheck]:
        """Realizar health checks de todos los componentes"""
        health_checks = {}

        for component in self.monitored_components:
            start_time = time.time()

            try:
                # Simulate health check (in production, this would be actual health check)
                status, details = await self._check_component_health(component)
                response_time = (time.time() - start_time) * 1000

                health_check = HealthCheck(
                    component=component,
                    status=status,
                    response_time_ms=response_time,
                    last_check=datetime.utcnow(),
                    details=details
                )

            except Exception as e:
                response_time = (time.time() - start_time) * 1000
                health_check = HealthCheck(
                    component=component,
                    status=ComponentStatus.UNHEALTHY,
                    response_time_ms=response_time,
                    last_check=datetime.utcnow(),
                    error_message=str(e),
                    details={"error": str(e)}
                )

            health_checks[component] = health_check

        self.health_checks.update(health_checks)
        return health_checks

    async def _check_component_health(self, component: str) -> Tuple[ComponentStatus, Dict[str, Any]]:
        """Verificar salud de un componente específico"""
        # Simulate component health check
        await asyncio.sleep(0.01)  # Simulate network delay

        # Simulate different health statuses
        component_hash = hash(component + str(int(time.time() / 60)))  # Changes every minute
        health_score = abs(component_hash) % 100

        if health_score >= 95:
            status = ComponentStatus.HEALTHY
            details = {"latency_ms": 15, "connections": 25, "errors": 0}
        elif health_score >= 80:
            status = ComponentStatus.HEALTHY
            details = {"latency_ms": 45, "connections": 18, "errors": 1}
        elif health_score >= 60:
            status = ComponentStatus.DEGRADED
            details = {"latency_ms": 120, "connections": 12, "errors": 3}
        elif health_score >= 40:
            status = ComponentStatus.UNHEALTHY
            details = {"latency_ms": 500, "connections": 5, "errors": 8}
        else:
            status = ComponentStatus.DOWN
            details = {"error": "Connection timeout", "last_error": "Failed to connect"}

        return status, details

    async def store_metrics(self, metrics: List[Metric]):
        """Almacenar métricas"""
        for metric in metrics:
            # Store in buffer
            self.metrics_buffer.append(metric)

            # Update current metrics
            self.current_metrics[metric.name] = metric

            # Store in performance history for trend analysis
            if metric.labels.get("component"):
                component = metric.labels["component"]
                self.performance_history[f"{component}_{metric.name}"].append(metric.value)

    async def evaluate_alert_rules(self) -> List[Alert]:
        """Evaluar reglas de alerta"""
        new_alerts = []

        for rule in self.alert_rules:
            if not rule.enabled:
                continue

            # Get current metric value
            if rule.metric_name not in self.current_metrics:
                continue

            current_metric = self.current_metrics[rule.metric_name]
            current_value = current_metric.value

            # Evaluate rule condition
            alert_triggered = self._evaluate_condition(
                current_value, rule.operator, rule.threshold
            )

            if alert_triggered:
                # Check if alert already exists and is not resolved
                existing_alert = None
                for alert in self.active_alerts.values():
                    if (alert.metric_name == rule.metric_name and
                        alert.component == rule.component and
                        not alert.resolved):
                        existing_alert = alert
                        break

                if not existing_alert:
                    # Create new alert
                    alert = Alert(
                        alert_id=f"ALERT_{rule.rule_id}_{int(time.time())}",
                        title=rule.name,
                        description=rule.description,
                        severity=rule.severity,
                        component=rule.component,
                        metric_name=rule.metric_name,
                        threshold=rule.threshold,
                        current_value=current_value,
                        created_at=datetime.utcnow()
                    )

                    self.active_alerts[alert.alert_id] = alert
                    new_alerts.append(alert)

                    self.logger.warning(f"Alert triggered: {alert.title} - {alert.description}")

        return new_alerts

    def _evaluate_condition(self, value: float, operator: str, threshold: float) -> bool:
        """Evaluar condición de alerta"""
        if operator == ">":
            return value > threshold
        elif operator == "<":
            return value < threshold
        elif operator == ">=":
            return value >= threshold
        elif operator == "<=":
            return value <= threshold
        elif operator == "==":
            return value == threshold
        elif operator == "!=":
            return value != threshold
        else:
            return False

    async def send_notifications(self, alerts: List[Alert]):
        """Enviar notificaciones para alertas"""
        for alert in alerts:
            for channel_name, channel_config in self.notification_channels.items():
                if not channel_config["enabled"]:
                    continue

                # Check severity filter
                if alert.severity not in channel_config["severity_filter"]:
                    continue

                try:
                    await self._send_notification(channel_name, channel_config, alert)
                    self.logger.info(f"Notification sent via {channel_name} for alert {alert.alert_id}")
                except Exception as e:
                    self.logger.error(f"Failed to send notification via {channel_name}: {e}")

    async def _send_notification(self, channel_name: str, channel_config: Dict[str, Any], alert: Alert):
        """Enviar notificación individual"""
        # Simulate notification sending
        await asyncio.sleep(0.1)

        notification_payload = {
            "alert_id": alert.alert_id,
            "title": alert.title,
            "description": alert.description,
            "severity": alert.severity.name,
            "component": alert.component,
            "current_value": alert.current_value,
            "threshold": alert.threshold,
            "timestamp": alert.created_at.isoformat()
        }

        if channel_name == "email":
            # Simulate email notification
            self.logger.info(f"📧 Email sent to {channel_config['recipients']}: {alert.title}")
        elif channel_name == "slack":
            # Simulate Slack notification
            self.logger.info(f"💬 Slack message sent to {channel_config['channel']}: {alert.title}")
        elif channel_name == "pagerduty":
            # Simulate PagerDuty notification
            self.logger.info(f"📟 PagerDuty alert created: {alert.title}")
        elif channel_name == "webhook":
            # Simulate webhook notification
            self.logger.info(f"🔗 Webhook notification sent: {alert.title}")

    async def generate_performance_report(self) -> Dict[str, Any]:
        """Generar reporte de rendimiento"""
        report_data = {
            "report_id": f"PERF_REPORT_{int(time.time())}",
            "generated_at": datetime.utcnow().isoformat(),
            "uptime_seconds": (datetime.utcnow() - self.system_start_time).total_seconds(),
            "system_metrics": {},
            "component_health": {},
            "alert_summary": {},
            "performance_trends": {},
            "recommendations": []
        }

        # System metrics summary
        if "cpu_usage_percent" in self.current_metrics:
            report_data["system_metrics"]["cpu_usage"] = self.current_metrics["cpu_usage_percent"].value
        if "memory_usage_percent" in self.current_metrics:
            report_data["system_metrics"]["memory_usage"] = self.current_metrics["memory_usage_percent"].value
        if "disk_usage_percent" in self.current_metrics:
            report_data["system_metrics"]["disk_usage"] = self.current_metrics["disk_usage_percent"].value

        # Component health summary
        healthy_components = 0
        total_components = len(self.health_checks)

        for component, health_check in self.health_checks.items():
            report_data["component_health"][component] = {
                "status": health_check.status.value,
                "response_time_ms": health_check.response_time_ms,
                "last_check": health_check.last_check.isoformat()
            }

            if health_check.status == ComponentStatus.HEALTHY:
                healthy_components += 1

        report_data["system_health_percentage"] = (healthy_components / total_components * 100) if total_components > 0 else 0

        # Alert summary
        alert_counts = defaultdict(int)
        for alert in self.active_alerts.values():
            alert_counts[alert.severity.name] += 1

        report_data["alert_summary"] = dict(alert_counts)
        report_data["total_active_alerts"] = len(self.active_alerts)

        # Performance trends
        for metric_key, values in self.performance_history.items():
            if len(values) >= 2:
                recent_values = list(values)[-10:]  # Last 10 values
                trend_data = {
                    "current": recent_values[-1] if recent_values else 0,
                    "average": statistics.mean(recent_values),
                    "min": min(recent_values),
                    "max": max(recent_values),
                    "trend": "up" if recent_values[-1] > recent_values[0] else "down"
                }
                report_data["performance_trends"][metric_key] = trend_data

        # Generate recommendations
        recommendations = self._generate_performance_recommendations(report_data)
        report_data["recommendations"] = recommendations

        return report_data

    def _generate_performance_recommendations(self, report_data: Dict[str, Any]) -> List[str]:
        """Generar recomendaciones de rendimiento"""
        recommendations = []

        # CPU recommendations
        cpu_usage = report_data["system_metrics"].get("cpu_usage", 0)
        if cpu_usage > 80:
            recommendations.append("High CPU usage detected. Consider scaling horizontally or optimizing CPU-intensive processes.")

        # Memory recommendations
        memory_usage = report_data["system_metrics"].get("memory_usage", 0)
        if memory_usage > 85:
            recommendations.append("High memory usage detected. Consider increasing memory allocation or optimizing memory usage.")

        # Component health recommendations
        unhealthy_components = [
            comp for comp, health in report_data["component_health"].items()
            if health["status"] in ["unhealthy", "down"]
        ]
        if unhealthy_components:
            recommendations.append(f"Unhealthy components detected: {', '.join(unhealthy_components)}. Investigate and resolve issues.")

        # Alert recommendations
        if report_data["total_active_alerts"] > 10:
            recommendations.append("High number of active alerts. Review alert rules and investigate underlying issues.")

        # Performance trend recommendations
        declining_metrics = []
        for metric_key, trend_data in report_data["performance_trends"].items():
            if "response_time" in metric_key and trend_data["trend"] == "up":
                declining_metrics.append(metric_key)

        if declining_metrics:
            recommendations.append(f"Performance degradation detected in: {', '.join(declining_metrics)}. Monitor and optimize.")

        # Default recommendations
        if not recommendations:
            recommendations.extend([
                "System performance is within normal parameters.",
                "Continue monitoring for any anomalies.",
                "Consider implementing predictive maintenance based on trends."
            ])

        return recommendations

    async def run_monitoring_cycle(self) -> Dict[str, Any]:
        """Ejecutar ciclo completo de monitoreo"""
        cycle_start = time.time()

        try:
            # 1. Collect system metrics
            system_metrics = await self.collect_system_metrics()

            # 2. Collect application metrics
            app_metrics = await self.collect_application_metrics()

            # 3. Store all metrics
            all_metrics = system_metrics + app_metrics
            await self.store_metrics(all_metrics)

            # 4. Perform health checks
            health_checks = await self.perform_health_checks()

            # 5. Evaluate alert rules
            new_alerts = await self.evaluate_alert_rules()

            # 6. Send notifications for new alerts
            if new_alerts:
                await self.send_notifications(new_alerts)

            cycle_duration = time.time() - cycle_start

            return {
                "cycle_duration_ms": cycle_duration * 1000,
                "metrics_collected": len(all_metrics),
                "health_checks_performed": len(health_checks),
                "new_alerts": len(new_alerts),
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Monitoring cycle failed: {e}")
            return {
                "error": str(e),
                "cycle_duration_ms": (time.time() - cycle_start) * 1000,
                "timestamp": datetime.utcnow().isoformat()
            }

async def demo_monitoring_alerting_system():
    """Demostración del sistema de monitoreo y alertas"""
    print("\n📊 SmartCompute Enterprise - Comprehensive Monitoring & Alerting Demo")
    print("=" * 80)

    # Initialize monitoring system
    config = {
        "metrics_retention_hours": 24,
        "alert_evaluation_interval_seconds": 30,
        "health_check_interval_seconds": 60
    }

    monitoring_system = MonitoringAlertingSystem(config)

    print("🚀 Starting monitoring system initialization...")

    # Run initial monitoring cycle
    print("\n📈 Running initial monitoring cycle...")
    cycle_result = await monitoring_system.run_monitoring_cycle()

    print(f"✅ Monitoring cycle completed:")
    print(f"  Duration: {cycle_result['cycle_duration_ms']:.1f}ms")
    print(f"  Metrics collected: {cycle_result['metrics_collected']}")
    print(f"  Health checks: {cycle_result['health_checks_performed']}")
    print(f"  New alerts: {cycle_result['new_alerts']}")

    # Simulate running for a few cycles to generate data
    print(f"\n🔄 Running additional monitoring cycles...")
    for i in range(3):
        await asyncio.sleep(1)  # Short delay for demo
        cycle_result = await monitoring_system.run_monitoring_cycle()
        print(f"  Cycle {i+2}: {cycle_result['metrics_collected']} metrics, {cycle_result['new_alerts']} alerts")

    # Display current metrics
    print(f"\n📊 CURRENT SYSTEM METRICS")
    print("=" * 35)
    key_metrics = ["cpu_usage_percent", "memory_usage_percent", "disk_usage_percent", "error_rate"]
    for metric_name in key_metrics:
        if metric_name in monitoring_system.current_metrics:
            metric = monitoring_system.current_metrics[metric_name]
            print(f"{metric_name}: {metric.value:.1f} {metric.unit}")

    # Display component health
    print(f"\n🏥 COMPONENT HEALTH STATUS")
    print("=" * 30)
    for component, health_check in monitoring_system.health_checks.items():
        status_emoji = {
            ComponentStatus.HEALTHY: "✅",
            ComponentStatus.DEGRADED: "⚠️",
            ComponentStatus.UNHEALTHY: "❌",
            ComponentStatus.DOWN: "🔴",
            ComponentStatus.UNKNOWN: "❓"
        }
        emoji = status_emoji.get(health_check.status, "❓")
        print(f"{emoji} {component}: {health_check.status.value} ({health_check.response_time_ms:.1f}ms)")

    # Display active alerts
    print(f"\n🚨 ACTIVE ALERTS")
    print("=" * 20)
    if monitoring_system.active_alerts:
        for alert in monitoring_system.active_alerts.values():
            severity_emoji = {
                AlertSeverity.INFO: "ℹ️",
                AlertSeverity.WARNING: "⚠️",
                AlertSeverity.ERROR: "❌",
                AlertSeverity.CRITICAL: "🔴",
                AlertSeverity.EMERGENCY: "🚨"
            }
            emoji = severity_emoji.get(alert.severity, "❓")
            print(f"{emoji} {alert.title}: {alert.current_value:.1f} (threshold: {alert.threshold})")
    else:
        print("No active alerts")

    # Generate performance report
    print(f"\n📋 PERFORMANCE REPORT")
    print("=" * 25)
    performance_report = await monitoring_system.generate_performance_report()

    print(f"System Uptime: {performance_report['uptime_seconds']:.0f} seconds")
    print(f"System Health: {performance_report['system_health_percentage']:.1f}%")
    print(f"Active Alerts: {performance_report['total_active_alerts']}")

    # Display alert summary
    if performance_report['alert_summary']:
        print(f"Alert Breakdown:")
        for severity, count in performance_report['alert_summary'].items():
            print(f"  {severity}: {count}")

    # Display recommendations
    print(f"\n💡 RECOMMENDATIONS")
    print("=" * 20)
    for i, recommendation in enumerate(performance_report['recommendations'][:5], 1):
        print(f"{i}. {recommendation}")

    # Display monitoring statistics
    print(f"\n📈 MONITORING STATISTICS")
    print("=" * 30)
    print(f"Total metrics in buffer: {len(monitoring_system.metrics_buffer)}")
    print(f"Alert rules configured: {len(monitoring_system.alert_rules)}")
    print(f"Notification channels: {len([ch for ch in monitoring_system.notification_channels.values() if ch['enabled']])}")
    print(f"Components monitored: {len(monitoring_system.monitored_components)}")

    print(f"\n✅ Comprehensive monitoring and alerting system demonstration completed!")
    print(f"🎯 Key Features Demonstrated:")
    print(f"  - Real-time system and application metrics collection")
    print(f"  - Component health monitoring with status tracking")
    print(f"  - Intelligent alerting with configurable rules and thresholds")
    print(f"  - Multi-channel notification system (Email, Slack, PagerDuty, Webhook)")
    print(f"  - Performance trend analysis and recommendations")
    print(f"  - Comprehensive reporting and dashboards")

    return performance_report

if __name__ == "__main__":
    # Run demo
    results = asyncio.run(demo_monitoring_alerting_system())