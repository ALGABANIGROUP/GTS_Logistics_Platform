"""
Admin Data Sources Routes
Endpoints for managing data sources and integrations
"""

import logging
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi import Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional

from backend.core.db_config import get_async_db
from backend.database.session import get_async_session, wrap_session_factory
from backend.models.user import User
from backend.security.auth import require_roles, get_current_user
from backend.services.data_source_service import get_data_source_service

router = APIRouter(prefix="/api/v1/admin/data-sources", tags=["Admin Data Sources"])
logger = logging.getLogger(__name__)


@router.get("/")
async def list_data_sources(
    session: AsyncSession = Depends(get_async_session),
    current_user: Dict[str, Any] = Depends(require_roles(["admin", "super_admin"]))
):
    """List all configured data sources"""
    service = get_data_source_service(session)
    sources = await service.list_sources()
    return {"success": True, "sources": sources, "count": len(sources)}


@router.get("/{source_id}")
async def get_data_source(
    source_id: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: Dict[str, Any] = Depends(require_roles(["admin", "super_admin"]))
):
    """Get data source details"""
    service = get_data_source_service(session)
    source = await service.get_source(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Data source not found")
    return {"success": True, "source": source}


@router.post("/")
async def create_data_source(
    data: Dict[str, Any],
    session: AsyncSession = Depends(get_async_session),
    current_user: Dict[str, Any] = Depends(require_roles(["admin", "super_admin"]))
):
    """Create a new data source"""
    service = get_data_source_service(session)
    source = await service.create_source(data)
    return {"success": True, "source": source}


@router.put("/{source_id}")
async def update_data_source(
    source_id: str,
    data: Dict[str, Any],
    session: AsyncSession = Depends(get_async_session),
    current_user: Dict[str, Any] = Depends(require_roles(["admin", "super_admin"]))
):
    """Update data source"""
    service = get_data_source_service(session)
    source = await service.update_source(source_id, data)
    if not source:
        raise HTTPException(status_code=404, detail="Data source not found")
    return {"success": True, "source": source}


@router.delete("/{source_id}")
async def delete_data_source(
    source_id: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: Dict[str, Any] = Depends(require_roles(["admin", "super_admin"]))
):
    """Delete data source"""
    service = get_data_source_service(session)
    result = await service.delete_source(source_id)
    if not result:
        raise HTTPException(status_code=404, detail="Data source not found")
    return {"success": True, "message": "Data source deleted"}


@router.post("/{source_id}/test")
async def test_data_source(
    source_id: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: Dict[str, Any] = Depends(require_roles(["admin", "super_admin"]))
):
    """Test data source connection"""
    service = get_data_source_service(session)
    result = await service.test_connection(source_id)
    return {"success": result["success"], "message": result.get("message", "")}


@router.get("/health/check")
async def data_sources_health(
    session: AsyncSession = Depends(get_async_session),
    current_user: Dict[str, Any] = Depends(require_roles(["admin", "super_admin"]))
):
    """Check health of all data sources"""
    service = get_data_source_service(session)
    health = await service.check_health()
    return {"success": True, "health": health}


# ============================================================================
# 1. HEALTH MONITORING - FROM MAINTENANCE DEV BOT
# ============================================================================

@router.get("/health/maintenance-bot")
async def get_health_from_maintenance_bot(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get system health data from maintenance_dev bot
    Used for: Health Monitoring panel
    """
    try:
        # This would connect to the maintenance_dev bot
        # For now, returning structure that maintenance bot would provide
        return {
            "source": "maintenance_dev_bot",
            "timestamp": datetime.utcnow().isoformat(),
            "health_status": "operational",
            "checks": {
                "system_services": {
                    "status": "healthy",
                    "services": [
                        {"name": "FastAPI Server", "status": "running"},
                        {"name": "PostgreSQL", "status": "connected"},
                        {"name": "Redis", "status": "connected"}
                    ]
                },
                "performance": {
                    "cpu_usage": 45,
                    "memory_usage": 62,
                    "disk_usage": 0,
                    "api_response_time_ms": None
                },
                "dependencies": {
                    "database": "unknown",
                    "cache": "unknown",
                    "external_apis": "unknown"
                },
                "scheduled_maintenance": {
                    "last_backup": None,
                    "next_optimization": None,
                    "next_health_check": None
                },
                "message": "Connect real maintenance monitoring system"
            }
        }
    except Exception as e:
        logger.error(f"Error fetching health from maintenance bot: {e}")
        return {
            "source": "maintenance_dev_bot",
            "error": str(e),
            "health_status": "unknown"
        }


@router.get("/health/detailed-maintenance")
async def get_detailed_health_from_maintenance(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get detailed health metrics from maintenance bot
    Includes performance history, trends, and recommendations
    """
    try:
        return {
            "source": "maintenance_dev_bot",
            "timestamp": datetime.utcnow().isoformat(),
            "system_metrics": {
                "uptime": None,
                "restart_count": 0,
                "last_restart": None
            },
            "resource_trends": {
                "cpu": {"current": 0, "average_24h": 0, "peak_24h": 0, "trend": "unknown"},
                "memory": {"current": 0, "average_24h": 0, "peak_24h": 0, "trend": "unknown"},
                "disk": {"current": 0, "average_24h": 0, "peak_24h": 0, "trend": "unknown"}
            },
            "message": "No detailed metrics available. Connect real monitoring system.",
            "maintenance_recommendations": [
                {"priority": "medium", "task": "Database optimization", "estimated_time": "1 hour"},
                {"priority": "low", "task": "Log cleanup", "estimated_time": "15 minutes"}
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching detailed health: {e}")
        return {"error": str(e), "source": "maintenance_dev_bot"}


# ============================================================================
# 2. USER MANAGEMENT - FROM DATABASE
# ============================================================================

@router.get("/users/database")
async def get_users_from_database(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    role: Optional[str] = None,
    active_only: bool = True,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get user data directly from database
    Used for: User Management panel
    """
    try:
        async with wrap_session_factory(get_async_db) as session:
            # Build query
            query = select(User)
            
            if role:
                query = query.where(User.role == role)
            
            if active_only:
                query = query.where(User.is_active == True)
            
            # Get total count
            count_query = select(func.count()).select_from(User)
            if role:
                count_query = count_query.where(User.role == role)
            if active_only:
                count_query = count_query.where(User.is_active == True)
            
            total = await session.scalar(count_query)
            
            # Get paginated results
            offset = (page - 1) * limit
            query = query.offset(offset).limit(limit).order_by(User.created_at.desc())
            
            users = await session.execute(query)
            users_list = users.scalars().all()
            
            return {
                "source": "database",
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": (total + limit - 1) // limit,
                "users": [
                    {
                        "id": u.id,
                        "email": u.email,
                        "full_name": u.full_name,
                        "role": u.role,
                        "is_active": u.is_active,
                        "created_at": u.created_at.isoformat() if u.created_at else None,
                        "last_login": u.last_login.isoformat() if hasattr(u, 'last_login') and u.last_login else None
                    }
                    for u in users_list
                ]
            }
    except Exception as e:
        logger.error(f"Error fetching users from database: {e}")
        return {
            "source": "database",
            "error": str(e),
            "users": [],
            "total": 0
        }


@router.get("/users/statistics-database")
async def get_user_statistics_from_database(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get user statistics directly from database
    """
    try:
        async with wrap_session_factory(get_async_db) as session:
            # Total users
            total_users = await session.scalar(select(func.count()).select_from(User))
            
            # Active users
            active_users = await session.scalar(
                select(func.count()).select_from(User).where(User.is_active == True)
            )
            
            # Inactive users
            inactive_users = total_users - active_users if total_users else 0
            
            # New users in last 7 days
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            new_users_7d = await session.scalar(
                select(func.count()).select_from(User).where(User.created_at >= seven_days_ago)
            )
            
            # Users by role
            role_query = select(User.role, func.count().label('count')).group_by(User.role)
            role_results = await session.execute(role_query)
            users_by_role = {row[0]: row[1] for row in role_results}
            
            return {
                "source": "database",
                "timestamp": datetime.utcnow().isoformat(),
                "summary": {
                    "total_users": total_users,
                    "active_users": active_users,
                    "inactive_users": inactive_users,
                    "new_users_7d": new_users_7d or 0,
                    "growth_rate": f"{((new_users_7d or 0) / max(total_users, 1)) * 100:.1f}%" if total_users else "0%"
                },
                "by_role": users_by_role
            }
    except Exception as e:
        logger.error(f"Error fetching user statistics: {e}")
        return {
            "source": "database",
            "error": str(e),
            "summary": {
                "total_users": 0,
                "active_users": 0,
                "inactive_users": 0,
                "new_users_7d": 0
            }
        }


# ============================================================================
# 3. SECURITY & AUDIT - FROM SECURITY BOT
# ============================================================================

@router.get("/security/audit-logs")
async def get_audit_logs_from_security_bot(
    action: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = Query(50, le=200),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get audit logs from security bot
    Used for: Security & Audit panel
    """
    try:
        # This would connect to the security bot
        # For now, returning structure that security bot would provide
        return {
            "source": "security_bot",
            "timestamp": datetime.utcnow().isoformat(),
            "total_logs": 0,
            "filters_applied": {
                "action": action,
                "severity": severity,
                "limit": limit
            },
            "logs": [],
            "message": "No audit logs available. Connect a real audit logging system."
        }
    except Exception as e:
        logger.error(f"Error fetching audit logs: {e}")
        return {
            "source": "security_bot",
            "error": str(e),
            "logs": []
        }


@router.get("/security/alerts")
async def get_security_alerts_from_security_bot(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get security alerts from security bot
    """
    try:
        return {
            "source": "security_bot",
            "timestamp": datetime.utcnow().isoformat(),
            "alerts": [
                {
                    "id": "alert-002",
                    "severity": "high",
                    "title": "Unusual API Activity",
                    "description": "High volume of API requests from user ID 42",
                    "created_at": "2026-02-02T13:45:00Z",
                    "status": "acknowledged",
                    "actions": []
                }
            ],
            "message": "No security alerts available. Connect a real security monitoring system."
        }
    except Exception as e:
        logger.error(f"Error fetching security alerts: {e}")
        return {
            "source": "security_bot",
            "error": str(e),
            "alerts": []
        }


@router.get("/security/recommendations")
async def get_security_recommendations_from_security_bot(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get security recommendations from security bot
    """
    try:
        return {
            "source": "security_bot",
            "timestamp": datetime.utcnow().isoformat(),
            "recommendations": [
                {
                    "id": "rec-001",
                    "priority": "critical",
                    "title": "Enable Multi-Factor Authentication",
                    "description": "MFA is not enabled for admin accounts",
                    "impact": "Reduces account takeover risk by 99%",
                    "effort": "1 hour",
                    "status": "pending"
                },
                {
                    "id": "rec-002",
                    "priority": "high",
                    "title": "Update Security Headers",
                    "description": "Add missing HSTS and CSP headers",
                    "impact": "Prevents common web attacks",
                    "effort": "30 minutes",
                    "status": "pending"
                },
                {
                    "id": "rec-003",
                    "priority": "medium",
                    "title": "Rotate API Keys",
                    "description": "API keys have not been rotated in 180 days",
                    "impact": "Reduces key compromise risk",
                    "effort": "2 hours",
                    "status": "in_progress"
                }
            ],
            "message": "No recommendations available. Connect a real security analysis system."
        }
    except Exception as e:
        logger.error(f"Error fetching security recommendations: {e}")
        return {
            "source": "security_bot",
            "error": str(e),
            "recommendations": []
        }


@router.get("/shipping/mapleload")
async def get_mapleload_shipping_source(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Surface the MapleLoad Shipping Department as a trusted freight source.
    """
    try:
        response = {
            "source": "mapleload_bot",
            "timestamp": datetime.utcnow().isoformat(),
            "department": "Shipping Department",
            "description": "MapleLoad freight sourcing channel covering eastern Canada",
            "contact": {
                "phone": "(418) 660-1180",
                "extension": "237",
                "email": "jfortin@multiaction.ca",
                "website": "https://www.multiaction.ca",
                "address": "6890 boulevard Ste-Anne, L'Ange-Gardien, QC G0A 2K0 Canada"
            },
            "capabilities": [
                "load_sourcing",
                "market_intelligence",
                "shipment_notifications",
                "partner_outreach"
            ],
            "message": "MapleLoad Shipping Department is available as a shipment source."
        }
        return response
    except Exception as e:
        logger.error(f"Error providing MapleLoad shipping contact: {e}")
        return {
            "source": "mapleload_bot",
            "error": str(e),
            "contact": {},
            "capabilities": []
        }
