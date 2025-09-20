#!/bin/bash
# SmartCompute Enterprise - Linux Installer
# ==========================================
# Instalador completo con Python embebido, validación de licencia y cifrado

set -euo pipefail

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables de configuración
PRODUCT_NAME="SmartCompute Enterprise"
PRODUCT_VERSION="1.0.0"
DOWNLOAD_SERVER="https://secure.smartcompute.enterprise"
LICENSE_SERVER="https://license.smartcompute.enterprise"
DEFAULT_INSTALL_DIR="/opt/smartcompute-enterprise"
PYTHON_VERSION="3.11.9"
TEMP_DIR="/tmp/smartcompute_install"
SERVICE_NAME="smartcompute-enterprise"

# Función para mostrar banner
show_banner() {
    echo -e "${BLUE}"
    echo "  ========================================================"
    echo "   SmartCompute Enterprise - Security Analysis Platform"
    echo "  ========================================================"
    echo "   Version: 1.0.0 | Build: 2025.09.17"
    echo "   Copyright (c) 2025 SmartCompute Security Solutions"
    echo "  ========================================================"
    echo -e "${NC}"
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

    log_step "1/10" "Verificando sistema..."
    check_root
    detect_distro
    install_system_deps

    log_step "2/10" "Verificando conectividad..."
    check_connectivity

    log_step "3/10" "Validación de licencia..."
    request_credentials
    if ! validate_license; then
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

    log_step "8/10" "Instalando SmartCompute Enterprise..."
    decrypt_smartcompute
    create_license_config

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
    echo "   SmartCompute Enterprise se ha instalado correctamente."
    echo
    echo "   Ubicación: $INSTALL_DIR"
    echo "   Licencia válida hasta: $LICENSE_EXPIRY"
    echo
    echo "   Comandos disponibles:"
    echo "     smartcompute        - CLI de análisis"
    echo "     smartcompute-tray   - Interfaz gráfica"
    echo "     systemctl start smartcompute-enterprise - Iniciar servicio"
    echo

    read -p "¿Desea iniciar SmartCompute Enterprise ahora? (S/N): " START_NOW
    if [[ "$START_NOW" =~ ^[Ss]$ ]]; then
        systemctl start smartcompute-enterprise
        log_info "SmartCompute Enterprise iniciado."
        log_info "Acceso web disponible en: http://localhost:8080"
    fi

    echo
    echo "Instalación finalizada. Presione Enter para continuar..."
    read
}

# Manejo de señales para cleanup
trap cleanup EXIT

# Ejecutar instalación principal
main "$@"