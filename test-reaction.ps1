# Test SQL Bot Reaction

. "C:\Users\gals\teams-support-analyst\graph-api-helpers.ps1"

$CHAT_ID = "19:9aa2d304ade8465baadcd9051e0a5cfc@thread.v2"  # ask the DB

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "TESTING SQL BOT REACTION IN 'ask the DB' CHAT" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "Sending test question..." -ForegroundColor Yellow
$result = Send-TeamsChatMessage -ChatId $CHAT_ID -Message "How many companies?"

if ($result -and $result.id) {
    Write-Host "✅ Question sent! Message ID: $($result.id)" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to send message" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Waiting 10 seconds for bot to process..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "Checking bot log for reaction..." -ForegroundColor Cyan
$logEntries = Get-Content "C:\Users\gals\text-to-sql-app\state\sql_bot_v2.log" -Tail 20

Write-Host ""
Write-Host "Recent log entries:" -ForegroundColor Yellow
$logEntries | ForEach-Object {
    if ($_ -match "reaction|Reaction|👀") {
        Write-Host $_ -ForegroundColor Green
    } elseif ($_ -match "How many companies") {
        Write-Host $_ -ForegroundColor Cyan
    } elseif ($_ -match "ERROR|Error") {
        Write-Host $_ -ForegroundColor Red
    } else {
        Write-Host $_ -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "Checking Teams for reaction..." -ForegroundColor Cyan
$messages = Get-TeamsChatMessages -ChatId $CHAT_ID -Top 3

$testMessage = $messages | Where-Object { $_.id -eq $result.id }
if ($testMessage -and $testMessage.reactions) {
    Write-Host "✅ Reaction found on message!" -ForegroundColor Green
    $testMessage.reactions | ForEach-Object {
        Write-Host "   Reaction: $($_.reactionType)" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ No reaction found on message" -ForegroundColor Red
}

Write-Host ""
