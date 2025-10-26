# 📋 Deployment Checklist - Text-to-SQL Teams Bot

## Pre-Deployment Checklist

### Prerequisites ✅
- [ ] Windows 10/11 installed
- [ ] Docker Desktop installed and running
- [ ] Python 3.12 installed
- [ ] Git installed
- [ ] ngrok installed (`choco install ngrok`)
- [ ] Bot Framework Emulator downloaded (optional)

**Run: `check_prerequisites.bat` to verify**

---

## Phase 1: Environment Setup

### ngrok Configuration ✅
- [ ] Created free ngrok account at https://dashboard.ngrok.com/signup
- [ ] Copied authtoken from dashboard
- [ ] Configured authtoken: `ngrok config add-authtoken YOUR_TOKEN`
- [ ] (Optional) Created static domain from ngrok dashboard
- [ ] Tested ngrok: `ngrok http 8000`

**Run: `setup_ngrok.bat` for guided setup**

### Python Dependencies ✅
- [ ] Installed all requirements: `pip install -r requirements.txt`
- [ ] Verified installation: `python -c "import fastapi, botbuilder.core, psycopg2"`

---

## Phase 2: Database Setup

### PostgreSQL Initialization ✅
- [ ] Started PostgreSQL container:
  ```bash
  docker run -d --name postgres-queue -p 5432:5432 \
    -e POSTGRES_PASSWORD=postgres \
    -e POSTGRES_DB=text_to_sql_queue \
    postgres:16-alpine
  ```
- [ ] Waited 10 seconds for initialization
- [ ] Ran database setup: `python setup_database.py`
- [ ] Verified schema: Sample requests added successfully
- [ ] Tested connection:
  ```bash
  python -c "import psycopg2; psycopg2.connect('dbname=text_to_sql_queue user=postgres password=postgres host=localhost').close()"
  ```

**Expected output**: "✅ Schema created successfully", "✅ Added 7 sample requests"

---

## Phase 3: Service Startup

### Start All Services ✅
- [ ] Started services: `startup.bat`
- [ ] Verified PostgreSQL running: `docker ps | find "postgres-queue"`
- [ ] Verified SQL Server running (if needed): `docker ps | find "sqlserver-target"`
- [ ] Verified Redis running: `docker ps | find "redis"`
- [ ] Verified FastAPI responding: `curl http://localhost:8000/health`
- [ ] Checked API docs: Opened http://localhost:8000/docs in browser

