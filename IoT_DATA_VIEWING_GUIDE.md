# 📱 IoT Data Viewing Guide - Dashboard
# Where to View IoT Data in Dashboard

## 🗂️ Main Pages for Data Display

### 1️⃣ **Map Page** (Real-time Tracking)
📍 **URL:** `http://localhost:5173/map`
- **File:** [frontend/src/pages/Map.jsx](frontend/src/pages/Map.jsx)
- **Component:** UnifiedShipmentMap
- **Features:**
  - Live GPS tracking for all shipments
  - Vehicle locations in real-time
  - Filter by shipment ID
  - Automatic updates every 5 seconds
  - Geofence visualization

```jsx
// Usage examples:
// View all shipments: http://localhost:5173/map
// View specific shipment: http://localhost:5173/map?shipment_id=123
```

**What You'll See:**
```
🗺️ Interactive Map with:
├─ Vehicle markers (with icons)
├─ Route lines (from pickup to delivery)
├─ Status indicators (color-coded)
├─ Real-time location updates
└─ Click for detailed info
```

---

### 2️⃣ **Main Dashboard**
📍 **URL:** `http://localhost:5173/dashboard`
- **File:** [frontend/src/pages/Dashboard.jsx](frontend/src/pages/Dashboard.jsx)
- **Features:**
  - Total shipments count
  - Active documents
  - System statistics
  - Quick stats cards

**Cards Displayed:**
```javascript
{
  shipments: { value: "42", helper: "Total shipments in system" },
  documents: { value: "156", helper: "Uploaded documents" },
  inventory: { value: "1,234", helper: "Items in stock" },
  activeUsers: { value: "25", helper: "Users online now" }
}
```

---

### 3️⃣ **Dispatch Board**
📍 **URL:** `http://localhost:5173/dispatch`
- **File:** [frontend/src/pages/Dispatch.jsx](frontend/src/pages/Dispatch.jsx)
- **Features:**
  - Kanban-style shipment board
  - 5 status columns
  - Drag-and-drop (future)
  - Real-time status updates
  - Driver assignment

**Status Columns:**
```
┌──────────────────────────────────────────────────────┐
│ Unassigned │ Assigned │ In Transit │ Delivered │ Cancelled │
├──────────────────────────────────────────────────────┤
│ • Shipment 1  │ • Shipment 5  │ • Shipment 8  │ ✓ Shipment 12 │ ✗ Shipment 15 │
│ • Shipment 2  │ • Shipment 6  │ • Shipment 9  │ ✓ Shipment 13 │        │
│ • Shipment 3  │ • Shipment 7  │               │ ✓ Shipment 14 │        │
└──────────────────────────────────────────────────────┘
```

---

### 4️⃣ **Fleet Management**
📍 **URL:** `http://localhost:5173/fleet`
- **File:** [frontend/src/pages/Fleet.jsx](frontend/src/pages/Fleet.jsx)
- **Features:**
  - Vehicle fleet overview
  - Maintenance tracking
  - Fuel consumption
  - Driver assignments
  - Expense tracking

---

### 5️⃣ **System Admin Panel**
📍 **URL:** `http://localhost:5173/ai-bots/system-admin`
- **File:** [frontend/src/components/bots/panels/system-admin/SystemAdminPanel.jsx](frontend/src/components/bots/panels/system-admin/SystemAdminPanel.jsx)
- **Features:**
  - System health metrics
  - User statistics
  - Database status
  - Resource utilization

**Data Cards:**
```
┌─────────────────────────────────────┐
│ System Health: 98%                  │
│ Active Users: 25                    │
│ Database Size: 290 GB               │
│ CPU Usage: 45%                      │
│ Memory: 62%                         │
│ Disk: 290 GB                        │
└─────────────────────────────────────┘
```

**Backend API Endpoints:**
```bash
GET /api/v1/admin/health/system          # CPU, Memory, Disk
GET /api/v1/admin/health/database        # Table counts
GET /api/v1/admin/users/statistics       # User stats
GET /api/v1/admin/dashboard/stats        # Overall dashboard
GET /api/v1/admin/users/list             # User list
```

---

