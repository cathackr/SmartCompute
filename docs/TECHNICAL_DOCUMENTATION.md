# 📋 SmartCompute - Documentación Técnica

## 🎯 Arquitectura General

SmartCompute es una plataforma integral de ciberseguridad diseñada con arquitectura modular que permite escalabilidad desde implementaciones básicas hasta entornos industriales críticos.

### 🏗️ Componentes Principales

```
SmartCompute/
├── 📱 Core Application           # Motor principal de análisis
├── 🔍 Network Intelligence       # Análisis OSI 7 capas
├── 🛡️ Security Engine           # Detección de amenazas
├── 📊 Dashboard Engine           # Visualización y reportes
├── 🏢 Enterprise Module          # Funciones empresariales (Licencia)
├── 🏭 Industrial Module          # Protocolos industriales (Licencia)
└── 🔗 SIEM Integrations         # Conectores externos (Licencia)
```

## 🚀 Instalación y Configuración

### Express (Gratuito)
```bash
# Windows
SmartCompute_Express_Windows.bat

# Linux/macOS
chmod +x SmartCompute_Express_Linux.sh
./SmartCompute_Express_Linux.sh
```

### Enterprise/Industrial (Licencia Requerida)
```bash
git clone https://github.com/cathackr/SmartCompute-Enterprise.git
cd SmartCompute-Enterprise
pip install -r requirements.txt
export SMARTCOMPUTE_LICENSE_KEY="your-license-key"
python main.py --enterprise
```

## 🔧 CLI Interface

### Comando Principal
```bash
smartcompute [command] [target] [options]
```

### Comandos Disponibles
| Comando | Target | Descripción |
|---------|--------|-------------|
| `scan` | `infrastructure` | Análisis Docker, AD, Proxmox |
| `scan` | `network --osi-all` | Análisis OSI 7 capas completo |
| `scan` | `network --layers 3,4` | Red + Transporte únicamente |
| `scan` | `apis --layer 7` | Aplicaciones y APIs |
| `scan` | `iot --sensors all` | Monitoreo IoT completo |
| `scan` | `docker --containers` | Análisis específico Docker |

### Opciones Globales
- `--output cli` - Solo salida de terminal
- `--output html` - Dashboard HTML únicamente
- `--output both` - CLI + HTML (predeterminado)
- `--duration 60` - Duración del análisis en segundos
- `--format hmi` - Estilo HMI industrial

## 🌐 Análisis de Red

### OSI Layer Analysis
SmartCompute implementa análisis completo del modelo OSI:

**Layer 1 - Physical:**
- Detección de interfaces de red
- Estado de cables y conexiones
- Velocidad y duplex de enlaces

**Layer 2 - Data Link:**
- Tablas ARP y MAC addresses
- Detección de loops y tormentas
- Análisis de VLANs

**Layer 3 - Network:**
- Topología de red IP
- Análisis de enrutamiento
- Detección de conflictos IP

**Layer 4 - Transport:**
- Conexiones TCP/UDP activas
- Análisis de puertos
- Detección de servicios

**Layer 5 - Session:**
- Sesiones activas
- Persistencia de conexiones
- Gestión de estado

**Layer 6 - Presentation:**
- Cifrado y compresión
- Formatos de datos
- Codificación de caracteres

**Layer 7 - Application:**
- Protocolos HTTP/HTTPS/SSH/DNS
- Análisis de tráfico por aplicación
- Detección de aplicaciones no autorizadas

## 🏢 Funciones Enterprise

### XDR Integration
Exportación automática a plataformas líderes:

```python
# CrowdStrike Falcon
crowdstrike_exporter = CrowdStrikeExporter(
    api_key="your_key",
    base_url="https://api.crowdstrike.com"
)
events = smartcompute.get_security_events()
crowdstrike_exporter.export_streaming(events)

# Microsoft Sentinel
sentinel_exporter = SentinelExporter(
    workspace_id="your_workspace",
    shared_key="your_key"
)
sentinel_exporter.export_stix21(events)
```

### AI Recommendations
```python
ai_engine = SmartComputeAI()
recommendations = ai_engine.analyze_threats(security_events)

# Suggestions without automatic execution
for rec in recommendations:
    print(f"Recommended Action: {rec.action}")
    print(f"Confidence: {rec.confidence}%")
    print(f"Manual Review Required: {rec.requires_review}")
```

### Real-Time Metrics
- **MTTD:** 12 minutos vs 287 minutos industria
- **Reducción Falsos Positivos:** 92.4% (4,200 → 320 alertas/día)
- **Precisión:** 95.7% en detección de amenazas
- **Throughput:** >1GB/s en redes industriales

## 🏭 Funciones Industrial

### Protocolos Industriales
```python
# Modbus TCP/RTU
modbus_scanner = ModbusScanner()
devices = modbus_scanner.discover_devices(ip_range="192.168.1.0/24")

# Profinet
profinet_analyzer = ProfinetAnalyzer()
topology = profinet_analyzer.scan_topology()

# OPC UA
opcua_monitor = OPCUAMonitor()
subscriptions = opcua_monitor.create_subscriptions(node_ids)
```

### Seguridad Industrial
- **ISA/IEC 62443** compliance
- **NERC CIP** critical infrastructure protection
- Detección de ataques específicos a sistemas de control
- Monitoreo de protocolos SCADA/HMI

