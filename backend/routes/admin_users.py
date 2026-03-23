"""
Admin Users Management API Routes
Manage users, roles, permissions, and access control
"""

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_, func
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, ConfigDict, EmailStr

from backend.security.auth import get_current_user
from backend.security.passwords import hash_password
from backend.security.rbac import has_required_role, normalize_role
from backend.database.session import wrap_session_factory, async_session
from backend.models.user import User
from backend.models.tenant import Tenant
from backend.models.subscription import Role, Bot
from backend.models.bot_os import BotRun
from backend.utils.cache import cached, invalidate_cache_pattern
from backend.services.system_admin_bot import SystemAdminBot
from backend.security.access_context import ROLE_PERMISSIONS

router = APIRouter(prefix="/api/v1/admin/users", tags=["Admin Users"])


async def check_admin_access(user: Dict[str, Any]):
    """Check if user has admin access (admin or super_admin role)"""
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    user_role = str(user.get("role") or "").strip().lower()
    normalized_role = normalize_role(user_role)
    
    # Allow admin or super_admin (expanded roles hierarchy includes both)
    if not has_required_role(user_role, ["admin"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Forbidden: role '{normalized_role}' does not have admin access"
        )


# ============================================================================
# Pydantic Models
# ============================================================================

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    role: Optional[str] = None
    role_key: Optional[str] = None
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: Optional[datetime] = None
    tenant_id: Optional[str] = None
    assigned_bots: Optional[List[str]] = None
    features: Optional[List[str]] = None

    model_config = ConfigDict(from_attributes=True)


class RoleResponse(BaseModel):
    key: str
    name: Optional[str] = None
    name_ar: str
    name_en: str
    permissions: List[str] = []
    is_system: bool

    model_config = ConfigDict(from_attributes=True)


class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    role_key: Optional[str] = None
    is_active: Optional[bool] = None
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    phone_number: Optional[str] = None
    company: Optional[str] = None
    country: Optional[str] = None
    user_type: Optional[str] = None
    is_banned: Optional[bool] = None
    ban_reason: Optional[str] = None
    banned_until: Optional[datetime] = None
    manager_id: Optional[int] = None
    password: Optional[str] = None
    assigned_bots: Optional[List[str]] = None
    features: Optional[List[str]] = None


class RoleCreateRequest(BaseModel):
    key: str
    name_en: str
    name_ar: Optional[str] = None
    permissions: List[str] = []
    is_system: Optional[bool] = False


class RoleUpdateRequest(BaseModel):
    name_en: Optional[str] = None
    name_ar: Optional[str] = None
    permissions: Optional[List[str]] = None
    is_system: Optional[bool] = None


class UserCreateRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: Optional[str] = None
    username: Optional[str] = None
    phone_number: Optional[str] = None
    company: Optional[str] = None
    country: Optional[str] = None
    user_type: Optional[str] = None
    manager_id: Optional[int] = None
    is_active: Optional[bool] = True
    is_banned: Optional[bool] = False
    ban_reason: Optional[str] = None
    banned_until: Optional[datetime] = None
    assigned_bots: Optional[List[str]] = None
    features: Optional[List[str]] = None


# ============================================================================
# Dependencies
# ============================================================================

async def get_admin_session():
    """Get database session for admin operations"""
    async with wrap_session_factory(async_session) as session:
        yield session


# ============================================================================
# Endpoints - User Management
# ============================================================================

@router.post("", response_model=UserResponse, summary="Create user")
async def create_user(
    payload: UserCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_admin_session),
):
    """Create a new user (admin only)"""
    await check_admin_access(current_user)
    bot = SystemAdminBot(session)
    success, user, message = await bot.create_user(
        payload.model_dump(),
        created_by=current_user.get("id"),
    )
    if not success or user is None:
        raise HTTPException(status_code=409, detail=message)
    try:
        from backend.services.platform_webhook_dispatcher import dispatch_from_platform_settings

        await dispatch_from_platform_settings(
            db=session,
            event_type="user.created",
            data={
                "user_id": user.id,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active,
            },
        )
    except Exception:
        pass
    return user

