# ==============================================================================
# Text-to-SQL System - Complete Startup Script
# ==============================================================================
# This script starts all required services for the Teams bot
# Author: Auto-generated
# Date: 2025-10-26
# ==============================================================================

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  Starting Text-to-SQL System for Microsoft Teams" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[WARNING] Not running as Administrator. Some features may not work." -ForegroundColor Yellow
    Write-Host ""
}

# Change to application directory
$APP_DIR = "C:\Users\gals\text-to-sql-app"
Set-Location $APP_DIR
Write-Host "[INFO] Working directory: $APP_DIR" -ForegroundColor Green

# ==============================================================================
# STEP 1: Check Prerequisites
# ==============================================================================
Write-Host ""
Write-Host "STEP 1: Checking Prerequisites..." -ForegroundColor Yellow
Write-Host "-----------------------------------" -ForegroundColor Yellow

# Check Python
Write-Host "[CHECK] Python installation..." -NoNewline
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host " OK ($pythonVersion)" -ForegroundColor Green
} else {
    Write-Host " FAILED" -ForegroundColor Red
    Write-Host "[ERROR] Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Check Docker (for PostgreSQL)
Write-Host "[CHECK] Docker Desktop..." -NoNewline
$dockerStatus = docker ps 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host " OK" -ForegroundColor Green
} else {
    Write-Host " FAILED" -ForegroundColor Red
    Write-Host "[ERROR] Docker not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Check PostgreSQL container
Write-Host "[CHECK] PostgreSQL container..." -NoNewline
$postgresContainer = docker ps --filter "name=postgres-queue" --format "{{.Status}}"
if ($postgresContainer -match "Up") {
    Write-Host " OK ($postgresContainer)" -ForegroundColor Green
} else {
    Write-Host " NOT RUNNING" -ForegroundColor Red
    Write-Host "[INFO] Starting PostgreSQL container..." -ForegroundColor Yellow
    docker start postgres-queue
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[SUCCESS] PostgreSQL container started" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Failed to start PostgreSQL. Check Docker." -ForegroundColor Red
        exit 1
    }
}

# Check .env file
Write-Host "[CHECK] Configuration file (.env)..." -NoNewline
if (Test-Path ".env") {
    Write-Host " OK" -ForegroundColor Green

    # Check if Teams credentials are configured
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "MICROSOFT_APP_ID=\s*$" -or $envContent -notmatch "MICROSOFT_APP_ID=") {
        Write-Host "[WARNING] Teams credentials not configured in .env" -ForegroundColor Yellow
        Write-Host "          Please follow TEAMS_SETUP_GUIDE.md to configure bot" -ForegroundColor Yellow
        $teamsConfigured = $false
    } else {
        Write-Host "[INFO] Teams credentials found in .env" -ForegroundColor Green
        $teamsConfigured = $true
    }
} else {
    Write-Host " FAILED" -ForegroundColor Red
    Write-Host "[ERROR] .env file not found. Please create it first." -ForegroundColor Red
    exit 1
}

# Check ngrok (optional for Teams)
Write-Host "[CHECK] ngrok (for Teams tunnel)..." -NoNewline
$ngrokPath = $null
if (Test-Path "C:\Users\gals\ngrok.exe") {
    $ngrokPath = "C:\Users\gals\ngrok.exe"
    Write-Host " OK (found at $ngrokPath)" -ForegroundColor Green
} elseif (Get-Command ngrok -ErrorAction SilentlyContinue) {
    $ngrokPath = (Get-Command ngrok).Source
    Write-Host " OK (found in PATH)" -ForegroundColor Green
} else {
    Write-Host " NOT FOUND" -ForegroundColor Yellow
    Write-Host "[WARNING] ngrok not found. You'll need it for Teams integration." -ForegroundColor Yellow
    Write-Host "          Download from: https://ngrok.com/download" -ForegroundColor Yellow
}

# ==============================================================================
# STEP 2: Start FastAPI Server
# ==============================================================================
Write-Host ""
Write-Host "STEP 2: Starting FastAPI Server (port 8000)..." -ForegroundColor Yellow
Write-Host "------------------------------------------------" -ForegroundColor Yellow

