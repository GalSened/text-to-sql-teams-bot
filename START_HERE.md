# 🚀 START HERE - Text-to-SQL Teams Bot

## Welcome! 👋

You're about to deploy a **completely FREE** Microsoft Teams bot that lets your team query databases using natural language!

**What you're getting:**
- 💰 **$0/month** (vs $500-800/month for cloud solutions)
- 🤖 **Microsoft Teams integration**
- 🌍 **English + Hebrew support**
- 🔒 **Production-ready security**
- 📊 **Full audit trail**
- ⚡ **Fast and responsive**

---

## ⏱️ Time Commitment

- **First-time setup**: 30-40 minutes
- **Daily startup**: 2 minutes
- **Per query**: 30 seconds (manual processing)

---

## 🎯 Quick Start Path

Choose your approach:

### Option 1: Automated Wizard (Recommended) ⭐
**Best for**: First-time users, want step-by-step guidance

```bash
deploy_step_by_step.bat
```

This interactive wizard will:
- ✅ Check all prerequisites
- ✅ Initialize database
- ✅ Start all services
- ✅ Set up ngrok
- ✅ Guide through Teams installation
- ✅ Run end-to-end tests
- ✅ Create desktop shortcuts

**Just run it and follow the prompts!**

---

### Option 2: Manual Step-by-Step
**Best for**: Want to understand each step, prefer control

#### Step 1: Check Prerequisites (2 min)
```bash
check_prerequisites.bat
```

**Fix any issues before proceeding!**

#### Step 2: Set Up ngrok (5 min)
```bash
setup_ngrok.bat
```

- Creates free account
- Configures authtoken
- Optionally sets up static domain

#### Step 3: Initialize Database (2 min)
```bash
# Start PostgreSQL
docker run -d --name postgres-queue -p 5432:5432 ^
  -e POSTGRES_PASSWORD=postgres ^
  -e POSTGRES_DB=text_to_sql_queue ^
  postgres:16-alpine

# Wait for startup
timeout 10

# Initialize schema
python setup_database.py
```

#### Step 4: Start Services (1 min)
```bash
startup.bat
```

#### Step 5: Start ngrok (1 min)
```bash
# In a NEW terminal
ngrok http 8000

# Copy the Forwarding URL!
```

#### Step 6: Test Locally (Optional) (5 min)
```bash
python test_bot_locally.py
```

#### Step 7: Create Teams Package (5 min)
1. Add icons to `teams-app-manifest/` folder
   - color.png (192x192)
   - outline.png (32x32)
2. Zip: manifest.json + icons
3. Name: TextToSQL.zip

#### Step 8: Install in Teams (2 min)
1. Teams → Apps → Manage your apps
2. Upload a custom app
3. Select TextToSQL.zip
4. Add to Teams

#### Step 9: Test End-to-End (5 min)
1. Ask question in Teams
2. Run: `python process_queue.py`
3. Check results: `/history`

**Done! 🎉**

---

### Option 3: Quick Install (Experienced Users)
**Best for**: Know what you're doing, want speed

```bash
# 1. Prerequisites
check_prerequisites.bat

# 2. Database
docker run -d --name postgres-queue -p 5432:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=text_to_sql_queue postgres:16-alpine
timeout 10
python setup_database.py

# 3. Services
startup.bat

# 4. ngrok (separate terminal)
ngrok http 8000

# 5. Test
python test_bot_locally.py

# 6. Create Teams package and install
# (Follow Teams installation in docs)
```

---

## 📚 Documentation Guide

**Start with these** (in order):

1. **START_HERE.md** (this file) - Where to begin
2. **DEPLOYMENT_CHECKLIST.md** - Complete checklist for deployment
3. **QUICK_REFERENCE.md** - One-page cheat sheet for daily use
4. **TEAMS_INTEGRATION_GUIDE.md** - Complete setup guide with examples
5. **IMPLEMENTATION_SUMMARY.md** - Technical details and architecture

**Reference these as needed:**

- **CLAUDE_CODE_PROCESSING_GUIDE.md** - How to process queries
- **QUEUE_PROCESSING_README.md** - Queue system details

---

## 🛠️ Helper Scripts Reference

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `deploy_step_by_step.bat` | Interactive wizard | First deployment |
| `check_prerequisites.bat` | Verify tools installed | Before starting |
| `setup_ngrok.bat` | Configure ngrok | One-time setup |
| `startup.bat` | Start all services | Every day |
| `shutdown.bat` | Stop all services | When done |
| `diagnose.bat` | Check system health | Troubleshooting |
| `test_bot_locally.py` | Test bot without Teams | Before Teams install |
| `process_queue.py` | Process user queries | When users ask questions |

---

## 🎯 Your First 5 Minutes

Let's get you up and running right now!

