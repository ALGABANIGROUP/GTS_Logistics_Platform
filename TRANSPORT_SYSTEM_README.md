# Transport Mapping & Tracking System

Complete real-time transport tracking system with interactive maps, live vehicle tracking, and comprehensive shipment management.

## 🎯 System Overview

This system provides:
- **Real-Time Tracking**: Live GPS tracking of trucks and shipments
- **Interactive Maps**: Leaflet-based mapping with multiple layers
- **Shipment Management**: Complete shipment lifecycle tracking
- **Driver Portal**: WebSocket-based driver app integration
- **Analytics & Reports**: Performance metrics and KPIs
- **Alert System**: Real-time notifications for delays and incidents

## 📦 What's Included

### Frontend Components
```
frontend/src/components/Map/
├── TransportMap.jsx           # Main map component
├── TransportMap.css           # Map styling
├── TransportDashboard.jsx     # Full dashboard
└── TransportDashboard.css     # Dashboard styling
```

### Backend API
```
backend/routes/
└── transport_tracking_api.py  # All API endpoints & WebSocket
```

### Database Models
```
backend/models/
├── shipment.py                # Shipment tracking model
└── truck_location.py          # Vehicle tracking models
```

### Documentation
- `TRANSPORT_QUICK_START.md` - Get started in 5 minutes
- `TRANSPORT_MAPPING_GUIDE.md` - Complete feature documentation
- `TRANSPORT_INTEGRATION_SETUP.py` - Integration instructions
- `test_transport_api.py` - API testing script
- `.env.transport.example` - Environment configuration template

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd frontend
npm install leaflet react-leaflet
```

### 2. Add to Backend
Edit `backend/main.py`:
```python
from backend.routes.transport_tracking_api import router as transport_router
app.include_router(transport_router)
```

### 3. Run Dashboard
In your React component:
```jsx
import TransportDashboard from '@components/Map/TransportDashboard';

export default function Page() {
  return <TransportDashboard />;
}
```

### 4. Start Servers
```bash
# Backend (Terminal 1)
cd backend && uvicorn main:app --reload

# Frontend (Terminal 2)
cd frontend && npm run dev
```

## 📡 API Endpoints

### Shipments
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/transport/shipments` | List all shipments |
| GET | `/api/v1/transport/shipments/{id}` | Get shipment details |
| POST | `/api/v1/transport/shipments` | Create shipment |
| PUT | `/api/v1/transport/shipments/{id}` | Update shipment |
| GET | `/api/v1/transport/shipments/{id}/track` | Get tracking info |
| POST | `/api/v1/transport/shipments/{id}/update-location` | Update location |

### Trucks
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/transport/trucks` | List all trucks |
| GET | `/api/v1/transport/trucks/{id}` | Get truck details |
| POST | `/api/v1/transport/trucks/{id}/location` | Update location |

### Routes & Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/transport/routes/optimize` | Optimize route |
| GET | `/api/v1/transport/statistics` | Get statistics |
| GET | `/api/v1/transport/performance` | Get metrics |

### WebSocket
| Endpoint | Purpose |
|----------|---------|
| `WS /api/v1/transport/ws/tracking` | Real-time location updates |
| `WS /api/v1/transport/ws/alerts` | Alert notifications |
| `WS /api/v1/transport/ws/driver/{id}` | Driver app communication |

## 🗺️ Map Features

### Layers
- ✓ Street Map (OpenStreetMap)
- ✓ Satellite View (Google)
- ✓ Truck Markers (Customizable icons)
- ✓ Shipment Origins/Destinations
- ✓ Route Polylines
- ✓ Coverage Circles

### Interactions
- Click to select truck/shipment
- Zoom controls
- Location switcher (NYC, LA, Chicago, etc.)
- Layer control
- Sidebar with details

## 📊 Dashboard Features

### Key Metrics
- Total Shipments
- In Transit Count
- Delivered Count
- Active Trucks
- Average Speed
- Pending Shipments

### Filters
- All Shipments
- In Transit
- Delivered
- Pending

### Information Panels
- Shipment List (with search)
- Active Routes Display
- Selected Item Details
- Status Legend

## 🔒 Security Features

- ✓ JWT Authentication Ready
- ✓ API Rate Limiting Support
- ✓ WebSocket Auth Validation
- ✓ CORS Configuration
- ✓ Input Validation
- ✓ SQL Injection Prevention

## 📱 Responsive Design

- ✓ Desktop (1920px+)
- ✓ Tablet (768px - 1024px)
- ✓ Mobile (< 768px)
- ✓ Touch-friendly controls
- ✓ Adaptive layouts

## 🔄 Real-Time Updates

### WebSocket Events
```javascript
// Location Update
{
  "type": "location_update",
  "shipment_id": 1,
  "data": {
    "lat": 35.5353,
    "lng": -97.4867,
    "timestamp": "2025-02-05T10:30:00Z"
  }
}

// Truck Location
{
  "type": "truck_location_update",
  "truck_id": 1,
  "data": {
    "latitude": 35.5353,
    "longitude": -97.4867,
    "speed": 65,
    "heading": 45,
    "status": "moving"
  }
}

// Alert
{
  "type": "alert",
  "severity": "high",
  "title": "Delivery Delayed",
  "message": "Shipment 1 delayed by 30 minutes"
}
```

