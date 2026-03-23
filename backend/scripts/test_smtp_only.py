#!/usr/bin/env python
"""
SMTP authentication smoke test.

Tests SMTP login only and does not send any email.
"""

from __future__ import annotations

import smtplib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.config import settings


def main() -> None:
    host = settings.SMTP_HOST
    port = settings.SMTP_PORT
    user = settings.SMTP_USER
    from_email = settings.SMTP_FROM

    print("\n" + "=" * 60)
    print("SMTP Authentication Test")
    print("=" * 60)
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"SMTP_USER: {user}")
    print(f"SMTP_FROM: {from_email}")

    if not host or not port or not user or not settings.SMTP_PASSWORD:
        print("FAIL: SMTP settings are incomplete.")
        raise SystemExit(1)

    try:
        if int(port) == 465:
            server = smtplib.SMTP_SSL(host, int(port), timeout=20)
        else:
            server = smtplib.SMTP(host, int(port), timeout=20)
            if settings.SMTP_SECURE:
                server.ehlo()
                server.starttls()
                server.ehlo()

        try:
            server.login(user, settings.SMTP_PASSWORD)
            print("OK: authentication succeeded")
        finally:
            server.quit()
    except Exception as exc:
        print(f"FAIL: {type(exc).__name__}: {exc}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
