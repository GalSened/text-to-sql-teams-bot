# Stop SQL Bot Orchestrator

Write-Host "🛑 Stopping SQL Bot..." -ForegroundColor Cyan
Write-Host ""

# Kill processes running sql-bot-orchestrator.ps1
$stopped = 0
Get-Process powershell -ErrorAction SilentlyContinue | ForEach-Object {
    $process = $_
    try {
        $cmdLine = (Get-CimInstance Win32_Process -Filter "ProcessId = $($process.Id)" -ErrorAction SilentlyContinue).CommandLine
        if ($cmdLine -and $cmdLine -like "*sql-bot-orchestrator*") {
            Write-Host "  Stopping PID: $($process.Id)" -ForegroundColor Yellow
            Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
            $stopped++
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

if ($stopped -gt 0) {
    Write-Host "✅ Stopped $stopped SQL Bot process(es)" -ForegroundColor Green
} else {
    Write-Host "ℹ️  No SQL Bot processes found" -ForegroundColor Gray
}
