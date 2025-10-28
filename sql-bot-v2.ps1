# SQL Bot for Teams - V2
# Responds to questions in "ask the DB" chat with actual query results

# Fix encoding for Hebrew
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['*:Encoding'] = 'utf8'

# ═══════════════════════════════════════════════════════════════
# PROCESS LOCKING
# ═══════════════════════════════════════════════════════════════
$LOCK_FILE = "$PSScriptRoot\state\sql_bot_v2.lock"
$LOCK_DIR = Split-Path $LOCK_FILE
if (!(Test-Path $LOCK_DIR)) {
    New-Item -ItemType Directory -Force -Path $LOCK_DIR | Out-Null
}

if (Test-Path $LOCK_FILE) {
    $lockPid = Get-Content $LOCK_FILE -ErrorAction SilentlyContinue
    if ($lockPid -and ($lockPid -match '^\d+$')) {
        $existingProcess = Get-Process -Id $lockPid -ErrorAction SilentlyContinue
        if ($existingProcess) {
            Write-Host "❌ SQL Bot V2 already running (PID: $lockPid)" -ForegroundColor Red
            Write-Host "To restart, run: .\restart-sql-bot-v2.ps1" -ForegroundColor Yellow
            exit 1
        } else {
            Remove-Item $LOCK_FILE -Force -ErrorAction SilentlyContinue
        }
    }
}

Set-Content $LOCK_FILE $PID -Force
Write-Host "✅ SQL Bot V2 lock acquired (PID: $PID)" -ForegroundColor Green

# Cleanup on exit
$null = Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action {
    $lockPath = "$PSScriptRoot\state\sql_bot_v2.lock"
    if (Test-Path $lockPath) {
        Remove-Item $lockPath -Force -ErrorAction SilentlyContinue
    }
}

# Import Graph API helpers
. "C:\Users\gals\teams-support-analyst\graph-api-helpers.ps1"

# Configuration
$POLL_INTERVAL = 5
$STATE_FILE = "$PSScriptRoot\state\sql_bot_v2_last_msg.txt"
$BOT_MESSAGES_FILE = "$PSScriptRoot\state\sql_bot_v2_sent.json"
$LOG_FILE = "$PSScriptRoot\state\sql_bot_v2.log"
$SQL_API_URL = "http://localhost:8000/query/ask"
$CHAT_ID = "19:9aa2d304ade8465baadcd9051e0a5cfc@thread.v2"  # "ask the DB"

# Database configuration
$DB_SERVER = "DEVTEST\SQLEXPRESS"
$DB_NAME = "WeSign"
$DB_USER = "sa"
$DB_PASSWORD = "Aa123456"

# Initialize state files
if (!(Test-Path $STATE_FILE)) {
    "0" | Out-File $STATE_FILE -Encoding utf8
}
if (!(Test-Path $BOT_MESSAGES_FILE)) {
    "{}" | Out-File $BOT_MESSAGES_FILE -Encoding utf8
}

# Logging function
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp | $Level | $Message" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    Write-Host "[$Level] $Message"
}

# Check if message was sent by bot
function Is-BotMessage {
    param([string]$MessageId)
    $botMessages = Get-Content $BOT_MESSAGES_FILE -Raw | ConvertFrom-Json
    return $botMessages.PSObject.Properties.Name -contains $MessageId
}

# Mark message as sent by bot
function Mark-BotMessage {
    param([string]$MessageId)
    $botMessages = Get-Content $BOT_MESSAGES_FILE -Raw | ConvertFrom-Json
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $botMessages | Add-Member -MemberType NoteProperty -Name $MessageId -Value $timestamp -Force
    $botMessages | ConvertTo-Json | Out-File $BOT_MESSAGES_FILE -Encoding utf8
}

