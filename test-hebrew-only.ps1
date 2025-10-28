# Test Hebrew message with @mention
. "$PSScriptRoot\graph-api-helpers.ps1"

$CHAT_ID = "19:9aa2d304ade8465baadcd9051e0a5cfc@thread.v2"

$botUserId = Get-CurrentUserId
$token = Get-GraphToken
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json; charset=utf-8"
}

# Get bot name
$uri = "https://graph.microsoft.com/v1.0/me"
$me = Invoke-RestMethod -Uri $uri -Method Get -Headers $headers
$botName = $me.displayName

Write-Host "Sending Hebrew test message with @mention..." -ForegroundColor Cyan

$hebrewMessage = @{
    body = @{
        contentType = "html"
        content = "<at id=`"0`">$botName</at> כמה חברות יש במערכת?"
    }
    mentions = @(
        @{
            id = 0
            mentionText = $botName
            mentioned = @{
                user = @{
                    id = $botUserId
                    displayName = $botName
                }
            }
        }
    )
}

$bodyJson = $hebrewMessage | ConvertTo-Json -Depth 5
$uri = "https://graph.microsoft.com/v1.0/chats/$CHAT_ID/messages"

$response = Invoke-RestMethod -Uri $uri -Method Post -Headers $headers -Body ([System.Text.Encoding]::UTF8.GetBytes($bodyJson))
Write-Host "✓ Message sent! ID: $($response.id)" -ForegroundColor Green
Write-Host "Waiting 20 seconds for bot response..." -ForegroundColor Gray
Start-Sleep -Seconds 20

# Check for response
$messages = Get-TeamsChatMessages -ChatId $CHAT_ID -Top 3
Write-Host ""
Write-Host "Latest messages:" -ForegroundColor Yellow
foreach ($msg in $messages) {
    $from = $msg.from.user.displayName
    $content = $msg.body.content -replace '<[^>]+>', '' -replace '\s+', ' '
    $content = $content.Substring(0, [Math]::Min(150, $content.Length))
    Write-Host "  [$from]: $content" -ForegroundColor $(if ($from -eq $botName) { "Green" } else { "White" })
}
