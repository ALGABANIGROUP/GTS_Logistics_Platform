# backend/routes/admin_users.py
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, Any, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

from backend.database.session import get_async_session
from backend.security.auth import get_current_user
from backend.models.user import User

router = APIRouter(prefix="/api/v1/admin/users", tags=["Admin Users"])


# ==================== Models ====================
class UserUpdate(BaseModel):
    """Model for user update request"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    phone: Optional[str] = None
    tenant_id: Optional[int] = None


class UserResponse(BaseModel):
    """Model for user response"""
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    phone: Optional[str] = None
    created_at: str
    last_login: Optional[str] = None


# ==================== Update Endpoint ====================
@router.patch("/{user_id}", response_model=UserResponse)
@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_async_session),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update a user by ID (admin only)
    
    - **user_id**: ID of the user to update
    - **user_update**: Fields to update
    """
    
    # Check admin permissions
    user_role = current_user.get("role", "").lower()
    if user_role not in ["super_admin", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Find the user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    # Update fields
    update_data = user_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        if value is not None:
            setattr(user, field, value)
    
    user.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(user)
    
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        phone=getattr(user, "phone", None),
        created_at=user.created_at.isoformat() if user.created_at else datetime.utcnow().isoformat(),
        last_login=user.last_login.isoformat() if user.last_login else None
    )


# ==================== GET Users Endpoint ====================
@router.get("/management")
async def get_users_management(
    page: int = 1,
    limit: int = 25,
    search: Optional[str] = None,
    role: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_async_session),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get users for management page"""
    
    user_role = current_user.get("role", "").lower()
    if user_role not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    query = select(User)
    
    if search:
        query = query.where(
            (User.email.contains(search)) | 
            (User.full_name.contains(search))
        )
    
    if role and role != "all":
        query = query.where(User.role == role)
    
    if status == "active":
        query = query.where(User.is_active == True)
    elif status == "inactive":
        query = query.where(User.is_active == False)
    
    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar() or 0
    
    query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    users = result.scalars().all()
    
    users_list = []
    for user in users:
        users_list.append({
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None
        })
    
    return {
        "users": users_list,
        "total": total,
        "page": page,
        "limit": limit
    }


@router.get("/{user_id}")
async def get_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get user by ID"""
    
    user_role = current_user.get("role", "").lower()
    if user_role not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    result = await db.execute(select(User).where(User.id == user_id))
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
        "last_login": user.last_login.isoformat() if user.last_login else None
    }


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    permanent: bool = False,
    db: AsyncSession = Depends(get_async_session),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete or deactivate a user"""
    
    user_role = current_user.get("role", "").lower()
    if user_role != "super_admin":
        raise HTTPException(status_code=403, detail="Super admin access required")
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if permanent:
        await db.delete(user)
        message = "User permanently deleted"
    else:
        user.is_active = False
        message = "User deactivated"
    
    await db.commit()
    
    return {"message": message, "user_id": user_id}
