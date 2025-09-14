# SmartCompute Dashboard Template - Estándar de Visualización

## 🎯 Visión General

El **SmartCompute Dashboard Template** es una plantilla estandarizada que mantiene consistencia visual en todos los dashboards de SmartCompute, permitiendo cambiar completamente los datos y análisis sin perder la identidad visual profesional.

## 🏗️ Arquitectura del Template

### Layout Estándar (4 Filas Fijas)

```
┌─────────────────────────────────────────────────────┐
│ SYSTEM STATUS (izq)    TÍTULO PRINCIPAL (centro)    │ ← Header
├─────────────────────────────────────────────────────┤
│ ANÁLISIS PRINCIPAL (grande)  │  MÉTRICAS SISTEMA    │ ← Fila 1
├─────────────────────────────────────────────────────┤
│ PANEL 1 │ PANEL 2 │    PANEL 3 (doble ancho)     │ ← Fila 2
├─────────────────────────────────────────────────────┤
│           GRÁFICO TIEMPO REAL (ancho completo)      │ ← Fila 3
├─────────────────────────────────────────────────────┤
│ INFO TÉCNICA (izq)    │    INFO TÉCNICA (der)      │ ← Fila 4
└─────────────────────────────────────────────────────┘
```

### Especificaciones Técnicas

