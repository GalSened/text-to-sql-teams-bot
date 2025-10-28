. "C:\Users\gals\teams-support-analyst\graph-api-helpers.ps1"

$CHAT_ID = "19:9aa2d304ade8465baadcd9051e0a5cfc@thread.v2"

Write-Host "📥 Fetching last 10 messages from 'ask the DB' chat..." -ForegroundColor Cyan
Write-Host ""

$messages = Get-TeamsChatMessages -ChatId $CHAT_ID -Top 10

foreach ($msg in $messages) {
    $from = $msg.from.user.displayName
    $time = $msg.createdDateTime
    $msgId = $msg.id
    $content = ($msg.body.content -replace '<[^>]+>', '')

    Write-Host "═══════════════════════════════════════" -ForegroundColor Gray
    Write-Host "ID: $msgId" -ForegroundColor Yellow
    Write-Host "From: $from" -ForegroundColor White
    Write-Host "Time: $time" -ForegroundColor Gray
    Write-Host "Content:" -ForegroundColor Cyan
    Write-Host $content -ForegroundColor White

    if ($msg.reactions -and $msg.reactions.Count -gt 0) {
        Write-Host "Reactions:" -ForegroundColor Green
        foreach ($reaction in $msg.reactions) {
            Write-Host "  $($reaction.reactionType)" -ForegroundColor Green
        }
    }
    Write-Host ""
}
