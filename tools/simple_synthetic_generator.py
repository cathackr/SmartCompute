#!/usr/bin/env python3
"""
Simple Synthetic Dataset Generator for SmartCompute (no external dependencies)
"""

import json
import numpy as np
from pathlib import Path
import sys
from datetime import datetime

def generate_basic_datasets(output_dir="datasets/synthetic"):
    """Generate basic synthetic datasets"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print("Generating synthetic datasets...")
    
    # Set seed for reproducibility
    np.random.seed(42)
    
    # Basic matrices dataset
    basic_dataset = {
        "metadata": {
            "name": "basic_matrices",
            "description": "Basic random matrices for multiplication testing",
            "type": "float32",
            "generated_at": datetime.now().isoformat()
        },
        "test_cases": []
    }
    
    sizes = [(10, 10, 10, 10), (20, 20, 20, 20), (50, 50, 50, 50)]
    case_id = 0
    
    for m1, n1, m2, n2 in sizes:
        for sample in range(3):  # 3 samples per size
            # Generate matrices
            A = np.random.randn(m1, n1).astype(np.float32)
            B = np.random.randn(m2, n2).astype(np.float32)
            expected = np.dot(A, B)
            
            test_case = {
                "id": case_id,
                "name": f"basic_{m1}x{n1}_{m2}x{n2}_sample_{sample}",
                "matrix_a_shape": [m1, n1],
                "matrix_b_shape": [m2, n2],
                "matrix_a": A.tolist(),
                "matrix_b": B.tolist(),
                "expected_result": expected.tolist(),
                "properties": {
                    "type": "basic",
                    "a_norm": float(np.linalg.norm(A)),
                    "b_norm": float(np.linalg.norm(B)),
                    "expected_norm": float(np.linalg.norm(expected))
                }
            }
            
            basic_dataset["test_cases"].append(test_case)
            case_id += 1
    
    # Save basic dataset
    basic_file = output_path / "basic_matrices.json"
    with open(basic_file, 'w') as f:
        json.dump(basic_dataset, f, indent=2)
    
    # Special matrices dataset
    special_dataset = {
        "metadata": {
            "name": "special_matrices",
            "description": "Matrices with special mathematical properties",
            "type": "float32",
            "generated_at": datetime.now().isoformat()
        },
        "test_cases": []
    }
    
    case_id = 0
    sizes = [5, 10, 20]
    
    for size in sizes:
        # Identity matrix test
        A = np.eye(size, dtype=np.float32)
        B = np.random.randn(size, size).astype(np.float32)
        expected = B.copy()
        
        special_dataset["test_cases"].append({
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
        
        # Zero matrix test
        A = np.zeros((size, size), dtype=np.float32)
        B = np.random.randn(size, size).astype(np.float32)
        expected = np.zeros((size, size), dtype=np.float32)
        
        special_dataset["test_cases"].append({
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
    
    # Save special dataset
    special_file = output_path / "special_matrices.json"
    with open(special_file, 'w') as f:
        json.dump(special_dataset, f, indent=2)
    
    # Generate summary
    summary = {
        "generated_datasets": 2,
        "total_test_cases": len(basic_dataset["test_cases"]) + len(special_dataset["test_cases"]),
        "files": {
            "basic": str(basic_file),
            "special": str(special_file)
        },
        "generated_at": datetime.now().isoformat(),
        "seed": 42
    }
    
    summary_file = output_path / "dataset_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"✅ Generated datasets:")
    print(f"  - Basic matrices: {basic_file} ({len(basic_dataset['test_cases'])} cases)")
    print(f"  - Special matrices: {special_file} ({len(special_dataset['test_cases'])} cases)")
    print(f"  - Summary: {summary_file}")
    print(f"  - Total test cases: {summary['total_test_cases']}")
    
    return summary

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='datasets/synthetic', help='Output directory')
    args = parser.parse_args()
    
    generate_basic_datasets(args.output)