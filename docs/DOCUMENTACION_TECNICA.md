# 🧠 SmartCompute Documentación Técnica

<div align="center">
  <img src="../assets/smartcompute_hmi_logo.png" alt="SmartCompute Logo" width="200">
  
  **Versión 1.0.0-beta** | **Plataforma de Ciberseguridad Empresarial**
  
  [🇪🇸 Español](#) | [🇺🇸 English](TECHNICAL_DOCUMENTATION.md) | [🚀 Inicio Rápido](GUIA_INICIO_RAPIDO.md) | [💼 Empresarial](GUIA_EMPRESARIAL.md)
</div>

---

## 📋 Tabla de Contenidos

- [🎯 Descripción de la Plataforma](#-descripción-de-la-plataforma)
- [🏠 SmartCompute Starter](#-smartcompute-starter)
- [📱 Móviles y Google Colab](#-móviles-y-google-colab)  
- [💻 Instalación en Escritorio](#-instalación-en-escritorio)
- [🏢 Edición Empresarial](#-edición-empresarial)
- [🏭 Edición Industrial](#-edición-industrial)
- [🔧 Referencia de APIs](#-referencia-de-apis)
- [🚀 Opciones de Despliegue](#-opciones-de-despliegue)
- [🛠️ Solución de Problemas](#️-solución-de-problemas)

---

## 🎯 Descripción de la Plataforma

SmartCompute es una plataforma integral de monitoreo de ciberseguridad con capacidades de **detección de amenazas impulsada por IA** y **optimización de rendimiento**.

### 🌟 Características Principales

| Característica | Starter | Empresarial | Industrial |
|----------------|---------|-------------|------------|
| **Monitoreo en Tiempo Real** | ✅ Básico | ✅ Avanzado | ✅ Protocolos Industriales |
| **Detección IA de Amenazas** | ✅ Limitado | ✅ Suite IA Completa | ✅ Específico Industrial |
| **Análisis de Rendimiento** | ✅ Básico | ✅ Avanzado | ✅ Convergencia OT/IT |
| **Acceso API** | ❌ | ✅ APIs RESTful | ✅ APIs Industriales |
| **Dashboard** | ✅ Web | ✅ Personalizable | ✅ Integración HMI |
| **Nivel de Soporte** | Comunidad | Profesional | Premium + Consultoría |

---

## 🏠 SmartCompute Starter

**Versión gratuita para uso personal y pequeñas empresas**

### ✨ Características Incluidas

- **🔍 Monitoreo Básico**: Uso de CPU, memoria, red
- **🤖 Detección IA Simple**: Patrones de amenazas comunes  
- **📊 Dashboard Web**: Visualización de métricas en tiempo real
- **📱 Soporte Google Colab**: Acceso móvil universal
- **💾 Almacenamiento Local**: Base de datos SQLite

### 🚀 Instalación Rápida

#### Opción 1: Instalación Local
```bash
git clone https://github.com/cathackr/SmartCompute.git
cd SmartCompute
pip install -r requirements-core.txt
python main.py --starter
```

#### Opción 2: Google Colab (Recomendado para Móviles)
```python
# Abrir: https://colab.research.google.com
!git clone https://github.com/cathackr/SmartCompute.git
%cd SmartCompute
!pip install -r requirements-core.txt
!python examples/colab_interactive_demo.py
```

### 🎯 Casos de Uso

- **Seguridad Personal**: Monitoreo de red doméstica
- **Pequeña Empresa**: Detección básica de amenazas para <10 dispositivos
- **Aprendizaje**: Entrenamiento en ciberseguridad y educación
- **Desarrollo**: Pruebas y conceptos de prueba

---

## 📱 Móviles y Google Colab

**Acceso universal desde cualquier dispositivo con navegador web**

### 🌟 Ventajas de Google Colab

| Beneficio | Descripción |
|-----------|-------------|
| **🌐 Universal** | Funciona en iPhone, Android, tablets, PCs |
| **⚡ Sin Instalación** | Solo abrir un navegador web |
| **🚀 GPU Gratuita** | Google proporciona aceleración GPU gratis |
| **💾 Almacenamiento en Nube** | Se guarda automáticamente en Google Drive |
| **📊 Visualizaciones Enriquecidas** | Gráficos y tablas interactivos |

### 🎮 Características del Demo Interactivo

- **Alertas de Amenazas en Tiempo Real**: Niveles de severidad codificados por colores
- **Gráficos de Rendimiento en Vivo**: Métricas de CPU, memoria, red
- **Dashboards Animados**: Interfaz optimizada para móviles
- **Clasificación de Amenazas**: Categorización automática
- **Capacidades de Exportación**: Reportes JSON y visualizaciones

### 🔧 Uso Móvil Avanzado

Para usuarios avanzados que quieren instalación móvil local:

#### Opciones Android
```bash
# Termux (Usuarios avanzados)
pkg install python git
git clone https://github.com/cathackr/SmartCompute.git
cd SmartCompute && python main.py --starter --mobile

# QPython 3L (Amigable para usuarios)
# Instalar QPython 3L desde Google Play
# Importar proyecto SmartCompute
# Ejecutar versión starter
```

---

## 💻 Instalación en Escritorio

**Instalación completa para Windows, macOS y Linux**

### 🖥️ Requisitos del Sistema

| Componente | Mínimo | Recomendado |
|------------|---------|-------------|
| **SO** | Windows 10, macOS 11, Ubuntu 20.04 | Versiones más recientes |
| **Python** | 3.8+ | 3.11+ |
| **RAM** | 4GB | 8GB+ |
| **Almacenamiento** | 1GB | 5GB+ |
| **Red** | 100 Mbps | 1 Gbps+ |

### 🐧 Instalación Linux

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install python3 python3-pip git
git clone https://github.com/cathackr/SmartCompute.git
cd SmartCompute
pip3 install -r requirements.txt
python3 main.py

# CentOS/RHEL
sudo yum install python3 python3-pip git
# Seguir los mismos pasos que Ubuntu

# Arch Linux
sudo pacman -S python python-pip git
# Seguir los mismos pasos que Ubuntu
```

### 🪟 Instalación Windows

```powershell
# Usando Windows Package Manager
winget install Python.Python.3.11
winget install Git.Git

# Clonar y configurar
git clone https://github.com/cathackr/SmartCompute.git
cd SmartCompute
pip install -r requirements.txt
python main.py
```

### 🍎 Instalación macOS

```bash
# Usando Homebrew
brew install python git
git clone https://github.com/cathackr/SmartCompute.git
cd SmartCompute
pip3 install -r requirements.txt
python3 main.py
```

---

## 🏢 Edición Empresarial

**Características avanzadas para empresas medianas a grandes**

### 🌟 Características Empresariales

| Categoría | Capacidades |
|-----------|-------------|
| **🤖 Motor IA** | Modelos ML avanzados, análisis de comportamiento, detección zero-day |
| **📊 Analíticas** | Dashboards personalizados, reportes avanzados, análisis de tendencias |
| **🔗 Integraciones** | SIEM, SOAR, sistemas de tickets, plataformas en la nube |
| **🛡️ Seguridad** | Multi-inquilino, SSO, acceso basado en roles, logs de auditoría |
| **📈 Escalabilidad** | Despliegue multi-nodo, balanceador de carga, auto-escalado |

### 🚀 Instalación Empresarial

```bash
# Instalación empresarial
git clone https://github.com/cathackr/SmartCompute.git
cd SmartCompute

# Instalar dependencias empresariales
pip install -r requirements.txt
pip install -r requirements-enterprise.txt

# Configurar base de datos empresarial
python -m app.core.database --setup --enterprise

# Iniciar servicios empresariales
python main.py --enterprise --api
```

### 🎯 Casos de Uso Empresariales

- **Seguridad Corporativa**: Monitoreo de 100-10,000 endpoints
- **Cumplimiento**: Requisitos SOC 2, ISO 27001, HIPAA  
- **Multi-ubicación**: Monitoreo centralizado en múltiples oficinas
- **Integración**: Conectar con stack de seguridad existente

---

## 🏭 Edición Industrial

**Especializada para Sistemas de Control Industrial e Infraestructura Crítica**

### 🏗️ Características Industriales

| Soporte de Protocolo | Caso de Uso | Capacidades de Monitoreo |
|---------------------|-------------|-------------------------|
| **Modbus TCP/RTU** | Sistemas SCADA | Monitoreo de comunicación en tiempo real |
| **Profinet** | Ethernet Industrial | Salud y rendimiento de dispositivos |
| **OPC UA** | Industria 4.0 | Monitoreo de intercambio seguro de datos |
| **EtherNet/IP** | PLCs Allen-Bradley | Análisis de topología de red |
| **DNP3** | Servicios eléctricos | Protección de infraestructura crítica |

### 🚀 Instalación Industrial

```bash
# La edición industrial requiere privilegios de red
git clone https://github.com/cathackr/SmartCompute.git
cd SmartCompute/smartcompute_industrial

# Instalar dependencias industriales
sudo pip install -r requirements_industrial.txt

# Iniciar monitoreo industrial
sudo ./start_network_intelligence.sh
# Acceso: http://127.0.0.1:8002
```

### 🎯 Casos de Uso Industriales

- **Plantas Manufactureras**: Monitoreo de líneas de producción
- **Generación de Energía**: Protección de infraestructura crítica
- **Tratamiento de Agua**: Seguridad de sistemas SCADA
- **Petróleo y Gas**: Monitoreo de tuberías y refinerías
- **Edificios Inteligentes**: Sistemas de automatización de edificios

---

## 🔧 Referencia de APIs

### 🌐 Endpoints API RESTful

#### Autenticación
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "contraseña_segura"
}

Respuesta: {
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### Endpoints de Monitoreo
```http
# Obtener estado del sistema
GET /api/v1/monitoring/status
Authorization: Bearer {token}

# Obtener alertas de amenazas
GET /api/v1/security/alerts?severity=high&limit=50

# Obtener métricas de rendimiento
GET /api/v1/metrics/performance?timeframe=1h

# Topología de red industrial
GET /api/v1/industrial/topology
```

---

## 🚀 Opciones de Despliegue

### ☁️ Despliegue en la Nube

#### Despliegue AWS
```bash
# Usando AWS CDK
npm install -g aws-cdk
cdk init smartcompute --language=python
cdk deploy SmartComputeStack
```

#### Despliegue Azure
```bash
# Usando Azure CLI
az group create --name smartcompute-rg --location eastus
az container create \
    --resource-group smartcompute-rg \
    --name smartcompute \
    --image smartcompute/enterprise:latest \
    --ports 8000
```

### 🏢 Despliegue On-Premises

```bash
# Configuración de alta disponibilidad
./scripts/deploy-ha.sh --nodes 3 --database postgresql --storage nfs

# Despliegue de nodo único
./scripts/deploy-single.sh --database sqlite --storage local

# Despliegue industrial con aislamiento de red
./scripts/deploy-industrial.sh --network-isolation --air-gapped
```

---

## 🛠️ Solución de Problemas

### 🚨 Problemas Comunes

#### Problemas de Instalación
```bash
# Problemas de versión de Python
python --version  # Debería ser 3.8+
pip install --upgrade pip

# Errores de permisos
sudo chown -R $USER:$USER ~/.local/
pip install --user -r requirements.txt
```

#### Problemas de Rendimiento
```bash
# Verificar recursos del sistema
htop
df -h
free -m

# Monitorear procesos de SmartCompute
ps aux | grep smartcompute
netstat -tulpn | grep 8000
```

### 📞 Canales de Soporte

| Tipo de Problema | Canal de Soporte | Tiempo de Respuesta |
|------------------|------------------|---------------------|
| **Starter** | GitHub Issues | Impulsado por la comunidad |
| **Empresarial** | Soporte Profesional | 24-48 horas |
| **Industrial** | Soporte Premium + Consultoría | 4-8 horas |
| **Crítico** | Línea de Emergencia | 1 hora |

---

<div align="center">

**🎯 ¿Listo para asegurar tu infraestructura?**

[🚀 Inicio Rápido](GUIA_INICIO_RAPIDO.md) | [💼 Guía Empresarial](GUIA_EMPRESARIAL.md) | [📧 Contactar Soporte](mailto:ggwre04p0@mozmail.com)

---

© 2024 SmartCompute. Monitoreo profesional de ciberseguridad para la empresa moderna.

</div>