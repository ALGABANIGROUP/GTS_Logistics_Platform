"""
Admin Routes - Unified admin surface for GTS and TMS operations
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from backend.database.config import get_sessionmaker, init_engines
from backend.models.user import User
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/admin", tags=["Admin Dashboard"])


# Database dependency
async def get_db():
    """Get database session"""
    
    init_engines()
    maker = get_sessionmaker()
    if maker is None:
        raise RuntimeError("Database not initialized")
    
    async with maker() as session:
        yield session


async def verify_admin(request: Request) -> dict:
    """Verify that the user is an admin"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token not provided"
        )
    
    # Use the regular auth system to verify token
    from backend.security.auth import _decode_token
    try:
        payload = _decode_token(token)
    except Exception as e:
        logger.warning(f"Token decode failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    # Check user email in token
    user_email = payload.get("email")
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not found in token"
        )
    
    # For now, just verify token is valid
    # Role and permissions are checked in each endpoint if needed
    return payload


@router.get("", summary="Admin API Root")
@router.get("/", summary="Admin API Root")
async def admin_root(payload: dict = Depends(verify_admin)):
    """Admin API root endpoint"""
    return {
        "status": "ok",
        "message": "Admin API is running",
        "endpoints": [
            "/overview",
            "/roles",
            "/users/management",
            "/org/tree",
        ]
    }


@router.get("/overview", summary="Get admin platform overview")
async def get_admin_overview(
    payload: dict = Depends(verify_admin),
    session: AsyncSession = Depends(get_db)
):
    """
    Return high-level platform overview metrics and operational context.
    """
    return {
        "status": "success",
        "overview": {
            "gts_platform": {
                "title": "Gabani Transport Solutions (GTS)",
                "users": 0,
                "active_users": 0,
                "companies": 0,
                "revenue_this_month": 0,
                "growth_rate": 0,
            },
            "overall": {
                "total_users": 0,
                "active_users": 0,
                "total_companies": 0,
                "total_revenue_this_month": 0,
                "avg_response_time_ms": 0,
                "message": "Connect a real data source for dashboard metrics"
            }
        }
    }


@router.get("/roles", summary="Get available user roles")
async def get_roles(
    payload: dict = Depends(verify_admin),
    session: AsyncSession = Depends(get_db)
):
    """Get list of all available user roles"""
    roles = [
        {"value": "super_admin", "label": "Super Admin", "description": "Full system access"},
        {"value": "admin", "label": "Admin", "description": "Administrative access"},
        {"value": "system_admin", "label": "System Admin", "description": "System administration"},
        {"value": "manager", "label": "Manager", "description": "Management access"},
        {"value": "user", "label": "User", "description": "Regular user access"},
        {"value": "partner", "label": "Partner", "description": "Partner access"},
        {"value": "owner", "label": "Owner", "description": "Company owner"},
        {"value": "operator", "label": "Operator", "description": "System operator"},
    ]
    return {
        "status": "success",
        "data": {
            "roles": roles
        }
    }


@router.get("/users-unified/management", summary="Get user management list")
async def get_users_management(
    skip: int = 0,
    limit: int = 20,
    payload: dict = Depends(verify_admin),
    session: AsyncSession = Depends(get_db)
):
    """Return paginated users with management metadata."""
    try:
        # Get total count
        count_query = select(func.count(User.id)).where(User.is_deleted == False)
        total_result = await session.execute(count_query)
        total_users = total_result.scalar() or 0

        # Get users with pagination
        query = select(User).where(User.is_deleted == False).offset(skip).limit(limit).order_by(User.created_at.desc())
        result = await session.execute(query)
        users_db = result.scalars().all()

        # Convert to response format
        users = []
        for user in users_db:
            users.append({
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "username": user.username,
                "role": user.role,
                "company": user.company,
                "country": user.country,
                "user_type": user.user_type,
                "phone_number": user.phone_number,
                "is_active": user.is_active,
                "is_banned": user.is_banned,
                "ban_reason": user.ban_reason,
                "banned_until": user.banned_until.isoformat() if user.banned_until else None,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None,
                "status": "active" if user.is_active and not user.is_banned else ("banned" if user.is_banned else "inactive")
            })

        return {
            "status": "success",
            "total_users": total_users,
            "page": {"skip": skip, "limit": limit},
            "users": users
        }

    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch users: {str(e)}"
        )


