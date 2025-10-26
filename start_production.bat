@echo off
REM ====================================================================
REM   Start Text-to-SQL System - PRODUCTION MODE
REM   Starts all services for 24/7 automated operation
REM ====================================================================

echo.
echo ============================================================
echo  🚀 Starting Text-to-SQL System (Production Mode)
echo ============================================================
echo.

REM Check prerequisites
echo [1/5] Checking prerequisites...
echo.

REM Check Docker
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running
    echo    Please start Docker Desktop first
    pause
    exit /b 1
)
echo ✓ Docker is running

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed
    pause
    exit /b 1
)
echo ✓ Python is installed

REM Check PostgreSQL container
echo.
echo [2/5] Starting PostgreSQL queue database...
docker ps | find "postgres-queue" >nul
if %errorlevel% neq 0 (
    echo    Starting PostgreSQL container...
    docker start postgres-queue >nul 2>&1
    if %errorlevel% neq 0 (
        echo    Creating new PostgreSQL container...
        docker run -d --name postgres-queue -p 5433:5432 ^
            -e POSTGRES_PASSWORD=postgres ^
            -e POSTGRES_DB=text_to_sql_queue ^
            postgres:16-alpine
    )
    timeout /t 5 /nobreak >nul
)
echo ✓ PostgreSQL is running

REM Start FastAPI
echo.
echo [3/5] Starting FastAPI server...
echo    Starting on http://localhost:8000
start /B "FastAPI Server" cmd /c "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > logs\fastapi.log 2>&1"
timeout /t 3 /nobreak >nul

REM Check if FastAPI started
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ FastAPI is responding
) else (
    echo ⚠️  FastAPI may still be starting up...
)

REM Start Worker Service
echo.
echo [4/5] Starting background worker service...
echo    Poll interval: 10 seconds
start /B "Worker Service" cmd /c "python worker_service.py > logs\worker.log 2>&1"
timeout /t 2 /nobreak >nul
echo ✓ Worker service started

REM Start ngrok (if configured)
echo.
echo [5/5] Starting ngrok tunnel...
echo    IMPORTANT: Keep this window open!
echo.

REM Check if static domain is configured
set NGROK_DOMAIN=
if exist ".ngrok-domain" (
    set /p NGROK_DOMAIN=<.ngrok-domain
)

if defined NGROK_DOMAIN (
    echo    Using static domain: %NGROK_DOMAIN%
    start "ngrok tunnel" ngrok http 8000 --domain=%NGROK_DOMAIN%
) else (
    echo    Using dynamic URL (changes each restart)
    echo    Tip: Get a free static domain at https://dashboard.ngrok.com
    start "ngrok tunnel" ngrok http 8000
)

timeout /t 3 /nobreak >nul

echo.
echo ============================================================
echo  ✅ System Started Successfully!
echo ============================================================
echo.
echo Services Running:
echo   • FastAPI:      http://localhost:8000
echo   • PostgreSQL:   localhost:5433
echo   • Worker:       Background (polling every 10s)
echo   • ngrok:        Check the ngrok window for URL
echo.
echo Logs:
echo   • FastAPI:  logs\fastapi.log
echo   • Worker:   logs\worker.log
echo.
echo Next Steps:
echo   1. Copy the ngrok URL from the ngrok window
echo   2. Test system: Use Bot Framework Emulator or Teams
echo   3. Monitor logs: tail -f logs\worker.log
echo   4. When done: Run shutdown.bat
echo.
echo System is now running 24/7!
echo Users can ask questions in Teams at any time.
echo.
pause
