# Microsoft Teams Integration Setup Guide
## "ask the DB" Chat Configuration

**Version:** 1.0
**System:** Text-to-SQL Application
**Last Updated:** 2025-10-26

---

## Prerequisites

✅ **Already Completed:**
- FastAPI server running on localhost:8000
- Worker service running and processing queue
- PostgreSQL queue database configured
- Teams bot code implemented (teams_bot.py)
- Bot endpoint configured (/api/messages)

⏳ **Still Needed:**
- Microsoft Azure account with Bot Service access
- Bot Framework registration
- Public endpoint (ngrok or Azure)
- Teams chat "ask the DB" created

---

## Setup Steps

### Step 1: Register Bot with Azure Bot Service

#### Option A: Using Azure Portal (Recommended)

1. **Navigate to Azure Portal**
   - Go to https://portal.azure.com
   - Sign in with your Microsoft account

2. **Create Azure Bot Resource**
   - Search for "Azure Bot" in the marketplace
   - Click "Create"
   - Fill in details:
     - **Bot handle:** `wesign-text-to-sql-bot` (unique name)
     - **Subscription:** Select your subscription
     - **Resource group:** Create new or use existing
     - **Pricing tier:** F0 (Free tier - 10,000 messages/month)
     - **Microsoft App ID:** Create new

