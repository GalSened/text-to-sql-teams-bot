# 🚀 Teams Integration Setup Guide

## Complete FREE Text-to-SQL System with Microsoft Teams

This guide will help you set up the complete system to query databases using natural language through Microsoft Teams.

---

## 📋 Prerequisites

✅ **Already Have:**
- [x] Windows 10/11
- [x] Docker Desktop
- [x] Python 3.12
- [x] Git

✅ **Need to Install:**
- [ ] ngrok (for Teams connectivity)
- [ ] Bot Framework Emulator (for testing)

---

## 🎯 Quick Start (5 Minutes)

### Step 1: Install ngrok

```bash
# Install with Chocolatey
choco install ngrok

# OR download from https://ngrok.com/download
# Extract to C:\ngrok and add to PATH
```

**Create free ngrok account:**
1. Go to https://dashboard.ngrok.com/signup
2. Get your authtoken
3. Configure:
```bash
ngrok config add-authtoken YOUR_TOKEN_HERE
```

### Step 2: Initialize Database

```bash
cd text-to-sql-app

# Start PostgreSQL
docker run -d --name postgres-queue -p 5432:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=text_to_sql_queue postgres:16-alpine

# Wait 10 seconds for startup
timeout 10

# Initialize database with schema and sample data
python setup_database.py
```

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
✅ Added 7 sample requests
...
```

### Step 3: Start All Services

```bash
# Simple one-command startup
startup.bat
```

This will start:
- ✅ PostgreSQL (port 5432)
- ✅ SQL Server (port 1433)
- ✅ Redis (port 6379)
- ✅ FastAPI (port 8000)

### Step 4: Start ngrok Tunnel

**In a NEW terminal:**
```bash
ngrok http 8000
```

You'll see:
```
Session Status                online
Account                       your@email.com
Forwarding                    https://abc123.ngrok-free.app -> http://localhost:8000
```

✨ **Copy this URL** (https://abc123.ngrok-free.app) - you'll need it!

### Step 5: Test Locally (Optional)

**Option A: Bot Framework Emulator**
1. Download: https://github.com/Microsoft/BotFramework-Emulator/releases
2. Open emulator
3. Connect to: `http://localhost:8000/api/messages`
4. Start chatting!

**Option B: Test API directly**
```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/health/teams
```

### Step 6: Install in Teams

**Prepare App Package:**
1. Go to `teams-app-manifest/`
2. Add icons (color.png 192x192, outline.png 32x32)
   - Use https://www.canva.com to create simple database icons
   - Or use placeholders from internet
3. Zip the files:
   ```bash
   # In teams-app-manifest directory
   zip TextToSQL.zip manifest.json color.png outline.png
   ```

**Install in Teams:**
1. Open Microsoft Teams
2. Click **Apps** in left sidebar
3. Click **Manage your apps** (bottom left)
4. Click **Upload a custom app** → **Upload for me or my teams**
5. Select `TextToSQL.zip`
6. Click **Add**

**Start Chatting:**
```
You: How many customers joined last month?
Bot: ⏳ Processing your question...
Bot: ✅ Query Submitted
     📝 Note: Claude Code will process this query.
```

---

## 💬 How It Works

### The Complete Flow:

```
1. User asks question in Teams
   ↓
2. Teams sends message to ngrok URL
   ↓
3. ngrok tunnels to localhost:8000
   ↓
4. FastAPI receives message at /api/messages
   ↓
5. Bot handler processes message
   ↓
6. Question inserted into PostgreSQL queue
   ↓
7. Bot responds "Query submitted, processing..."
   ↓
8. Claude Code processes queue (YOU!)
   ↓
9. SQL generated, executed, results stored
   ↓
10. User checks results via bot commands
```

### Your Role as Claude Code:

When a user asks a question:

1. **User in Teams:** "How many companies joined last month?"

2. **Bot Response:** "✅ Query submitted, processing..."

3. **You (Claude Code) get notified** (desktop notification if configured)

