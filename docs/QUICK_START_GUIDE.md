# 🚀 SmartCompute Quick Start Guide

<div align="center">
  <img src="../assets/smartcompute_hmi_logo.png" alt="SmartCompute Logo" width="150">
  
  **Get up and running in 5 minutes** | [🇪🇸 Español](GUIA_INICIO_RAPIDO.md)
</div>

---

## ⚡ Choose Your Path

<table>
<tr>
<td width="33%" align="center">

### 📱 **Mobile/Universal**
**Google Colab**

Perfect for iPhone, Android, tablets

[👆 Start Here](#-mobile--universal-google-colab)

</td>
<td width="33%" align="center">

### 💻 **Desktop/Server**
**Local Installation**

Full control, enterprise features

[👆 Start Here](#-desktop--server-installation)

</td>
<td width="33%" align="center">

### 🏭 **Industrial**
**Network Monitoring**

Critical infrastructure protection

[👆 Start Here](#-industrial--network-monitoring)

</td>
</tr>
</table>

---

## 📱 Mobile / Universal (Google Colab)

**✅ Works on: iPhone, Android, tablets, laptops, desktops**  
**⏱️ Time: 2-3 minutes**  
**💰 Cost: 100% Free (Google Colab)**

### Step 1: Open Google Colab
👆 **Click here:** [https://colab.research.google.com](https://colab.research.google.com)

### Step 2: Create New Notebook
- Click **"+ New notebook"**
- You'll see an empty code cell

### Step 3: Copy & Paste This Code

**Cell 1 - Download SmartCompute:**
```python
# Download and setup SmartCompute
!git clone https://github.com/cathackr/SmartCompute.git
%cd SmartCompute
!pip install -r requirements-core.txt
```

**Cell 2 - Run Interactive Demo:**
```python
# Run the interactive cybersecurity demo
!python examples/colab_interactive_demo.py
```

### Step 4: Watch the Magic! ✨

You'll see:
- 🚨 **Real-time threat alerts** with color coding
- 📊 **Animated performance charts**
- 🎯 **Security score tracking**  
- 💻 **Mobile-optimized interface**

### 🎮 What You're Seeing

```
🔴 CRITICAL THREAT (Score: 0.87)
   192.168.1.45:2234 → 10.0.0.1:22
   Type: SSH Brute Force | Confidence: 94%

📊 Performance: EXCELLENT (8.5ms avg)
⚡ Events Processed: 150/150
🛡️ Threats Detected: 23 (15.3%)
```

### 🔗 Optional: Web Dashboard
```python
# OPTIONAL: Start full web server
!python main.py --starter &

# Access dashboard (Colab will show the public URL)
from IPython.display import IFrame
IFrame('http://localhost:8000', width=1000, height=600)
```

---

## 💻 Desktop / Server Installation

**✅ Works on: Windows, macOS, Linux**  
**⏱️ Time: 3-5 minutes**  
**💰 Cost: Free (Starter) / Paid (Enterprise)**

### Prerequisites Check

**Windows:**
```powershell
# Check Python version (need 3.8+)
python --version

# If not installed:
winget install Python.Python.3.11
```

**macOS:**
```bash
# Check Python version
python3 --version

# If not installed:
brew install python
```

**Linux:**
```bash
# Check Python version
python3 --version

# If not installed (Ubuntu/Debian):
sudo apt update && sudo apt install python3 python3-pip git
```

### Step 1: Download SmartCompute
```bash
git clone https://github.com/cathackr/SmartCompute.git
cd SmartCompute
```

### Step 2: Install Dependencies
```bash
# For Starter version (free)
pip install -r requirements-core.txt

# For Enterprise version (paid)
pip install -r requirements.txt
```

### Step 3: First Run
```bash
# Quick demo
python examples/synthetic_demo.py

# Full Starter version
python main.py --starter

# Enterprise version (if licensed)
python main.py --enterprise --api
```

### Step 4: Access Dashboard

Open your browser and go to:
- **Starter:** http://localhost:8000
- **Enterprise:** http://localhost:8000 (with additional features)

### 🎯 What You'll See

**Starter Dashboard:**
- System metrics (CPU, Memory, Network)
- Basic threat detection
- Simple alerting

**Enterprise Dashboard:**
- Advanced AI threat detection
- Custom reporting
- API access
- Multi-user support

---

## 🏭 Industrial / Network Monitoring

**✅ Works on: Industrial networks, PLCs, SCADA systems**  
**⏱️ Time: 5-10 minutes**  
**💰 Cost: Paid license required**

### Prerequisites

- **Network access**: Requires network monitoring privileges
- **Protocols**: Modbus, Profinet, OPC UA, EtherNet/IP
- **Permissions**: sudo/administrator access

### Step 1: Download Industrial Edition
```bash
git clone https://github.com/cathackr/SmartCompute.git
cd SmartCompute/smartcompute_industrial
```

### Step 2: Install Industrial Dependencies
```bash
# Requires elevated privileges for network access
sudo pip install -r requirements_industrial.txt
```

### Step 3: Configure Network Monitoring
```bash
# Edit configuration
nano industrial_config.yaml

# Example configuration:
network_monitoring:
  target_networks:
    - "192.168.1.0/24"    # Your industrial network
    - "10.0.0.0/16"       # Extended network
  protocols:
    modbus: true
    profinet: true
    opc_ua: true
```

### Step 4: Start Industrial Monitoring
```bash
# Start with network intelligence
sudo ./start_network_intelligence.sh

# Or manual start
sudo python network_api.py
```

### Step 5: Access Industrial Dashboard

Open: **http://127.0.0.1:8002**

### 🎯 Industrial Features

- **🏭 Protocol Analysis**: Real-time Modbus, Profinet monitoring
- **🗺️ Network Topology**: Automatic device discovery
- **⚠️ Conflict Detection**: IP conflicts, high latency alerts
- **📊 Performance Metrics**: Industrial KPIs and SLAs
- **🛡️ Security Monitoring**: OT-specific threat detection

---

## 🛠️ Troubleshooting

### Common Issues

**❌ "Command not found" / "python not recognized"**
```bash
# Make sure Python is installed and in PATH
python --version  # or python3 --version

# Windows: Add Python to PATH in System Environment Variables
# macOS/Linux: Add to ~/.bashrc or ~/.zshrc
export PATH="/usr/local/bin/python3:$PATH"
```

**❌ "Permission denied" / "Access denied"**
```bash
# Install as user (recommended)
pip install --user -r requirements-core.txt

# Or use virtual environment
python -m venv smartcompute_env
source smartcompute_env/bin/activate  # Windows: smartcompute_env\Scripts\activate
pip install -r requirements-core.txt
```

**❌ "Port 8000 already in use"**
```bash
# Check what's using the port
netstat -tulpn | grep 8000

# Kill the process or use different port
python main.py --starter --port 8001
```

**❌ Google Colab "Runtime disconnected"**
- This is normal - Colab times out after inactivity
- Simply re-run the cells to restart
- Your work is auto-saved to Google Drive

### Performance Tips

**🚀 Speed up installation:**
```bash
# Use faster package index
pip install -r requirements-core.txt --index-url https://pypi.org/simple/

# Install in parallel (Linux/macOS)
pip install -r requirements-core.txt --use-feature=fast-deps
```

**📊 Monitor resource usage:**
```bash
# Check CPU/memory usage
htop  # Linux/macOS
taskmgr  # Windows

# SmartCompute built-in diagnostics
python -m smartcompute.diagnostics
```

---

## 🎯 Next Steps

### After Basic Setup

1. **📖 Read the docs**: [Technical Documentation](TECHNICAL_DOCUMENTATION.md)
2. **🏢 Upgrade to Enterprise**: [Enterprise Guide](ENTERPRISE_GUIDE.md)
3. **🔗 Integrate with your tools**: APIs, SIEM, cloud platforms
4. **📞 Get support**: Issues, professional support, consulting

### Advanced Configuration

**Custom Monitoring:**
```python
# Custom metrics collection
from smartcompute import SmartComputeEngine

engine = SmartComputeEngine()
engine.add_metric('custom_cpu', source='your_app')
engine.start_monitoring(interval=10)
```

**API Integration:**
```python
# Connect to external systems
import requests

# Send alerts to Slack
def send_alert(alert):
    requests.post('https://hooks.slack.com/your-webhook', 
                  json={'text': f'🚨 SmartCompute Alert: {alert}'})

engine.on_alert(send_alert)
```

### Production Deployment

- **🐳 Docker**: `docker-compose up -d`
- **☁️ Cloud**: AWS, Azure, Google Cloud
- **🎛️ Kubernetes**: Enterprise-grade orchestration
- **🏢 On-premises**: High-availability setup

---

## 💡 Quick Tips

### For Beginners
- Start with Google Colab - it's the easiest way
- Run the interactive demo first to see what SmartCompute can do
- Don't worry about configuration - defaults work great

### For IT Professionals  
- Use the desktop installation for production
- Enable API access for integrations
- Consider Enterprise edition for multi-user environments

### For Industrial Engineers
- Industrial edition requires network privileges
- Test on a development network first
- Configure protocol-specific monitoring carefully

---

<div align="center">

### 🎉 Congratulations!

**You now have SmartCompute running and protecting your infrastructure.**

**Questions?** [📧 Contact Support](mailto:ggwre04p0@mozmail.com) | [💬 Community](https://github.com/cathackr/SmartCompute/discussions)

---

**⭐ Found this helpful?** [Give us a star on GitHub](https://github.com/cathackr/SmartCompute) 

</div>