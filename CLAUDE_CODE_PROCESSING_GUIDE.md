# Claude Code Processing Guide

## Purpose

This guide explains how Claude Code (me) processes the SQL queue to convert natural language questions into SQL queries, execute them, and return natural language responses in English or Hebrew.

---

## When to Use This Guide

The user will say things like:
- "Process SQL queue"
- "Check for pending requests"
- "Generate SQL for pending queries"
- "Handle the queue"

When you hear these phrases, follow the steps in this guide.

---

## Overview of the Process

```
1. Fetch pending requests from database
2. For each request:
   a. Generate SQL query
   b. Classify query type (READ/WRITE/etc.)
   c. Check environment restrictions
   d. Execute SQL (if allowed)
   e. Parse results
   f. Generate natural language response
   g. Update database with results
3. Report summary to user
```

---

## Step-by-Step Processing Instructions

### Step 1: Fetch Pending Requests

Use the MCP postgres tool to query pending requests:

```sql
SELECT
  job_id,
  question,
  schema_info,
  environment,
  language,
  user_id,
  created_at
FROM sql_queue
WHERE status = 'pending'
ORDER BY created_at ASC
LIMIT 10;  -- Process in batches of 10
```

**If no pending requests**:
Tell the user: "No pending requests in the queue."

**If there are pending requests**:
Tell the user: "Found X pending requests. Processing now..."

---

### Step 2: Process Each Request

For each pending request, follow these sub-steps:

#### 2.1 Mark as Processing

```sql
UPDATE sql_queue
SET status = 'processing'
WHERE job_id = '<job_id>'::uuid;
```

#### 2.2 Analyze the Question

Read the question and schema_info to understand what the user wants.

**Key considerations**:
- What tables are involved?
- What columns are needed?
- Are there filters (WHERE clauses)?
- Are there aggregations (COUNT, SUM, AVG)?
- Are there JOINs?
- Is there sorting or limiting?

#### 2.3 Generate SQL Query

Based on the question and schema, generate appropriate SQL.

**Guidelines**:
- Use SQL Server (T-SQL) syntax
- Use proper table and column names from schema
- Add appropriate WHERE clauses for filtering
- Use JOINs when needed
- Add ORDER BY for "top N" queries
- Use TOP N instead of LIMIT
- Handle date functions properly (GETDATE(), DATEADD(), etc.)
- Escape special characters

**Example Translations**:

| Question (English) | SQL |
|--------------------|-----|
| "How many companies joined in the past 3 months?" | `SELECT COUNT(*) as company_count FROM companies WHERE created_date >= DATEADD(month, -3, GETDATE())` |
| "Show top 10 customers by revenue" | `SELECT TOP 10 customer_name, total_revenue FROM customers ORDER BY total_revenue DESC` |
| "List all active users" | `SELECT * FROM users WHERE status = 'active'` |

| Question (Hebrew) | SQL |
|-------------------|-----|
| "כמה חברות הצטרפו ב-3 החודשים האחרונים?" | Same SQL as English equivalent |
| "הראה את 10 הלקוחות המובילים לפי הכנסות" | Same SQL as English equivalent |

**Important**: The SQL is language-agnostic. Hebrew and English questions generate the same SQL if they ask the same thing.

#### 2.4 Classify Query Type

Analyze the SQL to determine its type:

- **READ**: SELECT statements only
- **WRITE_SAFE**: INSERT, UPDATE, DELETE with WHERE clause
- **WRITE_RISKY**: UPDATE/DELETE without WHERE (affects all rows)
- **ADMIN**: DROP, CREATE, ALTER, TRUNCATE, GRANT, REVOKE

**Examples**:
```sql
SELECT * FROM customers                          → READ
INSERT INTO customers VALUES (...)               → WRITE_SAFE
UPDATE customers SET status='active' WHERE id=1  → WRITE_SAFE
DELETE FROM customers WHERE id=1                 → WRITE_SAFE
UPDATE customers SET status='inactive'           → WRITE_RISKY (no WHERE!)
DELETE FROM old_data                             → WRITE_RISKY (affects all)
DROP TABLE customers                             → ADMIN
CREATE TABLE test (id INT)                       → ADMIN
```

#### 2.5 Assess Risk Level

Based on query type and impact:

- **low**: SELECT with simple WHERE
- **medium**: SELECT with JOINs, or WRITE_SAFE with clear WHERE
- **high**: WRITE_RISKY operations
- **critical**: ADMIN operations

#### 2.6 Check Environment Restrictions

**DevTest Environment**: All query types allowed
**Production Environment**: ONLY READ queries allowed

```python
# Pseudo-logic
if environment == 'prod' and query_type != 'READ':
    execution_allowed = False
    error_message = "Non-SELECT queries are not allowed in production"
    error_type = "environment_restriction"
else:
    execution_allowed = True
```

