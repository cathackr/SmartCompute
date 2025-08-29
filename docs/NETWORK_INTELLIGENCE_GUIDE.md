# SmartCompute Network Intelligence System

## 🌐 Descripción General

El **SmartCompute Network Intelligence System** es un sistema de **monitoreo pasivo e inteligencia local** diseñado específicamente para entornos industriales. Observa, analiza y sugiere, pero nunca modifica automáticamente la infraestructura de red. Mantiene toda la información dentro del segmento de red local sin enviar datos al exterior.

## 🎯 Filosofía del Sistema

### ✅ **Lo que SÍ hace SmartCompute:**
- **Monitorea pasivamente** la red sin interferir con operaciones
- **Descubre dispositivos** automáticamente mediante escaneo no intrusivo
- **Analiza protocolos** industriales para detectar patrones
- **Detecta conflictos** de IP, MAC y VLAN automáticamente
- **Sugiere optimizaciones** basadas en análisis local
- **Aprende patrones** localmente para mejorar recomendaciones
- **Genera alertas** que requieren acción del administrador
- **Mantiene datos locales** sin conectividad externa

### ❌ **Lo que NO hace:**
- **No modifica configuraciones** de red automáticamente
- **No envía información** a internet o redes externas
- **No toma acciones correctivas** sin autorización del administrador
- **No cambia reglas** de firewall o switch automáticamente
- **No comparte datos** con servicios cloud o externos
- **No implementa cambios** sugeridos sin intervención humana

## ✨ Características Principales

### 🔍 **Monitoreo Pasivo Inteligente**
- **Escaneo no intrusivo**: Descubrimiento de dispositivos sin impacto
- **Análisis de tráfico**: Observación de patrones sin modificar flujos
- **Detección de anomalías**: Identificación de comportamientos inusuales
- **Aprendizaje local**: Mejora de precisión basada en patrones observados

### 📡 **Análisis Multi-Protocolo Industrial**
```
Protocolos Monitoreados:
├── Modbus TCP (Puerto 502)
│   ├── Análisis de códigos de función
│   ├── Monitoreo de registros accedidos
│   └── Detección de tráfico anómalo
├── PROFINET (Ethernet Type 0x8892)
│   ├── Frames RT en tiempo real
│   ├── Tiempos de ciclo
│   └── Calidad de comunicación
├── EtherNet/IP (Puerto 44818)
│   ├── Comandos CIP
│   ├── Sesiones activas
│   └── Estado de conexiones
└── OPC UA (Puerto 4840)
    ├── Servicios activos
    ├── Sesiones de cliente
    └── Certificados utilizados
```

### 🏭 **Clasificación Inteligente de Dispositivos**
- **PLCs**: Detectados por puertos Modbus, S7, EtherNet/IP
- **HMIs**: Identificados por servicios web y VNC
- **Switches**: Reconocidos por SNMP y múltiples conexiones
- **Servidores**: Clasificados por servicios empresariales
- **Dispositivos I/O**: Detectados por protocolos específicos

### 🚨 **Sistema de Alertas y Recomendaciones**
```json
{
  "alert_type": "ip_conflict",
  "severity": "high",
  "message": "Conflicto IP detectado - ACCIÓN REQUERIDA: El administrador debe verificar la configuración de red",
  "details": {
    "conflicting_devices": ["PLC-Line-1", "HMI-Station-2"],
    "suggested_action": "Revisar configuración DHCP o asignar IPs estáticas únicas",
    "automated_action": "none - monitoring only",
    "requires_admin_action": true
  }
}
```

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────┐
│              Network Intelligence Dashboard              │
├─────────────────────────────────────────────────────────┤
│  • Visualización de topología en tiempo real            │
│  • Alertas de conflictos y recomendaciones             │
│  • Métricas de rendimiento y análisis de protocolos    │
│  • Panel de configuración para administradores         │
└─────────────────────────────────────────────────────────┘
                           ↕ REST API Local
┌─────────────────────────────────────────────────────────┐
│                Network Intelligence API                 │
├─────────────────────────────────────────────────────────┤
│  • Endpoints de descubrimiento de dispositivos         │
│  • Servicios de análisis de protocolos                 │
│  • Gestión de alertas y recomendaciones               │
│  • Métricas de rendimiento y conflictos               │
└─────────────────────────────────────────────────────────┘
                           ↕ Análisis Local
