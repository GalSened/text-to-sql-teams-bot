# Text-to-SQL Application - Test Plan

## Test Environment Status

### ✅ Completed Checks
1. **Python Version**: 3.12.0 ✓
2. **Dependencies Installed**:
   - fastapi: 0.116.1 ✓
   - openai: 1.96.0 ✓
   - pyodbc: 5.2.0 ✓
3. **Project Structure**: All core files present ✓
4. **Code Review**: Architecture reviewed ✓

### ⚠️ Required for Testing
1. **Environment Configuration**: Create `.env` file from `.env.example`
2. **OpenAI API Key**: Required for SQL generation
3. **SQL Server**: Need a test database connection
4. **Missing Dependencies**: Some requirements may need installation

---

## Test Execution Plan

### Phase 1: Environment Setup Tests

#### Test 1.1: Install Missing Dependencies
```bash
cd text-to-sql-app
pip install -r requirements.txt
```

**Expected Result**: All dependencies installed without errors

#### Test 1.2: Create Environment File
```bash
cp .env.test .env
# Edit .env with real credentials:
# - OPENAI_API_KEY (required)
# - DB_SERVER, DB_NAME, DB_USER, DB_PASSWORD (for database tests)
```

#### Test 1.3: Verify ODBC Driver
```bash
# Windows:
odbcad32.exe
# Check if "ODBC Driver 18 for SQL Server" is installed

# If not installed, download from:
# https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
```

---

### Phase 2: Application Startup Tests

#### Test 2.1: Import Check
```bash
cd text-to-sql-app
python -c "from app.config import settings; print('Config loaded successfully')"
```

**Expected Result**: Configuration loads without errors

**Common Errors**:
- Missing `.env` file → Create from `.env.example`
- Missing required variables → Check all required fields in config

#### Test 2.2: Database Connection Test
```bash
python -c "
from app.core.database import db_manager
try:
    if db_manager.test_connection():
        print('✓ Database connection successful')
    else:
        print('✗ Database connection failed')
except Exception as e:
    print(f'✗ Connection error: {e}')
"
```

**Expected Result**: Database connection successful

**Alternative**: Use SQLite for testing without SQL Server:
- Modify `config.py` to support SQLite
- Use in-memory database: `sqlite:///:memory:`

#### Test 2.3: Application Startup
```bash
# Option 1: Direct run
python -m app.main

# Option 2: With uvicorn
uvicorn app.main:app --reload --port 8000
```

**Expected Result**:
- Server starts on http://localhost:8000
- No startup errors
- Database connection successful
- Schema cache loaded

**Check startup logs for**:
- "Starting Text-to-SQL Application"
- "Database connection successful"
- "Schema cache loaded"

---

### Phase 3: API Endpoint Tests

#### Test 3.1: Root Endpoint
```bash
curl http://localhost:8000/
```

**Expected Response**:
```json
{
  "app": "Text-to-SQL Application",
  "version": "1.0.0",
  "status": "running",
  "docs": "/docs"
}
```

#### Test 3.2: Health Check
```bash
curl http://localhost:8000/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

#### Test 3.3: Interactive API Documentation
Open in browser:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Verify**:
- All endpoints are visible
- Request/response models are documented
- Can execute test requests

---

### Phase 4: Core Functionality Tests

#### Test 4.1: Get Database Schema
```bash
curl http://localhost:8000/schema
```

**Expected Response**: JSON with tables, columns, and relationships

#### Test 4.2: Simple SELECT Query
```bash
curl -X POST http://localhost:8000/query/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show me all tables in the database",
    "execute_immediately": true
  }'
```

**Expected Response**:
```json
{
  "query_id": "uuid-here",
  "sql": "SELECT * FROM INFORMATION_SCHEMA.TABLES",
  "query_type": "READ",
  "risk_level": "low",
  "explanation": "...",
  "requires_confirmation": false,
  "executed": true,
  "results": [...],
  "row_count": 10
}
```

#### Test 4.3: Write Query with Confirmation
```bash
# Step 1: Ask question (don't execute)
curl -X POST http://localhost:8000/query/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Insert a test customer with name John Doe",
    "execute_immediately": false
  }'
# Save the query_id from response

