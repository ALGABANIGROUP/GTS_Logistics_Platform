from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.admin_control import models
from backend.models.user import User
from backend.security.hashing import get_password_hash

_SUPER_ADMIN_ROLES = {"super_admin", "owner"}


def _normalize_role(value: Optional[str]) -> str:
    return str(value or "user").strip().lower()


def _is_super_admin_role(value: Optional[str]) -> bool:
    return _normalize_role(value) in _SUPER_ADMIN_ROLES


def _user_to_safe(user: User) -> Dict[str, Any]:
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "username": user.username,
        "company": getattr(user, "company", None),
        "country": getattr(user, "country", None),
        "user_type": getattr(user, "user_type", None),
        "phone_number": getattr(user, "phone_number", None),
        "role": user.role,
        "is_active": user.is_active,
        "is_banned": getattr(user, "is_banned", False),
        "ban_reason": getattr(user, "ban_reason", None),
        "banned_until": getattr(user, "banned_until", None),
        "is_deleted": getattr(user, "is_deleted", False),
        "deleted_at": getattr(user, "deleted_at", None),
        "manager_id": getattr(user, "manager_id", None),
    }


async def _super_admin_count(db: AsyncSession) -> int:
    stmt = select(func.count(User.id)).where(User.role.in_(_SUPER_ADMIN_ROLES))
    if hasattr(User, "is_deleted"):
        stmt = stmt.where(User.is_deleted.is_(False))
    res = await db.execute(stmt)
    return int(res.scalar() or 0)


def _ensure_not_self(actor_user_id: Optional[int], target_user_id: int, action: str) -> None:
    if actor_user_id and int(actor_user_id) == int(target_user_id):
        raise ValueError(f"Cannot {action} current user")


async def _ensure_not_last_super_admin(
    db: AsyncSession,
    target_user: User,
    *,
    new_role: Optional[str] = None,
) -> None:
    if _is_super_admin_role(target_user.role):
        if new_role is not None and _is_super_admin_role(new_role):
            return
        count = await _super_admin_count(db)
        if count <= 1:
            raise ValueError("Cannot modify the last super admin")


async def log_audit(
    db: AsyncSession,
    *,
    actor_user_id: Optional[int],
    action: str,
    target_type: Optional[str],
    target_id: Optional[str],
    diff_json: Optional[Dict[str, Any]],
    ip: Optional[str],
    severity: Optional[str] = None,
) -> None:
    entry = models.AuditLog(
        actor_user_id=actor_user_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        diff_json=diff_json,
        ip=ip,
        severity=severity,
    )
    db.add(entry)
    await db.commit()


async def get_org_tree(
    db: AsyncSession,
    *,
    audit: Optional[Dict[str, Any]] = None,
    audit_action: Optional[str] = None,
) -> Dict[str, Any]:
    stmt = select(User).order_by(User.id)
    if hasattr(User, "is_deleted"):
        stmt = stmt.where(User.is_deleted.is_(False))
    res = await db.execute(stmt)
    users = res.scalars().all()
    if audit:
        await log_audit(
            db,
            actor_user_id=audit.get("actor_user_id"),
            action=audit_action or "org_chart_get",
            target_type="user",
            target_id=None,
            diff_json=None,
            ip=audit.get("ip"),
            severity=audit.get("severity", "info"),
        )
    return {"tree": _build_user_tree(users), "count": len(users)}


