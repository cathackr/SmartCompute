@echo off
setlocal EnableDelayedExpansion

:: SmartCompute Unified - Windows Installer
:: ==========================================
:: Instalador completo con Python embebido, validación de licencia y cifrado
:: Soporte para Enterprise/Industrial y modo Cliente/Servidor

title SmartCompute Unified - Installer v2.0.0
color 0B

echo.
echo  ========================================================
echo   SmartCompute Unified - Security Analysis Platform
echo  ========================================================
echo   Version: 2.0.0 ^| Build: 2025.09.18
echo   Enterprise ^& Industrial ^| Client ^& Server modes
echo   Copyright (c) 2025 SmartCompute Security Solutions
echo  ========================================================
echo.

:: Variables de configuración base
set "PRODUCT_VERSION=2.0.0"
set "DOWNLOAD_SERVER=https://secure.smartcompute.enterprise"
set "LICENSE_SERVER=https://license.smartcompute.enterprise"
set "PYTHON_VERSION=3.11.9"
set "TEMP_DIR=%TEMP%\SmartCompute_Install"

:: Variables que se configurarán según selección
set "PRODUCT_NAME="
set "PRODUCT_TYPE="
set "DEPLOYMENT_MODE="
set "DEFAULT_INSTALL_DIR="

:: Verificar privilegios de administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Este instalador requiere privilegios de administrador.
    echo         Ejecute como administrador y vuelva a intentar.
    pause
    exit /b 1
)

echo [INFO] Verificando privilegios... OK
echo.

:: Selección de producto y modo
call :SelectProductAndMode
if %errorLevel% neq 0 (
    echo [ERROR] Selección cancelada por el usuario.
    pause
    exit /b 1
)

:: Crear directorio temporal
if exist "%TEMP_DIR%" rmdir /s /q "%TEMP_DIR%"
mkdir "%TEMP_DIR%"
cd /d "%TEMP_DIR%"

echo [INFO] Directorio temporal: %TEMP_DIR%
echo.

:: Verificar conexión a internet
echo [STEP 1/8] Verificando conectividad...
ping -n 1 google.com >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] No se detectó conexión a internet.
    echo         SmartCompute Enterprise requiere conexión para validar la licencia.
    pause
    exit /b 1
)
echo [INFO] Conectividad verificada... OK
echo.

:: Solicitar credenciales de licencia
echo [STEP 2/8] Validación de licencia...
echo.
echo Por favor, ingrese sus credenciales de licencia:
echo (Estas credenciales se proporcionan al momento de la compra)
echo.
set /p "LICENSE_USER=Usuario de licencia: "
echo.
set /p "LICENSE_PASS=Contraseña: "
echo.

if "%LICENSE_USER%"=="" (
    echo [ERROR] Usuario de licencia requerido.
    pause
    exit /b 1
)

if "%LICENSE_PASS%"=="" (
    echo [ERROR] Contraseña de licencia requerida.
    pause
    exit /b 1
)

:: Validar licencia de red online
echo [INFO] Validando licencia de red con servidor...
call :ValidateLicenseNetwork "%LICENSE_USER%" "%LICENSE_PASS%"
if %errorLevel% neq 0 (
    echo [ERROR] Licencia inválida o expirada.
    pause
    exit /b 1
)
echo [INFO] Licencia válida... OK
echo.

:: Solicitar directorio de instalación
echo [STEP 3/8] Configuración de directorio...
echo.
echo Directorio de instalación predeterminado:
echo %DEFAULT_INSTALL_DIR%
echo.
set /p "CUSTOM_DIR=Presione Enter para usar el predeterminado o ingrese ruta personalizada: "

if "%CUSTOM_DIR%"=="" (
    set "INSTALL_DIR=%DEFAULT_INSTALL_DIR%"
) else (
    set "INSTALL_DIR=%CUSTOM_DIR%"
)

echo [INFO] Directorio de instalación: %INSTALL_DIR%
echo.

:: Verificar espacio en disco
echo [INFO] Verificando espacio en disco...
for %%A in ("%INSTALL_DIR%") do set "DRIVE=%%~dA"
for /f "tokens=3" %%a in ('dir /-c %DRIVE% ^| find "bytes free"') do set "FREE_SPACE=%%a"
set FREE_SPACE=%FREE_SPACE:,=%

if %FREE_SPACE% LSS 1073741824 (
    echo [ERROR] Espacio insuficiente. Se requieren al menos 1 GB libres.
    pause
    exit /b 1
)
echo [INFO] Espacio en disco suficiente... OK
echo.

:: Descargar Python embebido
echo [STEP 4/8] Descargando Python embebido...
call :DownloadPythonEmbedded
if %errorLevel% neq 0 (
    echo [ERROR] Fallo al descargar Python embebido.
    pause
    exit /b 1
)
echo [INFO] Python embebido descargado... OK
echo.

:: Descargar SmartCompute Enterprise
echo [STEP 5/8] Descargando SmartCompute Enterprise...
call :DownloadSmartComputeSecure "%LICENSE_USER%" "%LICENSE_PASS%"
if %errorLevel% neq 0 (
    echo [ERROR] Fallo al descargar SmartCompute Enterprise.
    pause
    exit /b 1
)
echo [INFO] SmartCompute Enterprise descargado... OK
echo.