# Execute SQL and return formatted results
function Execute-SQL {
    param([string]$Query)

    try {
        Write-Log "Executing SQL query..."

        # Create connection string
        $connString = "Server=$DB_SERVER;Database=$DB_NAME;User Id=$DB_USER;Password=$DB_PASSWORD;TrustServerCertificate=True;"

        # Create connection
        $connection = New-Object System.Data.SqlClient.SqlConnection
        $connection.ConnectionString = $connString
        $connection.Open()

        # Execute query
        $command = $connection.CreateCommand()
        $command.CommandText = $Query
        $command.CommandTimeout = 30

        $adapter = New-Object System.Data.SqlClient.SqlDataAdapter $command
        $dataset = New-Object System.Data.DataSet
        $adapter.Fill($dataset) | Out-Null

        $connection.Close()

        if ($dataset.Tables[0].Rows.Count -eq 0) {
            return "No results found."
        }

        # Format results
        $table = $dataset.Tables[0]
        $results = @()

        # If single value result (like COUNT)
        if ($table.Columns.Count -eq 1 -and $table.Rows.Count -eq 1) {
            $colName = $table.Columns[0].ColumnName
            $value = $table.Rows[0][$colName]
            return "**Result:** $value"
        }

        # Multiple rows - format as table
        $header = ($table.Columns | ForEach-Object { $_.ColumnName }) -join " | "
        $separator = ($table.Columns | ForEach-Object { "---" }) -join " | "
        $results += $header
        $results += $separator

        foreach ($row in $table.Rows) {
            $rowData = ($table.Columns | ForEach-Object { $row[$_.ColumnName] }) -join " | "
            $results += $rowData
        }

        $resultText = $results -join "`n"
        return "**Results:**`n``````$resultText``````"

    } catch {
        Write-Log "SQL execution error: $_" "ERROR"
        return "❌ Error executing query: $($_.Exception.Message)"
    }
}

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          🤖 SQL BOT V2 - TEAMS ORCHESTRATOR                    ║" -ForegroundColor Cyan
Write-Host "║                                                                ║" -ForegroundColor Cyan
Write-Host "║  Chat: ask the DB                                              ║" -ForegroundColor Cyan
Write-Host "║  Trigger: Messages ending with ?                               ║" -ForegroundColor Cyan
Write-Host "║  Response: Query results only (not SQL)                        ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

Write-Log "SQL Bot V2 starting..." "INFO"

