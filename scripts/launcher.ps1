param (
    [string]$ProjectDir = ""
)

$ErrorActionPreference = "Continue"

if (-not $ProjectDir -or $ProjectDir -eq "" -or $ProjectDir -eq $PSScriptRoot) {
    $ProjectDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}


Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "CropCare PowerShell Launcher" -ForegroundColor Cyan
Write-Host "Project: $ProjectDir" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Ensure runtime folder exists
$runtimeDir = Join-Path $ProjectDir "runtime"
if (-not (Test-Path $runtimeDir)) {
    New-Item -ItemType Directory -Force -Path $runtimeDir | Out-Null
}

# 1. Database Initialization
Write-Host "`nUsing Cloud Neon PostgreSQL Database (configured via DATABASE_URL)." -ForegroundColor Green


# 2. Virtual Environment & Requirements
$venvPy = Join-Path $ProjectDir "venv\Scripts\python.exe"
$rebuildVenv = $false

if (-not (Test-Path $venvPy)) {
    $rebuildVenv = $true
} else {
    & $venvPy -c "import sys" 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        $rebuildVenv = $true
    }
}

if ($rebuildVenv) {
    Write-Host "`nRebuilding virtual environment..." -ForegroundColor Yellow
    $venvDir = Join-Path $ProjectDir "venv"
    if (Test-Path $venvDir) {
        Remove-Item -Recurse -Force $venvDir -ErrorAction SilentlyContinue
    }
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to create virtual environment." -ForegroundColor Red
        exit 1
    }
}

Write-Host "`nRefreshing Python dependencies..." -ForegroundColor Cyan
& $venvPy -m pip install -r (Join-Path $ProjectDir "requirements.txt") | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install requirements." -ForegroundColor Red
    exit 1
}

# 3. Launch Backend Server & Capture Exact PIDs
Write-Host "`nLaunching FastAPI/Uvicorn server..." -ForegroundColor Green
$backendCmd = "Set-Location '$ProjectDir'; .\venv\Scripts\Activate.ps1; python -m uvicorn backend.main:app --reload --port 8000"
$backendWindow = Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $backendCmd -PassThru -WindowStyle Normal

Write-Host "Performing health check for local server (waiting for port 8000)..." -ForegroundColor Yellow
$maxAttempts = 30
$attempt = 0
$serverReady = $false
$backendPid = $null

while ($attempt -lt $maxAttempts) {
    Start-Sleep -Milliseconds 500
    $attempt++
    
    $tcpConn = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($tcpConn) {
        $serverReady = $true
        $backendPid = $tcpConn.OwningProcess
        break
    }
}

if (-not $backendPid) {
    # Fallback to querying python processes with uvicorn in CommandLine via WMI/CIM
    $pyProcs = Get-CimInstance Win32_Process -Filter "Name = 'python.exe' OR Name = 'pythonw.exe'" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*uvicorn backend.main:app*" } | Select-Object -First 1
    if ($pyProcs) {
        $backendPid = $pyProcs.ProcessId
        $serverReady = $true
    }
}

if ($serverReady) {
    Write-Host "Local server booted successfully on port 8000 (Backend PID: $backendPid)." -ForegroundColor Green
} else {
    Write-Host "WARNING: Could not confirm port 8000 listening within timeout, but window PID is $($backendWindow.Id)." -ForegroundColor Yellow
}

$frontendPid = $backendPid # Unified server serves backend API and frontend templates on port 8000

# 4. Open Browser
Write-Host "Opening browser at http://127.0.0.1:8000 ..." -ForegroundColor Cyan
Start-Process "http://127.0.0.1:8000"

# 5. Intelligent Ngrok Discovery & Tunneling
Write-Host "`nDetecting Ngrok installation..." -ForegroundColor Cyan
$ngrokExe = $null

