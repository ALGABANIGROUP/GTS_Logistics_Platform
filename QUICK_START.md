# 🚀 Quick Start Guide - Unified System

## ⚡ Quick Start (3 Steps Only)

### Method 1️⃣: Automatic Method (Recommended)

```bash
# In the root directory
python setup_and_run.py
```

This will:
- ✅ Set up virtual environments
- ✅ Install requirements
- ✅ Run Database Migrations
- ✅ Start Backend on 8000
- ✅ Start Frontend on 5173

---

### Method 2️⃣: Manual Method

#### Step 1: Run Backend
```bash
# Terminal 1
cd backend
python -m alembic upgrade head  # Run migrations once only
python main.py                  # Start server
```

#### Step 2: Start Frontend
```bash
# Terminal 2
cd frontend
npm install                     # once only
npm run dev
```

#### Step 3: Start Tests
```bash
# Terminal 3
python test_unified_system.py
```

---

## 📋 Detailed Steps

### 1. Database Preparation
```bash
cd backend
python -m alembic -c alembic.ini upgrade head
```

### 2. Start Backend
```bash
# From root folder
python backend/main.py

# Or from backend folder
cd backend
python main.py
```

**Server will be available at:**
- API: `http://127.0.0.1:8000`
- Docs: `http://127.0.0.1:8000/docs`

### 3. Start Frontend
```bash
# From root folder
cd frontend
npm run dev

# Or use yarn
yarn dev
```

**Frontend will be available at:**
- `http://127.0.0.1:5173`

### 4. Run Tests
```bash
python test_unified_system.py
```

---

## 🧪 Comprehensive Testing

### 1. Login Test
```bash
POST http://127.0.0.1:8000/auth/token
Content-Type: application/x-www-form-urlencoded

email=enjoy983@hotmail.com&password=password123
```

### 2. Test Available Systems
```bash
GET http://127.0.0.1:8000/api/v1/systems/available
Authorization: Bearer <TOKEN>
```

### 3. Test System Switch
```bash
POST http://127.0.0.1:8000/api/v1/systems/switch
Authorization: Bearer <TOKEN>
Content-Type: application/json

{
  "new_system": "tms"
}
```

### 4. Test Admin Dashboard
```bash
GET http://127.0.0.1:8000/api/v1/admin/overview
Authorization: Bearer <TOKEN>
```

---

## 🌐 Usage Flow

```
1. Login Page (http://127.0.0.1:5173/login)
   ↓ Enter email + password
   
2. System Selector (http://127.0.0.1:5173/system-selector)
   ↓ Choose GTS or TMS
   
3. Dashboard
   ├─ /dashboard (Main GTS)
   ├─ /tms/dashboard (TMS)
   └─ /admin/unified-dashboard (Admin)
```

---

## 🛠️ Troubleshooting

### Port 8000 busy
```bash
# On Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# On macOS/Linux
lsof -i :8000
kill -9 <PID>
```

### Port 5173 busy
```bash
# On Windows
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# On macOS/Linux
lsof -i :5173
kill -9 <PID>
```

### Database Error
```bash
cd backend
python -m alembic -c alembic.ini current
python -m alembic -c alembic.ini history
python -m alembic -c alembic.ini downgrade -1  # rollback one step
python -m alembic -c alembic.ini upgrade head   # upgrade to latest
```

### npm Error
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

---

## 📊 Available Routes

### Authentication
```
POST /auth/token                 - Login
POST /auth/refresh              - Refresh token
POST /auth/logout               - Logout
```

### Systems
```
GET  /api/v1/systems/available       - Available systems
POST /api/v1/systems/switch          - Switch system
GET  /api/v1/systems/selector        - Selector data
GET  /api/v1/systems/current         - Current system
```

### Admin
```
GET  /api/v1/admin/overview              - Overview
GET  /api/v1/admin/users/management      - User management
GET  /api/v1/admin/subscriptions/analytics - Subscription analytics
GET  /api/v1/admin/bots/status           - Bots status
GET  /api/v1/admin/shipments/analytics   - Shipment analytics
GET  /api/v1/admin/system-health         - System health
POST /api/v1/admin/broadcast-notification - Broadcast notification
```

---

## 📝 Test Data

### Test Accounts
```
Email:    enjoy983@hotmail.com
Password: password123

Or any account existing in the database
```

---

## 🎯 Next Steps

After successful startup:

1. ✅ Test login
2. ✅ Test system selection
3. ✅ Test system switching
4. ✅ Test admin dashboard
5. ✅ Test various functions

---

## 📞 Support and Help

For more information:
- 📖 [UNIFIED_SYSTEM_GUIDE.md](./UNIFIED_SYSTEM_GUIDE.md) - Comprehensive system guide
- 📚 [Swagger API Docs](http://127.0.0.1:8000/docs) - Complete API documentation
- 🐛 In case of errors, check Logs

---

## ⚙️ Requirements

### Backend
- Python 3.8+
- PostgreSQL (or any supported database)
- pip packages (from requirements.txt)

### Frontend
- Node.js 14+
- npm/yarn

### System
- RAM: 2GB+
- Internet: Connected (for external APIs)

---

**🎉 Congratulations! The system is ready for use**
