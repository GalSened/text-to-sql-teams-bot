# Manual Setup Guide - Teams Bot "ask the DB"
## Complete Step-by-Step Instructions

**Estimated Time:** 30 minutes
**Prerequisites:** Microsoft account with Azure access

---

## 📋 Setup Checklist

- [ ] Step 1: Register Azure Bot (10 min)
- [ ] Step 2: Configure Bot Credentials (2 min)
- [ ] Step 3: Start Local Services (3 min)
- [ ] Step 4: Setup ngrok Tunnel (2 min)
- [ ] Step 5: Configure Bot Endpoint (2 min)
- [ ] Step 6: Enable Teams Channel (1 min)
- [ ] Step 7: Create Teams Chat (2 min)
- [ ] Step 8: Test the Bot (5 min)

---

## STEP 1: Register Azure Bot (10 minutes)

### 1.1 Open Azure Portal
1. Open browser and go to: **https://portal.azure.com**
2. Sign in with your Microsoft account
3. Wait for portal to load (you should see the Azure dashboard)

### 1.2 Create Azure Bot Resource
1. In the search bar at top, type: **"Azure Bot"**
2. Click on **"Azure Bot"** from the results
3. Click the **"+ Create"** button

### 1.3 Fill in Bot Details

**Basics Tab:**
- **Bot handle:** `wesign-text-to-sql-bot` (must be globally unique)
  - If taken, try: `wesign-sql-bot-yourname` or `wesign-db-bot-2025`
- **Subscription:** Select your Azure subscription
- **Resource group:**
  - Click "Create new"
  - Name: `wesign-bots-rg`
- **Location:** Choose closest to you (e.g., "West Europe")
- **Pricing tier:** **F0 (Free)** - 10,000 messages/month
- **Type of App:** Select **"Multi Tenant"**
- **Microsoft App ID:** Click **"Create new Microsoft App ID"**

**Click "Review + create"**

### 1.4 Wait for Deployment
1. Click **"Create"**
2. Wait 1-2 minutes for deployment to complete
3. You'll see "Your deployment is complete"
4. Click **"Go to resource"**

✅ **Checkpoint:** You should now see your bot's Overview page

---

## STEP 2: Configure Bot Credentials (2 minutes)

### 2.1 Get Application ID
1. On your bot's page, click **"Configuration"** in the left menu
2. You'll see **"Microsoft App ID"** - this is a GUID like `12345678-1234-1234-1234-123456789abc`
3. **Copy this ID** - save it in Notepad temporarily

### 2.2 Create Client Secret (Password)
1. Next to Microsoft App ID, click the **"Manage"** link
   - This opens a new tab with Azure AD app registration
2. In the left menu, click **"Certificates & secrets"**
3. Click **"+ New client secret"**
4. Fill in:
   - **Description:** `Production-2025`
   - **Expires:** **24 months** (recommended)
5. Click **"Add"**
6. **IMMEDIATELY COPY THE VALUE** (the long alphanumeric string in the "Value" column)
   - ⚠️ **CRITICAL:** You can only see this ONCE! If you don't copy it now, you'll need to create a new one
   - Save it in Notepad with the App ID

### 2.3 Update .env File
1. Open file: `C:\Users\gals\text-to-sql-app\.env`
2. Find lines 23-24:
   ```env
   MICROSOFT_APP_ID=
   MICROSOFT_APP_PASSWORD=
   ```
3. Paste your values:
   ```env
   MICROSOFT_APP_ID=12345678-1234-1234-1234-123456789abc
   MICROSOFT_APP_PASSWORD=abcXYZ123~_yoursecretvaluehere
   ```
4. **Save the file** (Ctrl+S)

✅ **Checkpoint:** .env file now has both MICROSOFT_APP_ID and MICROSOFT_APP_PASSWORD filled in

---

## STEP 3: Start Local Services (3 minutes)

### 3.1 Verify Prerequisites
```powershell
# Open PowerShell in text-to-sql-app directory
cd C:\Users\gals\text-to-sql-app

# Check Docker is running
docker ps
# Should show postgres-queue container

# If not running, start it:
docker start postgres-queue
```

### 3.2 Start All Services
```powershell
# Run the automated startup script
.\start-all-services.ps1
```

