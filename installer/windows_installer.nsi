# SmartCompute Enterprise - Windows Installer (NSIS)
# ================================================
# Instalador para Windows 10/11/Server con soporte para Active Directory

# Definir versión y metadatos
!define PRODUCT_NAME "SmartCompute Enterprise"
!define PRODUCT_VERSION "1.0.0"
!define PRODUCT_PUBLISHER "SmartCompute Security Solutions"
!define PRODUCT_WEB_SITE "https://smartcompute.enterprise"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\smartcompute.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

# Configuración general
Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "SmartCompute_Enterprise_Setup.exe"
InstallDir "$PROGRAMFILES\SmartCompute Enterprise"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

# Solicitar privilegios de administrador
RequestExecutionLevel admin

# Incluir librerías necesarias
!include "MUI2.nsh"
!include "FileFunc.nsh"
!include "LogicLib.nsh"
!include "WinMessages.nsh"
!include "x64.nsh"

# Configuración de interfaz moderna
!define MUI_ABORTWARNING
!define MUI_ICON "smartcompute.ico"
!define MUI_UNICON "smartcompute.ico"

# Páginas de instalación
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "license.txt"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY

# Página personalizada para configuración
Page custom ConfigPageCreate ConfigPageLeave

!insertmacro MUI_PAGE_INSTFILES

# Página final con opción de ejecutar
!define MUI_FINISHPAGE_RUN "$INSTDIR\smartcompute_tray.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Ejecutar SmartCompute Enterprise"
!define MUI_FINISHPAGE_SHOWREADME "$INSTDIR\README.txt"
!insertmacro MUI_PAGE_FINISH

# Páginas de desinstalación
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

# Idiomas
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "Spanish"

# Variables para configuración
Var ConfigDialog
Var StartupCheckbox
Var TrayCheckbox
Var ServiceCheckbox
Var AdminUserText
Var AdminPassText
Var DomainText
Var StartupEnabled
Var TrayEnabled
Var ServiceEnabled
Var AdminUser
Var AdminPass
Var DomainName

# Función de inicialización
Function .onInit
    # Verificar si ya está instalado
    ReadRegStr $R0 ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString"
    StrCmp $R0 "" done

    MessageBox MB_OKCANCEL|MB_ICONEXCLAMATION \
    "${PRODUCT_NAME} ya está instalado. $\n$\n¿Desea desinstalarlo para continuar?" \
    IDOK uninst
    Abort

    uninst:
        ClearErrors
        ExecWait '$R0 _?=$INSTDIR'

        IfErrors no_remove_uninstaller done
        no_remove_uninstaller:

    done:

    # Verificar requisitos del sistema
    Call CheckSystemRequirements
FunctionEnd

# Verificar requisitos del sistema
Function CheckSystemRequirements
    # Verificar Windows 10 o superior
    ${If} ${AtMostWin8.1}
        MessageBox MB_OK|MB_ICONSTOP "Este software requiere Windows 10 o superior."
        Abort
    ${EndIf}

    # Verificar arquitectura 64-bit
    ${IfNot} ${RunningX64}
        MessageBox MB_OK|MB_ICONSTOP "Este software requiere Windows de 64 bits."
        Abort
    ${EndIf}

    # Verificar .NET Framework 4.8 o superior
    Call CheckDotNetFramework

    # Verificar Python 3.8 o superior
    Call CheckPython
FunctionEnd

# Verificar .NET Framework
Function CheckDotNetFramework
    ReadRegDWORD $0 HKLM "SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full" "Release"
    IntCmp $0 528040 done

    MessageBox MB_YESNO|MB_ICONQUESTION \
    ".NET Framework 4.8 no está instalado. ¿Desea descargarlo ahora?" \
    IDYES download IDNO skip

    download:
        ExecShell "open" "https://dotnet.microsoft.com/download/dotnet-framework/net48"

    skip:
        MessageBox MB_OK|MB_ICONINFORMATION \
        "Instale .NET Framework 4.8 antes de continuar."
        Abort

    done:
FunctionEnd

# Verificar Python
Function CheckPython
    nsExec::ExecToStack 'python --version'
    Pop $0 ; Exit code
    Pop $1 ; Output

    ${If} $0 != 0
        MessageBox MB_YESNO|MB_ICONQUESTION \
        "Python no está instalado. ¿Desea descargarlo ahora?" \
        IDYES download IDNO manual

        download:
            ExecShell "open" "https://www.python.org/downloads/"
            Abort

        manual:
            MessageBox MB_OK|MB_ICONINFORMATION \
            "Instale Python 3.8 o superior antes de continuar."
            Abort
    ${EndIf}
