# Test edge cases for SQL bot v2

. "C:\Users\gals\teams-support-analyst\graph-api-helpers.ps1"

$CHAT_ID = "19:9aa2d304ade8465baadcd9051e0a5cfc@thread.v2"

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Test 1: Message WITHOUT question mark (should be ignored)" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan

$nonQuestion = "This is just a statement about companies"
Write-Host "Sending: $nonQuestion" -ForegroundColor Gray
$result1 = Send-TeamsChatMessage -ChatId $CHAT_ID -Message $nonQuestion

if ($result1 -and $result1.id) {
    Write-Host "✅ Non-question sent (ID: $($result1.id))" -ForegroundColor Green
    Write-Host "   Bot should IGNORE this message" -ForegroundColor Gray
}

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Test 2: Hebrew question (should respond)" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan

$hebrewQuestion = "כמה משתמשים יש במערכת?"
Write-Host "Sending: $hebrewQuestion" -ForegroundColor Gray
$result2 = Send-TeamsChatMessage -ChatId $CHAT_ID -Message $hebrewQuestion

if ($result2 -and $result2.id) {
    Write-Host "✅ Hebrew question sent (ID: $($result2.id))" -ForegroundColor Green
    Write-Host "   Bot should respond with user count" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Waiting 10 seconds for bot to process..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "Checking log for bot activity..." -ForegroundColor Cyan
$log = Get-Content "C:\Users\gals\text-to-sql-app\state\sql_bot_v2.log" -Tail 15
$log | Select-String -Pattern "statement|משתמשים" -Context 1, 1
