from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field


class OrgUnitCreate(BaseModel):
    name: str = Field(..., min_length=1)
    parent_id: Optional[int] = None
    type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class OrgUnitUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class OrgUnitMove(BaseModel):
    parent_id: Optional[int] = None


class RoleCreate(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    priority: Optional[int] = None
    parent_role_id: Optional[int] = None


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    parent_role_id: Optional[int] = None


class PermissionCreate(BaseModel):
    code: str = Field(..., min_length=1)
    description: Optional[str] = None
    scope_type: str = Field(..., min_length=1)
    scope_key: Optional[str] = None


class PermissionTemplateCreate(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    permission_ids: List[int] = Field(default_factory=list)


class PermissionTemplateApply(BaseModel):
    role_id: int


class UserCreatePayload(BaseModel):
    email: EmailStr
    password: Optional[str] = Field(default=None, min_length=8)
    full_name: Optional[str] = None
    username: Optional[str] = None
    role: Optional[str] = None
    company: Optional[str] = None
    country: Optional[str] = None
    user_type: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: Optional[bool] = True
    manager_id: Optional[int] = None


class UserUpdatePayload(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(default=None, min_length=8)
    full_name: Optional[str] = None
    username: Optional[str] = None
    role: Optional[str] = None
    company: Optional[str] = None
    country: Optional[str] = None
    user_type: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: Optional[bool] = None
    manager_id: Optional[int] = None


class UserRoleUpdatePayload(BaseModel):
    role: str = Field(..., min_length=1)


class UserBanPayload(BaseModel):
    reason: Optional[str] = None
    banned_until: Optional[datetime] = None


class UserRoleAssignPayload(BaseModel):
    role_id: int
    org_unit_id: Optional[int] = None
    expires_at: Optional[datetime] = None


class SessionRevokePayload(BaseModel):
    reason: Optional[str] = None


class AuditSearchQuery(BaseModel):
    actor_user_id: Optional[int] = None
    action: Optional[str] = None
    target_type: Optional[str] = None
    severity: Optional[str] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None


class AlertRuleCreate(BaseModel):
    name: str = Field(..., min_length=1)
    severity: Optional[str] = None
    condition_json: Optional[Dict[str, Any]] = None
    channels_json: Optional[Dict[str, Any]] = None
    is_enabled: Optional[bool] = True


class AlertRuleUpdate(BaseModel):
    name: Optional[str] = None
    severity: Optional[str] = None
    condition_json: Optional[Dict[str, Any]] = None
    channels_json: Optional[Dict[str, Any]] = None
    is_enabled: Optional[bool] = None