:: Crear directorio de instalación
echo [STEP 6/8] Instalando archivos...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

:: Extraer Python embebido
echo [INFO] Extrayendo Python embebido...
tar -xf python-embedded.zip -C "%INSTALL_DIR%"
if %errorLevel% neq 0 (
    echo [ERROR] Fallo al extraer Python embebido.
    pause
    exit /b 1
)

:: Extraer SmartCompute (cifrado)
echo [INFO] Extrayendo y descifrando SmartCompute Enterprise...
call :ExtractAndDecryptSmartCompute "%INSTALL_DIR%" "%LICENSE_USER%" "%LICENSE_PASS%"
if %errorLevel% neq 0 (
    echo [ERROR] Fallo al instalar SmartCompute Enterprise.
    pause
    exit /b 1
)

:: Configurar entorno Python
echo [INFO] Configurando entorno Python...
cd /d "%INSTALL_DIR%"

:: Crear archivo pth para módulos
echo smartcompute > python311._pth
echo Lib >> python311._pth
echo . >> python311._pth

:: Instalar dependencias
echo [INFO] Instalando dependencias...
python.exe -m pip install --no-warn-script-location psutil pystray Pillow cryptography requests asyncio

:: Crear configuración de licencia cifrada
echo [INFO] Configurando licencia...
call :CreateLicenseConfig "%LICENSE_USER%" "%LICENSE_PASS%"

:: Instalar componentes específicos del modo
call :InstallModeSpecificComponents

echo [INFO] Instalación de archivos completada... OK
echo.

:: Configurar servicio del sistema
echo [STEP 7/8] Configurando servicios del sistema...

:: Crear servicio de Windows
call :CreateWindowsService "%INSTALL_DIR%"

:: Configurar inicio automático
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /v "SmartCompute Enterprise" /t REG_SZ /d "\"%INSTALL_DIR%\smartcompute_tray.exe\"" /f >nul

:: Configurar firewall
echo [INFO] Configurando reglas de firewall...
netsh advfirewall firewall add rule name="SmartCompute Enterprise" dir=in action=allow program="%INSTALL_DIR%\smartcompute_tray.exe" >nul
netsh advfirewall firewall add rule name="SmartCompute Enterprise Out" dir=out action=allow program="%INSTALL_DIR%\smartcompute_tray.exe" >nul

:: Crear desinstalador
echo [INFO] Creando desinstalador...
call :CreateUninstaller "%INSTALL_DIR%"

echo [INFO] Configuración del sistema completada... OK
echo.

:: Registrar en el sistema
echo [STEP 8/8] Registrando en el sistema...

:: Crear entradas en el registro
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\SmartCompute Enterprise" /v "DisplayName" /t REG_SZ /d "%PRODUCT_NAME%" /f >nul
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\SmartCompute Enterprise" /v "DisplayVersion" /t REG_SZ /d "%PRODUCT_VERSION%" /f >nul
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\SmartCompute Enterprise" /v "Publisher" /t REG_SZ /d "SmartCompute Security Solutions" /f >nul
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\SmartCompute Enterprise" /v "InstallLocation" /t REG_SZ /d "%INSTALL_DIR%" /f >nul
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\SmartCompute Enterprise" /v "UninstallString" /t REG_SZ /d "\"%INSTALL_DIR%\uninstall.bat\"" /f >nul

:: Crear accesos directos
mkdir "%ProgramData%\Microsoft\Windows\Start Menu\Programs\SmartCompute Enterprise" 2>nul
echo [InternetShortcut] > "%ProgramData%\Microsoft\Windows\Start Menu\Programs\SmartCompute Enterprise\SmartCompute Enterprise.url"
echo URL=file:///%INSTALL_DIR%\smartcompute_tray.exe >> "%ProgramData%\Microsoft\Windows\Start Menu\Programs\SmartCompute Enterprise\SmartCompute Enterprise.url"

:: Crear acceso directo en el escritorio
echo [InternetShortcut] > "%PUBLIC%\Desktop\SmartCompute Enterprise.url"
echo URL=file:///%INSTALL_DIR%\smartcompute_tray.exe >> "%PUBLIC%\Desktop\SmartCompute Enterprise.url"

echo [INFO] Registro en sistema completado... OK
echo.

:: Limpiar archivos temporales
echo [INFO] Limpiando archivos temporales...
cd /d "%TEMP%"
rmdir /s /q "%TEMP_DIR%" 2>nul

:: Iniciar aplicación
echo.
echo  ========================================================
echo   INSTALACIÓN COMPLETADA EXITOSAMENTE
echo  ========================================================
echo.
echo   SmartCompute Enterprise se ha instalado correctamente.
echo.
echo   Ubicación: %INSTALL_DIR%
echo   Licencia válida hasta: %LICENSE_EXPIRY%
echo.
echo   La aplicación se iniciará automáticamente con Windows.
echo   Puede acceder desde el icono en la bandeja del sistema.
echo.

set /p "START_NOW=¿Desea iniciar SmartCompute Enterprise ahora? (S/N): "
if /i "%START_NOW%"=="S" (
    start "" "%INSTALL_DIR%\smartcompute_tray.exe"
    echo [INFO] SmartCompute Enterprise iniciado.
)

