# 📞 API Connection & Call Files - Project Guide

## 🌐 Frontend Files (React/JavaScript)

### 1️⃣ **axiosClient.js** - Main HTTP Client
📁 `frontend/src/api/axiosClient.js`

**Function:**
- Main Axios client for all API calls
- Auto-adds Token to requests (JWT Bearer)
- Handles 401 errors (token expiration)
- Timeout: 30 seconds

**Key Features:**
```javascript
- baseURL: http://127.0.0.1:8000
- timeout: 30000ms
- Auto-add Authorization: Bearer <token>
- 401 → clearAuthCache() → dispatch 'auth:expired'
```

---

### 2️⃣ **aiClient.js** - AI Bots Calls
📁 `frontend/src/api/aiClient.js`

**Function:**
- Call smart bots
- Get bot status and config
- Run bot with custom payload

**API Endpoints:**
```javascript
GET  /api/v1/ai/bots/{name}/status    → getBotStatus(name)
GET  /api/v1/ai/bots/{name}/config    → getBotConfig(name)
POST /api/v1/ai/bots/{name}/run       → runBot(name, payload)
GET  /api/v1/system/bots/status       → getAllBotsStatus()
```

**Usage Example:**
```javascript
import { runBot } from './api/aiClient';
const result = await runBot('freight_broker', { action: 'search' });
```

---

### 3️⃣ **governanceClient.js** - Bot Management
📁 `frontend/src/api/governanceClient.js`

**Function:**
- Register new bots
- Approve bots
- Activate bots in production

**API Endpoints:**
```javascript
GET  /api/v1/bots                        → listBots()
GET  /api/v1/bots/{botId}                → getBot(botId)
POST /api/v1/bots/register               → registerBot(manifest)
POST /api/v1/bots/{botId}/approve        → approveBot(botId, approver, role)
POST /api/v1/bots/{botId}/activate       → activateBot(botId, environment)
```

---

### 4️⃣ **integrationClient.js** - External Integrations
📁 `frontend/src/api/integrationClient.js`

**Function:**
- Integration with VIZION API (shipment tracking)
- Integration with DAT LoadBoard (truck loads)
- Webhooks and notifications management

**Features:**
```javascript
- subscribeToUpdates(shipmentId, callbackUrl)  → Webhook subscription
- getShipmentTracking(shipmentId)             → VIZION tracking
- searchLoads(criteria)                        → DAT loads
- generateInvoice(shipmentId)                  → Auto invoice
```

---

### 5️⃣ **authApi.js** - Authentication and Login
📁 `frontend/src/api/authApi.js`

**Function:**
- User login
- Get user information
- Token renewal

---

## 🔌 Backend Files (Python/FastAPI)

### 6️⃣ **ws_routes.py** - Main WebSocket
📁 `backend/routes/ws_routes.py`

**Function:**
- WebSocket connection for real-time updates
- Publish/Subscribe system for channels
- Broadcasting events to connected clients

**WebSocket Endpoint:**
```
WS /api/v1/ws/live
```

**Message Protocol:**
```json
// Subscribe to channel
{"type": "subscribe", "channel": "bots.*"}

// Ping/Pong
{"type": "ping"} → {"type": "pong"}

// Unsubscribe
{"type": "unsubscribe", "channel": "bots.*"}
```

**Available Channels:**
- `bots.*` - Bot events
- `commands.*` - Command execution
- `governance.*` - Bot management
- `shipments.*` - Shipment updates

---

### 7️⃣ **ai_calls_websocket.py** - AI Calls
📁 `backend/routes/ai_calls_websocket.py`

**Function:**
- Simulate smart AI calls
- Send call events to connected clients
- Track call status

**WebSocket Endpoint:**
```
WS /ws/ai/calls
```

**Message Structure:**
```json
{
  "caller": "+1-202-555-1234",
  "status": "in_progress",
  "timestamp": "2026-01-08T12:30:00",
  "reason": "Follow-up on delayed shipment"
}
```

**States:**
- `initiated` - Call started
- `in_progress` - In progress
- `completed` - Completed
- `failed` - Failed

---

### 8️⃣ **ai_bots_routes.py** - Bot Routes
📁 `backend/routes/ai_bots_routes.py`

**Function:**
- Call smart bots
- Manage bot status
- Return operation results

**Endpoints:**
```python
GET  /api/v1/ai/bots/{bot_name}/status
GET  /api/v1/ai/bots/{bot_name}/config
POST /api/v1/ai/bots/{bot_name}/run
```

---

### 9️⃣ **bot_governance_routes.py** - Bot Governance
📁 `backend/routes/bot_governance_routes.py`

**Function:**
- Register new bots
- Approval system (at least 2 approvers)
- Activation in production
- Activity log

**Endpoints:**
```python
POST /api/v1/bots/register
POST /api/v1/bots/{bot_id}/approve
POST /api/v1/bots/{bot_id}/activate
GET  /api/v1/bots
GET  /api/v1/bots/{bot_id}
```

---

### 🔟 **mapleload_canada_routes.py** - MapleLoad Canada Bot
📁 `backend/routes/mapleload_canada_routes.py`

