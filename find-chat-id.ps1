# Find Chat ID for "ask the DB" chat
. "$PSScriptRoot\graph-api-helpers.ps1"

Write-Host "Finding 'ask the DB' chat..." -ForegroundColor Cyan

try {
    $token = Get-GraphToken
    $headers = @{
        "Authorization" = "Bearer $token"
    }

    $uri = "https://graph.microsoft.com/v1.0/me/chats"
    $response = Invoke-RestMethod -Uri $uri -Method Get -Headers $headers

    foreach ($chat in $response.value) {
        if ($chat.topic -like "*ask the DB*") {
            Write-Host "`nFound chat!" -ForegroundColor Green
            Write-Host "Chat ID: $($chat.id)" -ForegroundColor Yellow
            Write-Host "Topic: $($chat.topic)" -ForegroundColor White

            # Save to file
            $chat.id | Set-Content "$PSScriptRoot\.chat-id.txt"
            Write-Host "`nSaved to .chat-id.txt" -ForegroundColor Green
            break
        }
    }
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}
