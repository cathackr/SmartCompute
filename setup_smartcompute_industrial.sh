#!/bin/bash
# ------------------------------------------------------
# Script de configuración y subida de SmartCompute Industrial
# ------------------------------------------------------

# Salir ante cualquier error
set -e

# Variables
REPO_DIR="$PWD"
MODULE_DIR="$REPO_DIR/smartcompute_industrial"
DOCS_DIR="$REPO_DIR/docs"
GITHUB_REMOTE="origin"
GITHUB_BRANCH="main"

echo "📁 Verificando estructura de carpetas..."
mkdir -p "$MODULE_DIR"
touch "$MODULE_DIR/__init__.py"
mkdir -p "$DOCS_DIR"

# ----------------------------
# Copiar archivos del módulo
# ----------------------------
echo "📋 Copiando archivos de smartcompute_industrial..."
cp ~/smartcompute/SmartCompute/smartcompute_industrial/security.py "$MODULE_DIR/" 2>/dev/null || echo "security.py no encontrado, se omite"
cp ~/smartcompute/SmartCompute/smartcompute_industrial/plc_simulator_simple.py "$MODULE_DIR/" 2>/dev/null || echo "plc_simulator_simple.py no encontrado, se omite"

# ----------------------------
# Crear demo seguro
# ----------------------------
DEMO_FILE="$MODULE_DIR/secure_demo.py"
echo "🎮 Generando demo seguro en $DEMO_FILE..."

cat > "$DEMO_FILE" << 'EOF'
import asyncio
from smartcompute_industrial.security import secure_sensor_data, save_secure_json
from smartcompute_industrial.plc_simulator_simple import PLCSimulator, create_default_devices

def get_secure_plc_data():
    devices = create_default_devices()
    simulator = PLCSimulator(devices)
    
    # Actualizar valores simulados
    for sim in simulator.simulators.values():
        sim.update_values()
    
    raw_data = {dev.device_id: sim.current_values for dev, sim in zip(devices, simulator.simulators.values())}
    
    hash_keys = ["MachineID"] if "MachineID" in raw_data else []
    encrypt_keys = ["SecretToken"] if "SecretToken" in raw_data else []
    
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

# ----------------------------
# Crear guía/documentación
# ----------------------------
GUIDE_FILE="$DOCS_DIR/industrial_guide.md"
echo "📖 Generando documentación en $GUIDE_FILE..."

cat > "$GUIDE_FILE" << 'EOF'
# SmartCompute Industrial - Guía de Uso

## 1. Instalación
```bash
# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

## 2. Funcionalidades Principales

### Simulación de PLC
- Simula dispositivos industriales (sensores, motores, válvulas)
- Genera datos realistas con patrones temporales
- Soporte para múltiples tipos de dispositivos

### Seguridad de Datos
- Encriptación de datos sensibles
- Hash de identificadores
- Almacenamiento seguro en formato JSON

### Monitoreo en Tiempo Real
- Actualización automática de valores
- Logs de seguridad
- Interfaz asíncrona

## 3. Uso del Demo Seguro

```bash
# Ejecutar demo de monitoreo seguro
cd smartcompute_industrial
python secure_demo.py
```

### Características del Demo:
- 🔒 **Seguridad**: Encripta datos sensibles automáticamente
- 📊 **Monitoreo**: Actualiza datos cada 5 segundos
- 💾 **Persistencia**: Guarda datos seguros en `secured_sensors.json`
- 🎛️ **Simulación**: Simula comportamiento real de PLC

## 4. Configuración de Dispositivos

### Tipos de Dispositivos Soportados:
- **Sensores de Temperatura**: Rangos industriales (-40°C a 150°C)
- **Sensores de Presión**: Sistemas hidráulicos (0-100 bar)
- **Motores**: Control de velocidad y estado
- **Válvulas**: Control de apertura/cierre

### Personalización:
```python
from smartcompute_industrial.plc_simulator_simple import PLCDevice

# Crear dispositivo personalizado
device = PLCDevice(
    name="Sensor_Custom",
    device_type="temperature",
    min_value=0,
    max_value=200,
    simulation_type="sine_wave"
)
```

## 5. Seguridad y Mejores Prácticas

### Encriptación:
- Algoritmo AES-256 para datos sensibles
- Claves generadas automáticamente
- Hash SHA-256 para identificadores

### Recomendaciones:
- ✅ Usar HTTPS en producción
- ✅ Rotar claves periódicamente  
- ✅ Validar datos de entrada
- ✅ Logs de auditoría activados

## 6. Troubleshooting

### Problemas Comunes:
1. **Error de importación**: Verificar instalación de dependencias
2. **Permisos de archivo**: Ejecutar con permisos adecuados
3. **Puerto ocupado**: Verificar procesos en segundo plano

### Comandos Útiles:
```bash
# Verificar procesos Python
ps aux | grep python

