param(
    [string]$CertDir = (Join-Path $PSScriptRoot 'certs')
)

$ErrorActionPreference = 'Stop'
$openssl = (Get-Command openssl.exe -ErrorAction Stop).Source
$caKey = Join-Path $CertDir 'local-dev-ca.key'
$caCert = Join-Path $CertDir 'local-dev-ca.crt'
$caSrl = Join-Path $CertDir 'local-dev-ca.srl'
$leafKey = Join-Path $CertDir 'localhost.key'
$leafCsr = Join-Path $CertDir 'localhost.csr'
$leafCert = Join-Path $CertDir 'localhost.crt'
$fullchain = Join-Path $CertDir 'localhost.fullchain.crt'
$caConfig = Join-Path $PSScriptRoot 'openssl-ca.cnf'
$leafConfig = Join-Path $PSScriptRoot 'openssl-localhost.cnf'

New-Item -ItemType Directory -Force -Path $CertDir | Out-Null

if (-not (Test-Path $caKey) -or -not (Test-Path $caCert)) {
    & $openssl req -x509 -nodes -newkey rsa:2048 -days 3650 -keyout $caKey -out $caCert -config $caConfig
}

if (-not (Test-Path $leafKey) -or -not (Test-Path $leafCert)) {
    & $openssl req -new -nodes -newkey rsa:2048 -keyout $leafKey -out $leafCsr -config $leafConfig
    & $openssl x509 -req -in $leafCsr -CA $caCert -CAkey $caKey -CAcreateserial -out $leafCert -days 825 -sha256 -extensions req_ext -extfile $leafConfig
}

(Get-Content $leafCert), (Get-Content $caCert) | Set-Content -LiteralPath $fullchain -Encoding Ascii

$cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2($caCert)
$rootStore = New-Object System.Security.Cryptography.X509Certificates.X509Store('Root', 'CurrentUser')
$rootStore.Open([System.Security.Cryptography.X509Certificates.OpenFlags]::ReadWrite)
try {
    $alreadyTrusted = $rootStore.Certificates | Where-Object { $_.Thumbprint -eq $cert.Thumbprint }
    if (-not $alreadyTrusted) {
        $rootStore.Add($cert)
    }
}
finally {
    $rootStore.Close()
}

Write-Output "Generated and trusted localhost certificate in $CertDir"
