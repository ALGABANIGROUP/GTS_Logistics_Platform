@echo off
REM GTS Logistics Platform - Development Server Launcher
REM Simple Development Server Launcher

echo 🚀 GTS Logistics Platform - Development Server
echo.


REM GTS Logistics Platform - Development Server

echo. REM Check if virtual environment exists
if not exist "backend\.venv\Scripts\activate.bat" ( 
echo ❌ Virtual environment not found in backend\.venv 
echo Please run setup first: 
echo cd backend 
echo python -m venv .venv 
echo .venv\Scripts\activate 
echo pip install -r ../requirements-simple.txt 
pause 
exit /b 1
)

REM Activate virtual environment
echo 📦 Activating virtual environment...
call backend\.venv\Scripts\activate.bat

REM Install/update requirements if needed
echo 📦 Installation requirements...
pip install -r requirements-simple.txt

REM Create uploads directory
if not exist "uploads" mkdir uploads

REM Start the server
echo.
echo ✅ Starting development server...
echo 📖 API docs: http://localhost:8000/docs
echo 🏥 Health check: http://localhost:8000/health
echo 🛑Press Ctrl+C to stop
echo.

cd backend
python main_simple.py