$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Arquivo .env criado a partir de .env.example." -ForegroundColor Yellow
    Write-Host "Abra .env e configure suas chaves antes de usar IA ou WhatsApp." -ForegroundColor Yellow
}

docker compose up --build -d
if ($LASTEXITCODE -ne 0) {
    throw "Não foi possível iniciar o CANA. Confira se o Docker Desktop está aberto."
}

Write-Host "CANA iniciado. Simulador: http://localhost:8000" -ForegroundColor Green
Write-Host "Painel administrativo: http://localhost:8000/admin" -ForegroundColor Green
Write-Host "Acesso inicial: nicolas ou pedro.lucas | senha: 123 (troque antes de produção)." -ForegroundColor Yellow
Write-Host "Prontidão dos serviços: http://localhost:8000/ready"
