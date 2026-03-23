from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from datetime import datetime
import asyncio
import random

router = APIRouter()

# List of active WebSocket connections
call_ws_connections = []

# WebSocket route to display real-time smart call updates
@router.websocket("/ws/ai/calls")
async def ai_calls_websocket(websocket: WebSocket):
    await websocket.accept()
    call_ws_connections.append(websocket)
    try:
        while True:
            # Simulate a smart call event
            sample_call = {
                "client": random.choice(["John Doe", "Sarah Malik", "Carlos Rivera"]),
                "event": "shipment delayed",
                "summary": "Hello, this is GTS AI assistant. Your shipment SH12345 is delayed due to weather. We're working to resolve it and will update you shortly.",
                "timestamp": datetime.utcnow().isoformat()
            }

            for conn in call_ws_connections:
                await conn.send_json(sample_call)

            await asyncio.sleep(15)
    except WebSocketDisconnect:
        call_ws_connections.remove(websocket)