# Main polling loop
while ($true) {
    try {
        # Get last processed message ID
        $lastMessageId = Get-Content $STATE_FILE -Raw
        $lastMessageId = $lastMessageId.Trim()
        if (!$lastMessageId -or $lastMessageId -eq "0") {
            $lastMessageId = "0"
        }

        # Fetch recent messages
        $messages = Get-TeamsChatMessages -ChatId $CHAT_ID -Top 5

        # Process new messages (oldest first)
        $newMessages = $messages | Where-Object {
            [int64]$_.id -gt [int64]$lastMessageId
        } | Sort-Object { [int64]$_.id }

        foreach ($msg in $newMessages) {
            $msgId = $msg.id
            $fromName = $msg.from.user.displayName
            $msgText = $msg.body.content

            # Skip bot's own messages
            if (Is-BotMessage $msgId) {
                Write-Log "Skipping bot message: $msgId" "DEBUG"
                Set-Content $STATE_FILE $msgId -Force
                continue
            }

            # Clean HTML tags
            $cleanMessage = $msgText -replace '<[^>]+>', ''
            $cleanMessage = $cleanMessage.Trim()

            if (!$cleanMessage) {
                Set-Content $STATE_FILE $msgId -Force
                continue
            }

            # Only process messages ending with ?
            if (!$cleanMessage.EndsWith("?")) {
                Write-Log "Skipping non-question: $cleanMessage" "DEBUG"
                Set-Content $STATE_FILE $msgId -Force
                continue
            }

            Write-Host ""
            Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Yellow
            Write-Host "📨 NEW QUESTION from $fromName" -ForegroundColor Cyan
            Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Yellow
            Write-Host "Question: $cleanMessage" -ForegroundColor White
            Write-Log "Processing question from $fromName`: $cleanMessage" "INFO"
            Write-Host ""

            # Add 👀 reaction
            Write-Host "👀 Adding reaction..." -ForegroundColor Cyan
            $reactionResult = Add-MessageReaction -ChatId $CHAT_ID -MessageId $msgId -ReactionType "👀"
            if ($reactionResult) {
                Write-Host "✅ Reaction added" -ForegroundColor Green
                Write-Log "Reaction added successfully" "INFO"
            } else {
                Write-Host "⚠️  Reaction failed" -ForegroundColor Yellow
                Write-Log "Reaction failed for message $msgId" "WARN"
            }

            # Call SQL API to generate query
            Write-Host "🔍 Calling SQL API to generate query..." -ForegroundColor Cyan
            try {
                $requestBody = @{
                    question = $cleanMessage
                } | ConvertTo-Json

                $apiResponse = Invoke-RestMethod -Uri $SQL_API_URL -Method Post -Body $requestBody -ContentType "application/json; charset=utf-8" -TimeoutSec 60

                $sql = $apiResponse.sql
                $method = $apiResponse.explanation

                Write-Host "✅ SQL generated" -ForegroundColor Green
                Write-Host "   Method: $method" -ForegroundColor Gray
                Write-Host "   SQL: $sql" -ForegroundColor Gray
                Write-Log "SQL generated: $sql" "INFO"

                # ═══════════════════════════════════════════════════════════
                # SECURITY CHECK: Block non-SELECT queries
                # ═══════════════════════════════════════════════════════════
                if ($sql -match '^\s*(UPDATE|DELETE|INSERT|DROP|CREATE|ALTER|TRUNCATE|EXEC|EXECUTE|MERGE|GRANT|REVOKE)') {
                    Write-Host "🚫 SECURITY BLOCK: Non-SELECT query blocked" -ForegroundColor Red
                    Write-Host "   SQL: $sql" -ForegroundColor Gray
                    Write-Log "SECURITY BLOCK: Non-SELECT query attempted: $sql" "WARN"

                    $securityMsg = @"
🚫 **Security Policy**

The bot only supports read queries (SELECT)
הבוט תומך רק בשאילתות קריאה (SELECT)

For data modifications, please contact your administrator.
"@

                    try {
                        $sentMessage = Send-TeamsChatMessage -ChatId $CHAT_ID -Message $securityMsg
                        if ($sentMessage -and $sentMessage.id) {
                            Mark-BotMessage $sentMessage.id
                            Write-Host "✅ Security message sent to user" -ForegroundColor Green
                            Write-Log "Security message sent: $($sentMessage.id)" "INFO"
                        }
                    } catch {
                        Write-Host "⚠️  Error sending security message: $_" -ForegroundColor Yellow
                        Write-Log "Error sending security message: $_" "ERROR"
                    }

                    Set-Content $STATE_FILE $msgId -Force
                    continue
                }

                # Execute SQL and get results
                Write-Host "⚡ Executing SQL..." -ForegroundColor Cyan
                $results = Execute-SQL -Query $sql

                Write-Host "✅ Query executed" -ForegroundColor Green
                Write-Log "Query executed successfully" "INFO"

                # Send ONLY results to Teams (not the SQL query)
                Write-Host "📤 Sending results to Teams..." -ForegroundColor Cyan
                try {
                    $sentMessage = Send-TeamsChatMessage -ChatId $CHAT_ID -Message $results

                    if ($sentMessage -and $sentMessage.id) {
                        Mark-BotMessage $sentMessage.id
                        Write-Host "✅ Results sent successfully" -ForegroundColor Green
                        Write-Log "Results sent: $($sentMessage.id)" "INFO"
                    } else {
                        Write-Host "⚠️  Failed to send results" -ForegroundColor Yellow
                        Write-Log "Failed to send results - no message ID" "WARN"
                    }
                } catch {
                    Write-Host "❌ Error sending to Teams: $_" -ForegroundColor Red
                    Write-Log "Error sending to Teams: $_" "ERROR"
                }

            } catch {
                Write-Host "❌ Error calling SQL API: $_" -ForegroundColor Red
                Write-Log "Error calling SQL API: $_" "ERROR"

                # Parse API error to check if it's a security block
                $errorMessage = $_.ToString()
                $errorResponse = ""

                # Check if it's the security block message
                if ($errorMessage -match "only supports read queries" -or $errorMessage -match "הבוט תומך רק בשאילתות קריאה") {
                    # Show the bilingual security message
                    $errorResponse = @"
🚫 **Security Policy**

The bot only supports read queries (SELECT)
הבוט תומך רק בשאילתות קריאה (SELECT)

For data modifications, please contact your administrator.
"@
                    Write-Host "🔒 Security block - sending bilingual message to user" -ForegroundColor Yellow
                } else {
                    # Generic error for other issues (table not found, etc.)
                    $errorResponse = "❌ Sorry, I encountered an error processing your query."
                }

                try {
                    $sentMessage = Send-TeamsChatMessage -ChatId $CHAT_ID -Message $errorResponse
                    if ($sentMessage -and $sentMessage.id) {
                        Mark-BotMessage $sentMessage.id
                        Write-Log "Error message sent: $($sentMessage.id)" "INFO"
                    }
                } catch {
                    Write-Log "Error sending error message: $_" "ERROR"
                }
            }

            # Update last processed message
            Set-Content $STATE_FILE $msgId -Force
        }

    } catch {
        Write-Log "Error in main loop: $_" "ERROR"
    }

    Start-Sleep -Seconds $POLL_INTERVAL
}
