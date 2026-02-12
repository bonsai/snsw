# SNSW-AI Agent - Multi-Step Orchestrator
# This script automates cleanup, build, model loading, TTS, and Image generation.

# Use built-in $PSScriptRoot
Set-Location $PSScriptRoot

function Show-Header {
    Clear-Host
    Write-Host "=========================================================" -ForegroundColor Cyan
    Write-Host "   SNSW-AI AI Agent - Orchestrator (8 Patterns)" -ForegroundColor Cyan
    Write-Host "=========================================================" -ForegroundColor Cyan
}

function Cleanup-All {
    Write-Host ">>> [STEP 1] Deleting all Docker images and build cache..." -ForegroundColor Yellow
    docker system prune -a -f
    docker builder prune -a -f
    docker buildx prune -f --all
    Write-Host "OK: Cleanup complete." -ForegroundColor Green
}

function Build-Single-Image {
    Write-Host ">>> [STEP 2] Building single optimized image..." -ForegroundColor Yellow
    docker build -t snsw-ai-image -f Dockerfile.optimized .
    Write-Host "OK: Build complete (snsw-ai-image)." -ForegroundColor Green
}

function Load-Models {
    Write-Host ">>> [STEP 3] Preparing models (Download/Setup)..." -ForegroundColor Yellow
    docker run --rm `
        -v "${PSScriptRoot}:/app" `
        -v "C:\Models\TTS:/app/models/external" `
        -w /app `
        snsw-ai-image src/setup-common-env.py
    Write-Host "OK: Models ready." -ForegroundColor Green
}

function Run-Multi-TTS {
    Write-Host ">>> [STEP 4] Running tts-multi-selector.py..." -ForegroundColor Yellow
    if (!(Test-Path "tts_outputs")) { New-Item -ItemType Directory "tts_outputs" | Out-Null }
    docker run --rm `
        -v "${PSScriptRoot}:/app" `
        -v "C:\Models\TTS:/app/models/external" `
        -v "C:\Models\TTS\.cache:/root/.cache" `
        -v "C:\Models\TTS\.local:/root/.local" `
        -v "${PSScriptRoot}/tts_outputs:/app/tts_outputs" `
        -e "COQUI_TOS_AGREED=1" `
        -w /app `
        snsw-ai-image src/tts-multi-selector.py
    Write-Host "OK: TTS complete." -ForegroundColor Green
}

function Run-Image-Gen {
    Write-Host ">>> [STEP 5] Running image-generator.py (絵ジェント)..." -ForegroundColor Yellow
    if (!(Test-Path "image_outputs")) { New-Item -ItemType Directory "image_outputs" | Out-Null }
    docker run --rm `
        -v "${PSScriptRoot}:/app" `
        -v "C:\Models\TTS:/app/models/external" `
        -v "${PSScriptRoot}/image_outputs:/app/image_outputs" `
        -w /app `
        snsw-ai-image src/image-generator.py
    Write-Host "OK: Image generation complete." -ForegroundColor Green
}

function Run-Web-UI {
    Write-Host ">>> Starting WebView Manager (Flask + Single HTML)..." -ForegroundColor Cyan
    Write-Host "Access URL: http://localhost:7860" -ForegroundColor Green
    # Run locally with python (to access host docker) or via docker
    python src/webview-manager.py
}

function Run-Mail-Agent {
    Write-Host ">>> Starting Mail Order Agent (Background Processor)..." -ForegroundColor Cyan
    docker run --rm `
        -v "${PSScriptRoot}:/app" `
        -v "C:\Models\TTS:/app/models/external" `
        -w /app `
        snsw-ai-image src/mail-order-agent.py
}

# Main Loop
do {
    Show-Header
    Write-Host " [1] FULL FLOW: Clean -> Build -> Load -> TTS -> Image" -ForegroundColor Cyan
    Write-Host " [2] SKIP CLEAN: Build -> Load -> TTS -> Image" -ForegroundColor Cyan
    Write-Host " [3] SKIP BUILD: Load -> TTS -> Image" -ForegroundColor Cyan
    Write-Host " [4] RUN TTS ONLY: (Step 4 only)"
    Write-Host " [5] RUN IMAGE GEN ONLY: (Step 5 only)"
    Write-Host " ---------------------------------------------------------"
    Write-Host " [V] Launch WebView Manager (IDE Sidebar Style)" -ForegroundColor Green
    Write-Host " [M] Run Mail Order Agent (Processor)" -ForegroundColor Green
    Write-Host " [Q] Quit"
    Write-Host ""
    $choice = Read-Host "Select an option"

    switch ($choice.ToLower()) {
        "1" { Cleanup-All; Build-Single-Image; Load-Models; Run-Multi-TTS; Run-Image-Gen; Pause }
        "2" { Build-Single-Image; Load-Models; Run-Multi-TTS; Run-Image-Gen; Pause }
        "3" { Load-Models; Run-Multi-TTS; Run-Image-Gen; Pause }
        "4" { Run-Multi-TTS; Pause }
        "5" { Run-Image-Gen; Pause }
        "v" { Run-Web-UI; Pause }
        "m" { Run-Mail-Agent; Pause }
        "q" { break }
    }
} while ($true)
