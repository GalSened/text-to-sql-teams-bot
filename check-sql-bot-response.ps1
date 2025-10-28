. "C:\Users\gals\teams-support-analyst\graph-api-helpers.ps1"

$CHAT_ID = "19:9aa2d304ade8465baadcd9051e0a5cfc@thread.v2"

Write-Host "📥 Checking 'ask the DB' chat messages..." -ForegroundColor Cyan
Write-Host ""

$messages = Get-TeamsChatMessages -ChatId $CHAT_ID -Top 3

foreach ($msg in $messages) {
    $from = $msg.from.user.displayName
    $time = $msg.createdDateTime
    $content = ($msg.body.content -replace '<[^>]+>', '').Substring(0, [Math]::Min(200, ($msg.body.content -replace '<[^>]+>', '').Length))

    Write-Host "---" -ForegroundColor Gray
    Write-Host "From: $from" -ForegroundColor White
    Write-Host "Time: $time" -ForegroundColor Gray
    Write-Host "Content: $content..." -ForegroundColor White

    # Check for reactions
    if ($msg.reactions -and $msg.reactions.Count -gt 0) {
        Write-Host "Reactions:" -ForegroundColor Green
        foreach ($reaction in $msg.reactions) {
            Write-Host "  $($reaction.reactionType)" -ForegroundColor Green
        }
    }
    Write-Host ""
}
