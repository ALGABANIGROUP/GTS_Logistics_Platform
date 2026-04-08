from __future__ import annotations

import json
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


@router.websocket("/api/v1/ws/customer-service")
async def customer_service_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    await websocket.send_json(
        {
            "channel": "system",
            "type": "connected",
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

    try:
        while True:
            raw_message = await websocket.receive_text()
            try:
                payload = json.loads(raw_message)
            except json.JSONDecodeError:
                payload = {"message": raw_message}

            await websocket.send_json(
                {
                    "channel": payload.get("channel", "system"),
                    "type": "ack",
                    "payload": payload,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
    except WebSocketDisconnect:
        return