# Search Hierarchy:
# a. ./tools/ngrok.exe
$checkPath = Join-Path $ProjectDir "tools\ngrok.exe"
if (Test-Path $checkPath) {
    $ngrokExe = (Resolve-Path $checkPath).Path
}

# b. ./ngrok/ngrok.exe
if (-not $ngrokExe) {
    $checkPath = Join-Path $ProjectDir "ngrok\ngrok.exe"
    if (Test-Path $checkPath) {
        $ngrokExe = (Resolve-Path $checkPath).Path
    }
}

# c. System PATH via where / Get-Command
if (-not $ngrokExe) {
    $cmd = Get-Command ngrok.exe -ErrorAction SilentlyContinue
    if (-not $cmd) {
        $cmd = Get-Command ngrok -ErrorAction SilentlyContinue
    }
    if ($cmd -and (Test-Path $cmd.Source)) {
        $ngrokExe = (Resolve-Path $cmd.Source).Path
    }
}

# d. Common Windows install locations
if (-not $ngrokExe) {
    $commonPaths = @(
        "$env:ProgramFiles\ngrok\ngrok.exe",
        "${env:ProgramFiles(x86)}\ngrok\ngrok.exe",
        "C:\ngrok\ngrok.exe",
        "$env:USERPROFILE\Desktop\ngrok.exe",
        "$env:USERPROFILE\Downloads\ngrok.exe"
    )
    # Also check WinGet packages
    $wingetPaths = Get-ChildItem -Path "$env:USERPROFILE\AppData\Local\Microsoft\WinGet\Packages" -Filter "ngrok.exe" -Recurse -ErrorAction SilentlyContinue
    if ($wingetPaths) {
        $commonPaths += $wingetPaths | Select-Object -ExpandProperty FullName
    }
    
    foreach ($cp in $commonPaths) {
        if (Test-Path $cp) {
            $ngrokExe = (Resolve-Path $cp).Path
            break
        }
    }
}

$ngrokPid = $null
$ngrokWindowPid = $null

