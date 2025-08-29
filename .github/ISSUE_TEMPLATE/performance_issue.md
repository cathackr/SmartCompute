---
name: Performance Issue
about: Report performance problems or slowdowns in SmartCompute
title: '[PERFORMANCE] Brief description of the performance issue'
labels: ['performance', 'needs-triage']
assignees: ''
---

## ⚡ Performance Issue Summary
A clear and concise description of the performance problem you're experiencing.

## 📊 Performance Metrics
Please provide specific measurements:

**Current Performance:**
- **Execution Time**: [e.g. 2.5 seconds]
- **Memory Usage**: [e.g. 8GB RAM]
- **CPU Usage**: [e.g. 95% for 30 seconds]
- **GPU Usage** (if applicable): [e.g. 80% GPU utilization]

**Expected Performance:**
- **Expected Execution Time**: [e.g. < 1 second]
- **Expected Memory Usage**: [e.g. < 4GB RAM]
- **Baseline/Reference**: [e.g. NumPy takes 0.5 seconds for same operation]

## 🔄 Reproducible Example
Please provide a complete, minimal example that demonstrates the performance issue:

```python
import numpy as np
import time
from smartcompute import SmartCompute

# Setup
sc = SmartCompute()
A = np.random.randn(1000, 1000).astype(np.float32)
B = np.random.randn(1000, 1000).astype(np.float32)

# Performance test
start_time = time.perf_counter()
result = sc.mult(A, B, method='auto')  # Replace with your slow operation
end_time = time.perf_counter()

print(f"Execution time: {(end_time - start_time)*1000:.2f}ms")
# Add memory profiling if possible
```

## 💻 Environment Details
**Hardware:**
- **CPU**: [e.g. Intel Core i7-12700K, 8 cores, 16 threads]
- **RAM**: [e.g. 32GB DDR4-3200]
- **GPU**: [e.g. NVIDIA RTX 4090, 24GB VRAM]
- **Storage**: [e.g. NVMe SSD, 7000 MB/s read]

**Software:**
- **OS**: [e.g. Ubuntu 22.04 LTS]
- **Python**: [e.g. 3.11.5]
- **SmartCompute**: [e.g. 1.0.0]
- **NumPy**: [e.g. 1.24.3]
- **CUDA** (if applicable): [e.g. 12.2]

## 📋 Matrix/Data Characteristics
**Input Data:**
- **Matrix A shape**: [e.g. (5000, 2000)]
- **Matrix B shape**: [e.g. (2000, 3000)]
- **Data type**: [e.g. float32]
- **Data distribution**: [e.g. random normal, sparse, structured]
- **Memory layout**: [e.g. C-contiguous, Fortran-contiguous]

**Operation Details:**
- **Method used**: [e.g. 'auto', 'fast', 'precise']
- **Repeated calls**: [e.g. single call vs 1000 iterations]
- **Batch processing**: [e.g. processing 100 matrix pairs]

## 📈 Profiling Information
If you have profiling data, please include it:

**Time Profiling** (using cProfile, line_profiler, etc.):
```
[Paste profiling output here]
```

**Memory Profiling** (using memory_profiler, tracemalloc, etc.):
```
[Paste memory profiling output here]
```

**System Monitoring** (htop, nvidia-smi, etc.):
```
[Paste system monitoring output here]
```

## 🔍 Analysis Performed
What investigation have you done?
- [ ] Compared with NumPy performance
- [ ] Tested different SmartCompute methods ('auto', 'fast', 'precise')
- [ ] Tested with different matrix sizes
- [ ] Tested with different data types
- [ ] Profiled the code
- [ ] Monitored system resources
- [ ] Tested on different hardware

## 🏁 Comparison Benchmarks
If you've compared with other libraries:

| Library | Method | Time | Memory | Notes |
|---------|--------|------|---------|-------|
| NumPy | np.dot() | 0.5s | 4GB | Baseline |
| SmartCompute | auto | 2.5s | 8GB | Current issue |
| SciPy | method | 0.7s | 4.5GB | Alternative |

## 🔧 Potential Optimizations
Do you have suggestions for improvement?
- Algorithm changes
- Memory optimizations
- Parallelization opportunities
- GPU utilization improvements
- Caching strategies

## 📊 Performance Regression
Is this a regression from a previous version?
- [ ] Yes, it was faster in version [X.X.X]
- [ ] No, consistently slow across versions
- [ ] Unknown, first time using SmartCompute
- [ ] Not applicable

If regression:
- **Previous version that worked well**: [e.g. 0.9.5]
- **Performance difference**: [e.g. 3x slower than before]

## 🎯 Performance Goals
What performance characteristics would be acceptable?
- **Target execution time**: [e.g. < 1 second]
- **Target memory usage**: [e.g. < 6GB]
- **Target throughput**: [e.g. > 100 operations/second]
- **Acceptable trade-offs**: [e.g. slightly more memory for 2x speed]

## 📋 Additional Context
- **Workload type**: [e.g. batch processing, real-time inference, interactive]
- **Frequency**: [e.g. runs once per day, 1000x per minute]
- **Business impact**: [e.g. blocks production deployment, affects user experience]
- **Constraints**: [e.g. must run on limited memory, GPU memory constraints]

## 📋 Checklist
- [ ] I have provided a minimal reproducible example
- [ ] I have included specific performance measurements
- [ ] I have tested with the latest version of SmartCompute
- [ ] I have compared performance with alternative approaches
- [ ] I have included relevant hardware/software specifications
- [ ] I have provided profiling information (if available)

---

**🚀 Thank you for helping optimize SmartCompute!**

Performance reports help us identify bottlenecks and make SmartCompute faster for everyone.