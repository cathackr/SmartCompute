#!/bin/bash
# SmartCompute Secure Payment Server Deployment Script
# Despliega servidor de pagos con máxima seguridad para producción

set -euo pipefail

echo "🔒 SmartCompute Secure Payment Server Deployment v2.0.0"
echo "=============================================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función de logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Verificar si se ejecuta como root
if [[ $EUID -eq 0 ]]; then
   error "Este script no debe ejecutarse como root por seguridad"
fi

# Verificar sistema operativo
if ! command -v systemctl &> /dev/null; then
    error "Este script requiere systemd (Ubuntu 18+, CentOS 7+, etc.)"
fi

log "🔍 Verificando requisitos del sistema..."

# Verificar Python 3.8+
if ! command -v python3 &> /dev/null; then
    error "Python 3.8+ es requerido"
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)"; then
    error "Python 3.8+ requerido, encontrado: $PYTHON_VERSION"
fi

log "✅ Python $PYTHON_VERSION detectado"

# Verificar Redis
if ! command -v redis-server &> /dev/null; then
    warn "Redis no encontrado, instalando..."
    sudo apt update
    sudo apt install -y redis-server
    sudo systemctl enable redis-server
    sudo systemctl start redis-server
fi

log "✅ Redis configurado"

# Verificar nginx
if ! command -v nginx &> /dev/null; then
    warn "Nginx no encontrado, instalando..."
    sudo apt update
    sudo apt install -y nginx
    sudo systemctl enable nginx
fi

log "✅ Nginx disponible"

# Crear usuario del sistema para el servidor de pagos
if ! id "smartcompute" &>/dev/null; then
    log "👤 Creando usuario del sistema 'smartcompute'..."
    sudo useradd -r -s /bin/false -d /opt/smartcompute -m smartcompute
fi

# Crear estructura de directorios segura
log "📁 Configurando estructura de directorios..."

sudo mkdir -p /opt/smartcompute/{app,logs,ssl,backups}
sudo mkdir -p /var/log/smartcompute
sudo mkdir -p /etc/smartcompute

# Establecer permisos seguros
sudo chown -R smartcompute:smartcompute /opt/smartcompute
sudo chown -R smartcompute:smartcompute /var/log/smartcompute
sudo chmod 750 /opt/smartcompute
sudo chmod 750 /var/log/smartcompute
sudo chmod 700 /opt/smartcompute/ssl

log "🔐 Configurando permisos de seguridad..."

# Copiar archivos de la aplicación
log "📋 Copiando archivos de la aplicación..."

