@echo off
REM ====================================================================
REM   System Diagnostics - Text-to-SQL Teams Bot
REM   Quick health check for all components
REM ====================================================================

echo.
echo ============================================================
echo  🔍 System Diagnostics
echo ============================================================
echo.

set ERRORS=0
set WARNINGS=0

REM Check 1: Docker
echo [1/8] Docker Status...
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo     ❌ Docker not responding
    set /a ERRORS+=1
) else (
    echo     ✓ Docker is running
)

REM Check 2: PostgreSQL Container
echo.
echo [2/8] PostgreSQL Container...
docker ps | find "postgres-queue" >nul
if %errorlevel% neq 0 (
    echo     ❌ PostgreSQL container not running
    echo        Fix: docker start postgres-queue
    set /a ERRORS+=1
) else (
    echo     ✓ PostgreSQL container running
)

REM Check 3: PostgreSQL Connection
echo.
echo [3/8] PostgreSQL Connection...
python -c "import psycopg2; psycopg2.connect('dbname=text_to_sql_queue user=postgres password=postgres host=localhost').close()" >nul 2>&1
if %errorlevel% neq 0 (
    echo     ❌ Cannot connect to PostgreSQL
    echo        Fix: Check container is running and port 5432 is open
    set /a ERRORS+=1
) else (
    echo     ✓ PostgreSQL connection successful
)

REM Check 4: FastAPI Server
echo.
echo [4/8] FastAPI Server...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% neq 0 (
    echo     ❌ FastAPI not responding on port 8000
    echo        Fix: Run startup.bat to start the server
    set /a ERRORS+=1
) else (
    echo     ✓ FastAPI responding on port 8000
)

REM Check 5: Teams Endpoint
echo.
echo [5/8] Teams Bot Endpoint...
curl -s http://localhost:8000/api/health/teams >nul 2>&1
if %errorlevel% neq 0 (
    echo     ⚠️  Teams endpoint not responding
    echo        This may be normal if endpoint doesn't exist yet
    set /a WARNINGS+=1
) else (
    echo     ✓ Teams endpoint responding
)

REM Check 6: Queue Status
echo.
echo [6/8] Queue Status...
python -c "import psycopg2; conn=psycopg2.connect('dbname=text_to_sql_queue user=postgres password=postgres host=localhost'); cur=conn.cursor(); cur.execute('SELECT COUNT(*) FROM sql_queue WHERE status=%%s', ('pending',)); count=cur.fetchone()[0]; print(f'     ✓ {count} pending request(s) in queue'); conn.close()" 2>nul
if %errorlevel% neq 0 (
    echo     ⚠️  Cannot query queue table
    echo        Run: python setup_database.py
    set /a WARNINGS+=1
)

REM Check 7: ngrok
echo.
echo [7/8] ngrok Status...
ngrok version >nul 2>&1
if %errorlevel% neq 0 (
    echo     ⚠️  ngrok not installed
    echo        Install: choco install ngrok
    set /a WARNINGS+=1
) else (
    tasklist | find /i "ngrok.exe" >nul
    if %errorlevel% neq 0 (
        echo     ⚠️  ngrok installed but not running
        echo        Start: ngrok http 8000 (in separate terminal)
        set /a WARNINGS+=1
    ) else (
        echo     ✓ ngrok is running
    )
)

REM Check 8: Environment Variables
echo.
echo [8/8] Configuration...
if exist .env.devtest (
    echo     ✓ .env.devtest found
) else (
    echo     ❌ .env.devtest not found
    set /a ERRORS+=1
)

REM Summary
echo.
echo ============================================================
if %ERRORS% equ 0 (
    if %WARNINGS% equ 0 (
        echo  ✅ All systems operational!
        echo.
        echo  System is ready to process queries.
    ) else (
        echo  ⚠️  System running with %WARNINGS% warning(s)
        echo.
        echo  System should work but check warnings above.
    )
) else (
    echo  ❌ Found %ERRORS% error(s) and %WARNINGS% warning(s)
    echo.
    echo  Please fix errors before proceeding.
    echo.
    echo  Quick fixes:
    echo  - Start Docker Desktop
    echo  - Run: startup.bat
    echo  - Run: python setup_database.py
    echo  - Install missing tools
)
echo ============================================================
echo.

REM Detailed Status
echo.
echo Detailed Status:
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 📦 Docker Containers:
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>nul
echo.
echo 🌐 Network Ports:
netstat -an | find "LISTENING" | find ":8000" >nul && echo     ✓ Port 8000 (FastAPI) - LISTENING || echo     ❌ Port 8000 (FastAPI) - NOT LISTENING
netstat -an | find "LISTENING" | find ":5432" >nul && echo     ✓ Port 5432 (PostgreSQL) - LISTENING || echo     ⚠️  Port 5432 (PostgreSQL) - NOT LISTENING
echo.
echo 📊 Queue Statistics:
python -c "import psycopg2; conn=psycopg2.connect('dbname=text_to_sql_queue user=postgres password=postgres host=localhost'); cur=conn.cursor(); cur.execute('SELECT status, COUNT(*) FROM sql_queue GROUP BY status'); for row in cur: print(f'     {row[0]}: {row[1]}'); conn.close()" 2>nul || echo     ⚠️  Cannot query queue
echo.
echo 💾 Disk Usage:
docker system df 2>nul
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
pause
