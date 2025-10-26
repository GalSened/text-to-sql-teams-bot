# Text-to-SQL Queue Processing System

## Overview

This system processes natural language queries from a PostgreSQL queue, converts them to SQL, executes them (if allowed), and generates natural language responses in English or Hebrew.

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Client    │─────▶│ PostgreSQL   │◀────▶│ Claude Code │
│   (n8n)     │      │ Queue (sql_  │      │ Processor   │
└─────────────┘      │   queue)     │      └─────────────┘
                     └──────────────┘             │
                                                  ▼
                                         ┌─────────────┐
                                         │ SQL Server  │
                                         │ (Target DB) │
                                         └─────────────┘
```

## Files Created

### 1. `process_queue.py`
Main queue processor that:
- Fetches pending requests from PostgreSQL
- Generates SQL queries (currently uses simple pattern matching)
- Classifies queries by type and risk
- Executes queries (respecting environment restrictions)
- Generates natural language responses
- Updates database with results

### 2. `setup_database.py`
Database initialization script that:
- Creates database schema (tables, indexes, views)
- Adds sample test data
- Verifies setup

### 3. `docker-compose-with-queue.yml`
Enhanced Docker Compose with PostgreSQL queue database

## Quick Start

### Step 1: Start PostgreSQL Database

**Option A: Using Docker (Recommended)**

```bash
# Wait for Docker Desktop to start (check system tray)
# Then run:
cd text-to-sql-app
docker-compose -f docker-compose-with-queue.yml up -d queue-db

# Wait for database to be ready (about 10-15 seconds)
docker-compose -f docker-compose-with-queue.yml logs -f queue-db
```

**Option B: Using Local PostgreSQL**

If you have PostgreSQL installed locally:
- Ensure it's running on port 5432
- Create database: `createdb text_to_sql_queue`
- Update `.env.devtest` with your credentials

### Step 2: Initialize Database

```bash
python setup_database.py
```

This will:
- Create the `sql_queue` table and related objects
- Add 7 sample test requests (English and Hebrew)
- Verify the setup

Expected output:
```
============================================================
SQL Queue Database Setup
============================================================
🔌 Connecting to database...
✅ Connected successfully

📝 Creating database schema...
✅ Schema created successfully

📥 Adding sample test requests...
   ✓ Added request 1: How many companies joined in the past 3 months?...
   ✓ Added request 2: Show top 10 customers by revenue...
   ...

✅ Added 7 sample requests

📊 Queue Status:
   Environment | Language | Count
   -----------------------------------
   devtest     | en       |     4
   devtest     | he       |     3
   prod        | he       |     1

🔍 Verifying setup...
✅ Database setup verified
   - sql_queue table exists
   - 8 pending requests

============================================================
✅ Setup completed successfully!
============================================================
```

### Step 3: Process the Queue

```bash
python process_queue.py
```

This will:
- Connect to the queue database
- Fetch pending requests
- Process each one (generate SQL, classify, execute)
- Update database with results
- Show summary

Expected output:
```
============================================================
SQL Queue Processor - DEVTEST Environment
============================================================

🔌 Connecting to databases...
   ✅ Connected to queue database
   ⚠️  Target database not available - will process but not execute

📥 Fetching pending requests (batch size: 10)...
   Found 8 pending request(s)

============================================================
Processing Job: abc-123-...
Question (en): How many companies joined in the past 3 months?
📝 Generating SQL...
   SQL: SELECT COUNT(*) as company_count FROM companies WHERE created_date >= DATEADD(month, -3, GETDATE())
🏷️  Type: READ, Risk: low
⚙️  Executing SQL...
✅ Success: 47 rows
💬 Response: Found 47 results.

============================================================
Processing Job: def-456-...
Question (he): כמה חברות הצטרפו ב-3 החודשים האחרונים?
📝 Generating SQL...
   SQL: SELECT COUNT(*) as company_count FROM companies WHERE created_date >= DATEADD(month, -3, GETDATE())
🏷️  Type: READ, Risk: low
⚙️  Executing SQL...
✅ Success: 47 rows
💬 Response: נמצאו 47 תוצאות.

...

