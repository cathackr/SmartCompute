# SmartCompute
Performance-based anomaly detection for security monitoring
# SmartCompute

> My first GitHub repository - Performance-based anomaly detection system

## Background

As a Certified Ethical Hacker and IT/OT consultant from Argentina, I was frustrated by how traditional antivirus software impacts system performance while protecting it. This led me to explore: **What if we could detect threats by monitoring how they affect system behavior?wtf?**

## The Concept

Instead of scanning files (intrusive), monitor system performance patterns (elegant):

```python
# Establish normal baseline
baseline_cpu = learn_normal_patterns()

# Detect anomalies in real-time
current_cpu = psutil.cpu_percent()
z_score = abs(current_cpu - baseline_cpu) / std_dev

if z_score > 2.5:
    # Potential security issue detected
    investigate_threat()
## 🚀 NEW: Portable Edition

**SmartCompute Portable** - Works on ANY system:
- ✅ x86/x64 (Intel/AMD)  
- ✅ ARM (Raspberry Pi, Mac M1/M2)
- ✅ Windows/Linux/macOS
- ✅ With or without GPU
- ✅ Auto-detects and optimizes

### Quick Test:
```bash
python3 smartcompute_portable.py
