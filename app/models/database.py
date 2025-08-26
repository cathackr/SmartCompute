"""
SmartCompute Database Models
SQLAlchemy models for performance monitoring and anomaly detection
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Dict, Any, Optional

Base = declarative_base()


class SystemProfile(Base):
    """System profile information"""
    __tablename__ = "system_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    profile_name = Column(String(100), unique=True, index=True)
    os_name = Column(String(50), nullable=False)
    architecture = Column(String(50), nullable=False)
    cpu_model = Column(String(200), nullable=False)
    cpu_cores = Column(Integer, nullable=False)
    cpu_threads = Column(Integer, nullable=False)
    ram_gb = Column(Float, nullable=False)
    gpu_type = Column(String(100), nullable=False)
    gpu_available = Column(Boolean, default=False)
    cuda_available = Column(Boolean, default=False)
    opencl_available = Column(Boolean, default=False)
    optimization_strategy = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PerformanceBaseline(Base):
    """Performance baseline measurements"""
    __tablename__ = "performance_baselines"
    
    id = Column(Integer, primary_key=True, index=True)
    system_profile_id = Column(Integer, nullable=False)
    baseline_name = Column(String(100), nullable=False)
    cpu_mean = Column(Float, nullable=False)
    cpu_stdev = Column(Float, nullable=False)
    memory_mean = Column(Float, nullable=False)
    memory_stdev = Column(Float, nullable=False)
    measurement_duration = Column(Integer, nullable=False)  # seconds
    sample_count = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)


class ComputationOptimization(Base):
    """Computation optimization results"""
    __tablename__ = "computation_optimizations"
    
    id = Column(Integer, primary_key=True, index=True)
    system_profile_id = Column(Integer, nullable=False)
    operation_type = Column(String(50), nullable=False)  # e.g., 'matrix_multiply'
    operation_key = Column(String(200), nullable=False)  # e.g., 'mult_500x500'
    precision_required = Column(Float, nullable=False)
    speed_priority = Column(Float, nullable=False)
    chosen_method = Column(String(50), nullable=False)  # 'fast' or 'precise'
    execution_time = Column(Float, nullable=False)
    accuracy_achieved = Column(Float, nullable=False)
    speedup_factor = Column(Float, nullable=False)
    meets_precision = Column(Boolean, nullable=False)
    metrics = Column(JSON)  # Additional metrics as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AnomalyDetection(Base):
    """Anomaly detection results"""
    __tablename__ = "anomaly_detections"
    
    id = Column(Integer, primary_key=True, index=True)
    system_profile_id = Column(Integer, nullable=False)
    baseline_id = Column(Integer, nullable=False)
    anomaly_score = Column(Float, nullable=False)
    severity = Column(String(20), nullable=False)  # 'normal', 'low', 'medium', 'high'
    cpu_usage = Column(Float, nullable=False)
    memory_usage = Column(Float, nullable=False)
    cpu_zscore = Column(Float, nullable=False)
    memory_zscore = Column(Float, nullable=False)
    additional_metrics = Column(JSON)  # Additional metrics as JSON
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    alert_generated = Column(Boolean, default=False)


class MonitoringSession(Base):
    """Monitoring session information"""
    __tablename__ = "monitoring_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    system_profile_id = Column(Integer, nullable=False)
    baseline_id = Column(Integer, nullable=False)
    session_name = Column(String(100), nullable=False)
    check_interval = Column(Integer, nullable=False)  # seconds
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    total_checks = Column(Integer, default=0)
    total_alerts = Column(Integer, default=0)
    status = Column(String(20), default="active")  # 'active', 'stopped', 'error'


class SecurityAlert(Base):
    """Security alerts from anomaly detection"""
    __tablename__ = "security_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    monitoring_session_id = Column(Integer, nullable=False)
    anomaly_detection_id = Column(Integer, nullable=False)
    severity = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    anomaly_score = Column(Float, nullable=False)
    cpu_usage = Column(Float, nullable=False)
    memory_usage = Column(Float, nullable=False)
    context = Column(JSON)  # Alert context as JSON
    acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    acknowledged_by = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PerformanceReport(Base):
    """Generated performance reports"""
    __tablename__ = "performance_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    system_profile_id = Column(Integer, nullable=False)
    report_type = Column(String(50), nullable=False)  # 'audit', 'optimization', 'security'
    title = Column(String(200), nullable=False)
    summary = Column(Text, nullable=False)
    report_data = Column(JSON, nullable=False)  # Full report data as JSON
    recommendations = Column(JSON)  # Recommendations as JSON array
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    generated_by = Column(String(100), nullable=True)  # User or service name


class OptimizationHistory(Base):
    """Historical optimization performance data"""
    __tablename__ = "optimization_history"
    
    id = Column(Integer, primary_key=True, index=True)
    system_profile_id = Column(Integer, nullable=False)
    operation_key = Column(String(200), nullable=False)
    precise_time = Column(Float, nullable=False)
    fast_time = Column(Float, nullable=False)
    accuracy = Column(Float, nullable=False)
    speedup = Column(Float, nullable=False)
    chosen_method = Column(String(50), nullable=False)
    sample_count = Column(Integer, default=1)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'operation_key': self.operation_key,
            'precise_time': self.precise_time,
            'fast_time': self.fast_time,
            'accuracy': self.accuracy,
            'speedup': self.speedup,
            'chosen_method': self.chosen_method,
            'sample_count': self.sample_count,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }


# Helper functions for database operations

def create_system_profile_dict(detector) -> Dict[str, Any]:
    """Create system profile dictionary from PortableSystemDetector"""
    info = detector.system_info
    profile = detector.optimization_profile
    
    return {
        'profile_name': f"{info['arch']}_{info['os']}_{int(info['ram_gb'])}GB",
        'os_name': info['os'],
        'architecture': info['arch'],
        'cpu_model': info['cpu_model'],
        'cpu_cores': info['cpu_cores'],
        'cpu_threads': info['cpu_threads'],
        'ram_gb': info['ram_gb'],
        'gpu_type': info['gpu_type'],
        'gpu_available': info['gpu_available'],
        'cuda_available': info['cuda_available'],
        'opencl_available': info['opencl_available'],
        'optimization_strategy': profile['strategy']
    }


def create_baseline_dict(baseline_metrics: Dict[str, float], duration: int, sample_count: int) -> Dict[str, Any]:
    """Create baseline dictionary from metrics"""
    return {
        'baseline_name': f"baseline_{datetime.now().strftime('%Y%m%d_%H%M')}",
        'cpu_mean': baseline_metrics['cpu_mean'],
        'cpu_stdev': baseline_metrics['cpu_stdev'],
        'memory_mean': baseline_metrics['memory_mean'],
        'memory_stdev': baseline_metrics['memory_stdev'],
        'measurement_duration': duration,
        'sample_count': sample_count
    }


def create_optimization_dict(
    operation_key: str, 
    precision: float, 
    speed_priority: float, 
    result: Dict[str, Any]
) -> Dict[str, Any]:
    """Create optimization dictionary from result"""
    return {
        'operation_type': 'matrix_multiply',  # Can be extended for other operations
        'operation_key': operation_key,
        'precision_required': precision,
        'speed_priority': speed_priority,
        'chosen_method': result['choice'],
        'execution_time': result['time'],
        'accuracy_achieved': result['accuracy'],
        'speedup_factor': result['speedup'],
        'meets_precision': result['meets_precision'],
        'metrics': result['metrics']
    }


def create_anomaly_dict(anomaly_result: Dict[str, Any]) -> Dict[str, Any]:
    """Create anomaly dictionary from detection result"""
    return {
        'anomaly_score': anomaly_result['anomaly_score'],
        'severity': anomaly_result['severity'],
        'cpu_usage': anomaly_result['cpu_current'],
        'memory_usage': anomaly_result['memory_current'],
        'cpu_zscore': anomaly_result['cpu_zscore'],
        'memory_zscore': anomaly_result['memory_zscore'],
        'additional_metrics': {
            'detection_timestamp': datetime.now().isoformat()
        }
    }