async def create_org_unit(
    db: AsyncSession,
    payload: Dict[str, Any],
    *,
    audit: Optional[Dict[str, Any]] = None,
    audit_action: Optional[str] = None,
) -> Dict[str, Any]:
    obj = models.OrgUnit(
        name=str(payload.get("name") or "").strip(),
        parent_id=payload.get("parent_id"),
        type=payload.get("type"),
        metadata_json=payload.get("metadata"),
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    if audit:
        await log_audit(
            db,
            actor_user_id=audit.get("actor_user_id"),
            action=audit_action or "org_unit_create",
            target_type="org_unit",
            target_id=str(obj.id),
            diff_json={"name": obj.name, "parent_id": obj.parent_id, "type": obj.type},
            ip=audit.get("ip"),
            severity=audit.get("severity", "info"),
        )
    return {"id": obj.id, "name": obj.name, "parent_id": obj.parent_id}


async def update_org_unit(
    db: AsyncSession,
    unit_id: int,
    payload: Dict[str, Any],
    *,
    audit: Optional[Dict[str, Any]] = None,
    audit_action: Optional[str] = None,
) -> Dict[str, Any]:
    res = await db.execute(select(models.OrgUnit).where(models.OrgUnit.id == unit_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise ValueError("Org unit not found")

    if payload.get("name") is not None:
        obj.name = str(payload.get("name") or "").strip()
    if payload.get("type") is not None:
        obj.type = payload.get("type")
    if payload.get("metadata") is not None:
        obj.metadata_json = payload.get("metadata")

    obj.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(obj)
    if audit:
        await log_audit(
            db,
            actor_user_id=audit.get("actor_user_id"),
            action=audit_action or "org_unit_update",
            target_type="org_unit",
            target_id=str(obj.id),
            diff_json={"name": obj.name, "parent_id": obj.parent_id, "type": obj.type},
            ip=audit.get("ip"),
            severity=audit.get("severity", "info"),
        )
    return {"id": obj.id, "name": obj.name}


async def move_org_unit(
    db: AsyncSession,
    unit_id: int,
    payload: Dict[str, Any],
    *,
    audit: Optional[Dict[str, Any]] = None,
    audit_action: Optional[str] = None,
) -> Dict[str, Any]:
    stmt = select(User).order_by(User.id)
    if hasattr(User, "is_deleted"):
        stmt = stmt.where(User.is_deleted.is_(False))
    res = await db.execute(stmt)
    users = res.scalars().all()
    parent_map = {user.id: getattr(user, "manager_id", None) for user in users}
    if unit_id not in parent_map:
        raise ValueError("User not found")
    if payload.get("parent_id") is not None and payload.get("parent_id") not in parent_map:
        raise ValueError("Manager not found")
    if _is_cycle(unit_id, payload.get("parent_id"), parent_map):
        raise ValueError("Move would create a cycle")

    res = await db.execute(select(User).where(User.id == unit_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise ValueError("User not found")

    obj.manager_id = payload.get("parent_id")
    obj.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(obj)
    if audit:
        await log_audit(
            db,
            actor_user_id=audit.get("actor_user_id"),
            action=audit_action or "org_unit_move",
            target_type="user",
            target_id=str(obj.id),
            diff_json={"manager_id": obj.manager_id},
            ip=audit.get("ip"),
            severity=audit.get("severity", "info"),
        )
    return {"id": obj.id, "manager_id": obj.manager_id}


async def list_users(
    db: AsyncSession,
    *,
    audit: Optional[Dict[str, Any]] = None,
    audit_action: Optional[str] = None,
) -> Dict[str, Any]:
    stmt = select(User).order_by(User.id)
    if hasattr(User, "is_deleted"):
        stmt = stmt.where(User.is_deleted.is_(False))
    res = await db.execute(stmt)
    users = res.scalars().all()
    if audit:
        await log_audit(
            db,
            actor_user_id=audit.get("actor_user_id"),
            action=audit_action or "user_list",
            target_type="user",
            target_id=None,
            diff_json=None,
            ip=audit.get("ip"),
            severity=audit.get("severity", "info"),
        )
    return {"users": [_user_to_safe(u) for u in users], "count": len(users)}


async def create_user(
    db: AsyncSession,
    payload: Dict[str, Any],
    *,
    audit: Optional[Dict[str, Any]] = None,
    audit_action: Optional[str] = None,
) -> Dict[str, Any]:
    email = str(payload.get("email") or "").strip().lower()
    if not email:
        raise ValueError("Email is required")
    res = await db.execute(select(User).where(User.email == email))
    if res.scalar_one_or_none():
        raise ValueError("User already exists")

    obj = User(
        email=email,
        full_name=payload.get("full_name"),
        username=payload.get("username"),
        role=_normalize_role(payload.get("role")),
        company=payload.get("company"),
        country=payload.get("country"),
        user_type=payload.get("user_type"),
        phone_number=payload.get("phone_number"),
        is_active=True if payload.get("is_active") is None else bool(payload.get("is_active")),
        is_banned=False,
        is_deleted=False,
        manager_id=payload.get("manager_id"),
    )
    raw_password = payload.get("password")
    if raw_password:
        obj.hashed_password = get_password_hash(raw_password)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    if audit:
        await log_audit(
            db,
            actor_user_id=audit.get("actor_user_id"),
            action=audit_action or "user_create",
            target_type="user",
            target_id=str(obj.id),
            diff_json={"email": obj.email, "role": obj.role},
            ip=audit.get("ip"),
            severity=audit.get("severity", "info"),
        )
    return _user_to_safe(obj)


async def update_user(
    db: AsyncSession,
    user_id: int,
    payload: Dict[str, Any],
    *,
    audit: Optional[Dict[str, Any]] = None,
    audit_action: Optional[str] = None,
) -> Dict[str, Any]:
    res = await db.execute(select(User).where(User.id == user_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise ValueError("User not found")

    if "email" in payload:
        new_email = str(payload.get("email") or "").strip().lower()
        if not new_email:
            raise ValueError("Email is required")
        if new_email != obj.email:
            email_res = await db.execute(select(User).where(User.email == new_email))
            if email_res.scalar_one_or_none():
                raise ValueError("Email already exists")
            obj.email = new_email

    for key in ("full_name", "username", "company", "country", "user_type", "phone_number"):
        if key in payload:
            setattr(obj, key, payload.get(key))

    if payload.get("role") is not None:
        new_role = _normalize_role(payload.get("role"))
        await _ensure_not_last_super_admin(db, obj, new_role=new_role)
        obj.role = new_role
    if payload.get("is_active") is not None:
        obj.is_active = bool(payload.get("is_active"))
    if payload.get("manager_id") is not None:
        obj.manager_id = payload.get("manager_id")
    raw_password = payload.get("password")
    if raw_password:
        obj.hashed_password = get_password_hash(raw_password)

    obj.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(obj)
    if audit:
        await log_audit(
            db,
            actor_user_id=audit.get("actor_user_id"),
            action=audit_action or "user_update",
            target_type="user",
            target_id=str(obj.id),
            diff_json={"role": obj.role, "is_active": obj.is_active},
            ip=audit.get("ip"),
            severity=audit.get("severity", "info"),
        )
    return _user_to_safe(obj)


async def deactivate_user(
    db: AsyncSession,
    user_id: int,
    payload: Optional[Dict[str, Any]] = None,
    *,
    audit: Optional[Dict[str, Any]] = None,
    audit_action: Optional[str] = None,
) -> Dict[str, Any]:
    res = await db.execute(select(User).where(User.id == user_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise ValueError("User not found")
    _ensure_not_self(audit.get("actor_user_id") if audit else None, obj.id, "deactivate")
    await _ensure_not_last_super_admin(db, obj)

    obj.is_active = False
    obj.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(obj)
    if audit:
        await log_audit(
            db,
            actor_user_id=audit.get("actor_user_id"),
            action=audit_action or "user_deactivate",
            target_type="user",
            target_id=str(obj.id),
            diff_json={"is_active": False, "reason": (payload or {}).get("reason")},
            ip=audit.get("ip"),
            severity=audit.get("severity", "warning"),
        )
    return {"id": obj.id, "is_active": obj.is_active}


async def delete_user(
    db: AsyncSession,
    user_id: int,
    *,
    audit: Optional[Dict[str, Any]] = None,
    audit_action: Optional[str] = None,
) -> Dict[str, Any]:
    res = await db.execute(select(User).where(User.id == user_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise ValueError("User not found")
    _ensure_not_self(audit.get("actor_user_id") if audit else None, obj.id, "delete")
    await _ensure_not_last_super_admin(db, obj)

    if hasattr(obj, "is_deleted"):
        obj.is_deleted = True
    if hasattr(obj, "deleted_at"):
        obj.deleted_at = datetime.now(timezone.utc)
    obj.is_active = False
    await db.commit()
    await db.refresh(obj)
    if audit:
        await log_audit(
            db,
            actor_user_id=audit.get("actor_user_id"),
            action=audit_action or "user_delete",
            target_type="user",
            target_id=str(user_id),
            diff_json={},
            ip=audit.get("ip"),
            severity=audit.get("severity", "warning"),
        )
    return _user_to_safe(obj)


async def set_user_role(
    db: AsyncSession,
    user_id: int,
    payload: Dict[str, Any],
    *,
    audit: Optional[Dict[str, Any]] = None,
    audit_action: Optional[str] = None,
) -> Dict[str, Any]:
    res = await db.execute(select(User).where(User.id == user_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise ValueError("User not found")
    new_role = _normalize_role(payload.get("role"))
    await _ensure_not_last_super_admin(db, obj, new_role=new_role)
    obj.role = new_role
    obj.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(obj)
    if audit:
        await log_audit(
            db,
            actor_user_id=audit.get("actor_user_id"),
            action=audit_action or "user_role_update",
            target_type="user",
            target_id=str(obj.id),
            diff_json={"role": obj.role},
            ip=audit.get("ip"),
            severity=audit.get("severity", "info"),
        )
    return _user_to_safe(obj)


async def ban_user(
    db: AsyncSession,
    user_id: int,
    payload: Dict[str, Any],
    *,
    audit: Optional[Dict[str, Any]] = None,
    audit_action: Optional[str] = None,
) -> Dict[str, Any]:
    res = await db.execute(select(User).where(User.id == user_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise ValueError("User not found")
    _ensure_not_self(audit.get("actor_user_id") if audit else None, obj.id, "ban")
    await _ensure_not_last_super_admin(db, obj)

    if hasattr(obj, "is_banned"):
        obj.is_banned = True
    if hasattr(obj, "ban_reason"):
        obj.ban_reason = payload.get("reason")
    if hasattr(obj, "banned_until"):
        obj.banned_until = payload.get("banned_until")
    obj.is_active = False
    obj.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(obj)
    if audit:
        await log_audit(
            db,
            actor_user_id=audit.get("actor_user_id"),
            action=audit_action or "user_ban",
            target_type="user",
            target_id=str(obj.id),
            diff_json={"is_banned": True, "reason": payload.get("reason")},
            ip=audit.get("ip"),
            severity=audit.get("severity", "warning"),
        )
    return _user_to_safe(obj)


async def unban_user(
    db: AsyncSession,
    user_id: int,
    *,
    audit: Optional[Dict[str, Any]] = None,
    audit_action: Optional[str] = None,
) -> Dict[str, Any]:
    res = await db.execute(select(User).where(User.id == user_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise ValueError("User not found")
    _ensure_not_self(audit.get("actor_user_id") if audit else None, obj.id, "unban")

    if hasattr(obj, "is_banned"):
        obj.is_banned = False
    if hasattr(obj, "ban_reason"):
        obj.ban_reason = None
    if hasattr(obj, "banned_until"):
        obj.banned_until = None
    obj.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(obj)
    if audit:
        await log_audit(
            db,
            actor_user_id=audit.get("actor_user_id"),
            action=audit_action or "user_unban",
            target_type="user",
            target_id=str(obj.id),
            diff_json={"is_banned": False},
            ip=audit.get("ip"),
            severity=audit.get("severity", "info"),
        )
    return _user_to_safe(obj)


async def assign_user_role(
    db: AsyncSession,
    user_id: int,
    payload: Dict[str, Any],
    *,
    audit: Optional[Dict[str, Any]] = None,
    audit_action: Optional[str] = None,
) -> Dict[str, Any]:
    res = await db.execute(select(User).where(User.id == user_id))
    if res.scalar_one_or_none() is None:
        raise ValueError("User not found")

    role_id = int(payload.get("role_id") or 0)
    res = await db.execute(select(models.Role).where(models.Role.id == role_id))
    if res.scalar_one_or_none() is None:
        raise ValueError("Role not found")

    res = await db.execute(
        select(models.UserRole).where(
            (models.UserRole.user_id == user_id) & (models.UserRole.role_id == role_id)
        )
    )
    assignment = res.scalar_one_or_none()
    if assignment:
        assignment.org_unit_id = payload.get("org_unit_id")
        assignment.expires_at = payload.get("expires_at")
    else:
        db.add(
            models.UserRole(
                user_id=user_id,
                role_id=role_id,
                org_unit_id=payload.get("org_unit_id"),
                expires_at=payload.get("expires_at"),
            )
        )
    await db.commit()
    if audit:
        await log_audit(
            db,
            actor_user_id=audit.get("actor_user_id"),
            action=audit_action or "role_assign",
            target_type="user_role",
            target_id=f"{user_id}:{role_id}",
            diff_json={"org_unit_id": payload.get("org_unit_id"), "expires_at": payload.get("expires_at")},
            ip=audit.get("ip"),
            severity=audit.get("severity", "info"),
        )
    return {"user_id": user_id, "role_id": role_id}


async def list_roles(
    db: AsyncSession,
    *,
    audit: Optional[Dict[str, Any]] = None,
    audit_action: Optional[str] = None,
) -> Dict[str, Any]:
    res = await db.execute(select(models.Role).order_by(models.Role.id))
    roles = res.scalars().all()
    if audit:
        await log_audit(
            db,
            actor_user_id=audit.get("actor_user_id"),
            action=audit_action or "role_list",
            target_type="role",
            target_id=None,
            diff_json=None,
            ip=audit.get("ip"),
            severity=audit.get("severity", "info"),
        )
    return {
        "roles": [
            {
                "id": r.id,
                "name": r.name,
                "description": r.description,
                "priority": r.priority,
                "parent_role_id": r.parent_role_id,
            }
            for r in roles
        ],
        "count": len(roles),
    }


async def create_role(
    db: AsyncSession,
    payload: Dict[str, Any],
    *,
    audit: Optional[Dict[str, Any]] = None,
    audit_action: Optional[str] = None,
) -> Dict[str, Any]:
    obj = models.Role(
        name=str(payload.get("name") or "").strip().lower(),
        description=payload.get("description"),
        priority=payload.get("priority"),
        parent_role_id=payload.get("parent_role_id"),
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    if audit:
        await log_audit(
            db,
            actor_user_id=audit.get("actor_user_id"),
            action=audit_action or "role_create",
            target_type="role",
            target_id=str(obj.id),
            diff_json={"name": obj.name},
            ip=audit.get("ip"),
            severity=audit.get("severity", "info"),
        )
    return {"id": obj.id, "name": obj.name}


async def update_role(
    db: AsyncSession,
    role_id: int,
    payload: Dict[str, Any],
    *,
    audit: Optional[Dict[str, Any]] = None,
    audit_action: Optional[str] = None,
) -> Dict[str, Any]:
    res = await db.execute(select(models.Role).where(models.Role.id == role_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise ValueError("Role not found")

    if "name" in payload:
        obj.name = str(payload.get("name") or "").strip().lower()
    if "description" in payload:
        obj.description = payload.get("description")
    if "priority" in payload:
        obj.priority = payload.get("priority")
    if "parent_role_id" in payload:
        obj.parent_role_id = payload.get("parent_role_id")

    obj.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(obj)
    if audit:
        await log_audit(
            db,
            actor_user_id=audit.get("actor_user_id"),
            action=audit_action or "role_update",
            target_type="role",
            target_id=str(obj.id),
            diff_json={"name": obj.name},
            ip=audit.get("ip"),
            severity=audit.get("severity", "info"),
        )
    return {"id": obj.id, "name": obj.name}


async def list_role_library(
    db: AsyncSession,
    *,
    audit: Optional[Dict[str, Any]] = None,
    audit_action: Optional[str] = None,
) -> Dict[str, Any]:
    roles_res = await db.execute(select(models.Role).order_by(models.Role.id))
    roles = roles_res.scalars().all()
    perms_res = await db.execute(select(models.Permission).order_by(models.Permission.id))
    permissions = perms_res.scalars().all()
    if audit:
        await log_audit(
            db,
            actor_user_id=audit.get("actor_user_id"),
            action=audit_action or "org_role_library_list",
            target_type="role",
            target_id=None,
            diff_json=None,
            ip=audit.get("ip"),
            severity=audit.get("severity", "info"),
        )
    return {
        "roles": [
            {
                "id": r.id,
                "name": r.name,
                "description": r.description,
                "priority": r.priority,
                "parent_role_id": r.parent_role_id,
            }
            for r in roles
        ],
        "permissions": [
            {
                "id": p.id,
                "code": p.code,
                "description": p.description,
                "scope_type": p.scope_type,
                "scope_key": p.scope_key,
            }
            for p in permissions
        ],
    }


async def create_permission(
    db: AsyncSession,
    payload: Dict[str, Any],
    *,
    audit: Optional[Dict[str, Any]] = None,
    audit_action: Optional[str] = None,
) -> Dict[str, Any]:
    obj = models.Permission(
        code=str(payload.get("code") or "").strip().lower(),
        description=payload.get("description"),
        scope_type=str(payload.get("scope_type") or "").strip().lower(),
        scope_key=payload.get("scope_key"),
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    if audit:
        await log_audit(
            db,
            actor_user_id=audit.get("actor_user_id"),
            action=audit_action or "permission_create",
            target_type="permission",
            target_id=str(obj.id),
            diff_json={"code": obj.code},
            ip=audit.get("ip"),
            severity=audit.get("severity", "info"),
        )
    return {"id": obj.id, "code": obj.code}


async def list_permissions(
    db: AsyncSession,
    *,
    audit: Optional[Dict[str, Any]] = None,
    audit_action: Optional[str] = None,
) -> Dict[str, Any]:
    res = await db.execute(select(models.Permission).order_by(models.Permission.id))
    permissions = res.scalars().all()
    if audit:
        await log_audit(
            db,
            actor_user_id=audit.get("actor_user_id"),
            action=audit_action or "permission_list",
            target_type="permission",
            target_id=None,
            diff_json=None,
            ip=audit.get("ip"),
            severity=audit.get("severity", "info"),
        )
    return {
        "permissions": [
            {
                "id": p.id,
                "code": p.code,
                "description": p.description,
                "scope_type": p.scope_type,
                "scope_key": p.scope_key,
            }
            for p in permissions
        ]
    }


async def list_permission_templates(
    db: AsyncSession,
    *,
    audit: Optional[Dict[str, Any]] = None,
    audit_action: Optional[str] = None,
) -> Dict[str, Any]:
    res = await db.execute(select(models.PermissionTemplate).order_by(models.PermissionTemplate.id))
    templates = res.scalars().all()
    if audit:
        await log_audit(
            db,
            actor_user_id=audit.get("actor_user_id"),
            action=audit_action or "permission_template_list",
            target_type="permission_template",
            target_id=None,
            diff_json=None,
            ip=audit.get("ip"),
            severity=audit.get("severity", "info"),
        )
    return {"templates": [{"id": t.id, "name": t.name, "description": t.description} for t in templates]}


async def create_permission_template(
    db: AsyncSession,
    payload: Dict[str, Any],
    *,
    audit: Optional[Dict[str, Any]] = None,
    audit_action: Optional[str] = None,
) -> Dict[str, Any]:
    obj = models.PermissionTemplate(
        name=str(payload.get("name") or "").strip().lower(),
        description=payload.get("description"),
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)

    for perm_id in payload.get("permission_ids") or []:
        db.add(models.TemplatePermission(template_id=obj.id, permission_id=int(perm_id)))
    await db.commit()

    if audit:
        await log_audit(
            db,
            actor_user_id=audit.get("actor_user_id"),
            action=audit_action or "permission_template_create",
            target_type="permission_template",
            target_id=str(obj.id),
            diff_json={"name": obj.name},
            ip=audit.get("ip"),
            severity=audit.get("severity", "info"),
        )
    return {"id": obj.id, "name": obj.name}


async def apply_permission_template(
    db: AsyncSession,
    template_id: int,
    payload: Dict[str, Any],
    *,
    audit: Optional[Dict[str, Any]] = None,
    audit_action: Optional[str] = None,
) -> Dict[str, Any]:
    res = await db.execute(
        select(models.PermissionTemplate).where(models.PermissionTemplate.id == template_id)
    )
    if res.scalar_one_or_none() is None:
        raise ValueError("Template not found")

    role_id = int(payload.get("role_id") or 0)
    res = await db.execute(
        select(models.TemplatePermission).where(models.TemplatePermission.template_id == template_id)
    )
    template_perms = res.scalars().all()
    for tp in template_perms:
        db.add(models.RolePermission(role_id=role_id, permission_id=tp.permission_id))
    await db.commit()
    if audit:
        await log_audit(
            db,
            actor_user_id=audit.get("actor_user_id"),
            action=audit_action or "permission_template_apply",
            target_type="role",
            target_id=str(role_id),
            diff_json={"template_id": template_id},
            ip=audit.get("ip"),
            severity=audit.get("severity", "info"),
        )
    return {"role_id": role_id, "template_id": template_id}


async def list_sessions(
    db: AsyncSession,
    *,
    audit: Optional[Dict[str, Any]] = None,
    audit_action: Optional[str] = None,
) -> Dict[str, Any]:
    res = await db.execute(select(models.Session).order_by(models.Session.created_at.desc()))
    sessions = res.scalars().all()
    if audit:
        await log_audit(
            db,
            actor_user_id=audit.get("actor_user_id"),
            action=audit_action or "session_list",
            target_type="session",
            target_id=None,
            diff_json=None,
            ip=audit.get("ip"),
            severity=audit.get("severity", "info"),
        )
    return {
        "sessions": [
            {
                "id": s.id,
                "user_id": s.user_id,
                "created_at": s.created_at,
                "last_seen_at": s.last_seen_at,
                "ip": s.ip,
                "user_agent": s.user_agent,
                "revoked_at": s.revoked_at,
            }
            for s in sessions
        ],
        "count": len(sessions),
    }


async def revoke_session(
    db: AsyncSession,
    session_id: int,
    payload: Optional[Dict[str, Any]] = None,
    *,
    audit: Optional[Dict[str, Any]] = None,
    audit_action: Optional[str] = None,
) -> Dict[str, Any]:
    res = await db.execute(select(models.Session).where(models.Session.id == session_id))
    sess = res.scalar_one_or_none()
    if not sess:
        raise ValueError("Session not found")

    sess.revoked_at = datetime.now(timezone.utc)
    await db.commit()
    if audit:
        await log_audit(
            db,
            actor_user_id=audit.get("actor_user_id"),
            action=audit_action or "session_revoke",
            target_type="session",
            target_id=str(session_id),
            diff_json={"reason": (payload or {}).get("reason")},
            ip=audit.get("ip"),
            severity=audit.get("severity", "warning"),
        )
    return {"id": session_id, "revoked_at": sess.revoked_at}


async def search_audit_logs(
    db: AsyncSession,
    params: Dict[str, Any],
    *,
    audit: Optional[Dict[str, Any]] = None,
    audit_action: Optional[str] = None,
) -> Dict[str, Any]:
    stmt = select(models.AuditLog).order_by(models.AuditLog.created_at.desc())
    conditions = []
    if params.get("actor_user_id") is not None:
        conditions.append(models.AuditLog.actor_user_id == params["actor_user_id"])
    if params.get("action"):
        conditions.append(models.AuditLog.action == params["action"])
    if params.get("target_type"):
        conditions.append(models.AuditLog.target_type == params["target_type"])
    if params.get("severity"):
        conditions.append(models.AuditLog.severity == params["severity"])
    if params.get("start_at"):
        conditions.append(models.AuditLog.created_at >= params["start_at"])
    if params.get("end_at"):
        conditions.append(models.AuditLog.created_at <= params["end_at"])
    if conditions:
        stmt = stmt.where(and_(*conditions))

    res = await db.execute(stmt)
    logs = res.scalars().all()
    if audit:
        await log_audit(
            db,
            actor_user_id=audit.get("actor_user_id"),
            action=audit_action or "audit_log_search",
            target_type="audit_log",
            target_id=None,
            diff_json=params,
            ip=audit.get("ip"),
            severity=audit.get("severity", "info"),
        )
    return {
        "logs": [
            {
                "id": log.id,
                "actor_user_id": log.actor_user_id,
                "action": log.action,
                "target_type": log.target_type,
                "target_id": log.target_id,
                "diff_json": log.diff_json,
                "ip": log.ip,
                "created_at": log.created_at,
                "severity": log.severity,
            }
            for log in logs
        ],
        "count": len(logs),
    }


async def activity_summary(
    db: AsyncSession,
    *,
    audit: Optional[Dict[str, Any]] = None,
    audit_action: Optional[str] = None,
) -> Dict[str, Any]:
    res = await db.execute(
        select(models.AuditLog.action, func.count(models.AuditLog.id)).group_by(models.AuditLog.action)
    )
    summary = {row[0]: row[1] for row in res.all()}
    if audit:
        await log_audit(
            db,
            actor_user_id=audit.get("actor_user_id"),
            action=audit_action or "activity_summary",
            target_type="audit_log",
            target_id=None,
            diff_json=None,
            ip=audit.get("ip"),
            severity=audit.get("severity", "info"),
        )
    return {"summary": summary}


async def list_alert_rules(
    db: AsyncSession,
    *,
    audit: Optional[Dict[str, Any]] = None,
    audit_action: Optional[str] = None,
) -> Dict[str, Any]:
    res = await db.execute(select(models.AlertRule).order_by(models.AlertRule.id))
    rules = res.scalars().all()
    if audit:
        await log_audit(
            db,
            actor_user_id=audit.get("actor_user_id"),
            action=audit_action or "alert_rule_list",
            target_type="alert_rule",
            target_id=None,
            diff_json=None,
            ip=audit.get("ip"),
            severity=audit.get("severity", "info"),
        )
    return {
        "rules": [
            {
                "id": r.id,
                "name": r.name,
                "severity": r.severity,
                "condition_json": r.condition_json,
                "channels_json": r.channels_json,
                "is_enabled": r.is_enabled,
                "created_at": r.created_at,
            }
            for r in rules
        ],
        "count": len(rules),
    }


async def create_alert_rule(
    db: AsyncSession,
    payload: Dict[str, Any],
    *,
    audit: Optional[Dict[str, Any]] = None,
    audit_action: Optional[str] = None,
) -> Dict[str, Any]:
    obj = models.AlertRule(
        name=str(payload.get("name") or "").strip(),
        severity=payload.get("severity"),
        condition_json=payload.get("condition_json"),
        channels_json=payload.get("channels_json"),
        is_enabled=True if payload.get("is_enabled") is None else bool(payload.get("is_enabled")),
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    if audit:
        await log_audit(
            db,
            actor_user_id=audit.get("actor_user_id"),
            action=audit_action or "alert_rule_create",
            target_type="alert_rule",
            target_id=str(obj.id),
            diff_json={"name": obj.name, "severity": obj.severity},
            ip=audit.get("ip"),
            severity=audit.get("severity", "info"),
        )
    return {"id": obj.id, "name": obj.name}


async def update_alert_rule(
    db: AsyncSession,
    rule_id: int,
    payload: Dict[str, Any],
    *,
    audit: Optional[Dict[str, Any]] = None,
    audit_action: Optional[str] = None,
) -> Dict[str, Any]:
    res = await db.execute(select(models.AlertRule).where(models.AlertRule.id == rule_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise ValueError("Alert rule not found")

    if payload.get("name") is not None:
        obj.name = str(payload.get("name") or "").strip()
    if payload.get("severity") is not None:
        obj.severity = payload.get("severity")
    if payload.get("condition_json") is not None:
        obj.condition_json = payload.get("condition_json")
    if payload.get("channels_json") is not None:
        obj.channels_json = payload.get("channels_json")
    if payload.get("is_enabled") is not None:
        obj.is_enabled = bool(payload.get("is_enabled"))

    await db.commit()
    await db.refresh(obj)
    if audit:
        await log_audit(
            db,
            actor_user_id=audit.get("actor_user_id"),
            action=audit_action or "alert_rule_update",
            target_type="alert_rule",
            target_id=str(obj.id),
            diff_json={"name": obj.name, "severity": obj.severity, "is_enabled": obj.is_enabled},
            ip=audit.get("ip"),
            severity=audit.get("severity", "info"),
        )
    return {"id": obj.id, "name": obj.name}


def _build_org_tree(units: List[models.OrgUnit]) -> List[Dict[str, Any]]:
    nodes: Dict[int, Dict[str, Any]] = {}
    for unit in units:
        nodes[unit.id] = {
            "id": unit.id,
            "name": unit.name,
            "parent_id": unit.parent_id,
            "type": unit.type,
            "metadata": unit.metadata_json,
            "children": [],
        }

    roots: List[Dict[str, Any]] = []
    for unit_id, node in nodes.items():
        parent_id = node.get("parent_id")
        if parent_id and parent_id in nodes:
            nodes[parent_id]["children"].append(node)
        else:
            roots.append(node)
    return roots


def _build_user_tree(users: List[User]) -> List[Dict[str, Any]]:
    nodes: Dict[int, Dict[str, Any]] = {}
    for user in users:
        nodes[user.id] = {
            "id": user.id,
            "name": user.full_name or user.email,
            "email": user.email,
            "role": user.role,
            "manager_id": getattr(user, "manager_id", None),
            "is_active": user.is_active,
            "is_banned": getattr(user, "is_banned", False),
            "children": [],
        }

    roots: List[Dict[str, Any]] = []
    for user_id, node in nodes.items():
        manager_id = node.get("manager_id")
        if manager_id and manager_id in nodes:
            nodes[manager_id]["children"].append(node)
        else:
            roots.append(node)
    return roots


def _is_cycle(
    unit_id: int, new_parent_id: Optional[int], parent_map: Dict[int, Optional[int]]
) -> bool:
    if new_parent_id is None:
        return False
    current = new_parent_id
    while current is not None:
        if current == unit_id:
            return True
        current = parent_map.get(current)
    return False

