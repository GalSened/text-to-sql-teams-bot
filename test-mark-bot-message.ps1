$BOT_MESSAGES_FILE = "$PSScriptRoot\state\sql_bot_messages.json"

function Mark-BotMessage {
    param([string]$MessageId)

    Write-Host "Reading bot messages file..." -ForegroundColor Gray
    $botMessages = Get-Content $BOT_MESSAGES_FILE -Raw | ConvertFrom-Json

    Write-Host "Adding message ID: $MessageId" -ForegroundColor Gray
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $botMessages | Add-Member -MemberType NoteProperty -Name $MessageId -Value $timestamp -Force

    Write-Host "Saving to file..." -ForegroundColor Gray
    $botMessages | ConvertTo-Json | Out-File $BOT_MESSAGES_FILE -Encoding utf8

    Write-Host "✅ Done" -ForegroundColor Green
}

Write-Host "Testing Mark-BotMessage function..." -ForegroundColor Cyan
Write-Host "Before:" -ForegroundColor Yellow
Get-Content $BOT_MESSAGES_FILE

Mark-BotMessage "test123"

Write-Host "`nAfter:" -ForegroundColor Yellow
Get-Content $BOT_MESSAGES_FILE
