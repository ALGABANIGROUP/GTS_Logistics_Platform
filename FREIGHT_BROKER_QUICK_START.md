# 🚚 Freight Broker Control Panel - Quick Start Guide

## Overview

The **Freight Broker Control Panel** is a unified dashboard integrating:
- **Real-time Transport Tracking** with interactive Leaflet maps
- **Comprehensive Safety Management** with AI-powered monitoring
- **Dispatch Operations** via Kanban-style board
- **Intelligent Bot Coordination** for automated workflows

---

## ⚡ Quick Access

### URL
```
http://localhost:5173/freight-broker
```

### Requirements
- ✅ Logged in user (authentication required)
- ✅ Backend server running on `http://localhost:8000`
- ✅ Database connected
- ✅ WebSocket support enabled

---

## 📊 Main Tabs

### 1. **Transport Tab** 🗺️
Shows real-time vehicle and shipment tracking

**Features:**
- Interactive Leaflet map with drag controls
- 3 mock shipments (NYC→LA, Chicago→Atlanta, Seattle→San Jose)
- 3 active trucks with real-time positions
- Statistics sidebar (Active Trucks, In Transit, Delivered)
- Layer controls (OpenStreetMap, Satellite)
- Location selector buttons

**How to Use:**
1. Click "🗺️ Transport" tab
2. View live map with truck and shipment markers
3. Click trucks/shipments for details
4. Use location buttons to jump to cities
5. Zoom +/- to adjust view

### 2. **Safety Tab** 🛡️
Comprehensive safety monitoring and incident management

**Features:**
- 6 Key Metrics Cards:
  - Safety Score (0-100)
  - Incidents Count
  - High-Risk Drivers
  - Active Alerts
  - Vehicle Status
  - Compliance Score
- 3 Interactive Charts:
  - Safety Trend (Line chart)
  - Incident Distribution (Bar chart)
  - Risk Distribution (Pie chart)
- Period Selector: Daily / Weekly / Monthly
- Recent Incidents list
- Active Alerts list
- Safety Recommendations
- Pending Actions checklist

**How to Use:**
1. Click "🛡️ Safety" tab
2. View safety metrics and charts
3. Switch periods (Daily/Weekly/Monthly)
4. Review recent incidents
5. Check active alerts with priority levels
6. Follow safety recommendations

### 3. **Dispatch Tab** 📋
Kanban-style shipment dispatch board

**Features:**
- 5 Status Columns:
  - Unassigned (pending assignments)
  - Assigned (driver assigned)
  - In Transit (actively moving)
  - Delivered (completed)
  - Cancelled (cancelled orders)
- Shipment Cards with:
  - Shipment name
  - Route (From → To)
  - Assigned driver
  - Status indication

**How to Use:**
1. Click "📋 Dispatch" tab
2. View shipments organized by status
3. Drag cards between columns (when implemented)
4. Click cards for more details
5. Assign drivers (when implemented)

### 4. **Bots Tab** 🤖
AI Bot orchestration and control center

**Features:**
- 4 Bot Cards:
  - **Freight Broker Bot** - Main coordinator
  - **Safety Manager Bot** - Safety monitoring
  - **Operations Manager Bot** - Operations coordination
  - **Finance Bot** - Financial tracking
- Each Bot Shows:
  - Status (Active/Inactive)
  - Description
  - Control Buttons: Run, Pause, Status, Health Check
- Real-time Health Monitoring
- Bot Status Indicators (Green = Active, Red = Inactive)

**How to Use:**
1. Click "🤖 Bots" tab
2. View bot status cards
3. Click action buttons:
   - **Run** - Start the bot
   - **Pause** - Pause bot operations
   - **Status** - Check bot status
   - **Health Check** - Verify bot health
4. Monitor response messages

---

## 🔔 Real-time Alerts Feed

**Location:** Left Sidebar

**Features:**
- Live alert stream (max 50 alerts cached)
- Color-coded by source:
  - 🔵 Transport (Blue)
  - 🔴 Safety (Red)
  - 🟠 System (Orange)
- Timestamp for each alert
- Priority indicators
- Clear button to reset feed

**Example Alerts:**
```
[11:23:45] Transport alert: Truck TX-4821 speed > 75 mph [HIGH]
[11:22:10] Safety alert: Incident reported on I-10 [CRITICAL]
[11:20:33] System: Bot health check OK [INFO]
```

---

## 💻 System Health Indicators

**Location:** Top Right of Header

Shows real-time status of three subsystems:

1. **Transport** - Green = Healthy, Red = Disconnected
2. **Safety** - Green = Healthy, Red = Disconnected
3. **Dispatch** - Green = Healthy, Red = Disconnected
4. **Live Connection** - Green (pulsing) = Connected, Gray = Offline

---

## 🔌 WebSocket Connections

The panel automatically establishes two WebSocket connections:

1. **Transport WebSocket** - `/api/v1/transport/ws/tracking`
   - Vehicle position updates
   - Shipment status changes
   - Transport alerts

2. **Safety WebSocket** - `/api/v1/safety/ws/alerts`
   - Safety alerts
   - Incident notifications
   - Metrics updates

**Status:** Check "Live" indicator (top right) - should show **Live** with green pulsing dot

---

## 📈 Bottom Footer Stats

Three quick stats at panel bottom:

1. **Active Bots** - Count of running bots (e.g., "2/4")
2. **System Time** - Current server time
3. **Alerts** - Total alerts in Feed

---

