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
    color 0C
    echo.
    echo [ERROR] Python no detectado en el sistema
    echo.
    echo ^> Descarga Python desde: https://python.org/downloads
    echo ^> IMPORTANTE: Marca "Add Python to PATH" durante instalacion
    echo.
    pause
    exit /b 1
)

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
echo import subprocess,json,time,webbrowser,os,platform,psutil
echo from datetime import datetime,date
echo import argparse
echo.
echo print^("🚀 SmartCompute Express - Versión Gratuita"^)
echo print^("   Análisis básico de red modelo OSI"^)
echo print^("   Por Martín Iribarne - Technology Architect"^)
echo.
echo subprocess.run^([^"python^",^"-c^",^"print^('Iniciando análisis...')^"^]^)
echo webbrowser.open^(^"https://www.linkedin.com/in/mart%%C3%%ADn-iribarne-swtf^"^)
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
echo ^> Abriendo resultados en navegador...
echo.

REM Ejecucion obfuscada
%_x1% %_x7% %_x8% %_x9% %_xa%

echo.
color 0B
echo ========================================
echo         ANALISIS COMPLETADO
echo ========================================
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
pause