sudo cp payments/secure_production_server.py /opt/smartcompute/app/
sudo cp payments/production_environment.env /opt/smartcompute/app/.env
sudo chown smartcompute:smartcompute /opt/smartcompute/app/*
sudo chmod 640 /opt/smartcompute/app/.env
sudo chmod 644 /opt/smartcompute/app/secure_production_server.py

# Instalar dependencias Python en entorno virtual
log "🐍 Configurando entorno virtual Python..."

sudo -u smartcompute python3 -m venv /opt/smartcompute/venv
sudo -u smartcompute /opt/smartcompute/venv/bin/pip install --upgrade pip

# Crear requirements.txt para producción
cat > /tmp/requirements_production.txt << 'EOF'
Flask==2.3.3
Flask-CORS==4.0.0
Flask-Limiter==3.5.0
redis==5.0.1
requests==2.31.0
gunicorn==21.2.0
cryptography==41.0.7
PyJWT==2.8.0
python-dotenv==1.0.0
EOF

sudo -u smartcompute /opt/smartcompute/venv/bin/pip install -r /tmp/requirements_production.txt
rm /tmp/requirements_production.txt

log "✅ Dependencias Python instaladas"

# Configurar systemd service
log "🔧 Configurando servicio systemd..."

sudo tee /etc/systemd/system/smartcompute-payments.service > /dev/null << 'EOF'
[Unit]
Description=SmartCompute Secure Payment Server
After=network.target redis.service
Wants=redis.service

[Service]
Type=forking
User=smartcompute
Group=smartcompute
WorkingDirectory=/opt/smartcompute/app
Environment=PATH=/opt/smartcompute/venv/bin
EnvironmentFile=/opt/smartcompute/app/.env
ExecStart=/opt/smartcompute/venv/bin/gunicorn --daemon --bind 127.0.0.1:8443 --workers 4 --timeout 120 --max-requests 1000 --max-requests-jitter 100 --preload --log-level info --access-logfile /var/log/smartcompute/access.log --error-logfile /var/log/smartcompute/error.log secure_production_server:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
NoNewPrivileges=true
ReadWritePaths=/var/log/smartcompute /opt/smartcompute/logs

[Install]
WantedBy=multi-user.target
EOF

# Configurar logrotate
log "📝 Configurando rotación de logs..."

sudo tee /etc/logrotate.d/smartcompute > /dev/null << 'EOF'
/var/log/smartcompute/*.log {
    daily
    missingok
    rotate 90
    compress
    delaycompress
    notifempty
    create 640 smartcompute smartcompute
    postrotate
        systemctl reload smartcompute-payments.service > /dev/null 2>&1 || true
    endscript
}
EOF

# Configurar nginx como proxy reverso con SSL
log "🌐 Configurando nginx con SSL..."

sudo tee /etc/nginx/sites-available/smartcompute-payments > /dev/null << 'EOF'
# SmartCompute Secure Payment Server - Nginx Configuration

# Rate limiting
limit_req_zone $binary_remote_addr zone=payment_api:10m rate=5r/m;
limit_req_zone $binary_remote_addr zone=webhooks:10m rate=50r/m;

# Upstream backend
upstream smartcompute_payments {
    server 127.0.0.1:8443 max_fails=3 fail_timeout=30s;
    keepalive 32;
}

server {
    listen 80;
    server_name payments.smartcompute.io;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name payments.smartcompute.io;

    # SSL Configuration
    ssl_certificate /opt/smartcompute/ssl/smartcompute.crt;
    ssl_certificate_key /opt/smartcompute/ssl/smartcompute.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header Content-Security-Policy "default-src 'self'" always;

    # Logging
    access_log /var/log/nginx/smartcompute-payments-access.log;
    error_log /var/log/nginx/smartcompute-payments-error.log;

    # API endpoints with strict rate limiting
    location /api/ {
        limit_req zone=payment_api burst=10 nodelay;
        limit_req_status 429;

        proxy_pass http://smartcompute_payments;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Webhook endpoints with higher rate limits
    location /webhooks/ {
        limit_req zone=webhooks burst=100 nodelay;

        proxy_pass http://smartcompute_payments;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Download endpoints
    location /download/ {
        limit_req zone=payment_api burst=5 nodelay;

        proxy_pass http://smartcompute_payments;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check (no rate limiting)
    location /health {
        proxy_pass http://smartcompute_payments;
        access_log off;
    }

    # Block all other requests
    location / {
        return 404;
    }
}
EOF

# Activar sitio nginx
sudo ln -sf /etc/nginx/sites-available/smartcompute-payments /etc/nginx/sites-enabled/
sudo nginx -t

log "🔥 Configurando firewall..."

# Configurar UFW firewall
if command -v ufw &> /dev/null; then
    sudo ufw --force enable
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    sudo ufw allow ssh
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    sudo ufw allow from 127.0.0.1 to any port 8443
    log "✅ Firewall configurado"
else
    warn "UFW no disponible, configurar firewall manualmente"
fi

# Configurar fail2ban para protección DDoS
log "🛡️ Configurando fail2ban..."

if ! command -v fail2ban-server &> /dev/null; then
    sudo apt install -y fail2ban
fi

sudo tee /etc/fail2ban/jail.d/smartcompute.conf > /dev/null << 'EOF'
[smartcompute-payments]
enabled = true
port = 80,443
protocol = tcp
filter = smartcompute-payments
logpath = /var/log/nginx/smartcompute-payments-access.log
maxretry = 10
bantime = 3600
findtime = 600
action = iptables-multiport[name=smartcompute-payments, port="80,443", protocol=tcp]
EOF

sudo tee /etc/fail2ban/filter.d/smartcompute-payments.conf > /dev/null << 'EOF'
[Definition]
failregex = ^<HOST> - - \[.*\] "(GET|POST|HEAD).*" (4\d\d|5\d\d) .*$
ignoreregex =
EOF

sudo systemctl enable fail2ban
sudo systemctl restart fail2ban

log "✅ Fail2ban configurado"

# Generar certificados SSL autofirmados (para testing)
log "🔐 Generando certificados SSL temporales..."

if [ ! -f /opt/smartcompute/ssl/smartcompute.key ]; then
    sudo openssl req -x509 -newkey rsa:4096 -keyout /opt/smartcompute/ssl/smartcompute.key -out /opt/smartcompute/ssl/smartcompute.crt -days 365 -nodes -subj "/C=AR/ST=CABA/L=Buenos Aires/O=SmartCompute/CN=payments.smartcompute.io"
    sudo chown smartcompute:smartcompute /opt/smartcompute/ssl/*
    sudo chmod 400 /opt/smartcompute/ssl/smartcompute.key
    sudo chmod 444 /opt/smartcompute/ssl/smartcompute.crt
fi

warn "⚠️  Certificados SSL autofirmados generados para testing"
warn "⚠️  En producción, usar certificados de Let's Encrypt o CA confiable"

# Configurar variables de entorno de producción
log "🔧 Configurando variables de entorno..."

echo ""
echo -e "${YELLOW}🔑 CONFIGURACIÓN CRÍTICA REQUERIDA:${NC}"
echo ""
echo "Edita el archivo: /opt/smartcompute/app/.env"
echo "Configura las siguientes variables con valores reales:"
echo ""
echo "  MP_ACCESS_TOKEN=tu-token-real-de-mercadopago"
echo "  MP_CLIENT_ID=tu-client-id-real"
echo "  MP_CLIENT_SECRET=tu-client-secret-real"
echo "  BITSO_API_KEY=tu-api-key-real-de-bitso"
echo "  BITSO_API_SECRET=tu-api-secret-real"
echo "  REDIS_PASSWORD=tu-password-redis-seguro"
echo ""

# Configurar sistema de respaldo
log "💾 Configurando sistema de respaldo..."

sudo tee /opt/smartcompute/backup.sh > /dev/null << 'EOF'
#!/bin/bash
# SmartCompute Payment Server Backup Script

BACKUP_DIR="/opt/smartcompute/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup de configuraciones
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" /opt/smartcompute/app/.env /etc/nginx/sites-available/smartcompute-payments

# Backup de logs de seguridad
tar -czf "$BACKUP_DIR/logs_$DATE.tar.gz" /var/log/smartcompute/

# Backup de base de datos Redis
redis-cli --rdb "$BACKUP_DIR/redis_$DATE.rdb"

# Limpiar backups antiguos (mantener 30 días)
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete
find "$BACKUP_DIR" -name "*.rdb" -mtime +30 -delete

echo "Backup completado: $DATE"
EOF

sudo chmod +x /opt/smartcompute/backup.sh
sudo chown smartcompute:smartcompute /opt/smartcompute/backup.sh

# Configurar cron para backup diario
(sudo crontab -u smartcompute -l 2>/dev/null; echo "0 2 * * * /opt/smartcompute/backup.sh >> /var/log/smartcompute/backup.log 2>&1") | sudo crontab -u smartcompute -

# Habilitar servicios
log "🚀 Habilitando servicios..."

sudo systemctl daemon-reload
sudo systemctl enable redis-server
sudo systemctl enable smartcompute-payments
sudo systemctl enable nginx

log "🎯 Iniciando servicios..."

sudo systemctl start redis-server
sudo systemctl restart nginx

# Mostrar estado de servicios
log "📊 Estado de los servicios:"

echo ""
sudo systemctl status redis-server --no-pager -l
echo ""
sudo systemctl status nginx --no-pager -l
echo ""

# Instrucciones finales
echo ""
echo -e "${GREEN}✅ INSTALACIÓN COMPLETADA${NC}"
echo "=============================================================="
echo ""
echo -e "${BLUE}📋 PASOS FINALES REQUERIDOS:${NC}"
echo ""
echo "1. 🔑 Configurar credenciales reales:"
echo "   sudo nano /opt/smartcompute/app/.env"
echo ""
echo "2. 🔐 Configurar certificados SSL reales:"
echo "   sudo certbot --nginx -d payments.smartcompute.io"
echo ""
echo "3. 🚀 Iniciar el servidor de pagos:"
echo "   sudo systemctl start smartcompute-payments"
echo ""
echo "4. ✅ Verificar funcionamiento:"
echo "   curl -k https://payments.smartcompute.io/health"
echo ""
echo "5. 📊 Monitorear logs:"
echo "   sudo tail -f /var/log/smartcompute/security_events.log"
echo ""
echo -e "${GREEN}🎯 URLs de Producción:${NC}"
echo "   API: https://payments.smartcompute.io/api/"
echo "   Webhooks: https://payments.smartcompute.io/webhooks/"
echo "   Health: https://payments.smartcompute.io/health"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANTE: Configurar monitoreo 24/7 para logs de seguridad${NC}"
echo ""

log "🔒 Deployment completado con éxito"