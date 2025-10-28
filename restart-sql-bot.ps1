# Restart SQL Bot Orchestrator

Write-Host "🔄 Restarting SQL Bot..." -ForegroundColor Cyan
Write-Host ""

# Stop existing processes
Write-Host "🛑 Stopping existing SQL Bot processes..." -ForegroundColor Yellow

# Kill processes running sql-bot-orchestrator.ps1
Get-Process powershell -ErrorAction SilentlyContinue | ForEach-Object {
    $process = $_
    try {
        $cmdLine = (Get-CimInstance Win32_Process -Filter "ProcessId = $($process.Id)" -ErrorAction SilentlyContinue).CommandLine
        if ($cmdLine -and $cmdLine -like "*sql-bot-orchestrator*") {
            Write-Host "  Stopping PID: $($process.Id)" -ForegroundColor Gray
            Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        }
    } catch {
        # Silently skip
    }
}

# Remove lock file
$lockFile = "$PSScriptRoot\state\sql_orchestrator.lock"
if (Test-Path $lockFile) {
    Remove-Item $lockFile -Force
    Write-Host "✅ Lock file removed" -ForegroundColor Green
}

Write-Host ""
Write-Host "⏳ Waiting for cleanup..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

# Start fresh
Write-Host ""
& "$PSScriptRoot\start-sql-bot.ps1"
