# 📊 EN
# IoT Data Dashboard Quick Reference

## EN

### EN

```
╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                    PAGES & DATA AVAILABILITY MATRIX                                                                      ║
╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ EN (Page)         │ EN (URL)                     │ EN (Available Data)                                              ║
╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ 🗺️ Map (EN)     │ /map                            │ • GPS Location (EN)                                                      ║
║                       │                                 │ • Shipment Status (EN)                                              ║
║                       │                                 │ • Route Visualization (EN)                                          ║
║                       │                                 │ • ETA Tracking (EN)                                        ║
║                       │                                 │ • Real-time Updates (EN 5 EN)                                   ║
║                       │                                 │ • Driver Info (EN)                                              ║
╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ 📦 Dispatch (EN)│ /dispatch                       │ • Unassigned Shipments (EN)                                  ║
║                       │                                 │ • Assigned Shipments (EN)                                          ║
║                       │                                 │ • In Transit (EN)                                                 ║
║                       │                                 │ • Delivered (EN)                                                   ║
║                       │                                 │ • Cancelled (EN)                                                          ║
║                       │                                 │ • Driver Assignment (EN)                                          ║
║                       │                                 │ • Notes & ETA (EN)                                    ║
╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ 📊 Dashboard (EN)│ /dashboard                      │ • Total Shipments (EN)                                         ║
║                       │                                 │ • Total Documents (EN)                                         ║
║                       │                                 │ • Inventory Count (EN)                                             ║
║                       │                                 │ • Active Users (EN)                                        ║
║                       │                                 │ • System Status (EN)                                               ║
╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ ⚙️ System Admin      │ /ai-bots/                      │ • CPU Usage (EN)                                              ║
║    (EN)          │ system-admin                    │ • Memory Usage (EN)                                           ║
║                       │                                 │ • Disk Space (EN)                                                 ║
║                       │                                 │ • Total Users (EN)                                         ║
║                       │                                 │ • Active Users (EN)                                        ║
║                       │                                 │ • Database Health (EN)                                    ║
║                       │                                 │ • System Health Score (EN)                                   ║
║                       │                                 │ • New Users (7 days) (EN)                                       ║
╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ 🚗 Fleet (EN)   │ /fleet                          │ • Vehicle List (EN)                                            ║
║                       │                                 │ • Driver Assignments (EN)                                   ║
║                       │                                 │ • Maintenance Status (EN)                                        ║
║                       │                                 │ • Fuel Consumption (EN)                                       ║
║                       │                                 │ • Expenses (EN)                                                        ║
║                       │                                 │ • Recent Activity (EN)                                         ║
╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ ℹ️ Information       │ /ai-bots/                      │ • Live KPIs (EN)                                      ║
║    Coordinator       │ information-coordinator         │ • System Alerts (EN)                                           ║
║    (EN)       │                                 │ • Operational Metrics (EN)                                   ║
║                       │                                 │ • Performance Trends (EN)                                    ║
║                       │                                 │ • Real-time Statistics (EN)                                    ║
║                       │                                 │ • Alert Notifications (EN)                                 ║
╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
```

---

## 📈 EN

```
╔═══════════════════════════════════════════════════════════════╗
║              UPDATE FREQUENCIES (EN)              ║
╠═══════════════════════════════════════════════════════════════╣
║ Page              │ Update Frequency │ Method                 ║
╠═══════════════════════════════════════════════════════════════╣
║ Map (EN)    │ 5 seconds       │ WebSocket / Polling   ║
║ Dispatch (EN) │ Real-time      │ WebSocket            ║
║ Dashboard         │ 10 seconds      │ REST API Polling     ║
║ System Admin      │ 30 seconds      │ REST API Polling     ║
║ Fleet             │ 10 seconds      │ REST API Polling     ║
║ Info Coordinator  │ 5 seconds       │ WebSocket            ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## 🔌 EN

### GPS & Location Data (EN)
```
┌─────────────────────────────────────────────┐
│ Location Data Available:                     │
├─────────────────────────────────────────────┤
│ ✅ Latitude (EN)                     │
│ ✅ Longitude (EN)                    │
│ ✅ Accuracy (EN)                   │
│ ✅ Timestamp (EN)                 │
│ ✅ Speed (EN)                          │
│ ✅ Heading (EN)                       │
│ ✅ Distance Traveled (EN)  │
└─────────────────────────────────────────────┘
```

### Shipment Status Data (EN)
```
┌─────────────────────────────────────────────┐
│ Status Tracking:                             │
├─────────────────────────────────────────────┤
│ 📋 Created (EN)                    │
│ 🏪 Picked Up (EN)                │
│ 🚗 In Transit (EN)                │
│ 🔴 Delayed (EN)                        │
│ ✅ Delivered (EN)                 │
│ ❌ Cancelled (EN)                       │
└─────────────────────────────────────────────┘
```

### System Health Metrics (EN)
```
┌─────────────────────────────────────────────┐
│ System Metrics Available:                    │
├─────────────────────────────────────────────┤
│ 💻 CPU Usage (%)                           │
│ 🧠 Memory Usage (%)                        │
│ 💾 Disk Usage (%)                          │
│ 👥 Connected Users                         │
│ 📊 Active Connections                      │
│ ⏱️  API Response Time (ms)                 │
│ 📉 Error Rate (%)                          │
│ 🔌 Database Connection Status              │
└─────────────────────────────────────────────┘
```

---

## 🎯 EN

### EN 1: EN
```
EN:
1. EN: http://localhost:5173/map?shipment_id=123
2. EN #123
3. EN
4. EN
5. EN 5 EN
```

### EN 2: EN
```
EN:
1. EN: http://localhost:5173/dispatch
2. EN 5 EN)
3. EN
4. EN
5. EN
```

### EN 3: EN
```
EN:
1. EN: http://localhost:5173/ai-bots/system-admin
2. EN 8 EN:
   - System Health Score
   - Total Users
   - Active Users
   - CPU Usage
   - Memory Usage
   - Disk Space
   - Database Health
   - Growth Rate
3. EN 30 EN
4. EN
```

### EN 4: EN
```
EN:
1. EN: /ai-bots/information-coordinator
2. EN:
   - On-time Delivery Rate (EN)
   - Average Shipment Value (EN)
   - Customer Satisfaction (EN)
   - Active Shipments (EN)
3. EN
4. EN
```

---

## 📱 EN

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃         QUICK ACCESS CHEAT SHEET               ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ 🗺️  EN              → /map           ┃
┃ 📦 EN              → /dispatch      ┃
┃ 📊 EN             → /dashboard     ┃
┃ ⚙️  EN              → /ai-bots/      ┃
┃                               system-admin     ┃
┃ 🚗 EN           → /fleet         ┃
┃ 📈 EN             → /ai-bots/      ┃
┃                               info-coordinator ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

---

## 🔐 EN

```
┌─────────────────────────────────────────────┐
│ Authentication Requirements:                │
├─────────────────────────────────────────────┤
│ ✅ JWT Token (EN localStorage)            │
│ ✅ Admin Role (EN)   │
│ ✅ Active Session (EN)             │
│ ✅ Network Connection (EN)      │
└─────────────────────────────────────────────┘
```

---

## 🚀 EN

```bash
# EN
curl http://localhost:8000/api/v1/system/readiness

# EN
open http://localhost:5173/map

# EN
open http://localhost:5173/ai-bots/system-admin
```

---

**EN:** 2026-02-02  
**EN:** 1.0  
**EN:** ✅ EN