### Start ngrok Tunnel ✅
- [ ] Opened NEW terminal window
- [ ] Started ngrok: `ngrok http 8000` (or with static domain)
- [ ] Copied "Forwarding" URL (e.g., https://abc123.ngrok-free.app)
- [ ] Kept ngrok terminal open
- [ ] Tested ngrok: `curl https://YOUR_NGROK_URL/health`

**Run: `diagnose.bat` to check all services**

---

## Phase 4: Local Testing (Optional)

### Bot Framework Emulator ✅
- [ ] Opened Bot Framework Emulator
- [ ] Connected to: `http://localhost:8000/api/messages`
- [ ] Left App ID and Password empty
- [ ] Sent test message: "hello"
- [ ] Received welcome message from bot
- [ ] Tested commands:
  - [ ] `/help` - Received help card
  - [ ] `/status` - Received queue status
  - [ ] `/examples` - Received example questions
  - [ ] `/history` - Received query history (empty initially)

### Question Processing Test ✅
- [ ] Sent question: "How many customers joined last month?"
- [ ] Received "✅ Query Submitted" response with Job ID
- [ ] Ran queue processor: `python process_queue.py`
- [ ] Saw successful processing in console
- [ ] Sent `/history` command
- [ ] Saw completed query with results

**Run: `python test_bot_locally.py` for automated testing**

---

## Phase 5: Teams App Package

### Icon Creation ✅
- [ ] Created color.png (192x192 pixels)
  - Options: Canva, Flaticon, or custom design
  - Theme: Database/SQL related
- [ ] Created outline.png (32x32 pixels, transparent background)
- [ ] Saved both icons to: `teams-app-manifest/` folder
- [ ] Verified file sizes and formats

### Package Creation ✅
- [ ] Reviewed manifest.json in `teams-app-manifest/`
- [ ] Updated validDomains if needed (for static ngrok domain)
- [ ] Created ZIP file:
  - Selected: manifest.json, color.png, outline.png
  - Right-click → "Send to > Compressed folder"
  - Named: TextToSQL.zip
- [ ] Verified ZIP contains all 3 files
- [ ] (Optional) Validated at https://dev.teams.microsoft.com/appvalidation.html

---

## Phase 6: Teams Installation

### Upload to Teams ✅
- [ ] Opened Microsoft Teams (desktop or web)
- [ ] Clicked "Apps" in left sidebar
- [ ] Clicked "Manage your apps" (bottom left)
- [ ] Clicked "Upload a custom app"
- [ ] Selected "Upload for me or my teams"
- [ ] Chose `teams-app-manifest/TextToSQL.zip`
- [ ] Clicked "Add"
- [ ] Bot appeared in Teams apps list

### First Conversation ✅
- [ ] Clicked on bot to open chat
- [ ] Received welcome message
- [ ] Bot commands visible in compose box
- [ ] Sent test message: "hello"
- [ ] Received appropriate response

**If permission error**: Contact Teams admin for custom app upload permission

---

## Phase 7: End-to-End Testing

### Command Testing ✅
- [ ] `/help` - Received help card with examples
- [ ] `/status` - Received queue statistics
- [ ] `/examples` - Received EN/HE examples
- [ ] `/schema` - Received database schema info
- [ ] `/history` - Received query history

### English Question Flow ✅
- [ ] Sent: "How many customers joined last month?"
- [ ] Received: "✅ Query Submitted" with Job ID and status
- [ ] Ran: `python process_queue.py`
- [ ] Processor showed successful execution
- [ ] Sent: `/history`
- [ ] Saw completed query with results

### Hebrew Question Flow ✅
- [ ] Sent: "כמה לקוחות הצטרפו בחודש שעבר?"
- [ ] Bot responded in Hebrew
- [ ] Query submitted successfully
- [ ] Ran: `python process_queue.py`
- [ ] Hebrew response generated
- [ ] Verified in `/history`

### Error Handling ✅
- [ ] Sent invalid command: `/invalid`
- [ ] Received helpful error message
- [ ] Sent gibberish: "asdfasdf"
- [ ] Bot provided helpful guidance

---

## Phase 8: Production Configuration

### Environment Configuration ✅
- [ ] Reviewed `.env.devtest` settings
- [ ] Configured target database connection (if needed)
- [ ] Set `DEPLOYMENT_ENVIRONMENT=devtest` for testing
- [ ] (For prod) Created `.env.prod` with `DEPLOYMENT_ENVIRONMENT=prod`
- [ ] Tested database connections

### Static ngrok Domain ✅
- [ ] Got free static domain from ngrok dashboard
- [ ] Updated startup script to use static domain
- [ ] Updated Teams manifest validDomains
- [ ] Tested with static domain: `ngrok http 8000 --domain=YOUR_DOMAIN`
- [ ] Verified URL doesn't change on restart

### Monitoring Setup ✅
- [ ] Configured log rotation (optional)
- [ ] Set up desktop notifications (optional)
- [ ] Created monitoring dashboard (optional)
- [ ] Documented logging locations

---

## Phase 9: Daily Operations

### Desktop Shortcuts ✅
- [ ] "Start Teams Bot.bat" created on desktop
- [ ] "Process SQL Queue.bat" created on desktop
- [ ] "Start ngrok.bat" created (if using static domain)
- [ ] Tested all shortcuts work correctly

### Documentation ✅
- [ ] Shared QUICK_REFERENCE.md with team
- [ ] Explained bot commands to users
- [ ] Demonstrated `/help` and `/examples`
- [ ] Explained users get results via `/history`
- [ ] Created internal team guide (optional)

### Daily Workflow Test ✅
- [ ] Double-clicked "Start Teams Bot.bat"
- [ ] All services started successfully
- [ ] Started ngrok (manually or via shortcut)
- [ ] User asked question in Teams
- [ ] Ran "Process SQL Queue.bat"
- [ ] User saw results via `/history`
- [ ] Graceful shutdown: `shutdown.bat`

---

## Phase 10: Validation & Sign-Off

### System Health Check ✅
- [ ] All Docker containers running: `docker ps`
- [ ] FastAPI responding: `curl http://localhost:8000/health`
- [ ] Database accessible: Check with diagnose.bat
- [ ] ngrok tunnel active: Check ngrok terminal
- [ ] Teams bot responding: Test with `/help`
- [ ] Queue processing working: Test end-to-end

**Run: `diagnose.bat` for comprehensive health check**

### Performance Validation ✅
- [ ] Query submitted in < 2 seconds
- [ ] Bot responses appear immediately
- [ ] Queue processing completes in reasonable time
- [ ] No error messages in logs
- [ ] System stable over 1 hour

### Security Validation ✅
- [ ] Environment restrictions working (devtest vs prod)
- [ ] Query classification accurate (READ/WRITE/ADMIN)
- [ ] No SQL injection vulnerabilities
- [ ] User tracking operational
- [ ] Audit logging functioning

### Documentation Review ✅
- [ ] QUICK_REFERENCE.md up to date
- [ ] TEAMS_INTEGRATION_GUIDE.md accurate
- [ ] IMPLEMENTATION_SUMMARY.md complete
- [ ] All helper scripts working
- [ ] Comments added where needed

---

## Post-Deployment

### User Training ✅
- [ ] Demonstrated bot to team
- [ ] Showed example questions
- [ ] Explained available commands
- [ ] Shared tips and best practices
- [ ] Answered user questions

### Monitoring Plan ✅
- [ ] Scheduled queue processing frequency
- [ ] Set up alert notifications (optional)
- [ ] Defined SLA for query responses
- [ ] Created escalation procedure
- [ ] Documented troubleshooting steps

### Maintenance Schedule ✅
- [ ] Weekly: Review logs for errors
- [ ] Monthly: Update dependencies
- [ ] Quarterly: Review and optimize queries
- [ ] As needed: Add new features

---

## Success Criteria ✅

All these should be true:

- ✅ Teams bot responds to all commands
- ✅ English and Hebrew questions work
- ✅ Queue processing generates SQL
- ✅ Users see results via /history
- ✅ System starts with one command
- ✅ Graceful shutdown works
- ✅ All documentation accurate
- ✅ Zero monthly costs
- ✅ Team trained and using bot
- ✅ Monitoring in place

---

## Rollback Procedure

If anything goes wrong:

```bash
# Stop everything
shutdown.bat

# Remove all containers
docker rm -f postgres-queue sqlserver-target redis

# Remove data
docker volume rm pgdata

# Start fresh from Phase 2
```

---

## Support Resources

- **Local Docs**: QUICK_REFERENCE.md, TEAMS_INTEGRATION_GUIDE.md
- **API Docs**: http://localhost:8000/docs
- **Diagnostics**: `diagnose.bat`
- **Testing**: `python test_bot_locally.py`
- **Bot Framework**: https://dev.botframework.com
- **Teams Dev**: https://dev.teams.microsoft.com
- **ngrok Docs**: https://ngrok.com/docs

---

## Troubleshooting Quick Reference

| Issue | Fix |
|-------|-----|
| Bot not responding | Run `diagnose.bat`, check services |
| Database error | `docker restart postgres-queue` |
| ngrok down | Restart: `ngrok http 8000` |
| Can't install in Teams | Check manifest, contact admin |
| Queue not processing | Verify DB connection, check logs |

---

## Sign-Off

- [ ] All checklist items completed
- [ ] System tested end-to-end
- [ ] Users trained and satisfied
- [ ] Documentation reviewed
- [ ] Monitoring operational
- [ ] Ready for production use!

**Deployment Date**: ___________

**Deployed By**: ___________

**Sign-Off**: ___________

---

**🎉 Congratulations! Your FREE Teams Text-to-SQL Bot is deployed!**

**Monthly Cost**: $0
**Value Delivered**: $500-800/month equivalent
**Users Supported**: Unlimited
**Queries Processed**: As many as you can handle!
