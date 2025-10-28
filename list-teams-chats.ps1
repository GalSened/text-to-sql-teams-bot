# List all Teams chats to find or create "ask the DB" chat
. "C:\Users\gals\teams-support-analyst\graph-api-helpers.ps1"

Write-Host "📋 Fetching Teams chats..." -ForegroundColor Cyan

$token = Get-GraphToken
$headers = @{
    'Authorization' = "Bearer $token"
    'Content-Type' = 'application/json'
}

$uri = 'https://graph.microsoft.com/v1.0/me/chats'
$chats = Invoke-RestMethod -Uri $uri -Method Get -Headers $headers

Write-Host ""
Write-Host "=== Available Teams Chats ===" -ForegroundColor Yellow
Write-Host ""

foreach ($chat in $chats.value) {
    $chatType = $chat.chatType
    $topic = if ($chat.topic) { $chat.topic } else { "(No topic)" }
    $id = $chat.id

    Write-Host "Chat ID: $id" -ForegroundColor Green
    Write-Host "  Type: $chatType"
    Write-Host "  Topic: $topic"
    Write-Host ""
}

Write-Host "Total chats: $($chats.value.Count)" -ForegroundColor Cyan
