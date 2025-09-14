#!/bin/bash
"""
SmartCompute Installation Script
Instala SmartCompute CLI en el sistema para uso global
"""

echo "🚀 SmartCompute Installation Script"
echo "=================================="

# Check if running as root for system-wide install
if [[ $EUID -eq 0 ]]; then
    INSTALL_DIR="/usr/local/bin"
    INSTALL_TYPE="system-wide"
else
    INSTALL_DIR="$HOME/.local/bin"
    INSTALL_TYPE="user-local"
    mkdir -p "$INSTALL_DIR"
fi

echo "📁 Installing SmartCompute ($INSTALL_TYPE)"
echo "   Target directory: $INSTALL_DIR"

# Get current script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create SmartCompute wrapper script
cat > "$INSTALL_DIR/smartcompute" << 'EOF'
#!/bin/bash
# SmartCompute CLI Wrapper
SMARTCOMPUTE_HOME="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"

# Try to find SmartCompute installation
if [ -f "/usr/local/share/smartcompute/smartcompute" ]; then
    SMARTCOMPUTE_HOME="/usr/local/share/smartcompute"
elif [ -f "$HOME/.local/share/smartcompute/smartcompute" ]; then
    SMARTCOMPUTE_HOME="$HOME/.local/share/smartcompute"
elif [ -f "$(dirname "$0")/smartcompute_infrastructure.py" ]; then
    SMARTCOMPUTE_HOME="$(dirname "$0")"
else
    echo "❌ SmartCompute installation not found"
    echo "Please run install_smartcompute.sh from the SmartCompute directory"
    exit 1
fi

cd "$SMARTCOMPUTE_HOME"
exec python3 smartcompute "$@"
EOF

chmod +x "$INSTALL_DIR/smartcompute"

# Install SmartCompute files
if [[ $EUID -eq 0 ]]; then
    SMARTCOMPUTE_HOME="/usr/local/share/smartcompute"
else
    SMARTCOMPUTE_HOME="$HOME/.local/share/smartcompute"
fi

echo "📦 Copying SmartCompute files to $SMARTCOMPUTE_HOME"
mkdir -p "$SMARTCOMPUTE_HOME"
mkdir -p "$SMARTCOMPUTE_HOME/examples"

# Copy main files
cp "$SCRIPT_DIR/smartcompute" "$SMARTCOMPUTE_HOME/"
cp "$SCRIPT_DIR/smartcompute_infrastructure.py" "$SMARTCOMPUTE_HOME/"
cp "$SCRIPT_DIR/smartcompute_express.py" "$SMARTCOMPUTE_HOME/"
cp "$SCRIPT_DIR/smartcompute_dashboard_template.py" "$SMARTCOMPUTE_HOME/"

# Copy examples
cp "$SCRIPT_DIR/examples/"*.py "$SMARTCOMPUTE_HOME/examples/" 2>/dev/null || true

# Copy requirements and scripts
cp "$SCRIPT_DIR/scripts/"*.py "$SMARTCOMPUTE_HOME/scripts/" 2>/dev/null || true
mkdir -p "$SMARTCOMPUTE_HOME/scripts"
cp "$SCRIPT_DIR/scripts/"*.py "$SMARTCOMPUTE_HOME/scripts/" 2>/dev/null || true

echo "✅ SmartCompute installed successfully!"
echo ""
echo "📋 Usage examples:"
echo "   smartcompute scan infrastructure    # Analyze Docker, AD, Proxmox"
echo "   smartcompute scan network           # Complete OSI analysis"
echo "   smartcompute scan docker            # Docker-specific analysis"
echo "   smartcompute scan apis              # Layer 7 API analysis"
echo "   smartcompute scan iot               # IoT sensor monitoring"
echo "   smartcompute --help                 # Show all options"
echo ""

# Check if directory is in PATH
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo "⚠️  Warning: $INSTALL_DIR is not in your PATH"
    echo "Add this line to your ~/.bashrc or ~/.profile:"
    echo "   export PATH=\"$INSTALL_DIR:\$PATH\""
    echo ""
fi

echo "🎯 Quick test - run: smartcompute scan infrastructure"