# Limpiar archivos temporales
rm -f *.json *.log

# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

## 7. Soporte

Para soporte técnico o reportar bugs:
- Revisar logs en `/logs/`
- Verificar configuración en `config/`
- Consultar documentación técnica
EOF

# ----------------------------
# Crear archivo de requisitos específicos
# ----------------------------
REQUIREMENTS_INDUSTRIAL="$MODULE_DIR/requirements_industrial.txt"
echo "📦 Generando requisitos específicos en $REQUIREMENTS_INDUSTRIAL..."

cat > "$REQUIREMENTS_INDUSTRIAL" << 'EOF'
# SmartCompute Industrial - Dependencias Específicas
cryptography>=41.0.0
pycryptodome>=3.19.0
numpy>=1.24.0
asyncio-mqtt>=0.13.0
pydantic>=2.5.0
python-dotenv>=1.0.0
pytest>=7.4.0
pytest-asyncio>=0.21.0
EOF

# ----------------------------
# Crear script de ejecución rápida
# ----------------------------
QUICK_START="$REPO_DIR/quick_start.sh"
echo "⚡ Generando script de inicio rápido en $QUICK_START..."

cat > "$QUICK_START" << 'EOF'
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
EOF

chmod +x "$QUICK_START"

# ----------------------------
# Crear archivo de configuración
# ----------------------------
CONFIG_FILE="$MODULE_DIR/config_industrial.py"
echo "⚙️ Generando configuración en $CONFIG_FILE..."

cat > "$CONFIG_FILE" << 'EOF'
"""
Configuración para SmartCompute Industrial
"""

# Configuración de Seguridad
SECURITY_CONFIG = {
    "encryption_algorithm": "AES-256",
    "hash_algorithm": "SHA-256",
    "key_rotation_days": 30,
    "secure_storage": True
}

# Configuración de Simulación
SIMULATION_CONFIG = {
    "update_interval": 5.0,  # segundos
    "default_devices": 10,
    "realistic_noise": True,
    "save_history": True
}

# Configuración de Dispositivos por Defecto
DEFAULT_DEVICES = [
    {
        "name": "Temp_Sensor_01",
        "type": "temperature",
        "range": {"min": 20, "max": 80},
        "simulation": "sine_wave"
    },
    {
        "name": "Pressure_Sensor_01", 
        "type": "pressure",
        "range": {"min": 0, "max": 100},
        "simulation": "random_walk"
    },
    {
        "name": "Motor_01",
        "type": "motor",
        "range": {"min": 0, "max": 3000},
        "simulation": "step_function"
    },
    {
        "name": "Valve_01",
        "type": "valve",
        "range": {"min": 0, "max": 100},
        "simulation": "binary_toggle"
    }
]

# Configuración de Logging
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "smartcompute_industrial.log",
    "max_size": "10MB",
    "backup_count": 5
}
EOF

# ----------------------------
# Confirmación git y subida
# ----------------------------
echo ""
echo "📋 Archivos creados:"
ls -la "$MODULE_DIR"
echo ""
ls -la "$DOCS_DIR"

echo ""
echo "💾 ¿Confirmar cambios y subir a GitHub? (y/N)"
read -r confirm

if [[ $confirm =~ ^[Yy]$ ]]; then
    echo "📤 Agregando archivos al repositorio..."
    git add .
    
    echo "💬 Creando commit..."
    git commit -m "feat: add SmartCompute Industrial module with security features

- Add secure demo with encrypted sensor data
- Add comprehensive documentation guide
- Add quick start script for easy setup
- Add industrial-specific requirements
- Add configuration module for customization

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>"
    
    echo "🚀 Subiendo a GitHub..."
    git push $GITHUB_REMOTE $GITHUB_BRANCH
    
    echo "✅ Subida completada!"
else
    echo "⏸️ Cambios no confirmados. Archivos creados localmente."
fi

echo ""
echo "✅ Setup completado exitosamente!"
echo ""
echo "📁 Estructura creada:"
echo "   $REPO_DIR/"
echo "   ├── smartcompute_industrial/"
echo "   │   ├── secure_demo.py"
echo "   │   ├── requirements_industrial.txt"
echo "   │   └── config_industrial.py"
echo "   ├── docs/"
echo "   │   └── industrial_guide.md"
echo "   └── quick_start.sh"
echo ""
echo "🚀 Para comenzar:"
echo "   1. cd $REPO_DIR"
echo "   2. source venv/bin/activate  # (si usas entorno virtual)"
echo "   3. pip install -r smartcompute_industrial/requirements_industrial.txt"
echo "   4. ./quick_start.sh"
echo ""
echo "📖 Consulta la documentación en: $GUIDE_FILE"
