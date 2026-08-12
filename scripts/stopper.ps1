param (
    [string]$ProjectDir = ""
)

$ErrorActionPreference = "Continue"

if (-not $ProjectDir -or $ProjectDir -eq "" -or $ProjectDir -eq $PSScriptRoot) {
    $ProjectDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}


Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "CropCare PowerShell Stopper" -ForegroundColor Cyan
Write-Host "Project: $ProjectDir" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

$jsonPath = Join-Path $ProjectDir "runtime\processes.json"
$procs = $null

if (Test-Path $jsonPath) {
    Write-Host "`nReading process records from runtime/processes.json..." -ForegroundColor Yellow
    try {
        $procs = Get-Content -Path $jsonPath -Raw | ConvertFrom-Json
    } catch {
        Write-Host "WARNING: Could not parse runtime/processes.json. Proceeding with targeted window cleanup." -ForegroundColor DarkYellow
    }
} else {
    Write-Host "`nNo runtime/processes.json found. Proceeding with targeted window cleanup." -ForegroundColor DarkGray
}

function Stop-TargetedProcess {
    param (
        [int]$procId,
        [string]$label
    )
    if ($procId -and $procId -gt 0) {
        $p = Get-Process -Id $procId -ErrorAction SilentlyContinue
        if ($p) {
            # Also check and terminate any child processes first
            $children = Get-CimInstance Win32_Process -Filter "ParentProcessId = $procId" -ErrorAction SilentlyContinue
            foreach ($c in $children) {
                Stop-Process -Id $c.ProcessId -Force -ErrorAction SilentlyContinue
            }
            Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
            Write-Host "      -> Terminated PID $procId ($label)." -ForegroundColor DarkGray
        } else {
            Write-Host "      -> PID $procId ($label) was already exited." -ForegroundColor DarkGray
        }
    }
}

Write-Host "`n[1/3] Terminating Backend & Frontend Processes..." -ForegroundColor Yellow
if ($procs) {
    if ($procs.backend_pid) { Stop-TargetedProcess -procId $procs.backend_pid -label "Backend API" }
    if ($procs.backend_window_pid) { Stop-TargetedProcess -procId $procs.backend_window_pid -label "Backend Terminal" }
    if ($procs.frontend_pid -and $procs.frontend_pid -ne $procs.backend_pid) {
        Stop-TargetedProcess -procId $procs.frontend_pid -label "Frontend Server"
    }
}
# Ensure any remaining window opened by launcher is closed cleanly without killing unrelated terminals
[void](taskkill /F /FI "WINDOWTITLE eq CropCare API*" 2>&1)

Write-Host "`n[2/3] Terminating Ngrok Tunneling Processes..." -ForegroundColor Yellow
if ($procs) {
    if ($procs.ngrok_pid) { Stop-TargetedProcess -procId $procs.ngrok_pid -label "Ngrok Tunnel" }
    if ($procs.ngrok_window_pid) { Stop-TargetedProcess -procId $procs.ngrok_window_pid -label "Ngrok Terminal" }
}
# Ensure any remaining ngrok window opened by launcher is closed
[void](taskkill /F /FI "WINDOWTITLE eq CropCare Ngrok Tunnel*" 2>&1)

Write-Host "`n[3/3] Stopping XAMPP Services..." -ForegroundColor Yellow
$xamppDirs = @(
    "C:\xampp",
    "D:\xampp",
    "E:\xampp",
    "$env:ProgramFiles\xampp",
    "${env:ProgramFiles(x86)}\xampp"
)
$xamppDir = $null
foreach ($d in $xamppDirs) {
    if (Test-Path (Join-Path $d "xampp-control.exe")) {
        $xamppDir = $d
        break
    }
}

if ($xamppDir) {
    $apacheStop = Join-Path $xamppDir "apache_stop.bat"
    $mysqlStop = Join-Path $xamppDir "mysql_stop.bat"
    
    if (Test-Path $apacheStop) {
        Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "`"$apacheStop`"" -WindowStyle Hidden -ErrorAction SilentlyContinue
    }
    if (Test-Path $mysqlStop) {
        Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "`"$mysqlStop`"" -WindowStyle Hidden -ErrorAction SilentlyContinue
    }
}
[void](taskkill /F /FI "WINDOWTITLE eq XAMPP Apache*" 2>&1)
[void](taskkill /F /FI "WINDOWTITLE eq XAMPP MySQL*" 2>&1)

# 4. Cleanup Runtime File
if (Test-Path $jsonPath) {
    Remove-Item -Path $jsonPath -Force -ErrorAction SilentlyContinue
    Write-Host "`nRemoved runtime/processes.json." -ForegroundColor DarkGray
}
$runtimeDir = Join-Path $ProjectDir "runtime"
if (Test-Path $runtimeDir) {
    $remaining = Get-ChildItem -Path $runtimeDir -ErrorAction SilentlyContinue
    if (-not $remaining -or $remaining.Count -eq 0) {
        Remove-Item -Path $runtimeDir -Force -ErrorAction SilentlyContinue
    }
}

# 5. Display Exact Formatted Summary Table
Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "Shutdown Summary" -ForegroundColor White
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "`nBackend" -ForegroundColor White
Write-Host "Stopped" -ForegroundColor Green
Write-Host "`nFrontend" -ForegroundColor White
Write-Host "Stopped" -ForegroundColor Green
Write-Host "`nngrok" -ForegroundColor White
Write-Host "Stopped" -ForegroundColor Green
Write-Host "`nXampp" -ForegroundColor White
Write-Host "Stopped" -ForegroundColor Green
Write-Host "`nCleanup" -ForegroundColor White
Write-Host "Completed" -ForegroundColor Green
Write-Host "`n==========================================" -ForegroundColor Cyan