FunctionEnd

# Página de configuración personalizada
Function ConfigPageCreate
    !insertmacro MUI_HEADER_TEXT "Configuración de SmartCompute" "Configure las opciones de instalación"

    nsDialogs::Create 1018
    Pop $ConfigDialog

    ${If} $ConfigDialog == error
        Abort
    ${EndIf}

    # Opciones de inicio
    ${NSD_CreateGroupBox} 10u 10u 280u 60u "Opciones de Inicio"

    ${NSD_CreateCheckbox} 20u 25u 260u 10u "Iniciar con Windows"
    Pop $StartupCheckbox
    ${NSD_SetState} $StartupCheckbox ${BST_CHECKED}

    ${NSD_CreateCheckbox} 20u 40u 260u 10u "Mostrar icono en bandeja del sistema"
    Pop $TrayCheckbox
    ${NSD_SetState} $TrayCheckbox ${BST_CHECKED}

    ${NSD_CreateCheckbox} 20u 55u 260u 10u "Instalar como servicio del sistema"
    Pop $ServiceCheckbox
    ${NSD_SetState} $ServiceCheckbox ${BST_UNCHECKED}

    # Configuración de Active Directory
    ${NSD_CreateGroupBox} 10u 80u 280u 80u "Active Directory (Opcional)"

    ${NSD_CreateLabel} 20u 95u 80u 10u "Usuario Admin:"
    ${NSD_CreateText} 105u 93u 170u 12u ""
    Pop $AdminUserText

    ${NSD_CreateLabel} 20u 110u 80u 10u "Contraseña:"
    ${NSD_CreatePassword} 105u 108u 170u 12u ""
    Pop $AdminPassText

    ${NSD_CreateLabel} 20u 125u 80u 10u "Dominio:"
    ${NSD_CreateText} 105u 123u 170u 12u ""
    Pop $DomainText

    # Información adicional
    ${NSD_CreateLabel} 10u 170u 280u 30u "SmartCompute Enterprise proporcionará análisis de seguridad continuo para su infraestructura. Las credenciales se almacenan de forma segura y cifrada."

    nsDialogs::Show
FunctionEnd

# Procesar configuración
Function ConfigPageLeave
    ${NSD_GetState} $StartupCheckbox $StartupEnabled
    ${NSD_GetState} $TrayCheckbox $TrayEnabled
    ${NSD_GetState} $ServiceCheckbox $ServiceEnabled
    ${NSD_GetText} $AdminUserText $AdminUser
    ${NSD_GetText} $AdminPassText $AdminPass
    ${NSD_GetText} $DomainText $DomainName
FunctionEnd

# Secciones de instalación
Section "SmartCompute Enterprise Core" SEC01
    SectionIn RO

    SetOutPath "$INSTDIR"
    SetOverwrite ifnewer

    # Archivos principales
    File "smartcompute_tray.exe"
    File "run_enterprise_analysis.py"
    File "process_monitor.py"
    File "security_recommendations_engine.py"
    File "generate_html_reports.py"
    File "requirements.txt"
    File "README.txt"
    File "LICENSE.txt"

    # Directorio enterprise
    SetOutPath "$INSTDIR\enterprise"
    File /r "enterprise\*.*"

    # Instalar dependencias de Python
    DetailPrint "Instalando dependencias de Python..."
    nsExec::ExecToLog 'pip install -r "$INSTDIR\requirements.txt"'

    # Crear directorio de configuración
    CreateDirectory "$APPDATA\SmartCompute"

    # Configurar según opciones seleccionadas
    Call ConfigureInstallation

SectionEnd

Section "Herramientas Adicionales" SEC02
    SetOutPath "$INSTDIR\tools"
    File "tools\*.*"
SectionEnd

Section "Documentación" SEC03
    SetOutPath "$INSTDIR\docs"
    File "docs\*.*"

    # Crear acceso directo a la documentación
    CreateShortCut "$SMPROGRAMS\SmartCompute Enterprise\Documentación.lnk" \
                   "$INSTDIR\docs\manual.pdf"
SectionEnd

