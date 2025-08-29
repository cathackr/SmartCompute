#!/usr/bin/env python3
"""
Simple latency benchmark - exactly as requested
"""

import requests
import time  
import statistics

# Configuration - adjust URL to match available endpoint
URL = 'http://127.0.0.1:8000/optimize'  # Using /optimize endpoint (port 8000 as discovered)
N = 100

# Payload for /optimize endpoint
PAYLOAD = {
    "precision_needed": 0.95,
    "speed_priority": 0.5, 
    "enable_verbose": False
}

print(f"🏃 Running {N} requests to {URL}")
print("⏱️  Measuring latency...")

times = []
for i in range(N):
    try:
        t0 = time.perf_counter()
        r = requests.post(URL, json=PAYLOAD, timeout=10)
        times.append((time.perf_counter()-t0)*1000)
        
        # Progress indicator
        if (i + 1) % 10 == 0:
            print(f"   {i + 1}/{N} completed...")
            
    except Exception as e:
        print(f"   ❌ Request {i+1} failed: {e}")

if times:
    print(f"\n📊 Results (n={len(times)}):")
    print(f"   mean_ms: {statistics.mean(times):.2f}")
    print(f"   median (p50): {statistics.median(times):.2f}")
    
    if len(times) > 1:
        times_sorted = sorted(times)
        p95 = times_sorted[int(0.95*len(times))-1] if len(times) > 1 else times[0]
        p99 = times_sorted[int(0.99*len(times))-1] if len(times) > 1 else times[0]
        
        print(f"   p95: {p95:.2f}")
        print(f"   p99: {p99:.2f}")
        
        # Validate claims
        print(f"\n🎯 Validation:")
        print(f"   Mean <50ms: {'✅ PASS' if statistics.mean(times) < 50 else '❌ FAIL'}")
        print(f"   P95 <100ms: {'✅ PASS' if p95 < 100 else '❌ FAIL'}")
else:
    print("❌ No successful requests completed!")

# Original compact format as requested
if times:
    n_actual = len(times)
    mean_ms = statistics.mean(times)
    p50 = statistics.median(times)
    
    times_sorted = sorted(times)
    p95 = times_sorted[int(0.95*n_actual)-1] if n_actual > 1 else times[0]
    p99 = times_sorted[int(0.99*n_actual)-1] if n_actual > 1 else times[0]
    
    print(f"\n📋 Compact format:")
    print("n", n_actual, "mean_ms", mean_ms, "p50", p50, "p95", p95, "p99", p99)