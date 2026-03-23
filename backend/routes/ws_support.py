from fastapi import APIRouter, WebSocket
from backend.models.support_ticket import SupportTicket
from backend.database.config import get_db
from sqlalchemy.ext.asyncio import AsyncSession
import json
router = APIRouter()
connected_clients = []

@router.websocket('/ws/support/updates')
async def support_ws(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except Exception:
        connected_clients.remove(websocket)

async def broadcast_new_ticket(ticket: SupportTicket):
    message = {'id': ticket.id, 'customer_name': ticket.customer_name, 'subject': ticket.subject, 'status': ticket.status, 'created_at': str(ticket.created_at)}
    for client in connected_clients:
        try:
            await client.send_text(json.dumps(message))
        except:
            pass