4. **You run:**
   ```bash
   python process_queue.py
   ```

5. **Processing happens:**
   - Fetch pending request
   - Generate SQL: `SELECT COUNT(*) FROM companies WHERE created_date >= DATEADD(month, -1, GETDATE())`
   - Execute query
   - Generate response: "Found 47 companies that joined last month"
   - Update database

6. **User checks result:** "/history" command in Teams

---

## 🎨 Using the Bot

### Basic Usage

Just type your question naturally:
```
"How many orders were placed today?"
"Show top 10 customers by revenue"
"List active users from California"
```

### Commands

| Command | Description |
|---------|-------------|
| `/help` | Show help and examples |
| `/status` | Check queue status |
| `/history` | Your recent queries |
| `/schema` | View database tables |
| `/examples` | Example questions |

### Multilingual Support

**English:**
```
"How many customers joined last month?"
→ Found 47 customers that joined last month.
```

**Hebrew:**
```
"כמה לקוחות הצטרפו בחודש שעבר?"
→ נמצאו 47 לקוחות שהצטרפו בחודש שעבר.
```

The bot automatically detects language and responds accordingly!

---

## 🔄 Daily Operations

### Starting the System

```bash
# Start all services
startup.bat

# In another terminal, start ngrok
ngrok http 8000
```

### Processing Queries

