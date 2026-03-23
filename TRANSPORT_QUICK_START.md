# Transport Tracking System - Quick Start Guide

## 5-Minute Setup

### Step 1: Install Frontend Dependencies
```bash
cd frontend
npm install leaflet react-leaflet
```

### Step 2: Add Transport Routes to Backend
Edit `backend/main.py`:

```python
from backend.routes.transport_tracking_api import router as transport_router

# Add this where you include other routers:
app.include_router(transport_router)
```

### Step 3: Use the Dashboard Component
In your React app or page:

```jsx
import TransportDashboard from '@components/Map/TransportDashboard';

export default function TransportPage() {
  return <TransportDashboard />;
}
```

### Step 4: Run the Application
```bash
# Terminal 1: Backend
cd backend
uvicorn main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

Visit: `http://localhost:5173` (or your Vite port)

## Available Features

### Real-Time Tracking
- Live truck and shipment locations on map
- Multiple map layers (street, satellite)
- Click markers for detailed information
- Route visualization between origin and destination

### Dashboard
- Key statistics (shipments, trucks, speeds)
- Filterable shipment list
- Active routes display
- Status color coding

### API Ready
All endpoints return mock data by default:
- Shipments: Various status (in_transit, delivered, pending)
- Trucks: Real-time speed and heading
- Routes: Optimized paths

## Default Mock Data

### Sample Shipments
1. **Medical Supplies** - NYC to LA (65% progress)
2. **Electronic Components** - Chicago to Atlanta (45% progress)
3. **Chemical Containers** - Seattle to San Jose (30% progress)

### Sample Trucks
1. **TX-4821** - 65 mph, moving northeast
2. **GA-7293** - 72 mph, moving southeast
3. **CA-5612** - 58 mph, moving south

## Replace Mock Data with Real Data

### Option A: Connect to Real Database
1. Update API endpoints in `TransportDashboard.jsx`:
```javascript
// Replace mock URLs:
const response = await fetch('http://localhost:8000/api/v1/transport/shipments');
```

2. Ensure your backend returns proper data format

### Option B: Use WebSocket for Live Updates
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/transport/ws/tracking');

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  // Process real-time location updates
};
```

## Common Customizations

### Change Default Center
In `TransportMap.jsx`:
```javascript
const [center, setCenter] = useState([40.7128, -74.0060]); // NYC
```

### Add Custom Markers
```javascript
const customMarker = new L.Icon({
  iconUrl: 'your-icon-url.png',
  iconSize: [40, 40]
});
```

### Modify Status Colors
In `TransportMap.jsx`:
```javascript
const getStatusColor = (status) => {
  switch (status) {
    case 'in_transit': return 'blue';
    case 'delivered': return 'green';
    // ... customize here
  }
};
```

## API Endpoints

### View All Shipments
```
GET http://localhost:8000/api/v1/transport/shipments
```

Response:
```json
{
  "data": [
    {
      "id": 1,
      "name": "Medical Supplies",
      "status": "in_transit",
      "progress": 65
    }
  ],
  "total": 3
}
```

### View All Trucks
```
GET http://localhost:8000/api/v1/transport/trucks
```

### Track Specific Shipment
```
GET http://localhost:8000/api/v1/transport/shipments/1/track
```

### Update Truck Location
```
POST http://localhost:8000/api/v1/transport/trucks/1/location
Content-Type: application/json

{
  "latitude": 35.5353,
  "longitude": -97.4867,
  "speed": 65,
  "heading": 45,
  "status": "moving"
}
```

## Component Props

### TransportDashboard
No props required - uses defaults
```jsx
<TransportDashboard />
```

### TransportMap
```jsx
<TransportMap 
  shipments={shipmentArray}  // Optional
  trucks={truckArray}         // Optional
/>
```

If no props provided, shows mock data.

## Styling

- **Responsive Design**: Works on desktop, tablet, mobile
- **Color Scheme**: Professional blue/gray theme
- **Customizable CSS**: All styles in `TransportMap.css` and `TransportDashboard.css`

Change theme colors by editing CSS variables in the stylesheet files.

## Performance Tips

1. **Limit Markers**: Show only top 50-100 items
2. **Debounce Updates**: Limit WebSocket updates to every 5-10 seconds
3. **Lazy Load Imagery**: Load satellite imagery only when selected
4. **Virtual Scrolling**: Use for large shipment lists

## Troubleshooting

### Map shows blank
✓ Check browser console for errors
✓ Verify Leaflet CSS is imported
✓ Ensure map container has height/width

### No data showing
✓ Check if backend is running on `http://localhost:8000`
✓ Look in network tab for failed requests
✓ Check if CORS is configured

### WebSocket won't connect
✓ Backend should be running
✓ Check if WS endpoint: `ws://localhost:8000/api/v1/transport/ws/tracking`
✓ Verify no firewall blocking WebSocket

## Next Steps

1. ✓ Test with mock data (current)
2. Connect to real database
3. Integrate actual GPS feeds
4. Add authentication
5. Deploy to production

## Support Resources

- **Documentation**: See `TRANSPORT_MAPPING_GUIDE.md`
- **API Routes**: Check `backend/routes/transport_tracking_api.py`
- **Models**: Review `backend/models/truck_location.py` and `shipment.py`
- **Frontend**: Check `frontend/src/components/Map/`

## Key Files

```
Frontend:
├── src/components/Map/
│   ├── TransportMap.jsx           (Map component)
│   ├── TransportMap.css           (Styles)
│   ├── TransportDashboard.jsx     (Dashboard)
│   └── TransportDashboard.css     (Dashboard styles)

Backend:
├── routes/
│   └── transport_tracking_api.py  (API endpoints & WebSocket)
├── models/
│   ├── shipment.py                (Shipment model)
│   └── truck_location.py          (Truck & tracking models)
```

## Legal & Compliance

- **Privacy**: Ensure compliance with location tracking laws
- **Data Retention**: Implement proper data retention policies
- **Authentication**: Require authentication for all APIs
- **Permissions**: Get explicit consent before tracking

---

Happy tracking! For detailed documentation, see `TRANSPORT_MAPPING_GUIDE.md`
