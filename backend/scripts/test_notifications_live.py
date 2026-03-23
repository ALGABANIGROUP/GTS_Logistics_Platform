#!/usr/bin/env python
"""
Live notification test.

Sends one real email to verify SMTP authentication and delivery path.
Use a disposable or controlled test mailbox.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.config import settings
from backend.services.notification_service import notification_service
from backend.utils.email_utils import send_bot_email


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Send one live notification email.")
    parser.add_argument(
        "--to",
        required=True,
        help="Recipient email address for the live test.",
    )
    parser.add_argument(
        "--skip-service",
        action="store_true",
        help="Only test direct send_bot_email and skip notification_service.",
    )
    parser.add_argument(
        "--plain",
        action="store_true",
        help="Force plain-text direct send instead of HTML.",
    )
    return parser


async def test_live_email(recipient: str, skip_service: bool, plain: bool) -> None:
    print("\n" + "=" * 60)
    print("Live Email Test")
    print("=" * 60)
    print(f"\nRecipient: {recipient}")
    print(f"SMTP host: {settings.SMTP_HOST}")
    print(f"SMTP port: {settings.SMTP_PORT}")
    print(f"SMTP sender: {settings.SMTP_FROM or settings.SMTP_USER}")

    context = {
        "user_name": "Live Test User",
        "timestamp": "2026-03-19 12:00:00 UTC",
        "ip_address": "127.0.0.1",
        "device": "Live Test Script",
        "user_email": recipient,
    }

    print("\nRendering template...")
    rendered = await notification_service.render_template("security_login_success", context)
    print(f"  OK subject: {rendered['subject']}")
    print(f"  OK body length: {len(rendered['body'])}")

    print("\nSending via send_bot_email...")
    direct_result = send_bot_email(
        bot_name="security_manager",
        subject=rendered["subject"],
        body=rendered["body"],
        to=[recipient],
        html=not plain,
        plain_text=rendered["text_body"],
    )
    print(f"  HTML mode: {not plain}")
    print(f"  Result: {direct_result}")

    if skip_service:
        print("\nSkipped notification_service test")
        return

    print("\nSending via notification_service...")
    service_result = await notification_service.send_security_notification(
        event_type="login_success",
        user_email=recipient,
        user_name="Live Test User",
        ip_address="127.0.0.1",
        device="Live Test Script",
    )
    print(f"  Result: {service_result}")


if __name__ == "__main__":
    args = build_parser().parse_args()
    asyncio.run(test_live_email(args.to, args.skip_service, args.plain))
