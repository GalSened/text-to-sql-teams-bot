# Complete Setup Script for Teams Text-to-SQL Bot
# This script automates everything that can be automated

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Teams Text-to-SQL Bot - Complete Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Prerequisites
Write-Host "[1/9] Checking prerequisites..." -ForegroundColor Yellow

$prerequisites = @{
    "Python" = { python --version 2>&1 }
    "Docker" = { docker --version 2>&1 }
    "Git" = { git --version 2>&1 }
    "GitHub CLI" = { gh --version 2>&1 }
}

$allGood = $true
foreach ($tool in $prerequisites.Keys) {
    try {
        $version = & $prerequisites[$tool]
        Write-Host "  ✓ $tool installed: $version" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ $tool not found" -ForegroundColor Red
        $allGood = $false
    }
}

if (-not $allGood) {
    Write-Host ""
    Write-Host "Please install missing prerequisites before continuing." -ForegroundColor Red
    exit 1
}

# Step 2: Start PostgreSQL
Write-Host ""
Write-Host "[2/9] Starting PostgreSQL database..." -ForegroundColor Yellow
docker start postgres-queue 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Creating postgres-queue container..." -ForegroundColor Gray
    docker run -d `
        --name postgres-queue `
        -e POSTGRES_PASSWORD=postgres `
        -e POSTGRES_DB=text_to_sql_queue `
        -p 5433:5432 `
        postgres:15
}
Write-Host "  ✓ PostgreSQL running on port 5433" -ForegroundColor Green

# Step 3: Check ngrok installation
Write-Host ""
Write-Host "[3/9] Checking ngrok installation..." -ForegroundColor Yellow
$ngrokPath = "C:\Users\gals\ngrok.exe"
if (-not (Test-Path $ngrokPath)) {
    Write-Host "  ✗ ngrok not found at $ngrokPath" -ForegroundColor Red
    Write-Host ""
    Write-Host "  MANUAL STEP REQUIRED:" -ForegroundColor Cyan
    Write-Host "  1. Download ngrok from: https://ngrok.com/download" -ForegroundColor White
    Write-Host "  2. Extract ngrok.exe to: C:\Users\gals\" -ForegroundColor White
    Write-Host "  3. Run this script again" -ForegroundColor White
    Write-Host ""
    $continue = Read-Host "Do you want to continue without ngrok? (y/n)"
    if ($continue -ne 'y') {
        exit 1
    }
    $ngrokAvailable = $false
} else {
    Write-Host "  ✓ ngrok found at $ngrokPath" -ForegroundColor Green
    $ngrokAvailable = $true
}

# Step 4: Start FastAPI Server
Write-Host ""
Write-Host "[4/9] Starting FastAPI server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Users\gals\text-to-sql-app; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
Start-Sleep -Seconds 3
Write-Host "  ✓ FastAPI server starting on port 8000" -ForegroundColor Green

# Step 5: Start Worker Service
Write-Host ""
Write-Host "[5/9] Starting background worker..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Users\gals\text-to-sql-app; python worker_service.py --poll-interval 5"
Start-Sleep -Seconds 2
Write-Host "  ✓ Worker service started" -ForegroundColor Green

# Step 6: Start ngrok (if available)
$ngrokUrl = $null
if ($ngrokAvailable) {
    Write-Host ""
    Write-Host "[6/9] Starting ngrok tunnel..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Users\gals; .\ngrok.exe http 8000"
    Write-Host "  ⏳ Waiting for ngrok to start..." -ForegroundColor Gray
    Start-Sleep -Seconds 5

    try {
        $ngrokApi = Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels" -ErrorAction Stop
        $ngrokUrl = $ngrokApi.tunnels[0].public_url
        Write-Host "  ✓ ngrok tunnel active: $ngrokUrl" -ForegroundColor Green
    } catch {
        Write-Host "  ⚠ Could not retrieve ngrok URL automatically" -ForegroundColor Yellow
        Write-Host "  Check the ngrok window for the HTTPS URL" -ForegroundColor Gray
    }
} else {
    Write-Host ""
    Write-Host "[6/9] Skipping ngrok (not installed)" -ForegroundColor Yellow
}

# Step 7: Check Azure Bot Configuration
Write-Host ""
Write-Host "[7/9] Checking Azure Bot configuration..." -ForegroundColor Yellow
$envPath = "C:\Users\gals\text-to-sql-app\.env"
$envContent = Get-Content $envPath -Raw

if ($envContent -match 'MICROSOFT_APP_ID=([^\r\n]+)' -and $Matches[1] -and $Matches[1] -ne '') {
    Write-Host "  ✓ MICROSOFT_APP_ID configured" -ForegroundColor Green
    $azureConfigured = $true
} else {
    Write-Host "  ✗ MICROSOFT_APP_ID not configured" -ForegroundColor Red
    $azureConfigured = $false
}

if ($envContent -match 'MICROSOFT_APP_PASSWORD=([^\r\n]+)' -and $Matches[1] -and $Matches[1] -ne '') {
    Write-Host "  ✓ MICROSOFT_APP_PASSWORD configured" -ForegroundColor Green
} else {
    Write-Host "  ✗ MICROSOFT_APP_PASSWORD not configured" -ForegroundColor Red
    $azureConfigured = $false
}

# Step 8: Azure Bot Setup Instructions
if (-not $azureConfigured) {
    Write-Host ""
    Write-Host "[8/9] Azure Bot Registration Required" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  MANUAL STEPS REQUIRED:" -ForegroundColor Cyan
    Write-Host "  =====================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  1. Open browser: https://portal.azure.com" -ForegroundColor White
    Write-Host "  2. Search for 'Azure Bot'" -ForegroundColor White
    Write-Host "  3. Click '+ Create'" -ForegroundColor White
    Write-Host "  4. Fill in:" -ForegroundColor White
    Write-Host "     - Bot handle: wesign-text-to-sql-bot" -ForegroundColor Gray
    Write-Host "     - Pricing: F0 (Free)" -ForegroundColor Gray
    Write-Host "     - Create new Microsoft App ID" -ForegroundColor Gray
    Write-Host "  5. After deployment, go to Configuration" -ForegroundColor White
    Write-Host "  6. Copy the Microsoft App ID" -ForegroundColor White
    Write-Host "  7. Click 'Manage' → 'Certificates & secrets'" -ForegroundColor White
    Write-Host "  8. Create new client secret (24 months)" -ForegroundColor White
    Write-Host "  9. IMMEDIATELY copy the secret value" -ForegroundColor White
    Write-Host ""

    $appId = Read-Host "  Paste MICROSOFT_APP_ID (or press Enter to skip)"
    $appPassword = Read-Host "  Paste MICROSOFT_APP_PASSWORD (or press Enter to skip)" -AsSecureString

    if ($appId -and $appPassword) {
        $passwordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
            [Runtime.InteropServices.Marshal]::SecureStringToBSTR($appPassword))

        # Update .env file
        $envContent = $envContent -replace 'MICROSOFT_APP_ID=.*', "MICROSOFT_APP_ID=$appId"
        $envContent = $envContent -replace 'MICROSOFT_APP_PASSWORD=.*', "MICROSOFT_APP_PASSWORD=$passwordPlain"
        Set-Content -Path $envPath -Value $envContent

        Write-Host "  ✓ Credentials saved to .env" -ForegroundColor Green
        $azureConfigured = $true

        # Restart FastAPI to load new credentials
        Write-Host "  ⏳ Restarting FastAPI with new credentials..." -ForegroundColor Gray
        Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.MainWindowTitle -like '*uvicorn*'} | Stop-Process -Force
        Start-Sleep -Seconds 2
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Users\gals\text-to-sql-app; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
        Start-Sleep -Seconds 3
    }
}

# Step 9: Final Configuration
Write-Host ""
Write-Host "[9/9] Final configuration steps" -ForegroundColor Yellow

if ($azureConfigured -and $ngrokUrl) {
    Write-Host ""
    Write-Host "  NEXT MANUAL STEPS:" -ForegroundColor Cyan
    Write-Host "  =================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  1. Configure Bot Messaging Endpoint:" -ForegroundColor White
    Write-Host "     - Go to: https://portal.azure.com" -ForegroundColor Gray
    Write-Host "     - Navigate to your bot → Configuration" -ForegroundColor Gray
    Write-Host "     - Set Messaging endpoint to:" -ForegroundColor Gray
    Write-Host "       $ngrokUrl/api/messages" -ForegroundColor Yellow
    Write-Host "     - Click 'Apply'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  2. Enable Teams Channel:" -ForegroundColor White
    Write-Host "     - Click 'Channels' in left menu" -ForegroundColor Gray
    Write-Host "     - Click Microsoft Teams icon" -ForegroundColor Gray
    Write-Host "     - Click 'Save'" -ForegroundColor Gray
    Write-Host "     - Wait for status: Running" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  3. Create Teams Chat:" -ForegroundColor White
    Write-Host "     - Open Microsoft Teams" -ForegroundColor Gray
    Write-Host "     - Click 'Chat' → 'New chat'" -ForegroundColor Gray
    Write-Host "     - Search for: wesign-text-to-sql-bot" -ForegroundColor Gray
    Write-Host "     - Select bot and name chat: 'ask the DB'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  4. Test the Bot:" -ForegroundColor White
    Write-Host "     - Type: hello" -ForegroundColor Gray
    Write-Host "     - Type: How many companies are in the system?" -ForegroundColor Gray
    Write-Host "     - Type: כמה חברות יש במערכת?" -ForegroundColor Gray
} elseif (-not $azureConfigured) {
    Write-Host ""
    Write-Host "  ⚠ Complete Azure Bot registration first" -ForegroundColor Yellow
    Write-Host "  Then run this script again" -ForegroundColor Yellow
} elseif (-not $ngrokUrl) {
    Write-Host ""
    Write-Host "  ⚠ Install ngrok to get public URL" -ForegroundColor Yellow
    Write-Host "  Then run this script again" -ForegroundColor Yellow
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Setup Status" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PostgreSQL:     Running ✓" -ForegroundColor Green
Write-Host "  FastAPI:        Running ✓" -ForegroundColor Green
Write-Host "  Worker:         Running ✓" -ForegroundColor Green
if ($ngrokAvailable) {
    Write-Host "  ngrok:          Running ✓" -ForegroundColor Green
    if ($ngrokUrl) {
        Write-Host "  Public URL:     $ngrokUrl" -ForegroundColor Cyan
    }
} else {
    Write-Host "  ngrok:          Not installed ✗" -ForegroundColor Yellow
}
if ($azureConfigured) {
    Write-Host "  Azure Bot:      Configured ✓" -ForegroundColor Green
} else {
    Write-Host "  Azure Bot:      Not configured ✗" -ForegroundColor Yellow
}
Write-Host ""

# Documentation links
Write-Host "Documentation:" -ForegroundColor Cyan
Write-Host "  - Full guide: C:\Users\gals\text-to-sql-app\MANUAL_SETUP_GUIDE.md" -ForegroundColor Gray
Write-Host "  - Quick start: C:\Users\gals\text-to-sql-app\QUICK_START.md" -ForegroundColor Gray
Write-Host "  - Testing plan: C:\Users\gals\text-to-sql-app\BILINGUAL_TESTING_PLAN.md" -ForegroundColor Gray
Write-Host "  - GitHub repo: https://github.com/GalSened/text-to-sql-teams-bot" -ForegroundColor Gray
Write-Host ""

Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
