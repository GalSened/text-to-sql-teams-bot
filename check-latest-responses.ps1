# Check Latest Test Responses

. "C:\Users\gals\teams-support-analyst\graph-api-helpers.ps1"

$CHAT_ID = "19:9aa2d304ade8465baadcd9051e0a5cfc@thread.v2"

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "CHECKING LATEST MESSAGES IN TEAMS CHAT" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$messages = Get-TeamsChatMessages -ChatId $CHAT_ID -Top 10

Write-Host "Recent messages:" -ForegroundColor Yellow
Write-Host ""

$messages | Select-Object -First 10 | ForEach-Object {
    $from = $_.from.user.displayName
    $content = $_.body.content -replace '<[^>]+>', ''
    $content = $content.Trim()
    $time = $_.createdDateTime

    Write-Host "───────────────────────────────────────────────────────" -ForegroundColor Gray
    Write-Host "Time: $time" -ForegroundColor Yellow
    Write-Host "From: $from" -ForegroundColor Cyan

    if ($content.Length -gt 400) {
        Write-Host "Message: $($content.Substring(0, 400))..." -ForegroundColor White
    } else {
        Write-Host "Message: $content" -ForegroundColor White
    }
    Write-Host ""
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "CHECKING FOR BILINGUAL SECURITY MESSAGES" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$hasEnglishMessage = $messages | Where-Object { $_.body.content -match "only supports read queries" }
$hasHebrewMessage = $messages | Where-Object { $_.body.content -match "הבוט תומך רק בשאילתות קריאה" }
$hasSecurityPolicy = $messages | Where-Object { $_.body.content -match "Security Policy" }

if ($hasSecurityPolicy) {
    Write-Host "✅ Found 'Security Policy' message!" -ForegroundColor Green
    Write-Host ""
}

if ($hasEnglishMessage) {
    Write-Host "✅ Found English security message!" -ForegroundColor Green
} else {
    Write-Host "❌ English security message NOT found" -ForegroundColor Red
}

if ($hasHebrewMessage) {
    Write-Host "✅ Found Hebrew security message!" -ForegroundColor Green
} else {
    Write-Host "❌ Hebrew security message NOT found" -ForegroundColor Red
}

Write-Host ""
