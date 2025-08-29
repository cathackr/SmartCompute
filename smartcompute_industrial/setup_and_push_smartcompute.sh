#!/bin/bash
# ------------------------------------------------------------
# Setup SmartCompute Industrial y subir a GitHub
# ------------------------------------------------------------

# Salir ante cualquier error
set -e

echo "🚀 Iniciando setup completo de SmartCompute Industrial..."

# Variables
REPO_DIR="$PWD"
MODULE_DIR="$REPO_DIR"
PROJECT_NAME="SmartCompute Industrial"

# ----------------------------
# Verificar que estamos en el directorio correcto
# ----------------------------
if [ ! -f "security.py" ] || [ ! -f "plc_simulator_simple.py" ]; then
    echo "❌ Error: Ejecute este script desde el directorio smartcompute_industrial/"
    echo "   Los archivos security.py y plc_simulator_simple.py deben estar presentes"
    exit 1
fi

# ----------------------------
# Crear/actualizar secure_demo.py con imports correctos
# ----------------------------
echo "🔧 Actualizando secure_demo.py con imports correctos..."

cat > "secure_demo.py" << 'EOF'
#!/usr/bin/env python3
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from security import secure_sensor_data, save_secure_json
from plc_simulator_simple import PLCSimulator, create_default_devices

def get_secure_plc_data():
    devices = create_default_devices()
    simulator = PLCSimulator(devices)
    
    # Actualizar una vez los valores
    for sim in simulator.simulators.values():
        sim.update_values()
    
    raw_data = simulator.get_device_status()
    hash_keys = ["name"]
    encrypt_keys = ["simulation_type"]
    secured_data = secure_sensor_data(
        raw_data,
        hash_keys=hash_keys,
        encrypt_keys=encrypt_keys
    )
    save_secure_json(secured_data, "secured_sensors.json")
    return secured_data

async def monitor_secure_data():
    while True:
        data = get_secure_plc_data()
        print("🔹 Datos seguros PLC:", data)
        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(monitor_secure_data())
EOF

chmod +x "secure_demo.py"

# ----------------------------
# Crear requirements.txt específico
# ----------------------------
echo "📦 Creando requirements.txt..."

cat > "requirements.txt" << 'EOF'
# SmartCompute Industrial - Dependencias
cryptography>=41.0.0
pycryptodome>=3.19.0
numpy>=1.24.0
pydantic>=2.5.0
python-dotenv>=1.0.0
asyncio-mqtt>=0.13.0
pytest>=7.4.0
pytest-asyncio>=0.21.0
EOF

# ----------------------------
# Crear README.md para el módulo
# ----------------------------
echo "📖 Creando documentación README.md..."

cat > "README.md" << 'EOF'
# SmartCompute Industrial

Sistema de monitoreo industrial con funciones de seguridad avanzadas para simulación de PLC y manejo seguro de datos de sensores.

## 🚀 Características

- **Simulación de PLC**: Simula dispositivos industriales realistas
- **Seguridad**: Encriptación AES-256 y hashing SHA-256
- **Monitoreo en Tiempo Real**: Actualización continua de datos
- **Exportación de Datos**: Generación de datasets JSON
- **Detección de Anomalías**: Simulación de eventos anómalos

## 📋 Instalación

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar demo seguro
python secure_demo.py

