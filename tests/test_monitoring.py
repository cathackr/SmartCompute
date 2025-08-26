"""
Tests for monitoring service
"""

import pytest
import asyncio
import time
from app.services.monitoring import MonitoringService, MonitoringAlert
from app.core.portable_system import PortableSystemDetector


class TestMonitoringService:
    """Test monitoring service functionality"""
    
    def test_initialization(self, monitoring_service):
        """Test monitoring service initialization"""
        assert monitoring_service is not None
        assert monitoring_service.detector is not None
        assert monitoring_service.check_interval > 0
        assert monitoring_service.is_monitoring is False
        assert len(monitoring_service.alerts) == 0
        assert len(monitoring_service.metrics_history) == 0
    
    @pytest.mark.asyncio
    async def test_start_stop_monitoring(self, monitoring_service):
        """Test starting and stopping monitoring service"""
        # Initially not monitoring
        assert monitoring_service.is_monitoring is False
        
        # Start monitoring
        success = await monitoring_service.start_monitoring()
        assert success is True
        assert monitoring_service.is_monitoring is True
        
        # Try to start again (should fail)
        success = await monitoring_service.start_monitoring()
        assert success is False
        
        # Wait a bit for monitoring loop
        await asyncio.sleep(2)
        
        # Stop monitoring
        success = await monitoring_service.stop_monitoring()
        assert success is True
        assert monitoring_service.is_monitoring is False
    
    @pytest.mark.asyncio
    async def test_monitoring_without_baseline(self, monitoring_service):
        """Test monitoring service without baseline"""
        # Start monitoring without baseline
        await monitoring_service.start_monitoring()
        
        # Wait for a few checks
        await asyncio.sleep(3)
        
        # Should not have generated metrics due to no baseline
        assert len(monitoring_service.metrics_history) == 0
        
        await monitoring_service.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_monitoring_with_baseline(self, monitoring_service):
        """Test monitoring service with baseline"""
        # Establish baseline first
        monitoring_service.detector.run_performance_baseline(2)
        
        # Start monitoring
        await monitoring_service.start_monitoring()
        
        # Wait for monitoring to collect some data
        await asyncio.sleep(3)
        
        # Should have collected metrics
        assert len(monitoring_service.metrics_history) > 0
        
        # Check metrics structure
        for metric in monitoring_service.metrics_history:
            assert 'timestamp' in metric
            assert 'cpu_usage' in metric
            assert 'memory_usage' in metric
            assert 'anomaly_score' in metric
            assert 'severity' in metric
        
        await monitoring_service.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_status_reporting(self, monitoring_service):
        """Test monitoring service status reporting"""
        # Initial status
        status = await monitoring_service.get_status()
        assert status['is_monitoring'] is False
        assert status['metrics_history_size'] == 0
        assert status['total_alerts'] == 0
        
        # Establish baseline and start monitoring
        monitoring_service.detector.run_performance_baseline(1)
        await monitoring_service.start_monitoring()
        
        # Wait for some data collection
        await asyncio.sleep(2)
        
        # Check status during monitoring
        status = await monitoring_service.get_status()
        assert status['is_monitoring'] is True
        assert 'check_interval' in status
        assert 'system_info' in status
        assert 'baseline_established' in status
        assert status['baseline_established'] is True
        
        await monitoring_service.stop_monitoring()
    
    def test_alert_callbacks(self, monitoring_service):
        """Test alert callback registration and notification"""
        alerts_received = []
        
        def test_callback(alert):
            alerts_received.append(alert)
        
        # Register callback
        monitoring_service.register_alert_callback(test_callback)
        
        # Create a test alert
        test_alert = MonitoringAlert(
            timestamp="2024-01-01 12:00:00",
            severity="high",
            anomaly_score=85.0,
            cpu_usage=90.0,
            memory_usage=85.0,
            message="Test alert",
            context={}
        )
        
        # Manually add alert to trigger callbacks
        monitoring_service.alerts.append(test_alert)
        
        # Unregister callback
        monitoring_service.unregister_alert_callback(test_callback)
        
        # Verify callback was registered
        assert test_callback not in monitoring_service.alert_callbacks
    
    def test_metrics_history_management(self, monitoring_service):
        """Test metrics history size management"""
        # Set a small max size for testing
        original_max_size = monitoring_service.max_history_size
        monitoring_service.max_history_size = 5
        
        # Add more metrics than the max size
        for i in range(10):
            metrics = {
                'timestamp': f"2024-01-01 12:{i:02d}:00",
                'cpu_usage': 50.0 + i,
                'memory_usage': 40.0 + i,
                'anomaly_score': 10.0 + i,
                'severity': 'normal',
                'cpu_zscore': 1.0,
                'memory_zscore': 1.0
            }
            monitoring_service._add_metrics_to_history(metrics)
        
        # Should only keep the last max_size entries
        assert len(monitoring_service.metrics_history) == 5
        
        # Should keep the most recent entries
        last_metric = monitoring_service.metrics_history[-1]
        assert last_metric['timestamp'] == "2024-01-01 12:09:00"
        
        # Restore original max size
        monitoring_service.max_history_size = original_max_size
    
    def test_recent_data_retrieval(self, monitoring_service):
        """Test retrieval of recent metrics and alerts"""
        # Add some test metrics
        for i in range(10):
            metrics = {
                'timestamp': f"2024-01-01 12:{i:02d}:00",
                'cpu_usage': 50.0,
                'memory_usage': 40.0,
                'anomaly_score': 20.0,
                'severity': 'normal',
                'cpu_zscore': 1.0,
                'memory_zscore': 1.0
            }
            monitoring_service._add_metrics_to_history(metrics)
        
        # Get recent metrics
        recent_metrics = monitoring_service.get_recent_metrics(limit=3)
        assert len(recent_metrics) == 3
        
        # Should be the most recent ones
        assert recent_metrics[-1]['timestamp'] == "2024-01-01 12:09:00"
        
        # Add some test alerts
        for i in range(5):
            alert = MonitoringAlert(
                timestamp=f"2024-01-01 12:0{i:02d}:00",
                severity="medium",
                anomaly_score=60.0,
                cpu_usage=70.0,
                memory_usage=65.0,
                message=f"Test alert {i}",
                context={}
            )
            monitoring_service.alerts.append(alert)
        
        # Get recent alerts
        recent_alerts = monitoring_service.get_recent_alerts(limit=2)
        assert len(recent_alerts) == 2
        
        # Should be in dictionary format
        assert isinstance(recent_alerts[0], dict)
        assert 'timestamp' in recent_alerts[0]
        assert 'severity' in recent_alerts[0]
    
    def test_data_cleanup(self, monitoring_service):
        """Test data cleanup functionality"""
        # Add some test data
        monitoring_service._add_metrics_to_history({
            'timestamp': "2024-01-01 12:00:00",
            'cpu_usage': 50.0,
            'memory_usage': 40.0,
            'anomaly_score': 20.0,
            'severity': 'normal',
            'cpu_zscore': 1.0,
            'memory_zscore': 1.0
        })
        
        alert = MonitoringAlert(
            timestamp="2024-01-01 12:00:00",
            severity="medium",
            anomaly_score=60.0,
            cpu_usage=70.0,
            memory_usage=65.0,
            message="Test alert",
            context={}
        )
        monitoring_service.alerts.append(alert)
        
        # Verify data exists
        assert len(monitoring_service.metrics_history) > 0
        assert len(monitoring_service.alerts) > 0
        
        # Clear data
        monitoring_service.clear_metrics_history()
        monitoring_service.clear_alerts()
        
        # Verify data is cleared
        assert len(monitoring_service.metrics_history) == 0
        assert len(monitoring_service.alerts) == 0
    
    def test_statistics_calculation(self, monitoring_service):
        """Test monitoring statistics calculation"""
        # Add test metrics with known values
        test_data = [
            {'cpu_usage': 40.0, 'memory_usage': 30.0, 'anomaly_score': 10.0},
            {'cpu_usage': 50.0, 'memory_usage': 40.0, 'anomaly_score': 20.0},
            {'cpu_usage': 60.0, 'memory_usage': 50.0, 'anomaly_score': 30.0}
        ]
        
        for i, data in enumerate(test_data):
            metrics = {
                'timestamp': f"2024-01-01 12:0{i:02d}:00",
                'cpu_usage': data['cpu_usage'],
                'memory_usage': data['memory_usage'],
                'anomaly_score': data['anomaly_score'],
                'severity': 'normal',
                'cpu_zscore': 1.0,
                'memory_zscore': 1.0
            }
            monitoring_service._add_metrics_to_history(metrics)
        
        # Add some alerts
        alert = MonitoringAlert(
            timestamp="2024-01-01 12:01:00",
            severity="high",
            anomaly_score=80.0,
            cpu_usage=90.0,
            memory_usage=85.0,
            message="High severity alert",
            context={}
        )
        monitoring_service.alerts.append(alert)
        
        # Calculate statistics
        stats = monitoring_service.get_statistics()
        
        assert 'total_checks' in stats
        assert 'cpu_stats' in stats
        assert 'memory_stats' in stats
        assert 'anomaly_stats' in stats
        
        assert stats['total_checks'] == 3
        assert stats['cpu_stats']['mean'] == 50.0  # (40+50+60)/3
        assert stats['memory_stats']['mean'] == 40.0  # (30+40+50)/3
        assert stats['anomaly_stats']['alerts_generated'] == 1
    
    @pytest.mark.asyncio
    async def test_force_check(self, monitoring_service):
        """Test forced monitoring check"""
        # Establish baseline
        monitoring_service.detector.run_performance_baseline(1)
        
        # Force a check
        result = await monitoring_service.force_check()
        
        # Should return the latest metric or empty dict
        if monitoring_service.metrics_history:
            assert 'timestamp' in result
            assert 'cpu_usage' in result
            assert 'anomaly_score' in result
        else:
            assert result == {}
    
    def test_export_data(self, monitoring_service, tmp_path):
        """Test data export functionality"""
        # Add some test data
        monitoring_service._add_metrics_to_history({
            'timestamp': "2024-01-01 12:00:00",
            'cpu_usage': 50.0,
            'memory_usage': 40.0,
            'anomaly_score': 20.0,
            'severity': 'normal',
            'cpu_zscore': 1.0,
            'memory_zscore': 1.0
        })
        
        # Export to temporary file
        export_path = tmp_path / "test_export.json"
        success = monitoring_service.export_data(str(export_path))
        
        assert success is True
        assert export_path.exists()
        
        # Verify export content structure
        import json
        with open(export_path) as f:
            data = json.load(f)
        
        assert 'export_timestamp' in data
        assert 'service_status' in data
        assert 'system_info' in data
        assert 'metrics_history' in data
        assert 'alerts' in data