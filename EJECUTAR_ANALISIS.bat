@echo off
echo ========================================
echo    SmartCompute Express - Windows
echo    Analisis automatico de red OSI
echo ========================================
echo.

REM Verificar si Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no encontrado
    echo Por favor instala Python desde: https://python.org/downloads
    echo Asegurate de marcar "Add Python to PATH" durante la instalacion
    pause
    exit /b 1
)

REM Verificar si las dependencias estan instaladas
echo Verificando dependencias...
pip show psutil >nul 2>&1
if errorlevel 1 (
    echo Instalando dependencias necesarias...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: No se pudieron instalar las dependencias
        echo Ejecuta este archivo como Administrador
        pause
        exit /b 1
    )
)

echo.
echo Iniciando analisis SmartCompute Express...
echo.
python smartcompute_express.py --auto-open

echo.
echo ========================================
echo    Analisis completado!
echo    Dashboard abierto en tu navegador
echo ========================================
pause