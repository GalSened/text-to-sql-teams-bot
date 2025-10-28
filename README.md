# Text-to-SQL Teams Bot

A production-ready Microsoft Teams bot that converts natural language questions to SQL queries and returns results directly in Teams chat. Features bilingual support (English/Hebrew), read-only security enforcement, and real-time query execution.

![Bot Demo](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Security](https://img.shields.io/badge/Security-Read--Only%20Mode-blue)
![Languages](https://img.shields.io/badge/Languages-English%20%7C%20Hebrew-orange)

---

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Security](#security)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Reference](#api-reference)
- [PowerShell Bot Scripts](#powershell-bot-scripts)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Production Deployment](#production-deployment)
- [Contributing](#contributing)
- [License](#license)

---

## ✨ Features

### Core Functionality
- **Natural Language to SQL**: Converts questions in English or Hebrew to SQL queries
- **Direct Teams Integration**: Responds to questions in Microsoft Teams chat
- **Real-time Execution**: Executes queries and returns formatted results instantly
- **Bilingual Support**: Full support for English and Hebrew questions and responses
- **Smart Query Generation**: Uses pattern matching with Claude CLI fallback for complex queries

### Security Features
- **Read-Only Enforcement**: Double-layer security blocks all write operations (UPDATE, DELETE, INSERT, DROP, etc.)
- **API-Level Protection**: Primary security layer in FastAPI service
- **Bot-Level Failsafe**: Secondary regex validation before execution
- **Bilingual Error Messages**: Clear security messages in both English and Hebrew
- **Audit Logging**: All queries and security blocks are logged

### User Experience
- **Question Detection**: Only processes messages ending with `?`
- **Reaction Feedback**: Adds 👀 reaction when processing (indicates bot is working)
- **Clean Results**: Returns only query results, not SQL code
- **Formatted Output**: Tables and single values formatted for readability
- **Error Handling**: User-friendly error messages for common issues

---

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Microsoft Teams                           │
│                  "ask the DB" Chat                           │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   │ Microsoft Graph API
                   │
┌──────────────────▼──────────────────────────────────────────┐
│              PowerShell Bot (sql-bot-v2.ps1)                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ • Polls Teams chat every 5 seconds                     │ │
│  │ • Detects questions (messages ending with ?)           │ │
│  │ • Adds 👀 reaction                                      │ │
│  │ • Calls FastAPI service                                │ │
│  │ • Security check (regex failsafe)                      │ │
│  │ • Executes SQL via ADO.NET                             │ │
│  │ • Sends formatted results to Teams                     │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   │ HTTP POST /query/ask
                   │
┌──────────────────▼──────────────────────────────────────────┐
│              FastAPI Service (localhost:8000)                │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ SQL Generator Service                                  │ │
│  │ ├─ Pattern Matching (Primary)                          │ │
│  │ │  └─ Keyword-based SQL generation                     │ │
│  │ │                                                       │ │
│  │ ├─ Claude CLI (Fallback)                               │ │
│  │ │  └─ AI-powered complex query generation              │ │
│  │ │                                                       │ │
│  │ └─ Security Layer (Read-Only Validation)               │ │
│  │    └─ Blocks: UPDATE, DELETE, INSERT, DROP, etc.       │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   │ ADO.NET Connection
                   │
┌──────────────────▼──────────────────────────────────────────┐
│              SQL Server Database                             │
│                   (WeSign)                                   │
│          DEVTEST\SQLEXPRESS                                  │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Backend Services:**
- FastAPI 0.104.1 (Python 3.12)
- Pydantic for data validation
- Claude CLI for complex query generation
- Pattern matching for simple queries

**Bot Runtime:**
- PowerShell 5.1+
- Microsoft Graph API
- ADO.NET (System.Data.SqlClient)

**Database:**
- SQL Server (DEVTEST\SQLEXPRESS)
- Database: WeSign

**Infrastructure:**
- Docker (PostgreSQL queue - optional for background worker)
- Windows Server / Windows 10+

---

## 🔒 Security

### Multi-Layer Protection

#### Layer 1: API Security (Primary)
**Location:** `app/services/sql_generator.py`

```python
def _is_read_only_query(self, sql: str) -> bool:
    """Validates SQL is read-only (SELECT only)"""
    # Removes comments
    # Checks first keyword is SELECT or WITH
    # Scans for dangerous keywords
    # Returns: True if safe, False if dangerous
```

**Blocked Operations:**
- UPDATE
- DELETE
- INSERT
- DROP
- CREATE
- ALTER
- TRUNCATE
- EXEC/EXECUTE
- MERGE
- GRANT/REVOKE

**Response on Block:**
```json
{
  "error": "The bot only supports read queries (SELECT)\nהבוט תומך רק בשאילתות קריאה (SELECT)"
}
```

#### Layer 2: Bot Security (Failsafe)
**Location:** `sql-bot-v2.ps1` (line 248)

```powershell
if ($sql -match '^\s*(UPDATE|DELETE|INSERT|DROP|...)') {
    # Show bilingual security message
    # Log security block
    # Skip query execution
}
```

### Bilingual Security Messages

When dangerous query is detected:

```
🚫 **Security Policy**

The bot only supports read queries (SELECT)
הבוט תומך רק בשאילתות קריאה (SELECT)

For data modifications, please contact your administrator.
```

### Audit Trail

All security events are logged:
```
2025-10-27 09:33:32 | ERROR | Error calling SQL API: {"detail":"The bot only supports read queries..."}
2025-10-27 09:33:32 | INFO | Error message sent: 1761550412780
```

**Log Location:** `state/sql_bot_v2.log`

---

## 📦 Prerequisites

### Required Software

1. **Python 3.12+**
   ```bash
   python --version  # Should show 3.12 or higher
   ```

2. **PowerShell 5.1+**
   ```powershell
   $PSVersionTable.PSVersion  # Should show 5.1 or higher
   ```

3. **SQL Server**
   - SQL Server Express or higher
   - TCP/IP enabled
   - Mixed mode authentication

4. **Microsoft Teams**
   - Valid Microsoft 365 account
   - Teams desktop or web app

5. **Claude CLI** (for complex queries)
   ```bash
   claude --version
   ```
   Install from: https://github.com/anthropics/anthropic-tools

6. **Git** (for cloning repository)
   ```bash
   git --version
   ```

### Optional
- **Docker Desktop** (for PostgreSQL queue - background worker only)
- **ngrok** (for Teams webhook endpoint - production deployment)

---

## 🚀 Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/GalSened/text-to-sql-teams-bot.git
cd text-to-sql-teams-bot
```

### Step 2: Install Python Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

Create `.env` file in the project root:

```env
# Database Configuration
DB_SERVER=DEVTEST\SQLEXPRESS
DB_NAME=WeSign
DB_USER=sa
DB_PASSWORD=YourSecurePassword

# Microsoft Teams (for PowerShell bot)
TEAMS_TENANT_ID=your-tenant-id
TEAMS_CLIENT_ID=your-client-id
TEAMS_CLIENT_SECRET=your-client-secret

# Chat Configuration
TEAMS_CHAT_ID=19:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx@thread.v2

# Claude CLI Settings (optional)
CLAUDE_API_KEY=sk-ant-xxxxx
```

### Step 4: Set Up Microsoft Graph Authentication

Run the authentication helper:
```powershell
. .\graph-api-helpers.ps1
Get-GraphToken
```

This will:
- Prompt for device code authentication
- Save refresh token to `.msgraph-auth-with-refresh.json`
- Token auto-refreshes on expiry

### Step 5: Find Your Teams Chat ID

```powershell
.\list-teams-chats.ps1
```

Copy the Chat ID for "ask the DB" chat and update `.env`:
```env
TEAMS_CHAT_ID=19:9aa2d304ade8465baadcd9051e0a5cfc@thread.v2
```

---

## ⚙️ Configuration

### Database Connection

Edit `.env` file:
```env
DB_SERVER=YOUR_SERVER\INSTANCE
DB_NAME=YOUR_DATABASE
DB_USER=YOUR_USERNAME
DB_PASSWORD=YOUR_PASSWORD
```

### Bot Polling Interval

Edit `sql-bot-v2.ps1`:
```powershell
$POLL_INTERVAL = 5  # Seconds between checks (default: 5)
```

### Chat ID

Update `sql-bot-v2.ps1`:
```powershell
$CHAT_ID = "19:YOUR_CHAT_ID@thread.v2"
```

---

## 📖 Usage

### Start All Services

```powershell
.\start-all-services.ps1
```

This starts:
1. **FastAPI Server** (port 8000)
2. **Background Worker** (PostgreSQL queue processor)
3. Opens browser to API docs: http://localhost:8000/docs

### Start SQL Bot

```powershell
.\start-sql-bot-v2.ps1
```

**Console Output:**
```
╔════════════════════════════════════════════════════════════════╗
║          🤖 SQL BOT V2 - TEAMS ORCHESTRATOR                    ║
║                                                                ║
║  Chat: ask the DB                                              ║
║  Trigger: Messages ending with ?                               ║
║  Response: Query results only (not SQL)                        ║
╚════════════════════════════════════════════════════════════════╝

[INFO] SQL Bot V2 starting...
[INFO] Monitoring chat: ask the DB (ID: 19:9aa2...)
```

### Ask Questions in Teams

Open Teams → "ask the DB" chat → Type questions:

**Examples:**

```
How many companies are in the system?
```
**Bot Response:**
```
**Result:** 312
```

---

```
List the top 5 companies?
```
**Bot Response:**
```
**Results:**
Id | Name | Status
--- | --- | ---
1 | Company A | Active
2 | Company B | Active
...
```

---

```
כמה חברות יש במערכת?
```
**Bot Response:**
```
**Result:** 312
```

### Stop Services

**Stop SQL Bot:**
```powershell
.\stop-sql-bot-v2.ps1
```

**Stop All Services:**
```powershell
.\stop-all-services.ps1
```

**Restart SQL Bot:**
```powershell
.\restart-sql-bot-v2.ps1
```

---

## 🔌 API Reference

### Base URL
```
http://localhost:8000
```

### Endpoints

#### `POST /query/ask`
Convert natural language question to SQL and execute.

**Request:**
```json
{
  "question": "How many companies are there?"
}
```

**Response (Success):**
```json
{
  "success": true,
  "sql": "SELECT COUNT(*) as count FROM Companies",
  "results": [...],
  "explanation": "pattern_matching",
  "confidence": 0.95
}
```

**Response (Security Block):**
```json
{
  "success": false,
  "error": "The bot only supports read queries (SELECT)\nהבוט תומך רק בשאילתות קריאה (SELECT)",
  "sql": null,
  "confidence": 0,
  "method": "security_block"
}
```

#### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-27T10:30:00Z"
}
```

#### `GET /docs`
Interactive API documentation (Swagger UI).

Open in browser: http://localhost:8000/docs

---

## 🤖 PowerShell Bot Scripts

### Core Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `sql-bot-v2.ps1` | Main bot logic | Run with `start-sql-bot-v2.ps1` |
| `start-sql-bot-v2.ps1` | Start bot in new window | `.\start-sql-bot-v2.ps1` |
| `stop-sql-bot-v2.ps1` | Stop running bot | `.\stop-sql-bot-v2.ps1` |
| `restart-sql-bot-v2.ps1` | Restart bot | `.\restart-sql-bot-v2.ps1` |
| `graph-api-helpers.ps1` | Microsoft Graph API functions | Sourced by other scripts |

### Utility Scripts

| Script | Purpose |
|--------|---------|
| `list-teams-chats.ps1` | List all Teams chats to find Chat ID |
| `send-test-message.ps1` | Send test message to chat |
| `check-recent-messages.ps1` | View recent chat messages |
| `comprehensive-security-test.ps1` | Run security test suite |
| `cleanup-old-files.ps1` | Remove deprecated scripts |

### Bot State Files

| File | Purpose | Location |
|------|---------|----------|
| `sql_bot_v2.lock` | Process lock (prevents duplicate instances) | `state/` |
| `sql_bot_v2.log` | Bot activity log | `state/` |
| `sql_bot_v2_last_msg.txt` | Last processed message ID | `state/` |
| `sql_bot_v2_sent.json` | Sent message tracking (prevents loops) | `state/` |

---

## 🧪 Testing

### Run Comprehensive Tests

```powershell
.\comprehensive-security-test.ps1
```

**Test Coverage:**
- ✅ SELECT queries (English)
- ✅ SELECT queries (Hebrew)
- ✅ DELETE attempts (blocked)
- ✅ UPDATE attempts (blocked)
- ✅ INSERT attempts (blocked)
- ✅ DROP attempts (blocked)
- ✅ Complex SELECT with JOINs
- ✅ Bilingual error messages

**Expected Output:**
```
╔════════════════════════════════════════════════════════════════╗
║              COMPREHENSIVE SECURITY TEST                       ║
╚════════════════════════════════════════════════════════════════╝

Test 1: SELECT COUNT (English)
✅ PASS: Query allowed and returned results

Test 2: SELECT COUNT (Hebrew)
✅ PASS: Query allowed and returned results

Test 3: DELETE with WHERE
✅ PASS: Security block message shown

...

Overall: 7/7 Tests PASSED
```

### Test Individual Queries

```powershell
# Test pattern matching
python test_comprehensive.py

# Test Hebrew support
python test_hebrew_direct.py

# Test Claude CLI
python test_claude_simple.py
```

### Verify Security

```powershell
.\test-security-enforcement.ps1
```

Attempts dangerous queries and verifies they're blocked.

---

## 🔧 Troubleshooting

### Common Issues

#### Issue: Bot Not Responding

**Symptoms:** Messages in Teams, no bot response

**Solutions:**
1. Check bot is running:
   ```powershell
   Get-Process powershell | Where-Object { $_.MainWindowTitle -match "SQL Bot" }
   ```

2. Check log for errors:
   ```powershell
   Get-Content state\sql_bot_v2.log -Tail 20
   ```

3. Verify chat ID is correct:
   ```powershell
   .\list-teams-chats.ps1
   ```

4. Restart bot:
   ```powershell
   .\restart-sql-bot-v2.ps1
   ```

---

#### Issue: Authentication Expired

**Symptoms:** `401 Unauthorized` errors in log

**Solutions:**
1. Re-authenticate:
   ```powershell
   . .\graph-api-helpers.ps1
   Get-GraphToken
   ```

2. Verify token file exists:
   ```powershell
   Test-Path .msgraph-auth-with-refresh.json
   ```

---

#### Issue: SQL Connection Failed

**Symptoms:** `Cannot connect to database` errors

**Solutions:**
1. Verify SQL Server is running:
   ```powershell
   Get-Service MSSQL*
   ```

2. Test connection string:
   ```powershell
   sqlcmd -S DEVTEST\SQLEXPRESS -U sa -P YourPassword -Q "SELECT @@VERSION"
   ```

3. Check firewall allows SQL Server port (1433)

4. Enable TCP/IP in SQL Server Configuration Manager

---

#### Issue: FastAPI Service Not Starting

**Symptoms:** `Connection refused` to localhost:8000

**Solutions:**
1. Check if port 8000 is in use:
   ```powershell
   netstat -ano | findstr :8000
   ```

2. Start service manually:
   ```bash
   cd app
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

3. Check Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

#### Issue: Reactions Not Appearing

**Symptoms:** No 👀 reaction when bot processes questions

**Solutions:**
1. Check bot has permissions in Teams chat
2. Verify `Add-MessageReaction` function works:
   ```powershell
   .\test-reaction.ps1
   ```
3. Check log for reaction errors:
   ```powershell
   Get-Content state\sql_bot_v2.log | Select-String "Reaction"
   ```

---

### Debug Mode

Enable verbose logging in `sql-bot-v2.ps1`:

```powershell
# Change this line:
$VerbosePreference = "Continue"

# Add before running query:
Write-Verbose "About to execute SQL: $sql"
```

---

## 🌐 Production Deployment

### Architecture Overview

```
Internet
  │
  ├─ ngrok Tunnel (HTTPS)
  │   └─ https://your-subdomain.ngrok.io
  │
  ├─ Azure Bot Service
  │   └─ Messaging Endpoint: https://your-subdomain.ngrok.io/api/messages
  │
  └─ Microsoft Teams
      │
      ├─ "ask the DB" Chat
      │   └─ Users send questions
      │
      └─ Bot Responses
```

### Deployment Steps

#### 1. Set Up ngrok

```bash
# Install ngrok
choco install ngrok

# Start tunnel
ngrok http 8000
```

**Copy HTTPS URL:** `https://abc123.ngrok.io`

#### 2. Configure Azure Bot

1. Go to Azure Portal → Bot Services
2. Create new "Azure Bot"
3. Set **Messaging Endpoint:**
   ```
   https://abc123.ngrok.io/api/messages
   ```
4. Copy **App ID** and **App Secret**

#### 3. Update Configuration

Add to `.env`:
```env
AZURE_BOT_APP_ID=your-app-id
AZURE_BOT_APP_SECRET=your-app-secret
NGROK_URL=https://abc123.ngrok.io
```

#### 4. Deploy to Windows Server

```powershell
# Install as Windows Service
New-Service -Name "SQLBotV2" `
            -BinaryPathName "powershell.exe -ExecutionPolicy Bypass -File C:\bots\sql-bot-v2.ps1" `
            -StartupType Automatic `
            -DisplayName "SQL Teams Bot V2"

# Start service
Start-Service SQLBotV2
```

#### 5. Set Up Process Monitoring

Use Task Scheduler to restart bot on failure:

```powershell
# Create scheduled task
$action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-ExecutionPolicy Bypass -File C:\bots\restart-sql-bot-v2.ps1"

$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5)

Register-ScheduledTask -TaskName "Monitor SQL Bot" -Action $action -Trigger $trigger
```

### Production Checklist

- [ ] ngrok tunnel configured and running
- [ ] Azure Bot messaging endpoint updated
- [ ] Environment variables set in production
- [ ] SQL Server firewall rules configured
- [ ] Bot installed as Windows Service
- [ ] Process monitoring enabled
- [ ] Log rotation configured
- [ ] Backup/restore procedures documented
- [ ] Security review completed
- [ ] Load testing performed

---

## 📊 Monitoring & Logs

### Log Files

| Log | Location | Purpose |
|-----|----------|---------|
| Bot Activity | `state/sql_bot_v2.log` | All bot operations |
| FastAPI | `logs/api.log` | API requests/responses |
| Worker | `logs/worker.log` | Background queue processing |

### Log Rotation

Logs are automatically rotated:
- Max size: 10 MB
- Backup count: 5 files
- Format: `sql_bot_v2.log.1`, `sql_bot_v2.log.2`, etc.

### Monitoring Queries

Check bot health:
```powershell
# Last 20 log entries
Get-Content state\sql_bot_v2.log -Tail 20

# Check for errors
Get-Content state\sql_bot_v2.log | Select-String "ERROR"

# Monitor in real-time
Get-Content state\sql_bot_v2.log -Wait -Tail 10
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

### Development Setup

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes
4. Run tests: `.\comprehensive-security-test.ps1`
5. Commit changes: `git commit -m "Add amazing feature"`
6. Push to branch: `git push origin feature/amazing-feature`
7. Open Pull Request

### Code Standards

- **Python**: Follow PEP 8
- **PowerShell**: Use approved verbs (`Get-`, `Set-`, etc.)
- **Documentation**: Update README for all new features
- **Testing**: Add tests for security-critical changes

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Microsoft Graph API** for Teams integration
- **FastAPI** for high-performance API framework
- **Claude CLI** for advanced query generation
- **Anthropic** for Claude AI capabilities

---

## 📞 Support

For issues, questions, or contributions:

- **GitHub Issues:** https://github.com/GalSened/text-to-sql-teams-bot/issues
- **Documentation:** This README
- **Security Reports:** Please report security vulnerabilities privately

---

## 📈 Project Status

- **Version:** 2.0 (Production Ready)
- **Last Updated:** 2025-10-27
- **Status:** ✅ Active Development
- **Stability:** 🟢 Stable

### Recent Updates

- **2025-10-27:** Bilingual security messages implemented
- **2025-10-27:** Double-layer read-only security active
- **2025-10-27:** Pattern matching with Claude CLI fallback
- **2025-10-27:** PowerShell bot v2 deployed
- **2025-10-27:** Comprehensive testing suite added

---

**Built with ❤️ for secure, bilingual SQL querying in Microsoft Teams**
