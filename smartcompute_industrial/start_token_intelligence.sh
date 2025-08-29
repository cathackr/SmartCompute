#!/bin/bash

# SmartCompute Token Intelligence System Startup Script
# This script starts the complete token monitoring and dashboard system

set -e  # Exit on any error

echo "🚀 Starting SmartCompute Token Intelligence System..."
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "token_api.py" ]; then
    echo "❌ Error: token_api.py not found in current directory"
    echo "Please run this script from the smartcompute_industrial directory"
    exit 1
fi

# Check Python dependencies
echo "📋 Checking dependencies..."

python3 -c "import fastapi, uvicorn, prometheus_client, psutil" 2>/dev/null || {
    echo "❌ Missing required Python packages"
    echo "Installing dependencies..."
    pip3 install fastapi uvicorn prometheus-client psutil
}

echo "✅ Dependencies OK"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p ui/css ui/js
mkdir -p /tmp/smartcompute_preferences
echo "✅ Directories created"

# Check if UI files exist
if [ ! -f "ui/token_dashboard.html" ]; then
    echo "❌ Warning: Dashboard UI files not found"
    echo "Expected files:"
    echo "  - ui/token_dashboard.html"
    echo "  - ui/css/token_dashboard.css" 
    echo "  - ui/js/token_dashboard.js"
    echo ""
    echo "Please ensure UI files are in the correct location"
fi

# Start the API server
echo "🌐 Starting Token Intelligence API Server..."
echo ""
echo "📊 Dashboard will be available at: http://127.0.0.1:8001"
echo "📋 API Documentation at: http://127.0.0.1:8001/docs"
echo "⚙️ Customization panel: Click the ⚙️ icon in the dashboard"
echo ""
echo "🔧 Features included:"
echo "  ✅ Real-time token monitoring"
echo "  ✅ Cost tracking and budgets"
echo "  ✅ Prometheus metrics integration"
echo "  ✅ Customizable dashboard labels"
echo "  ✅ Multi-language support (ES/EN/PT)"
echo "  ✅ Unit conversions (currency, temperature, time)"
echo "  ✅ AI provider transparency indicators"
echo "  ✅ Smart optimization suggestions"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================================="

# Start the server
python3 token_api.py