┌─────────────────────────────────────────────────────────┐
│              Core Intelligence Engine                   │
├─────────────────────────────────────────────────────────┤
│  • NetworkIntelligenceAnalyzer                         │
│    - Escaneo pasivo de múltiples subredes             │
│    - Clasificación automática de dispositivos          │
│    - Detección de conflictos IP/MAC/VLAN              │
│    - Correlación de problemas de rendimiento          │
│                                                        │
│  • LocalThreatAnalyzer                                 │
│    - Análisis de patrones locales                     │
│    - Aprendizaje sin conexión externa                 │
│    - Generación de recomendaciones inteligentes       │
│                                                        │
│  • IndustrialProtocolAnalyzer                          │
│    - Parser Modbus TCP/RTU                            │
│    - Análisis PROFINET RT                             │
│    - Decodificación EtherNet/IP CIP                   │
└─────────────────────────────────────────────────────────┘
                           ↕ Monitoreo Pasivo
┌─────────────────────────────────────────────────────────┐
│                 Red Industrial Local                   │
├─────────────────────────────────────────────────────────┤
│  🏭 Dispositivos de Automatización                     │
│  🌐 Infraestructura de Red                            │
│  🛡️ Dispositivos de Seguridad (solo lectura)          │
│  📡 Equipos de Comunicación                           │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Instalación y Configuración

### Requisitos Mínimos
```bash
# Sistema operativo: Linux (Ubuntu 18.04+ / CentOS 7+)
uname -a

# Python 3.8 o superior
python3 --version

# Permisos de red para escaneo (recomendado)
sudo -v

# Espacio en disco: 1GB para logs y datos locales
df -h
```

### Instalación Rápida
```bash
# 1. Navegar al directorio SmartCompute Industrial
cd /ruta/a/smartcompute/smartcompute_industrial

# 2. Instalar dependencias
pip3 install fastapi uvicorn scapy psutil ipaddress

# 3. Ejecutar sistema (con permisos para escaneo completo)
sudo ./start_network_intelligence.sh

# 4. Acceder al dashboard
# http://127.0.0.1:8002
```

### Configuración de Escaneo
```bash
# Configurar subredes específicas para monitoreo
curl -X POST "http://127.0.0.1:8002/api/network/scan" \
  -H "Content-Type: application/json" \
  -d '{
    "subnets": [
      "192.168.100.0/24",  # Red de PLCs
      "192.168.200.0/24",  # Red de HMIs
      "10.0.1.0/24"        # Red de servidores
    ],
    "scan_ports": [22, 80, 443, 502, 44818, 4840, 102, 161]
  }'
```

## 📊 Usando el Dashboard

### 1. **Vista de Topología de Red**
- **Mapa visual automático**: Dispositivos organizados por tipo y subred
- **Iconografía clara**: PLCs (🏭), Switches (🔀), Servidores (🖥️)
- **Estado en tiempo real**: Colores indican estado de conectividad
- **Filtrado inteligente**: Por protocolo, tipo de dispositivo, o subred

### 2. **Panel de Dispositivos Descubiertos**
```json
{
  "ip_address": "192.168.100.50",
  "mac_address": "00:1a:2b:3c:4d:5e",
  "hostname": "PLC-Linea-Produccion-1",
  "device_type": "plc",
  "vendor": "Siemens",
  "protocols": ["modbus_tcp", "s7"],
  "open_ports": [22, 102, 502],
  "response_time_ms": 2.3,
  "last_seen": "2024-08-29T15:30:00Z",
  "security_notes": "Puerto Modbus abierto - normal para PLC"
}
```

### 3. **Análisis de Protocolos Industriales**
```javascript
// Dashboard muestra distribución de protocolos
{
  "protocol_distribution": {
    "modbus_tcp": {
      "device_count": 12,
      "percentage": 45.2,
      "security_status": "open_ports_normal",
      "performance_status": "optimal"
    },
    "profinet": {
      "device_count": 8,
      "percentage": 30.1,
      "cycle_time_average": "4ms",
      "real_time_performance": "excellent"
    },
    "ethernet_ip": {
      "device_count": 6,
      "percentage": 24.7,
      "active_sessions": 18,
      "cip_performance": "good"
    }
  }
}
```

### 4. **Alertas y Recomendaciones del Administrador**
```
🔴 CRÍTICO - ACCIÓN REQUERIDA
   Conflicto IP: 192.168.100.25 usado por PLC y HMI
   Sugerencia: Asignar IP estática única al PLC
   Acción automática: Ninguna - requiere intervención del administrador

🟡 MEDIO - REVISIÓN RECOMENDADA  
   Alta latencia en dispositivo 192.168.100.50 (150ms)
   Sugerencia: Verificar cableado de red o configuración de switch
   Impacto: Posible degradación de comunicación industrial

🟢 INFO - OPTIMIZACIÓN DISPONIBLE
   Frecuencia de polling Modbus muy alta (10ms)
   Sugerencia: Considerar aumentar a 50ms para reducir tráfico
   Beneficio: Reducción del 60% en uso de ancho de banda
```

