@echo off
REM ====================================================================
REM   Step-by-Step Deployment - Text-to-SQL Teams Bot
REM   Interactive guide through all deployment phases
REM ====================================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================
echo  🚀 Text-to-SQL Teams Bot - Deployment Wizard
echo ============================================================
echo.
echo This script will guide you through deploying your FREE
echo Microsoft Teams bot step-by-step.
echo.
echo Estimated time: 30-40 minutes (first time)
echo.
pause

REM ====================================================================
REM PHASE 1: Prerequisites
REM ====================================================================

:PHASE1
cls
echo.
echo ============================================================
echo  PHASE 1/10: Prerequisites Check
echo ============================================================
echo.
echo Checking if all required tools are installed...
echo.

call check_prerequisites.bat

echo.
echo Did all checks pass?
choice /C YN /M "Continue to Phase 2"
if errorlevel 2 goto END
if errorlevel 1 goto PHASE2

REM ====================================================================
REM PHASE 2: Database Initialization
REM ====================================================================

:PHASE2
cls
echo.
echo ============================================================
echo  PHASE 2/10: Database Initialization
echo ============================================================
echo.
echo This will:
echo 1. Start PostgreSQL container (if not running)
echo 2. Create database schema
echo 3. Add sample test data
echo.
pause

echo.
echo [Step 1/3] Starting PostgreSQL container...
docker ps | find "postgres-queue" >nul
if %errorlevel% neq 0 (
    echo Starting new PostgreSQL container...
    docker run -d --name postgres-queue -p 5432:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=text_to_sql_queue postgres:16-alpine
    echo Waiting 10 seconds for PostgreSQL to initialize...
    timeout /t 10 >nul
) else (
    echo PostgreSQL container already running
    docker start postgres-queue >nul 2>&1
)

echo.
echo [Step 2/3] Initializing database schema...
python setup_database.py

echo.
echo [Step 3/3] Verifying database connection...
python -c "import psycopg2; conn=psycopg2.connect('dbname=text_to_sql_queue user=postgres password=postgres host=localhost'); print('✓ Database connection successful'); conn.close()"

echo.
echo ✅ Phase 2 complete!
echo.
pause

REM ====================================================================
REM PHASE 3: Start All Services
REM ====================================================================

:PHASE3
cls
echo.
echo ============================================================
echo  PHASE 3/10: Start All Services
echo ============================================================
echo.
echo This will start:
echo - PostgreSQL (queue database)
echo - SQL Server (target database)
echo - Redis (cache)
echo - FastAPI (web server on port 8000)
echo.
pause

echo.
call startup.bat

