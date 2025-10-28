# Restart Orchestrator with Clean Slate
# This stops all services and restarts with new configuration

Write-Host "Stopping all services..." -ForegroundColor Yellow

# Kill all Python processes (including FastAPI backend)
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

# Kill all PowerShell orchestrator processes
Get-Process powershell -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*orchestrator*"
} | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "✓ All services stopped" -ForegroundColor Green
Write-Host ""
Write-Host "Starting FastAPI backend..." -ForegroundColor Cyan

# Start FastAPI backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Users\gals\text-to-sql-app; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

Write-Host "Waiting 3 seconds for backend to start..." -ForegroundColor Gray
Start-Sleep -Seconds 3

Write-Host "Starting orchestrator..." -ForegroundColor Cyan

# Start orchestrator
Start-Process powershell -ArgumentList "-ExecutionPolicy", "Bypass", "-NoExit", "-File", "C:\Users\gals\text-to-sql-app\text-to-sql-orchestrator.ps1"

Write-Host ""
Write-Host "✓ All services started!" -ForegroundColor Green
Write-Host ""
Write-Host "Bot is ready to receive @mentions in Teams!" -ForegroundColor Cyan
