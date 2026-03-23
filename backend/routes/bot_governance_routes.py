from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from backend.core.governance.bot_governance import (
    BotGovernanceSystem,
    BotManifest,
    BotPermission,
    get_governance,
)
from backend.security.auth import get_current_user
from backend.database.session import wrap_session_factory
from backend.database.config import get_db_async
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from backend.models.governance import GovernanceBot, GovernanceApproval, GovernanceActivity
try:
    from backend.bots.ws_manager import broadcast_event  # type: ignore
except Exception:
    broadcast_event = None  # type: ignore

router = APIRouter(prefix="/api/v1/governance", tags=["Governance"])


# Request models (Pydantic)
class PermissionModel(BaseModel):
    id: str
    name: str
    description: str
    resource: str
    action: str
    risk_level: int = Field(ge=1, le=5)


class ManifestModel(BaseModel):
    bot_id: str
    name: str
    version: str
    description: str
    author: str
    created_at: datetime
    updated_at: datetime
    required_permissions: List[PermissionModel] = []
    external_apis: List[Dict[str, Any]] = []
    database_access: List[str] = []
    constraints: Dict[str, Any] = {}
    code_hash: str
    config_hash: str
    signature: Optional[str] = None


class ApproveModel(BaseModel):
    approver: Optional[str] = None
    comments: Optional[str] = ""


class ActivateModel(BaseModel):
    environment: str


