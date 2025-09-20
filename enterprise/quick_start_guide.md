# 🚀 SmartCompute Enterprise - Guía de Inicio Rápido

## Análisis Local en Tiempo Real

### 🎯 ¿Qué hace?

SmartCompute Enterprise analiza tu sistema local en tiempo real durante **3 minutos** y muestra:

- 📊 **Métricas del Sistema**: CPU, memoria, conexiones, procesos
- 🔒 **Análisis de Seguridad**: Puntuación en tiempo real, detección de amenazas
- 🌐 **Actividad de Red**: Conexiones sospechosas, puertos, tráfico
- ⚙️ **Análisis de Procesos**: Procesos sospechosos, alto consumo de recursos
- 🚨 **Eventos de Seguridad**: Alertas en tiempo real
- 🧠 **IA de Amenazas**: Análisis inteligente con SmartCompute HRM

### 🚀 Cómo Ejecutar

#### Opción 1: Script Automático
```bash
cd /home/gatux/smartcompute/enterprise/
./launch_smartcompute_analysis.sh
```

#### Opción 2: Ejecución Directa
```bash
cd /home/gatux/smartcompute/enterprise/
python3 smartcompute_live_analysis.py
```

### 🌐 Interfaz Web

El sistema automáticamente:
1. ✅ Inicia el análisis del sistema
2. 🌐 Lanza servidor web en `http://localhost:8888`
3. 📱 Abre tu navegador automáticamente
4. 📊 Muestra dashboard en tiempo real por 3 minutos
5. 📄 Genera reporte final en `/tmp/smartcompute_live_analysis_report.json`

### 📊 Dashboard en Tiempo Real

El dashboard web muestra:

#### 📈 Panel Superior
- 🟢 **Estado**: Análisis Activo/Completado
- ⏱️ **Tiempo**: Progreso 00:00 / 03:00
- 📊 **Barra de Progreso**: Visual del análisis

#### 🔥 Métricas Principales
- **CPU**: Uso actual y gráfico histórico
- **Memoria**: Utilización en tiempo real
- **Conexiones**: Conexiones de red activas
- **Procesos**: Número de procesos ejecutándose

#### 🔒 Seguridad
- **Puntuación**: Score de seguridad en tiempo real (0-100)
- **Nivel de Amenaza**: BAJO/MEDIO/ALTO
- **Contadores**: Procesos sospechosos, red inusual, alertas

#### 🌐 Red
- **Conexiones Activas**: Monitoreo en tiempo real
- **Puertos**: Servicios escuchando
- **IPs Sospechosas**: Detección automática

#### 🚨 Eventos
- **Eventos de Seguridad**: Alertas clasificadas por severidad
- **Análisis IA**: Patrones detectados por SmartCompute HRM

### 🛠️ Requisitos

- ✅ **Python 3.7+**: Instalado
- ✅ **psutil**: Se instala automáticamente si no existe
- ✅ **Navegador web**: Para ver el dashboard

### 🔧 Solución de Problemas

#### Puerto Ocupado
Si el puerto 8888 está ocupado, el sistema automáticamente intentará 8889, 8890, etc.

#### Sin Navegador Automático
Si no se abre automáticamente, ve manualmente a:
```
http://localhost:8888
```

#### Dependencias
Si falta psutil:
```bash
pip3 install psutil --user
```

### 📄 Salidas del Sistema

#### Durante la Ejecución
- 🖥️ **Terminal**: Log de eventos en tiempo real
- 🌐 **Web**: Dashboard interactivo actualizado cada segundo

#### Al Finalizar
- 📄 **Reporte JSON**: `/tmp/smartcompute_live_analysis_report.json`
- 📊 **Estadísticas**: Resumen completo del análisis
- 🔒 **Score Final**: Puntuación de seguridad del sistema

### 🎯 Ejemplo de Uso

```bash
# 1. Navegar al directorio
cd /home/gatux/smartcompute/enterprise/

# 2. Ejecutar análisis
./launch_smartcompute_analysis.sh

# 3. Ver dashboard en navegador (se abre automáticamente)
# http://localhost:8888

# 4. Observar análisis por 3 minutos

# 5. Revisar reporte final
cat /tmp/smartcompute_live_analysis_report.json
```

### 🌟 Características Avanzadas

#### Detección Inteligente
- **Procesos Sospechosos**: Nombres maliciosos conocidos
- **IPs Peligrosas**: Rangos de red sospechosos
- **Uso Anómalo**: Patrones de consumo inusuales

#### Machine Learning
- **Análisis HRM**: IA de SmartCompute para patrones
- **Confianza**: Porcentaje de certeza en detecciones
- **Recomendaciones**: Sugerencias automáticas

#### Tiempo Real
- **Actualización**: Cada segundo
- **Sin Caché**: Datos siempre frescos
- **Responsivo**: Interfaz adaptativa

### 🚨 Importante

- ⏱️ **Duración Fija**: El análisis dura exactamente 3 minutos
- 🔒 **Seguro**: Solo monitorea, no modifica el sistema
- 📊 **Local**: Todos los datos permanecen en tu máquina
- 🌐 **Temporal**: El servidor web se cierra automáticamente

¡Listo para analizar tu sistema con SmartCompute Enterprise! 🚀