# Text-to-SQL Bot Orchestrator v3
# Architecture: Graph API + Claude Code CLI + FastAPI Backend
# - Calls Claude Code CLI directly from PowerShell (no API keys needed!)
# - FastAPI backend only executes SQL safely
# - Returns simple answers to Hebrew questions

# Import Graph API helpers
. "$PSScriptRoot\graph-api-helpers.ps1"

# Configuration
$CHAT_ID = "19:9aa2d304ade8465baadcd9051e0a5cfc@thread.v2"
$POLL_INTERVAL = 10  # seconds
$STATE_FILE = "$PSScriptRoot\.last-message-id.txt"
$API_BASE_URL = "http://localhost:8000"

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host " Text-to-SQL Bot v2 Starting" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Get bot's own user ID to skip self-messages
$botUserId = Get-CurrentUserId
Write-Host "Bot User ID: $botUserId" -ForegroundColor Yellow

# Load last processed message ID
if (Test-Path $STATE_FILE) {
    $lastMessageId = Get-Content $STATE_FILE
    Write-Host "Last processed message ID: $lastMessageId" -ForegroundColor Yellow
} else {
    $lastMessageId = ""
    Write-Host "No previous state found, starting fresh" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Polling for messages every $POLL_INTERVAL seconds..." -ForegroundColor Green
Write-Host "Chat: ask the DB" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""

# Main polling loop
while ($true) {
    try {
        # Get recent messages
        $messages = Get-TeamsChatMessages -ChatId $CHAT_ID -Top 5

        if ($null -eq $messages) {
            Write-Host "[$(Get-Date -Format 'HH:mm:ss')] No messages retrieved, sleeping..." -ForegroundColor Yellow
            Start-Sleep -Seconds $POLL_INTERVAL
            continue
        }

        # Process messages (newest first)
        $newMessagesProcessed = 0
        foreach ($msg in $messages) {
            # Skip if already processed
            if ($msg.id -eq $lastMessageId) {
                break  # We've reached the last processed message
            }

            # Skip system messages
            if ($msg.messageType -ne "message") {
                continue
            }

            # Get message content
            $messageText = $msg.body.content
            $userName = $msg.from.user.displayName

            # Skip if message is from the bot itself
            if ($msg.from.user.id -eq $botUserId) {
                continue
            }

            # Clean HTML tags from message
            $messageText = $messageText -replace '<[^>]*>', '' -replace '\s+', ' ' | ForEach-Object { $_.Trim() }

            # Only process messages ending with "?"
            if (-not $messageText.EndsWith('?')) {
                continue
            }

            Write-Host "[$(Get-Date -Format 'HH:mm:ss')] New message from $userName" -ForegroundColor Cyan
            Write-Host "  Question: $messageText" -ForegroundColor White

            # Send immediate "thinking" response
            Write-Host "  Sending 'thinking' message..." -ForegroundColor Gray
            Send-TeamsChatMessage -ChatId $CHAT_ID -Message "מעבד את השאלה..." -ReplyToId $msg.id

            # Step 1: Get database schema from FastAPI
            Write-Host "  Getting database schema..." -ForegroundColor Gray

            try {
                # Get schema from FastAPI
                $schema = Invoke-RestMethod -Uri "$API_BASE_URL/schema" -Method Get

                # Format schema for Claude
                $schemaText = ""
                foreach ($table in $schema.tables) {
                    $schemaText += "`nTable: $($table.name)`n"
                    $schemaText += "  Columns:`n"
                    foreach ($col in $table.columns) {
                        $pkMarker = if ($col.primary_key) { " (PK)" } else { "" }
                        $nullable = if ($col.nullable) { "NULL" } else { "NOT NULL" }
                        $schemaText += "    - $($col.name): $($col.type) $nullable$pkMarker`n"
                    }
                }

                # Step 2: Call Claude Code CLI to generate SQL
                Write-Host "  Calling Claude to generate SQL..." -ForegroundColor Gray

                $prompt = @"
Generate a T-SQL query for this question.

DATABASE SCHEMA:
$schemaText

QUESTION:
$messageText

Return ONLY a JSON object with these fields:
{
  "sql": "The T-SQL query",
  "explanation": "Brief explanation of what the query does"
}

IMPORTANT: Return ONLY the JSON, no markdown formatting or extra text.
"@

                # Call Claude Code CLI
                $claudeOutput = $prompt | claude --print

                # Remove markdown code blocks if present
                if ($claudeOutput -match '```json\s*(.*?)\s*```') {
                    $claudeOutput = $matches[1]
                } elseif ($claudeOutput -match '```\s*(.*?)\s*```') {
                    $claudeOutput = $matches[1]
                }

                # Parse JSON response from Claude
                $claudeResponse = $claudeOutput | ConvertFrom-Json

                Write-Host "  Generated SQL: $($claudeResponse.sql.Substring(0, [Math]::Min(80, $claudeResponse.sql.Length)))..." -ForegroundColor Gray

                # Step 3: Execute SQL via FastAPI
                Write-Host "  Executing SQL..." -ForegroundColor Gray

                $sqlRequest = @{
                    sql = $claudeResponse.sql
                    question = $messageText
                } | ConvertTo-Json -Depth 5

                $apiResponse = Invoke-RestMethod `
                    -Uri "$API_BASE_URL/query/execute-sql" `
                    -Method Post `
                    -ContentType "application/json; charset=utf-8" `
                    -Body ([System.Text.Encoding]::UTF8.GetBytes($sqlRequest))

                # Step 4: Format simple response
                if ($apiResponse.success) {
                    $response = $apiResponse.answer
                } else {
                    $response = "Error: $($apiResponse.error)"
                }

            } catch {
                Write-Host "  Error: $_" -ForegroundColor Red
                $response = "Sorry, I couldn't process that question. Error: $($_.Exception.Message)"
            }

            Write-Host "  Sending response..." -ForegroundColor Gray

            # Send response to Teams
            Send-TeamsChatMessage -ChatId $CHAT_ID -Message $response -ReplyToId $msg.id

            Write-Host "  ✓ Response sent!" -ForegroundColor Green
            Write-Host ""

            # Update last processed message ID
            $lastMessageId = $msg.id
            $lastMessageId | Set-Content $STATE_FILE
            $newMessagesProcessed++
        }

        if ($newMessagesProcessed -eq 0) {
            Write-Host "[$(Get-Date -Format 'HH:mm:ss')] No new messages" -ForegroundColor Gray
        }

    } catch {
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] ERROR: $_" -ForegroundColor Red
        Write-Host $_.ScriptStackTrace -ForegroundColor Red
    }

    # Sleep before next poll
    Start-Sleep -Seconds $POLL_INTERVAL
}