echo.
echo Presione cualquier tecla para finalizar...
pause >nul
exit /b 0

:: ============================================================================
:: FUNCIONES AUXILIARES
:: ============================================================================

:ValidateLicense
setlocal
set "user=%~1"
set "pass=%~2"

echo [INFO] Conectando al servidor de licencias...

:: Crear script PowerShell temporal para validación HTTPS
echo $user = '%user%'; > validate_license.ps1
echo $pass = '%pass%'; >> validate_license.ps1
echo $url = '%LICENSE_SERVER%/validate'; >> validate_license.ps1
echo $body = @{username=$user; password=$pass; product='enterprise'; version='%PRODUCT_VERSION%'} ^| ConvertTo-Json; >> validate_license.ps1
echo $headers = @{'Content-Type'='application/json'; 'User-Agent'='SmartCompute-Installer/1.0'}; >> validate_license.ps1
echo try { >> validate_license.ps1
echo     $response = Invoke-RestMethod -Uri $url -Method POST -Body $body -Headers $headers -TimeoutSec 30; >> validate_license.ps1
echo     if ($response.valid -eq $true) { >> validate_license.ps1
echo         Write-Host "LICENSE_VALID"; >> validate_license.ps1
echo         Write-Host "EXPIRY:" $response.expiry_date; >> validate_license.ps1
echo         exit 0; >> validate_license.ps1
echo     } else { >> validate_license.ps1
echo         Write-Host "LICENSE_INVALID:" $response.message; >> validate_license.ps1
echo         exit 1; >> validate_license.ps1
echo     } >> validate_license.ps1
echo } catch { >> validate_license.ps1
echo     Write-Host "CONNECTION_ERROR:" $_.Exception.Message; >> validate_license.ps1
echo     exit 2; >> validate_license.ps1
echo } >> validate_license.ps1

:: Ejecutar validación
powershell -ExecutionPolicy Bypass -File validate_license.ps1 > license_result.txt 2>&1
set "validation_result=%errorLevel%"

:: Procesar resultado
for /f "tokens=*" %%i in (license_result.txt) do (
    echo %%i | findstr "LICENSE_VALID" >nul
    if !errorLevel! equ 0 (
        echo [INFO] Licencia verificada correctamente.
    )
    echo %%i | findstr "EXPIRY:" >nul
    if !errorLevel! equ 0 (
        for /f "tokens=2" %%j in ("%%i") do set "LICENSE_EXPIRY=%%j"
        echo [INFO] Licencia válida hasta: !LICENSE_EXPIRY!
    )
    echo %%i | findstr "LICENSE_INVALID:" >nul
    if !errorLevel! equ 0 (
        for /f "tokens=2*" %%j in ("%%i") do echo [ERROR] Licencia inválida: %%k
    )
    echo %%i | findstr "CONNECTION_ERROR:" >nul
    if !errorLevel! equ 0 (
        for /f "tokens=2*" %%j in ("%%i") do echo [ERROR] Error de conexión: %%k
    )
)

:: Limpiar archivos temporales
del validate_license.ps1 2>nul
del license_result.txt 2>nul

endlocal
exit /b %validation_result%

:DownloadPythonEmbedded
setlocal

echo [INFO] Descargando Python %PYTHON_VERSION% embebido...

:: URL oficial de Python embebido
set "PYTHON_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-embed-amd64.zip"

:: Descargar usando PowerShell
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile 'python-embedded.zip' -UserAgent 'SmartCompute-Installer/1.0'}" 2>nul

if not exist "python-embedded.zip" (
    echo [ERROR] Fallo al descargar Python embebido.
    endlocal
    exit /b 1
)

:: Verificar integridad (tamaño mínimo esperado: 10MB)
for %%F in ("python-embedded.zip") do (
    if %%~zF LSS 10485760 (
        echo [ERROR] Archivo de Python embebido incompleto.
        endlocal
        exit /b 1
    )
)

echo [INFO] Python embebido descargado correctamente (%%~zF bytes).

endlocal
exit /b 0

:DownloadSmartComputeSecure
setlocal
set "user=%~1"
set "pass=%~2"

echo [INFO] Descargando SmartCompute Enterprise (cifrado)...

:: Crear script PowerShell para descarga segura
echo $user = '%user%'; > download_smartcompute.ps1
echo $pass = '%pass%'; >> download_smartcompute.ps1
echo $url = '%DOWNLOAD_SERVER%/enterprise/package'; >> download_smartcompute.ps1
echo $creds = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("$user`:$pass")); >> download_smartcompute.ps1
echo $headers = @{'Authorization'="Basic $creds"; 'User-Agent'='SmartCompute-Installer/1.0'}; >> download_smartcompute.ps1
echo try { >> download_smartcompute.ps1
echo     Invoke-WebRequest -Uri $url -OutFile 'smartcompute_enterprise.enc' -Headers $headers -TimeoutSec 120; >> download_smartcompute.ps1
echo     Write-Host "DOWNLOAD_SUCCESS"; >> download_smartcompute.ps1
echo     exit 0; >> download_smartcompute.ps1
echo } catch { >> download_smartcompute.ps1
echo     Write-Host "DOWNLOAD_ERROR:" $_.Exception.Message; >> download_smartcompute.ps1
echo     exit 1; >> download_smartcompute.ps1
echo } >> download_smartcompute.ps1

