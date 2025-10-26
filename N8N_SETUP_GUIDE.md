# n8n Setup Guide for Text-to-SQL with Claude Code

## Overview

This guide will help you set up n8n as the bridge between your FastAPI Text-to-SQL application and Claude Code for processing natural language queries in both English and Hebrew.

---

## Prerequisites

✅ Node.js 18+ installed
✅ PostgreSQL or SQLite installed (for queue database)
✅ Text-to-SQL FastAPI app running
✅ Database schema created (`database/schema.sql`)

---

## Installation Options

### Option 1: Quick Start with npx (Recommended for Testing)

```bash
# Start n8n directly (no installation needed)
npx n8n

# Opens at: http://localhost:5678
```

**Pros**: No installation, quick to test
**Cons**: Needs to run npx every time

---

### Option 2: Global Installation (Recommended for Development)

```bash
# Install n8n globally
npm install -g n8n

# Start n8n
n8n

# Opens at: http://localhost:5678
```

**Pros**: Install once, faster startup
**Cons**: ~500MB disk space

---

### Option 3: Docker (Recommended for Production)

```bash
# Create docker-compose.yml (see below)
docker-compose up -d n8n

# Access at: http://localhost:5678
```

**Pros**: Isolated, production-ready, persistent data
**Cons**: Requires Docker Desktop

---

## Docker Compose Setup (Production)

Create `docker-compose.yml` in your project root:

```yaml
version: '3.8'

services:
  # PostgreSQL for n8n and sql_queue
  postgres:
    image: postgres:16-alpine
    container_name: text-to-sql-postgres
    environment:
      POSTGRES_DB: text_to_sql_queue
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: your_secure_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/schema.sql:/docker-entrypoint-initdb.d/001-schema.sql
    restart: unless-stopped

  # n8n Workflow Automation
  n8n:
    image: n8nio/n8n:latest
    container_name: text-to-sql-n8n
    ports:
      - "5678:5678"
    environment:
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=n8n
      - DB_POSTGRESDB_USER=postgres
      - DB_POSTGRESDB_PASSWORD=your_secure_password
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=changeme
      - WEBHOOK_URL=http://localhost:5678/
      - GENERIC_TIMEZONE=Asia/Jerusalem
    volumes:
      - n8n_data:/home/node/.n8n
      - ./n8n-workflows:/workflows
    depends_on:
      - postgres
    restart: unless-stopped

  # FastAPI Text-to-SQL App
  text-to-sql-api:
    build: .
    container_name: text-to-sql-api
    ports:
      - "8000:8000"
    environment:
      - DEPLOYMENT_ENVIRONMENT=${ENV:-devtest}
      - N8N_WEBHOOK_URL=http://n8n:5678/webhook/nl-query
      - N8N_STATUS_URL=http://n8n:5678/webhook/nl-status
      - QUEUE_DB_HOST=postgres
      - QUEUE_DB_PORT=5432
      - QUEUE_DB_NAME=text_to_sql_queue
      - QUEUE_DB_USER=postgres
      - QUEUE_DB_PASSWORD=your_secure_password
    env_file:
      - .env.${ENV:-devtest}
    depends_on:
      - postgres
      - n8n
    restart: unless-stopped

volumes:
  postgres_data:
  n8n_data:
```

**Start the full stack:**
```bash
# DevTest environment
ENV=devtest docker-compose up -d

# Production environment
ENV=prod docker-compose up -d
```

---

## Initial Setup Steps

### Step 1: Start n8n

```bash
# Option 1: npx
npx n8n

# Option 2: Global install
n8n

# Option 3: Docker
docker-compose up -d n8n
```

**Expected output:**
```
n8n ready on port 5678
Version: 1.116.2

Editor is now accessible via:
http://localhost:5678/
```

###Step 2: Create n8n Account

1. Open http://localhost:5678
2. Create your account (stored locally)
3. Set up your workspace

