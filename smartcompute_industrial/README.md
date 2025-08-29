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
