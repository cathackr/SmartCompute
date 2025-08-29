#!/usr/bin/env python3
"""
SmartCompute Latency Benchmark Tool
Validates API response time claims through systematic testing
"""

import requests
import time
import statistics
import sys
import argparse
import json
from typing import List, Dict, Any


def run_latency_benchmark(url: str, payload: Dict[str, Any], n: int = 100, timeout: int = 10) -> Dict[str, float]:
    """
    Run latency benchmark against specified endpoint
    
    Args:
        url: API endpoint to test
        payload: JSON payload to send
        n: Number of requests to make
        timeout: Request timeout in seconds
    
    Returns:
        Dictionary with latency statistics
    """
    times = []
    successful_requests = 0
    failed_requests = 0
    
    print(f"🏃 Running latency benchmark...")
    print(f"   Endpoint: {url}")
    print(f"   Requests: {n}")
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    print()
    
    # Warmup request
    print("🔥 Warmup request...")
    try:
        warmup_start = time.perf_counter()
        r = requests.post(url, json=payload, timeout=timeout)
        warmup_time = (time.perf_counter() - warmup_start) * 1000
        print(f"   Warmup completed: {warmup_time:.2f}ms (status: {r.status_code})")
    except Exception as e:
        print(f"   ⚠️  Warmup failed: {e}")
        print("   This might indicate server connectivity issues")
    
    print()
    print("📊 Running benchmark requests...")
    
    # Main benchmark loop
    for i in range(n):
        try:
            t0 = time.perf_counter()
            r = requests.post(url, json=payload, timeout=timeout)
            request_time = (time.perf_counter() - t0) * 1000
            
            if r.status_code == 200:
                times.append(request_time)
                successful_requests += 1
            else:
                failed_requests += 1
                print(f"   ⚠️  Request {i+1} failed with status {r.status_code}")
                
        except requests.exceptions.Timeout:
            failed_requests += 1
            print(f"   ⏰ Request {i+1} timed out after {timeout}s")
            
        except Exception as e:
            failed_requests += 1
            print(f"   ❌ Request {i+1} failed: {e}")
        
        # Progress indicator
        if (i + 1) % 10 == 0:
            print(f"   Completed {i+1}/{n} requests...")
    
    if not times:
        print("❌ No successful requests completed!")
        return {}
    
    # Calculate statistics
    times_sorted = sorted(times)
    n_success = len(times)
    
    stats = {
        'requests_total': n,
        'requests_successful': successful_requests,
        'requests_failed': failed_requests,
        'success_rate': (successful_requests / n) * 100,
        'mean_ms': statistics.mean(times),
        'median_ms': statistics.median(times),
        'std_dev_ms': statistics.stdev(times) if len(times) > 1 else 0,
        'min_ms': min(times),
        'max_ms': max(times),
        'p50_ms': times_sorted[int(0.50 * n_success) - 1] if n_success > 0 else 0,
        'p90_ms': times_sorted[int(0.90 * n_success) - 1] if n_success > 1 else 0,
        'p95_ms': times_sorted[int(0.95 * n_success) - 1] if n_success > 1 else 0,
        'p99_ms': times_sorted[int(0.99 * n_success) - 1] if n_success > 1 else 0
    }
    
    return stats


def print_benchmark_results(stats: Dict[str, float]):
    """Print formatted benchmark results"""
    print("\n" + "="*60)
    print("📊 LATENCY BENCHMARK RESULTS")
    print("="*60)
    
    print(f"Requests Total:     {stats['requests_total']:>8}")
    print(f"Requests Successful: {stats['requests_successful']:>7}")
    print(f"Requests Failed:    {stats['requests_failed']:>8}")
    print(f"Success Rate:       {stats['success_rate']:>7.1f}%")
    print()
    
    print("📈 LATENCY STATISTICS (milliseconds)")
    print("-"*40)
    print(f"Mean:        {stats['mean_ms']:>10.2f}ms")
    print(f"Median:      {stats['median_ms']:>10.2f}ms")
    print(f"Std Dev:     {stats['std_dev_ms']:>10.2f}ms")
    print(f"Min:         {stats['min_ms']:>10.2f}ms")
    print(f"Max:         {stats['max_ms']:>10.2f}ms")
    print()
    
    print("📊 PERCENTILES")
    print("-"*40)
    print(f"P50 (median): {stats['p50_ms']:>9.2f}ms")
    print(f"P90:          {stats['p90_ms']:>9.2f}ms")
    print(f"P95:          {stats['p95_ms']:>9.2f}ms")
    print(f"P99:          {stats['p99_ms']:>9.2f}ms")
    print()


