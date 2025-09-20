# SmartCompute Enterprise - Instaladores
========================================

## Información del Build
- **Versión**: 1.0.0
- **Build**: 2025.09.17
- **Fecha**: 2025-09-17 19:43:41

## Instaladores Disponibles

### Windows
- `SmartCompute_Enterprise_Windows_v1.0.0.bat` - Instalador Batch con Python embebido
- `SmartCompute_Enterprise_Windows.nsi` - Script NSIS para compilación avanzada
- `smartcompute_tray_app.py` - Aplicación de bandeja del sistema

### Linux
- `SmartCompute_Enterprise_Linux_v1.0.0.sh` - Instalador Shell con compilación de Python

## Requisitos del Sistema

### Windows
- Windows 10/11 o Windows Server 2016+
- Arquitectura 64-bit
- 1 GB de espacio libre
- Conexión a internet (para validación de licencia)
- Privilegios de administrador

### Linux
- Distribuciones soportadas: Ubuntu 18.04+, CentOS/RHEL 7+, Fedora 30+, Arch Linux
- Kernel 4.0 o superior
- 1 GB de espacio libre
- Herramientas de desarrollo (gcc, make, etc.)
- Conexión a internet (para validación de licencia)
- Privilegios root

## Características de Seguridad

### Cifrado de Código
- Todo el código fuente está cifrado usando AES-256
- Las claves de descifrado se generan a partir de credenciales de usuario
- Validación online de licencias con metadatos

### Validación de Licencia
- Autenticación requerida durante la instalación
- Verificación online con servidor de licencias
- Expiración automática después de 1 año
- Validación de metadatos del sistema

### Protección del Sistema
- Instalación con privilegios elevados
- Configuración automática de firewall
- Servicios del sistema seguros
- Logs de auditoría

## Instalación

### Windows
1. Ejecutar como administrador: `SmartCompute_Enterprise_Windows_v1.0.0.bat`
2. Proporcionar credenciales de licencia
3. Seleccionar directorio de instalación
4. Completar configuración

### Linux
1. Ejecutar como root: `sudo ./SmartCompute_Enterprise_Linux_v1.0.0.sh`
2. Proporcionar credenciales de licencia
3. Seleccionar directorio de instalación
4. Completar configuración

## Desinstalación

### Windows
- Usar Panel de Control → Programas → SmartCompute Enterprise
- O ejecutar: `%PROGRAMFILES%\SmartCompute Enterprise\uninstall.bat`

### Linux
- Ejecutar: `/opt/smartcompute-enterprise/uninstall.sh`
- O usar systemctl: `sudo systemctl disable smartcompute-enterprise`

## Soporte y Documentación

- Documentación completa: [https://docs.smartcompute.enterprise]
- Soporte técnico: [support@smartcompute.enterprise]
- Portal de licencias: [https://license.smartcompute.enterprise]

## Notas de Seguridad

⚠️ **IMPORTANTE**: Los instaladores contienen código cifrado y requieren credenciales válidas.
No compartir credenciales de licencia ni distribuir instaladores sin autorización.

Las credenciales se verifican únicamente durante la instalación y se almacenan
de forma cifrada localmente para validaciones futuras.

---
Build generado automáticamente el 2025-09-17 19:43:41
