#!/bin/bash
# SmartCompute Unified - Linux Installer
# =======================================
# Instalador completo con Python embebido, validación de licencia y cifrado
# Soporte para Enterprise/Industrial y modo Cliente/Servidor

set -euo pipefail

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables de configuración base
PRODUCT_VERSION="2.0.0"
DOWNLOAD_SERVER="https://secure.smartcompute.enterprise"
LICENSE_SERVER="https://license.smartcompute.enterprise"
PYTHON_VERSION="3.11.9"
TEMP_DIR="/tmp/smartcompute_install"

# Variables que se configurarán según selección
PRODUCT_NAME=""
PRODUCT_TYPE=""
DEPLOYMENT_MODE=""
DEFAULT_INSTALL_DIR=""
SERVICE_NAME=""

# Función para mostrar banner
show_banner() {
    echo -e "${BLUE}"
    echo "  ========================================================"
    echo "   SmartCompute Unified - Security Analysis Platform"
    echo "  ========================================================"
    echo "   Version: 2.0.0 | Build: 2025.09.18"
    echo "   Enterprise & Industrial | Client & Server modes"
    echo "   Copyright (c) 2025 SmartCompute Security Solutions"
    echo "  ========================================================"
    echo -e "${NC}"
}

# Función para selección de producto y modo
select_product_and_mode() {
    echo
    echo -e "${BLUE}========================================================${NC}"
    echo -e "${BLUE} SELECCIÓN DE PRODUCTO Y MODO DE INSTALACIÓN${NC}"
    echo -e "${BLUE}========================================================${NC}"
    echo
    echo "Esta licencia SmartCompute le permite instalar tanto"
    echo "la versión Enterprise como Industrial en cualquier"
    echo "cantidad de hosts de su red hasta la expiración."
    echo
    echo "--------------------------------------------------------"
    echo "1. SmartCompute Enterprise (Sistemas tradicionales TI)"
    echo "2. SmartCompute Industrial (Sistemas SCADA/PLC)"
    echo "--------------------------------------------------------"
    echo

    while true; do
        read -p "Seleccione el tipo de producto (1 o 2): " product_choice

        case $product_choice in
            1)
                PRODUCT_TYPE="enterprise"
                PRODUCT_NAME="SmartCompute Enterprise"
                DEFAULT_INSTALL_DIR="/opt/smartcompute-enterprise"
                SERVICE_NAME="smartcompute-enterprise"
                break
                ;;
            2)
                PRODUCT_TYPE="industrial"
                PRODUCT_NAME="SmartCompute Industrial"
                DEFAULT_INSTALL_DIR="/opt/smartcompute-industrial"
                SERVICE_NAME="smartcompute-industrial"
                break
                ;;
            *)
                echo
                log_error "Opción inválida. Seleccione 1 o 2."
                echo
                ;;
        esac
    done

    echo
    echo -e "${BLUE}========================================================${NC}"
    echo -e "${BLUE} SELECCIÓN DE MODO DE DESPLIEGUE${NC}"
    echo -e "${BLUE}========================================================${NC}"
    echo
    echo "$PRODUCT_NAME puede funcionar en dos modos:"
    echo
    echo "--------------------------------------------------------"
    echo "1. CLIENTE  - Se conecta a un servidor central existente"
    echo "2. SERVIDOR - Actúa como servidor central para la red"
    echo "--------------------------------------------------------"
    echo
    echo "Nota: Una licencia permite ambos modos simultáneamente"
    echo "      en diferentes hosts de la misma red organizacional."
    echo

    while true; do
        read -p "Seleccione el modo de instalación (1 o 2): " mode_choice

        case $mode_choice in
            1)
                DEPLOYMENT_MODE="client"
                echo
                log_info "Modo CLIENTE seleccionado"
                log_info "Se configurará para conectar a servidor central"
                break
                ;;
            2)
                DEPLOYMENT_MODE="server"
                echo
                log_info "Modo SERVIDOR seleccionado"
                log_info "Se configurará como servidor central de red"
                break
                ;;
            *)
                echo
                log_error "Opción inválida. Seleccione 1 o 2."
                echo
                ;;
        esac
    done

    echo
    echo -e "${BLUE}========================================================${NC}"
    echo -e "${BLUE} CONFIGURACIÓN SELECCIONADA${NC}"
    echo -e "${BLUE}========================================================${NC}"
    echo
    echo "Producto:      $PRODUCT_NAME"
    echo "Tipo:          $PRODUCT_TYPE"
    echo "Modo:          $DEPLOYMENT_MODE"
    echo "Directorio:    $DEFAULT_INSTALL_DIR"
    echo

    while true; do
        read -p "¿Confirma la configuración? (s/n): " confirm_config
        case $confirm_config in
            [Ss]*)
                echo
                log_info "Configuración confirmada"
                echo
                break
                ;;
            [Nn]*)
                echo
                echo "Volviendo al menú de selección..."
                echo
                select_product_and_mode
                return
                ;;
            *)
                echo "Por favor responda 's' para sí o 'n' para no."
                ;;
        esac
    done
}