@router.get("", response_model=List[UserResponse], summary="List all users")
async def list_users(
    current_user: Dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_admin_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    tenant_id: Optional[str] = None,
    is_active: Optional[bool] = None,
):
    """
    List all users (admin only)
    
    - **skip**: Number of records to skip
    - **limit**: Number of records to return
    - **tenant_id**: Filter by tenant
    - **is_active**: Filter by active status
    """
    await check_admin_access(current_user)
    bot = SystemAdminBot(session)
    users = await bot.list_users(
        filters={
            "tenant_id": tenant_id,
            "is_active": is_active,
        },
        limit=limit,
        offset=skip,
    )
    return users


# ---- Compatibility routes for frontend ----
@router.get("/management", summary="List users (compat)")
async def list_users_management(
    current_user: Dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_admin_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    tenant_id: Optional[str] = None,
    is_active: Optional[bool] = None,
):
    await check_admin_access(current_user)
    bot = SystemAdminBot(session)
    users = await bot.list_users(
        filters={
            "tenant_id": tenant_id,
            "is_active": is_active,
        },
        limit=limit,
        offset=skip,
    )
    
    # Convert users to dict, handling datetime serialization
    users_list = []
    for user in users:
        user_dict = {
            "id": str(user.id) if hasattr(user, 'id') else None,
            "email": user.email,
            "full_name": user.full_name or "",
            "role": user.role or "user",
            "assigned_bots": list(getattr(user, "assigned_bots", None) or []),
            "features": list(getattr(user, "features", None) or []),
            "is_active": user.is_active if hasattr(user, 'is_active') else True,
            "last_login": user.last_login.isoformat() if hasattr(user, 'last_login') and user.last_login else None,
            "created_at": user.created_at.isoformat() if hasattr(user, 'created_at') and user.created_at else None,
            "tenant_id": user.tenant_id if hasattr(user, 'tenant_id') else None,
        }
        users_list.append(user_dict)
    
    return {"users": users_list}


