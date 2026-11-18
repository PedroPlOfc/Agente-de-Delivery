$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
docker compose down
if ($LASTEXITCODE -ne 0) {
    throw "Não foi possível parar os serviços."
}
Write-Host "Serviços parados. Os volumes e dados foram preservados." -ForegroundColor Green
