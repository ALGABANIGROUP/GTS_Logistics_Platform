# Transport Mapping System - Implementation Guide

## Overview
This transport mapping system provides real-time tracking of vehicles (trucks) and shipments across North America with WebSocket support for live updates.

## Features

### Frontend Components
- **TransportMap.jsx**: Interactive map component with Leaflet
  - Real-time truck and shipment markers
  - Multiple layer support (trucks, shipments, satellite view)
  - Click-to-track functionality
  - Responsive sidebar with detailed information
  - Status-based color coding

- **TransportDashboard.jsx**: Full dashboard interface
  - Key statistics cards
  - Filter controls
  - Shipments list with progress tracking
  - Active routes display
  - Real-time data updates

### Backend API Endpoints

#### Shipment Management
- `GET /api/v1/transport/shipments` - List all shipments with filtering
- `GET /api/v1/transport/shipments/{shipment_id}` - Get specific shipment
- `POST /api/v1/transport/shipments` - Create new shipment
- `PUT /api/v1/transport/shipments/{shipment_id}` - Update shipment
- `POST /api/v1/transport/shipments/{shipment_id}/track` - Get tracking info
- `POST /api/v1/transport/shipments/{shipment_id}/update-location` - Update shipment location

#### Truck Management
- `GET /api/v1/transport/trucks` - List all trucks
- `GET /api/v1/transport/trucks/{truck_id}` - Get specific truck
- `POST /api/v1/transport/trucks/{truck_id}/location` - Update truck location

#### Route Optimization
- `GET /api/v1/transport/routes/optimize` - Optimize route between points

#### Analytics
- `GET /api/v1/transport/statistics` - Get transport statistics
- `GET /api/v1/transport/performance` - Get performance metrics

#### WebSocket Endpoints
- `WS /api/v1/transport/ws/tracking` - Real-time tracking updates
- `WS /api/v1/transport/ws/alerts` - Alert notifications
- `WS /api/v1/transport/ws/driver/{driver_id}` - Driver app communication

## Installation

### 1. Frontend Dependencies
```bash
cd frontend
npm install leaflet react-leaflet
npm install leaflet-draw leaflet.markercluster leaflet-routing-machine
```

### 2. Database Models
Models are defined in:
- `backend/models/shipment.py` - Shipment tracking model
- `backend/models/truck_location.py` - Truck location and related models

Run migrations:
```bash
alembic upgrade head
```

### 3. API Integration
Add to your FastAPI main.py:
```python
from backend.routes.transport_tracking_api import router as transport_router
app.include_router(transport_router)
```

## Usage

### Display Transport Map
```jsx
import TransportDashboard from '@components/Map/TransportDashboard';

function App() {
  return <TransportDashboard />;
}
```

### Just Map Component
```jsx
import TransportMap from '@components/Map/TransportMap';

function MyComponent() {
  const trucks = [...]; // your truck data
  const shipments = [...]; // your shipment data
  
  return <TransportMap trucks={trucks} shipments={shipments} />;
}
```

### API Usage Examples

#### Get All Shipments
```javascript
const response = await fetch('http://localhost:8000/api/v1/transport/shipments');
const data = await response.json();
console.log(data.data); // Array of shipments
```

#### Track Specific Shipment
```javascript
const shipmentId = 1;
const response = await fetch(
  `http://localhost:8000/api/v1/transport/shipments/${shipmentId}/track`
);
const tracking = await response.json();
```

#### Update Shipment Location
```javascript
await fetch(
  'http://localhost:8000/api/v1/transport/shipments/1/update-location',
  {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      lat: 35.5353,
      lng: -97.4867
    })
  }
);
```

#### WebSocket Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/transport/ws/tracking');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'subscribe',
    channel: 'all'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Update:', data);
  // Process real-time updates
};
```

## Shipment Status Values
- `pending` - Awaiting assignment
- `assigned` - Truck and driver assigned
- `in_transit` - Currently being transported
- `delivered` - Delivery completed
- `cancelled` - Shipment cancelled
- `delayed` - Shipment delayed

## Truck Status Values
- `moving` - Vehicle in motion
- `stopped` - Vehicle stopped/idle
- `loading` - Loading cargo
- `unloading` - Unloading cargo
- `maintenance` - Under maintenance

## Mock Data
The components include mock data for demonstration purposes. To use real data:

1. Ensure your backend API is running and returning proper data
2. Remove or comment out mock data in components
3. Adjust API endpoints to match your configuration

## CSS Classes
All components include responsive CSS with media queries for mobile devices.

Main stylesheet locations:
- `TransportMap.css` - Map component styles
- `TransportDashboard.css` - Dashboard styles

## Performance Optimization

### Frontend
- Uses React memoization for heavy components
- Lazy loads satellite imagery
- Debounces location updates
- Implements virtual scrolling for large lists

### Backend
- Database indexes on frequently queried columns
- Connection pooling for database access
- Caching for statistical queries
- WebSocket connection pooling

## Security Considerations

1. **Authentication**: All endpoints should require valid JWT tokens
2. **Rate Limiting**: Implement rate limiting on tracking endpoints
3. **Data Validation**: Validate all incoming location data
4. **CORS**: Configure CORS properly for cross-origin requests
5. **WebSocket Auth**: Validate WebSocket connections

## Browser Compatibility
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Troubleshooting

### Map not displaying
- Ensure Leaflet CSS is imported: `import 'leaflet/dist/leaflet.css'`
- Check browser console for errors
- Verify map container has explicit height/width

### WebSocket connection fails
- Check backend is running
- Verify WS_BASE_URL environment variable
- Ensure CORS/proxy configured if behind firewall
- Check for authentication headers

### Mock data not showing
- Clear browser cache
- Verify mock data functions return arrays
- Check console for JavaScript errors

## Next Steps

1. **Database Setup**: Run migrations to create tables
2. **Authentication**: Integrate JWT authentication
3. **Real GPS Data**: Connect actual GPS devices/APIs
4. **Mobile App**: Build driver mobile application
5. **Notifications**: Implement push notifications
6. **Analytics**: Add advanced reporting

## Support
For issues or questions, refer to the API documentation and check server logs for detailed error messages.
