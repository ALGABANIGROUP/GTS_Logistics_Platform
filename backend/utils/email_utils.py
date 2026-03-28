import logging
import smtplib
from email.message import EmailMessage
from html import unescape
from html import escape as html_escape
import base64
from pathlib import Path
import re
from typing import Sequence

from backend.config import settings  # type: ignore[import]

logger = logging.getLogger(__name__)
_SMTP_TIMEOUT_SECONDS = 20

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_PLATFORM_LOGO_PATH = _PROJECT_ROOT / "frontend" / "src" / "assets" / "gabani_logo.png"


def _load_platform_logo_base64() -> str:
    try:
        if _PLATFORM_LOGO_PATH.exists():
            return base64.b64encode(_PLATFORM_LOGO_PATH.read_bytes()).decode("ascii")
    except Exception:
        return ""
    return ""


_PLATFORM_LOGO_BASE64 = _load_platform_logo_base64()


BOT_EMAIL_MAPPING = {
    "operations": "operations@gabanilogistics.com",
    "operations_manager": "operations@gabanilogistics.com",
    "operations_manager_bot": "operations@gabanilogistics.com",
    "freight": "freight@gabanilogistics.com",
    "freight_broker": "freight@gabanilogistics.com",
    "mapleload": "freight@gabanilogistics.com",
    "mapleload_bot": "freight@gabanilogistics.com",
    "mapleload_canada": "freight@gabanilogistics.com",
    "ai_dispatcher": "aidispatcher@gabanistore.com",
    "dispatcher": "aidispatcher@gabanistore.com",
    "information_coordinator": "intel@gabanilogistics.com",
    "intel": "intel@gabanilogistics.com",
    "intelligence_bot": "strategy@gabanilogistics.com",
    "executive_intelligence": "strategy@gabanilogistics.com",
    "general_manager": "operations@gabanilogistics.com",
    "strategy_advisor": "strategy@gabanilogistics.com",
    "finance": "finance@gabanilogistics.com",
    "finance_bot": "finance@gabanilogistics.com",
    "platform_expenses": "accounts@gabanilogistics.com",
    "expenses": "accounts@gabanilogistics.com",
    "documents": "doccontrol@gabanilogistics.com",
    "documents_manager": "doccontrol@gabanilogistics.com",
    "customer_service": "customers@gabanilogistics.com",
    "service": "support@gabanistore.com",
    "legal": "operations@gabanilogistics.com",
    "legal_bot": "operations@gabanilogistics.com",
    "legal_consultant": "legal@gabanilogistics.com",
    "marketing": "marketing@gabanilogistics.com",
    "marketing_manager": "marketing@gabanilogistics.com",
    "sales": "sales@gabanilogistics.com",
    "sales_bot": "sales@gabanilogistics.com",
    "sales_team": "sales@gabanilogistics.com",
    "safety": "safety@gabanilogistics.com",
    "safety_manager": "safety@gabanilogistics.com",
    "safety_manager_bot": "safety@gabanilogistics.com",
    "admin": "admin@gabanilogistics.com",
    "system_admin": "admin@gabanilogistics.com",
    "system_manager_bot": "admin@gabanilogistics.com",
    "maintenance_dev": "devops@gabanilogistics.com",
    "partner_manager": "investments@gabanilogistics.com",
    "partner_bot": "investments@gabanilogistics.com",
    "security": "security@gabanistore.com",
    "security_manager": "security@gabanistore.com",
    "security_manager_bot": "security@gabanistore.com",
    "system_bot": "admin@gabanilogistics.com",
    "freight_bot": "freight@gabanilogistics.com",
    "safety_bot": "safety@gabanilogistics.com",
    "accounts": "accounts@gabanilogistics.com",
    "ai_dispatcher": "aidispatcher@gabanistore.com",
    "aidispatcher": "aidispatcher@gabanistore.com",
}

# Backward-compatible alias used by older routes and scripts.
BOT_SENDERS = BOT_EMAIL_MAPPING


def _normalize_recipients(to: Sequence[str] | str) -> list[str]:
    if isinstance(to, str):
        candidate = to.strip()
        return [candidate] if candidate else []
    return [addr.strip() for addr in to if isinstance(addr, str) and addr.strip()]


def _mailboxes_set() -> set[str]:
    raw = (settings.EMAIL_MAILBOXES or "").strip()
    if not raw:
        return set()
    return {email.strip().lower() for email in raw.split(",") if email.strip()}


