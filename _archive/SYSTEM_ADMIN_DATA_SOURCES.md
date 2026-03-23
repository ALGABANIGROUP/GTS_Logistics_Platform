# 🎯 System Admin Bot - Data Sources Architecture
# EN

## 📋 EN **System Admin** EN:

```
┌─────────────────────────────────────────────────────────────────┐
│              SYSTEM ADMIN PANEL - DATA SOURCES                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  📊 HEALTH MONITORING                                          │
│  ├─ FROM: Maintenance Development Bot (maintenance_dev)        │
│  ├─ DATA: CPU, Memory, Disk, Uptime, Services Status          │
│  └─ ENDPOINT: /api/v1/admin/data-sources/health/*             │
│                                                                  │
│  👥 USER MANAGEMENT                                            │
│  ├─ FROM: PostgreSQL Database                                 │
│  ├─ DATA: Users, Statistics, Roles, Activity                 │
│  └─ ENDPOINT: /api/v1/admin/data-sources/users/*             │
│                                                                  │
│  🔐 SECURITY & AUDIT                                          │
│  ├─ FROM: Security Bot (security)                            │
│  ├─ DATA: Audit Logs, Alerts, Recommendations                │
│  └─ ENDPOINT: /api/v1/admin/data-sources/security/*          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 EN

### 1. Backend Routes EN
**EN:** `backend/routes/admin_data_sources.py` (EN)

#### EN) Health Monitoring Endpoints
```python
GET /api/v1/admin/data-sources/health/maintenance-bot
GET /api/v1/admin/data-sources/health/detailed-maintenance
```

**EN:**
```json
{
  "source": "maintenance_dev_bot",
  "health_status": "operational",
  "checks": {
    "system_services": {...},
    "performance": {
      "cpu_usage": 45,
      "memory_usage": 62,
      "disk_usage": 56
    },
    "scheduled_maintenance": {...}
  }
}
```

#### EN) User Management Endpoints
```python
GET /api/v1/admin/data-sources/users/database
GET /api/v1/admin/data-sources/users/statistics-database
```

**EN:**
```json
{
  "source": "database",
  "users": [
    {
      "id": 1,
      "email": "user@example.com",
      "full_name": "User Name",
      "role": "admin",
      "is_active": true,
      "created_at": "2026-02-02T..."
    }
  ],
  "summary": {
    "total_users": 25,
    "active_users": 25,
    "new_users_7d": 7,
    "growth_rate": "28%"
  }
}
```

#### EN) Security & Audit Endpoints
```python
GET /api/v1/admin/data-sources/security/audit-logs
GET /api/v1/admin/data-sources/security/alerts
GET /api/v1/admin/data-sources/security/recommendations
```

**EN:**
```json
{
  "source": "security_bot",
  "logs": [
    {
      "id": 1,
      "timestamp": "2026-02-02T14:30:00Z",
      "action": "LOGIN_SUCCESS",
      "severity": "low",
      "status": "success"
    }
  ],
  "alerts": [
    {
      "id": "alert-001",
      "severity": "critical",
      "title": "Multiple Failed Login Attempts",
      "status": "active"
    }
  ]
}
```

---

### 2. Frontend Service Layer Updates
**EN:** `frontend/src/services/adminService.js`

#### EN:
```javascript
// Health Monitoring from Maintenance Bot
adminService.getHealthFromMaintenanceBot()
adminService.getDetailedHealthFromMaintenance()

// User Management from Database
adminService.getUsersFromDatabase(page, limit, filters)
adminService.getUserStatisticsFromDatabase()