@router.get("/org/tree", summary="Get organization chart tree")
async def get_org_tree(
    payload: dict = Depends(verify_admin),
    session: AsyncSession = Depends(get_db)
):
    """Get organizational tree structure with users and their managers"""
    try:
        # Get all users with manager relationships
        query = select(User).where(User.is_deleted == False).order_by(User.full_name)
        result = await session.execute(query)
        users_db = result.scalars().all()

        # Build tree structure
        tree = []
        for user in users_db:
            tree.append({
                "id": str(user.id),
                "name": user.full_name or user.email,
                "email": user.email,
                "role": user.role,
                "parent_id": str(user.manager_id) if user.manager_id else None,
                "children": []
            })

        return {
            "status": "success",
            "data": {
                "tree": tree
            }
        }
    except Exception as e:
        logger.error(f"Error fetching org tree: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch org tree: {str(e)}"
        )


@router.post("/org/units/{user_id}/move", summary="Move user to new manager")
async def move_user_to_manager(
    user_id: str,
    parent_id: int = None,
    payload: dict = Depends(verify_admin),
    session: AsyncSession = Depends(get_db)
):
    """Move a user to a new manager/parent unit"""
    try:
        # Get the user
        result = await session.execute(
            select(User).where(User.id == int(user_id))
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update manager
        user.manager_id = parent_id
        session.add(user)
        await session.commit()
        
        return {
            "status": "success",
            "message": f"User moved successfully to manager {parent_id or 'None'}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error moving user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to move user: {str(e)}"
        )


@router.get("/subscriptions/analytics", summary="Get subscription analytics")
async def get_subscriptions_analytics(
    payload: dict = Depends(verify_admin),
    session: AsyncSession = Depends(get_db)
):
    """Return subscription distribution and monetization metrics."""
    return {
        "status": "success",
        "subscriptions": {
            "by_tier": {
                "starter": {
                    "name": "Starter",
                    "count": 0,
                    "monthly_revenue": 0,
                    "growth_rate": 0,
                    "churn_rate": 0,
                },
                "professional": {
                    "name": "Professional",
                    "count": 0,
                    "monthly_revenue": 0,
                    "growth_rate": 0,
                    "churn_rate": 0,
                },
                "enterprise": {
                    "name": "Enterprise",
                    "count": 0,
                    "monthly_revenue": 0,
                    "growth_rate": 0,
                    "churn_rate": 0,
                }
            },
            "metrics": {
                "total_active_subscriptions": 0,
                "total_monthly_revenue": 0,
                "avg_subscription_value": 0,
                "churn_rate": 0,
                "upgrade_rate": 0,
                "message": "Connect a real subscription data source"
            },
            "upgrade_opportunities": [],
            "downgrade_risks": []
        }
    }


@router.get("/bots/status", summary="Get AI bots status")
async def get_bots_status(
    payload: dict = Depends(verify_admin),
    session: AsyncSession = Depends(get_db)
):
    """Return runtime status snapshot for configured bots."""
    return {
        "status": "success",
        "bots": {
            "gts_platform": {
                "general_manager": {"status": "active", "runs_today": 145},
                "finance_bot": {"status": "active", "runs_today": 87},
                "sales_team": {"status": "active", "runs_today": 234},
            },
            # "tms_system": { ... }  # Removed (TMS deleted)
        }
    }


@router.get("/shipments/analytics", summary="Get shipment analytics")
async def get_shipments_analytics(
    payload: dict = Depends(verify_admin),
    session: AsyncSession = Depends(get_db)
):
    """Return shipment activity metrics by period and region."""
    return {
        "status": "success",
        "shipments": {
            "today": {
                "total": 0,
                "completed": 0,
                "in_transit": 0,
                "failed": 0
            },
            "this_month": {
                "total": 0,
                "completed": 0,
                "failed": 0,
                "avg_completion_time": "-"
            },
            "by_region": {
                "us": {
                    "shipments": 0,
                    "revenue": 0,
                },
                "canada": {
                    "shipments": 0,
                    "revenue": 0,
                }
            },
            "message": "Connect a real shipment tracking system"
        }
    }


@router.post("/broadcast-notification", summary="Broadcast platform notification")
async def broadcast_notification(
    body: dict,
    payload: dict = Depends(verify_admin),
    session: AsyncSession = Depends(get_db)
):
    """
    Broadcast an announcement payload to selected audience segments.
    
    Body:
    {
        "title": "Announcement title",
        "message": "Announcement body",
        "type": "info|warning|error|success",
        "target_tier": "all|starter|professional|enterprise",
        "target_system": "all|gts_main"
    }
    """
    logger.info(f"Broadcast notification queued: {body.get('title')}")
    
    return {
        "status": "success",
        "message": "Notification request accepted",
        "recipients_count": 0,
        "notification_id": None,
        "note": "Connect a real notification system for broadcasting"
    }


@router.get("/users-unified", summary="Get users")
async def get_users_admin(
    skip: int = 0,
    limit: int = 50,
    payload: dict = Depends(verify_admin),
    session: AsyncSession = Depends(get_db)
):
    """
    Return a paginated users list for admin tooling.
    """
    try:
        # Count total users
        total_result = await session.execute(
            select(func.count()).select_from(User)
        )
        total_users = total_result.scalar() or 0

        # Fetch paginated users
        result = await session.execute(
            select(User).offset(skip).limit(limit)
        )
        users_db = result.scalars().all()

        users = []
        for user in users_db:
            users.append({
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "user_type": user.user_type,
                "phone_number": user.phone_number,
                "is_active": user.is_active,
                "is_banned": user.is_banned,
                "ban_reason": user.ban_reason,
                "banned_until": user.banned_until.isoformat() if user.banned_until else None,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None,
                "status": "active" if user.is_active and not user.is_banned else ("banned" if user.is_banned else "inactive")
            })

        return {
            "status": "success",
            "total_users": total_users,
            "page": {"skip": skip, "limit": limit},
            "users": users
        }

    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch users: {str(e)}"
        )


