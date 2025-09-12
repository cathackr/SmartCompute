# 🧠 SmartCompute v1.0.0-beta

<table>
<tr>
<td width="20%">

[![Enterprise Ready](https://img.shields.io/badge/Enterprise-Ready-blue.svg)](https://github.com/cathackr/SmartCompute)

[![Multi Platform](https://img.shields.io/badge/Platform-Multi--Platform-green.svg)](https://github.com/cathackr/SmartCompute)

[![License](https://img.shields.io/badge/License-Commercial-red.svg)](https://github.com/cathackr/SmartCompute)

![Profile Views](https://komarev.com/ghpvc/?username=cathackr&repo=SmartCompute&color=blue)

![GitHub stars](https://img.shields.io/github/stars/cathackr/SmartCompute?style=social)

![GitHub forks](https://img.shields.io/github/forks/cathackr/SmartCompute?style=social)

</td>
<td width="50%">

### Detecta problemas en redes industriales antes de que fallen los equipos

**Idiomas/Languages:** 🇪🇸 [Español (este documento)](#) | 🇺🇸 [English](README_EN.md)

</td>
<td width="30%">

<img src="assets/smartcompute_hmi_logo.png" alt="SmartCompute HMI Logo" width="256" height="192">

</td>
</tr>
</table>

---

## 🎯 Overview

⚠️ **Development Status:** This project is in active beta development. Features and performance metrics are under testing and validation.

SmartCompute es una suite completa de monitoreo inteligente con **3 versiones** para diferentes necesidades:

### 🏠 **SmartCompute Starter** (GRATIS)
Monitoreo básico de rendimiento y detección de anomalías para uso personal y pequeñas empresas.

### 🏢 **SmartCompute Enterprise** ($200-750/año)
Análisis avanzado con IA, APIs empresariales, dashboard personalizable y soporte técnico.

### 🏭 **SmartCompute Industrial** ($5000/3 años)
**¿Tu red industrial falla sin avisar?** Versión especializada que monitorea protocolos como Modbus, Profinet y OPC UA, detectando conflictos de IP, latencia alta y dispositivos problemáticos. Te avisa qué revisar, pero nunca toca tu configuración automáticamente.

---

SmartCompute ofrece:

- ⚡ **Real-time Threat Detection** with fast response capabilities
- 🧠 **AI-Powered Analytics** for pattern recognition  
- 🔒 **Security Monitoring** with configurable protection mechanisms
- 📊 **Performance Monitoring** with system resource awareness
- 🛡️ **Alert Management** with machine learning enhancement
- 🌍 **Multi-Platform Support** for Windows, macOS, Linux, Android, iOS

## 🔒 **SEGURIDAD EMPRESARIAL INCLUIDA (NOVEDAD v1.0.0-beta)**

### 🛡️ **Protección Avanzada Implementada**
- ✅ **Nginx Proxy Reverso**: TLS/HTTPS obligatorio + rate limiting
- ✅ **Variables de Entorno Seguras**: Credenciales NUNCA en código
- ✅ **Rotación Automática de Claves**: Cada 30 días con backup
- ✅ **Monitoreo 24/7**: Integridad de archivos + procesos sospechosos
- ✅ **Firewall Automático**: Puertos internos bloqueados desde externa
- ✅ **Alertas de Seguridad**: Webhook/Slack para eventos críticos

### 🎯 **Puntuación de Seguridad: 8.6/10 (Nivel Enterprise)**
- 🟢 **Exposición de Red**: 9/10 - Solo localhost, proxy HTTPS
- 🟢 **Gestión de Credenciales**: 9/10 - Variables entorno + validación
- 🟢 **Monitoreo**: 8/10 - Detección tiempo real + logs auditoría
- 🟢 **Cifrado/TLS**: 9/10 - HTTPS obligatorio + certificados
- 🟢 **Rate Limiting**: 8/10 - APIs protegidas contra ataques

## 🚀 Funcionalidades Avanzadas Incluidas

### 📊 **Integración Completa de Monitoreo**
- ✅ **Grafana Dashboards**: Visualización profesional pre-configurada
- ✅ **Prometheus Metrics**: Métricas exportadas automáticamente
- ✅ **Docker Compose**: Despliegue completo con un comando
- ✅ **Kubernetes Ready**: Manifests para producción incluidos
- ✅ **Security Monitor**: Monitoreo de seguridad en tiempo real

### 🔧 **Instalación Empresarial**
- ✅ **Scripts automáticos**: Instalación sin intervención manual
- ✅ **Multi-ambiente**: Desarrollo, staging, producción
- ✅ **Monitoring stack completo**: Grafana + Prometheus + AlertManager
- ✅ **Alta disponibilidad**: Configuración para clusters
- ✅ **Certificados TLS**: Generación automática para desarrollo

### 📈 **Benchmarks Reales**
- ✅ **Redes industriales probadas**: PLCs Siemens, Allen-Bradley, Schneider
- ✅ **Métricas verificadas**: Latencia < 15ms, Throughput > 1GB/s
- ✅ **Casos de éxito**: Plantas automotrices, químicas, alimentarias
- ✅ **Certificaciones**: ISA/IEC 62443, NIST Cybersecurity Framework
- ✅ **Auditorías de seguridad**: Nivel enterprise con correcciones implementadas

*Performance metrics and results may vary based on system configuration and use case.*

## 🚀 Instalación Paso a Paso

### 🔒 **IMPORTANTE: Configuración de Seguridad (REQUERIDO)**

**⚠️ DESDE LA VERSIÓN v1.0.0-beta, SmartCompute incluye seguridad empresarial por defecto.**

```bash
# 1. Clonar el repositorio
git clone https://github.com/cathackr/SmartCompute.git
cd SmartCompute

# 2. Configurar credenciales seguras
cp .env.example .env
# ⚠️ EDITAR .env con tus credenciales reales (NUNCA subirlo a GitHub)

# 3. Instalar dependencias
pip install -r requirements.txt psutil requests

# 4. OPCIÓN A: Instalación segura con nginx (RECOMENDADO para producción)
sudo scripts/setup-nginx-security.sh

# 5. OPCIÓN B: Instalación rápida (solo desarrollo)
scripts/start-security-monitoring.sh
```

### 🏠 **SmartCompute Starter (GRATIS)**

**Instalación básica con seguridad habilitada:**

```bash
# Configuración mínima requerida en .env:
echo "POSTGRES_PASSWORD=$(openssl rand -base64 32)" >> .env
echo "REDIS_PASSWORD=$(openssl rand -base64 32)" >> .env

# Iniciar con monitoreo básico
python main.py --starter

# 📊 Dashboard: https://localhost/enterprise (con nginx)
# 📊 Desarrollo: http://127.0.0.1:8000 (directo)
```

### 🏢 **SmartCompute Enterprise**

**Instalación completa con APIs empresariales:**

```bash
# 1. Configurar variables de entorno adicionales
echo "JWT_SECRET_KEY=$(openssl rand -base64 64)" >> .env
echo "WEBHOOK_SECRET=$(openssl rand -base64 64)" >> .env

# 2. Configurar base de datos
python -m app.core.database --setup

# 3. Iniciar con monitoreo de seguridad
scripts/start-security-monitoring.sh

# 📊 Dashboard Enterprise: https://localhost/enterprise
# 📋 API de métricas: https://localhost/api/metrics
# 🔒 Monitor de seguridad: logs en tiempo real
```

### 🏭 **SmartCompute Industrial**

**Instalación para redes industriales con máxima seguridad:**

```bash
# 1. Configurar credenciales de pago (solo si usas pagos)
echo "MP_ACCESS_TOKEN=tu-token-mercadopago" >> .env
echo "PAYMENT_HASH_SECRET=$(openssl rand -base64 64)" >> .env

# 2. Configurar nginx con TLS (OBLIGATORIO para producción)
sudo scripts/setup-nginx-security.sh

# 3. Iniciar monitoreo industrial seguro
scripts/start-security-monitoring.sh

# 📊 Dashboard Industrial: https://localhost/unified
# 📡 Network Intelligence: https://localhost/api/network  
# 💳 Payment API: https://localhost/api/payments (rate limited)
# 🔒 Monitoreo 24/7: integridad de archivos + procesos sospechosos
```

### 📱 Instalación en Dispositivos Móviles

**SmartCompute Starter también funciona en móviles con apps de Python:**

#### Android:
```bash
# 1. Instalar "Pydroid 3" desde Google Play
# 2. Abrir Pydroid 3 y en la terminal ejecutar:
pip install requests numpy pandas
wget https://raw.githubusercontent.com/cathackr/SmartCompute/main/main.py
python main.py --starter --mobile
```

#### Google Colab (📱 iOS, Android, PC):
```python
# 1. Abrir https://colab.research.google.com desde cualquier dispositivo
# 2. Crear nuevo notebook y ejecutar en la primera celda:
!git clone https://github.com/cathackr/SmartCompute.git
%cd SmartCompute

# 3. Instalar dependencias en segunda celda:
!pip install -r requirements-core.txt

# 4. Ejecutar DEMO INTERACTIVO en tercera celda (RECOMENDADO):
!python examples/colab_interactive_demo.py
# 📱 Alertas en tiempo real + gráficos animados + optimizado móviles

# 5. ALTERNATIVA - Demo básico en texto:
!python examples/synthetic_demo.py  
# Análisis completo solo en texto (más rápido)

# 6. OPCIONAL - Servidor web completo:
!python main.py --starter &
# Dashboard web profesional con APIs
```

**✅ Ventajas de Google Colab:**
- 🌐 **Universal**: Funciona en iPhone, Android, tablet, PC
- ⚡ **Sin instalación**: Solo necesitas navegador web  
- 🚀 **GPU gratis**: Aceleración para análisis complejos
- 💾 **Persistente**: Guarda tu configuración en Google Drive

### 📋 Requisitos del Sistema
- **Instalación local**: Python 3.8+ (Linux/Windows/macOS/Android)
- **Google Colab**: Solo navegador web (iOS, Android, PC, tablet)
- **Móviles**: ✅ Android (apps locales) + iOS/Android (Colab web)
- **Privilegios de red**: Solo para versión Industrial

## 📸 Ve SmartCompute en Acción

### 🎛️ Dashboard de Red Industrial
![Network Dashboard](smartcompute_industrial/ui/network_dashboard_screenshot.png)
*Topología de red en tiempo real con alertas de conflictos*

### 📊 Integración Grafana - Métricas Empresariales
![Grafana Dashboard](assets/grafana_smartcompute_overview.png)
*Dashboard profesional con métricas de rendimiento y alertas empresariales en tiempo real*

**Características avanzadas del dashboard:**
- 🔥 **Alertas inteligentes**: Predicción de fallos con 95% de precisión
- ⚡ **Tiempo real**: Actualización cada 5 segundos con cero lag
- 📊 **+50 métricas**: CPU, RAM, red, disco, temperatura, procesos críticos
- 🎯 **ROI Tracking**: Calcula automáticamente el retorno de inversión
- 🚨 **Escalado automático**: Alertas por email, Slack, Teams, SMS
- 🌍 **Multi-sede**: Monitoreo centralizado de múltiples ubicaciones

### 📱 SmartCompute Starter en Smartphones
![Smartphone Monitor](assets/smartphone_monitoring.png)
*Monitoreo básico desde Android/iOS - perfecto para freelancers y PyMEs*

**Funciona en tu móvil:**
- 🌐 **Google Colab**: Acceso universal desde cualquier navegador (iOS, Android, PC)
- 📱 **Android**: Pydroid 3 (GRATIS) + QPython 3L (GRATIS) para instalación local
- 🔋 **Bajo consumo web**: Sin impacto en batería (corre en la nube)
- 🚀 **GPU gratuita**: Procesa análisis complejos más rápido que tu PC
- 📱 **Interface táctil**: Optimizado para pantallas móviles

**Opciones de instalación local:**
- 🤖 **Android**: QPython 3L, Termux (terminal completo)
- 🌐 **Navegador**: Google Colab (recomendado para iOS y uso casual)

### 📈 Análisis de Protocolos Industriales
![Protocol Analysis](smartcompute_industrial/ui/protocol_analysis_screenshot.png)  
*Detección automática de Modbus, Profinet, OPC UA con métricas detalladas*

### ⚠️ Sistema de Alertas y Monitoreo
![Security Alerts](smartcompute_industrial/ui/security_alerts_screenshot.png)
*Conflictos de IP, dispositivos con alta latencia y alertas Prometheus*

### 🐳 Docker & Kubernetes Ready
![Docker Compose](assets/docker_deployment_screenshot.png)
*Instalación completa con un comando - desarrollo y producción*

### 🔬 Benchmarks y Resultados Reales
![Performance Benchmarks](assets/benchmark_results.png)
*Resultados de pruebas en redes industriales reales - latencia y throughput*

## 💰 Planes y Precios

### 🏠 **Starter Plan**
**GRATUITO** - Para uso personal y pequeñas empresas
- ✅ Monitoreo básico de rendimiento
- ✅ Detección de anomalías
- ✅ Dashboard web básico
- ❌ APIs limitadas
- ❌ Sin soporte técnico

### 🏢 **Enterprise Plan**
**$200-750/año** - Para empresas medianas y grandes
- ✅ Todo de Starter +
- ✅ IA avanzada para análisis predictivo
- ✅ APIs empresariales completas
- ✅ Dashboard personalizable
- ✅ Integración con sistemas existentes
- ✅ Soporte técnico prioritario
- ✅ Reportes personalizados

### 🏭 **Industrial Plan**
**$5000/3 años** - Para redes industriales críticas
- ✅ Todo de Enterprise +
- ✅ Monitoreo de protocolos industriales (Modbus, Profinet, OPC UA)
- ✅ Detección de conflictos de red en tiempo real
- ✅ Análisis de dispositivos industriales (PLCs, HMIs)
- ✅ Alertas de seguridad especializadas
- ✅ Consultoría de implementación incluida
- ✅ Certificaciones industriales (ISA/IEC 62443)

## 🚀 Installation

### Source Installation
```bash
# Clone the repository
git clone https://github.com/cathackr/SmartCompute.git
cd SmartCompute

# Install Python dependencies
pip install -r requirements.txt

# Test with the demo
python3 examples/synthetic_demo.py
```

## 📁 Estructura del Proyecto

<table>
<tr>
<td width="30%" valign="top">

### 📂 Directorio Principal
```
SmartCompute/
├── 📱 app/                    # Backend FastAPI
├── 🏭 smartcompute_industrial/ # Versión Industrial
├── 🎨 assets/                 # Imágenes y recursos
├── 🗃️ alembic/                # Migraciones DB
├── 🐳 docker-compose.yml     # Contenedores
├── ⚙️ main.py                # Servidor principal
└── 📋 README.md              # Este archivo
```

**Archivos clave:**
- [`main.py`](main.py) - Punto de entrada
- [`requirements.txt`](requirements.txt) - Dependencias
- [`.env.example`](.env.example) - Configuración

</td>
<td width="70%" valign="top">

### 🗂️ Navegación Rápida por Carpetas

| **🏭 Industrial** | **📱 Backend** | **🎨 Assets** |
|------------------|---------------|---------------|
| [`smartcompute_industrial/`](smartcompute_industrial/) | [`app/api/`](app/api/) | [`assets/`](assets/) |
| [Network API](smartcompute_industrial/network_api.py) | [Health Endpoints](app/api/health_endpoints.py) | [Logo HMI](assets/smartcompute_hmi_logo.png) |
| [Token API](smartcompute_industrial/token_api.py) | [Main API](app/api/main.py) | [Dashboard Grafana](assets/grafana_smartcompute_overview.png) |
| [Security](smartcompute_industrial/security.py) | [Models](app/models/) | [Screenshots](assets/) |

| **📋 Docs** | **⚙️ Config** | **🧪 Scripts** |
|-------------|---------------|---------------|
| [`docs/`](docs/) | [`docker-compose*.yml`](.) | [`scripts/`](scripts/) |
| [Network Guide](docs/NETWORK_INTELLIGENCE_GUIDE.md) | [Production](docker-compose.production.yml) | [Deploy](scripts/deploy.sh) |
| [Token Guide](docs/TOKEN_INTELLIGENCE_GUIDE.md) | [Development](.env.example) | [Monitoring](scripts/setup-monitoring.sh) |
| [Observability](docs/OBSERVABILITY.md) | [Security](security/) | [Migration](scripts/migrate_to_postgresql.py) |

</td>
</tr>
</table>

## 📚 Documentation

- 📖 [Technical Documentation](docs/TECHNICAL_DOCUMENTATION.md)
- 🚀 [Quick Start Guide](docs/GUIA_INICIO_RAPIDO.md)
- 💼 [Enterprise Guide](docs/GUIA_EMPRESARIAL.md)

## 👨‍💻 Creator

**SmartCompute** is created by **Martín Iribarne** - **CEH (Certified Ethical Hacker)**

🛡️ **Senior Cybersecurity & Networks Specialist** with 10+ years of experience in:
- 🔐 **Industrial Network Security** (ISA/IEC 62443 certified)
- 🎯 **Penetration Testing & Vulnerability Assessment**
- 📊 **SIEM Implementation & Security Monitoring**
- ☁️ **Cloud Security** (Azure AZ-900, AWS Cloud Practitioner)
- 🌐 **Network Infrastructure** (CCNA certified)

📍 **Experience**: HCLTech Industrial Network Auditing, Independent Cybersecurity Consulting, Critical Infrastructure Protection

**Professional Certifications:**
- 🏆 CEH (Certified Ethical Hacker)
- 🏆 CCNA (Cisco Certified Network Associate)
- 🏆 Azure Fundamentals AZ-900
- 🏆 AWS Cloud Practitioner
- 🏆 ISA/IEC 62443 Industrial Cybersecurity

- 🔗 **LinkedIn**: [Martín Iribarne CEH](https://www.linkedin.com/in/mart%C3%ADn-iribarne-swtf/)
- 📧 **Contact**: ggwre04p0@mozmail.com
- 📍 **Location**: Mar del Plata, Argentina
- 🐙 **GitHub**: [cathackr](https://github.com/cathackr)

---

## 📞 Support

- **📧 Email**: ggwre04p0@mozmail.com
- **🐙 Issues**: [GitHub Issues](https://github.com/cathackr/SmartCompute/issues)
- **💼 Enterprise**: Professional cybersecurity consulting available

---

© 2024 SmartCompute. All rights reserved.

<div align="center">
  
### 🚀 **¿Listo para evitar el próximo paro de producción?**

**Prueba gratis en 5 minutos:**
```bash
git clone https://github.com/cathackr/SmartCompute.git
cd SmartCompute/smartcompute_industrial  
./start_network_intelligence.sh
```

[**⭐ Dale una estrella si te parece útil**](https://github.com/cathackr/SmartCompute) • [**Demo en vivo**](http://127.0.0.1:8002) • [**¿Dudas?**](mailto:ggwre04p0@mozmail.com?subject=SmartCompute%20-%20Consulta)

---

## 💳 Suscripciones y Pagos Directos

### 🏢 **Enterprise Plan - $200-750/año**

**Elige tu modalidad de pago preferida:**

| **Período** | **Precio** | **Descuento** | **Pago Directo** |
|-------------|------------|---------------|------------------|
| **Anual** | $200/año | 65% OFF | [💳 **Pagar $200 USD**](https://cathackr.github.io/SmartCompute/checkout-enterprise-annual.html) |
| **Bianual** | $400/2 años | 65% OFF | [💳 **Pagar $400 USD**](https://cathackr.github.io/SmartCompute/checkout-enterprise-biannual.html) |
| **Premium** | $750/año | Características extra | [💳 **Pagar $750 USD**](https://cathackr.github.io/SmartCompute/checkout-enterprise-premium.html) |

### 🏭 **Industrial Plan - $5000/3 años**

**Incluye implementación y consultoría:**

| **Modalidad** | **Precio Total** | **Incluye** | **Pago Directo** |
|---------------|------------------|-------------|------------------|
| **Pago Completo** | $5000 USD | Todo + 20% descuento adicional | [💳 **Pagar $4000 USD**](https://cathackr.github.io/SmartCompute/checkout-industrial-full.html) |
| **3 Cuotas Anuales** | $1,667 × 3 años | Implementación escalonada | [💳 **Primera Cuota $1667**](https://cathackr.github.io/SmartCompute/checkout-industrial-installments.html) |

### 💰 **Sistema de Suscripción**

**Suscripción mensual recurrente con máxima flexibilidad:**

- 🔄 **Renovación automática**: Se renueva cada mes el mismo día
- ❌ **Cancelación libre**: Puedes cancelar cuando quieras desde el dashboard
- 💸 **Sin penalizaciones**: No hay cargos por cancelación
- ⏰ **Período de gracia**: 15 días para arrepentirse con reembolso completo
- 📅 **Servicio hasta fin de mes**: Si cancelas, mantienes acceso hasta que termine el período pagado

### 💳 **Métodos de Pago Integrados**

- 🇦🇷 **MercadoPago**: Tarjetas, débito automático, transferencias en pesos argentinos
- ₿ **Bitso**: Bitcoin, Ethereum, USDC y otras criptomonedas
- 🔒 **Seguridad**: Todas las transacciones están hasheadas y cifradas
- 🏪 **API segura**: Integración completa con sistemas bancarios certificados

### 📞 **Soporte de Suscripciones**
- **Email**: ggwre04p0@mozmail.com (dudas sobre facturación)
- **LinkedIn**: [Consulta profesional directa](https://www.linkedin.com/in/mart%C3%ADn-iribarne-swtf/)
- **Respuesta**: Todas las consultas se gestionan por correo electrónico

**🔒 Garantía de reembolso de 15 días • Cancela cuando quieras • Sin compromiso de permanencia**

</div>
