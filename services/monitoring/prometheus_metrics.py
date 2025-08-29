#!/usr/bin/env python3
"""
SmartCompute Prometheus Metrics
Centralized metrics collection for all services
"""

import time
import logging
from typing import Dict, Any, Optional, Callable
from functools import wraps
from prometheus_client import (
    Counter, Histogram, Gauge, Info, Enum,
    CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST,
    start_http_server, push_to_gateway
)
from prometheus_client.multiprocess import MultiProcessCollector
from prometheus_client.openmetrics.exposition import CONTENT_TYPE_LATEST as OPENMETRICS_CONTENT_TYPE

logger = logging.getLogger(__name__)


class SmartComputeMetrics:
    """Centralized metrics collector for SmartCompute services"""
    
    def __init__(self, service_name: str, registry: Optional[CollectorRegistry] = None):
        self.service_name = service_name
        self.registry = registry or CollectorRegistry()
        
        # Initialize core metrics
        self._init_core_metrics()
        self._init_business_metrics()
        self._init_system_metrics()
        
    def _init_core_metrics(self):
        """Initialize core application metrics"""
        
        # HTTP Request metrics
        self.http_requests_total = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['service', 'method', 'endpoint', 'status'],
            registry=self.registry
        )
        
        self.http_request_duration_seconds = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['service', 'method', 'endpoint'],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
            registry=self.registry
        )
        
        self.http_request_size_bytes = Histogram(
            'http_request_size_bytes',
            'HTTP request size in bytes',
            ['service', 'method', 'endpoint'],
            registry=self.registry
        )
        
        self.http_response_size_bytes = Histogram(
            'http_response_size_bytes',
            'HTTP response size in bytes',
            ['service', 'method', 'endpoint'],
            registry=self.registry
        )
        
        # Database metrics
        self.database_connections_active = Gauge(
            'database_connections_active',
            'Active database connections',
            ['service', 'database'],
            registry=self.registry
        )
        
        self.database_query_duration_seconds = Histogram(
            'database_query_duration_seconds',
            'Database query duration in seconds',
            ['service', 'database', 'operation'],
            registry=self.registry
        )
        
        self.database_queries_total = Counter(
            'database_queries_total',
            'Total database queries',
            ['service', 'database', 'operation', 'status'],
            registry=self.registry
        )
        
        # Cache metrics
        self.cache_operations_total = Counter(
            'cache_operations_total',
            'Total cache operations',
            ['service', 'operation', 'result'],
            registry=self.registry
        )
        
        self.cache_hit_rate = Gauge(
            'cache_hit_rate',
            'Cache hit rate',
            ['service'],
            registry=self.registry
        )
        
    def _init_business_metrics(self):
        """Initialize business-specific metrics"""
        
        # Analysis metrics
        self.analysis_requests_total = Counter(
            'smartcompute_analysis_requests_total',
            'Total analysis requests',
            ['service', 'analysis_type', 'status'],
            registry=self.registry
        )
        
        self.analysis_duration_seconds = Histogram(
            'smartcompute_analysis_duration_seconds',
            'Analysis processing time in seconds',
            ['service', 'analysis_type'],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5],
            registry=self.registry
        )
        
        self.analysis_queue_size = Gauge(
            'smartcompute_analysis_queue_size',
            'Current analysis queue size',
            ['service'],
            registry=self.registry
        )
        
        self.threat_detections_total = Counter(
            'smartcompute_threat_detections_total',
            'Total threat detections',
            ['service', 'severity', 'type'],
            registry=self.registry
        )
        
        self.anomaly_score = Histogram(
            'smartcompute_anomaly_score',
            'Anomaly detection scores',
            ['service'],
            buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            registry=self.registry
        )
        
        # Performance optimization metrics
        self.optimization_speedup = Histogram(
            'smartcompute_optimization_speedup',
            'Optimization speedup factor',
            ['service', 'operation_type'],
            buckets=[1.0, 1.5, 2.0, 3.0, 5.0, 10.0, 25.0, 50.0, 100.0],
            registry=self.registry
        )
        
        self.optimization_accuracy = Histogram(
            'smartcompute_optimization_accuracy',
            'Optimization accuracy achieved',
            ['service', 'operation_type'],
            buckets=[0.90, 0.92, 0.94, 0.95, 0.96, 0.97, 0.98, 0.99, 0.995, 1.0],
            registry=self.registry
        )
        
        # Payment metrics
        self.payments_total = Counter(
            'smartcompute_payments_total',
            'Total payments processed',
            ['service', 'currency', 'status'],
            registry=self.registry
        )
        
        self.payment_amount_usd = Histogram(
            'smartcompute_payment_amount_usd',
            'Payment amounts in USD',
            ['service', 'currency'],
            buckets=[1, 5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000],
            registry=self.registry
        )
        
    def _init_system_metrics(self):
        """Initialize system-level metrics"""
        
        # Application info
        self.app_info = Info(
            'smartcompute_app_info',
            'Application information',
            registry=self.registry
        )
        
        # Service status
        self.service_status = Enum(
            'smartcompute_service_status',
            'Service status',
            ['service'],
            states=['starting', 'healthy', 'degraded', 'unhealthy'],
            registry=self.registry
        )
        
        # Resource usage
        self.memory_usage_bytes = Gauge(
            'smartcompute_memory_usage_bytes',
            'Memory usage in bytes',
            ['service'],
            registry=self.registry
        )
        
        self.cpu_usage_percent = Gauge(
            'smartcompute_cpu_usage_percent',
            'CPU usage percentage',
            ['service'],
            registry=self.registry
        )
        
        # Error tracking
        self.errors_total = Counter(
            'smartcompute_errors_total',
            'Total errors',
            ['service', 'error_type', 'severity'],
            registry=self.registry
        )
        
        # Background tasks
        self.background_tasks_active = Gauge(
            'smartcompute_background_tasks_active',
            'Active background tasks',
            ['service', 'task_type'],
            registry=self.registry
        )
        
        self.background_task_duration_seconds = Histogram(
            'smartcompute_background_task_duration_seconds',
            'Background task duration in seconds',
            ['service', 'task_type'],
            registry=self.registry
        )

    def track_http_request(self, method: str, endpoint: str, status_code: int, 
                          duration: float, request_size: int = 0, response_size: int = 0):
        """Track HTTP request metrics"""
        labels = {
            'service': self.service_name,
            'method': method,
            'endpoint': endpoint,
            'status': str(status_code)
        }
        
        self.http_requests_total.labels(**labels).inc()
        self.http_request_duration_seconds.labels(
            service=self.service_name,
            method=method,
            endpoint=endpoint
        ).observe(duration)
        
        if request_size > 0:
            self.http_request_size_bytes.labels(
                service=self.service_name,
                method=method,
                endpoint=endpoint
            ).observe(request_size)
            
        if response_size > 0:
            self.http_response_size_bytes.labels(
                service=self.service_name,
                method=method,
                endpoint=endpoint
            ).observe(response_size)

    def track_analysis(self, analysis_type: str, duration: float, status: str = 'completed'):
        """Track analysis request metrics"""
        self.analysis_requests_total.labels(
            service=self.service_name,
            analysis_type=analysis_type,
            status=status
        ).inc()
        
        if status == 'completed':
            self.analysis_duration_seconds.labels(
                service=self.service_name,
                analysis_type=analysis_type
            ).observe(duration)

    def track_threat_detection(self, severity: str, threat_type: str):
        """Track threat detection metrics"""
        self.threat_detections_total.labels(
            service=self.service_name,
            severity=severity,
            type=threat_type
        ).inc()

    def track_optimization(self, operation_type: str, speedup: float, accuracy: float):
        """Track optimization metrics"""
        self.optimization_speedup.labels(
            service=self.service_name,
            operation_type=operation_type
        ).observe(speedup)
        
        self.optimization_accuracy.labels(
            service=self.service_name,
            operation_type=operation_type
        ).observe(accuracy)

    def track_payment(self, currency: str, amount_usd: float, status: str):
        """Track payment metrics"""
        self.payments_total.labels(
            service=self.service_name,
            currency=currency,
            status=status
        ).inc()
        
        if status in ['completed', 'confirmed']:
            self.payment_amount_usd.labels(
                service=self.service_name,
                currency=currency
            ).observe(amount_usd)

    def track_database_query(self, database: str, operation: str, duration: float, status: str = 'success'):
        """Track database query metrics"""
        self.database_queries_total.labels(
            service=self.service_name,
            database=database,
            operation=operation,
            status=status
        ).inc()
        
        if status == 'success':
            self.database_query_duration_seconds.labels(
                service=self.service_name,
                database=database,
                operation=operation
            ).observe(duration)

    def set_queue_size(self, size: int):
        """Set current analysis queue size"""
        self.analysis_queue_size.labels(service=self.service_name).set(size)

    def set_service_status(self, status: str):
        """Set service status"""
        self.service_status.labels(service=self.service_name).state(status)

    def track_error(self, error_type: str, severity: str = 'error'):
        """Track error occurrence"""
        self.errors_total.labels(
            service=self.service_name,
            error_type=error_type,
            severity=severity
        ).inc()

    def set_app_info(self, version: str, build_date: str, git_commit: str = ''):
        """Set application information"""
        self.app_info.labels(service=self.service_name).info({
            'version': version,
            'build_date': build_date,
            'git_commit': git_commit,
            'service': self.service_name
        })

    def get_metrics(self) -> str:
        """Get metrics in Prometheus format"""
        return generate_latest(self.registry).decode('utf-8')


