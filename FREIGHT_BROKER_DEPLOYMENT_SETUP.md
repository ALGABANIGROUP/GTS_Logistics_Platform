# 🚀 FREIGHT BROKER CONTROL PANEL - DEPLOYMENT & SETUP GUIDE

## Quick Setup (5 Minutes)

### Prerequisites Check
```bash
# Check Node.js installed
node --version    # Should be 16+

# Check Python installed
python --version  # Should be 3.9+

# Check npm installed
npm --version     # Should be 8+
```

---

## Step-by-Step Installation

### Step 1: Start Backend Server (Terminal 1)

```bash
# Navigate to project root
cd c:\Users\enjoy\dev\GTS

# Install Python dependencies (first time only)
pip install fastapi uvicorn

# Start backend server
python -m uvicorn backend.main:app --reload --port 8000

# Expected output:
# Uvicorn running on http://127.0.0.1:8000
# Application startup complete
```

✅ **Backend Status Check:**
- Open browser: http://localhost:8000/docs
- Should see Swagger UI with all API endpoints

### Step 2: Start Frontend Server (Terminal 2)

```bash
# Navigate to frontend folder
cd c:\Users\enjoy\dev\GTS\frontend

# Install npm dependencies (first time only)
npm install

# Start development server
npm run dev

# Expected output:
#   VITE v... ready in ... ms
#   ➜  Local:   http://localhost:5173/
#   ➜  press h to show help
```

✅ **Frontend Status Check:**
- Open browser: http://localhost:5173
- Should see login page

### Step 3: Access Freight Broker Panel

1. **Log in** with your credentials
   - URL: http://localhost:5173/login
   - Enter username and password
   
2. **Navigate to Panel**
   - URL: http://localhost:5173/freight-broker
   - Should see unified dashboard
   
3. **Verify WebSocket Connection**
   - Check top-right corner for "Live" indicator
   - Should show green pulsing dot when connected

---

## System Check Verification

### ✅ Check 1: Frontend Running
```bash
curl http://localhost:5173 -I
# Should return: 200 OK
```

### ✅ Check 2: Backend Running
```bash
curl http://localhost:8000/api/v1/transport/statistics
# Should return JSON with statistics data
```

### ✅ Check 3: Database Connected
```bash
curl http://localhost:8000/api/health
# Should return: { "status": "healthy" }
```

### ✅ Check 4: WebSocket Ready
```
In browser console:
ws = new WebSocket('ws://localhost:8000/api/v1/transport/ws/tracking')
ws.onopen = () => console.log('✅ Connected')
ws.send(JSON.stringify({type: 'subscribe', channels: ['trucks']}))
```

---

## Component Status Dashboard

### 1. Transport Tab Status
```
✅ Map Loads              [Check map renders without errors]
✅ Mock Data Shows        [3 trucks, 3 shipments visible]
✅ Statistics Update      [Numbers change on refresh]
✅ WebSocket Receives     [Check browser console for messages]
```

**Test Command:**
```javascript
// In browser console
fetch('http://localhost:8000/api/v1/transport/statistics')
  .then(r => r.json())
  .then(d => console.log(d))
```

### 2. Safety Tab Status
```
✅ Charts Render          [3 charts visible]
✅ Metrics Display        [6 stat cards visible]
✅ Incidents Load         [List appears]
✅ Alerts Stream          [Real-time updates]
```

**Test Command:**
```javascript
fetch('http://localhost:8000/api/v1/safety/dashboard/stats')
  .then(r => r.json())
  .then(d => console.log(d))
```

### 3. Dispatch Tab Status
```
✅ Kanban Displays        [5 columns visible]
✅ Cards Render           [Shipment cards appear]
✅ Filtering Works        [Status columns accurate]
```

### 4. Bots Tab Status
```
✅ Bot Cards Display      [4 cards visible]
✅ Status Indicators      [Colors reflect status]
✅ Action Buttons Work    [Click triggers actions]
✅ Health Updates         [Numbers change]
```

**Test Command:**
```javascript
fetch('http://localhost:8000/api/v1/ai/bots/freight_broker/status')
  .then(r => r.json())
  .then(d => console.log(d))
```

---

## Troubleshooting Quick Reference

### Issue: "Cannot find module" (Frontend)

**Solution:**
```bash
cd frontend
rm -r node_modules package-lock.json
npm install
npm run dev
```

### Issue: 404 Not Found (Backend API)

**Solution:**
```bash
# Check endpoint exists
curl http://localhost:8000/docs

# Verify correct path
curl http://localhost:8000/api/v1/transport/statistics
```

### Issue: WebSocket Connection Failed

