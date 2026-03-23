🔧 Maintenance and Common Issues Guide

Date: March 7, 2026

🚨 Common Problems and Their Solutions
1. Problem: Backend Does Not Start
Symptoms
Error: ModuleNotFoundError: No module named 'backend'
Error: Could not load .env file
Error: database connection failed
Solution

Step 1: Check the Python environment

# Activate the Virtual Environment
.venv\Scripts\activate

# You should see (venv) at the beginning of the line

Step 2: Check installed libraries

# Reinstall requirements
pip install -r requirements.txt --force-reinstall

# Verify versions
pip list | grep -i fastapi
pip list | grep -i sqlalchemy
pip list | grep -i asyncpg

Step 3: Check the .env file

# Ensure the .env file exists
ls -la .env

# Check its contents
cat .env | grep -i "DATABASE_URL\|SECRET_KEY"

Step 4: Check the database connection

# Test the connection
python -c "
import asyncio
from backend.database.base import SessionLocal
asyncio.run(SessionLocal.connect())
print('✓ Database connection OK')
"
2. Problem: CORS Error
Symptoms
CORS policy: No 'Access-Control-Allow-Origin' header
Access to XMLHttpRequest from origin has been blocked
Solution

Step 1: Open backend/main.py

# Look for the CORS configuration
# It should look similar to:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Step 2: Check .env

# It should contain:
GTS_CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# In production:
GTS_CORS_ORIGINS=https://app.gtsdispatcher.com

Step 3: Restart the Backend

# Stop the current process
Ctrl+C

# Start again
python -m uvicorn backend.main:app --reload
3. Problem: Email Failure
Symptoms
SMTPAuthenticationError
ConnectionRefusedError: [Errno 10061] No connection could be made
TimeoutError: Connection timeout
Solution

Step 1: Check email settings in .env

# Ensure the following exist:
SMTP_HOST=mail.gabanilogistics.com
SMTP_PORT=465
SMTP_USER=noreply@gabanilogistics.com
SMTP_FROM=noreply@gabanilogistics.com
IMAP_HOST=mail.gabanilogistics.com
IMAP_PORT=993
IMAP_USER=noreply@gabanilogistics.com
POP3_HOST=mail.gabanilogistics.com
POP3_PORT=995
POP3_USER=noreply@gabanilogistics.com

Step 2: Test SMTP connection

import smtplib
smtp = smtplib.SMTP('mail.gabanilogistics.com', 465)
smtp.starttls()
smtp.login('noreply@gabanilogistics.com', 'PASSWORD')
print('✓ SMTP Connection OK')
smtp.quit()

Step 3: Test IMAP connection

import imaplib
imap = imaplib.IMAP4_SSL('mail.gabanilogistics.com', 993)
imap.login('noreply@gabanilogistics.com', 'PASSWORD')
print('✓ IMAP Connection OK')
imap.close()

Step 4: Check Firewall

# On Windows
netstat -an | grep :465
netstat -an | grep :993

# You should see listening connections
4. Problem: Frontend Returns 404
Symptoms
GET /api/v1/... 404 Not Found
Cannot GET /static/...
Solution

Step 1: Check the Vite server

# Ensure Frontend is running
cd frontend
npm run dev

# You should see:
# ➜ Local: http://localhost:5173/
# ➜ ready in 300ms

Step 2: Check Backend

# Test Backend endpoint
curl http://localhost:8000/api/v1/health

# Expected response: 200 OK

Step 3: Check the PORT

# Frontend should run on 5173
# Backend should run on 8000
netstat -ano | findstr :5173
netstat -ano | findstr :8000

Step 4: Clear Cache

# Inside frontend directory
rm -rf node_modules/.vite
npm run dev
5. Problem: Memory Leak
Symptoms
Process usage keeps increasing
Server gets slower over time
Out of Memory error
Solution

Step 1: Monitor memory

# Use monitoring tools
python monitor_memory.py
python monitor_memory_improved.py

# Or use Windows Task Manager
# Ctrl+Shift+Esc

Step 2: Clean memory

# Run garbage collector
python cleanup_memory.py
python cleanup_memory_improved.py

Step 3: Restart the server

# Kill the process
taskkill /F /IM python.exe

# Or use
Ctrl+C

Step 4: Check for query leaks

# There may be a database connection leak
# Check backend/routes/ to ensure:
# - All sessions are closed
# - All connections are released
6. Problem: Bots Not Appearing
Symptoms
Empty bot list in Dashboard
Bots panel shows "No bots available"
Bot status shows "offline"
Solution

Step 1: Check the database

