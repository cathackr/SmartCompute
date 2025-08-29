#!/usr/bin/env python3
"""
Synthetic Dataset Generator for SmartCompute
Generates reproducible test matrices with known mathematical properties
"""

import numpy as np
import pandas as pd
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
import hashlib
import logging
from datetime import datetime
import h5py

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DatasetMetadata:
    """Metadata for synthetic datasets"""
    name: str
    description: str
    matrix_sizes: List[Tuple[int, int, int, int]]
    test_cases: int
    seed: int
    data_type: str
    properties: Dict[str, Any]
    generated_at: str
    version: str = "1.0"

class SyntheticDataGenerator:
    """Generate synthetic datasets for testing matrix operations"""
    
    def __init__(self, seed: int = 42, output_dir: str = "datasets/synthetic"):
        self.seed = seed
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set random seed for reproducibility
        np.random.seed(seed)
        
    def generate_basic_matrices(
        self, 
        sizes: List[Tuple[int, int, int, int]], 
        samples_per_size: int = 10
    ) -> Dict[str, Any]:
        """Generate basic random matrices for multiplication testing"""
        
        logger.info(f"Generating basic matrices for {len(sizes)} sizes, {samples_per_size} samples each")
        
        dataset = {
            "metadata": {
                "name": "basic_matrices",
                "description": "Basic random matrices for multiplication testing",
                "type": "float32",
                "sizes": sizes,
                "samples_per_size": samples_per_size
            },
            "test_cases": []
        }
        
        case_id = 0
        for m1, n1, m2, n2 in sizes:
            if n1 != m2:
                logger.warning(f"Invalid dimensions for multiplication: ({m1}, {n1}) x ({m2}, {n2})")
                continue
                
            for sample in range(samples_per_size):
                # Set seed for reproducibility
                np.random.seed(self.seed + case_id)
                
                # Generate matrices
                A = np.random.randn(m1, n1).astype(np.float32)
                B = np.random.randn(m2, n2).astype(np.float32)
                
                # Calculate expected result
                expected = np.dot(A, B).astype(np.float32)
                
                test_case = {
                    "id": case_id,
                    "matrix_a_shape": [m1, n1],
                    "matrix_b_shape": [m2, n2],
                    "expected_shape": [m1, n2],
                    "matrix_a": A.tolist(),
                    "matrix_b": B.tolist(),
                    "expected_result": expected.tolist(),
                    "properties": {
                        "a_norm": float(np.linalg.norm(A)),
                        "b_norm": float(np.linalg.norm(B)),
                        "expected_norm": float(np.linalg.norm(expected)),
                        "condition_number_a": float(np.linalg.cond(A)) if min(A.shape) > 0 else 1.0,
                        "determinant_a": float(np.linalg.det(A)) if A.shape[0] == A.shape[1] else None
                    }
                }
                
                dataset["test_cases"].append(test_case)
                case_id += 1
        
        return dataset
    
    def generate_special_matrices(self) -> Dict[str, Any]:
        """Generate matrices with special mathematical properties"""
        
        logger.info("Generating special matrices (identity, zero, ones, etc.)")
        
        dataset = {
            "metadata": {
                "name": "special_matrices",
                "description": "Matrices with special mathematical properties",
                "type": "float32"
            },
            "test_cases": []
        }
        
        case_id = 0
        sizes = [5, 10, 20, 50]
        
        for size in sizes:
            # Identity matrix
            A = np.eye(size, dtype=np.float32)
            B = np.random.randn(size, size).astype(np.float32)
            expected = B.copy()  # I * B = B
            
            dataset["test_cases"].append({
                "id": case_id,
                "name": f"identity_{size}x{size}",
                "matrix_a_shape": [size, size],
                "matrix_b_shape": [size, size],
                "matrix_a": A.tolist(),
                "matrix_b": B.tolist(),
                "expected_result": expected.tolist(),
                "properties": {"type": "identity", "size": size}
            })
            case_id += 1
            
            # Zero matrix
            A = np.zeros((size, size), dtype=np.float32)
            B = np.random.randn(size, size).astype(np.float32)
            expected = np.zeros((size, size), dtype=np.float32)
            
            dataset["test_cases"].append({
                "id": case_id,
                "name": f"zero_{size}x{size}",
                "matrix_a_shape": [size, size],
                "matrix_b_shape": [size, size],
                "matrix_a": A.tolist(),
                "matrix_b": B.tolist(),
                "expected_result": expected.tolist(),
                "properties": {"type": "zero", "size": size}
            })
            case_id += 1
            
            # Diagonal matrix
            diag_values = np.random.randn(size).astype(np.float32)
            A = np.diag(diag_values)
            B = np.random.randn(size, size).astype(np.float32)
            expected = A @ B
            
            dataset["test_cases"].append({
                "id": case_id,
                "name": f"diagonal_{size}x{size}",
                "matrix_a_shape": [size, size],
                "matrix_b_shape": [size, size],
                "matrix_a": A.tolist(),
                "matrix_b": B.tolist(),
                "expected_result": expected.tolist(),
                "properties": {"type": "diagonal", "size": size, "diagonal_values": diag_values.tolist()}
            })
            case_id += 1
            
            # Orthogonal matrix (if size is reasonable)
            if size <= 20:
                # Generate random matrix and use QR decomposition
                random_matrix = np.random.randn(size, size)
                Q, R = np.linalg.qr(random_matrix)
                A = Q.astype(np.float32)
                B = np.random.randn(size, size).astype(np.float32)
                expected = A @ B
                
                dataset["test_cases"].append({
                    "id": case_id,
                    "name": f"orthogonal_{size}x{size}",
                    "matrix_a_shape": [size, size],
                    "matrix_b_shape": [size, size],
                    "matrix_a": A.tolist(),
                    "matrix_b": B.tolist(),
                    "expected_result": expected.tolist(),
                    "properties": {"type": "orthogonal", "size": size, "orthogonality_check": float(np.linalg.norm(A.T @ A - np.eye(size)))}
                })
                case_id += 1
        
        return dataset
    
    def generate_stress_test_matrices(self) -> Dict[str, Any]:
        """Generate matrices for stress testing (large, ill-conditioned, etc.)"""
        
        logger.info("Generating stress test matrices")
        
        dataset = {
            "metadata": {
                "name": "stress_test_matrices",
                "description": "Large and challenging matrices for stress testing",
                "type": "float32",
                "warning": "These matrices may require significant computational resources"
            },
            "test_cases": []
        }
        
        case_id = 0
        
        # Large matrices (but still manageable)
        large_sizes = [(100, 100, 100, 100), (200, 200, 200, 200), (300, 300, 300, 300)]
        
        for m1, n1, m2, n2 in large_sizes:
            np.random.seed(self.seed + case_id)
            
            A = np.random.randn(m1, n1).astype(np.float32)
            B = np.random.randn(m2, n2).astype(np.float32)
            expected = np.dot(A, B)
            
            dataset["test_cases"].append({
                "id": case_id,
                "name": f"large_{m1}x{n1}_{m2}x{n2}",
                "matrix_a_shape": [m1, n1],
                "matrix_b_shape": [m2, n2],
                "matrix_a": A.tolist(),
                "matrix_b": B.tolist(),
                "expected_result": expected.tolist(),
                "properties": {
                    "type": "large",
                    "elements_total": m1 * n1 + m2 * n2,
                    "result_elements": m1 * n2
                }
            })
            case_id += 1
        
        # Ill-conditioned matrices
        for size in [10, 20]:
            np.random.seed(self.seed + case_id)
            
            # Create ill-conditioned matrix using SVD
            U = np.random.randn(size, size)
            U, _ = np.linalg.qr(U)
            V = np.random.randn(size, size)  
            V, _ = np.linalg.qr(V)
            
            # Use exponentially decreasing singular values
            singular_values = np.exp(-np.linspace(0, 10, size))
            S = np.diag(singular_values)
            
            A = (U @ S @ V.T).astype(np.float32)
            B = np.random.randn(size, size).astype(np.float32)
            expected = A @ B
            
            dataset["test_cases"].append({
                "id": case_id,
                "name": f"ill_conditioned_{size}x{size}",
                "matrix_a_shape": [size, size],
                "matrix_b_shape": [size, size],
                "matrix_a": A.tolist(),
                "matrix_b": B.tolist(),
                "expected_result": expected.tolist(),
                "properties": {
                    "type": "ill_conditioned",
                    "condition_number": float(np.linalg.cond(A)),
                    "singular_values": singular_values.tolist()
                }
            })
            case_id += 1
        
        return dataset
    
    def generate_precision_test_matrices(self) -> Dict[str, Any]:
        """Generate matrices for precision testing"""
        
        logger.info("Generating precision test matrices")
        
        dataset = {
            "metadata": {
                "name": "precision_test_matrices", 
                "description": "Matrices designed to test numerical precision",
                "type": "float64"  # Higher precision for reference
            },
            "test_cases": []
        }
        
        case_id = 0
        
        # Small numbers test
        for size in [5, 10]:
            np.random.seed(self.seed + case_id)
            
            A = (np.random.randn(size, size) * 1e-6).astype(np.float64)
            B = (np.random.randn(size, size) * 1e-6).astype(np.float64)
            expected = A @ B
            
            dataset["test_cases"].append({
                "id": case_id,
                "name": f"small_numbers_{size}x{size}",
                "matrix_a_shape": [size, size],
                "matrix_b_shape": [size, size],
                "matrix_a": A.tolist(),
                "matrix_b": B.tolist(),
                "expected_result": expected.tolist(),
                "properties": {
                    "type": "small_numbers",
                    "magnitude": "1e-6",
                    "expected_precision_loss": "moderate"
                }
            })
            case_id += 1
        
        # Large numbers test
        for size in [5, 10]:
            np.random.seed(self.seed + case_id)
            
            A = (np.random.randn(size, size) * 1e6).astype(np.float64)
            B = (np.random.randn(size, size) * 1e6).astype(np.float64)
            expected = A @ B
            
            dataset["test_cases"].append({
                "id": case_id,
                "name": f"large_numbers_{size}x{size}",
                "matrix_a_shape": [size, size],
                "matrix_b_shape": [size, size],
                "matrix_a": A.tolist(),
                "matrix_b": B.tolist(),
                "expected_result": expected.tolist(),
                "properties": {
                    "type": "large_numbers",
                    "magnitude": "1e6",
                    "expected_precision_loss": "minimal"
                }
            })
            case_id += 1
        
        return dataset
    
    def save_dataset_json(self, dataset: Dict[str, Any], filename: str) -> Path:
        """Save dataset to JSON file"""
        filepath = self.output_dir / f"{filename}.json"
        
        # Add generation metadata
        dataset["generation_metadata"] = {
            "generated_at": datetime.now().isoformat(),
            "seed": self.seed,
            "version": "1.0",
            "generator": "SyntheticDataGenerator"
        }
        
        with open(filepath, 'w') as f:
            json.dump(dataset, f, indent=2)
        
        logger.info(f"Saved dataset to: {filepath}")
        return filepath
    
    def save_dataset_hdf5(self, dataset: Dict[str, Any], filename: str) -> Path:
        """Save dataset to HDF5 file (more efficient for large arrays)"""
        filepath = self.output_dir / f"{filename}.h5"
        
        with h5py.File(filepath, 'w') as f:
            # Save metadata
            metadata_group = f.create_group('metadata')
            for key, value in dataset['metadata'].items():
                if isinstance(value, (list, np.ndarray)):
                    metadata_group.create_dataset(key, data=value)
                else:
                    metadata_group.attrs[key] = value
            
            # Save test cases
            cases_group = f.create_group('test_cases')
            for i, case in enumerate(dataset['test_cases']):
                case_group = cases_group.create_group(f'case_{i}')
                
                # Save arrays
                case_group.create_dataset('matrix_a', data=np.array(case['matrix_a']))
                case_group.create_dataset('matrix_b', data=np.array(case['matrix_b']))
                case_group.create_dataset('expected_result', data=np.array(case['expected_result']))
                
                # Save attributes
                for key, value in case.items():
                    if key not in ['matrix_a', 'matrix_b', 'expected_result']:
                        if isinstance(value, dict):
                            props_group = case_group.create_group(key)
                            for prop_key, prop_value in value.items():
                                props_group.attrs[prop_key] = prop_value
                        else:
                            case_group.attrs[key] = value
        
        logger.info(f"Saved dataset to HDF5: {filepath}")
        return filepath
    
    def generate_all_datasets(self) -> Dict[str, Path]:
        """Generate all synthetic datasets"""
        
        logger.info("Generating all synthetic datasets...")
        
        generated_files = {}
        
        # Basic matrices
        basic_sizes = [
            (10, 10, 10, 10),
            (20, 20, 20, 20),
            (50, 50, 50, 50),
            (100, 100, 100, 100)
        ]
        basic_dataset = self.generate_basic_matrices(basic_sizes, samples_per_size=5)
        generated_files['basic'] = self.save_dataset_json(basic_dataset, 'basic_matrices')
        
        # Special matrices
        special_dataset = self.generate_special_matrices()
        generated_files['special'] = self.save_dataset_json(special_dataset, 'special_matrices')
        
        # Stress test matrices
        stress_dataset = self.generate_stress_test_matrices()
        generated_files['stress'] = self.save_dataset_json(stress_dataset, 'stress_test_matrices')
        
        # Precision test matrices
        precision_dataset = self.generate_precision_test_matrices()
        generated_files['precision'] = self.save_dataset_json(precision_dataset, 'precision_test_matrices')
        
        # Generate summary
        summary = {
            "generated_datasets": len(generated_files),
            "total_test_cases": sum(len(ds.get('test_cases', [])) for ds in [
                basic_dataset, special_dataset, stress_dataset, precision_dataset
            ]),
            "files": {name: str(path) for name, path in generated_files.items()},
            "generated_at": datetime.now().isoformat(),
            "seed": self.seed
        }
        
        summary_path = self.output_dir / 'dataset_summary.json'
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        generated_files['summary'] = summary_path
        
        logger.info(f"Generated {len(generated_files)} dataset files with {summary['total_test_cases']} total test cases")
        
        return generated_files