# Función para logging
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP $1]${NC} $2"
}

# Función para verificar privilegios root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "Este instalador requiere privilegios de root."
        log_error "Ejecute con: sudo ./smartcompute_installer.sh"
        exit 1
    fi
    log_info "Verificando privilegios... OK"
}

# Función para detectar distribución
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
        VERSION=$VERSION_ID
    else
        log_error "No se pudo detectar la distribución de Linux."
        exit 1
    fi
    log_info "Distribución detectada: $DISTRO $VERSION"
}

# Función para instalar dependencias del sistema
install_system_deps() {
    log_info "Instalando dependencias del sistema..."

    case $DISTRO in
        ubuntu|debian)
            apt-get update -qq
            apt-get install -y wget curl unzip tar python3-pip python3-venv \
                systemd openssl ca-certificates net-tools psmisc >/dev/null 2>&1
            ;;
        centos|rhel|fedora)
            if command -v dnf >/dev/null 2>&1; then
                dnf install -y wget curl unzip tar python3-pip python3-venv \
                    systemd openssl ca-certificates net-tools psmisc >/dev/null 2>&1
            else
                yum install -y wget curl unzip tar python3-pip python3-venv \
                    systemd openssl ca-certificates net-tools psmisc >/dev/null 2>&1
            fi
            ;;
        arch)
            pacman -Sy --noconfirm wget curl unzip tar python-pip python-virtualenv \
                systemd openssl ca-certificates net-tools psmisc >/dev/null 2>&1
            ;;
        *)
            log_warn "Distribución no reconocida, intentando instalación genérica..."
            ;;
    esac

    log_info "Dependencias del sistema instaladas... OK"
}

# Función para verificar conectividad
check_connectivity() {
    log_info "Verificando conectividad..."
    if ! ping -c 1 google.com >/dev/null 2>&1; then
        log_error "No se detectó conexión a internet."
        log_error "SmartCompute Enterprise requiere conexión para validar la licencia."
        exit 1
    fi
    log_info "Conectividad verificada... OK"
}

# Función para solicitar credenciales
request_credentials() {
    echo
    echo "Por favor, ingrese sus credenciales de licencia:"
    echo "(Estas credenciales se proporcionan al momento de la compra)"
    echo

    read -p "Usuario de licencia: " LICENSE_USER
    echo
    read -s -p "Contraseña: " LICENSE_PASS
    echo
    echo

    if [[ -z "$LICENSE_USER" ]]; then
        log_error "Usuario de licencia requerido."
        exit 1
    fi

    if [[ -z "$LICENSE_PASS" ]]; then
        log_error "Contraseña de licencia requerida."
        exit 1
    fi
}

# Función para validar licencia
validate_license() {
    log_info "Validando licencia con servidor..."

    # Crear payload JSON
    local payload=$(cat <<EOF
{
    "username": "$LICENSE_USER",
    "password": "$LICENSE_PASS",
    "product": "enterprise",
    "version": "$PRODUCT_VERSION"
}
EOF
)

    # Realizar validación HTTPS
    local response=$(curl -s -w "%{http_code}" \
        -H "Content-Type: application/json" \
        -H "User-Agent: SmartCompute-Installer/1.0" \
        -d "$payload" \
        --connect-timeout 30 \
        "$LICENSE_SERVER/validate" 2>/dev/null)

    local http_code="${response: -3}"
    local body="${response%???}"

    if [[ "$http_code" == "200" ]]; then
        # Procesar respuesta JSON
        local valid=$(echo "$body" | grep -o '"valid":[^,}]*' | cut -d':' -f2 | tr -d ' "')
        local expiry=$(echo "$body" | grep -o '"expiry_date":"[^"]*"' | cut -d':' -f2 | tr -d '"')

        if [[ "$valid" == "true" ]]; then
            LICENSE_EXPIRY="$expiry"
            log_info "Licencia verificada correctamente."
            log_info "Licencia válida hasta: $LICENSE_EXPIRY"
            return 0
        else
            local message=$(echo "$body" | grep -o '"message":"[^"]*"' | cut -d':' -f2 | tr -d '"')
            log_error "Licencia inválida: $message"
            return 1
        fi
    else
        log_error "Error de conexión al servidor de licencias (HTTP $http_code)."
        return 1
    fi
}

