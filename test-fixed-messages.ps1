# Test Fixed Error Messages

. "C:\Users\gals\teams-support-analyst\graph-api-helpers.ps1"

$CHAT_ID = "19:9aa2d304ade8465baadcd9051e0a5cfc@thread.v2"

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          🧪 TEST FIXED ERROR MESSAGES                          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Test 1: DELETE query (should show bilingual security message)
Write-Host "Test 1: DELETE query (should show bilingual security message)" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────────────" -ForegroundColor Gray
$question1 = "Delete all test data?"
Write-Host "Sending: $question1" -ForegroundColor White
$result1 = Send-TeamsChatMessage -ChatId $CHAT_ID -Message $question1
Write-Host "✅ Sent (ID: $($result1.id))" -ForegroundColor Green
Write-Host ""
Start-Sleep -Seconds 8

# Test 2: UPDATE query (should show bilingual security message)
Write-Host "Test 2: UPDATE query (should show bilingual security message)" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────────────" -ForegroundColor Gray
$question2 = "Update company status to inactive?"
Write-Host "Sending: $question2" -ForegroundColor White
$result2 = Send-TeamsChatMessage -ChatId $CHAT_ID -Message $question2
Write-Host "✅ Sent (ID: $($result2.id))" -ForegroundColor Green
Write-Host ""
Start-Sleep -Seconds 8

# Test 3: SELECT query (should work normally)
Write-Host "Test 3: SELECT query (should work normally)" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────────────" -ForegroundColor Gray
$question3 = "How many companies are there?"
Write-Host "Sending: $question3" -ForegroundColor White
$result3 = Send-TeamsChatMessage -ChatId $CHAT_ID -Message $question3
Write-Host "✅ Sent (ID: $($result3.id))" -ForegroundColor Green
Write-Host ""

Write-Host "Waiting for responses..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    RESULTS                                     ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check responses
$messages = Get-TeamsChatMessages -ChatId $CHAT_ID -Top 8

Write-Host "Recent messages:" -ForegroundColor Yellow
Write-Host ""

$messages | Select-Object -First 7 | ForEach-Object {
    $from = $_.from.user.displayName
    $content = $_.body.content -replace '<[^>]+>', ''
    $content = $content.Trim()

    Write-Host "───────────────────────────────────────────────────────────" -ForegroundColor Gray
    Write-Host "From: $from" -ForegroundColor Cyan

    if ($content.Length -gt 200) {
        Write-Host "Content:" -ForegroundColor White
        Write-Host $content.Substring(0, 200) -ForegroundColor White
        Write-Host "..." -ForegroundColor Gray
    } else {
        Write-Host "Content: $content" -ForegroundColor White
    }
    Write-Host ""
}

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    VERIFICATION                                ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check if bilingual message appears
$hasEnglishMessage = $messages | Where-Object { $_.body.content -match "only supports read queries" }
$hasHebrewMessage = $messages | Where-Object { $_.body.content -match "הבוט תומך רק בשאילתות קריאה" }

if ($hasEnglishMessage -and $hasHebrewMessage) {
    Write-Host "✅ PASS: Bilingual security message is showing correctly!" -ForegroundColor Green
    Write-Host "   - English message found: ✅" -ForegroundColor Green
    Write-Host "   - Hebrew message found: ✅" -ForegroundColor Green
} elseif ($hasEnglishMessage) {
    Write-Host "⚠️  PARTIAL: Only English message found" -ForegroundColor Yellow
} elseif ($hasHebrewMessage) {
    Write-Host "⚠️  PARTIAL: Only Hebrew message found" -ForegroundColor Yellow
} else {
    Write-Host "❌ FAIL: Bilingual security message not found" -ForegroundColor Red
    Write-Host "   Users are seeing generic error instead" -ForegroundColor Red
}

Write-Host ""
Write-Host "Check bot log:" -ForegroundColor Cyan
Get-Content "C:\Users\gals\text-to-sql-app\state\sql_bot_v2.log" -Tail 15 | Select-String -Pattern "Security block|bilingual" -Context 0, 1
