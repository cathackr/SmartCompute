#!/bin/bash
# SmartCompute Industrial - Instalación Segura
# Desarrollado por: ggwre04p0@mozmail.com
# LinkedIn: https://www.linkedin.com/in/martín-iribarne-swtf/

set -e  # Salir si cualquier comando falla

echo "🏭 ======== SMARTCOMPUTE INDUSTRIAL - INSTALACIÓN SEGURA ========"
echo "📧 Desarrollado por: ggwre04p0@mozmail.com"
echo "🔗 LinkedIn: https://www.linkedin.com/in/martín-iribarne-swtf/"
echo

# Verificar permisos de administrador
if [[ $EUID -ne 0 ]]; then
   echo "❌ Este script debe ejecutarse como administrador (sudo)"
   echo "   Uso: sudo ./install_secure.sh"
   exit 1
fi

# Verificar sistema operativo
if ! command -v apt-get &> /dev/null; then
    echo "❌ Este instalador requiere Ubuntu/Debian Linux"
    echo "   Para otros sistemas, consulte la documentación"
    exit 1
fi

echo "🔍 ======== VERIFICACIONES PREVIAS ========"

# Verificar recursos del sistema
RAM_GB=$(free -g | awk 'NR==2{print $2}')
if [ $RAM_GB -lt 4 ]; then
    echo "⚠️  ADVERTENCIA: RAM insuficiente ($RAM_GB GB). Recomendado: 8 GB+"
    read -p "¿Continuar de todos modos? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Verificar espacio en disco
DISK_GB=$(df -BG / | awk 'NR==2{gsub(/G/,"",$4); print $4}')
if [ $DISK_GB -lt 10 ]; then
    echo "❌ Espacio insuficiente en disco ($DISK_GB GB). Requerido: 10 GB+"
    exit 1
fi

echo "✅ Recursos del sistema verificados"

echo
echo "🔐 ======== CONFIGURACIÓN DE SEGURIDAD ========"

# Crear usuario del sistema
if ! id "smartcompute" &>/dev/null; then
    echo "👤 Creando usuario del sistema..."
    useradd -r -s /bin/false -d /opt/smartcompute smartcompute
else
    echo "✅ Usuario smartcompute ya existe"
fi

# Crear estructura de directorios
echo "📁 Creando estructura de directorios..."
mkdir -p /opt/smartcompute/{bin,data,logs,config,reports,venv}
mkdir -p /etc/smartcompute
mkdir -p /var/log/smartcompute
mkdir -p /var/backups/smartcompute

echo "🔧 ======== INSTALACIÓN DE DEPENDENCIAS ========"

# Actualizar repositorios
echo "📦 Actualizando repositorios del sistema..."
apt-get update -q

# Instalar dependencias del sistema
echo "📦 Instalando dependencias del sistema..."
apt-get install -y \
    python3 python3-pip python3-venv \
    nodejs npm \
    sqlite3 \
    nginx \
    ufw \
    fail2ban \
    logrotate \
    cron

# Verificar versiones
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)

if [[ $(echo "$PYTHON_VERSION >= 3.8" | bc -l) -eq 0 ]]; then
    echo "❌ Python $PYTHON_VERSION no soportado. Requerido: 3.8+"
    exit 1
fi

if [ $NODE_VERSION -lt 16 ]; then
    echo "❌ Node.js $NODE_VERSION no soportado. Requerido: 16+"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION y Node.js v$NODE_VERSION verificados"

echo
echo "🐍 ======== CONFIGURACIÓN PYTHON ========"

# Crear entorno virtual
echo "📦 Creando entorno virtual Python..."
python3 -m venv /opt/smartcompute/venv

# Activar entorno virtual e instalar paquetes
echo "📦 Instalando paquetes Python..."
source /opt/smartcompute/venv/bin/activate
pip install --upgrade pip

# Instalar dependencias principales (versiones específicas para seguridad)
pip install \
    pillow==10.0.1 \
    opencv-python==4.8.1.78 \
    qrcode==7.4.2 \
    pyotp==2.9.0 \
    pyjwt==2.8.0 \
    cryptography==41.0.7 \
    sqlite3 \
    flask==2.3.3 \
    flask-cors==4.0.0

