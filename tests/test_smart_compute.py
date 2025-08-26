"""
Tests for SmartCompute core engine
"""

import pytest
import numpy as np
import os
import json
from app.core.smart_compute import SmartComputeEngine


class TestSmartComputeEngine:
    """Test SmartCompute engine functionality"""
    
    def test_initialization(self, smart_engine, cleanup_test_files):
        """Test engine initialization"""
        assert smart_engine is not None
        assert smart_engine.cpu_cores > 0
        assert isinstance(smart_engine.history, dict)
    
    def test_measure_error(self, smart_engine):
        """Test error measurement between computation methods"""
        np.random.seed(42)
        a = np.random.rand(50, 50)
        b = np.random.rand(50, 50)
        
        # Same results should have zero error
        error = smart_engine.measure_error(a, a)
        assert error == 0.0
        
        # Different results should have some error
        c = a + np.random.rand(50, 50) * 0.1
        error = smart_engine.measure_error(a, c)
        assert error > 0.0
    
    def test_single_thread_multiply(self, smart_engine, test_matrices):
        """Test single-threaded matrix multiplication"""
        a, b = test_matrices['small']
        result, exec_time = smart_engine.single_thread_multiply(a, b)
        
        assert result.shape == (10, 10)
        assert exec_time > 0
        
        # Verify result correctness
        expected = np.dot(a, b)
        np.testing.assert_array_almost_equal(result, expected)
    
    def test_multi_thread_multiply(self, smart_engine, test_matrices):
        """Test multi-threaded matrix multiplication"""
        a, b = test_matrices['small']
        result, exec_time = smart_engine.multi_thread_multiply(a, b)
        
        assert result.shape == (10, 10)
        assert exec_time > 0
        
        # Verify result correctness
        expected = np.dot(a, b)
        np.testing.assert_array_almost_equal(result, expected)
    
    def test_smart_multiply_precision_priority(self, smart_engine, test_matrices):
        """Test smart multiply with precision priority"""
        a, b = test_matrices['medium']
        
        result = smart_engine.smart_multiply(
            a, b,
            precision_needed=0.99,
            speed_priority=0.1,  # Low speed priority
            verbose=False
        )
        
        assert 'result' in result
        assert 'method' in result
        assert 'time' in result
        assert 'accuracy' in result
        assert 'speedup' in result
        assert 'meets_precision' in result
        assert result['meets_precision'] is True
        assert result['accuracy'] >= 0.99
    
    def test_smart_multiply_speed_priority(self, smart_engine, test_matrices):
        """Test smart multiply with speed priority"""
        a, b = test_matrices['medium']
        
        result = smart_engine.smart_multiply(
            a, b,
            precision_needed=0.85,
            speed_priority=0.9,  # High speed priority
            verbose=False
        )
        
        assert result['meets_precision'] is True
        assert result['accuracy'] >= 0.85
    
    def test_history_persistence(self, smart_engine, test_matrices, cleanup_test_files):
        """Test that optimization history is saved and loaded"""
        a, b = test_matrices['small']
        
        # Perform operation to generate history
        result = smart_engine.smart_multiply(a, b, verbose=False)
        
        # Check that history was updated
        assert len(smart_engine.history) > 0
        
        # Save history
        smart_engine.save_history()
        assert os.path.exists(smart_engine.history_path)
        
        # Create new engine and verify history is loaded
        new_engine = SmartComputeEngine(history_path=smart_engine.history_path)
        assert len(new_engine.history) > 0
        assert len(new_engine.history) == len(smart_engine.history)
    
    def test_performance_summary(self, smart_engine, test_matrices):
        """Test performance summary generation"""
        a, b = test_matrices['small']
        
        # Perform some operations
        smart_engine.smart_multiply(a, b, verbose=False)
        smart_engine.smart_multiply(a, b, precision_needed=0.9, verbose=False)
        
        summary = smart_engine.get_performance_summary()
        
        assert 'total_operations' in summary
        assert 'fast_method_usage' in summary
        assert 'average_speedup' in summary
        assert 'average_accuracy' in summary
        assert 'operations' in summary
        assert summary['total_operations'] > 0
    
    def test_invalid_inputs(self, smart_engine):
        """Test handling of invalid inputs"""
        # Test with mismatched matrix dimensions
        a = np.random.rand(5, 3)
        b = np.random.rand(4, 3)  # Wrong dimensions
        
        with pytest.raises(ValueError):
            smart_engine.smart_multiply(a, b, verbose=False)
    
    def test_edge_cases(self, smart_engine):
        """Test edge cases"""
        # Very small matrices
        a = np.array([[1.0]])
        b = np.array([[2.0]])
        
        result = smart_engine.smart_multiply(a, b, verbose=False)
        assert result['result'].shape == (1, 1)
        assert result['result'][0, 0] == 2.0
        
        # Zero matrices
        a = np.zeros((5, 5))
        b = np.zeros((5, 5))
        
        result = smart_engine.smart_multiply(a, b, verbose=False)
        assert np.all(result['result'] == 0)
    
    def test_different_precision_requirements(self, smart_engine, test_matrices):
        """Test with different precision requirements"""
        a, b = test_matrices['medium']
        
        precisions = [0.5, 0.8, 0.9, 0.95, 0.99]
        
        for precision in precisions:
            result = smart_engine.smart_multiply(
                a, b,
                precision_needed=precision,
                verbose=False
            )
            assert result['accuracy'] >= precision
            assert result['meets_precision'] is True