from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.config import get_db_async
from backend.security.auth import get_current_user
from backend.services.integrations_store import (
    INTEGRATION_TYPES,
    connect_integration,
    disconnect_integration,
    get_integrations,
)

router = APIRouter(prefix="/api/v1/integrations", tags=["integrations"])


@router.get("")
async def list_integrations(db: AsyncSession = Depends(get_db_async)) -> Dict[str, Any]:
    return await get_integrations(db)


@router.post("/{integration_type}/connect")
async def connect_integration_endpoint(
    integration_type: str,
    payload: Dict[str, Any],
    db: AsyncSession = Depends(get_db_async),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    if integration_type not in INTEGRATION_TYPES:
        raise HTTPException(status_code=404, detail="Unknown integration type")
    return await connect_integration(
        db,
        integration_type=integration_type,
        credentials=payload,
        updated_by=str(current_user.get("email") or current_user.get("id") or "system"),
    )


@router.post("/{integration_type}/disconnect")
async def disconnect_integration_endpoint(
    integration_type: str,
    db: AsyncSession = Depends(get_db_async),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    if integration_type not in INTEGRATION_TYPES:
        raise HTTPException(status_code=404, detail="Unknown integration type")
    return await disconnect_integration(
        db,
        integration_type=integration_type,
        updated_by=str(current_user.get("email") or current_user.get("id") or "system"),
    )
