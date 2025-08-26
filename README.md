# SmartCompute

> **Performance-based anomaly detection for security monitoring**

🧠 **Intelligent performance optimization** meets 🛡️ **security monitoring** in a production-ready system that adapts to ANY architecture.

## 🌟 Overview

As a Certified Ethical Hacker and IT/OT consultant from Argentina, I was frustrated by how traditional antivirus software impacts system performance while protecting it. This led me to explore: **What if we could detect threats by monitoring how they affect system behavior?**

SmartCompute revolutionizes security monitoring by:
- **Non-intrusive detection**: Monitors performance patterns instead of scanning files
- **Intelligent optimization**: Automatically chooses between speed and precision
- **Universal compatibility**: Works on x86, ARM, with/without GPU
- **Production-ready**: Full API, database integration, monitoring service

## 🚀 Quick Start

### Option 1: Interactive Demo
```bash
cd SmartCompute
python main.py
```

### Option 2: API Server
```bash
python main.py --api
# Visit http://localhost:8000/docs for API documentation
```

### Option 3: Direct Integration
```python
from app.core.smart_compute import SmartComputeEngine
from app.core.portable_system import PortableSystemDetector

# Initialize system
detector = PortableSystemDetector()
engine = SmartComputeEngine()

# Establish baseline and detect anomalies
detector.run_performance_baseline(30)
anomalies = detector.detect_anomalies()
print(f"Anomaly score: {anomalies['anomaly_score']}")
```

## 🏗️ Architecture

```
SmartCompute/
├── app/
│   ├── core/                 # Core algorithms
│   │   ├── smart_compute.py  # Intelligent optimization engine
│   │   └── portable_system.py # Multi-architecture compatibility
│   ├── api/                  # FastAPI endpoints
│   │   └── main.py          # REST API implementation
│   ├── services/            # Business logic
│   │   └── monitoring.py    # Continuous monitoring service
│   └── models/              # Database models
│       └── database.py      # SQLAlchemy schemas
├── main.py                  # CLI entry point
├── requirements.txt         # Dependencies
└── docs/                   # Documentation
```

## 🎯 Core Features

### 1. Intelligent Performance Optimization
```python
# Automatically chooses between speed and precision
result = engine.smart_multiply(
    matrix_a, matrix_b,
    precision_needed=0.95,    # Minimum 95% accuracy
    speed_priority=0.7        # Prefer speed when possible
)
```

### 2. Universal Hardware Compatibility
- ✅ **x86/x64** (Intel/AMD processors)
- ✅ **ARM** (Raspberry Pi, Mac M1/M2, mobile)
- ✅ **GPU Support** (NVIDIA CUDA, AMD ROCm, Intel integrated)
- ✅ **Fallback Mode** (CPU-only for any system)

### 3. Real-time Anomaly Detection
```python
# Establish baseline behavior
detector.run_performance_baseline(60)

# Continuous monitoring
anomaly = detector.detect_anomalies()
if anomaly['severity'] == 'high':
    trigger_security_alert(anomaly)
```

### 4. Production-Ready API
```bash
curl -X POST "http://localhost:8000/optimize" \
     -H "Content-Type: application/json" \
     -d '{"precision_needed": 0.95, "speed_priority": 0.5}'
```

## 📊 How It Works

### The Innovation: Behavioral Detection
Instead of scanning files (traditional approach), SmartCompute monitors system behavior patterns:

```python
# Traditional antivirus: Scan every file (slow, resource-intensive)
scan_all_files()  # ❌ High system impact

# SmartCompute: Monitor performance patterns (elegant, efficient)
baseline = establish_normal_behavior()
current_metrics = get_system_metrics()
anomaly_score = calculate_deviation(current_metrics, baseline)

if anomaly_score > threshold:
    # Potential security issue detected! 🚨
    investigate_and_alert()
```

### Intelligent Decision Engine
The system automatically optimizes between speed and accuracy:

1. **Benchmark Phase**: Tests both single-thread (precise) and multi-thread (fast) methods
2. **Analysis Phase**: Measures accuracy difference and speedup factor  
3. **Decision Phase**: Chooses optimal method based on requirements
4. **Learning Phase**: Stores results for future optimizations
