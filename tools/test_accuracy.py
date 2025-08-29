#!/usr/bin/env python3
"""
Accuracy Testing Tool for SmartCompute
Tests computational accuracy against synthetic datasets
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import argparse
import logging
import time
from dataclasses import dataclass, asdict
import sys
import h5py

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from smartcompute.core.smart_compute import SmartCompute
    from smartcompute.core.portable_system import PortableSmartCompute
except ImportError:
    print("Warning: SmartCompute modules not found, using mock implementations")
    
    class SmartCompute:
        def mult(self, A, B, method="auto"):
            time.sleep(0.01)
            return np.dot(A, B)
    
    class PortableSmartCompute:
        def mult(self, A, B, method="auto"):
            time.sleep(0.005)
            return np.dot(A, B)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AccuracyResult:
    """Result of accuracy test"""
    test_id: str
    test_name: str
    matrix_size: Tuple[int, int]
    method: str
    engine: str
    execution_time_ms: float
    relative_error: float
    absolute_error: float
    max_error: float
    accuracy_score: float
    passed: bool
    error_message: Optional[str] = None

@dataclass
class AccuracySummary:
    """Summary of all accuracy tests"""
    total_tests: int
    passed_tests: int
    failed_tests: int
    mean_accuracy: float
    min_accuracy: float
    max_accuracy: float
    mean_relative_error: float
    mean_execution_time_ms: float
    results: List[AccuracyResult]

class AccuracyTester:
    """Test computational accuracy against known datasets"""
    
    def __init__(self, datasets_dir: str = "datasets/synthetic"):
        self.datasets_dir = Path(datasets_dir)
        
        # Initialize compute engines
        self.engines = {
            'smart': SmartCompute(),
            'portable': PortableSmartCompute()
        }
        
        # Accuracy thresholds
        self.thresholds = {
            'excellent': 1e-6,  # Relative error < 1e-6
            'good': 1e-4,       # Relative error < 1e-4  
            'acceptable': 1e-2,  # Relative error < 1e-2
            'poor': 1e-1        # Relative error < 1e-1
        }
        
    def load_dataset(self, filename: str) -> Dict[str, Any]:
        """Load dataset from JSON or HDF5 file"""
        filepath = self.datasets_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Dataset not found: {filepath}")
        
        if filepath.suffix == '.json':
            with open(filepath, 'r') as f:
                return json.load(f)
        elif filepath.suffix == '.h5':
            return self.load_hdf5_dataset(filepath)
        else:
            raise ValueError(f"Unsupported file format: {filepath.suffix}")
    
    def load_hdf5_dataset(self, filepath: Path) -> Dict[str, Any]:
        """Load dataset from HDF5 file"""
        dataset = {'test_cases': []}
        
        with h5py.File(filepath, 'r') as f:
            # Load metadata
            if 'metadata' in f:
                dataset['metadata'] = {}
                for key in f['metadata'].attrs:
                    dataset['metadata'][key] = f['metadata'].attrs[key]
            
            # Load test cases
            if 'test_cases' in f:
                for case_name in f['test_cases'].keys():
                    case_group = f['test_cases'][case_name]
                    
                    test_case = {}
                    
                    # Load arrays
                    test_case['matrix_a'] = case_group['matrix_a'][:].tolist()
                    test_case['matrix_b'] = case_group['matrix_b'][:].tolist()
                    test_case['expected_result'] = case_group['expected_result'][:].tolist()
                    
                    # Load attributes
                    for key in case_group.attrs:
                        test_case[key] = case_group.attrs[key]
                    
                    dataset['test_cases'].append(test_case)
        
        return dataset
    
    def calculate_accuracy_metrics(
        self, 
        result: np.ndarray, 
        expected: np.ndarray
    ) -> Tuple[float, float, float]:
        """Calculate accuracy metrics"""
        
        if result.shape != expected.shape:
            raise ValueError(f"Shape mismatch: {result.shape} vs {expected.shape}")
        
        # Absolute error
        abs_error = np.abs(result - expected)
        mean_abs_error = np.mean(abs_error)
        max_abs_error = np.max(abs_error)
        
        # Relative error (avoid division by zero)
        with np.errstate(divide='ignore', invalid='ignore'):
            rel_error = abs_error / (np.abs(expected) + 1e-15)
            rel_error = np.where(np.isfinite(rel_error), rel_error, 0)
        
        mean_rel_error = np.mean(rel_error)
        
        return mean_rel_error, mean_abs_error, max_abs_error
    
    def calculate_accuracy_score(self, relative_error: float) -> float:
        """Convert relative error to accuracy score (0-1)"""
        if relative_error <= self.thresholds['excellent']:
            return 1.0
        elif relative_error <= self.thresholds['good']:
            return 0.9
        elif relative_error <= self.thresholds['acceptable']:
            return 0.7
        elif relative_error <= self.thresholds['poor']:
            return 0.5
        else:
            return max(0.0, 1.0 - relative_error)
    
    def test_single_case(
        self, 
        test_case: Dict[str, Any], 
        engine_name: str, 
        method: str = "auto"
    ) -> AccuracyResult:
        """Test accuracy for a single test case"""
        
        try:
            # Extract test data
            test_id = str(test_case.get('id', 'unknown'))
            test_name = test_case.get('name', f"case_{test_id}")
            
            matrix_a = np.array(test_case['matrix_a'], dtype=np.float32)
            matrix_b = np.array(test_case['matrix_b'], dtype=np.float32)
            expected = np.array(test_case['expected_result'], dtype=np.float32)
            
            engine = self.engines[engine_name]
            
            # Execute computation
            start_time = time.perf_counter()
            result = engine.mult(matrix_a, matrix_b, method=method)
            end_time = time.perf_counter()
            
            execution_time_ms = (end_time - start_time) * 1000
            
            # Convert result to numpy array if needed
            if not isinstance(result, np.ndarray):
                result = np.array(result)
            
            # Calculate accuracy metrics
            rel_error, abs_error, max_error = self.calculate_accuracy_metrics(result, expected)
            accuracy_score = self.calculate_accuracy_score(rel_error)
            
            # Determine pass/fail
            passed = accuracy_score >= 0.7  # 70% accuracy threshold
            
            return AccuracyResult(
                test_id=test_id,
                test_name=test_name,
                matrix_size=(matrix_a.shape[0], matrix_a.shape[1]),
                method=method,
                engine=engine_name,
                execution_time_ms=execution_time_ms,
                relative_error=rel_error,
                absolute_error=abs_error,
                max_error=max_error,
                accuracy_score=accuracy_score,
                passed=passed
            )
            
        except Exception as e:
            logger.error(f"Test case {test_id} failed: {e}")
            return AccuracyResult(
                test_id=test_id,
                test_name=test_case.get('name', f"case_{test_id}"),
                matrix_size=(0, 0),
                method=method,
                engine=engine_name,
                execution_time_ms=0.0,
                relative_error=1.0,
                absolute_error=1.0,
                max_error=1.0,
                accuracy_score=0.0,
                passed=False,
                error_message=str(e)
            )
    
    def test_dataset(
        self, 
        dataset_name: str, 
        engines: List[str] = None,
        methods: List[str] = None,
        max_cases: int = None
    ) -> AccuracySummary:
        """Test accuracy against a complete dataset"""
        
        if engines is None:
            engines = list(self.engines.keys())
        if methods is None:
            methods = ["auto", "fast", "precise"]
        
        logger.info(f"Testing dataset: {dataset_name}")
        
        # Load dataset
        dataset = self.load_dataset(dataset_name)
        test_cases = dataset.get('test_cases', [])
        
        if max_cases:
            test_cases = test_cases[:max_cases]
        
        logger.info(f"Found {len(test_cases)} test cases")
        
        # Run tests
        all_results = []
        
        for engine_name in engines:
            for method in methods:
                for i, test_case in enumerate(test_cases):
                    logger.info(f"Testing {engine_name}/{method}: case {i+1}/{len(test_cases)}")
                    
                    result = self.test_single_case(test_case, engine_name, method)
                    all_results.append(result)
        
        # Calculate summary statistics
        passed_tests = sum(1 for r in all_results if r.passed)
        failed_tests = len(all_results) - passed_tests
        
        if all_results:
            accuracies = [r.accuracy_score for r in all_results]
            rel_errors = [r.relative_error for r in all_results]
            exec_times = [r.execution_time_ms for r in all_results]
            
            summary = AccuracySummary(
                total_tests=len(all_results),
                passed_tests=passed_tests,
                failed_tests=failed_tests,
                mean_accuracy=np.mean(accuracies),
                min_accuracy=np.min(accuracies),
                max_accuracy=np.max(accuracies),
                mean_relative_error=np.mean(rel_errors),
                mean_execution_time_ms=np.mean(exec_times),
                results=all_results
            )
        else:
            summary = AccuracySummary(
                total_tests=0, passed_tests=0, failed_tests=0,
                mean_accuracy=0.0, min_accuracy=0.0, max_accuracy=0.0,
                mean_relative_error=1.0, mean_execution_time_ms=0.0,
                results=[]
            )
        
        return summary
    
    def generate_accuracy_report(self, summary: AccuracySummary, output_file: str = None) -> str:
        """Generate detailed accuracy report"""
        
        report = f"""