#### 2.7 Update Database with SQL and Classification

```sql
UPDATE sql_queue
SET
  sql_query = '<generated_sql>',
  query_type = '<READ|WRITE_SAFE|WRITE_RISKY|ADMIN>',
  risk_level = '<low|medium|high|critical>',
  execution_allowed = <true|false>,
  error_message = CASE WHEN execution_allowed = false THEN '<error_message>' ELSE NULL END,
  error_type = CASE WHEN execution_allowed = false THEN '<error_type>' ELSE NULL END,
  sql_generated_at = NOW(),
  status = CASE WHEN execution_allowed = true THEN 'processing' ELSE 'failed' END
WHERE job_id = '<job_id>'::uuid;
```

#### 2.8 Execute SQL (if execution_allowed)

**If execution_allowed = false**:
Skip execution, move to Step 2.11 to update status as 'failed'.

**If execution_allowed = true**:
Execute the SQL query on the target database.

**Use MCP tools for database access**:
- For postgres: Use mcp__serena__* tools or postgres MCP
- For SQL Server: May need to use Bash with `sqlcmd` or similar

**Example (PostgreSQL)**:
```sql
-- Execute the generated SQL
<generated_sql>
```

**Record**:
- Query results (as JSONB)
- Rows affected (if UPDATE/INSERT/DELETE)
- Execution time

#### 2.9 Parse Results

Convert SQL results into a structured format:

```json
{
  "columns": ["column1", "column2"],
  "rows": [
    {"column1": "value1", "column2": "value2"},
    ...
  ],
  "row_count": 47,
  "execution_time_ms": 123
}
```

#### 2.10 Generate Natural Language Response

**Critical**: Generate response in the SAME language as the question!

**Language Detection**:
- `language = 'en'` → Generate English response
- `language = 'he'` → Generate Hebrew response

**Response Templates**:

**For English (language = 'en')**:
```
# For COUNT queries:
"Found {count} {entity} that {condition}."

# For SELECT with results:
"Found {count} results. Here are the details: {summary_of_results}"

# For empty results:
"No results found matching your criteria."

# For blocked queries:
"This operation is not allowed in the current environment ({environment}). Only SELECT queries are permitted."

# For errors:
"An error occurred while processing your request: {error_message}"
```

**For Hebrew (language = 'he')**:
```
# For COUNT queries:
"נמצאו {count} {entity} ש{condition}."

# For SELECT with results:
"נמצאו {count} תוצאות. הנה הפרטים: {summary_of_results}"

# For empty results:
"לא נמצאו תוצאות התואמות את הקריטריונים שלך."

# For blocked queries:
"פעולה זו אינה מותרת בסביבה הנוכחית ({environment}). רק שאילתות SELECT מותרות."

# For errors:
"אירעה שגיאה בעיבוד בקשתך: {error_message}"
```

**Example Responses**:

| Question | Language | SQL Result | Natural Language Response |
|----------|----------|------------|---------------------------|
| "How many companies joined in the past 3 months?" | en | `[{"count": 47}]` | "Found 47 companies that joined in the past 3 months." |
| "כמה חברות הצטרפו ב-3 החודשים האחרונים?" | he | `[{"count": 47}]` | "נמצאו 47 חברות שהצטרפו ב-3 החודשים האחרונים." |
| "Show top 5 customers" | en | `[{"name": "Acme", "revenue": 50000}, ...]` | "Found 5 customers. Here are the top customers by revenue: 1. Acme ($50,000), 2. ..." |
| "הראה את 5 הלקוחות המובילים" | he | `[{"name": "Acme", "revenue": 50000}, ...]` | "נמצאו 5 לקוחות. הנה הלקוחות המובילים לפי הכנסות: 1. Acme ($50,000), 2. ..." |

**For blocked queries (production)**:
```
English: "This UPDATE operation is not allowed in production. Only SELECT queries are permitted in the production environment for safety."

Hebrew: "פעולת UPDATE זו אינה מותרת בסביבת ייצור. רק שאילתות SELECT מותרות בסביבת הייצור למען הבטיחות."
```

#### 2.11 Update Database with Final Result

**If execution succeeded**:
```sql
UPDATE sql_queue
SET
  status = 'completed',
  query_results = '<results_as_jsonb>',
  rows_affected = <number_of_rows>,
  execution_time_ms = <execution_time>,
  natural_language_response = '<generated_response>',
  executed_at = NOW(),
  completed_at = NOW(),
  total_processing_time_ms = EXTRACT(EPOCH FROM (NOW() - created_at)) * 1000
WHERE job_id = '<job_id>'::uuid;
```