# Exportar datos de simulación
python plc_simulator_simple.py --mode export --output plc_data.json
```

## 🛠️ Uso

### Demo de Monitoreo Seguro
```bash
python secure_demo.py
```
Ejecuta un monitoreo continuo de 3 dispositivos industriales con datos encriptados.

### Exportación de Datos
```bash
python plc_simulator_simple.py --mode export --output datos.json
```
Genera 100 puntos de datos de simulación industrial.

### Simulación Interactiva
```bash
python plc_simulator_simple.py --mode interactive
```
Ejecuta simulación en tiempo real con logging detallado.

## 📊 Datos Simulados

- **Bomba Principal**: Temperatura, presión, flujo, vibración
- **Motor Compresor**: Control de velocidad y eficiencia  
- **Sistema HVAC**: Monitoreo ambiental

## 🔒 Seguridad

- Encriptación automática de datos sensibles
- Hash de identificadores únicos
- Almacenamiento seguro en JSON
- Rotación automática de claves

## 📈 Rendimiento

- Actualización de datos cada 5 segundos
- Soporte para múltiples dispositivos concurrentes
- Logging estructurado con niveles configurables
- Detección automática de anomalías

---

🤖 **SmartCompute Industrial** - Sistema de monitoreo inteligente para entornos industriales
EOF

# ----------------------------
# Verificar estructura de archivos
# ----------------------------
echo ""
echo "📋 Verificando archivos creados:"
ls -la

# ----------------------------
# Añadir al control de versiones Git
# ----------------------------
echo ""
echo "📤 Preparando para Git..."

# Ir al directorio raíz del repositorio
cd ..

# Verificar si estamos en un repositorio Git
if [ ! -d ".git" ]; then
    echo "⚠️  No es un repositorio Git. Inicializando..."
    git init
fi

# Añadir archivos
echo "➕ Añadiendo archivos al staging..."
git add smartcompute_industrial/

# Verificar estado
echo ""
echo "📊 Estado del repositorio:"
git status

# ----------------------------
# Crear commit
# ----------------------------
echo ""
echo "💾 ¿Crear commit y subir cambios? (y/N)"
read -r confirm

if [[ $confirm =~ ^[Yy]$ ]]; then
    echo "💬 Creando commit..."
    
    git commit -m "feat: add SmartCompute Industrial security module

- Add secure PLC data monitoring with AES-256 encryption
- Add industrial device simulation (pumps, motors, HVAC)
- Add real-time data export with anomaly detection
- Add comprehensive documentation and setup scripts
- Add security features for sensitive data protection

Key Features:
- 🔒 Encrypted sensor data handling
- 🏭 Realistic industrial device simulation  
- 📊 JSON data export capabilities
- 🚨 Anomaly detection and logging
- ⚡ Real-time monitoring dashboard

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>"
    
    # Verificar si hay remote configurado
    if git remote get-url origin &>/dev/null; then
        echo ""
        echo "🚀 ¿Subir a GitHub? (y/N)"
        read -r push_confirm
        
        if [[ $push_confirm =~ ^[Yy]$ ]]; then
            echo "📤 Subiendo a GitHub..."
            
            # Obtener rama actual
            CURRENT_BRANCH=$(git branch --show-current)
            
            git push origin "$CURRENT_BRANCH"
            
            echo "✅ Cambios subidos exitosamente!"
        else
            echo "⏸️  Commit creado localmente. Use 'git push' para subir cuando esté listo."
        fi
    else
        echo "⚠️  No hay remote configurado. Configure primero:"
        echo "   git remote add origin <URL_REPOSITORIO>"
        echo "   git push -u origin main"
    fi
    
else
    echo "⏸️  Setup completado sin commit."
fi

echo ""
echo "✅ Setup de SmartCompute Industrial completado!"
echo ""
echo "📁 Archivos disponibles:"
echo "   📁 smartcompute_industrial/"
echo "   ├── 🔒 secure_demo.py           # Demo de monitoreo seguro"
echo "   ├── 🏭 plc_simulator_simple.py  # Simulador PLC"  
echo "   ├── 🛡️  security.py              # Módulo de seguridad"
echo "   ├── 📦 requirements.txt         # Dependencias"
echo "   └── 📖 README.md               # Documentación"
echo ""
echo "🚀 Para probar:"
echo "   cd smartcompute_industrial"
echo "   pip install -r requirements.txt"
echo "   python secure_demo.py"
echo ""
echo "📊 Para exportar datos:"
echo "   python plc_simulator_simple.py --mode export --output datos.json"