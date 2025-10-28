Write-Host "🔍 Testing SQL API directly..." -ForegroundColor Cyan

$body = @{
    question = "כמה חברות יש במערכת?"
} | ConvertTo-Json

Write-Host "Request: $body" -ForegroundColor Gray

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/query/ask" -Method Post -Body $body -ContentType "application/json; charset=utf-8" -TimeoutSec 30

    Write-Host "✅ API Response:" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 5
} catch {
    Write-Host "❌ ERROR: $_" -ForegroundColor Red
    Write-Host "Status: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
}
