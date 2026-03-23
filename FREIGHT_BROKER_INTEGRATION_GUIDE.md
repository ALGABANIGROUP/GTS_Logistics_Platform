# 🚚 Freight Broker Control Panel - Complete Integration Guide

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Frontend Components](#frontend-components)
4. [Backend APIs](#backend-apis)
5. [WebSocket Connections](#websocket-connections)
6. [Bot Coordination](#bot-coordination)
7. [Data Flow](#data-flow)
8. [Testing & Verification](#testing--verification)
9. [Troubleshooting](#troubleshooting)
10. [Deployment](#deployment)

---

## System Overview

The **Freight Broker Control Panel** is a unified dashboard that integrates:
- **Transport Tracking**: Real-time vehicle and shipment tracking with interactive maps
- **Safety Management**: Comprehensive safety monitoring, incident tracking, and alerts
- **Dispatch Operations**: Kanban-style dispatch board for shipment assignment
- **Bot Coordination**: Automated orchestration through multiple AI bots

The system follows a **modular bot architecture** where each bot handles its domain while the FreightBrokerBot orchestrates overall operations.

---

## Architecture

### Frontend Structure
```
frontend/src/
├── pages/
│   └── FreightBrokerPanel.jsx          # Main unified dashboard
│       └── FreightBrokerPanel.css      # Panel styling
├── components/
│   ├── Map/
│   │   ├── TransportMap.jsx            # Leaflet interactive map
│   │   ├── TransportMap.css
│   │   ├── TransportDashboard.jsx      # Transport stats & filtering
│   │   └── TransportDashboard.css
│   └── Safety/
│       ├── SafetyDashboard.jsx         # Safety metrics & alerts
│       └── SafetyDashboard.css
```

### Backend Structure
```
backend/
├── routes/
│   ├── transport_tracking_api.py       # Transport API (21 endpoints)
│   ├── safety_routes.py                # Safety API (20+ endpoints)
│   └── ai_bots_routes.py              # Bot orchestration
├── safety/
│   ├── bot.py                          # Safety Manager Bot orchestrator
│   ├── traffic_analysis.py             # Traffic monitoring
│   ├── weather_forecast.py             # Weather analysis
│   ├── reports_generator.py            # Report generation
│   └── alerts_system.py                # Alert management
├── models/
│   ├── truck_location.py               # Transport models (5 models)
│   ├── shipment.py                     # Shipment model (40+ fields)
│   └── safety_enhanced.py              # Safety models (7 models)
```

---

## Frontend Components

### 1. FreightBrokerPanel.jsx (Main Component)

**Purpose**: Unified control center for all freight operations

**Props**: None (managed internally)

**State Management**:
```javascript
{
  activeTab: 'transport' | 'safety' | 'dispatch' | 'bots',
  botsStatus: {
    freightBroker: 'active' | 'inactive',
    safetyManager: 'active' | 'inactive',
    operationsManager: 'pending',
    finance: 'idle'
  },
  realTimeAlerts: [], // Array of alert objects
  wsConnected: boolean,
  systemHealth: {
    transport: 'healthy' | 'disconnected',
    safety: 'healthy' | 'disconnected',
    dispatch: 'healthy' | 'disconnected'
  }
}
```

**Features**:
- **Tabbed Interface**: Switch between Transport, Safety, Dispatch, and Bots
- **Real-time Alerts Feed**: 50+ alerts cached with timestamps
- **System Health Indicators**: Live status of all subsystems
- **WebSocket Connections**: Dual connections (Transport + Safety)
- **Bot Health Monitoring**: 60-second health checks

**Key Methods**:
```javascript
setupWebSocketConnections()    // Establish dual WebSocket connections
addAlert(alert, source)         // Add alert to feed
checkBotsHealth()               // Poll bot status endpoints
handleBotAction(botName, action) // Trigger bot operations
clearAlerts()                   // Clear alert feed
```

### 2. TransportMap.jsx

**Purpose**: Interactive real-time map with vehicle tracking

**Props**:
```javascript
{
  shipments: Array<Shipment>,  // Array of shipment objects
  trucks: Array<Truck>         // Array of truck objects
}
```

**Features**:
- Leaflet map with OpenStreetMap + Google Satellite layers
- Custom icons: trucks, shipments, warehouses
- Route polylines with color coding by status
- Circle indicators for current location
- Zoom and location controls
- Sidebar with statistics and selection details

**Mock Data**: 3 shipments, 3 trucks (fallback when API unavailable)

### 3. TransportDashboard.jsx

**Purpose**: Statistics, filtering, and shipment/route listing

**Features**:
- 6 stat cards: Total, In Transit, Delivered, Active Trucks, Avg Speed, Pending
- Filter buttons: All, In Transit, Delivered, Pending
- Recent shipments list (max 5)
- Active routes list (max 3)
- Real-time polling every 30 seconds
- Graceful fallback to mock data

**API Calls**:
```javascript
GET /api/v1/transport/shipments
GET /api/v1/transport/trucks
```

### 4. SafetyDashboard.jsx

**Purpose**: Comprehensive safety monitoring and incident management

**Features**:
- 6 stat cards: Safety Score, Incidents, High-Risk Drivers, Active Alerts, Vehicle Status, Compliance
- 3 interactive charts: Line (trend), Bar (distribution), Pie (risk)
- Incidents list with severity filtering
- Active alerts with priority levels
- Safety recommendations with deadlines
- Pending action items (checklist)
- Period selector: Daily / Weekly / Monthly
- WebSocket real-time updates

**API Calls**:
```javascript
GET  /api/v1/safety/reports/{period}
GET  /api/v1/safety/incidents?limit=10
GET  /api/v1/safety/metrics
WebSocket: /api/v1/safety/ws/alerts
```

### 5. DispatchBoard Component (In-Panel)

**Purpose**: Kanban-style dispatch board for shipment management

**Features**:
- 5-column layout: Unassigned, Assigned, In Transit, Delivered, Cancelled
- Drag-and-drop shipment cards
- Driver assignment functionality
- Status tracking

---

## Backend APIs

### Transport Tracking API (`/api/v1/transport/*`)

**Base Endpoints**:

#### Shipments
```javascript
GET    /api/v1/transport/shipments              // List all shipments
POST   /api/v1/transport/shipments              // Create shipment
GET    /api/v1/transport/shipments/{id}        // Get specific shipment
PUT    /api/v1/transport/shipments/{id}        // Update shipment
DELETE /api/v1/transport/shipments/{id}        // Delete shipment
POST   /api/v1/transport/shipments/{id}/track  // Get tracking data
```

#### Trucks
```javascript
GET    /api/v1/transport/trucks                 // List all trucks
POST   /api/v1/transport/trucks                 // Register truck
GET    /api/v1/transport/trucks/{id}           // Get truck details
GET    /api/v1/transport/trucks/{id}/location  // Real-time location
POST   /api/v1/transport/trucks/{id}/status    // Update truck status
```

#### Routes & Optimization
```javascript
POST   /api/v1/transport/routes/optimize        // Optimize route
GET    /api/v1/transport/routes/{id}           // Get route details
GET    /api/v1/transport/routes/analyze        // Route analysis
```

#### Statistics & Analytics
```javascript
GET    /api/v1/transport/statistics             // Overall statistics
GET    /api/v1/transport/statistics/daily       // Daily metrics
GET    /api/v1/transport/analytics/efficiency   // Efficiency metrics
GET    /api/v1/transport/analytics/costs        // Cost analysis
```

#### WebSocket
```javascript
WebSocket: /api/v1/transport/ws/tracking       // Real-time tracking updates
WebSocket: /api/v1/transport/ws/alerts         // Transport alerts
```

### Safety Management API (`/api/v1/safety/*`)

**Base Endpoints**:

#### Safety Checks & Assessments
```javascript
POST   /api/v1/safety/check-route               // Assess route safety
POST   /api/v1/safety/check-vehicle/{id}       // Vehicle inspection
POST   /api/v1/safety/check-driver/{id}        // Driver behavior check
```

#### Incidents
```javascript
GET    /api/v1/safety/incidents                 // List incidents
POST   /api/v1/safety/incidents                 // Report incident
GET    /api/v1/safety/incidents/{id}           // Get incident details
PUT    /api/v1/safety/incidents/{id}           // Update investigation
```

#### Reporting
```javascript
GET    /api/v1/safety/reports/daily             // Daily safety report
GET    /api/v1/safety/reports/weekly            // Weekly safety report
GET    /api/v1/safety/reports/monthly           // Monthly safety report
POST   /api/v1/safety/reports/generate          // Generate custom report
```

#### Analytics
```javascript
GET    /api/v1/safety/metrics                   // Current metrics
GET    /api/v1/safety/metrics/trends            // Safety trends
GET    /api/v1/safety/driver/{id}/behavior      // Driver analysis
GET    /api/v1/safety/vehicle/{id}/status       // Vehicle status
GET    /api/v1/safety/compliance/audit          // Compliance audit
```

#### Environmental Data
```javascript
GET    /api/v1/safety/weather/forecast          // Weather data
GET    /api/v1/safety/traffic/analyze           // Traffic conditions
POST   /api/v1/safety/traffic/predict           // Traffic prediction
```

#### Dashboard
```javascript
GET    /api/v1/safety/dashboard/stats           // Dashboard statistics
GET    /api/v1/safety/dashboard/alerts          // Current alerts
GET    /api/v1/safety/dashboard/recommendations // Safety recommendations
```

#### WebSocket
```javascript
WebSocket: /api/v1/safety/ws/alerts             // Real-time safety alerts
WebSocket: /api/v1/safety/ws/incidents          // Incident notifications
```

### Bot Orchestration API (`/api/v1/ai/bots/*`)

**Base Endpoints**:

```javascript
GET    /api/v1/ai/bots                          // List all bots
GET    /api/v1/ai/bots/{bot_name}              // Get bot details
GET    /api/v1/ai/bots/{bot_name}/status       // Bot status
POST   /api/v1/ai/bots/{bot_name}/run          // Run bot
POST   /api/v1/ai/bots/{bot_name}/pause        // Pause bot
POST   /api/v1/ai/bots/{bot_name}/health_check // Health check
POST   /api/v1/ai/bots/{bot_name}/execute      // Execute specific action
```

**Bot Names**:
- `freight_broker` - Main coordinator
- `safety_manager` - Safety monitoring
- `operations_manager` - Operations coordination
- `finance` - Financial tracking

---

## WebSocket Connections

### Transport WebSocket (`/api/v1/transport/ws/tracking`)

**Connection**:
```javascript
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const ws = new WebSocket(`${protocol}//${window.location.host}/api/v1/transport/ws/tracking`);
```

**Messages Received**:
```javascript
{
  type: 'truck_update',
  data: {
    truck_id: number,
    location: [lat, lng],
    speed: number,
    heading: number,
    status: 'moving' | 'stopped' | 'idle',
    timestamp: ISO8601
  }
}

{
  type: 'shipment_update',
  data: {
    shipment_id: number,
    status: 'pending' | 'in_transit' | 'delivered',
    progress: 0-100,
    eta: ISO8601,
    location: [lat, lng]
  }
}

{
  type: 'alert',
  data: {
    message: string,
    severity: 'info' | 'warning' | 'critical',
    shipment_id: optional,
    truck_id: optional
  }
}
```

**Subscribe Message**:
```javascript
ws.send(JSON.stringify({
  type: 'subscribe',
  channels: ['trucks', 'shipments', 'routes']
}));
```

### Safety WebSocket (`/api/v1/safety/ws/alerts`)

**Connection**:
```javascript
const ws = new WebSocket(`${protocol}//${window.location.host}/api/v1/safety/ws/alerts`);
```

**Messages Received**:
```javascript
{
  type: 'safety_alert',
  data: {
    id: string,
    message: string,
    priority: 'low' | 'medium' | 'high' | 'critical',
    category: 'traffic' | 'weather' | 'vehicle' | 'driver' | 'compliance',
    location: optional,
    timestamp: ISO8601
  }
}

{
  type: 'incident',
  data: {
    id: string,
    incident_type: string,
    severity: 'minor' | 'moderate' | 'severe',
    description: string,
    location: [lat, lng],
    timestamp: ISO8601
  }
}

{
  type: 'metrics_update',
  data: {
    safety_score: 0-100,
    incident_count: number,
    alerts_count: number
  }
}
```

**Subscribe Message**:
```javascript
ws.send(JSON.stringify({
  type: 'subscribe',
  channels: ['alerts', 'incidents', 'metrics']
}));
```

---

## Bot Coordination

### Bot Architecture

```
FreightBrokerBot (Coordinator)
├── SafetyManagerBot (Safety domain)
│   ├── Traffic Analysis
│   ├── Weather Forecasting
│   ├── Reports Generation
│   └── Alerts System
├── OperationsManagerBot (Operations domain)
├── FinanceBot (Finance domain)
└── OtherBots...
```

### Bot Communication Flow

1. **User Action** (in FreightBrokerPanel)
   ```javascript
   handleBotAction('freight_broker', 'run')
   ```

2. **Request to API**
   ```
   POST /api/v1/ai/bots/freight_broker/run
   ```

3. **Bot Execution**
   - Freight Broker Bot receives request
   - Coordinates with associated bots
   - Safety Manager Bot checks safety
   - Operations Manager Bot schedules operations
   - Returns combined response

4. **Response to Frontend**
   ```javascript
   {
     status: 'success',
     message: 'Operations started',
     active_bots: ['freight_broker', 'safety_manager', 'operations_manager']
   }
   ```

### Bot Health Monitoring

**Health Check Interval**: 60 seconds (configurable)

**Response Structure**:
```javascript
{
  bot_name: 'freight_broker',
  status: 'active' | 'inactive' | 'error',
  health: 'healthy' | 'degraded' | 'critical',
  uptime: number (seconds),
  last_action: ISO8601,
  metrics: {
    executions: number,
    success_rate: 0-100,
    avg_response_time: number (ms)
  }
}
```

---

## Data Flow

### Complete Transport Update Flow

1. **Truck sends location update**
   ```
   Real truck GPS → Backend API
   ```

2. **Backend processes update**
   ```
   POST /api/v1/transport/trucks/{id}/location
   → Update database
   → Broadcast via WebSocket
   ```

3. **WebSocket broadcasts to all connected clients**
   ```javascript
   {
     type: 'truck_update',
     data: { ... }
   }
   ```

4. **Frontend receives and updates**
   ```javascript
   TransportMap re-renders with new location
   TransportDashboard updates statistics
   FreightBrokerPanel alerts feed shows update
   ```

### Complete Safety Incident Flow

1. **Incident occurs**
   ```
   Traffic accident detected / Safety violation / Vehicle issue
   ```

2. **Safety Bot processes**
   ```
   SafetyManagerBot.process_incident()
   → Create incident record
   → Assess severity
   → Generate recommendations
   ```

3. **Broadcast via WebSocket**
   ```javascript
   {
     type: 'incident',
     data: {
       severity: 'severe',
       recommendations: [...]
     }
   }
   ```

4. **Frontend receives and alerts**
   ```javascript
   SafetyDashboard updates incidents list
   Alert feed shows high-priority notification
   Bot status may change based on incident
   ```

---

## Testing & Verification

### 1. Test WebSocket Connections

```javascript
// In browser console
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const ws = new WebSocket(`${protocol}//${window.location.host}/api/v1/transport/ws/tracking`);

ws.onopen = () => {
  console.log('✅ Transport WebSocket connected');
  ws.send(JSON.stringify({
    type: 'subscribe',
    channels: ['trucks', 'shipments']
  }));
};

ws.onmessage = (event) => {
  console.log('📨 Message received:', JSON.parse(event.data));
};

ws.onerror = (error) => {
  console.error('❌ WebSocket error:', error);
};
```

### 2. Test API Endpoints

```bash
# Test Transport API
curl http://localhost:8000/api/v1/transport/statistics

# Test Safety API
curl http://localhost:8000/api/v1/safety/dashboard/stats

# Test Bot Status
curl http://localhost:8000/api/v1/ai/bots/freight_broker/status

# Trigger Bot Action
curl -X POST http://localhost:8000/api/v1/ai/bots/freight_broker/run
```

### 3. Test Panel Components

1. **Transport Tab**
   - Verify map loads
   - Check 3 mock shipments/trucks display
   - Test location selector buttons
   - Verify sidebar updates

2. **Safety Tab**
   - Check 6 stat cards render
   - Test period selector (Daily/Weekly/Monthly)
   - Verify charts display (mock data)
   - Check incidents and alerts lists

3. **Dispatch Tab**
   - Verify 5 columns display
   - Check shipment cards appear
   - Test driver assignment modal

4. **Bots Tab**
   - Check 4 bot cards render
   - Verify status indicators
   - Test action buttons
   - Check health status updates

### 4. Alert Feed Testing

1. **Add manual alert** (for testing)
   ```javascript
   // In FreightBrokerPanel console
   addAlert({
     message: 'Test alert',
     priority: 'warning'
   }, 'transport');
   ```

2. **Verify alert appears** in sidebar
3. **Test clear alerts** button

---

## Troubleshooting

### WebSocket Connection Issues

**Problem**: WebSocket stays disconnected

**Solutions**:
1. Check backend server is running
   ```bash
   # Windows
   netstat -an | findstr "8000"
   
   # Linux/Mac
   lsof -i :8000
   ```

2. Check WebSocket endpoint exists
   ```bash
   curl http://localhost:8000/docs  # Check Swagger docs
   ```

3. Check browser console for errors
4. Verify protocol (ws: vs wss:)

### API Endpoints 404

**Problem**: API calls return 404

**Solutions**:
1. Verify endpoint exists in backend routes
2. Check correct path format: `/api/v1/{resource}/{action}`
3. Verify HTTP method (GET vs POST)
4. Check authentication token in headers

### Mock Data Not Showing

**Problem**: Dashboard shows empty lists

**Solutions**:
1. API is down - fallback should trigger
2. Check network tab in DevTools
3. Enable console.warn to see mock data activation
4. Verify component props pass correctly

### Bot Status Showing "Inactive"

**Problem**: All bots showing inactive

**Solutions**:
1. Check bot health endpoints return valid responses
2. Verify bot processes are running
3. Check database connections
4. Review error logs: `backend/logs/`

---

## Deployment

### Prerequisites
- Node.js 16+ (frontend)
- Python 3.9+ (backend)
- FastAPI + uvicorn
- WebSocket support enabled

### Frontend Deployment

```bash
# 1. Build Vite project
cd frontend
npm run build

# 2. Deploy to production
# Option A: Static hosting (Vercel, Netlify)
npm run build && deploy dist/

# Option B: With backend
# Copy dist/ to backend/static/
```

### Backend Deployment

```bash
# 1. Install dependencies
pip install -r backend/requirements.txt

# 2. Set environment variables
export DATABASE_URL="postgresql://user:pass@localhost/db"
export SAFETY_BOT_ENABLED="true"
export TRANSPORT_TRACKING_ENABLED="true"

# 3. Run migrations
alembic upgrade head

# 4. Start server (production)
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4

# 5. Enable WebSocket support in reverse proxy (nginx example)
# location /api/v1/transport/ws/ {
#     proxy_pass http://localhost:8000;
#     proxy_http_version 1.1;
#     proxy_set_header Upgrade \$http_upgrade;
#     proxy_set_header Connection "upgrade";
# }
```

### Environment Configuration

**`.env` (Backend)**:
```
DATABASE_URL=postgresql://...
SAFETY_BOT_ENABLED=true
TRANSPORT_TRACKING_ENABLED=true
WS_KEEP_ALIVE_INTERVAL=30
LOG_LEVEL=INFO
CORS_ORIGINS=["http://localhost:5173", "https://yourdomain.com"]
```

**`.env` (Frontend)**:
```
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_PROTOCOL=ws
VITE_APP_NAME=Freight Broker Control Panel
```

---

## Performance Optimization

### Frontend Optimization
- Use React.memo() on heavy components
- Virtual scrolling for long alert lists
- WebSocket message debouncing
- Map layer culling

### Backend Optimization
- Database connection pooling
- Redis caching for statistics
- Async processing for heavy computations
- WebSocket connection pooling

### Infrastructure
- CDN for static assets
- Load balancing for multiple backends
- Database replication for read scaling
- Message queue (RabbitMQ/Redis) for bot coordination

---

## Support & Documentation

For additional help:
- Backend API Docs: `http://localhost:8000/docs`
- Component Stories: `frontend/src/stories/`
- Bot Documentation: `backend/BOTS_README.md`
- Safety System: `backend/safety/README.md`

---

**Last Updated**: 2025-02-12
**System Version**: 1.0.0
**Status**: Production Ready ✅
