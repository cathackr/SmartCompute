#!/bin/bash

# SmartCompute Network Intelligence System Startup Script
# Complete network monitoring, protocol analysis, and security integration

set -e  # Exit on any error

echo "🌐 Starting SmartCompute Network Intelligence System..."
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "network_api.py" ]; then
    echo "❌ Error: network_api.py not found in current directory"
    echo "Please run this script from the smartcompute_industrial directory"
    exit 1
fi

# Check Python dependencies
echo "📋 Checking dependencies..."

python3 -c "import fastapi, uvicorn, scapy, asyncio, ipaddress" 2>/dev/null || {
    echo "❌ Missing required Python packages"
    echo "Installing dependencies..."
    
    # Check if running as root for scapy
    if [ "$EUID" -ne 0 ]; then
        echo "⚠️  Warning: Some network functions may require root privileges"
        echo "   Consider running with sudo for full functionality"
    fi
    
    pip3 install fastapi uvicorn scapy psutil
}

echo "✅ Dependencies OK"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p ui/css ui/js
mkdir -p logs
mkdir -p network_data
echo "✅ Directories created"

# Check network permissions
echo "🔍 Checking network permissions..."
if [ "$EUID" -ne 0 ]; then
    echo "ℹ️  Running without root privileges"
    echo "   - Network discovery will use basic scanning"
    echo "   - Packet capture features may be limited"
    echo "   - For full functionality, consider: sudo ./start_network_intelligence.sh"
else
    echo "✅ Running with elevated privileges - full functionality available"
fi

# Check if UI files exist
if [ ! -f "ui/network_dashboard.html" ]; then
    echo "❌ Warning: Network dashboard UI files not found"
    echo "Expected files:"
    echo "  - ui/network_dashboard.html"
    echo "  - ui/css/network_dashboard.css"
    echo "  - ui/js/network_dashboard.js"
fi

# Display system information
echo ""
echo "🖥️  System Information:"
echo "   Hostname: $(hostname)"
echo "   IP Address: $(hostname -I | awk '{print $1}')"
echo "   Network Interfaces: $(ip link show | grep -E '^[0-9]+:' | cut -d: -f2 | tr -d ' ' | grep -v lo | head -3 | tr '\n' ' ')"

# Start the Network Intelligence API
echo ""
echo "🚀 Starting Network Intelligence API Server..."
echo ""
echo "🌐 Dashboard available at: http://127.0.0.1:8002"
echo "📋 API Documentation at: http://127.0.0.1:8002/docs"
echo "🗺️  Network topology at: http://127.0.0.1:8002/api/network/topology"
echo ""
echo "🔧 Network Intelligence Features:"
echo "  ✅ Multi-protocol analysis (Modbus, Profinet, EtherNet/IP, OPC UA)"
echo "  ✅ Industrial device discovery and classification"
echo "  ✅ Network performance monitoring"
echo "  ✅ IP/MAC/VLAN conflict detection"
echo "  ✅ Security device integration (Cisco, Fortigate, Palo Alto)"
echo "  ✅ Cisco XDR and Umbrella integration"
echo "  ✅ Real-time threat intelligence sharing"
echo "  ✅ Network topology visualization"
echo "  ✅ Automated security alerts"
echo ""
echo "🔒 Security Integrations:"
echo "  • Cisco XDR - Threat intelligence sharing"
echo "  • Cisco Umbrella - Domain reputation"
echo "  • Fortinet - Firewall rule analysis"
echo "  • Palo Alto - Traffic inspection"
echo "  • Check Point - Security policy review"
echo "  • OpenGear - Console server monitoring"
echo ""
echo "⚙️  Configuration:"
echo "  • Use the ⚙️ button in the dashboard to configure network scanning"
echo "  • Add security devices via API or dashboard"
echo "  • Configure Cisco integrations for enhanced threat intelligence"
echo ""
echo "📊 Available Endpoints:"
echo "  • GET /api/network/devices - Discovered devices"
echo "  • GET /api/network/topology - Network topology"
echo "  • GET /api/network/protocols - Protocol analysis"
echo "  • GET /api/network/performance - Performance metrics"
echo "  • GET /api/network/alerts - Security alerts"
echo "  • GET /api/network/conflicts - Network conflicts"
echo "  • POST /api/network/scan - Trigger manual scan"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================================="

# Create log file
touch logs/network_intelligence.log

# Start the server with logging
python3 network_api.py 2>&1 | tee logs/network_intelligence.log