:: Ejecutar descarga
powershell -ExecutionPolicy Bypass -File download_smartcompute.ps1 > download_result.txt 2>&1
set "download_result=%errorLevel%"

:: Verificar resultado
if %download_result% neq 0 (
    echo [ERROR] Fallo al descargar SmartCompute Enterprise.
    for /f "tokens=*" %%i in (download_result.txt) do echo %%i
    del download_smartcompute.ps1 2>nul
    del download_result.txt 2>nul
    endlocal
    exit /b 1
)

:: Verificar que se descargó el archivo
if not exist "smartcompute_enterprise.enc" (
    echo [ERROR] Archivo de SmartCompute Enterprise no encontrado.
    endlocal
    exit /b 1
)

echo [INFO] SmartCompute Enterprise descargado correctamente.

:: Limpiar
del download_smartcompute.ps1 2>nul
del download_result.txt 2>nul

endlocal
exit /b 0

:ExtractAndDecryptSmartCompute
setlocal
set "install_dir=%~1"
set "user=%~2"
set "pass=%~3"

echo [INFO] Descifrando SmartCompute Enterprise...

:: Crear script Python para descifrado
echo import base64 > decrypt_smartcompute.py
echo import hashlib >> decrypt_smartcompute.py
echo from cryptography.fernet import Fernet >> decrypt_smartcompute.py
echo import zipfile >> decrypt_smartcompute.py
echo import os >> decrypt_smartcompute.py
echo. >> decrypt_smartcompute.py
echo # Generar clave de descifrado basada en credenciales >> decrypt_smartcompute.py
echo user = '%user%' >> decrypt_smartcompute.py
echo password = '%pass%' >> decrypt_smartcompute.py
echo key_material = f"{user}:{password}:smartcompute:enterprise".encode() >> decrypt_smartcompute.py
echo key = base64.urlsafe_b64encode(hashlib.sha256(key_material).digest()) >> decrypt_smartcompute.py
echo. >> decrypt_smartcompute.py
echo try: >> decrypt_smartcompute.py
echo     fernet = Fernet(key) >> decrypt_smartcompute.py
echo     with open('smartcompute_enterprise.enc', 'rb') as f: >> decrypt_smartcompute.py
echo         encrypted_data = f.read() >> decrypt_smartcompute.py
echo     decrypted_data = fernet.decrypt(encrypted_data) >> decrypt_smartcompute.py
echo     with open('smartcompute_enterprise.zip', 'wb') as f: >> decrypt_smartcompute.py
echo         f.write(decrypted_data) >> decrypt_smartcompute.py
echo     print("DECRYPT_SUCCESS") >> decrypt_smartcompute.py
echo except Exception as e: >> decrypt_smartcompute.py
echo     print(f"DECRYPT_ERROR: {e}") >> decrypt_smartcompute.py
echo     exit(1) >> decrypt_smartcompute.py

:: Ejecutar descifrado usando Python embebido
"%install_dir%\python.exe" decrypt_smartcompute.py > decrypt_result.txt 2>&1
set "decrypt_result=%errorLevel%"

if %decrypt_result% neq 0 (
    echo [ERROR] Fallo al descifrar SmartCompute Enterprise.
    for /f "tokens=*" %%i in (decrypt_result.txt) do echo %%i
    endlocal
    exit /b 1
)

:: Extraer archivos
echo [INFO] Extrayendo archivos del programa...
tar -xf smartcompute_enterprise.zip -C "%install_dir%"
if %errorLevel% neq 0 (
    echo [ERROR] Fallo al extraer archivos.
    endlocal
    exit /b 1
)

:: Limpiar archivos temporales de descifrado
del decrypt_smartcompute.py 2>nul
del decrypt_result.txt 2>nul
del smartcompute_enterprise.enc 2>nul
del smartcompute_enterprise.zip 2>nul

echo [INFO] SmartCompute Enterprise instalado correctamente.

endlocal
exit /b 0

:CreateLicenseConfig
setlocal
set "user=%~1"
set "pass=%~2"
set "install_dir=%INSTALL_DIR%"

echo [INFO] Configurando licencia de usuario...

:: Crear directorio de configuración
mkdir "%install_dir%\config" 2>nul

:: Crear configuración cifrada de licencia
echo import base64 > create_license_config.py
echo import hashlib >> create_license_config.py
echo from cryptography.fernet import Fernet >> create_license_config.py
echo import json >> create_license_config.py
echo from datetime import datetime, timedelta >> create_license_config.py
echo. >> create_license_config.py
echo # Datos de licencia >> create_license_config.py
echo license_data = { >> create_license_config.py
echo     'username': '%user%', >> create_license_config.py
echo     'license_hash': hashlib.sha256('%user%:%pass%'.encode()).hexdigest(), >> create_license_config.py
echo     'product': 'SmartCompute Enterprise', >> create_license_config.py
echo     'version': '%PRODUCT_VERSION%', >> create_license_config.py
echo     'install_date': datetime.now().isoformat(), >> create_license_config.py
echo     'expiry_date': '%LICENSE_EXPIRY%', >> create_license_config.py
echo     'machine_id': hashlib.md5(str(hash(os.environ.get('COMPUTERNAME', 'unknown'))).encode()).hexdigest() >> create_license_config.py
echo } >> create_license_config.py
echo. >> create_license_config.py
echo # Cifrar configuración >> create_license_config.py
echo key_material = '%user%:%pass%:config'.encode() >> create_license_config.py
echo key = base64.urlsafe_b64encode(hashlib.sha256(key_material).digest()) >> create_license_config.py
echo fernet = Fernet(key) >> create_license_config.py
echo encrypted_config = fernet.encrypt(json.dumps(license_data).encode()) >> create_license_config.py
echo. >> create_license_config.py
echo with open('%install_dir%\\config\\license.enc', 'wb') as f: >> create_license_config.py
echo     f.write(encrypted_config) >> create_license_config.py
echo. >> create_license_config.py
echo print("LICENSE_CONFIG_CREATED") >> create_license_config.py

