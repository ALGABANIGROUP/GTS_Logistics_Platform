@echo off
title GTS Platform Test Runner
color 0A

echo ========================================
echo GTS Logistics Platform - Test Runner
echo ========================================
echo.

cd /d C:\Users\enjoy\dev\GTS-new

echo [1/4] Checking backend port 8000...
netstat -ano | findstr ":8000" >nul
if errorlevel 1 (
  echo Starting backend server...
  start "GTS Backend" cmd /k "cd /d C:\Users\enjoy\dev\GTS-new && .venv\Scripts\activate && python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000"
  echo Waiting 8 seconds for backend to start...
  timeout /t 8 /nobreak > nul
) else (
  echo Backend already running on port 8000.
)

echo.
echo [2/4] Checking frontend port 5173...
netstat -ano | findstr ":5173" >nul
if errorlevel 1 (
  echo Starting frontend server...
  start "GTS Frontend" cmd /k "cd /d C:\Users\enjoy\dev\GTS-new\frontend && npm run dev"
  echo Waiting 8 seconds for frontend to start...
  timeout /t 8 /nobreak > nul
) else (
  echo Frontend already running on port 5173.
)

echo.
echo [3/4] Running quick check...
powershell -ExecutionPolicy Bypass -File "%~dp0quick_check.ps1" -Fix

echo.
echo [4/4] Running diagnostics...
powershell -ExecutionPolicy Bypass -File "%~dp0debug.ps1" -Full

echo.
echo ========================================
echo Tests Complete
echo Backend : http://localhost:8000
echo Frontend: http://localhost:5173
echo Docs    : http://localhost:8000/docs
echo ========================================
echo.
pause
