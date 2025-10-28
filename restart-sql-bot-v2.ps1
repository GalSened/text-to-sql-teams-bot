# Restart SQL Bot V2
# Stops the old instance and starts a new one

Write-Host "🔄 Restarting SQL Bot V2..." -ForegroundColor Cyan
Write-Host ""

# Stop old instance
$stopScript = Join-Path $PSScriptRoot "stop-sql-bot-v2.ps1"
if (Test-Path $stopScript) {
    & $stopScript
} else {
    Write-Host "⚠️  stop-sql-bot-v2.ps1 not found, attempting manual stop..." -ForegroundColor Yellow

    $lockFile = Join-Path $PSScriptRoot "state\sql_bot_v2.lock"
    if (Test-Path $lockFile) {
        $lockPid = Get-Content $lockFile -ErrorAction SilentlyContinue
        if ($lockPid -and ($lockPid -match '^\d+$')) {
            Stop-Process -Id $lockPid -Force -ErrorAction SilentlyContinue
        }
        Remove-Item $lockFile -Force -ErrorAction SilentlyContinue
    }
}

Write-Host ""
Start-Sleep -Seconds 2

# Start new instance
$startScript = Join-Path $PSScriptRoot "start-sql-bot-v2.ps1"
if (Test-Path $startScript) {
    & $startScript
} else {
    Write-Host "❌ Error: start-sql-bot-v2.ps1 not found" -ForegroundColor Red
    exit 1
}
