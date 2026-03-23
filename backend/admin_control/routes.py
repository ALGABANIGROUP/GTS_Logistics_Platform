from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, NoReturn, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.admin_control import schemas, service
from backend.database.config import get_db
from backend.security.auth import require_roles


ADMIN_ROLES = ["admin", "system_admin", "super_admin", "owner"]
SUPER_ADMIN_ROLES = ["super_admin", "owner"]
admin_required = require_roles(ADMIN_ROLES)
super_admin_required = require_roles(SUPER_ADMIN_ROLES)

router = APIRouter(prefix="/api/v1/admin", tags=["Admin Control"])


def _actor_id(current_user: Dict[str, Any]) -> Optional[int]:
    try:
        return int(current_user.get("sub") or 0) or None
    except Exception:
        return None


def _client_ip(request: Request) -> Optional[str]:
    try:
        return request.client.host if request.client else None
    except Exception:
        return None


def _handle_value_error(exc: ValueError) -> NoReturn:
    message = str(exc)
    status_code = status.HTTP_404_NOT_FOUND if "not found" in message.lower() else status.HTTP_400_BAD_REQUEST
    raise HTTPException(status_code=status_code, detail=message) from exc


@router.get("/org/tree", dependencies=[Depends(admin_required)])
async def get_org_tree(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    data = await service.get_org_tree(db)
    return {"ok": True, "data": data}


@router.post("/org/units", dependencies=[Depends(admin_required)])
async def create_org_unit(
    payload: schemas.OrgUnitCreate,
    request: Request,
    current_user: Dict[str, Any] = Depends(admin_required),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    data = await service.create_org_unit(
        db,
        payload.model_dump(),
        audit={"actor_user_id": _actor_id(current_user), "ip": _client_ip(request)},
    )
    return {"ok": True, "data": data}


@router.put("/org/units/{unit_id}", dependencies=[Depends(admin_required)])
async def update_org_unit(
    unit_id: int,
    payload: schemas.OrgUnitUpdate,
    request: Request,
    current_user: Dict[str, Any] = Depends(admin_required),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    data = await service.update_org_unit(
        db,
        unit_id,
        payload.model_dump(),
        audit={"actor_user_id": _actor_id(current_user), "ip": _client_ip(request)},
    )
    return {"ok": True, "data": data}


@router.post("/org/units/{unit_id}/move", dependencies=[Depends(admin_required)])
async def move_org_unit(
    unit_id: int,
    payload: schemas.OrgUnitMove,
    request: Request,
    current_user: Dict[str, Any] = Depends(admin_required),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    try:
        data = await service.move_org_unit(
            db,
            unit_id,
            payload.model_dump(),
            audit={"actor_user_id": _actor_id(current_user), "ip": _client_ip(request)},
        )
        return {"ok": True, "data": data}
    except ValueError as exc:
        _handle_value_error(exc)


@router.get("/users", dependencies=[Depends(super_admin_required)])
async def list_users(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    data = await service.list_users(db)
    return {"ok": True, "data": data}


@router.post("/users", dependencies=[Depends(super_admin_required)])
async def create_user(
    payload: schemas.UserCreatePayload,
    request: Request,
    current_user: Dict[str, Any] = Depends(super_admin_required),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    try:
        data = await service.create_user(
            db,
            payload.model_dump(),
            audit={"actor_user_id": _actor_id(current_user), "ip": _client_ip(request)},
        )
        return {"ok": True, "data": data}
    except ValueError as exc:
        _handle_value_error(exc)


@router.put("/users/{user_id}", dependencies=[Depends(super_admin_required)])
async def update_user(
    user_id: int,
    payload: schemas.UserUpdatePayload,
    request: Request,
    current_user: Dict[str, Any] = Depends(super_admin_required),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    try:
        data = await service.update_user(
            db,
            user_id,
            payload.model_dump(exclude_unset=True),
            audit={"actor_user_id": _actor_id(current_user), "ip": _client_ip(request)},
        )
        return {"ok": True, "data": data}
    except ValueError as exc:
        _handle_value_error(exc)


@router.patch("/users/{user_id}", dependencies=[Depends(super_admin_required)])
async def patch_user(
    user_id: int,
    payload: schemas.UserUpdatePayload,
    request: Request,
    current_user: Dict[str, Any] = Depends(super_admin_required),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    try:
        data = await service.update_user(
            db,
            user_id,
            payload.model_dump(exclude_unset=True),
            audit={"actor_user_id": _actor_id(current_user), "ip": _client_ip(request)},
        )
        return {"ok": True, "data": data}
    except ValueError as exc:
        _handle_value_error(exc)


@router.post("/users/{user_id}/deactivate", dependencies=[Depends(super_admin_required)])
async def deactivate_user(
    user_id: int,
    request: Request,
    payload: Optional[Dict[str, Any]] = None,
    current_user: Dict[str, Any] = Depends(super_admin_required),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    try:
        data = await service.deactivate_user(
            db,
            user_id,
            payload or {},
            audit={"actor_user_id": _actor_id(current_user), "ip": _client_ip(request)},
        )
        return {"ok": True, "data": data}
    except ValueError as exc:
        _handle_value_error(exc)


@router.delete("/users/{user_id}", dependencies=[Depends(super_admin_required)])
async def delete_user(
    user_id: int,
    request: Request,
    current_user: Dict[str, Any] = Depends(super_admin_required),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    try:
        data = await service.delete_user(
            db,
            user_id,
            audit={"actor_user_id": _actor_id(current_user), "ip": _client_ip(request)},
        )
        return {"ok": True, "data": data}
    except ValueError as exc:
        _handle_value_error(exc)


@router.post("/users/{user_id}/roles", dependencies=[Depends(super_admin_required)])
async def assign_user_role(
    user_id: int,
    payload: schemas.UserRoleAssignPayload,
    request: Request,
    current_user: Dict[str, Any] = Depends(super_admin_required),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    try:
        data = await service.assign_user_role(
            db,
            user_id,
            payload.model_dump(),
            audit={"actor_user_id": _actor_id(current_user), "ip": _client_ip(request)},
        )
        return {"ok": True, "data": data}
    except ValueError as exc:
        _handle_value_error(exc)


@router.patch("/users/{user_id}/role", dependencies=[Depends(super_admin_required)])
async def update_user_role(
    user_id: int,
    payload: schemas.UserRoleUpdatePayload,
    request: Request,
    current_user: Dict[str, Any] = Depends(super_admin_required),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    try:
        data = await service.set_user_role(
            db,
            user_id,
            payload.model_dump(),
            audit={"actor_user_id": _actor_id(current_user), "ip": _client_ip(request)},
        )
        return {"ok": True, "data": data}
    except ValueError as exc:
        _handle_value_error(exc)


@router.post("/users/{user_id}/ban", dependencies=[Depends(super_admin_required)])
async def ban_user(
    user_id: int,
    payload: schemas.UserBanPayload,
    request: Request,
    current_user: Dict[str, Any] = Depends(super_admin_required),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    try:
        data = await service.ban_user(
            db,
            user_id,
            payload.model_dump(),
            audit={"actor_user_id": _actor_id(current_user), "ip": _client_ip(request)},
        )
        return {"ok": True, "data": data}
    except ValueError as exc:
        _handle_value_error(exc)


@router.post("/users/{user_id}/unban", dependencies=[Depends(super_admin_required)])
async def unban_user(
    user_id: int,
    request: Request,
    current_user: Dict[str, Any] = Depends(super_admin_required),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    try:
        data = await service.unban_user(
            db,
            user_id,
            audit={"actor_user_id": _actor_id(current_user), "ip": _client_ip(request)},
        )
        return {"ok": True, "data": data}
    except ValueError as exc:
        _handle_value_error(exc)


@router.get("/roles", dependencies=[Depends(admin_required)])
async def list_roles(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    data = await service.list_roles(db)
    return {"ok": True, "data": data}


@router.post("/roles", dependencies=[Depends(admin_required)])
async def create_role(
    payload: schemas.RoleCreate,
    request: Request,
    current_user: Dict[str, Any] = Depends(admin_required),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    try:
        data = await service.create_role(
            db,
            payload.model_dump(),
            audit={"actor_user_id": _actor_id(current_user), "ip": _client_ip(request)},
        )
        return {"ok": True, "data": data}
    except ValueError as exc:
        _handle_value_error(exc)


@router.put("/roles/{role_id}", dependencies=[Depends(admin_required)])
async def update_role(
    role_id: int,
    payload: schemas.RoleUpdate,
    request: Request,
    current_user: Dict[str, Any] = Depends(admin_required),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    try:
        data = await service.update_role(
            db,
            role_id,
            payload.model_dump(),
            audit={"actor_user_id": _actor_id(current_user), "ip": _client_ip(request)},
        )
        return {"ok": True, "data": data}
    except ValueError as exc:
        _handle_value_error(exc)


@router.get("/roles/library", dependencies=[Depends(admin_required)])
async def list_role_library(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    data = await service.list_role_library(db)
    return {"ok": True, "data": data}


@router.post("/roles/permissions", dependencies=[Depends(admin_required)])
async def create_permission(
    payload: schemas.PermissionCreate,
    request: Request,
    current_user: Dict[str, Any] = Depends(admin_required),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    try:
        data = await service.create_permission(
            db,
            payload.model_dump(),
            audit={"actor_user_id": _actor_id(current_user), "ip": _client_ip(request)},
        )
        return {"ok": True, "data": data}
    except ValueError as exc:
        _handle_value_error(exc)


@router.get("/roles/permissions", dependencies=[Depends(admin_required)])
async def list_permissions(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    data = await service.list_permissions(db)
    return {"ok": True, "data": data}


@router.get("/roles/permissions/templates", dependencies=[Depends(admin_required)])
async def list_permission_templates(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    data = await service.list_permission_templates(db)
    return {"ok": True, "data": data}


@router.post("/roles/permissions/templates", dependencies=[Depends(admin_required)])
async def create_permission_template(
    payload: schemas.PermissionTemplateCreate,
    request: Request,
    current_user: Dict[str, Any] = Depends(admin_required),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    try:
        data = await service.create_permission_template(
            db,
            payload.model_dump(),
            audit={"actor_user_id": _actor_id(current_user), "ip": _client_ip(request)},
        )
        return {"ok": True, "data": data}
    except ValueError as exc:
        _handle_value_error(exc)


@router.post("/roles/permissions/templates/{template_id}/apply", dependencies=[Depends(admin_required)])
async def apply_permission_template(
    template_id: int,
    payload: schemas.PermissionTemplateApply,
    request: Request,
    current_user: Dict[str, Any] = Depends(admin_required),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    try:
        data = await service.apply_permission_template(
            db,
            template_id,
            payload.model_dump(),
            audit={"actor_user_id": _actor_id(current_user), "ip": _client_ip(request)},
        )
        return {"ok": True, "data": data}
    except ValueError as exc:
        _handle_value_error(exc)


@router.get("/sessions", dependencies=[Depends(admin_required)])
async def list_sessions(
    user_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    data = await service.list_sessions(db)
    if user_id is not None:
        sessions = [s for s in data.get("sessions", []) if s.get("user_id") == user_id]
        data = {"sessions": sessions, "count": len(sessions)}
    return {"ok": True, "data": data}


@router.post("/sessions/{session_id}/revoke", dependencies=[Depends(admin_required)])
async def revoke_session(
    session_id: int,
    request: Request,
    payload: Optional[schemas.SessionRevokePayload] = None,
    current_user: Dict[str, Any] = Depends(admin_required),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    try:
        data = await service.revoke_session(
            db,
            session_id,
            payload.model_dump() if payload else {},
            audit={"actor_user_id": _actor_id(current_user), "ip": _client_ip(request)},
        )
        return {"ok": True, "data": data}
    except ValueError as exc:
        _handle_value_error(exc)


@router.get("/audit", dependencies=[Depends(admin_required)])
async def search_audit_logs(
    actor_user_id: Optional[int] = None,
    action: Optional[str] = None,
    target_type: Optional[str] = None,
    severity: Optional[str] = None,
    start_at: Optional[datetime] = None,
    end_at: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    params: Dict[str, Any] = {
        "actor_user_id": actor_user_id,
        "action": action,
        "target_type": target_type,
        "severity": severity,
        "start_at": start_at,
        "end_at": end_at,
    }
    data = await service.search_audit_logs(db, params)
    return {"ok": True, "data": data}


@router.get("/audit/activity-summary", dependencies=[Depends(admin_required)])
async def activity_summary(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    data = await service.activity_summary(db)
    return {"ok": True, "data": data}


@router.get("/alerts", dependencies=[Depends(admin_required)])
async def list_alert_rules(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    data = await service.list_alert_rules(db)
    return {"ok": True, "data": data}


@router.post("/alerts", dependencies=[Depends(admin_required)])
async def create_alert_rule(
    payload: schemas.AlertRuleCreate,
    request: Request,
    current_user: Dict[str, Any] = Depends(admin_required),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    try:
        data = await service.create_alert_rule(
            db,
            payload.model_dump(),
            audit={"actor_user_id": _actor_id(current_user), "ip": _client_ip(request)},
        )
        return {"ok": True, "data": data}
    except ValueError as exc:
        _handle_value_error(exc)


@router.put("/alerts/{rule_id}", dependencies=[Depends(admin_required)])
async def update_alert_rule(
    rule_id: int,
    payload: schemas.AlertRuleUpdate,
    request: Request,
    current_user: Dict[str, Any] = Depends(admin_required),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    try:
        data = await service.update_alert_rule(
            db,
            rule_id,
            payload.model_dump(),
            audit={"actor_user_id": _actor_id(current_user), "ip": _client_ip(request)},
        )
        return {"ok": True, "data": data}
    except ValueError as exc:
        _handle_value_error(exc)