**Function:**
- Specialized bot for Canadian market
- Market analytics
- Carrier discovery
- Smart matching

**Endpoints:**
```python
GET  /api/v1/ai/bots/mapleload-canada/health
GET  /api/v1/ai/bots/mapleload-canada/status
POST /api/v1/ai/bots/mapleload-canada/market-intelligence
POST /api/v1/ai/bots/mapleload-canada/carrier-discovery
POST /api/v1/ai/bots/mapleload-canada/smart-matching
POST /api/v1/ai/bots/mapleload-canada/predictive-analytics
POST /api/v1/ai/bots/mapleload-canada/lead-generation
GET  /api/v1/ai/bots/mapleload-canada/integrations
```

---

## 🛠️ Helper Service Files

### **openai_client.py** - OpenAI Client
📁 `backend/services/llm/openai_client.py`

**Function:**
- Call GPT-4 for smart processing
- Text analysis
- Generate responses

---

### **ws_manager.py** - WebSocket Manager
📁 `backend/bots/ws_manager.py`

**Function:**
- Manage active connections
- Pub/Sub system for channels
- Broadcast events to all clients

**Main Functions:**
```python
await hub.connect(websocket)
await hub.subscribe(websocket, channel)
await hub.broadcast(channel, data)
await hub.disconnect(websocket)
```

---

## 📊 Files Summary

### Frontend (JavaScript)
| File | Function | Priority |
|------|----------|----------|
| `axiosClient.js` | Base HTTP client | ⭐⭐⭐⭐⭐ |
| `aiClient.js` | Bot calls | ⭐⭐⭐⭐⭐ |
| `governanceClient.js` | Bot management | ⭐⭐⭐⭐ |
| `integrationClient.js` | External integrations | ⭐⭐⭐⭐ |
| `authApi.js` | Authentication | ⭐⭐⭐⭐⭐ |

### Backend (Python)
| File | Function | Priority |
|------|----------|----------|
| `ws_routes.py` | Main WebSocket | ⭐⭐⭐⭐⭐ |
| `ai_calls_websocket.py` | AI calls | ⭐⭐⭐ |
| `ai_bots_routes.py` | Bot routes | ⭐⭐⭐⭐⭐ |
| `bot_governance_routes.py` | Bot governance | ⭐⭐⭐⭐ |
| `mapleload_canada_routes.py` | Canada bot | ⭐⭐⭐⭐ |

---

## 🔗 Connection Diagram

```
┌─────────────────────────────────────────┐
│         Frontend (React)                │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │     axiosClient.js               │  │
│  │  (Base HTTP Client)              │  │
│  └──────────┬───────────────────────┘  │
│             │                           │
│  ┌──────────▼───────────────────────┐  │
│  │  aiClient.js                     │  │
│  │  governanceClient.js             │  │
│  │  integrationClient.js            │  │
│  └──────────┬───────────────────────┘  │
└─────────────┼───────────────────────────┘
              │ HTTP/REST
              │ (Port 8000)
┌─────────────▼───────────────────────────┐
│         Backend (FastAPI)               │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │  ai_bots_routes.py               │  │
│  │  bot_governance_routes.py        │  │
│  │  mapleload_canada_routes.py      │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │  ws_routes.py                    │◄─┼─ WebSocket
│  │  (WebSocket Hub)                 │  │  (Port 8000)
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │  ai_calls_websocket.py           │  │
│  │  (AI Call Events)                │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

---

## 🧪 Testing Guide

### 1. Test HTTP Endpoints
```powershell
# Get bot status
$token = $env:TEST_TOKEN
Invoke-RestMethod "http://127.0.0.1:8000/api/v1/ai/bots/freight_broker/status" `
    -Headers @{"Authorization" = "Bearer $token"}

# Run bot action
$body = @{ action = "search" } | ConvertTo-Json
Invoke-RestMethod "http://127.0.0.1:8000/api/v1/ai/bots/freight_broker/run" `
    -Method Post `
    -Headers @{"Authorization" = "Bearer $token"; "Content-Type" = "application/json"} `
    -Body $body
```

### 2. Test WebSocket (JavaScript)
```javascript
const ws = new WebSocket('ws://127.0.0.1:8000/api/v1/ws/live');

ws.onopen = () => {
    // Subscribe to bots channel
    ws.send(JSON.stringify({
        type: 'subscribe',
        channel: 'bots.*'
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};
```

### 3. Test MapleLoad Canada Bot
```powershell
# Use existing script
.\test_mapleload_canada_bot.ps1
```

---

## 📝 Important Notes

### Authentication
- All APIs require JWT Token
- Token sent in Header: `Authorization: Bearer <token>`
- On expiration (401), cache is automatically cleared

### WebSocket
- Connection is persistent
- Channel system for filtering
- Ping/Pong support for disconnection detection
- Automatic reconnection from Frontend

### Error Handling
- All APIs return unified JSON
- Errors contain `detail` and `error`
- Interceptors handle errors automatically

### Performance
- Default timeout: 30 seconds
- WebSocket uses JSON for messages
- Axios supports request cancellation

---

**EN:** 8 EN 2026  
**EN:** 1.0  
**EN:** GTS Logistics Platform
