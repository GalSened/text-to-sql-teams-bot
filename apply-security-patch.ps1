# Apply Security Patch to SQL Bot V2
# Adds READ-ONLY mode to prevent data modification

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Red
Write-Host "║          🔒 SQL BOT V2 - SECURITY PATCH                        ║" -ForegroundColor Red
Write-Host "║                                                                ║" -ForegroundColor Red
Write-Host "║  This patch adds READ-ONLY mode to prevent:                   ║" -ForegroundColor Red
Write-Host "║  - DELETE operations                                           ║" -ForegroundColor Red
Write-Host "║  - UPDATE operations                                           ║" -ForegroundColor Red
Write-Host "║  - INSERT operations                                           ║" -ForegroundColor Red
Write-Host "║  - DROP/ALTER/CREATE operations                                ║" -ForegroundColor Red
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Red
Write-Host ""

$botScript = Join-Path $PSScriptRoot "sql-bot-v2.ps1"
$backupScript = Join-Path $PSScriptRoot "sql-bot-v2.backup.ps1"

if (!(Test-Path $botScript)) {
    Write-Host "❌ Error: sql-bot-v2.ps1 not found" -ForegroundColor Red
    exit 1
}

# Create backup
Write-Host "📦 Creating backup: sql-bot-v2.backup.ps1" -ForegroundColor Cyan
Copy-Item $botScript $backupScript -Force
Write-Host "✅ Backup created" -ForegroundColor Green

# Read the current script
$content = Get-Content $botScript -Raw

# Check if patch already applied
if ($content -match "SECURITY: Block non-READ queries") {
    Write-Host ""
    Write-Host "ℹ️  Security patch already applied!" -ForegroundColor Yellow
    Write-Host "   No changes needed." -ForegroundColor Gray
    exit 0
}

# Create the security check code
$securityCheck = @'

                # ═══════════════════════════════════════════════════════════
                # SECURITY CHECK: Block non-READ queries
                # ═══════════════════════════════════════════════════════════
                if ($sql -match '^\s*(UPDATE|DELETE|INSERT|DROP|CREATE|ALTER|TRUNCATE|EXEC|EXECUTE|MERGE|GRANT|REVOKE)') {
                    Write-Host "🚫 SECURITY BLOCK: Non-READ query blocked" -ForegroundColor Red
                    Write-Host "   SQL: $sql" -ForegroundColor Gray
                    Write-Log "SECURITY BLOCK: Non-READ query attempted: $sql" "WARN"

                    $securityMsg = @"
🚫 **Security Policy Violation**

This bot only executes **READ queries** (SELECT statements) for safety.

The following operation was **blocked**:
- Query type: Data modification
- Risk level: High

For data modifications (INSERT/UPDATE/DELETE), please:
1. Use the admin web interface at http://localhost:8000
2. Contact your database administrator

Your question was: $cleanMessage
"@

                    try {
                        $sentMessage = Send-TeamsChatMessage -ChatId $CHAT_ID -Message $securityMsg
                        if ($sentMessage -and $sentMessage.id) {
                            Mark-BotMessage $sentMessage.id
                            Write-Host "✅ Security warning sent to user" -ForegroundColor Green
                        }
                    } catch {
                        Write-Host "⚠️  Error sending security message: $_" -ForegroundColor Yellow
                        Write-Log "Error sending security message: $_" "ERROR"
                    }

                    Set-Content $STATE_FILE $msgId -Force
                    continue
                }

'@

# Find the line where we call Execute-SQL and insert security check before it
# Looking for the pattern: Write-Host "⚡ Executing SQL..." -ForegroundColor Cyan
$pattern = '(\s+)(Write-Host "⚡ Executing SQL\.\.\." -ForegroundColor Cyan)'
$replacement = $securityCheck + '$1$2'

if ($content -match $pattern) {
    $content = $content -replace $pattern, $replacement

    # Save the patched script
    Set-Content $botScript $content -Encoding UTF8 -NoNewline

    Write-Host ""
    Write-Host "✅ Security patch applied successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Changes made:" -ForegroundColor Cyan
    Write-Host "  • Added READ-ONLY mode enforcement" -ForegroundColor Gray
    Write-Host "  • Blocks UPDATE/DELETE/INSERT/DROP operations" -ForegroundColor Gray
    Write-Host "  • Sends security warning to users" -ForegroundColor Gray
    Write-Host "  • Logs blocked attempts" -ForegroundColor Gray
    Write-Host ""
    Write-Host "⚠️  Important: Restart the bot for changes to take effect" -ForegroundColor Yellow
    Write-Host "   Run: .\restart-sql-bot-v2.ps1" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To rollback, restore from backup:" -ForegroundColor Gray
    Write-Host "   Copy-Item sql-bot-v2.backup.ps1 sql-bot-v2.ps1 -Force" -ForegroundColor Gray
    Write-Host ""

} else {
    Write-Host "❌ Error: Could not find insertion point in script" -ForegroundColor Red
    Write-Host "   Manual patching required. See SECURITY_REPORT.md" -ForegroundColor Yellow
    exit 1
}