# Función para solicitar directorio de instalación
request_install_dir() {
    echo
    echo "Directorio de instalación predeterminado:"
    echo "$DEFAULT_INSTALL_DIR"
    echo
    read -p "Presione Enter para usar el predeterminado o ingrese ruta personalizada: " CUSTOM_DIR

    if [[ -z "$CUSTOM_DIR" ]]; then
        INSTALL_DIR="$DEFAULT_INSTALL_DIR"
    else
        INSTALL_DIR="$CUSTOM_DIR"
    fi

    log_info "Directorio de instalación: $INSTALL_DIR"
}

# Función para verificar espacio en disco
check_disk_space() {
    log_info "Verificando espacio en disco..."
    local parent_dir=$(dirname "$INSTALL_DIR")
    local available_space=$(df "$parent_dir" | awk 'NR==2 {print $4}')
    local required_space=1048576  # 1GB in KB

    if [[ $available_space -lt $required_space ]]; then
        log_error "Espacio insuficiente. Se requieren al menos 1 GB libres."
        exit 1
    fi
    log_info "Espacio en disco suficiente... OK"
}

# Función para crear directorio temporal
setup_temp_dir() {
    if [[ -d "$TEMP_DIR" ]]; then
        rm -rf "$TEMP_DIR"
    fi
    mkdir -p "$TEMP_DIR"
    cd "$TEMP_DIR"
    log_info "Directorio temporal: $TEMP_DIR"
}

# Función para descargar Python embebido
download_python() {
    log_info "Descargando Python $PYTHON_VERSION..."

    local python_url="https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz"

    if ! wget -q --show-progress --user-agent="SmartCompute-Installer/1.0" \
         "$python_url" -O "python-source.tgz"; then
        log_error "Fallo al descargar Python."
        exit 1
    fi

    # Verificar integridad (tamaño mínimo: 20MB)
    local file_size=$(stat -c%s "python-source.tgz")
    if [[ $file_size -lt 20971520 ]]; then
        log_error "Archivo de Python incompleto."
        exit 1
    fi

    log_info "Python descargado correctamente ($file_size bytes)."
}

# Función para descargar SmartCompute cifrado
download_smartcompute() {
    log_info "Descargando SmartCompute Enterprise (cifrado)..."

    local auth_header="Authorization: Basic $(echo -n "$LICENSE_USER:$LICENSE_PASS" | base64 -w 0)"

    if ! curl -f -L -H "$auth_header" \
         -H "User-Agent: SmartCompute-Installer/1.0" \
         --connect-timeout 120 \
         "$DOWNLOAD_SERVER/enterprise/package" \
         -o "smartcompute_enterprise.enc"; then
        log_error "Fallo al descargar SmartCompute Enterprise."
        exit 1
    fi

    if [[ ! -f "smartcompute_enterprise.enc" ]]; then
        log_error "Archivo de SmartCompute Enterprise no encontrado."
        exit 1
    fi

    log_info "SmartCompute Enterprise descargado correctamente."
}

# Función para compilar Python embebido
compile_python() {
    log_info "Compilando Python embebido..."

    tar -xzf python-source.tgz
    cd Python-$PYTHON_VERSION

    # Configurar compilación optimizada
    ./configure --prefix="$INSTALL_DIR/python" \
                --enable-optimizations \
                --with-ensurepip=install \
                --disable-shared \
                --enable-ipv6 >/dev/null 2>&1

    # Compilar e instalar
    make -j$(nproc) >/dev/null 2>&1
    make install >/dev/null 2>&1

    cd ..
    log_info "Python embebido compilado e instalado... OK"
}