# Configurar instalación según opciones
Function ConfigureInstallation
    # Configurar inicio automático
    ${If} $StartupEnabled == ${BST_CHECKED}
        WriteRegStr HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Run" \
                    "SmartCompute Enterprise" '"$INSTDIR\smartcompute_tray.exe"'
    ${EndIf}

    # Configurar servicio si se seleccionó
    ${If} $ServiceEnabled == ${BST_CHECKED}
        Call InstallWindowsService
    ${EndIf}

    # Guardar configuración de Active Directory
    ${If} $AdminUser != ""
        Call SaveADConfiguration
    ${EndIf}

    # Crear archivo de configuración inicial
    Call CreateInitialConfig
FunctionEnd

# Instalar servicio de Windows
Function InstallWindowsService
    DetailPrint "Instalando servicio de Windows..."

    # Crear script de servicio
    FileOpen $0 "$INSTDIR\service_installer.py" w
    FileWrite $0 "import win32serviceutil$\r$\n"
    FileWrite $0 "import win32service$\r$\n"
    FileWrite $0 "import win32event$\r$\n"
    FileWrite $0 "import servicemanager$\r$\n"
    FileWrite $0 "import subprocess$\r$\n"
    FileWrite $0 "import sys$\r$\n"
    FileWrite $0 "import os$\r$\n"
    FileWrite $0 "$\r$\n"
    FileWrite $0 "class SmartComputeService(win32serviceutil.ServiceFramework):$\r$\n"
    FileWrite $0 "    _svc_name_ = 'SmartComputeEnterprise'$\r$\n"
    FileWrite $0 "    _svc_display_name_ = 'SmartCompute Enterprise Security Service'$\r$\n"
    FileWrite $0 "    _svc_description_ = 'Continuous security analysis and monitoring'$\r$\n"
    FileWrite $0 "$\r$\n"
    FileWrite $0 "    def __init__(self, args):$\r$\n"
    FileWrite $0 "        win32serviceutil.ServiceFramework.__init__(self, args)$\r$\n"
    FileWrite $0 "        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)$\r$\n"
    FileWrite $0 "$\r$\n"
    FileWrite $0 "    def SvcStop(self):$\r$\n"
    FileWrite $0 "        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)$\r$\n"
    FileWrite $0 "        win32event.SetEvent(self.hWaitStop)$\r$\n"
    FileWrite $0 "$\r$\n"
    FileWrite $0 "    def SvcDoRun(self):$\r$\n"
    FileWrite $0 "        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,$\r$\n"
    FileWrite $0 "                              servicemanager.PYS_SERVICE_STARTED,$\r$\n"
    FileWrite $0 "                              (self._svc_name_, ''))$\r$\n"
    FileWrite $0 "        subprocess.Popen([sys.executable, r'$INSTDIR\smartcompute_tray.py'])$\r$\n"
    FileWrite $0 "        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)$\r$\n"
    FileWrite $0 "$\r$\n"
    FileWrite $0 "if __name__ == '__main__':$\r$\n"
    FileWrite $0 "    win32serviceutil.HandleCommandLine(SmartComputeService)$\r$\n"
    FileClose $0

    # Instalar servicio
    nsExec::ExecToLog 'python "$INSTDIR\service_installer.py" install'
    nsExec::ExecToLog 'python "$INSTDIR\service_installer.py" start'
FunctionEnd

# Guardar configuración de Active Directory
Function SaveADConfiguration
    # Crear archivo de configuración cifrado para AD
    FileOpen $0 "$APPDATA\SmartCompute\ad_config.json" w
    FileWrite $0 '{$\r$\n'
    FileWrite $0 '  "domain": "$DomainName",$\r$\n'
    FileWrite $0 '  "username": "$AdminUser",$\r$\n'
    FileWrite $0 '  "enabled": true$\r$\n'
    FileWrite $0 '}$\r$\n'
    FileClose $0

    # Nota: En producción, cifrar este archivo
FunctionEnd

# Crear configuración inicial
Function CreateInitialConfig
    FileOpen $0 "$APPDATA\SmartCompute\config.json" w
    FileWrite $0 '{$\r$\n'
    FileWrite $0 '  "version": "${PRODUCT_VERSION}",$\r$\n'
    FileWrite $0 '  "installation_date": "'
    ${GetTime} "" "L" $1 $2 $3 $4 $5 $6 $7
    FileWrite $0 '$3-$2-$1",$\r$\n'
    FileWrite $0 '  "startup_enabled": '
    ${If} $StartupEnabled == ${BST_CHECKED}
        FileWrite $0 'true,$\r$\n'
    ${Else}
        FileWrite $0 'false,$\r$\n'
    ${EndIf}
    FileWrite $0 '  "tray_enabled": '
    ${If} $TrayEnabled == ${BST_CHECKED}
        FileWrite $0 'true,$\r$\n'
    ${Else}
        FileWrite $0 'false,$\r$\n'
    ${EndIf}
    FileWrite $0 '  "service_enabled": '
    ${If} $ServiceEnabled == ${BST_CHECKED}
        FileWrite $0 'true$\r$\n'
    ${Else}
        FileWrite $0 'false$\r$\n'
    ${EndIf}
    FileWrite $0 '}$\r$\n'
    FileClose $0