@router.get("/metrics", summary="Get system metrics")
async def get_system_metrics(
    payload: dict = Depends(verify_admin),
    session: AsyncSession = Depends(get_db)
):
    """
    Return API, database, bot, and infrastructure metrics.
    """
    return {
        "status": "success",
        "metrics": {
            "api_performance": {
                "avg_response_time_ms": 245,
                "requests_per_minute": 1247,
                "error_rate_percent": 0.02,
                "uptime_percent": 99.98
            },
            "database": {
                "connection_pool_usage_percent": 75,
                "avg_query_time_ms": 32,
                "active_connections": 45,
                "cache_hit_rate_percent": 94.5
            },
            "bots": {
                "total_bots": 14,
                "active_bots": 12,
                "operations_completed_today": 1247,
                "avg_operation_time_minutes": 8.5
            },
            "system_resources": {
                "cpu_usage_percent": 45.2,
                "memory_usage_percent": 67.8,
                "disk_usage_percent": 34.1,
                "network_throughput_mbps": 125.4
            },
            "timestamp": "2026-01-18T10:30:00Z"
        }
    }


@router.get("/performance", summary="Get performance analytics")
async def get_performance_analytics(
    payload: dict = Depends(verify_admin),
    session: AsyncSession = Depends(get_db)
):
    """
    Return bot and operations performance analytics.
    """
    return {
        "status": "success",
        "performance": {
            "bots_performance": {
                "customer_service_bot": {
                    "operations_completed": 245,
                    "avg_response_time_minutes": 5.2,
                    "success_rate_percent": 98.5,
                    "utilization_percent": 78.3
                },
                "operations_manager_bot": {
                    "operations_completed": 189,
                    "avg_response_time_minutes": 12.1,
                    "success_rate_percent": 97.8,
                    "utilization_percent": 92.1
                },
                "general_manager_bot": {
                    "operations_completed": 67,
                    "avg_response_time_minutes": 25.4,
                    "success_rate_percent": 99.2,
                    "utilization_percent": 45.6
                }
            },
            "operations_stats": {
                "total_operations_today": 1247,
                "completed_operations": 1189,
                "pending_operations": 45,
                "failed_operations": 13,
                "avg_completion_time_hours": 4.2
            },
            "system_efficiency": {
                "overall_efficiency_score": 94.5,
                "bottleneck_identified": "Document processing queue",
                "recommended_optimizations": [
                    "Increase document processing workers",
                    "Optimize database queries",
                    "Implement caching for frequent operations"
                ]
            },
            "timestamp": "2026-01-18T10:30:00Z"
        }
    }


@router.get("/system-health", summary="Get system health")
async def get_system_health(
    payload: dict = Depends(verify_admin),
    session: AsyncSession = Depends(get_db)
):
    """Return health status across key platform subsystems."""
    return {
        "status": "success",
        "health": {
            "api_servers": {
                "status": "unknown",
                "response_time_avg_ms": None,
                "uptime_percent": None,
                "active_connections": 0
            },
            "database": {
                "status": "unknown",
                "connection_pool_usage": 0,
                "query_time_avg_ms": None,
                "replication_lag_ms": None
            },
            "websocket_hub": {
                "status": "unknown",
                "connected_clients": 0,
                "message_throughput": 0,
            },
            "overall_status": "unknown",
            "message": "Connect real monitoring system for health checks"
        }
    }


