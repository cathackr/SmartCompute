@echo off
REM SmartCompute Express - Launcher para PowerShell Firmado
REM Este archivo ejecuta la version PowerShell firmada digitalmente

title SmartCompute Express - Launcher

echo.
echo  ========================================
echo    SMARTCOMPUTE EXPRESS - POWERSHELL
echo  ========================================
echo.
echo  Version firmada digitalmente
echo  Desarrollado por Martin Iribarne
echo.

REM Verificar si existe el archivo PowerShell
if not exist "SmartCompute_Express.ps1" (
    color 0C
    echo [ERROR] Archivo SmartCompute_Express.ps1 no encontrado
    echo.
    echo Asegurate de que todos los archivos esten en la misma carpeta:
    echo - SmartCompute_Express.ps1
    echo - SmartCompute_Express_PS.bat ^(este archivo^)
    echo.
    pause
    exit /b 1
)

REM Verificar política de ejecución PowerShell
echo [INFO] Verificando configuracion PowerShell...
powershell -Command "if ((Get-ExecutionPolicy -Scope CurrentUser) -eq 'Restricted') { Write-Host 'CONFIGURACION_NECESARIA' }"

REM Si necesita configuración, la aplicamos
for /f %%i in ('powershell -Command "Get-ExecutionPolicy -Scope CurrentUser"') do set policy=%%i
if "%policy%"=="Restricted" (
    echo [CONFIG] Configurando PowerShell para archivos firmados...
    powershell -Command "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force"
    if errorlevel 1 (
        color 0E
        echo [WARNING] No se pudo configurar automaticamente
        echo.
        echo Ejecuta manualmente en PowerShell como Administrador:
        echo Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
        echo.
        echo Luego ejecuta: .\SmartCompute_Express.ps1
        echo.
        pause
        exit /b 1
    )
    echo [OK] PowerShell configurado correctamente
)

echo [INFO] Iniciando SmartCompute Express...
echo.

REM Ejecutar PowerShell firmado
powershell -ExecutionPolicy Bypass -File "SmartCompute_Express.ps1"

REM Verificar si se ejecuto correctamente
if errorlevel 1 (
    color 0C
    echo.
    echo [ERROR] SmartCompute no se ejecuto correctamente
    echo.
    echo Opciones de solucion:
    echo 1. Ejecutar PowerShell como Administrador
    echo 2. Verificar que Python este instalado
    echo 3. Ejecutar: Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
    echo.
    pause
    exit /b 1
)

REM Mensaje final
color 0A
echo.
echo ========================================
echo   ✅ SMARTCOMPUTE EJECUTADO CON EXITO
echo ========================================
echo.
echo La version PowerShell proporciona:
echo - ✅ Firma digital automatica
echo - ✅ Mejor integracion con Windows
echo - ✅ Ejecucion mas confiable
echo - ✅ Mensajes de error mas claros
echo.
timeout /t 5 >nul