from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.ai.customer_service import customer_service_learning_bot
from backend.database.config import get_db_async

router = APIRouter(prefix="/api/v1/customer-service", tags=["Customer Service"])


class TicketCreateIn(BaseModel):
    customer_email: str
    subject: str
    description: str


class TicketUpdateIn(BaseModel):
    subject: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[int] = None
    comments: Optional[List[Dict[str, Any]]] = None


class TicketOut(BaseModel):
    id: int
    customer_email: str
    subject: str
    description: str
    status: str
    created_at: datetime
    priority: Optional[str] = None
    assigned_to: Optional[int] = None


class ChatRequest(BaseModel):
    message: str
    user_id: str
    conversation_id: Optional[str] = None


class FeedbackRequest(BaseModel):
    conversation_id: str
    rating: int
    feedback: Optional[str] = None


@router.get("/analytics/live-stats")
async def get_live_stats() -> Dict[str, Any]:
    stats = customer_service_learning_bot.get_stats()
    return {
        "activeConversations": stats["conversations"],
        "pendingTickets": stats["pending_tickets"],
        "avgResponseTime": f'{round(stats["average_response_time_ms"])}ms' if stats["average_response_time_ms"] else "0ms",
        "satisfactionRate": f'{round((stats["average_rating"] / 5) * 100)}%' if stats["average_rating"] else "0%",
    }


@router.get("/analytics/recent-activity")
async def get_recent_activity(range: str = "today") -> Dict[str, Any]:
    return {
        "range": range,
        "activity": customer_service_learning_bot.get_recent_activity(range),
    }


@router.get("/analytics/top-agents")
async def get_top_agents() -> Dict[str, Any]:
    return {"agents": customer_service_learning_bot.get_top_agents()}


@router.get("/analytics/conversation-metrics")
async def get_conversation_metrics(range: str = "today") -> Dict[str, Any]:
    return customer_service_learning_bot.get_conversation_metrics(range)


@router.get("/tickets", response_model=List[TicketOut])
async def get_tickets(
    id: Optional[int] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assigned_to: Optional[int] = None,
    search: Optional[str] = None,
) -> List[TicketOut]:
    """Get all customer service tickets."""
    tickets = customer_service_learning_bot.list_tickets({
        "id": id,
        "status": status,
        "priority": priority,
        "assigned_to": assigned_to,
        "search": search,
    })
    return [
        TicketOut(
            id=ticket["id"],
            customer_email=ticket["customer_email"],
            subject=ticket["subject"],
            description=ticket["description"],
            status=ticket["status"],
            created_at=datetime.fromisoformat(ticket["created_at"]),
            priority=ticket.get("priority"),
            assigned_to=ticket.get("assigned_to"),
        )
        for ticket in tickets
    ]


@router.post("/tickets", response_model=TicketOut)
async def create_ticket(
    payload: TicketCreateIn,
    db: AsyncSession = Depends(get_db_async),
) -> TicketOut:
    """Create a new support ticket."""
    ticket = customer_service_learning_bot.create_ticket(
        customer_email=payload.customer_email,
        subject=payload.subject,
        description=payload.description,
        customer_name=payload.customer_email.split("@")[0],
    )
    try:
        from backend.services.platform_webhook_dispatcher import dispatch_from_platform_settings

        await dispatch_from_platform_settings(
            db=db,
            event_type="support.ticket.created",
            data={
                "ticket_id": ticket["id"],
                "customer_email": ticket["customer_email"],
                "subject": ticket["subject"],
                "status": ticket["status"],
            },
        )
    except Exception:
        pass
    return TicketOut(
        id=ticket["id"],
        customer_email=ticket["customer_email"],
        subject=ticket["subject"],
        description=ticket["description"],
        status=ticket["status"],
        created_at=datetime.fromisoformat(ticket["created_at"]),
        priority=ticket.get("priority"),
        assigned_to=ticket.get("assigned_to"),
    )


@router.put("/tickets/{ticket_id}", response_model=TicketOut)
async def update_ticket(
    ticket_id: int,
    payload: TicketUpdateIn,
    db: AsyncSession = Depends(get_db_async),
) -> TicketOut:
    """Update an existing customer service ticket."""
    try:
        ticket = customer_service_learning_bot.update_ticket(ticket_id, payload.model_dump(exclude_none=True))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Ticket not found") from exc
    try:
        from backend.services.platform_webhook_dispatcher import dispatch_from_platform_settings

        await dispatch_from_platform_settings(
            db=db,
            event_type="support.ticket.updated",
            data={
                "ticket_id": ticket["id"],
                "subject": ticket["subject"],
                "status": ticket["status"],
            },
        )
    except Exception:
        pass
    return TicketOut(
        id=ticket["id"],
        customer_email=ticket["customer_email"],
        subject=ticket["subject"],
        description=ticket["description"],
        status=ticket["status"],
        created_at=datetime.fromisoformat(ticket["created_at"]),
        priority=ticket.get("priority"),
        assigned_to=ticket.get("assigned_to"),
    )


