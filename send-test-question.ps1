# Send a test question to "ask the DB" chat

. "C:\Users\gals\teams-support-analyst\graph-api-helpers.ps1"

$CHAT_ID = "19:9aa2d304ade8465baadcd9051e0a5cfc@thread.v2"

$testQuestion = "List all active companies?"

Write-Host "📤 Sending test question: $testQuestion" -ForegroundColor Cyan

$result = Send-TeamsChatMessage -ChatId $CHAT_ID -Message $testQuestion

if ($result -and $result.id) {
    Write-Host "✅ Test question sent successfully (ID: $($result.id))" -ForegroundColor Green
    Write-Host ""
    Write-Host "Now watch for:" -ForegroundColor Yellow
    Write-Host "  1. 👀 reaction added to your message" -ForegroundColor Gray
    Write-Host "  2. Bot response with query results" -ForegroundColor Gray
} else {
    Write-Host "❌ Failed to send test question" -ForegroundColor Red
}
