# ⚙️ Configuration Required

## 🔴 Action Required: Update Your .env File

I've created a `.env` file with placeholder values. You need to update these settings:

### 1. OpenAI API Key (Required for SQL Generation)

**Current**: `OPENAI_API_KEY=sk-placeholder-replace-with-real-key`

**Get your key**:
1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Create a new API key
4. Copy and paste it in `.env`

**Update to**:
```
OPENAI_API_KEY=sk-proj-your-actual-key-here
```

---

### 2. SQL Server Configuration (Required for Database Queries)

**Current**:
```
DB_SERVER=localhost
DB_NAME=TestDB
DB_USER=sa
DB_PASSWORD=YourPassword123!
```

**Update with your actual SQL Server details**:
```
DB_SERVER=your-actual-server
DB_NAME=your-actual-database
DB_USER=your-actual-username
DB_PASSWORD=your-actual-password
```

---

## ✅ Already Configured

These are already set and don't need changes:
- ✅ **SECRET_KEY**: Securely generated
- ✅ **APP_PORT**: 8000 (change if needed)
- ✅ **Safety settings**: Enabled
- ✅ **Debug mode**: Enabled for development

---

## 🧪 Testing Without Full Configuration

You can test parts of the system even without full configuration:

### Test 1: Check Configuration Loading
```bash
cd text-to-sql-app
python -c "from app.config import settings; print('Config loaded!')"
```

### Test 2: Test Query Classifier (Works Without Database!)
```bash
python -c "
from app.core.query_classifier import query_classifier
sql = 'SELECT * FROM customers'
query_type, risk = query_classifier.classify_query(sql)
print(f'Query Type: {query_type.value}, Risk: {risk.value}')
"
```

---

## 📋 Configuration Options

### Option A: Local SQL Server
If you have SQL Server installed locally:
```env
DB_SERVER=localhost
# or
DB_SERVER=(local)
# or
DB_SERVER=.\SQLEXPRESS
```

### Option B: Remote SQL Server
If your SQL Server is on another machine:
```env
DB_SERVER=192.168.1.100
# or
DB_SERVER=myserver.company.com
```

### Option C: Azure SQL Database
If using Azure SQL:
```env
DB_SERVER=myserver.database.windows.net
DB_NAME=mydatabase
DB_USER=myadmin
DB_PASSWORD=MySecurePassword123!
```

### Option D: Docker SQL Server (Quick Setup)
Want to set up a test database quickly? Run:
```bash
docker run -e "ACCEPT_EULA=Y" -e "SA_PASSWORD=YourPassword123!" -p 1433:1433 --name sql-server -d mcr.microsoft.com/mssql/server:2022-latest
```

Then use:
```env
DB_SERVER=localhost
DB_NAME=master
DB_USER=sa
DB_PASSWORD=YourPassword123!
```

---

## 🔍 Verify Your Configuration

After updating `.env`, run:
```bash
python test_basic.py
```

**Expected**: 6/6 tests should pass ✅

If tests fail:
- Check OpenAI API key is correct
- Test SQL Server connection manually
- Verify credentials are correct

---

## 🚀 Once Configured, Start the App

```bash
uvicorn app.main:app --reload
```

Then open: http://localhost:8000/docs

---

## 💡 Don't Have SQL Server?

### Quick Option: Use SQLite Instead
I can modify the app to use SQLite for testing (no SQL Server needed).
Just ask: "Can you modify it to use SQLite?"

### Free SQL Server Options:
1. **SQL Server Express** (free, local)
   - Download: https://www.microsoft.com/en-us/sql-server/sql-server-downloads

2. **Azure SQL Database** (cloud, free tier)
   - https://azure.microsoft.com/en-us/free/

3. **Docker SQL Server** (quick, isolated)
   - See Option D above

---

## 📞 Need Help?

Tell me what you have:
- "I have OpenAI key: sk-..."
- "I have SQL Server at: localhost"
- "I don't have SQL Server yet"
- "I want to use Docker SQL Server"

I'll help you configure everything!
