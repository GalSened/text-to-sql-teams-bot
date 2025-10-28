# Start SQL Bot V2
# Launches the SQL bot orchestrator in a new window

$scriptPath = Join-Path $PSScriptRoot "sql-bot-v2.ps1"

if (!(Test-Path $scriptPath)) {
    Write-Host "❌ Error: sql-bot-v2.ps1 not found at $scriptPath" -ForegroundColor Red
    exit 1
}

# Check if already running
$lockFile = Join-Path $PSScriptRoot "state\sql_bot_v2.lock"
if (Test-Path $lockFile) {
    $lockPid = Get-Content $lockFile -ErrorAction SilentlyContinue
    if ($lockPid -and ($lockPid -match '^\d+$')) {
        $existingProcess = Get-Process -Id $lockPid -ErrorAction SilentlyContinue
        if ($existingProcess) {
            Write-Host "⚠️  SQL Bot V2 already running (PID: $lockPid)" -ForegroundColor Yellow
            Write-Host "To restart, use: .\restart-sql-bot-v2.ps1" -ForegroundColor Cyan
            exit 0
        }
    }
}

Write-Host "🚀 Starting SQL Bot V2..." -ForegroundColor Green

# Start in new PowerShell window
Start-Process powershell -ArgumentList "-ExecutionPolicy", "Bypass", "-NoExit", "-File", "`"$scriptPath`""

Start-Sleep -Seconds 2

# Verify it started
if (Test-Path $lockFile) {
    $botPid = Get-Content $lockFile -ErrorAction SilentlyContinue
    Write-Host "✅ SQL Bot V2 started successfully (PID: $botPid)" -ForegroundColor Green
} else {
    Write-Host "⚠️  SQL Bot V2 may not have started. Check the window for errors." -ForegroundColor Yellow
}
