@echo off
echo ===============================
echo GTS Quick Diagnostic
echo ===============================

python tools/gts-python-module-check.py
echo.

powershell -ExecutionPolicy Bypass -File tools/gts-full-diagnostic.ps1 -BaseUrl http://127.0.0.1:8020

pause