def main():
    parser = argparse.ArgumentParser(description='Generate synthetic datasets for SmartCompute testing')
    parser.add_argument('--seed', type=int, default=42, help='Random seed for reproducibility')
    parser.add_argument('--output', default='datasets/synthetic', help='Output directory')
    parser.add_argument('--dataset', choices=['basic', 'special', 'stress', 'precision', 'all'], 
                       default='all', help='Dataset type to generate')
    parser.add_argument('--samples', type=int, default=5, help='Samples per size for basic matrices')
    
    args = parser.parse_args()
    
    generator = SyntheticDataGenerator(seed=args.seed, output_dir=args.output)
    
    if args.dataset == 'all':
        files = generator.generate_all_datasets()
        print(f"✅ Generated all datasets:")
        for name, path in files.items():
            print(f"  - {name}: {path}")
    else:
        if args.dataset == 'basic':
            basic_sizes = [(10, 10, 10, 10), (50, 50, 50, 50), (100, 100, 100, 100)]
            dataset = generator.generate_basic_matrices(basic_sizes, args.samples)
            path = generator.save_dataset_json(dataset, 'basic_matrices')
        elif args.dataset == 'special':
            dataset = generator.generate_special_matrices()
            path = generator.save_dataset_json(dataset, 'special_matrices')
        elif args.dataset == 'stress':
            dataset = generator.generate_stress_test_matrices()
            path = generator.save_dataset_json(dataset, 'stress_test_matrices')
        elif args.dataset == 'precision':
            dataset = generator.generate_precision_test_matrices()
            path = generator.save_dataset_json(dataset, 'precision_test_matrices')
        
        print(f"✅ Generated {args.dataset} dataset: {path}")

if __name__ == "__main__":
    main()