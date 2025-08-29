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
