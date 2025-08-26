"""
SmartCompute Core Engine
Performance-based anomaly detection with intelligent optimization
"""

import numpy as np
import time
import json
import os
import multiprocessing as mp
from typing import Dict, Tuple, Any, Optional
from pathlib import Path


class SmartComputeEngine:
    """
    Core SmartCompute engine for intelligent performance optimization
    """
    
    def __init__(self, history_path: Optional[str] = None):
        """
        Initialize SmartCompute engine
        
        Args:
            history_path: Optional path to history file
        """
        self.cpu_cores = mp.cpu_count()
        self.history_path = history_path or "smart_history.json"
        self.history = self.load_history()
        print(f"🚀 SmartCompute Engine initialized - {self.cpu_cores} cores detected")
    
    def load_history(self) -> Dict:
        """Load historical performance data"""
        if os.path.exists(self.history_path):
            try:
                with open(self.history_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load history file: {e}")
                return {}
        return {}
    
    def save_history(self) -> None:
        """Save historical performance data"""
        try:
            # Only create directory if path has a directory component
            if os.path.dirname(self.history_path):
                os.makedirs(os.path.dirname(self.history_path), exist_ok=True)
            with open(self.history_path, 'w') as f:
                json.dump(self.history, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save history file: {e}")
    
    def measure_error(self, precise: np.ndarray, fast: np.ndarray) -> float:
        """
        Measure relative error between two computation methods
        
        Args:
            precise: Result from precise method
            fast: Result from fast method
            
        Returns:
            Relative error as float
        """
        try:
            diff = np.abs(precise - fast)
            max_val = np.max(np.abs(precise))
            if max_val == 0:
                return 0.0
            return float(np.mean(diff) / max_val)
        except Exception as e:
            print(f"Error measuring computation difference: {e}")
            return 1.0
    
    def single_thread_multiply(self, a: np.ndarray, b: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Precise single-threaded matrix multiplication
        
        Args:
            a: First matrix
            b: Second matrix
            
        Returns:
            Tuple of (result, execution_time)
        """
        os.environ['OMP_NUM_THREADS'] = '1'
        start = time.time()
        result = np.dot(a, b)
        exec_time = time.time() - start
        return result, exec_time
    
    def multi_thread_multiply(self, a: np.ndarray, b: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Fast multi-threaded matrix multiplication
        
        Args:
            a: First matrix
            b: Second matrix
            
        Returns:
            Tuple of (result, execution_time)
        """
        os.environ['OMP_NUM_THREADS'] = str(self.cpu_cores)
        start = time.time()
        result = np.dot(a, b)
        exec_time = time.time() - start
        return result, exec_time
    
    def smart_multiply(
        self, 
        a: np.ndarray, 
        b: np.ndarray, 
        precision_needed: float = 0.95, 
        speed_priority: float = 0.5,
        verbose: bool = True
    ) -> Dict[str, Any]:
        """
        Intelligent matrix multiplication with automatic optimization
        
        Args:
            a: First matrix
            b: Second matrix
            precision_needed: Minimum required precision (0-1)
            speed_priority: Speed vs precision priority (0-1)
            verbose: Enable verbose output
            
        Returns:
            Dictionary containing result and metrics
        """
        operation_key = f"mult_{a.shape}x{b.shape}"
        
        if verbose:
            print(f"\n🔬 Analyzing {operation_key}")
            print(f"🎯 Precision required: {precision_needed:.1%}")
            print(f"⚡ Speed priority: {speed_priority:.1%}")
            print("📊 Executing benchmarks...")
        
        # Execute both methods for comparison
        precise_result, precise_time = self.single_thread_multiply(a, b)
        fast_result, fast_time = self.multi_thread_multiply(a, b)
        
        # Calculate metrics
        error = self.measure_error(precise_result, fast_result)
        accuracy = 1.0 - error
        speedup = precise_time / fast_time if fast_time > 0 else 1.0
        
        if verbose:
            print(f"  ⚙️  Single-thread: {precise_time:.4f}s (precision: 100%)")
            print(f"  🔥 Multi-thread: {fast_time:.4f}s (precision: {accuracy:.1%})")
            print(f"  ⚡ Speedup: {speedup:.2f}x")
        
        # INTELLIGENT DECISION
        if accuracy >= precision_needed:
            # Multi-thread meets precision requirements
            if speed_priority > 0.5:
                choice = "fast"
                chosen_result = fast_result
                chosen_time = fast_time
                chosen_name = "Multi-thread (Speed optimized)"
            else:
                # Evaluate if speedup is worth it
                if speedup > 1.5:  # Significant performance gain
                    choice = "fast"
                    chosen_result = fast_result
                    chosen_time = fast_time
                    chosen_name = "Multi-thread (Balanced)"
                else:
                    choice = "precise"
                    chosen_result = precise_result
                    chosen_time = precise_time
                    chosen_name = "Single-thread (Precision focused)"
        else:
            # Multi-thread doesn't meet precision - use single-thread
            choice = "precise"
            chosen_result = precise_result
            chosen_time = precise_time
            chosen_name = "Single-thread (Precision enforced)"
        
        # Save learning data
        self.history[operation_key] = {
            'precise_time': precise_time,
            'fast_time': fast_time,
            'accuracy': accuracy,
            'speedup': speedup,
            'last_choice': choice,
            'samples': self.history.get(operation_key, {}).get('samples', 0) + 1
        }
        self.save_history()
        
        if verbose:
            print(f"\n✅ DECISION: {chosen_name}")
            print(f"📊 Final precision: {accuracy if choice == 'fast' else 1.0:.1%}")
            print(f"⏱️  Time: {chosen_time:.4f}s")
        
        return {
            'result': chosen_result,
            'method': chosen_name,
            'time': chosen_time,
            'accuracy': accuracy if choice == 'fast' else 1.0,
            'speedup': speedup if choice == 'fast' else 1.0,
            'meets_precision': True,
            'choice': choice,
            'metrics': {
                'precise_time': precise_time,
                'fast_time': fast_time,
                'error': error,
                'speedup': speedup
            }
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary from history"""
        if not self.history:
            return {"message": "No performance data available"}
        
        total_operations = len(self.history)
        fast_choices = sum(1 for op in self.history.values() if op.get('last_choice') == 'fast')
        avg_speedup = np.mean([op.get('speedup', 1.0) for op in self.history.values()])
        avg_accuracy = np.mean([op.get('accuracy', 1.0) for op in self.history.values()])
        
        return {
            'total_operations': total_operations,
            'fast_method_usage': f"{(fast_choices/total_operations)*100:.1f}%",
            'average_speedup': f"{avg_speedup:.2f}x",
            'average_accuracy': f"{avg_accuracy:.1%}",
            'operations': list(self.history.keys())
        }