# Clean up old unused SQL bot files

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          🧹 CLEANUP - Delete Old Bot Files                     ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$filesToDelete = @(
    "sql-bot-orchestrator.ps1",
    "run-sql-bot-foreground.ps1",
    "state\sql_orchestrator.lock",
    "state\last_sql_message_id.txt",
    "state\sql_bot_messages.json",
    "state\sql_bot.log"
)

$deletedCount = 0

foreach ($file in $filesToDelete) {
    $fullPath = Join-Path $PSScriptRoot $file

    if (Test-Path $fullPath) {
        try {
            Remove-Item $fullPath -Force -ErrorAction Stop
            Write-Host "✅ Deleted: $file" -ForegroundColor Green
            $deletedCount++
        } catch {
            Write-Host "⚠️  Could not delete: $file ($_)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "ℹ️  Not found: $file (already deleted)" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Cleanup complete: $deletedCount files deleted" -ForegroundColor Green
Write-Host ""
Write-Host "Current bot files (keeping these):" -ForegroundColor Cyan
Write-Host "  • sql-bot-v2.ps1" -ForegroundColor Green
Write-Host "  • start-sql-bot-v2.ps1" -ForegroundColor Green
Write-Host "  • stop-sql-bot-v2.ps1" -ForegroundColor Green
Write-Host "  • restart-sql-bot-v2.ps1" -ForegroundColor Green
Write-Host "  • state\sql_bot_v2_*.* (all v2 state files)" -ForegroundColor Green
Write-Host ""