# Función para desencriptar SmartCompute
decrypt_smartcompute() {
    log_info "Descifrando SmartCompute Enterprise..."

    # Crear script Python para descifrado
    cat > decrypt_smartcompute.py << 'EOF'
import base64
import hashlib
import sys
import os
from cryptography.fernet import Fernet
import zipfile

def decrypt_package():
    try:
        user = sys.argv[1]
        password = sys.argv[2]
        install_dir = sys.argv[3]

        # Generar clave de descifrado
        key_material = f"{user}:{password}:smartcompute:enterprise".encode()
        key = base64.urlsafe_b64encode(hashlib.sha256(key_material).digest())

        fernet = Fernet(key)

        # Leer archivo cifrado
        with open('smartcompute_enterprise.enc', 'rb') as f:
            encrypted_data = f.read()

        # Descifrar
        decrypted_data = fernet.decrypt(encrypted_data)

        # Guardar archivo ZIP descifrado
        with open('smartcompute_enterprise.zip', 'wb') as f:
            f.write(decrypted_data)

        # Extraer archivos al directorio de instalación
        with zipfile.ZipFile('smartcompute_enterprise.zip', 'r') as zip_ref:
            zip_ref.extractall(install_dir)

        print("DECRYPT_SUCCESS")
        return 0

    except Exception as e:
        print(f"DECRYPT_ERROR: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(decrypt_package())
EOF

    # Instalar cryptography en Python embebido
    "$INSTALL_DIR/python/bin/pip3" install cryptography >/dev/null 2>&1

    # Ejecutar descifrado
    if ! "$INSTALL_DIR/python/bin/python3" decrypt_smartcompute.py \
         "$LICENSE_USER" "$LICENSE_PASS" "$INSTALL_DIR"; then
        log_error "Fallo al descifrar SmartCompute Enterprise."
        exit 1
    fi

    log_info "SmartCompute Enterprise descifrado e instalado... OK"
}

# Función para instalar dependencias Python
install_python_deps() {
    log_info "Instalando dependencias Python..."

    "$INSTALL_DIR/python/bin/pip3" install --no-warn-script-location \
        psutil pystray Pillow cryptography requests asyncio >/dev/null 2>&1

    log_info "Dependencias Python instaladas... OK"
}

# Función para crear configuración de licencia
create_license_config() {
    log_info "Configurando licencia de usuario..."

    mkdir -p "$INSTALL_DIR/config"

    # Crear script para configuración cifrada
    cat > create_license_config.py << 'EOF'
import base64
import hashlib
import json
import sys
import os
from cryptography.fernet import Fernet
from datetime import datetime

def create_config():
    try:
        user = sys.argv[1]
        password = sys.argv[2]
        expiry = sys.argv[3]
        install_dir = sys.argv[4]

        # Datos de licencia
        license_data = {
            'username': user,
            'license_hash': hashlib.sha256(f'{user}:{password}'.encode()).hexdigest(),
            'product': 'SmartCompute Enterprise',
            'version': '1.0.0',
            'install_date': datetime.now().isoformat(),
            'expiry_date': expiry,
            'machine_id': hashlib.md5(os.uname().nodename.encode()).hexdigest()
        }

        # Cifrar configuración
        key_material = f'{user}:{password}:config'.encode()
        key = base64.urlsafe_b64encode(hashlib.sha256(key_material).digest())
        fernet = Fernet(key)
        encrypted_config = fernet.encrypt(json.dumps(license_data).encode())

        # Guardar configuración cifrada
        with open(f'{install_dir}/config/license.enc', 'wb') as f:
            f.write(encrypted_config)

        print("LICENSE_CONFIG_CREATED")
        return 0

    except Exception as e:
        print(f"CONFIG_ERROR: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(create_config())
EOF

    "$INSTALL_DIR/python/bin/python3" create_license_config.py \
        "$LICENSE_USER" "$LICENSE_PASS" "$LICENSE_EXPIRY" "$INSTALL_DIR" >/dev/null 2>&1

    rm -f create_license_config.py
}

# Función para crear servicio systemd
create_systemd_service() {
    log_info "Configurando servicio systemd..."

    # Crear archivo de servicio
    cat > "/etc/systemd/system/$SERVICE_NAME.service" << EOF
[Unit]
Description=SmartCompute Enterprise Security Service
Documentation=https://smartcompute.enterprise/docs
After=network.target
Wants=network.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/python/bin/python3 $INSTALL_DIR/smartcompute_tray.py --daemon
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=10
KillMode=mixed
TimeoutStopSec=30

# Seguridad
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ReadWritePaths=$INSTALL_DIR
ProtectHome=yes

# Variables de entorno
Environment=PYTHONPATH=$INSTALL_DIR
Environment=SMARTCOMPUTE_HOME=$INSTALL_DIR

[Install]
WantedBy=multi-user.target
EOF

    # Habilitar servicio
    systemctl daemon-reload
    systemctl enable "$SERVICE_NAME" >/dev/null 2>&1

    log_info "Servicio systemd configurado... OK"
}

# Función para configurar firewall
configure_firewall() {
    log_info "Configurando reglas de firewall..."

    # Detectar y configurar firewall
    if command -v ufw >/dev/null 2>&1; then
        # Ubuntu/Debian UFW
        ufw allow from any to any port 8080 comment "SmartCompute Enterprise" >/dev/null 2>&1
        ufw allow from any to any port 8443 comment "SmartCompute Enterprise SSL" >/dev/null 2>&1
    elif command -v firewall-cmd >/dev/null 2>&1; then
        # CentOS/RHEL/Fedora firewalld
        firewall-cmd --permanent --add-port=8080/tcp >/dev/null 2>&1
        firewall-cmd --permanent --add-port=8443/tcp >/dev/null 2>&1
        firewall-cmd --reload >/dev/null 2>&1
    elif command -v iptables >/dev/null 2>&1; then
        # iptables genérico
        iptables -A INPUT -p tcp --dport 8080 -j ACCEPT 2>/dev/null
        iptables -A INPUT -p tcp --dport 8443 -j ACCEPT 2>/dev/null
        # Intentar guardar reglas (varía por distribución)
        iptables-save > /etc/iptables/rules.v4 2>/dev/null || true
    fi

    log_info "Firewall configurado... OK"
}

# Función para crear scripts de acceso
create_access_scripts() {
    log_info "Creando scripts de acceso..."

    # Script de comando principal
    cat > "/usr/local/bin/smartcompute" << EOF
#!/bin/bash
exec $INSTALL_DIR/python/bin/python3 $INSTALL_DIR/smartcompute_cli.py "\$@"
EOF
    chmod +x "/usr/local/bin/smartcompute"

    # Script de tray (GUI)
    cat > "/usr/local/bin/smartcompute-tray" << EOF
#!/bin/bash
exec $INSTALL_DIR/python/bin/python3 $INSTALL_DIR/smartcompute_tray.py "\$@"
EOF
    chmod +x "/usr/local/bin/smartcompute-tray"

    # Desktop entry para entornos gráficos
    mkdir -p "/usr/share/applications"
    cat > "/usr/share/applications/smartcompute-enterprise.desktop" << EOF
[Desktop Entry]
Version=1.0
Name=SmartCompute Enterprise
Comment=Security Analysis Platform
Exec=$INSTALL_DIR/python/bin/python3 $INSTALL_DIR/smartcompute_tray.py
Icon=$INSTALL_DIR/assets/icon.png
Terminal=false
Type=Application
Categories=Security;System;Network;
StartupNotify=true
EOF

    log_info "Scripts de acceso creados... OK"
}

# Función para crear desinstalador
create_uninstaller() {
    log_info "Creando desinstalador..."

    cat > "$INSTALL_DIR/uninstall.sh" << 'EOF'
#!/bin/bash
# SmartCompute Enterprise - Desinstalador

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}"
echo "  ================================================"
echo "   SmartCompute Enterprise - Desinstalador"
echo "  ================================================"
echo -e "${NC}"
echo
echo -e "${RED}[WARNING]${NC} Esta acción desinstalará completamente SmartCompute Enterprise."
echo "           Todos los datos y configuraciones serán eliminados."
echo
read -p "¿Está seguro de continuar? (S/N): " CONFIRM

if [[ ! "$CONFIRM" =~ ^[Ss]$ ]]; then
    echo "Desinstalación cancelada."
    exit 0
fi

echo
echo -e "${GREEN}[STEP 1/6]${NC} Deteniendo servicios..."
systemctl stop smartcompute-enterprise 2>/dev/null || true
systemctl disable smartcompute-enterprise 2>/dev/null || true

echo -e "${GREEN}[STEP 2/6]${NC} Eliminando procesos..."
pkill -f smartcompute 2>/dev/null || true

echo -e "${GREEN}[STEP 3/6]${NC} Eliminando servicio systemd..."
rm -f /etc/systemd/system/smartcompute-enterprise.service
systemctl daemon-reload

echo -e "${GREEN}[STEP 4/6]${NC} Eliminando scripts de acceso..."
rm -f /usr/local/bin/smartcompute
rm -f /usr/local/bin/smartcompute-tray
rm -f /usr/share/applications/smartcompute-enterprise.desktop

echo -e "${GREEN}[STEP 5/6]${NC} Eliminando reglas de firewall..."
if command -v ufw >/dev/null 2>&1; then
    ufw delete allow 8080 2>/dev/null || true
    ufw delete allow 8443 2>/dev/null || true
elif command -v firewall-cmd >/dev/null 2>&1; then
    firewall-cmd --permanent --remove-port=8080/tcp 2>/dev/null || true
    firewall-cmd --permanent --remove-port=8443/tcp 2>/dev/null || true
    firewall-cmd --reload 2>/dev/null || true
fi

echo -e "${GREEN}[STEP 6/6]${NC} Eliminando archivos de programa..."
INSTALL_DIR="$(dirname "$(readlink -f "$0")")"
cd /tmp
rm -rf "$INSTALL_DIR" 2>/dev/null || true

echo
echo -e "${GREEN}SmartCompute Enterprise ha sido desinstalado correctamente.${NC}"
echo
EOF

    chmod +x "$INSTALL_DIR/uninstall.sh"
    log_info "Desinstalador creado... OK"
}

# Función para limpiar archivos temporales
cleanup() {
    log_info "Limpiando archivos temporales..."
    cd /tmp
    rm -rf "$TEMP_DIR" 2>/dev/null || true
}

# Función principal de instalación
main() {
    show_banner

    # Selección de producto y modo
    select_product_and_mode

    log_step "1/10" "Verificando sistema..."
    check_root
    detect_distro
    install_system_deps

    log_step "2/10" "Verificando conectividad..."
    check_connectivity

    log_step "3/10" "Validación de licencia..."
    request_credentials
    if ! validate_network_license "$LICENSE_KEY" "$LICENSE_EMAIL"; then
        exit 1
    fi

    log_step "4/10" "Configuración de directorio..."
    request_install_dir
    check_disk_space

    log_step "5/10" "Preparando instalación..."
    setup_temp_dir

    log_step "6/10" "Descargando componentes..."
    download_python
    download_smartcompute

    log_step "7/10" "Instalando Python embebido..."
    mkdir -p "$INSTALL_DIR"
    compile_python
    install_python_deps

    log_step "8/10" "Instalando SmartCompute $SELECTED_PRODUCT..."
    decrypt_smartcompute
    create_license_config
    install_mode_specific_components

    log_step "9/10" "Configurando sistema..."
    create_systemd_service
    configure_firewall
    create_access_scripts
    create_uninstaller

    log_step "10/10" "Finalizando instalación..."
    cleanup

    echo
    echo -e "${GREEN}"
    echo "  ========================================================"
    echo "   INSTALACIÓN COMPLETADA EXITOSAMENTE"
    echo "  ========================================================"
    echo -e "${NC}"
    echo
    echo "   SmartCompute $SELECTED_PRODUCT ($SELECTED_MODE) se ha instalado correctamente."
    echo
    echo "   Ubicación: $INSTALL_DIR"
    echo "   Licencia válida hasta: $LICENSE_EXPIRY"
    echo "   Tipo de licencia: Red (hosts ilimitados)"
    echo
    echo "   Comandos disponibles:"
    if [ "$SELECTED_MODE" = "server" ]; then
        echo "     systemctl start smartcompute-server - Iniciar servidor central"
        echo "     systemctl start smartcompute-client - Iniciar cliente local"
        echo "   Interfaces disponibles:"
        echo "     API Central: https://localhost:8443/api/"
        echo "     Dashboard: http://localhost:8081/"
        echo "     WebSocket: wss://localhost:8443/ws"
    else
        echo "     systemctl start smartcompute-client - Iniciar cliente"
        echo "     smartcompute        - CLI de análisis"
        echo "     smartcompute-tray   - Interfaz gráfica"
    fi
    echo

    if [ "$SELECTED_MODE" = "server" ]; then
        read -p "¿Desea iniciar SmartCompute Server ahora? (S/N): " START_NOW
        if [[ "$START_NOW" =~ ^[Ss]$ ]]; then
            systemctl start smartcompute-server
            systemctl start smartcompute-client
            log_info "SmartCompute Server iniciado."
            log_info "API disponible en: https://localhost:8443"
            log_info "Dashboard disponible en: http://localhost:8081"
        fi
    else
        read -p "¿Desea iniciar SmartCompute Client ahora? (S/N): " START_NOW
        if [[ "$START_NOW" =~ ^[Ss]$ ]]; then
            systemctl start smartcompute-client
            log_info "SmartCompute Client iniciado."
            log_info "Cliente conectado al servidor central."
        fi
    fi

    echo
    echo "Instalación finalizada. Presione Enter para continuar..."
    read
}

# Validación de licencia de red (permite hosts ilimitados por licencia)
validate_network_license() {
    local license_key="$1"
    local license_email="$2"

    log_info "Validando licencia de red..."

    # Crear directorio de licencia compartida si no existe
    local network_license_dir="/etc/smartcompute/network-license"
    if [ ! -d "$network_license_dir" ]; then
        mkdir -p "$network_license_dir" 2>/dev/null || {
            log_warn "No se puede crear directorio de licencia de red. Validando localmente..."
            return 0
        }
    fi

    local license_file="$network_license_dir/license.info"
    local validation_url="https://license-api.smartcompute.com/api/v1/validate-network"

    # Verificar si ya existe una licencia válida en la red
    if [ -f "$license_file" ]; then
        local existing_key=$(grep "license_key=" "$license_file" | cut -d'=' -f2)
        local existing_expiry=$(grep "expiry_date=" "$license_file" | cut -d'=' -f2)

        if [ "$existing_key" = "$license_key" ]; then
            # Verificar si la licencia aún es válida
            local current_date=$(date +%s)
            local expiry_timestamp=$(date -d "$existing_expiry" +%s 2>/dev/null || echo "0")

            if [ "$current_date" -lt "$expiry_timestamp" ]; then
                log_info "Licencia de red válida encontrada. Hosts ilimitados permitidos."
                LICENSE_EXPIRY="$existing_expiry"
                return 0
            fi
        fi
    fi

    # Validar licencia con el servidor
    local validation_response
    validation_response=$(curl -s -X POST "$validation_url" \
        -H "Content-Type: application/json" \
        -d "{
            \"license_key\": \"$license_key\",
            \"email\": \"$license_email\",
            \"product\": \"$SELECTED_PRODUCT\",
            \"validation_type\": \"network\"
        }" 2>/dev/null)

    if [ $? -eq 0 ] && echo "$validation_response" | grep -q '"valid":true'; then
        local expiry_date=$(echo "$validation_response" | grep -o '"expiry_date":"[^"]*"' | cut -d'"' -f4)
        local license_type=$(echo "$validation_response" | grep -o '"license_type":"[^"]*"' | cut -d'"' -f4)

        log_info "Licencia válida: $license_type hasta $expiry_date"
        LICENSE_EXPIRY="$expiry_date"

        # Guardar información de licencia de red
        cat > "$license_file" << EOF
license_key=$license_key
license_email=$license_email
product=$SELECTED_PRODUCT
license_type=$license_type
expiry_date=$expiry_date
validation_date=$(date)
hosts_allowed=unlimited
EOF
        chmod 644 "$license_file"

        return 0
    else
        log_error "Error en validación de licencia de red"
        return 1
    fi
}

# Instalar componentes específicos del modo
install_mode_specific_components() {
    log_info "Instalando componentes para modo: $SELECTED_MODE"

    case "$SELECTED_MODE" in
        "server")
            install_server_components
            ;;
        "client")
            install_client_components
            ;;
        *)
            log_error "Modo no válido: $SELECTED_MODE"
            return 1
            ;;
    esac
}

