"""
Transport Management API Routes
Handles shipments, trucks, tracking, and WebSocket real-time updates
"""

from datetime import datetime, timedelta
import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import OperationalError

from backend.database.config import get_db
from ..models.shipment import Shipment
from ..models.truck_location import TruckLocation

router = APIRouter(prefix="/api/v1/transport", tags=["transport"])
logger = logging.getLogger(__name__)

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


def _to_iso(value: Any) -> str | None:
    if isinstance(value, datetime):
        return value.isoformat()
    return None


def _coords(lat: Any, lng: Any) -> list[float] | None:
    if lat is None or lng is None:
        return None
    try:
        return [float(lat), float(lng)]
    except (TypeError, ValueError):
        return None


def _format_currency(amount: Any, currency: str | None = "USD") -> str | None:
    if amount is None:
        return None
    try:
        return f"{currency or 'USD'} {float(amount):,.2f}"
    except (TypeError, ValueError):
        return None


def _serialize_shipment(shipment: Shipment) -> dict[str, Any]:
    origin = _coords(
        getattr(shipment, "origin_latitude", None),
        getattr(shipment, "origin_longitude", None),
    )
    destination = _coords(
        getattr(shipment, "destination_latitude", None),
        getattr(shipment, "destination_longitude", None),
    )
    current_location = _coords(
        getattr(shipment, "current_latitude", None),
        getattr(shipment, "current_longitude", None),
    ) or origin or destination

    progress = getattr(shipment, "progress_percentage", None)
    if progress is None:
        total = getattr(shipment, "distance_total_km", None)
        traveled = getattr(shipment, "distance_traveled_km", None)
        if total:
            try:
                progress = round((float(traveled or 0) / float(total)) * 100, 2)
            except (TypeError, ValueError, ZeroDivisionError):
                progress = 0

    name = (
        getattr(shipment, "goods_description", None)
        or getattr(shipment, "shipment_number", None)
        or f"Shipment #{getattr(shipment, 'id', 'unknown')}"
    )
    from_label = ", ".join(
        part
        for part in [
            getattr(shipment, "origin_city", None),
            getattr(shipment, "origin_state", None),
        ]
        if part
    ) or getattr(shipment, "origin_address", None) or "Origin"
    to_label = ", ".join(
        part
        for part in [
            getattr(shipment, "destination_city", None),
            getattr(shipment, "destination_state", None),
        ]
        if part
    ) or getattr(shipment, "destination_address", None) or "Destination"

    return {
        "id": getattr(shipment, "id", None),
        "shipmentNumber": getattr(shipment, "shipment_number", None),
        "name": name,
        "status": getattr(shipment, "status", "pending"),
        "from": origin,
        "to": destination,
        "fromLabel": from_label,
        "toLabel": to_label,
        "currentLocation": current_location,
        "currentLocationDescription": getattr(shipment, "current_location_description", None),
        "driver": getattr(shipment, "driver_name", None),
        "driverPhone": getattr(shipment, "driver_phone", None),
        "estimatedArrival": _to_iso(getattr(shipment, "delivery_deadline", None))
        or _to_iso(getattr(shipment, "delivery_scheduled", None)),
        "pickupScheduled": _to_iso(getattr(shipment, "pickup_scheduled", None)),
        "deliveryScheduled": _to_iso(getattr(shipment, "delivery_scheduled", None)),
        "weight": f"{getattr(shipment, 'weight_kg', 0)} kg" if getattr(shipment, "weight_kg", None) is not None else None,
        "value": _format_currency(
            getattr(shipment, "total_price", None) or getattr(shipment, "base_price", None),
            getattr(shipment, "currency", "USD"),
        ),
        "progress": progress or 0,
        "shipmentType": getattr(shipment, "shipment_type", None),
        "paymentStatus": getattr(shipment, "payment_status", None),
        "referenceNumber": getattr(shipment, "reference_number", None),
        "truckId": getattr(shipment, "truck_id", None),
        "driverId": getattr(shipment, "driver_id", None),
        "assigned_driver": getattr(shipment, "driver_name", None),
        "raw": shipment.to_dict(),
    }


def _serialize_truck(truck: TruckLocation) -> dict[str, Any]:
    return {
        "id": getattr(truck, "id", None),
        "license": getattr(truck, "license_plate", None),
        "licensePlate": getattr(truck, "license_plate", None),
        "truckNumber": getattr(truck, "truck_number", None),
        "status": getattr(truck, "status", "stopped"),
        "currentLocation": _coords(
            getattr(truck, "latitude", None),
            getattr(truck, "longitude", None),
        ),
        "driver": getattr(truck, "driver_name", None),
        "driverId": getattr(truck, "driver_id", None),
        "speed": getattr(truck, "speed", 0) or 0,
        "heading": getattr(truck, "heading", 0) or 0,
        "shipmentId": getattr(truck, "current_shipment_id", None),
        "fuelLevel": getattr(truck, "fuel_level", None),
        "lastUpdate": _to_iso(getattr(truck, "last_update", None)),
        "raw": truck.to_dict(),
    }


