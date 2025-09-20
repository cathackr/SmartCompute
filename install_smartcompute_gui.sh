#!/bin/bash

# SmartCompute Enterprise GUI Installer
# Version: 2.0.0 Enterprise Edition
# Supports: Ubuntu, CentOS, Fedora, Arch Linux, macOS
# Date: 2025-09-19

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ASCII Art Banner
print_banner() {
    echo -e "${CYAN}"
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ███████╗███╗   ███╗ █████╗ ██████╗ ████████╗               ║
║   ██╔════╝████╗ ████║██╔══██╗██╔══██╗╚══██╔══╝               ║
║   ███████╗██╔████╔██║███████║██████╔╝   ██║                  ║
║   ╚════██║██║╚██╔╝██║██╔══██║██╔══██╗   ██║                  ║
║   ███████║██║ ╚═╝ ██║██║  ██║██║  ██║   ██║                  ║
║   ╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝                  ║
║                                                              ║
║    ██████╗ ██████╗ ███╗   ███╗██████╗ ██╗   ██╗████████╗    ║
║   ██╔════╝██╔═══██╗████╗ ████║██╔══██╗██║   ██║╚══██╔══╝    ║
║   ██║     ██║   ██║██╔████╔██║██████╔╝██║   ██║   ██║       ║
║   ██║     ██║   ██║██║╚██╔╝██║██╔═══╝ ██║   ██║   ██║       ║
║   ╚██████╗╚██████╔╝██║ ╚═╝ ██║██║     ╚██████╔╝   ██║       ║
║    ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝      ╚═════╝    ╚═╝       ║
║                                                              ║
║                 ENTERPRISE GUI INSTALLER                    ║
║                      Version 2.0.0                          ║
╚══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# Detect operating system
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/debian_version ]; then
            OS="ubuntu"
            PACKAGE_MANAGER="apt"
        elif [ -f /etc/redhat-release ]; then
            if grep -q "CentOS" /etc/redhat-release; then
                OS="centos"
            elif grep -q "Fedora" /etc/redhat-release; then
                OS="fedora"
            else
                OS="rhel"
            fi
            PACKAGE_MANAGER="yum"
        elif [ -f /etc/arch-release ]; then
            OS="arch"
            PACKAGE_MANAGER="pacman"
        else
            OS="unknown"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        PACKAGE_MANAGER="brew"
    else
        OS="unknown"
    fi

    log_info "Detected OS: $OS"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_warning "Running as root. Some operations may require sudo privileges."
        SUDO=""
    else
        SUDO="sudo"
    fi
}

# Install system dependencies
install_dependencies() {
    log_step "Installing system dependencies..."

    case $OS in
        "ubuntu")
            $SUDO apt update
            $SUDO apt install -y python3 python3-pip python3-venv python3-tk git curl wget
            $SUDO apt install -y build-essential libssl-dev libffi-dev
            # GUI dependencies
            $SUDO apt install -y python3-tkinter tcl-dev tk-dev
            ;;
        "centos"|"rhel")
            $SUDO yum update -y
            $SUDO yum install -y python3 python3-pip git curl wget
            $SUDO yum groupinstall -y "Development Tools"
            # GUI dependencies
            $SUDO yum install -y tkinter tcl-devel tk-devel
            ;;
        "fedora")
            $SUDO dnf update -y
            $SUDO dnf install -y python3 python3-pip python3-virtualenv git curl wget
            $SUDO dnf groupinstall -y "Development Tools"
            # GUI dependencies
            $SUDO dnf install -y python3-tkinter tcl-devel tk-devel
            ;;
        "arch")
            $SUDO pacman -Syu --noconfirm
            $SUDO pacman -S --noconfirm python python-pip git curl wget base-devel
            # GUI dependencies
            $SUDO pacman -S --noconfirm tk tcl
            ;;
        "macos")
            if ! command -v brew &> /dev/null; then
                log_info "Installing Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            brew install python3 git curl wget tcl-tk
            ;;
        *)
            log_error "Unsupported operating system: $OS"
            exit 1
            ;;
    esac

    log_success "System dependencies installed"
}

# Create virtual environment
create_venv() {
    log_step "Creating Python virtual environment..."

    VENV_DIR="$HOME/.smartcompute_venv"

    if [ -d "$VENV_DIR" ]; then
        log_warning "Virtual environment already exists. Recreating..."
        rm -rf "$VENV_DIR"
    fi

    python3 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"

    # Upgrade pip
    pip install --upgrade pip setuptools wheel

    log_success "Virtual environment created at $VENV_DIR"
}

