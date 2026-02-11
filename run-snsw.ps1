
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$targetDir =　.

if (-not (Test-Path $targetDir)) {
    Write-Host "❌ Directory not found: $targetDir" -ForegroundColor Red
    exit 1
}

Push-Location $targetDir

Write-Host " Starting Docker Compose..." -ForegroundColor Cyan
docker compose up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host " Launched successfully." -ForegroundColor Green
    docker compose ps
} else {
    Write-Host " Failed to launch. Please check if Docker is running." -ForegroundColor Red
}

Pop-Location

