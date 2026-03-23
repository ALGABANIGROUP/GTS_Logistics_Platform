from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import logging

from backend.bots.ws_manager import hub, broadcast_event as _broadcast_event

router = APIRouter()
log = logging.getLogger(__name__)

broadcast_event = _broadcast_event

@router.websocket("/live")
async def live_ws(ws: WebSocket):
    await hub.connect(ws)

    try:
        await hub.send(ws, {"type": "hello", "message": "ws live connected"})
    except Exception as e:
        log.warning("WS hello send failed: %s", e)
        await hub.disconnect(ws)
        return

    try:
        while True:
            text = await ws.receive_text()
            try:
                msg = json.loads(text)
            except Exception:
                continue

            msg_type = msg.get("type")
            if msg_type == "ping":
                await hub.send(ws, {"type": "pong"})
                continue
            if msg_type == "subscribe":
                channel = msg.get("channel") or ""
                await hub.subscribe(ws, channel)
                await hub.send(ws, {"type": "subscribed", "channel": channel})
                continue
            if msg_type == "unsubscribe":
                channel = msg.get("channel") or ""
                await hub.unsubscribe(ws, channel)
                await hub.send(ws, {"type": "unsubscribed", "channel": channel})
                continue

    except WebSocketDisconnect:
        await hub.disconnect(ws)
        return
    except Exception as e:
        log.exception("WS crashed: %s", e)
        await hub.disconnect(ws)
        return