============================================================
SUMMARY
============================================================
✅ Completed: 7
🚫 Blocked: 0
❌ Failed: 1
============================================================
```

## Understanding the Process

### Query Flow

1. **Client submits request** → Creates row in `sql_queue` with status='pending'
2. **Processor fetches pending** → Gets oldest pending requests
3. **Generate SQL** → Converts natural language to SQL
4. **Classify query** → Determines type (READ/WRITE/ADMIN) and risk level
5. **Check restrictions** → Production only allows READ queries
6. **Execute (if allowed)** → Runs query on target database
7. **Generate response** → Creates natural language response in same language as question
8. **Update database** → Sets status='completed' or 'failed' with results

### Environment Restrictions

#### DevTest Environment
- ✅ READ queries: Allowed
- ✅ WRITE_SAFE queries: Allowed
- ✅ WRITE_RISKY queries: Allowed
- ✅ ADMIN queries: Allowed

#### Production Environment
- ✅ READ queries: Allowed
- ❌ WRITE queries: **BLOCKED**
- ❌ ADMIN queries: **BLOCKED**

### Query Classification

| SQL Pattern | Type | Risk | Example |
|------------|------|------|---------|
| SELECT | READ | low-medium | `SELECT * FROM customers` |
| INSERT, UPDATE/DELETE with WHERE | WRITE_SAFE | medium | `UPDATE customers SET status='active' WHERE id=1` |
| UPDATE/DELETE without WHERE | WRITE_RISKY | high | `DELETE FROM old_data` |
| CREATE, DROP, ALTER | ADMIN | critical | `DROP TABLE test` |

### Multilingual Support

The system supports **English** and **Hebrew**:

- Questions can be in either language
- SQL is language-agnostic (same SQL for same question)
- Responses are generated in the **same language as the question**

**Example:**

| Question | Language | SQL | Response |
|----------|----------|-----|----------|
| "How many companies joined?" | en | `SELECT COUNT(*) ...` | "Found 47 companies..." |
| "כמה חברות הצטרפו?" | he | `SELECT COUNT(*) ...` | "נמצאו 47 חברות..." |

## Database Schema

### Main Table: `sql_queue`

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL | Primary key |
| `job_id` | UUID | Unique job identifier |
| `question` | TEXT | Natural language question |
| `schema_info` | JSONB | Database schema context |
| `environment` | VARCHAR | 'devtest' or 'prod' |
| `language` | VARCHAR | 'en' or 'he' |
| `status` | VARCHAR | 'pending', 'processing', 'completed', 'failed' |
| `sql_query` | TEXT | Generated SQL |
| `query_type` | VARCHAR | 'READ', 'WRITE_SAFE', 'WRITE_RISKY', 'ADMIN' |
| `risk_level` | VARCHAR | 'low', 'medium', 'high', 'critical' |
| `execution_allowed` | BOOLEAN | Whether execution was allowed |
| `query_results` | JSONB | Results from execution |
| `rows_affected` | INTEGER | Number of rows affected |
| `natural_language_response` | TEXT | Response in user's language |
| `error_message` | TEXT | Error details if failed |
| ... | ... | Various timestamps |

### Views

- **`pending_queries`**: Quick view of pending requests
- **`queue_stats`**: Statistics by environment and status

### Audit Table: `sql_audit_log`

Automatically tracks all queue events for compliance.

## Monitoring

### Check Queue Status

```sql
-- PostgreSQL
psql -U postgres -d text_to_sql_queue

-- View stats
SELECT * FROM queue_stats;

-- View pending
SELECT * FROM pending_queries;

-- Recent completions
SELECT job_id, question, status, natural_language_response
FROM sql_queue
WHERE completed_at > NOW() - INTERVAL '1 hour'
ORDER BY completed_at DESC;
```

### Check from Python

```python
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='text_to_sql_queue',
    user='postgres',
    password='postgres'
)

cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM sql_queue WHERE status='pending'")
print(f"Pending: {cursor.fetchone()[0]}")
```

## Troubleshooting

### Issue: "Connection refused" error

**Problem:** PostgreSQL is not running

**Solution:**
```bash
# Check Docker
docker ps

# Start queue database
docker-compose -f docker-compose-with-queue.yml up -d queue-db

