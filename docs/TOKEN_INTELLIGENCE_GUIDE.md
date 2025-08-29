# SmartCompute Token Intelligence System

## 🎯 Descripción General

El **SmartCompute Token Intelligence System** es una solución completa para monitorear, optimizar y gestionar el uso de tokens y costos de IA en tiempo real. Diseñado específicamente para empresas que necesitan controlar gastos, optimizar recursos y obtener transparencia total sobre su uso de servicios de IA.

## ✨ Características Principales

### 📊 **Dashboard Inteligente y Personalizable**
- **Dashboard limpio**: 90% del espacio dedicado a información clave
- **Personalización discreta**: Panel de configuración oculto (ícono ⚙️)
- **Tiempo real**: Actualizaciones automáticas cada 30 segundos
- **Responsivo**: Funciona perfecto en desktop, tablet y móvil

### 🏷️ **Personalización Completa**
- **Etiquetas personalizables**: Cambia "Gastos" por "Inversión", etc.
- **Conversiones de unidades**: USD/EUR/MXN, °C/°F, ms/segundos
- **Multi-idioma**: Español, English, Português con un click
- **Seguridad**: Personalización separada de datos críticos

### 🔍 **Transparencia Total**
- **Indicadores de fuente**: Distingue entre datos reales y estimaciones
- **Precisión en tiempo real**: Muestra exactitud de estimaciones ML
- **Educación progresiva**: El usuario aprende sobre costos gradualmente
- **Alertas contextuales**: Solo notificaciones relevantes

### 💰 **Gestión de Presupuestos**
- **Presupuestos por proyecto**: Límites diarios y mensuales
- **Alertas inteligentes**: 75%, 90%, 100% del presupuesto
- **Proyecciones**: "Se agotará en X días" basado en tendencias
- **Optimización automática**: Sugerencias cuando se acerca el límite

### 📈 **Métricas y Analytics**
- **Prometheus integration**: Métricas estándar de la industria
- **Dashboards Grafana**: Compatible con infraestructura existente
- **Análisis por proveedor**: OpenAI, Anthropic, Google, Azure
- **ROI por proyecto**: Retorno de inversión detallado

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────┐
│           Frontend Dashboard                │
├─────────────────────────────────────────────┤
│  - HTML5/CSS3/JavaScript (Vanilla)         │
│  - Chart.js para visualizaciones           │  
│  - Responsive design                        │
│  - Personalización en tiempo real          │
└─────────────────────────────────────────────┘
                    ↕ HTTP/REST API
┌─────────────────────────────────────────────┐
│              FastAPI Backend               │
├─────────────────────────────────────────────┤
│  - Token tracking endpoints                │
│  - User preferences management             │
│  - Budget controls                         │
│  - Real-time metrics                       │
└─────────────────────────────────────────────┘
                    ↕ Python Services
┌─────────────────────────────────────────────┐
│            Core Services                    │
├─────────────────────────────────────────────┤
│  • TokenMonitoringService                  │
│    - Prometheus metrics                    │
│    - Cost calculation & estimation         │
│    - Budget alerts                         │
│    - ML learning for accuracy              │
│                                            │
│  • UserPreferencesManager                  │
│    - Secure label customization            │
│    - Unit conversions                      │
│    - Multi-language support                │
│    - Security validation                   │
└─────────────────────────────────────────────┘
                    ↕ External APIs
┌─────────────────────────────────────────────┐
│           AI Provider APIs                  │
├─────────────────────────────────────────────┤
│  ✅ OpenAI API (usage data)                │
│  ⚠️  Anthropic (ML estimation)              │
│  ✅ Google Cloud Billing API               │
│  ✅ Azure Cost Management API              │
└─────────────────────────────────────────────┘
```

## 🚀 Instalación y Configuración

### Requisitos Previos
```bash
# Python 3.8+
python3 --version

# Dependencias
pip3 install fastapi uvicorn prometheus-client psutil
```

### Instalación Rápida
```bash
# 1. Ir al directorio SmartCompute Industrial
cd /path/to/smartcompute/smartcompute_industrial

# 2. Ejecutar el script de inicio
./start_token_intelligence.sh

# 3. Abrir el dashboard
# http://127.0.0.1:8001
```

### Configuración Manual
```bash
# 1. Iniciar API
python3 token_api.py

# 2. Configurar presupuestos (opcional)
curl -X POST "http://127.0.0.1:8001/api/budget/set" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "mi_proyecto",
    "monthly_budget": 1000.0,
    "daily_budget": 50.0
  }'
```

## 📊 Usando el Dashboard

### 1. **Vista Principal**
- **Métricas clave**: Gastos, eficiencia, tokens, tiempo de respuesta
- **Gráficos**: Análisis de costos y distribución por modelo
- **Estado de proveedores**: Conectividad y precisión en tiempo real

### 2. **Personalización (ícono ⚙️)**
```javascript
// Cambiar etiquetas
"Gastos Hoy" → "Inversión Diaria"
"Eficiencia" → "Rendimiento"
"Tokens" → "Unidades"

// Cambiar unidades  
USD → EUR → MXN
°F → °C
ms → segundos

// Cambiar idioma
Español → English → Português
```

### 3. **Alertas Inteligentes**
```
🟡 ADVERTENCIA: 75% del presupuesto diario usado
🔴 CRÍTICO: 90% del presupuesto alcanzado
⚠️ MODO APRENDIZAJE: Estimando costos para Anthropic (94% ± 3% precisión)
✅ DATOS REALES: Conectado con OpenAI API
```

## 🔧 Integración con APIs

### OpenAI (Datos Reales)
```python
# Tracking automático cuando tienes API key
import openai
from token_monitoring import token_service