@router.get("/bots/catalog", summary="List bot catalog for RBAC assignment")
async def list_bot_catalog(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    await check_admin_access(current_user)
    from backend.ai.roles.bot_permissions import BOT_CAPABILITIES, BOT_POLICIES

    bots = []
    feature_set = set()
    for bot_key, meta in BOT_CAPABILITIES.items():
        policy = BOT_POLICIES.get(bot_key)
        required_features = sorted(list(getattr(policy, "required_features", set()) or set()))
        feature_set.update(required_features)
        bots.append(
            {
                "key": bot_key,
                "name": meta.get("name", bot_key),
                "category": meta.get("category", ""),
                "icon": meta.get("icon", ""),
                "required_features": required_features,
            }
        )

    bots.sort(key=lambda item: (item["category"], item["name"]))
    return {
        "bots": bots,
        "features": sorted(feature_set),
        "count": len(bots),
    }


@router.get("/roles/test-raw", summary="Test roles without auth")
async def test_roles_raw(session: AsyncSession = Depends(get_admin_session)):
    """Test endpoint to check if roles can be queried"""
    try:
        from sqlalchemy import text
        result = await session.execute(text("SELECT key, name_en, name_ar, permissions, is_system FROM roles LIMIT 5"))
        rows = result.all()
        return {
            "status": "success",
            "count": len(rows),
            "roles": [
                {
                    "key": r[0],
                    "name_en": r[1],
                    "name_ar": r[2],
                    "permissions": r[3],
                    "is_system": r[4]
                }
                for r in rows
            ]
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "message": str(e),
            "type": type(e).__name__
        }


@router.get("/health-test", summary="Simple health test")
def health_test():
    """Simple endpoint with no dependencies"""
    return {"status": "ok", "message": "Admin users router is working"}


@router.get("/roles/public", summary="List roles (public, no auth)")
async def list_roles_public():
    """List public role metadata for login, registration, and admin UI bootstrap."""
    try:
        from sqlalchemy import text

        async with wrap_session_factory(async_session) as session:
            result = await session.execute(
                text("SELECT key, name, name_en, name_ar, permissions, is_system FROM roles ORDER BY key")
            )
            rows = result.all()

        roles = [
            {
                "key": r[0],
                "name": r[1],
                "name_en": r[2] or r[1] or r[0].replace("_", " ").title(),
                "name_ar": r[3] or r[2] or r[1] or r[0].replace("_", " ").title(),
                "permissions": r[4] or [],
                "is_system": bool(r[5]),
            }
            for r in rows
        ]
        return {"status": "ok", "roles": roles, "count": len(roles)}
    except Exception:
        role_labels = {
            "guest": "Guest",
            "user": "User",
            "subscription_user": "Subscription User",
            "partner": "Partner",
            "support": "Support",
            "finance": "Finance",
            "driver": "Driver",
            "dispatcher": "Dispatcher",
            "ops": "Operations",
            "manager": "Manager",
            "admin": "Admin",
            "system_admin": "System Admin",
            "super_admin": "Super Admin",
            "owner": "Owner",
        }
        roles = [
            {
                "key": key,
                "name": role_labels.get(key, key.replace("_", " ").title()),
                "name_en": role_labels.get(key, key.replace("_", " ").title()),
                "name_ar": role_labels.get(key, key.replace("_", " ").title()),
                "permissions": sorted(list(permissions)),
                "is_system": key in {"admin", "system_admin", "super_admin", "owner"},
            }
            for key, permissions in sorted(ROLE_PERMISSIONS.items(), key=lambda item: item[0])
        ]
        return {
            "status": "ok",
            "roles": roles,
            "count": len(roles),
            "warning": "Database role catalog unavailable; using RBAC fallback.",
        }


@router.get("/roles/db-test", summary="Test database connection")
async def test_db_connection(session: AsyncSession = Depends(get_admin_session)):
    """Test if we can connect to database"""
    try:
        from sqlalchemy import text
        result = await session.execute(text("SELECT 1"))
        return {"status": "ok", "db_connection": "working"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/roles", summary="List roles (compat)")
async def list_roles_compat():
    """List all roles - with fallback if auth fails"""
    try:
        # Use raw SQL to avoid ORM issues
        from sqlalchemy import text
        async with wrap_session_factory(async_session) as session:
            result = await session.execute(
                text("SELECT key, name, name_en, name_ar, permissions, is_system FROM roles ORDER BY key")
            )
            rows = result.all()
        return {
            "roles": [
                {
                    "key": r[0],
                    "name": r[1],
                    "name_en": r[2],
                    "name_ar": r[3],
                    "permissions": r[4] or [],
                    "is_system": bool(r[5]),
                }
                for r in rows
            ],
            "status": "ok"
        }
    except Exception as e:
        import traceback
        print(f"ERROR in list_roles_compat: {e}")
        traceback.print_exc()
        # Return fallback default roles instead of crashing
        return {
            "roles": [
                {"key": "admin", "name": "Admin", "name_en": "Administrator", "name_ar": "Administrator", "permissions": [], "is_system": True},
                {"key": "user", "name": "User", "name_en": "User", "name_ar": "User", "permissions": [], "is_system": False},
            ],
            "status": "ok",
            "warning": f"Using default roles due to: {str(e) [:50]}"
        }


@router.get("/org/tree", summary="Organization tree (compat)")
async def org_tree_compat(
    current_user: Dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_admin_session),
):
    await check_admin_access(current_user)
    return {"tree": []}


@router.get("/{user_id}", response_model=UserResponse, summary="Get user details")
@cached(ttl=300, key_prefix="admin:user")  # Cache for 5 minutes
async def get_user(
    user_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_admin_session),
):
    """Get detailed information about a specific user (cached)"""
    await check_admin_access(current_user)
    bot = SystemAdminBot(session)
    user = await bot.get_user(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@router.patch("/{user_id}", response_model=UserResponse, summary="Update user")
async def update_user(
    user_id: int,
    update_data: UserUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_admin_session),
):
    """Update user information (admin only)"""
    await check_admin_access(current_user)
    current = await session.get(User, user_id)
    if not current:
        raise HTTPException(status_code=404, detail="User not found")
    old_role = current.role
    bot = SystemAdminBot(session)
    success, user, message = await bot.update_user(
        user_id,
        update_data.model_dump(exclude_unset=True),
        updated_by=current_user.get("id"),
    )
    if not success or user is None:
        raise HTTPException(status_code=404, detail=message)
    try:
        from backend.services.platform_webhook_dispatcher import dispatch_from_platform_settings

        await dispatch_from_platform_settings(
            db=session,
            event_type="user.updated",
            data={
                "user_id": user.id,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active,
            },
        )
        if old_role != user.role:
            await dispatch_from_platform_settings(
                db=session,
                event_type="user.role.updated",
                data={
                    "user_id": user.id,
                    "email": user.email,
                    "old_role": old_role,
                    "new_role": user.role,
                },
            )
    except Exception:
        pass
    
    return user


