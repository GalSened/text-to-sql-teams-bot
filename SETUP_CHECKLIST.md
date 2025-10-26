# Setup Checklist - Quick Reference

Print this and check off each step as you complete it.

---

## ☐ STEP 1: Azure Bot Registration (10 min)

1. ☐ Go to https://portal.azure.com
2. ☐ Search for "Azure Bot"
3. ☐ Click "+ Create"
4. ☐ Bot handle: `wesign-text-to-sql-bot`
5. ☐ Pricing: F0 (Free)
6. ☐ Click "Create" → Wait for deployment
7. ☐ Click "Go to resource"

---

## ☐ STEP 2: Get Credentials (2 min)

1. ☐ Click "Configuration" in left menu
2. ☐ Copy **Microsoft App ID**: `________________________________`
3. ☐ Click "Manage" link
4. ☐ Click "Certificates & secrets"
5. ☐ Click "+ New client secret"
6. ☐ Expires: 24 months
7. ☐ Click "Add"
8. ☐ **IMMEDIATELY COPY THE SECRET VALUE**: `________________________________`

---

## ☐ STEP 3: Update .env (1 min)

1. ☐ Open: `C:\Users\gals\text-to-sql-app\.env`
2. ☐ Find lines 23-24
3. ☐ Paste App ID and Password
4. ☐ Save file (Ctrl+S)

---

## ☐ STEP 4: Start Services (3 min)

```powershell
cd C:\Users\gals\text-to-sql-app
.\start-all-services.ps1
```

1. ☐ PostgreSQL running
2. ☐ FastAPI started
3. ☐ Worker started
4. ☐ Test: `curl http://localhost:8000/health`

---

## ☐ STEP 5: Setup ngrok (2 min)

```powershell
cd C:\Users\gals
./ngrok.exe http 8000
```

1. ☐ ngrok running
2. ☐ Copy https:// URL: `https://________________________________.ngrok.io`

---

## ☐ STEP 6: Configure Bot Endpoint (2 min)

1. ☐ Azure Portal → Your bot → Configuration
2. ☐ Messaging endpoint: `https://your-url.ngrok.io/api/messages`
3. ☐ Click "Apply"
4. ☐ Green checkmark appears

---

## ☐ STEP 7: Enable Teams (1 min)

1. ☐ Click "Channels" in left menu
2. ☐ Click Microsoft Teams icon
3. ☐ Click "Save"
4. ☐ Status shows "Running"

---

## ☐ STEP 8: Create Chat & Test (5 min)

1. ☐ Open Microsoft Teams
2. ☐ Click "Chat" → "New chat"
3. ☐ Search for: `wesign-text-to-sql-bot`
4. ☐ Select bot
5. ☐ Name chat: `ask the DB`

**Test queries:**
- ☐ Type: `hello` → Receives welcome
- ☐ Type: `help` → Receives help
- ☐ Type: `How many companies are in the system?` → Receives SQL + results
- ☐ Type: `כמה חברות יש במערכת?` → Receives Hebrew response
- ☐ Type: `status` → Receives queue status

---

## ✅ Success!

All items checked = Bot is working! 🎉

---

## Quick Troubleshooting

**Bot not responding?**
1. ☐ Check ngrok is running
2. ☐ Check ngrok URL matches Azure endpoint
3. ☐ Check FastAPI health: `curl http://localhost:8000/health`
4. ☐ Check logs: `Get-Content logs\orchestrator.log -Tail 50`

**401 Unauthorized?**
1. ☐ Verify .env has correct App ID and Password
2. ☐ Restart: `.\start-all-services.ps1`

**Stuck in pending?**
1. ☐ Check worker window for errors
2. ☐ Restart worker: `python worker_service.py --fast`

---

**For detailed instructions, see: MANUAL_SETUP_GUIDE.md**