# El sistema detecta automáticamente el uso y obtiene costos reales
response = openai.ChatCompletion.create(...)
# → Costos exactos mostrados en dashboard
```

### Anthropic (Estimación ML)
```python
# Estimación inteligente que mejora con uso
usage = token_service.track_token_usage(
    provider="anthropic",
    model="claude-3-sonnet", 
    tokens_input=150,
    tokens_output=300,
    duration=1.2
)
# → Estimación 94% precisa, mejora automáticamente
```

## 📈 Métricas Prometheus

### Métricas Disponibles
```promql
# Token consumption
smartcompute_tokens_consumed_total{provider="openai", model="gpt-4"}

# Cost tracking  
smartcompute_tokens_cost_usd_total{provider="openai", project_id="production"}

# Budget utilization
smartcompute_budget_utilization_percent{project_id="development", budget_type="daily"}

# Estimation accuracy
smartcompute_estimation_accuracy_score{provider="anthropic", model="claude-3-sonnet"}

# Optimization savings
smartcompute_tokens_saved_optimization_total{optimization_type="model_switch"}
```

### Grafana Dashboard
```json
{
  "dashboard": {
    "title": "SmartCompute Token Intelligence",
    "panels": [
      {
        "title": "Costo por Hora",
        "targets": ["rate(smartcompute_tokens_cost_usd_total[1h])"]
      },
      {
        "title": "Uso del Presupuesto", 
        "targets": ["smartcompute_budget_utilization_percent"]
      }
    ]
  }
}
```

## 💡 Casos de Uso Empresariales

### 1. **Control de Costos Departamental**
```python
# Configurar presupuestos por departamento
departments = {
    "desarrollo": {"monthly": 2000, "daily": 100},
    "marketing": {"monthly": 1500, "daily": 75}, 
    "research": {"monthly": 5000, "daily": 250}
}

for dept, budget in departments.items():
    token_service.set_project_budget(dept, budget["monthly"], budget["daily"])
```

### 2. **Optimización Automática**
```python
# El sistema sugiere automáticamente:
# - Cambiar a GPT-3.5 para tareas simples (ahorro: $8.50/día)
# - Reducir longitud de respuestas (reducción tokens: 25%)
# - Cachear respuestas frecuentes (ahorro: 40%)
# - Batch operations (eficiencia: +30%)
```

### 3. **Compliance y Auditoría**
```python
# Exportar datos para auditoría
token_service.export_usage_data(
    filepath="audit_2024_Q1.json",
    project_id="production",
    days=90
)

# Datos incluyen:
# - Uso detallado por usuario/proyecto
# - Costos reales vs estimados
# - Decisiones de optimización
# - Alertas y respuestas
```

## 🔒 Seguridad y Privacidad

### Separación de Capas
- **Capa de datos**: Inmutable, contiene lógica crítica
- **Capa de presentación**: Personalizable, validación estricta
- **Validación**: Previene XSS, injection, caracteres maliciosos

### Configuración Segura
```python
# Etiquetas permitidas: solo caracteres alphanuméricas y espacios
label_pattern = r'^[a-zA-Z0-9áéíóúñüÁÉÍÓÚÑÜ\s\-_.:()]+$'

# Keywords prohibidas
forbidden = ['script', 'javascript', 'eval', 'exec', ...]

# Longitud máxima
max_label_length = 50
```

## 🎛️ API Reference

### Endpoints Principales

#### Dashboard Metrics
```http
GET /api/dashboard/metrics
Headers: X-User-ID: usuario123

Response:
{
  "daily_cost": 24.50,
  "efficiency": 94.0,
  "token_count": 1240,
  "response_time": 1.2,
  "budget_utilization": 65.0
}
```

#### Track Token Usage
```http
POST /api/tokens/track
Content-Type: application/json

{
  "provider": "openai",
  "model": "gpt-4",
  "operation_type": "chat", 
  "tokens_input": 150,
  "tokens_output": 300,
  "duration_seconds": 1.2,
  "project_id": "production"
}
```

#### Set Custom Label
```http
POST /api/preferences/label
Headers: X-User-ID: usuario123
Content-Type: application/json

{
  "key": "cost",
  "value": "Inversión Diaria",
  "preference_type": "label"
}
```

#### Budget Management
```http
POST /api/budget/set
Content-Type: application/json

{
  "project_id": "desarrollo",
  "monthly_budget": 1000.0,
  "daily_budget": 50.0
}
```

## 🔄 Roadmap y Mejoras Futuras

### V1.1 (Próximo Release)
- [ ] Integración directa con más APIs (Cohere, Hugging Face)
- [ ] Dashboard móvil nativo
- [ ] Alertas por email/Slack/Teams
- [ ] Análisis predictivo mejorado

### V1.2 (Mediano Plazo) 
- [ ] Multi-tenancy empresarial
- [ ] SSO integration (SAML, OAuth)
- [ ] Reportes automatizados PDF
- [ ] A/B testing para optimización

### V2.0 (Largo Plazo)
- [ ] AI-powered optimization recommendations
- [ ] Carbon footprint tracking
- [ ] Cost allocation algorithms
- [ ] Enterprise audit trails

## 📄 Licencia

Este proyecto está bajo la licencia especificada en el repositorio principal de SmartCompute.

---

*SmartCompute Token Intelligence System - Optimización inteligente de recursos de IA*