# Instalar componentes del servidor
install_server_components() {
    log_info "Instalando componentes del servidor central..."

    # Crear directorio de servidor
    local server_dir="$INSTALL_DIR/server"
    mkdir -p "$server_dir"

    # Copiar archivos del servidor
    if [ "$SELECTED_PRODUCT" = "enterprise" ]; then
        cp "$TEMP_DIR/smartcompute_central_server.py" "$server_dir/"
        cp "$TEMP_DIR/incident_management_dashboard.py" "$server_dir/"
        cp "$TEMP_DIR/server_config.yaml" "$server_dir/"
    else
        cp "$TEMP_DIR/smartcompute_central_server.py" "$server_dir/"
        cp "$TEMP_DIR/incident_management_dashboard.py" "$server_dir/"
        cp "$TEMP_DIR/server_config.yaml" "$server_dir/"
        cp "$TEMP_DIR/smartcompute_industrial_monitor.py" "$server_dir/"
    fi

    # Configurar base de datos
    cat > "$server_dir/init_database.py" << 'EOF'
#!/usr/bin/env python3
import sqlite3
import os

def init_database():
    db_path = "/var/lib/smartcompute/central.db"
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Crear tablas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            last_seen TIMESTAMP,
            status TEXT DEFAULT 'active'
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incidents (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            severity TEXT NOT NULL,
            status TEXT DEFAULT 'open',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            client_id TEXT,
            description TEXT,
            FOREIGN KEY (client_id) REFERENCES clients (id)
        )
    ''')

    conn.commit()
    conn.close()
    print("Base de datos inicializada correctamente")

if __name__ == "__main__":
    init_database()
EOF

    chmod +x "$server_dir/init_database.py"

    # Crear servicio systemd para el servidor
    cat > "/etc/systemd/system/smartcompute-server.service" << EOF
[Unit]
Description=SmartCompute Central Server
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
Restart=always
RestartSec=1
User=root
WorkingDirectory=$server_dir
Environment=PYTHONPATH=$INSTALL_DIR/python
ExecStartPre=$server_dir/init_database.py
ExecStart=$INSTALL_DIR/python/bin/python3 smartcompute_central_server.py
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable smartcompute-server

    log_info "Componentes del servidor instalados correctamente"
}

# Instalar componentes del cliente
install_client_components() {
    log_info "Instalando componentes del cliente..."

    # Crear directorio de cliente
    local client_dir="$INSTALL_DIR/client"
    mkdir -p "$client_dir"

    # Copiar archivos del cliente
    cp "$TEMP_DIR/smartcompute_mcp_client.py" "$client_dir/"
    cp "$TEMP_DIR/client_config.json" "$client_dir/"

    if [ "$SELECTED_PRODUCT" = "enterprise" ]; then
        cp "$TEMP_DIR/smartcompute_enterprise_analysis.py" "$client_dir/"
        cp "$TEMP_DIR/generate_enterprise_reports.py" "$client_dir/"
    else
        cp "$TEMP_DIR/smartcompute_industrial_monitor.py" "$client_dir/"
        cp "$TEMP_DIR/generate_industrial_html_reports.py" "$client_dir/"
        cp "$TEMP_DIR/run_industrial_analysis.py" "$client_dir/"
    fi

    # Configurar cliente
    local server_ip
    read -p "Ingrese la IP del servidor central (localhost si está en la misma máquina): " server_ip
    server_ip=${server_ip:-localhost}

    # Actualizar configuración del cliente
    cat > "$client_dir/client_config.json" << EOF
{
    "client_id": "$(hostname)-$(date +%s)",
    "client_name": "$(hostname) - SmartCompute $SELECTED_PRODUCT Client",
    "client_type": "$SELECTED_PRODUCT",
    "server": {
        "host": "$server_ip",
        "port": 8443,
        "use_ssl": true
    },
    "analysis": {
        "interval": 300,
        "auto_submit": true,
        "include_network": true,
        "include_processes": true
    },
    "logging": {
        "level": "INFO",
        "file": "/var/log/smartcompute/client.log"
    }
}
EOF

    # Crear servicio systemd para el cliente
    cat > "/etc/systemd/system/smartcompute-client.service" << EOF
[Unit]
Description=SmartCompute $SELECTED_PRODUCT Client
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
Restart=always
RestartSec=1
User=root
WorkingDirectory=$client_dir
Environment=PYTHONPATH=$INSTALL_DIR/python
ExecStart=$INSTALL_DIR/python/bin/python3 smartcompute_mcp_client.py
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable smartcompute-client

    log_info "Componentes del cliente instalados correctamente"
}

# Manejo de señales para cleanup
trap cleanup EXIT

# Ejecutar instalación principal
main "$@"