def validate_performance_claims(stats: Dict[str, float]) -> Dict[str, bool]:
    """
    Validate SmartCompute performance claims against benchmark results
    
    Returns:
        Dictionary with validation results
    """
    print("🎯 PERFORMANCE CLAIMS VALIDATION")
    print("="*40)
    
    validations = {}
    
    # SmartCompute claims <50ms response time
    claim_latency_50ms = stats['mean_ms'] < 50
    validations['latency_under_50ms'] = claim_latency_50ms
    status_50ms = "✅ PASS" if claim_latency_50ms else "❌ FAIL"
    print(f"Mean latency <50ms:    {status_50ms} ({stats['mean_ms']:.2f}ms)")
    
    # P95 should be reasonable (under 100ms)
    claim_p95_100ms = stats['p95_ms'] < 100
    validations['p95_under_100ms'] = claim_p95_100ms
    status_p95 = "✅ PASS" if claim_p95_100ms else "❌ FAIL"
    print(f"P95 latency <100ms:    {status_p95} ({stats['p95_ms']:.2f}ms)")
    
    # Success rate should be high
    claim_success_rate = stats['success_rate'] > 95
    validations['high_success_rate'] = claim_success_rate
    status_success = "✅ PASS" if claim_success_rate else "❌ FAIL"
    print(f"Success rate >95%:     {status_success} ({stats['success_rate']:.1f}%)")
    
    # Low variability (std dev should be reasonable)
    claim_low_variance = stats['std_dev_ms'] < stats['mean_ms']
    validations['low_variance'] = claim_low_variance
    status_variance = "✅ PASS" if claim_low_variance else "❌ FAIL"
    print(f"Low variance:          {status_variance} (σ={stats['std_dev_ms']:.2f}ms)")
    
    print()
    
    # Overall validation
    all_passed = all(validations.values())
    overall_status = "✅ ALL CLAIMS VALIDATED" if all_passed else "⚠️  SOME CLAIMS FAILED"
    print(f"OVERALL RESULT: {overall_status}")
    print()
    
    return validations


def main():
    """Main benchmark execution"""
    parser = argparse.ArgumentParser(description='SmartCompute Latency Benchmark')
    parser.add_argument('--url', default='http://127.0.0.1:8000/optimize',
                       help='API endpoint to benchmark (default: http://127.0.0.1:8000/optimize)')
    parser.add_argument('--port', type=int, default=8000,
                       help='Server port (default: 8000)')
    parser.add_argument('-n', '--requests', type=int, default=100,
                       help='Number of requests to make (default: 100)')
    parser.add_argument('--timeout', type=int, default=10,
                       help='Request timeout in seconds (default: 10)')
    parser.add_argument('--precision', type=float, default=0.95,
                       help='Precision parameter for optimization (default: 0.95)')
    parser.add_argument('--speed', type=float, default=0.5,
                       help='Speed priority parameter (default: 0.5)')
    parser.add_argument('--output', choices=['json', 'text'], default='text',
                       help='Output format (default: text)')
    
    args = parser.parse_args()
    
    # Build URL with custom port if specified
    if args.port != 8000:
        base_url = f"http://127.0.0.1:{args.port}"
        endpoint = args.url.split('/')[-1]  # Extract endpoint name
        url = f"{base_url}/{endpoint}"
    else:
        url = args.url
    
    # Prepare payload based on endpoint
    if 'optimize' in url:
        payload = {
            "precision_needed": args.precision,
            "speed_priority": args.speed,
            "enable_verbose": False  # Reduce noise for benchmarking
        }
    else:
        # Generic payload for other endpoints
        payload = {"sample": [0]}
    
    print("🧠 SmartCompute Latency Benchmark Tool")
    print("="*50)
    print()
    
    # Run benchmark
    try:
        stats = run_latency_benchmark(url, payload, args.requests, args.timeout)
        
        if not stats:
            print("❌ Benchmark failed - no successful requests completed")
            sys.exit(1)
        
        # Output results
        if args.output == 'json':
            print(json.dumps(stats, indent=2))
        else:
            print_benchmark_results(stats)
            validate_performance_claims(stats)
        
        # Exit with appropriate code
        if stats['success_rate'] < 50:
            sys.exit(1)  # Too many failures
        elif stats['mean_ms'] > 1000:
            sys.exit(2)  # Unacceptable latency
        else:
            sys.exit(0)  # Success
            
    except KeyboardInterrupt:
        print("\n⚠️  Benchmark interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Benchmark failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()