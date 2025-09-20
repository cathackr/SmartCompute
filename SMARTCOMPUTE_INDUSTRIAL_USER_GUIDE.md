# SmartCompute Industrial v2.0 - Guía Completa del Usuario

## 🏭 Sistema Inteligente de Diagnóstico Industrial

**Desarrollado por:** ggwre04p0@mozmail.com
**LinkedIn:** https://www.linkedin.com/in/martín-iribarne-swtf/

---

## 📋 Índice

1. [Introducción](#introducción)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Instalación y Configuración](#instalación-y-configuración)
4. [Configuración de Seguridad](#configuración-de-seguridad)
5. [Uso del Sistema](#uso-del-sistema)
6. [Configuración Personalizada](#configuración-personalizada)
7. [Mejores Prácticas de Seguridad](#mejores-prácticas-de-seguridad)
8. [Resolución de Problemas](#resolución-de-problemas)
9. [Soporte Técnico](#soporte-técnico)

---

## 🎯 Introducción

SmartCompute Industrial es un sistema completo de diagnóstico inteligente que combina:

- **🔐 Seguridad avanzada** con autenticación 2FA y verificación GPS
- **🤖 Inteligencia artificial** para análisis visual de equipos
- **🧠 Razonamiento HRM** para generación de soluciones
- **⚡ Flujo de trabajo** automatizado con aprobaciones
- **📱 Interfaz móvil** para técnicos de campo

### ✨ Características Principales

| Característica | Descripción | Beneficio |
|---------------|-------------|-----------|
| Autenticación 2FA | Códigos TOTP + verificación GPS | Acceso 100% seguro |
| Análisis Visual IA | Reconocimiento de equipos y estados | Diagnóstico automático |
| Razonamiento HRM | Generación inteligente de soluciones | Recomendaciones precisas |
| Flujo de Aprobaciones | Sistema multi-nivel automatizado | Control y trazabilidad |
| Aprendizaje Continuo | IA que mejora con cada uso | Precisión creciente |

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    SMARTCOMPUTE INDUSTRIAL                  │
├─────────────────────────────────────────────────────────────┤
│  🔐 CAPA DE SEGURIDAD                                      │
│  ├── Autenticación 2FA (TOTP)                              │
│  ├── Verificación GPS/Geofencing                           │
│  ├── Túneles VPN/SSH seguros                               │
│  └── Tokens JWT con expiración                             │
├─────────────────────────────────────────────────────────────┤
│  🤖 CAPA DE INTELIGENCIA ARTIFICIAL                        │
│  ├── Análisis Visual (OpenCV + ML)                         │
│  ├── Reconocimiento de Equipos                             │
│  ├── Detección de Anomalías                                │
│  └── Sistema HRM (Hierarchical Reasoning)                  │
├─────────────────────────────────────────────────────────────┤
│  ⚡ CAPA DE FLUJO DE TRABAJO                               │
│  ├── Sistema de Aprobaciones Multi-nivel                   │
│  ├── Notificaciones en Tiempo Real                         │
│  ├── Escalamiento Automático                               │
│  └── Documentación de Sesiones                             │
├─────────────────────────────────────────────────────────────┤
│  🔗 CAPA DE INTEGRACIÓN INDUSTRIAL                         │
│  ├── Protocolos: Modbus, PROFINET, S7comm                  │
│  ├── SCADA: WinCC, FactoryTalk, Wonderware                 │
│  ├── PLCs: Siemens S7, Allen-Bradley                       │
│  └── Comunicación: Ethernet/IP, OPC-UA                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Instalación y Configuración

### Prerequisitos del Sistema

| Componente | Versión Mínima | Recomendada |
|------------|----------------|-------------|
| **SO** | Ubuntu 18.04 / RHEL 7 | Ubuntu 22.04 LTS |
| **Python** | 3.8+ | 3.10+ |
| **Node.js** | 16+ | 18+ |
| **RAM** | 4 GB | 8 GB |
| **Almacenamiento** | 10 GB | 50 GB |
| **Red** | 100 Mbps | 1 Gbps |

### Instalación Automática

```bash
# Descargar el paquete
wget https://releases.smartcompute.com/v2.0/smartcompute-industrial-v2.0.tar.gz

# Extraer
tar -xzf smartcompute-industrial-v2.0.tar.gz
cd smartcompute-industrial-v2.0

# Ejecutar instalador
sudo chmod +x install.sh
sudo ./install.sh
```

### Instalación Manual

```bash
# 1. Actualizar sistema
sudo apt-get update && sudo apt-get upgrade -y

# 2. Instalar dependencias
sudo apt-get install -y python3 python3-pip python3-venv nodejs npm
sudo apt-get install -y python3-opencv python3-pil sqlite3

# 3. Crear usuario del sistema
sudo useradd -r -s /bin/false smartcompute
sudo mkdir -p /opt/smartcompute/{data,logs,config,reports}
sudo chown -R smartcompute:smartcompute /opt/smartcompute

# 4. Configurar entorno Python
python3 -m venv /opt/smartcompute/venv
source /opt/smartcompute/venv/bin/activate
pip install pillow opencv-python qrcode pyotp pyjwt cryptography

# 5. Instalar dependencias Node.js
npm install express socket.io jsonwebtoken
```

---

## 🔐 Configuración de Seguridad

### 1. Configuración de Autenticación 2FA

Editar `/etc/smartcompute/config.ini`:

```ini
[security]
# ⚠️ CAMBIAR EN PRODUCCIÓN
jwt_secret = GENERATE_SECURE_JWT_SECRET_HERE
encryption_key = GENERATE_AES_256_KEY_HERE

# Configuración 2FA
totp_issuer = SmartCompute Industrial
totp_digits = 6
totp_period = 30

# Sesiones
session_timeout_hours = 8
max_failed_attempts = 3
lockout_duration_minutes = 15
```

### 2. Configuración de Ubicaciones GPS

Editar `/etc/smartcompute/authorized_locations.json`:

```json
{
  "planta_principal": {
    "name": "Planta Principal",
    "lat": -34.6037,
    "lng": -58.3816,
    "radius_meters": 100,
    "authorized_operators": ["OP001", "OP002", "OP003"],
    "emergency_contact": "+54911234567",
    "backup_contact": "+54911234568"
  },
  "almacen_repuestos": {
    "name": "Almacén de Repuestos",
    "lat": -34.6045,
    "lng": -58.3820,
    "radius_meters": 50,
    "authorized_operators": ["OP001", "OP004"],
    "emergency_contact": "+54911234567"
  },
  "subestacion_electrica": {
    "name": "Subestación Eléctrica",
    "lat": -34.6055,
    "lng": -58.3825,
    "radius_meters": 30,
    "authorized_operators": ["OP005"],
    "emergency_contact": "+54911234569",
    "special_requirements": ["electrical_permit", "safety_equipment"]
  }
}
```

### 3. Configuración de Operadores

Editar `/etc/smartcompute/operators.json`:

```json
{
  "operators": {
    "OP001": {
      "name": "Juan Carlos Técnico",
      "role": "technician",
      "level": 2,
      "certifications": ["electrical", "mechanical"],
      "phone": "+54911111111",
      "email": "juan.carlos@empresa.com",
      "totp_secret": "GENERATE_UNIQUE_SECRET",
      "authorized_locations": ["planta_principal", "almacen_repuestos"]
    },
    "OP002": {
      "name": "María González Supervisora",
      "role": "supervisor",
      "level": 3,
      "certifications": ["electrical", "mechanical", "safety"],
      "phone": "+54911111112",
      "email": "maria.gonzalez@empresa.com",
      "totp_secret": "GENERATE_UNIQUE_SECRET",
      "authorized_locations": ["planta_principal", "almacen_repuestos", "subestacion_electrica"]
    }
  }
}
```

---

## 📱 Uso del Sistema

### Proceso Paso a Paso

#### 1. **🔐 Autenticación**

```bash
# El operador inicia sesión con:
# - ID de operador (ej: OP001)
# - Código 2FA de 6 dígitos (de app como Google Authenticator)
# - Verificación automática de ubicación GPS
```

#### 2. **📸 Captura de Problema**

```bash
# El operador:
# 1. Toma foto del equipo problemático
# 2. Sistema verifica ubicación autorizada
# 3. Imagen se encripta y sube al servidor
# 4. IA inicia análisis automático
```

#### 3. **🤖 Análisis Inteligente**

```bash
# Sistema automáticamente:
# ✅ Identifica tipo de equipo (PLC, HMI, Switch, etc.)
# ✅ Analiza estado de LEDs y displays
# ✅ Detecta anomalías visuales
# ✅ Lee códigos de error y etiquetas
# ✅ Genera diagnóstico con nivel de confianza
```

#### 4. **🧠 Generación de Solución**

```bash
# Sistema HRM:
# ✅ Categoriza el tipo de problema
# ✅ Busca patrones similares en base de datos
# ✅ Evalúa estrategias de resolución
# ✅ Prioriza acciones por impacto y seguridad
# ✅ Genera plan detallado con tiempos y herramientas
```

#### 5. **✅ Flujo de Aprobaciones**

```bash
# Sistema automáticamente:
# ✅ Determina nivel de aprobación requerido
# ✅ Notifica al supervisor correspondiente
# ✅ Envía detalles por email/SMS/Slack
# ✅ Registra respuesta y comentarios
# ✅ Autoriza ejecución de acciones
```

#### 6. **📊 Documentación y Aprendizaje**

```bash
# Sistema:
# ✅ Genera reporte completo de la sesión
# ✅ Registra resultados de las acciones
# ✅ Actualiza base de conocimiento
# ✅ Mejora algoritmos para próximas veces
# ✅ Calcula métricas de eficiencia
```

---

## ⚙️ Configuración Personalizada

### 1. Configuración de Equipos Soportados

Editar `/etc/smartcompute/equipment_database.json`:

```json
{
  "equipment_types": {
    "siemens_s7_1200": {
      "manufacturer": "Siemens",
      "model": "S7-1200",
      "type": "PLC",
      "visual_indicators": {
        "run_led": {"position": "top_left", "states": ["green", "yellow", "red"]},
        "error_led": {"position": "top_center", "states": ["off", "red_solid", "red_blink"]},
        "maint_led": {"position": "top_right", "states": ["off", "yellow"]}
      },
      "common_issues": [
        {
          "pattern": "run_led_red_error_led_red",
          "description": "Falla crítica del CPU",
          "actions": ["verify_power", "check_program", "restart_cpu"]
        }
      ],
      "communication_protocols": ["S7comm", "Modbus_TCP"],
      "safety_considerations": ["high_voltage", "machinery_control"]
    }
  }
}
```

### 2. Configuración de Niveles de Aprobación

Editar `/etc/smartcompute/approval_levels.json`:

```json
{
  "approval_matrix": {
    "low_risk": {
      "description": "Acciones de bajo riesgo y bajo impacto",
      "required_level": 1,
      "approvers": ["technician", "supervisor"],
      "auto_approve": true,
      "timeout_minutes": 5,
      "examples": ["restart_device", "check_connections", "read_diagnostics"]
    },
    "medium_risk": {
      "description": "Acciones de riesgo medio con impacto operacional",
      "required_level": 2,
      "approvers": ["supervisor", "manager"],
      "auto_approve": false,
      "timeout_minutes": 15,
      "examples": ["replace_component", "modify_parameters", "stop_process"]
    },
    "high_risk": {
      "description": "Acciones críticas que afectan seguridad o producción",
      "required_level": 3,
      "approvers": ["manager", "director"],
      "auto_approve": false,
      "timeout_minutes": 30,
      "escalation_required": true,
      "examples": ["emergency_shutdown", "bypass_safety", "critical_repair"]
    }
  }
}
```

### 3. Configuración de Notificaciones

Editar `/etc/smartcompute/notifications.json`:

```json
{
  "notification_channels": {
    "email": {
      "enabled": true,
      "smtp_server": "smtp.empresa.com",
      "smtp_port": 587,
      "username": "smartcompute@empresa.com",
      "password": "SECURE_PASSWORD",
      "use_tls": true
    },
    "sms": {
      "enabled": true,
      "provider": "twilio",
      "account_sid": "YOUR_TWILIO_SID",
      "auth_token": "YOUR_TWILIO_TOKEN",
      "from_number": "+54911234567"
    },
    "slack": {
      "enabled": true,
      "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
      "channel": "#mantenimiento",
      "username": "SmartCompute"
    }
  },
  "notification_rules": {
    "high_priority": {
      "channels": ["email", "sms", "slack"],
      "immediate": true,
      "retry_attempts": 3
    },
    "medium_priority": {
      "channels": ["email", "slack"],
      "immediate": false,
      "batch_interval_minutes": 5
    },
    "low_priority": {
      "channels": ["email"],
      "immediate": false,
      "batch_interval_minutes": 30
    }
  }
}
```

---

## 🛡️ Mejores Prácticas de Seguridad

### ⚠️ **CRÍTICO: Prácticas PROHIBIDAS**

| ❌ **NUNCA HACER** | ⚡ **RIESGO** | ✅ **ALTERNATIVA SEGURA** |
|-------------------|---------------|---------------------------|
| Usar contraseñas por defecto | Acceso no autorizado | Generar claves únicas por instalación |
| Deshabilitar verificación GPS | Acceso desde ubicaciones no autorizadas | Configurar zonas GPS precisas |
| Compartir códigos 2FA | Compromiso de identidad | Un código por operador |
| Ejecutar sin aprobación | Acciones no autorizadas | Siempre usar flujo de aprobaciones |
| Modificar logs manualmente | Pérdida de trazabilidad | Dejar logs intactos, usar reportes |
| Usar conexiones no encriptadas | Intercepción de datos | Forzar HTTPS/TLS en todas las conexiones |

### 🔒 **Configuración Segura Obligatoria**

#### 1. **Generación de Claves Seguras**

```bash
# Generar clave JWT única
openssl rand -hex 32

# Generar clave de encriptación AES-256
openssl rand -hex 32

# Generar secreto TOTP por operador
python3 -c "import pyotp; print(pyotp.random_base32())"
```

#### 2. **Configuración de Firewall**

```bash
# Permitir solo puertos necesarios
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing

# SmartCompute API
sudo ufw allow from 192.168.1.0/24 to any port 3000
# WebSocket
sudo ufw allow from 192.168.1.0/24 to any port 3001
# SSH (solo desde red administrativa)
sudo ufw allow from 192.168.100.0/24 to any port 22
```

#### 3. **Configuración de Logs de Auditoría**

```bash
# Configurar rotación de logs
echo "/var/log/smartcompute/*.log {
    daily
    missingok
    rotate 90
    compress
    notifempty
    copytruncate
    create 644 smartcompute smartcompute
}" | sudo tee /etc/logrotate.d/smartcompute
```

#### 4. **Backup Automático de Configuración**

```bash
# Script de backup diario
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf /backup/smartcompute_config_$DATE.tar.gz \
  /etc/smartcompute/ \
  /opt/smartcompute/data/ \
  /var/log/smartcompute/

# Retener solo 30 días
find /backup -name "smartcompute_config_*.tar.gz" -mtime +30 -delete
```

### 🔍 **Monitoreo de Seguridad**

#### Métricas Críticas a Monitorear

| Métrica | Umbral de Alerta | Acción |
|---------|------------------|--------|
| Intentos de login fallidos | > 5 en 15 min | Bloquear IP temporalmente |
| Accesos desde ubicaciones no autorizadas | > 1 | Alerta inmediata al administrador |
| Sesiones simultáneas por operador | > 2 | Verificar actividad sospechosa |
| Modificaciones de configuración | Cualquiera | Log completo + notificación |
| Análisis con confianza < 50% | > 10% del total | Revisar modelos de IA |

---

## 🔧 Resolución de Problemas

### Problemas Comunes y Soluciones

#### 1. **Error de Autenticación 2FA**

```bash
# Síntoma: "Código 2FA inválido"
# Causa: Reloj del dispositivo desincronizado

# Solución:
sudo ntpdate -s time.nist.gov
sudo systemctl restart smartcompute

# Verificar configuración del operador
sudo python3 -c "
import pyotp
secret = 'SECRET_DEL_OPERADOR'
totp = pyotp.TOTP(secret)
print(f'Código actual: {totp.now()}')
"
```

#### 2. **Falla de Verificación GPS**

```bash
# Síntoma: "Ubicación no autorizada"
# Causa: GPS impreciso o configuración incorrecta

# Verificar ubicación actual:
curl -s "http://ip-api.com/json/" | jq '.lat, .lon'

# Ajustar radio en authorized_locations.json:
# Aumentar "radius_meters" temporalmente para testing
```

#### 3. **Error de Análisis Visual**

```bash
# Síntoma: "Error procesando imagen"
# Causa: Imagen corrupta o formato no soportado

# Verificar formatos soportados:
file /path/to/image.jpg
identify /path/to/image.jpg

# Formatos válidos: JPEG, PNG, TIFF
# Tamaño máximo: 10MB
# Resolución mínima: 640x480
```

#### 4. **Problemas de Conectividad**

```bash
# Verificar servicios
sudo systemctl status smartcompute
sudo systemctl status smartcompute-worker

# Verificar puertos
sudo netstat -tlnp | grep :3000
sudo netstat -tlnp | grep :3001

# Verificar logs
sudo tail -f /var/log/smartcompute/system.log
sudo tail -f /var/log/smartcompute/error.log
```

### 📊 Diagnóstico del Sistema

```bash
# Script de diagnóstico completo
#!/bin/bash
echo "=== DIAGNÓSTICO SMARTCOMPUTE INDUSTRIAL ==="

echo "1. Estado de servicios:"
systemctl is-active smartcompute
systemctl is-active smartcompute-worker

echo "2. Uso de recursos:"
echo "CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "RAM: $(free -m | awk 'NR==2{printf "%.1f%%", $3*100/$2}')"
echo "Disco: $(df -h /opt/smartcompute | awk 'NR==2{print $5}')"

echo "3. Conectividad:"
nc -zv localhost 3000
nc -zv localhost 3001

echo "4. Base de datos:"
sqlite3 /opt/smartcompute/data/smartcompute.db ".tables"

echo "5. Últimos logs de error:"
tail -5 /var/log/smartcompute/error.log

echo "=== FIN DIAGNÓSTICO ==="
```

---

## 📞 Soporte Técnico

### Niveles de Soporte

#### **🟢 Soporte Básico (Incluido)**
- ✅ Documentación completa
- ✅ FAQ y guías de resolución
- ✅ Soporte por email (48h respuesta)
- ✅ Actualizaciones de seguridad

#### **🟡 Soporte Profesional ($199/mes)**
- ✅ Todo lo anterior +
- ✅ Chat en vivo 8x5
- ✅ Asistencia remota
- ✅ Tiempo de respuesta: 4 horas
- ✅ Actualizaciones prioritarias

#### **🔴 Soporte Enterprise ($499/mes)**
- ✅ Todo lo anterior +
- ✅ Soporte 24x7x365
- ✅ Ingeniero dedicado
- ✅ Tiempo de respuesta: 1 hora
- ✅ Desarrollo personalizado
- ✅ Integración con sistemas existentes

### Contacto de Emergencia

| Canal | Disponibilidad | Tiempo de Respuesta |
|-------|---------------|---------------------|
| **🚨 Emergencias** | 24x7 | < 30 minutos |
| **📧 Email** | Lun-Vie 9-18 | < 4 horas |
| **💬 Chat** | Lun-Vie 9-18 | < 15 minutos |
| **📞 Teléfono** | Lun-Vie 9-18 | Inmediato |

**📧 Email:** ggwre04p0@mozmail.com
**🔗 LinkedIn:** https://www.linkedin.com/in/martín-iribarne-swtf/
**📞 Emergencias:** +54 911 234567

### Información para Reportes de Bugs

Incluir siempre:

```bash
# 1. Versión del sistema
cat /opt/smartcompute/VERSION.json

# 2. Logs relevantes
sudo journalctl -u smartcompute --since "1 hour ago"

# 3. Configuración sanitizada (sin secretos)
sudo grep -v "secret\|password\|token" /etc/smartcompute/config.ini

# 4. Estado del sistema
sudo systemctl status smartcompute --no-pager -l
```

---

## 📋 Checklist de Implementación

### ✅ Pre-Implementación

- [ ] Hardware cumple requisitos mínimos
- [ ] Red industrial separada de red corporativa
- [ ] Backup del sistema existente
- [ ] Plan de rollback definido
- [ ] Personal capacitado en el sistema

### ✅ Configuración de Seguridad

- [ ] Claves JWT y AES-256 generadas únicamente
- [ ] Secretos TOTP configurados por operador
- [ ] Ubicaciones GPS definidas y verificadas
- [ ] Firewall configurado correctamente
- [ ] Certificados SSL válidos instalados

### ✅ Testing

- [ ] Autenticación 2FA probada
- [ ] Verificación GPS validada
- [ ] Análisis visual funcionando
- [ ] Flujo de aprobaciones operativo
- [ ] Notificaciones llegando correctamente

### ✅ Go-Live

- [ ] Personal entrenado
- [ ] Procedimientos de emergencia definidos
- [ ] Contactos de soporte configurados
- [ ] Monitoreo implementado
- [ ] Plan de mantenimiento establecido

---

**© 2025 SmartCompute Industrial. Todos los derechos reservados.**

*Esta documentación es confidencial y está destinada únicamente para uso autorizado en instalaciones industriales licenciadas.*