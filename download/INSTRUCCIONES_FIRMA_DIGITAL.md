# Instrucciones para Firma Digital SmartCompute

## Problema: "Autor Desconocido" en Windows

Cuando Windows muestra "Autor desconocido" es porque el archivo .bat no está firmado digitalmente.

## Solución 1: Certificado Self-Signed (Gratuito)

### Paso 1: Crear Certificado
```powershell
# Ejecutar PowerShell como Administrador
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\crear_certificado_smartcompute.ps1
```

### Paso 2: Firmar el archivo .bat
```cmd
# Instalar Windows SDK (incluye signtool.exe)
# O descargar signtool individualmente

signtool sign /f SmartCompute_CodeSigning.pfx /p SmartCompute2024! /t http://timestamp.digicert.com SmartCompute_Express_Windows.bat
```

### Paso 3: Verificar firma
```cmd
signtool verify /pa SmartCompute_Express_Windows.bat
```

## Solución 2: Certificado Comercial (Recomendado)

### Proveedores recomendados:
- **Sectigo** (~$199/año) - Buena relación calidad-precio
- **DigiCert** (~$599/año) - Premium, reconocimiento inmediato
- **GlobalSign** (~$299/año) - Opción intermedia

### Ventajas certificado comercial:
- ✅ No aparece advertencia de "Autor desconocido"
- ✅ Windows confía inmediatamente
- ✅ No requiere instalación manual del certificado
- ✅ Mejora la reputación del software

## Solución 3: Alternativa sin certificado

### Mejorar mensaje de Windows:
1. Agregar información de la empresa en las propiedades del archivo
2. Incluir descripción detallada del software
3. Versionar correctamente el ejecutable

### Script para agregar metadatos:
```bat
REM Agregar al inicio del .bat
echo ; SmartCompute Express v1.0
echo ; Desarrollado por Martin Iribarne Technology
echo ; Contacto: ggwre04p0@mozmail.com
echo ; Sitio web: linkedin.com/in/martín-iribarne-swtf
```

## Mejoras Implementadas

### ✅ Descarga Automática de Python
- Detecta arquitectura del sistema (32/64 bits)
- Descarga Python 3.11 oficial desde python.org
- Instalación silenciosa con PATH habilitado
- Limpieza automática de archivos temporales

### ✅ CLI Mejorada
- Permanece abierta durante el escaneo
- Indicadores de progreso visual
- Emojis para mejor experiencia
- Cierre automático después de 10 segundos
- Mensaje de éxito claro

### ✅ Mejor Experiencia de Usuario
- Opciones claras para descarga manual o automática
- Mensajes de error más informativos
- Colores para diferenciar estados
- Timeouts apropiados entre operaciones

## Próximos Pasos

1. **Obtener certificado de firma** (Sectigo recomendado)
2. **Firmar el archivo .bat** con el certificado
3. **Probar en máquinas Windows limpias**
4. **Distribuir la versión firmada**

## Comando Final de Compilación

```cmd
REM 1. Firmar el archivo
signtool sign /f certificado.pfx /p password /t http://timestamp.digicert.com SmartCompute_Express_Windows.bat

REM 2. Verificar firma
signtool verify /pa SmartCompute_Express_Windows.bat

REM 3. Probar instalación
SmartCompute_Express_Windows.bat
```

## Notas Importantes

- El certificado self-signed funcionará pero mostrará una advertencia
- Para producción se recomienda certificado comercial
- Mantener el certificado seguro y hacer backup
- Renovar certificados antes de expiración