### Step 3: Configure Database Connection

1. Go to **Settings** → **Credentials**
2. Click **Add Credential**
3. Search for "Postgres"
4. Fill in:
   - **Name**: `sql_queue_db`
   - **Host**: `localhost` (or `postgres` if using Docker)
   - **Port**: `5432`
   - **Database**: `text_to_sql_queue`
   - **User**: `postgres`
   - **Password**: (your postgres password)
5. Click **Test Connection** → Should succeed
6. Click **Save**

### Step 4: Create Database Schema

**If not using Docker init script**, run manually:

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE text_to_sql_queue;

# Connect to it
\c text_to_sql_queue

# Run schema
\i database/schema.sql

# Verify tables created
\dt

# Should show: sql_queue, sql_audit_log
```

---

## Importing Workflows

### Method 1: Import from Files

I've created 3 workflow JSON files in `n8n-workflows/`:
1. `receive_question.json` - Receives natural language questions
2. `check_status.json` - Checks processing status
3. `list_pending.json` - Lists pending requests for Claude Code

**To import**:
1. Click **Workflows** → **Add Workflow**
2. Click **⋮** (menu) → **Import from File**
3. Select workflow JSON file
4. Click **Save**
5. Click **Activate** (toggle in top right)

Repeat for all 3 workflows.

---

### Method 2: Create Manually (if import doesn't work)

See detailed steps in next section.

---

## Workflow 1: Receive Natural Language Question

**Purpose**: Receives question from FastAPI, stores in database, returns job_id

**Endpoint**: `POST http://localhost:5678/webhook/nl-query`

**Nodes**:

### 1. Webhook Node
- **Type**: Webhook
- **HTTP Method**: POST
- **Path**: `nl-query`
- **Response Mode**: "Using 'Respond to Webhook' Node"

### 2. Set Environment Info
- **Type**: Set
- **Values**:
  - `environment`: `{{$env.DEPLOYMENT_ENVIRONMENT || "devtest"}}`
  - `question`: `{{$json.body.question}}`
  - `user_id`: `{{$json.body.user_id || "anonymous"}}`

### 3. Detect Language
- **Type**: Code
- **JavaScript**:
```javascript
const question = items[0].json.question;
const hebrewRegex = /[\u0590-\u05FF]/;
const language = hebrewRegex.test(question) ? 'he' : 'en';

return items.map(item => ({
  json: {
    ...item.json,
    language
  }
}));
```

### 4. Get Schema Info
- **Type**: Postgres
- **Operation**: Execute Query
- **Query**:
```sql
SELECT jsonb_build_object(
  'tables', json_agg(
    jsonb_build_object(
      'name', table_name,
      'columns', columns
    )
  )
) as schema_info
FROM information_schema.tables t
LEFT JOIN (
  SELECT table_name, json_agg(
    jsonb_build_object(
      'name', column_name,
      'type', data_type
    )
  ) as columns
  FROM information_schema.columns
  WHERE table_schema = 'public'
  GROUP BY table_name
) c ON t.table_name = c.table_name
WHERE t.table_schema = 'public'
  AND t.table_type = 'BASE TABLE';
```

### 5. Insert to Queue
- **Type**: Postgres
- **Operation**: Insert
- **Table**: `sql_queue`
- **Columns**:
  - `question`: `{{$json.question}}`
  - `schema_info`: `{{$json.schema_info}}`
  - `environment`: `{{$json.environment}}`
  - `language`: `{{$json.language}}`
  - `user_id`: `{{$json.user_id}}`
  - `status`: `'pending'`

### 6. Respond to Webhook
- **Type**: Respond to Webhook
- **Response Mode**: JSON
- **Response Body**:
```json
{
  "job_id": "{{$json.job_id}}",
  "status": "pending",
  "message": "{{$json.language === 'he' ? 'בקשתך התקבלה ומועברת לעיבוד' : 'Your request has been received and is being processed'}}",
  "estimated_wait_seconds": 300,
  "status_url": "http://localhost:5678/webhook/nl-status/{{$json.job_id}}"
}
```

