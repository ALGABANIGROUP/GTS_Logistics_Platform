@echo off
setlocal
set PY=%~dp0\.venv\Scripts\python.exe
if not exist "%PY%" set PY=python
set VIZION_EYE_ENABLE=1
set VIZION_EYE_PATH=F:\ASUS ROG Strix G614JV\GTS Logistics\TheVIZION
set VIZION_EYE_AUTODASH=1
%PY% -m uvicorn backend.main:app --reload --port 8000
endlocal
