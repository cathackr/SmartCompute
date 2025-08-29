#!/usr/bin/env python3
"""
SmartCompute Production Performance Monitor
Real-time monitoring of system impact in production environments
"""

import psutil
import time
import threading
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import deque, defaultdict
import statistics
import numpy as np


@dataclass
class ResourceSnapshot:
    """Single point-in-time resource measurement"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_sent_mb: float
    network_recv_mb: float
    process_count: int
    smartcompute_cpu: float
    smartcompute_memory_mb: float
    system_load_1min: float
    system_load_5min: float
    system_load_15min: float


@dataclass
class PerformanceImpact:
    """Analysis of SmartCompute's impact on system performance"""
    cpu_overhead_percent: float
    memory_overhead_mb: float
    disk_io_impact_percent: float
    network_impact_percent: float
    performance_degradation: float
    resource_efficiency_score: float
    impact_severity: str
    recommendations: List[str]


class ProductionResourceMonitor:
    """
    Monitors SmartCompute's resource consumption and system impact
    in production environments
    """
    
    def __init__(self, sampling_interval: int = 5, max_history_hours: int = 24):
        self.sampling_interval = sampling_interval
        self.max_history_samples = (max_history_hours * 3600) // sampling_interval
        self.resource_history: deque = deque(maxlen=self.max_history_samples)
        self.baseline_metrics = None
        self.is_monitoring = False
        self.monitor_thread = None
        self.smartcompute_pids = set()
        self.start_time = None
        
        # Performance thresholds
        self.thresholds = {
            'cpu_overhead_warning': 5.0,  # 5% CPU overhead
            'cpu_overhead_critical': 15.0,  # 15% CPU overhead
            'memory_overhead_warning': 100,  # 100MB memory overhead
            'memory_overhead_critical': 500,  # 500MB memory overhead
            'performance_degradation_warning': 0.1,  # 10% degradation
            'performance_degradation_critical': 0.25,  # 25% degradation
        }
        
        # Initialize SmartCompute process detection
        self._identify_smartcompute_processes()
    
    def _identify_smartcompute_processes(self) -> None:
        """Identify SmartCompute-related processes"""
        try:
            current_pid = os.getpid()
            self.smartcompute_pids.add(current_pid)
            
            # Look for other SmartCompute processes
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if ('smartcompute' in cmdline.lower() or 
                        'smart_compute' in cmdline.lower() or
                        proc.info['name'] and 'python' in proc.info['name'] and 
                        any('smartcompute' in arg.lower() for arg in (proc.info['cmdline'] or []))):
                        self.smartcompute_pids.add(proc.info['pid'])
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            print(f"📊 Monitoring {len(self.smartcompute_pids)} SmartCompute processes")
        
        except Exception as e:
            print(f"⚠️ Error identifying SmartCompute processes: {e}")
    
    def _get_smartcompute_resources(self) -> Tuple[float, float]:
        """Get current CPU and memory usage of SmartCompute processes"""
        total_cpu = 0.0
        total_memory_mb = 0.0
        
        valid_pids = set()
        
        for pid in self.smartcompute_pids.copy():
            try:
                proc = psutil.Process(pid)
                cpu_percent = proc.cpu_percent(interval=None)
                memory_info = proc.memory_info()
                memory_mb = memory_info.rss / (1024 * 1024)  # Convert to MB
                
                total_cpu += cpu_percent
                total_memory_mb += memory_mb
                valid_pids.add(pid)
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Process no longer exists
                continue
        
        # Update valid PIDs
        self.smartcompute_pids = valid_pids
        
        return total_cpu, total_memory_mb
    
    def _take_resource_snapshot(self) -> ResourceSnapshot:
        """Take a snapshot of current system resources"""
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk_io = psutil.disk_io_counters()
        network_io = psutil.net_io_counters()
        
        # System load
        try:
            load_avg = os.getloadavg()
        except (OSError, AttributeError):
            load_avg = (0, 0, 0)
        
        # SmartCompute-specific metrics
        smartcompute_cpu, smartcompute_memory = self._get_smartcompute_resources()
        
        return ResourceSnapshot(
            timestamp=datetime.now(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_used_mb=memory.used / (1024 * 1024),
            disk_io_read_mb=(disk_io.read_bytes if disk_io else 0) / (1024 * 1024),
            disk_io_write_mb=(disk_io.write_bytes if disk_io else 0) / (1024 * 1024),
            network_sent_mb=(network_io.bytes_sent if network_io else 0) / (1024 * 1024),
            network_recv_mb=(network_io.bytes_recv if network_io else 0) / (1024 * 1024),
            process_count=len(psutil.pids()),
            smartcompute_cpu=smartcompute_cpu,
            smartcompute_memory_mb=smartcompute_memory,
            system_load_1min=load_avg[0],
            system_load_5min=load_avg[1],
            system_load_15min=load_avg[2]
        )
    
    def start_monitoring(self) -> None:
        """Start continuous resource monitoring"""
        if self.is_monitoring:
            print("⚠️ Monitoring already active")
            return
        
        self.is_monitoring = True
        self.start_time = datetime.now()
        
        # Take initial baseline if not exists
        if self.baseline_metrics is None:
            print("📊 Establishing performance baseline...")
            self._establish_baseline()
        
        def monitor_loop():
            while self.is_monitoring:
                try:
                    snapshot = self._take_resource_snapshot()
                    self.resource_history.append(snapshot)
                    
                    # Periodic impact analysis
                    if len(self.resource_history) % 60 == 0:  # Every 5 minutes
                        impact = self.analyze_performance_impact()
                        if impact.impact_severity in ['warning', 'critical']:
                            print(f"⚠️ Performance impact detected: {impact.impact_severity}")
                            print(f"   CPU overhead: {impact.cpu_overhead_percent:.1f}%")
                            print(f"   Memory overhead: {impact.memory_overhead_mb:.1f}MB")
                    
                    time.sleep(self.sampling_interval)
                
                except Exception as e:
                    print(f"⚠️ Error in monitoring loop: {e}")
                    time.sleep(self.sampling_interval * 2)  # Wait longer on error
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
        print(f"🚀 Production monitoring started (interval: {self.sampling_interval}s)")
    
    def stop_monitoring(self) -> None:
        """Stop continuous monitoring"""
        self.is_monitoring = False
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)
        
        print("🔚 Production monitoring stopped")
    
    def _establish_baseline(self, duration_minutes: int = 5) -> None:
        """Establish performance baseline before SmartCompute impact"""
        print(f"🔍 Collecting baseline for {duration_minutes} minutes...")
        
        baseline_samples = []
        samples_needed = (duration_minutes * 60) // self.sampling_interval
        
        for i in range(samples_needed):
            snapshot = self._take_resource_snapshot()
            baseline_samples.append(snapshot)
            
            if i % 12 == 0:  # Progress update every minute
                progress = (i / samples_needed) * 100
                print(f"   Progress: {progress:.0f}%")
            
            time.sleep(self.sampling_interval)
        
        # Calculate baseline averages
        if baseline_samples:
            self.baseline_metrics = {
                'cpu_percent': statistics.mean(s.cpu_percent for s in baseline_samples),
                'memory_percent': statistics.mean(s.memory_percent for s in baseline_samples),
                'memory_used_mb': statistics.mean(s.memory_used_mb for s in baseline_samples),
                'disk_io_read_mb': statistics.mean(s.disk_io_read_mb for s in baseline_samples),
                'disk_io_write_mb': statistics.mean(s.disk_io_write_mb for s in baseline_samples),
                'network_sent_mb': statistics.mean(s.network_sent_mb for s in baseline_samples),
                'network_recv_mb': statistics.mean(s.network_recv_mb for s in baseline_samples),
                'system_load_1min': statistics.mean(s.system_load_1min for s in baseline_samples),
            }
            print("✅ Baseline established")
        else:
            print("⚠️ Could not establish baseline")
    
    def analyze_performance_impact(self, analysis_window_hours: int = 1) -> PerformanceImpact:
        """Analyze SmartCompute's impact on system performance"""
        if not self.resource_history or not self.baseline_metrics:
            return self._create_empty_impact_analysis()
        
        # Get recent samples for analysis
        cutoff_time = datetime.now() - timedelta(hours=analysis_window_hours)
        recent_samples = [
            s for s in self.resource_history 
            if s.timestamp > cutoff_time
        ]
        
        if len(recent_samples) < 10:
            return self._create_empty_impact_analysis()
        
        # Calculate current averages
        current_metrics = {
            'cpu_percent': statistics.mean(s.cpu_percent for s in recent_samples),
            'memory_percent': statistics.mean(s.memory_percent for s in recent_samples),
            'memory_used_mb': statistics.mean(s.memory_used_mb for s in recent_samples),
            'disk_io_read_mb': statistics.mean(s.disk_io_read_mb for s in recent_samples),
            'disk_io_write_mb': statistics.mean(s.disk_io_write_mb for s in recent_samples),
            'network_sent_mb': statistics.mean(s.network_sent_mb for s in recent_samples),
            'network_recv_mb': statistics.mean(s.network_recv_mb for s in recent_samples),
        }
        
        # Calculate SmartCompute overhead
        smartcompute_cpu = statistics.mean(s.smartcompute_cpu for s in recent_samples)
        smartcompute_memory = statistics.mean(s.smartcompute_memory_mb for s in recent_samples)
        
        # Calculate impact metrics
        cpu_overhead = smartcompute_cpu
        memory_overhead = smartcompute_memory
        
        # Performance degradation (compared to baseline)
        cpu_degradation = max(0, current_metrics['cpu_percent'] - self.baseline_metrics['cpu_percent'])
        memory_degradation = max(0, current_metrics['memory_percent'] - self.baseline_metrics['memory_percent'])
        
        # Overall performance degradation
        performance_degradation = (cpu_degradation + memory_degradation) / 200  # Normalize to 0-1
        
        # Disk and network impact
        disk_baseline = self.baseline_metrics['disk_io_read_mb'] + self.baseline_metrics['disk_io_write_mb']
        disk_current = current_metrics['disk_io_read_mb'] + current_metrics['disk_io_write_mb']
        disk_impact = ((disk_current - disk_baseline) / max(disk_baseline, 1)) * 100 if disk_baseline > 0 else 0
        
        network_baseline = self.baseline_metrics['network_sent_mb'] + self.baseline_metrics['network_recv_mb']
        network_current = current_metrics['network_sent_mb'] + current_metrics['network_recv_mb']
        network_impact = ((network_current - network_baseline) / max(network_baseline, 1)) * 100 if network_baseline > 0 else 0
        
        # Calculate efficiency score
        efficiency_score = self._calculate_efficiency_score(
            cpu_overhead, memory_overhead, performance_degradation
        )
        
        # Determine severity
        severity = self._determine_impact_severity(
            cpu_overhead, memory_overhead, performance_degradation
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            cpu_overhead, memory_overhead, performance_degradation, severity
        )
        
        return PerformanceImpact(
            cpu_overhead_percent=cpu_overhead,
            memory_overhead_mb=memory_overhead,
            disk_io_impact_percent=disk_impact,
            network_impact_percent=network_impact,
            performance_degradation=performance_degradation,
            resource_efficiency_score=efficiency_score,
            impact_severity=severity,
            recommendations=recommendations
        )
    
    def _create_empty_impact_analysis(self) -> PerformanceImpact:
        """Create empty impact analysis for insufficient data"""
        return PerformanceImpact(
            cpu_overhead_percent=0.0,
            memory_overhead_mb=0.0,
            disk_io_impact_percent=0.0,
            network_impact_percent=0.0,
            performance_degradation=0.0,
            resource_efficiency_score=1.0,
            impact_severity='unknown',
            recommendations=['Insufficient data for analysis']
        )
    
    def _calculate_efficiency_score(self, 
                                   cpu_overhead: float, 
                                   memory_overhead: float, 
                                   degradation: float) -> float:
        """Calculate resource efficiency score (0-1, higher is better)"""
        # Penalize high resource usage
        cpu_penalty = min(cpu_overhead / 20, 1.0)  # Penalty for >20% CPU
        memory_penalty = min(memory_overhead / 1000, 1.0)  # Penalty for >1GB memory
        degradation_penalty = min(degradation * 2, 1.0)  # Penalty for degradation
        
        # Calculate score (1.0 - penalties)
        efficiency = 1.0 - (cpu_penalty + memory_penalty + degradation_penalty) / 3
        return max(0.0, efficiency)
    
    def _determine_impact_severity(self, 
                                  cpu_overhead: float, 
                                  memory_overhead: float, 
                                  degradation: float) -> str:
        """Determine impact severity level"""
        if (cpu_overhead > self.thresholds['cpu_overhead_critical'] or
            memory_overhead > self.thresholds['memory_overhead_critical'] or
            degradation > self.thresholds['performance_degradation_critical']):
            return 'critical'
        elif (cpu_overhead > self.thresholds['cpu_overhead_warning'] or
              memory_overhead > self.thresholds['memory_overhead_warning'] or
              degradation > self.thresholds['performance_degradation_warning']):
            return 'warning'
        else:
            return 'normal'
    
    def _generate_recommendations(self, 
                                 cpu_overhead: float, 
                                 memory_overhead: float, 
                                 degradation: float,
                                 severity: str) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        if cpu_overhead > self.thresholds['cpu_overhead_warning']:
            recommendations.append(f"High CPU overhead ({cpu_overhead:.1f}%) - consider reducing monitoring frequency")
        
        if memory_overhead > self.thresholds['memory_overhead_warning']:
            recommendations.append(f"High memory usage ({memory_overhead:.0f}MB) - review memory management and buffer sizes")
        
        if degradation > self.thresholds['performance_degradation_warning']:
            recommendations.append(f"Performance degradation detected ({degradation:.1%}) - consider optimizing detection algorithms")
        
        if severity == 'critical':
            recommendations.append("CRITICAL: Consider temporarily reducing SmartCompute monitoring scope")
        
        if len(recommendations) == 0:
            recommendations.append("Performance impact within acceptable limits")
        
        return recommendations
    
    def get_monitoring_statistics(self) -> Dict[str, Any]:
        """Get comprehensive monitoring statistics"""
        if not self.resource_history:
            return {'status': 'no_data'}
        
        recent_samples = list(self.resource_history)[-60:]  # Last 60 samples (5 minutes)
        
        stats = {
            'monitoring_status': 'active' if self.is_monitoring else 'stopped',
            'monitoring_duration_hours': (
                (datetime.now() - self.start_time).total_seconds() / 3600 
                if self.start_time else 0
            ),
            'total_samples': len(self.resource_history),
            'smartcompute_processes': len(self.smartcompute_pids),
            'current_performance': {
                'cpu_overhead': statistics.mean(s.smartcompute_cpu for s in recent_samples),
                'memory_overhead_mb': statistics.mean(s.smartcompute_memory_mb for s in recent_samples),
                'system_cpu': statistics.mean(s.cpu_percent for s in recent_samples),
                'system_memory': statistics.mean(s.memory_percent for s in recent_samples),
            } if recent_samples else {},
            'baseline_available': self.baseline_metrics is not None,
            'latest_impact_analysis': asdict(self.analyze_performance_impact())
        }
        
        return stats
    
    def export_performance_report(self, filename: str = None) -> str:
        """Export detailed performance report"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"smartcompute_performance_report_{timestamp}.json"
        
        report = {
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'monitoring_period_hours': (
                    (datetime.now() - self.start_time).total_seconds() / 3600 
                    if self.start_time else 0
                ),
                'total_samples': len(self.resource_history),
                'sampling_interval_seconds': self.sampling_interval
            },
            'baseline_metrics': self.baseline_metrics,
            'performance_impact': asdict(self.analyze_performance_impact()),
            'monitoring_statistics': self.get_monitoring_statistics(),
            'configuration': {
                'thresholds': self.thresholds,
                'smartcompute_processes': list(self.smartcompute_pids)
            }
        }
        
        # Add historical data summary
        if self.resource_history:
            samples_data = [asdict(s) for s in self.resource_history]
            # Convert datetime to string for JSON serialization
            for sample in samples_data:
                sample['timestamp'] = sample['timestamp'].isoformat()
            
            report['historical_data_summary'] = {
                'sample_count': len(samples_data),
                'time_range': {
                    'start': samples_data[0]['timestamp'],
                    'end': samples_data[-1]['timestamp']
                },
                # Include statistical summaries instead of raw data to keep file size reasonable
                'cpu_stats': {
                    'min': min(s['cpu_percent'] for s in samples_data),
                    'max': max(s['cpu_percent'] for s in samples_data),
                    'avg': statistics.mean(s['cpu_percent'] for s in samples_data),
                    'std': statistics.stdev(s['cpu_percent'] for s in samples_data) if len(samples_data) > 1 else 0
                },
                'smartcompute_cpu_stats': {
                    'min': min(s['smartcompute_cpu'] for s in samples_data),
                    'max': max(s['smartcompute_cpu'] for s in samples_data),
                    'avg': statistics.mean(s['smartcompute_cpu'] for s in samples_data),
                    'std': statistics.stdev(s['smartcompute_cpu'] for s in samples_data) if len(samples_data) > 1 else 0
                },
                'smartcompute_memory_stats': {
                    'min': min(s['smartcompute_memory_mb'] for s in samples_data),
                    'max': max(s['smartcompute_memory_mb'] for s in samples_data),
                    'avg': statistics.mean(s['smartcompute_memory_mb'] for s in samples_data),
                    'std': statistics.stdev(s['smartcompute_memory_mb'] for s in samples_data) if len(samples_data) > 1 else 0
                }
            }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📊 Performance report exported: {filename}")
        return filename


if __name__ == "__main__":
    # Demo production monitoring
    monitor = ProductionResourceMonitor(sampling_interval=2)
    
    print("SmartCompute Production Performance Monitor")
    print("Starting 30-second demo...")
    
    monitor.start_monitoring()
    
    try:
        time.sleep(30)
        
        # Analyze impact
        impact = monitor.analyze_performance_impact()
        print(f"\nPerformance Impact Analysis:")
        print(f"CPU Overhead: {impact.cpu_overhead_percent:.1f}%")
        print(f"Memory Overhead: {impact.memory_overhead_mb:.1f}MB")
        print(f"Performance Degradation: {impact.performance_degradation:.1%}")
        print(f"Efficiency Score: {impact.resource_efficiency_score:.2f}")
        print(f"Impact Severity: {impact.impact_severity}")
        
        # Export report
        report_file = monitor.export_performance_report()
        print(f"Report saved: {report_file}")
        
    finally:
        monitor.stop_monitoring()