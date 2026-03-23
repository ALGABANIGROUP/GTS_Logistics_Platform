@echo off
setlocal
set "BASE=I:\GTS Logistics"
set "APP=%BASE%\backend"
set "VENV=%BASE%\.venv"
set "PY=%VENV%\Scripts\python.exe"
set "LOGD=%BASE%\logs"
if not exist "%LOGD%" mkdir "%LOGD%"
set "OUT=%LOGD%\gts-api.out.log"
set "ERR=%LOGD%\gts-api.err.log"

echo [runner] PY="%PY%" APP="%APP%" > "%OUT%"
if not exist "%PY%" (
  echo [runner][FATAL] python not found at "%PY%" >> "%ERR%"
  exit /b 1
)
if not exist "%APP%\main.py" (
  echo [runner][FATAL] main.py not found under "%APP%" >> "%ERR%"
  exit /b 1
)

echo [runner] starting uvicorn... >> "%OUT%"
"%PY%" -X dev -m uvicorn main:app --app-dir "%APP%" --host 127.0.0.1 --port 8001 --proxy-headers --forwarded-allow-ips="*" --log-level info >> "%OUT%" 2>> "%ERR%"

set RC=%ERRORLEVEL%
echo [runner] uvicorn exit code %RC% >> "%OUT%"
endlocal & exit /b %RC%
