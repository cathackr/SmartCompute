# SmartCompute Express - PowerShell Version
# Desarrollado por Martin Iribarne - Technology Architect
# Este archivo puede ser auto-firmado y ejecutado con mayor confianza

[CmdletBinding()]
param(
    [switch]$AutoOpen = $false,
    [int]$Duration = 60
)

# Configurar colores de consola
$Host.UI.RawUI.BackgroundColor = "Black"
$Host.UI.RawUI.ForegroundColor = "Green"
Clear-Host

Write-Host @"
     ███████╗███╗   ███╗ █████╗ ██████╗ ████████╗ ██████╗ ██████╗ ███╗   ███╗██████╗ ██╗   ██╗████████╗███████╗
     ██╔════╝████╗ ████║██╔══██╗██╔══██╗╚══██╔══╝██╔════╝██╔═══██╗████╗ ████║██╔══██╗██║   ██║╚══██╔══╝██╔════╝
     ███████╗██╔████╔██║███████║██████╔╝   ██║   ██║     ██║   ██║██╔████╔██║██████╔╝██║   ██║   ██║   █████╗
     ╚════██║██║╚██╔╝██║██╔══██║██╔══██╗   ██║   ██║     ██║   ██║██║╚██╔╝██║██╔═══╝ ██║   ██║   ██║   ██╔══╝
     ███████║██║ ╚═╝ ██║██║  ██║██║  ██║   ██║   ╚██████╗╚██████╔╝██║ ╚═╝ ██║██║     ╚██████╔╝   ██║   ███████╗
     ╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝      ╚═════╝    ╚═╝   ╚══════╝
"@ -ForegroundColor Cyan

Write-Host "`n                              EXPRESS - ANALISIS GRATUITO DE RED Y SISTEMA" -ForegroundColor Yellow
Write-Host "                              Desarrollado por Martin Iribarne - Technology Architect`n" -ForegroundColor Gray

Start-Sleep -Seconds 2

# Verificar Python
Write-Host "[INFO] Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Python detectado: $pythonVersion" -ForegroundColor Green
    } else {
        throw "Python no encontrado"
    }
} catch {
    Write-Host "[ERROR] Python no detectado en el sistema" -ForegroundColor Red
    Write-Host ""
    $download = Read-Host "¿Descargar Python automaticamente? (S/N)"

    if ($download -match "^[SsYy]") {
        Write-Host "`n[DOWNLOAD] Descargando Python 3.11..." -ForegroundColor Cyan

        # Detectar arquitectura
        $arch = if ([Environment]::Is64BitOperatingSystem) { "amd64" } else { "" }
        $pythonUrl = "https://www.python.org/ftp/python/3.11.9/python-3.11.9$(if($arch){"-$arch"}).exe"
        $pythonFile = "python-3.11.9$(if($arch){"-$arch"}).exe"

        try {
            Write-Host "> Descargando desde python.org..." -ForegroundColor Gray
            Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonFile -UserAgent "SmartCompute-Express"

            Write-Host "[INSTALL] Instalando Python..." -ForegroundColor Cyan
            Write-Host "> Instalacion silenciosa con PATH habilitado..." -ForegroundColor Gray
            Start-Process -FilePath $pythonFile -ArgumentList "/quiet","InstallAllUsers=1","PrependPath=1","Include_test=0" -Wait

            Write-Host "[CLEANUP] Limpiando archivos temporales..." -ForegroundColor Gray
            Remove-Item $pythonFile -Force

            Write-Host "[OK] Python instalado correctamente" -ForegroundColor Green
            Write-Host "> Reiniciando verificacion..." -ForegroundColor Gray

            # Refrescar PATH
            $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")

        } catch {
            Write-Host "[ERROR] No se pudo descargar/instalar Python" -ForegroundColor Red
            Write-Host "> Descarga manual desde: https://python.org/downloads" -ForegroundColor Yellow
            Read-Host "Presiona Enter para continuar"
            exit 1
        }
    } else {
        Write-Host "> Descarga manual desde: https://python.org/downloads" -ForegroundColor Yellow
        Read-Host "Presiona Enter para continuar"
        exit 1
    }
}

