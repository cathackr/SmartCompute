# 🏢 SmartCompute Enterprise MCP Integration

## 🎯 **Visión General**

Esta documentación describe la integración MCP (Model Context Protocol) + HRM (Human Resource Management) para **SmartCompute Enterprise**, proporcionando capacidades avanzadas de auto-scaling, load balancing inteligente y disaster recovery multi-región.

### **¿Qué es MCP + HRM?**
- **MCP**: Protocolo estándar para comunicación entre modelos y aplicaciones
- **HRM**: Sistema de análisis avanzado de SmartCompute con ML y análisis comportamental
- **Integración**: Combina la estandarización MCP con la inteligencia específica de ciberseguridad HRM

---

## 🏗️ **Arquitectura de la Integración**

```
┌─────────────────────────────────────────────────────────────────┐
│                     SmartCompute Enterprise                     │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐ │
│  │   MCP Server    │    │  MCP-HRM Bridge │    │ Orchestrator │ │
│  │   (WebSocket)   │◄──►│   (Protocol)    │◄──►│ (Enterprise) │ │
│  └─────────────────┘    └─────────────────┘    └──────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                       HRM Components                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Integrated      │  │ Stream          │  │ Threat          │ │
│  │ Analysis        │  │ Processor       │  │ Intelligence    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                    Enterprise Features                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ XDR Export      │  │ SIEM Export     │  │ Multi-Region    │ │
│  │ (Existing)      │  │ (Existing)      │  │ DR              │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 **Instalación y Configuración**

### **Prerequisitos**
```bash
# Python 3.8+ requerido
python3 --version

# Dependencias adicionales
pip install websockets aiohttp

# Verificar HRM prototype disponible
ls -la smartcompute_hrm_proto/
```

### **1. Instalación Básica**
```bash
# 1. Crear directorio enterprise si no existe
mkdir -p enterprise/

# 2. Los archivos principales ya están creados:
# - enterprise/mcp_hrm_bridge.py
# - enterprise/mcp_enterprise_orchestrator.py
# - enterprise/mcp_server.py

# 3. Verificar integración HRM
cd enterprise/
python3 -c "import sys; sys.path.append('../smartcompute_hrm_proto/python'); import integrated_analysis; print('HRM integration: OK')"
```

### **2. Configuración del Servidor MCP**
```bash
# Iniciar servidor MCP básico
python3 mcp_server.py --host localhost --port 8080 --log-level INFO

# Con orquestador Enterprise habilitado
python3 mcp_server.py --host 0.0.0.0 --port 8080 --max-connections 200

# Solo bridge HRM (sin orquestador)
python3 mcp_server.py --disable-orchestrator
```

### **3. Configuración Avanzada**
```python
# config/enterprise_config.py
ENTERPRISE_CONFIG = {
    "regions": {
        "us-east-1": {"primary": True, "capacity": 10},
        "eu-west-1": {"primary": False, "capacity": 8},
        "ap-southeast-1": {"primary": False, "capacity": 6}
    },
    "scaling_thresholds": {
        "cpu_threshold": 70.0,
        "memory_threshold": 80.0,
        "threat_queue_threshold": 50,
        "response_time_threshold": 500
    },
    "business_hours": {
        "start": 8, "end": 18,
        "timezone": "UTC"
    },
    "disaster_recovery": {
        "rto_minutes": 15,
        "rpo_minutes": 1,
        "auto_failover": True
    }
}
```

---

## 🔧 **Uso y Ejemplos**

### **1. Análisis de Amenaza Básico**
```python
import asyncio
import json
from mcp_hrm_bridge import create_mcp_hrm_bridge, MCPRequest

async def test_threat_analysis():
    bridge = create_mcp_hrm_bridge()

    request = MCPRequest(
        method="smartcompute/analyze_threat",
        params={
            "event": {
                "event_id": "enterprise_001",
                "timestamp": "2024-01-15T10:30:00Z",
                "event_type": "process_injection",
                "source_ip": "192.168.1.100",
                "target_process": "explorer.exe",
                "severity": "high"
            },
            "business_context": {
                "business_unit": "finance",
                "compliance_frameworks": ["SOX", "PCI-DSS"],
                "asset_criticality": "high",
                "risk_tolerance": "low"
            }
        }
    )

    response = await bridge.handle_mcp_request(request)
    print(json.dumps(response.result, indent=2))

