# backend/routes/system_admin_bot.py
from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from pydantic import BaseModel, Field, EmailStr

from backend.database.session import get_async_session
from backend.security.auth import get_current_user
from backend.models.user import User
from backend.models.tenant import Tenant

router = APIRouter(tags=["System Admin Bot"])
logger = logging.getLogger(__name__)


# ==================== Pydantic Models ====================
class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    role: str = Field(default="user", description="user, manager, admin, super_admin")
    is_active: bool = True
    phone: Optional[str] = None
    tenant_id: Optional[int] = None


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    phone: Optional[str] = None
    tenant_id: Optional[int] = None


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    phone: Optional[str]
    created_at: str
    last_login: Optional[str]
    tenant_name: Optional[str]


# ==================== Mock Database (للتطوير - استبدل بقاعدة بيانات حقيقية) ====================
MOCK_USERS = [
    {
        "id": 1,
        "email": "superadmin@gts.com",
        "full_name": "Super Administrator",
        "role": "super_admin",
        "is_active": True,
        "phone": "+1-800-555-0001",
        "created_at": "2024-01-01T00:00:00",
        "last_login": "2026-04-05T10:30:00",
        "tenant_id": 1,
        "tenant_name": "GTS Logistics"
    },
    {
        "id": 2,
        "email": "admin@gts.com",
        "full_name": "System Administrator",
        "role": "admin",
        "is_active": True,
        "phone": "+1-800-555-0002",
        "created_at": "2024-01-02T00:00:00",
        "last_login": "2026-04-05T09:15:00",
        "tenant_id": 1,
        "tenant_name": "GTS Logistics"
    },
    {
        "id": 3,
        "email": "manager@gts.com",
        "full_name": "Operations Manager",
        "role": "manager",
        "is_active": True,
        "phone": "+1-800-555-0003",
        "created_at": "2024-01-03T00:00:00",
        "last_login": "2026-04-04T14:20:00",
        "tenant_id": 1,
        "tenant_name": "GTS Logistics"
    },
    {
        "id": 4,
        "email": "dispatcher@gts.com",
        "full_name": "Dispatcher",
        "role": "dispatcher",
        "is_active": True,
        "phone": "+1-800-555-0004",
        "created_at": "2024-01-04T00:00:00",
        "last_login": "2026-04-04T08:00:00",
        "tenant_id": 1,
        "tenant_name": "GTS Logistics"
    },
    {
        "id": 5,
        "email": "carrier@fastfreight.com",
        "full_name": "Fast Freight Carrier",
        "role": "carrier",
        "is_active": True,
        "phone": "+1-800-555-0005",
        "created_at": "2024-01-05T00:00:00",
        "last_login": "2026-04-03T16:45:00",
        "tenant_id": 2,
        "tenant_name": "Fast Freight Inc."
    },
    {
        "id": 6,
        "email": "shipper@abcmfg.com",
        "full_name": "ABC Manufacturing",
        "role": "shipper",
        "is_active": True,
        "phone": "+1-800-555-0006",
        "created_at": "2024-01-06T00:00:00",
        "last_login": "2026-04-03T11:30:00",
        "tenant_id": 3,
        "tenant_name": "ABC Manufacturing"
    },
    {
        "id": 7,
        "email": "inactive@example.com",
        "full_name": "Inactive User",
        "role": "user",
        "is_active": False,
        "phone": "+1-800-555-0007",
        "created_at": "2024-01-07T00:00:00",
        "last_login": "2025-12-01T10:00:00",
        "tenant_id": 1,
        "tenant_name": "GTS Logistics"
    }
]

MOCK_TENANTS = [
    {"id": 1, "name": "GTS Logistics", "domain": "gtsdispatcher.com", "is_active": True},
    {"id": 2, "name": "Fast Freight Inc.", "domain": "fastfreight.com", "is_active": True},
    {"id": 3, "name": "ABC Manufacturing", "domain": "abcmfg.com", "is_active": True},
]


# ==================== System Metrics ====================
SYSTEM_METRICS = {
    "total_users": len([u for u in MOCK_USERS if u["is_active"]]),
    "total_tenants": len(MOCK_TENANTS),
    "active_sessions": 42,
    "api_requests_today": 15234,
    "avg_response_time": 234,
    "error_rate": 0.28,
    "cpu_usage": 45,
    "memory_usage": 62,
    "disk_usage": 58,
    "uptime_days": 45,
    "last_backup": (datetime.now() - timedelta(hours=12)).isoformat(),
    "pending_updates": 3
}


# ==================== API Endpoints ====================

@router.get("/users")
async def get_all_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    role: Optional[str] = None,
    status: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get all users with pagination and filtering"""

    # التحقق من صلاحيات super_admin
    user_role = current_user.get("role", "").lower()
    if user_role not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")

    users = MOCK_USERS.copy()

    # تطبيق الفلاتر
    if search:
        search_lower = search.lower()
        users = [
            u for u in users
            if search_lower in u["email"].lower()
            or search_lower in u["full_name"].lower()
            or (u.get("phone") and search_lower in u["phone"].lower())
        ]

    if role and role != "all":
        users = [u for u in users if u["role"] == role]

    if status == "active":
        users = [u for u in users if u["is_active"]]
    elif status == "inactive":
        users = [u for u in users if not u["is_active"]]

    # Pagination
    total = len(users)
    start = (page - 1) * limit
    end = start + limit
    users = users[start:end]

    return {
        "users": users,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit if total else 0
    }


@router.get("/users/{user_id}")
async def get_user_by_id(
    user_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get single user by ID"""

    user_role = current_user.get("role", "").lower()
    if user_role not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")

    user = next((u for u in MOCK_USERS if u["id"] == user_id), None)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.post("/users")