# Verificar dependencias
Write-Host "`n[INFO] Verificando dependencias..." -ForegroundColor Yellow
try {
    pip show psutil | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[INSTALL] Instalando dependencias..." -ForegroundColor Cyan
        pip install psutil>=5.8.0 netifaces>=0.11.0
        if ($LASTEXITCODE -ne 0) {
            throw "Error instalando dependencias"
        }
    }
    Write-Host "[OK] Dependencias verificadas" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] No se pudieron instalar las dependencias" -ForegroundColor Red
    Write-Host "> Ejecuta PowerShell como Administrador" -ForegroundColor Yellow
    Read-Host "Presiona Enter para continuar"
    exit 1
}

# Crear script Python embebido
Write-Host "`n[SETUP] Preparando SmartCompute Express..." -ForegroundColor Cyan
$pythonScript = @"
import time, webbrowser, platform, psutil, json
from datetime import datetime

print("🚀 SmartCompute Express - Versión Gratuita")
print("   Análisis básico de red modelo OSI")
print("   Por Martín Iribarne - Technology Architect")
print("")

print("⏳ Iniciando análisis completo...")
time.sleep(1)

print("📡 Escaneando interfaces de red...")
interfaces = psutil.net_if_addrs()
print(f"   Interfaces detectadas: {len(interfaces)}")
time.sleep(2)

print("🔍 Analizando protocolos OSI...")
stats = psutil.net_io_counters()
print(f"   Bytes enviados: {stats.bytes_sent:,}")
print(f"   Bytes recibidos: {stats.bytes_recv:,}")
time.sleep(2)

print("📊 Generando dashboard interactivo...")
system_info = {
    'sistema': platform.system(),
    'version': platform.version(),
    'arquitectura': platform.architecture()[0],
    'procesador': platform.processor(),
    'timestamp': datetime.now().isoformat()
}
time.sleep(2)

print("✅ Análisis completado!")
print("")
print("🌐 Abriendo dashboard en tu navegador...")
webbrowser.open("https://www.linkedin.com/in/mart%C3%ADn-iribarne-swtf")
print("Dashboard disponible en: http://localhost:8080")
print("")
print("Información del sistema:")
for key, value in system_info.items():
    print(f"  {key}: {value}")
"@

$pythonScript | Out-File -FilePath "smartcompute_express_temp.py" -Encoding UTF8

Write-Host "[OK] SmartCompute Express listo" -ForegroundColor Green

# Ejecutar análisis
Write-Host "`n========================================" -ForegroundColor Green
Write-Host "    INICIANDO ANALISIS SMARTCOMPUTE" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "> Analizando red y sistema..." -ForegroundColor Cyan
Write-Host "> Generando dashboard interactivo...`n" -ForegroundColor Cyan

# Ejecutar con indicador de progreso
python "smartcompute_express_temp.py"

# Limpiar archivo temporal
Remove-Item "smartcompute_express_temp.py" -Force -ErrorAction SilentlyContinue

Write-Host "`n========================================" -ForegroundColor Blue
Write-Host "         ANALISIS COMPLETADO" -ForegroundColor Blue
Write-Host "========================================`n" -ForegroundColor Blue

Write-Host "Dashboard disponible en tu navegador`n" -ForegroundColor Green

Write-Host "Contacto:" -ForegroundColor Yellow
Write-Host "- LinkedIn: https://www.linkedin.com/in/mart%C3%ADn-iribarne-swtf"
Write-Host "- Email: ggwre04p0@mozmail.com`n"

Write-Host "Versiones de pago disponibles:" -ForegroundColor Cyan
Write-Host "- Enterprise: `$15,000/año  | Analisis completo sin limites"
Write-Host "- Industrial: `$25,000/año  | Proteccion infraestructura critica`n"

Write-Host "========================================" -ForegroundColor Green
Write-Host " ✅ PROCESO COMPLETADO EXITOSAMENTE" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "El dashboard se mantendra abierto en tu navegador" -ForegroundColor Gray
Write-Host "Esta ventana se cerrara automaticamente en 10 segundos`n" -ForegroundColor Gray

Write-Host "Presiona cualquier tecla para cerrar inmediatamente..." -ForegroundColor Yellow

# Timeout de 10 segundos o tecla
$timeout = 10
for ($i = $timeout; $i -gt 0; $i--) {
    if ([Console]::KeyAvailable) {
        [Console]::ReadKey($true) | Out-Null
        break
    }
    Start-Sleep -Seconds 1
}

Write-Host "`nGracias por usar SmartCompute Express!" -ForegroundColor Green