#!/usr/bin/env python
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.config import settings
from backend.services.notification_service import notification_service
from backend.utils.email_utils import BOT_SENDERS


async def main() -> None:
    print("\n" + "=" * 60)
    print("Notification System Smoke Test")
    print("=" * 60)

    context = {
        "user_name": "Test User",
        "user_email": "test@example.com",
        "shipment_id": 42,
        "origin": "Toronto",
        "destination": "Montreal",
        "estimated_delivery": "2026-03-20",
        "tracking_url": "http://test.local/shipments/42",
        "amount": 1500.0,
        "currency": "USD",
        "invoice_number": "INV-2026-001",
        "due_date": "2026-03-25",
        "customer_name": "Test Customer",
        "invoice_url": "http://test.local/invoices/1",
        "payment_date": "2026-03-18",
        "payment_method": "Smoke Test",
        "receipt_url": "http://test.local/invoices/1/receipt",
        "days_overdue": 2,
        "ip_address": "127.0.0.1",
        "device": "Smoke Test Device",
        "timestamp": "2026-03-18 15:30:00 UTC",
        "document_name": "Sample Document.pdf",
        "document_type": "contract",
        "uploaded_by": "Smoke Test",
        "file_size": "24 KB",
        "document_url": "http://test.local/documents/1",
        "incident_id": "INC-42",
        "incident_type": "vehicle_issue",
        "location": "Toronto",
        "severity": "medium",
        "reported_by": "Smoke Test",
        "incident_url": "http://test.local/incidents/42",
    }

    print("\n1. Template rendering")
    for template_key in [
        "security_login_success",
        "shipment_created",
        "finance_invoice_created",
        "document_uploaded",
        "safety_incident_reported",
    ]:
        rendered = await notification_service.render_template(template_key, context)
        print(f"  [OK] {template_key}: {rendered['subject']}")

    print("\n2. Bot sender mapping")
    required_bots = [
        "security_manager",
        "finance_bot",
        "documents_manager",
        "freight_broker",
        "safety_manager",
        "maintenance_dev",
        "general_manager",
        "operations_manager",
        "system_admin",
        "legal_consultant",
        "sales_team",
        "partner_manager",
    ]
    missing = [bot for bot in required_bots if bot not in BOT_SENDERS]
    for bot in required_bots:
        sender = BOT_SENDERS.get(bot, "MISSING")
        label = "OK" if bot in BOT_SENDERS else "FAIL"
        print(f"  [{label}] {bot:20} -> {sender}")
    if missing:
        raise RuntimeError(f"Missing bot senders: {', '.join(missing)}")

    print("\n3. Notification methods")
    methods = [
        "send_security_notification",
        "send_shipment_notification",
        "send_finance_notification",
        "send_document_notification",
        "send_safety_notification",
    ]
    for method_name in methods:
        if not hasattr(notification_service, method_name):
            raise AttributeError(f"Missing method: {method_name}")
        print(f"  [OK] {method_name}")

    print("\n4. SMTP configuration")
    smtp_fields = {
        "SMTP_HOST": settings.SMTP_HOST,
        "SMTP_PORT": settings.SMTP_PORT,
        "SMTP_USER": settings.SMTP_USER,
        "SMTP_FROM": settings.SMTP_FROM,
    }
    for key, value in smtp_fields.items():
        state = "OK" if value else "WARN"
        print(f"  [{state}] {key:10} = {value or 'NOT SET'}")

    print("\n5. Background task support")
    async def _noop() -> str:
        return "done"
    task = asyncio.create_task(_noop())
    await task
    print("  [OK] asyncio.create_task works")

    print("\n6. Email preparation")
    rendered = await notification_service.render_template("security_login_success", context)
    print(f"  [OK] Subject: {rendered['subject']}")
    print(f"  [OK] Body length: {len(rendered['body'])}")

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Templates checked: 5")
    print(f"Bot senders available: {len(BOT_SENDERS)}")
    print(f"Methods checked: {len(methods)}")
    print("Smoke test completed")


if __name__ == "__main__":
    asyncio.run(main())