# Install Python dependencies
install_python_deps() {
    log_step "Installing Python dependencies..."

    # Activate virtual environment
    source "$HOME/.smartcompute_venv/bin/activate"

    # Core dependencies
    pip install requests psutil netifaces scapy

    # GUI dependencies
    pip install tkinter-tooltip pillow

    # Data processing
    pip install pandas numpy matplotlib seaborn

    # Network and security
    pip install python-nmap cryptography paramiko

    # Industrial protocols
    pip install pymodbus opcua-client

    # AI and ML (optional)
    pip install scikit-learn tensorflow-lite openai-whisper || log_warning "Some AI dependencies failed to install"

    # Web and API
    pip install flask fastapi uvicorn websockets

    # Database
    pip install sqlite3-db redis-py psycopg2-binary || log_warning "Some database dependencies failed to install"

    log_success "Python dependencies installed"
}

# Create application directory
setup_app_directory() {
    log_step "Setting up application directory..."

    APP_DIR="$HOME/.smartcompute"

    if [ ! -d "$APP_DIR" ]; then
        mkdir -p "$APP_DIR"
    fi

    # Create subdirectories
    mkdir -p "$APP_DIR/config"
    mkdir -p "$APP_DIR/logs"
    mkdir -p "$APP_DIR/reports"
    mkdir -p "$APP_DIR/data"
    mkdir -p "$APP_DIR/plugins"

    # Copy application files
    if [ -f "smartcompute_enterprise_gui.py" ]; then
        cp smartcompute_enterprise_gui.py "$APP_DIR/"
        chmod +x "$APP_DIR/smartcompute_enterprise_gui.py"
    fi

    # Copy other SmartCompute files
    for file in smartcompute_*.py *.sh; do
        if [ -f "$file" ]; then
            cp "$file" "$APP_DIR/"
        fi
    done

    # Copy enterprise directory
    if [ -d "enterprise" ]; then
        cp -r enterprise "$APP_DIR/"
    fi

    log_success "Application directory setup complete"
}

# Create desktop entry (Linux only)
create_desktop_entry() {
    if [[ "$OS" != "linux-gnu"* ]]; then
        return
    fi

    log_step "Creating desktop entry..."

    DESKTOP_FILE="$HOME/.local/share/applications/smartcompute-enterprise.desktop"

    mkdir -p "$(dirname "$DESKTOP_FILE")"

    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=SmartCompute Enterprise GUI
Comment=Professional Security Analysis Tool
Exec=$HOME/.smartcompute_venv/bin/python $HOME/.smartcompute/smartcompute_enterprise_gui.py
Icon=applications-system
Terminal=false
Categories=System;Security;Network;
Keywords=security;analysis;industrial;enterprise;
EOF

    chmod +x "$DESKTOP_FILE"

    log_success "Desktop entry created"
}

# Create launch scripts
create_launch_scripts() {
    log_step "Creating launch scripts..."

    APP_DIR="$HOME/.smartcompute"

    # Linux/macOS launch script
    cat > "$APP_DIR/launch_gui.sh" << 'EOF'
#!/bin/bash
cd "$HOME/.smartcompute"
source "$HOME/.smartcompute_venv/bin/activate"
python smartcompute_enterprise_gui.py "$@"
EOF

    chmod +x "$APP_DIR/launch_gui.sh"

    # Windows batch file (if running under WSL)
    cat > "$APP_DIR/launch_gui.bat" << 'EOF'
@echo off
cd /d "%USERPROFILE%\.smartcompute"
call "%USERPROFILE%\.smartcompute_venv\Scripts\activate.bat"
python smartcompute_enterprise_gui.py %*
EOF

    # Create symlink in user's bin directory
    mkdir -p "$HOME/.local/bin"
    ln -sf "$APP_DIR/launch_gui.sh" "$HOME/.local/bin/smartcompute-gui"

    log_success "Launch scripts created"
}

# Configure firewall (if needed)
configure_firewall() {
    log_step "Configuring firewall rules..."

    case $OS in
        "ubuntu")
            if command -v ufw &> /dev/null; then
                $SUDO ufw allow 8080/tcp comment "SmartCompute Web Interface"
                $SUDO ufw allow 9090/tcp comment "SmartCompute MCP Server"
            fi
            ;;
        "centos"|"rhel"|"fedora")
            if command -v firewall-cmd &> /dev/null; then
                $SUDO firewall-cmd --permanent --add-port=8080/tcp
                $SUDO firewall-cmd --permanent --add-port=9090/tcp
                $SUDO firewall-cmd --reload
            fi
            ;;
    esac

    log_success "Firewall configured"
}

