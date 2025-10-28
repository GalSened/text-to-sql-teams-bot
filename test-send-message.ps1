. "C:\Users\gals\teams-support-analyst\graph-api-helpers.ps1"

$CHAT_ID = "19:9aa2d304ade8465baadcd9051e0a5cfc@thread.v2"

Write-Host "📤 Testing Send-TeamsChatMessage function..." -ForegroundColor Cyan

$testMessage = @"
**SQL Query:**
``````sql
SELECT COUNT(*) as count FROM Companies
``````

**Method:** pattern_matching
**Type:** READ
"@

Write-Host "Message to send:" -ForegroundColor Gray
Write-Host $testMessage -ForegroundColor White
Write-Host ""

try {
    $result = Send-TeamsChatMessage -ChatId $CHAT_ID -Message $testMessage

    if ($result -and $result.id) {
        Write-Host "✅ Message sent successfully!" -ForegroundColor Green
        Write-Host "   Message ID: $($result.id)" -ForegroundColor Gray
    } else {
        Write-Host "⚠️  Send function returned but no message ID" -ForegroundColor Yellow
        $result | ConvertTo-Json -Depth 5
    }
} catch {
    Write-Host "❌ ERROR: $_" -ForegroundColor Red
}
