$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

if (-not (Test-Path ".env")) {
    throw "Arquivo .env não encontrado. Execute iniciar-cana.ps1 primeiro."
}

# Carrega somente as variáveis necessárias do arquivo .env, sem exibir chaves na tela.
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

$apiKey = $settings["EVOLUTION_API_KEY"]
$instance = $settings["EVOLUTION_INSTANCE"]
$webhookToken = $settings["WEBHOOK_TOKEN"]
if ([string]::IsNullOrWhiteSpace($apiKey) -or [string]::IsNullOrWhiteSpace($instance)) {
    throw "Configure EVOLUTION_API_KEY e EVOLUTION_INSTANCE no arquivo .env."
}

$webhookUrl = "http://python-api:8000/webhook/whatsapp"
if (-not [string]::IsNullOrWhiteSpace($webhookToken)) {
    $webhookUrl += "?token=$([uri]::EscapeDataString($webhookToken))"
}

$body = @{
    enabled = $true
    url = $webhookUrl
    webhookByEvents = $false
    webhookBase64 = $false
    events = @("MESSAGES_UPSERT")
} | ConvertTo-Json -Depth 5

Invoke-RestMethod `
    -Method Post `
    -Uri "http://localhost:8080/webhook/set/$instance" `
    -Headers @{ apikey = $apiKey; "Content-Type" = "application/json" } `
    -Body $body | Out-Null

Write-Host "Webhook MESSAGES_UPSERT configurado para a instância $instance." -ForegroundColor Green
