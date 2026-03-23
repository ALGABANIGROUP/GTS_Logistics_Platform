@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo [run-backend] Creating virtual environment .venv ...
  py -3 -m venv .venv
)

echo [run-backend] Upgrading pip ...
".venv\Scripts\python.exe" -m pip install --upgrade pip

if exist "backend\requirements.txt" (
  echo [run-backend] Installing backend requirements ...
  ".venv\Scripts\python.exe" -m pip install -r backend\requirements.txt
)

echo [run-backend] Starting Uvicorn ...
".venv\Scripts\python.exe" -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
