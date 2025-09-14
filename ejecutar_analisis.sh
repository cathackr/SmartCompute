#!/bin/bash

echo "========================================"
echo "   SmartCompute Express - Linux/Mac"
echo "   Análisis automático de red OSI"
echo "========================================"
echo

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 no encontrado"
    echo "Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "macOS: brew install python3"
    exit 1
fi

# Verificar si pip está disponible
if ! command -v pip3 &> /dev/null; then
    echo "ERROR: pip3 no encontrado"
    echo "Ubuntu/Debian: sudo apt install python3-pip"
    exit 1
fi

# Verificar dependencias
echo "Verificando dependencias..."
python3 -c "import psutil" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Instalando dependencias necesarias..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: No se pudieron instalar las dependencias"
        echo "Intenta con: sudo pip3 install -r requirements.txt"
        exit 1
    fi
fi

echo
echo "Iniciando análisis SmartCompute Express..."
echo
python3 smartcompute_express.py --auto-open

echo
echo "========================================"
echo "   Análisis completado!"
echo "   Dashboard abierto en tu navegador"
echo "========================================"