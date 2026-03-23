# routes/ws_marketing_updates.py

import asyncio
import random
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()
active_clients = []

# WebSocket endpoint for live marketing updates
@router.websocket("/ws/marketing/updates")
async def marketing_updates_websocket(websocket: WebSocket):
    await websocket.accept()
    active_clients.append(websocket)

    try:
        while True:
            # Mocked data for live marketing updates
            update = {
                "campaign": random.choice(["Spring Sale", "Winter Promo", "Email Blitz"]),
                "status": random.choice(["Running", "Completed", "Paused"]),
                "open_rate": round(random.uniform(20.0, 80.0), 2),
                "click_rate": round(random.uniform(5.0, 25.0), 2),
                "timestamp": asyncio.get_event_loop().time()
            }

            for client in active_clients:
                await client.send_json(update)

            await asyncio.sleep(15)  # send updates every 15 seconds

    except WebSocketDisconnect:
        active_clients.remove(websocket)