**Manual (When you're available):**
```bash
python process_queue.py
```

**Check what's pending:**
```bash
python quick_check.py  # (we can create this)
```

**View results:**
- Use Teams bot `/status` and `/history` commands
- Or check database directly

### Monitoring

**Dashboard (if created):**
```
http://localhost:9000
```

**Check logs:**
```bash
tail -f logs/fastapi.log
tail -f logs/app.log
```

**Database queries:**
```sql
-- Connect to PostgreSQL
psql -U postgres -d text_to_sql_queue

-- Check queue
SELECT * FROM pending_queries;

-- View stats
SELECT * FROM queue_stats;
```

### Stopping the System

```bash
shutdown.bat
```

---

## 🔧 Configuration

### Environment Variables (.env.devtest)

```env
# Queue Database
QUEUE_DB_HOST=localhost
QUEUE_DB_PORT=5432
QUEUE_DB_NAME=text_to_sql_queue
QUEUE_DB_USER=postgres
QUEUE_DB_PASSWORD=postgres

# Target Database (SQL Server)
DB_SERVER=localhost
DB_PORT=1433
DB_NAME=TestDB
DB_USER=sa
DB_PASSWORD=YourStrong@Password123

# Environment
DEPLOYMENT_ENVIRONMENT=devtest  # or 'prod'

# Language
DEFAULT_LANGUAGE=en
SUPPORTED_LANGUAGES=en,he

# Teams Bot (leave empty for local dev)
MICROSOFT_APP_ID=
MICROSOFT_APP_PASSWORD=
```

### ngrok Configuration

For a permanent URL (free):
1. Sign up at https://ngrok.com
2. Get a static domain (free tier: 1 domain)
3. Use: `ngrok http 8000 --domain=your-static-domain.ngrok-free.app`

---

## 🎯 Advanced Features

### Auto-Processing (Future Enhancement)

Create a background watcher:
```python
# watcher.py
# Runs continuously
# Checks queue every 5 seconds
# Sends notification when new request arrives
# Can auto-process if configured
```

### Desktop Notifications

```python
from win10toast import ToastNotifier

toaster = ToastNotifier()
toaster.show_toast(
    "New SQL Query",
    "User asked: How many customers...",
    duration=10
)
```

### Proactive Messages

Send results back to Teams automatically:
```python
# After processing, send result to user
# Via Teams webhook or Bot Framework API
```

---

## 🐛 Troubleshooting

### Bot not responding in Teams

**Check:**
```bash
# 1. Is FastAPI running?
curl http://localhost:8000/health

# 2. Is ngrok running?
curl https://your-ngrok-url.ngrok.io/health

# 3. Check logs
tail -f logs/fastapi.log
```

### Can't install app in Teams

**Solutions:**
- Ensure you have permission to upload custom apps
- Check manifest.json is valid (use validator: https://dev.teams.microsoft.com/appvalidation.html)
- Verify icon files are correct size

### Database connection errors

```bash
# Check if PostgreSQL is running
docker ps | grep postgres-queue

# Check logs
docker logs postgres-queue

# Restart if needed
docker restart postgres-queue
```

### ngrok tunnel expired

**Free tier limitations:**
- Tunnel restarts when ngrok restarts
- URL changes each time (unless using static domain)

**Solution:**
- Get free static domain from ngrok dashboard
- Or just restart and update Teams manifest

---

## 📊 Example Session

**1. Start system:**
```bash
startup.bat
# In another terminal:
ngrok http 8000
```

**2. User in Teams:**
```
User: How many companies joined in Q1 2024?
Bot: ⏳ Processing your question...
Bot: ✅ Query Submitted
     Job ID: abc123
     Status: Pending
     📝 Note: Claude Code will process this query.
```

**3. You (Claude Code):**
```bash
# Check pending
python process_queue.py

Output:
============================================================
Processing Job: abc123
Question (en): How many companies joined in Q1 2024?
📝 Generating SQL...
   SQL: SELECT COUNT(*) FROM companies WHERE created_date BETWEEN '2024-01-01' AND '2024-03-31'
🏷️  Type: READ, Risk: low
⚙️  Executing SQL...
✅ Success: 127 rows
💬 Response: Found 127 companies that joined in Q1 2024.
============================================================
SUMMARY
✅ Completed: 1
============================================================
```

**4. User checks result:**
```
User: /history
Bot: 📝 Your Recent Queries

1. How many companies joined in Q1 2024?
   Status: completed | 2024-10-25 10:30
   Response: Found 127 companies that joined in Q1 2024.
```

---

## 🚀 Production Enhancements (Optional)

### 1. Scheduled Processing
```bash
# Windows Task Scheduler
# Run process_queue.py every 5 minutes
```

### 2. Real AI Integration
Instead of pattern matching, integrate real AI:
```python
# Use Anthropic Claude API (paid)
# Or keep using Claude Code (free!)
```

### 3. Enhanced Security
- Add user authentication
- Implement row-level security
- Add data masking for sensitive columns

### 4. Performance Optimization
- Add query caching
- Optimize database indexes
- Implement connection pooling

---

## 💰 Cost Breakdown

| Service | Cost |
|---------|------|
| Your Computer | $0 (already have) |
| Docker Desktop | $0 (free) |
| PostgreSQL | $0 (container) |
| SQL Server | $0 (developer edition) |
| Redis | $0 (container) |
| ngrok | $0 (free tier) |
| Teams | $0 (included with M365) |
| Claude Code (YOU!) | $0 (free) |
| **TOTAL** | **$0/month** 🎉 |

---

## 📚 Next Steps

1. ✅ **Get it running** - Follow Quick Start
2. ✅ **Test with Bot Emulator** - Verify locally
3. ✅ **Install in Teams** - Upload custom app
4. ✅ **Process some queries** - Run process_queue.py
5. 📈 **Add more features** - Desktop notifications, auto-processing
6. 🎨 **Customize** - Add your own database schema
7. 🚀 **Share with team** - Let others start asking questions!

---

## 🎉 You're Ready!

You now have a completely FREE, locally-hosted, Teams-integrated text-to-SQL system!

**Start asking database questions in Teams chat! 🚀**

Need help? Check:
- FastAPI docs: http://localhost:8000/docs
- Bot Framework: https://dev.botframework.com
- Teams Developer: https://dev.teams.microsoft.com

---

**Built with ❤️ using:**
- FastAPI
- Bot Framework SDK
- PostgreSQL
- Microsoft Teams
- Claude Code (YOU!)