# SmartCompute Accuracy Test Report

## Summary
- **Total Tests**: {summary.total_tests}
- **Passed**: {summary.passed_tests} ({summary.passed_tests/max(summary.total_tests,1)*100:.1f}%)
- **Failed**: {summary.failed_tests} ({summary.failed_tests/max(summary.total_tests,1)*100:.1f}%)
- **Mean Accuracy**: {summary.mean_accuracy:.4f}
- **Min Accuracy**: {summary.min_accuracy:.4f}
- **Max Accuracy**: {summary.max_accuracy:.4f}
- **Mean Relative Error**: {summary.mean_relative_error:.2e}
- **Mean Execution Time**: {summary.mean_execution_time_ms:.2f}ms

## Quality Gates
"""
        
        # Quality gates
        gates = [
            ("Overall Pass Rate > 90%", summary.passed_tests / max(summary.total_tests, 1) > 0.9),
            ("Mean Accuracy > 0.95", summary.mean_accuracy > 0.95),
            ("Mean Relative Error < 1e-3", summary.mean_relative_error < 1e-3),
            ("Mean Execution Time < 100ms", summary.mean_execution_time_ms < 100),
        ]
        
        for gate_name, passed in gates:
            status = "✅ PASS" if passed else "❌ FAIL"
            report += f"- {gate_name}: {status}\n"
        
        report += "\n## Results by Engine and Method\n"
        
        # Group results by engine and method
        if summary.results:
            df = pd.DataFrame([asdict(r) for r in summary.results])
            
            grouped = df.groupby(['engine', 'method']).agg({
                'accuracy_score': ['count', 'mean', 'min'],
                'relative_error': 'mean',
                'execution_time_ms': 'mean',
                'passed': 'sum'
            }).round(4)
            
            report += f"\n{grouped.to_string()}\n"
            
            # Failed tests detail
            failed_results = [r for r in summary.results if not r.passed]
            if failed_results:
                report += f"\n## Failed Tests ({len(failed_results)})\n"
                for result in failed_results[:10]:  # Show first 10 failures
                    report += f"- **{result.test_name}** ({result.engine}/{result.method}): "
                    report += f"Accuracy: {result.accuracy_score:.4f}, "
                    report += f"Rel Error: {result.relative_error:.2e}\n"
                    if result.error_message:
                        report += f"  Error: {result.error_message}\n"
                
                if len(failed_results) > 10:
                    report += f"\n... and {len(failed_results) - 10} more failures\n"
        
        # Save report if output file specified
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(report)
            logger.info(f"Report saved to: {output_path}")
        
        return report
    
    def save_results_json(self, summary: AccuracySummary, output_file: str):
        """Save detailed results to JSON"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = asdict(summary)
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"Results saved to: {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Test SmartCompute accuracy against synthetic datasets')
    parser.add_argument('dataset', help='Dataset filename (e.g., basic_matrices.json)')
    parser.add_argument('--datasets-dir', default='datasets/synthetic', help='Datasets directory')
    parser.add_argument('--engines', nargs='+', choices=['smart', 'portable'], 
                       default=['smart', 'portable'], help='Engines to test')
    parser.add_argument('--methods', nargs='+', choices=['auto', 'fast', 'precise'],
                       default=['auto'], help='Methods to test')
    parser.add_argument('--max-cases', type=int, help='Maximum number of test cases')
    parser.add_argument('--output-report', help='Output markdown report file')
    parser.add_argument('--output-json', help='Output JSON results file')
    parser.add_argument('--quiet', action='store_true', help='Reduce output verbosity')
    
    args = parser.parse_args()
    
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    
    tester = AccuracyTester(datasets_dir=args.datasets_dir)
    
    try:
        summary = tester.test_dataset(
            dataset_name=args.dataset,
            engines=args.engines,
            methods=args.methods,
            max_cases=args.max_cases
        )
        
        # Generate and display report
        report = tester.generate_accuracy_report(summary, args.output_report)
        print(report)
        
        # Save JSON results if requested
        if args.output_json:
            tester.save_results_json(summary, args.output_json)
        
        # Exit with error code if quality gates failed
        pass_rate = summary.passed_tests / max(summary.total_tests, 1)
        if pass_rate < 0.9 or summary.mean_accuracy < 0.95:
            print("\n❌ Quality gates failed!")
            sys.exit(1)
        else:
            print("\n✅ All quality gates passed!")
            sys.exit(0)
    
    except Exception as e:
        logger.error(f"Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()