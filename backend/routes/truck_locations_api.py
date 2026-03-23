# ✅ File path: routes/truck_locations_api.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import random
import asyncio

router = APIRouter()
active_connections: List[WebSocket] = []

@router.websocket("/ws/trucks/live")
async def truck_location_ws(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            truck_data = {
                "id": random.randint(1000, 9999),
                "latitude": round(random.uniform(25.0, 50.0), 6),
                "longitude": round(random.uniform(-125.0, -70.0), 6),
                "status": random.choice(["Loading", "In Transit", "Delivered"])
            }
            for connection in active_connections:
                await connection.send_json(truck_data)
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        active_connections.remove(websocket)