echo
echo "📦 ======== CONFIGURACIÓN NODE.JS ========"

# Copiar archivos del proyecto
echo "📂 Copiando archivos del proyecto..."
cp *.py /opt/smartcompute/bin/
cp *.js /opt/smartcompute/bin/
cp package.json /opt/smartcompute/bin/

# Instalar dependencias Node.js
cd /opt/smartcompute/bin
npm install --production

echo
echo "🔒 ======== CONFIGURACIÓN DE SEGURIDAD ========"

# Configurar firewall
echo "🔥 Configurando firewall..."
ufw --force enable
ufw default deny incoming
ufw default allow outgoing

# Permitir solo puertos necesarios desde red local
ufw allow from 192.168.0.0/16 to any port 3000 comment 'SmartCompute API'
ufw allow from 192.168.0.0/16 to any port 3001 comment 'SmartCompute WebSocket'
ufw allow from 10.0.0.0/8 to any port 3000 comment 'SmartCompute API'
ufw allow from 10.0.0.0/8 to any port 3001 comment 'SmartCompute WebSocket'

# SSH solo desde red administrativa (ajustar según necesidades)
ufw allow from 192.168.100.0/24 to any port 22 comment 'SSH Admin'

# Configurar fail2ban
echo "🛡️  Configurando fail2ban..."
cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log

[smartcompute]
enabled = true
port = 3000,3001
logpath = /var/log/smartcompute/security.log
maxretry = 5
EOF

systemctl enable fail2ban
systemctl restart fail2ban