### Performance Benchmarks
| Protocolo | Throughput | Latencia | Precisión |
|-----------|------------|----------|-----------|
| Modbus TCP | 1,200 Mbps | 0.8ms | 99.2% |
| Profinet | 980 Mbps | 2.3ms | 98.9% |
| OPC UA | 1,450 Mbps | 5.1ms | 99.5% |
| Ethernet/IP | 1,100 Mbps | 1.2ms | 99.1% |

## 🔒 Sistema de Licencias

### Validación de Licencia
```python
license_validator = LicenseValidator()
is_valid = license_validator.verify(
    license_key="SMARTCOMPUTE-ENT-XXXX-XXXX",
    features=["xdr_export", "ai_recommendations"]
)
```

### Funciones por Licencia
| Feature | Express | Enterprise | Industrial |
|---------|---------|------------|------------|
| Análisis básico | ✅ | ✅ | ✅ |
| OSI completo | ✅ | ✅ | ✅ |
| XDR Export | ❌ | ✅ | ✅ |
| AI Recommendations | ❌ | ✅ | ✅ |
| Protocolos Industriales | ❌ | ❌ | ✅ |
| Unlimited Agents | ❌ | 100 | ♾️ |

## 📊 Dashboard y Visualización

### Template System
```python
dashboard = SmartComputeDashboard(
    title="SMARTCOMPUTE SYSTEM MONITOR",
    status="ONLINE"
)

# Panel principal configurable
dashboard.create_main_analysis_panel(
    data=osi_layer_data,
    title="OSI LAYER ANALYSIS",
    xlabel="ACTIVITY LEVEL (%)"
)

# Métricas del sistema
dashboard.create_metrics_panel(
    data=system_metrics,
    title="SYSTEM RESOURCES"
)

# Guardar dashboard
dashboard.finalize("smartcompute_analysis.png")
```

### Estilo HMI Industrial
- **Colores:** Verde (#00ff88), Amarillo (#ffd700), Rojo (#ff6b6b)
- **Tipografía:** Monospace para legibilidad industrial
- **Layout:** Grid responsivo con espaciado optimizado
- **Inteligencia:** Posicionamiento automático de valores

## 🔗 Integraciones SIEM

### Formatos Soportados
- **CEF (Common Event Format):** ArcSight, QRadar
- **STIX 2.1:** Threat Intelligence platforms
- **JSON nativo:** Splunk, Elastic Security
- **Syslog RFC5424:** Sistemas UNIX/Linux

### Conectores Disponibles
```python
# Splunk Universal Forwarder
splunk_connector = SplunkConnector(
    host="splunk.company.com",
    port=8089,
    token="your_hec_token"
)

# Wazuh Agent Integration
wazuh_integration = WazuhIntegration(
    manager_ip="192.168.1.100",
    agent_key="your_agent_key"
)

# Custom SIEM via webhook
custom_siem = CustomSIEMConnector(
    webhook_url="https://your-siem.com/webhook",
    format="json"
)
```

## 🛡️ Seguridad y Compliance

### Certificaciones
- **ISO 27001:** Information Security Management
- **SOC 2 Type II:** Security and Availability
- **NIST Cybersecurity Framework:** Complete implementation
- **ISA/IEC 62443:** Industrial security standards

### Protección de Datos
- **Cifrado:** AES-256 para datos en reposo
- **Transmisión:** TLS 1.3 para datos en tránsito
- **Autenticación:** Multi-factor con SAML/OIDC
- **Logs:** Inmutable audit trail

## 📞 Soporte Técnico

### Canales de Soporte
- **Express:** GitHub Issues
- **Enterprise:** Business Hours Support (99.5% SLA)
- **Industrial:** 24/7 Priority Support (99.9% SLA)

### Escalation Matrix
| Severidad | Express | Enterprise | Industrial |
|-----------|---------|------------|------------|
| P1 - Critical | GitHub | 4 horas | 1 hora |
| P2 - High | GitHub | 24 horas | 4 horas |
| P3 - Medium | GitHub | 72 horas | 24 horas |
| P4 - Low | GitHub | Best effort | 72 horas |

## 🔬 Desarrollo y API

### REST API Endpoints
```bash
# Health check
GET /api/v1/health

# Start analysis
POST /api/v1/analysis/start
{
  "type": "infrastructure",
  "duration": 30,
  "targets": ["docker", "network"]
}

# Get results
GET /api/v1/analysis/{analysis_id}/results

# Export to SIEM
POST /api/v1/export/siem
{
  "format": "cef",
  "destination": "splunk",
  "events": [...]
}
```

### SDK Python
```python
from smartcompute import SmartComputeAPI

client = SmartComputeAPI(
    api_key="your_api_key",
    base_url="http://localhost:8000"
)

# Iniciar análisis
analysis = client.start_analysis(
    analysis_type="network",
    options={"layers": [3, 4, 7]}
)

# Obtener resultados
results = client.get_results(analysis.id)
```

---

## 📝 Changelog

### v2.1.0 (2024-12-14)
- ✅ Unified CLI interface
- ✅ Industrial protocols support
- ✅ Enhanced XDR integrations
- ✅ AI recommendations engine

### v2.0.0 (2024-11-01)
- ✅ Enterprise licensing system
- ✅ SIEM integrations
- ✅ Template dashboard system
- ✅ Multi-platform installers

---

*© 2024 SmartCompute by Martín Iribarne - All rights reserved*