@router.put("/{user_id}", response_model=UserResponse, summary="Update user (full)")
async def update_user_full(
    user_id: int,
    update_data: UserUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_admin_session),
):
    """Full update user information (admin only)"""
    await check_admin_access(current_user)
    return await update_user(user_id=user_id, update_data=update_data, current_user=current_user, session=session)


@router.delete("/{user_id}", status_code=204, summary="Deactivate user")
async def deactivate_user(
    user_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_admin_session),
):
    """Deactivate a user (soft delete)"""
    await check_admin_access(current_user)
    bot = SystemAdminBot(session)
    success, message = await bot.delete_user(user_id, deleted_by=current_user.get("id"))
    if not success:
        raise HTTPException(status_code=404, detail=message)
    return None


@router.post("/{user_id}/toggle-status", summary="Toggle user status immediately")
async def toggle_user_status(
    user_id: int,
    activate: bool = Query(...),
    current_user: Dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_admin_session),
):
    await check_admin_access(current_user)
    bot = SystemAdminBot(session)
    success, user, message = await bot.toggle_user_status(
        user_id,
        activate,
        updated_by=current_user.get("id"),
    )
    if not success:
        raise HTTPException(status_code=404, detail=message)
    return {
        "ok": True,
        "message": message,
        "managed_by": bot.bot_name,
        "user_id": user.id if user else user_id,
        "is_active": user.is_active if user else activate,
    }


# ============================================================================
# Endpoints - Role Management
# ============================================================================

@router.get("/roles/list", response_model=List[RoleResponse], summary="List all roles")
async def list_roles(
    current_user: Dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_admin_session),
):
    """List all available roles"""
    await check_admin_access(current_user)

    stmt = select(
        Role.key,
        Role.name,
        Role.name_ar,
        Role.name_en,
        Role.permissions,
        Role.is_system
    )
    result = await session.execute(stmt)
    roles_data = result.all()
    
    # Convert to RoleResponse format
    return [
        RoleResponse(
            key=r.key,
            name=r.name,
            name_ar=r.name_ar,
            name_en=r.name_en,
            permissions=r.permissions or [],
            is_system=bool(r.is_system)
        )
        for r in roles_data
    ]


@router.get("/roles/{role_key}", response_model=RoleResponse, summary="Get role details")
async def get_role(
    role_key: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_admin_session),
):
    """Get detailed information about a specific role"""
    await check_admin_access(current_user)

    stmt = select(
        Role.key,
        Role.name,
        Role.name_ar,
        Role.name_en,
        Role.permissions,
        Role.is_system
    ).where(Role.key == role_key)
    result = await session.execute(stmt)
    role_data = result.first()
    
    if not role_data:
        raise HTTPException(status_code=404, detail="Role not found")
    
    return RoleResponse(
        key=role_data.key,
        name=role_data.name,
        name_ar=role_data.name_ar,
        name_en=role_data.name_en,
        permissions=role_data.permissions or [],
        is_system=bool(role_data.is_system)
    )
    
    return role


@router.post("/roles", response_model=RoleResponse, summary="Create role")
async def create_role(
    payload: RoleCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_admin_session),
):
    """Create a new role (admin only)"""
    await check_admin_access(current_user)

    existing = (await session.execute(select(Role).where(Role.key == payload.key))).scalars().first()
    if existing:
        raise HTTPException(status_code=409, detail="Role already exists")

    role = Role(
        key=payload.key.strip().lower(),
        name=payload.name_en,
        name_en=payload.name_en,
        name_ar=payload.name_ar or payload.name_en,
        permissions=payload.permissions or [],
        is_system=bool(payload.is_system),
    )

    session.add(role)
    await session.commit()
    await session.refresh(role)
    return role


