# Quick Start Guide - Text-to-SQL Teams Bot

## 🚀 Get Started in 3 Steps

### 1. Start All Services (1 minute)

**Windows (PowerShell):**
```powershell
cd C:\Users\gals\text-to-sql-app
.\start-all-services.ps1
```

This will automatically:
- ✅ Start PostgreSQL queue database
- ✅ Start FastAPI server (port 8000)
- ✅ Start background worker service
- ✅ Optionally start ngrok tunnel (for Teams)

---

### 2. Test Locally - No Teams Required (1 minute)

```bash
python test_bot_locally.py
```

This tests the bot without needing Teams or ngrok. Try asking:
- "How many companies are in the system?"
- "כמה חברות יש במערכת?" (Hebrew)

---

### 3. Connect to Microsoft Teams (Optional - 10 minutes)

Follow **TEAMS_SETUP_GUIDE.md** for detailed steps:
1. Register bot with Azure Bot Service
2. Get App ID and Password
3. Update `.env` with credentials
4. Create "ask the DB" chat in Teams
5. Add bot to chat

---

## Example Queries

### English Queries
```
How many companies are in the system?
List all contacts
Show documents from last month
Top 10 companies
Count documents by status
```

### Hebrew Queries (עברית)
```
כמה חברות יש במערכת?
רשום את כל אנשי הקשר
הצג מסמכים מהחודש שעבר
10 החברות המובילות
ספור מסמכים לפי סטטוס
```

---

## Bot Commands

| Command | Description |
|---------|-------------|
| `help` or `עזרה` | Show help message |
| `status` | System status and queue info |
| `examples` or `דוגמאות` | Example queries |
| `schema` | Database schema |
| `history` | Your query history |
| `clear` | Clear history |

---

## System Status Checks

```powershell
# Check FastAPI is running
curl http://localhost:8000/health

# Check background worker
tasklist | findstr python

# Check PostgreSQL queue
docker ps | grep postgres-queue

# View live logs
Get-Content logs\orchestrator.log -Tail 50 -Wait
```

---

## WeSign Database Tables

The bot can query these WeSign tables:
- **Companies** - Company information
- **Contacts** - Contact records
- **Documents** - Document records
- **DocumentCollections** - Document collections
- **ActiveDirectoryConfigurations** - AD configs
- **Groups** - Group information
- **Logs** - System logs

---

## Stop All Services

```powershell
.\stop-all-services.ps1
```

Or close the PowerShell windows manually (FastAPI, Worker, ngrok).

---

## Documentation Files

| File | Purpose |
|------|---------|
| **QUICK_START.md** | This file - get started quickly |
| **TEAMS_SETUP_GUIDE.md** | Detailed Teams integration (Azure, ngrok, etc.) |
| **BILINGUAL_TESTING_PLAN.md** | Complete testing plan (English + Hebrew) |

---

## Troubleshooting

### Bot Not Responding

**Check Services:**
```powershell
# 1. FastAPI health
curl http://localhost:8000/health

# 2. Worker logs
Get-Content logs\orchestrator.log -Tail 50

# 3. Queue database
docker exec -it postgres-queue psql -U postgres -d text_to_sql_queue -c "SELECT * FROM sql_queue ORDER BY created_at DESC LIMIT 5;"
```

### Worker Not Processing Queries

1. Check worker window for errors
2. Restart: `.\start-all-services.ps1`
3. Verify database connection in `.env`

### Teams Not Receiving Messages

1. Check ngrok is running (copy URL from ngrok window)
2. Update Azure Bot messaging endpoint with latest ngrok URL
3. Verify `MICROSOFT_APP_ID` and `MICROSOFT_APP_PASSWORD` in `.env`
4. Check Teams channel enabled in Azure Bot

---

## Architecture Overview

```
Microsoft Teams
      ↓
   ngrok tunnel (public HTTPS)
      ↓
FastAPI Server (localhost:8000)
      ↓
PostgreSQL Queue (localhost:5433)
      ↓
Background Worker (polls every 5s)
      ↓
SQL Generator (pattern-based)
      ↓
WeSign Database (DEVTEST\SQLEXPRESS)
      ↓
Results → Teams Message
```

---

## Next Steps

1. ✅ **Local Testing**: Run `python test_bot_locally.py`
2. ⏳ **Teams Setup**: Follow `TEAMS_SETUP_GUIDE.md`
3. ⏳ **Full Testing**: Use `BILINGUAL_TESTING_PLAN.md`
4. ⏳ **Production**: See deployment checklist in TEAMS_SETUP_GUIDE.md

---

## Support & Logs

- **Logs:** `C:\Users\gals\text-to-sql-app\logs\orchestrator.log`
- **Config:** `.env` file (check credentials)
- **Teams Setup:** TEAMS_SETUP_GUIDE.md
- **Testing Plan:** BILINGUAL_TESTING_PLAN.md

---

**Ready to query WeSign database from Microsoft Teams!** 🚀