3. **Generate App Password**
   - After bot creation, go to "Configuration"
   - Click "Manage" next to Microsoft App ID
   - In "Certificates & secrets", click "New client secret"
   - Description: "Text-to-SQL Bot"
   - Expiry: 24 months
   - Click "Add"
   - **IMPORTANT:** Copy the secret value immediately (you won't see it again)

4. **Copy Credentials**
   ```
   MICROSOFT_APP_ID: [Your App ID - looks like a GUID]
   MICROSOFT_APP_PASSWORD: [Your secret value - alphanumeric string]
   ```

#### Option B: Using Bot Framework Portal (Alternative)

1. Go to https://dev.botframework.com
2. Click "My bots" → "Create a bot" → "Register"
3. Fill in bot details and create
4. Copy App ID and generate password

---

### Step 2: Configure Public Endpoint with ngrok

Your bot needs to be accessible from the internet for Teams to send messages to it.

#### Install/Verify ngrok

```bash
# Check if ngrok exists
where ngrok

# If found at C:\Users\gals\ngrok.exe, configure authtoken
./ngrok.exe config add-authtoken 30TAhaHj4Dt8ko9Q6hdoh32F1Wr_BM1Xk2HcLibB8jW2NeeC
```

#### Start ngrok Tunnel

```bash
# Open new terminal window
cd C:\Users\gals
./ngrok.exe http 8000 --log=stdout

# You should see output like:
# Forwarding: https://abc123.ngrok.io -> http://localhost:8000
```

**IMPORTANT:** Copy the `https://` URL (e.g., `https://abc123.ngrok.io`)

---

### Step 3: Update Azure Bot Configuration

1. **Go back to Azure Portal**
   - Navigate to your Azure Bot resource
   - Click "Configuration"

2. **Set Messaging Endpoint**
   - Messaging endpoint: `https://[YOUR-NGROK-URL]/api/messages`
   - Example: `https://abc123.ngrok.io/api/messages`
   - Click "Apply"

3. **Enable Teams Channel**
   - Go to "Channels" section
   - Click "Microsoft Teams" icon
   - Click "Apply"
   - Teams channel should now show as "Running"

---

### Step 4: Update Application Configuration

#### Update .env File

```bash
# Open .env file
code C:\Users\gals\text-to-sql-app\.env
```

**Add the following:**
```env
# Teams Bot Configuration
MICROSOFT_APP_ID=<your-app-id-from-azure>
MICROSOFT_APP_PASSWORD=<your-app-password-from-azure>
```

Example:
```env
MICROSOFT_APP_ID=12345678-1234-1234-1234-123456789abc
MICROSOFT_APP_PASSWORD=abcXYZ123~_secretvalue.here
```

#### Restart Services

```bash
# Kill existing FastAPI server
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *uvicorn*"

# Restart with new configuration
cd C:\Users\gals\text-to-sql-app
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

### Step 5: Create "ask the DB" Teams Chat

#### Method 1: Add Bot to New Chat

1. **Open Microsoft Teams**
   - Desktop or web app

2. **Create New Chat**
   - Click "Chat" in left sidebar
   - Click "New chat" button
   - Name it: `ask the DB`

3. **Add the Bot**
   - In the chat, type `@` to mention someone
   - Search for your bot name: `wesign-text-to-sql-bot`
   - Select the bot from the list
   - Bot should join the chat

4. **Test Connection**
   - Type any message: `hello`
   - Bot should respond with welcome message

#### Method 2: Add Bot to Existing Channel

1. **Open a Team/Channel**
2. Click the `+` button to add a tab/app
3. Search for your bot
4. Add to channel
5. Configure and save

---

### Step 6: Verify Connection

#### Test Bot Responsiveness

```
# In Teams chat, send:
help

# Expected response:
Bot should reply with help message showing:
- Available commands
- Example queries
- Language options
```

#### Test Database Query

```
# In Teams chat, send:
How many companies are in the system?

# Expected response:
- SQL query shown: SELECT COUNT(*) as count FROM Companies
- Result displayed in adaptive card
- Response time < 5 seconds
```

#### Test Hebrew Query

```
# In Teams chat, send:
כמה חברות יש במערכת?

# Expected response:
- Hebrew language detected
- Same SQL query generated
- Result in Hebrew adaptive card
```

---

## Troubleshooting

### Issue 1: Bot Not Responding in Teams

**Symptoms:** Messages sent but no response

**Checks:**
1. Is ngrok running?
   ```bash
   # Check ngrok status in terminal window
   # Should show "online" and list connections
   ```

2. Is FastAPI server running?
   ```bash
   curl http://localhost:8000/health
   # Should return: {"status": "healthy"}
   ```

3. Check Azure Bot messaging endpoint
   - Go to Azure Portal → Bot Configuration
   - Verify messaging endpoint matches current ngrok URL
   - **Note:** ngrok URL changes each restart (unless you have paid plan)

4. Check logs
   ```bash
   Get-Content C:\Users\gals\text-to-sql-app\logs\orchestrator.log -Tail 50 -Wait
   ```

### Issue 2: Authentication Errors

**Symptoms:** "Unauthorized" or "401" errors in logs

**Fix:**
1. Verify MICROSOFT_APP_ID and MICROSOFT_APP_PASSWORD in .env
2. Ensure no extra spaces or quotes
3. Restart FastAPI server after updating .env
4. Check Azure Bot credentials haven't expired

### Issue 3: ngrok URL Expired

**Symptoms:** Bot was working, now doesn't respond

**Fix:**
1. Restart ngrok (URL changes on free tier)
2. Copy new ngrok URL
3. Update Azure Bot messaging endpoint
4. Test again in Teams

### Issue 4: Worker Not Processing Queries

**Symptoms:** Bot responds but says "pending", never completes

**Checks:**
1. Is worker service running?
   ```bash
   tasklist | findstr python
   # Should show multiple python processes
   ```

2. Check worker logs
   ```bash
   Get-Content C:\Users\gals\text-to-sql-app\logs\orchestrator.log -Tail 50
   ```

3. Check queue database
   ```bash
   docker exec -it postgres-queue psql -U postgres -d text_to_sql_queue -c "SELECT id, status, question FROM sql_queue ORDER BY created_at DESC LIMIT 5;"
   ```

4. Restart worker if needed
   ```bash
   taskkill /F /IM python.exe /FI "WINDOWTITLE eq *worker_service*"
   cd C:\Users\gals\text-to-sql-app
   python worker_service.py --fast
   ```

### Issue 5: Hebrew Text Not Displaying Correctly

**Symptoms:** Hebrew shows as gibberish or boxes

**Fix:**
1. Verify UTF-8 encoding in logs
2. Check Teams app language settings
3. Ensure database connection string has proper encoding
4. Test with simple Hebrew message first

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Microsoft Teams                          │
│                  (User sends message)                        │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTPS POST
                     │ to /api/messages
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                        ngrok                                 │
│              (Public tunnel to localhost)                    │
│            https://abc123.ngrok.io → localhost:8000          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Server (port 8000)                      │
│                teams_endpoint.py                             │
│  - Receives Teams messages                                   │
│  - Validates Bot Framework authentication                    │
│  - Routes to TeamsBot class                                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                  TeamsBot (teams_bot.py)                     │
│  - Detects language (en/he)                                  │
│  - Handles commands (help, status, examples)                 │
│  - Creates queue entry for queries                           │
│  - Sends "processing" message to user                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│            PostgreSQL Queue (port 5433)                      │
│  - Stores pending requests                                   │
│  - Fields: question, language, user_id, conversation_id      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓ (polled every 5 seconds)
┌─────────────────────────────────────────────────────────────┐
│           Worker Service (worker_service.py)                 │
│  - Polls queue for pending requests                          │
│  - Calls SQL generator                                       │
│  - Executes SQL against WeSign DB                            │
│  - Updates queue with results                                │
│  - Sends proactive message to Teams                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│          SQL Generator (sql_generator.py)                    │
│  - Pattern matching (COUNT, SELECT, etc.)                    │
│  - Entity extraction (table, columns, filters)               │
│  - WeSign table mapping                                      │
│  - Generates SQL query                                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│        WeSign Database (DEVTEST\SQLEXPRESS)                  │
│  - Executes generated SQL                                    │
│  - Returns results                                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│            Teams Proactive Message                           │
│  - Worker sends results back to Teams                        │
│  - Formatted as Adaptive Card                                │
│  - Shows SQL query + results table                           │
│  - User receives in "ask the DB" chat                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Security Considerations

### 1. Credentials Management
- ✅ Store credentials in .env file (never commit to git)
- ✅ Use Azure Key Vault for production (recommended)
- ✅ Rotate App Password every 6 months

### 2. Network Security
- ✅ ngrok provides HTTPS automatically
- ✅ Bot Framework validates requests (signature verification)
- ✅ SQL injection prevented by pattern-based generation

### 3. Access Control
- ⚠️ Currently, anyone who can message the bot can query the database
- 🔒 Consider adding:
  - User authentication via Azure AD
  - Role-based access control (RBAC)
  - Query approval workflow for sensitive data
  - Audit logging of all queries

### 4. Data Privacy
- ⚠️ Query results may contain sensitive data
- 🔒 Consider:
  - Row-level security in SQL Server
  - Data masking for PII
  - Limit result set size (currently 100 rows)
  - Private Teams channels only

---

## Monitoring & Maintenance

### Daily Checks
```bash
# 1. Check services are running
tasklist | findstr python
docker ps | grep postgres

# 2. Check recent logs for errors
Get-Content C:\Users\gals\text-to-sql-app\logs\orchestrator.log -Tail 100 | findstr ERROR

# 3. Check queue health
docker exec -it postgres-queue psql -U postgres -d text_to_sql_queue -c "SELECT status, COUNT(*) FROM sql_queue WHERE created_at > CURRENT_DATE GROUP BY status;"
```

### Weekly Maintenance
- Review error logs for patterns
- Check disk space for logs
- Verify ngrok tunnel is stable
- Test example queries from testing plan
- Review query performance metrics

### Monthly Tasks
- Rotate Azure Bot credentials
- Review and optimize slow queries
- Update testing plan with new queries
- Check for bot framework updates
- Archive old logs

---

## Production Deployment Checklist

When moving to production, replace ngrok with a proper setup:

- [ ] Azure App Service or Azure Container Instances for hosting
- [ ] Azure Application Gateway for HTTPS endpoint
- [ ] Azure Key Vault for secrets management
- [ ] Azure Monitor for logging and alerts
- [ ] Azure SQL Database (if migrating from DEVTEST)
- [ ] Azure AD authentication for users
- [ ] Rate limiting and throttling
- [ ] Backup and disaster recovery plan
- [ ] Load testing with expected user volume
- [ ] Documentation for operations team

---

## Quick Reference Commands

```bash
# Start ngrok
cd C:\Users\gals
./ngrok.exe http 8000

# Start FastAPI server
cd C:\Users\gals\text-to-sql-app
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Start worker service
cd C:\Users\gals\text-to-sql-app
python worker_service.py --fast

# Check PostgreSQL queue
docker exec -it postgres-queue psql -U postgres -d text_to_sql_queue -c "SELECT * FROM sql_queue ORDER BY created_at DESC LIMIT 5;"

# Monitor logs
Get-Content C:\Users\gals\text-to-sql-app\logs\orchestrator.log -Tail 50 -Wait

# Health check
curl http://localhost:8000/health

# Test bot locally (without Teams)
cd C:\Users\gals\text-to-sql-app
python test_bot_locally.py
```

---

## Support Resources

- **Azure Bot Service Docs:** https://docs.microsoft.com/azure/bot-service/
- **Bot Framework SDK:** https://github.com/microsoft/botbuilder-python
- **Teams Bot Development:** https://docs.microsoft.com/microsoftteams/platform/bots/what-are-bots
- **ngrok Documentation:** https://ngrok.com/docs

---

**END OF SETUP GUIDE**

Next Step: Execute Step 1 (Register Bot with Azure) to get MICROSOFT_APP_ID and MICROSOFT_APP_PASSWORD