def prometheus_middleware(metrics: SmartComputeMetrics):
    """FastAPI middleware for automatic metrics collection"""
    
    def middleware(request, call_next):
        start_time = time.time()
        
        async def process_request():
            try:
                response = await call_next(request)
                duration = time.time() - start_time
                
                # Extract endpoint pattern (remove path parameters)
                endpoint = request.url.path
                method = request.method
                status_code = response.status_code
                
                # Get request/response sizes
                request_size = int(request.headers.get('content-length', 0))
                response_size = len(getattr(response, 'body', b''))
                
                # Track metrics
                metrics.track_http_request(
                    method=method,
                    endpoint=endpoint,
                    status_code=status_code,
                    duration=duration,
                    request_size=request_size,
                    response_size=response_size
                )
                
                return response
                
            except Exception as e:
                duration = time.time() - start_time
                metrics.track_http_request(
                    method=request.method,
                    endpoint=request.url.path,
                    status_code=500,
                    duration=duration
                )
                metrics.track_error('http_request_error', 'error')
                raise
                
        return process_request()
    
    return middleware


def track_function_duration(metrics: SmartComputeMetrics, metric_name: str, labels: Dict[str, str] = None):
    """Decorator to track function execution time"""
    
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Track successful execution
                if hasattr(metrics, metric_name):
                    metric = getattr(metrics, metric_name)
                    if labels:
                        metric.labels(**labels).observe(duration)
                    else:
                        metric.observe(duration)
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                metrics.track_error(f'function_error_{func.__name__}', 'error')
                raise
                
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Track successful execution
                if hasattr(metrics, metric_name):
                    metric = getattr(metrics, metric_name)
                    if labels:
                        metric.labels(**labels).observe(duration)
                    else:
                        metric.observe(duration)
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                metrics.track_error(f'function_error_{func.__name__}', 'error')
                raise
                
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
            
    return decorator


