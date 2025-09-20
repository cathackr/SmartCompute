#!/bin/bash
# Script para abrir el informe SmartCompute Enterprise

echo "🚀 Abriendo informe SmartCompute Enterprise..."

# Buscar navegadores disponibles
if command -v google-chrome &> /dev/null; then
    google-chrome "/home/gatux/smartcompute/enterprise/informe_evaluacion_completa.html"
elif command -v firefox &> /dev/null; then
    firefox "/home/gatux/smartcompute/enterprise/informe_evaluacion_completa.html"
elif command -v chromium-browser &> /dev/null; then
    chromium-browser "/home/gatux/smartcompute/enterprise/informe_evaluacion_completa.html"
elif command -v microsoft-edge &> /dev/null; then
    microsoft-edge "/home/gatux/smartcompute/enterprise/informe_evaluacion_completa.html"
else
    echo "❌ No se encontró navegador web instalado"
    echo "📄 Abra manualmente: /home/gatux/smartcompute/enterprise/informe_evaluacion_completa.html"
fi