## 🔧 Gestión de Conflictos de Red

### Detección Automática de Conflictos IP
```python
# El sistema detecta automáticamente:
detected_conflicts = {
    "ip_conflicts": {
        "192.168.1.100": {
            "devices": [
                {"mac": "00:1a:2b:3c:4d:5e", "name": "PLC-Principal"},
                {"mac": "00:1a:2b:3c:4d:5f", "name": "HMI-Operador"}
            ],
            "first_detected": "2024-08-29T10:30:00Z",
            "admin_action": "Asignar IPs estáticas diferentes",
            "impact_level": "high",
            "automated_resolution": "none - requires admin"
        }
    }
}
```

### Análisis de Problemas VLAN
```python
vlan_analysis = {
    "vlan_100_production": {
        "issue": "Tipos mixtos de dispositivos en VLAN de producción",
        "devices_found": [
            {"type": "plc", "count": 8},
            {"type": "office_pc", "count": 3},
            {"type": "printer", "count": 1}
        ],
        "security_risk": "medium",
        "recommendation": "Aislar PLCs en VLAN dedicada",
        "admin_action_required": true
    }
}
```

### Detección de Problemas MAC
```python
mac_issues = {
    "duplicate_mac_addresses": [
        {
            "mac_address": "00:1a:2b:3c:4d:5e",
            "devices": ["192.168.1.100", "192.168.1.101"],
            "probable_cause": "Dispositivos clonados o problema de switch",
            "admin_action": "Verificar configuración física de red"
        }
    ]
}
```

## 📈 API Reference Completa

### Descubrimiento de Dispositivos
```http
GET /api/network/devices
Query Parameters:
  - device_type: plc|hmi|switch|router|server
  - protocol: modbus_tcp|profinet|ethernet_ip|opcua
  - subnet: 192.168.1.0/24

Response:
{
  "devices": [{
    "ip_address": "192.168.100.50",
    "mac_address": "00:1a:2b:3c:4d:5e",
    "hostname": "PLC-Linea-1", 
    "device_type": "plc",
    "vendor": "Siemens",
    "protocols": ["modbus_tcp", "s7"],
    "open_ports": [22, 102, 502],
    "response_time_ms": 2.3,
    "security_assessment": "standard_industrial_device",
    "admin_notes": "Puerto Modbus normal para PLC"
  }],
  "discovery_status": "active",
  "last_scan": "2024-08-29T15:30:00Z"
}
```

### Recomendaciones Inteligentes
```http
GET /api/network/recommendations

Response:
{
  "recommendations": [{
    "type": "performance",
    "priority": "medium",
    "device_ip": "192.168.100.50",
    "issue": "High latency detected (150.2ms)",
    "suggestion": "Administrator should check network path to device",
    "automated_action": "none - monitoring only", 
    "requires_admin": true,
    "potential_impact": "Communication delays in production line",
    "suggested_timeline": "Review within 4 hours"
  }],
  "note": "SmartCompute provides recommendations only. All actions require administrator approval."
}
```

### Análisis Local de Amenazas
```http
POST /api/network/threats/analyze
Content-Type: application/json

{
  "threat_type": "unusual_modbus_traffic",
  "device_ip": "192.168.100.25", 
  "severity": "medium",
  "details": {
    "function_codes": ["0x90", "0x91"],
    "frequency": "unusual_high"
  }
}

Response:
{
  "message": "Threat analyzed locally",
  "analysis": {
    "administrative_recommendations": [{
      "type": "security_review",
      "message": "Unusual Modbus function codes detected",
      "action_required": "Administrator should verify device programming",
      "urgency": "medium"
    }]
  },
  "external_sharing": "disabled - local analysis only",
  "admin_action_required": true
}
```

### Conflictos de Red
```http
GET /api/network/conflicts

Response:
{
  "conflicts": [{
    "timestamp": "2024-08-29T15:25:00Z",
    "conflict_type": "ip_conflict",
    "severity": "high",
    "message": "IP conflict detected - ACCIÓN REQUERIDA: El administrador debe verificar la configuración de red",
    "details": {
      "ip_address": "192.168.1.100",
      "conflicting_macs": ["00:1a:2b:3c:4d:5e", "00:1a:2b:3c:4d:5f"],
      "requires_admin_action": true,
      "suggested_action": "Revisar configuración DHCP o asignar IPs estáticas únicas",
      "automated_action": "none - monitoring only"
    }
  }],
  "admin_note": "Todos los conflictos requieren acción manual del administrador"
}
```