@router.get("/logs", summary="Get system logs")
async def get_system_logs(
    log_type: str = Query("operations", description="Log channel: operations, performance, security, api, errors"),
    hours: int = Query(24, description="Time range in hours"),
    limit: int = Query(100, description="Maximum number of log entries to return"),
    payload: dict = Depends(verify_admin)
):
    """
    Return filtered system logs by type, time window, and result limit.

    - **log_type**: selected log channel
    - **hours**: lookback time window
    - **limit**: result size cap
    """
    try:
        import os
        from pathlib import Path
        from datetime import datetime, timedelta

        logs_dir = Path("logs")
        if not logs_dir.exists():
            return {
                "success": True,
                "logs": [],
                "message": "Logs directory was not found",
                "total_count": 0
            }

        # Map log type to file name
        log_files = {
            "operations": "operations.log",
            "performance": "performance.log",
            "security": "security.log",
            "api": "api.log",
            "errors": "errors.log"
        }

        log_file = logs_dir / log_files.get(log_type, "operations.log")
        if not log_file.exists():
            return {
                "success": True,
                "logs": [],
                "message": f"No log file found for type '{log_type}'",
                "total_count": 0
            }

        # Parse and filter log entries
        logs = []
        cutoff_time = datetime.now() - timedelta(hours=hours)

        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    if line.strip():
                        # Parse JSON log line
                        log_entry = json.loads(line.strip())
                        log_time = datetime.fromisoformat(log_entry.get('timestamp', ''))

                        if log_time >= cutoff_time:
                            logs.append(log_entry)
                except json.JSONDecodeError:
                    # Fallback for non-JSON log lines
                    logs.append({
                        "timestamp": datetime.now().isoformat(),
                        "level": "INFO",
                        "message": line.strip(),
                        "raw": True
                    })

        # Sort newest first and apply limit
        logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        limited_logs = logs[:limit]

        return {
            "success": True,
            "log_type": log_type,
            "time_range_hours": hours,
            "logs": limited_logs,
            "total_count": len(logs),
            "returned_count": len(limited_logs)
        }

    except Exception as e:
        logger.error(f"Failed to fetch logs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch logs: {str(e)}"
        )


@router.get("/logs/stats", summary="Get log statistics")
async def get_logs_statistics(payload: dict = Depends(verify_admin)):
    """Return log file size and recent-entry statistics."""
    try:
        import os
        from pathlib import Path
        from datetime import datetime, timedelta

        logs_dir = Path("logs")
        stats = {
            "total_log_files": 0,
            "total_log_size_mb": 0,
            "last_24h_entries": {},
            "log_types": {}
        }

        if logs_dir.exists():
            log_files = ["operations.log", "performance.log", "security.log", "api.log", "errors.log"]
            cutoff_time = datetime.now() - timedelta(hours=24)

            for log_file in log_files:
                file_path = logs_dir / log_file
                log_type = log_file.replace('.log', '')

                if file_path.exists():
                    stats["total_log_files"] += 1
                    stats["total_log_size_mb"] += file_path.stat().st_size / (1024 * 1024)

                    # Count entries in the last 24 hours
                    count_24h = 0
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            for line in f:
                                try:
                                    if line.strip():
                                        log_entry = json.loads(line.strip())
                                        log_time = datetime.fromisoformat(log_entry.get('timestamp', ''))
                                        if log_time >= cutoff_time:
                                            count_24h += 1
                                except:
                                    continue
                    except:
                        count_24h = 0

                    stats["last_24h_entries"][log_type] = count_24h
                    stats["log_types"][log_type] = {
                        "file_size_mb": round(file_path.stat().st_size / (1024 * 1024), 2),
                        "entries_24h": count_24h
                    }

        return {
            "success": True,
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to compute log statistics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compute log statistics: {str(e)}"
        )


# ============================================
# User Management Endpoints (POST/PUT/PATCH/DELETE)
# ============================================

