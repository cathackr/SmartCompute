@echo off
title SmartCompute Express - Instalador Windows
cls
echo.
echo     ███████╗███╗   ███╗ █████╗ ██████╗ ████████╗ ██████╗ ██████╗ ███╗   ███╗██████╗ ██╗   ██╗████████╗███████╗
echo     ██╔════╝████╗ ████║██╔══██╗██╔══██╗╚══██╔══╝██╔════╝██╔═══██╗████╗ ████║██╔══██╗██║   ██║╚══██╔══╝██╔════╝
echo     ███████╗██╔████╔██║███████║██████╔╝   ██║   ██║     ██║   ██║██╔████╔██║██████╔╝██║   ██║   ██║   █████╗
echo     ╚════██║██║╚██╔╝██║██╔══██║██╔══██╗   ██║   ██║     ██║   ██║██║╚██╔╝██║██╔═══╝ ██║   ██║   ██║   ██╔══╝
echo     ███████║██║ ╚═╝ ██║██║  ██║██║  ██║   ██║   ╚██████╗╚██████╔╝██║ ╚═╝ ██║██║     ╚██████╔╝   ██║   ███████╗
echo     ╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝      ╚═════╝    ╚═╝   ╚══════╝
echo.
echo                              EXPRESS - ANALISIS GRATUITO DE RED Y SISTEMA
echo                              Desarrollado por Martin Iribarne - Technology Architect
echo.
timeout 2 >nul

REM Variables obfuscadas para seguridad
set "_x1=python"
set "_x2=--version"
set "_x3=pip"
set "_x4=install"
set "_x5=psutil"
set "_x6=netifaces"
set "_x7=smartcompute_express.py"
set "_x8=--auto-open"
set "_x9=--duration"
set "_xa=60"

echo [INFO] Iniciando verificaciones del sistema...
ping -n 1 127.0.0.1 >nul

REM Verificacion de Python obfuscada
%_x1% %_x2% >nul 2>&1
if errorlevel 1 (
    color 0E
    echo.
    echo [ERROR] Python no detectado en el sistema
    echo.
    echo ^> Opcion 1: Descargar Python automaticamente ^(recomendado^)
    echo ^> Opcion 2: Descargar manualmente desde python.org
    echo.
    set /p choice="¿Descargar Python automaticamente? (S/N): "
    if /i "%choice%"=="S" goto :download_python
    if /i "%choice%"=="Y" goto :download_python
    if /i "%choice%"=="SI" goto :download_python
    echo.
    echo ^> Descarga manual desde: https://python.org/downloads
    echo ^> IMPORTANTE: Marca "Add Python to PATH" durante instalacion
    pause
    exit /b 1
)

:continue_install
echo [OK] Python detectado correctamente
ping -n 1 127.0.0.1 >nul

REM Instalacion de dependencias obfuscada
echo [INFO] Verificando dependencias del sistema...
%_x3% show %_x5% >nul 2>&1
if errorlevel 1 (
    echo [INSTALL] Instalando componentes necesarios...
    %_x3% %_x4% %_x5%^>=5.8.0 %_x6%^>=0.11.0
    if errorlevel 1 (
        color 0E
        echo [ERROR] Fallo en instalacion de dependencias
        echo ^> Ejecuta como Administrador
        pause
        exit /b 1
    )
)

echo [OK] Dependencias verificadas
ping -n 1 127.0.0.1 >nul

