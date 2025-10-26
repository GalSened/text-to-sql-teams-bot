@echo off
REM ====================================================================
REM   Text-to-SQL Teams Bot - Startup Script
REM   Starts all required services for local development
REM ====================================================================

echo.
echo ============================================================
echo  Text-to-SQL Teams Bot - Starting Services
echo ============================================================
echo.

REM Check if Docker is running
echo [1/6] Checking Docker...
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)
echo     ✓ Docker is running

REM Start PostgreSQL Queue Database
echo.
echo [2/6] Starting PostgreSQL queue database...
docker start postgres-queue >nul 2>&1
if %errorlevel% neq 0 (
    echo     Creating new PostgreSQL container...
    docker run -d ^
      --name postgres-queue ^
      -p 5432:5432 ^
      -e POSTGRES_PASSWORD=postgres ^
      -e POSTGRES_DB=text_to_sql_queue ^
      -v pgdata:/var/lib/postgresql/data ^
      postgres:16-alpine
)
echo     ✓ PostgreSQL running on port 5432

REM Start SQL Server (if needed)
echo.
echo [3/6] Starting SQL Server target database...
docker start sqlserver-target >nul 2>&1
if %errorlevel% neq 0 (
    echo     Creating new SQL Server container...
    docker run -d ^
      --name sqlserver-target ^
      -p 1433:1433 ^
      -e "ACCEPT_EULA=Y" ^
      -e "SA_PASSWORD=YourStrong@Password123" ^
      mcr.microsoft.com/mssql/server:2022-latest >nul 2>&1
)
echo     ✓ SQL Server running on port 1433

REM Start Redis (optional, for caching)
echo.
echo [4/6] Starting Redis cache...
docker start redis >nul 2>&1
if %errorlevel% neq 0 (
    echo     Creating new Redis container...
    docker run -d ^
      --name redis ^
      -p 6379:6379 ^
      redis:alpine >nul 2>&1
)
echo     ✓ Redis running on port 6379

REM Wait for databases to be ready
echo.
echo [5/6] Waiting for databases to initialize...
timeout /t 10 /nobreak >nul
echo     ✓ Databases ready

REM Start FastAPI server in background
echo.
echo [6/6] Starting FastAPI server...
cd /d "%~dp0"
start /B python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > logs/fastapi.log 2>&1
echo     ✓ FastAPI running on http://localhost:8000

REM Show instructions for ngrok
echo.
echo ============================================================
echo  Services Started Successfully!
echo ============================================================
echo.
echo NEXT STEPS:
echo.
echo 1. Start ngrok tunnel (in a NEW terminal):
echo    ngrok http 8000
echo.
echo 2. Copy the ngrok URL (e.g., https://xyz.ngrok.io)
echo.
echo 3. Update Teams manifest with the ngrok URL
echo.
echo 4. Test the bot:
echo    - Open Bot Framework Emulator
echo    - Connect to http://localhost:8000/api/messages
echo    OR
echo    - Install in Teams and start chatting!
echo.
echo ============================================================
echo  Service URLs:
echo ============================================================
echo.
echo  FastAPI:        http://localhost:8000
echo  API Docs:       http://localhost:8000/docs
echo  Teams Endpoint: http://localhost:8000/api/messages
echo  Health Check:   http://localhost:8000/health
echo.
echo ============================================================
echo  Database Connections:
echo ============================================================
echo.
echo  PostgreSQL Queue:  localhost:5432
echo     Database:       text_to_sql_queue
echo     User:           postgres
echo     Password:       postgres
echo.
echo  SQL Server Target: localhost:1433
echo     User:           sa
echo     Password:       YourStrong@Password123
echo.
echo ============================================================
echo.
echo Press any key to open API documentation in browser...
pause >nul
start http://localhost:8000/docs
echo.
echo Press any key to exit (services will continue running in background)
pause >nul
