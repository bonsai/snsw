# Find Large and Unnecessary Files on C:\ Drive - v2 (Interactive & Data-driven)
# Usage: .\find-large-files.ps1

$reportPath = Join-Path $PSScriptRoot "disk_usage_report.json"
$global:scanResults = @{}

function Show-Header {
    Clear-Host
    Write-Host "=========================================================" -ForegroundColor Cyan
    Write-Host "   Disk Space Manager v2 - Interactive Cleanup Tool" -ForegroundColor Cyan
    Write-Host "=========================================================" -ForegroundColor Cyan
    $drive = Get-PSDrive C
    $freeGB = [math]::Round($drive.Free / 1GB, 2)
    $usedGB = [math]::Round(($drive.Used + $drive.Free - $drive.Free) / 1GB, 2) # Simplified
    $totalGB = [math]::Round(($drive.Used + $drive.Free) / 1GB, 2)
    $color = "Green"
    if ($freeGB -lt 5) { $color = "Red" }
    Write-Host " C:\ Drive Status: $freeGB GB Free / $totalGB GB Total" -ForegroundColor $color
    Write-Host "---------------------------------------------------------"
}

function Run-Scan {
    Write-Host "[*] Scanning for large files and caches..." -ForegroundColor Yellow
    
    $cacheDirs = @(
        "$env:LOCALAPPDATA\Temp",
        "$env:TEMP",
        "$env:USERPROFILE\AppData\Local\pip\cache",
        "$env:USERPROFILE\.cache",
        "$env:USERPROFILE\.npm",
        "C:\Windows\Temp",
        "C:\Windows\SoftwareDistribution\Download"
    )

    $cacheResults = @()
    foreach ($dir in $cacheDirs) {
        if (Test-Path $dir) {
            try {
                $files = Get-ChildItem -Path $dir -Recurse -File -ErrorAction SilentlyContinue
                $size = ($files | Measure-Object -Property Length -Sum).Sum
                if ($size -gt 1MB) {
                    $cacheResults += @{
                        Path = $dir
                        SizeGB = [math]::Round($size / 1GB, 3)
                        Count = $files.Count
                        Type = "Cache/Temp"
                    }
                }
            } catch {}
        }
    }

    Write-Host "[*] Finding largest files (>500MB)..." -ForegroundColor Yellow
    $largeFiles = Get-ChildItem -Path "$env:USERPROFILE" -Recurse -File -ErrorAction SilentlyContinue |
                  Where-Object { $_.Length -gt 500MB } |
                  Select-Object @{N='Path';E={$_.FullName}}, @{N='SizeGB';E={[math]::Round($_.Length/1GB,3)}}, @{N='Type';E={"Large File"}}

    $global:scanResults = @{
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Caches = $cacheResults
        LargeFiles = $largeFiles
        Docker = (docker system df --format '{{.Type}}: {{.Size}}' 2>$null)
        DockerBuildCache = (docker builder du --filter "until=24h" 2>$null | Select-Object -Skip 1)
    }

    $global:scanResults | ConvertTo-Json -Depth 5 | Out-File $reportPath
    Write-Host "[+] Scan complete. Data saved to $reportPath" -ForegroundColor Green
    Pause
}

function Show-Plan {
    if (-not $global:scanResults.Timestamp) {
        Write-Host "[!] No scan data found. Please run Scan first." -ForegroundColor Red
        Pause
        return
    }

    Show-Header
    Write-Host "--- Proposed Deletion Plan ---" -ForegroundColor Yellow
    
    $totalPotential = 0
    Write-Host "`n[Safe to Delete (Caches)]" -ForegroundColor Green
    foreach ($item in $global:scanResults.Caches) {
        Write-Host "  - $($item.Path) ($($item.SizeGB) GB)"
        $totalPotential += $item.SizeGB
    }

    Write-Host "`n[Docker Build History (Large Items)]" -ForegroundColor Magenta
    if ($global:scanResults.DockerBuildCache) {
        $global:scanResults.DockerBuildCache | ForEach-Object {
            if ($_ -match "(\d+\.?\d*)\s*(GB|MB)") {
                $sizeStr = $matches[0]
                Write-Host "  - Build Cache Item: $sizeStr"
            }
        }
        Write-Host "  * Use 'docker builder prune' to reclaim space." -ForegroundColor Gray
    }

    Write-Host "`n[Review Required (Large Files)]" -ForegroundColor Cyan
    foreach ($item in $global:scanResults.LargeFiles) {
        Write-Host "  - $($item.Path) ($($item.SizeGB) GB)"
    }

    Write-Host "`nTotal potential space saving: $([math]::Round($totalPotential, 2)) GB" -ForegroundColor Yellow
    Write-Host "---------------------------------------------------------"
    Pause
}

function Execute-Cleanup {
    Write-Warning "This will delete temporary files and caches. Continue? (y/n)"
    $choice = Read-Host
    if ($choice -ne 'y') { return }

    foreach ($item in $global:scanResults.Caches) {
        Write-Host "Cleaning: $($item.Path)..." -ForegroundColor Gray
        Remove-Item -Path "$($item.Path)\*" -Recurse -Force -ErrorAction SilentlyContinue
    }
    
    Write-Host "[+] Basic cleanup finished." -ForegroundColor Green
    
    Write-Host "Clean Docker? (y/n)"
    if ((Read-Host) -eq 'y') {
        docker system prune -f
    }
    Pause
}

function Start-Monitoring {
    Write-Host "Press 'Ctrl+C' to stop monitoring." -ForegroundColor Cyan
    try {
        while ($true) {
            Show-Header
            Write-Host "Monitoring Active (Refreshing every 10s)..." -ForegroundColor Gray
            Start-Sleep -Seconds 10
        }
    } catch {
        Write-Host "`nMonitoring stopped."
    }
}

# Main Loop
do {
    Show-Header
    Write-Host " [1] Run System Scan (Generate Data)"
    Write-Host " [2] Show Analysis & Deletion Plan"
    Write-Host " [3] Execute Cleanup (Caches & Docker)"
    Write-Host " [4] Start Real-time Monitoring"
    Write-Host " [Q] Quit"
    Write-Host ""
    $input = Read-Host "Select an option"

    switch ($input) {
        "1" { Run-Scan }
        "2" { Show-Plan }
        "3" { Execute-Cleanup }
        "4" { Start-Monitoring }
    }
} while ($input -ne "q")