@router.post("/tickets/{ticket_id}/close")
async def close_ticket(
    ticket_id: int,
    payload: Optional[Dict[str, Any]] = None,
    db: AsyncSession = Depends(get_db_async),
) -> Dict[str, Any]:
    """Close a support ticket."""
    resolution = (payload or {}).get("resolution", "")
    try:
        ticket = customer_service_learning_bot.close_ticket(ticket_id, resolution)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Ticket not found") from exc
    try:
        from backend.services.platform_webhook_dispatcher import dispatch_from_platform_settings

        await dispatch_from_platform_settings(
            db=db,
            event_type="support.ticket.closed",
            data={
                "ticket_id": ticket_id,
                "resolution": resolution,
            },
        )
    except Exception:
        pass
    return {"ok": True, "ticket_id": ticket["id"], "status": ticket["status"], "resolution": resolution}


@router.get("/conversations")
async def get_conversations(status: Optional[str] = None, channel: Optional[str] = None) -> Dict[str, Any]:
    return {"conversations": customer_service_learning_bot.list_conversations({"status": status, "channel": channel})}


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(conversation_id: str) -> Dict[str, Any]:
    conversation = customer_service_learning_bot.get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"conversation_id": conversation_id, "messages": conversation.get("messages", [])}


@router.post("/conversations")
async def start_conversation(payload: Dict[str, Any]) -> Dict[str, Any]:
    user_id = str(payload.get("user_id") or "guest")
    conversation_id = payload.get("conversation_id")
    conversation = customer_service_learning_bot.start_conversation(
        user_id=user_id,
        conversation_id=conversation_id,
        metadata=payload,
    )
    return {"conversation": conversation}


@router.post("/conversations/{conversation_id}/read")
async def mark_conversation_read(conversation_id: str) -> Dict[str, Any]:
    return {"ok": True, "conversation_id": conversation_id}


@router.post("/ai/response")
async def generate_ai_response(payload: Dict[str, Any]) -> Dict[str, Any]:
    context = payload.get("context") or []
    fallback_message = payload.get("message")
    user_message = fallback_message
    for entry in reversed(context):
        if entry.get("role") == "user" and entry.get("content"):
            user_message = entry["content"]
            break
    if not user_message:
        raise HTTPException(status_code=400, detail="Message content is required")

    conversation_id = payload.get("conversation_id") or f"conv_{int(datetime.utcnow().timestamp())}"
    user_id = str(payload.get("user_id") or "panel-user")
    return await customer_service_learning_bot.process_message(
        message=user_message,
        user_id=user_id,
        conversation_id=conversation_id,
    )


@router.post("/chat")
async def chat(request: ChatRequest) -> Dict[str, Any]:
    conversation_id = request.conversation_id or f"conv_{request.user_id}_{int(datetime.utcnow().timestamp())}"
    return await customer_service_learning_bot.process_message(
        message=request.message,
        user_id=request.user_id,
        conversation_id=conversation_id,
    )


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest) -> Dict[str, Any]:
    if request.rating < 1 or request.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    try:
        customer_service_learning_bot.collect_conversation_feedback(
            conversation_id=request.conversation_id,
            rating=request.rating,
            feedback=request.feedback,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Conversation not found") from exc
    return {"status": "success", "message": "Feedback recorded"}


@router.get("/stats")
async def get_customer_service_stats() -> Dict[str, Any]:
    return customer_service_learning_bot.get_stats()


@router.get("/calls/active")
async def get_active_calls() -> Dict[str, Any]:
    return {"calls": []}


@router.post("/calls/outbound")
async def make_outbound_call(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "call": {
            "id": f"call_{int(datetime.utcnow().timestamp())}",
            "status": "dialing",
            **payload,
        }
    }


@router.post("/calls/{call_id}/answer")
async def answer_call(call_id: str) -> Dict[str, Any]:
    return {"ok": True, "call_id": call_id, "status": "in_progress"}


@router.post("/calls/{call_id}/end")
async def end_call(call_id: str) -> Dict[str, Any]:
    return {"ok": True, "call_id": call_id, "status": "ended"}


@router.post("/calls/{call_id}/transfer")
async def transfer_call(call_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "ok": True,
        "call_id": call_id,
        "target_agent": payload.get("target_agent"),
    }


@router.post("/calls/{call_id}/recording/start")
async def start_recording(call_id: str) -> Dict[str, Any]:
    return {"ok": True, "call_id": call_id, "recording": True}


@router.get("/messaging/campaigns")
async def get_campaigns() -> Dict[str, Any]:
    return {"campaigns": []}


@router.post("/messaging/campaigns")
async def create_campaign(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "campaign": {
            "id": f"camp_{int(datetime.utcnow().timestamp())}",
            "status": "draft",
            **payload,
        }
    }


@router.post("/messaging/campaigns/{campaign_id}/launch")
async def launch_campaign(campaign_id: str) -> Dict[str, Any]:
    return {"ok": True, "campaign_id": campaign_id, "status": "launched"}


@router.post("/messaging/campaigns/{campaign_id}/test")
async def send_test_message(campaign_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "ok": True,
        "campaign_id": campaign_id,
        "phone_number": payload.get("phone_number"),
    }


@router.get("/messaging/queue")
async def get_message_queue() -> Dict[str, Any]:
    return {"queue": []}
