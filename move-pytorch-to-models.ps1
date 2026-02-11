# Script to move existing PyTorch cache to C:\MODELS
# This helps keep the Docker environment clean and reuses model data across containers.

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$sourceDir = "$HOME\.cache\torch"
$destDir = "C:\MODELS\torch"

# Check if source exists
if (-not (Test-Path $sourceDir)) {
    Write-Host "ℹ️ No PyTorch cache found at $sourceDir" -ForegroundColor Yellow
    exit 0
}

# Ensure destination exists
if (-not (Test-Path "C:\MODELS")) {
    Write-Host "🚀 Creating C:\MODELS directory..." -ForegroundColor Cyan
    New-Item -ItemType Directory -Path "C:\MODELS" -Force | Out-Null
}

Write-Host "📦 Moving PyTorch cache from $sourceDir to $destDir..." -ForegroundColor Cyan

try {
    if (Test-Path $destDir) {
        Write-Host "⚠️ Destination $destDir already exists. Merging contents..." -ForegroundColor Yellow
        Copy-Item -Path "$sourceDir\*" -Destination $destDir -Recurse -Force
        Remove-Item -Path $sourceDir -Recurse -Force
    } else {
        Move-Item -Path $sourceDir -Destination $destDir -Force
    }
    Write-Host "✅ Successfully moved PyTorch cache." -ForegroundColor Green
    Write-Host "👉 Your models are now located in: $destDir" -ForegroundColor Gray
} catch {
    Write-Host "❌ Failed to move files: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