```bash
# 1. Check if you have everything (30 seconds)
check_prerequisites.bat

# 2. If all green, deploy! (or fix issues first)
deploy_step_by_step.bat
```

That's it! The wizard handles everything else.

---

## 💬 What You'll Be Able to Do

Once deployed, users can:

**In Teams chat with your bot:**

```
User: How many customers joined last month?
Bot:  ✅ Query submitted, processing...

[You run: python process_queue.py]

User: /history
Bot:  📝 Your Recent Queries
      1. How many customers joined last month?
         Status: completed | Results: Found 47 customers
```

**Commands:**
- `/help` - Show help and examples
- `/status` - Check queue status
- `/history` - View your queries
- `/schema` - See database tables
- `/examples` - Example questions

**Languages:**
- English: "How many orders were placed today?"
- Hebrew: "כמה הזמנות בוצעו היום?"

---

## 🏗️ Architecture Overview

```
Teams User → ngrok (FREE tunnel) → FastAPI (localhost:8000)
  ↓
PostgreSQL Queue (Docker)
  ↓
You (Claude Code) run: python process_queue.py
  ↓
Generate SQL → Execute → Update Results
  ↓
User sees results via /history
```

**All running on your computer. Zero cloud costs. Forever. 🎉**

---

## 🆘 Getting Help

### Something not working?

1. **Run diagnostics:**
   ```bash
   diagnose.bat
   ```

2. **Check specific issue:**
   - Bot not responding → Check FastAPI: `curl http://localhost:8000/health`
   - Database error → Restart: `docker restart postgres-queue`
   - ngrok down → Restart: `ngrok http 8000`

3. **Complete restart:**
   ```bash
   shutdown.bat
   # Wait 10 seconds
   startup.bat
   # Restart ngrok in separate terminal
   ```

### Documentation Lookup

| Question | Check |
|----------|-------|
| How do I start the system? | QUICK_REFERENCE.md |
| How do I install in Teams? | TEAMS_INTEGRATION_GUIDE.md |
| What commands does bot support? | IMPLEMENTATION_SUMMARY.md |
| How do I process queries? | CLAUDE_CODE_PROCESSING_GUIDE.md |
| Is my system healthy? | Run `diagnose.bat` |
| How do I test locally? | Run `python test_bot_locally.py` |

---

## 🎓 Learning Path

**Level 1: Get it running** (30 min)
- Run `deploy_step_by_step.bat`
- Follow wizard to completion
- Test with one question

**Level 2: Daily operations** (10 min)
- Practice start/stop: `startup.bat` / `shutdown.bat`
- Process queue: `python process_queue.py`
- Test commands in Teams

**Level 3: Understand architecture** (20 min)
- Read IMPLEMENTATION_SUMMARY.md
- Review app/bots/teams_bot.py
- Understand queue flow

**Level 4: Customize** (Variable)
- Add your database schema
- Modify bot responses
- Add custom commands
- Enhance SQL generation

---

## 🚀 Next Steps After Reading This

Choose your path:

**Path A: Let's Go!** (Ready to deploy)
```bash
deploy_step_by_step.bat
```

**Path B: Learn More First** (Want to understand)
1. Read IMPLEMENTATION_SUMMARY.md
2. Review TEAMS_INTEGRATION_GUIDE.md
3. Then run `deploy_step_by_step.bat`

**Path C: Just Test First** (Cautious approach)
1. Run `check_prerequisites.bat`
2. Run `python setup_database.py`
3. Run `python test_bot_locally.py`
4. When confident, run `deploy_step_by_step.bat`

---

## ✅ Success Looks Like...

After deployment, you should have:

- ✅ Teams bot responding to messages
- ✅ Commands working (`/help`, `/status`, `/history`)
- ✅ English + Hebrew questions working
- ✅ Queue processing generating SQL
- ✅ Users seeing results
- ✅ Desktop shortcuts for easy startup
- ✅ System starts in 2 minutes
- ✅ **Zero monthly costs** 💰

---

## 💡 Pro Tips

1. **Get ngrok static domain** (free!) - URL stays same on restart
2. **Create desktop shortcuts** - Done automatically by wizard
3. **Test locally first** - Use Bot Framework Emulator
4. **Keep ngrok running** - Don't close that terminal!
5. **Process queue regularly** - Users expect fast responses
6. **Share `/help` with team** - Teach them the commands

---

## 🎉 Ready?

Pick your starting point and go! You're 30-40 minutes away from having a fully functional, **FREE**, Teams-integrated database query bot.

**Recommended for most users:**

```bash
deploy_step_by_step.bat
```

**See you on the other side! 🚀**

---

**Questions?**
- Check TEAMS_INTEGRATION_GUIDE.md (500+ lines of help)
- Run `diagnose.bat` (system health check)
- Read QUICK_REFERENCE.md (one-page guide)

**Let's build something amazing! 💪**
