"""backend.ai.roles.bot_documents

A small HTTP client used by the AI Documents Manager bot to talk to the Documents API.

Design goals:
- Import must never fail (DocsClient must always be defined).
- Auth is optional. When a token is not provided, the client can fetch a dev token
  from /auth/dev-token (if enabled on the server).
- Endpoint paths can vary across older router versions; therefore each action
  tries a short list of candidate paths.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

# NOTE: httpx is an optional dependency in some environments.
# We import it lazily inside request() so the module remains importable.


class DocsClientError(RuntimeError):
    """Raised when the Documents API call fails."""


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_iso_datetime(value: Any) -> Optional[datetime]:
    """Best-effort ISO-8601 parser (server responses may vary)."""
    if not value:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)

    s = str(value).strip()
    if not s:
        return None

    # Normalize common variants: 'Z' suffix and missing timezone.
    s = s.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(s)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        return None


def _days_until(dt: Optional[datetime]) -> Optional[int]:
    if dt is None:
        return None
    delta = dt - _utc_now()
    return int(delta.total_seconds() // 86400)


@dataclass
class DocsClientConfig:
    base_url: str
    token: Optional[str] = None
    timeout_sec: float = 25.0
    dev_secret: Optional[str] = None
    dev_role: str = "super_admin"


class DocsClient:
    """Async client for the Documents API."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
        timeout_sec: float = 25.0,
        dev_secret: Optional[str] = None,
        dev_role: str = "super_admin",
    ) -> None:
        base = (base_url or os.getenv("INTERNAL_BASE_URL") or "http://localhost:8000").rstrip("/")
        self.cfg = DocsClientConfig(
            base_url=base,
            token=token,
            timeout_sec=float(timeout_sec),
            dev_secret=dev_secret
            or os.getenv("GTS_DEV_SECRET")
            or os.getenv("DEV_SECRET")
            or "dev-secret",
            dev_role=dev_role,
        )

    # ------------------------------------------------------------------
    # Auth helpers
    # ------------------------------------------------------------------
    async def _get_dev_token(self) -> Optional[str]:
        """Fetch a dev token from the backend if DEV_MODE is enabled."""
        # Opt-out switch (useful in production).
        if os.getenv("GTS_DEV_MODE", "1").lower() not in ("1", "true", "yes", "on"):
            return None

        url = f"{self.cfg.base_url}/api/v1/auth/dev-token"
        params = {"role": self.cfg.dev_role, "secret": self.cfg.dev_secret}

        try:
            import httpx  # type: ignore
        except Exception as e:
            raise DocsClientError(f"httpx not installed (needed for dev token): {e}")

        async with httpx.AsyncClient(timeout=self.cfg.timeout_sec) as client:
            r = await client.get(url, params=params)
            if r.status_code // 100 != 2:
                return None
            data = r.json() if r.content else {}
            token = (data or {}).get("access_token")
            return str(token) if token else None

    async def _ensure_token(self) -> Optional[str]:
        if self.cfg.token:
            return self.cfg.token
        self.cfg.token = await self._get_dev_token()
        return self.cfg.token

    async def _auth_headers(self) -> Dict[str, str]:
        token = await self._ensure_token()
        headers = {"accept": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    # ------------------------------------------------------------------
    # Low-level request layer
    # ------------------------------------------------------------------
    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        try:
            import httpx  # type: ignore
        except Exception as e:
            raise DocsClientError(f"httpx not installed: {e}")

        url = f"{self.cfg.base_url}{path}"
        headers = await self._auth_headers()

        async with httpx.AsyncClient(timeout=self.cfg.timeout_sec) as client:
            r = await client.request(method, url, params=params, json=json_body, headers=headers)

        if r.status_code // 100 != 2:
            snippet = (r.text or "").strip()
            if len(snippet) > 400:
                snippet = snippet[:400] + "..."
            raise DocsClientError(f"{method} {path} failed: {r.status_code} {snippet}")

        if not r.content:
            return {}
        try:
            return r.json()
        except Exception:
            return {"raw": r.text}

    async def _try_paths(
        self,
        method: str,
        paths: Tuple[str, ...],
        *,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
    ) -> Tuple[str, Dict[str, Any]]:
        last_err: Optional[Exception] = None
        for p in paths:
            try:
                data = await self._request(method, p, params=params, json_body=json_body)
                return p, data
            except Exception as e:
                last_err = e
                continue
        raise DocsClientError(f"All candidate paths failed for {method}: {paths}. Last error: {last_err}")

    # ------------------------------------------------------------------
    # High-level API
    # ------------------------------------------------------------------
    async def get_status(self) -> Dict[str, Any]:
        path, data = await self._try_paths(
            "GET",
            (
                "/documents/status/",
                "/documents/status",
                "/documents/health/",
                "/documents/health",
            ),
        )
        return {"path": path, **(data or {})}

    async def list_expiring(self, days: int = 30) -> Dict[str, Any]:
        path, data = await self._try_paths(
            "GET",
            (
                "/documents/expiring/",
                "/documents/expiring",
                "/documents/expiring-soon/",
                "/documents/expiring-soon",
            ),
            params={"days": int(days)},
        )

        items = data.get("results") or data.get("items") or data.get("data") or data.get("documents") or []
        normalized = []
        for it in items if isinstance(items, list) else []:
            exp = _parse_iso_datetime(it.get("expires_at") if isinstance(it, dict) else None)
            normalized.append(
                {
                    **(it if isinstance(it, dict) else {"value": it}),
                    "_expires_at": exp.isoformat() if exp else None,
                    "_days_left": _days_until(exp),
                }
            )

        return {
            "path": path,
            "days": int(days),
            "total": int(data.get("total") or len(normalized)),
            "items": normalized,
            "raw": data,
        }

    async def extend(self, record_id: int, days: int) -> Dict[str, Any]:
        rid = int(record_id)
        dd = int(days)
        if rid <= 0 or dd <= 0:
            raise DocsClientError("extend() requires record_id > 0 and days > 0")

        # Different router versions:
        # - POST /documents/{id}/extend/  {"days": N}
        # - POST /documents/extend/       {"id": id, "days": N}
        path, data = await self._try_paths(
            "POST",
            (
                f"/documents/{rid}/extend/",
                f"/documents/{rid}/extend",
                "/documents/extend/",
                "/documents/extend",
            ),
            json_body={"id": rid, "days": dd},
        )
        return {"path": path, **(data or {})}

    async def notify_expiring(self) -> Dict[str, Any]:
        path, data = await self._try_paths(
            "POST",
            (
                "/documents/notify-expiring/",
                "/documents/notify-expiring",
                "/documents/notify/",
                "/documents/notify",
            ),
            json_body={},
        )
        return {"path": path, **(data or {})}


# ----------------------------------------------------------------------
# Command parsing (used by DocumentsManagerBot)
# ----------------------------------------------------------------------
_WS = re.compile(r"\s+")
_INT = re.compile(r"^[0-9]+$")


def _parse_command(text: str) -> Tuple[str, Dict[str, Any]]:
    """Parse a small command DSL.

    Supported examples:
    - "status"
    - "list expiring"
    - "list expiring 14"
    - "extend 123 30"
    - "notify"
    """
    raw = (text or "").strip().lower()
    if not raw:
        return "status", {}

    parts = [p for p in _WS.split(raw) if p]
    if not parts:
        return "status", {}

    if parts[0] in ("status", "health"):
        return "status", {}

    if parts[0] == "list":
        # list expiring [days]
        if len(parts) >= 2 and parts[1] in ("expiring", "expiry", "expires", "expiring-soon"):
            days = 30
            if len(parts) >= 3 and _INT.match(parts[2]):
                days = int(parts[2])
            return "list_expiring", {"days": days}
        return "list_expiring", {"days": 30}

    if parts[0] in ("expiring", "expires"):
        days = 30
        if len(parts) >= 2 and _INT.match(parts[1]):
            days = int(parts[1])
        return "list_expiring", {"days": days}

    if parts[0] == "extend":
        # extend <id> <days>
        args: Dict[str, Any] = {}
        if len(parts) >= 2 and _INT.match(parts[1]):
            args["id"] = int(parts[1])
        if len(parts) >= 3 and _INT.match(parts[2]):
            args["days"] = int(parts[2])
        return "extend", args

    if parts[0] in ("notify", "alert"):
        return "notify", {}

    return "status", {}