# Create configuration files
create_config_files() {
    log_step "Creating configuration files..."

    APP_DIR="$HOME/.smartcompute"
    CONFIG_DIR="$APP_DIR/config"

    # Main configuration
    cat > "$CONFIG_DIR/smartcompute.json" << 'EOF'
{
    "version": "2.0.0",
    "gui": {
        "theme": "modern",
        "auto_start": false,
        "window_size": "1400x900",
        "check_updates": true
    },
    "network": {
        "default_target": "192.168.1.0/24",
        "timeout": 30,
        "max_threads": 50
    },
    "security": {
        "encryption": "AES-256",
        "secure_storage": true,
        "audit_log": true
    },
    "reporting": {
        "default_format": "html",
        "include_charts": true,
        "auto_open": true
    },
    "ai": {
        "enabled": true,
        "model": "local",
        "max_context": 4000
    }
}
EOF

    # Logging configuration
    cat > "$CONFIG_DIR/logging.json" << 'EOF'
{
    "version": 1,
    "disable_existing_loggers": false,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s"
        }
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.FileHandler",
            "filename": "logs/smartcompute.log",
            "mode": "a"
        },
        "console": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout"
        }
    },
    "loggers": {
        "": {
            "handlers": ["default", "console"],
            "level": "INFO",
            "propagate": false
        }
    }
}
EOF

    log_success "Configuration files created"
}

# Setup systemd service (Linux only)
setup_service() {
    if [[ "$OS" != "linux-gnu"* ]] || [[ $EUID -ne 0 ]]; then
        return
    fi

    log_step "Setting up systemd service..."

    cat > /etc/systemd/system/smartcompute-server.service << EOF
[Unit]
Description=SmartCompute Enterprise Server
After=network.target

[Service]
Type=simple
User=$SUDO_USER
WorkingDirectory=$HOME/.smartcompute
ExecStart=$HOME/.smartcompute_venv/bin/python smartcompute_central_server.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable smartcompute-server.service

    log_success "Systemd service configured"
}

# Run tests
run_tests() {
    log_step "Running installation tests..."

    APP_DIR="$HOME/.smartcompute"
    source "$HOME/.smartcompute_venv/bin/activate"

    cd "$APP_DIR"

    # Test Python imports
    python3 -c "
import tkinter as tk
import requests
import psutil
print('✅ All core modules imported successfully')
"

    # Test GUI can be imported
    python3 -c "
import sys
sys.path.append('.')
from smartcompute_enterprise_gui import SmartComputeEnterpriseGUI
print('✅ GUI module imported successfully')
"

    log_success "All tests passed"
}

# Main installation function
main() {
    print_banner

    log_info "Starting SmartCompute Enterprise GUI installation..."
    log_info "This installer will set up a complete GUI environment for SmartCompute"

    # Detect system
    detect_os
    check_root

    # Installation steps
    install_dependencies
    create_venv
    install_python_deps
    setup_app_directory
    create_config_files
    create_launch_scripts
    create_desktop_entry
    configure_firewall
    setup_service
    run_tests

    # Final message
    echo -e "${GREEN}"
    cat << 'EOF'

╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                    INSTALLATION COMPLETE!                   ║
║                                                              ║
║  🚀 SmartCompute Enterprise GUI v2.0.0 is now installed    ║
║                                                              ║
║  📍 Installation Directory: ~/.smartcompute                 ║
║  🔧 Virtual Environment: ~/.smartcompute_venv               ║
║                                                              ║
║  🎯 To launch the GUI:                                      ║
║     • Command: smartcompute-gui                             ║
║     • Or: ~/.smartcompute/launch_gui.sh                     ║
║     • Desktop: SmartCompute Enterprise GUI                  ║
║                                                              ║
║  📚 Features Available:                                     ║
║     ✅ Modern GUI with tabbed interface                    ║
║     ✅ 94+ integrated security tools                       ║
║     ✅ Industrial SCADA/PLC analysis                       ║
║     ✅ AI-powered recommendations                           ║
║     ✅ Real-time monitoring and alerting                    ║
║     ✅ Compliance reporting (ISO/NIST/MITRE)               ║
║                                                              ║
║  🔗 Quick Start:                                            ║
║     1. Launch GUI: smartcompute-gui                         ║
║     2. Configure network targets                            ║
║     3. Select analysis tools                                ║
║     4. Run comprehensive scan                               ║
║     5. Review AI recommendations                            ║
║                                                              ║
║  📞 Support: github.com/smartcompute/enterprise             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

EOF
    echo -e "${NC}"

    log_success "Installation completed successfully!"
    log_info "You can now run: smartcompute-gui"
}

# Run main function
main "$@"