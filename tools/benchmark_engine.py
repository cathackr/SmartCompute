#!/usr/bin/env python3
"""
SmartCompute Benchmark Engine
Automated performance testing with visualization and reporting
"""

import json
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import logging
import hashlib
import subprocess
import psutil
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from smartcompute.core.smart_compute import SmartCompute
    from smartcompute.core.portable_system import PortableSmartCompute
except ImportError:
    # Fallback for when module isn't installed
    print("Warning: SmartCompute modules not found, using mock implementations")
    
    class SmartCompute:
        def __init__(self):
            pass
        
        def mult(self, A, B, method="auto"):
            # Mock implementation
            time.sleep(0.001 + np.random.random() * 0.05)
            return np.dot(A, B)
    
    class PortableSmartCompute:
        def __init__(self):
            pass
        
        def mult(self, A, B, method="auto"):
            # Mock implementation  
            time.sleep(0.001 + np.random.random() * 0.03)
            return np.dot(A, B)

@dataclass
class BenchmarkResult:
    """Single benchmark result"""
    test_name: str
    method: str
    matrix_size: Tuple[int, int, int, int]  # (m1, n1, m2, n2)
    execution_time_ms: float
    memory_usage_mb: float
    accuracy_score: float
    cpu_percent: float
    timestamp: str
    system_info: Dict[str, Any]
    
@dataclass  
class BenchmarkSuite:
    """Complete benchmark suite results"""
    suite_name: str
    timestamp: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    total_duration_ms: float
    results: List[BenchmarkResult]
    system_summary: Dict[str, Any]
    performance_summary: Dict[str, float]