if (-not $ngrokExe -or -not (Test-Path $ngrokExe)) {
    Write-Host "`n==================================================" -ForegroundColor DarkYellow
    Write-Host "NGROK NOT FOUND" -ForegroundColor Yellow
    Write-Host "==================================================" -ForegroundColor DarkYellow
    Write-Host "Ngrok is not installed or not found in search paths."
    Write-Host "To enable public URL access for your local website,"
    Write-Host "please download Ngrok from: https://ngrok.com/download"
    Write-Host "`nContinuing with local-only access (http://127.0.0.1:8000)..." -ForegroundColor Cyan
    Write-Host "==================================================`n" -ForegroundColor DarkYellow
} else {
    Write-Host "Found Ngrok at: $ngrokExe" -ForegroundColor Green
    
    # Check Authentication
    $isAuthenticated = $false
    $ngrokConfigPath = Join-Path $env:USERPROFILE "AppData\Local\ngrok\ngrok.yml"
    if (Test-Path $ngrokConfigPath) {
        $configContent = Get-Content -Path $ngrokConfigPath -ErrorAction SilentlyContinue | Out-String
        if ($configContent -match "authtoken:") {
            $isAuthenticated = $true
        }
    }
    if (-not $isAuthenticated) {
        $checkOut = & "$ngrokExe" config check 2>&1 | Out-String
        if ($checkOut -match "authtoken" -or $checkOut -match "valid") {
            $isAuthenticated = $true
        }
    }
    
    if (-not $isAuthenticated) {
        Write-Host "`n==================================================" -ForegroundColor Red
        Write-Host "NGROK AUTHENTICATION REQUIRED" -ForegroundColor Yellow
        Write-Host "==================================================" -ForegroundColor Red
        Write-Host "Ngrok was detected at: $ngrokExe"
        Write-Host "However, your authtoken is not configured."
        Write-Host "`nPlease run:" -ForegroundColor Yellow
        Write-Host "    `"$ngrokExe`" config add-authtoken YOUR_TOKEN" -ForegroundColor White
        Write-Host "`nDo not attempt to start ngrok without authtoken."
        Write-Host "Continuing with local-only access (http://127.0.0.1:8000)..." -ForegroundColor Cyan
        Write-Host "==================================================`n" -ForegroundColor Red
    } else {
        Write-Host "Ngrok authtoken verified. Starting public tunnel..." -ForegroundColor Green
        $ngrokWindow = Start-Process -FilePath "cmd.exe" -ArgumentList "/k", "`"$ngrokExe`" http http://127.0.0.1:8000" -PassThru -WindowStyle Normal
        $ngrokWindowPid = $ngrokWindow.Id
        
        # Poll local Ngrok API at http://127.0.0.1:4040/api/tunnels
        Write-Host "Performing health check on Ngrok API (http://127.0.0.1:4040/api/tunnels)..." -ForegroundColor Yellow
        $tunnelAttempts = 20
        $tAttempt = 0
        $publicUrl = $null
        
        while ($tAttempt -lt $tunnelAttempts) {
            Start-Sleep -Milliseconds 500
            $tAttempt++
            
            # Check TCP port 4040 for ngrok child PID
            if (-not $ngrokPid) {
                $nTcp = Get-NetTCPConnection -LocalPort 4040 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
                if ($nTcp) { $ngrokPid = $nTcp.OwningProcess }
            }
            
            # Query tunnel URL
            try {
                $apiResp = Invoke-RestMethod -Uri "http://127.0.0.1:4040/api/tunnels" -ErrorAction Stop
                if ($apiResp.tunnels -and $apiResp.tunnels.Count -gt 0) {
                    $httpsTunnel = $apiResp.tunnels | Where-Object { $_.proto -eq "https" } | Select-Object -First 1
                    if ($httpsTunnel) {
                        $publicUrl = $httpsTunnel.public_url
                        break
                    } elseif ($apiResp.tunnels[0].public_url) {
                        $publicUrl = $apiResp.tunnels[0].public_url
                        break
                    }
                }
            } catch {
                # API not ready yet, continue looping
            }
        }
        
        if (-not $ngrokPid) {
            $nProcs = Get-Process -Name "ngrok" -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($nProcs) { $ngrokPid = $nProcs.Id }
        }
        
        if ($publicUrl) {
            Write-Host "`n==================================================" -ForegroundColor Green
            Write-Host "🚀 CropCare is Live Online via Ngrok!" -ForegroundColor White -BackgroundColor DarkGreen
            Write-Host "Public URL:  $publicUrl" -ForegroundColor Cyan
            Write-Host "Local URL:   http://127.0.0.1:8000" -ForegroundColor White
            Write-Host "==================================================`n" -ForegroundColor Green
        } else {
            Write-Host "WARNING: Ngrok tunnel started, but could not read public URL from local API." -ForegroundColor Yellow
        }
    }
}

# 6. Record Exact PIDs to runtime/processes.json
$processData = [ordered]@{
    backend_pid = if ($backendPid) { [int]$backendPid } else { $null }
    backend_window_pid = if ($backendWindow -and $backendWindow.Id) { [int]$backendWindow.Id } else { $null }
    frontend_pid = if ($frontendPid) { [int]$frontendPid } else { $null }
    ngrok_pid = if ($ngrokPid) { [int]$ngrokPid } else { $null }
    ngrok_window_pid = if ($ngrokWindowPid) { [int]$ngrokWindowPid } else { $null }
}

$jsonPath = Join-Path $runtimeDir "processes.json"
$processData | ConvertTo-Json -Depth 5 | Set-Content -Path $jsonPath -Force

Write-Host "Process PIDs recorded cleanly to runtime/processes.json." -ForegroundColor Green
Write-Host "CropCare launcher completed. To terminate services, run stop.bat." -ForegroundColor Cyan
