"""
Tests for portable system detection and optimization
"""

import pytest
import time
from app.core.portable_system import PortableSystemDetector


class TestPortableSystemDetector:
    """Test portable system detection functionality"""
    
    def test_initialization(self, portable_detector):
        """Test system detector initialization"""
        assert portable_detector is not None
        assert portable_detector.system_info is not None
        assert portable_detector.optimization_profile is not None
        
        # Check required system info fields
        required_fields = [
            'os', 'arch', 'cpu_model', 'cpu_cores', 
            'cpu_threads', 'ram_gb', 'gpu_type'
        ]
        for field in required_fields:
            assert field in portable_detector.system_info
    
    def test_system_detection(self, portable_detector):
        """Test system detection accuracy"""
        info = portable_detector.system_info
        
        # Basic sanity checks
        assert info['cpu_cores'] > 0
        assert info['cpu_threads'] >= info['cpu_cores']
        assert info['ram_gb'] > 0
        assert info['os'] in ['Linux', 'Darwin', 'Windows']
        assert len(info['cpu_model']) > 0
    
    def test_optimization_profile_creation(self, portable_detector):
        """Test optimization profile creation"""
        profile = portable_detector.optimization_profile
        
        assert 'strategy' in profile
        assert 'cpu_weight' in profile
        assert 'gpu_weight' in profile
        assert 'features' in profile
        
        # Weights should sum to reasonable values
        assert 0 <= profile['cpu_weight'] <= 1.0
        assert 0 <= profile['gpu_weight'] <= 1.0
        assert isinstance(profile['features'], list)
    
    def test_system_optimization(self, portable_detector):
        """Test system optimization recommendations"""
        results = portable_detector.optimize_for_current_system()
        
        assert 'system' in results
        assert 'strategy_used' in results
        assert 'optimizations_applied' in results
        assert 'performance_gain' in results
        
        assert isinstance(results['optimizations_applied'], list)
        assert results['performance_gain'] >= 0
        assert len(results['optimizations_applied']) > 0
    
    def test_baseline_establishment(self, portable_detector):
        """Test performance baseline establishment"""
        # Short baseline for testing
        baseline = portable_detector.run_performance_baseline(5)
        
        assert 'cpu_mean' in baseline
        assert 'cpu_stdev' in baseline
        assert 'memory_mean' in baseline
        assert 'memory_stdev' in baseline
        
        assert baseline['cpu_mean'] >= 0
        assert baseline['memory_mean'] >= 0
        assert baseline['cpu_stdev'] >= 0
        assert baseline['memory_stdev'] >= 0
    
    def test_anomaly_detection_without_baseline(self, portable_detector):
        """Test anomaly detection without baseline"""
        result = portable_detector.detect_anomalies()
        assert 'error' in result
        assert result['error'] == 'No baseline established'
    
    def test_anomaly_detection_with_baseline(self, portable_detector):
        """Test anomaly detection with baseline"""
        # Establish baseline first
        portable_detector.run_performance_baseline(3)
        
        # Now test anomaly detection
        result = portable_detector.detect_anomalies()
        
        assert 'anomaly_score' in result
        assert 'severity' in result
        assert 'cpu_current' in result
        assert 'memory_current' in result
        assert 'cpu_zscore' in result
        assert 'memory_zscore' in result
        
        assert 0 <= result['anomaly_score'] <= 100
        assert result['severity'] in ['normal', 'low', 'medium', 'high']
        assert result['cpu_current'] >= 0
        assert result['memory_current'] >= 0
    
    def test_severity_classification(self, portable_detector):
        """Test anomaly severity classification"""
        # Test different severity levels
        test_scores = [10, 35, 60, 85]
        expected_severities = ['normal', 'low', 'medium', 'high']
        
        for score, expected in zip(test_scores, expected_severities):
            severity = portable_detector._classify_severity(score)
            assert severity == expected
    
    def test_report_generation(self, portable_detector):
        """Test comprehensive report generation"""
        # Establish baseline for complete report
        portable_detector.run_performance_baseline(3)
        
        report = portable_detector.generate_report()
        
        assert 'timestamp' in report
        assert 'system_profile' in report
        assert 'optimization_applied' in report
        assert 'security_status' in report
        assert 'recommendations' in report
        
        # Check system profile completeness
        system_profile = report['system_profile']
        required_profile_fields = ['os', 'architecture', 'cpu', 'cores', 'ram_gb', 'gpu']
        for field in required_profile_fields:
            assert field in system_profile
    
    def test_recommendations_generation(self, portable_detector):
        """Test system-specific recommendations"""
        recommendations = portable_detector._generate_recommendations()
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        # Each recommendation should be a non-empty string
        for rec in recommendations:
            assert isinstance(rec, str)
            assert len(rec) > 0
    
    def test_gpu_detection(self, portable_detector):
        """Test GPU detection functionality"""
        info = portable_detector.system_info
        
        # GPU type should be one of expected values
        assert info['gpu_type'] in ['none', 'nvidia', 'amd', 'intel', 'arm'] or \
               info['gpu_type'].startswith(('nvidia:', 'amd:', 'intel:', 'arm:'))
        
        # GPU availability should be consistent
        if info['gpu_type'] == 'none':
            assert info['gpu_available'] is False
        else:
            assert info['gpu_available'] is True
    
    def test_cpu_model_detection(self, portable_detector):
        """Test CPU model detection"""
        cpu_model = portable_detector._get_cpu_model()
        assert isinstance(cpu_model, str)
        assert len(cpu_model) > 0
    
    def test_system_summary(self, portable_detector):
        """Test system summary generation"""
        summary = portable_detector.get_system_summary()
        
        assert 'hardware' in summary
        assert 'optimization_profile' in summary
        assert 'baseline_available' in summary
        assert 'capabilities' in summary
        
        capabilities = summary['capabilities']
        assert 'gpu_compute' in capabilities
        assert 'cuda_support' in capabilities
        assert 'opencl_support' in capabilities
        assert 'multi_threading' in capabilities
    
    def test_architecture_specific_optimizations(self, portable_detector):
        """Test architecture-specific optimizations"""
        results = portable_detector.optimize_for_current_system()
        optimizations = results['optimizations_applied']
        
        # Should have some architecture-specific optimization
        arch_specific = any(
            'arm' in opt or 'x86' in opt or 'avx' in opt or 'neon' in opt
            for opt in optimizations
        )
        assert arch_specific or 'thread_optimization' in optimizations
    
    def test_memory_based_optimizations(self, portable_detector):
        """Test memory-based optimizations"""
        results = portable_detector.optimize_for_current_system()
        optimizations = results['optimizations_applied']
        
        # Should have memory-related optimization based on available RAM
        memory_opts = [opt for opt in optimizations if 'memory' in opt.lower()]
        if portable_detector.system_info['ram_gb'] > 2:
            assert len(memory_opts) > 0
    
    def test_continuous_monitoring_data(self, portable_detector):
        """Test data structures for continuous monitoring"""
        # Establish baseline
        portable_detector.run_performance_baseline(2)
        
        # Generate multiple anomaly detections
        anomalies = []
        for _ in range(3):
            anomaly = portable_detector.detect_anomalies()
            anomalies.append(anomaly)
            time.sleep(0.1)
        
        # Verify consistency in data structure
        for anomaly in anomalies:
            assert all(key in anomaly for key in [
                'anomaly_score', 'severity', 'cpu_current', 
                'memory_current', 'cpu_zscore', 'memory_zscore'
            ])