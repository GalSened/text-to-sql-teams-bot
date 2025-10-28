# SQL Bot - Quick Usage Guide

**Status:** ✅ Fully functional with Claude CLI integration

---

## 🚀 Quick Start

### Start the Server

```powershell
cd C:\Users\gals\text-to-sql-app
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Test It Works

```powershell
# Health check
Invoke-RestMethod -Uri "http://localhost:8000/health"

# Simple test
python test_hebrew_direct.py

# Comprehensive test
python test_comprehensive.py
```

---

## 💬 Example Queries

### ✅ Simple Queries (Fast - Pattern Matching)

**English:**
- "How many companies are in the system?"
- "List all contacts"
- "Show documents from last month"
- "Count all companies"

**Hebrew:**
- "כמה חברות יש במערכת?"
- "הצג את כל אנשי הקשר"
- "כמה מסמכים יש במערכת?"

**Response Time:** < 100ms
**Cost:** $0.00
**Method:** pattern_matching

---

### 🧠 Complex Queries (Smart - Claude CLI)

**English:**
- "Which companies have the most documents?"
- "Show me companies with more than 5 active users"
- "List documents that haven't been signed yet"
- "Which users have sent the most documents?"

**Hebrew:**
- "אילו חברות יש להן הכי הרבה מסמכים?"
- "הראה לי חברות עם יותר מ-5 משתמשים פעילים"

**Response Time:** ~10-15 seconds
**Cost:** $0.00 (local Claude CLI)
**Method:** claude_cli

---

## 📡 API Usage

### Python

```python
import requests

# Simple query
response = requests.post(
    "http://localhost:8000/query/ask",
    json={"question": "How many companies are in the system?"}
)

result = response.json()
print(f"SQL: {result['sql']}")
print(f"Method: {result['explanation']}")
```

### PowerShell

```powershell
$body = @{
    question = "כמה חברות יש במערכת?"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/query/ask" `
    -Method Post -Body $body -ContentType "application/json; charset=utf-8"

Write-Host "SQL: $($response.sql)"
```

### cURL

```bash
curl -X POST "http://localhost:8000/query/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "How many companies are in the system?"}'
```

---

## 🔍 Available Endpoints

### Health Check
```
GET /health
```

### Ask Question (Main endpoint)
```
POST /query/ask
Body: {"question": "your question here"}
```

### Get Schema
```
GET /schema
```

### Refresh Schema Cache
```
POST /schema/refresh
```

---

## 🎯 Pattern Matching Coverage

The bot can handle these patterns **instantly** without AI:

| Pattern | English Keywords | Hebrew Keywords |
|---------|-----------------|-----------------|
| COUNT | how many, count | כמה, ספור, מספר |
| SUM | total, sum | סכום, סה"כ |
| AVERAGE | average, mean | ממוצע |
| SELECT | list, show, get | רשימה, הצג, הראה |
| RECENT | recent, last, latest | אחרונים, לאחרונה |
| GROUP | by, group, per | לפי, קבוצה |

### Supported Tables

English/Hebrew mappings:
- companies / חברות → `Companies`
- contacts / אנשי קשר → `Contacts`
- documents / מסמכים → `Documents`
- groups / קבוצות → `Groups`

---

## ⚙️ Configuration

### Environment Variables (.env)

```env
# AI Configuration (Claude CLI - no keys needed!)
USE_CLAUDE_CLI=true
CLAUDE_CLI_COMMAND=claude

# Database (WeSign)
DB_SERVER=DEVTEST\SQLEXPRESS
DB_NAME=WeSign
DB_USER=sa
DB_PASSWORD=Aa123456

# Application
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=true
```

---

## 🐛 Troubleshooting

### "Claude CLI not found"

Check if claude command works:
```powershell
claude --version
```

If not found, install Claude Desktop or add to PATH.

### "Could not understand the question"

The query is too complex for patterns. This triggers Claude CLI fallback automatically. Wait 10-15 seconds for AI response.

### "Database connection failed"

Check SQL Server is running:
```powershell
# Check SQL Server service
Get-Service -Name "MSSQL*"

# Test connection
sqlcmd -S "DEVTEST\SQLEXPRESS" -U sa -P Aa123456 -Q "SELECT @@VERSION"
```

### Hebrew text showing as ???

Make sure you're using UTF-8 encoding:
```python
# Python - use proper encoding
response = requests.post(url, json={"question": question},
    headers={"Content-Type": "application/json; charset=utf-8"})

# PowerShell - set output encoding
$OutputEncoding = [System.Text.Encoding]::UTF8
```

---

## 📊 Performance Tips

### For Best Performance

1. **Use simple patterns when possible**
   - "How many X" instead of "Give me the count of X"
   - "List Y" instead of "Show me all the Y records"

2. **Be specific with table names**
   - ✅ "How many companies?"
   - ❌ "How many records in the database?"

3. **Avoid unnecessary complexity**
   - If patterns work, no need for complex phrasing

### When to Use Complex Queries

Save AI-powered queries for when you need:
- JOINs across multiple tables
- Complex WHERE conditions
- Subqueries
- Window functions
- CTEs (Common Table Expressions)

---

## 🎓 Examples by Use Case

### Reporting Queries

```python
questions = [
    "How many companies joined last month?",      # Time-based filter
    "List the top 10 companies by document count", # Ranking
    "Show me documents that are unsigned",         # Status filter
]
```

### Analytics Queries

```python
questions = [
    "Which companies have the most documents?",           # Complex JOIN
    "Show me users who haven't signed any documents",     # Negative filter
    "List companies with more than 5 active documents",   # Aggregation
]
```

### Bilingual Support

```python
# Same query, different language
questions = [
    "How many companies are in the system?",  # English
    "כמה חברות יש במערכת?",                  # Hebrew
]

# Both return identical SQL:
# SELECT COUNT(*) as count FROM Companies
```

---

## 🔒 Security Notes

- ✅ READ-only queries executed automatically
- ⚠️ WRITE queries require explicit confirmation
- 🛡️ Query validation before execution
- 🔍 Automatic risk level assessment
- 📝 Full audit trail in logs

---

## 📞 Support

**Logs:** `text-to-sql-app/logs/app.log`

**Tests:**
- `test_comprehensive.py` - Full test suite
- `test_hebrew_direct.py` - Hebrew pattern matching
- `test_claude_simple.py` - Claude CLI fallback

**Documentation:**
- `CLAUDE_CLI_INTEGRATION_COMPLETE.md` - Implementation details
- `FIXES_APPLIED_CLAUDE_CLI.md` - Change history
- This file - Usage guide

---

**Ready to use! No API keys required!** 🎉