# Run the inspection script
python get_bot_names.py

# Or run SQL directly:
# SELECT * FROM bots;

Step 2: Reconfigure bots

python create_bot_os_tables.py
python fix_bots_service.py

Step 3: Check Backend routes

# Test the bots endpoint
curl http://localhost:8000/api/v1/bots/list

# Expected output:
# [ { "id": 1, "name": "bot_name", ... } ]

Step 4: Check Frontend

// In browser console (F12)
fetch('http://localhost:8000/api/v1/bots/list')
  .then(r => r.json())
  .then(d => console.log(d))
7. Problem: Database Connection Pool Exhausted
Symptoms
QueuePool limit of size exceeded
Cannot acquire connection from pool
Connection timeout
Solution

Step 1: Check Pool settings in .env

DB_POOL_SIZE=10
DB_MAX_OVERFLOW=15
DB_POOL_TIMEOUT=20
DB_POOL_RECYCLE=600

Step 2: Check number of active connections

psql -h dpg-cuicq2qj1k6c73asm5c0-a.oregon-postgres.render.com \
  -U gabani_transport_solutions_user \
  -d gabani_transport_solutions \
  -c "SELECT count(*) FROM pg_stat_activity;"

Step 3: Close idle connections

SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE pid <> pg_backend_pid() 
AND state = 'idle';

Step 4: Restart Backend

Ctrl+C

# Wait for connections to close
sleep 5

# Restart
python -m uvicorn backend.main:app --reload
8. Problem: Authentication Token Expired
Symptoms
401 Unauthorized
Token is invalid or expired
Please log in again
Solution

Step 1: Check token expiration time

# In .env
ACCESS_TOKEN_EXPIRE_MINUTES=30

Step 2: Use Refresh Token

const response = await fetch('/api/v1/auth/refresh', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ refresh_token: oldToken })
});

Step 3: Clean old tokens

python run_cleanup.py
9. Problem: Database Migration Failed
Symptoms
FAILED: Alembic revision failed
Cannot apply migration
Schema mismatch error
Solution

Step 1: Check migration status

alembic current
alembic history

Step 2: Roll back

alembic downgrade -1

Or:

alembic downgrade <revision_id>

Step 3: Upgrade again

alembic upgrade head

Or:

alembic upgrade <revision_id>

Step 4: Rebuild tables (if necessary)

python backend/init_db.py
10. Problem: Slow API Response
Symptoms
API takes more than 5 seconds to respond
Timeout errors
High CPU usage
Solution

Step 1: Measure performance

time curl http://localhost:8000/api/v1/users

Or:

ab -n 100 -c 10 http://localhost:8000/api/v1/users

Step 2: Enable SQL logs

SQLALCHEMY_ECHO = True

Step 3: Optimize queries

users = session.query(User).options(
    joinedload(User.posts)
).all()

Step 4: Add caching

from functools import lru_cache

@lru_cache(maxsize=100)
def get_users():
    pass
🛠️ Routine Maintenance Tools
Daily Tasks
python SYSTEM_DIAGNOSTICS.py
python COMPREHENSIVE_SYSTEM_CHECK.py

python check_db.py
python list_tables.py

tail -f logs/backend.log
Weekly Tasks
pg_dump $SYNC_DATABASE_URL > backup_$(date +%Y%m%d).sql

python analyze_memsnap.py

rm -rf cache/*
rm -rf __pycache__/*
Monthly Tasks
pip install --upgrade -r requirements.txt
npm update --prefix frontend

pytest tests/

grep ERROR logs/backend.log | tail -20
📊 Performance Monitoring
Important Metrics
API Response Time: < 100ms
Database Query: < 50ms
Frontend Load Time: < 2s
Memory Usage: < 500MB
CPU Usage: < 50%
Tools
python monitor_memory.py

curl -w "@curl-format.txt" http://localhost:8000/api/v1/health

psql -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
🆘 If You Are Confused
Basic troubleshooting steps

Check logs

tail -f logs/backend.log
# In browser: F12 → Console

Restart all services

Ctrl+C

python -m uvicorn backend.main:app --reload
npm run dev --prefix frontend

Check connections

psql $DATABASE_URL -c "SELECT 1"

curl http://localhost:8000/health

curl http://localhost:5173

Read errors carefully

Understand the exact error message

Identify possible causes

Apply solutions step by step

Request support

support@gabanistore.com

operations@gabanilogistics.com

📚 Useful References

FastAPI Documentation

SQLAlchemy ORM Documentation

PostgreSQL Documentation

React Documentation

Vite Guide

Last Updated: March 7, 2026