def _looks_like_full_html_document(body: str) -> bool:
    head = body.lstrip()[:400].lower()
    return head.startswith("<!doctype html") or "<html" in head


def _extract_html_body_fragment(body: str) -> str:
    match = re.search(r"<body[^>]*>(.*)</body>", body, flags=re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return body


def _text_to_html(text: str) -> str:
    escaped = html_escape(unescape(text or ""))
    paragraphs = [p.strip() for p in escaped.replace("\r", "").split("\n\n") if p.strip()]
    if not paragraphs:
        return "<p style='margin:0;font-size:16px;line-height:1.7;color:#334155;'>No content provided.</p>"
    return "".join(
        f"<p style='margin:0 0 16px 0;font-size:16px;line-height:1.7;color:#334155;'>{p.replace(chr(10), '<br>')}</p>"
        for p in paragraphs
    )


def render_platform_email_html(*, subject: str, content_html: str) -> str:
    logo_block = (
        f'<img src="data:image/png;base64,{_PLATFORM_LOGO_BASE64}" alt="Gabani Transport Solutions" '
        'style="display:block;max-width:230px;width:100%;height:auto;margin:0 auto;">'
        if _PLATFORM_LOGO_BASE64
        else '<div style="font-size:42px;font-weight:800;letter-spacing:0.08em;color:#ffffff;">GTS</div>'
    )
    subject_label = html_escape(subject or "Platform Email")
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{subject_label}</title>
</head>
<body style="margin:0;padding:0;background:#eef2f9;font-family:'Segoe UI',Tahoma,Verdana,sans-serif;color:#0f172a;">
  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#eef2f9;padding:32px 16px;">
    <tr>
      <td align="center">
        <table width="960" cellpadding="0" cellspacing="0" border="0" style="max-width:960px;width:100%;background:#ffffff;border-radius:0;overflow:hidden;box-shadow:0 20px 50px rgba(15,23,42,0.08);">
          <tr>
            <td align="center" style="background:#171c30;padding:54px 36px 42px 36px;">
              {logo_block}
              <div style="margin-top:26px;color:#ffffff;font-size:34px;font-weight:800;letter-spacing:0.03em;line-height:1.2;text-align:center;">
                GABANI TRANSPORT SOLUTIONS
              </div>
              <div style="margin-top:14px;color:#cbd5e1;font-size:18px;line-height:1.6;text-align:center;">
                Where Intelligence Meets Logistics
              </div>
            </td>
          </tr>
          <tr>
            <td style="padding:38px 42px 40px 42px;">
              <div style="margin:0 0 24px 0;color:#111827;font-size:18px;font-weight:700;line-height:1.4;">
                {subject_label}
              </div>
              <div style="background:#ffffff;border:0;border-radius:0;padding:0;">
                {content_html}
              </div>
              <div style="margin-top:28px;padding:22px 28px;background:#eff4ff;border:1px solid #c9d8ff;border-radius:18px;color:#334155;font-size:14px;line-height:1.8;">
                This message was sent automatically by Gabani Transport Solutions. If you need assistance, reply to the appropriate team mailbox or contact support.
              </div>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def render_unified_email_html(*, subject: str, body: str, html: bool) -> str:
    if html:
        content_html = _extract_html_body_fragment(body) if _looks_like_full_html_document(body) else body
    else:
        content_html = _text_to_html(unescape(body).replace("\r", ""))
    return render_platform_email_html(subject=subject, content_html=content_html)


def _resolve_sender_credentials(
    from_email: str | None,
    smtp_user: str | None,
) -> tuple[str | None, str | None]:
    resolved_from = from_email.strip().lower() if from_email else None
    resolved_user = smtp_user.strip().lower() if smtp_user else None
    allowed_mailboxes = _mailboxes_set()

    if resolved_from and not resolved_user:
        if not allowed_mailboxes or resolved_from in allowed_mailboxes:
            resolved_user = resolved_from

    if resolved_user and not resolved_from:
        if not allowed_mailboxes or resolved_user in allowed_mailboxes:
            resolved_from = resolved_user

    return resolved_from, resolved_user


def resolve_bot_email(bot_name: str) -> str:
    key = (bot_name or "").strip().lower().replace("-", "_").replace(" ", "_")
    resolved = BOT_EMAIL_MAPPING.get(key)
    if resolved:
        return resolved
    return settings.SMTP_FROM or settings.SMTP_USER or "no-reply@gabanilogistics.com"


def get_bot_email(bot_name: str) -> str:
    """Return the approved sender mailbox for a bot."""
    return resolve_bot_email(bot_name)


def send_email(
    subject: str,
    body: str,
    to: Sequence[str] | str,
    html: bool = False,
    plain_text: str | None = None,
    from_email: str | None = None,
    smtp_user: str | None = None,
    smtp_password: str | None = None,
    smtp_host: str | None = None,
    smtp_port: int | None = None,
    smtp_secure: bool | None = None,
) -> bool:
    """
    Generic email sender for the GTS Logistics backend.

    - Uses SMTP over SSL when smtp_secure is True and port is typically 465.
    - Falls back to STARTTLS when smtp_secure is True and port is not 465.
    - If SMTP is not configured, logs the email instead of sending it.
    """

    recipients = _normalize_recipients(to)
    if not recipients:
        return False

    from_email, smtp_user = _resolve_sender_credentials(from_email, smtp_user)
    smtp_user = smtp_user or settings.SMTP_USER
    smtp_password = smtp_password or settings.SMTP_PASSWORD
    smtp_host = smtp_host or settings.SMTP_HOST
    smtp_port = smtp_port or settings.SMTP_PORT
    smtp_secure = settings.SMTP_SECURE if smtp_secure is None else smtp_secure
    from_email = from_email or settings.SMTP_FROM or smtp_user or "no-reply@gabanilogistics.com"

    if not smtp_host or not smtp_user:
        logger.warning("[email] SMTP not configured. Skipping send to %s", recipients)
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_email or settings.SMTP_USER
    msg["To"] = ", ".join(recipients)

    if html:
        fallback = plain_text or re.sub(r"<[^>]+>", "", body)
        fallback = unescape(fallback).replace("\r", "")
        html_body = render_unified_email_html(subject=subject, body=body, html=True)
        msg.set_content(fallback)
        msg.add_alternative(html_body, subtype="html")
    else:
        fallback = unescape(body).replace("\r", "")
        msg.set_content(fallback)
        msg.add_alternative(
            render_unified_email_html(subject=subject, body=fallback, html=False),
            subtype="html",
        )

    try:
        if smtp_secure:
            if smtp_port == 465:
                # SSL/TLS direct connection (default for your config)
                with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=_SMTP_TIMEOUT_SECONDS) as server:
                    server.login(smtp_user, smtp_password or "")
                    server.send_message(msg)
            else:
                # STARTTLS mode (e.g. port 587)
                with smtplib.SMTP(smtp_host, smtp_port, timeout=_SMTP_TIMEOUT_SECONDS) as server:
                    server.ehlo()
                    server.starttls()
                    server.ehlo()
                    server.login(smtp_user, smtp_password or "")
                    server.send_message(msg)
        else:
            # Non-secure SMTP (not recommended, but supported)
            with smtplib.SMTP(smtp_host, smtp_port, timeout=_SMTP_TIMEOUT_SECONDS) as server:
                server.login(smtp_user, smtp_password or "")
                server.send_message(msg)

        logger.info("[email] Sent to %s: %s", recipients, subject)
        return True

    except Exception as exc:
        logger.error("[email] ERROR sending email to %s: %s", recipients, repr(exc))
        return False


def send_admin_notification(
    subject: str,
    body: str,
    html: bool = False,
    bot_name: str | None = None,
) -> bool:
    """
    Convenience helper to send an email directly to the configured admin email.
    """

    admin = settings.ADMIN_EMAIL
    if not admin:
        logger.warning("[email] ADMIN_EMAIL is not configured. Skipping admin notification.")
        return False

    if bot_name:
        return send_bot_email(
            bot_name=bot_name,
            subject=subject,
            body=body,
            to=[admin],
            html=html,
        )

    return send_email(subject=subject, body=body, to=[admin], html=html)


def send_bot_email(
    bot_name: str,
    subject: str,
    body: str,
    to: Sequence[str] | str,
    html: bool = False,
    plain_text: str | None = None,
) -> bool:
    sender = resolve_bot_email(bot_name)
    return send_email(
        subject=subject,
        body=body,
        to=to,
        html=html,
        plain_text=plain_text,
        from_email=sender,
    )
