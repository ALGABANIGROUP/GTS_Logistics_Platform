"""
Transport Management API Routes
Handles shipments, trucks, tracking, and WebSocket real-time updates
"""

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Dict, Any
from datetime import datetime, timedelta
import json
import asyncio
from ..database import get_db
from ..models.shipment import Shipment
from ..models.truck_location import TruckLocation

router = APIRouter(prefix="/api/v1/transport", tags=["transport"])

# Active WebSocket connections for real-time updates
active_connections: Dict[str, List[WebSocket]] = {
    'tracking': [],
    'alerts': [],
    'drivers': []
}


class ConnectionManager:
    def __init__(self):
        self.active_connections = active_connections

    async def connect(self, websocket: WebSocket, channel: str):
        await websocket.accept()
        self.active_connections[channel].append(websocket)

    def disconnect(self, websocket: WebSocket, channel: str):
        self.active_connections[channel].remove(websocket)

    async def broadcast(self, message: dict, channel: str):
        for connection in self.active_connections[channel]:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting: {e}")

    async def send_personal(self, websocket: WebSocket, message: dict):
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Error sending personal message: {e}")


manager = ConnectionManager()


# ==================== Shipment Routes ====================

@router.get("/shipments")
async def get_shipments(
    status: str = Query(None),
    limit: int = Query(100),
    offset: int = Query(0),
    db: Session = Depends(get_db)
):
    """
    Get all shipments with optional filtering
    """
    query = db.query(Shipment)
    
    if status:
        query = query.filter(Shipment.status == status)
    
    total = query.count()
    shipments = query.offset(offset).limit(limit).all()
    
    return {
        "data": shipments,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/shipments/{shipment_id}")
async def get_shipment(shipment_id: int, db: Session = Depends(get_db)):
    """
    Get details of a specific shipment
    """
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    
    if not shipment:
        return {"error": "Shipment not found"}, 404
    
    return {
        "data": shipment,
        "current_location": {
            "lat": getattr(shipment, 'current_lat', None),
            "lng": getattr(shipment, 'current_lng', None),
            "timestamp": getattr(shipment, 'last_location_update', None)
        }
    }


@router.post("/shipments")
async def create_shipment(
    shipment_data: dict,
    db: Session = Depends(get_db)
):
    """
    Create a new shipment
    """
    new_shipment = Shipment(**shipment_data)
    db.add(new_shipment)
    db.commit()
    db.refresh(new_shipment)
    
    return {"data": new_shipment, "message": "Shipment created successfully"}


@router.put("/shipments/{shipment_id}")
async def update_shipment(
    shipment_id: int,
    update_data: dict,
    db: Session = Depends(get_db)
):
    """
    Update a shipment's details
    """
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    
    if not shipment:
        return {"error": "Shipment not found"}, 404
    
    for key, value in update_data.items():
        setattr(shipment, key, value)
    
    db.commit()
    db.refresh(shipment)
    
    return {"data": shipment, "message": "Shipment updated successfully"}


@router.post("/shipments/{shipment_id}/track")
async def track_shipment(shipment_id: int, db: Session = Depends(get_db)):
    """
    Get tracking information for a specific shipment
    """
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    
    if not shipment:
        return {"error": "Shipment not found"}, 404
    
    # Calculate distance remaining (mock)
    total_distance = 2000  # Mock total distance in km
    estimated_progress = 65
    distance_remaining = int(total_distance * (100 - estimated_progress) / 100)
    
    return {
        "shipment_id": shipment_id,
        "status": getattr(shipment, 'status', 'in_transit'),
        "current_location": {
            "lat": getattr(shipment, 'current_lat', 35.5),
            "lng": getattr(shipment, 'current_lng', -97.5)
        },
        "origin": {
            "lat": getattr(shipment, 'origin_lat', 40.7),
            "lng": getattr(shipment, 'origin_lng', -74.0)
        },
        "destination": {
            "lat": getattr(shipment, 'dest_lat', 34.0),
            "lng": getattr(shipment, 'dest_lng', -118.2)
        },
        "progress": estimated_progress,
        "distance_remaining": distance_remaining,
        "estimated_arrival": getattr(shipment, 'estimated_delivery', None),
        "driver": getattr(shipment, 'driver_name', 'Unknown'),
        "vehicle_license": getattr(shipment, 'vehicle_license', 'N/A')
    }


@router.post("/shipments/{shipment_id}/update-location")
async def update_shipment_location(
    shipment_id: int,
    location: dict,
    db: Session = Depends(get_db)
):
    """
    Update shipment current location (from GPS/tracking device)
    """
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    
    if not shipment:
        return {"error": "Shipment not found"}, 404
    
    setattr(shipment, 'current_lat', location.get('lat'))
    setattr(shipment, 'current_lng', location.get('lng'))
    setattr(shipment, 'last_location_update', datetime.utcnow())
    
    db.commit()
    
    # Broadcast location update to tracking channel
    await manager.broadcast({
        "type": "location_update",
        "shipment_id": shipment_id,
        "data": {
            "lat": location.get('lat'),
            "lng": location.get('lng'),
            "timestamp": datetime.utcnow().isoformat()
        }
    }, 'tracking')
    
    return {"status": "updated", "message": "Location updated successfully"}


# ==================== Truck Routes ====================

@router.get("/trucks")
async def get_trucks(
    active_only: bool = Query(False),
    limit: int = Query(100),
    offset: int = Query(0),
    db: Session = Depends(get_db)
):
    """
    Get all trucks with optional filtering for active only
    """
    query = db.query(TruckLocation)
    
    if active_only:
        # Filter for recent updates (last 30 minutes)
        cutoff_time = datetime.utcnow() - timedelta(minutes=30)
        query = query.filter(TruckLocation.last_update > cutoff_time)
    
    total = query.count()
    trucks = query.offset(offset).limit(limit).all()
    
    return {
        "data": trucks,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/trucks/{truck_id}")
async def get_truck(truck_id: int, db: Session = Depends(get_db)):
    """
    Get details of a specific truck
    """
    truck = db.query(TruckLocation).filter(TruckLocation.id == truck_id).first()
    
    if not truck:
        return {"error": "Truck not found"}, 404
    
    return {
        "data": truck
    }


@router.post("/trucks/{truck_id}/location")
async def update_truck_location(
    truck_id: int,
    location_data: dict,
    db: Session = Depends(get_db)
):
    """
    Update truck location from driver app or tracking device
    """
    truck = db.query(TruckLocation).filter(TruckLocation.id == truck_id).first()
    
    if not truck:
        # Create new truck location record
        truck = TruckLocation(
            id=truck_id,
            license_plate=location_data.get('license_plate', f'TRUCK-{truck_id}'),
            latitude=location_data.get('latitude'),
            longitude=location_data.get('longitude'),
            speed=location_data.get('speed', 0),
            heading=location_data.get('heading', 0),
            status=location_data.get('status', 'moving'),
            last_update=datetime.utcnow()
        )
        db.add(truck)
    else:
        truck.latitude = location_data.get('latitude')
        truck.longitude = location_data.get('longitude')
        truck.speed = location_data.get('speed', truck.speed)
        truck.heading = location_data.get('heading', truck.heading)
        truck.status = location_data.get('status', truck.status)
        truck.last_update = datetime.utcnow()
    
    db.commit()
    db.refresh(truck)
    
    # Broadcast location update
    await manager.broadcast({
        "type": "truck_location_update",
        "truck_id": truck_id,
        "data": {
            "latitude": truck.latitude,
            "longitude": truck.longitude,
            "speed": truck.speed,
            "heading": truck.heading,
            "status": truck.status,
            "timestamp": truck.last_update.isoformat()
        }
    }, 'tracking')
    
    return {"status": "updated", "message": "Truck location updated"}


# ==================== Route Optimization ====================

@router.get("/routes/optimize")
async def optimize_route(
    origin: str = Query(...),
    destination: str = Query(...),
    stops: List[str] = Query(None)
):
    """
    Optimize route between origin and destination
    This is a mock implementation - integrate with real routing service
    """
    
    # Mock implementation - would integrate with Google Maps or OSRM
    optimized_route = {
        "origin": origin,
        "destination": destination,
        "total_distance": "450 km",
        "estimated_time": "5 hours 30 minutes",
        "fuel_estimate": "85 liters",
        "stops": stops or [],
        "waypoints": [
            [39.8283, -98.5795],
            [35.5353, -97.4867],
            [34.0522, -118.2437]
        ]
    }
    
    return optimized_route


# ==================== WebSocket Endpoints ====================

@router.websocket("/ws/tracking")
async def websocket_tracking(websocket: WebSocket):
    """
    WebSocket endpoint for real-time tracking updates
    Clients receive live location updates for trucks and shipments
    """
    await manager.connect(websocket, 'tracking')
    
    try:
        while True:
            # Receive data from client
            data = await websocket.receive_json()
            
            if data.get('type') == 'subscribe':
                # Client subscribing to updates
                subscription = {
                    "type": "subscribed",
                    "channel": data.get('channel', 'all'),
                    "message": "Successfully subscribed to tracking updates"
                }
                await manager.send_personal(websocket, subscription)
            
            elif data.get('type') == 'ping':
                # Keep-alive ping
                pong = {"type": "pong", "timestamp": datetime.utcnow().isoformat()}
                await manager.send_personal(websocket, pong)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, 'tracking')


@router.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    """
    WebSocket endpoint for alert notifications
    Clients receive alerts for delays, incidents, etc.
    """
    await manager.connect(websocket, 'alerts')
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get('type') == 'subscribe':
                await manager.send_personal(websocket, {
                    "type": "subscribed",
                    "message": "Subscribed to alerts channel"
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, 'alerts')


@router.websocket("/ws/driver/{driver_id}")
async def websocket_driver(websocket: WebSocket, driver_id: str):
    """
    WebSocket endpoint for driver app communication
    Drivers send location updates and receive delivery instructions
    """
    await manager.connect(websocket, 'drivers')
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get('type') == 'location_update':
                # Process driver location update
                location = data.get('location', {})
                print(f"Driver {driver_id} update: {location}")
                
                # Broadcast to tracking channel
                await manager.broadcast({
                    "type": "driver_location",
                    "driver_id": driver_id,
                    "data": location
                }, 'tracking')
            
            elif data.get('type') == 'status_update':
                # Process driver status change
                status = data.get('status')
                print(f"Driver {driver_id} status: {status}")
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, 'drivers')


# ==================== Statistics & Reports ====================

@router.get("/statistics")
async def get_transport_statistics(db: Session = Depends(get_db)):
    """
    Get transport statistics and metrics
    """
    shipments = db.query(Shipment).all() if hasattr(db, 'query') else []
    trucks = db.query(TruckLocation).all() if hasattr(db, 'query') else []
    
    stats = {
        "total_shipments": len(shipments),
        "in_transit": len([s for s in shipments if getattr(s, 'status', '') == 'in_transit']),
        "delivered": len([s for s in shipments if getattr(s, 'status', '') == 'delivered']),
        "delayed": len([s for s in shipments if getattr(s, 'status', '') == 'delayed']),
        "active_trucks": len([t for t in trucks if getattr(t, 'status', '') == 'moving']),
        "avg_speed": sum([getattr(t, 'speed', 0) for t in trucks]) / len(trucks) if trucks else 0,
        "total_distance_traveled": 45000,  # Mock data
        "fuel_consumed": 3400  # Mock data
    }
    
    return stats


@router.get("/performance")
async def get_performance_metrics(db: Session = Depends(get_db)):
    """
    Get performance metrics and KPIs
    """
    metrics = {
        "on_time_delivery": 94.5,
        "average_delivery_time": 5.2,  # hours
        "fuel_efficiency": 7.2,  # km/liter
        "driver_safety_score": 95,
        "vehicle_utilization": 87,  # percent
        "total_revenue": 125000,  # dollars
        "cost_per_mile": 2.15,
        "customer_satisfaction": 4.7  # out of 5
    }
    
    return metrics
