# Bilingual Testing Plan - WeSign Text-to-SQL System
## Teams Bot "ask the DB" - Comprehensive Test Coverage

**Version:** 1.0
**Date:** 2025-10-26
**System:** Text-to-SQL Application with Microsoft Teams Integration
**Languages:** English (en) + Hebrew (he)

---

## 1. Test Environment Setup

### Prerequisites
- ✅ PostgreSQL queue database running (localhost:5433)
- ✅ Worker service running (`python worker_service.py --fast`)
- ✅ WeSign SQL Server database accessible (DEVTEST\SQLEXPRESS)
- ✅ Teams bot endpoint available (http://localhost:8000)
- ⏳ Teams chat "ask the DB" created
- ⏳ Bot added to Teams chat

### Verification Commands
```bash
# Check PostgreSQL is running
docker ps | grep postgres-queue

# Check worker service is running
tasklist | findstr python

# Check FastAPI server is running
curl http://localhost:8000/health
```

---

## 2. Test Categories & Coverage

### 2.1 COUNT Operations (Aggregation)

| Test ID | English Query | Hebrew Query | Expected SQL | Expected Result |
|---------|--------------|--------------|--------------|-----------------|
| **COUNT-01** | "How many companies are in the system?" | "כמה חברות יש במערכת?" | `SELECT COUNT(*) as count FROM Companies` | Count of companies |
| **COUNT-02** | "Count all contacts" | "ספור את כל אנשי הקשר" | `SELECT COUNT(*) as count FROM Contacts` | Count of contacts |
| **COUNT-03** | "How many documents?" | "כמה מסמכים?" | `SELECT COUNT(*) as count FROM Documents` | Count of documents |
| **COUNT-04** | "Count document collections" | "ספור אוספי מסמכים" | `SELECT COUNT(*) as count FROM DocumentCollections` | Count of collections |
| **COUNT-05** | "How many active directory configurations?" | "כמה תצורות Active Directory?" | `SELECT COUNT(*) as count FROM ActiveDirectoryConfigurations` | Count of configs |
| **COUNT-06** | "Count groups" | "ספור קבוצות" | `SELECT COUNT(*) as count FROM Groups` | Count of groups |
| **COUNT-07** | "How many log entries?" | "כמה רשומות לוג?" | `SELECT COUNT(*) as count FROM Logs` | Count of logs |

**Success Criteria:**
- Pattern detection: `COUNT` pattern matched with confidence ≥ 0.9
- SQL generated correctly for each WeSign table
- Query executes within 3 seconds
- Results returned in adaptive card format
- Language detection accurate (en vs he)

---

### 2.2 SELECT/LIST Operations (Retrieval)

| Test ID | English Query | Hebrew Query | Expected SQL | Expected Result |
|---------|--------------|--------------|--------------|-----------------|
| **SELECT-01** | "List all companies" | "רשום את כל החברות" | `SELECT TOP 100 * FROM Companies` | Up to 100 companies |
| **SELECT-02** | "Show all contacts" | "הצג את כל אנשי הקשר" | `SELECT TOP 100 * FROM Contacts` | Up to 100 contacts |
| **SELECT-03** | "Get all documents" | "הבא את כל המסמכים" | `SELECT TOP 100 * FROM Documents` | Up to 100 documents |
| **SELECT-04** | "List document collections" | "רשום אוספי מסמכים" | `SELECT TOP 100 * FROM DocumentCollections` | Collections list |
| **SELECT-05** | "Show groups" | "הצג קבוצות" | `SELECT TOP 100 * FROM Groups` | Groups list |
| **SELECT-06** | "List active directory configurations" | "רשום תצורות Active Directory" | `SELECT TOP 100 * FROM ActiveDirectoryConfigurations` | Config list |
| **SELECT-07** | "Get logs" | "הבא לוגים" | `SELECT TOP 100 * FROM Logs` | Log entries |

**Success Criteria:**
- Pattern detection: `SELECT` pattern matched with confidence ≥ 0.8
- Default limit of 100 rows applied
- Results formatted as table in Teams card
- Empty result handling graceful
- Hebrew text displays correctly (RTL)

---

### 2.3 Time-Based Filtering (Recent/Last)

| Test ID | English Query | Hebrew Query | Expected SQL | Expected Result |
|---------|--------------|--------------|--------------|-----------------|
| **TIME-01** | "Companies created last month" | "חברות שנוצרו בחודש שעבר" | `SELECT TOP 100 * FROM Companies WHERE created_at >= DATEADD(month, -1, GETDATE())` | Companies from last month |
| **TIME-02** | "Contacts added last week" | "אנשי קשר שנוספו בשבוע שעבר" | `SELECT TOP 100 * FROM Contacts WHERE created_at >= DATEADD(week, -1, GETDATE())` | Contacts from last week |
| **TIME-03** | "Documents from today" | "מסמכים מהיום" | `SELECT TOP 100 * FROM Documents WHERE created_at >= DATEADD(day, 0, GETDATE())` | Today's documents |
| **TIME-04** | "Last 30 days of logs" | "30 הימים האחרונים של לוגים" | `SELECT TOP 100 * FROM Logs WHERE created_at >= DATEADD(day, -30, GETDATE())` | Logs from last 30 days |
| **TIME-05** | "Companies created this year" | "חברות שנוצרו השנה" | `SELECT TOP 100 * FROM Companies WHERE created_at >= DATEADD(year, -1, GETDATE())` | This year's companies |

**Success Criteria:**
- Pattern detection: `RECENT` pattern matched with confidence ≥ 0.75
- Time period correctly extracted (day/week/month/year)
- Date column defaulted to `created_at` when not specified
- SQL date functions use GETDATE() and DATEADD()
- Results filtered correctly by date range

---

### 2.4 TOP N Queries (Limiting)

| Test ID | English Query | Hebrew Query | Expected SQL | Expected Result |
|---------|--------------|--------------|--------------|-----------------|
| **TOPN-01** | "Top 10 companies" | "10 החברות המובילות" | `SELECT TOP 10 * FROM Companies` | First 10 companies |
| **TOPN-02** | "Show 5 most recent contacts" | "הצג 5 אנשי קשר אחרונים" | `SELECT TOP 5 * FROM Contacts ORDER BY created_at DESC` | 5 newest contacts |
| **TOPN-03** | "Latest 20 documents" | "20 המסמכים האחרונים" | `SELECT TOP 20 * FROM Documents ORDER BY created_at DESC` | 20 newest documents |
| **TOPN-04** | "First 3 groups" | "3 הקבוצות הראשונות" | `SELECT TOP 3 * FROM Groups` | First 3 groups |
| **TOPN-05** | "Top 50 log entries" | "50 רשומות הלוג המובילות" | `SELECT TOP 50 * FROM Logs` | First 50 logs |

**Success Criteria:**
- Numeric values extracted from query
- TOP N clause correctly inserted into SQL
- ORDER BY applied when "recent" or "latest" keywords present
- Results limited to requested count
- Default limit (100) overridden by explicit value

---

### 2.5 GROUP BY Operations (Grouping)

| Test ID | English Query | Hebrew Query | Expected SQL | Expected Result |
|---------|--------------|--------------|--------------|-----------------|
| **GROUP-01** | "Documents by status" | "מסמכים לפי סטטוס" | `SELECT Status, COUNT(*) as count FROM Documents GROUP BY Status` | Document counts per status |
| **GROUP-02** | "Companies by type" | "חברות לפי סוג" | `SELECT CompanyType, COUNT(*) as count FROM Companies GROUP BY CompanyType` | Company counts per type |
| **GROUP-03** | "Contacts by company" | "אנשי קשר לפי חברה" | `SELECT CompanyId, COUNT(*) as count FROM Contacts GROUP BY CompanyId` | Contact counts per company |
| **GROUP-04** | "Logs by level" | "לוגים לפי רמה" | `SELECT LogLevel, COUNT(*) as count FROM Logs GROUP BY LogLevel` | Log counts per level |

**Success Criteria:**
- Pattern detection: `GROUP` pattern matched with confidence ≥ 0.7
- GROUP BY column correctly identified
- COUNT aggregation applied
- Results grouped correctly
- Multiple groups displayed in table format

---

### 2.6 Error Handling & Edge Cases

| Test ID | Query | Language | Expected Behavior |
|---------|-------|----------|-------------------|
| **ERROR-01** | "Show me the data" | en | Error: "Could not identify which table to query" |
| **ERROR-02** | "מידע" (just "information") | he | Error: No table identified |
| **ERROR-03** | "Count xyz" (non-existent table) | en | Error: Table not found |
| **ERROR-04** | "" (empty message) | en | Help message displayed |
| **ERROR-05** | "!!!???" (nonsense) | en | Error: No pattern matched |
| **ERROR-06** | Very long query (500+ chars) | en | Query processed or truncated gracefully |
| **ERROR-07** | SQL injection attempt: `"Show companies'; DROP TABLE Companies; --"` | en | Pattern-based generation prevents injection |
| **ERROR-08** | Mixed language: "How many חברות?" | en/he | Best-effort language detection |

**Success Criteria:**
- Graceful error messages in correct language
- No system crashes or unhandled exceptions
- SQL injection attempts safely handled (pattern-based, not direct string insertion)
- Help guidance provided for unclear queries
- Error details logged but not exposed to user

---

### 2.7 Bot Commands

| Command | Expected Response |
|---------|------------------|
| "help" | Help message with examples in detected language |
| "עזרה" | Hebrew help message |
| "status" | Current queue status and system health |
| "examples" | List of example queries in detected language |
| "דוגמאות" | Hebrew examples list |
| "schema" | Database schema information |
| "history" | Last 5 queries for the user |
| "clear" | Clear user's query history |

**Success Criteria:**
- Commands recognized regardless of case
- Hebrew commands work correctly
- Status shows accurate queue information
- Schema displays WeSign tables correctly
- History persists across sessions

---

## 3. Test Execution Strategy

### 3.1 Manual Testing (Teams UI)

**Step 1: Create Teams Chat**
1. Open Microsoft Teams
2. Create new chat named "ask the DB"
3. Add the text-to-sql bot to the chat
4. Verify bot sends welcome message

**Step 2: Test Each Category**
1. Copy test query from table above
2. Send in Teams chat
3. Wait for response (should be < 5 seconds)
4. Verify:
   - Response received
   - SQL query shown in card
   - Results accurate
   - Formatting correct
   - Language appropriate
5. Document any failures

**Step 3: Language Switching**
1. Send 3 English queries in sequence
2. Send 3 Hebrew queries in sequence
3. Alternate between languages
4. Verify language detection works each time

### 3.2 Automated Testing (test_bot_locally.py)

**Update test script with WeSign queries:**
```python
# Add to test_bot_locally.py
wesign_test_cases = [
    # English COUNT tests
    {"text": "How many companies are in the system?", "language": "en", "expected_table": "Companies"},
    {"text": "Count all contacts", "language": "en", "expected_table": "Contacts"},

    # Hebrew COUNT tests
    {"text": "כמה חברות יש במערכת?", "language": "he", "expected_table": "Companies"},
    {"text": "ספור את כל אנשי הקשר", "language": "he", "expected_table": "Contacts"},

    # English SELECT tests
    {"text": "List all companies", "language": "en", "expected_table": "Companies"},
    {"text": "Show all documents", "language": "en", "expected_table": "Documents"},

    # Hebrew SELECT tests
    {"text": "רשום את כל החברות", "language": "he", "expected_table": "Companies"},
    {"text": "הצג את כל המסמכים", "language": "he", "expected_table": "Documents"},

    # Time-based tests
    {"text": "Companies created last month", "language": "en", "expected_pattern": "RECENT"},
    {"text": "חברות שנוצרו בחודש שעבר", "language": "he", "expected_pattern": "RECENT"},
]
```

**Run automated tests:**
```bash
python test_bot_locally.py --wesign-tests
```

### 3.3 End-to-End Workflow Testing

**Test complete flow:**
1. User sends message in Teams → Teams API → FastAPI endpoint
2. FastAPI creates queue entry → PostgreSQL queue
3. Worker polls queue → Fetches pending request
4. Worker generates SQL → Executes against WeSign DB
5. Worker updates queue → Marks as completed
6. Worker sends proactive message → Teams notification
7. User receives result in Teams chat

**Verification points:**
- Message received by FastAPI (check logs)
- Queue entry created (check PostgreSQL)
- Worker picks up request (check worker logs)
- SQL generated correctly (check worker logs)
- SQL executed successfully (check WeSign DB)
- Queue updated to "completed" (check PostgreSQL)
- Teams notification sent (check Teams chat)

---

## 4. Success Metrics

### 4.1 Functional Metrics
- ✅ 100% of test queries generate valid SQL
- ✅ 95%+ of queries execute successfully (allow 5% for data-dependent failures)
- ✅ 100% of language detection correct for unambiguous queries
- ✅ All 7 WeSign tables successfully queried
- ✅ Both languages (en/he) work for all test categories

### 4.2 Performance Metrics
- ⚡ Queue → Response time < 5 seconds (95th percentile)
- ⚡ SQL generation < 100ms
- ⚡ SQL execution < 2 seconds (for typical queries)
- ⚡ Teams notification delivery < 1 second

### 4.3 Reliability Metrics
- 🛡️ Zero system crashes during test suite
- 🛡️ Zero SQL injection vulnerabilities
- 🛡️ All errors handled gracefully with user-friendly messages
- 🛡️ Worker service remains stable for 1+ hour of continuous operation

---

## 5. Test Execution Log Template

```markdown
## Test Execution: [DATE] [TIME]

**Tester:** [NAME]
**Environment:** [dev/test/prod]
**Worker Version:** [COMMIT/VERSION]

### Results Summary
- Total Tests: [ ]
- Passed: [ ]
- Failed: [ ]
- Skipped: [ ]

### Test Results

#### COUNT-01: "How many companies are in the system?"
- ✅/❌ Status:
- Generated SQL:
- Execution Time:
- Result Count:
- Notes:

#### COUNT-02: "כמה חברות יש במערכת?"
- ✅/❌ Status:
- Generated SQL:
- Execution Time:
- Result Count:
- Notes:

[Continue for all tests...]

### Issues Found
1. [Issue description]
   - Severity: Critical/High/Medium/Low
   - Test ID:
   - Reproduction steps:
   - Expected:
   - Actual:

### Recommendations
- [Recommendation 1]
- [Recommendation 2]
```

---

## 6. Next Steps After Testing

1. **Fix identified issues** from test execution
2. **Update documentation** based on test findings
3. **Add regression tests** for any bugs found
4. **Performance optimization** if metrics not met
5. **User acceptance testing** with real WeSign users
6. **Production deployment** plan

---

## 7. Testing Tools & Resources

### Required Tools
- Microsoft Teams Desktop/Web
- PostgreSQL client (psql or GUI)
- SQL Server Management Studio (SSMS) for WeSign DB
- Python 3.11+ with dependencies installed
- Text editor for documenting results

### Helpful Commands
```bash
# Monitor worker logs in real-time
Get-Content C:\Users\gals\text-to-sql-app\logs\orchestrator.log -Tail 50 -Wait

# Check queue status
psql -h localhost -p 5433 -U postgres -d text_to_sql_queue -c "SELECT id, status, question, created_at FROM sql_queue ORDER BY created_at DESC LIMIT 10;"

# Test local bot without Teams
python test_bot_locally.py

# Start worker in fast mode
python worker_service.py --fast

# Check WeSign table counts
sqlcmd -S DEVTEST\SQLEXPRESS -d WeSign -Q "SELECT 'Companies' as TableName, COUNT(*) as Count FROM Companies UNION ALL SELECT 'Contacts', COUNT(*) FROM Contacts UNION ALL SELECT 'Documents', COUNT(*) FROM Documents"
```

---

## Appendix A: WeSign Database Schema Reference

```sql
-- Companies Table
SELECT TOP 5 * FROM Companies;

-- Contacts Table
SELECT TOP 5 * FROM Contacts;

-- Documents Table
SELECT TOP 5 * FROM Documents;

-- DocumentCollections Table
SELECT TOP 5 * FROM DocumentCollections;

-- ActiveDirectoryConfigurations Table
SELECT TOP 5 * FROM ActiveDirectoryConfigurations;

-- Groups Table
SELECT TOP 5 * FROM Groups;

-- Logs Table
SELECT TOP 5 * FROM Logs;
```

---

**END OF TESTING PLAN**
