# SmartCompute Industrial - Guía de Uso Avanzado

## Índice
1. [Introducción al Sistema](#introducción-al-sistema)
2. [Arquitectura y Componentes](#arquitectura-y-componentes)
3. [Instalación y Configuración](#instalación-y-configuración)
4. [Gestión de Conectividad MPLS DCI](#gestión-de-conectividad-mpls-dci)
5. [Protocolos Industriales Avanzados](#protocolos-industriales-avanzados)
6. [Monitoreo de Variables Industriales](#monitoreo-de-variables-industriales)
7. [Gestión de Vulnerabilidades](#gestión-de-vulnerabilidades)
8. [Sistema de Logs SCADA/ICS](#sistema-de-logs-scadaics)
9. [Exportación Segura de Reportes](#exportación-segura-de-reportes)
10. [Cumplimiento Normativo](#cumplimiento-normativo)
11. [Casos de Uso Avanzados](#casos-de-uso-avanzados)
12. [Solución de Problemas](#solución-de-problemas)

---

## Introducción al Sistema

SmartCompute Industrial es una plataforma integral de ciberseguridad diseñada específicamente para entornos industriales, que integra múltiples sistemas ICS/SCADA, protocolos industriales estándar y normativas internacionales de seguridad.

### Características Principales
- **Conectividad Híbrida**: Integración Enterprise-Industrial mediante MPLS DCI
- **Protocolos Nativos**: Soporte para Modbus, PROFINET, EtherNet/IP, S7comm, OPC-UA
- **Seguridad Multinivel**: Niveles SL-0 a SL-4 según ISA/IEC 62443
- **Cifrado Obligatorio**: Todos los reportes se cifran con clave del operador
- **Cumplimiento Total**: ISA/IEC 62443, IEC 61508/61511, NIST CSF, FDA 21 CFR 11

---

## Arquitectura y Componentes

### Estructura del Sistema

```
SmartCompute Industrial/
├── Capa de Conectividad (MPLS DCI)
│   ├── smartcompute_network_bridge.py
│   └── smartcompute_central_bridge_server.py
├── Capa de Protocolos Industriales
│   ├── industrial_protocols_engine.py
│   └── industrial_systems_integrator.py
├── Capa de Monitoreo y Variables
│   ├── industrial_variables_monitor.py
│   └── industrial_variable_configurator.py
├── Capa de Seguridad
│   ├── secure_credentials_manager.py
│   ├── industrial_vulnerability_manager.py
│   └── industrial_scada_logging_system.py
├── Capa de Reportes y Cumplimiento
│   ├── industrial_reports_exporter.py
│   ├── decrypt_report.py
│   └── industrial_standards_compliance.py
└── Interfaz Principal
    └── smartcompute_industrial_gui.py
```

### Componentes Críticos

#### 1. **Red MPLS DCI** (`smartcompute_network_bridge.py`)
- Conectividad L2/L3 entre dominios Enterprise e Industrial
- VPN instances con aislamiento de tráfico
- QoS policies para tráfico crítico de control
- LSP establishment automático

#### 2. **Motor de Protocolos** (`industrial_protocols_engine.py`)
- Parsers nativos para protocolos industriales
- Autenticación challenge-response
- Rate limiting y detección de anomalías
- Cifrado AES-GCM para comunicaciones

#### 3. **Gestor de Vulnerabilidades** (`industrial_vulnerability_manager.py`)
- Mapeo físico de plantas industriales
- Scoring CVSS con contexto industrial
- Correlación por zonas de criticidad
- Algoritmos de priorización de riesgos

---

## Instalación y Configuración

### Requisitos del Sistema
```bash
# Sistema Operativo
Ubuntu 20.04+ / RHEL 8+ / CentOS 8+

# Python y Dependencias
Python 3.8+
cryptography >= 3.4.8
sqlite3 (incluido en Python)

# Espacio en Disco
Mínimo: 2GB
Recomendado: 10GB (para logs y reportes)

# Red
Acceso a redes industriales (VLAN segregada)
Puertos TCP: 502 (Modbus), 44818 (OPC-UA), 102 (S7comm)
```

### Instalación Paso a Paso

```bash
# 1. Crear estructura de directorios
mkdir -p /home/gatux/smartcompute/{data,logs,reports,backups}

# 2. Configurar permisos
chmod 750 /home/gatux/smartcompute
chmod 700 /home/gatux/smartcompute/{data,logs}

# 3. Inicializar bases de datos
python3 smartcompute_industrial_gui.py --init-db

# 4. Verificar conectividad de protocolos
python3 industrial_protocols_engine.py --test-protocols

# 5. Configurar credenciales de administrador
python3 secure_credentials_manager.py --setup-admin
```

### Variables de Entorno Críticas

```bash
# Cifrado de reportes
export REPORTS_ENCRYPTION_PASSWORD="tu_clave_maestra_segura"

# Configuración de red industrial
export INDUSTRIAL_NETWORK_CIDR="192.168.100.0/24"
export SCADA_NETWORK_CIDR="192.168.200.0/24"

# Configuración de cumplimiento
export COMPLIANCE_AUDIT_LEVEL="STRICT"
export SIL_CERTIFICATION_REQUIRED="true"
```

---

## Gestión de Conectividad MPLS DCI

### Configuración de Bridging Enterprise-Industrial

```python
from smartcompute_network_bridge import MPLSDataCenterInterconnect

# Inicializar DCI
dci = MPLSDataCenterInterconnect()

# Configurar VPN instances
await dci.configure_vpn_instances([
    {
        'name': 'ENTERPRISE_VPN',
        'vrf': 'ENT:100',
        'networks': ['10.0.0.0/16'],
        'qos_class': 'enterprise'
    },
    {
        'name': 'INDUSTRIAL_VPN',
        'vrf': 'IND:200',
        'networks': ['192.168.0.0/16'],
        'qos_class': 'critical_control'
    }
])

# Establecer LSPs con redundancia
lsp_config = {
    'primary_path': ['PE1', 'P1', 'P2', 'PE2'],
    'backup_path': ['PE1', 'P3', 'P4', 'PE2'],
    'protection_type': '1+1',
    'bandwidth': '100Mbps'
}

await dci.establish_lsps(lsp_config)
```

### Monitoreo de Conectividad en Tiempo Real

```python
# Verificar estado de LSPs
lsp_status = await dci.check_lsp_status()
print(f"LSPs Activos: {lsp_status['active_lsps']}")
print(f"Redundancia: {lsp_status['protection_status']}")

# Métricas de rendimiento
metrics = await dci.get_performance_metrics()
print(f"Latencia: {metrics['latency_ms']}ms")
print(f"Pérdida de paquetes: {metrics['packet_loss']}%")
print(f"Jitter: {metrics['jitter_ms']}ms")
```

---

## Protocolos Industriales Avanzados

### Configuración Multi-Protocolo

```python
from industrial_protocols_engine import IndustrialProtocolsEngine

engine = IndustrialProtocolsEngine()

# Configurar Modbus TCP con autenticación
modbus_config = {
    'host': '192.168.100.10',
    'port': 502,
    'unit_id': 1,
    'authentication': {
        'method': 'challenge_response',
        'key': 'industrial_modbus_key_2024',
        'timeout': 30
    },
    'encryption': True
}

await engine.configure_modbus(modbus_config)

# Configurar PROFINET con certificados
profinet_config = {
    'device_name': 'SIMATIC_PLC_001',
    'ip_address': '192.168.100.20',
    'certificates': {
        'device_cert': '/path/to/device.crt',
        'ca_cert': '/path/to/ca.crt'
    },
    'security_level': 'high'
}

await engine.configure_profinet(profinet_config)
```

### Lecturas Seguras de Variables

```python
# Lectura Modbus con verificación de integridad
result = await engine.read_modbus_registers(
    address=1000,
    count=10,
    verify_integrity=True,
    retry_count=3
)

if result['success']:
    values = result['values']
    checksum = result['integrity_checksum']
    print(f"Valores leídos: {values}")
    print(f"Checksum verificado: {checksum}")

# Escritura PROFINET con logging de auditoría
write_result = await engine.write_profinet_variable(
    variable_name="PROCESS_SETPOINT",
    value=75.5,
    operator_id="operator_001",
    audit_log=True
)
```

---

## Monitoreo de Variables Industriales

### Configuración de Especificaciones Técnicas

```python
from industrial_variable_configurator import IndustrialVariableConfigurator
from industrial_variables_monitor import IndustrialVariablesMonitor

configurator = IndustrialVariableConfigurator()

# Configurar variable eléctrica de alta tensión
electrical_spec = {
    'variable_name': 'MAIN_TRANSFORMER_VOLTAGE',
    'voltage_class': 'HIGH_VOLTAGE',  # 35-138kV
    'phase_type': 'THREE_PHASE_WYE',
    'supply_type': 'MAIN_GRID',
    'safety_classification': 'SIL_2',
    'maintenance_schedule': {
        'preventive_days': 90,
        'calibration_days': 365,
        'inspection_days': 30
    },
    'alarm_limits': {
        'low_low': 110000,  # 110kV
        'low': 115000,      # 115kV
        'high': 140000,     # 140kV
        'high_high': 145000 # 145kV
    }
}

await configurator.configure_electrical_variable(electrical_spec)

# Configurar almacenamiento refrigerado
cold_storage_spec = {
    'variable_name': 'FREEZER_CHAMBER_TEMP',
    'application_type': 'FREEZER_STORAGE',  # -20°C a -10°C
    'temperature_range': (-25, -15),
    'product_categories': ['vaccines', 'biological_samples'],
    'expiry_monitoring': True,
    'haccp_compliance': True,
    'alarm_delays': {
        'temp_deviation': 300,  # 5 minutos
        'door_open': 120,       # 2 minutos
        'power_failure': 60     # 1 minuto
    }
}

await configurator.configure_temperature_variable(cold_storage_spec)
```

---

## Exportación Segura de Reportes

### Configuración de Permisos Granulares

```python
from industrial_reports_exporter import IndustrialReportsExporter, ExportRequest, ReportType, ReportFormat

exporter = IndustrialReportsExporter()

# Configurar permisos por rol
permissions = [
    {
        'user_id': 'plant_manager',
        'role': 'management',
        'allowed_reports': [
            ReportType.VULNERABILITY_ASSESSMENT,
            ReportType.COMPLIANCE_AUDIT,
            ReportType.RISK_ANALYSIS
        ],
        'allowed_formats': [ReportFormat.PDF, ReportFormat.EXCEL],
        'access_level': AccessLevel.SECRET,
        'restrictions': {
            'ip_whitelist': ['192.168.1.0/24'],
            'time_window': {'start': '08:00', 'end': '18:00'},
            'max_exports_daily': 20,
            'approval_required': False,
            'watermark_required': True
        }
    }
]

await exporter.configure_user_permissions(permissions)
```

### Exportación con Cifrado Obligatorio

```python
# El operador DEBE proporcionar clave de cifrado
operator_encryption_key = input("Ingrese clave de cifrado para el reporte: ")

# Crear solicitud de exportación
export_request = ExportRequest(
    request_id=f"REQ-{secrets.token_hex(8).upper()}",
    user_id="security_analyst",
    report_type=ReportType.VULNERABILITY_ASSESSMENT,
    format=ReportFormat.PDF,
    operator_encryption_key=operator_encryption_key,  # ⚠️ OBLIGATORIO
    filters={
        'severity': ['CRITICAL', 'HIGH'],
        'location': 'PROD_ZONE_A',
        'date_range': (
            datetime.now() - timedelta(days=30),
            datetime.now()
        )
    }
)

# Exportar (archivo resultante estará CIFRADO)
encrypted_file_path = await exporter.export_report(export_request, user_ip="192.168.1.100")

if encrypted_file_path:
    print(f"✅ Reporte exportado y cifrado: {encrypted_file_path}")
    print(f"⚠️  IMPORTANTE: Sin la clave '{operator_encryption_key}' el archivo NO se puede recuperar")
```

### Descifrado de Reportes

```python
from decrypt_report import decrypt_report

# Descifrar reporte con clave del operador
success = decrypt_report(
    encrypted_file_path="/path/to/report.pdf.encrypted",
    operator_key=operator_encryption_key,
    output_path="/path/to/report.pdf"
)

if success:
    print("✅ Reporte descifrado exitosamente")
else:
    print("❌ Error: Clave de descifrado incorrecta")
```

---

## Cumplimiento Normativo

### Evaluación ISA/IEC 62443

```python
from industrial_standards_compliance import IndustrialStandardsCompliance, ComplianceLevel, SecurityLevel

compliance = IndustrialStandardsCompliance()

# Evaluar requisito de identificación y autenticación
await compliance.assess_compliance(
    requirement_id="ISA-62443-3-3-SR-1.1",
    status=ComplianceLevel.COMPLIANT,
    evidence=[
        "Sistema LDAP integrado con autenticación multifactor",
        "Logs de acceso con trazabilidad completa",
        "Política de contraseñas conforme a ISA-62443-3-3",
        "Certificado de auditoría externa (Anexo A-1)"
    ],
    gaps=[],
    remediation="Cumplimiento completo. Mantener revisión anual.",
    assessor="compliance_officer"
)

# Evaluar nivel de seguridad objetivo para zona crítica
sl_assessment = await compliance.conduct_security_level_assessment(
    zone="CRITICAL_PROCESS_CONTROL",
    target_sl=SecurityLevel.SL3
)

print(f"=== EVALUACIÓN SL-3 ===")
print(f"Zona: {sl_assessment['zone']}")
print(f"Nivel objetivo: {sl_assessment['target_security_level']}")

print("\nControles requeridos para SL-3:")
for control in sl_assessment['required_controls']:
    print(f"✓ {control}")
```

### Validación IEC 61508 (SIL)

```python
# Validar requisitos SIL-3 para sistema instrumentado de seguridad
sil_validation = await compliance.validate_sil_requirements(
    system="REACTOR_EMERGENCY_SHUTDOWN",
    target_sil=SafetyIntegrityLevel.SIL_3
)

print(f"=== VALIDACIÓN SIL-3 ===")
print(f"Sistema: {sil_validation['system']}")
print(f"Objetivo PFD: {sil_validation['requirements']['pfd_target']}")
print(f"Arquitectura requerida: {sil_validation['requirements']['architecture']}")
print(f"Intervalo de pruebas: {sil_validation['requirements']['proof_test_interval']}")
```

---

## Casos de Uso Avanzados

### Caso 1: Respuesta a Incidente de Ciberseguridad

```python
# Escenario: Detección de actividad anómala en red industrial
async def incident_response_workflow():

    # 1. Detección automática de anomalía
    anomaly = await scada_logger.detect_network_anomaly()
    print(f"🚨 ANOMALÍA DETECTADA: {anomaly['description']}")

    # 2. Correlación con eventos SCADA
    related_events = await scada_logger.correlate_with_scada_events(
        anomaly['timestamp'],
        time_window_minutes=15
    )

    # 3. Evaluación de impacto en vulnerabilidades
    impact_assessment = await vuln_manager.assess_incident_impact(
        affected_assets=anomaly['affected_assets'],
        attack_vector=anomaly['attack_vector']
    )

    # 4. Activación de procedimientos de emergencia
    if impact_assessment['risk_level'] == 'CRITICAL':
        # Aislamiento automático de red
        await dci.isolate_affected_segments(anomaly['affected_segments'])

        # Generación de reporte forense cifrado
        forensic_request = ExportRequest(
            request_id=f"FORENSIC-{anomaly['incident_id']}",
            user_id="incident_commander",
            report_type=ReportType.SECURITY_INCIDENTS,
            format=ReportFormat.JSON,
            operator_encryption_key="FORENSIC_KEY_2024",
            filters={'incident_id': anomaly['incident_id']}
        )

        forensic_report = await exporter.export_report(forensic_request)
        print(f"📊 Reporte forense generado: {forensic_report}")

# Ejecutar workflow de respuesta
await incident_response_workflow()
```

### Caso 2: Auditoría de Cumplimiento Automática

```python
# Auditoría programada mensual
async def automated_compliance_audit():

    audit_results = {}

    # 1. Evaluación automática ISA/IEC 62443
    isa_assessment = await compliance.automated_isa_assessment()
    audit_results['ISA_IEC_62443'] = isa_assessment

    # 2. Verificación de configuraciones de seguridad
    security_configs = await engine.audit_security_configurations()

    # 3. Análisis de logs de los últimos 30 días
    log_analysis = await scada_logger.compliance_log_analysis(days=30)

    # 4. Compilación de evidencias
    evidence_package = {
        'isa_compliance': isa_assessment,
        'security_configs': security_configs,
        'log_analysis': log_analysis,
        'audit_timestamp': datetime.now().isoformat()
    }

    # 5. Generación de reporte ejecutivo cifrado
    exec_report_request = ExportRequest(
        request_id=f"AUDIT-{datetime.now().strftime('%Y%m%d')}",
        user_id="compliance_officer",
        report_type=ReportType.COMPLIANCE_AUDIT,
        format=ReportFormat.PDF,
        operator_encryption_key="MONTHLY_AUDIT_2024",
        parameters={'evidence_package': evidence_package}
    )

    audit_report = await exporter.export_report(exec_report_request)

    return audit_report

# Programar auditoría mensual
monthly_audit = await automated_compliance_audit()
print(f"✅ Auditoría mensual completada: {monthly_audit}")
```

---

## Solución de Problemas

### Problemas Comunes y Soluciones

#### 1. **Error de Conectividad MPLS**

```bash
# Diagnóstico
python3 smartcompute_network_bridge.py --diagnostic

# Solución: Reestablecer LSPs
python3 smartcompute_network_bridge.py --reset-lsps
```

#### 2. **Fallo en Protocolo Industrial**

```bash
# Diagnóstico de protocolos
python3 industrial_protocols_engine.py --test-protocols

# Verificar logs específicos
tail -f /home/gatux/smartcompute/logs/industrial_protocols_engine.log
```

#### 3. **Error en Descifrado de Reportes**

```bash
# Verificar estructura del archivo
hexdump -C report_file.encrypted | head -5

# Solución: Usar herramienta de recuperación
python3 decrypt_report.py --recovery-mode report_file.encrypted
```

#### 4. **Base de Datos Corrupta**

```bash
# Verificar integridad
sqlite3 /home/gatux/smartcompute/data/compliance.db "PRAGMA integrity_check;"

# Backup y reparación
cp compliance.db compliance.db.backup
sqlite3 compliance.db ".recover compliance_recovered.db"
```

### Comandos de Diagnóstico Rápido

```bash
# Estado general del sistema
python3 -c "
import asyncio
from smartcompute_industrial_gui import SmartComputeIndustrialGUI

async def system_status():
    gui = SmartComputeIndustrialGUI()
    status = await gui.get_system_health()
    print(f'Estado: {status}')

asyncio.run(system_status())
"

# Verificar permisos y archivos
find /home/gatux/smartcompute -type f -name "*.db"

# Monitoreo de recursos
htop -p $(pgrep -f smartcompute)
```

---

## Información de Contacto

Para consultas técnicas y soporte del sistema SmartCompute Industrial:

**Desarrollador Principal:**
- **Email:** ggwre04p0@mozmail.com
- **LinkedIn:** https://www.linkedin.com/in/mart%C3%ADn-iribarne-swtf/

---

## Conclusión

Esta guía proporciona una cobertura comprensiva del sistema SmartCompute Industrial, desde configuración básica hasta casos de uso avanzados. El sistema está diseñado para cumplir con los más altos estándares de ciberseguridad industrial mientras mantiene la operabilidad y eficiencia de los procesos críticos.

**Puntos Clave:**
- ✅ Cifrado obligatorio de todos los reportes
- ✅ Cumplimiento multi-normativo (ISA/IEC 62443, IEC 61508, NIST, FDA)
- ✅ Integración nativa con sistemas SCADA/ICS
- ✅ Monitoreo en tiempo real con especificaciones técnicas
- ✅ Gestión de vulnerabilidades con contexto industrial
- ✅ Trazabilidad completa y auditoría forense

---
*SmartCompute Industrial v2024.09 - Ciberseguridad Industrial de Clase Mundial*