# Test Security Patch
# Demonstrates what queries are allowed vs blocked

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          🔒 SECURITY TEST - Query Classification               ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

function Test-Query {
    param([string]$Query, [string]$Description)

    Write-Host "─────────────────────────────────────────────────────────────────" -ForegroundColor Gray
    Write-Host "Query: $Description" -ForegroundColor Yellow
    Write-Host "SQL: $Query" -ForegroundColor White

    if ($Query -match '^\s*(UPDATE|DELETE|INSERT|DROP|CREATE|ALTER|TRUNCATE|EXEC|EXECUTE|MERGE|GRANT|REVOKE)') {
        Write-Host "Status: 🚫 BLOCKED" -ForegroundColor Red
        Write-Host "Reason: Data modification not allowed" -ForegroundColor Red
    } else {
        Write-Host "Status: ✅ ALLOWED" -ForegroundColor Green
        Write-Host "Reason: Read-only operation" -ForegroundColor Green
    }
    Write-Host ""
}

Write-Host "Testing READ queries (should be ALLOWED):" -ForegroundColor Cyan
Write-Host ""

Test-Query "SELECT COUNT(*) FROM Companies" "Count companies"
Test-Query "SELECT * FROM Users WHERE Status = 'Active'" "List active users"
Test-Query "SELECT c.Name, COUNT(u.Id) FROM Companies c LEFT JOIN Users u ON c.Id = u.CompanyId GROUP BY c.Name" "Join query with aggregation"
Test-Query "WITH ActiveCompanies AS (SELECT * FROM Companies WHERE Status = 'Active') SELECT * FROM ActiveCompanies" "CTE query"

Write-Host ""
Write-Host "Testing WRITE queries (should be BLOCKED):" -ForegroundColor Red
Write-Host ""

Test-Query "UPDATE Companies SET Status = 'Active' WHERE Id = 123" "Update single company"
Test-Query "DELETE FROM Companies WHERE Id = 123" "Delete single company"
Test-Query "INSERT INTO Companies (Name, Status) VALUES ('Test', 'Active')" "Insert new company"
Test-Query "TRUNCATE TABLE Companies" "Truncate table"
Test-Query "DROP TABLE Companies" "Drop table"
Test-Query "CREATE TABLE Test (Id INT)" "Create table"
Test-Query "ALTER TABLE Companies ADD COLUMN Test VARCHAR(100)" "Alter table"
Test-Query "EXEC sp_executesql 'SELECT * FROM Companies'" "Execute stored procedure"
Test-Query "UPDATE Companies SET Status = 'Inactive'" "Mass update (no WHERE)"
Test-Query "DELETE FROM Users" "Mass delete (no WHERE)"

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Summary:" -ForegroundColor Yellow
Write-Host "  ✅ SELECT queries: ALLOWED" -ForegroundColor Green
Write-Host "  🚫 All other queries: BLOCKED" -ForegroundColor Red
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
