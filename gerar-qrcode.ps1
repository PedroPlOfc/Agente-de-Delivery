$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

if (-not (Test-Path ".env")) {
    throw "Arquivo .env não encontrado. Execute .\iniciar-cana.ps1 primeiro."
}

# Lê as configurações sem imprimir chaves ou tokens no terminal.
$settings = @{}
Get-Content ".env" | ForEach-Object {
    $line = $_.Trim()
    if ($line -and -not $line.StartsWith("#") -and $line.Contains("=")) {
        $separator = $line.IndexOf("=")
        $key = $line.Substring(0, $separator).Trim()
        $value = $line.Substring($separator + 1).Trim().Trim('"').Trim("'")
        $settings[$key] = $value
    }
}

$baseUrl = $settings["EVOLUTION_LOCAL_API_URL"]
if ([string]::IsNullOrWhiteSpace($baseUrl)) { $baseUrl = "http://localhost:8080" }
$baseUrl = $baseUrl.TrimEnd("/")
$apiKey = $settings["EVOLUTION_API_KEY"]
$instance = $settings["EVOLUTION_INSTANCE"]
if ([string]::IsNullOrWhiteSpace($apiKey) -or [string]::IsNullOrWhiteSpace($instance)) {
    throw "Configure EVOLUTION_API_KEY e EVOLUTION_INSTANCE no arquivo .env."
}

$headers = @{ apikey = $apiKey }
$body = @{
    instanceName = $instance
    token = $apiKey
    qrcode = $true
    integration = "WHATSAPP-BAILEYS"
} | ConvertTo-Json -Depth 5

Write-Host "Verificando a instância $instance..." -ForegroundColor Cyan
try {
    Invoke-RestMethod -Method Post -Uri "$baseUrl/instance/create" -Headers $headers `
        -ContentType "application/json" -Body $body | Out-Null
} catch {
    # Se a instância já existir, a consulta de conexão abaixo ainda pode retornar o QR Code.
    Write-Host "A instância já pode existir; vou solicitar o QR Code." -ForegroundColor Yellow
}

Write-Host "Solicitando QR Code..." -ForegroundColor Cyan
$response = Invoke-RestMethod -Method Get -Uri "$baseUrl/instance/connect/$instance" -Headers $headers
$base64 = $response.base64
$qrText = $response.code
if ($response.qrcode) {
    if ([string]::IsNullOrWhiteSpace($base64)) { $base64 = $response.qrcode.base64 }
    if ([string]::IsNullOrWhiteSpace($qrText)) { $qrText = $response.qrcode.code }
}

if (-not [string]::IsNullOrWhiteSpace($base64)) {
    if (-not $base64.StartsWith("data:image")) { $base64 = "data:image/png;base64,$base64" }
    $qrMarkup = "<img src=`"$base64`" alt=`"QR Code de conexão do WhatsApp`">"
} elseif (-not [string]::IsNullOrWhiteSpace($qrText)) {
    $qrTextJson = ConvertTo-Json -InputObject ([string]$qrText) -Compress
    $qrMarkup = @"
<div id="qrcode"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
<script>new QRCode(document.getElementById("qrcode"), { text: $qrTextJson, width: 300, height: 300 });</script>
"@
} else {
    Write-Host "A Evolution API não retornou o QR Code. A instância talvez já esteja conectada." -ForegroundColor Yellow
    $response | ConvertTo-Json -Depth 8
    exit 0
}

$html = @"
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Conectar WhatsApp ao CANA</title>
  <style>
    body { min-height: 100vh; margin: 0; display: grid; place-items: center; background: #f1f5f9; font-family: Arial, sans-serif; color: #172554; }
    main { max-width: 420px; margin: 24px; padding: 28px; border-radius: 18px; background: white; text-align: center; box-shadow: 0 12px 40px #0f172a18; }
    img { width: min(300px, 80vw); height: auto; }
    p { line-height: 1.55; color: #475569; }
  </style>
</head>
<body>
  <main>
    <h1>Conecte o WhatsApp ao CANA</h1>
    $qrMarkup
    <p>No WhatsApp, abra <strong>Dispositivos conectados</strong> e escolha <strong>Conectar dispositivo</strong>.</p>
    <p>Depois do pareamento, execute <code>configurar-webhook.ps1</code> nesta pasta.</p>
  </main>
</body>
</html>
"@

$output = Join-Path $PSScriptRoot "qrcode_view.html"
Set-Content -Path $output -Value $html -Encoding UTF8
Start-Process $output
Write-Host "QR Code aberto no navegador. Faça o pareamento pelo WhatsApp." -ForegroundColor Green