# ==================== Shipment Routes ====================

@router.get("/shipments")
async def get_shipments(
    status: str = Query(None),
    limit: int = Query(100),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all shipments with optional filtering
    """
    query = select(Shipment)

    if status:
        query = query.where(Shipment.status == status)

    try:
        result = await db.execute(query.offset(offset).limit(limit))
        shipments = result.scalars().all()
    except OperationalError as exc:
        logger.warning("Transport shipments query unavailable: %s", exc)
        return []
    return [_serialize_shipment(shipment) for shipment in shipments]


@router.get("/shipments/{shipment_id}")
async def get_shipment(shipment_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get details of a specific shipment
    """
    result = await db.execute(select(Shipment).where(Shipment.id == shipment_id))
    shipment = result.scalar_one_or_none()

    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    return {
        "data": _serialize_shipment(shipment),
        "current_location": {
            "lat": getattr(shipment, 'current_latitude', None),
            "lng": getattr(shipment, 'current_longitude', None),
            "timestamp": _to_iso(getattr(shipment, 'updated_at', None)),
        },
    }


@router.post("/shipments")
async def create_shipment(
    shipment_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new shipment
    """
    new_shipment = Shipment(**shipment_data)
    db.add(new_shipment)
    await db.commit()
    await db.refresh(new_shipment)
    
    return {"data": _serialize_shipment(new_shipment), "message": "Shipment created successfully"}


@router.put("/shipments/{shipment_id}")
async def update_shipment(
    shipment_id: int,
    update_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a shipment's details
    """
    result = await db.execute(select(Shipment).where(Shipment.id == shipment_id))
    shipment = result.scalar_one_or_none()

    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    for key, value in update_data.items():
        setattr(shipment, key, value)

    await db.commit()
    await db.refresh(shipment)

    return {"data": _serialize_shipment(shipment), "message": "Shipment updated successfully"}


@router.post("/shipments/{shipment_id}/track")
async def track_shipment(shipment_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get tracking information for a specific shipment
    """
    shipment_result = await db.execute(select(Shipment).where(Shipment.id == shipment_id))
    shipment = shipment_result.scalar_one_or_none()
    
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    truck_location = None
    truck_id = getattr(shipment, 'truck_id', None)
    if truck_id is not None:
        truck_result = await db.execute(select(TruckLocation).where(TruckLocation.id == truck_id))
        truck_location = truck_result.scalar_one_or_none()

    current_lat = getattr(shipment, 'current_latitude', None)
    current_lng = getattr(shipment, 'current_longitude', None)

    if current_lat is None and truck_location is not None:
        current_lat = getattr(truck_location, 'latitude', None)
    if current_lng is None and truck_location is not None:
        current_lng = getattr(truck_location, 'longitude', None)

    if current_lat is None or current_lng is None:
        raise HTTPException(
            status_code=503,
            detail="Real-time tracking unavailable for this shipment because GPS telemetry is missing",
        )

    total_distance = getattr(shipment, 'distance_total_km', None)
    distance_traveled = getattr(shipment, 'distance_traveled_km', None)
    distance_remaining = getattr(shipment, 'distance_remaining_km', None)
    progress = getattr(shipment, 'progress_percentage', None)

    if distance_remaining is None and total_distance is not None and distance_traveled is not None:
        distance_remaining = max(total_distance - distance_traveled, 0)

    if progress is None and total_distance:
        if distance_traveled is not None:
            progress = round((distance_traveled / total_distance) * 100, 2)
        elif distance_remaining is not None:
            progress = round(((total_distance - distance_remaining) / total_distance) * 100, 2)

    if total_distance is None and distance_traveled is not None and distance_remaining is not None:
        total_distance = distance_traveled + distance_remaining

    if progress is None and total_distance is None and distance_remaining is None:
        raise HTTPException(
            status_code=503,
            detail="Tracking metrics unavailable for this shipment because route telemetry is incomplete",
        )
    
    return {
        "shipment_id": shipment_id,
        "status": getattr(shipment, 'status', 'in_transit'),
        "current_location": {
            "lat": current_lat,
            "lng": current_lng
        },
        "origin": {
            "lat": getattr(shipment, 'origin_latitude', None),
            "lng": getattr(shipment, 'origin_longitude', None)
        },
        "destination": {
            "lat": getattr(shipment, 'destination_latitude', None),
            "lng": getattr(shipment, 'destination_longitude', None)
        },
        "progress": progress,
        "distance_remaining": distance_remaining,
        "distance_total": total_distance,
        "distance_traveled": distance_traveled,
        "estimated_arrival": getattr(shipment, 'delivery_deadline', None),
        "driver": getattr(shipment, 'driver_name', None),
        "vehicle_license": getattr(truck_location, 'license_plate', None) if truck_location else None
    }


@router.post("/shipments/{shipment_id}/update-location")
async def update_shipment_location(
    shipment_id: int,
    location: dict,
    db: AsyncSession = Depends(get_db)
):
    """
    Update shipment current location (from GPS/tracking device)
    """
    result = await db.execute(select(Shipment).where(Shipment.id == shipment_id))
    shipment = result.scalar_one_or_none()

    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    setattr(shipment, 'current_latitude', location.get('lat'))
    setattr(shipment, 'current_longitude', location.get('lng'))
    setattr(shipment, 'updated_at', datetime.utcnow())

    await db.commit()

    # Broadcast location update to tracking channel
    await manager.broadcast({
        "type": "location_update",
        "shipment_id": shipment_id,
        "data": {
            "lat": location.get('lat'),
            "lng": location.get('lng'),
            "timestamp": datetime.utcnow().isoformat()
        },
    }, 'tracking')

    return {"status": "updated", "message": "Location updated successfully"}


# ==================== Truck Routes ====================

@router.get("/trucks")
async def get_trucks(
    active_only: bool = Query(False),
    limit: int = Query(100),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all trucks with optional filtering for active only
    """
    query = select(TruckLocation)

    if active_only:
        # Filter for recent updates (last 30 minutes)
        cutoff_time = datetime.utcnow() - timedelta(minutes=30)
        query = query.where(TruckLocation.last_update > cutoff_time)

    try:
        result = await db.execute(query.offset(offset).limit(limit))
        trucks = result.scalars().all()
    except OperationalError as exc:
        logger.warning("Transport trucks query unavailable: %s", exc)
        return []

    return [_serialize_truck(truck) for truck in trucks]


@router.get("/trucks/{truck_id}")
async def get_truck(truck_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get details of a specific truck
    """
    result = await db.execute(select(TruckLocation).where(TruckLocation.id == truck_id))
    truck = result.scalar_one_or_none()

    if not truck:
        raise HTTPException(status_code=404, detail="Truck not found")

    return {
        "data": _serialize_truck(truck)
    }


@router.post("/trucks/{truck_id}/location")
async def update_truck_location(
    truck_id: int,
    location_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """
    Update truck location from driver app or tracking device
    """
    result = await db.execute(select(TruckLocation).where(TruckLocation.id == truck_id))
    truck = result.scalar_one_or_none()
    
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
    
    await db.commit()
    await db.refresh(truck)
    
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
    """
    del origin, destination, stops
    raise HTTPException(
        status_code=503,
        detail="Route optimization requires a configured routing provider and is not available in this environment",
    )


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
async def get_transport_statistics(db: AsyncSession = Depends(get_db)):
    """
    Get transport statistics and metrics
    """
    try:
        shipments_result = await db.execute(select(Shipment))
        shipments = shipments_result.scalars().all()
    except OperationalError as exc:
        logger.warning("Transport statistics shipment query unavailable: %s", exc)
        shipments = []

    try:
        trucks_result = await db.execute(select(TruckLocation))
        trucks = trucks_result.scalars().all()
    except OperationalError as exc:
        logger.warning("Transport statistics truck query unavailable: %s", exc)
        trucks = []
    
    stats = {
        "total_shipments": len(shipments),
        "in_transit": len([s for s in shipments if getattr(s, 'status', '') == 'in_transit']),
        "delivered": len([s for s in shipments if getattr(s, 'status', '') == 'delivered']),
        "delayed": len([s for s in shipments if getattr(s, 'status', '') == 'delayed']),
        "active_trucks": len([t for t in trucks if getattr(t, 'status', '') == 'moving']),
        "avg_speed": sum([getattr(t, 'speed', 0) for t in trucks]) / len(trucks) if trucks else 0,
        "total_distance_traveled": sum([getattr(t, 'odometer_km', 0) or 0 for t in trucks]),
        "fuel_consumed": None
    }
    
    return stats


@router.get("/performance")
async def get_performance_metrics(db: AsyncSession = Depends(get_db)):
    """
    Get performance metrics and KPIs
    """
    del db
    raise HTTPException(
        status_code=503,
        detail="Transport performance metrics require a configured telemetry analytics backend",
    )
