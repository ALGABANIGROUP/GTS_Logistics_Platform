from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

TABLE_NAME = "admin_tenants"


async def _ensure_table(session: AsyncSession) -> None:
    await session.execute(
        text(
            f"""
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                tenant_id TEXT PRIMARY KEY,
                company_name TEXT NOT NULL,
                domain TEXT NOT NULL,
                status TEXT NOT NULL,
                users_count INTEGER NOT NULL DEFAULT 0,
                max_users INTEGER NOT NULL DEFAULT 0,
                plan TEXT NOT NULL,
                subscription_end TEXT,
                created_date TEXT,
                contact_email TEXT,
                contact_phone TEXT,
                storage_used TEXT,
                total_storage TEXT,
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );
            """
        )
    )
    await session.commit()


def _row_to_dict(row: Any) -> Dict[str, Any]:
    return {
        "id": row.tenant_id,
        "companyName": row.company_name,
        "domain": row.domain,
        "status": row.status,
        "usersCount": int(row.users_count or 0),
        "maxUsers": int(row.max_users or 0),
        "plan": row.plan,
        "subscriptionEnd": row.subscription_end,
        "createdDate": row.created_date,
        "contactEmail": row.contact_email,
        "contactPhone": row.contact_phone,
        "storageUsed": row.storage_used,
        "totalStorage": row.total_storage,
    }


async def list_admin_tenants(session: AsyncSession) -> list[Dict[str, Any]]:
    await _ensure_table(session)
    result = await session.execute(
        text(
            f"""
            SELECT tenant_id, company_name, domain, status, users_count, max_users, plan,
                   subscription_end, created_date, contact_email, contact_phone, storage_used, total_storage
            FROM {TABLE_NAME}
            ORDER BY created_date DESC NULLS LAST, tenant_id
            """
        )
    )
    return [_row_to_dict(row) for row in result.fetchall()]


async def get_admin_tenant(session: AsyncSession, tenant_id: str) -> Optional[Dict[str, Any]]:
    await _ensure_table(session)
    result = await session.execute(
        text(
            f"""
            SELECT tenant_id, company_name, domain, status, users_count, max_users, plan,
                   subscription_end, created_date, contact_email, contact_phone, storage_used, total_storage
            FROM {TABLE_NAME}
            WHERE tenant_id = :tenant_id
            """
        ),
        {"tenant_id": tenant_id},
    )
    row = result.first()
    return _row_to_dict(row) if row else None


async def create_admin_tenant(
    session: AsyncSession, tenant_id: str, payload: Dict[str, Any]
) -> Dict[str, Any]:
    await _ensure_table(session)
    await session.execute(
        text(
            f"""
            INSERT INTO {TABLE_NAME} (
                tenant_id, company_name, domain, status, users_count, max_users, plan,
                subscription_end, created_date, contact_email, contact_phone, storage_used, total_storage
            ) VALUES (
                :tenant_id, :company_name, :domain, :status, :users_count, :max_users, :plan,
                :subscription_end, :created_date, :contact_email, :contact_phone, :storage_used, :total_storage
            )
            """
        ),
        {
            "tenant_id": tenant_id,
            "company_name": payload.get("company_name"),
            "domain": payload.get("domain"),
            "status": payload.get("status"),
            "users_count": payload.get("users_count", 0),
            "max_users": payload.get("max_users", 0),
            "plan": payload.get("plan"),
            "subscription_end": payload.get("subscription_end"),
            "created_date": payload.get("created_date"),
            "contact_email": payload.get("contact_email"),
            "contact_phone": payload.get("contact_phone"),
            "storage_used": payload.get("storage_used"),
            "total_storage": payload.get("total_storage"),
        },
    )
    await session.commit()
    result = await get_admin_tenant(session, tenant_id)
    return result or {"id": tenant_id}


async def update_admin_tenant(
    session: AsyncSession, tenant_id: str, payload: Dict[str, Any]
) -> Dict[str, Any]:
    await _ensure_table(session)
    await session.execute(
        text(
            f"""
            UPDATE {TABLE_NAME}
            SET company_name = :company_name,
                domain = :domain,
                status = :status,
                users_count = :users_count,
                max_users = :max_users,
                plan = :plan,
                subscription_end = :subscription_end,
                created_date = :created_date,
                contact_email = :contact_email,
                contact_phone = :contact_phone,
                storage_used = :storage_used,
                total_storage = :total_storage,
                updated_at = NOW()
            WHERE tenant_id = :tenant_id
            """
        ),
        {
            "tenant_id": tenant_id,
            "company_name": payload.get("company_name"),
            "domain": payload.get("domain"),
            "status": payload.get("status"),
            "users_count": payload.get("users_count", 0),
            "max_users": payload.get("max_users", 0),
            "plan": payload.get("plan"),
            "subscription_end": payload.get("subscription_end"),
            "created_date": payload.get("created_date"),
            "contact_email": payload.get("contact_email"),
            "contact_phone": payload.get("contact_phone"),
            "storage_used": payload.get("storage_used"),
            "total_storage": payload.get("total_storage"),
        },
    )
    await session.commit()
    result = await get_admin_tenant(session, tenant_id)
    return result or {"id": tenant_id}


async def delete_admin_tenant(session: AsyncSession, tenant_id: str) -> None:
    await _ensure_table(session)
    await session.execute(
        text(f"DELETE FROM {TABLE_NAME} WHERE tenant_id = :tenant_id"),
        {"tenant_id": tenant_id},
    )
    await session.commit()
