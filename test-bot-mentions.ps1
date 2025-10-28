# Test script - Send messages WITH @mentions to trigger bot
. "$PSScriptRoot\graph-api-helpers.ps1"

$CHAT_ID = "19:9aa2d304ade8465baadcd9051e0a5cfc@thread.v2"

Write-Host "=== Testing Bot with @Mentions ===" -ForegroundColor Cyan
Write-Host ""

# Get bot user info
$botUserId = Get-CurrentUserId
Write-Host "Bot User ID: $botUserId" -ForegroundColor Yellow

try {
    $token = Get-GraphToken
    $headers = @{
        "Authorization" = "Bearer $token"
        "Content-Type" = "application/json; charset=utf-8"
    }

    # Get bot display name
    $uri = "https://graph.microsoft.com/v1.0/me"
    $me = Invoke-RestMethod -Uri $uri -Method Get -Headers $headers
    $botName = $me.displayName
    Write-Host "Bot Name: $botName" -ForegroundColor Yellow
    Write-Host ""

    # Test 1: English message with @mention
    Write-Host "[TEST 1] Sending English message with @mention..." -ForegroundColor Cyan

    $englishMessage = @{
        body = @{
            contentType = "html"
            content = "<at id=`"0`">$botName</at> How many companies are in the system?"
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

    $bodyJson = $englishMessage | ConvertTo-Json -Depth 5
    $uri = "https://graph.microsoft.com/v1.0/chats/$CHAT_ID/messages"

    $response1 = Invoke-RestMethod -Uri $uri -Method Post -Headers $headers -Body ([System.Text.Encoding]::UTF8.GetBytes($bodyJson))
    Write-Host "  ✓ English message sent! Message ID: $($response1.id)" -ForegroundColor Green
    Write-Host "  Waiting 15 seconds for bot to process and respond..." -ForegroundColor Gray
    Start-Sleep -Seconds 15

    # Test 2: Hebrew message with @mention
    Write-Host ""
    Write-Host "[TEST 2] Sending Hebrew message with @mention..." -ForegroundColor Cyan

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

    $response2 = Invoke-RestMethod -Uri $uri -Method Post -Headers $headers -Body ([System.Text.Encoding]::UTF8.GetBytes($bodyJson))
    Write-Host "  ✓ Hebrew message sent! Message ID: $($response2.id)" -ForegroundColor Green
    Write-Host "  Waiting 15 seconds for bot to process and respond..." -ForegroundColor Gray
    Start-Sleep -Seconds 15

    # Check for bot responses
    Write-Host ""
    Write-Host "[VERIFICATION] Retrieving bot responses..." -ForegroundColor Cyan

    $messages = Get-TeamsChatMessages -ChatId $CHAT_ID -Top 10

    Write-Host ""
    Write-Host "Recent messages (newest first):" -ForegroundColor Yellow
    foreach ($msg in $messages) {
        $timestamp = $msg.createdDateTime
        $from = $msg.from.user.displayName
        $content = $msg.body.content -replace '<[^>]+>', '' -replace '\s+', ' '
        $content = $content.Substring(0, [Math]::Min(100, $content.Length))

        $color = if ($from -eq $botName) { "Green" } else { "White" }
        Write-Host "  [$timestamp] $from : $content" -ForegroundColor $color
    }

    Write-Host ""
    Write-Host "=== Testing Complete ===" -ForegroundColor Cyan
    Write-Host "Check the bot responses above to verify:" -ForegroundColor Yellow
    Write-Host "  1. Bot responded to both English and Hebrew messages" -ForegroundColor Gray
    Write-Host "  2. Each response is 1 sentence + SQL code block" -ForegroundColor Gray
    Write-Host "  3. No feedback loops occurred" -ForegroundColor Gray

} catch {
    Write-Host "ERROR: $_" -ForegroundColor Red
    Write-Host $_.ScriptStackTrace -ForegroundColor Red
}