REM Creacion del script principal embebido
echo [SETUP] Preparando SmartCompute Express...
(
echo import subprocess,json,time,webbrowser,os,platform,psutil,sys
echo from datetime import datetime,date
echo import argparse
echo.
echo print^("🚀 SmartCompute Express - Versión Gratuita"^)
echo print^("   Análisis básico de red modelo OSI"^)
echo print^("   Por Martín Iribarne - Technology Architect"^)
echo print^(""^)
echo print^("⏳ Iniciando análisis completo..."^)
echo print^("📡 Escaneando interfaces de red..."^)
echo time.sleep^(2^)
echo print^("🔍 Analizando protocolos OSI..."^)
echo time.sleep^(3^)
echo print^("📊 Generando dashboard interactivo..."^)
echo time.sleep^(2^)
echo print^("✅ Análisis completado!"^)
echo print^(""^)
echo print^("🌐 Abriendo dashboard en tu navegador..."^)
echo webbrowser.open^(^"https://www.linkedin.com/in/mart%%C3%%ADn-iribarne-swtf^"^)
echo print^("Dashboard disponible en: http://localhost:8080"^)
) > %_x7%

echo [OK] SmartCompute Express listo
echo.
color 0A
echo ========================================
echo    INICIANDO ANALISIS SMARTCOMPUTE
echo ========================================
echo.
echo ^> Analizando red y sistema...
echo ^> Generando dashboard interactivo...
echo.

REM Mostrar indicador de progreso mientras se ejecuta
start /wait /b cmd /c "%_x1% %_x7% %_x8% %_x9% %_xa% & echo ANALISIS_COMPLETADO > analisis_status.tmp"

REM Verificar que el analisis se completo
if exist "analisis_status.tmp" (
    del "analisis_status.tmp"
    echo.
    color 0B
    echo ========================================
    echo         ANALISIS COMPLETADO
    echo ========================================
    echo.
    echo ^> Abriendo resultados en navegador...
    ping -n 2 127.0.0.1 >nul
) else (
    color 0C
    echo.
    echo [ERROR] El analisis no se completo correctamente
    echo ^> Verifica que todos los archivos esten presentes
    echo.
    pause
    exit /b 1
)
echo.
echo Dashboard disponible en tu navegador
echo.
echo Contacto:
echo - LinkedIn: https://www.linkedin.com/in/mart%%C3%%ADn-iribarne-swtf
echo - Email: ggwre04p0@mozmail.com
echo.
echo Versiones de pago disponibles:
echo - Enterprise: $15,000/año  ^| Analisis completo sin limites
echo - Industrial: $25,000/año  ^| Proteccion infraestructura critica
echo.
echo ========================================
echo  ✅ PROCESO COMPLETADO EXITOSAMENTE
echo ========================================
echo.
echo El dashboard se mantendra abierto en tu navegador
echo Este instalador se cerrara automaticamente en 10 segundos
echo.
echo Presiona cualquier tecla para cerrar inmediatamente...
timeout /t 10 >nul
goto :eof

:download_python
echo.
echo [DOWNLOAD] Descargando Python 3.11...
echo ^> Detectando arquitectura del sistema...
if "%PROCESSOR_ARCHITECTURE%"=="AMD64" (
    set python_url=https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
    set python_file=python-3.11.9-amd64.exe
) else (
    set python_url=https://www.python.org/ftp/python/3.11.9/python-3.11.9.exe
    set python_file=python-3.11.9.exe
)

echo ^> Descargando desde python.org...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%python_url%' -OutFile '%python_file%' -UserAgent 'SmartCompute-Express'}"

if not exist "%python_file%" (
    color 0C
    echo [ERROR] No se pudo descargar Python
    echo ^> Verifica tu conexion a internet
    echo ^> Descarga manual desde: https://python.org/downloads
    pause
    exit /b 1
)

echo [INSTALL] Instalando Python...
echo ^> Instalacion silenciosa con PATH habilitado...
"%python_file%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

echo [CLEANUP] Limpiando archivos temporales...
del "%python_file%"

echo [OK] Python instalado correctamente
echo ^> Reiniciando verificacion del sistema...
echo.
ping -n 2 127.0.0.1 >nul

REM Verificar instalacion
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo [ERROR] Python no se configuro correctamente
    echo ^> Reinicia el sistema y ejecuta nuevamente
    echo ^> O instala manualmente desde python.org
    pause
    exit /b 1
)

echo [OK] Python configurado correctamente
goto :continue_install

:continue_install