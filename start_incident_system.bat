@echo off
REM GTS Incident Response System - Windows Startup Script

echo 🚀 Starting GTS Incident Response System...
echo.

REM Set environment
set PYTHONPATH=%~dp0backend;%PYTHONPATH%
cd /d %~dp0

REM Load environment variables
if exist ".env" (
    for /f "tokens=*" %%a in (.env) do (
        set %%a 2>nul
    )
    echo ✅ Environment file loaded
) else (
    echo ❌ .env file not found
    pause
    exit /b 1
)

REM Create log directories
if not exist "logs" mkdir logs
if not exist "C:\var\log\gts" mkdir "C:\var\log\gts" 2>nul

echo 📁 Log directories created

REM Function to start service in background
:start_service
setlocal
set "service_name=%~1"
set "command=%~2"

echo 📡 Starting %service_name%...
start /B "GTS-%service_name%" cmd /c "%command%"
echo ✅ %service_name% started
goto :eof

REM Start log monitoring
call :start_service "LogMonitor" "python scripts\monitor_logs.py"

REM Start backend server (if not already running)
tasklist /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq GTS Backend" 2>NUL | find /I /N "python.exe">NUL
if %ERRORLEVEL% NEQ 0 (
    call :start_service "Backend" "python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"
) else (
    echo ℹ️  Backend server already running
)

REM Start alert processor (if configured)
if defined SLACK_WEBHOOK_URL (
    call :start_service "AlertProcessor" "python scripts\process_alerts.py" "logs\alerts.log"
) else if defined ALERT_EMAIL (
    call :start_service "AlertProcessor" "python scripts\process_alerts.py" "logs\alerts.log"
) else (
    echo ⚠️  No alert destinations configured - skipping alert processor
)

echo.
echo 🎉 Incident Response System started successfully!
echo.
echo Active Services:
echo   📊 Log Monitor: Running
echo   🚀 Backend API: Check logs\backend.log
if defined SLACK_WEBHOOK_URL (
    echo   📢 Alert Processor: Running (Slack enabled)
) else if defined ALERT_EMAIL (
    echo   📢 Alert Processor: Running (Email enabled)
) else (
    echo   📢 Alert Processor: Not configured
)
echo.
echo Monitor logs:
echo   Get-Content logs\monitor.log -Wait
echo   Get-Content logs\backend.log -Wait
echo.
echo Stop services: .\stop_incident_system.bat

pause