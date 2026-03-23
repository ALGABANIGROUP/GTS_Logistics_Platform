from __future__ import annotations

import imaplib
import pathlib
import re
from datetime import datetime, timezone
from email import message_from_bytes
from email.header import decode_header
from email.utils import getaddresses, parsedate_to_datetime
from html import unescape
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.config import settings
from backend.models.email_center import (
    EmailAttachment,
    EmailAuditLog,
    EmailMessage,
    EmailThread,
    Mailbox,
    MailboxCredentials,
)
from backend.models.user import User
from backend.services.email_crypto import decrypt_credentials, encrypt_credentials
from backend.utils.email_utils import send_email


BOT_REQUIRE_APPROVAL = {"security_manager", "finance_bot", "system_admin"}


class EmailCenterService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def resolve_user_id(self, email: str | None) -> Optional[int]:
        if not email:
            return None
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        return int(user.id) if user else None

    async def list_mailboxes_for_user(self, *, user_id: Optional[int], role: str, is_admin: bool) -> List[Mailbox]:
        del role
        if is_admin:
            return await self.list_mailboxes()
        if not user_id:
            return []
        result = await self.db.execute(
            select(Mailbox)
            .where(Mailbox.owner_user_id == user_id)
            .order_by(Mailbox.email_address.asc())
        )
        return list(result.scalars().all())

    async def get_mailbox_access(
        self,
        *,
        mailbox_id: int,
        user_id: Optional[int],
        role: str,
        is_admin: bool,
    ) -> Dict[str, bool]:
        del role
        if is_admin:
            return {"read": True, "send": True, "manage": True}
        mailbox = await self.db.get(Mailbox, mailbox_id)
        if not mailbox or not user_id:
            return {"read": False, "send": False, "manage": False}
        owns_mailbox = mailbox.owner_user_id == user_id
        can_send = owns_mailbox and bool(mailbox.outbound_enabled)
        return {"read": owns_mailbox, "send": can_send, "manage": owns_mailbox}

    async def create_mailbox(
        self,
        *,
        email_address: str,
        display_name: Optional[str],
        bot_name: Optional[str],
        owner_user_id: Optional[int],
        mode: str,
        inbound_enabled: bool,
        outbound_enabled: bool,
        imap_host: Optional[str],
        imap_port: Optional[int],
        imap_user: Optional[str],
        imap_password: Optional[str],
        smtp_host: Optional[str],
        smtp_port: Optional[int],
        smtp_user: Optional[str],
        smtp_password: Optional[str],
        imap_ssl: bool,
        smtp_ssl: bool,
    ) -> Mailbox:
        mailbox = Mailbox(
            owner_user_id=owner_user_id,
            bot_code=bot_name,
            email_address=email_address,
            display_name=display_name,
            mode=(mode or "HUMAN").upper(),
            imap_host=imap_host,
            imap_port=imap_port,
            imap_user=imap_user or email_address,
            imap_ssl=bool(imap_ssl),
            smtp_host=smtp_host,
            smtp_port=smtp_port,
            smtp_user=smtp_user or email_address,
            smtp_ssl=bool(smtp_ssl),
            inbound_enabled=bool(inbound_enabled),
            outbound_enabled=bool(outbound_enabled),
            is_enabled=True,
            polling_enabled=bool(inbound_enabled),
        )
        self.db.add(mailbox)
        await self.db.flush()

        shared_secret = imap_password or smtp_password
        if shared_secret:
            ciphertext, key_version = encrypt_credentials(shared_secret)
            self.db.add(
                MailboxCredentials(
                    mailbox_id=mailbox.id,
                    credentials_ciphertext=ciphertext,
                    key_version=key_version,
                    rotated_at=datetime.now(timezone.utc),
                )
            )

        await self.db.commit()
        await self.db.refresh(mailbox)
        return mailbox

    async def update_mailbox(self, mailbox: Mailbox, payload: Dict[str, Any]) -> Mailbox:
        for key, value in payload.items():
            if hasattr(mailbox, key):
                setattr(mailbox, key, value)
        mailbox.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(mailbox)
        return mailbox

    async def assign_mailbox_to_user(
        self,
        *,
        mailbox_id: int,
        user_id: int,
        can_read: bool,
        can_send: bool,
        can_manage: bool,
    ) -> Mailbox:
        del can_read, can_send, can_manage
        mailbox = await self.db.get(Mailbox, mailbox_id)
        if mailbox is None:
            raise ValueError("Mailbox not found")
        mailbox.owner_user_id = user_id
        mailbox.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(mailbox)
        return mailbox

    async def assign_mailbox_to_role(
        self,
        *,
        mailbox_id: int,
        role_name: str,
        can_read: bool,
        can_send: bool,
        can_manage: bool,
    ) -> Mailbox:
        del role_name, can_read, can_send, can_manage
        mailbox = await self.db.get(Mailbox, mailbox_id)
        if mailbox is None:
            raise ValueError("Mailbox not found")
        return mailbox

    async def list_mailboxes(self) -> List[Mailbox]:
        result = await self.db.execute(select(Mailbox).order_by(Mailbox.email_address.asc()))
        return list(result.scalars().all())

    async def set_mailbox_mode(self, mailbox_id: int, mode: str) -> Mailbox:
        mailbox = await self.db.get(Mailbox, mailbox_id)
        if mailbox is None:
            raise ValueError("Mailbox not found")
        mailbox.mode = (mode or mailbox.mode).upper()
        mailbox.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(mailbox)
        return mailbox

    def _resolve_smtp_settings(self, mailbox: Mailbox) -> Dict[str, Any]:
        return {
            "host": mailbox.smtp_host or settings.SMTP_HOST,
            "port": mailbox.smtp_port or settings.SMTP_PORT,
            "user": mailbox.smtp_user or mailbox.email_address or settings.SMTP_USER,
            "password": self._get_mailbox_password(mailbox, allow_fallback=True),
            "secure": mailbox.smtp_ssl if mailbox.smtp_ssl is not None else settings.SMTP_SECURE,
        }

    def _resolve_imap_settings(self, mailbox: Mailbox) -> Dict[str, Any]:
        return {
            "host": mailbox.imap_host or settings.IMAP_HOST,
            "port": mailbox.imap_port or settings.IMAP_PORT,
            "user": mailbox.imap_user or mailbox.email_address or settings.IMAP_USER,
            "password": self._get_mailbox_password(mailbox, allow_fallback=True),
            "ssl": mailbox.imap_ssl if mailbox.imap_ssl is not None else settings.IMAP_SSL,
        }

    def _get_mailbox_password(self, mailbox: Mailbox, *, allow_fallback: bool = False) -> Optional[str]:
        creds = mailbox.credentials
        if creds and creds.credentials_ciphertext:
            try:
                return decrypt_credentials(creds.credentials_ciphertext)
            except Exception as exc:
                creds.last_error = str(exc)[:500]
        if allow_fallback:
            return settings.IMAP_PASSWORD or settings.SMTP_PASSWORD or None
        return None

    async def list_messages(self, mailbox_id: int, skip: int = 0, limit: int = 50) -> List[EmailMessage]:
        stmt = (
            select(EmailMessage)
            .where(EmailMessage.mailbox_id == mailbox_id)
            .order_by(EmailMessage.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_thread(self, thread_id: int) -> Tuple[Optional[EmailThread], List[EmailMessage]]:
        thread = await self.db.get(EmailThread, thread_id)
        if not thread:
            return None, []
        result = await self.db.execute(
            select(EmailMessage)
            .where(EmailMessage.thread_id == thread_id)
            .order_by(EmailMessage.created_at.asc())
        )
        return thread, list(result.scalars().all())

    async def poll_mailboxes(self) -> Dict[str, Any]:
        result = await self.db.execute(
            select(Mailbox)
            .where(
                Mailbox.is_enabled == True,
                Mailbox.polling_enabled == True,
                Mailbox.inbound_enabled == True,
            )
            .options(selectinload(Mailbox.credentials))
            .order_by(Mailbox.email_address.asc())
        )
        mailboxes = list(result.scalars().all())
        summary: Dict[str, Any] = {"checked": len(mailboxes), "created": 0, "errors": []}
        for mailbox in mailboxes:
            try:
                summary["created"] += await self._poll_mailbox(mailbox)
            except Exception as exc:
                summary["errors"].append({"mailbox": mailbox.email_address, "error": str(exc)})
        return summary

    async def send_message(
        self,
        *,
        mailbox_id: int,
        to: List[str],
        subject: str,
        body: str,
        html: bool = False,
        send: bool = True,
    ) -> EmailMessage:
        mailbox = await self.db.get(Mailbox, mailbox_id)
        if mailbox is None:
            raise ValueError("Mailbox not found")

        thread = await self._get_or_create_thread(mailbox_id, subject)
        message = EmailMessage(
            thread_id=thread.id,
            mailbox_id=mailbox_id,
            direction="outbound",
            from_addr=mailbox.email_address,
            to_addrs=to,
            cc_addrs=[],
            subject=subject,
            body_preview=_text_preview(body, html=html),
            status="queued" if send else "draft",
            assigned_bot=mailbox.bot_code,
            processed_by_bot=mailbox.bot_code if mailbox.mode == "BOT" else None,
            sent_at=datetime.now(timezone.utc) if send else None,
        )
        self.db.add(message)
        thread.last_message_at = datetime.now(timezone.utc)
        self.db.add(thread)
        await self.db.flush()

        if send and mailbox.outbound_enabled:
            smtp = self._resolve_smtp_settings(mailbox)
            sent = send_email(
                subject=subject,
                body=body,
                to=to,
                html=html,
                from_email=mailbox.email_address,
                smtp_user=smtp["user"],
                smtp_password=smtp["password"],
                smtp_host=smtp["host"],
                smtp_port=smtp["port"],
                smtp_secure=smtp["secure"],
            )
            message.status = "processed" if sent else "failed"

        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def _poll_mailbox(self, mailbox: Mailbox) -> int:
        if not mailbox.inbound_enabled:
            return 0
        imap = self._resolve_imap_settings(mailbox)
        if not imap["host"] or not imap["user"] or not imap["password"]:
            return 0

        created = 0
        connection = (
            imaplib.IMAP4_SSL(imap["host"], imap["port"])
            if imap["ssl"]
            else imaplib.IMAP4(imap["host"], imap["port"])
        )

        with connection as conn:
            conn.login(imap["user"], imap["password"])
            conn.select("INBOX")
            status, data = conn.uid("search", None, "UNSEEN")
            if status != "OK":
                return 0

            uid_values = data[0].split()[-20:]
            max_uid = mailbox.last_uid
            last_message_id = mailbox.last_message_id

            for uid_bytes in uid_values:
                uid_int = int(uid_bytes.decode("utf-8", errors="ignore") or "0")
                status, msg_data = conn.uid("fetch", uid_bytes, "(RFC822)")
                if status != "OK" or not msg_data:
                    continue
                raw = msg_data[0][1]
                parsed = message_from_bytes(raw)
                message_id = parsed.get("Message-ID")
                if await self._message_exists(mailbox.id, message_id, uid_int):
                    continue
                created += await self._store_message(mailbox, parsed, message_id, uid_int)
                max_uid = uid_int if max_uid is None else max(max_uid, uid_int)
                if message_id:
                    last_message_id = message_id

            mailbox.last_polled_at = datetime.now(timezone.utc)
            mailbox.last_uid = max_uid
            mailbox.last_message_id = last_message_id
            if mailbox.credentials:
                mailbox.credentials.last_error = None
            await self.db.commit()

        return created

    async def _message_exists(self, mailbox_id: int, message_id: Optional[str], imap_uid: Optional[int]) -> bool:
        if message_id:
            existing = await self.db.scalar(
                select(EmailMessage).where(
                    EmailMessage.mailbox_id == mailbox_id,
                    EmailMessage.message_id == message_id,
                )
            )
            if existing is not None:
                return True
        if imap_uid is not None:
            existing = await self.db.scalar(
                select(EmailMessage).where(
                    EmailMessage.mailbox_id == mailbox_id,
                    EmailMessage.imap_uid == imap_uid,
                )
            )
            if existing is not None:
                return True
        return False

    async def _store_message(
        self,
        mailbox: Mailbox,
        parsed: Any,
        message_id: Optional[str],
        imap_uid: Optional[int],
    ) -> int:
        subject = _decode_header_value(parsed.get("Subject"))
        from_addr = parsed.get("From")
        to_addrs = [addr for _, addr in getaddresses(parsed.get_all("To", [])) if addr]
        cc_addrs = [addr for _, addr in getaddresses(parsed.get_all("Cc", [])) if addr]
        body_preview, attachments = _parse_email_body(parsed)
        received_at = _parse_email_datetime(parsed.get("Date"))

        thread = await self._get_or_create_thread(mailbox.id, subject)
        assigned_bot = mailbox.bot_code or mailbox.assigned_bot_key

        message = EmailMessage(
            thread_id=thread.id,
            mailbox_id=mailbox.id,
            message_id=message_id,
            imap_uid=imap_uid,
            direction="inbound",
            from_addr=from_addr,
            to_addrs=to_addrs,
            cc_addrs=cc_addrs,
            subject=subject or None,
            received_at=received_at,
            body_preview=body_preview,
            status="new",
            assigned_bot=assigned_bot,
            raw_headers_json={key: str(parsed.get(key)) for key in parsed.keys()},
        )
        self.db.add(message)
        await self.db.flush()

        if attachments:
            await self._store_attachments(message.id, attachments)

        thread.last_message_at = received_at or datetime.now(timezone.utc)
        self.db.add(thread)

        if assigned_bot:
            await self._log_bot_event(
                action="email_ingested",
                mailbox_id=mailbox.id,
                message_id=message.id,
                payload={"bot": assigned_bot, "subject": subject},
            )

        if mailbox.mode == "BOT" and mailbox.auto_reply_enabled:
            await self._maybe_auto_reply(mailbox, message)

        await self.db.commit()
        return 1

    async def _get_or_create_thread(self, mailbox_id: int, subject: str | None) -> EmailThread:
        normalized_subject = _normalize_subject(subject)
        existing = await self.db.scalar(
            select(EmailThread).where(
                EmailThread.mailbox_id == mailbox_id,
                EmailThread.subject == normalized_subject,
            )
        )
        if existing:
            return existing
        thread = EmailThread(
            mailbox_id=mailbox_id,
            subject=normalized_subject or "(no subject)",
            status="open",
            last_message_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.db.add(thread)
        await self.db.flush()
        return thread

    async def _store_attachments(self, message_id: int, attachments: List[Dict[str, Any]]) -> None:
        if not attachments:
            return
        base_dir = pathlib.Path("uploads/email").resolve()
        base_dir.mkdir(parents=True, exist_ok=True)
        for attach in attachments:
            filename = attach["filename"]
            storage_path = base_dir / f"{message_id}_{filename}"
            content = attach.get("content") or b""
            if content:
                storage_path.write_bytes(content)
            self.db.add(
                EmailAttachment(
                    message_id=message_id,
                    filename=filename,
                    content_type=attach.get("content_type"),
                    size=attach.get("size"),
                    storage_ref=str(storage_path),
                )
            )
        await self.db.flush()

    async def _maybe_auto_reply(self, mailbox: Mailbox, message: EmailMessage) -> None:
        reply_to = [message.from_addr] if message.from_addr else []
        if not reply_to or not mailbox.outbound_enabled:
            return
        requires_approval = (mailbox.bot_code or "") in BOT_REQUIRE_APPROVAL
        reply_body = _bot_reply_template(mailbox.bot_code or mailbox.assigned_bot_key or "customer_service")
        reply = EmailMessage(
            thread_id=message.thread_id,
            mailbox_id=mailbox.id,
            direction="outbound",
            from_addr=mailbox.email_address,
            to_addrs=reply_to,
            cc_addrs=[],
            subject=f"Re: {message.subject or ''}".strip(),
            body_preview=reply_body[:1000],
            status="pending_approval" if requires_approval else "queued",
            assigned_bot=mailbox.bot_code,
            processed_by_bot=mailbox.bot_code,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(reply)
        await self.db.flush()

        if not requires_approval:
            smtp = self._resolve_smtp_settings(mailbox)
            sent = send_email(
                subject=reply.subject or "Re:",
                body=reply_body,
                to=reply_to,
                from_email=mailbox.email_address,
                smtp_user=smtp["user"],
                smtp_password=smtp["password"],
                smtp_host=smtp["host"],
                smtp_port=smtp["port"],
                smtp_secure=smtp["secure"],
            )
            reply.status = "processed" if sent else "failed"
            reply.sent_at = datetime.now(timezone.utc) if sent else None

    async def update_thread(
        self,
        thread_id: int,
        *,
        status: Optional[str] = None,
        assigned_to_user_id: Optional[int] = None,
        tags: Optional[List[str]] = None,
        priority: Optional[str] = None,
    ) -> EmailThread:
        thread = await self.db.get(EmailThread, thread_id)
        if not thread:
            raise ValueError("Thread not found")
        if status is not None:
            thread.status = status
        if assigned_to_user_id is not None:
            thread.assigned_to_user_id = assigned_to_user_id
        if tags is not None:
            thread.tags = tags
        if priority is not None:
            thread.priority = priority
        thread.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(thread)
        return thread

    async def approve_message(self, message_id: int, approved_by_user_id: Optional[int]) -> EmailMessage:
        del approved_by_user_id
        message = await self.db.get(EmailMessage, message_id)
        if not message:
            raise ValueError("Message not found")
        if message.sent_at:
            return message
        mailbox = await self.db.get(Mailbox, message.mailbox_id)
        if not mailbox or not mailbox.outbound_enabled:
            return message

        smtp = self._resolve_smtp_settings(mailbox)
        sent = send_email(
            subject=message.subject or "",
            body=message.body_preview or "",
            to=message.to_addrs or [],
            from_email=mailbox.email_address,
            smtp_user=smtp["user"],
            smtp_password=smtp["password"],
            smtp_host=smtp["host"],
            smtp_port=smtp["port"],
            smtp_secure=smtp["secure"],
        )
        if sent:
            message.sent_at = datetime.now(timezone.utc)
            message.status = "processed"
        else:
            message.status = "failed"
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def _log_bot_event(
        self,
        *,
        action: str,
        mailbox_id: Optional[int],
        message_id: Optional[int],
        payload: Dict[str, Any],
        severity: str = "info",
    ) -> None:
        self.db.add(
            EmailAuditLog(
                action=action,
                mailbox_id=mailbox_id,
                message_id=message_id,
                diff_json=payload,
                severity=severity,
                created_at=datetime.now(timezone.utc),
            )
        )
        await self.db.flush()


def _decode_header_value(value: Optional[str]) -> str:
    if not value:
        return ""
    decoded = decode_header(value)
    parts: List[str] = []
    for text, encoding in decoded:
        if isinstance(text, bytes):
            parts.append(text.decode(encoding or "utf-8", errors="ignore"))
        else:
            parts.append(str(text))
    return "".join(parts).strip()


def _normalize_subject(subject: Optional[str]) -> str:
    clean = _decode_header_value(subject)
    return re.sub(r"^(re|fw|fwd):\s*", "", clean, flags=re.IGNORECASE).strip()


def _parse_email_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        parsed = parsedate_to_datetime(value)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed
    except Exception:
        return None


def _strip_html(value: str) -> str:
    without_tags = re.sub(r"<[^>]+>", " ", value)
    without_entities = unescape(without_tags)
    return re.sub(r"\s+", " ", without_entities).strip()


def _text_preview(body: str, *, html: bool) -> str:
    text = _strip_html(body) if html else body
    return re.sub(r"\s+", " ", text).strip()[:1000]


def _parse_email_body(parsed: Any) -> Tuple[str, List[Dict[str, Any]]]:
    body_text: Optional[str] = None
    body_html: Optional[str] = None
    attachments: List[Dict[str, Any]] = []

    if parsed.is_multipart():
        for part in parsed.walk():
            content_disposition = part.get("Content-Disposition", "")
            content_type = part.get_content_type()
            payload = part.get_payload(decode=True) or b""

            if "attachment" in content_disposition.lower():
                attachments.append(
                    {
                        "filename": part.get_filename() or "attachment",
                        "content_type": content_type,
                        "size": len(payload),
                        "content": payload,
                    }
                )
                continue

            if content_type == "text/plain" and body_text is None:
                body_text = payload.decode(errors="ignore")
            elif content_type == "text/html" and body_html is None:
                body_html = payload.decode(errors="ignore")
    else:
        payload = parsed.get_payload(decode=True) or b""
        content_type = parsed.get_content_type()
        if content_type == "text/html":
            body_html = payload.decode(errors="ignore")
        else:
            body_text = payload.decode(errors="ignore")

    preview_source = body_text or _strip_html(body_html or "")
    return re.sub(r"\s+", " ", (preview_source or "")).strip()[:5000], attachments


def _bot_reply_template(bot_name: str) -> str:
    templates = {
        "security_manager": "Your report has been received. A security analyst will review it shortly.",
        "partner_manager": "Thanks for reaching out. Our partnership team will follow up shortly.",
        "operations_manager": "We received your operations request and will respond soon.",
        "freight_broker": "Your shipment request is being reviewed. We will send an update shortly.",
        "finance_bot": "Finance received your request. A response is being prepared.",
        "documents_manager": "We received your documents. We will review and confirm shortly.",
        "safety_manager": "Safety team received the report. We will follow up shortly.",
        "customer_service": "Thanks for contacting GTS. Our team will respond soon.",
        "sales_team": "Thanks for your interest. Our sales team will follow up shortly.",
        "system_admin": "Your request has been logged and will be reviewed.",
    }
    return templates.get(bot_name, "Thank you for contacting GTS. We will respond shortly.")
