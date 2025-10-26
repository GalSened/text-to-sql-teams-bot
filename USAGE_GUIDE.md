# 🚀 How to Use Text-to-SQL Application

## Current Setup Status

✅ **Ready**: Configuration file created
⚠️ **Update Needed**: OpenAI API key and SQL Server details

---

## 🎯 3 Ways to Get Started

### 1️⃣ Interactive Setup (Recommended)

Run the configuration wizard:
```bash
cd text-to-sql-app
python configure.py
```

It will ask you for:
- OpenAI API key (get from https://platform.openai.com)
- SQL Server details (host, database, username, password)

Then it creates a complete `.env` file for you!

---

### 2️⃣ Manual Setup

Edit the `.env` file directly:
```bash
cd text-to-sql-app
notepad .env
```

**Update these lines**:
```env
OPENAI_API_KEY=your-actual-key-here
DB_SERVER=your-server-here
DB_NAME=your-database-here
DB_USER=your-username-here
DB_PASSWORD=your-password-here
```

---

### 3️⃣ Test Without Full Setup

You can test the **query classification system** without any database!

**Test query classifier**:
```bash
cd text-to-sql-app
python -c "
from app.core.query_classifier import query_classifier

# Test different queries
queries = [
    'SELECT * FROM customers',
    'DELETE FROM users WHERE inactive = 1',
    'DROP TABLE old_data',
]

for sql in queries:
    qtype, risk = query_classifier.classify_query(sql)
    print(f'{sql[:40]:40} -> Type: {qtype.value:12} Risk: {risk.value}')
"
```

---

## 📝 What Information You Need

### For OpenAI (Required for SQL Generation)
1. Go to https://platform.openai.com/api-keys
2. Sign in or create account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-proj-...`)
5. Paste in `.env` file

### For SQL Server (Required for Database Access)

**If you have SQL Server**:
- Server hostname (e.g., `localhost`, `192.168.1.100`)
- Database name (e.g., `Northwind`, `MyDatabase`)
- Username (e.g., `sa`, `dbuser`)
- Password

**Don't have SQL Server?** Quick options:

#### Option A: Docker (5 minutes)
```bash
docker run -e "ACCEPT_EULA=Y" -e "SA_PASSWORD=MyPass123!" -p 1433:1433 -d mcr.microsoft.com/mssql/server:2022-latest
```

Then use:
```env
DB_SERVER=localhost
DB_NAME=master
DB_USER=sa
DB_PASSWORD=MyPass123!
```

#### Option B: SQL Server Express (Free)
Download from: https://www.microsoft.com/en-us/sql-server/sql-server-downloads

#### Option C: Azure SQL (Free Tier)
https://azure.microsoft.com/en-us/free/

---

## ▶️ Starting the Application

### Step 1: Verify Configuration
```bash
cd text-to-sql-app
python test_basic.py
```

**Expected**: 6/6 tests pass ✅

### Step 2: Start the Server
```bash
uvicorn app.main:app --reload
```

**You'll see**:
```
INFO: Uvicorn running on http://0.0.0.0:8000
Starting Text-to-SQL Application v1.0.0
Database connection successful
Schema cache loaded
```

### Step 3: Open the API Documentation
Open your browser to: **http://localhost:8000/docs**

---

## 🎮 Using the Application

### Via Swagger UI (Web Interface)

1. Go to http://localhost:8000/docs
2. Click on any endpoint to expand it
3. Click **"Try it out"**
4. Enter your parameters
5. Click **"Execute"**
6. See the results!

### Example 1: Ask a Question

**Endpoint**: POST /query/ask

**Request**:
```json
{
  "question": "Show me all customers from New York",
  "execute_immediately": true
}
```

**Response**:
```json
{
  "query_id": "abc-123",
  "sql": "SELECT * FROM customers WHERE city = 'New York'",
  "query_type": "READ",
  "risk_level": "low",
  "explanation": "This query retrieves customers from New York",
  "requires_confirmation": false,
  "executed": true,
  "results": [
    {"id": 1, "name": "John Doe", "city": "New York"},
    {"id": 2, "name": "Jane Smith", "city": "New York"}
  ],
  "row_count": 2
}
```

### Example 2: Risky Operation (with Preview)

**Step 1 - Ask**:
```json
POST /query/ask
{
  "question": "Delete all inactive customers",
  "execute_immediately": false
}
```

**Step 2 - Preview**:
```
GET /query/preview/{query_id}
```
Shows you what will be deleted!

**Step 3 - Confirm & Execute**:
```json
POST /query/execute
{
  "query_id": "{query_id}",
  "confirmed": true
}
```

---

## 🔥 Quick Test Examples

### Test 1: Simple Query
```bash
curl -X POST http://localhost:8000/query/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How many tables are in the database?", "execute_immediately": true}'
```

### Test 2: Get Schema
```bash
curl http://localhost:8000/schema
```

### Test 3: Health Check
```bash
curl http://localhost:8000/health
```

### Test 4: Query History
```bash
curl http://localhost:8000/query/history
```

---

## 🎯 Natural Language Examples

Try these questions:

### Data Exploration
- "Show me all customers"
- "How many orders were placed last month?"
- "What are the top 5 products by sales?"
- "List all employees in the sales department"

### Filtering & Searching
- "Find customers from California"
- "Show orders over $1000"
- "Get products with low stock"

### Aggregations
- "What's the average order value?"
- "Count customers by country"
- "Sum total sales by month"

### Joins
- "Show customers with their recent orders"
- "List products and their categories"
- "Find orders with customer names"

### Updates (with confirmation)
- "Update customer email where ID is 123"
- "Set product status to inactive for old items"
- "Mark orders as shipped"

### Deletes (with preview + confirmation)
- "Delete test records"
- "Remove inactive users"
- "Clean up old logs"

---

## 🛡️ Safety Features in Action

### The System Protects You!

**READ queries** (Safe):
- ✅ Execute immediately (or ask for confirmation based on settings)
- 🔵 Risk: Low

**WRITE_SAFE queries** (Targeted writes):
- ⚠️ Require confirmation
- 🟡 Risk: Medium
- Examples: `UPDATE ... WHERE id = 123`

**WRITE_RISKY queries** (Bulk operations):
- 🛑 Show preview of affected rows
- ⚠️ Require explicit confirmation
- 🔴 Risk: High/Critical
- Examples: `DELETE FROM table` (no WHERE clause)

**ADMIN queries** (Schema changes):
- 🚫 Blocked by default
- 🔴 Risk: Critical
- Examples: `DROP TABLE`, `CREATE TABLE`

---

## 📊 Understanding the Response

Every query returns:

```json
{
  "query_id": "unique-id",           // For tracking
  "sql": "SELECT ...",                // Generated SQL
  "query_type": "READ",               // READ/WRITE_SAFE/WRITE_RISKY/ADMIN
  "risk_level": "low",                // low/medium/high/critical
  "explanation": "What this does",    // Plain English
  "requires_confirmation": false,     // Do you need to confirm?
  "executed": true,                   // Was it run?
  "results": [...],                   // The data (if executed)
  "row_count": 42                     // Number of rows
}
```

---

## ⚙️ Configuration Options

Edit `.env` to customize:

### Safety Settings
```env
# Require confirmation for all writes
REQUIRE_CONFIRMATION_FOR_WRITES=true

# Enable/disable DROP/CREATE/ALTER commands
ENABLE_ADMIN_OPERATIONS=false
```

### Performance Settings
```env
# Maximum rows to return
MAX_ROWS_RETURN=1000

# Query timeout in seconds
QUERY_TIMEOUT_SECONDS=30
```

### OpenAI Settings
```env
# Use cheaper model for testing
OPENAI_MODEL=gpt-3.5-turbo

# Or use more powerful model
OPENAI_MODEL=gpt-4
```

---

## 🔍 Troubleshooting

### "Database connection failed"
1. Check SQL Server is running
2. Verify credentials in `.env`
3. Test with SQL Server Management Studio
4. Check firewall allows port 1433

### "OpenAI API error"
1. Verify key at https://platform.openai.com/api-keys
2. Check credits/billing
3. Try cheaper model: `gpt-3.5-turbo`

### "Module import error"
```bash
cd text-to-sql-app
pip install -r requirements.txt
```

### "Port already in use"
```bash
# Use different port
uvicorn app.main:app --reload --port 8001
```

---

## 🎓 Advanced Usage

### Using Python Client
```python
import requests

# Ask a question
response = requests.post(
    "http://localhost:8000/query/ask",
    json={
        "question": "Show top 10 customers by sales",
        "execute_immediately": True
    }
)
result = response.json()
print(result['sql'])
print(result['results'])
```

### Batch Processing
```python
questions = [
    "How many customers?",
    "What's the total revenue?",
    "Show recent orders"
]

for q in questions:
    response = requests.post(
        "http://localhost:8000/query/ask",
        json={"question": q, "execute_immediately": True}
    )
    print(f"{q}: {response.json()['results']}")
```

---

## 📈 Performance Tips

1. **Schema caching**: First query loads schema, subsequent queries are faster
2. **Refresh schema**: If database changes, call `/schema/refresh`
3. **Limit results**: Set `MAX_ROWS_RETURN` appropriately
4. **Use indexes**: Ensure your database has proper indexes
5. **Monitor API costs**: OpenAI charges per token used

---

## 🎯 Next Steps

1. **Configure** your `.env` file
2. **Test** with `python test_basic.py`
3. **Start** the application
4. **Explore** the API at http://localhost:8000/docs
5. **Query** your database in plain English!

---

**Need help?** Check:
- `CONFIGURE_ME.md` - Configuration guide
- `TESTING_SUMMARY.md` - Detailed test results
- `TEST_PLAN.md` - Comprehensive testing
- http://localhost:8000/docs - Interactive API docs

**Ready to start?** Run: `python configure.py`
