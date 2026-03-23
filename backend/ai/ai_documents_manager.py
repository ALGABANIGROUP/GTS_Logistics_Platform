from __future__ import annotations
import os
import re
import asyncio
from typing import Dict, Any, Tuple
try:
    import httpx
except Exception:
    httpx = None
INTERNAL_BASE_URL = os.getenv('INTERNAL_BASE_URL', 'http://localhost:8000').rstrip('/')
try:
    from backend.ai.email_bot import generate_reply as _llm_generate_reply
except Exception:
    _llm_generate_reply = None

class DocsClient:

    def __init__(self, base_url: str=INTERNAL_BASE_URL) -> None:
        self.base_url = base_url

    async def get_status(self) -> Dict[str, Any]:
        return await self._get('/ai/documents/status')

    async def list_expiring(self) -> Any:
        return await self._get('/ai/documents/expiring')

    async def notify_expiring(self) -> Any:
        return await self._post('/documents/notify-expiring/', {})

    async def extend(self, doc_id: int, days: int) -> Any:
        """Read a document then PUT with a new expires_at (+days)."""
        doc = await self._get(f'/documents/{doc_id}')
        if not isinstance(doc, dict) or doc.get('detail'):
            return {'ok': False, 'error': 'Document not found'}
        from datetime import datetime, timedelta
        exp = doc.get('expires_at')
        if exp:
            try:
                current = datetime.fromisoformat(str(exp).replace('Z', ''))
            except Exception:
                current = datetime.utcnow()
        else:
            current = datetime.utcnow()
        new_exp = current + timedelta(days=max(1, int(days)))
        payload = {'title': doc.get('title'), 'file_url': doc.get('file_url'), 'file_type': doc.get('file_type'), 'expires_at': new_exp.isoformat() + 'Z', 'notify_before_days': doc.get('notify_before_days', 7), 'owner_id': doc.get('owner_id')}
        return await self._put(f'/documents/{doc_id}', payload)

    async def _get(self, path: str):
        if not httpx:
            return {}
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                r = await client.get(self.base_url + path)
                return r.json() if r.status_code // 100 == 2 else {'detail': f'GET {path} -> {r.status_code}', 'text': r.text}
        except Exception as e:
            return {'detail': f'GET {path} error: {e}'}

    async def _post(self, path: str, payload: Dict[str, Any]):
        if not httpx:
            return {}
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.post(self.base_url + path, json=payload)
                return r.json() if r.status_code // 100 == 2 else {'detail': f'POST {path} -> {r.status_code}', 'text': r.text}
        except Exception as e:
            return {'detail': f'POST {path} error: {e}'}

    async def _put(self, path: str, payload: Dict[str, Any]):
        if not httpx:
            return {}
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.put(self.base_url + path, json=payload)
                return r.json() if r.status_code // 100 == 2 else {'detail': f'PUT {path} -> {r.status_code}', 'text': r.text}
        except Exception as e:
            return {'detail': f'PUT {path} error: {e}'}

def _parse_command(text: str) -> Tuple[str, Dict[str, Any]]:
    """
    Returns (command, args) based on a simple natural-language parse.
    Supported:
      - 'status' / 'summary'
      - 'list expiring' / 'expired'
      - 'extend <id> <days>' or 'extend #123 by 30 days'
      - 'notify'
    """
    t = (text or '').strip().lower()
    if re.search('\\b(status|summary)\\b', t):
        return ('status', {})
    if re.search('\\b(expiring|expired)\\b', t) or 'list expiring' in t:
        return ('list_expiring', {})
    m = re.search('\\bextend\\s+#?(\\d+)\\s+(?:by\\s+)?(\\d+)\\s*(?:day|days)?\\b', t)
    if m:
        return ('extend', {'id': int(m.group(1)), 'days': int(m.group(2))})
    if re.search('\\bnotify\\b', t):
        return ('notify', {})
    return ('help', {})

async def _rule_based_reply(email_body: str) -> str:
    (cmd, args) = _parse_command(email_body)
    api = DocsClient()
    if cmd == 'status':
        data = await api.get_status()
        if not isinstance(data, dict):
            return 'Could not fetch documents status.'
        return f"Documents status:\n- Expired: {data.get('expired', 0)}\n- Expiring soon (30d): {data.get('expiring_soon', 0)}\n- Valid: {data.get('valid', 0)}"
    if cmd == 'list_expiring':
        items = await api.list_expiring()
        if not isinstance(items, list) or not items:
            return 'No expiring or expired documents.'
        lines = []
        for d in items[:10]:
            title = d.get('title', 'Untitled')
            eid = d.get('id')
            status = d.get('status', 'expiring_soon')
            exp = str(d.get('expires_at') or '')[:10]
            lines.append(f'#{eid} · {title} · {status} · expires: {exp}')
        return 'Top expiring documents:\n' + '\n'.join(lines)
    if cmd == 'extend':
        rid = args['id']
        days = args['days']
        res = await api.extend(rid, days)
        if isinstance(res, dict) and res.get('id'):
            new_exp = res.get('expires_at') or 'updated'
            return f'Document #{rid} extended by {days} day(s). New expiry: {str(new_exp)[:10]}'
        return f'Failed to extend document #{rid}. {res}'
    if cmd == 'notify':
        res = await api.notify_expiring()
        msg = res.get('message') if isinstance(res, dict) else None
        return msg or 'Notification triggered.'
    return "I can help with documents.\n- 'status' → show counts\n- 'list expiring' → list expiring documents\n- 'extend <id> <days>' → extend a document\n- 'notify' → email summary to admins"

def handle_email(email_body: str) -> str:
    """
    Entry-point used by the email ingestion system.

    If ai.email_bot.generate_reply exists, call it first (LLM draft).
    Otherwise, use our rule-based handler that talks to /ai/documents/* and /documents/*.
    """
    if _llm_generate_reply:
        try:
            draft = _llm_generate_reply(f'System: You are the GTS Documents Bot. If the user asks for documents status, expiring list, extending a document (extend <id> <days>), or triggering notifications, respond briefly with the result. Otherwise, provide a short polite reply.\n\nUser email:\n{email_body}')
            if isinstance(draft, str) and draft.strip():
                return draft
        except Exception:
            pass
    try:
        return asyncio.run(_rule_based_reply(email_body))
    except RuntimeError:
        return 'Documents bot is processing your request; please try again shortly.'