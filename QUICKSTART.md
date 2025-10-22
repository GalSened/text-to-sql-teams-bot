# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Create GitHub Repository

Go to [GitHub](https://github.com/new) and create a new repository named `text-to-sql-app`.

### 2. Push to GitHub

```bash
cd text-to-sql-app
git remote add origin https://github.com/YOUR_USERNAME/text-to-sql-app.git
git push -u origin master
```

### 3. Set Up Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your actual credentials
# Required: OPENAI_API_KEY, DB_SERVER, DB_NAME, DB_USER, DB_PASSWORD, SECRET_KEY
```

### 4. Install Dependencies

#### Option A: Using Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Option B: Using Docker

```bash
# Just run docker-compose (requires .env file)
docker-compose up -d
```

### 5. Run the Application

#### Without Docker:
```bash
python -m app.main
```

#### With Docker:
```bash
docker-compose up
```

### 6. Test It!

Open your browser: `http://localhost:8000/docs`

#### Try These Examples:

**Example 1: Simple SELECT**
```json
POST /query/ask
{
  "question": "Show me all customers",
  "execute_immediately": true
}
```

**Example 2: With Confirmation**
```json
POST /query/ask
{
  "question": "Update customer email where ID is 123",
  "execute_immediately": false
}

Then:
GET /query/preview/{query_id}

Then:
POST /query/execute
{
  "query_id": "{query_id}",
  "confirmed": true
}
```

## 🔑 Generate SECRET_KEY

```bash
# On Windows (PowerShell):
python -c "import secrets; print(secrets.token_hex(32))"

# On Linux/Mac:
openssl rand -hex 32
```

## 📝 Minimal .env Example

```env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
DB_SERVER=localhost
DB_PORT=1433
DB_NAME=MyDatabase
DB_USER=sa
DB_PASSWORD=YourPassword123
SECRET_KEY=your_generated_secret_key_here
```

## 🐛 Common Issues

### Issue: "ODBC Driver not found"

**Windows**: Download from [Microsoft](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

**Linux**:
```bash
# Ubuntu/Debian
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18
```

### Issue: "Can't connect to SQL Server"

1. Check SQL Server is running
2. Verify SQL Server allows remote connections:
   - SQL Server Configuration Manager
   - TCP/IP protocol enabled
   - Port 1433 open
3. Check firewall allows port 1433
4. Try adding `TrustServerCertificate=yes` to connection string

### Issue: "OpenAI API error"

1. Verify API key is correct
2. Check you have credits/billing set up
3. Try a different model (gpt-3.5-turbo is cheaper for testing)

## 📚 Next Steps

1. **Read the full [README.md](README.md)** for detailed documentation
2. **Check the API docs** at `http://localhost:8000/docs`
3. **Test with your database** - start with simple READ queries
4. **Explore safety features** - try UPDATE/DELETE to see confirmation workflow
5. **Customize** - adjust settings in `.env` for your needs

## 🎯 Test Workflow

```bash
# 1. Ask a safe question (auto-executes)
curl -X POST http://localhost:8000/query/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How many rows in customers table?", "execute_immediately": true}'

# 2. Ask a risky question (requires confirmation)
curl -X POST http://localhost:8000/query/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Delete all inactive customers"}'

# Returns query_id: "abc-123"

# 3. Preview what would be affected
curl http://localhost:8000/query/preview/abc-123

# 4. Execute with confirmation
curl -X POST http://localhost:8000/query/execute \
  -H "Content-Type: application/json" \
  -d '{"query_id": "abc-123", "confirmed": true}'

# 5. Check history
curl http://localhost:8000/query/history
```

## ✅ You're Ready!

Start querying your database in plain English! 🎉