# Configurar rotación de logs
echo "📋 Configurando rotación de logs..."
cat > /etc/logrotate.d/smartcompute << EOF
/var/log/smartcompute/*.log {
    daily
    missingok
    rotate 90
    compress
    notifempty
    copytruncate
    create 644 smartcompute smartcompute
    postrotate
        systemctl reload smartcompute
    endscript
}
EOF

echo
echo "⚙️ ======== CONFIGURACIÓN DEL SERVICIO ========"

# Crear servicio systemd
echo "🔧 Configurando servicio systemd..."
cat > /etc/systemd/system/smartcompute.service << EOF
[Unit]
Description=SmartCompute Industrial Service
Documentation=file:///opt/smartcompute/SMARTCOMPUTE_INDUSTRIAL_USER_GUIDE.md
After=network.target

[Service]
Type=simple
User=smartcompute
Group=smartcompute
WorkingDirectory=/opt/smartcompute/bin
Environment=PATH=/opt/smartcompute/venv/bin
ExecStart=/opt/smartcompute/venv/bin/python smartcompute_integrated_workflow.py
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=smartcompute

# Configuración de seguridad
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/smartcompute /var/log/smartcompute

[Install]
WantedBy=multi-user.target
EOF

# Configurar permisos
echo "🔐 Configurando permisos..."
chown -R smartcompute:smartcompute /opt/smartcompute
chown -R smartcompute:smartcompute /var/log/smartcompute
chmod -R 750 /opt/smartcompute
chmod +x /opt/smartcompute/bin/*.py
chmod +x /opt/smartcompute/bin/*.js

# Proteger archivos de configuración
chmod 600 /etc/smartcompute/*
chown root:root /etc/smartcompute/*

# Recargar systemd
systemctl daemon-reload
systemctl enable smartcompute

echo
echo "📄 ======== CREANDO CONFIGURACIÓN INICIAL ========"

# Generar claves seguras únicas
JWT_SECRET=$(openssl rand -hex 32)
ENCRYPTION_KEY=$(openssl rand -hex 32)

cat > /etc/smartcompute/config.ini << EOF
[security]
# ⚠️ CLAVES GENERADAS AUTOMÁTICAMENTE - NO COMPARTIR
jwt_secret = $JWT_SECRET
encryption_key = $ENCRYPTION_KEY
session_timeout_hours = 8
max_failed_attempts = 3

[database]
db_path = /opt/smartcompute/data/smartcompute.db
backup_interval_hours = 24
max_history_days = 90

[network]
api_port = 3000
websocket_port = 3001
max_connections = 100
bind_ip = 0.0.0.0

[logging]
log_level = INFO
log_file = /var/log/smartcompute/smartcompute.log
security_log_file = /var/log/smartcompute/security.log
max_log_size_mb = 100

[ai]
visual_confidence_threshold = 0.85
hrm_confidence_threshold = 0.80
learning_enabled = true
auto_update_models = true
EOF

# Crear configuración de ubicaciones de ejemplo
cat > /etc/smartcompute/authorized_locations.json << EOF
{
  "ejemplo_planta": {
    "name": "Planta de Ejemplo - CAMBIAR COORDENADAS",
    "lat": -34.603700,
    "lng": -58.381600,
    "radius_meters": 100,
    "authorized_operators": ["OP001"],
    "emergency_contact": "+54911234567",
    "notes": "CONFIGURAR CON COORDENADAS REALES ANTES DE USO"
  }
}
EOF

# Crear configuración de operadores de ejemplo
cat > /etc/smartcompute/operators.json << EOF
{
  "operators": {
    "OP001": {
      "name": "Operador de Ejemplo - CAMBIAR",
      "role": "technician",
      "level": 2,
      "phone": "+54911111111",
      "email": "operador@empresa.com",
      "totp_secret": "$(python3 -c 'import pyotp; print(pyotp.random_base32())')",
      "authorized_locations": ["ejemplo_planta"],
      "notes": "CONFIGURAR CON DATOS REALES ANTES DE USO"
    }
  }
}
EOF

echo
echo "📋 ======== CONFIGURACIÓN DE BACKUP ========"

# Crear script de backup
cat > /opt/smartcompute/bin/backup.sh << 'EOF'
#!/bin/bash
# Backup automático de SmartCompute Industrial

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/smartcompute"
BACKUP_FILE="$BACKUP_DIR/smartcompute_backup_$DATE.tar.gz"

# Crear backup
tar -czf "$BACKUP_FILE" \
    /etc/smartcompute/ \
    /opt/smartcompute/data/ \
    /var/log/smartcompute/

# Mantener solo backups de 30 días
find "$BACKUP_DIR" -name "smartcompute_backup_*.tar.gz" -mtime +30 -delete

echo "Backup creado: $BACKUP_FILE"
EOF

chmod +x /opt/smartcompute/bin/backup.sh

# Configurar cron para backup diario
echo "0 2 * * * /opt/smartcompute/bin/backup.sh >> /var/log/smartcompute/backup.log 2>&1" | crontab -u root -

echo
echo "✅ ======== INSTALACIÓN COMPLETADA ========"
echo
echo "🎉 SmartCompute Industrial instalado exitosamente!"
echo
echo "📋 PRÓXIMOS PASOS OBLIGATORIOS:"
echo
echo "1. 🔐 CONFIGURAR SEGURIDAD:"
echo "   sudo nano /etc/smartcompute/operators.json"
echo "   sudo nano /etc/smartcompute/authorized_locations.json"
echo
echo "2. 🚀 INICIAR SERVICIOS:"
echo "   sudo systemctl start smartcompute"
echo "   sudo systemctl status smartcompute"
echo
echo "3. 🌐 VERIFICAR CONEXIÓN:"
echo "   curl -k https://localhost:3000/health"
echo
echo "4. 📱 CONFIGURAR 2FA:"
echo "   - Instalar Google Authenticator en dispositivos móviles"
echo "   - Escanear códigos QR generados para cada operador"
echo
echo "5. 📍 VERIFICAR GPS:"
echo "   - Probar desde ubicaciones autorizadas"
echo "   - Ajustar radios según precisión GPS local"
echo
echo "📖 DOCUMENTACIÓN COMPLETA:"
echo "   /opt/smartcompute/SMARTCOMPUTE_INDUSTRIAL_USER_GUIDE.md"
echo
echo "🔒 ADVERTENCIAS DE SEGURIDAD:"
echo "   ⚠️  Cambiar operadores de ejemplo antes de uso"
echo "   ⚠️  Configurar coordenadas GPS reales"
echo "   ⚠️  Verificar configuración de firewall"
echo "   ⚠️  Configurar backup externo"
echo
echo "📞 SOPORTE:"
echo "   📧 Email: ggwre04p0@mozmail.com"
echo "   🔗 LinkedIn: https://www.linkedin.com/in/martín-iribarne-swtf/"
echo
echo "🎯 ¡Sistema listo para configuración de producción!"