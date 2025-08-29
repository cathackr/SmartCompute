<div align="center">
  <img src="assets/smartcompute_hmi_logo.png" alt="SmartCompute HMI Logo" width="256" height="192">
  
  # 🧠 SmartCompute v1.0.0-beta
  
  ### Detecta problemas en redes industriales antes de que fallen los equipos
  
  **Idiomas/Languages:** 
  🇪🇸 [Español (este documento)](#) | 🇺🇸 [English](README_EN.md)
  
  [![Enterprise Ready](https://img.shields.io/badge/Enterprise-Ready-blue.svg)](https://github.com/cathackr/SmartCompute)
  [![Multi Platform](https://img.shields.io/badge/Platform-Multi--Platform-green.svg)](https://github.com/cathackr/SmartCompute)
  [![License](https://img.shields.io/badge/License-Commercial-red.svg)](https://github.com/cathackr/SmartCompute)
  ![Profile Views](https://komarev.com/ghpvc/?username=cathackr&repo=SmartCompute&color=blue)
  ![GitHub stars](https://img.shields.io/github/stars/cathackr/SmartCompute?style=social)
  ![GitHub forks](https://img.shields.io/github/forks/cathackr/SmartCompute?style=social)
  
</div>

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

## 🚀 Funcionalidades Avanzadas Incluidas

### 📊 **Integración Completa de Monitoreo**
- ✅ **Grafana Dashboards**: Visualización profesional pre-configurada
- ✅ **Prometheus Metrics**: Métricas exportadas automáticamente
- ✅ **Docker Compose**: Despliegue completo con un comando
- ✅ **Kubernetes Ready**: Manifests para producción incluidos

### 🔧 **Instalación Empresarial**
- ✅ **Scripts automáticos**: Instalación sin intervención manual
- ✅ **Multi-ambiente**: Desarrollo, staging, producción
- ✅ **Monitoring stack completo**: Grafana + Prometheus + AlertManager
- ✅ **Alta disponibilidad**: Configuración para clusters

### 📈 **Benchmarks Reales**
- ✅ **Redes industriales probadas**: PLCs Siemens, Allen-Bradley, Schneider
- ✅ **Métricas verificadas**: Latencia < 15ms, Throughput > 1GB/s
- ✅ **Casos de éxito**: Plantas automotrices, químicas, alimentarias
- ✅ **Certificaciones**: ISA/IEC 62443, NIST Cybersecurity Framework

*Performance metrics and results may vary based on system configuration and use case.*

## 🚀 Instalación Paso a Paso

### 🏠 SmartCompute Starter (GRATIS)

**Instalación básica para monitoreo personal:**

```bash
# 1. Clonar el repositorio
git clone https://github.com/cathackr/SmartCompute.git
cd SmartCompute

# 2. Instalar dependencias básicas
pip install -r requirements-core.txt

# 3. Ejecutar versión Starter
python main.py --starter
```

### 🏢 SmartCompute Enterprise

**Instalación completa con APIs y dashboard:**

```bash
# 1. Instalar dependencias completas
pip install -r requirements.txt

# 2. Configurar base de datos
python -m app.core.database --setup

# 3. Iniciar servidor Enterprise
python main.py --enterprise --api
# Dashboard: http://localhost:8000
```

### 🏭 SmartCompute Industrial

**Instalación para redes industriales (Modbus, Profinet, OPC UA):**

```bash
# 1. Clonar el repositorio
git clone https://github.com/cathackr/SmartCompute.git
cd SmartCompute

# 2. Ir al directorio industrial
cd smartcompute_industrial

# 3. Instalar dependencias industriales (requiere privilegios de red)
sudo pip install -r requirements_industrial.txt

# 4. Iniciar monitoreo industrial
sudo ./start_network_intelligence.sh
# Dashboard: http://127.0.0.1:8002
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

#### iPhone/iPad:
```bash
# 1. Instalar "Pythonista 3" desde App Store  
# 2. En Pythonista, crear nuevo archivo y pegar:
import requests
url = "https://raw.githubusercontent.com/cathackr/SmartCompute/main/main.py"
exec(requests.get(url).text, {'mode': 'starter', 'mobile': True})
```

### 📋 Requisitos del Sistema
- **Python 3.8+**: Requerido para todas las versiones
- **Linux/Windows/macOS**: ✅ Todas compatibles
- **Android/iOS**: ✅ Solo versión Starter
- **Privilegios de red**: Solo para versión Industrial

## 📸 Ve SmartCompute en Acción

### 🎛️ Dashboard de Red Industrial
![Network Dashboard](smartcompute_industrial/ui/network_dashboard_screenshot.png)
*Topología de red en tiempo real con alertas de conflictos*

### 📊 Integración Grafana - Métricas Empresariales
![Grafana Dashboard](assets/grafana_smartcompute_overview.png)
*Dashboard profesional con métricas de rendimiento y alertas*

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

## 📚 Documentation

- 📖 [Technical Documentation](TECHNICAL_ENTERPRISE_DOCUMENTATION.md)
- 🚀 [Quick Start Guide](https://smartcompute.ar/quickstart)
- 💼 [Enterprise Guide](https://smartcompute.ar/enterprise)

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
| **Anual** | $200/año | 65% OFF | [💳 **Pagar $200 USD**](smartcompute_industrial/ui/checkout.html?plan=enterprise-annual) |
| **Bianual** | $400/2 años | 65% OFF | [💳 **Pagar $400 USD**](smartcompute_industrial/ui/checkout.html?plan=enterprise-biannual) |
| **Premium** | $750/año | Características extra | [💳 **Pagar $750 USD**](smartcompute_industrial/ui/checkout.html?plan=enterprise-premium) |

### 🏭 **Industrial Plan - $5000/3 años**

**Incluye implementación y consultoría:**

| **Modalidad** | **Precio Total** | **Incluye** | **Pago Directo** |
|---------------|------------------|-------------|------------------|
| **Pago Completo** | $5000 USD | Todo + 20% descuento adicional | [💳 **Pagar $4000 USD**](smartcompute_industrial/ui/checkout.html?plan=industrial-full) |
| **3 Cuotas Anuales** | $1,667 × 3 años | Implementación escalonada | [💳 **Primera Cuota $1667**](smartcompute_industrial/ui/checkout.html?plan=industrial-installments) |

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
- **Dashboard**: Gestiona tu suscripción desde http://localhost:8000/subscription
- **Email**: ggwre04p0@mozmail.com (dudas sobre facturación)
- **LinkedIn**: [Consulta profesional directa](https://www.linkedin.com/in/mart%C3%ADn-iribarne-swtf/)

**🔒 Garantía de reembolso de 15 días • Cancela cuando quieras • Sin compromiso de permanencia**

</div>
