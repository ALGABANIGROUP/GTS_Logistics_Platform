
# 📚 Comprehensive GTS Unified System Operation Guide
# 🚀 Complete Operation Guide for GTS Unified System

---

## Table of Contents

1. [Basic Requirements](#basic-requirements)
2. [Installation and Setup](#installation-and-setup)
3. [Running the System](#running-the-system)
4. [Testing the System](#testing-the-system)
5. [Troubleshooting](#troubleshooting)
6. [Key Features](#key-features)
7. [Contact Information](#contact-information)
8. [Pre-Launch Checklist](#pre-launch-checklist)

---

## Basic Requirements

### Required Software:
- **Python 3.10+** - Core programming language
- **Node.js 18+** - For running the frontend
- **PostgreSQL 14+** - Database
- **Git** - Version control system

### System Requirements:
- RAM: 8GB or more
- Disk Space: 5GB
- Stable internet connection

---

## Installation and Setup

### 1. Clone the Project
```bash
git clone <repository-url>
cd GTS
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Requirements
```bash
pip install -r requirements.txt
pip install requests  # for testing
```

### 4. Environment Variables Setup
Create a `.env` file in the project root:
```env
# Database
ASYNC_DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/gts_db
DATABASE_URL=postgresql://user:password@localhost:5432/gts_db

# Server
BACKEND_PORT=8000
FRONTEND_URL=http://127.0.0.1:5173

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
EMAIL_FROM=noreply@gtsdispatcher.com
EMAIL_PASSWORD=your_app_password

# OpenAI (Optional)
OPENAI_API_KEY=sk-...

# Security
SECRET_KEY=your-super-secret-key-change-this
```

### 5. Database Setup
```bash
# Apply migrations
python -m alembic -c backend/alembic.ini upgrade head

# Create initial admin (Seed Admin)
python backend/tools/create_admin_user.py
```

---

## System Startup

### Method 1: Manual Startup

**Start Backend:**
```bash
# Activate virtual environment first
.venv\Scripts\activate  # Windows

# Start server
python backend/main.py
# or
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

**Start Frontend (in new window):**
```bash
cd frontend
npm run dev
```

**Result:**
- Backend: http://127.0.0.1:8000
- Frontend: http://127.0.0.1:5173
- API Docs: http://127.0.0.1:8000/docs

### Method 2: Using Scripts (Recommended)

**Windows (PowerShell):**
```bash
# Start full system
.\run-dev.ps1

# or start specific part
.\run-backend.ps1
.\run-frontend.ps1
```

### Method 3: Docker (if available)
```bash
# Build and start containers
docker-compose up -d

# Check status
docker-compose ps
```

---

## System Testing

### Comprehensive Test
```bash
# Run comprehensive test
python comprehensive_system_test.py
```

**Expected Result:**
```
✅ Backend connectivity - PASS
✅ Database connection - PASS
✅ User authentication - PASS
✅ Admin authentication - PASS
✅ Shipment creation - PASS
✅ Pricing tiers - PASS
✅ Email notifications - PASS
✅ Admin dashboard - PASS
✅ Frontend connectivity - PASS
✅ CORS configured - PASS
✅ AI Bots available - PASS

📊 Pass Rate: 100%
✅ ALL CRITICAL TESTS PASSED!
```

### Specific Tests

**Authentication Test:**
```bash
curl -X POST http://127.0.0.1:8000/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "email=test@gtsdispatcher.com&password=TestPass123!"
```

**Shipments List Test:**
```bash
curl -X GET http://127.0.0.1:8000/api/v1/shipments \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Dashboard Test:**
```bash
curl -X GET http://127.0.0.1:8000/api/v1/admin/dashboard \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

---

## Troubleshooting

### Problem: Cannot connect to server

**Solution:**
```bash
# Ensure virtual environment is activated
.venv\Scripts\activate

# Check port
netstat -ano | findstr :8000

# Kill process on port (if needed)
taskkill /PID <PID> /F
```

### Problem: Database error

**Solution:**
```bash
# Check connection
python -c "import psycopg2; print('OK')"

# Reapply migrations
python -m alembic -c backend/alembic.ini downgrade base
python -m alembic -c backend/alembic.ini upgrade head

# Recreate tables
python backend/init_db.py
```

### Problem: Email not working

**Solution:**
```bash
# Check email settings in .env
# - Ensure data is correct
# - Use Google app password

# Test email
python -c "from backend.services.unified_email import UnifiedEmailSystem; print('Email OK')"
```

### Problem: Frontend cannot connect to backend

**Solution:**
```bash
# Check CORS settings in .env
# - Ensure CORS is enabled
# - Check frontend URL

# Restart frontend
npm run dev
```

---

## Main Features

### 1️⃣ Unified Authentication System
```
✅ Secure login
✅ Encrypted passwords
✅ JWT Tokens
✅ System switching
✅ Multiple sessions
```

### 2️⃣ Load Boards
```
✅ Available Shipments display
✅ Advanced filtering
✅ Interactive map
✅ Price management
✅ Real-time Shipment tracking
```

### 3️⃣ Pricing and Subscriptions System
```
✅ Three plans (Starter, Professional, Enterprise)
✅ Dynamic price calculation
✅ Subscription management
✅ Financial reports
✅ Automatic invoices
```

### 4️⃣ Email Notifications
```
✅ Welcome new users
✅ Shipment confirmations
✅ Delivery alerts
✅ Daily reports
✅ Dynamic templates
```

### 5️⃣ Dashboard
```
✅ User management
✅ Statistics display
✅ Subscription management
✅ Log display
✅ Price management
```

### 6️⃣ AI System
```
✅ 10+ smart bots
✅ Natural language processing
✅ Smart predictions
✅ Automatic optimizations
✅ Analytical reports
```

---

## Contact Information

### Main API Endpoints

**Authentication:**
- `POST /auth/token` - Login
- `POST /auth/logout` - Logout
- `GET /auth/me` - Current user data

**Shipments:**
- `GET /api/v1/shipments` - Shipments list
- `POST /api/v1/shipments` - Create shipment
- `GET /api/v1/shipments/{id}` - Shipment details

**Management:**
- `GET /api/v1/admin/dashboard` - Dashboard
- `GET /api/v1/admin/users` - Users list
- `GET /api/v1/admin/statistics` - Statistics

**Email:**
- `POST /api/v1/email/send-welcome` - Send welcome
- `GET /api/v1/notifications/preferences` - Notification preferences

---

## Pre-Launch Checklist

```
[ ] Backend runs without errors
[ ] Frontend runs successfully
[ ] Authentication works
[ ] Database connected
[ ] Email works
[ ] All tests pass
[ ] Performance acceptable
[ ] Security achieved
[ ] Documentation complete
[ ] Backup exists
```

---

**Last Update:** January 8, 2026
**Version:** 1.0.0
**Status:** ✅ Production Ready