# Global metrics instances for each service
_metrics_instances: Dict[str, SmartComputeMetrics] = {}


def get_metrics(service_name: str) -> SmartComputeMetrics:
    """Get or create metrics instance for service"""
    if service_name not in _metrics_instances:
        _metrics_instances[service_name] = SmartComputeMetrics(service_name)
    return _metrics_instances[service_name]


def start_metrics_server(port: int = 8090):
    """Start Prometheus metrics HTTP server"""
    try:
        start_http_server(port)
        logger.info(f"Prometheus metrics server started on port {port}")
    except Exception as e:
        logger.error(f"Failed to start metrics server: {e}")


def push_metrics_to_gateway(gateway_host: str, job_name: str, service_name: str):
    """Push metrics to Prometheus Pushgateway"""
    try:
        metrics = get_metrics(service_name)
        push_to_gateway(gateway_host, job=job_name, registry=metrics.registry)
        logger.info(f"Metrics pushed to gateway: {gateway_host}")
    except Exception as e:
        logger.error(f"Failed to push metrics to gateway: {e}")


if __name__ == "__main__":
    # Test metrics
    import asyncio
    
    async def test_metrics():
        metrics = get_metrics("test-service")
        
        # Set app info
        metrics.set_app_info("1.0.0", "2025-08-27", "abc123")
        metrics.set_service_status("healthy")
        
        # Test some metrics
        metrics.track_http_request("GET", "/health", 200, 0.001)
        metrics.track_analysis("threat_analysis", 0.05, "completed")
        metrics.track_threat_detection("high", "malware")
        metrics.track_optimization("matrix_multiply", 2.5, 0.98)
        
        print("Sample metrics:")
        print(metrics.get_metrics())
        
    asyncio.run(test_metrics())