:: Ejecutar creación de configuración
"%install_dir%\python.exe" create_license_config.py >nul 2>&1

:: Limpiar
del create_license_config.py 2>nul

endlocal
exit /b 0

:CreateWindowsService
setlocal
set "install_dir=%~1"

echo [INFO] Configurando servicio de Windows...

:: Crear script de servicio
echo import win32serviceutil > "%install_dir%\service.py"
echo import win32service >> "%install_dir%\service.py"
echo import win32event >> "%install_dir%\service.py"
echo import servicemanager >> "%install_dir%\service.py"
echo import subprocess >> "%install_dir%\service.py"
echo import sys >> "%install_dir%\service.py"
echo import os >> "%install_dir%\service.py"
echo. >> "%install_dir%\service.py"
echo class SmartComputeService(win32serviceutil.ServiceFramework): >> "%install_dir%\service.py"
echo     _svc_name_ = 'SmartComputeEnterprise' >> "%install_dir%\service.py"
echo     _svc_display_name_ = 'SmartCompute Enterprise Security Service' >> "%install_dir%\service.py"
echo     _svc_description_ = 'Continuous security analysis and monitoring service' >> "%install_dir%\service.py"
echo. >> "%install_dir%\service.py"
echo     def __init__(self, args): >> "%install_dir%\service.py"
echo         win32serviceutil.ServiceFramework.__init__(self, args) >> "%install_dir%\service.py"
echo         self.hWaitStop = win32event.CreateEvent(None, 0, 0, None) >> "%install_dir%\service.py"
echo. >> "%install_dir%\service.py"
echo     def SvcStop(self): >> "%install_dir%\service.py"
echo         self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING) >> "%install_dir%\service.py"
echo         win32event.SetEvent(self.hWaitStop) >> "%install_dir%\service.py"
echo. >> "%install_dir%\service.py"
echo     def SvcDoRun(self): >> "%install_dir%\service.py"
echo         servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, >> "%install_dir%\service.py"
echo                               servicemanager.PYS_SERVICE_STARTED, >> "%install_dir%\service.py"
echo                               (self._svc_name_, '')) >> "%install_dir%\service.py"
echo         subprocess.Popen([r'%install_dir%\python.exe', r'%install_dir%\smartcompute_tray.py']) >> "%install_dir%\service.py"
echo         win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE) >> "%install_dir%\service.py"
echo. >> "%install_dir%\service.py"
echo if __name__ == '__main__': >> "%install_dir%\service.py"
echo     win32serviceutil.HandleCommandLine(SmartComputeService) >> "%install_dir%\service.py"

endlocal
exit /b 0

:CreateUninstaller
setlocal
set "install_dir=%~1"

echo [INFO] Creando desinstalador...