**Solution:**
```javascript
// In browser console, check protocol
console.log(window.location.protocol)  // Should be 'http:' or 'https:'

// Verify WebSocket URL
ws_protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
console.log(`${ws_protocol}//${window.location.host}/api/v1/transport/ws/tracking`)
```

### Issue: Database Connection Error

**Solution:**
```bash
# Check database is running
# Windows: Check Services for PostgreSQL
# Linux: systemctl status postgresql
# Mac: brew services list | grep postgresql

# Check connection string
echo %DATABASE_URL%  # Windows
echo $DATABASE_URL  # Linux/Mac
```

### Issue: Port Already in Use

**Solution:**
```bash
# Backend (Port 8000)
# Windows
netstat -ano | findstr 8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8000
kill -9 <PID>

# Frontend (Port 5173)
# Windows
netstat -ano | findstr 5173
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :5173
kill -9 <PID>
```

---

## Environment Configuration

### Frontend (.env or .env.local)
```
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_PROTOCOL=ws://
VITE_APP_NAME=Freight Broker Control Panel
VITE_LOG_LEVEL=debug
```

### Backend (backend/.env)
```
DATABASE_URL=postgresql://user:password@localhost/gts_db
SAFETY_BOT_ENABLED=true
TRANSPORT_TRACKING_ENABLED=true
WS_KEEP_ALIVE_INTERVAL=30
LOG_LEVEL=INFO
CORS_ORIGINS=["http://localhost:5173"]
SECRET_KEY=your-secret-key-here
```

---

## File Paths Quick Reference

### Frontend Files
```
frontend/src/
├── pages/
│   ├── FreightBrokerPanel.jsx       ← Main component
│   └── FreightBrokerPanel.css       ← Styles
├── components/
│   ├── Map/
│   │   ├── TransportMap.jsx          
│   │   └── TransportDashboard.jsx   
│   └── Safety/
│       └── SafetyDashboard.jsx      
└── App.jsx                          ← Updated with route
```

### Backend Files
```
backend/
├── routes/
│   ├── transport_tracking_api.py    ← 21 endpoints
│   ├── safety_routes.py             ← 20+ endpoints
│   └── ai_bots_routes.py            ← Bot control
├── safety/
│   ├── bot.py                       ← Safety orchestrator
│   ├── traffic_analysis.py
│   ├── weather_forecast.py
│   ├── reports_generator.py
│   └── alerts_system.py
├── models/
│   ├── truck_location.py            ← Transport models
│   ├── shipment.py                  ← Shipment model
│   └── safety_enhanced.py           ← Safety models
└── main.py                          ← FastAPI app
```

### Documentation Files
```
Project Root/
├── FREIGHT_BROKER_INTEGRATION_GUIDE.md       ← Full API docs
├── FREIGHT_BROKER_QUICK_START.md             ← Quick reference
├── FREIGHT_BROKER_CONTROL_PANEL_COMPLETE_SYSTEM.md ← Overview
└── FREIGHT_BROKER_DEPLOYMENT_SETUP.md        ← THIS FILE
```

---

## API Endpoint Testing

### Transport Endpoints
```bash
# Get all statistics
curl http://localhost:8000/api/v1/transport/statistics

# Get shipments list
curl http://localhost:8000/api/v1/transport/shipments

# Get trucks list
curl http://localhost:8000/api/v1/transport/trucks

# Optimize route
curl -X POST http://localhost:8000/api/v1/transport/routes/optimize \
  -H "Content-Type: application/json" \
  -d '{"origin": [40.7128, -74.0060], "destination": [34.0522, -118.2437]}'
```

### Safety Endpoints
```bash
# Get safety metrics
curl http://localhost:8000/api/v1/safety/dashboard/stats

# Get incidents
curl http://localhost:8000/api/v1/safety/incidents

# Get daily report
curl http://localhost:8000/api/v1/safety/reports/daily

# Get weather forecast
curl http://localhost:8000/api/v1/safety/weather/forecast
```

### Bot Endpoints
```bash
# Get all bots
curl http://localhost:8000/api/v1/ai/bots

# Get bot status
curl http://localhost:8000/api/v1/ai/bots/freight_broker/status

# Run bot
curl -X POST http://localhost:8000/api/v1/ai/bots/freight_broker/run

# Pause bot
curl -X POST http://localhost:8000/api/v1/ai/bots/freight_broker/pause

# Health check
curl -X POST http://localhost:8000/api/v1/ai/bots/freight_broker/health_check
```

---

## Browser Console Utilities

### Check System Health
```javascript
async function checkHealth() {
  const checks = {
    'Transport API': await fetch('http://localhost:8000/api/v1/transport/statistics').then(r => r.ok),
    'Safety API': await fetch('http://localhost:8000/api/v1/safety/dashboard/stats').then(r => r.ok),
    'Bot API': await fetch('http://localhost:8000/api/v1/ai/bots').then(r => r.ok),
  };
  
  console.table(checks);
  return checks;
}

