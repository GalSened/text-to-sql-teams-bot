# Teams Bot Authentication & Token Management Plan

## Current Situation

**Available Tools:**
- ✅ Microsoft Bot Framework (in teams_bot.py)
- ✅ FastAPI endpoint for Teams messages
- ✅ BotFrameworkAdapter with authentication
- ❌ No Teams MCP server available

**What We Need:**
- Persistent token storage (avoid re-authentication)
- Automated chat creation
- End-to-end testing workflow

---

## Execution Plan

### Phase 1: Azure Bot Service Registration (One-Time Setup)

**Goal:** Get App ID and Password that persist across sessions

#### Step 1.1: Register Bot via Azure Portal
```
Manual steps (required once):
1. Go to https://portal.azure.com
2. Create "Azure Bot" resource
3. Name: wesign-text-to-sql-bot
4. Pricing: F0 (Free)
5. Create Microsoft App ID (auto-generated)
```

#### Step 1.2: Generate Client Secret
```
1. In Azure Bot → Configuration → Manage
2. Certificates & secrets → New client secret
3. Description: "Production Token"
4. Expires: 24 months
5. COPY THE SECRET VALUE (only shown once)
```

#### Step 1.3: Save Credentials to .env
```env
# Add to .env file (persistent storage)
MICROSOFT_APP_ID=<your-app-id-guid>
MICROSOFT_APP_PASSWORD=<your-secret-value>

# These credentials are long-lived (24 months)
# No need to re-authenticate during this period
```

**Result:** ✅ Persistent authentication tokens stored in .env

---

### Phase 2: Bot Framework Token Management

**How Bot Framework Handles Tokens:**

```python
# In teams_bot.py - Already implemented
class TeamsBot(ActivityHandler):
    def __init__(self, app_id: str, app_password: str):
        self.adapter = BotFrameworkAdapter(
            settings=BotFrameworkAdapterSettings(
                app_id=app_id,
                app_password=app_password
            )
        )
        # Adapter handles token refresh automatically
        # Uses OAuth2 to get access tokens
        # Caches tokens and refreshes when expired
```

**Token Lifecycle:**
1. Bot Framework Adapter uses App ID + Password
2. Exchanges for OAuth2 access token (valid ~1 hour)
3. Automatically refreshes when needed
4. No manual refresh required

**Storage Location:**
- App ID & Password: `.env` file (persistent)
- Access tokens: In-memory (BotFrameworkAdapter handles)
- Refresh tokens: Managed by Azure Bot Service

---

### Phase 3: Create "ask the DB" Chat

**Two Approaches:**

#### Approach A: Manual Chat Creation (Recommended for Testing)
```
1. Open Microsoft Teams
2. Click "Chat" → "New chat"
3. Name: "ask the DB"
4. Search for bot: "wesign-text-to-sql-bot"
5. Add bot to chat
6. Bot sends welcome message
```

**Pros:**
- Simple and reliable
- Works with free Azure tier
- No API limitations

**Cons:**
- Manual step required

#### Approach B: Programmatic Chat Creation (Requires Graph API)
```python
# Requires Microsoft Graph API permissions
# Need additional setup:
# 1. Grant "Chat.Create" permission in Azure
# 2. Use Microsoft Graph SDK
# 3. May require upgraded Azure plan

import requests

def create_teams_chat(access_token, bot_app_id):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    data = {
        "chatType": "oneOnOne",
        "members": [
            {
                "user": {"id": bot_app_id},
                "roles": ["owner"]
            }
        ]
    }

    response = requests.post(
        'https://graph.microsoft.com/v1.0/chats',
        headers=headers,
        json=data
    )
    return response.json()
```

**Pros:**
- Fully automated

**Cons:**
- Requires Graph API setup
- May need Azure AD app registration
- More complex

**Recommendation:** Use Approach A for initial testing

---

### Phase 4: Testing Workflow

#### Test 1: Local Bot Testing (No Teams Required)
```powershell
# Already working
cd C:\Users\gals\text-to-sql-app
python test_bot_locally.py
```

**Expected output:**
- ✅ Welcome message in English/Hebrew
- ✅ Help command works
- ✅ Sample queries generate SQL

#### Test 2: ngrok + Azure Connection Test
```powershell
# Terminal 1: Start ngrok
cd C:\Users\gals
./ngrok.exe http 8000

# Copy the https:// URL (e.g., https://abc123.ngrok.io)

# Terminal 2: Update Azure Bot
# Go to Azure Portal → Bot → Configuration
# Set messaging endpoint: https://abc123.ngrok.io/api/messages
# Click "Apply"

# Terminal 3: Start services
cd C:\Users\gals\text-to-sql-app
.\start-all-services.ps1
```

**Verification:**
```powershell
# Check FastAPI is running
curl http://localhost:8000/health

# Check ngrok tunnel
# Visit ngrok dashboard or check terminal output
```