---

## Workflow 2: Check Status

**Purpose**: Check processing status by job_id

**Endpoint**: `GET http://localhost:5678/webhook/nl-status/:job_id`

**Nodes**:

### 1. Webhook Node
- **Type**: Webhook
- **HTTP Method**: GET
- **Path**: `nl-status/:job_id`
- **Response Mode**: "Using 'Respond to Webhook' Node"

### 2. Get Status from DB
- **Type**: Postgres
- **Operation**: Execute Query
- **Query**:
```sql
SELECT
  job_id,
  status,
  question,
  sql_query,
  query_type,
  risk_level,
  execution_allowed,
  natural_language_response,
  error_message,
  created_at,
  completed_at,
  EXTRACT(EPOCH FROM (COALESCE(completed_at, NOW()) - created_at)) as processing_time_seconds
FROM sql_queue
WHERE job_id = '{{$json.params.job_id}}'::uuid;
```

### 3. Respond to Webhook
- **Type**: Respond to Webhook
- **Response Mode**: JSON
- **Response Body**:
```json
{
  "job_id": "{{$json.job_id}}",
  "status": "{{$json.status}}",
  "question": "{{$json.question}}",
  "answer": "{{$json.natural_language_response}}",
  "sql_executed": "{{$json.sql_query}}",
  "query_type": "{{$json.query_type}}",
  "risk_level": "{{$json.risk_level}}",
  "execution_allowed": "{{$json.execution_allowed}}",
  "error": "{{$json.error_message}}",
  "processing_time_seconds": "{{$json.processing_time_seconds}}"
}
```

---

## Workflow 3: List Pending Queries (for Claude Code)

**Purpose**: List all pending queries that need processing

**Endpoint**: `GET http://localhost:5678/webhook/pending-queries`

**Nodes**:

### 1. Webhook Node
- **Type**: Webhook
- **HTTP Method**: GET
- **Path**: `pending-queries`
- **Response Mode**: "Using 'Respond to Webhook' Node"

### 2. Get Pending from DB
- **Type**: Postgres
- **Operation**: Execute Query
- **Query**:
```sql
SELECT
  job_id,
  question,
  schema_info,
  environment,
  language,
  created_at,
  EXTRACT(EPOCH FROM (NOW() - created_at)) as age_seconds
FROM sql_queue
WHERE status = 'pending'
ORDER BY created_at ASC
LIMIT 50;
```

### 3. Respond to Webhook
- **Type**: Respond to Webhook
- **Response Mode**: JSON
- **Response Body**:
```json
{
  "total_pending": "{{$json.length}}",
  "requests": "{{$json}}",
  "oldest_age_seconds": "{{$json[0].age_seconds}}"
}
```

---

## Testing the Workflows

### Test 1: Submit Question (English)

```bash
curl -X POST http://localhost:5678/webhook/nl-query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How many companies joined in the past 3 months?",
    "user_id": "test_user"
  }'
```

**Expected Response**:
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "pending",
  "message": "Your request has been received and is being processed",
  "estimated_wait_seconds": 300,
  "status_url": "http://localhost:5678/webhook/nl-status/123e4567-e89b-12d3-a456-426614174000"
}
```

### Test 2: Submit Question (Hebrew)

```bash
curl -X POST http://localhost:5678/webhook/nl-query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "כמה חברות הצטרפו ב-3 החודשים האחרונים?",
    "user_id": "test_user"
  }'
