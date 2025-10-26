# ⚡ Text-to-SQL Teams Bot - Quick Reference

## 🚀 Start System (Every Day)

```bash
# Terminal 1: Start services
cd C:\Users\gals\text-to-sql-app
startup.bat

# Terminal 2: Start ngrok
ngrok http 8000
```

**That's it!** System is running.

---

## 💬 Using in Teams

### Ask Questions Naturally

```
"How many customers joined last month?"
"Show top 10 orders by revenue"
"What's the average order value?"
```

### Bot Commands

| Command | What it does |
|---------|--------------|
| `/help` | Show help |
| `/status` | Queue status |
| `/history` | Your queries |
| `/schema` | Database tables |
| `/examples` | Example questions |

---

## 🔄 Process Queue (When User Asks Question)

```bash
# You see: "User asked question in Teams"
# You run:
python process_queue.py

# Bot in Teams will show results!
```

---

## 📊 Check Queue Status

```bash
# Quick check
python -c "import psycopg2; conn=psycopg2.connect('dbname=text_to_sql_queue user=postgres password=postgres'); cur=conn.cursor(); cur.execute('SELECT COUNT(*) FROM sql_queue WHERE status=\'pending\''); print(f'Pending: {cur.fetchone()[0]}')"

# OR connect to database
psql -U postgres -d text_to_sql_queue -c "SELECT * FROM queue_stats;"
```

---

## 🛑 Stop System

```bash
shutdown.bat
```

---

## 🐛 Quick Fixes

### Bot not responding?
```bash
# Check if services running
docker ps
curl http://localhost:8000/health
```

### Restart everything
```bash
shutdown.bat
# Wait 10 seconds
startup.bat
```

### View logs
```bash
tail -f logs/fastapi.log
```

---

## 🔗 Important URLs

- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Teams Endpoint**: /api/messages
- **Health**: http://localhost:8000/health

---

## 📞 Database Info

**PostgreSQL (Queue):**
- Host: localhost:5432
- DB: text_to_sql_queue
- User: postgres
- Pass: postgres

**SQL Server (Target):**
- Host: localhost:1433
- User: sa
- Pass: YourStrong@Password123

---

## 🎯 Complete Flow

```
User in Teams → Message → ngrok → FastAPI
→ Queue DB → Claude Code (you!) → SQL
→ Execute → Results → User sees via /history
```

---

## 💡 Pro Tips

1. Keep ngrok and FastAPI running always
2. Process queue when you see notifications
3. Use `/status` to check if queries pending
4. Test locally first with Bot Framework Emulator
5. Hebrew and English both work automatically!

---

## 🆘 Emergency Contacts

- FastAPI docs: http://localhost:8000/docs
- Bot Framework: https://dev.botframework.com
- Full guide: TEAMS_INTEGRATION_GUIDE.md

---

**🎉 You're the AI! Process queries and make magic happen! ✨**