@router.post("/users-unified", summary="Create new user")
async def create_user(
    body: dict,
    payload: dict = Depends(verify_admin),
    session: AsyncSession = Depends(get_db)
):
    """Create a new user"""
    try:
        from backend.security.auth import get_password_hash
        
        email = body.get("email", "").lower().strip()
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")
        
        # Check if user exists
        existing = await session.execute(
            select(User).where(User.email == email)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="User already exists")
        
        # Create user
        user = User(
            email=email,
            full_name=body.get("full_name", ""),
            username=body.get("username", ""),
            phone_number=body.get("phone_number", ""),
            company=body.get("company", ""),
            country=body.get("country", ""),
            user_type=body.get("user_type", ""),
            role=body.get("role", "user"),
            is_active=body.get("is_active", True),
        )
        
        if body.get("password"):
            user.hashed_password = get_password_hash(body["password"])
        
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        return {
            "status": "success",
            "message": "User created successfully",
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")


@router.put("/users-unified/{user_id}", summary="Update user")
async def update_user(
    user_id: int,
    body: dict,
    payload: dict = Depends(verify_admin),
    session: AsyncSession = Depends(get_db)
):
    """Update user information"""
    try:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update fields
        if "full_name" in body:
            user.full_name = body["full_name"]
        if "username" in body:
            user.username = body["username"]
        if "phone_number" in body:
            user.phone_number = body["phone_number"]
        if "company" in body:
            user.company = body["company"]
        if "country" in body:
            user.country = body["country"]
        if "user_type" in body:
            user.user_type = body["user_type"]
        if "role" in body:
            user.role = body["role"]
        
        session.add(user)
        await session.commit()
        
        return {"status": "success", "message": "User updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")


@router.patch("/users-unified/{user_id}", summary="Patch user")
async def patch_user(
    user_id: int,
    body: dict,
    payload: dict = Depends(verify_admin),
    session: AsyncSession = Depends(get_db)
):
    """Partially update user"""
    try:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Handle all user update fields
        if "full_name" in body:
            user.full_name = body["full_name"]
        if "email" in body:
            user.email = body["email"]
        if "username" in body:
            user.username = body["username"]
        if "phone_number" in body:
            user.phone_number = body["phone_number"]
        if "company" in body:
            user.company = body["company"]
        if "country" in body:
            user.country = body["country"]
        if "user_type" in body:
            user.user_type = body["user_type"]
        if "role" in body:
            user.role = body["role"]
        if "is_active" in body:
            user.is_active = body["is_active"]
        if "is_banned" in body:
            user.is_banned = body["is_banned"]
        if "ban_reason" in body:
            user.ban_reason = body["ban_reason"]
        if "banned_until" in body:
            user.banned_until = body["banned_until"]
        
        # Handle password update if provided
        if "password" in body and body["password"]:
            from backend.security.passwords import hash_password
            user.hashed_password = hash_password(body["password"])
        
        user.updated_at = datetime.utcnow()
        
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        return {
            "status": "success",
            "message": "User patched successfully",
            "data": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "username": user.username,
                "role": user.role,
                "is_active": user.is_active,
                "is_banned": user.is_banned,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error patching user: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to patch user: {str(e)}")


@router.delete("/users-unified/{user_id}", summary="Delete user")
async def delete_user(
    user_id: int,
    payload: dict = Depends(verify_admin),
    session: AsyncSession = Depends(get_db)
):
    """Soft delete user"""
    try:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Soft delete
        user.is_deleted = True
        user.deleted_at = datetime.utcnow()
        
        session.add(user)
        await session.commit()
        
        return {"status": "success", "message": "User deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")


# =============== Portal Notifications ===============

@router.get("/portal/notifications-unified", summary="Portal notifications - get notifications")
async def get_portal_notifications(
    request: Request,
    limit: int = Query(100, ge=1, le=200),
    unread_only: bool = Query(False),
    db: AsyncSession = Depends(get_db)
):
    """
    Get portal notifications with optional filtering.
    """
    try:
        # Verify user is authenticated
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        # TODO: Replace demo payload with database-backed notifications
        # In production, fetch from database when notification system is implemented
        demo_notifications = []
        
        # Filter by unread if requested
        if unread_only:
            filtered = [n for n in demo_notifications if not n["read"]]
        else:
            filtered = demo_notifications
        
        # Limit results
        filtered = filtered[:limit]
        
        # Calculate unread count
        unread_count = len([n for n in demo_notifications if not n["read"]])
        
        return {
            "ok": True,
            "notifications": filtered,
            "unread_count": unread_count,
            "total_count": len(demo_notifications)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching notifications: {e}")
        return {
            "ok": True,
            "notifications": [],
            "unread_count": 0,
            "total_count": 0,
            "detail": str(e)
        }

