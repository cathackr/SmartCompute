# SmartCompute
Performance-based anomaly detection for security monitoring
# SmartCompute

> My first GitHub repository - Performance-based anomaly detection system

## Background

As a Certified Ethical Hacker and IT/OT consultant from Argentina, I was frustrated by how traditional antivirus software impacts system performance while protecting it. This led me to explore: **What if we could detect threats by monitoring how they affect system behavior?wtf?yes**

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
