# Kill ALL background orchestrators

Write-Host "Stopping all PowerShell orchestrator processes..." -ForegroundColor Yellow

# Find and kill PowerShell processes running orchestrator scripts
Get-Process powershell -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*orchestrator*"
} | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "✓ All orchestrators stopped" -ForegroundColor Green