:: Crear script de desinstalación
echo @echo off > "%install_dir%\uninstall.bat"
echo setlocal EnableDelayedExpansion >> "%install_dir%\uninstall.bat"
echo. >> "%install_dir%\uninstall.bat"
echo title SmartCompute Enterprise - Desinstalador >> "%install_dir%\uninstall.bat"
echo. >> "%install_dir%\uninstall.bat"
echo echo. >> "%install_dir%\uninstall.bat"
echo echo  ================================================ >> "%install_dir%\uninstall.bat"
echo echo   SmartCompute Enterprise - Desinstalador >> "%install_dir%\uninstall.bat"
echo echo  ================================================ >> "%install_dir%\uninstall.bat"
echo echo. >> "%install_dir%\uninstall.bat"
echo. >> "%install_dir%\uninstall.bat"
echo echo [WARNING] Esta acción desinstalará completamente SmartCompute Enterprise. >> "%install_dir%\uninstall.bat"
echo echo           Todos los datos y configuraciones serán eliminados. >> "%install_dir%\uninstall.bat"
echo echo. >> "%install_dir%\uninstall.bat"
echo set /p "CONFIRM=¿Está seguro de continuar? (S/N): " >> "%install_dir%\uninstall.bat"
echo if /i not "!CONFIRM!"=="S" ( >> "%install_dir%\uninstall.bat"
echo     echo Desinstalación cancelada. >> "%install_dir%\uninstall.bat"
echo     pause >> "%install_dir%\uninstall.bat"
echo     exit /b 0 >> "%install_dir%\uninstall.bat"
echo ^) >> "%install_dir%\uninstall.bat"
echo. >> "%install_dir%\uninstall.bat"
echo echo [STEP 1/5] Deteniendo servicios... >> "%install_dir%\uninstall.bat"
echo taskkill /f /im smartcompute_tray.exe 2^>nul >> "%install_dir%\uninstall.bat"
echo python.exe service.py stop 2^>nul >> "%install_dir%\uninstall.bat"
echo python.exe service.py remove 2^>nul >> "%install_dir%\uninstall.bat"
echo. >> "%install_dir%\uninstall.bat"
echo echo [STEP 2/5] Eliminando del inicio automático... >> "%install_dir%\uninstall.bat"
echo reg delete "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /v "SmartCompute Enterprise" /f 2^>nul >> "%install_dir%\uninstall.bat"
echo. >> "%install_dir%\uninstall.bat"
echo echo [STEP 3/5] Eliminando reglas de firewall... >> "%install_dir%\uninstall.bat"
echo netsh advfirewall firewall delete rule name="SmartCompute Enterprise" 2^>nul >> "%install_dir%\uninstall.bat"
echo netsh advfirewall firewall delete rule name="SmartCompute Enterprise Out" 2^>nul >> "%install_dir%\uninstall.bat"
echo. >> "%install_dir%\uninstall.bat"
echo echo [STEP 4/5] Eliminando accesos directos... >> "%install_dir%\uninstall.bat"
echo del "%PUBLIC%\Desktop\SmartCompute Enterprise.url" 2^>nul >> "%install_dir%\uninstall.bat"
echo rmdir /s /q "%ProgramData%\Microsoft\Windows\Start Menu\Programs\SmartCompute Enterprise" 2^>nul >> "%install_dir%\uninstall.bat"
echo. >> "%install_dir%\uninstall.bat"
echo echo [STEP 5/5] Eliminando archivos de programa... >> "%install_dir%\uninstall.bat"
echo reg delete "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\SmartCompute Enterprise" /f 2^>nul >> "%install_dir%\uninstall.bat"
echo. >> "%install_dir%\uninstall.bat"
echo cd /d "%%TEMP%%" >> "%install_dir%\uninstall.bat"
echo rmdir /s /q "%install_dir%" 2^>nul >> "%install_dir%\uninstall.bat"
echo. >> "%install_dir%\uninstall.bat"
echo echo. >> "%install_dir%\uninstall.bat"
echo echo SmartCompute ha sido desinstalado correctamente. >> "%install_dir%\uninstall.bat"
echo echo. >> "%install_dir%\uninstall.bat"
echo pause >> "%install_dir%\uninstall.bat"

:SelectProductAndMode
setlocal

echo.
echo  ========================================================
echo   SELECCIÓN DE PRODUCTO Y MODO DE INSTALACIÓN
echo  ========================================================
echo.
echo   Esta licencia SmartCompute le permite instalar tanto
echo   la versión Enterprise como Industrial en cualquier
echo   cantidad de hosts de su red hasta la expiración.
echo.
echo  --------------------------------------------------------
echo   1. SmartCompute Enterprise (Sistemas tradicionales TI)
echo   2. SmartCompute Industrial (Sistemas SCADA/PLC)
echo  --------------------------------------------------------
echo.

:SelectProductType
set /p "PRODUCT_CHOICE=Seleccione el tipo de producto (1 o 2): "

if "%PRODUCT_CHOICE%"=="1" (
    set "PRODUCT_TYPE=enterprise"
    set "PRODUCT_NAME=SmartCompute Enterprise"
    set "DEFAULT_INSTALL_DIR=%ProgramFiles%\SmartCompute Enterprise"
) else if "%PRODUCT_CHOICE%"=="2" (
    set "PRODUCT_TYPE=industrial"
    set "PRODUCT_NAME=SmartCompute Industrial"
    set "DEFAULT_INSTALL_DIR=%ProgramFiles%\SmartCompute Industrial"
) else (
    echo.
    echo [ERROR] Opción inválida. Seleccione 1 o 2.
    echo.
    goto SelectProductType
)

echo.
echo  ========================================================
echo   SELECCIÓN DE MODO DE DESPLIEGUE
echo  ========================================================
echo.
echo   %PRODUCT_NAME% puede funcionar en dos modos:
echo.
echo  --------------------------------------------------------
echo   1. CLIENTE  - Se conecta a un servidor central existente
echo   2. SERVIDOR - Actúa como servidor central para la red
echo  --------------------------------------------------------
echo.
echo   Nota: Una licencia permite ambos modos simultáneamente
echo         en diferentes hosts de la misma red organizacional.
echo.

:SelectDeploymentMode
set /p "MODE_CHOICE=Seleccione el modo de instalación (1 o 2): "

if "%MODE_CHOICE%"=="1" (
    set "DEPLOYMENT_MODE=client"
    echo.
    echo [INFO] Modo CLIENTE seleccionado
    echo        Se configurará para conectar a servidor central
) else if "%MODE_CHOICE%"=="2" (
    set "DEPLOYMENT_MODE=server"
    echo.
    echo [INFO] Modo SERVIDOR seleccionado
    echo        Se configurará como servidor central de red
) else (
    echo.
    echo [ERROR] Opción inválida. Seleccione 1 o 2.
    echo.
    goto SelectDeploymentMode
)

