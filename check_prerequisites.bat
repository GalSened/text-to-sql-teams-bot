@echo off
REM ====================================================================
REM   Prerequisites Checker - Text-to-SQL Teams Bot
REM   Verifies all required tools are installed
REM ====================================================================

echo.
echo ============================================================
echo  Prerequisites Check - Text-to-SQL Teams Bot
echo ============================================================
echo.

set ERRORS=0

REM Check Python
echo [1/5] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo     ❌ Python not found! Install Python 3.12+
    set ERRORS=1
) else (
    python --version
    echo     ✓ Python installed
)

echo.

REM Check Docker
echo [2/5] Checking Docker...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo     ❌ Docker not found! Install Docker Desktop
    set ERRORS=1
) else (
    docker --version
    docker ps >nul 2>&1
    if %errorlevel% neq 0 (
        echo     ⚠️  Docker installed but not running! Start Docker Desktop
        set ERRORS=1
    ) else (
        echo     ✓ Docker installed and running
    )
)

echo.

REM Check ngrok
echo [3/5] Checking ngrok...
ngrok version >nul 2>&1
if %errorlevel% neq 0 (
    echo     ⚠️  ngrok not found!
    echo     Install: choco install ngrok
    echo     Or download from: https://ngrok.com/download
    set ERRORS=1
) else (
    ngrok version
    echo     ✓ ngrok installed
)

echo.

REM Check pip packages
echo [4/5] Checking Python dependencies...
python -c "import fastapi" >nul 2>&1
if %errorlevel% neq 0 (
    echo     ⚠️  FastAPI not installed
    echo     Run: pip install -r requirements.txt
    set ERRORS=1
) else (
    echo     ✓ FastAPI installed
)

python -c "import psycopg2" >nul 2>&1
if %errorlevel% neq 0 (
    echo     ⚠️  psycopg2 not installed
    echo     Run: pip install -r requirements.txt
    set ERRORS=1
) else (
    echo     ✓ psycopg2 installed
)

python -c "import botbuilder.core" >nul 2>&1
if %errorlevel% neq 0 (
    echo     ⚠️  botbuilder-core not installed
    echo     Run: pip install -r requirements.txt
    set ERRORS=1
) else (
    echo     ✓ Bot Framework SDK installed
)

echo.

REM Check if .env file exists
echo [5/5] Checking configuration...
if exist .env.devtest (
    echo     ✓ .env.devtest found
) else (
    echo     ⚠️  .env.devtest not found!
    echo     Create .env.devtest with required configuration
    set ERRORS=1
)

echo.
echo ============================================================
if %ERRORS% equ 0 (
    echo  ✅ All prerequisites met! Ready to proceed.
    echo.
    echo  Next steps:
    echo  1. Run: python setup_database.py
    echo  2. Run: startup.bat
    echo  3. Run: ngrok http 8000 ^(in separate terminal^)
) else (
    echo  ❌ Some prerequisites missing! Fix issues above.
    echo.
    echo  Quick fixes:
    echo  - Python: Download from python.org
    echo  - Docker: Download from docker.com
    echo  - ngrok: choco install ngrok
    echo  - Dependencies: pip install -r requirements.txt
)
echo ============================================================
echo.
pause
