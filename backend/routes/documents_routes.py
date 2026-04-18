# backend/routes/documents_routes.py
from __future__ import annotations
import os
from fastapi import APIRouter, HTTPException, Query, Body, Request
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import date, timedelta

# ------------------------------
# In-memory seed store
# ------------------------------
_DOCS: Dict[int, Dict[str, Any]] = {
    1: {"id": 1, "name": "Vehicle Registration", "status": "valid",   "expires_at": "2026-01-01", "owner": "Ops"},
    2: {"id": 2, "name": "Insurance Policy",     "status": "warning", "expires_at": "2025-12-01", "owner": "Finance"},
    3: {"id": 3, "name": "Permit XYZ",           "status": "expired", "expires_at": "2024-01-01", "owner": "Ops"},
}
_next_id = 4

# ------------------------------
# Schemas
# ------------------------------
class DocumentIn(BaseModel):
    name: str = Field(..., min_length=1)
    status: str = Field(..., pattern="^(valid|warning|expired)$")
    expires_at: date
    owner: str = Field(..., min_length=1)

class DocumentOut(DocumentIn):
    id: int

class ExtendPayload(BaseModel):
    doc_id: int = Field(..., gt=0)
    days: int = Field(..., gt=0, le=3650)

# ------------------------------
# Routers
# ------------------------------
router = APIRouter(prefix="/documents", tags=["documents"])
ai_router = APIRouter(prefix="/ai/documents", tags=["documents-ai"])
internal_router = APIRouter(prefix="/documents", tags=["documents-internal"])


def _require_internal_key(request: Request) -> None:
    expected = (os.getenv("INTERNAL_CRON_KEY") or "").strip()
    if not expected:
        raise HTTPException(status_code=503, detail="Internal key is not configured")
    provided = request.headers.get("X-INTERNAL-KEY", "")
    if provided != expected:
        raise HTTPException(status_code=403, detail="Invalid internal key")

# ------------------------------
# Health
# ------------------------------
@router.get("/healthz", name="documents_health")
async def documents_health():
    return {"ok": True, "module": "documents", "router": "real", "count": len(_DOCS)}

# ------------------------------
# CRUD
# ------------------------------
@router.get("/", name="list_docs")
async def list_docs(
    status: Optional[str] = Query(None),
    owner: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
):
    items: List[Dict[str, Any]] = list(_DOCS.values())
    if status:
        items = [d for d in items if d.get("status") == status]
    if owner:
        items = [d for d in items if str(d.get("owner", "")).lower() == owner.lower()]
    if q:
        ql = q.lower()
        items = [d for d in items if ql in str(d.get("name", "")).lower()]
    return {"ok": True, "count": len(items), "items": items}

@router.get("/{doc_id}", name="get_doc", response_model=DocumentOut)
async def get_doc(doc_id: int):
    doc = _DOCS.get(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {
        "id": int(doc["id"]),
        "name": doc["name"],
        "status": doc["status"],
        "expires_at": date.fromisoformat(str(doc["expires_at"])),
        "owner": doc["owner"],
    }

@router.post("/", name="create_doc", response_model=DocumentOut)
async def create_doc(payload: DocumentIn):
    global _next_id
    new_id = _next_id
    _next_id += 1
    doc = {"id": new_id, **payload.model_dump()}
    # store expires_at as iso string for the in-memory store
    doc["expires_at"] = str(doc["expires_at"])
    _DOCS[new_id] = doc
    return {"id": new_id, **payload.model_dump()}

@router.put("/{doc_id}", name="update_doc", response_model=DocumentOut)
async def update_doc(doc_id: int, payload: DocumentIn):
    if doc_id not in _DOCS:
        raise HTTPException(status_code=404, detail="Document not found")
    _DOCS[doc_id] = {"id": doc_id, **payload.model_dump(), "expires_at": str(payload.expires_at)}
    return {"id": doc_id, **payload.model_dump()}

@router.delete("/{doc_id}", name="delete_doc")
async def delete_doc(doc_id: int):
    if doc_id not in _DOCS:
        raise HTTPException(status_code=404, detail="Document not found")
    del _DOCS[doc_id]
    return {"ok": True, "deleted": doc_id}

# ------------------------------
# Extras
# ------------------------------
def _notify_expiring_impl(dry_run: bool = True) -> Dict[str, Any]:
    items = [d for d in _DOCS.values() if d.get("status") in ("warning", "expired")]
    return {"ok": True, "count": len(items), "dry_run": dry_run, "items": items}


@router.get("/expiring-soon/", name="expiring_soon")
async def expiring_soon():
    items = [d for d in _DOCS.values() if d.get("status") in ("warning", "expired")]
    return {"ok": True, "count": len(items), "items": items}

@router.post("/notify-expiring/", name="notify_expiring")
async def notify_expiring(dry_run: bool = True):
    items = [d for d in _DOCS.values() if d.get("status") in ("warning", "expired")]
    # Here you can build real notification logic later
    return {"ok": True, "count": len(items), "dry_run": dry_run, "items": items}

# ------------------------------
# AI endpoints
# ------------------------------
@ai_router.get("/status", name="ai_docs_status")
async def ai_docs_status():
    return {"ok": True, "docs_count": len(_DOCS)}

@ai_router.get("/expiring", name="ai_docs_expiring")
async def ai_docs_expiring():
    items = [d for d in _DOCS.values() if d.get("status") in ("warning", "expired")]
    return {"ok": True, "count": len(items), "items": items}

@ai_router.post("/extend", name="ai_docs_extend")
async def ai_docs_extend(
    # Either Query:
    q_doc_id: Optional[int] = Query(default=None, gt=0, alias="doc_id"),
    q_days: Optional[int] = Query(default=None, gt=0, le=3650, alias="days"),
    # Or JSON body:
    payload: Optional[ExtendPayload] = Body(default=None),
):
    # Merge both sources
    doc_id = q_doc_id or (payload.doc_id if payload else None)
    days = q_days or (payload.days if payload else None)
    if not doc_id or not days:
        raise HTTPException(status_code=422, detail="doc_id and days are required (query or JSON body).")

    doc = _DOCS.get(int(doc_id))
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    old = date.fromisoformat(str(doc["expires_at"]))
    new = old + timedelta(days=int(days))
    doc["expires_at"] = new.isoformat()

    # If document was expired and extended enough, optionally mark it valid again
    if doc.get("status") == "expired" and (new - date.today()).days > 30:
        doc["status"] = "valid"

    return {"ok": True, "id": int(doc_id), "old_expires_at": old.isoformat(), "new_expires_at": new.isoformat()}


@internal_router.post("/notify-expiring/internal", include_in_schema=False)
async def notify_expiring_internal(request: Request, dry_run: bool = True):
    _require_internal_key(request)
    return _notify_expiring_impl(dry_run=dry_run)
