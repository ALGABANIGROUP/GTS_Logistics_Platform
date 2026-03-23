"""Pipeline entry to connect pollers/IMAP to the intelligent processor + router."""
from __future__ import annotations

from typing import Any, Dict

from backend.email_service import IntelligentEmailProcessor, IntelligentEmailRouter, EmailBotMonitor
from backend.utils.email_utils import send_email

processor = IntelligentEmailProcessor()
router = IntelligentEmailRouter()
monitor = EmailBotMonitor()


def process_incoming(email_message: Dict[str, Any]) -> Dict[str, Any]:
    """Main entrypoint: run processor -> router -> monitoring -> optional auto-response."""
    proc_result = processor.process_incoming_email(email_message)
    route_result = router.route_and_process(email_message)
    monitor.track_processing(proc_result.get("bot", "unknown"), email_message.get("id"), route_result)

    # Optional auto-response using send_email if requested
    if proc_result.get("response_sent") and email_message.get("from"):
        send_email(
            subject="Acknowledged",
            body="We have received your email and are processing it.",
            to=[email_message.get("from")],
        )

    return {
        "processor": proc_result,
        "router": route_result,
        "metrics": monitor.metrics,
    }
