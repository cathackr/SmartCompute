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
    return PortableSystemDetector()


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