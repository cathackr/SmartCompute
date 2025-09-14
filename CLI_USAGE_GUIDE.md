# SmartCompute CLI - Guía de Uso Completa

## 🚀 Instalación Rápida

```bash
# Desde el directorio SmartCompute
./install_smartcompute.sh

# O instalación manual
chmod +x smartcompute
export PATH="$(pwd):$PATH"
```

## 📋 Comandos Disponibles

### Análisis de Infraestructura Completa

```bash
# Análisis completo con CLI y HTML
smartcompute scan infrastructure

# Solo CLI
smartcompute scan infrastructure --output cli

# Solo HTML dashboard
smartcompute scan infrastructure --output html
```

**Detecta y analiza:**
- 🐳 **Docker**: Contenedores, imágenes, estados
- 🏢 **Active Directory**: Dominios, usuarios, grupos (Windows/Linux)
- 🖥️ **Proxmox VE**: Clusters, nodos, VMs
- 👥 **Grupos de trabajo**: Servicios, usuarios, procesos
- 📡 **Red**: Interfaces, conexiones, puertos abiertos
- 💾 **Sistema**: CPU, RAM, disco, uptime

### Análisis de Red OSI

```bash
# Análisis completo 7 capas OSI
smartcompute scan network --osi-all

# Capas específicas (Red + Transporte)
smartcompute scan network --layers 3,4

# Con duración personalizada
smartcompute scan network --duration 60
```

### Análisis de APIs y Aplicaciones (Capa 7)

```bash
# Análisis de Layer 7 - APIs
smartcompute scan apis

# Puerto específico
smartcompute scan apis --port 443
```

**Analiza:**
- 🔌 **Protocolos**: REST, GraphQL, WebSocket, gRPC
- 💻 **Lenguajes**: Python, JavaScript, Java, Go, Rust
- 📊 **Performance**: Requests/sec, latencia, errores
- 🌐 **Endpoints**: URLs más utilizadas

### Monitoreo IoT

```bash
# Sensores IoT completo
smartcompute scan iot

# Sensores específicos
smartcompute scan iot --sensors temp,humidity
```

**Monitorea:**
- 🌡️ **Temperatura**: Múltiples sensores en tiempo real
- 💧 **Humedad**: Niveles ambientales
- 📊 **Presión atmosférica**
- 🔋 **Estado de baterías**
- 📡 **Conectividad**: WiFi, Zigbee, LoRA

### Docker Específico

```bash
# Solo análisis Docker
smartcompute scan docker --containers
```

## 🎨 Formatos de Salida

### CLI Output (Terminal)
```bash
============================================================
🚀 SMARTCOMPUTE INFRASTRUCTURE ANALYSIS RESULTS
============================================================
📊 TIMESTAMP: 2025-09-14T10:37:01
🖥️ HOSTNAME: production-server
💻 PLATFORM: Linux

🐳 DOCKER ANALYSIS:
   Status: RUNNING
   Containers: 12 total, 10 running
   Images: 8 available

🏢 ACTIVE DIRECTORY:
   Status: LINUX_INTEGRATION
   SSSD: active

🖥️ PROXMOX VE:
   Status: DETECTED
   VMs: 15 detected
============================================================
```

### HTML Dashboard (Gráfico)
- **Formato HMI industrial** estandarizado
- **Gráficos interactivos** con Chart.js
- **Tiempo real** - actualizaciones automáticas
- **Responsive design** - funciona en mobile
- **Datos técnicos detallados** en formato CLI

## 🔧 Opciones Avanzadas

### Personalización de Output

```bash
# Solo mostrar en CLI sin generar HTML
smartcompute scan infrastructure --output cli

# Solo generar HTML sin mostrar CLI
smartcompute scan infrastructure --output html

# Ambos (default)
smartcompute scan infrastructure --output both
```

### Duración de Análisis

```bash
# Análisis de 60 segundos
smartcompute scan network --duration 60

# Análisis rápido de 10 segundos
smartcompute scan network --duration 10
```

### Formato de Dashboard

```bash
# Formato HMI industrial (default)
smartcompute scan infrastructure --format hmi

# Formato estándar
smartcompute scan infrastructure --format standard
```

## 📊 Tipos de Análisis Disponibles

### 1. Infrastructure Analysis
**Comando**: `smartcompute scan infrastructure`

**Detecta**:
- Servicios Docker corriendo
- Integración Active Directory
- Infraestructura Proxmox
- Grupos de trabajo Windows/Linux
- Estado de servicios del sistema
- Conexiones de red activas

### 2. Network Analysis
**Comando**: `smartcompute scan network`

**Analiza**:
- 7 capas del modelo OSI
- Protocolos TCP/UDP por puerto
- Estados de conexión
- Throughput y latencia
- Routing tables
- ARP entries

### 3. API Analysis
**Comando**: `smartcompute scan apis`

**Monitorea**:
- Endpoints REST/GraphQL
- Performance de APIs
- Error rates y status codes
- Lenguajes de programación detectados
- Microservicios activos

### 4. IoT Monitoring
**Comando**: `smartcompute scan iot`

**Supervisa**:
- Sensores ambientales
- Conectividad de dispositivos
- Consumo energético
- Alertas y thresholds
- Estado de red IoT

## 🎯 Ejemplos Prácticos

### Diagnóstico Rápido del Servidor
```bash
# Ver estado general en 30 segundos
smartcompute scan infrastructure --output cli
```

### Monitoreo de Aplicaciones Web
```bash
# Análisis de APIs y servicios web
smartcompute scan apis --port 443
smartcompute scan network --layers 7
```

### Diagnóstico de Red
```bash
# Análisis completo OSI + infrastructura
smartcompute scan network --osi-all
smartcompute scan infrastructure
```

### Monitoreo Industrial
```bash
# IoT + infrastructure para entorno industrial
smartcompute scan iot --sensors all
smartcompute scan infrastructure --format hmi
```

## 📈 Dashboard Features

### Tiempo Real
- **CPU/Memory usage**: Actualización continua
- **Network throughput**: Gráficos de línea
- **Sensor readings**: Para sistemas IoT
- **API performance**: Requests/sec, latencia

### Información Técnica
- **Formato CLI estructurado** en el dashboard
- **Dos columnas organizadas** por categoría
- **Datos específicos** según el tipo de análisis
- **Métricas clave** destacadas

### Diseño Profesional
- **Colores HMI** - Verde/Amarillo/Rojo para estados
- **Espaciado perfecto** - Sin superposiciones
- **Tipografía monospace** - Fácil lectura técnica
- **Layout consistente** - Mismo formato siempre

## 🆘 Troubleshooting

### Comando no encontrado
```bash
# Verificar instalación
which smartcompute

# Reinstalar si es necesario
./install_smartcompute.sh
```

### Permisos insuficientes
```bash
# Para análisis de servicios del sistema
sudo smartcompute scan infrastructure

# Para análisis de red en puertos privilegiados
sudo smartcompute scan network
```

### Python dependencies
```bash
# Instalar dependencias
pip install psutil matplotlib

# O usar el entorno virtual
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 🎯 SmartCompute CLI - Una línea de comando, análisis completo de infraestructura

El objetivo es que con un solo comando puedas obtener:
1. **CLI output inmediato** para diagnóstico rápido
2. **HTML dashboard profesional** para análisis detallado
3. **Datos técnicos completos** organizados y legibles
4. **Formato estandarizado** sin importar el tipo de análisis