echo.
echo  ========================================================
echo   CONFIGURACIÓN SELECCIONADA
echo  ========================================================
echo.
echo   Producto:      %PRODUCT_NAME%
echo   Tipo:          %PRODUCT_TYPE%
echo   Modo:          %DEPLOYMENT_MODE%
echo   Directorio:    %DEFAULT_INSTALL_DIR%
echo.

set /p "CONFIRM_CONFIG=¿Confirma la configuración? (S/N): "
if /i not "%CONFIRM_CONFIG%"=="S" (
    echo.
    echo Volviendo al menú de selección...
    echo.
    goto SelectProductType
)

:: Exportar variables al entorno principal
endlocal & (
    set "PRODUCT_NAME=%PRODUCT_NAME%"
    set "PRODUCT_TYPE=%PRODUCT_TYPE%"
    set "DEPLOYMENT_MODE=%DEPLOYMENT_MODE%"
    set "DEFAULT_INSTALL_DIR=%DEFAULT_INSTALL_DIR%"
)

echo.
echo [INFO] Configuración confirmada
echo.

exit /b 0

:ValidateLicenseNetwork
setlocal
set "user=%~1"
set "pass=%~2"

echo [INFO] Validando licencia de red...

:: Crear script PowerShell extendido para validación de red
echo $user = '%user%'; > validate_network_license.ps1
echo $pass = '%pass%'; >> validate_network_license.ps1
echo $productType = '%PRODUCT_TYPE%'; >> validate_network_license.ps1
echo $deploymentMode = '%DEPLOYMENT_MODE%'; >> validate_network_license.ps1
echo $machineName = $env:COMPUTERNAME; >> validate_network_license.ps1
echo $domainName = (Get-WmiObject Win32_ComputerSystem).Domain; >> validate_network_license.ps1
echo $ipAddress = (Get-NetIPConfiguration ^| Where-Object {$_.NetAdapter.Status -eq "Up"}).IPv4Address.IPAddress ^| Select-Object -First 1; >> validate_network_license.ps1
echo $url = '%LICENSE_SERVER%/validate-network'; >> validate_network_license.ps1
echo. >> validate_network_license.ps1
echo $body = @{ >> validate_network_license.ps1
echo     username = $user; >> validate_network_license.ps1
echo     password = $pass; >> validate_network_license.ps1
echo     product = $productType; >> validate_network_license.ps1
echo     deployment_mode = $deploymentMode; >> validate_network_license.ps1
echo     version = '%PRODUCT_VERSION%'; >> validate_network_license.ps1
echo     machine_name = $machineName; >> validate_network_license.ps1
echo     domain_name = $domainName; >> validate_network_license.ps1
echo     ip_address = $ipAddress; >> validate_network_license.ps1
echo     unlimited_hosts = $true >> validate_network_license.ps1
echo } ^| ConvertTo-Json; >> validate_network_license.ps1
echo. >> validate_network_license.ps1
echo $headers = @{'Content-Type'='application/json'; 'User-Agent'='SmartCompute-Installer/2.0'}; >> validate_network_license.ps1
echo. >> validate_network_license.ps1
echo try { >> validate_network_license.ps1
echo     $response = Invoke-RestMethod -Uri $url -Method POST -Body $body -Headers $headers -TimeoutSec 30; >> validate_network_license.ps1
echo     if ($response.valid -eq $true) { >> validate_network_license.ps1
echo         Write-Host "LICENSE_VALID"; >> validate_network_license.ps1
echo         Write-Host "NETWORK_LICENSE:True"; >> validate_network_license.ps1
echo         Write-Host "UNLIMITED_HOSTS:True"; >> validate_network_license.ps1
echo         Write-Host "EXPIRY:" $response.expiry_date; >> validate_network_license.ps1
echo         Write-Host "LICENSED_PRODUCTS:" $response.licensed_products; >> validate_network_license.ps1
echo         Write-Host "MAX_CONCURRENT:" $response.max_concurrent_installations; >> validate_network_license.ps1
echo         exit 0; >> validate_network_license.ps1
echo     } else { >> validate_network_license.ps1
echo         Write-Host "LICENSE_INVALID:" $response.message; >> validate_network_license.ps1
echo         exit 1; >> validate_network_license.ps1
echo     } >> validate_network_license.ps1
echo } catch { >> validate_network_license.ps1
echo     Write-Host "CONNECTION_ERROR:" $_.Exception.Message; >> validate_network_license.ps1
echo     exit 2; >> validate_network_license.ps1
echo } >> validate_network_license.ps1

:: Ejecutar validación
powershell -ExecutionPolicy Bypass -File validate_network_license.ps1 > network_license_result.txt 2>&1
set "validation_result=%errorLevel%"