# Step 2: Preview the query
curl http://localhost:8000/query/preview/{query_id}

# Step 3: Execute with confirmation
curl -X POST http://localhost:8000/query/execute \
  -H "Content-Type: application/json" \
  -d '{
    "query_id": "{query_id}",
    "confirmed": true
  }'
```

#### Test 4.4: Risky Query (UPDATE/DELETE without WHERE)
```bash
curl -X POST http://localhost:8000/query/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Delete all customers",
    "execute_immediately": false
  }'
```

**Expected Behavior**:
- Query classified as `WRITE_RISKY`
- Risk level: `critical`
- Requires confirmation: `true`
- Should show preview before execution

#### Test 4.5: Query History
```bash
curl http://localhost:8000/query/history?limit=10
```

**Expected Response**: Array of recent query executions

---

### Phase 5: Safety Feature Tests

#### Test 5.1: Query Classification
Test each query type:

**READ (Low Risk)**:
```sql
SELECT * FROM customers WHERE id = 123
```

**WRITE_SAFE (Medium Risk)**:
```sql
INSERT INTO customers (name, email) VALUES ('John', 'john@example.com')
UPDATE customers SET email = 'new@email.com' WHERE id = 123
```

**WRITE_RISKY (High Risk)**:
```sql
UPDATE customers SET status = 'inactive'  -- No WHERE clause
DELETE FROM old_logs WHERE created_date < '2020-01-01'  -- Bulk operation
```

**ADMIN (Critical Risk)**:
```sql
DROP TABLE customers
CREATE TABLE new_table (id INT)
ALTER TABLE customers ADD new_column VARCHAR(50)
```

#### Test 5.2: Confirmation Workflow
Verify that:
- READ queries can execute immediately (if configured)
- WRITE_SAFE queries require confirmation
- WRITE_RISKY queries show preview + require confirmation
- ADMIN queries are blocked (if `ENABLE_ADMIN_OPERATIONS=false`)

#### Test 5.3: SQL Injection Prevention
Test with potentially malicious input:
```bash
curl -X POST http://localhost:8000/query/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show customers; DROP TABLE users;--",
    "execute_immediately": false
  }'
```

**Expected**: Query should be validated and potentially blocked

---

### Phase 6: Error Handling Tests

#### Test 6.1: Invalid SQL
```bash
curl -X POST http://localhost:8000/query/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Do something impossible with the database",
    "execute_immediately": false
  }'
```

**Expected**: Graceful error message

#### Test 6.2: Missing Query ID
```bash
curl http://localhost:8000/query/preview/non-existent-id
```

**Expected**: 404 error with clear message

#### Test 6.3: Database Connection Loss
- Stop SQL Server
- Try executing a query
- **Expected**: Service unavailable error

---

### Phase 7: Performance Tests

#### Test 7.1: Large Result Set
```bash
# Query that returns many rows
curl -X POST http://localhost:8000/query/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show all records from the largest table",
    "execute_immediately": true
  }'
```

**Verify**:
- Results are limited by `MAX_ROWS_RETURN` setting
- Response time is reasonable
- No timeout errors

#### Test 7.2: Complex Query
```bash
curl -X POST http://localhost:8000/query/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show top 10 customers by total purchase amount with their order counts and average order value",
    "execute_immediately": true
  }'
```

**Verify**:
- OpenAI generates correct JOIN and aggregation logic
- Query executes within timeout
- Results are accurate

---

### Phase 8: Integration Tests

#### Test 8.1: End-to-End Workflow
1. Ask a question
2. Review generated SQL
3. Preview affected rows (if write operation)
4. Execute with confirmation
5. Check results
6. Verify in query history

#### Test 8.2: Schema Refresh
```bash
# Add a new table to database
# Then refresh schema
curl -X POST http://localhost:8000/schema/refresh

# Ask question about new table
curl -X POST http://localhost:8000/query/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show me the new_table",
    "execute_immediately": true
  }'
