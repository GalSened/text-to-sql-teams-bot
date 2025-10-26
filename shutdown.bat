@echo off
REM ====================================================================
REM   Text-to-SQL Teams Bot - Shutdown Script
REM   Stops all services gracefully
REM ====================================================================

echo.
echo ============================================================
echo  Text-to-SQL Teams Bot - Stopping Services
echo ============================================================
echo.

echo [1/5] Stopping Worker Service...
wmic process where "commandline like '%%worker_service.py%%'" delete >nul 2>&1
echo     ✓ Worker service stopped

echo.
echo [2/5] Stopping FastAPI server...
for /f "tokens=5" %%a in ('netstat -ano ^| find ":8000" ^| find "LISTENING"') do taskkill /F /PID %%a >nul 2>&1
echo     ✓ FastAPI stopped

echo.
echo [3/5] Stopping ngrok...
taskkill /F /IM ngrok.exe >nul 2>&1
echo     ✓ ngrok stopped

echo.
echo [4/5] Stopping Docker containers...
docker stop postgres-queue >nul 2>&1
docker stop sqlserver-target >nul 2>&1
docker stop redis >nul 2>&1
echo     ✓ Containers stopped

echo.
echo [5/5] System shutdown complete

echo.
echo ============================================================
echo  All services stopped successfully!
echo ============================================================
echo.
echo Note: Docker containers are stopped but not removed.
echo To start again, just run startup.bat
echo.
echo To remove all containers and data:
echo   docker rm postgres-queue sqlserver-target redis
echo   docker volume rm pgdata
echo.
pause