#### Test 3: Teams Chat Testing
```
In Microsoft Teams:
1. Open "ask the DB" chat
2. Send: "hello"
   → Expect: Welcome message

3. Send: "help"
   → Expect: Help message with examples

4. Send: "How many companies are in the system?"
   → Expect:
      - "Processing your request..." (immediate)
      - Result card with SQL and count (within 5s)

5. Send: "כמה חברות יש במערכת?"
   → Expect: Same but in Hebrew
```

---

## Complete Execution Steps (In Order)

### Preparation (5 minutes)
```powershell
# 1. Verify services are running
cd C:\Users\gals\text-to-sql-app
docker ps | grep postgres-queue  # Should show "Up"

# 2. Check environment
cat .env | grep MICROSOFT_APP_ID
# If empty, need Azure registration first
```

### Azure Registration (10 minutes - One Time Only)
```
1. Open browser: https://portal.azure.com
2. Search: "Azure Bot"
3. Click: "Create"
4. Fill form:
   - Bot handle: wesign-text-to-sql-bot
   - Subscription: Your subscription
   - Resource group: Create new "wesign-bots"
   - Pricing: F0 (Free)
   - Microsoft App ID: Create new
5. Click: "Review + create"
6. Wait for deployment (1-2 minutes)
7. Go to resource → Configuration
8. Click: "Manage" next to App ID
9. Copy: Application (client) ID
10. Click: "Certificates & secrets"
11. Click: "New client secret"
12. Description: "Production"
13. Expires: 24 months
14. Click: "Add"
15. IMMEDIATELY COPY: Secret value
16. Open: C:\Users\gals\text-to-sql-app\.env
17. Add:
    MICROSOFT_APP_ID=<paste-app-id>
    MICROSOFT_APP_PASSWORD=<paste-secret>
18. Save .env
```

### Configure Bot Endpoint (5 minutes)
```
1. In Azure Portal → Bot → Configuration
2. Enable Teams channel:
   - Click: "Channels"
   - Click: "Microsoft Teams" icon
   - Click: "Save"
3. Set messaging endpoint (need ngrok URL first):
   - Leave this step for now
   - Will update after starting ngrok
```

### Start Services (2 minutes)
```powershell
# Start everything
cd C:\Users\gals\text-to-sql-app
.\start-all-services.ps1

# This will:
# - Start PostgreSQL (if not running)
# - Start FastAPI (port 8000)
# - Start Worker service
# - Prompt to start ngrok (if configured)
```

### Setup ngrok (3 minutes)
```powershell
# If ngrok not installed:
# 1. Download from https://ngrok.com/download
# 2. Extract to C:\Users\gals\
# 3. Configure auth token:
./ngrok.exe config add-authtoken 30TAhaHj4Dt8ko9Q6hdoh32F1Wr_BM1Xk2HcLibB8jW2NeeC

# Start tunnel
./ngrok.exe http 8000

# Look for line like:
# Forwarding  https://abc123.ngrok.io -> http://localhost:8000
# COPY THE HTTPS URL
```

### Update Azure Messaging Endpoint (1 minute)
```
1. Go back to Azure Portal → Bot → Configuration
2. Messaging endpoint: https://<your-ngrok-url>/api/messages
   Example: https://abc123.ngrok.io/api/messages
3. Click: "Apply"
4. Wait for green checkmark
```

### Create Teams Chat (1 minute)
```
1. Open Microsoft Teams (desktop or web)
2. Click: "Chat" in sidebar
3. Click: "New chat" button (top right)
4. In "To:" field, type: wesign-text-to-sql-bot
5. Select the bot from dropdown
6. Bot should appear in chat
7. Name chat: "ask the DB" (optional)
```

### Test Bot (5 minutes)
```
Test 1: Basic connectivity
→ Type: hello
← Expected: Welcome message

Test 2: Help command
→ Type: help
← Expected: Help with examples

Test 3: English query
→ Type: How many companies are in the system?
← Expected: Processing... then result card

Test 4: Hebrew query
→ Type: כמה חברות יש במערכת?
← Expected: Hebrew result card

Test 5: Status check
→ Type: status
← Expected: Queue status and system health
```

---

## Token Persistence Strategy

### Current Implementation (Already in Code)

**File: app/config.py**
```python
class Settings(BaseSettings):
    microsoft_app_id: Optional[str] = Field(default=None, env="MICROSOFT_APP_ID")
    microsoft_app_password: Optional[str] = Field(default=None, env="MICROSOFT_APP_PASSWORD")

    class Config:
        env_file = ".env"  # ← Loads from .env on startup
```

**File: app/bots/teams_bot.py**
```python
# Credentials loaded from .env
adapter = BotFrameworkAdapter(
    BotFrameworkAdapterSettings(
        app_id=settings.microsoft_app_id,
        app_password=settings.microsoft_app_password
    )
)
# Adapter handles token refresh internally
```

**Token Refresh Flow:**
```
1. App starts → Load credentials from .env
2. First request → Adapter exchanges credentials for access token
3. Access token cached in memory
4. Token expires (after ~1 hour) → Adapter auto-refreshes
5. App restart → Reload credentials, get fresh token
6. Credentials expire (after 24 months) → Rotate in Azure Portal
```

