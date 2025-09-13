"""
Pytest configuration and fixtures
"""

import pytest
import os
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.smart_compute import SmartComputeEngine
from app.core.portable_system import PortableSystemDetector
from app.services.monitoring import MonitoringService
from app.core.database import get_db, create_tables, drop_tables, engine
from app.security.audit_system import SecurityAuditSystem

import numpy as np


@pytest.fixture(scope="session")
def test_database():
    """Setup test database"""
    # Use in-memory SQLite for tests
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    create_tables()
    yield
    # Cleanup after all tests
    drop_tables()


@pytest.fixture
def smart_engine():
    """SmartCompute engine fixture"""
    return SmartComputeEngine(history_path="test_history.json")


@pytest.fixture
def portable_detector():
    """Portable system detector fixture"""
    try:
        return PortableSystemDetector()
    except Exception as e:
        print(f"Warning: Could not initialize PortableSystemDetector: {e}")
        # Return a mock object for testing
        class MockDetector:
            def __init__(self):
                self.system_info = {
                    'os': 'Linux',
                    'arch': 'x86_64',
                    'cpu_model': 'Test CPU',
                    'cpu_cores': 4,
                    'ram_gb': 8.0,
                    'gpu_type': 'None'
                }
                self.baseline_metrics = {}
            
            def detect_anomalies(self):
                return {
                    'anomaly_score': 1.0,
                    'severity': 'low',
                    'cpu_current': 10.0,
                    'memory_current': 50.0
                }
            
            def run_performance_baseline(self, duration):
                return {'cpu_avg': 10.0, 'memory_avg': 50.0}
            
            def generate_report(self):
                return {
                    'system_profile': self.system_info,
                    'optimization_applied': {'optimizations_applied': [], 'performance_gain': 0},
                    'recommendations': ['Test recommendation']
                }
        return MockDetector()


@pytest.fixture
def monitoring_service(portable_detector):
    """Monitoring service fixture"""
    return MonitoringService(portable_detector, check_interval=1)


@pytest.fixture
def test_matrices():
    """Test matrices for computation tests"""
    np.random.seed(42)
    return {
        'small': (np.random.rand(10, 10), np.random.rand(10, 10)),
        'medium': (np.random.rand(100, 100), np.random.rand(100, 100)),
        'large': (np.random.rand(200, 200), np.random.rand(200, 200))
    }


@pytest.fixture
def security_audit_system():
    """Security audit system fixture"""
    return SecurityAuditSystem("enterprise", storage_path="test_security/")


@pytest.fixture
def cleanup_test_files():
    """Cleanup test files after tests"""
    yield
    # Cleanup
    test_files = [
        "test_history.json",
        "test_smartcompute.db",
        "test_report.json"
    ]
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)