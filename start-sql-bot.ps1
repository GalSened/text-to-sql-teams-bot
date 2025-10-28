# Start SQL Bot Orchestrator

Write-Host "🚀 Starting SQL Bot for Teams..." -ForegroundColor Cyan
Write-Host ""

# Check if SQL API is running
try {
    $apiCheck = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 5
    Write-Host "✅ SQL API is running" -ForegroundColor Green
} catch {
    Write-Host "⚠️  WARNING: SQL API is not responding at http://localhost:8000" -ForegroundColor Yellow
    Write-Host "   Start it with: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000" -ForegroundColor Yellow
    Write-Host ""
}

# Start orchestrator in new window
Write-Host "🤖 Starting SQL Bot orchestrator..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-ExecutionPolicy Bypass -NoExit -File `"$PSScriptRoot\sql-bot-orchestrator.ps1`""

Write-Host "✅ SQL Bot started in new window!" -ForegroundColor Green
Write-Host ""
Write-Host "The bot will:" -ForegroundColor White
Write-Host "  - Monitor the 'ask the DB' Teams chat" -ForegroundColor White
Write-Host "  - Add 👀 reaction to questions" -ForegroundColor White
Write-Host "  - Generate SQL and respond" -ForegroundColor White