# Kill any existing FastAPI processes
Write-Host "[INFO] Checking for existing FastAPI processes..." -ForegroundColor Cyan
$existingFastAPI = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match "uvicorn" }
if ($existingFastAPI) {
    Write-Host "[INFO] Stopping existing FastAPI processes..." -ForegroundColor Yellow
    $existingFastAPI | Stop-Process -Force
    Start-Sleep -Seconds 2
}

# Start FastAPI in new window
Write-Host "[INFO] Starting FastAPI server..." -ForegroundColor Cyan
$fastapiScript = @"
cd '$APP_DIR'
Write-Host 'FastAPI Server Starting...' -ForegroundColor Green
Write-Host 'Press Ctrl+C to stop' -ForegroundColor Yellow
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $fastapiScript -WindowStyle Normal

# Wait for FastAPI to start
Write-Host "[INFO] Waiting for FastAPI to initialize..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

# Check if FastAPI is responding
Write-Host "[CHECK] Testing FastAPI health endpoint..." -NoNewline
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 5
    if ($response.status -eq "healthy") {
        Write-Host " OK" -ForegroundColor Green
        Write-Host "[SUCCESS] FastAPI is running on http://localhost:8000" -ForegroundColor Green
    } else {
        Write-Host " UNHEALTHY" -ForegroundColor Yellow
    }
} catch {
    Write-Host " FAILED" -ForegroundColor Red
    Write-Host "[ERROR] FastAPI not responding. Check the server window for errors." -ForegroundColor Red
}

# ==============================================================================
# STEP 3: Start Worker Service
# ==============================================================================
Write-Host ""
Write-Host "STEP 3: Starting Background Worker Service..." -ForegroundColor Yellow
Write-Host "-----------------------------------------------" -ForegroundColor Yellow

# Kill any existing worker processes
Write-Host "[INFO] Checking for existing worker processes..." -ForegroundColor Cyan
$existingWorkers = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match "worker_service" }
if ($existingWorkers) {
    Write-Host "[INFO] Stopping existing worker processes..." -ForegroundColor Yellow
    $existingWorkers | Stop-Process -Force
    Start-Sleep -Seconds 2
}

# Start Worker in new window
Write-Host "[INFO] Starting worker service..." -ForegroundColor Cyan
$workerScript = @"
cd '$APP_DIR'
Write-Host 'Background Worker Service Starting...' -ForegroundColor Green
Write-Host 'Poll Interval: 5 seconds' -ForegroundColor Cyan
Write-Host 'Press Ctrl+C to stop' -ForegroundColor Yellow
Write-Host ''
python worker_service.py --fast
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $workerScript -WindowStyle Normal

Write-Host "[SUCCESS] Worker service started in separate window" -ForegroundColor Green

# ==============================================================================
# STEP 4: Start ngrok (Optional - for Teams)
# ==============================================================================
if ($ngrokPath -and $teamsConfigured) {
    Write-Host ""
    Write-Host "STEP 4: Starting ngrok Tunnel (for Teams)..." -ForegroundColor Yellow
    Write-Host "----------------------------------------------" -ForegroundColor Yellow

    # Kill existing ngrok
    $existingNgrok = Get-Process ngrok -ErrorAction SilentlyContinue
    if ($existingNgrok) {
        Write-Host "[INFO] Stopping existing ngrok..." -ForegroundColor Yellow
        $existingNgrok | Stop-Process -Force
        Start-Sleep -Seconds 2
    }

    Write-Host "[INFO] Starting ngrok tunnel..." -ForegroundColor Cyan
    $ngrokScript = @"
cd '$APP_DIR'
Write-Host 'ngrok Tunnel Starting...' -ForegroundColor Green
Write-Host 'This creates a public HTTPS URL for Teams to reach your bot' -ForegroundColor Cyan
Write-Host ''
Write-Host 'IMPORTANT: Copy the https:// URL and update it in:' -ForegroundColor Yellow
Write-Host '  1. Azure Bot Configuration (Messaging endpoint)' -ForegroundColor Yellow
Write-Host '  2. Add /api/messages to the end' -ForegroundColor Yellow
Write-Host ''
Write-Host 'Example: https://abc123.ngrok.io/api/messages' -ForegroundColor Cyan
Write-Host ''
& '$ngrokPath' http 8000 --log=stdout
"@

    Start-Process powershell -ArgumentList "-NoExit", "-Command", $ngrokScript -WindowStyle Normal
    Write-Host "[SUCCESS] ngrok started in separate window" -ForegroundColor Green
    Write-Host "[ACTION] Copy the ngrok URL and update Azure Bot messaging endpoint" -ForegroundColor Yellow

} elseif (-not $ngrokPath) {
    Write-Host ""
    Write-Host "STEP 4: ngrok Not Available" -ForegroundColor Yellow
    Write-Host "----------------------------" -ForegroundColor Yellow
    Write-Host "[INFO] ngrok not found. Teams integration requires a public endpoint." -ForegroundColor Cyan
    Write-Host "[INFO] Download ngrok from: https://ngrok.com/download" -ForegroundColor Cyan
    Write-Host "[INFO] Or use Azure deployment for production." -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "STEP 4: Teams Not Configured" -ForegroundColor Yellow
    Write-Host "-----------------------------" -ForegroundColor Yellow
    Write-Host "[INFO] Teams credentials not configured." -ForegroundColor Cyan
    Write-Host "[INFO] To enable Teams integration:" -ForegroundColor Cyan
    Write-Host "       1. Follow instructions in TEAMS_SETUP_GUIDE.md" -ForegroundColor Cyan
    Write-Host "       2. Add MICROSOFT_APP_ID and MICROSOFT_APP_PASSWORD to .env" -ForegroundColor Cyan
    Write-Host "       3. Re-run this script" -ForegroundColor Cyan
}

