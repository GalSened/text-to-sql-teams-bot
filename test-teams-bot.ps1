# Test Teams Bot - Simulates Teams messages to test the bot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Testing Teams Text-to-SQL Bot" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if FastAPI is running
Write-Host "[1/5] Checking FastAPI server..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 5
    Write-Host "  ✓ FastAPI server is healthy" -ForegroundColor Green
} catch {
    Write-Host "  ✗ FastAPI server not responding" -ForegroundColor Red
    Write-Host "  Please run: .\start-all-services.ps1" -ForegroundColor Yellow
    exit 1
}

# Test 1: Welcome message
Write-Host ""
Write-Host "[2/5] Testing welcome message..." -ForegroundColor Yellow
$welcomePayload = @{
    type = "message"
    text = "hello"
    from = @{
        id = "test-user"
        name = "Test User"
    }
    conversation = @{
        id = "test-conversation"
    }
    serviceUrl = "https://test.local"
} | ConvertTo-Json -Depth 10

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/messages" -Method Post -Body $welcomePayload -ContentType "application/json" -TimeoutSec 10
    Write-Host "  ✓ Bot responded to hello" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ Error: $_" -ForegroundColor Red
}

# Test 2: English query
Write-Host ""
Write-Host "[3/5] Testing English query..." -ForegroundColor Yellow
$englishPayload = @{
    type = "message"
    text = "How many companies are in the system?"
    from = @{
        id = "test-user"
        name = "Test User"
    }
    conversation = @{
        id = "test-conversation"
    }
    serviceUrl = "https://test.local"
} | ConvertTo-Json -Depth 10

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/messages" -Method Post -Body $englishPayload -ContentType "application/json" -TimeoutSec 10
    Write-Host "  ✓ Bot processed English query" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ Error: $_" -ForegroundColor Red
}

Start-Sleep -Seconds 3

# Test 3: Hebrew query
Write-Host ""
Write-Host "[4/5] Testing Hebrew query..." -ForegroundColor Yellow
$hebrewPayload = @{
    type = "message"
    text = "כמה חברות יש במערכת?"
    from = @{
        id = "test-user"
        name = "Test User"
    }
    conversation = @{
        id = "test-conversation"
    }
    serviceUrl = "https://test.local"
} | ConvertTo-Json -Depth 10

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/messages" -Method Post -Body $hebrewPayload -ContentType "application/json" -TimeoutSec 10
    Write-Host "  ✓ Bot processed Hebrew query" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ Error: $_" -ForegroundColor Red
}

Start-Sleep -Seconds 3

# Test 4: Check queue results
Write-Host ""
Write-Host "[5/5] Checking queue results..." -ForegroundColor Yellow
docker exec postgres-queue psql -U postgres -d text_to_sql_queue -c "SELECT id, question, language, status FROM sql_queue ORDER BY created_at DESC LIMIT 3;" | Out-String | Write-Host

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Test Complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Check worker logs for processing details" -ForegroundColor White
Write-Host "2. Verify SQL generation was correct" -ForegroundColor White
Write-Host "3. For real Teams integration, complete Azure Bot setup" -ForegroundColor White
Write-Host ""