### 6️⃣ **Information Coordinator (Operational Dashboard)**
📍 **URL:** `/ai-bots/information-coordinator`
- **File:** [frontend/src/components/bots/panels/information-coordinator/OperationalDashboard.jsx](frontend/src/components/bots/panels/information-coordinator/OperationalDashboard.jsx)
- **Features:**
  - Live operational metrics
  - Key Performance Indicators (KPIs)
  - System alerts
  - Real-time statistics
  - Metric filtering

**What's Available:**
```javascript
{
  KPIs: ['On-time delivery rate', 'Average shipment value', 'Customer satisfaction'],
  Metrics: ['Active shipments', 'Pending orders', 'System load'],
  Alerts: ['Critical', 'High', 'Medium', 'Low'],
  TimeRange: ['Today', 'This week', 'This month', 'Custom']
}
```

---

## 📊 Data Points Available

### A) Tracking Data
- **Current Location** (GPS coordinates)
- **Shipment Status** (Created → Picked Up → In Transit → Delivered)
- **Timestamp** (Creation, update, delivery time)
- **Distance Traveled** (in kilometers/miles)
- **ETA** (Estimated Time of Arrival)
- **Route Progress** (percentage complete)

### B) Vehicle Data
- **Vehicle ID** (License plate, Fleet ID)
- **Assigned Driver**
- **Current Status**
- **GPS Location** (real-time)
- **Speed** (current)
- **Fuel Level**
- **Maintenance Status**

### C) System Data
- **CPU Usage** (percentage)
- **Memory Usage** (GB/percentage)
- **Disk Space** (used/free)
- **Database Health**
- **Active Connections**
- **API Response Time**
- **Error Rate**

### D) User Data
- **Total Users** (count)
- **Active Users** (currently online)
- **User Roles** (distribution)
- **Last Activity** (timestamp)
- **Login Status**

---

## 🔌 API Endpoints for Data Retrieval

### Tracking Endpoints
```bash
# Get all shipments
GET /api/v1/tracking/shipments
    ?status=in_transit
    &limit=50
    &offset=0

# Get shipment details
GET /api/v1/tracking/shipments/{shipment_id}

# Get tracking events for shipment
GET /api/v1/tracking/events/{shipment_id}
    ?limit=100
    &sort=desc
```

### System Endpoints
```bash
# System health metrics
GET /api/v1/admin/health/system
    # Returns: CPU%, Memory%, Disk%

# Database statistics
GET /api/v1/admin/health/database
    # Returns: Table counts, DB size

# User statistics
GET /api/v1/admin/users/statistics
    # Returns: Total, Active, New (7d), Inactive

# Dashboard overview
GET /api/v1/admin/dashboard/stats
    # Returns: Combined metrics
```

### Dispatch Endpoints
```bash
# Get dispatch board
GET /api/v1/dispatch/board
    # Returns: Shipments grouped by status

# Assign shipment
POST /api/v1/dispatch/assign
    {
      "shipment_id": 123,
      "driver_id": 456,
      "eta": "2026-02-02T18:30:00"
    }
```

---

## 🔄 Real-Time Data Updates

### Methods Used:

#### 1. **WebSocket Connection** (Live Updates)
```javascript
// For live events (bots.*, commands.*)
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/live');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    // Update UI immediately
    setShipmentData(data);
};
```

#### 2. **REST API Polling** (Periodic Updates)
```javascript
// Poll every 5 seconds
useEffect(() => {
    const interval = setInterval(async () => {
        const data = await axiosClient.get('/api/v1/admin/dashboard/stats');
        setDashboardData(data);
    }, 5000);
    return () => clearInterval(interval);
}, []);
```

#### 3. **React Query** (with Caching)
```javascript
import { useQuery } from '@tanstack/react-query';

const { data, isLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => axiosClient.get('/api/v1/admin/dashboard/stats'),
    refetchInterval: 5000  // Refresh every 5 seconds
});
```

---

## 📱 Steps to Access IoT Data

### Method 1️⃣: Via Map Page
```
1. Navigate to http://localhost:5173/map
2. See all vehicles and shipments on interactive map
3. Click any marker for detailed information
4. Data updates automatically every 5 seconds
5. Filter by shipment ID using query parameter
```