# Ejecutar
asyncio.run(test_threat_analysis())
```

### **2. Orquestación Enterprise Completa**
```python
from mcp_enterprise_orchestrator import create_mcp_enterprise_orchestrator

async def test_enterprise_orchestration():
    orchestrator = create_mcp_enterprise_orchestrator()
    await orchestrator.start_orchestration()

    # Procesar amenaza empresarial
    result = await orchestrator.process_enterprise_threat(
        threat_event={
            "event_id": "apt_001",
            "event_type": "advanced_persistent_threat",
            "target_system": "financial_db_server",
            "indicators": ["unusual_network_traffic", "privilege_escalation"]
        },
        business_context={
            "business_unit": "finance",
            "compliance_frameworks": ["SOX"],
            "asset_criticality": "critical"
        }
    )

    print("Orchestration Result:")
    print(json.dumps(result, indent=2))

    await orchestrator.stop_orchestration()

asyncio.run(test_enterprise_orchestration())
```

### **3. Cliente WebSocket**
```python
import asyncio
import websockets
import json

async def mcp_client():
    uri = "ws://localhost:8080"

    async with websockets.connect(uri) as websocket:
        # Inicializar cliente
        init_message = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "clientInfo": {
                    "name": "SmartCompute Client",
                    "version": "1.0.0"
                },
                "capabilities": {}
            },
            "id": "init-1"
        }

        await websocket.send(json.dumps(init_message))
        response = await websocket.recv()
        print("Initialization:", json.loads(response))

        # Analizar amenaza
        threat_request = {
            "jsonrpc": "2.0",
            "method": "smartcompute/analyze_threat",
            "params": {
                "event": {
                    "event_id": "client_test_001",
                    "event_type": "malware_detection",
                    "severity": "medium"
                }
            },
            "id": "threat-1"
        }

        await websocket.send(json.dumps(threat_request))
        response = await websocket.recv()
        print("Threat Analysis:", json.loads(response))

asyncio.run(mcp_client())
```

---

## 📊 **Métodos MCP Disponibles**

### **Namespace: smartcompute/**

| **Método** | **Descripción** | **Parámetros** |
|------------|-----------------|----------------|
| `smartcompute/analyze_threat` | Análisis de amenaza con HRM | `event`, `business_context`, `options` |
| `smartcompute/enterprise_context` | Análisis de contexto empresarial | `business_unit`, `compliance_frameworks` |
| `smartcompute/stream_events` | Procesamiento de eventos en stream | `stream_config`, `events` |
| `smartcompute/get_metrics` | Métricas del bridge | - |
| `smartcompute/health_check` | Health check del sistema | - |

### **Namespace: orchestrator/**

| **Método** | **Descripción** | **Parámetros** |
|------------|-----------------|----------------|
| `orchestrator/process_threat` | Orquestación completa Enterprise | `threat_event`, `business_context` |
| `orchestrator/status` | Estado del orquestador | - |
| `orchestrator/scaling_history` | Historial de escalado | - |

### **MCP Estándar**

| **Método** | **Descripción** | **Soporte** |
|------------|-----------------|-------------|
| `initialize` | Inicialización MCP | ✅ Completo |
| `tools/list` | Listar herramientas | ✅ SmartCompute tools |
| `tools/call` | Ejecutar herramienta | ✅ Threat analysis, Orchestration |
| `resources/list` | Listar recursos | ✅ Status, Health, Recent threats |
| `resources/read` | Leer recurso | ✅ JSON resources |
| `prompts/list` | Listar prompts | ✅ Enterprise prompts |
| `prompts/get` | Obtener prompt | ✅ Analysis templates |

---

## 🎯 **Integración con Sistemas Existentes**

### **1. XDR Integration (Existente)**
```python
# La integración MCP mantiene compatibilidad con XDR existentes
xdr_systems = {
    "crowdstrike": "✅ Compatible - Exportación automática",
    "sentinel": "✅ Compatible - STIX 2.1 format",
    "cisco_umbrella": "✅ Compatible - Enforcement API"
}

# Configuración automática basada en threat level
if threat_level == "CRITICAL":
    export_to_all_xdr_systems()
