# SNSW-AI Quick Run Script
# このスクリプトは、適切なディレクトリから docker-compose を実行します。

$PSScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $PSScriptRoot

Write-Host "[*] Starting SNSW-AI via docker-compose..." -ForegroundColor Cyan

# docker-compose.models.yml を使用して起動
docker-compose -f docker-compose.models.yml up -d

Write-Host "[+] Containers are starting. Use 'snsw-agent.ps1' for full automation." -ForegroundColor Green