## 🛠️ Casos de Uso Prácticos

### 1. **Auditoría de Red Industrial**
```bash
# Script para generar reporte completo de seguridad
#!/bin/bash

echo "=== SmartCompute Network Security Audit ==="

# Obtener dispositivos con puertos industriales abiertos
curl -s "http://127.0.0.1:8002/api/network/devices?protocol=modbus_tcp" | \
  jq '.devices[] | select(.open_ports[] == 502) | {ip: .ip_address, type: .device_type, vendor: .vendor}'

# Verificar conflictos activos
curl -s "http://127.0.0.1:8002/api/network/conflicts" | \
  jq '.conflicts[] | select(.resolved == false)'

# Obtener recomendaciones de seguridad
curl -s "http://127.0.0.1:8002/api/network/recommendations" | \
  jq '.recommendations[] | select(.type == "security")'
```

### 2. **Monitoreo de Rendimiento de Producción**
```python
import requests
import json
from datetime import datetime

def monitor_production_network():
    """Monitorear red de producción y generar alertas"""
    
    # Obtener métricas de rendimiento
    response = requests.get("http://127.0.0.1:8002/api/network/performance?hours=1")
    metrics = response.json()
    
    # Identificar dispositivos con problemas
    problematic_devices = []
    for metric in metrics["metrics"]:
        if metric["latency_ms"] > 100:
            problematic_devices.append({
                "device_ip": metric["device_ip"],
                "issue": f"High latency: {metric['latency_ms']}ms",
                "admin_action": "Verify network infrastructure",
                "impact": "Production communication delays possible"
            })
    
    # Generar reporte para administrador
    if problematic_devices:
        print("⚠️ NETWORK PERFORMANCE ISSUES DETECTED")
        print("Administrator action required:")
        for device in problematic_devices:
            print(f"  • {device['device_ip']}: {device['issue']}")
            print(f"    Action: {device['admin_action']}")
    
    return problematic_devices
```

### 3. **Optimización de Comunicación Industrial**
```python
def analyze_protocol_efficiency():
    """Analizar eficiencia de protocolos y sugerir optimizaciones"""
    
    # Obtener análisis de protocolos
    response = requests.get("http://127.0.0.1:8002/api/network/protocols")
    protocols = response.json()
    
    optimization_suggestions = []
    
    for protocol, data in protocols["protocols"].items():
        if protocol == "modbus_tcp" and data["device_count"] > 10:
            optimization_suggestions.append({
                "protocol": protocol,
                "current_devices": data["device_count"],
                "suggestion": "Consider implementing Modbus gateway for device consolidation",
                "benefit": "Reduce network traffic and improve response times",
                "admin_action": "Evaluate Modbus gateway implementation",
                "automated_implementation": "No - requires network architecture review"
            })
    
    return {
        "suggestions": optimization_suggestions,
        "note": "All optimizations require administrator evaluation and implementation"
    }
```

## 📋 Mejores Prácticas

### Implementación de Monitoreo Pasivo
1. **Configuración inicial**: Definir subredes críticas para monitoreo
2. **Establecer baselines**: Permitir 24-48 horas para aprendizaje inicial
3. **Configurar alertas**: Ajustar umbrales según criticidad del entorno
4. **Revisión regular**: Evaluar recomendaciones semanalmente
5. **Documentar acciones**: Mantener registro de cambios implementados

### Seguridad de la Información
1. **Acceso local únicamente**: Sin conectividad a internet
2. **Datos encriptados**: Información sensible protegida localmente
3. **Logs auditables**: Registro completo de actividades de monitoreo
4. **Acceso controlado**: Dashboard accesible solo desde red interna
5. **Respaldos locales**: Datos críticos respaldados en el mismo segmento

### Gestión de Recomendaciones
1. **Priorización**: Revisar alertas críticas inmediatamente
2. **Validación**: Verificar recomendaciones antes de implementar
3. **Pruebas**: Implementar cambios en ambiente de prueba primero
4. **Monitoreo post-cambio**: Verificar mejoras después de implementar
5. **Retroalimentación**: Usar resultados para mejorar el sistema

---

**SmartCompute Network Intelligence System**  
*Monitoreo inteligente, recomendaciones precisas, control total del administrador*