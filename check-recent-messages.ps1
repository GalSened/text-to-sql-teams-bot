# Check recent messages in "ask the DB" chat

. "C:\Users\gals\teams-support-analyst\graph-api-helpers.ps1"

$CHAT_ID = "19:9aa2d304ade8465baadcd9051e0a5cfc@thread.v2"

$messages = Get-TeamsChatMessages -ChatId $CHAT_ID -Top 10

Write-Host ""
Write-Host "Recent messages in 'ask the DB' chat:" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan

foreach ($msg in $messages) {
    $from = $msg.from.user.displayName
    $time = $msg.createdDateTime
    $content = $msg.body.content -replace '<[^>]+>', ''  # Remove HTML tags
    $content = $content.Trim()

    # Truncate long messages
    if ($content.Length -gt 150) {
        $content = $content.Substring(0, 150) + "..."
    }

    Write-Host ""
    Write-Host "From: $from" -ForegroundColor Yellow
    Write-Host "Time: $time" -ForegroundColor Gray
    Write-Host "Content: $content" -ForegroundColor White
}
