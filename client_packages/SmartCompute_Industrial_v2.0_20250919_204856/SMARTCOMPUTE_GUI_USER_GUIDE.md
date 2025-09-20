# 🚀 SmartCompute Enterprise GUI - Guía de Usuario

**Versión:** 2.0.0 Enterprise Edition
**Fecha:** 2025-09-19
**Compatibilidad:** Windows 10/11, Linux (Ubuntu/CentOS/Fedora/Arch), macOS

---

## 📋 Índice

1. [Introducción](#introducción)
2. [Instalación](#instalación)
3. [Interfaz Principal](#interfaz-principal)
4. [Configuración de Herramientas](#configuración-de-herramientas)
5. [Configuración de Red](#configuración-de-red)
6. [Frameworks de Seguridad](#frameworks-de-seguridad)
7. [Ejecución de Análisis](#ejecución-de-análisis)
8. [Resultados y Reportes](#resultados-y-reportes)
9. [Asistente IA](#asistente-ia)
10. [Solución de Problemas](#solución-de-problemas)

---

## 🎯 Introducción

SmartCompute Enterprise GUI es una aplicación gráfica moderna que unifica todas las herramientas de análisis de seguridad empresarial e industrial de SmartCompute. Proporciona una interfaz intuitiva para:

### ✨ **Características Principales:**

- **🔧 94+ Herramientas Integradas**: Acceso a todas las herramientas de análisis
- **🏭 Análisis Industrial**: SCADA, PLC, protocolos industriales (Modbus, EtherNet/IP, PROFINET)
- **🏢 Seguridad Enterprise**: Frameworks OWASP, NIST, ISO 27001, MITRE ATT&CK
- **🤖 IA Integrada**: Asistente inteligente para recomendaciones
- **📊 Reportes Avanzados**: HTML, PDF, JSON con gráficos interactivos
- **🌐 Configuración Avanzada**: Redes, protocolos, capas OSI
- **⚡ Tiempo Real**: Monitoreo y análisis en vivo

---

## 🔧 Instalación

### **Instalación Automática (Recomendada)**

```bash
# Descargar y ejecutar instalador
wget https://raw.githubusercontent.com/smartcompute/enterprise/main/install_smartcompute_gui.sh
chmod +x install_smartcompute_gui.sh
./install_smartcompute_gui.sh
```

### **Instalación Manual**

```bash
# 1. Clonar repositorio
git clone https://github.com/smartcompute/enterprise.git
cd enterprise

# 2. Crear entorno virtual
python3 -m venv ~/.smartcompute_venv
source ~/.smartcompute_venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar GUI
python3 smartcompute_enterprise_gui.py
```

### **Verificación de Instalación**

```bash
# Verificar instalación
smartcompute-gui --version

# Ejecutar tests
smartcompute-gui --test
```

---

## 🖥️ Interfaz Principal

### **Ventana Principal**

La aplicación se organiza en **6 pestañas principales**:

1. **🔧 Herramientas** - Selección y configuración de herramientas
2. **🌐 Red y Protocolos** - Configuración de objetivos y protocolos
3. **🛡️ Frameworks de Seguridad** - Selección de estándares de seguridad
4. **▶️ Ejecución** - Control del análisis y configuración de reportes
5. **📊 Resultados** - Visualización de resultados y exportación
6. **🤖 Asistente IA** - Consultas y recomendaciones inteligentes

### **Header de Control**

- **💾 Guardar Config**: Guardar configuración actual
- **📁 Cargar Config**: Cargar configuración guardada
- **🔄 Actualizar**: Refrescar herramientas disponibles

---

## 🔧 Configuración de Herramientas

### **Categorías de Herramientas**

#### **🏢 Core Enterprise**
- **Sistema Unificado**: Análisis completo Enterprise + Industrial
- **Servidor Central MCP**: Servidor centralizado con WebSocket
- **Análisis de Infraestructura**: Análisis completo de infraestructura TI

#### **🏭 Industrial SCADA**
- **Monitor Industrial**: SCADA, PLC, protocolos industriales
- **Escáner Modbus TCP**: Detección de dispositivos Modbus
  - *Parámetros*: Rango de puertos, timeout
- **EtherNet/IP Scanner**: Detección Allen-Bradley
  - *Parámetros*: CIP scan, tipo de dispositivo
- **PROFINET Scanner**: Detección Siemens PROFINET
  - *Parámetros*: DCP scan, topología

#### **🔐 Seguridad Enterprise**
- **Sistema de Autenticación**: Autenticación multi-factor
- **Gestión de Secretos**: Gestión centralizada AES-256
- **Análisis MITRE ATT&CK**: Tácticas y técnicas de adversarios
- **Correlación de Amenazas**: Motor de correlación inteligente

#### **🧠 Machine Learning**
- **Framework HRM**: Aprendizaje automático avanzado
- **Motor MLE-STAR**: Integración con BotConf 2024
- **Priorización ML**: Priorización inteligente de amenazas
- **Evolución Adaptativa**: Capacidades evolutivas automáticas

#### **📊 Monitoreo y Alertas**
- **Análisis en Vivo**: Monitoreo en tiempo real
- **Agregador de Alertas**: Consolidación inteligente
- **Coordinador SIEM**: Integración SIEM/SOAR

### **Selección de Herramientas**

1. **✅ Marcar/Desmarcar**: Click en checkbox para habilitar herramienta
2. **⚙️ Parámetros**: Se despliegan automáticamente al seleccionar herramientas con configuración
3. **📝 Configuración**: Ajustar parámetros específicos por herramienta

### **Parámetros Avanzados**

- **Rango de Puertos**: Especificar puertos a escanear (ej: 502,102,44818)
- **Timeout**: Tiempo límite por conexión (1-30 segundos)
- **Tipo de Dispositivo**: PLC, HMI, Drive, I/O
- **Modo de Escaneo**: CIP scan, DCP scan, topology discovery

---

## 🌐 Configuración de Red

### **🎯 Configuración de Objetivos**

- **IP/Rango Objetivo**:
  - IP única: `192.168.1.10`
  - Rango CIDR: `192.168.1.0/24`
  - Rango explícito: `192.168.1.1-192.168.1.254`
  - Hostname: `server.company.com`

- **Servidor/Host**: Servidor central para comunicación MCP

### **🔌 Configuración de Red Avanzada**

- **Rango IP Específico**: Definir rango exacto para escaneo
- **Análisis DHCP**: Incluir detección de servidores DHCP y leases
- **Configuración VLAN**: Detección de VLANs y segmentación

### **📡 Configuración de Protocolos**

#### **Protocolos Disponibles:**
- **TCP/UDP/ICMP**: Protocolos básicos de red
- **Modbus**: Protocolo industrial estándar
- **EtherNet/IP**: Protocolo Allen-Bradley
- **PROFINET**: Protocolo Siemens
- **OPC-UA**: Protocolo industrial moderno
- **DNP3**: Protocolo para utilities
- **BACnet**: Protocolo para automatización de edificios

### **🔗 Capas del Modelo OSI**

Seleccionar capas específicas para análisis:

- **L1 - Física**: Análisis de hardware y conectividad
- **L2 - Enlace**: Switches, VLANs, MAC addresses
- **L3 - Red**: Routing, IP, ICMP
- **L4 - Transporte**: TCP, UDP, puertos
- **L5 - Sesión**: Gestión de sesiones
- **L6 - Presentación**: Cifrado, compresión
- **L7 - Aplicación**: Protocolos de aplicación

### **🔍 Tipos de Escaneo**

- **Quick**: Escaneo rápido de puertos comunes
- **Comprehensive**: Escaneo completo de todos los puertos
- **Stealth**: Escaneo sigiloso para evitar detección
- **Aggressive**: Escaneo intensivo con fingerprinting
- **Custom**: Configuración personalizada

---

## 🛡️ Frameworks de Seguridad

### **🔒 Frameworks Principales**

#### **ISO 27001:2022**
- Gestión de Seguridad de la Información
- Controles de seguridad A.8, A.9, A.12, A.13, A.16
- Evaluación de riesgos y controles

#### **MITRE ATT&CK**
- Tácticas, Técnicas y Procedimientos de Adversarios
- Mapping de técnicas detectadas
- Análisis de cadenas de ataque

#### **ISA/IEC 62443**
- Ciberseguridad en Sistemas de Control Industrial
- Security Zones & Conduits
- Niveles de seguridad SL1-SL4

#### **OWASP Top 10**
- Vulnerabilidades Web más Críticas
- Análisis de aplicaciones web
- Controles preventivos

#### **NIST Cybersecurity Framework**
- Marco de Ciberseguridad NIST
- Funciones: Identify, Protect, Detect, Respond, Recover
- Evaluación de madurez

### **🏭 Estándares Industriales Específicos**

#### **ISA-95**
- Integración Sistema de Control Empresarial
- Niveles de automatización
- Interfaces MES/ERP

#### **IEC 61511**
- Safety Instrumented Systems (SIS)
- Análisis SIL (Safety Integrity Level)
- Sistemas de seguridad funcional

#### **IEC 61850**
- Comunicaciones para Dispositivos Electrónicos Inteligentes
- Protocolo para subestaciones eléctricas
- Comunicación IED

#### **ISA-101**
- Interfaz Humano-Máquina Optimizada
- Diseño de HMI/SCADA
- Ergonomía y usabilidad

### **📋 Configuración de Cumplimiento**

- **Nivel de Cumplimiento**: Basic, Medium, High, Critical
- **Generar Evidencias**: Documentación automática para auditorías
- **Reportes de Compliance**: Matrices de cumplimiento detalladas

---

## ▶️ Ejecución de Análisis

### **🚀 Control de Ejecución**

#### **Botones Principales:**
- **🔍 Iniciar Análisis Completo**: Ejecutar análisis con configuración actual
- **⏸️ Pausar**: Pausar análisis en curso
- **⏹️ Detener**: Detener análisis completamente
- **📊 Ver Estado**: Mostrar estado detallado del sistema

### **📄 Configuración de Reportes**

#### **Formatos Disponibles:**
- **HTML**: Reporte interactivo con gráficos (recomendado)
- **PDF**: Documento profesional para presentaciones
- **JSON**: Datos estructurados para integración
- **XML**: Formato estándar para intercambio
- **CSV**: Datos tabulares para análisis
- **XLSX**: Hoja de cálculo Excel

#### **Opciones de Reporte:**
- **✅ Incluir gráficos y visualizaciones**: Charts interactivos
- **✅ Incluir datos en bruto**: Información técnica detallada
- **✅ Auto-abrir**: Abrir reporte automáticamente al completar

### **📈 Monitoreo de Progreso**

- **Barra de Progreso**: Progreso visual del análisis (0-100%)
- **Estado Actual**: Descripción de la fase actual
- **Tiempo Estimado**: Estimación de tiempo restante
- **Herramientas Activas**: Lista de herramientas en ejecución

### **🔍 Fases del Análisis**

1. **Preparación**: Validación de configuración y objetivos
2. **Descubrimiento**: Detección de hosts y servicios
3. **Escaneo**: Análisis de puertos y protocolos
4. **Identificación**: Fingerprinting de sistemas y servicios
5. **Análisis**: Evaluación de vulnerabilidades y riesgos
6. **Correlación**: Análisis de patrones y amenazas
7. **Reporte**: Generación de documentación

---

## 📊 Resultados y Reportes

### **📋 Visualización de Resultados**

#### **Secciones del Reporte:**

**📊 RESUMEN EJECUTIVO:**
- Herramientas ejecutadas
- Vulnerabilidades encontradas
- Dispositivos industriales detectados
- Score de seguridad general

**🚨 HALLAZGOS CRÍTICOS:**
- Lista priorizada de vulnerabilidades críticas
- Ubicación y descripción detallada
- Nivel de riesgo y severidad

**📈 ESTADÍSTICAS:**
- Tiempo de análisis
- IPs escaneadas
- Puertos analizados
- Protocolos detectados

**🎯 RECOMENDACIONES:**
- Acciones prioritarias
- Plan de remediación
- Mejores prácticas

### **🔧 Controles de Resultados**

- **🔄 Actualizar**: Refrescar resultados mostrados
- **📁 Abrir Reporte**: Abrir reporte HTML en navegador
- **📤 Exportar**: Exportar a diferentes formatos
- **🤖 Consultar IA**: Cambiar a asistente IA para análisis

### **📤 Exportación Avanzada**

#### **Formatos de Exportación:**
- **TXT**: Texto plano para logs
- **JSON**: Datos estructurados
- **CSV**: Datos tabulares
- **PDF**: Documento profesional

#### **Filtros de Exportación:**
- Por severidad de vulnerabilidad
- Por tipo de dispositivo
- Por framework de seguridad
- Por fecha/hora

---

## 🤖 Asistente IA

### **🧠 Características del Asistente**

El Asistente IA de SmartCompute proporciona:

- **💬 Chat Interactivo**: Conversación natural sobre resultados
- **🎯 Recomendaciones Inteligentes**: Análisis contextual de hallazgos
- **🔧 Planes de Remediación**: Guías paso a paso para resolver problemas
- **📊 Análisis de Tendencias**: Identificación de patrones y correlaciones

### **💬 Uso del Chat**

#### **Área de Chat:**
- **Historial**: Conversación completa con timestamps
- **Input de Usuario**: Área de texto para consultas
- **Botones de Acción**: Enviar, Recomendar, Remediar, Limpiar

#### **Consultas Efectivas:**

```
🚨 "¿Cuáles son las amenazas más críticas encontradas?"
🔧 "Genera un plan de remediación priorizado para el PLC Siemens"
📊 "Analiza el cumplimiento con ISO 27001 basado en los hallazgos"
🎯 "¿Qué acciones debo tomar primero para mejorar la seguridad?"
```

### **⚡ Consultas Rápidas**

#### **Botones de Acceso Rápido:**

- **🚨 Amenazas Críticas**: Lista priorizada de vulnerabilidades críticas
- **🔧 Plan de Remediación**: Plan detallado de acciones correctivas
- **📊 Resumen Ejecutivo**: Resumen para presentación a directivos
- **🎯 Próximos Pasos**: Recomendaciones de siguientes acciones

### **🎯 Tipos de Recomendaciones**

#### **🔴 ACCIONES INMEDIATAS (0-24 horas):**
- Cerrar puertos críticos expuestos
- Cambiar credenciales por defecto
- Aislar sistemas comprometidos

#### **🟡 MEJORAS A CORTO PLAZO (1-4 semanas):**
- Actualizar firmware de dispositivos
- Implementar segmentación de red
- Configurar autenticación robusta

#### **🟢 FORTALECIMIENTO A LARGO PLAZO (1-6 meses):**
- Desplegar sistemas de monitoreo avanzado
- Implementar PKI empresarial
- Establecer SOC industrial

### **📋 Ejemplos de Interacción**

```
Usuario: "¿Por qué el puerto Modbus 502 es una vulnerabilidad crítica?"

IA: "🚨 El puerto Modbus TCP 502 expuesto representa una vulnerabilidad crítica porque:

1. **Acceso Directo a PLC**: Permite control completo del dispositivo industrial
2. **Sin Autenticación**: Modbus TCP no incluye autenticación nativa
3. **Comandos de Escritura**: Un atacante puede modificar valores y lógica
4. **Interrupción de Procesos**: Riesgo de parada de producción

🔧 REMEDIACIÓN INMEDIATA:
• Configurar firewall para restringir acceso al puerto 502
• Implementar VPN para comunicación remota
• Considerar gateway Modbus con autenticación

¿Te gustaría que detalle los pasos específicos para implementar estas medidas?"
```

---

## 🔧 Solución de Problemas

### **❌ Problemas Comunes**

#### **🔌 Error de Conexión**

**Síntoma**: No se puede conectar al objetivo
```
Solución:
1. Verificar conectividad de red: ping [objetivo]
2. Comprobar firewall local
3. Validar permisos de red
4. Revisar configuración de proxy
```

#### **🐍 Error de Dependencias Python**

**Síntoma**: Módulos no encontrados
```
Solución:
1. Activar entorno virtual: source ~/.smartcompute_venv/bin/activate
2. Reinstalar dependencias: pip install -r requirements.txt
3. Verificar versión Python: python3 --version (≥3.8)
```

#### **🖥️ Error de GUI**

**Síntoma**: No se abre la interfaz gráfica
```
Solución:
1. Verificar X11/Display: echo $DISPLAY
2. Instalar tkinter: sudo apt install python3-tk
3. Verificar permisos: xhost +local:
```

#### **🔐 Error de Permisos**

**Síntoma**: Acceso denegado a dispositivos de red
```
Solución:
1. Ejecutar con sudo para raw sockets
2. Agregar usuario a grupo netdev: sudo usermod -a -G netdev $USER
3. Configurar capabilities: sudo setcap cap_net_raw=eip python3
```

### **📝 Logs y Debugging**

#### **Ubicaciones de Logs:**
```bash
# Logs principales
~/.smartcompute/logs/smartcompute.log

# Logs de errores
~/.smartcompute/logs/error.log

# Logs de análisis
~/.smartcompute/logs/analysis_[timestamp].log
```

#### **Habilitar Debug Mode:**
```bash
# Ejecutar en modo debug
smartcompute-gui --debug

# Ver logs en tiempo real
tail -f ~/.smartcompute/logs/smartcompute.log
```

### **🔧 Comandos de Diagnóstico**

```bash
# Verificar instalación
smartcompute-gui --version
smartcompute-gui --test

# Limpiar configuración
rm -rf ~/.smartcompute/config/*

# Reinstalar dependencias
pip install --force-reinstall -r requirements.txt

# Verificar conectividad
nc -zv [objetivo] [puerto]
```

### **📞 Soporte**

#### **Recursos de Ayuda:**
- **📖 Documentación**: `~/.smartcompute/docs/`
- **💬 Issues**: GitHub Issues para reportar problemas
- **📧 Email**: support@smartcompute.com
- **🌐 Wiki**: GitHub Wiki con ejemplos

#### **Información para Soporte:**
```bash
# Generar reporte de diagnóstico
smartcompute-gui --diagnostic > diagnostic_report.txt
```

---

## 📚 Recursos Adicionales

### **🔗 Enlaces Útiles**
- [Repositorio GitHub](https://github.com/smartcompute/enterprise)
- [Documentación Completa](https://docs.smartcompute.com)
- [Video Tutoriales](https://youtube.com/smartcompute)
- [Foro de la Comunidad](https://community.smartcompute.com)

### **📖 Documentación Relacionada**
- `SMARTCOMPUTE_USER_GUIDE.md` - Guía general del sistema
- `SECURITY_README.md` - Configuración de seguridad
- `INSTALLERS_README.md` - Instaladores empresariales
- `claude_inc` - Estado y cambios recientes

### **🏆 Mejores Prácticas**
1. **Configurar objetivos específicos** antes de iniciar análisis
2. **Seleccionar frameworks relevantes** para su industria
3. **Revisar configuración de red** para evitar falsos positivos
4. **Consultar IA regularmente** para maximizar valor del análisis
5. **Exportar reportes en múltiples formatos** para diferentes audiencias
6. **Mantener configuraciones guardadas** para análisis recurrentes

---

**© 2025 SmartCompute Enterprise - Todos los derechos reservados**