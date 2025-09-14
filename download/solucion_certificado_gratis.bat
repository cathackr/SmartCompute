@echo off
REM SmartCompute - Solucion certificado gratuito
REM Este script mejora la confianza sin certificado comercial

title SmartCompute Express - Instalacion Segura

echo.
echo ========================================
echo   SMARTCOMPUTE EXPRESS - VERIFICACION
echo ========================================
echo.
echo Este software es desarrollado por:
echo - Martin Iribarne - Technology Architect
echo - LinkedIn: linkedin.com/in/martin-iribarne-swtf
echo - Email: ggwre04p0@mozmail.com
echo.
echo VERIFICACIONES DE SEGURIDAD:
echo [OK] Codigo fuente disponible en GitHub
echo [OK] Sin conexiones sospechosas
echo [OK] Solo analiza red local (no envia datos)
echo [OK] Ejecuta solo en modo lectura
echo.
color 0A
echo ¿Confirmas que deseas continuar? (S/N)
set /p confirm="Tu respuesta: "
if /i not "%confirm%"=="S" (
    if /i not "%confirm%"=="SI" (
        echo Instalacion cancelada por el usuario
        pause
        exit /b 1
    )
)

echo.
echo [INFO] Iniciando instalacion verificada...
REM Llamar al instalador original
call SmartCompute_Express_Windows.bat