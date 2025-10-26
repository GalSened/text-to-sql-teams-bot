@echo off
REM ====================================================================
REM   ngrok Setup Helper - Text-to-SQL Teams Bot
REM   Helps configure ngrok for Teams connectivity
REM ====================================================================

echo.
echo ============================================================
echo  🌐 ngrok Setup Helper
echo ============================================================
echo.

REM Check if ngrok is installed
ngrok version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ngrok is not installed!
    echo.
    echo Please install ngrok first:
    echo   Option 1: choco install ngrok
    echo   Option 2: Download from https://ngrok.com/download
    echo.
    pause
    exit /b 1
)

echo ✓ ngrok is installed
ngrok version
echo.

REM Check if authtoken is configured
echo Checking ngrok configuration...
echo.

REM Test if we can start ngrok
echo ============================================================
echo  Configuration Steps
echo ============================================================
echo.
echo Step 1: Get your ngrok authtoken
echo ───────────────────────────────────────────────────────────
echo.
echo 1. Go to: https://dashboard.ngrok.com/signup
echo 2. Sign up for a FREE account
echo 3. Go to: https://dashboard.ngrok.com/get-started/your-authtoken
echo 4. Copy your authtoken
echo.
echo Have you created an account and copied your authtoken?
pause

echo.
echo Step 2: Configure authtoken
echo ───────────────────────────────────────────────────────────
echo.
set /p AUTHTOKEN="Paste your ngrok authtoken here: "

echo.
echo Configuring ngrok...
ngrok config add-authtoken %AUTHTOKEN%

if %errorlevel% equ 0 (
    echo ✓ Authtoken configured successfully!
) else (
    echo ❌ Failed to configure authtoken
    echo Please try manually: ngrok config add-authtoken YOUR_TOKEN
    pause
    exit /b 1
)

echo.
echo Step 3: Get static domain (Optional but Recommended)
echo ───────────────────────────────────────────────────────────
echo.
echo Free tier includes 1 static domain!
echo Benefits:
echo   - URL stays the same when you restart ngrok
echo   - No need to update Teams manifest
echo   - More professional
echo.
echo To get your free static domain:
echo 1. Go to: https://dashboard.ngrok.com/cloud-edge/domains
echo 2. Click "Create Domain" or "New Domain"
echo 3. Choose a subdomain name (e.g., mycompany-sql)
echo 4. Copy the full domain (e.g., mycompany-sql.ngrok-free.app)
echo.
echo Do you want to set up a static domain?
choice /C YN /M "Yes or No"
if errorlevel 2 goto TEST_NGROK
if errorlevel 1 goto STATIC_DOMAIN

:STATIC_DOMAIN
echo.
set /p STATIC_DOMAIN="Enter your static domain (e.g., mycompany-sql.ngrok-free.app): "
echo.
echo Great! You can now start ngrok with:
echo   ngrok http 8000 --domain=%STATIC_DOMAIN%
echo.
echo Creating a shortcut for you...
echo @echo off > "%USERPROFILE%\Desktop\Start ngrok.bat"
echo cd /d "%CD%" >> "%USERPROFILE%\Desktop\Start ngrok.bat"
echo echo Starting ngrok tunnel... >> "%USERPROFILE%\Desktop\Start ngrok.bat"
echo echo. >> "%USERPROFILE%\Desktop\Start ngrok.bat"
echo echo Your static URL: https://%STATIC_DOMAIN% >> "%USERPROFILE%\Desktop\Start ngrok.bat"
echo echo. >> "%USERPROFILE%\Desktop\Start ngrok.bat"
echo echo Keep this window open! >> "%USERPROFILE%\Desktop\Start ngrok.bat"
echo echo. >> "%USERPROFILE%\Desktop\Start ngrok.bat"
echo ngrok http 8000 --domain=%STATIC_DOMAIN% >> "%USERPROFILE%\Desktop\Start ngrok.bat"
echo ✓ Created "Start ngrok.bat" on your desktop
echo.
goto TEST_NGROK

:TEST_NGROK
echo.
echo Step 4: Test ngrok
echo ───────────────────────────────────────────────────────────
echo.
echo Let's test if ngrok works!
echo.
echo Make sure FastAPI is running first:
echo   - Run: startup.bat (if not already running)
echo   - Wait for "Application startup complete"
echo.
echo Is FastAPI running?
choice /C YN /M "Continue"
if errorlevel 2 goto END

echo.
echo Starting ngrok tunnel...
echo.
echo ⚠️  This will open ngrok in a NEW terminal window.
echo    Keep that window open!
echo.
echo After ngrok starts, you'll see a "Forwarding" URL like:
echo    https://abc123.ngrok-free.app -> http://localhost:8000
echo.
echo Copy that URL - you'll need it for Teams!
echo.
pause

REM Start ngrok in a new window
if defined STATIC_DOMAIN (
    start "ngrok tunnel" ngrok http 8000 --domain=%STATIC_DOMAIN%
) else (
    start "ngrok tunnel" ngrok http 8000
)

echo.
echo ngrok started! Check the new terminal window.
echo.
echo Wait a few seconds, then we'll test the connection...
timeout /t 5 >nul

echo.
echo Testing connection...
echo.

REM Try to get ngrok API info
curl -s http://localhost:4040/api/tunnels >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ ngrok tunnel is active!
    echo.
    echo Getting tunnel info...
    curl -s http://localhost:4040/api/tunnels | find "public_url"
) else (
    echo ⚠️  Cannot reach ngrok API
    echo    This is normal if ngrok just started
    echo    Check the ngrok terminal window for the URL
)

echo.
echo ============================================================
echo  ✅ ngrok Setup Complete!
echo ============================================================
echo.
echo Next Steps:
echo ───────────────────────────────────────────────────────────
echo.
echo 1. Copy the Forwarding URL from ngrok terminal
echo    Example: https://abc123.ngrok-free.app
echo.
echo 2. Test the URL:
echo    curl https://YOUR_URL/health
echo.
echo 3. Use this URL when installing Teams app
echo    (Add to manifest.json validDomains)
echo.
echo 4. Keep the ngrok terminal window open!
echo    If you close it, the tunnel stops.
echo.
echo Daily Usage:
echo ───────────────────────────────────────────────────────────
if defined STATIC_DOMAIN (
    echo Double-click "Start ngrok.bat" on your desktop
    echo Your URL is always: https://%STATIC_DOMAIN%
) else (
    echo Run: ngrok http 8000
    echo Note: URL changes each time (get static domain to fix this)
)
echo.
echo ============================================================
echo.
pause

:END
echo.
echo Setup complete! Check TEAMS_INTEGRATION_GUIDE.md for next steps.
echo.