:: Procesar resultado
for /f "tokens=*" %%i in (network_license_result.txt) do (
    echo %%i | findstr "LICENSE_VALID" >nul
    if !errorLevel! equ 0 (
        echo [INFO] Licencia de red verificada correctamente.
    )
    echo %%i | findstr "NETWORK_LICENSE:" >nul
    if !errorLevel! equ 0 (
        echo [INFO] Licencia de red ilimitada confirmada.
    )
    echo %%i | findstr "UNLIMITED_HOSTS:" >nul
    if !errorLevel! equ 0 (
        echo [INFO] Hosts ilimitados en red organizacional.
    )
    echo %%i | findstr "EXPIRY:" >nul
    if !errorLevel! equ 0 (
        for /f "tokens=2" %%j in ("%%i") do set "LICENSE_EXPIRY=%%j"
        echo [INFO] Licencia válida hasta: !LICENSE_EXPIRY!
    )
    echo %%i | findstr "LICENSED_PRODUCTS:" >nul
    if !errorLevel! equ 0 (
        for /f "tokens=2" %%j in ("%%i") do echo [INFO] Productos licenciados: %%j
    )
    echo %%i | findstr "MAX_CONCURRENT:" >nul
    if !errorLevel! equ 0 (
        for /f "tokens=2" %%j in ("%%i") do (
            if "%%j"=="unlimited" (
                echo [INFO] Instalaciones concurrentes: Ilimitadas
            ) else (
                echo [INFO] Instalaciones concurrentes máximas: %%j
            )
        )
    )
    echo %%i | findstr "LICENSE_INVALID:" >nul
    if !errorLevel! equ 0 (
        for /f "tokens=2*" %%j in ("%%i") do echo [ERROR] Licencia inválida: %%k
    )
    echo %%i | findstr "CONNECTION_ERROR:" >nul
    if !errorLevel! equ 0 (
        for /f "tokens=2*" %%j in ("%%i") do echo [ERROR] Error de conexión: %%k
    )
)

:: Limpiar archivos temporales
del validate_network_license.ps1 2>nul
del network_license_result.txt 2>nul

endlocal
exit /b %validation_result%

:InstallModeSpecificComponents
setlocal

echo [INFO] Instalando componentes específicos del modo %DEPLOYMENT_MODE%...

if "%DEPLOYMENT_MODE%"=="server" (
    call :InstallServerComponents
) else (
    call :InstallClientComponents
)

endlocal
exit /b 0

:InstallServerComponents
echo [INFO] Instalando componentes del servidor central...

:: Copiar archivos del servidor
echo import sys > "%INSTALL_DIR%\start_server.py"
echo sys.path.append('.') >> "%INSTALL_DIR%\start_server.py"
echo from smartcompute_central_server import main >> "%INSTALL_DIR%\start_server.py"
echo if __name__ == '__main__': main() >> "%INSTALL_DIR%\start_server.py"

:: Crear archivo de configuración del servidor
echo server: > "%INSTALL_DIR%\server_config.yaml"
echo   host: "0.0.0.0" >> "%INSTALL_DIR%\server_config.yaml"
echo   port: 8080 >> "%INSTALL_DIR%\server_config.yaml"
echo   ssl_port: 8443 >> "%INSTALL_DIR%\server_config.yaml"
echo database: >> "%INSTALL_DIR%\server_config.yaml"
echo   path: "%INSTALL_DIR%\data\smartcompute.db" >> "%INSTALL_DIR%\server_config.yaml"
echo   backup_enabled: true >> "%INSTALL_DIR%\server_config.yaml"
echo   raid_config: "raid1" >> "%INSTALL_DIR%\server_config.yaml"
echo security: >> "%INSTALL_DIR%\server_config.yaml"
echo   api_key_required: true >> "%INSTALL_DIR%\server_config.yaml"
echo   jwt_expiration: 86400 >> "%INSTALL_DIR%\server_config.yaml"
echo incident_management: >> "%INSTALL_DIR%\server_config.yaml"
echo   auto_escalation: true >> "%INSTALL_DIR%\server_config.yaml"

:: Crear directorio de datos
mkdir "%INSTALL_DIR%\data" 2>nul
mkdir "%INSTALL_DIR%\logs" 2>nul
mkdir "%INSTALL_DIR%\backups" 2>nul

echo [INFO] Componentes del servidor instalados.
exit /b 0

:InstallClientComponents
echo [INFO] Instalando componentes del cliente...

:: Crear archivo de configuración del cliente
echo { > "%INSTALL_DIR%\client_config.json"
echo   "server_url": "https://smartcompute-server.local:8443", >> "%INSTALL_DIR%\client_config.json"
echo   "api_key": "smartcompute-%PRODUCT_TYPE%-key-2025", >> "%INSTALL_DIR%\client_config.json"
echo   "client_type": "%PRODUCT_TYPE%", >> "%INSTALL_DIR%\client_config.json"
echo   "ssl_verify": false, >> "%INSTALL_DIR%\client_config.json"
echo   "reconnect_attempts": 5, >> "%INSTALL_DIR%\client_config.json"
echo   "heartbeat_interval": 30, >> "%INSTALL_DIR%\client_config.json"
echo   "auto_submit": true, >> "%INSTALL_DIR%\client_config.json"
echo   "analysis_interval": 300 >> "%INSTALL_DIR%\client_config.json"
echo } >> "%INSTALL_DIR%\client_config.json"

:: Crear script de conexión
echo import sys > "%INSTALL_DIR%\connect_to_server.py"
echo sys.path.append('.') >> "%INSTALL_DIR%\connect_to_server.py"
echo from smartcompute_mcp_client import main >> "%INSTALL_DIR%\connect_to_server.py"
echo if __name__ == '__main__': main() >> "%INSTALL_DIR%\connect_to_server.py"

echo [INFO] Componentes del cliente instalados.
exit /b 0

endlocal
exit /b 0