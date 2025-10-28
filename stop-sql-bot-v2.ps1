# Stop SQL Bot V2
# Cleanly stops the SQL bot orchestrator

$lockFile = Join-Path $PSScriptRoot "state\sql_bot_v2.lock"

if (!(Test-Path $lockFile)) {
    Write-Host "ℹ️  SQL Bot V2 is not running (no lock file found)" -ForegroundColor Cyan
    exit 0
}

$lockPid = Get-Content $lockFile -ErrorAction SilentlyContinue

if (!$lockPid -or !($lockPid -match '^\d+$')) {
    Write-Host "⚠️  Invalid lock file, cleaning up..." -ForegroundColor Yellow
    Remove-Item $lockFile -Force -ErrorAction SilentlyContinue
    exit 0
}

$process = Get-Process -Id $lockPid -ErrorAction SilentlyContinue

if (!$process) {
    Write-Host "ℹ️  SQL Bot V2 process (PID: $lockPid) not found, cleaning up lock file..." -ForegroundColor Cyan
    Remove-Item $lockFile -Force -ErrorAction SilentlyContinue
    exit 0
}

Write-Host "🛑 Stopping SQL Bot V2 (PID: $lockPid)..." -ForegroundColor Yellow

try {
    Stop-Process -Id $lockPid -Force -ErrorAction Stop
    Start-Sleep -Seconds 1

    # Clean up lock file
    if (Test-Path $lockFile) {
        Remove-Item $lockFile -Force -ErrorAction SilentlyContinue
    }

    Write-Host "✅ SQL Bot V2 stopped successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Error stopping SQL Bot V2: $_" -ForegroundColor Red
    exit 1
}
