from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import get_db
from backend.security.auth import require_roles

router = APIRouter(prefix="/api/v1/admin/audit", tags=["admin", "audit"])

admin_required = require_roles(["admin", "super_admin", "owner", "system_admin"])


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    candidate = str(value).strip()
    if not candidate:
        return None
    try:
        return datetime.fromisoformat(candidate.replace("Z", "+00:00"))
    except Exception:
        return None


def _parse_json_blob(value: Any) -> Any:
    if value is None or isinstance(value, (dict, list, int, float, bool)):
        return value
    if not isinstance(value, str):
        return value
    raw = value.strip()
    if not raw:
        return None
    try:
        return json.loads(raw)
    except Exception:
        return {"details": raw}


def _build_admin_query(
    *,
    action: Optional[str],
    target_type: Optional[str],
    severity: Optional[str],
    start_dt: Optional[datetime],
    end_dt: Optional[datetime],
    limit: int,
) -> tuple[str, dict[str, Any]]:
    conditions: list[str] = []
    params: dict[str, Any] = {"limit": limit}

    if action:
        conditions.append("lower(a.action) = lower(:action)")
        params["action"] = action
    if target_type:
        conditions.append("lower(COALESCE(a.target_type, '')) = lower(:target_type)")
        params["target_type"] = target_type
    if severity:
        conditions.append("lower(COALESCE(a.severity, '')) = lower(:severity)")
        params["severity"] = severity
    if start_dt:
        conditions.append("a.created_at >= :start_at")
        params["start_at"] = start_dt
    if end_dt:
        conditions.append("a.created_at <= :end_at")
        params["end_at"] = end_dt

    where_sql = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    sql = f"""
        SELECT
            a.id,
            a.actor_user_id,
            u.full_name AS actor_name,
            u.email AS actor_email,
            a.action,
            a.target_type,
            a.target_id,
            a.diff_json::text AS details_json,
            a.ip,
            NULL::text AS user_agent,
            a.created_at,
            COALESCE(a.severity, 'info') AS severity,
            'audit_logs' AS source
        FROM audit_logs AS a
        LEFT JOIN users AS u ON u.id = a.actor_user_id
        {where_sql}
        ORDER BY a.created_at DESC
        LIMIT :limit
    """
    return sql, params


def _build_auth_query(
    *,
    action: Optional[str],
    severity: Optional[str],
    start_dt: Optional[datetime],
    end_dt: Optional[datetime],
    limit: int,
) -> tuple[str, dict[str, Any]]:
    conditions: list[str] = []
    params: dict[str, Any] = {"limit": limit}

    if action:
        conditions.append("lower(a.action) = lower(:action)")
        params["action"] = action
    if severity:
        conditions.append(
            "lower(CASE WHEN COALESCE(a.success, TRUE) THEN 'info' ELSE 'warning' END) = lower(:severity)"
        )
        params["severity"] = severity
    if start_dt:
        conditions.append("a.created_at >= :start_at")
        params["start_at"] = start_dt
    if end_dt:
        conditions.append("a.created_at <= :end_at")
        params["end_at"] = end_dt

    where_sql = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    sql = f"""
        SELECT
            a.id,
            a.user_id AS actor_user_id,
            COALESCE(u.full_name, a.email, 'System') AS actor_name,
            COALESCE(a.email, u.email) AS actor_email,
            a.action,
            'auth' AS target_type,
            NULL::text AS target_id,
            a.details AS details_json,
            COALESCE(a.ip_address, a.ip) AS ip,
            a.user_agent,
            a.created_at,
            CASE
                WHEN COALESCE(a.success, TRUE) THEN 'info'
                ELSE 'warning'
            END AS severity,
            'auth_audit_logs' AS source
        FROM auth_audit_logs AS a
        LEFT JOIN users AS u ON u.id = a.user_id
        {where_sql}
        ORDER BY a.created_at DESC
        LIMIT :limit
    """
    return sql, params


@router.get("")
async def list_audit_logs(
    action: Optional[str] = None,
    target_type: Optional[str] = Query(None, alias="target_type"),
    severity: Optional[str] = None,
    start_at: Optional[str] = Query(None, alias="start_at"),
    end_at: Optional[str] = Query(None, alias="end_at"),
    limit: int = Query(50, ge=1, le=200),
    current_user: Dict[str, Any] = Depends(admin_required),
    db: AsyncSession = Depends(get_db),
):
    start_dt = _parse_datetime(start_at)
    end_dt = _parse_datetime(end_at)

    admin_sql, admin_params = _build_admin_query(
        action=action,
        target_type=target_type,
        severity=severity,
        start_dt=start_dt,
        end_dt=end_dt,
        limit=limit,
    )
    admin_rows = await db.execute(text(admin_sql), admin_params)
    admin_logs = []
    for row in admin_rows.mappings().all():
        admin_logs.append(
            {
                "id": f"audit-{row['id']}",
                "actor_user_id": row["actor_user_id"],
                "actor_name": row["actor_name"],
                "actor_email": row["actor_email"],
                "action": row["action"],
                "target_type": row["target_type"],
                "target_id": row["target_id"],
                "diff_json": _parse_json_blob(row["details_json"]),
                "ip": row["ip"],
                "user_agent": row["user_agent"],
                "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                "severity": row["severity"],
                "source": row["source"],
            }
        )

    auth_logs: list[dict[str, Any]] = []
    include_auth_logs = not target_type or str(target_type).strip().lower() == "auth"
    if include_auth_logs:
        auth_sql, auth_params = _build_auth_query(
            action=action,
            severity=severity,
            start_dt=start_dt,
            end_dt=end_dt,
            limit=limit,
        )
        auth_rows = await db.execute(text(auth_sql), auth_params)
        for row in auth_rows.mappings().all():
            auth_logs.append(
                {
                    "id": f"auth-{row['id']}",
                    "actor_user_id": row["actor_user_id"],
                    "actor_name": row["actor_name"],
                    "actor_email": row["actor_email"],
                    "action": row["action"],
                    "target_type": row["target_type"],
                    "target_id": row["target_id"],
                    "diff_json": _parse_json_blob(row["details_json"]),
                    "ip": row["ip"],
                    "user_agent": row["user_agent"],
                    "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                    "severity": row["severity"],
                    "source": row["source"],
                }
            )

    merged_logs = sorted(
        [*admin_logs, *auth_logs],
        key=lambda item: str(item.get("created_at") or ""),
        reverse=True,
    )[:limit]

    return {
        "source": "database",
        "timestamp": datetime.utcnow().isoformat(),
        "filters_applied": {
            "action": action,
            "target_type": target_type,
            "severity": severity,
            "start_at": start_at,
            "end_at": end_at,
            "limit": limit,
        },
        "logs": merged_logs,
        "count": len(merged_logs),
        "viewer_role": current_user.get("role"),
    }
