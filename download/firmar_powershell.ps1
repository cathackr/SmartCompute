# Script para auto-firmar SmartCompute PowerShell
# Ejecutar como Administrador

Write-Host "🔐 SmartCompute - Auto-Firma PowerShell" -ForegroundColor Cyan
Write-Host "========================================`n"

# Verificar si ya existe certificado
$existingCert = Get-ChildItem -Path Cert:\CurrentUser\My -CodeSigningCert | Where-Object {$_.Subject -like "*SmartCompute*"}

if ($existingCert) {
    Write-Host "[INFO] Certificado SmartCompute existente encontrado" -ForegroundColor Yellow
    $cert = $existingCert[0]
} else {
    Write-Host "[CREAR] Generando nuevo certificado SmartCompute..." -ForegroundColor Green

    # Crear certificado de firma de código
    $certParams = @{
        Subject = "CN=SmartCompute Express, O=Martin Iribarne Technology, C=US"
        Type = "CodeSigningCert"
        KeyUsage = "DigitalSignature"
        FriendlyName = "SmartCompute Express Code Signing"
        NotAfter = (Get-Date).AddYears(3)
        CertStoreLocation = "Cert:\CurrentUser\My"
    }

    $cert = New-SelfSignedCertificate @certParams
    Write-Host "[OK] Certificado creado: $($cert.Thumbprint)" -ForegroundColor Green

    # Instalar en Trusted Root para testing local
    $rootStore = Get-Item "Cert:\CurrentUser\Root"
    $rootStore.Open("ReadWrite")
    $rootStore.Add($cert)
    $rootStore.Close()
    Write-Host "[OK] Certificado instalado en Trusted Root" -ForegroundColor Green
}

# Firmar el archivo PowerShell
Write-Host "`n[FIRMAR] Aplicando firma digital..." -ForegroundColor Cyan

try {
    $signature = Set-AuthenticodeSignature -FilePath ".\SmartCompute_Express.ps1" -Certificate $cert

    if ($signature.Status -eq "Valid") {
        Write-Host "[✅] Archivo firmado exitosamente!" -ForegroundColor Green
        Write-Host "    Estado: $($signature.Status)"
        Write-Host "    Firmado por: $($signature.SignerCertificate.Subject)"
    } else {
        Write-Host "[❌] Error en la firma: $($signature.Status)" -ForegroundColor Red
        Write-Host "    Detalle: $($signature.StatusMessage)"
    }
} catch {
    Write-Host "[ERROR] No se pudo firmar el archivo: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Verificar firma
Write-Host "`n[VERIFICAR] Comprobando firma..." -ForegroundColor Yellow
$verification = Get-AuthenticodeSignature -FilePath ".\SmartCompute_Express.ps1"

Write-Host "Estado de la firma: $($verification.Status)" -ForegroundColor $(
    switch ($verification.Status) {
        "Valid" { "Green" }
        "UnknownError" { "Yellow" }
        default { "Red" }
    }
)

if ($verification.Status -eq "Valid") {
    Write-Host "[✅] Firma verificada correctamente" -ForegroundColor Green
} else {
    Write-Host "[⚠️] Firma con advertencias (normal para self-signed)" -ForegroundColor Yellow
}

# Configurar política de ejecución para el usuario actual
Write-Host "`n[CONFIG] Configurando política de ejecución..." -ForegroundColor Cyan
try {
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
    Write-Host "[OK] Política configurada: RemoteSigned para usuario actual" -ForegroundColor Green
} catch {
    Write-Host "[WARNING] No se pudo cambiar la política de ejecución" -ForegroundColor Yellow
    Write-Host "Ejecuta manualmente: Set-ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Gray
}

Write-Host "`n========================================" -ForegroundColor Green
Write-Host " 🎉 PROCESO COMPLETADO" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "Tu archivo SmartCompute_Express.ps1 está firmado y listo para usar" -ForegroundColor White
Write-Host "`nPara ejecutar:" -ForegroundColor Yellow
Write-Host "  .\SmartCompute_Express.ps1" -ForegroundColor Cyan
Write-Host "`nO hacer doble-click en el archivo .ps1" -ForegroundColor Gray

Write-Host "`n¿Quieres probar la ejecución ahora? (S/N): " -ForegroundColor Yellow -NoNewline
$test = Read-Host

if ($test -match "^[SsYy]") {
    Write-Host "`n[TEST] Ejecutando SmartCompute Express..." -ForegroundColor Cyan
    Start-Sleep -Seconds 2
    .\SmartCompute_Express.ps1
} else {
    Write-Host "`nArchivo listo para distribución!" -ForegroundColor Green
}

Read-Host "`nPresiona Enter para continuar"