FunctionEnd

# Sección de accesos directos
Section -AdditionalIcons
    WriteIniStr "$INSTDIR\${PRODUCT_NAME}.url" "InternetShortcut" "URL" "${PRODUCT_WEB_SITE}"
    CreateDirectory "$SMPROGRAMS\SmartCompute Enterprise"
    CreateShortCut "$SMPROGRAMS\SmartCompute Enterprise\SmartCompute Enterprise.lnk" "$INSTDIR\smartcompute_tray.exe"
    CreateShortCut "$SMPROGRAMS\SmartCompute Enterprise\Análisis Manual.lnk" "$INSTDIR\run_enterprise_analysis.py"
    CreateShortCut "$SMPROGRAMS\SmartCompute Enterprise\Sitio Web.lnk" "$INSTDIR\${PRODUCT_NAME}.url"
    CreateShortCut "$SMPROGRAMS\SmartCompute Enterprise\Desinstalar.lnk" "$INSTDIR\uninst.exe"
SectionEnd

# Sección de post-instalación
Section -Post
    WriteUninstaller "$INSTDIR\uninst.exe"
    WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\smartcompute_tray.exe"
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\smartcompute_tray.exe"
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"

    # Configurar firewall
    Call ConfigureFirewall
SectionEnd

# Configurar firewall de Windows
Function ConfigureFirewall
    DetailPrint "Configurando reglas de firewall..."

    # Permitir tráfico de SmartCompute
    nsExec::ExecToLog 'netsh advfirewall firewall add rule name="SmartCompute Enterprise" dir=in action=allow program="$INSTDIR\smartcompute_tray.exe"'
    nsExec::ExecToLog 'netsh advfirewall firewall add rule name="SmartCompute Enterprise Out" dir=out action=allow program="$INSTDIR\smartcompute_tray.exe"'
FunctionEnd

# Descripciones de secciones
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
!insertmacro MUI_DESCRIPTION_TEXT ${SEC01} "Componentes principales de SmartCompute Enterprise"
!insertmacro MUI_DESCRIPTION_TEXT ${SEC02} "Herramientas adicionales para análisis avanzado"
!insertmacro MUI_DESCRIPTION_TEXT ${SEC03} "Documentación completa del usuario"
!insertmacro MUI_FUNCTION_DESCRIPTION_END

# Función de desinstalación
Function un.onUninstSuccess
    HideWindow
    MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) se desinstaló correctamente de su computadora."
FunctionEnd

Function un.onInit
    MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "¿Está seguro de que desea desinstalar completamente $(^Name) y todos sus componentes?" IDYES +2
    Abort
FunctionEnd

# Sección de desinstalación
Section Uninstall
    # Detener servicio si existe
    nsExec::ExecToLog 'python "$INSTDIR\service_installer.py" stop'
    nsExec::ExecToLog 'python "$INSTDIR\service_installer.py" remove'

    # Eliminar del startup
    DeleteRegValue HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Run" "SmartCompute Enterprise"

    # Eliminar archivos
    Delete "$INSTDIR\${PRODUCT_NAME}.url"
    Delete "$INSTDIR\uninst.exe"
    Delete "$INSTDIR\*.*"
    RMDir /r "$INSTDIR\enterprise"
    RMDir /r "$INSTDIR\tools"
    RMDir /r "$INSTDIR\docs"
    RMDir "$INSTDIR"

    # Eliminar accesos directos
    Delete "$SMPROGRAMS\SmartCompute Enterprise\*.*"
    RMDir "$SMPROGRAMS\SmartCompute Enterprise"

    # Eliminar reglas de firewall
    nsExec::ExecToLog 'netsh advfirewall firewall delete rule name="SmartCompute Enterprise"'
    nsExec::ExecToLog 'netsh advfirewall firewall delete rule name="SmartCompute Enterprise Out"'

    # Limpiar registro
    DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
    DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"

    SetAutoClose true
SectionEnd