# ==============================================================================
# System Status Summary
# ==============================================================================
Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  System Status Summary" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Services Running:" -ForegroundColor Green
Write-Host "  FastAPI Server:       http://localhost:8000" -ForegroundColor White
Write-Host "  Health Check:         http://localhost:8000/health" -ForegroundColor White
Write-Host "  API Documentation:    http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Worker Service:       Background processing (5s poll)" -ForegroundColor White
Write-Host "  PostgreSQL Queue:     localhost:5433 (Docker)" -ForegroundColor White
Write-Host ""

Write-Host "Next Steps:" -ForegroundColor Yellow
if (-not $teamsConfigured) {
    Write-Host "  1. Configure Teams bot credentials (see TEAMS_SETUP_GUIDE.md)" -ForegroundColor White
    Write-Host "  2. Create 'ask the DB' chat in Microsoft Teams" -ForegroundColor White
    Write-Host "  3. Add bot to the chat" -ForegroundColor White
    Write-Host "  4. Test with: 'How many companies are in the system?'" -ForegroundColor White
} else {
    Write-Host "  1. Copy ngrok URL from ngrok window" -ForegroundColor White
    Write-Host "  2. Update Azure Bot messaging endpoint" -ForegroundColor White
    Write-Host "  3. Create 'ask the DB' chat in Microsoft Teams" -ForegroundColor White
    Write-Host "  4. Add bot to the chat" -ForegroundColor White
    Write-Host "  5. Test with: 'How many companies are in the system?'" -ForegroundColor White
}
Write-Host ""

Write-Host "Testing Options:" -ForegroundColor Yellow
Write-Host "  Local test (no Teams):  python test_bot_locally.py" -ForegroundColor White
Write-Host "  View testing plan:      cat BILINGUAL_TESTING_PLAN.md" -ForegroundColor White
Write-Host "  View logs:              Get-Content logs\orchestrator.log -Tail 50 -Wait" -ForegroundColor White
Write-Host ""

Write-Host "Documentation:" -ForegroundColor Yellow
Write-Host "  Teams Setup:     TEAMS_SETUP_GUIDE.md" -ForegroundColor White
Write-Host "  Testing Plan:    BILINGUAL_TESTING_PLAN.md" -ForegroundColor White
Write-Host "  Architecture:    See TEAMS_SETUP_GUIDE.md (Architecture Diagram)" -ForegroundColor White
Write-Host ""

Write-Host "To Stop All Services:" -ForegroundColor Red
Write-Host "  Run: .\stop-all-services.ps1" -ForegroundColor White
Write-Host "  Or close the PowerShell windows manually" -ForegroundColor White
Write-Host ""

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  All services started successfully!" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# Keep this window open
Write-Host "Press any key to close this status window..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
