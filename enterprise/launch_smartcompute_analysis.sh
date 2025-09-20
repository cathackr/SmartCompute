#!/bin/bash

# SmartCompute Enterprise - Script de Lanzamiento para Análisis Local
# ===================================================================

echo "🚀 SmartCompute Enterprise - Análisis Local en Tiempo Real"
echo "=========================================================="
echo ""
echo "🔍 Preparando análisis del sistema local..."
echo "⏱️  Duración: 3 minutos"
echo "🌐 Interfaz web: http://localhost:8888"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no encontrado. Por favor instala Python 3.7+"
    exit 1
fi

# Verificar dependencias básicas
echo "🔧 Verificando dependencias..."
python3 -c "import psutil, asyncio, json, webbrowser" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Instalando dependencia psutil..."
    pip3 install psutil --user --break-system-packages 2>/dev/null || pip3 install psutil --user
fi

# Cambiar al directorio correcto
cd /home/gatux/smartcompute/enterprise/

# Ejecutar análisis
echo ""
echo "🎯 Iniciando SmartCompute Enterprise Analysis..."
echo "📱 Se abrirá automáticamente en tu navegador: http://localhost:8888"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔥 ANÁLISIS INICIADO - Monitoreando sistema en tiempo real..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Lanzar análisis
python3 smartcompute_live_analysis.py