**No Additional Code Needed!**
- ✅ Tokens stored: .env file (App ID + Password)
- ✅ Auto-refresh: BotFrameworkAdapter handles it
- ✅ Persistent: Credentials last 24 months

---

## Troubleshooting Guide

### Issue 1: "Unauthorized" in Teams
**Cause:** App ID or Password incorrect

**Fix:**
```powershell
# Verify credentials in .env
cat .env | grep MICROSOFT_APP

# Should show:
# MICROSOFT_APP_ID=<guid-format>
# MICROSOFT_APP_PASSWORD=<alphanumeric-string>

# If empty or wrong, update from Azure Portal
# Bot → Configuration → Manage → Copy correct values
```

### Issue 2: Teams not receiving messages
**Cause:** ngrok URL not updated or expired

**Fix:**
```powershell
# 1. Check ngrok is running
# Look for "Forwarding" line in ngrok terminal

# 2. Copy current ngrok URL
# Should be https://<random>.ngrok.io

# 3. Update Azure Bot
# Portal → Bot → Configuration → Messaging endpoint
# Set to: https://<your-ngrok-url>/api/messages

# 4. Test endpoint
curl https://<your-ngrok-url>/api/messages
# Should return 405 Method Not Allowed (normal, means endpoint exists)
```

### Issue 3: Bot doesn't appear in Teams search
**Cause:** Teams channel not enabled or bot not published

**Fix:**
```
1. Azure Portal → Bot → Channels
2. Verify "Microsoft Teams" shows "Running"
3. If not, click Teams icon → Save
4. Wait 2-3 minutes
5. Retry searching in Teams
```

### Issue 4: Messages stuck in "pending"
**Cause:** Worker service not running or database connection issue

**Fix:**
```powershell
# Check worker logs
Get-Content C:\Users\gals\text-to-sql-app\logs\orchestrator.log -Tail 50

# Restart worker
# Close worker window and run:
cd C:\Users\gals\text-to-sql-app
python worker_service.py --fast
```

---

## Monitoring & Logs

### Check Service Health
```powershell
# FastAPI
curl http://localhost:8000/health

# PostgreSQL
docker exec postgres-queue psql -U postgres -d text_to_sql_queue -c "SELECT COUNT(*) FROM sql_queue;"

# Worker (check logs)
Get-Content logs\orchestrator.log -Tail 20 -Wait
```

### Monitor Queue
```powershell
# Pending requests
docker exec postgres-queue psql -U postgres -d text_to_sql_queue -c "SELECT COUNT(*) FROM sql_queue WHERE status = 'pending';"

# Recent completions
docker exec postgres-queue psql -U postgres -d text_to_sql_queue -c "SELECT id, question, status, created_at FROM sql_queue ORDER BY created_at DESC LIMIT 5;"
```

### View Teams Message Logs
```powershell
# Filter for Teams-related logs
Get-Content logs\orchestrator.log | Select-String "Teams"

# Filter for errors
Get-Content logs\orchestrator.log | Select-String "ERROR"
```

---

## Alternative: Use Graph API for Full Automation

If you need fully automated chat creation:

### Additional Setup Required:
1. **Register Azure AD App** (separate from Bot)
2. **Grant Graph API Permissions:**
   - Chat.Create
   - User.Read
   - TeamsAppInstallation.ReadWriteForUser
3. **Get Access Token:**
```python
import msal

config = {
    "client_id": "<azure-ad-app-id>",
    "client_secret": "<azure-ad-secret>",
    "authority": "https://login.microsoftonline.com/<tenant-id>"
}

app = msal.ConfidentialClientApplication(
    config["client_id"],
    authority=config["authority"],
    client_credential=config["client_secret"]
)

result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
access_token = result["access_token"]
```

4. **Create Chat Programmatically:**
```python
import requests

def create_teams_chat_with_bot(access_token, user_id, bot_app_id):
    url = "https://graph.microsoft.com/v1.0/chats"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "chatType": "oneOnOne",
        "members": [
            {
                "@odata.type": "#microsoft.graph.aadUserConversationMember",
                "roles": ["owner"],
                "user@odata.bind": f"https://graph.microsoft.com/v1.0/users/{user_id}"
            },
            {
                "@odata.type": "#microsoft.graph.aadUserConversationMember",
                "roles": ["owner"],
                "user@odata.bind": f"https://graph.microsoft.com/v1.0/users/{bot_app_id}"
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()
```

**Complexity:** High
**Recommendation:** Only if manual chat creation is a blocker

---

## Summary

### What's Already Working:
- ✅ Token management (via BotFrameworkAdapter)
- ✅ Auto token refresh (built into adapter)
- ✅ Persistent credentials (stored in .env)
- ✅ End-to-end query processing

### What You Need to Do:
1. **One-time:** Register Azure Bot (10 min)
2. **One-time:** Save credentials to .env
3. **Per session:** Start ngrok, update Azure endpoint
4. **One-time:** Create Teams chat manually
5. **Test:** Send messages and verify responses

### Time Estimate:
- **First time:** ~30 minutes (with Azure registration)
- **Subsequent times:** ~5 minutes (just start services)

---

**Ready to proceed with Azure Bot registration?** 🚀
