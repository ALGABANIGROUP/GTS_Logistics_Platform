# backend/routes/admin_users.py
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from backend.database.session import get_async_session
from backend.security.auth import require_roles, get_current_user
from backend.models.user import User

router = APIRouter(tags=["Admin Users"])
logger = logging.getLogger(__name__)

# Create require_auth for admin access
require_auth = require_roles(["admin", "super_admin"])


@router.get("/management")
async def get_users_management(
    page: int = 1,
    limit: int = 25,
    search: Optional[str] = None,
    role: Optional[str] = None,
    status: Optional[str] = None,
    session: AsyncSession = Depends(get_async_session),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get all users from database for management page
    """
    
    # التحقق من صلاحيات admin
    user_role = current_user.get("role", "").lower()
    if user_role not in ["super_admin", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        # استعلام أساسي
        query = select(User)
        
        # تطبيق البحث
        if search:
            query = query.where(
                (User.email.contains(search)) |
                (User.full_name.contains(search))
            )
        
        # تطبيق فلتر الدور
        if role and role != "all":
            query = query.where(User.role == role)
        
        # تطبيق فلتر الحالة
        if status and status != "all":
            is_active = status == "active"
            query = query.where(User.is_active == is_active)
        
        # حساب العدد الإجمالي
        count_query = select(func.count()).select_from(query.subquery())
        total = await session.scalar(count_query)
        
        # تطبيق pagination
        query = query.offset((page - 1) * limit).limit(limit)
        
        # تنفيذ الاستعلام
        result = await session.execute(query)
        users = result.scalars().all()
        
        # تنسيق البيانات
        users_list = []
        for user in users:
            users_list.append({
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name or user.email.split('@')[0],
                "role": user.role,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else datetime.now().isoformat(),
                "last_login": None  # Not implemented yet
            })
        
        logger.info(f"Returning {len(users_list)} users")
        logger.info(f"Returning {len(users_list)} users")
        return {
            "users": users_list,
            "total": total or 0,
            "page": page,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch users: {e}")
        return {
            "users": [],
            "total": 0,
            "page": page,
            "limit": limit,
            "error": str(e)
        }


@router.get("/stats")
async def get_users_stats(
    session: AsyncSession = Depends(get_async_session),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get user statistics"""
    
    try:
        # إجمالي المستخدمين
        total_result = await session.execute(select(func.count()).select_from(User))
        total = total_result.scalar() or 0
        
        # المستخدمين النشطين
        active_result = await session.execute(
            select(func.count()).where(User.is_active == True)
        )
        active = active_result.scalar() or 0
        
        # المستخدمين المعطلين
        inactive = total - active
        
        return {
            "total": total,
            "active": active,
            "inactive": inactive
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch user stats: {e}")
        return {
            "total": 0,
            "active": 0,
            "inactive": 0
        }


@router.get("/activity/recent")
async def get_recent_activity(
    limit: int = 10,
    session: AsyncSession = Depends(get_async_session),
    payload: Dict[str, Any] = Depends(require_auth)
):
    """Get recent user login activity"""
    
    user_role = payload.get("role", "").lower()
    if user_role not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # جلب المستخدمين الذين سجلوا دخول مؤخراً
        query = select(User).where(
            User.last_login.isnot(None)
        ).order_by(User.last_login.desc()).limit(limit)
        
        result = await session.execute(query)
        users = result.scalars().all()
        
        activity = []
        for user in users:
            activity.append({
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "is_active": user.is_active
            })
        
        return {"activity": activity}
        
    except Exception as e:
        logger.error(f"Failed to fetch recent activity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.get("/{user_id}")
async def get_user_by_id(
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
    payload: Dict[str, Any] = Depends(require_auth)
):
    """Get single user by ID"""
    
    user_role = payload.get("role", "").lower()
    if user_role not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "phone": getattr(user, "phone", None)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))