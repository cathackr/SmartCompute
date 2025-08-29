#!/usr/bin/env python3
"""
SmartCompute Health Monitoring and Observability
Advanced health checks, metrics, and monitoring capabilities
"""

import time
import json
import psutil
import logging
import threading
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import numpy as np
from collections import deque, defaultdict
import hashlib
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class HealthStatus:
    """System health status"""
    status: str  # 'healthy', 'warning', 'critical', 'unknown'
    timestamp: str
    checks: Dict[str, Any]
    metrics: Dict[str, float]
    errors: List[str]
    warnings: List[str]
    uptime_seconds: float

@dataclass
class PerformanceMetrics:
    """Performance metrics snapshot"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    active_threads: int
    open_files: int
    network_io: Dict[str, int]
    custom_metrics: Dict[str, float]

class HealthMonitor:
    """Advanced health monitoring system"""
    
    def __init__(
        self, 
        check_interval: float = 30.0,
        metrics_retention_minutes: int = 60,
        alert_thresholds: Dict[str, float] = None
    ):
        self.check_interval = check_interval
        self.metrics_retention_minutes = metrics_retention_minutes
        self.start_time = time.time()
        
        # Default alert thresholds
        self.thresholds = alert_thresholds or {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_usage_percent': 90.0,
            'response_time_ms': 1000.0,
            'error_rate_percent': 5.0
        }
        
        # Metrics storage (in-memory ring buffers)
        max_samples = int(metrics_retention_minutes * 60 / check_interval)
        self.metrics_history: deque = deque(maxlen=max_samples)
        self.health_history: deque = deque(maxlen=max_samples)
        
        # Custom health checks
        self.health_checks: Dict[str, Callable] = {}
        self.custom_metrics: Dict[str, Callable] = {}
        
        # Monitoring state
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        # Register default health checks
        self._register_default_checks()
    
    def _register_default_checks(self):
        """Register default health checks"""
        self.register_health_check('system_resources', self._check_system_resources)
        self.register_health_check('disk_space', self._check_disk_space)
        self.register_health_check('memory_usage', self._check_memory_usage)
        self.register_health_check('cpu_usage', self._check_cpu_usage)
    
    def register_health_check(self, name: str, check_func: Callable) -> None:
        """Register custom health check function"""
        self.health_checks[name] = check_func
        logger.info(f"Registered health check: {name}")
    
    def register_custom_metric(self, name: str, metric_func: Callable) -> None:
        """Register custom metric collection function"""
        self.custom_metrics[name] = metric_func
        logger.info(f"Registered custom metric: {name}")
    
    def _check_system_resources(self) -> Dict[str, Any]:
        """Check overall system resource health"""
        try:
            cpu = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            status = 'healthy'
            issues = []
            
            if cpu > self.thresholds['cpu_percent']:
                status = 'warning'
                issues.append(f"High CPU usage: {cpu:.1f}%")
            
            if memory.percent > self.thresholds['memory_percent']:
                status = 'critical' if memory.percent > 95 else 'warning'
                issues.append(f"High memory usage: {memory.percent:.1f}%")
            
            return {
                'status': status,
                'cpu_percent': cpu,
                'memory_percent': memory.percent,
                'issues': issues
            }
        except Exception as e:
            return {
                'status': 'unknown',
                'error': str(e)
            }
    
    def _check_disk_space(self) -> Dict[str, Any]:
        """Check disk space availability"""
        try:
            disk = psutil.disk_usage('/')
            usage_percent = (disk.used / disk.total) * 100
            
            status = 'healthy'
            if usage_percent > self.thresholds['disk_usage_percent']:
                status = 'critical' if usage_percent > 95 else 'warning'
            
            return {
                'status': status,
                'disk_usage_percent': usage_percent,
                'disk_free_gb': disk.free / (1024**3),
                'disk_total_gb': disk.total / (1024**3)
            }
        except Exception as e:
            return {
                'status': 'unknown',
                'error': str(e)
            }
    
    def _check_memory_usage(self) -> Dict[str, Any]:
        """Detailed memory usage check"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            status = 'healthy'
            issues = []
            
            if memory.percent > 90:
                status = 'critical'
                issues.append("Critical memory usage")
            elif memory.percent > 75:
                status = 'warning'
                issues.append("High memory usage")
            
            if swap.percent > 50:
                status = max(status, 'warning', key=['healthy', 'warning', 'critical'].index)
                issues.append("High swap usage")
            
            return {
                'status': status,
                'memory_used_gb': memory.used / (1024**3),
                'memory_available_gb': memory.available / (1024**3),
                'memory_percent': memory.percent,
                'swap_percent': swap.percent,
                'issues': issues
            }
        except Exception as e:
            return {
                'status': 'unknown',
                'error': str(e)
            }
    
    def _check_cpu_usage(self) -> Dict[str, Any]:
        """Detailed CPU usage check"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1.0)
            cpu_count = psutil.cpu_count()
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else (0, 0, 0)
            
            status = 'healthy'
            issues = []
            
            if cpu_percent > 90:
                status = 'critical'
                issues.append("Critical CPU usage")
            elif cpu_percent > 70:
                status = 'warning'  
                issues.append("High CPU usage")
            
            # Check load average (if available)
            if load_avg[0] > cpu_count * 2:
                status = max(status, 'warning', key=['healthy', 'warning', 'critical'].index)
                issues.append("High system load")
            
            return {
                'status': status,
                'cpu_percent': cpu_percent,
                'cpu_count': cpu_count,
                'load_average': load_avg,
                'issues': issues
            }
        except Exception as e:
            return {
                'status': 'unknown',
                'error': str(e)
            }
    
    def collect_metrics(self) -> PerformanceMetrics:
        """Collect current performance metrics"""
        try:
            # System metrics
            cpu = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Process metrics
            process = psutil.Process()
            active_threads = process.num_threads()
            open_files = len(process.open_files()) if hasattr(process, 'open_files') else 0
            
            # Network I/O
            try:
                net_io = psutil.net_io_counters()
                network_io = {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                    'packets_sent': net_io.packets_sent,
                    'packets_recv': net_io.packets_recv
                }
            except:
                network_io = {}
            
            # Custom metrics
            custom_metrics = {}
            for name, metric_func in self.custom_metrics.items():
                try:
                    custom_metrics[name] = metric_func()
                except Exception as e:
                    logger.warning(f"Custom metric {name} failed: {e}")
                    custom_metrics[name] = 0.0
            
            return PerformanceMetrics(
                timestamp=datetime.now(timezone.utc).isoformat(),
                cpu_percent=cpu,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / (1024**2),
                memory_available_mb=memory.available / (1024**2),
                disk_usage_percent=(disk.used / disk.total) * 100,
                active_threads=active_threads,
                open_files=open_files,
                network_io=network_io,
                custom_metrics=custom_metrics
            )
            
        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")
            return PerformanceMetrics(
                timestamp=datetime.now(timezone.utc).isoformat(),
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_used_mb=0.0,
                memory_available_mb=0.0,
                disk_usage_percent=0.0,
                active_threads=0,
                open_files=0,
                network_io={},
                custom_metrics={}
            )
    
    def run_health_checks(self) -> HealthStatus:
        """Run all registered health checks"""
        start_time = time.time()
        
        all_checks = {}
        all_errors = []
        all_warnings = []
        overall_status = 'healthy'
        
        # Run each health check
        for check_name, check_func in self.health_checks.items():
            try:
                result = check_func()
                all_checks[check_name] = result
                
                # Update overall status
                check_status = result.get('status', 'unknown')
                if check_status == 'critical':
                    overall_status = 'critical'
                elif check_status == 'warning' and overall_status != 'critical':
                    overall_status = 'warning'
                elif check_status == 'unknown' and overall_status == 'healthy':
                    overall_status = 'unknown'
                
                # Collect issues
                if 'error' in result:
                    all_errors.append(f"{check_name}: {result['error']}")
                
                issues = result.get('issues', [])
                if isinstance(issues, list):
                    all_warnings.extend([f"{check_name}: {issue}" for issue in issues])
                elif isinstance(issues, str):
                    all_warnings.append(f"{check_name}: {issues}")
                    
            except Exception as e:
                logger.error(f"Health check {check_name} failed: {e}")
                all_errors.append(f"{check_name}: {str(e)}")
                all_checks[check_name] = {'status': 'unknown', 'error': str(e)}
                if overall_status == 'healthy':
                    overall_status = 'unknown'
        
        # Collect current metrics
        metrics = self.collect_metrics()
        
        # Create health status
        health_status = HealthStatus(
            status=overall_status,
            timestamp=datetime.now(timezone.utc).isoformat(),
            checks=all_checks,
            metrics=asdict(metrics),
            errors=all_errors,
            warnings=all_warnings,
            uptime_seconds=time.time() - self.start_time
        )
        
        # Store in history
        self.health_history.append(health_status)
        self.metrics_history.append(metrics)
        
        return health_status
    
    def get_health_summary(self, last_minutes: int = 10) -> Dict[str, Any]:
        """Get health summary for the last N minutes"""
        cutoff_time = datetime.now(timezone.utc).timestamp() - (last_minutes * 60)
        
        recent_health = [
            h for h in self.health_history 
            if datetime.fromisoformat(h.timestamp.replace('Z', '+00:00')).timestamp() > cutoff_time
        ]
        
        recent_metrics = [
            m for m in self.metrics_history
            if datetime.fromisoformat(m.timestamp.replace('Z', '+00:00')).timestamp() > cutoff_time
        ]
        
        if not recent_health:
            return {'status': 'unknown', 'message': 'No recent health data'}
        
        # Calculate summary statistics
        status_counts = defaultdict(int)
        total_errors = []
        total_warnings = []
        
        for health in recent_health:
            status_counts[health.status] += 1
            total_errors.extend(health.errors)
            total_warnings.extend(health.warnings)
        
        # Current status (most recent)
        current_status = recent_health[-1].status
        
        # Metrics averages
        if recent_metrics:
            avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
            avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
            avg_disk = sum(m.disk_usage_percent for m in recent_metrics) / len(recent_metrics)
        else:
            avg_cpu = avg_memory = avg_disk = 0.0
        
        return {
            'current_status': current_status,
            'time_range_minutes': last_minutes,
            'total_checks': len(recent_health),
            'status_distribution': dict(status_counts),
            'total_errors': len(set(total_errors)),
            'total_warnings': len(set(total_warnings)),
            'average_metrics': {
                'cpu_percent': round(avg_cpu, 2),
                'memory_percent': round(avg_memory, 2),
                'disk_usage_percent': round(avg_disk, 2)
            },
            'uptime_seconds': time.time() - self.start_time,
            'unique_errors': list(set(total_errors))[-5:],  # Last 5 unique errors
            'unique_warnings': list(set(total_warnings))[-5:]  # Last 5 unique warnings
        }
    
    def export_metrics(self, format='json', include_history: bool = True) -> str:
        """Export metrics in various formats"""
        current_health = self.run_health_checks()
        
        if format.lower() == 'prometheus':
            # Prometheus metrics format
            lines = []
            lines.append('# HELP smartcompute_health_status Current health status')
            lines.append('# TYPE smartcompute_health_status gauge')
            
            status_value = {'healthy': 1, 'warning': 0.5, 'critical': 0, 'unknown': -1}
            lines.append(f'smartcompute_health_status {status_value.get(current_health.status, -1)}')
            
            # System metrics
            metrics = current_health.metrics
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    metric_name = f'smartcompute_{key.replace(".", "_")}'
                    lines.append(f'# HELP {metric_name} {key}')
                    lines.append(f'# TYPE {metric_name} gauge')
                    lines.append(f'{metric_name} {value}')
            
            lines.append(f'# HELP smartcompute_uptime_seconds Uptime in seconds')
            lines.append(f'# TYPE smartcompute_uptime_seconds counter')
            lines.append(f'smartcompute_uptime_seconds {current_health.uptime_seconds}')
            
            return '\n'.join(lines)
        
        elif format.lower() == 'json':
            export_data = {
                'current_health': asdict(current_health),
                'summary': self.get_health_summary()
            }
            
            if include_history:
                export_data['metrics_history'] = [asdict(m) for m in list(self.metrics_history)]
                export_data['health_history'] = [asdict(h) for h in list(self.health_history)]
            
            return json.dumps(export_data, indent=2, default=str)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def start_monitoring(self) -> None:
        """Start background health monitoring"""
        if self.monitoring:
            logger.warning("Monitoring already running")
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        logger.info(f"Started health monitoring (interval: {self.check_interval}s)")
    
    def stop_monitoring(self) -> None:
        """Stop background health monitoring"""
        self.monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5.0)
        logger.info("Stopped health monitoring")
    
    def _monitoring_loop(self) -> None:
        """Background monitoring loop"""
        while self.monitoring:
            try:
                health_status = self.run_health_checks()
                
                # Log critical issues
                if health_status.status == 'critical':
                    logger.critical(f"Critical health issues: {health_status.errors}")
                elif health_status.status == 'warning':
                    logger.warning(f"Health warnings: {health_status.warnings}")
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                time.sleep(self.check_interval)

# Flask/FastAPI endpoint helpers
def create_health_endpoint(monitor: HealthMonitor):
    """Create health check endpoint for web frameworks"""
    
    def health_check():
        """Health check endpoint handler"""
        health_status = monitor.run_health_checks()
        
        response_data = {
            'status': health_status.status,
            'timestamp': health_status.timestamp,
            'uptime': health_status.uptime_seconds,
            'checks': {k: v.get('status', 'unknown') for k, v in health_status.checks.items()},
            'errors': health_status.errors,
            'warnings': health_status.warnings
        }
        
        # Return appropriate HTTP status
        if health_status.status == 'healthy':
            return response_data, 200
        elif health_status.status == 'warning':
            return response_data, 200  # Still operational
        elif health_status.status == 'critical':
            return response_data, 503  # Service unavailable
        else:
            return response_data, 500  # Unknown state
    
    def metrics_endpoint(format='json'):
        """Metrics endpoint handler"""
        try:
            metrics_data = monitor.export_metrics(format=format, include_history=False)
            
            if format == 'prometheus':
                return metrics_data, 200, {'Content-Type': 'text/plain; version=0.0.4'}
            else:
                return metrics_data, 200, {'Content-Type': 'application/json'}
        except Exception as e:
            return {'error': str(e)}, 500
    
    return health_check, metrics_endpoint

def main():
    """Example usage of health monitor"""
    monitor = HealthMonitor(check_interval=5.0)
    
    # Add custom metrics
    monitor.register_custom_metric('random_value', lambda: np.random.random())
    
    # Run health check
    health = monitor.run_health_checks()
    print("Health Status:")
    print(json.dumps(asdict(health), indent=2, default=str))
    
    # Export metrics
    print("\nPrometheus Metrics:")
    print(monitor.export_metrics(format='prometheus'))
    
    # Start monitoring for 30 seconds
    print("\nStarting monitoring for 30 seconds...")
    monitor.start_monitoring()
    time.sleep(30)
    monitor.stop_monitoring()
    
    # Get summary
    summary = monitor.get_health_summary(last_minutes=1)
    print("\nHealth Summary:")
    print(json.dumps(summary, indent=2, default=str))

if __name__ == "__main__":
    main()