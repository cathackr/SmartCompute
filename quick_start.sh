#!/bin/bash
echo "🚀 Iniciando SmartCompute Industrial..."
cd "$(dirname "$0")/smartcompute_industrial"

# Verificar entorno virtual
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Recomendación: Activar entorno virtual primero"
    echo "   source venv/bin/activate"
fi

# Ejecutar demo seguro
python secure_demo.py
