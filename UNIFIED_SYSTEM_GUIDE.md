# 🌐 GTS Unified System -Gabani Transport Solutions (GTS)


## 📋 Overview

**The Unified System** combines two main systems under one interface:
- **Main GTS** 🏢 - Partner and customer management
- **TMS** 🚚 - Comprehensive transportation management system

---

## 🏗️ Technical Architecture

### 1. Unified Authentication
```
User Login → Unified Auth System → Single JWT Token
                                  ↓
                        Multiple Systems Access
                        (GTS + TMS)
```

**Files:**
- `backend/auth/unified_auth.py` - Central authentication system
- `backend/models/unified_models.py` - Unified models

### 2. System Switching System
```
User selects System → System Switcher → New JWT Token
                                       ↓
                          Redirect to System Dashboard
```

**Files:**
- `backend/routes/system_switcher.py` - Switching APIs
- `frontend/src/pages/SystemSelector.jsx` - Selection interface

### 3. Unified Database
```sql
unified_users
├── Basic user information
└── Last login date

user_systems_access
├── System (gts_main, tms)
├── Permission level
└── Subscription plan

tms_subscriptions
├── Plan information
└── Available features

auth_audit_log
└── Login and activity log
```

---

## 🔐 Permission Systems

### Permission Levels

| Level | Permissions | Usage |
|-------|-------------|-------|
| **VIEW_ONLY** | View only | Guest or trial |
| **QUICK_RUN** | Quick run | Starter Plan |
| **CONTROL_PANEL** | Full panel | Professional Plan |
| **CONFIGURE** | Settings & integration | Enterprise Plan |

### Three Packages

#### 1. 📦 Starter - $99/month
```
- Maximum: 100 shipments/month
- Team: 3 members
- Available Bots:
  ✓ Customer service (quick run)
  ✓ Document manager (quick run)
  ✓ Shipping broker (quick run)
- Features:
  ✓ Basic tracking
  ✓ Email notifications
  ✗ API access
  ✗ Custom reports
```

#### 2. 💼 Professional - $299/month
```
- Maximum: 1000 shipments/month
- Team: 10 members
- Available Bots:
  ✓ All Bots (full panel)
  ✓ Finance bot
  ✓ Sales team
- Features:
  ✓ All Starter features
  ✓ API Access
  ✓ Custom reports
  ✓ Advanced automation
```

#### 3. 🚀 Enterprise - $799/month
```
- Maximum: Unlimited
- Team: Unlimited
- Available Bots:
  ✓ All Bots (full settings)
  ✓ General manager
  ✓ Maintenance bot
- Features:
  ✓ All Professional features
  ✓ Webhooks
  ✓ SSO
  ✓ Custom support
  ✓ Custom integrations
```

---

## 🚀 Basic Routes

### Registration and Login
```
POST /auth/token
├── Input: email, password
└── Output: JWT Token + Systems

GET /api/v1/systems/selector
├── Output: List of available systems
└── Current: Currently selected system
```

### System Switching
```
GET /api/v1/systems/available
├── Available systems
└── Complete information

POST /api/v1/systems/switch
├── Input: new_system
└── Output: New JWT Token
```

### Admin Dashboard
```
GET /api/v1/admin/overview
├── GTS and TMS statistics
└── Comprehensive numbers

GET /api/v1/admin/subscriptions/analytics
├── Subscription distribution
└── Revenue and growth

GET /api/v1/admin/users/management
├── Complete list of all users
└── Full information

GET /api/v1/admin/system-health
├── Server health
└── Performance metrics
```

---

## 🛠️ Installation Steps

### 1. Run Migrations
```bash
cd backend
python -m alembic upgrade head
```

### 2. Update `main.py`
```python
# Add to backend/main.py
from backend.routes.system_switcher import router as switcher_router
from backend.routes.admin_unified import router as admin_router

app.include_router(switcher_router)
app.include_router(admin_router)
```

### 3. Start Servers
```bash
# Backend
python backend/main.py

# Frontend
cd frontend && npm run dev
```

### 4. Access Application
```
http://127.0.0.1:5173/
↓
System Selector
↓
GTS Dashboard or TMS Dashboard
```

---

## 📊 Complete Workflow

### Regular User
```
1. Login
   → email + password

2. Select System
   → GTS or TMS

3. Use System
   → According to permissions

4. Switch System (optional)
   → POST /api/v1/systems/switch
```

### Administrator
```
1. Login
   → email + password

2. Select Admin Dashboard
   → Admin Dashboard

3. Manage:
   ✓ Users
   ✓ Subscriptions
   ✓ Bots
   ✓ Statistics
   ✓ System health
```

---

## 🔒 Security

### Geographic Control
```python
# Only for Load Board in TMS
# Allowed countries: US, CA
def geo_restrict_load_board(request):
    if not in_allowed_country(request.ip):
        raise PermissionError("Not allowed in this country")
```

### Rate Limiting
```
super_admin: 30 req/min
admin:       20 req/min
manager:     10 req/min
user:        5 req/min
```

---

## 📁 File Structure

```
backend/
├── auth/
│   └── unified_auth.py          ← Central auth system
├── models/
│   └── unified_models.py         ← Unified models
├── routes/
│   ├── system_switcher.py        ← Switching APIs
│   └── admin_unified.py          ← Admin dashboard
├── tms/
│   └── core/
│       └── tms_core.py           ← TMS Core
└── alembic/
    └── versions/
        └── 003_unified_auth.py   ← Migration

frontend/
├── src/
│   └── pages/
│       ├── SystemSelector.jsx    ← System selector
│       ├── SystemSelector.css
│       └── admin/
│           ├── UnifiedAdminDashboard.jsx
│           └── UnifiedAdminDashboard.css
```

---

## 🧪 Testing

### Login Test
```bash
POST http://127.0.0.1:8000/auth/token
Content-Type: application/x-www-form-urlencoded

email=user@example.com&password=password123
```

### System Selection Test
```bash
GET http://127.0.0.1:8000/api/v1/systems/selector
Authorization: Bearer <TOKEN>
```

### Switching Test
```bash
POST http://127.0.0.1:8000/api/v1/systems/switch
Authorization: Bearer <TOKEN>
Content-Type: application/json

{
  "new_system": "tms"
}
```

---

## 📈 Next Phase

1. ✅ Unified authentication system
2. ✅ Database tables
3. ✅ System switching system
4. ✅ System selection interface
5. ✅ Unified admin dashboard
6. ⏳ Billing and payment system
7. ⏳ Additional integrations (Google Maps, Email)
8. ⏳ Advanced reporting

---

## 📞 Support

For more information:
- 📖 [Complete Documentation](./DOCUMENTATION.md)
- 🐛 [Common Issues](./TROUBLESHOOTING.md)
- 💬 [FAQ](./FAQ.md)
