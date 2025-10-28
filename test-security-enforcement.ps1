# Test Security Enforcement - End to End

. "C:\Users\gals\teams-support-analyst\graph-api-helpers.ps1"

$CHAT_ID = "19:9aa2d304ade8465baadcd9051e0a5cfc@thread.v2"

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          🔒 SECURITY ENFORCEMENT TEST                          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Test 1: SELECT query (should work)
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "Test 1: SELECT query (should work)" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
$question1 = "How many companies are in the system?"
Write-Host "Sending: $question1" -ForegroundColor White
$result1 = Send-TeamsChatMessage -ChatId $CHAT_ID -Message $question1
Write-Host "✅ Sent (ID: $($result1.id))" -ForegroundColor Green
Write-Host ""
Start-Sleep -Seconds 8

# Test 2: DELETE query (should be blocked)
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Red
Write-Host "Test 2: DELETE query (should be blocked)" -ForegroundColor Red
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Red
$question2 = "Delete company with ID 123?"
Write-Host "Sending: $question2" -ForegroundColor White
$result2 = Send-TeamsChatMessage -ChatId $CHAT_ID -Message $question2
Write-Host "✅ Sent (ID: $($result2.id))" -ForegroundColor Green
Write-Host ""
Start-Sleep -Seconds 8

# Test 3: Hebrew SELECT query (should work)
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "Test 3: Hebrew SELECT query (should work)" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
$question3 = "כמה חברות יש במערכת?"
Write-Host "Sending: $question3" -ForegroundColor White
$result3 = Send-TeamsChatMessage -ChatId $CHAT_ID -Message $question3
Write-Host "✅ Sent (ID: $($result3.id))" -ForegroundColor Green
Write-Host ""

Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Waiting for responses..." -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Start-Sleep -Seconds 10

# Check responses
Write-Host ""
Write-Host "Checking responses..." -ForegroundColor Cyan
$messages = Get-TeamsChatMessages -ChatId $CHAT_ID -Top 10

Write-Host ""
Write-Host "Recent messages:" -ForegroundColor Yellow
$messages | Select-Object -First 6 | ForEach-Object {
    $from = $_.from.user.displayName
    $content = $_.body.content -replace '<[^>]+>', ''
    $content = $content.Trim().Substring(0, [Math]::Min(100, $content.Length))
    Write-Host "---"
    Write-Host "From: $from" -ForegroundColor Gray
    Write-Host "Content: $content" -ForegroundColor White
}

Write-Host ""
Write-Host "Check bot log for security blocks:" -ForegroundColor Cyan
Get-Content "C:\Users\gals\text-to-sql-app\state\sql_bot_v2.log" -Tail 20 | Select-String -Pattern "SECURITY|blocked|SELECT" -Context 0, 1
