# Docker Resource Manager v1
# Usage: .\docker-manager.ps1

function Show-Header {
    Clear-Host
    Write-Host "=========================================================" -ForegroundColor Cyan
    Write-Host "   Docker Resource Manager - Analyze & Cleanup" -ForegroundColor Cyan
    Write-Host "=========================================================" -ForegroundColor Cyan
}

function Get-DockerSummary {
    Show-Header
    Write-Host "[*] Gathering Docker System Information..." -ForegroundColor Yellow
    docker system df
    Write-Host "`n[Tips] RECLAIMABLEが高い項目は削除可能です。" -ForegroundColor Cyan
    Write-Host "---------------------------------------------------------"
}

function Show-DetailedUsage {
    Show-Header
    Write-Host "--- Detailed System Usage (docker system df -v) ---" -ForegroundColor Yellow
    docker system df -v
    Write-Host "`nPress Enter to return to Main Menu..."
    Read-Host
}

function Manage-Containers {
    Show-Header
    Write-Host "--- Container Management ---" -ForegroundColor Yellow
    docker ps -a --format 'table {{.ID}}\t{{.Names}}\t{{.Status}}\t{{.Image}}'
    
    Write-Host "`nOptions:"
    Write-Host " [1] Stop all running containers"
    Write-Host " [2] Remove all stopped containers (prune)"
    Write-Host " [B] Back to Main Menu"
    
    $choice = Read-Host "`nSelect an option"
    switch ($choice) {
        "1" { docker stop $(docker ps -q) }
        "2" { docker container prune -f }
    }
}

function Manage-Images {
    Show-Header
    Write-Host "--- Image Management ---" -ForegroundColor Yellow
    docker images --format 'table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.ID}}'
    
    $images = docker images --format '{{.Repository}}|{{.Tag}}|{{.Size}}|{{.ID}}'
    $usedImages = docker ps -a --format '{{.Image}}' | Sort-Object -Unique
    $totalSize = 0
    $suggestions = @()

    foreach ($line in $images) {
        $parts = $line.Split("|")
        $repo = $parts[0]
        $tag = $parts[1]
        $sizeStr = $parts[2]
        $id = $parts[3]

        $val = 0
        if ($sizeStr -match '(\d+\.?\d*)\s*GB') { $val = [double]$matches[1] }
        elseif ($sizeStr -match '(\d+\.?\d*)\s*MB') { $val = [double]$matches[1] / 1024 }
        
        $totalSize += $val

        # Check if used
        $isUsed = $false
        foreach ($u in $usedImages) {
            if ($u -eq $id -or $u -eq "${repo}:${tag}" -or $u -eq $repo) {
                $isUsed = $true
                break
            }
        }

        # Suggestion Logic:
        if ($repo -eq "<none>" -or $tag -eq "<none>") {
            $suggestions += [PSCustomObject]@{ ID = $id; Reason = "Dangling/Untagged"; Size = $sizeStr }
        }
        elseif (-not $isUsed) {
            $suggestions += [PSCustomObject]@{ ID = $id; Reason = "Not used by any container"; Size = $sizeStr }
        }
        elseif ($val -gt 20) {
            $suggestions += [PSCustomObject]@{ ID = $id; Reason = "Large image (>20GB) - consider optimizing"; Size = $sizeStr }
        }
    }
    
    Write-Host "`nTotal Image Space: $([math]::Round($totalSize, 2)) GB" -ForegroundColor Cyan

    if ($suggestions.Count -gt 0) {
        Write-Host "`n[!] Deletion Suggestions:" -ForegroundColor Red
        foreach ($s in $suggestions) {
            Write-Host "  - $($s.ID) ($($s.Size)): $($s.Reason)" -ForegroundColor Gray
        }
    }
    
    Write-Host "`nOptions:"
    Write-Host " [1] Remove dangling images (none)"
    Write-Host " [2] Remove ALL unused images (prune -a)"
    Write-Host " [3] Remove a specific image (ID/Name)"
    Write-Host " [4] Inspect image history (size per layer)"
    Write-Host " [B] Back to Main Menu"
    
    $choice = Read-Host "`nSelect an option"
    switch ($choice) {
        "1" { docker image prune -f }
        "2" { docker image prune -a -f }
        "3" { 
            $target = Read-Host "Enter Image ID or Name to remove"
            if ($target) { docker rmi $target }
        }
        "4" {
            $target = Read-Host "Enter Image ID or Name to inspect"
            if ($target) { docker history $target }
            Read-Host "`nPress Enter to continue..."
        }
    }
}

function Manage-BuildCache {
    Show-Header
    Write-Host "--- Build Cache & History Management ---" -ForegroundColor Yellow
    Write-Host "[*] Current Build Cache Usage:"
    docker builder du
    
    Write-Host "`nOptions:"
    Write-Host " [1] Remove all build cache (prune -a)"
    Write-Host " [2] Remove unused build cache only"
    Write-Host " [3] Clear Build History (buildx prune)"
    Write-Host " [B] Back to Main Menu"
    
    $choice = Read-Host "`nSelect an option"
    switch ($choice) {
        "1" { docker builder prune -f -a }
        "2" { docker builder prune -f }
        "3" { 
            Write-Host "[*] Clearing BuildKit build history..." -ForegroundColor Yellow
            docker buildx prune -f --all
            Write-Host "[+] Build history cleared." -ForegroundColor Green
            Pause
        }
    }
}

function Full-Cleanup {
    Show-Header
    Write-Host "!!! WARNING: Full System Prune !!!" -ForegroundColor Red
    Write-Host "This will remove:"
    Write-Host " - All stopped containers"
    Write-Host " - All networks not used by at least one container"
    Write-Host " - All dangling images"
    Write-Host " - All build cache"
    
    $confirm = Read-Host "`nAre you sure you want to proceed? (y/n)"
    if ($confirm -eq 'y') {
        Write-Host "[*] Executing system prune..." -ForegroundColor Yellow
        docker system prune -f
        docker builder prune -f
        Write-Host "[+] Cleanup complete." -ForegroundColor Green
        Pause
    }
}

function Manage-Volumes {
    Show-Header
    Write-Host "--- Volume Management ---" -ForegroundColor Yellow
    docker volume ls
    
    Write-Host "`nOptions:"
    Write-Host " [1] Remove all unused volumes (prune)"
    Write-Host " [B] Back to Main Menu"
    
    $choice = Read-Host "`nSelect an option"
    switch ($choice) {
        "1" { docker volume prune -f }
    }
}

# Main Loop
do {
    Get-DockerSummary
    Write-Host " [1] Manage Containers"
    Write-Host " [2] Manage Images"
    Write-Host " [3] Manage Volumes"
    Write-Host " [4] Manage Build Cache"
    Write-Host " [5] Show Detailed Usage (df -v)"
    Write-Host " [6] Execute FULL System Cleanup"
    Write-Host " [Q] Quit"
    Write-Host ""
    $input = Read-Host "Select an option"

    switch ($input) {
        "1" { Manage-Containers }
        "2" { Manage-Images }
        "3" { Manage-Volumes }
        "4" { Manage-BuildCache }
        "5" { Show-DetailedUsage }
        "6" { Full-Cleanup }
    }
} while ($input -ne "q")