checkHealth();
```

### Monitor WebSocket
```javascript
function monitorWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const ws = new WebSocket(`${protocol}//${window.location.host}/api/v1/transport/ws/tracking`);
  
  ws.onopen = () => console.log('✅ WebSocket connected');
  ws.onmessage = (e) => console.log('📨 Message:', JSON.parse(e.data));
  ws.onerror = (e) => console.error('❌ Error:', e);
  ws.onclose = () => console.log('⚠️ Connection closed');
  
  window.ws = ws;  // Save for inspection
}

monitorWebSocket();
```

### Simulate Alerts
```javascript
function simulateAlert(source, message) {
  // This simulates what would happen when alerts arrive
  console.log(`[${source}] ${message}`);
  // In real system, alerts come via WebSocket
}

simulateAlert('transport', 'Truck TX-4821 exceeded speed limit');
simulateAlert('safety', 'Weather alert: Heavy rain on I-10');
simulateAlert('system', 'SafetyManagerBot health check passed');
```

---

## Performance Optimization

### Frontend Optimization
```bash
# Build for production
cd frontend
npm run build

# Check bundle size
npm run build -- --report

# Output will be in: frontend/dist/
```

### Backend Optimization
```bash
# Start with multiple workers (production)
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4

# Enable production mode
export ENV=production
python -m uvicorn backend.main:app --reload --port 8000
```

---

## Monitoring & Logging

### Frontend Logs
```javascript
// Enable verbose logging
localStorage.setItem('DEBUG', 'freight-broker:*');
// Reload page to see detailed logs

// Check localStorage
console.log(localStorage.getItem('DEBUG'));
```

### Backend Logs
```bash
# Watch backend logs (Linux/Mac)
tail -f backend/logs/app.log

# Check for errors
grep ERROR backend/logs/app.log

# Listen for specific errors
grep -i websocket backend/logs/app.log
```

---

## Deployment to Production

### Step 1: Build Frontend
```bash
cd frontend
npm install  # Install dependencies
npm run build  # Create optimized build
# Output: frontend/dist/ (static files)
```

### Step 2: Configure Backend
```bash
cd backend

# Set environment variables
export DATABASE_URL="postgresql://user:pass@prod-db:5432/gts"
export SAFETY_BOT_ENABLED="true"
export TRANSPORT_TRACKING_ENABLED="true"
export CORS_ORIGINS='["https://yourdomain.com"]'

# Run migrations
alembic upgrade head

# Start server with gunicorn (production WSGI)
gunicorn -w 4 -b 0.0.0.0:8000 backend.main:app
```

### Step 3: Configure Reverse Proxy (Nginx)
```nginx
upstream fastapi {
    server 127.0.0.1:8000;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Static files (frontend)
    location / {
        root /var/www/freight-broker/dist;
        try_files $uri /index.html;
    }

    # API endpoints
    location /api/ {
        proxy_pass http://fastapi;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # WebSocket support
    location /api/v1/transport/ws/ {
        proxy_pass http://fastapi;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    location /api/v1/safety/ws/ {
        proxy_pass http://fastapi;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

### Step 4: Start Services
```bash
# Using systemd (Linux)
sudo systemctl start nginx
sudo systemctl start freight-broker-api
sudo systemctl start freight-broker-bots

# Using Docker (recommended)
docker-compose up -d
```

---

## Health Check URLs

After setup, verify all systems are working:

```
✅ Frontend:     http://localhost:5173
✅ Backend API:  http://localhost:8000/docs
✅ Health:       http://localhost:8000/api/health
✅ Transport:    http://localhost:8000/api/v1/transport/statistics
✅ Safety:       http://localhost:8000/api/v1/safety/dashboard/stats
✅ Bots:         http://localhost:8000/api/v1/ai/bots
```

---

## Summary

| Component | Port | Status URL | Expected |
|-----------|------|-----------|----------|
| Frontend | 5173 | http://localhost:5173 | Login page |
| Backend | 8000 | http://localhost:8000/docs | Swagger UI |
| Database | 5432 | (internal) | Connected |
| WebSocket | 8000 | ws://localhost:8000/ws | Connected |

---

## Next Steps

After successful setup:

1. **Create test account** (if needed)
2. **Load sample data** (transport/safety data)
3. **Verify integrations** (all tabs working)
4. **Test WebSocket** (real-time updates)
5. **Monitor bot health** (all 4 bots active)
6. **Review alerts** (real-time feed working)

---

**Status:** ✅ Ready for Deployment
**Created:** 2025-02-12
**Version:** 1.0.0

For detailed information, see:
- `FREIGHT_BROKER_QUICK_START.md` - Quick reference
- `FREIGHT_BROKER_INTEGRATION_GUIDE.md` - Complete API docs
- `FREIGHT_BROKER_CONTROL_PANEL_COMPLETE_SYSTEM.md` - System overview
