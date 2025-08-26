"""
SmartCompute Monitoring Service
Continuous performance monitoring and anomaly detection
"""

import asyncio
import time
import json
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
import psutil

from ..core.portable_system import PortableSystemDetector


@dataclass
class MonitoringAlert:
    """Monitoring alert data structure"""
    timestamp: str
    severity: str
    anomaly_score: float
    cpu_usage: float
    memory_usage: float
    message: str
    context: Dict[str, Any]


class MonitoringService:
    """
    Continuous monitoring service for performance anomaly detection
    """
    
    def __init__(self, detector: PortableSystemDetector, check_interval: int = 5):
        """
        Initialize monitoring service
        
        Args:
            detector: PortableSystemDetector instance
            check_interval: Monitoring check interval in seconds
        """
        self.detector = detector
        self.check_interval = check_interval
        self.is_monitoring = False
        self.monitoring_task: Optional[asyncio.Task] = None
        
        self.alerts: List[MonitoringAlert] = []
        self.alert_callbacks: List[Callable] = []
        
        self.metrics_history: List[Dict[str, Any]] = []
        self.max_history_size = 1000
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    async def start_monitoring(self) -> bool:
        """
        Start continuous monitoring
        
        Returns:
            True if started successfully, False if already running
        """
        if self.is_monitoring:
            return False
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.logger.info("SmartCompute monitoring service started")
        return True
    
    async def stop_monitoring(self) -> bool:
        """
        Stop continuous monitoring
        
        Returns:
            True if stopped successfully
        """
        if not self.is_monitoring:
            return True
        
        self.is_monitoring = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
            self.monitoring_task = None
        
        self.logger.info("SmartCompute monitoring service stopped")
        return True
    
    async def stop(self):
        """Alias for stop_monitoring for compatibility"""
        await self.stop_monitoring()
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        self.logger.info(f"Monitoring loop started with {self.check_interval}s interval")
        
        while self.is_monitoring:
            try:
                await self._perform_check()
                await asyncio.sleep(self.check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def _perform_check(self):
        """Perform a single monitoring check"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            # Get current system metrics
            anomaly_result = self.detector.detect_anomalies()
            
            if 'error' in anomaly_result:
                self.logger.warning(f"Anomaly detection failed: {anomaly_result['error']}")
                return
            
            # Store metrics in history
            metrics = {
                'timestamp': timestamp,
                'cpu_usage': anomaly_result['cpu_current'],
                'memory_usage': anomaly_result['memory_current'],
                'anomaly_score': anomaly_result['anomaly_score'],
                'severity': anomaly_result['severity'],
                'cpu_zscore': anomaly_result['cpu_zscore'],
                'memory_zscore': anomaly_result['memory_zscore']
            }
            
            self._add_metrics_to_history(metrics)
            
            # Check for alerts
            await self._check_for_alerts(anomaly_result, timestamp)
            
        except Exception as e:
            self.logger.error(f"Error performing monitoring check: {e}")
    
    def _add_metrics_to_history(self, metrics: Dict[str, Any]):
        """Add metrics to history with size limit"""
        self.metrics_history.append(metrics)
        
        # Maintain history size limit
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history = self.metrics_history[-self.max_history_size:]
    
    async def _check_for_alerts(self, anomaly_result: Dict[str, Any], timestamp: str):
        """Check for alert conditions and generate alerts"""
        severity = anomaly_result['severity']
        anomaly_score = anomaly_result['anomaly_score']
        
        # Generate alert for medium and high severity
        if severity in ['medium', 'high']:
            alert = MonitoringAlert(
                timestamp=timestamp,
                severity=severity,
                anomaly_score=anomaly_score,
                cpu_usage=anomaly_result['cpu_current'],
                memory_usage=anomaly_result['memory_current'],
                message=self._generate_alert_message(anomaly_result),
                context={
                    'cpu_zscore': anomaly_result['cpu_zscore'],
                    'memory_zscore': anomaly_result['memory_zscore']
                }
            )
            
            self.alerts.append(alert)
            
            # Limit alerts history
            if len(self.alerts) > 100:
                self.alerts = self.alerts[-100:]
            
            # Notify callbacks
            await self._notify_alert_callbacks(alert)
            
            self.logger.warning(f"ALERT: {alert.message}")
    
    def _generate_alert_message(self, anomaly_result: Dict[str, Any]) -> str:
        """Generate alert message based on anomaly result"""
        severity = anomaly_result['severity']
        score = anomaly_result['anomaly_score']
        cpu = anomaly_result['cpu_current']
        memory = anomaly_result['memory_current']
        
        return (f"{severity.upper()} anomaly detected (score: {score:.1f}). "
                f"CPU: {cpu:.1f}%, Memory: {memory:.1f}%")
    
    async def _notify_alert_callbacks(self, alert: MonitoringAlert):
        """Notify registered alert callbacks"""
        for callback in self.alert_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(alert)
                else:
                    callback(alert)
            except Exception as e:
                self.logger.error(f"Error in alert callback: {e}")
    
    def register_alert_callback(self, callback: Callable):
        """Register callback for alert notifications"""
        self.alert_callbacks.append(callback)
    
    def unregister_alert_callback(self, callback: Callable):
        """Unregister alert callback"""
        if callback in self.alert_callbacks:
            self.alert_callbacks.remove(callback)
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current monitoring service status"""
        return {
            'is_monitoring': self.is_monitoring,
            'check_interval': self.check_interval,
            'metrics_history_size': len(self.metrics_history),
            'total_alerts': len(self.alerts),
            'recent_alerts': len([a for a in self.alerts 
                                if (datetime.now() - datetime.strptime(a.timestamp, '%Y-%m-%d %H:%M:%S')).seconds < 3600]),
            'last_check': self.metrics_history[-1]['timestamp'] if self.metrics_history else None,
            'baseline_established': bool(self.detector.baseline_metrics),
            'system_info': {
                'cpu_cores': self.detector.system_info['cpu_cores'],
                'ram_gb': self.detector.system_info['ram_gb'],
                'architecture': self.detector.system_info['arch']
            }
        }
    
    def get_recent_metrics(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent metrics history"""
        return self.metrics_history[-limit:] if self.metrics_history else []
    
    def get_recent_alerts(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        recent_alerts = self.alerts[-limit:] if self.alerts else []
        return [asdict(alert) for alert in recent_alerts]
    
    def clear_alerts(self):
        """Clear all alerts"""
        self.alerts.clear()
        self.logger.info("All alerts cleared")
    
    def clear_metrics_history(self):
        """Clear metrics history"""
        self.metrics_history.clear()
        self.logger.info("Metrics history cleared")
    
    async def force_check(self) -> Dict[str, Any]:
        """Force an immediate monitoring check"""
        await self._perform_check()
        if self.metrics_history:
            return self.metrics_history[-1]
        return {}
    
    def export_data(self, filepath: str):
        """Export monitoring data to JSON file"""
        data = {
            'export_timestamp': datetime.now().isoformat(),
            'service_status': {
                'is_monitoring': self.is_monitoring,
                'check_interval': self.check_interval
            },
            'system_info': self.detector.system_info,
            'baseline_metrics': self.detector.baseline_metrics,
            'metrics_history': self.metrics_history,
            'alerts': [asdict(alert) for alert in self.alerts]
        }
        
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            self.logger.info(f"Monitoring data exported to {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to export data: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get monitoring statistics"""
        if not self.metrics_history:
            return {'error': 'No metrics data available'}
        
        # Calculate statistics
        cpu_values = [m['cpu_usage'] for m in self.metrics_history]
        memory_values = [m['memory_usage'] for m in self.metrics_history]
        anomaly_scores = [m['anomaly_score'] for m in self.metrics_history]
        
        import statistics
        
        return {
            'monitoring_duration_hours': len(self.metrics_history) * self.check_interval / 3600,
            'total_checks': len(self.metrics_history),
            'cpu_stats': {
                'mean': statistics.mean(cpu_values),
                'max': max(cpu_values),
                'min': min(cpu_values),
                'stdev': statistics.stdev(cpu_values) if len(cpu_values) > 1 else 0
            },
            'memory_stats': {
                'mean': statistics.mean(memory_values),
                'max': max(memory_values),
                'min': min(memory_values),
                'stdev': statistics.stdev(memory_values) if len(memory_values) > 1 else 0
            },
            'anomaly_stats': {
                'mean_score': statistics.mean(anomaly_scores),
                'max_score': max(anomaly_scores),
                'alerts_generated': len(self.alerts),
                'high_severity_alerts': len([a for a in self.alerts if a.severity == 'high']),
                'medium_severity_alerts': len([a for a in self.alerts if a.severity == 'medium'])
            }
        }