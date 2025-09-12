# 🔒 SmartCompute Security Guide

<div align="center">
  <img src="../assets/smartcompute_hmi_logo.png" alt="SmartCompute Security" width="200">
  
  **Version 1.0.0-beta** | **Enterprise-Grade Security Implementation**
  
  [🇪🇸 Español](#) | [🇺🇸 English](#) | [🚀 Quick Start](QUICK_START_GUIDE.md) | [💼 Enterprise](ENTERPRISE_GUIDE.md)
</div>

---

## 🎯 Security Overview

SmartCompute implementa **seguridad de nivel empresarial** por defecto desde la versión v1.0.0-beta. Este documento cubre todas las medidas de seguridad implementadas y cómo configurarlas correctamente.

### 🏆 **Puntuación de Seguridad: 8.6/10 (Enterprise Grade)**

- 🟢 **Exposición de Red**: 9/10 - Solo localhost, proxy HTTPS
- 🟢 **Gestión de Credenciales**: 9/10 - Variables entorno + validación
- 🟢 **Monitoreo**: 8/10 - Detección tiempo real + logs auditoría
- 🟢 **Cifrado/TLS**: 9/10 - HTTPS obligatorio + certificados
- 🟢 **Rate Limiting**: 8/10 - APIs protegidas contra ataques

---

## 🛡️ Medidas de Seguridad Implementadas

### 1. **🔐 Gestión Segura de Credenciales**

**❌ ANTES (Vulnerable):**
```python
# ⚠️ NUNCA hacer esto - credenciales en código
access_token = "APP_USR-123456789"
database_password = "admin123"
```

**✅ DESPUÉS (Seguro):**
```python
# ✅ Variables de entorno con validación
access_token = os.getenv("MP_ACCESS_TOKEN")
if not access_token:
    raise ValueError("🚨 MP_ACCESS_TOKEN no configurado")
```

**Configuración en `.env`:**
```bash
# MercadoPago Production Keys
MP_ACCESS_TOKEN=tu-token-real-mercadopago
MP_PUBLIC_KEY=tu-clave-publica

# Database Passwords (32+ caracteres)
POSTGRES_PASSWORD=OTul#LNES3mfsh8EbOY8SuyItay1sX3s
REDIS_PASSWORD=ao!fTsVjcrk10kEIpo4RKvH^b0CsXCF*

# API Security (64+ caracteres)  
JWT_SECRET_KEY=TYYp71tyUEh1zN9ZGw18ZAC3rJmJLA3s092USZa3dsUptVglaFlc0hWz033rwAZg
WEBHOOK_SECRET=CNBrUVIF49GNvBnyFAIHRYMYBgHpAhiT2RuZ7EUn6Tpr2fXxyt9qZi3gBTEVYKeJ
```

### 2. **🌐 Exposición de Servicios Corregida**

**❌ ANTES (Vulnerable):**
```python
# ⚠️ Accesible desde cualquier IP en internet
uvicorn.run(app, host="0.0.0.0", port=8003)
```

**✅ DESPUÉS (Seguro):**
```python
# ✅ Solo localhost - usar nginx como proxy
uvicorn.run(app, host="127.0.0.1", port=8003)
```

### 3. **🔒 Nginx Proxy Reverso con TLS**

SmartCompute utiliza nginx como proxy reverso seguro:

```nginx
# Configuración en nginx/smartcompute-secure.conf
server {
    listen 443 ssl http2;
    server_name smartcompute.local;
    
    # SSL/TLS Configuration
    ssl_certificate /etc/nginx/ssl/smartcompute.crt;
    ssl_certificate_key /etc/nginx/ssl/smartcompute.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    
    # Rate Limiting
    location /api/payments {
        limit_req zone=payment_limit burst=2 nodelay;
        proxy_pass http://127.0.0.1:8003;
    }
    
    location /enterprise {
        limit_req zone=dashboard_limit burst=10 nodelay;
        proxy_pass http://127.0.0.1:8000;
    }
}
```

### 4. **📊 Monitoreo de Seguridad 24/7**

El sistema incluye un monitor de seguridad que detecta:

- ✅ **Integridad de archivos**: Cambios en `.env`, `secret.key`, archivos críticos
- ✅ **Procesos sospechosos**: Mining, malware, alto uso CPU
- ✅ **Conexiones de red**: Acceso externo a puertos internos
- ✅ **Salud de servicios**: APIs caídas o con errores

---

## 🚀 Configuración de Seguridad

### **Paso 1: Configurar Variables de Entorno**

```bash
# 1. Crear archivo de configuración
cp .env.example .env

# 2. Generar passwords seguras
echo "POSTGRES_PASSWORD=$(openssl rand -base64 32)" >> .env
echo "REDIS_PASSWORD=$(openssl rand -base64 32)" >> .env  
echo "JWT_SECRET_KEY=$(openssl rand -base64 64)" >> .env
echo "WEBHOOK_SECRET=$(openssl rand -base64 64)" >> .env

# 3. Configurar credenciales de pago (si usas pagos)
echo "MP_ACCESS_TOKEN=tu-token-mercadopago-real" >> .env
echo "PAYMENT_HASH_SECRET=$(openssl rand -base64 64)" >> .env
```

### **Paso 2: Configurar Nginx (Recomendado para Producción)**

```bash
# Configurar nginx con TLS y rate limiting
sudo scripts/setup-nginx-security.sh

# Esto configura automáticamente:
# ✅ Certificados TLS autofirmados
# ✅ Rate limiting por endpoint
# ✅ Firewall con ufw
# ✅ Headers de seguridad
# ✅ Bloqueo de puertos internos
```

### **Paso 3: Iniciar con Monitoreo de Seguridad**

```bash
# Iniciar todos los servicios con monitoreo
scripts/start-security-monitoring.sh

# Esto inicia:
# 🔒 Monitor de seguridad en background
# 📊 Dashboard Enterprise (puerto 8000)
# 📡 Network API (puerto 8002) 
# 🔄 Token API (puerto 8001)
# 💳 Payment API (puerto 8003, si configurado)
```

---

## 🛠️ Comandos de Monitoreo

### **Ver Estado de Seguridad**
```bash
# Reporte de seguridad completo
python3 security/security_monitor.py --report

# Logs de seguridad en tiempo real  
tail -f security/logs/security_events.log

# Verificar integridad de archivos
grep "file_integrity" security/logs/security_events.log
```

### **Verificar Configuración de Red**
```bash
# Verificar que servicios solo escuchen en localhost
sudo netstat -tulpn | grep ":800[0-3]"

# Verificar firewall está activo
sudo ufw status

# Probar acceso HTTPS
curl -k https://localhost/enterprise
```

### **Monitoreo de Procesos**
```bash
# Ver procesos de SmartCompute
ps aux | grep smartcompute

# Verificar uso de recursos
top -p $(pgrep -d, -f smartcompute)
```

---

## 🚨 Alertas de Seguridad

### **Configurar Webhooks**
```bash
# Agregar webhook para alertas críticas
echo "SECURITY_WEBHOOK_URL=https://hooks.slack.com/tu-webhook" >> .env

# Configurar email de alertas
echo "SECURITY_EMAIL_ALERTS=admin@tuempresa.com,security@tuempresa.com" >> .env
```

### **Tipos de Alertas**

| **Tipo de Evento** | **Severidad** | **Descripción** |
|-------------------|---------------|-----------------|
| `file_integrity_violation` | 🔴 HIGH | Archivo crítico modificado |
| `suspicious_process` | 🔴 CRITICAL | Proceso de mining/malware detectado |
| `external_connection_to_internal_port` | 🔴 CRITICAL | Conexión externa a puerto interno |
| `service_unavailable` | 🟡 MEDIUM | Servicio SmartCompute caído |
| `high_cpu_usage` | 🟡 MEDIUM | Proceso con >90% CPU |

---

## 🔧 Resolución de Problemas

### **Error: "Falta configuración crítica"**
```bash
# El sistema validará que existan las variables críticas
🚨 FALTA CONFIGURACIÓN CRÍTICA: ['MP_ACCESS_TOKEN']. Revisar archivo .env

# Solución: Configurar la variable faltante
echo "MP_ACCESS_TOKEN=tu-token-real" >> .env
```

### **Error: "Puerto ya en uso"**
```bash
# Si hay conflictos de puertos
sudo netstat -tulpn | grep ":8000"
sudo kill -9 $(lsof -t -i:8000)
```

### **Error: "Certificado SSL inválido"**
```bash
# Regenerar certificados
sudo rm /etc/nginx/ssl/smartcompute.*
sudo scripts/setup-nginx-security.sh
```

---

## 📋 Checklist de Seguridad

### **✅ Pre-Producción**
- [ ] Archivo `.env` configurado con credenciales reales
- [ ] Passwords de 32+ caracteres generadas
- [ ] `.env` agregado a `.gitignore` 
- [ ] Nginx configurado con TLS
- [ ] Firewall habilitado y configurado
- [ ] Monitor de seguridad funcionando

### **✅ Post-Despliegue**
- [ ] Servicios solo accesibles via HTTPS
- [ ] Puertos internos (8000-8003) bloqueados desde externa
- [ ] Rate limiting funcionando
- [ ] Logs de seguridad generándose
- [ ] Alertas de seguridad configuradas
- [ ] Monitoreo 24/7 activo

---

## 🆘 Soporte de Seguridad

Para reportar vulnerabilidades de seguridad:

- **📧 Email**: security@smartcompute.ar
- **🔗 LinkedIn**: [Martín Iribarne CEH](https://www.linkedin.com/in/martín-iribarne-swtf/)
- **🐙 GitHub Issues**: [Reportar vulnerabilidad](https://github.com/cathackr/SmartCompute/security)

### **⏰ SLA de Respuesta:**
- 🔴 **Crítico**: 4 horas
- 🟡 **Alto**: 24 horas  
- 🟢 **Medio/Bajo**: 72 horas

---

© 2024 SmartCompute Security Team. Todos los derechos reservados.

<div align="center">

**🔒 Tu seguridad es nuestra prioridad**

[📚 Documentación](TECHNICAL_DOCUMENTATION.md) • [🚀 Quick Start](QUICK_START_GUIDE.md) • [💼 Enterprise](ENTERPRISE_GUIDE.md)

</div>