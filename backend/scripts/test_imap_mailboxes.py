#!/usr/bin/env python
from __future__ import annotations

import asyncio
import imaplib
import logging
import sys
from pathlib import Path
from typing import Any, Dict

from sqlalchemy import select
from sqlalchemy.orm import selectinload

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.config import settings
from backend.database.config import get_sessionmaker
from backend.models.email_center import Mailbox
from backend.services.email_crypto import decrypt_credentials

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class IMAPMailboxTester:
    def __init__(self) -> None:
        self.session_maker = get_sessionmaker()
        self.results: Dict[str, Dict[str, Any]] = {}

    async def test_all(self) -> Dict[str, Dict[str, Any]]:
        async with self.session_maker() as session:
            result = await session.execute(
                select(Mailbox)
                .where(Mailbox.is_enabled == True)
                .options(selectinload(Mailbox.credentials))
                .order_by(Mailbox.email_address.asc())
            )
            mailboxes = result.scalars().all()

            logger.info("Testing %s mailboxes", len(mailboxes))
            for mailbox in mailboxes:
                self.results[mailbox.email_address] = await self._test_mailbox(mailbox)
            return self.results

    async def _test_mailbox(self, mailbox: Mailbox) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "id": mailbox.id,
            "email": mailbox.email_address,
            "display_name": mailbox.display_name,
            "mode": mailbox.mode,
            "inbound_enabled": mailbox.inbound_enabled,
            "imap_host": mailbox.imap_host or settings.IMAP_HOST,
            "imap_port": mailbox.imap_port or settings.IMAP_PORT,
            "imap_user": mailbox.imap_user or mailbox.email_address or settings.IMAP_USER,
            "imap_ssl": mailbox.imap_ssl if mailbox.imap_ssl is not None else settings.IMAP_SSL,
            "status": "unknown",
            "error": None,
            "folders": [],
            "inbox_count": None,
        }

        if not mailbox.inbound_enabled:
            result["status"] = "skipped (inbound disabled)"
            return result

        password = self._get_password(mailbox)
        if not password:
            result["status"] = "failed"
            result["error"] = "No password available"
            return result

        try:
            if result["imap_ssl"]:
                imap = imaplib.IMAP4_SSL(result["imap_host"], int(result["imap_port"]))
            else:
                imap = imaplib.IMAP4(result["imap_host"], int(result["imap_port"]))

            imap.login(str(result["imap_user"]), password)

            typ, folder_data = imap.list()
            if typ == "OK" and folder_data:
                folders = []
                for line in folder_data[:5]:
                    if isinstance(line, bytes):
                        folders.append(line.decode("utf-8", errors="ignore"))
                    else:
                        folders.append(str(line))
                result["folders"] = folders

            typ, status_data = imap.status("INBOX", "(MESSAGES)")
            if typ == "OK" and status_data:
                status_text = (
                    status_data[0].decode("utf-8", errors="ignore")
                    if isinstance(status_data[0], bytes)
                    else str(status_data[0])
                )
                parts = status_text.replace("(", " ").replace(")", " ").split()
                if "MESSAGES" in parts:
                    idx = parts.index("MESSAGES")
                    if idx + 1 < len(parts):
                        result["inbox_count"] = int(parts[idx + 1])

            imap.logout()
            result["status"] = "success"
            logger.info("OK %s", mailbox.email_address)
        except Exception as exc:
            result["status"] = "failed"
            result["error"] = str(exc)[:200]
            logger.error("FAIL %s: %s", mailbox.email_address, result["error"])

        return result

    def _get_password(self, mailbox: Mailbox) -> str | None:
        if mailbox.credentials and mailbox.credentials.credentials_ciphertext:
            try:
                return decrypt_credentials(mailbox.credentials.credentials_ciphertext)
            except Exception:
                pass
        return settings.IMAP_PASSWORD or None

    def print_summary(self) -> None:
        print("\n" + "=" * 80)
        print("IMAP Mailbox Test Summary")
        print("=" * 80)

        success = []
        failed = []
        skipped = []

        for email, result in self.results.items():
            if result["status"] == "success":
                success.append(email)
            elif result["status"].startswith("skipped"):
                skipped.append(email)
            else:
                failed.append(email)

        print(f"\nSuccess: {len(success)}")
        for email in success:
            data = self.results[email]
            print(f"  - {email} | inbox={data.get('inbox_count', 0)}")

        print(f"\nFailed: {len(failed)}")
        for email in failed:
            data = self.results[email]
            print(f"  - {email}: {data.get('error')}")

        if skipped:
            print(f"\nSkipped: {len(skipped)}")
            for email in skipped:
                print(f"  - {email}")

        print("\n" + "=" * 80)
        print("Security note:")
        print("  - Passwords are read from encrypted mailbox credentials or environment variables only.")
        print("  - No passwords are logged or written to disk.")


async def main() -> None:
    print("IMAP Mailbox Tester - Running")
    print("=" * 80)
    tester = IMAPMailboxTester()
    await tester.test_all()
    tester.print_summary()


if __name__ == "__main__":
    asyncio.run(main())
