# 📱 EN IoT EN
# Guide to View IoT Data in Dashboard

## 🗂️ EN

### 1️⃣ **EN (Map Page)**
📍 **EN:** `http://localhost:5173/map`
- **EN:** [frontend/src/pages/Map.jsx](frontend/src/pages/Map.jsx)
- **EN:**
  - EN (Real-time) EN

```jsx
// EN
// http://localhost:5173/map?shipment_id=123
// EN
```

---

### 2️⃣ **EN (Main Dashboard)**
📍 **EN:** `http://localhost:5173/dashboard`
- **EN:** [frontend/src/pages/Dashboard.jsx](frontend/src/pages/Dashboard.jsx)
- **EN:**
  - EN

```jsx
// EN:
- EN (Shipments)
- EN (Documents)
- EN (Inventory)
- EN (Active Users)
```

---

### 3️⃣ **EN (Dispatch Board)**
📍 **EN:** `http://localhost:5173/dispatch`
- **EN:** [frontend/src/pages/Dispatch.jsx](frontend/src/pages/Dispatch.jsx)
- **EN:**
  - EN ETA
  - EN

```
EN:
┌─────────────────────────────────────┐
│ Unassigned  │ Assigned  │ In Transit │
│ Delivered   │ Cancelled │            │
└─────────────────────────────────────┘
```

---

### 4️⃣ **EN (Fleet)**
📍 **EN:** `http://localhost:5173/fleet`
- **EN:** [frontend/src/pages/Fleet.jsx](frontend/src/pages/Fleet.jsx)
- **EN:**
  - EN

---

### 5️⃣ **EN (Information Coordinator)**
📍 **EN:** `/ai-bots/information-coordinator`
- **EN:** [frontend/src/components/bots/panels/information-coordinator/OperationalDashboard.jsx](frontend/src/components/bots/panels/information-coordinator/OperationalDashboard.jsx)
- **EN:**
  - EN (KPIs)
  - EN

```javascript
// EN:
- Operational Metrics
- KPIs (Key Performance Indicators)
- System Alerts
- Real-time Statistics
```

---

### 6️⃣ **EN (System Admin)**
📍 **EN:** `http://localhost:5173/ai-bots/system-admin`
- **EN:** [frontend/src/components/bots/panels/system-admin/SystemAdminPanel.jsx](frontend/src/components/bots/panels/system-admin/SystemAdminPanel.jsx)
- **EN:**
  - EN (CPU, Memory, Disk)
  - EN

```
EN:
├─ System Health: 98%
├─ Active Users: 25
├─ Database Size: 290 GB
├─ CPU Usage: 45%
├─ Memory: 62%
└─ Disk: 290 GB
```

---

## 📊 EN

### EN Tracking (EN)
- **EN**
- **EN** (Created, Picked Up, In Transit, Delivered, Cancelled)
- **EN**
- **EN**
- **ETA (EN)**

### EN (Vehicles)
- **EN**
- **EN**
- **EN**
- **EN GPS**
- **EN**
- **EN**

### EN (System)
- **EN CPU**
- **EN**
- **EN**
- **EN**
- **EN**

---

## 🔌 API Endpoints EN

### EN (Tracking)
```bash
GET /api/v1/tracking/shipments
GET /api/v1/tracking/shipments/{id}
GET /api/v1/tracking/events/{shipment_id}
```

### EN (System)
```bash
GET /api/v1/admin/health/system
GET /api/v1/admin/health/database
GET /api/v1/admin/users/statistics
GET /api/v1/admin/dashboard/stats
```

### EN (Dispatch)
```bash
GET /api/v1/dispatch/board
POST /api/v1/dispatch/assign
```

---

## 🔄 EN

### EN:

#### 1. **WebSocket** (EN)
```javascript
// Connection to /api/v1/ws/live
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/live');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    // EN
};
```

#### 2. **REST API Polling** (EN)
```javascript
// EN 5 EN
setInterval(async () => {
    const data = await axiosClient.get('/api/v1/admin/dashboard/stats');
    setDashboardData(data);
}, 5000);
```

#### 3. **React Query** (EN Cache)
```javascript
const { data, isLoading } = useQuery('dashboard', 
    () => axiosClient.get('/api/v1/admin/dashboard/stats'),
    { refetchInterval: 5000 }
);
```

---

## 📱 EN

### EN 1️⃣: EN
```
1. EN http://localhost:5173/map
2. EN
3. EN
4. EN 5 EN
```

### EN 2️⃣: EN
```
1. EN http://localhost:5173/dispatch
2. EN
3. EN "Refresh" EN
4. EN
```

### EN 3️⃣: EN
```
1. EN http://localhost:5173/ai-bots/system-admin
2. EN
3. EN
4. EN 30 EN
```

### EN 4️⃣: EN
```
1. EN /ai-bots/information-coordinator
2. EN
3. EN
4. EN (KPIs) EN
```

---

## 🔍 EN

| EN | EN |
|--------|-----------------|
| **Map** | EN GPSEN |
| **Dispatch** | EN ETAEN |
| **Dashboard** | EN |
| **Fleet** | EN |
| **System Admin** | EN |
| **Information Coordinator** | KPIsEN |

---

## ⚙️ EN

### EN
```javascript
// EN
const [refreshInterval, setRefreshInterval] = useState(5000); // 5 EN

useEffect(() => {
    const interval = setInterval(loadData, refreshInterval);
    return () => clearInterval(interval);
}, [refreshInterval]);
```

### EN
```javascript
// EN
const filteredShipments = shipments.filter(s => s.status === 'in_transit');

// EN
const filteredByDate = shipments.filter(s => 
    new Date(s.updated_at) > new Date(Date.now() - 24*60*60*1000)
);
```

### EN
```javascript
// EN CSV
const exportToCSV = (data) => {
    const csv = data.map(row => Object.values(row).join(',')).join('\n');
    download(csv, 'data.csv');
};
```

---

## 🚀 EN

- ✅ EN
- ✅ EN
- ✅ EN
- ✅ EN
- ✅ API EN

---

## 📞 EN:
- 📧 Email: support@gtsdispatcher.com
- 💬 Chat: Available 24/7
- 📱 Phone: +1-XXX-XXX-XXXX

---

**EN:** 2026-02-02
**EN:** ✅ EN