async def create_user(
    user_data: UserCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new user"""

    user_role = current_user.get("role", "").lower()
    if user_role not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")

    # التحقق من وجود البريد
    existing = next((u for u in MOCK_USERS if u["email"] == user_data.email), None)
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    new_id = max([u["id"] for u in MOCK_USERS]) + 1 if MOCK_USERS else 1

    new_user = {
        "id": new_id,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "role": user_data.role,
        "is_active": user_data.is_active,
        "phone": user_data.phone,
        "created_at": datetime.now().isoformat(),
        "last_login": None,
        "tenant_id": user_data.tenant_id,
        "tenant_name": next((t["name"] for t in MOCK_TENANTS if t["id"] == user_data.tenant_id), None)
    }

    MOCK_USERS.append(new_user)
    logger.info(f"User created: {user_data.email} by {current_user.get('email')}")

    return new_user


@router.patch("/users/{user_id}")
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update a user"""

    user_role = current_user.get("role", "").lower()
    if user_role not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")

    user = next((u for u in MOCK_USERS if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            user[key] = value

    if "tenant_id" in update_data:
        user["tenant_name"] = next((t["name"] for t in MOCK_TENANTS if t["id"] == user["tenant_id"]), None)

    logger.info(f"User updated: {user['email']} by {current_user.get('email')}")

    return user


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    permanent: bool = False,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete or deactivate a user"""

    user_role = current_user.get("role", "").lower()
    if user_role != "super_admin":
        raise HTTPException(status_code=403, detail="Super admin access required")

    user = next((u for u in MOCK_USERS if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if permanent:
        MOCK_USERS.remove(user)
        message = "User permanently deleted"
    else:
        user["is_active"] = False
        message = "User deactivated"

    logger.info(f"User {message}: {user['email']} by {current_user.get('email')}")

    return {"message": message, "user_id": user_id}


@router.get("/metrics/system")
async def get_system_metrics(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get system metrics and performance data"""

    user_role = current_user.get("role", "").lower()
    if user_role not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")

    return SYSTEM_METRICS


@router.get("/metrics/users")
async def get_user_metrics(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get user-related metrics"""

    user_role = current_user.get("role", "").lower()
    if user_role not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")

    total = len(MOCK_USERS)
    active = len([u for u in MOCK_USERS if u["is_active"]])
    inactive = total - active

    by_role = {}
    for user in MOCK_USERS:
        role = user["role"]
        by_role[role] = by_role.get(role, 0) + 1

    return {
        "total": total,
        "active": active,
        "inactive": inactive,
        "by_role": by_role,
        "new_this_month": len([u for u in MOCK_USERS if u["created_at"].startswith("2026-04")]),
        "last_week_active": len([u for u in MOCK_USERS if u.get("last_login") and "2026-04" in u["last_login"]])
    }


@router.get("/tenants")
async def get_tenants(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get all tenants"""

    user_role = current_user.get("role", "").lower()
    if user_role not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")

    return {"tenants": MOCK_TENANTS, "total": len(MOCK_TENANTS)}


@router.get("/dashboard")
async def get_admin_dashboard(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get complete admin dashboard data"""

    user_role = current_user.get("role", "").lower()
    if user_role not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")

    return {
        "users": MOCK_USERS[:10],
        "tenants": MOCK_TENANTS,
        "metrics": SYSTEM_METRICS,
        "user_metrics": {
            "total": len(MOCK_USERS),
            "active": len([u for u in MOCK_USERS if u["is_active"]]),
            "by_role": {
                "super_admin": len([u for u in MOCK_USERS if u["role"] == "super_admin"]),
                "admin": len([u for u in MOCK_USERS if u["role"] == "admin"]),
                "manager": len([u for u in MOCK_USERS if u["role"] == "manager"]),
                "user": len([u for u in MOCK_USERS if u["role"] == "user"])
            }
        }
    }


@router.get("/audit/recent")
async def get_recent_audit_logs(
    limit: int = 50,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get recent audit logs"""

    user_role = current_user.get("role", "").lower()
    if user_role not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")

    # بيانات تجريبية لسجل التدقيق
    audit_logs = [
        {"id": 1, "action": "USER_LOGIN", "user": "admin@gts.com", "timestamp": datetime.now().isoformat(), "status": "success"},
        {"id": 2, "action": "USER_CREATE", "user": "superadmin@gts.com", "timestamp": (datetime.now() - timedelta(hours=1)).isoformat(), "status": "success"},
        {"id": 3, "action": "ROLE_CHANGE", "user": "admin@gts.com", "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(), "status": "success"},
        {"id": 4, "action": "USER_DELETE", "user": "superadmin@gts.com", "timestamp": (datetime.now() - timedelta(hours=3)).isoformat(), "status": "success"},
        {"id": 5, "action": "LOGIN_FAILED", "user": "unknown", "timestamp": (datetime.now() - timedelta(hours=4)).isoformat(), "status": "failed"}
    ]

    return {"logs": audit_logs[:limit], "total": len(audit_logs)}