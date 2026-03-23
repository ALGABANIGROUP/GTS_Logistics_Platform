from fastapi import APIRouter, Body
from pydantic import BaseModel

from backend.email_service import (
    IntelligentEmailProcessor,
    IntelligentEmailRouter,
    EmailBotMonitor,
)
from backend.email_service.pipeline import process_incoming

router = APIRouter()


class EmailSimulationPayload(BaseModel):
    """Minimal payload to simulate inbound email processing."""

    id: str | None = None
    from_email: str | None = None
    to: str | None = None
    subject: str | None = None
    body: str | None = None
    attachments: list[dict] | None = None


processor = IntelligentEmailProcessor()
router_engine = IntelligentEmailRouter()
monitor = EmailBotMonitor()


@router.get("/test-email", tags=["Email"])
async def test_email_route():
    """Simple route to confirm email API is reachable."""
    return {"message": "email route is working"}


@router.post("/internal/email/simulate", tags=["Email"], summary="Simulate intelligent email processing")
async def simulate_email(payload: EmailSimulationPayload = Body(...)):
    # Step 1: classify and map to bot
    email_dict = {
        "id": payload.id,
        "from": payload.from_email,
        "to": payload.to,
        "subject": payload.subject,
        "body": payload.body,
        "attachments": payload.attachments or [],
    }
    proc_result = processor.process_incoming_email(email_dict)

    # Step 2: run through workflow router
    route_result = router_engine.route_and_process(email_dict)

    # Step 3: record monitoring stats
    monitor.track_processing(proc_result.get("bot", "unknown"), payload.id, route_result)

    # Step 4: return combined
    return {
        "processor": proc_result,
        "router": route_result,
        "metrics": monitor.metrics,
    }


@router.post("/internal/email/process", tags=["Email"], summary="Entry for real inbound email pipeline")
async def process_email(payload: EmailSimulationPayload = Body(...)):
    """Endpoint to be called by the IMAP/poller once a message is fetched."""
    email_dict = {
        "id": payload.id,
        "from": payload.from_email,
        "to": payload.to,
        "subject": payload.subject,
        "body": payload.body,
        "attachments": payload.attachments or [],
    }
    return process_incoming(email_dict)