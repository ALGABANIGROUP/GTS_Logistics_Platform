# ✅ Path: routes/ws_notifications.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import asyncio
import datetime

router = APIRouter()

# List to store all connected WebSocket clients
connected_clients: List[WebSocket] = []

@router.websocket("/ws/notifications")
async def websocket_notifications(websocket: WebSocket):
    # Accept the incoming WebSocket connection
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            # Create a notification message
            notification = {
                "type": "info",
                "message": "📦 New shipment assigned.",
                "timestamp": datetime.datetime.utcnow().isoformat()
            }
            # Send the notification to all connected clients
            for client in connected_clients:
                await client.send_json(notification)
            # Wait for 15 seconds before sending the next notification
            await asyncio.sleep(15)
    except WebSocketDisconnect:
        # Remove the disconnected client
        connected_clients.remove(websocket)
