🚀 Quick Start Guide – GTS Logistics Platform

Last Updated: March 7, 2026

📋 System Requirements
Basic Requirements

OS: Windows 10+ / Linux / macOS

Python: 3.9+

Node.js: 16+

npm: 8+

Git: Configured

PostgreSQL: 12+ (or use Render Database)

Installed Libraries
# Requirements verified
✓ FastAPI framework
✓ SQLAlchemy ORM
✓ AsyncPG driver
✓ React 18
✓ Vite build tool
🔧 Initial Setup
1. Clone / Verify the Project Directory
cd c:\Users\enjoy\dev\GTS
2. Activate Python Virtual Environment
# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate
3. Install Python Requirements
pip install -r requirements.txt
4. Install Frontend Dependencies
cd frontend
npm install
cd ..
5. Verify the .env File
# Verify .env exists
ls -la .env

# It must include:
# - DATABASE_URL
# - SYNC_DATABASE_URL
# - JWT_SECRET_KEY
# - SMTP_HOST and email settings
🗄️ Database Setup
1. Run Migrations
# Apply all migrations
alembic upgrade head
2. Verify Connection
# Run the check script
python backend/db_ping.py

# Expected output:
# ✓ Database connection successful
# ✓ Pool size: 10
# ✓ Tables: 48+
3. Create Admin User (Optional)
# Create Super Admin
python create_test_superadmin.py

# Output:
# ✓ Super Admin created
# ✓ Username: admin
# ✓ Password: (will be displayed)
🖥️ Running the Backend
Method 1: Using VS Code Task
1. Press Ctrl+Shift+P
2. Select "Tasks: Run Task"
3. Choose "Start Backend (FastAPI)"
Method 2: Manual Run
python -m uvicorn backend.main:app --reload

# Expected output:
# uvicorn running on http://127.0.0.1:8000
# ✓ Startup complete
Method 3: Using PowerShell Script
./run_gts_server.ps1
Backend Health Check
# After starting, open in browser:
http://localhost:8000/health

# You should see:
# { "status": "healthy" }
💻 Running the Frontend
Method 1: Using VS Code Task
1. Press Ctrl+Shift+P
2. Select "Tasks: Run Task"
3. Choose "Start Frontend (Vite)"
Method 2: Manual Run
cd frontend
npm run dev

# Expected output:
# ➜ Local: http://localhost:5173/
# ➜ ready in 300ms
Frontend Health Check
# Open browser:
http://localhost:5173

# You should see:
# ✓ GTS Logistics Dashboard
# ✓ Theme toggle
# ✓ Bot panels loading
🔐 Authentication Testing
1. Test /auth/me Endpoint
# If you have a token
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/v1/auth/me

# Expected response:
# { "id": 1, "username": "admin", "email": "admin@example.com" }
2. Login Test
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin_password"
  }'

# Expected response:
# { "access_token": "eyJ...", "token_type": "bearer" }
🤖 AI Bots Testing
1. Check Bots Status
curl http://localhost:8000/api/v1/bots/status

# You should see a list of all bots and their status
2. Access Bot Panels

Frontend URLs:

General Manager:
http://localhost:5173/ai-bots/general-manager

Freight Broker:
http://localhost:5173/ai-bots/freight-broker

Finance Bot:
http://localhost:5173/ai-bots/finance

Documents Manager:
http://localhost:5173/ai-bots/documents

Service Bot:
http://localhost:5173/ai-bots/service
📧 Email Testing
1. Check Email Configuration
python backend/email_service/test_connection.py

# Expected output:
# ✓ SMTP connection successful
# ✓ IMAP connection successful
# ✓ POP3 connection successful
2. Send Test Email
curl -X POST http://localhost:8000/api/v1/email/test \
  -H "Content-Type: application/json" \
  -d '{
    "to": "test@example.com",
    "subject": "Test Email",
    "body": "This is a test email"
  }'
📊 Daily Operations
Health Check
# Check all services
curl http://localhost:8000/api/v1/health