## 📈 Sample Data

### Shipments
1. **Medical Supplies** - NYC → LA (65%)
2. **Electronic Components** - Chicago → Atlanta (45%)
3. **Chemical Containers** - Seattle → San Jose (30%)

### Trucks
1. **TX-4821** - 65 mph, NE trajectory
2. **GA-7293** - 72 mph, SE trajectory
3. **CA-5612** - 58 mph, S trajectory

## 🛠️ Configuration

### Environment Variables
```bash
# Copy template
cp .env.transport.example .env.transport

# Edit with your values
API_BASE_URL=http://localhost:8000
WS_BASE_URL=ws://localhost:8000
USE_MOCK_DATA=true
```

### Mock Data Mode
All components default to mock data. No backend setup required for demo.

### Real Data Mode
1. Update API endpoints in components
2. Ensure backend returns proper format
3. Disable mock data in configuration

## 🧪 Testing

### Run Test Suite
```bash
python test_transport_api.py
```

### What Gets Tested
- All HTTP endpoints
- WebSocket connections
- Data formatting
- Error handling
- Authentication (if enabled)

### Requirements
```bash
pip install requests websocket-client
```

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `TRANSPORT_QUICK_START.md` | 5-minute setup guide |
| `TRANSPORT_MAPPING_GUIDE.md` | Complete documentation |
| `TRANSPORT_INTEGRATION_SETUP.py` | Integration checklist |
| `test_transport_api.py` | API testing script |

## 🔧 Customization

### Change Map Center
```javascript
// TransportMap.jsx
const [center, setCenter] = useState([40.7128, -74.0060]); // NYC
```

### Add Custom Icons
```javascript
const customIcon = new L.Icon({
  iconUrl: 'your-icon.png',
  iconSize: [40, 40],
  iconAnchor: [20, 40],
  popupAnchor: [0, -40]
});
```

### Modify Colors
Edit CSS files:
- `TransportMap.css`
- `TransportDashboard.css`

### Connect Real Data
```javascript
// Replace mock URLs in TransportDashboard.jsx
const response = await fetch('http://your-api.com/shipments');
```

## 📊 Performance Optimization

### Frontend
- React memoization for components
- Lazy loading of satellite tiles
- Debounced location updates
- Virtual scrolling for lists

### Backend
- Database connection pooling
- Efficient queries with indexes
- WebSocket connection management
- Caching for statistics

## 🚗 Typical use cases

1. **Logistics Companies** - Track fleet and deliveries
2. **Courier Services** - Real-time parcel tracking
3. **Supply Chain** - Monitor shipments and inventory
4. **E-commerce** - Customer tracking portals
5. **Field Services** - Technician routing and tracking

## ⚠️ Important Notes

- All sample data is mock for demonstration
- Implement proper authentication before production
- Ensure compliance with location tracking laws
- Set up proper SSL/HTTPS for production
- Implement rate limiting on APIs
- Use environment-based configuration

## 🐛 Troubleshooting

### Map Not Showing
```
✓ Check Leaflet CSS import
✓ Verify container has height/width
✓ Check browser console for errors
```

### No Data Displaying
```
✓ Ensure backend running on :8000
✓ Check network tab for failed requests
✓ Verify CORS configuration
✓ Check API_BASE_URL environment variable
```

### WebSocket Won't Connect
```
✓ Backend should be running
✓ Check endpoint URL: ws://localhost:8000
✓ Verify firewall not blocking WebSocket
✓ Check browser console for connection errors
```

## 📞 Support

For issues or questions:
1. Check documentation files
2. Review test output (`test_transport_api.py`)
3. Check browser/server console logs
4. Review API endpoint details

## 📄 File Structure

```
GTS/
├── frontend/src/components/Map/
│   ├── TransportMap.jsx
│   ├── TransportMap.css
│   ├── TransportDashboard.jsx
│   └── TransportDashboard.css
├── backend/
│   ├── routes/
│   │   └── transport_tracking_api.py
│   └── models/
│       ├── shipment.py
│       └── truck_location.py
└── Documentation/
    ├── TRANSPORT_QUICK_START.md
    ├── TRANSPORT_MAPPING_GUIDE.md
    ├── TRANSPORT_INTEGRATION_SETUP.py
    ├── test_transport_api.py
    └── .env.transport.example
```

## 🎓 Next Steps

1. **Immediate** - Run with mock data
2. **Short-term** - Connect to real database
3. **Medium-term** - Integrate GPS devices
4. **Long-term** - Add ML/AI analytics

## 📝 License

All components are part of the GTS system and follow the same licensing terms.

---

**Status**: Production Ready
**Last Updated**: February 5, 2026
**Version**: 1.0.0

For detailed setup, see `TRANSPORT_QUICK_START.md`