### Method 2️⃣: Via Dispatch Board
```
1. Go to http://localhost:5173/dispatch
2. View shipments organized by status columns
3. Click "Refresh" to get latest data
4. Assign shipments to drivers directly
5. See real-time status changes
```

### Method 3️⃣: Via System Admin Panel
```
1. Navigate to http://localhost:5173/ai-bots/system-admin
2. View system metrics and health
3. See user statistics
4. Data refreshes automatically every 30 seconds
5. Get alerts if metrics exceed thresholds
```

### Method 4️⃣: Via Information Coordinator
```
1. Go to /ai-bots/information-coordinator
2. View live operational metrics
3. See KPIs and alerts
4. Filter by time range
5. Get real-time insights
```

---

## 🎯 Data Availability Matrix

| Page | Tracking | System | Users | KPIs | Alerts |
|------|----------|--------|-------|------|--------|
| Map | ✅ | ❌ | ❌ | ❌ | ❌ |
| Dashboard | ⚠️ | ✅ | ⚠️ | ❌ | ❌ |
| Dispatch | ✅ | ❌ | ❌ | ❌ | ⚠️ |
| Fleet | ✅ | ⚠️ | ⚠️ | ❌ | ❌ |
| System Admin | ❌ | ✅ | ✅ | ❌ | ❌ |
| Info Coordinator | ❌ | ❌ | ❌ | ✅ | ✅ |

**Legend:** ✅ Full data | ⚠️ Partial data | ❌ Not available

---

## ⚙️ Advanced Configuration

### Custom Refresh Intervals
```javascript
// In your component
const [refreshInterval, setRefreshInterval] = useState(5000); // 5 seconds

useEffect(() => {
    const timer = setInterval(loadData, refreshInterval);
    return () => clearInterval(timer);
}, [refreshInterval]);
```

### Data Filtering
```javascript
// Filter by status
const activeShipments = shipments.filter(s => s.status === 'in_transit');

// Filter by date range
const todaysShipments = shipments.filter(s => 
    isToday(new Date(s.created_at))
);

// Filter by location
const nearbyVehicles = vehicles.filter(v => 
    calculateDistance(v.location, userLocation) < 5 // 5km radius
);
```

### Data Export
```javascript
// Export to CSV
const exportCSV = (data) => {
    const csv = Papa.unparse(data); // using PapaParse library
    downloadFile(csv, 'data.csv', 'text/csv');
};

// Export to JSON
const exportJSON = (data) => {
    downloadFile(JSON.stringify(data, null, 2), 'data.json', 'application/json');
};
```

---

## 🚀 Performance Tips

1. **Use Caching**: Cache API responses to reduce server load
2. **Pagination**: Load data in chunks, not all at once
3. **Debouncing**: Debounce search/filter inputs
4. **Lazy Loading**: Load images/data on demand
5. **Compression**: Enable gzip for API responses

---

## 🔐 Data Security

- All API calls include JWT Bearer token authentication
- Admin role required for system metrics
- Data is encrypted in transit (HTTPS/WSS)
- Database queries are parameterized to prevent SQL injection
- Rate limiting on API endpoints

---

## 🐛 Troubleshooting

### Map not showing data?
```bash
# Check WebSocket connection
# Check browser console for errors
# Verify API endpoint returns data:
curl http://localhost:8000/api/v1/tracking/shipments
```

### Dispatch board is empty?
```bash
# Check if shipments exist in database
# Verify dispatch service is running
# Check API response:
curl http://localhost:8000/api/v1/dispatch/board
```

### System metrics showing error?
```bash
# Verify admin endpoints are mounted
# Check user has 'admin' role
# Verify database connection is working
```

---

## 📞 Support & Resources

- **Documentation**: [API_REFERENCE_COMPLETE.md](API_REFERENCE_COMPLETE.md)
- **Backend API**: http://localhost:8000/docs (Swagger UI)
- **Email Support**: support@gtsdispatcher.com
- **Chat Support**: Available 24/7
- **Status Page**: https://status.gtsdispatcher.com

---

**Last Updated:** 2026-02-02  
**Status:** ✅ All features ready for production  
**Version:** 1.0.0