# Check logs
docker-compose -f docker-compose-with-queue.yml logs queue-db
```

### Issue: "Table does not exist"

**Problem:** Database not initialized

**Solution:**
```bash
python setup_database.py
```

### Issue: "Target database not available"

**Problem:** SQL Server connection failed

**Note:** This is expected if you don't have a SQL Server running. The processor will still:
- Generate SQL
- Classify queries
- Update the queue
- But mark queries as "failed" with connection error

To fix:
1. Start SQL Server or configure connection in `.env.devtest`
2. Ensure SQL Server allows remote connections

### Issue: SQL generation is too simple

**Current State:** The `generate_sql()` function uses basic pattern matching

**To Enhance:** Integrate with OpenAI or Claude:

```python
def generate_sql(self, question: str, schema_info: Dict) -> str:
    """Generate SQL using AI"""
    # Import AI client
    from app.core.openai_client import OpenAIClient

    client = OpenAIClient()
    sql = client.generate_sql_from_question(question, schema_info)
    return sql
```

## Next Steps

### 1. Enhance SQL Generation

Replace simple pattern matching with actual AI:
- Use OpenAI GPT-4 for SQL generation
- Or use Claude via Anthropic API
- Add schema-aware prompt engineering

### 2. Connect to Real Target Database

Update `.env.devtest` with your SQL Server credentials:
```env
DB_SERVER=your_server
DB_NAME=your_database
DB_USER=your_user
DB_PASSWORD=your_password
```

### 3. Set Up n8n Integration

Create n8n workflows to:
- Submit questions to the queue
- Poll for results
- Send responses back to users

### 4. Add Web Interface

Create a simple FastAPI endpoint:
```python
@app.post("/query/submit")
async def submit_query(question: str, language: str = "en"):
    """Submit a new query to the queue"""
    # Insert into sql_queue
    # Return job_id
```

### 5. Add Scheduled Processing

Run the processor on a schedule:
```bash
# Cron (Linux/Mac)
*/5 * * * * cd /path/to/text-to-sql-app && python process_queue.py

# Task Scheduler (Windows)
# Create task that runs process_queue.py every 5 minutes
```

## Integration with Claude Code

When you say **"Process SQL queue"** or **"Handle pending queries"**, Claude Code will:

1. Run `python process_queue.py`
2. Show you the results
3. Provide summary statistics
4. Alert if there are failures

You can also check specific requests:
```sql
-- Find failed requests
SELECT job_id, question, error_message
FROM sql_queue
WHERE status = 'failed'
ORDER BY created_at DESC
LIMIT 5;
```

## Configuration

### Environment Variables (`.env.devtest`)

Key settings:
```env
# Environment
DEPLOYMENT_ENVIRONMENT=devtest  # or 'prod'

# Queue Database
QUEUE_DB_HOST=localhost
QUEUE_DB_PORT=5432
QUEUE_DB_NAME=text_to_sql_queue
QUEUE_DB_USER=postgres
QUEUE_DB_PASSWORD=postgres

# Target Database (SQL Server)
DB_SERVER=localhost
DB_NAME=TestDB
DB_USER=sa
DB_PASSWORD=YourPassword123!

# Batch Processing
BATCH_PROCESSING_SIZE=10  # Process 10 at a time

# Language
DEFAULT_LANGUAGE=en
SUPPORTED_LANGUAGES=en,he
```

## Testing

### Add a test request manually

```sql
INSERT INTO sql_queue (
    job_id,
    question,
    schema_info,
    environment,
    language,
    status
)
VALUES (
    gen_random_uuid(),
    'How many orders were placed today?',
    '{"tables": [{"name": "orders", "columns": [...]}]}'::jsonb,
    'devtest',
    'en',
    'pending'
);
```

Then run:
```bash
python process_queue.py
```

### Test with Hebrew

```sql
INSERT INTO sql_queue (
    job_id,
    question,
    schema_info,
    environment,
    language,
    status
)
VALUES (
    gen_random_uuid(),
    'כמה הזמנות התקבלו היום?',
    '{"tables": [{"name": "orders", "columns": [...]}]}'::jsonb,
    'devtest',
    'he',
    'pending'
);
```

## Support

For questions or issues:
1. Check this README
2. Review `CLAUDE_CODE_PROCESSING_GUIDE.md`
3. Check logs: `logs/devtest.log`
4. Review database audit log: `SELECT * FROM sql_audit_log`

---

**Ready to process!** 🚀

When Docker is ready, run:
```bash
docker-compose -f docker-compose-with-queue.yml up -d queue-db
sleep 15
python setup_database.py
python process_queue.py
```
