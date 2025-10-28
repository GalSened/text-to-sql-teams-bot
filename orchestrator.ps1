# Teams Text-to-SQL Bot - Orchestrator Script
#
# This script:
# 1. Polls Microsoft Teams for new messages in "ask the DB" chat (via Teams MCP)
# 2. Invokes Claude Code to process SQL queries
# 3. Sends results back to Teams (via Teams MCP)
#
# Requirements:
# - Claude Desktop with Teams MCP configured
# - claude CLI in PATH
# - PostgreSQL queue database running
# - Background worker running

# Configuration
$POLL_INTERVAL = 5  # seconds
$STATE_FILE = "./state/last_message_id.txt"
$LOG_FILE = "./logs/orchestrator.log"
$CHAT_NAME = if ($env:TEAMS_CHAT_NAME) { $env:TEAMS_CHAT_NAME } else { "ask the DB" }
$CLAUDE_CLI = "C:\Users\gals\AppData\Roaming\npm\claude.cmd"

# Initialize
Write-Host "=== Teams Text-to-SQL Bot - Orchestrator Starting ===" -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path (Split-Path $STATE_FILE) | Out-Null
New-Item -ItemType Directory -Force -Path (Split-Path $LOG_FILE) | Out-Null

# Logging function
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"

    switch ($Level) {
        "ERROR" { Write-Host $logEntry -ForegroundColor Red }
        "SUCCESS" { Write-Host $logEntry -ForegroundColor Green }
        "WARN" { Write-Host $logEntry -ForegroundColor Yellow }
        default { Write-Host $logEntry }
    }

    Add-Content -Path $LOG_FILE -Value $logEntry
}

# Check dependencies
if (Test-Path $CLAUDE_CLI) {
    Write-Log "Claude CLI found at $CLAUDE_CLI" "SUCCESS"
} else {
    Write-Log "claude CLI not found at $CLAUDE_CLI. Please install Claude Desktop." "ERROR"
    exit 1
}

# Check worker is running
$workerRunning = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*worker_service.py*" }
if (-not $workerRunning) {
    Write-Log "Background worker not detected. Starting it now..." "WARN"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Users\gals\text-to-sql-app; python worker_service.py --poll-interval 2"
    Start-Sleep -Seconds 3
}

# Function to get last processed message ID
function Get-LastMessageId {
    if (Test-Path $STATE_FILE) {
        return Get-Content $STATE_FILE
    }
    return ""
}

# Function to save last processed message ID
function Save-LastMessageId {
    param([string]$MessageId)
    Set-Content -Path $STATE_FILE -Value $MessageId
}

# Function to detect language
function Detect-Language {
    param([string]$Text)

    if ($Text -match '[\u0590-\u05FF]') {
        return "he"
    }
    return "en"
}

# Function to process query with Claude Code
function Invoke-SqlQuery {
    param([string]$MessageText, [string]$Language)

    $prompt = @"
You are a text-to-SQL assistant for the WeSign database.

User question ($Language): $MessageText

Your task:
1. Detect if this is a database query or a command (help, status, examples)
2. If it's a query:
   - Insert it into the PostgreSQL queue database
   - Wait for the worker to process it
   - Retrieve and format the results
3. If it's a command:
   - Respond appropriately

Database connection string: postgresql://postgres:postgres@localhost:5433/text_to_sql_queue

Use these tools:
- Bash tool to run psql commands
- Read tool to check worker logs if needed

Return your response in a user-friendly format suitable for Teams chat.
"@

    Write-Log "Invoking Claude Code for query: $MessageText"

    # Save prompt to temp file
    $promptFile = [System.IO.Path]::GetTempFileName()
    Set-Content -Path $promptFile -Value $prompt

    try {
        # Invoke Claude Code CLI
        $response = & "$CLAUDE_CLI" -p $promptFile 2>&1 | Out-String
        Remove-Item $promptFile -Force

        if ($LASTEXITCODE -eq 0) {
            Write-Log "Claude Code response received" "SUCCESS"
            return $response
        } else {
            Write-Log "Claude Code invocation failed" "ERROR"
            return "Sorry, I encountered an error processing your request. Please try again."
        }
    } catch {
        Write-Log "Exception invoking Claude Code: $_" "ERROR"
        return "Sorry, I encountered an error processing your request. Please try again."
    }
}

# Function to send message to Teams
function Send-TeamsMessage {
    param([string]$ChatName, [string]$Message)

    $prompt = @"
Send this message to the Teams chat named "$ChatName":

$Message

Use the Teams MCP tools (mcp__teams__*) to send the message.
"@

    $promptFile = [System.IO.Path]::GetTempFileName()
    Set-Content -Path $promptFile -Value $prompt

    try {
        & "$CLAUDE_CLI" -p $promptFile 2>&1 | Out-Null
        Remove-Item $promptFile -Force
        Write-Log "Message sent to Teams chat: $ChatName" "SUCCESS"
    } catch {
        Write-Log "Failed to send message to Teams: $_" "ERROR"
    }
}

# Function to check for new messages
function Get-NewMessages {
    param([string]$ChatName, [string]$LastMessageId)

    $prompt = @"
Check for new messages in the Teams chat named "$ChatName".

Last processed message ID: $LastMessageId

Use the Teams MCP tools to:
1. List recent messages in the chat
2. Filter out messages we've already processed
3. Return only messages from other users (not the bot)

Return the messages in JSON format:
[
  {
    "id": "message_id",
    "text": "message text",
    "from": "user name",
    "timestamp": "ISO timestamp"
  }
]

If no new messages, return an empty array: []
"@

    $promptFile = [System.IO.Path]::GetTempFileName()
    Set-Content -Path $promptFile -Value $prompt

    try {
        $response = & "$CLAUDE_CLI" -p $promptFile 2>&1 | Out-String
        Remove-Item $promptFile -Force

        # Extract JSON from response
        if ($response -match '\[[\s\S]*\]') {
            $json = $Matches[0]
            $messages = $json | ConvertFrom-Json
            return $messages
        }

        return @()
    } catch {
        Write-Log "Failed to check for new messages: $_" "ERROR"
        return @()
    }
}

# Main polling loop
Write-Log "Starting polling loop for chat: $CHAT_NAME" "SUCCESS"
Write-Log "Press Ctrl+C to stop"

$lastMessageId = Get-LastMessageId

while ($true) {
    try {
        Write-Log "Checking for new messages..."

        $newMessages = Get-NewMessages -ChatName $CHAT_NAME -LastMessageId $lastMessageId

        if ($newMessages.Count -gt 0) {
            Write-Log "Found $($newMessages.Count) new message(s)" "SUCCESS"

            foreach ($message in $newMessages) {
                Write-Log "Processing message from $($message.from): $($message.text)"

                # Detect language
                $language = Detect-Language -Text $message.text

                # Process with Claude Code
                $response = Invoke-SqlQuery -MessageText $message.text -Language $language

                # Send response back to Teams
                Send-TeamsMessage -ChatName $CHAT_NAME -Message $response

                # Update last processed message ID
                $lastMessageId = $message.id
                Save-LastMessageId -MessageId $message.id

                Write-Log "Message processed successfully" "SUCCESS"
            }
        } else {
            Write-Log "No new messages"
        }

        # Wait before next poll
        Start-Sleep -Seconds $POLL_INTERVAL

    } catch {
        Write-Log "Error in main loop: $_" "ERROR"
        Start-Sleep -Seconds $POLL_INTERVAL
    }
}
