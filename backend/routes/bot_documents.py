# backend/ai/roles/bot_documents.py
from __future__ import annotations

import os
import re
import asyncio
from typing import Dict, Any, Tuple, Optional

try:
    import httpx
except Exception:  # pragma: no cover
    httpx = None

INTERNAL_BASE_URL = os.getenv("INTERNAL_BASE_URL", "http://localhost:8000").rstrip("/")


class DocsClient:
    def __init__(self, base_url: str = INTERNAL_BASE_URL) -> None:
        self.base_url = base_url

    async def get_status(self) -> Dict[str, Any]:
        return await self._get("/ai/documents/status")

    async def list_expiring(self) -> Any:
        return await self._get("/ai/documents/expiring")

    async def notify_expiring(self) -> Any:
        return await self._post("/documents/notify-expiring/", {})

    async def extend(self, doc_id: int, days: int) -> Any:
        doc = await self._get(f"/documents/{doc_id}")
        if not isinstance(doc, dict) or doc.get("detail"):
            return {"ok": False, "error": "Document not found"}

        from datetime import datetime, timedelta

        exp = doc.get("expires_at")
        if exp:
            try:
                current = datetime.fromisoformat(str(exp).replace("Z", ""))
            except Exception:
                current = datetime.utcnow()
        else:
            current = datetime.utcnow()

        new_exp = current + timedelta(days=max(1, int(days)))
        payload = {
            "title": doc.get("title"),
            "file_url": doc.get("file_url"),
            "file_type": doc.get("file_type"),
            "expires_at": new_exp.isoformat() + "Z",
            "notify_before_days": doc.get("notify_before_days", 7),
            "owner_id": doc.get("owner_id"),
        }
        return await self._put(f"/documents/{doc_id}", payload)

    async def _get(self, path: str):
        if not httpx:
            return {}
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(self.base_url + path)
                return r.json() if r.status_code // 100 == 2 else {"detail": f"GET {path} -> {r.status_code}", "text": r.text}
        except Exception as e:
            return {"detail": f"GET {path} error: {e}"}

    async def _post(self, path: str, payload: Dict[str, Any]):
        if not httpx:
            return {}
        try:
            async with httpx.AsyncClient(timeout=25.0) as client:
                r = await client.post(self.base_url + path, json=payload)
                return r.json() if r.status_code // 100 == 2 else {"detail": f"POST {path} -> {r.status_code}", "text": r.text}
        except Exception as e:
            return {"detail": f"POST {path} error: {e}"}

    async def _put(self, path: str, payload: Dict[str, Any]):
        if not httpx:
            return {}
        try:
            async with httpx.AsyncClient(timeout=25.0) as client:
                r = await client.put(self.base_url + path, json=payload)
                return r.json() if r.status_code // 100 == 2 else {"detail": f"PUT {path} -> {r.status_code}", "text": r.text}
        except Exception as e:
            return {"detail": f"PUT {path} error: {e}"}


def _parse_command(text: str) -> Tuple[str, Dict[str, Any]]:
    t = (text or "").strip().lower()

    if re.search(r"\b(status|summary)\b", t):
        return "status", {}

    if re.search(r"\b(expiring|expired)\b", t) or "list expiring" in t:
        return "list_expiring", {}

    m = re.search(r"\bextend\s+#?(\d+)\s+(?:by\s+)?(\d+)\s*(?:day|days)?\b", t)
    if m:
        return "extend", {"id": int(m.group(1)), "days": int(m.group(2))}

    if re.search(r"\bnotify\b", t):
        return "notify", {}

    return "help", {}