// Security & Audit from Security Bot
adminService.getAuditLogsFromSecurityBot(filters)
adminService.getSecurityAlertsFromSecurityBot()
adminService.getSecurityRecommendationsFromSecurityBot()
```

---

### 3. Frontend Components Updates

#### HealthMonitoring.jsx
```javascript
// EN:
const [maintenanceHealth, detailedFromMaintenance] = await Promise.all([
    adminService.getHealthFromMaintenanceBot(),
    adminService.getDetailedHealthFromMaintenance()
]);
```

#### UserManagement.jsx
```javascript
// EN:
const data = await adminService.getUsersFromDatabase(page, limit, filters);
const stats = await adminService.getUserStatisticsFromDatabase();
```

#### SecurityAudit.jsx
```javascript
// EN:
const [logsFromBot, alertsFromBot, recommendationsFromBot] = await Promise.all([
    adminService.getAuditLogsFromSecurityBot(filters),
    adminService.getSecurityAlertsFromSecurityBot(),
    adminService.getSecurityRecommendationsFromSecurityBot()
]);
```

---

## 🔄 Fallback Mechanism

EN fallback EN:

```javascript
if (data.error) {
    console.warn('Source unavailable, using original');
    const fallback = await adminService.originalMethod();
    // EN
}
```

---

## 📊 EN

```
┌──────────────────────────┐
│  System Admin Panel      │
├──────────────────────────┤
│                          │
│  ┌────────────────────┐  │
│  │ Health Monitoring  │  │
│  ├────────────────────┤  │
│  │ Source: Maint Bot  │──────────┐
│  │ Data: System Metrics           │
│  └────────────────────┘           │
│                          │        │
│  ┌────────────────────┐  │        │
│  │ User Management    │  │        │
│  ├────────────────────┤  │        │
│  │ Source: Database   │  │        │
│  │ Data: Users, Stats │  │        │
│  └────────────────────┘  │        │
│                          │        │
│  ┌────────────────────┐  │        │
│  │ Security & Audit   │  │        │
│  ├────────────────────┤  │        │
│  │ Source: Sec Bot    │  │        │
│  │ Data: Logs, Alerts │  │        │
│  └────────────────────┘  │        │
│                          │        │
└──────────────────────────┘        │
                                    │
       API LAYER                    │
       ↓                            │
┌──────────────────────────────────┘
│
├─ /api/v1/admin/data-sources/health/*
│  └─→ Connects to Maintenance Bot
│
├─ /api/v1/admin/data-sources/users/*
│  └─→ Queries Database directly
│
└─ /api/v1/admin/data-sources/security/*
   └─→ Connects to Security Bot
```

---

## 🚀 EN

### EN:
1. ✅ Backend routes EN `/api/v1/admin/data-sources/*`
2. ✅ Frontend services EN
3. ✅ Components EN fallback

### EN:
1. EN Maintenance Bot EN)
2. EN Security Bot EN
3. EN (caching) EN
4. EN
5. EN

---

## 📋 EN

| EN | EN | EN |
|-------|--------|--------|
| `backend/routes/admin_data_sources.py` | EN | ✅ EN |
| `backend/main.py` | EN | ✅ mounted |
| `frontend/src/services/adminService.js` | EN | ✅ methods EN |
| `frontend/src/components/.../HealthMonitoring.jsx` | EN | ✅ EN maintenance bot |
| `frontend/src/components/.../UserManagement.jsx` | EN | ✅ EN database |
| `frontend/src/components/.../SecurityAudit.jsx` | EN | ✅ EN security bot |

---

## 🧪 EN

### EN API EN:

```bash
# Health from Maintenance Bot
curl -H "Authorization: Bearer {token}" \
  http://localhost:8000/api/v1/admin/data-sources/health/maintenance-bot

# Users from Database
curl -H "Authorization: Bearer {token}" \
  http://localhost:8000/api/v1/admin/data-sources/users/database

# Security Alerts from Security Bot
curl -H "Authorization: Bearer {token}" \
  http://localhost:8000/api/v1/admin/data-sources/security/alerts
```

---

## 🔐 EN endpoints EN `Authorization` header
- EN endpoints EN `admin` role
- EN (sanitized) EN (safe error messages)

---

## 📞 EN:
- 📧 Email: support@gtsdispatcher.com
- 💬 Chat: Available 24/7

---

**EN:** 2026-02-02  
**EN:** ✅ EN  
**EN:** 1.0
