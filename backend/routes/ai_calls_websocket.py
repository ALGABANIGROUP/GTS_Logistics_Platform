# ✅ WebSocket Endpoint for AI Call Manager
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import random
from datetime import datetime

router = APIRouter()
call_connections = []

@router.websocket("/ws/ai/calls")
async def call_manager_websocket(websocket: WebSocket):
    await websocket.accept()
    call_connections.append(websocket)
    try:
        while True:
            # 🔁 Simulate a smart call event from AI
            fake_call = {
                "caller": f"+1-202-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                "status": random.choice(["initiated", "in_progress", "completed", "failed"]),
                "timestamp": datetime.utcnow().isoformat(),
                "reason": random.choice([
                    "Follow-up on delayed shipment",
                    "Customer inquiry - pricing",
                    "Carrier not responding",
                    "Automated confirmation call"
                ])
            }

            for conn in call_connections:
                await conn.send_json(fake_call)

            await asyncio.sleep(15)
    except WebSocketDisconnect:
        call_connections.remove(websocket)
