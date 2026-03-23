"""
API Connections Management Routes
Super Admin endpoints for managing external platform integrations
"""

from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List, Dict, Any, Optional
from datetime import datetime
import httpx
import logging

from backend.database.config import get_db_async
from backend.models.api_connections import APIConnection, ConnectionType, PlatformCategory
from backend.security.auth import require_roles
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)

router = APIRouter(tags=["admin-api-connections"])


# Pydantic models for request/response
class APIConnectionCreate(BaseModel):
    """Schema for creating new API connection"""
    platform_name: str = Field(..., min_length=1, max_length=255)
    platform_category: str = Field(..., description="Platform category")
    description: Optional[str] = None
    api_url: str = Field(..., min_length=1, max_length=500)
    connection_type: str = Field(..., description="Connection type")
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    oauth_callback_url: Optional[str] = None
    headers: Optional[dict] = None
    query_params: Optional[dict] = None
    extra_config: Optional[dict] = None
    is_active: bool = True


class APIConnectionUpdate(BaseModel):
    """Schema for updating API connection"""
    platform_name: Optional[str] = None
    platform_category: Optional[str] = None
    description: Optional[str] = None
    api_url: Optional[str] = None
    connection_type: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    oauth_callback_url: Optional[str] = None
    headers: Optional[dict] = None
    query_params: Optional[dict] = None
    extra_config: Optional[dict] = None
    is_active: Optional[bool] = None


class ConnectionTestRequest(BaseModel):
    """Schema for testing connection"""
    method: str = Field(default="GET", description="HTTP method")
    test_timeout: int = 10


# ==================== STATIC ROUTES (MUST BE BEFORE /{connection_id}) ====================

@router.get("/categories/list", dependencies=[Depends(require_roles(["super_admin", "admin"]))])
async def list_platform_categories() -> Dict[str, Any]:
    """Get list of available platform categories"""
    return {
        "status": "success",
        "categories": [
            {"value": cat.value, "label": cat.value.replace("_", " ").title()}
            for cat in PlatformCategory
        ]
    }


@router.get("/connection-types/list", dependencies=[Depends(require_roles(["super_admin", "admin"]))])
async def list_connection_types() -> Dict[str, Any]:
    """Get list of available connection types"""
    return {
        "status": "success",
        "connection_types": [
            {"value": ct.value, "label": ct.value.replace("_", " ").upper()}
            for ct in ConnectionType
        ]
    }


@router.get("/stats", dependencies=[Depends(require_roles(["super_admin", "admin"]))])
async def get_api_connections_stats(db: AsyncSession = Depends(get_db_async)) -> Dict[str, Any]:
    """Get API connections statistics"""
    try:
        result = await db.execute(select(APIConnection))
        connections = result.scalars().all()
        
        total = len(connections)
        active = sum(1 for c in connections if c.is_active)
        verified = sum(1 for c in connections if c.is_verified)
        
        by_category = {}
        for conn in connections:
            cat = conn.platform_category.value if conn.platform_category else "other"
            by_category[cat] = by_category.get(cat, 0) + 1
        
        total_requests = sum(c.total_requests for c in connections)
        total_successful = sum(c.successful_requests for c in connections)
        overall_success_rate = (total_successful / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "status": "success",
            "stats": {
                "total_connections": total,
                "active_connections": active,
                "verified_connections": verified,
                "inactive_connections": total - active,
                "connections_by_category": by_category,
                "total_requests": total_requests,
                "successful_requests": total_successful,
                "failed_requests": total_requests - total_successful,
                "overall_success_rate": round(overall_success_rate, 2)
            }
        }
    except Exception as e:
        logger.error(f"Failed to get API connections stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch statistics: {str(e)}"
        )


# ==================== DYNAMIC ROUTES (AFTER STATIC ROUTES) ====================

@router.get("/", dependencies=[Depends(require_roles(["super_admin", "admin"]))])
async def list_api_connections(
    db: AsyncSession = Depends(get_db_async),
    category: Optional[str] = Query(None),
    active_only: bool = Query(False),
    include_secrets: bool = Query(False)
) -> Dict[str, Any]:
    """List all API connections"""
    try:
        query = select(APIConnection)
        
        if category:
            query = query.where(APIConnection.platform_category == PlatformCategory(category))
        
        if active_only:
            query = query.where(APIConnection.is_active == True)
        
        query = query.order_by(APIConnection.created_at.desc())
        
        result = await db.execute(query)
        connections = result.scalars().all()
        
        return {
            "status": "success",
            "total": len(connections),
            "connections": [conn.to_dict(include_secrets=include_secrets) for conn in connections]
        }
    except Exception as e:
        logger.error(f"Failed to list API connections: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch API connections: {str(e)}"
        )


@router.get("/{connection_id}", dependencies=[Depends(require_roles(["super_admin", "admin"]))])
async def get_api_connection(
    connection_id: int,
    db: AsyncSession = Depends(get_db_async)
) -> Dict[str, Any]:
    """Get a specific API connection"""
    try:
        result = await db.execute(
            select(APIConnection).where(APIConnection.id == connection_id)
        )
        connection = result.scalar_one_or_none()
        
        if not connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API connection not found"
            )
        
        return {
            "status": "success",
            "connection": connection.to_dict(include_secrets=True)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get API connection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch API connection: {str(e)}"
        )


