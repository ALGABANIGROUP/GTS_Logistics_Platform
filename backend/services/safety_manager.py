# backend/services/safety_manager.py
from __future__ import annotations

from datetime import datetime
from typing import Optional, List, Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.models.models import Shipment
from backend.models.message_log import MessageLog
from backend.utils.email_utils import send_bot_email
from backend.services.notification_service import notification_service
import asyncio


class SafetyManager:
    """
    Simple safety manager that scans shipments, detects potential issues,
    logs them, and notifies the safety team (and optionally the driver).
    """

    def __init__(self, safety_team_email: str = "safety@gabanilogistics.com") -> None:
        self.safety_team_email = safety_team_email

    async def scan_shipments_for_issues(self, db: AsyncSession) -> None:
        """
        Fetch shipments and detect basic safety issues.
        """
        result = await db.execute(select(Shipment))
        shipments: Sequence[Shipment] = result.scalars().all()

        now = datetime.utcnow()

        for shipment in shipments:
            issue = self._detect_issue(shipment, now)
            if not issue:
                continue

            await self._log_issue(db, shipment, issue)
            await self._notify_team_and_driver(shipment, issue)

        await db.commit()

    def _detect_issue(self, shipment: Shipment, now: datetime) -> Optional[str]:
        """
        Very simple rules:
          - Delayed shipment past estimated delivery and not delivered.
          - Hazmat shipment without a recorded safety check flag.
        """
        status = str(getattr(shipment, "status", "") or "").lower()

        # Ignore cancelled/canceled shipments
        if status in ("cancelled", "canceled"):
            return None

        eta = getattr(shipment, "estimated_delivery", None) or getattr(
            shipment, "delivery_date", None
        )
        if isinstance(eta, datetime) and eta < now and status not in ("delivered", "completed"):
            return "Shipment appears delayed past the estimated delivery time."

        if bool(getattr(shipment, "hazmat", False)) and not bool(
            getattr(shipment, "safety_checked", False)
        ):
            return "HAZMAT shipment does not have a recorded safety check."

        return None

    async def _log_issue(self, db: AsyncSession, shipment: Shipment, issue: str) -> None:
        """
        Store a basic log entry about the safety issue.
        Adjust the fields to match MessageLog model if needed.
        """
        try:
            log_entry = MessageLog(
                subject="Safety issue detected",
                message=issue,
                shipment_id=getattr(shipment, "id", None),
                created_at=datetime.utcnow(),
            )
        except TypeError:
            # Fallback if MessageLog has different columns
            log_entry = MessageLog()  # type: ignore[call-arg]
            # If your MessageLog model has specific attributes, set them here
            # e.g. log_entry.text = issue

        db.add(log_entry)

    async def _notify_team_and_driver(self, shipment: Shipment, issue: str) -> None:
        """
        Send an email to the safety team and optionally to the driver.
        """
        driver_email = (getattr(shipment, "driver_email", None) or "").strip()

        reference = (
            getattr(shipment, "reference", None)
            or getattr(shipment, "tracking_number", None)
            or ""
        ).strip()

        subject = f"GTS Safety Alert – Shipment {reference or '#'}".strip()

        body_lines = [
            "A potential safety issue has been detected on a shipment.",
            "",
            f"Issue: {issue}",
            f"Shipment reference: {reference or 'N/A'}",
            "",
            "Please review this shipment in the GTS portal.",
        ]
        body = "\n".join(body_lines)

        recipients: list[str] = [self.safety_team_email]
        if driver_email:
            recipients.append(driver_email)

        send_bot_email(
            bot_name="safety",
            to=recipients,
            subject=subject,
            body=body,
        )
        try:
            asyncio.create_task(
                notification_service.send_safety_notification(
                    event_type="incident",
                    user_email=self.safety_team_email,
                    user_name="Safety Team",
                    safety_data={
                        "incident_id": reference or getattr(shipment, "id", "N/A"),
                        "incident_type": "shipment_issue",
                        "location": getattr(shipment, "pickup_location", None)
                        or getattr(shipment, "dropoff_location", None)
                        or "Unknown",
                        "severity": "medium",
                        "reported_by": "safety_scan",
                        "incident_url": "Safety review required",
                    },
                )
            )
        except Exception:
            pass


safety_manager = SafetyManager()
async def run_safety_scan(db: AsyncSession) -> None:
    """
    Convenience function to run the safety scan.
    """
    await safety_manager.scan_shipments_for_issues(db)