```

---

## Test Checklist

### Environment
- [ ] Python 3.12+ installed
- [ ] All requirements installed
- [ ] `.env` file configured
- [ ] OpenAI API key valid
- [ ] SQL Server accessible
- [ ] ODBC Driver 18 installed

### Application
- [ ] Application starts without errors
- [ ] Database connection successful
- [ ] Schema cache loads
- [ ] All endpoints accessible
- [ ] Documentation pages load

### Functionality
- [ ] SELECT queries work
- [ ] INSERT queries work with confirmation
- [ ] UPDATE queries require confirmation
- [ ] DELETE queries require confirmation
- [ ] Query classification accurate
- [ ] Risk assessment appropriate
- [ ] Preview shows correct data
- [ ] Query history tracked

### Safety
- [ ] Confirmation workflow enforced
- [ ] Risky queries blocked until confirmed
- [ ] ADMIN operations disabled (if configured)
- [ ] SQL injection attempts handled
- [ ] Invalid queries rejected

### Performance
- [ ] Response time < 5 seconds (typical query)
- [ ] Large result sets handled
- [ ] Complex queries execute correctly
- [ ] No memory leaks during extended use

---

## Test Results Template

### Test Execution Log

**Date**: _______________
**Tester**: _______________
**Environment**: Development / Staging / Production

#### Summary
- Total Tests: ___
- Passed: ___
- Failed: ___
- Blocked: ___

#### Failed Tests
| Test ID | Description | Error | Notes |
|---------|-------------|-------|-------|
|         |             |       |       |

#### Recommendations
1.
2.
3.

---

## Known Issues & Limitations

### Current Limitations
1. No test suite included (tests/ directory is empty)
2. No authentication/authorization implemented
3. CORS configured to allow all origins (needs restriction for production)
4. No rate limiting
5. Query history stored in memory (lost on restart)
6. No query result caching

### Recommendations for Production
1. **Security**:
   - Implement authentication (API keys, OAuth, JWT)
   - Add rate limiting
   - Restrict CORS to specific origins
   - Use secure database credentials storage
   - Enable SSL/TLS for all connections

2. **Reliability**:
   - Add persistent storage for query history (database or Redis)
   - Implement connection pooling
   - Add retry logic for transient failures
   - Set up health monitoring

3. **Testing**:
   - Create comprehensive unit tests
   - Add integration tests
   - Implement E2E tests
   - Set up CI/CD pipeline

4. **Performance**:
   - Implement query result caching
   - Add request/response compression
   - Optimize large result set handling
   - Consider async database operations

5. **Monitoring**:
   - Add metrics collection (Prometheus)
   - Set up logging aggregation (ELK stack)
   - Implement alerting for errors
   - Track API usage statistics

---

## Quick Test Script

Save as `quick_test.sh` or `quick_test.ps1`:

```bash
#!/bin/bash
echo "=== Text-to-SQL Quick Test ==="

# Test 1: Root endpoint
echo -e "\n1. Testing root endpoint..."
curl -s http://localhost:8000/ | jq

# Test 2: Health check
echo -e "\n2. Testing health check..."
curl -s http://localhost:8000/health | jq

# Test 3: Get schema
echo -e "\n3. Getting database schema..."
curl -s http://localhost:8000/schema | jq '.tables | length' | xargs echo "Number of tables:"

# Test 4: Simple query
echo -e "\n4. Testing simple query..."
curl -s -X POST http://localhost:8000/query/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Show me database tables", "execute_immediately": true}' | jq

# Test 5: Query history
echo -e "\n5. Checking query history..."
curl -s http://localhost:8000/query/history | jq 'length' | xargs echo "History entries:"

echo -e "\n=== Tests Complete ==="
```

---

## Support & Troubleshooting

### Getting Help
1. Check the README.md for detailed documentation
2. Review QUICKSTART.md for setup instructions
3. Check logs in `logs/app.log`
4. Enable DEBUG mode in .env for verbose logging

### Common Issues

**Issue**: "ODBC Driver not found"
**Solution**: Install ODBC Driver 18 for SQL Server

**Issue**: "Cannot connect to database"
**Solution**: Verify SQL Server is running, credentials are correct, and port 1433 is accessible

**Issue**: "OpenAI API error"
**Solution**: Check API key, credits, and rate limits

**Issue**: "Import errors"
**Solution**: Reinstall dependencies: `pip install -r requirements.txt`

---

**Generated**: 2025-10-23
**Version**: 1.0.0
