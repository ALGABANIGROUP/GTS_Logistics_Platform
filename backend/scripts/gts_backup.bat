@echo off
echo 🚀 Starting GTS Backup Process...
cd /d "D:\GTS Logistics"
call .venv\Scripts\activate
python backend\tools\backup_database.py
echo ✅ Backup completed!
