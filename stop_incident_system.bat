@echo off
REM GTS Incident Response System - Windows Stop Script

echo 🛑 Stopping GTS Incident Response System...
echo.

REM Function to stop service
:stop_service
setlocal
set "service_name=%~1"

echo Stopping %service_name%...
taskkill /FI "WINDOWTITLE eq GTS-%service_name%" /T /F >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ %service_name% stopped
) else (
    echo ℹ️  %service_name% was not running
)
goto :eof

REM Stop services in reverse order
call :stop_service "AlertProcessor"
call :stop_service "LogMonitor"
call :stop_service "Backend"

echo.
echo 🎯 All Incident Response System services stopped

pause