```

**Expected Response**:
```json
{
  "job_id": "...",
  "status": "pending",
  "message": "בקשתך התקבלה ומועברת לעיבוד",
  ...
}
```

### Test 3: Check Status

```bash
curl -X GET http://localhost:5678/webhook/nl-status/123e4567-e89b-12d3-a456-426614174000
```

**Expected Response (before processing)**:
```json
{
  "job_id": "...",
  "status": "pending",
  "answer": null,
  "processing_time_seconds": 5.2
}
```

### Test 4: List Pending (for Claude Code)

```bash
curl -X GET http://localhost:5678/webhook/pending-queries
```

**Expected Response**:
```json
{
  "total_pending": 2,
  "requests": [
    {
      "job_id": "...",
      "question": "How many companies...",
      "language": "en",
      "environment": "devtest",
      "age_seconds": 12.5
    },
    ...
  ]
}
```

---

## Troubleshooting

### Issue: "Connection refused" to n8n

**Solution**:
```bash
# Check if n8n is running
ps aux | grep n8n

# If not, start it:
npx n8n
# or
n8n
```

### Issue: "Database connection failed"

**Solution**:
1. Verify PostgreSQL is running: `pg_isready`
2. Check credentials in n8n
3. Test connection manually:
```bash
psql -U postgres -h localhost -d text_to_sql_queue -c "SELECT 1;"
```

### Issue: "Table sql_queue does not exist"

**Solution**:
```bash
# Run schema creation
psql -U postgres -d text_to_sql_queue -f database/schema.sql
```

### Issue: "Webhook not found"

**Solution**:
1. Check workflow is **Activated** (toggle in top right)
2. Verify webhook path matches exactly
3. Check n8n logs for errors

### Issue: "Hebrew text showing as ???"

**Solution**:
1. Ensure database encoding is UTF-8:
```sql
SHOW SERVER_ENCODING;  -- Should be UTF8
```
2. Check Content-Type header in requests: `application/json; charset=utf-8`

---

## Monitoring and Maintenance

### View Queue Stats

```sql
SELECT * FROM queue_stats ORDER BY environment, status;
```

### Find Stuck Queries

```sql
SELECT job_id, question, status,
       EXTRACT(EPOCH FROM (NOW() - created_at))/60 as minutes_old
FROM sql_queue
WHERE status = 'processing'
  AND created_at < NOW() - INTERVAL '10 minutes';
```

### View Recent Activity

```sql
SELECT
    created_at,
    environment,
    language,
    status,
    LEFT(question, 50) as question_preview
FROM sql_queue
ORDER BY created_at DESC
LIMIT 20;
```

### Clear Old Completed Requests

```sql
DELETE FROM sql_queue
WHERE status IN ('completed', 'failed')
AND completed_at < NOW() - INTERVAL '30 days';
```

---

## Next Steps

After n8n is set up and workflows are running:

1. ✅ **Phase 1 Complete**: Infrastructure is ready
2. ⏭️ **Phase 3**: Create Claude Code processing guide
3. ⏭️ **Phase 4**: Create FastAPI client to call n8n webhooks
4. ⏭️ **Phase 5**: Implement language support
5. ⏭️ **Phase 6**: Add security and environment restrictions

---

## Quick Reference

### n8n URLs
- **UI**: http://localhost:5678
- **Submit Question**: POST http://localhost:5678/webhook/nl-query
- **Check Status**: GET http://localhost:5678/webhook/nl-status/:job_id
- **List Pending**: GET http://localhost:5678/webhook/pending-queries

### Database Tables
- **sql_queue**: Main queue table
- **sql_audit_log**: Audit trail
- **pending_queries**: View of pending requests
- **queue_stats**: Statistics view

### Common Commands
```bash
# Start n8n
npx n8n

# Check database
psql -U postgres -d text_to_sql_queue

# View pending count
psql -U postgres -d text_to_sql_queue -c "SELECT COUNT(*) FROM sql_queue WHERE status='pending';"

# Submit test question
curl -X POST http://localhost:5678/webhook/nl-query \
  -H "Content-Type: application/json" \
  -d '{"question": "test query"}'
```

---

**Ready to continue?** Once n8n is running and workflows are imported, we can move to Phase 3: Creating the Claude Code processing guide!