def _require_admin(user: Dict[str, Any]) -> None:
    role = str(user.get("effective_role") or user.get("role") or "user").strip().lower()
    if role not in {"admin", "system_admin", "super_admin", "owner"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")


@router.post("/bots/register")
async def register_bot(
    manifest: ManifestModel,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    _require_admin(current_user)
    gov: BotGovernanceSystem = get_governance()
    perms = [
        BotPermission(
            id=p.id,
            name=p.name,
            description=p.description,
            resource=p.resource,
            action=p.action,
            risk_level=p.risk_level,
        )
        for p in (manifest.required_permissions or [])
    ]
    mf = BotManifest(
        bot_id=manifest.bot_id,
        name=manifest.name,
        version=manifest.version,
        description=manifest.description,
        author=manifest.author,
        created_at=manifest.created_at,
        updated_at=manifest.updated_at,
        required_permissions=perms,
        external_apis=list(manifest.external_apis or []),
        database_access=list(manifest.database_access or []),
        constraints=dict(manifest.constraints or {}),
        code_hash=manifest.code_hash,
        config_hash=manifest.config_hash,
        signature=manifest.signature,
    )
    result = gov.register_bot(mf)
    # Persist to DB on success
    if result.get("success"):
        try:
            async with wrap_session_factory(get_db_async) as session:
                existing = await session.get(GovernanceBot, manifest.bot_id)
                manifest_json = {
                    "required_permissions": [
                        {
                            "id": p.id,
                            "name": p.name,
                            "description": p.description,
                            "resource": p.resource,
                            "action": p.action,
                            "risk_level": p.risk_level,
                        }
                        for p in (manifest.required_permissions or [])
                    ],
                    "external_apis": list(manifest.external_apis or []),
                    "database_access": list(manifest.database_access or []),
                    "constraints": dict(manifest.constraints or {}),
                }
                if existing is None:
                    row = GovernanceBot(
                        bot_id=manifest.bot_id,
                        name=manifest.name,
                        version=manifest.version,
                        description=manifest.description,
                        author=manifest.author,
                        status="under_review",
                        approvals_count=0,
                        manifest_json=manifest_json,
                        code_hash=manifest.code_hash,
                        config_hash=manifest.config_hash,
                        signature=manifest.signature,
                    )
                    session.add(row)
                else:
                    existing.name = manifest.name
                    existing.version = manifest.version
                    existing.description = manifest.description
                    existing.author = manifest.author
                    existing.status = "under_review"
                    existing.manifest_json = manifest_json
                    existing.code_hash = manifest.code_hash
                    existing.config_hash = manifest.config_hash
                    existing.signature = manifest.signature
                await session.commit()
        except SQLAlchemyError:
            # Ignore persistence failure to keep API responsive
            pass
    if broadcast_event is not None:
        try:
            await broadcast_event(
                channel="governance.bots.register",
                payload={
                    "bot_id": manifest.bot_id,
                    "name": manifest.name,
                    "status": result.get("status"),
                },
            )
        except Exception:
            pass
    return result


@router.post("/bots/{bot_id}/approve")
async def approve_bot(
    bot_id: str,
    payload: ApproveModel,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    _require_admin(current_user)
    gov: BotGovernanceSystem = get_governance()
    approver = payload.approver or str(current_user.get("email") or current_user.get("name") or "admin")
    result = gov.approve_bot(bot_id, approver=approver, comments=payload.comments or "")
    # Persist approval and update status if threshold met
    if result.get("success"):
        try:
            async with wrap_session_factory(get_db_async) as session:
                bot = await session.get(GovernanceBot, bot_id)
                if bot is None:
                    raise HTTPException(status_code=404, detail="bot not found")
                approval = GovernanceApproval(
                    bot_id=bot_id,
                    approver=approver,
                    role="security_team",
                    decision="approved",
                    comments=payload.comments or "",
                )
                session.add(approval)
                # increment approvals_count and update status if needed
                bot.approvals_count = int(bot.approvals_count or 0) + 1
                min_needed = int(gov.approval_workflow.get("min_approvals", 2))
                if bot.approvals_count >= min_needed:
                    bot.status = "approved"
                await session.commit()
        except SQLAlchemyError:
            pass
    if broadcast_event is not None and result.get("success"):
        try:
            await broadcast_event(
                channel="governance.bots.approve",
                payload={
                    "bot_id": bot_id,
                    "status": result.get("status"),
                    "approver": approver,
                },
            )
        except Exception:
            pass
    return result


@router.post("/bots/{bot_id}/activate")
async def activate_bot(
    bot_id: str,
    payload: ActivateModel,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    _require_admin(current_user)
    gov: BotGovernanceSystem = get_governance()
    result = gov.activate_bot(bot_id, environment=payload.environment)
    if result.get("success"):
        try:
            async with wrap_session_factory(get_db_async) as session:
                bot = await session.get(GovernanceBot, bot_id)
                if bot is not None:
                    activity = GovernanceActivity(
                        bot_id=bot_id,
                        action="activation",
                        environment=payload.environment,
                        details={
                            "message": result.get("message"),
                            "monitoring_dashboard": result.get("monitoring_dashboard"),
                        },
                    )
                    session.add(activity)
                    if payload.environment == "production":
                        bot.status = "active"
                    await session.commit()
        except SQLAlchemyError:
            pass
    if broadcast_event is not None and result.get("success"):
        try:
            await broadcast_event(
                channel="governance.bots.activate",
                payload={
                    "bot_id": bot_id,
                    "environment": payload.environment,
                    "status": result.get("message"),
                },
            )
        except Exception:
            pass
    return result


@router.get("/bots/{bot_id}")
async def get_bot_status(
    bot_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    _require_admin(current_user)
    # Prefer DB if available, fallback to in-memory
    try:
        async with wrap_session_factory(get_db_async) as session:
            bot = await session.get(GovernanceBot, bot_id)
            if bot is None:
                raise HTTPException(status_code=404, detail="bot not found")
            # recent approvals
            approvals = (await session.execute(
                select(GovernanceApproval).where(GovernanceApproval.bot_id == bot_id).order_by(GovernanceApproval.created_at.desc())
            )).scalars().all()
            # recent activity
            activity = (await session.execute(
                select(GovernanceActivity).where(GovernanceActivity.bot_id == bot_id).order_by(GovernanceActivity.created_at.desc())
            )).scalars().all()
            return {
                "ok": True,
                "bot_id": bot_id,
                "name": bot.name,
                "status": bot.status,
                "approvals": [
                    {
                        "approver": a.approver,
                        "role": a.role,
                        "decision": a.decision,
                        "comments": a.comments,
                        "timestamp": a.created_at,
                    }
                    for a in approvals
                ],
                "activity_log": [
                    {
                        "action": ac.action,
                        "environment": ac.environment,
                        "timestamp": ac.created_at,
                        "details": ac.details,
                    }
                    for ac in activity
                ],
            }
    except SQLAlchemyError:
        pass
    # fallback to in-memory registry
    gov: BotGovernanceSystem = get_governance()
    rec = gov.bot_registry.get(bot_id)
    if not rec:
        raise HTTPException(status_code=404, detail="bot not found")
    st = rec.get("status")
    status_value = st.value if (st is not None and hasattr(st, "value")) else st
    return {
        "ok": True,
        "bot_id": bot_id,
        "status": status_value,
        "approvals": rec.get("approvals", []),
        "activity_log": rec.get("activity_log", []),
    }


@router.get("/bots")
async def list_bots(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    _require_admin(current_user)
    # Prefer DB listing, fallback to in-memory
    try:
        async with wrap_session_factory(get_db_async) as session:
            rows = (await session.execute(select(GovernanceBot))).scalars().all()
            items: List[Dict[str, Any]] = [
                {
                    "bot_id": r.bot_id,
                    "name": r.name,
                    "status": r.status,
                    "registered_at": r.created_at,
                    "approvals": int(r.approvals_count or 0),
                }
                for r in rows
            ]
            return {"ok": True, "count": len(items), "bots": items}
    except SQLAlchemyError:
        pass
    gov: BotGovernanceSystem = get_governance()
    items: List[Dict[str, Any]] = []
    for bot_id, rec in gov.bot_registry.items():
        st = rec.get("status")
        status_value = st.value if (st is not None and hasattr(st, "value")) else st
        items.append({
            "bot_id": bot_id,
            "name": getattr(rec.get("manifest"), "name", None),
            "status": status_value,
            "registered_at": rec.get("registration_date"),
            "approvals": len(rec.get("approvals", [])),
        })
    return {"ok": True, "count": len(items), "bots": items}


