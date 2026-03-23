from .base import Base

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List

router = APIRouter()

active_notification_connections: List[WebSocket] = []

@router.websocket("/ws/notifications")
async def websocket_notifications(websocket: WebSocket):
    await websocket.accept()
    active_notification_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()  # Wait for ping or message (optional)
    except WebSocketDisconnect:
        active_notification_connections.remove(websocket)

# Broadcast notification to all active WebSocket clients
async def broadcast_notification(data: dict):
    for connection in active_notification_connections:
        await connection.send_json(data)
