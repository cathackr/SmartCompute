#!/bin/bash
# ------------------------------------------------------------
# Script para iniciar API segura con túnel ngrok
# ------------------------------------------------------------

# Variables
API_PORT=8000
API_FILE="secure_api.py"
LOG_FILE="api_server.log"

echo "🚀 Iniciando SmartCompute Industrial Secure API..."

# Verificar si estamos en el directorio correcto
if [ ! -f "$API_FILE" ]; then
    echo "❌ Error: $API_FILE no encontrado"
    echo "   Ejecute este script desde el directorio smartcompute_industrial/"
    exit 1
fi

# Activar entorno virtual si existe
if [ -f "../venv/bin/activate" ]; then
    echo "🔧 Activando entorno virtual..."
    source ../venv/bin/activate
elif [ -f "venv/bin/activate" ]; then
    echo "🔧 Activando entorno virtual local..."
    source venv/bin/activate
else
    echo "⚠️  No se encontró entorno virtual, usando Python global"
fi

# Verificar si FastAPI está instalado
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "📦 FastAPI no encontrado, instalando dependencias..."
    pip install fastapi uvicorn
fi

# Matar procesos existentes en el puerto
echo "🔄 Verificando puerto $API_PORT..."
lsof -ti:$API_PORT | xargs kill -9 2>/dev/null || true

# Ejecutar API en background
echo "🚀 Iniciando API segura en http://127.0.0.1:$API_PORT..."
echo "📝 Log disponible en: $LOG_FILE"

nohup python3 "$API_FILE" > "$LOG_FILE" 2>&1 &
API_PID=$!

# Esperar a que arranque la API
echo "⏳ Esperando a que la API arranque..."
sleep 3

# Verificar si la API está corriendo
if ps -p $API_PID > /dev/null; then
    echo "✅ API iniciada correctamente (PID: $API_PID)"
    
    # Mostrar información de la API
    echo ""
    echo "📡 API Endpoints disponibles:"
    echo "   • http://127.0.0.1:$API_PORT/ (Info general)"
    echo "   • http://127.0.0.1:$API_PORT/api/health (Health check)"
    echo "   • http://127.0.0.1:$API_PORT/api/sensors (Datos PLC - requiere API key)"
    echo "   • http://127.0.0.1:$API_PORT/docs (Documentación Swagger)"
    echo ""
    echo "🔑 API Key requerida: X-API-Key: mi_clave_secreta_123"
    echo ""
else
    echo "❌ Error: La API no pudo iniciarse"
    echo "📋 Revisando log:"
    tail -n 10 "$LOG_FILE"
    exit 1
fi

# Verificar si ngrok está disponible
if command -v ngrok >/dev/null 2>&1; then
    echo "🔗 Iniciando túnel ngrok..."
    echo "   • Túnel HTTP público se creará automáticamente"
    echo "   • Use Ctrl+C para detener ngrok (la API seguirá corriendo)"
    echo ""
    
    # Iniciar ngrok
    ngrok http $API_PORT
    
else
    echo "⚠️  ngrok no encontrado en el sistema"
    echo ""
    echo "🔧 Para instalar ngrok:"
    echo "   1. Visite: https://ngrok.com/download"
    echo "   2. Descargue e instale ngrok"
    echo "   3. Configure su token: ngrok authtoken <TOKEN>"
    echo ""
    echo "🌐 Mientras tanto, la API está disponible localmente en:"
    echo "   http://127.0.0.1:$API_PORT"
    echo ""
    echo "📋 Para detener la API ejecute: kill $API_PID"
    echo "📝 Monitor de logs: tail -f $LOG_FILE"
fi