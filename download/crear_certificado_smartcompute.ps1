# Script para crear certificado digital SmartCompute
# Ejecutar como Administrador

$certSubject = "CN=SmartCompute Express, O=Martin Iribarne Technology, C=US"
$certStore = "Cert:\CurrentUser\My"

Write-Host "Creando certificado SmartCompute..." -ForegroundColor Green

# Crear certificado self-signed
$cert = New-SelfSignedCertificate -Subject $certSubject -Type CodeSigning -KeyUsage DigitalSignature -FriendlyName "SmartCompute Express Code Signing" -NotAfter (Get-Date).AddYears(3)

Write-Host "Certificado creado: $($cert.Thumbprint)" -ForegroundColor Yellow

# Exportar certificado para firma
$certPath = ".\SmartCompute_CodeSigning.pfx"
$certPassword = ConvertTo-SecureString "SmartCompute2024!" -AsPlainText -Force
Export-PfxCertificate -Cert $cert -FilePath $certPath -Password $certPassword

Write-Host "Certificado exportado a: $certPath" -ForegroundColor Green
Write-Host "Password: SmartCompute2024!" -ForegroundColor Red

# Instalar en Trusted Root (opcional para testing local)
$rootStore = Get-Item "Cert:\CurrentUser\Root"
$rootStore.Open("ReadWrite")
$rootStore.Add($cert)
$rootStore.Close()

Write-Host "Certificado instalado en Trusted Root" -ForegroundColor Green
Write-Host ""
Write-Host "Para firmar archivos .bat:"
Write-Host "signtool sign /f SmartCompute_CodeSigning.pfx /p SmartCompute2024! archivo.bat" -ForegroundColor Cyan