@router.post("/", dependencies=[Depends(require_roles(["super_admin"]))])
async def create_api_connection(
    payload: APIConnectionCreate,
    db: AsyncSession = Depends(get_db_async)
) -> Dict[str, Any]:
    """Create a new API connection"""
    try:
        # Validate connection type
        try:
            conn_type = ConnectionType(payload.connection_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid connection type: {payload.connection_type}"
            )
        
        # Validate platform category
        try:
            platform_cat = PlatformCategory(payload.platform_category)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid platform category: {payload.platform_category}"
            )
        
        # Create connection
        new_connection = APIConnection(
            platform_name=payload.platform_name,
            platform_category=platform_cat,
            description=payload.description,
            api_url=payload.api_url,
            connection_type=conn_type,
            api_key=payload.api_key,
            api_secret=payload.api_secret,
            access_token=payload.access_token,
            refresh_token=payload.refresh_token,
            client_id=payload.client_id,
            client_secret=payload.client_secret,
            oauth_callback_url=payload.oauth_callback_url,
            headers=payload.headers or {},
            query_params=payload.query_params or {},
            extra_config=payload.extra_config or {},
            is_active=payload.is_active
        )
        
        db.add(new_connection)
        await db.commit()
        await db.refresh(new_connection)
        
        return {
            "status": "success",
            "message": "API connection created successfully",
            "connection": new_connection.to_dict(include_secrets=True)
        }
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create API connection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create API connection: {str(e)}"
        )


@router.put("/{connection_id}", dependencies=[Depends(require_roles(["super_admin"]))])
async def update_api_connection(
    connection_id: int,
    payload: APIConnectionUpdate,
    db: AsyncSession = Depends(get_db_async)
) -> Dict[str, Any]:
    """Update an API connection"""
    try:
        result = await db.execute(
            select(APIConnection).where(APIConnection.id == connection_id)
        )
        connection = result.scalar_one_or_none()
        
        if not connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API connection not found"
            )
        
        # Update fields
        update_data = payload.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if field == "connection_type" and value:
                try:
                    setattr(connection, field, ConnectionType(value))
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid connection type: {value}"
                    )
            elif field == "platform_category" and value:
                try:
                    setattr(connection, field, PlatformCategory(value))
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid platform category: {value}"
                    )
            elif value is not None:
                setattr(connection, field, value)
        
        connection.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(connection)
        
        return {
            "status": "success",
            "message": "API connection updated successfully",
            "connection": connection.to_dict(include_secrets=True)
        }
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to update API connection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update API connection: {str(e)}"
        )


@router.delete("/{connection_id}", dependencies=[Depends(require_roles(["super_admin"]))])
async def delete_api_connection(
    connection_id: int,
    db: AsyncSession = Depends(get_db_async)
) -> Dict[str, Any]:
    """Delete an API connection"""
    try:
        result = await db.execute(
            select(APIConnection).where(APIConnection.id == connection_id)
        )
        connection = result.scalar_one_or_none()
        
        if not connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API connection not found"
            )
        
        await db.delete(connection)
        await db.commit()
        
        return {
            "status": "success",
            "message": "API connection deleted successfully"
        }
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to delete API connection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete API connection: {str(e)}"
        )


@router.post("/{connection_id}/test", dependencies=[Depends(require_roles(["super_admin", "admin"]))])
async def test_api_connection(
    connection_id: int,
    db: AsyncSession = Depends(get_db_async),
    request: Optional[ConnectionTestRequest] = None
) -> Dict[str, Any]:
    """Test an API connection"""
    try:
        result = await db.execute(
            select(APIConnection).where(APIConnection.id == connection_id)
        )
        connection = result.scalar_one_or_none()
        
        if not connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API connection not found"
            )
        
        method = request.method if request else "GET"
        timeout = request.test_timeout if request else 10
        
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                if connection.connection_type == ConnectionType.API_KEY:
                    headers = {
                        **connection.headers,
                        "X-API-Key": connection.api_key
                    }
                elif connection.connection_type == ConnectionType.BEARER_TOKEN:
                    headers = {
                        **connection.headers,
                        "Authorization": f"Bearer {connection.access_token}"
                    }
                elif connection.connection_type == ConnectionType.BASIC_AUTH:
                    auth = (connection.client_id, connection.api_secret)
                    response = await client.request(method, connection.api_url, auth=auth)
                    http_status = response.status_code
                elif connection.connection_type == ConnectionType.OAUTH2:
                    headers = {
                        **connection.headers,
                        "Authorization": f"Bearer {connection.access_token}"
                    }
                else:
                    headers = connection.headers or {}
                
                if connection.connection_type != ConnectionType.BASIC_AUTH:
                    response = await client.request(method, connection.api_url, headers=headers)
                
                http_status = response.status_code
                
                # Update connection stats
                connection.total_requests += 1
                if http_status < 400:
                    connection.successful_requests += 1
                    connection.is_verified = True
                else:
                    connection.failed_requests += 1
                connection.last_tested_at = datetime.utcnow()
                connection.last_test_status = "success" if http_status < 400 else "failed"
                connection.last_test_message = f"HTTP {http_status}"
                connection.last_used_at = datetime.utcnow()
                
                await db.commit()
                
                return {
                    "status": "success" if http_status < 400 else "failed",
                    "test_result": {
                        "http_status": http_status,
                        "message": f"Connection test completed with HTTP {http_status}",
                        "is_verified": http_status < 400
                    }
                }
        except httpx.TimeoutException:
            connection.failed_requests += 1
            connection.last_tested_at = datetime.utcnow()
            connection.last_test_status = "failed"
            connection.last_test_message = "Timeout"
            await db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="API connection test timed out"
            )
        except Exception as e:
            connection.failed_requests += 1
            connection.last_tested_at = datetime.utcnow()
            connection.last_test_status = "failed"
            connection.last_test_message = str(e)
            await db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to test connection: {str(e)}"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to test API connection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test API connection: {str(e)}"
        )
