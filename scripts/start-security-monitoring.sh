#!/bin/bash
# =================================================================
# SMARTCOMPUTE SECURITY MONITORING STARTUP
# =================================================================
# 🔒 Inicia todos los servicios con monitoreo de seguridad

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🔒 Iniciando SmartCompute con monitoreo de seguridad..."

# Verificar que existe .env
if [[ ! -f "$PROJECT_DIR/.env" ]]; then
    echo "❌ Archivo .env no encontrado. Copialo desde .env.example y configúralo."
    exit 1
fi

# Cargar variables de entorno
set -a
source "$PROJECT_DIR/.env"
set +a

# Función para manejar cleanup
cleanup() {
    echo "🛑 Deteniendo servicios SmartCompute..."
    pkill -f "smartcompute" 2>/dev/null || true
    pkill -f "security_monitor" 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# 1. Iniciar monitor de seguridad en background
echo "🔒 Iniciando monitor de seguridad..."
cd "$PROJECT_DIR"
python3 security/security_monitor.py &
SECURITY_PID=$!

# 2. Iniciar servicios SmartCompute
echo "🚀 Iniciando servicios SmartCompute..."

# Dashboard Enterprise (puerto 8000)
cd "$PROJECT_DIR" 
python3 -m smartcompute.api.health_endpoints --port 8000 &
DASHBOARD_PID=$!

# Network Intelligence API (puerto 8002)
cd "$PROJECT_DIR/smartcompute_industrial"
python3 network_api.py &
NETWORK_PID=$!

# Token Intelligence API (puerto 8001)
python3 token_api.py &
TOKEN_PID=$!

# Payment API (puerto 8003) - SOLO si está configurado
if [[ -n "${MP_ACCESS_TOKEN:-}" ]]; then
    python3 payment_api.py &
    PAYMENT_PID=$!
    echo "💳 Payment API iniciado (puerto 8003)"
else
    echo "⚠️  Payment API omitido (MP_ACCESS_TOKEN no configurado)"
fi

echo "✅ Servicios SmartCompute iniciados"
echo ""
echo "📊 Servicios disponibles:"
echo "   • Dashboard: http://127.0.0.1:8000"
echo "   • Token API: http://127.0.0.1:8001" 
echo "   • Network API: http://127.0.0.1:8002"
echo "   • Payment API: http://127.0.0.1:8003 (si configurado)"
echo ""
echo "🔒 Monitor de seguridad activo (PID: $SECURITY_PID)"
echo ""

# 3. Verificar que los servicios están respondiendo
echo "🔍 Verificando servicios..."
sleep 5

check_service() {
    local service_name=$1
    local port=$2
    local endpoint=${3:-"/health"}
    
    if curl -sf "http://127.0.0.1:${port}${endpoint}" > /dev/null 2>&1; then
        echo "✅ $service_name - OK"
    else
        echo "❌ $service_name - FALLO"
    fi
}

check_service "Dashboard" "8000"
check_service "Token API" "8001" "/api/health"
check_service "Network API" "8002" "/api/health"

if [[ -n "${MP_ACCESS_TOKEN:-}" ]]; then
    check_service "Payment API" "8003"
fi

echo ""
echo "🔒 SmartCompute iniciado con monitoreo de seguridad"
echo "⚠️  Presiona Ctrl+C para detener todos los servicios"
echo ""

# Mostrar logs de seguridad en tiempo real
echo "📋 Logs de seguridad (Ctrl+C para salir):"
tail -f "$PROJECT_DIR/security/logs/security_events.log" 2>/dev/null || echo "Esperando eventos de seguridad..."

# Esperar hasta recibir señal
wait