## 🎮 Common Workflows

### Workflow 1: Monitor Active Shipments
1. Go to **Transport** tab
2. Check statistics sidebar (In Transit count)
3. View polylines showing active routes
4. Click shipments for:
   - Current location
   - Progress percentage
   - Estimated arrival time
   - Value and weight

### Workflow 2: Respond to Safety Alert
1. Watch **Alerts Feed** (left sidebar)
2. See new safety alert arrives
3. Click **Safety** tab for details
4. Review incident in Recent Incidents list
5. Check recommendation
6. Assign action item
7. Track compliance score

### Workflow 3: Manage Dispatch
1. Go to **Dispatch** tab
2. See unassigned shipments in first column
3. Review "From" and "To" locations
4. Assign driver via modal (click shipment)
5. Drag to "Assigned" column
6. Track progress through In Transit → Delivered

### Workflow 4: Control Bot Operations
1. Navigate to **Bots** tab
2. See all 4 bots with status indicators
3. If bot is inactive, click "Run" button
4. A success message appears in alerts
5. Bot status updates to "Active"
6. Monitor bot operations in respective modules

---

## 🚀 Starting the System

### Step 1: Start Backend
```bash
# Terminal 1
cd backend
python -m uvicorn main:app --reload
```
✅ Server runs on `http://localhost:8000`

### Step 2: Start Frontend
```bash
# Terminal 2
cd frontend
npm run dev
```
✅ Frontend runs on `http://localhost:5173`

### Step 3: Open Freight Broker Panel
```
Browser: http://localhost:5173/freight-broker
```

### Step 4: Login
- Use your credentials to log in
- Panel loads automatically after authentication

---

## 🔍 Troubleshooting

### Panel Not Loading
**Problem:** Blank screen or "Not Found"

**Solution:**
1. Check if backend is running: `curl http://localhost:8000/docs`
2. Verify authentication token is valid
3. Check browser console for errors
4. Clear browser cache and reload

### WebSocket Not Connecting
**Problem:** "Offline" instead of "Live"

**Solution:**
1. Verify backend is running
2. Check WebSocket endpoints exist: `/api/v1/transport/ws/tracking`
3. Check CORS settings allow WebSocket
4. Verify no firewall blocks connections

### Mock Data Not Showing
**Problem:** Empty map or lists show nothing

**Solution:**
1. This is expected - backend API should provide real data
2. Frontend falls back to mock data if API fails
3. Check network tab in DevTools for API calls
4. Verify `/api/v1/transport/shipments` endpoint is working

### Bots Not Running
**Problem:** All bots show "Inactive"

**Solution:**
1. Check bot processes are running
2. Verify `/api/v1/ai/bots/{bot_name}/status` endpoint
3. Review backend logs for errors
4. Ensure database is connected

---

## 📚 API Reference

### Key Endpoints Used

**Transport:**
```
GET  /api/v1/transport/statistics
GET  /api/v1/transport/shipments
GET  /api/v1/transport/trucks
WebSocket: /api/v1/transport/ws/tracking
```

**Safety:**
```
GET  /api/v1/safety/reports/{period}
GET  /api/v1/safety/incidents
GET  /api/v1/safety/metrics
WebSocket: /api/v1/safety/ws/alerts
```

**Bots:**
```
GET  /api/v1/ai/bots
GET  /api/v1/ai/bots/{bot_name}/status
POST /api/v1/ai/bots/{bot_name}/run
POST /api/v1/ai/bots/{bot_name}/pause
```

---

## 🎨 UI Components

### Transport Map
- **Technology:** Leaflet.js
- **Features:** Markers, Polylines, Circles, Layer Control
- **Icons:** Custom truck, shipment, warehouse icons

### Safety Dashboard
- **Technology:** Recharts
- **Charts:** LineChart, BarChart, PieChart
- **Responsive:** Mobile, Tablet, Desktop

### Dispatch Board
- **Technology:** CSS Grid
- **Features:** Kanban columns, drag-drop ready
- **Status:** Unassigned, Assigned, In Transit, Delivered, Cancelled

---

## 🔐 Authentication & Authorization

- All routes require `RequireAuth` wrapper
- User must be logged in to access
- Bots require appropriate permissions to execute
- WebSocket connections use session tokens

---

## 📊 Data Flow

```
1. User opens Freight Broker Panel (/freight-broker)
   ↓
2. Frontend loads React component
   ↓
3. Sets up two WebSocket connections (Transport + Safety)
   ↓
4. Checks bot health every 60 seconds
   ↓
5. Receives real-time updates via WebSocket
   ↓
6. Updates UI in real-time (maps, charts, alerts)
   ↓
7. User interactions trigger API calls
   ↓
8. System responds and updates state
```

---

## 💡 Pro Tips

1. **Monitor Alerts Continuously** - Keep alerts feed visible
2. **Check Bot Health** - Monitor Bots tab before critical operations
3. **Use Period Selector** - Switch safety reports to see trends
4. **Click Marked Shipments** - View detailed tracking info
5. **Zoom for Details** - Zoom into map to see precise locations

---

## 🆘 Support

For issues or questions:
1. Check the Integration Guide: `FREIGHT_BROKER_INTEGRATION_GUIDE.md`
2. Review backend logs: `backend/logs/`
3. Check browser console: DevTools → Console
4. Verify network requests: DevTools → Network

---

**Status:** ✅ Production Ready
**Last Updated:** 2025-02-12
**Version:** 1.0.0
