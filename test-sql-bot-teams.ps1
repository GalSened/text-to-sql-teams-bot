. "C:\Users\gals\teams-support-analyst\graph-api-helpers.ps1"

$CHAT_ID = "19:9aa2d304ade8465baadcd9051e0a5cfc@thread.v2"

Write-Host "📤 Sending test question to 'ask the DB' chat..." -ForegroundColor Cyan

$testQuestion = "כמה חברות יש במערכת?"

$message = @{
    body = @{
        contentType = 'text'
        content = $testQuestion
    }
}

$token = Get-GraphToken
$headers = @{
    'Authorization' = "Bearer $token"
    'Content-Type' = 'application/json; charset=utf-8'
}

$bodyJson = $message | ConvertTo-Json -Depth 5
$uri = "https://graph.microsoft.com/v1.0/chats/$CHAT_ID/messages"

$response = Invoke-RestMethod -Uri $uri -Method Post -Headers $headers -Body ([System.Text.Encoding]::UTF8.GetBytes($bodyJson))
$messageId = $response.id

Write-Host "✅ Test message sent!" -ForegroundColor Green
Write-Host "   Question: $testQuestion" -ForegroundColor White
Write-Host "   Message ID: $messageId" -ForegroundColor Gray
Write-Host ""
Write-Host "⏳ Waiting for SQL bot to respond..." -ForegroundColor Yellow
Write-Host "   Expected:" -ForegroundColor White
Write-Host "   1. 👀 reaction added" -ForegroundColor White
Write-Host "   2. SQL query generated" -ForegroundColor White
Write-Host "   3. Response with SQL sent to chat" -ForegroundColor White
Write-Host ""
Write-Host "Check the SQL Bot orchestrator window for activity!" -ForegroundColor Cyan