**Expected output:**
- ✅ PostgreSQL container: Running
- ✅ FastAPI server starting on port 8000
- ✅ Worker service starting
- ⏳ ngrok prompt (we'll do this next)

**Verification:**
```powershell
# In a NEW PowerShell window, test FastAPI:
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy"}
```

✅ **Checkpoint:** Three PowerShell windows open (status, FastAPI, Worker)

---

## STEP 4: Setup ngrok Tunnel (2 minutes)

### 4.1 Check if ngrok is Installed
```powershell
# Try to find ngrok
where ngrok

# If not found, download from: https://ngrok.com/download
# Extract ngrok.exe to C:\Users\gals\
```

### 4.2 Configure ngrok (One-time)
```powershell
# Navigate to ngrok location
cd C:\Users\gals

# Set auth token (already provided in previous session)
./ngrok.exe config add-authtoken 30TAhaHj4Dt8ko9Q6hdoh32F1Wr_BM1Xk2HcLibB8jW2NeeC
```

### 4.3 Start ngrok Tunnel
```powershell
# In a NEW PowerShell window
cd C:\Users\gals
./ngrok.exe http 8000
```

**You should see:**
```
ngrok

Session Status                online
Account                       [your account]
Version                       [version]
Region                        [region]
Latency                       [ms]
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123xyz.ngrok.io -> http://localhost:8000
Forwarding                    http://abc123xyz.ngrok.io -> http://localhost:8000
```

### 4.4 Copy Your ngrok URL
1. Look for the line that says **"Forwarding"** with **https://**
2. Copy the URL: `https://abc123xyz.ngrok.io`
   - ⚠️ Your URL will be different! Don't use the example above
3. Save it in Notepad - you'll need it in the next step

✅ **Checkpoint:** ngrok running, HTTPS URL copied

---

## STEP 5: Configure Bot Endpoint (2 minutes)

### 5.1 Update Messaging Endpoint
1. Go back to **Azure Portal** (https://portal.azure.com)
2. Navigate to your bot: **wesign-text-to-sql-bot**
3. Click **"Configuration"** in the left menu
4. Find **"Messaging endpoint"** field
5. Paste your ngrok URL and add `/api/messages`:
   ```
   https://abc123xyz.ngrok.io/api/messages
   ```
   - Replace `abc123xyz.ngrok.io` with YOUR actual ngrok URL
6. Click **"Apply"** at the top
7. Wait for green checkmark (✓) "Saved successfully"

### 5.2 Verify Endpoint
```powershell
# Test the endpoint is reachable
curl https://your-ngrok-url.ngrok.io/api/messages

# Expected: 405 Method Not Allowed (this is CORRECT - means endpoint exists)
```

✅ **Checkpoint:** Messaging endpoint configured and responding

---

## STEP 6: Enable Teams Channel (1 minute)

### 6.1 Activate Microsoft Teams
1. Still in Azure Portal, on your bot page
2. Click **"Channels"** in the left menu
3. Under **"Available Channels"**, find **"Microsoft Teams"**
4. Click the **Microsoft Teams icon**
5. Click **"Save"** (or "Apply")
6. Wait for status to change to **"Running"**

✅ **Checkpoint:** Teams channel shows "Running" status

---

## STEP 7: Create Teams Chat (2 minutes)

### 7.1 Open Microsoft Teams
1. Open **Microsoft Teams** (desktop app recommended, or web at https://teams.microsoft.com)
2. Sign in if needed
3. Wait for Teams to fully load

### 7.2 Create New Chat
1. In the left sidebar, click **"Chat"** (💬 icon)
2. Click **"New chat"** button (pencil icon, top-right)
3. In the **"To:"** field at the top, type: `wesign-text-to-sql-bot`
   - Or search for your bot handle if different
4. **Select your bot** from the dropdown
   - It should appear with your bot handle
   - May take 2-3 minutes after enabling Teams channel for bot to appear in search

### 7.3 Name the Chat
1. Click in the chat name field (top of chat window)
2. Type: `ask the DB`
3. Press Enter

✅ **Checkpoint:** Chat created with bot, named "ask the DB"

---

## STEP 8: Test the Bot (5 minutes)

### 8.1 First Message (Welcome)
**In Teams chat, type:**
```
hello
```

**Expected response:**
- Bot should reply with a welcome message
- Should include examples in English and Hebrew
- Should mention available commands

**If no response:**
- Check ngrok is still running
- Check FastAPI server logs
- Check Azure Bot messaging endpoint matches current ngrok URL

### 8.2 Test Help Command
**Type:**
```
help
```

**Expected response:**
- Detailed help message
- List of commands (help, status, examples, schema, history, clear)
- Example questions in English and Hebrew

### 8.3 Test English Query
**Type:**
```
How many companies are in the system?
```

**Expected response:**
1. Immediate: "Processing your request..." message
2. Within 5 seconds: Result card showing:
   - Your question
   - Generated SQL: `SELECT COUNT(*) as count FROM Companies`
   - Results table with count
   - Execution time

### 8.4 Test Hebrew Query
**Type:**
```
כמה חברות יש במערכת?
```

**Expected response:**
- Same as English but in Hebrew
- SQL should be identical
- Result card in Hebrew

### 8.5 Test Status Command
**Type:**
```
status
```

**Expected response:**
- Queue status
- Pending/completed requests count
- System health information

### 8.6 Test More Queries

**Try these:**
```
List all contacts
הצג את כל המסמכים
Count all documents
Show documents from last month
```

✅ **Checkpoint:** All queries working, receiving responses in correct language

---

## 🎉 Success Criteria

You've successfully set up the bot when:

- ✅ Bot responds to messages in Teams
- ✅ English queries generate correct SQL
- ✅ Hebrew queries generate correct SQL
- ✅ Results display in adaptive cards
- ✅ Help and status commands work
- ✅ Queries process within 5 seconds

---

## 🔧 Troubleshooting

### Problem 1: Bot not responding in Teams

**Check #1: ngrok URL**
```powershell
# In ngrok window, verify "Session Status" shows "online"
# Copy the current https:// URL
# Update Azure Bot → Configuration → Messaging endpoint
```

**Check #2: FastAPI Server**
```powershell
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

**Check #3: Logs**
```powershell
Get-Content C:\Users\gals\text-to-sql-app\logs\orchestrator.log -Tail 50
# Look for errors or "401 Unauthorized"
```

### Problem 2: "Unauthorized" errors

**Fix:**
1. Verify `.env` has correct App ID and Password
2. Restart FastAPI server:
   - Close FastAPI window
   - Run: `.\start-all-services.ps1`

### Problem 3: Messages stuck in "pending"

**Check Worker:**
```powershell
# Check worker logs
Get-Content logs\orchestrator.log -Tail 20

# Check queue database
docker exec postgres-queue psql -U postgres -d text_to_sql_queue -c "SELECT id, question, status FROM sql_queue ORDER BY created_at DESC LIMIT 5;"
```

**Restart Worker:**
- Close worker window
- Run: `python worker_service.py --fast`

### Problem 4: ngrok URL changed

**⚠️ Free ngrok URLs change every restart**

When you restart ngrok:
1. Copy the NEW https:// URL
2. Go to Azure Portal → Bot → Configuration
3. Update Messaging endpoint with NEW URL
4. Click Apply

**Solution for permanent URL:**
- Upgrade to ngrok paid plan ($8/month) for static domain
- OR deploy to Azure App Service (production)

### Problem 5: Bot not found in Teams search

**Wait 2-3 minutes** after enabling Teams channel

**If still not found:**
1. Azure Portal → Bot → Channels
2. Verify Teams shows "Running"
3. Try searching by App ID instead of bot handle
4. Clear Teams cache: Settings → Privacy → Clear cache

---

## 📊 Monitor Your System

### View Logs Live
```powershell
# FastAPI logs
Get-Content logs\app.log -Tail 50 -Wait

# Worker logs
Get-Content logs\orchestrator.log -Tail 50 -Wait
```

### Check Queue Status
```powershell
docker exec postgres-queue psql -U postgres -d text_to_sql_queue -c "
SELECT
    status,
    COUNT(*) as count
FROM sql_queue
GROUP BY status;
"
```

### View Recent Queries
```powershell
docker exec postgres-queue psql -U postgres -d text_to_sql_queue -c "
SELECT
    id,
    question,
    status,
    sql_query,
    created_at
FROM sql_queue
ORDER BY created_at DESC
LIMIT 10;
"
```

---

## 🔄 Daily Usage

### Starting the System
```powershell
# 1. Start services (if not already running)
cd C:\Users\gals\text-to-sql-app
.\start-all-services.ps1

# 2. Start ngrok (in separate window)
cd C:\Users\gals
./ngrok.exe http 8000

# 3. Update Azure Bot endpoint if ngrok URL changed
#    (Check ngrok window for current URL)

# 4. Use Teams chat!
```

### Stopping the System
```powershell
# Run stop script
cd C:\Users\gals\text-to-sql-app
.\stop-all-services.ps1

# Or manually:
# - Close FastAPI window
# - Close Worker window
# - Close ngrok window
# - Keep PostgreSQL running (or stop with: docker stop postgres-queue)
```

---

## 📚 Quick Reference

### Bot Commands
| Command | Description |
|---------|-------------|
| `help` or `עזרה` | Show help with examples |
| `status` | Queue and system status |
| `examples` or `דוגמאות` | List example queries |
| `schema` | Show database schema |
| `history` | Your recent queries |
| `clear` | Clear query history |

### Example Queries

**English:**
- How many companies are in the system?
- List all contacts
- Show documents from last month
- Count all documents
- Top 10 companies

**Hebrew:**
- כמה חברות יש במערכת?
- רשום את כל אנשי הקשר
- הצג מסמכים מהחודש שעבר
- ספור את כל המסמכים
- הצג את כל החברות

### Key URLs
- **Azure Portal:** https://portal.azure.com
- **Microsoft Teams:** https://teams.microsoft.com
- **ngrok Dashboard:** http://127.0.0.1:4040 (when ngrok running)
- **FastAPI Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

---

## 🎯 What You've Built

```
Microsoft Teams (User Interface)
         ↓
    ngrok (Public Tunnel)
         ↓
  FastAPI Server (Bot Framework)
         ↓
 PostgreSQL Queue (Request Storage)
         ↓
  Background Worker (SQL Generation)
         ↓
    SQL Generator (Pattern Matching)
         ↓
  WeSign Database (DEVTEST\SQLEXPRESS)
         ↓
    Results → Teams Adaptive Card
```

**Features:**
- ✅ Bilingual support (English + Hebrew)
- ✅ Pattern-based SQL generation (fast, no AI cost)
- ✅ Automatic query processing
- ✅ Persistent token management (24 months)
- ✅ Queue-based architecture
- ✅ Real-time results in Teams

---

## 📞 Next Steps

### To Improve Pattern Matching:
1. Add more keywords to `app\services\sql_generator.py`
2. Test with `BILINGUAL_TESTING_PLAN.md`
3. Iterate on patterns based on failures

### For Production Deployment:
1. Replace ngrok with Azure App Service
2. Use Azure Key Vault for credentials
3. Enable authentication (Azure AD)
4. Set up monitoring and alerts
5. Configure rate limiting

### To Add AI Fallback:
1. Configure OpenAI API key in `.env`
2. Implement `generate_with_ai()` in sql_generator.py
3. Fall back to AI for queries that don't match patterns

---

**You're ready to use "ask the DB" in Microsoft Teams!** 🚀

---

## Appendix: Full File Structure

```
C:\Users\gals\text-to-sql-app\
├── app\
│   ├── bots\
│   │   └── teams_bot.py          # Teams bot logic (WeSign schema)
│   ├── services\
│   │   ├── sql_generator.py       # Pattern-based SQL generation
│   │   └── teams_notifier.py      # Proactive messaging
│   ├── api\
│   │   └── teams_endpoint.py      # FastAPI endpoint for Teams
│   └── config.py                  # Configuration (loads .env)
├── worker_service.py              # Background queue processor
├── .env                           # Credentials (updated in Step 2)
├── start-all-services.ps1         # Automated startup script
├── stop-all-services.ps1          # Automated shutdown script
├── BILINGUAL_TESTING_PLAN.md      # Complete testing plan
├── TEAMS_SETUP_GUIDE.md           # Detailed technical guide
├── MANUAL_SETUP_GUIDE.md          # This guide
└── SESSION_SUMMARY.md             # Previous session summary
```

---

**END OF MANUAL SETUP GUIDE**