# Expected output:
# {
#   "database": "ok",
#   "cache": "ok",
#   "email": "ok",
#   "bots": "ok"
# }
Log Monitoring
# Backend logs
tail -f logs/backend.log

# Frontend logs
# Open Developer Console in browser (F12)
Performance Check
# API response time
curl -w "@curl-format.txt" -o /dev/null http://localhost:8000/api/v1/users
🐛 Troubleshooting
Issue: Cannot Connect to Database
# 1. Check environment variables
echo $DATABASE_URL

# 2. Test connection directly
psql $DATABASE_URL -c "SELECT 1"

# 3. Check firewall
# Ensure connection is not blocked

# 4. Verify credentials
# Ensure username and password are correct
Issue: Frontend Cannot Connect to Backend
# 1. Check CORS settings
# Open browser console (F12)
# Look for CORS errors

# 2. Verify FRONTEND_URL in .env
# Must match localhost:5173

# 3. Restart both servers
# Kill and restart:
# - Backend (Ctrl+C)
# - Frontend (Ctrl+C)
Issue: Email Sending Failed
# 1. Check SMTP credentials
# SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD

# 2. Test SMTP connection
python -c "
import smtplib
smtp = smtplib.SMTP('mail.gabanilogistics.com', 465)
print('SMTP OK')
"

# 3. Check firewall
# Ensure ports 465, 993, 995 are not blocked
🔍 Useful Commands
Python / Backend
# Create new migration
alembic revision --autogenerate -m "description"

# Run tests
pytest tests/

# Format code
black backend/

# Linting
flake8 backend/
Frontend
# Production build
npm run build

# Preview build
npm run serve

# Clean Arabic encoding
npm run lint:arabic
Database
# Backup
pg_dump $SYNC_DATABASE_URL > backup.sql

# Restore
psql $SYNC_DATABASE_URL < backup.sql

# Undo last migration
alembic downgrade -1
🚀 Production Deployment
1. Preparation
# Update .env with production variables
nano .env

# Update values:
ENVIRONMENT=production
DEBUG=false
ENABLE_OPENAPI=false
GTS_CORS_ORIGINS=https://app.gtsdispatcher.com
2. Build
# Backend: already ready

# Frontend production build
cd frontend
npm run build

# This will generate the dist/ folder
3. Deploy (Render)
# Use the existing render.yaml
# Or deploy manually to Render

git push

# This will trigger automatic deployment on Render
📈 Performance Metrics
Backend Performance

Request latency: < 100ms

Database query time: < 50ms

API throughput: 1000+ req/sec

Frontend Performance

Bundle size: < 500KB

First contentful paint: < 2s

Time to interactive: < 3s

Database Performance

Connection pool: 10 connections

Max overflow: 15 connections

Query timeout: 30 seconds

📞 Support & Help
Common Issues
Problem	Solution
Backend won't start	Check Python version and .env
Frontend slow	Delete node_modules and run npm install again
Database unavailable	Check internet connection
Email not working	Verify SMTP credentials
Contact Points

Technical Support:
support@gabanistore.com

Operations:
operations@gabanilogistics.com

Emergency:
+966-XXXX-XXXX-XX

✅ First Run Checklist
[ ] Python virtual environment activated
[ ] Libraries installed (pip install -r requirements.txt)
[ ] Frontend installed (npm install)
[ ] .env file exists and correct
[ ] Migrations applied (alembic upgrade head)
[ ] Database connection tested
[ ] Backend running (localhost:8000)
[ ] Frontend running (localhost:5173)
[ ] Authentication working
[ ] Bots visible in Dashboard
[ ] Email working
📚 Additional References

Backend API Documentation → API_REFERENCE_COMPLETE.md

Database Schema Guide → DATABASE_LOCAL_GUIDE.md

AI Bots System → BOT_IMPLEMENTATION_SUMMARY.md

Security Guide → PORTAL_SECURITY_GUIDE.md

Deployment Procedures → DEPLOYMENT_PROCEDURES_INDEX.md

Last Updated: March 7, 2026
Version: 1.0-RC1