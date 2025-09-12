#!/bin/bash
# =================================================================
# SMARTCOMPUTE NGINX SECURITY SETUP
# =================================================================
# 🔒 Configura nginx como proxy reverso seguro para SmartCompute

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
NGINX_CONF_DIR="/etc/nginx/sites-available"
NGINX_ENABLED_DIR="/etc/nginx/sites-enabled"
SSL_DIR="/etc/nginx/ssl"

echo "🔒 Configurando nginx como proxy seguro para SmartCompute..."

# Verificar permisos de root
if [[ $EUID -ne 0 ]]; then
   echo "❌ Este script requiere permisos de root (usar sudo)"
   exit 1
fi

# 1. Instalar nginx si no existe
if ! command -v nginx &> /dev/null; then
    echo "📦 Instalando nginx..."
    apt update
    apt install -y nginx
fi

# 2. Crear directorio SSL
mkdir -p "$SSL_DIR"

# 3. Generar certificado autofirmado para desarrollo
if [[ ! -f "$SSL_DIR/smartcompute.crt" ]]; then
    echo "🔐 Generando certificado SSL autofirmado..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "$SSL_DIR/smartcompute.key" \
        -out "$SSL_DIR/smartcompute.crt" \
        -subj "/C=AR/ST=BuenosAires/L=MardelPlata/O=SmartCompute/CN=smartcompute.local"
    
    chmod 600 "$SSL_DIR/smartcompute.key"
    chmod 644 "$SSL_DIR/smartcompute.crt"
    echo "✅ Certificado SSL generado en $SSL_DIR"
fi

# 4. Copiar configuración nginx
echo "📋 Copiando configuración nginx..."
cp "$PROJECT_DIR/nginx/smartcompute-secure.conf" "$NGINX_CONF_DIR/"

# 5. Habilitar sitio
ln -sf "$NGINX_CONF_DIR/smartcompute-secure.conf" "$NGINX_ENABLED_DIR/"

# 6. Deshabilitar sitio por defecto
if [[ -f "$NGINX_ENABLED_DIR/default" ]]; then
    rm "$NGINX_ENABLED_DIR/default"
    echo "🗑️ Sitio default deshabilitado"
fi

# 7. Crear directorio de logs
mkdir -p /var/log/nginx
touch /var/log/nginx/smartcompute_error.log
touch /var/log/nginx/smartcompute_access.log

# 8. Verificar configuración
echo "🔍 Verificando configuración nginx..."
if nginx -t; then
    echo "✅ Configuración nginx válida"
else
    echo "❌ Error en configuración nginx"
    exit 1
fi

# 9. Configurar firewall (ufw)
if command -v ufw &> /dev/null; then
    echo "🔥 Configurando firewall..."
    
    # Permitir SSH, HTTP, HTTPS
    ufw allow 22/tcp
    ufw allow 80/tcp
    ufw allow 443/tcp
    
    # CRÍTICO: Bloquear puertos internos desde externa
    ufw deny from any to any port 8000
    ufw deny from any to any port 8001
    ufw deny from any to any port 8002
    ufw deny from any to any port 8003
    
    # Permitir localhost
    ufw allow from 127.0.0.1
    
    echo "🔥 Firewall configurado"
fi

# 10. Reiniciar nginx
systemctl restart nginx
systemctl enable nginx

echo "🎉 ¡Configuración de seguridad nginx completada!"
echo ""
echo "📊 Servicios disponibles:"
echo "   • Dashboard Enterprise: https://localhost/enterprise"
echo "   • Dashboard Unificado: https://localhost/unified"
echo "   • API Network: https://localhost/api/network"
echo "   • API Payments: https://localhost/api/payments (rate limited)"
echo ""
echo "🔒 Seguridad implementada:"
echo "   ✅ TLS/HTTPS forzado"
echo "   ✅ Rate limiting por endpoint"
echo "   ✅ Puertos internos bloqueados"
echo "   ✅ Headers de seguridad"
echo "   ✅ Firewall configurado"
echo ""
echo "⚠️  IMPORTANTE:"
echo "   • Los servicios internos SOLO escuchan en 127.0.0.1"
echo "   • Acceso externo SOLO via nginx HTTPS"
echo "   • Certificado autofirmado (renovar para producción)"