```

### **2. SIEM Integration (Existente)**
```python
# Los conectores SIEM existentes se mantienen
siem_systems = {
    "wazuh": "✅ Compatible - CTI correlation",
    "splunk": "✅ Compatible - Compliance ready",
    "elastic": "✅ Compatible - Forensics format"
}

# Enrutamiento inteligente basado en compliance
if "SOX" in compliance_frameworks:
    route_to_splunk_with_extended_retention()
```

### **3. Monitoring Stack (Existente)**
```python
# Prometheus + Grafana siguen funcionando
monitoring_integration = {
    "prometheus": "✅ Métricas MCP exportadas automáticamente",
    "grafana": "✅ Dashboards MCP + HRM incluidos",
    "alertmanager": "✅ Alertas de escalado automático"
}
```

---

## 📈 **Auto-scaling Inteligente**

### **Triggers de Escalado**
```python
# Basado en análisis HRM
scaling_triggers = {
    "threat_based": {
        "CRITICAL + confidence > 0.85": "emergency_scale (5 instances)",
        "HIGH + confidence > 0.70": "scale_up (2 instances)",
        "queue_size > 100": "horizontal_scale (workers)"
    },
    "performance_based": {
        "avg_response_time > 500ms": "scale_up",
        "cpu_utilization > 70%": "scale_up",
        "memory_utilization > 80%": "scale_up"
    },
    "business_based": {
        "business_hours + critical_asset": "proactive_scale",
        "compliance_audit_period": "maintain_capacity",
        "low_utilization < 30%": "scale_down"
    }
}
```

### **Decisión Inteligente**
```python
# Algoritmo de decisión
def intelligent_scaling_decision(hrm_analysis, business_context):
    factors = {
        "threat_severity": weight_threat_level(hrm_analysis),
        "false_positive_confidence": weight_ml_confidence(hrm_analysis),
        "business_impact": weight_business_context(business_context),
        "compliance_requirements": weight_compliance(business_context),
        "current_capacity": weight_current_load(),
        "cost_optimization": weight_financial_impact()
    }

    return calculate_optimal_action(factors)
```

---

## 🌍 **Multi-Region Disaster Recovery**

### **Configuración DR**
```python
# Configuración automática de DR
dr_configuration = {
    "primary_region": "us-east-1",
    "secondary_regions": ["eu-west-1", "ap-southeast-1"],
    "replication": {
        "threat_intelligence_data": "real_time",
        "configuration": "near_real_time",
        "logs": "batch_hourly"
    },
    "failover": {
        "automatic": True,
        "rto_minutes": 15,  # Recovery Time Objective
        "rpo_minutes": 1,   # Recovery Point Objective
        "health_check_interval": 30
    }
}
```

### **Proceso de Failover**
```python
async def intelligent_failover(failed_region, current_load):
    # 1. Análisis HRM de la situación
    situation_analysis = await analyze_failover_situation(
        failed_region, current_load
    )

    # 2. Selección inteligente de región de destino
    target_region = await select_optimal_failover_region(
        situation_analysis, available_regions
    )

    # 3. Redistribución de carga con contexto empresarial
    redistribution_plan = await create_redistribution_plan(
        current_load, target_region, business_priorities
    )

    # 4. Ejecución coordinada
    return await execute_failover(redistribution_plan)
```

---

## 🧪 **Testing y Validación**

### **1. Test de Integración Básico**
```bash
# Test automático de componentes
cd enterprise/
python3 -m pytest test_mcp_integration.py -v

# Test manual de conectividad
python3 mcp_hrm_bridge.py
python3 mcp_enterprise_orchestrator.py
python3 mcp_server.py --port 8081
```

### **2. Test de Carga Enterprise**
```python
import asyncio
import time

async def load_test_enterprise():
    concurrent_requests = 50
    total_requests = 1000

    # Simular carga empresarial realista
    business_scenarios = [
        {"unit": "finance", "criticality": "high"},
        {"unit": "healthcare", "criticality": "critical"},
        {"unit": "technology", "criticality": "medium"}
    ]

    start_time = time.time()
    results = await run_concurrent_threat_analysis(
        concurrent_requests, total_requests, business_scenarios
    )

    duration = time.time() - start_time

    print(f"Load Test Results:")
    print(f"- Requests: {total_requests}")
    print(f"- Duration: {duration:.2f}s")
    print(f"- RPS: {total_requests/duration:.2f}")
    print(f"- Avg Response Time: {results.avg_response_time:.2f}ms")
    print(f"- Success Rate: {results.success_rate:.2f}%")

