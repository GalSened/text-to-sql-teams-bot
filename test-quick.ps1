# Quick test of the SQL bot API
$body = @{
    question = 'How many companies are in the system?'
} | ConvertTo-Json

Write-Host "Testing: How many companies are in the system?" -ForegroundColor Cyan
$response = Invoke-RestMethod -Uri 'http://localhost:8000/query/ask' -Method Post -Body $body -ContentType 'application/json'
Write-Host "`nResponse:" -ForegroundColor Green
$response | ConvertTo-Json -Depth 5

Write-Host "`n`n---`n" -ForegroundColor Yellow

# Test Hebrew query
$bodyHe = @{
    question = 'כמה חברות יש במערכת?'
} | ConvertTo-Json -Depth 5

Write-Host "Testing: כמה חברות יש במערכת?" -ForegroundColor Cyan
$responseHe = Invoke-RestMethod -Uri 'http://localhost:8000/query/ask' -Method Post -Body $bodyHe -ContentType 'application/json'
Write-Host "`nResponse:" -ForegroundColor Green
$responseHe | ConvertTo-Json -Depth 5