- **Dimensiones**: 24x18 inches (alta resolución)
- **Espaciado**: hspace=0.9, wspace=0.4 (separación óptima)
- **Colores estándar**: Fondo oscuro industrial (#0c1420)
- **Tipografía**: Monospace para datos técnicos
- **Grid**: Líneas sutiles (#444444) no intrusivas

## 📊 Componentes Reutilizables

### 1. Panel Principal de Análisis
```python
dashboard.create_main_analysis_panel(gs, data, title, xlabel)
```
- **Posición**: Fila 1, columnas 0-2 (75% del ancho)
- **Tipo**: Barras horizontales con posicionamiento inteligente
- **Uso**: Análisis primario (OSI, sensores, APIs, etc.)

### 2. Panel de Métricas
```python
dashboard.create_metrics_panel(gs, data, title)
```
- **Posición**: Fila 1, columna 3 (25% del ancho)
- **Tipo**: Barras verticales con valores encima
- **Uso**: KPIs principales del sistema

### 3. Paneles Secundarios
```python
dashboard.create_bar_panel(gs, position, data, title, ylabel)
dashboard.create_horizontal_bar_panel(gs, position, data, title, xlabel)
```
- **Posición**: Fila 2, flexible
- **Uso**: Análisis específicos, distribuciones, estados

### 4. Panel Tiempo Real
```python
dashboard.create_realtime_panel(gs, data, title)
```
- **Posición**: Fila 3, ancho completo
- **Tipo**: Múltiples líneas con áreas rellenas
- **Uso**: Tendencias temporales, monitoreo continuo

### 5. Panel de Información
```python
dashboard.create_info_panel(gs, left_data, right_data)
```
- **Posición**: Fila 4, dos columnas
- **Tipo**: Texto monospace estilo CLI/terminal
- **Uso**: Datos técnicos detallados

## 🎨 Sistema de Colores Estándar

```python
colors = {
    'background': '#0c1420',  # Fondo principal oscuro
    'panel_bg': '#1a2332',    # Fondo de paneles
    'primary': '#00ff88',     # Verde primario (éxito/activo)
    'secondary': '#ffd700',   # Amarillo (advertencias/info)
    'danger': '#ff6b6b',      # Rojo (errores/crítico)
    'warning': '#ffa502',     # Naranja (alertas)
    'info': '#48dbfb',        # Azul (información)
    'grid': '#444444',        # Líneas de grid sutiles
    'text': 'white'           # Texto principal
}
```

## 🚀 Ejemplos de Uso

### 1. Análisis OSI Completo
```bash
python smartcompute_dashboard_template.py
# Output: smartcompute_osi_template_example.png
```

### 2. Análisis Capas 3-4 (Red + Transporte)
```bash
python examples/layer3_4_analysis.py
# Output: smartcompute_l3_l4_analysis.png
```

### 3. Monitoreo IoT Sensores
```bash
python examples/iot_sensors.py
# Output: smartcompute_iot_sensors.png
```

### 4. Análisis Capa 7 - APIs
```bash
python examples/layer7_apis.py
# Output: smartcompute_layer7_apis.png
```

## 🔧 Características Inteligentes

### Posicionamiento Automático de Labels
- **Valores altos**: Se posicionan dentro de las barras
- **Valores bajos**: Se posicionan fuera de las barras
- **Lógica**: Evita superposiciones automáticamente

### Espaciado Adaptativo
- **hspace=0.9**: Separación vertical generosa
- **pad=25-40**: Espaciado de títulos sin colisiones
- **Margins**: Automático para diferentes tamaños de datos

### Colores Contextuales
- **Verde (#00ff88)**: Estados normales/saludables
- **Amarillo (#ffd700)**: Advertencias/atención
- **Rojo (#ff6b6b)**: Errores/críticos
- **Azul (#48dbfb)**: Información/datos

## 📋 Casos de Uso Típicos

### Análisis de Infraestructura
- **OSI 7 capas**: Análisis completo de red
- **L3-L4 específico**: Routing, TCP/UDP, puertos
- **L7 aplicaciones**: APIs, servicios, lenguajes

### Monitoreo Industrial
- **Sensores IoT**: Temperatura, humedad, presión
- **SCADA systems**: Controladores, actuadores
- **Procesos industriales**: Líneas de producción

### Seguridad y Amenazas
- **Threat detection**: Análisis de tráfico sospechoso
- **Vulnerability scan**: Estados de seguridad
- **Incident response**: Métricas de respuesta

### Performance y Recursos
- **System monitoring**: CPU, RAM, disco, red
- **Application performance**: Latencia, throughput
- **Database metrics**: Queries, connections, cache

## 🎯 Ventajas del Template

### Consistencia Visual
- **Misma experiencia** en todos los dashboards
- **Aprendizaje único**: Los usuarios aprenden el layout una vez
- **Identidad de marca**: SmartCompute reconocible

### Flexibilidad Total
- **Cualquier tipo de datos**: Números, porcentajes, métricas
- **Cualquier dominio**: Red, IoT, seguridad, performance
- **Escalabilidad**: Desde 5 hasta 50 elementos

### Mantenibilidad
- **Código centralizado**: Un template, múltiples usos
- **Updates fáciles**: Cambios propagados automáticamente
- **Testing simplificado**: Validación en un solo lugar

### Profesionalismo
- **Estilo HMI industrial**: Familiar para técnicos
- **Legibilidad óptima**: Colores y espaciado calculados
- **Información densa**: Máximo contenido, mínimo ruido

## 📖 Guía de Implementación

### Paso 1: Importar Template
```python
from smartcompute_dashboard_template import SmartComputeDashboard
```

### Paso 2: Crear Dashboard
```python
dashboard = SmartComputeDashboard("MI TÍTULO PERSONALIZADO")
gs = dashboard.create_base_layout()
```

### Paso 3: Preparar Datos
```python
mi_data = {
    'labels': ['ITEM 1', 'ITEM 2', 'ITEM 3'],
    'values': [85, 67, 92],
    'colors': ['#00ff88', '#ffd700', '#ff6b6b']
}
```

### Paso 4: Crear Paneles
```python
dashboard.create_main_analysis_panel(gs, mi_data, 'MI ANÁLISIS', 'UNIDADES (%)')
# ... más paneles según necesidad
```

### Paso 5: Finalizar
```python
dashboard.add_footer("Mi contacto y información")
dashboard.finalize('mi_dashboard.png')
```

## 🔍 Esta es la base estándar para todos los dashboards SmartCompute

El template garantiza que sin importar qué tipo de análisis hagamos - desde protocolos de red hasta sensores industriales - siempre mantenemos la misma calidad visual profesional y la experiencia de usuario consistente.