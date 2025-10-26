# ==============================================================================
# Text-to-SQL System - Stop All Services Script
# ==============================================================================
# This script stops all running services safely
# Author: Auto-generated
# Date: 2025-10-26
# ==============================================================================

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  Stopping Text-to-SQL System Services" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

$APP_DIR = "C:\Users\gals\text-to-sql-app"

# ==============================================================================
# Stop FastAPI Server
# ==============================================================================
Write-Host "[INFO] Stopping FastAPI server..." -ForegroundColor Yellow
$fastapiProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match "uvicorn" }
if ($fastapiProcesses) {
    $fastapiProcesses | Stop-Process -Force
    Write-Host "[SUCCESS] FastAPI server stopped" -ForegroundColor Green
} else {
    Write-Host "[INFO] No FastAPI processes found" -ForegroundColor Cyan
}

# ==============================================================================
# Stop Worker Service
# ==============================================================================
Write-Host "[INFO] Stopping worker service..." -ForegroundColor Yellow
$workerProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match "worker_service" }
if ($workerProcesses) {
    $workerProcesses | Stop-Process -Force
    Write-Host "[SUCCESS] Worker service stopped" -ForegroundColor Green
} else {
    Write-Host "[INFO] No worker processes found" -ForegroundColor Cyan
}

# ==============================================================================
# Stop ngrok
# ==============================================================================
Write-Host "[INFO] Stopping ngrok..." -ForegroundColor Yellow
$ngrokProcesses = Get-Process ngrok -ErrorAction SilentlyContinue
if ($ngrokProcesses) {
    $ngrokProcesses | Stop-Process -Force
    Write-Host "[SUCCESS] ngrok stopped" -ForegroundColor Green
} else {
    Write-Host "[INFO] No ngrok processes found" -ForegroundColor Cyan
}

# ==============================================================================
# Optional: Stop PostgreSQL Container
# ==============================================================================
Write-Host ""
Write-Host "[QUESTION] Stop PostgreSQL container? (Keeps data)" -ForegroundColor Yellow
Write-Host "  (Y)es - Stop PostgreSQL" -ForegroundColor White
Write-Host "  (N)o  - Keep PostgreSQL running (recommended)" -ForegroundColor White
$response = Read-Host "Choice (Y/N)"

if ($response -eq "Y" -or $response -eq "y") {
    Write-Host "[INFO] Stopping PostgreSQL container..." -ForegroundColor Yellow
    docker stop postgres-queue
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[SUCCESS] PostgreSQL container stopped" -ForegroundColor Green
    } else {
        Write-Host "[WARNING] Failed to stop PostgreSQL" -ForegroundColor Red
    }
} else {
    Write-Host "[INFO] PostgreSQL container left running" -ForegroundColor Cyan
}

# ==============================================================================
# Summary
# ==============================================================================
Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  All services stopped successfully!" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "To restart services, run:" -ForegroundColor Yellow
Write-Host "  .\start-all-services.ps1" -ForegroundColor White
Write-Host ""

# Wait before closing
Start-Sleep -Seconds 3