@router.put("/roles/{role_key}", response_model=RoleResponse, summary="Update role")
async def update_role(
    role_key: str,
    payload: RoleUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_admin_session),
):
    """Update an existing role (admin only)"""
    await check_admin_access(current_user)

    role = (await session.execute(select(Role).where(Role.key == role_key))).scalars().first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    if payload.name_en is not None:
        role.name_en = payload.name_en
        role.name = payload.name_en
    if payload.name_ar is not None:
        role.name_ar = payload.name_ar
    if payload.permissions is not None:
        role.permissions = payload.permissions
    if payload.is_system is not None:
        role.is_system = bool(payload.is_system)

    session.add(role)
    await session.commit()
    await session.refresh(role)
    return role


@router.delete("/roles/{role_key}", status_code=204, summary="Delete role")
async def delete_role(
    role_key: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_admin_session),
):
    """Delete a role (admin only)"""
    await check_admin_access(current_user)

    role = (await session.execute(select(Role).where(Role.key == role_key))).scalars().first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    if role.is_system:
        raise HTTPException(status_code=400, detail="System roles cannot be deleted")

    await session.delete(role)
    await session.commit()
    return None


# ============================================================================
# Endpoints - User Statistics
# ============================================================================

@router.get("/stats/summary", summary="Get user statistics summary")
async def get_user_stats(
    current_user: Dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_admin_session),
):
    """Get summary statistics about users"""
    await check_admin_access(current_user)
    bot = SystemAdminBot(session)
    stats = await bot.get_user_stats()
    stmt = select(User.role, func.count(User.id)).group_by(User.role)
    result = await session.execute(stmt)
    users_by_role = {str(role or "user"): int(count or 0) for role, count in result.all()}
    return {
        "total_users": stats["total"],
        "active_users": stats["active"],
        "inactive_users": stats["inactive"],
        "users_by_role": users_by_role,
        "managed_by": stats["managed_by"],
        "last_updated": stats["last_updated"],
    }


@router.get("/stats", summary="Get user statistics summary (flat)")
async def get_user_stats_flat(
    current_user: Dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_admin_session),
):
    await check_admin_access(current_user)
    bot = SystemAdminBot(session)
    return await bot.get_user_stats()


@router.get("/activity/recent", summary="Get recent user activity")
async def get_recent_activity(
    current_user: Dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_admin_session),
    limit: int = Query(20, ge=1, le=100),
):
    """Get recent user login activity"""
    await check_admin_access(current_user)

    stmt = select(User).where(User.last_login.isnot(None))
    stmt = stmt.order_by(User.last_login.desc()).limit(limit)
    result = await session.execute(stmt)
    users = result.scalars().all()
    
    return [
        {
            "user_id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "last_login": u.last_login,
        }
        for u in users
    ]


# ============================================================================
# Endpoints - Bulk Operations
# ============================================================================

@router.post("/bulk/activate", summary="Activate multiple users")
async def bulk_activate(
    user_ids: List[str] = Body(...),
    current_user: Dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_admin_session),
):
    """Activate multiple users at once"""
    await check_admin_access(current_user)

    stmt = select(User).where(User.id.in_(user_ids))
    result = await session.execute(stmt)
    users = result.scalars().all()
    
    for user in users:
        user.is_active = True
    
    session.add_all(users)
    await session.commit()
    
    return {"updated": len(users)}


@router.post("/bulk/deactivate", summary="Deactivate multiple users")
async def bulk_deactivate(
    user_ids: List[str] = Body(...),
    current_user: Dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_admin_session),
):
    """Deactivate multiple users at once"""
    await check_admin_access(current_user)

    stmt = select(User).where(User.id.in_(user_ids))
    result = await session.execute(stmt)
    users = result.scalars().all()
    
    for user in users:
        user.is_active = False
    
    session.add_all(users)
    await session.commit()
    
    return {"updated": len(users)}