**If execution failed or was blocked**:
```sql
UPDATE sql_queue
SET
  status = 'failed',
  error_message = '<error_description>',
  error_type = '<error_type>',  -- 'environment_restriction', 'sql_error', 'execution_error', etc.
  natural_language_response = '<error_response_in_user_language>',
  completed_at = NOW(),
  total_processing_time_ms = EXTRACT(EPOCH FROM (NOW() - created_at)) * 1000
WHERE job_id = '<job_id>'::uuid;
```

---

### Step 3: Report Summary to User

After processing all requests, provide a summary:

```
Processed 10 requests:
- ✅ 7 completed successfully
- ❌ 2 blocked (production restrictions)
- ⚠️  1 failed (SQL error)

Details:
1. Job abc123: "How many companies..." → Completed (47 results)
2. Job def456: "כמה חברות..." → Completed (47 results)
3. Job ghi789: "Update all customers..." → Blocked (production)
...
```

---

## Special Cases

### Case 1: Complex JOIN Queries

**Question**: "Show customers with their total order values"

**Analysis**:
- Need to join `customers` and `orders` tables
- Aggregate order values per customer
- Group by customer

**SQL**:
```sql
SELECT
  c.customer_name,
  SUM(o.total_amount) as total_order_value
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.customer_name
ORDER BY total_order_value DESC;
```

**Response (English)**:
"Found 150 customers with their order totals. Here are the top customers: 1. Acme Corp ($125,000), 2. TechStart ($98,500), ..."

**Response (Hebrew)**:
"נמצאו 150 לקוחות עם סכומי ההזמנות שלהם. הנה הלקוחות המובילים: 1. Acme Corp ($125,000), 2. TechStart ($98,500), ..."

### Case 2: Date Range Queries

**Question**: "Show sales from last week"

**SQL**:
```sql
SELECT *
FROM sales
WHERE sale_date >= DATEADD(week, -1, GETDATE())
  AND sale_date < GETDATE()
ORDER BY sale_date DESC;
```

### Case 3: Ambiguous Questions

If the question is unclear or missing information:

**Update database**:
```sql
UPDATE sql_queue
SET
  status = 'failed',
  error_message = 'Question is ambiguous or missing information',
  error_type = 'ambiguous_question',
  natural_language_response = CASE
    WHEN language = 'he' THEN 'השאילתה אינה ברורה. אנא פרט יותר.'
    ELSE 'The question is unclear. Please provide more details.'
  END
WHERE job_id = '<job_id>'::uuid;
```

### Case 4: Schema Mismatch

If the question references tables/columns that don't exist:

**Update database**:
```sql
UPDATE sql_queue
SET
  status = 'failed',
  error_message = 'Referenced table or column does not exist in schema',
  error_type = 'schema_mismatch',
  natural_language_response = CASE
    WHEN language = 'he' THEN 'הטבלה או העמודה שצוינו אינם קיימים במסד הנתונים.'
    ELSE 'The specified table or column does not exist in the database.'
  END
WHERE job_id = '<job_id>'::uuid;
```

---

## Environment-Specific Behavior

### DevTest Environment (environment = 'devtest')

**Allowed**:
- ✅ READ (SELECT)
- ✅ WRITE_SAFE (INSERT, UPDATE with WHERE, DELETE with WHERE)
- ✅ WRITE_RISKY (UPDATE/DELETE without WHERE)
- ✅ ADMIN (CREATE, DROP, ALTER)

**Restrictions**:
- None (all operations allowed)

**Example**:
```
Question: "Delete all test data"
SQL: "DELETE FROM test_data"
Classification: WRITE_RISKY
Environment: devtest
Execution: ✅ ALLOWED
```

### Production Environment (environment = 'prod')

**Allowed**:
- ✅ READ (SELECT only)

**Blocked**:
- ❌ WRITE_SAFE
- ❌ WRITE_RISKY
- ❌ ADMIN

**Example**:
```
Question: "Delete all test data"
SQL: "DELETE FROM test_data"
Classification: WRITE_RISKY
Environment: prod
Execution: ❌ BLOCKED
Response: "This operation is not allowed in production. Only SELECT queries are permitted."
```

---

## Error Handling

### SQL Execution Errors

If SQL execution fails (syntax error, permission error, etc.):

```sql
UPDATE sql_queue
SET
  status = 'failed',
  error_message = '<actual_error_from_database>',
  error_type = 'sql_execution_error',
  natural_language_response = CASE
    WHEN language = 'he' THEN 'אירעה שגיאה בביצוע השאילתה: <translated_error>'
    ELSE 'An error occurred while executing the query: <error>'
  END,
  completed_at = NOW()
WHERE job_id = '<job_id>'::uuid;
```

### Connection Errors

If database connection fails:

```sql
UPDATE sql_queue
SET
  status = 'failed',
  error_message = 'Database connection failed',
  error_type = 'connection_error',
  natural_language_response = CASE
    WHEN language = 'he' THEN 'נכשלה התחברות למסד הנתונים. אנא נסה שוב מאוחר יותר.'
    ELSE 'Failed to connect to database. Please try again later.'
  END,
  completed_at = NOW()
WHERE job_id = '<job_id>'::uuid;
```

---

## Performance Guidelines

### Batch Processing

Process requests in batches of 10-20 to avoid overwhelming the system.

```sql
-- Fetch in batches
SELECT * FROM sql_queue WHERE status = 'pending' ORDER BY created_at ASC LIMIT 10;
```

### Timeout Handling

If a query takes too long (>30 seconds in prod, >60 in devtest):
- Cancel the query
- Mark as failed with timeout error

### Result Size Limits

- Production: Maximum 1000 rows
- DevTest: Maximum 10000 rows

If results exceed limit:
```
Response: "Found 5,000 results (showing first 1,000). To see all results, please refine your query."
```

---

## Quality Checks

Before updating the database with results, verify:

1. ✅ SQL is syntactically correct
2. ✅ Query type classification is accurate
3. ✅ Environment restrictions are enforced
4. ✅ Natural language response is in correct language
5. ✅ Results are properly formatted as JSONB
6. ✅ All required fields are populated

---

## Monitoring

After processing, the user can check:

**Queue status**:
```sql
SELECT * FROM queue_stats;
```

**Recent failures**:
```sql
SELECT job_id, question, error_message, error_type
FROM sql_queue
WHERE status = 'failed'
ORDER BY created_at DESC
LIMIT 10;
```

**Performance metrics**:
```sql
SELECT
  AVG(total_processing_time_ms) as avg_processing_ms,
  MAX(total_processing_time_ms) as max_processing_ms,
  MIN(total_processing_time_ms) as min_processing_ms
FROM sql_queue
WHERE status = 'completed'
  AND created_at > NOW() - INTERVAL '24 hours';
```

---

## Quick Reference Commands

### Check pending count:
```sql
SELECT COUNT(*) FROM sql_queue WHERE status = 'pending';
```

### Get oldest pending request:
```sql
SELECT job_id, question, EXTRACT(EPOCH FROM (NOW() - created_at))/60 as age_minutes
FROM sql_queue
WHERE status = 'pending'
ORDER BY created_at ASC
LIMIT 1;
```

### Mark stuck requests as failed:
```sql
UPDATE sql_queue
SET
  status = 'failed',
  error_message = 'Processing timeout',
  error_type = 'timeout'
WHERE status = 'processing'
  AND sql_generated_at < NOW() - INTERVAL '10 minutes';
```

---

## Example Processing Session

**User**: "Process SQL queue"

**Claude Code**:
```
Checking queue...
Found 3 pending requests. Processing now...

1. Job abc-123 (English): "How many companies joined last month?"
   → Generated SQL: SELECT COUNT(*) FROM companies WHERE created_date >= DATEADD(month, -1, GETDATE())
   → Query type: READ, Risk: low
   → Environment: devtest ✅
   → Executed: 47 results
   → Response: "Found 47 companies that joined last month."
   ✅ Completed

2. Job def-456 (Hebrew): "כמה חברות הצטרפו בחודש שעבר?"
   → Generated SQL: SELECT COUNT(*) FROM companies WHERE created_date >= DATEADD(month, -1, GETDATE())
   → Query type: READ, Risk: low
   → Environment: prod ✅
   → Executed: 47 results
   → Response: "נמצאו 47 חברות שהצטרפו בחודש שעבר."
   ✅ Completed

3. Job ghi-789 (English): "Delete all test customers"
   → Generated SQL: DELETE FROM customers WHERE customer_name LIKE '%test%'
   → Query type: WRITE_SAFE, Risk: medium
   → Environment: prod ❌ BLOCKED
   → Response: "This operation is not allowed in production. Only SELECT queries are permitted."
   ❌ Blocked

Processing complete!
✅ 2 successful
❌ 1 blocked (production restriction)
```

---

## Troubleshooting

### "No MCP postgres tool available"
- Check claude_desktop_config.json
- Ensure postgres MCP server is configured

### "Cannot connect to database"
- Verify database credentials in .env file
- Check if PostgreSQL is running
- Test connection manually

### "Hebrew text not displaying correctly"
- Ensure database encoding is UTF-8
- Check terminal encoding
- Verify unicode support

---

## Summary Checklist

When processing requests, ensure:
- [ ] Fetch pending from database
- [ ] Generate correct SQL
- [ ] Classify query type accurately
- [ ] Check environment restrictions
- [ ] Execute only if allowed
- [ ] Generate response in correct language
- [ ] Update database with results
- [ ] Provide summary to user

---

**Ready to process!** When the user asks, follow this guide step-by-step.
