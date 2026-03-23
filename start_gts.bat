@echo off
title 🚛 GTS Logistics Platform - Launcher
color 1F

echo Starting GTS Logistics Platform...

:: Start the backend (FastAPI with Uvicorn)
start "GTS Backend" cmd /k "cd /d E:\GTS Logistics\backend && uvicorn main:app --reload"

:: Wait for 2 seconds before starting the frontend
timeout /t 2 /nobreak > nul

:: Start the frontend (Vite React App)
start "GTS Frontend" cmd /k "cd /d E:\GTS Logistics\frontend && npm run dev"

echo ✅ Backend and frontend servers launched successfully.
pause