asyncio.run(load_test_enterprise())
```

### **3. Test de Disaster Recovery**
```python
async def test_disaster_recovery():
    # Simular falla de región primaria
    print("🔥 Simulating primary region failure...")

    # Monitorear proceso de failover
    failover_start = time.time()

    # Ejecutar failover automático
    result = await simulate_region_failure("us-east-1")

    failover_duration = time.time() - failover_start

    print(f"✅ Failover completed in {failover_duration:.2f}s")
    print(f"RTO Target: 15min, Actual: {failover_duration/60:.2f}min")
    print(f"New Primary: {result['new_primary_region']}")
    print(f"Data Consistency: {result['data_consistency']}")
```

---

## 🔧 **Troubleshooting**

### **Problemas Comunes**

**1. HRM Components Not Available**
```bash
# Error: "HRM modules not available"
# Solución:
cd smartcompute_hrm_proto/
ls python/  # Verificar archivos HRM
python3 -c "import integrated_analysis"  # Test importación
```

**2. WebSocket Connection Issues**
```bash
# Error: Connection refused
# Verificar:
netstat -tulpn | grep 8080  # Puerto en uso?
python3 mcp_server.py --log-level DEBUG  # Debug detallado
```

**3. Orchestrator Not Starting**
```bash
# Error: "Orchestrator failed to start"
# Solución:
python3 mcp_server.py --disable-orchestrator  # Test sin orquestador
python3 mcp_enterprise_orchestrator.py  # Test standalone
```

### **Logs y Monitoreo**
```bash
# Logs del servidor MCP
tail -f /var/log/smartcompute/mcp_server.log

# Métricas en tiempo real
curl http://localhost:8080/metrics

# Estado del orquestador
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"orchestrator/status","id":"status-1"}'
```

---

## 📚 **Referencias**

### **Documentación Relacionada**
- [SmartCompute HRM Prototype](../smartcompute_hrm_proto/README_RUN.txt)
- [Enterprise Features](../README.md#enterprise-features)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [WebSocket Protocol](https://tools.ietf.org/html/rfc6455)

### **APIs y Integraciones**
- [XDR Integration Guide](../docs/xdr_integration.md)
- [SIEM Connectors](../docs/siem_connectors.md)
- [Prometheus Metrics](../docs/prometheus_metrics.md)

### **Compliance y Seguridad**
- [Security Policy](../SECURITY.md)
- [SOX Compliance](../docs/compliance/sox.md)
- [HIPAA Compliance](../docs/compliance/hipaa.md)
- [PCI-DSS Compliance](../docs/compliance/pci_dss.md)

---

## 🤝 **Contribución**

### **Desarrollo Local**
```bash
# Fork del repositorio
git clone https://github.com/cathackr/SmartCompute.git

# Branch para desarrollo
git checkout -b feature/mcp-hrm-enhancement

# Desarrollo y testing
python3 -m pytest enterprise/tests/ -v

# Pull request con documentación actualizada
```

### **Guidelines de Código**
- Seguir PEP 8 para Python
- Documentar todas las funciones públicas
- Tests unitarios para nuevas funcionalidades
- Logs estructurados con nivel apropiado
- Manejo de errores comprehensivo

---

## 📞 **Soporte**

### **Canales de Soporte**
- **📧 Email Personal**: ggwre04p0@mozmail.com
- **🐙 GitHub Issues**: [SmartCompute Issues](https://github.com/cathackr/SmartCompute/issues)
- **📱 LinkedIn**: [Martín Iribarne CEH](https://www.linkedin.com/in/mart%C3%ADn-iribarne-swtf/)

### **SLA Enterprise**
- **Respuesta inicial**: < 4 horas (horario empresarial)
- **Resolución P1 (Critical)**: < 24 horas
- **Resolución P2 (High)**: < 72 horas
- **Consultas técnicas**: Vía email o LinkedIn

---

**© 2024 SmartCompute Enterprise. Documentación MCP + HRM Integration v1.0.0**

*Desarrollado por Martín Iribarne - Technology Architect*
*Integración MCP + HRM para SmartCompute Enterprise ($15,000 USD/año)*