# Send test message to Teams
. .\graph-api-helpers.ps1

$CHAT_ID = '19:9aa2d304ade8465baadcd9051e0a5cfc@thread.v2'
$hebrewQuestion = 'כמה חברות יש במערכת?'

Send-TeamsChatMessage -ChatId $CHAT_ID -Message $hebrewQuestion
Write-Host "Test message sent: $hebrewQuestion" -ForegroundColor Green