class BenchmarkEngine:
    """Advanced benchmarking engine with visualization"""
    
    def __init__(self, output_dir: str = "benchmark_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize compute engines
        self.smart_compute = SmartCompute()
        self.portable_compute = PortableSmartCompute()
        
        # Benchmark configuration
        self.matrix_sizes = [
            (10, 10, 10, 10),
            (50, 50, 50, 50),
            (100, 100, 100, 100),
            (200, 200, 200, 200),
            (300, 300, 300, 300),
            (500, 500, 500, 500),
            (1000, 1000, 1000, 1000),
        ]
        
        self.methods = ["fast", "precise", "auto"]
        self.engines = {
            "smart": self.smart_compute,
            "portable": self.portable_compute
        }
        
    def generate_test_matrices(self, m1: int, n1: int, m2: int, n2: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Generate reproducible test matrices and expected result"""
        # Use fixed seed for reproducibility
        np.random.seed(42 + m1 + n1 + m2 + n2)
        
        A = np.random.randn(m1, n1).astype(np.float32)
        B = np.random.randn(m2, n2).astype(np.float32)
        
        # Expected result using NumPy (reference implementation)
        expected = np.dot(A, B)
        
        return A, B, expected
    
    def calculate_accuracy(self, result: np.ndarray, expected: np.ndarray) -> float:
        """Calculate accuracy score between result and expected"""
        try:
            # Handle different shapes
            if result.shape != expected.shape:
                return 0.0
                
            # Calculate relative error
            relative_error = np.abs((result - expected) / (expected + 1e-8))
            mean_error = np.mean(relative_error)
            
            # Convert to accuracy score (1.0 = perfect, 0.0 = completely wrong)
            accuracy = max(0.0, 1.0 - mean_error)
            return min(1.0, accuracy)
        except Exception as e:
            self.logger.warning(f"Accuracy calculation failed: {e}")
            return 0.0
    
    def measure_system_resources(self) -> Dict[str, Any]:
        """Measure current system resources"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            return {
                "cpu_percent": cpu_percent,
                "memory_total_mb": memory.total / 1024 / 1024,
                "memory_available_mb": memory.available / 1024 / 1024,
                "memory_used_mb": memory.used / 1024 / 1024,
                "memory_percent": memory.percent
            }
        except Exception as e:
            self.logger.warning(f"System resource measurement failed: {e}")
            return {
                "cpu_percent": 0.0,
                "memory_total_mb": 0.0,
                "memory_available_mb": 0.0,
                "memory_used_mb": 0.0,
                "memory_percent": 0.0
            }
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        try:
            import platform
            
            return {
                "python_version": platform.python_version(),
                "platform": platform.platform(),
                "processor": platform.processor(),
                "architecture": platform.architecture(),
                "cpu_count": psutil.cpu_count(),
                "cpu_count_logical": psutil.cpu_count(logical=True),
                "total_memory_gb": psutil.virtual_memory().total / 1024**3,
                "hostname": platform.node(),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            self.logger.warning(f"System info collection failed: {e}")
            return {"error": str(e)}
    
    def run_single_benchmark(
        self, 
        engine_name: str, 
        engine: Any, 
        method: str, 
        matrix_size: Tuple[int, int, int, int]
    ) -> Optional[BenchmarkResult]:
        """Run a single benchmark test"""
        try:
            m1, n1, m2, n2 = matrix_size
            test_name = f"{engine_name}_{method}_{m1}x{n1}_{m2}x{n2}"
            
            # Generate test data
            A, B, expected = self.generate_test_matrices(m1, n1, m2, n2)
            
            # Measure system state before
            system_before = self.measure_system_resources()
            
            # Execute benchmark
            start_time = time.perf_counter()
            result = engine.mult(A, B, method=method)
            end_time = time.perf_counter()
            
            # Measure system state after
            system_after = self.measure_system_resources()
            
            # Calculate metrics
            execution_time_ms = (end_time - start_time) * 1000
            accuracy = self.calculate_accuracy(result, expected)
            memory_usage_mb = system_after["memory_used_mb"] - system_before["memory_used_mb"]
            cpu_percent = max(system_before["cpu_percent"], system_after["cpu_percent"])
            
            return BenchmarkResult(
                test_name=test_name,
                method=method,
                matrix_size=matrix_size,
                execution_time_ms=execution_time_ms,
                memory_usage_mb=memory_usage_mb,
                accuracy_score=accuracy,
                cpu_percent=cpu_percent,
                timestamp=datetime.now(timezone.utc).isoformat(),
                system_info=system_after
            )
            
        except Exception as e:
            self.logger.error(f"Benchmark failed for {test_name}: {e}")
            return None
    
    def run_benchmark_suite(
        self, 
        suite_name: str = "complete",
        parallel: bool = False,
        max_workers: int = 4
    ) -> BenchmarkSuite:
        """Run complete benchmark suite"""
        self.logger.info(f"Starting benchmark suite: {suite_name}")
        
        start_time = time.perf_counter()
        results = []
        failed_tests = 0
        
        # Generate all test combinations
        test_combinations = []
        for engine_name, engine in self.engines.items():
            for method in self.methods:
                for matrix_size in self.matrix_sizes:
                    test_combinations.append((engine_name, engine, method, matrix_size))
        
        # Run benchmarks
        if parallel:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_test = {
                    executor.submit(self.run_single_benchmark, *combo): combo 
                    for combo in test_combinations
                }
                
                for future in as_completed(future_to_test):
                    result = future.result()
                    if result:
                        results.append(result)
                    else:
                        failed_tests += 1
        else:
            for combo in test_combinations:
                result = self.run_single_benchmark(*combo)
                if result:
                    results.append(result)
                else:
                    failed_tests += 1
        
        end_time = time.perf_counter()
        total_duration = (end_time - start_time) * 1000
        
        # Calculate performance summary
        performance_summary = self.calculate_performance_summary(results)
        
        suite = BenchmarkSuite(
            suite_name=suite_name,
            timestamp=datetime.now(timezone.utc).isoformat(),
            total_tests=len(test_combinations),
            passed_tests=len(results),
            failed_tests=failed_tests,
            total_duration_ms=total_duration,
            results=results,
            system_summary=self.get_system_info(),
            performance_summary=performance_summary
        )
        
        self.logger.info(f"Benchmark suite completed: {len(results)}/{len(test_combinations)} tests passed")
        return suite
    
    def calculate_performance_summary(self, results: List[BenchmarkResult]) -> Dict[str, float]:
        """Calculate performance summary statistics"""
        if not results:
            return {}
        
        execution_times = [r.execution_time_ms for r in results]
        accuracies = [r.accuracy_score for r in results]
        memory_usage = [r.memory_usage_mb for r in results]
        
        return {
            "latency_mean_ms": np.mean(execution_times),
            "latency_p50_ms": np.percentile(execution_times, 50),
            "latency_p95_ms": np.percentile(execution_times, 95),
            "latency_p99_ms": np.percentile(execution_times, 99),
            "latency_max_ms": np.max(execution_times),
            "accuracy_mean": np.mean(accuracies),
            "accuracy_min": np.min(accuracies),
            "memory_usage_mean_mb": np.mean(memory_usage),
            "memory_usage_max_mb": np.max(memory_usage),
            "tests_with_perfect_accuracy": sum(1 for a in accuracies if a >= 0.999),
            "tests_with_good_accuracy": sum(1 for a in accuracies if a >= 0.95)
        }
    
    def save_results(self, suite: BenchmarkSuite) -> Path:
        """Save benchmark results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"benchmark_{suite.suite_name}_{timestamp}.json"
        filepath = self.output_dir / filename
        
        # Convert to serializable format
        data = asdict(suite)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        self.logger.info(f"Results saved to: {filepath}")
        return filepath
    
    def generate_visualizations(self, suite: BenchmarkSuite) -> List[Path]:
        """Generate comprehensive visualizations"""
        self.logger.info("Generating benchmark visualizations...")
        
        # Set style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        generated_files = []
        
        # Create DataFrame for analysis
        df = pd.DataFrame([asdict(r) for r in suite.results])
        
        # 1. Latency vs Matrix Size
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f'SmartCompute Benchmark Results - {suite.suite_name}', fontsize=16)
        
        # Extract matrix size for plotting
        df['matrix_area'] = df['matrix_size'].apply(lambda x: x[0] * x[1])
        
        # Latency by method
        for method in df['method'].unique():
            method_data = df[df['method'] == method]
            axes[0, 0].scatter(method_data['matrix_area'], method_data['execution_time_ms'], 
                             label=method, alpha=0.7)
        
        axes[0, 0].set_xlabel('Matrix Area (elements)')
        axes[0, 0].set_ylabel('Execution Time (ms)')
        axes[0, 0].set_title('Latency vs Matrix Size by Method')
        axes[0, 0].legend()
        axes[0, 0].set_xscale('log')
        axes[0, 0].set_yscale('log')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Accuracy distribution
        axes[0, 1].hist(df['accuracy_score'], bins=20, alpha=0.7, color='skyblue', edgecolor='black')
        axes[0, 1].set_xlabel('Accuracy Score')
        axes[0, 1].set_ylabel('Number of Tests')
        axes[0, 1].set_title('Accuracy Distribution')
        axes[0, 1].axvline(x=0.95, color='red', linestyle='--', label='95% threshold')
        axes[0, 1].axvline(x=0.99, color='green', linestyle='--', label='99% threshold')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # Performance by engine
        if 'test_name' in df.columns:
            df['engine'] = df['test_name'].str.split('_').str[0]
            engine_perf = df.groupby('engine')['execution_time_ms'].mean()
            axes[1, 0].bar(engine_perf.index, engine_perf.values, color=['lightblue', 'lightgreen'])
            axes[1, 0].set_ylabel('Mean Execution Time (ms)')
            axes[1, 0].set_title('Performance by Engine')
            axes[1, 0].grid(True, alpha=0.3)
        
        # Memory usage vs execution time
        axes[1, 1].scatter(df['execution_time_ms'], df['memory_usage_mb'], alpha=0.6, color='coral')
        axes[1, 1].set_xlabel('Execution Time (ms)')
        axes[1, 1].set_ylabel('Memory Usage (MB)')
        axes[1, 1].set_title('Memory Usage vs Execution Time')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save main visualization
        main_viz_path = self.output_dir / f"benchmark_visualization_{suite.suite_name}.png"
        plt.savefig(main_viz_path, dpi=300, bbox_inches='tight')
        plt.close()
        generated_files.append(main_viz_path)
        
        # 2. Detailed heatmap
        if len(df) > 10:
            pivot_data = df.pivot_table(
                values='execution_time_ms', 
                index='matrix_area', 
                columns='method', 
                aggfunc='mean'
            )
            
            fig, ax = plt.subplots(figsize=(10, 8))
            sns.heatmap(pivot_data, annot=True, fmt='.2f', cmap='YlOrRd', ax=ax)
            ax.set_title('Execution Time Heatmap (ms)')
            ax.set_xlabel('Method')
            ax.set_ylabel('Matrix Area')
            
            heatmap_path = self.output_dir / f"benchmark_heatmap_{suite.suite_name}.png"
            plt.savefig(heatmap_path, dpi=300, bbox_inches='tight')
            plt.close()
            generated_files.append(heatmap_path)
        
        self.logger.info(f"Generated {len(generated_files)} visualizations")
        return generated_files
    
    def generate_html_report(self, suite: BenchmarkSuite, viz_paths: List[Path]) -> Path:
        """Generate comprehensive HTML report"""
        template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SmartCompute Benchmark Report - {suite.suite_name}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        .metric {{ background: #ecf0f1; padding: 15px; margin: 10px 0; border-left: 4px solid #3498db; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #2980b9; }}
        .status-pass {{ color: #27ae60; font-weight: bold; }}
        .status-warn {{ color: #f39c12; font-weight: bold; }}
        .status-fail {{ color: #e74c3c; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #3498db; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .visualization {{ text-align: center; margin: 30px 0; }}
        .visualization img {{ max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 5px; }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }}
        pre {{ background: #2c3e50; color: #ecf0f1; padding: 20px; border-radius: 5px; overflow-x: auto; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 SmartCompute Benchmark Report</h1>
        
        <div class="summary-grid">
            <div class="metric">
                <div>Suite: <span class="metric-value">{suite.suite_name}</span></div>
            </div>
            <div class="metric">
                <div>Tests: <span class="metric-value">{suite.passed_tests}/{suite.total_tests}</span></div>
            </div>
            <div class="metric">
                <div>Duration: <span class="metric-value">{suite.total_duration_ms:.1f}ms</span></div>
            </div>
            <div class="metric">
                <div>Timestamp: <span class="metric-value">{suite.timestamp[:19]}</span></div>
            </div>
        </div>

        <h2>📊 Performance Summary</h2>
        <div class="summary-grid">
            <div class="metric">
                <div>Mean Latency</div>
                <div class="metric-value">{suite.performance_summary.get('latency_mean_ms', 0):.2f}ms</div>
            </div>
            <div class="metric">
                <div>P95 Latency</div>
                <div class="metric-value">{suite.performance_summary.get('latency_p95_ms', 0):.2f}ms</div>
            </div>
            <div class="metric">
                <div>P99 Latency</div>
                <div class="metric-value">{suite.performance_summary.get('latency_p99_ms', 0):.2f}ms</div>
            </div>
            <div class="metric">
                <div>Mean Accuracy</div>
                <div class="metric-value">{suite.performance_summary.get('accuracy_mean', 0):.4f}</div>
            </div>
        </div>

        <h2>🎯 Quality Gates</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Threshold</th>
                <th>Actual</th>
                <th>Status</th>
            </tr>
            <tr>
                <td>Mean Latency</td>
                <td>&lt; 50ms</td>
                <td>{suite.performance_summary.get('latency_mean_ms', 0):.2f}ms</td>
                <td class="{'status-pass' if suite.performance_summary.get('latency_mean_ms', 0) < 50 else 'status-fail'}">
                    {'PASS' if suite.performance_summary.get('latency_mean_ms', 0) < 50 else 'FAIL'}
                </td>
            </tr>
            <tr>
                <td>P95 Latency</td>
                <td>&lt; 100ms</td>
                <td>{suite.performance_summary.get('latency_p95_ms', 0):.2f}ms</td>
                <td class="{'status-pass' if suite.performance_summary.get('latency_p95_ms', 0) < 100 else 'status-fail'}">
                    {'PASS' if suite.performance_summary.get('latency_p95_ms', 0) < 100 else 'FAIL'}
                </td>
            </tr>
            <tr>
                <td>Mean Accuracy</td>
                <td>&gt; 95%</td>
                <td>{suite.performance_summary.get('accuracy_mean', 0)*100:.2f}%</td>
                <td class="{'status-pass' if suite.performance_summary.get('accuracy_mean', 0) > 0.95 else 'status-fail'}">
                    {'PASS' if suite.performance_summary.get('accuracy_mean', 0) > 0.95 else 'FAIL'}
                </td>
            </tr>
        </table>
        """
        
        # Add visualizations
        for i, viz_path in enumerate(viz_paths):
            template += f"""
        <div class="visualization">
            <h3>Visualization {i+1}</h3>
            <img src="{viz_path.name}" alt="Benchmark Visualization {i+1}">
        </div>
            """
        
        # Add system info
        template += f"""
        <h2>💻 System Information</h2>
        <pre>{json.dumps(suite.system_summary, indent=2)}</pre>
        
        <h2>📋 Detailed Results</h2>
        <table>
            <tr>
                <th>Test</th>
                <th>Method</th>
                <th>Matrix Size</th>
                <th>Time (ms)</th>
                <th>Accuracy</th>
                <th>Memory (MB)</th>
            </tr>
        """
        
        # Add detailed results
        for result in suite.results[:20]:  # Show first 20 results
            m1, n1, m2, n2 = result.matrix_size
            template += f"""
            <tr>
                <td>{result.test_name}</td>
                <td>{result.method}</td>
                <td>{m1}×{n1} × {m2}×{n2}</td>
                <td>{result.execution_time_ms:.2f}</td>
                <td>{result.accuracy_score:.4f}</td>
                <td>{result.memory_usage_mb:.2f}</td>
            </tr>
            """
        
        if len(suite.results) > 20:
            template += f"<tr><td colspan='6'>... and {len(suite.results) - 20} more results</td></tr>"
        
        template += """
        </table>
        
        <footer style="margin-top: 50px; text-align: center; color: #7f8c8d;">
            <p>Generated by SmartCompute Benchmark Engine</p>
        </footer>
    </div>
</body>
</html>
        """
        
        # Save HTML report
        report_path = self.output_dir / f"benchmark_report_{suite.suite_name}.html"
        with open(report_path, 'w') as f:
            f.write(template)
        
        self.logger.info(f"HTML report generated: {report_path}")
        return report_path

def main():
    """Main function for running benchmarks"""
    import argparse
    
    parser = argparse.ArgumentParser(description='SmartCompute Benchmark Engine')
    parser.add_argument('--suite', default='complete', help='Benchmark suite name')
    parser.add_argument('--output', default='benchmark_results', help='Output directory')
    parser.add_argument('--parallel', action='store_true', help='Run benchmarks in parallel')
    parser.add_argument('--workers', type=int, default=4, help='Number of parallel workers')
    parser.add_argument('--no-viz', action='store_true', help='Skip visualization generation')
    
    args = parser.parse_args()
    
    # Initialize benchmark engine
    engine = BenchmarkEngine(output_dir=args.output)
    
    # Run benchmark suite
    suite = engine.run_benchmark_suite(
        suite_name=args.suite,
        parallel=args.parallel,
        max_workers=args.workers
    )
    
    # Save results
    json_path = engine.save_results(suite)
    
    # Generate visualizations and report
    viz_paths = []
    if not args.no_viz:
        viz_paths = engine.generate_visualizations(suite)
        html_path = engine.generate_html_report(suite, viz_paths)
        print(f"HTML report: {html_path}")
    
    print(f"JSON results: {json_path}")
    
    # Performance summary
    print("\n" + "="*60)
    print("BENCHMARK SUMMARY")
    print("="*60)
    print(f"Suite: {suite.suite_name}")
    print(f"Tests: {suite.passed_tests}/{suite.total_tests} passed")
    print(f"Duration: {suite.total_duration_ms:.1f}ms")
    print(f"Mean Latency: {suite.performance_summary.get('latency_mean_ms', 0):.2f}ms")
    print(f"P95 Latency: {suite.performance_summary.get('latency_p95_ms', 0):.2f}ms")
    print(f"Mean Accuracy: {suite.performance_summary.get('accuracy_mean', 0):.4f}")
    
    # Quality gates
    latency_ok = suite.performance_summary.get('latency_mean_ms', 0) < 50
    accuracy_ok = suite.performance_summary.get('accuracy_mean', 0) > 0.95
    
    print("\nQUALITY GATES:")
    print(f"Latency < 50ms: {'✅ PASS' if latency_ok else '❌ FAIL'}")
    print(f"Accuracy > 95%: {'✅ PASS' if accuracy_ok else '❌ FAIL'}")
    
    # Exit code based on quality gates
    if not (latency_ok and accuracy_ok):
        print("\n❌ Quality gates failed!")
        sys.exit(1)
    else:
        print("\n✅ All quality gates passed!")
        sys.exit(0)

if __name__ == "__main__":
    main()