echo.
echo ✅ Phase 3 complete!
echo.
echo ⚠️  IMPORTANT: Now you need to start ngrok in a SEPARATE terminal:
echo.
echo     1. Open a NEW Command Prompt
echo     2. Run: ngrok http 8000
echo     3. Copy the "Forwarding" URL (e.g., https://abc123.ngrok-free.app)
echo     4. Keep that terminal window open!
echo.
echo Have you started ngrok and copied the URL?
pause

echo.
echo Enter your ngrok URL (e.g., https://abc123.ngrok-free.app):
set /p NGROK_URL="URL: "

echo.
echo Testing API access...
curl -s %NGROK_URL%/health >nul
if %errorlevel% equ 0 (
    echo ✓ API is accessible via ngrok!
) else (
    echo ⚠️  Could not reach API via ngrok. Check the URL and try again.
    pause
)

echo.
pause

REM ====================================================================
REM PHASE 4: Local Testing (Optional)
REM ====================================================================

:PHASE4
cls
echo.
echo ============================================================
echo  PHASE 4/10: Local Testing (Optional)
echo ============================================================
echo.
echo You can test the bot locally before installing in Teams.
echo.
echo Option 1: Bot Framework Emulator
echo   - Download from: https://github.com/Microsoft/BotFramework-Emulator/releases
echo   - Connect to: http://localhost:8000/api/messages
echo   - Test commands: /help, /status, /examples
echo.
echo Option 2: Skip to Teams installation
echo.
choice /C ST /M "Skip or Test locally"
if errorlevel 2 goto LOCAL_TEST
if errorlevel 1 goto PHASE5

:LOCAL_TEST
echo.
echo Testing with Bot Framework Emulator:
echo 1. Open Bot Framework Emulator
echo 2. Click "Open Bot"
echo 3. Bot URL: http://localhost:8000/api/messages
echo 4. Leave App ID and Password empty
echo 5. Click "Connect"
echo 6. Send message: "hello"
echo.
echo Expected: Bot responds with welcome message
echo.
echo Test these commands:
echo - /help
echo - /status
echo - /examples
echo - "How many customers joined last month?"
echo.
echo After testing, run: python process_queue.py
echo Then send: /history
echo.
echo Have you completed local testing?
pause
goto PHASE5

REM ====================================================================
REM PHASE 5: Teams App Package Creation
REM ====================================================================

:PHASE5
cls
echo.
echo ============================================================
echo  PHASE 5/10: Teams App Package Creation
echo ============================================================
echo.
echo You need to create a ZIP package with:
echo - manifest.json (already created)
echo - color.png (192x192 icon)
echo - outline.png (32x32 icon)
echo.
echo Creating icons:
echo.
echo Option 1: Use Canva (https://www.canva.com)
echo   - Create 192x192 image with database/SQL theme
echo   - Export as "color.png"
echo   - Create 32x32 version as "outline.png" (transparent background)
echo.
echo Option 2: Download free icons
echo   - Visit: https://www.flaticon.com
echo   - Search: "database" or "sql"
echo   - Download and resize to 192x192 and 32x32
echo.
echo Save both icons to: teams-app-manifest\
echo.
pause

echo.
echo Checking for icon files...
if exist teams-app-manifest\color.png (
    echo ✓ color.png found
    set ICON1=1
) else (
    echo ⚠️  color.png not found in teams-app-manifest\
    set ICON1=0
)

if exist teams-app-manifest\outline.png (
    echo ✓ outline.png found
    set ICON2=1
) else (
    echo ⚠️  outline.png not found in teams-app-manifest\
    set ICON2=0
)

if !ICON1! equ 0 (
    echo.
    echo Please add color.png to teams-app-manifest\ folder
    echo Then press any key to continue...
    pause
)

if !ICON2! equ 0 (
    echo.
    echo Please add outline.png to teams-app-manifest\ folder
    echo Then press any key to continue...
    pause
)

echo.
echo Creating ZIP package...
echo.
echo Manual steps:
echo 1. Go to: teams-app-manifest\ folder
echo 2. Select: manifest.json, color.png, outline.png
echo 3. Right-click and select "Send to > Compressed (zipped) folder"
echo 4. Name it: TextToSQL.zip
echo.
echo Have you created TextToSQL.zip?
pause
goto PHASE6

REM ====================================================================
REM PHASE 6: Teams Installation
REM ====================================================================

:PHASE6
cls
echo.
echo ============================================================
echo  PHASE 6/10: Teams Installation
echo ============================================================
echo.
echo Follow these steps to install the bot in Microsoft Teams:
echo.
echo 1. Open Microsoft Teams (desktop or web)
echo 2. Click "Apps" in the left sidebar
echo 3. Click "Manage your apps" at the bottom left
echo 4. Click "Upload a custom app"
echo 5. Select "Upload for me or my teams"
echo 6. Choose: teams-app-manifest\TextToSQL.zip
echo 7. Click "Add"
echo.
echo The bot should now appear in your Teams apps!
echo.
echo Note: If you get a permission error, you may need admin approval
echo       for custom app uploads in your organization.
echo.
echo Have you successfully installed the bot in Teams?
pause
goto PHASE7

REM ====================================================================
REM PHASE 7: End-to-End Testing
REM ====================================================================

:PHASE7
cls
echo.
echo ============================================================
echo  PHASE 7/10: End-to-End Testing
echo ============================================================
echo.
echo Let's test the complete flow:
echo.
echo [Test 1] In Teams, click on your bot and start a conversation
echo Expected: Bot sends welcome message
echo.
pause

echo [Test 2] Send command: /help
echo Expected: Help card with examples
echo.
pause

echo [Test 3] Send question: "How many customers joined last month?"
echo Expected: "✅ Query Submitted" with Job ID
echo.
pause

echo [Test 4] Now YOU process the queue (Claude Code time!)
echo.
echo In this terminal, run:
echo     python process_queue.py
echo.
echo This will:
echo - Fetch pending request from queue
echo - Generate SQL query
echo - Execute query
echo - Update results
echo.
pause

python process_queue.py

echo.
echo [Test 5] Back in Teams, send command: /history
echo Expected: See your question with "completed" status and results
echo.
pause

echo [Test 6] Test Hebrew: "כמה לקוחות הצטרפו בחודש שעבר?"
echo Expected: Bot responds in Hebrew
echo Process queue again, then check /history
echo.
echo Have all tests passed?
choice /C YN /M "Continue to Phase 8"
if errorlevel 2 goto TROUBLESHOOT
if errorlevel 1 goto PHASE8

REM ====================================================================
REM PHASE 8: Production Configuration (Optional)
REM ====================================================================

:PHASE8
cls
echo.
echo ============================================================
echo  PHASE 8/10: Production Configuration (Optional)
echo ============================================================
echo.
echo Optional enhancements:
echo.
echo 1. Get static ngrok domain (free)
echo    - Login to: https://dashboard.ngrok.com
echo    - Get your free static subdomain
echo    - Use: ngrok http 8000 --domain=your-domain.ngrok-free.app
echo    - Benefit: URL stays the same on restart
echo.
echo 2. Configure target database
echo    - Set up your real SQL Server connection
echo    - Update .env.devtest with credentials
echo.
echo 3. Set deployment environment
echo    - devtest: All operations allowed
echo    - prod: READ queries only
echo.
echo Do you want to configure production settings now?
choice /C YN /M "Skip or Configure"
if errorlevel 2 goto PHASE9
if errorlevel 1 (
    echo.
    echo Edit .env.devtest with your settings, then press any key...
    notepad .env.devtest
    pause
)
goto PHASE9

REM ====================================================================
REM PHASE 9: Daily Operations Setup
REM ====================================================================

:PHASE9
cls
echo.
echo ============================================================
echo  PHASE 9/10: Daily Operations Setup
echo ============================================================
echo.
echo Creating shortcuts for daily use...
echo.

echo [1/2] Creating startup shortcut on desktop...
echo @echo off > "%USERPROFILE%\Desktop\Start Teams Bot.bat"
echo cd /d "%CD%" >> "%USERPROFILE%\Desktop\Start Teams Bot.bat"
echo call startup.bat >> "%USERPROFILE%\Desktop\Start Teams Bot.bat"
echo ✓ Created: Start Teams Bot.bat on desktop

echo.
echo [2/2] Creating process queue shortcut on desktop...
echo @echo off > "%USERPROFILE%\Desktop\Process SQL Queue.bat"
echo cd /d "%CD%" >> "%USERPROFILE%\Desktop\Process SQL Queue.bat"
echo python process_queue.py >> "%USERPROFILE%\Desktop\Process SQL Queue.bat"
echo pause >> "%USERPROFILE%\Desktop\Process SQL Queue.bat"
echo ✓ Created: Process SQL Queue.bat on desktop

echo.
echo Daily workflow:
echo 1. Double-click "Start Teams Bot.bat" on desktop
echo 2. Run: ngrok http 8000 (in separate terminal)
echo 3. Users ask questions in Teams
echo 4. Double-click "Process SQL Queue.bat" on desktop
echo 5. Users see results via /history command
echo.
echo ✅ Phase 9 complete!
pause
goto PHASE10

REM ====================================================================
REM PHASE 10: Validation & Completion
REM ====================================================================

:PHASE10
cls
echo.
echo ============================================================
echo  PHASE 10/10: Final Validation
echo ============================================================
echo.
echo Running final checks...
echo.

echo [Check 1] Docker containers running...
docker ps | find "postgres-queue" >nul
if %errorlevel% equ 0 (
    echo ✓ PostgreSQL running
) else (
    echo ⚠️  PostgreSQL not running
)

echo.
echo [Check 2] FastAPI responding...
curl -s http://localhost:8000/health >nul
if %errorlevel% equ 0 (
    echo ✓ FastAPI responding
) else (
    echo ⚠️  FastAPI not responding
)

echo.
echo [Check 3] Database accessible...
python -c "import psycopg2; psycopg2.connect('dbname=text_to_sql_queue user=postgres password=postgres host=localhost').close(); print('✓ Database accessible')" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  Database not accessible
)

echo.
echo ============================================================
echo  🎉 DEPLOYMENT COMPLETE!
echo ============================================================
echo.
echo ✅ Your FREE Teams Text-to-SQL Bot is ready!
echo.
echo Quick Reference:
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 📂 Documentation:
echo    - QUICK_REFERENCE.md        (daily operations)
echo    - TEAMS_INTEGRATION_GUIDE.md (complete guide)
echo    - IMPLEMENTATION_SUMMARY.md  (technical details)
echo.
echo 🚀 Daily Startup:
echo    1. Double-click: "Start Teams Bot.bat" (on desktop)
echo    2. Run: ngrok http 8000 (separate terminal)
echo.
echo 💬 In Teams:
echo    - Ask questions naturally
echo    - Commands: /help, /status, /history, /examples
echo.
echo 🔄 Processing Queries:
echo    Double-click: "Process SQL Queue.bat" (on desktop)
echo.
echo 💰 Monthly Cost: $0
echo 💾 Saves: $500-800/month vs cloud solution
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo Need help? Check QUICK_REFERENCE.md for troubleshooting!
echo.
pause
goto END

REM ====================================================================
REM TROUBLESHOOTING
REM ====================================================================

:TROUBLESHOOT
cls
echo.
echo ============================================================
echo  🔧 Troubleshooting
echo ============================================================
echo.
echo Common issues:
echo.
echo 1. Bot not responding in Teams
echo    - Check: curl http://localhost:8000/health
echo    - Check: curl NGROK_URL/health
echo    - View logs: tail -f logs/fastapi.log
echo.
echo 2. Database connection error
echo    - Check: docker ps ^| find "postgres"
echo    - Restart: docker restart postgres-queue
echo.
echo 3. ngrok tunnel not working
echo    - Check ngrok is running
echo    - Verify URL in ngrok terminal
echo    - Test: curl NGROK_URL/health
echo.
echo 4. Complete restart
echo    - Run: shutdown.bat
echo    - Wait 10 seconds
echo    - Run: startup.bat
echo    - Restart: ngrok http 8000
echo.
pause
goto PHASE7

:END
echo.
echo Exiting deployment wizard...
echo.
pause
