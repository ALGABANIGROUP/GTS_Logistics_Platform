from __future__ import annotations

import json
import logging
from copy import deepcopy
from typing import Any, Dict, Optional

from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import async_session, wrap_session_factory
from backend.utils.crypto import encrypt_secret

logger = logging.getLogger(__name__)

DEFAULT_SETTINGS: Dict[str, Any] = {
    "general": {
        "platformName": "GTS Logistics Platform",
        "platformLogo": "",
        "timeZone": "UTC",
        "dateFormat": "YYYY-MM-DD",
        "currency": "USD",
    },
    "technical": {
        "sessionTimeout": 30,
        "maxUploadSize": 10,
        "cachingEnabled": True,
        "maintenanceMode": False,
        "apiRateLimit": "100/hour",
        "backupFrequency": "daily",
    },
    "database": {
        "dbType": "postgres",
        "backupRetentionDays": 14,
        "cleanupOldDataDays": 90,
        "enableDbLogs": True,
        "backupWindow": "02:00",
    },
    "integrations": {
        "apiKeysEnabled": True,
        "webhookUrl": "",
        "webhookSecret": "",
        "ssoEnabled": False,
        "ssoProvider": "none",
        "mapEnabled": False,
        "mapProvider": "google",
        "mapApiKey": "",
        "mapDefaultZoom": 10,
        "mapDefaultLat": 43.653226,
        "mapDefaultLng": -79.383184,
    },
    "branding": {
        "platformName": "GTS Logistics Platform",
        "logoUrl": "",
        "faviconUrl": "",
    },
    "theme": {
        "primaryColor": "#2E71EE",
        "background": "#0F1C2F",
        "transparency": 0.15,
        "blur": 10,
    },
    "social": {
        "facebook": {"pageId": "", "accessToken": "", "appId": "", "appSecret": ""},
        "twitter": {"accessToken": "", "apiKey": "", "apiSecret": ""},
        "linkedin": {"accessToken": "", "clientId": "", "clientSecret": ""},
    },
    "social_links": {
        "linkedin": "",
        "x": "",
        "facebook": "",
        "youtube": "",
        "instagram": "",
    },
    "email": {
        "smtpServer": "",
        "smtpPort": 587,
        "smtpPassword": "",
        "fromEmail": "",
        "fromName": "",
        "useSSL": True,
        "useTLS": True,
    },
    "security": {
        "allowedDomains": "",
        "passwordPolicy": {
            "minLength": 8,
            "requireUppercase": True,
            "requireNumber": True,
            "requireSymbol": True,
        },
    },
}

SECRET_PATHS = [
    ("social", "facebook", "accessToken"),
    ("social", "facebook", "appSecret"),
    ("social", "twitter", "accessToken"),
    ("social", "twitter", "apiSecret"),
    ("social", "linkedin", "accessToken"),
    ("social", "linkedin", "clientSecret"),
    ("integrations", "webhookSecret"),
    ("email", "smtpPassword"),
]
_MASK_PLACEHOLDER = "********"


async def _ensure_schema(session: AsyncSession) -> None:
    await session.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS platform_settings (
                id BIGSERIAL PRIMARY KEY,
                settings TEXT NOT NULL,
                updated_at TIMESTAMPTZ DEFAULT NOW(),
                updated_by TEXT
            );
            """
        )
    )
    # Backward-compatible multi-tenant columns.
    await session.execute(
        text("ALTER TABLE platform_settings ADD COLUMN IF NOT EXISTS tenant_id TEXT")
    )
    await session.execute(
        text("ALTER TABLE platform_settings ADD COLUMN IF NOT EXISTS tenant_type TEXT")
    )
    await session.execute(
        text("ALTER TABLE platform_settings ADD COLUMN IF NOT EXISTS created_by TEXT")
    )
    await session.execute(
        text(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS ux_platform_settings_tenant_id
            ON platform_settings (tenant_id)
            """
        )
    )
    # Keep BIGSERIAL in sync when legacy row id=1 was inserted manually.
    await session.execute(
        text(
            """
            SELECT setval(
                pg_get_serial_sequence('platform_settings', 'id'),
                COALESCE((SELECT MAX(id) FROM platform_settings), 1),
                true
            )
            """
        )
    )
    await session.commit()


def _merge(base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    merged = deepcopy(base)
    for key, value in (updates or {}).items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _get_in(data: Dict[str, Any], path: tuple[str, ...]) -> Any:
    cur = data
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return None
        cur = cur[key]
    return cur


def _set_in(data: Dict[str, Any], path: tuple[str, ...], value: Any) -> None:
    cur = data
    for key in path[:-1]:
        if key not in cur or not isinstance(cur[key], dict):
            cur[key] = {}
        cur = cur[key]
    cur[path[-1]] = value


def _mask_secret(value: Optional[str]) -> str:
    if not value:
        return ""
    return _MASK_PLACEHOLDER


def _apply_secret_handling(
    incoming: Dict[str, Any], existing: Dict[str, Any]
) -> Dict[str, Any]:
    merged = _merge(existing, incoming)
    for path in SECRET_PATHS:
        new_val = _get_in(incoming, path)
        if isinstance(new_val, str) and new_val.strip() == _MASK_PLACEHOLDER:
            new_val = None

        if new_val is None:
            existing_val = _get_in(existing, path)
            if existing_val is not None:
                _set_in(merged, path, existing_val)
            continue

        if new_val == "":
            _set_in(merged, path, "")
            continue

        try:
            _set_in(merged, path, encrypt_secret(str(new_val)))
        except Exception as exc:
            logger.warning("secret encryption failed: %s", exc)
            _set_in(merged, path, str(new_val))
    return merged


def _mask_secrets_for_output(settings: Dict[str, Any]) -> Dict[str, Any]:
    masked = deepcopy(settings)
    for path in SECRET_PATHS:
        if _get_in(masked, path):
            _set_in(masked, path, _mask_secret(_get_in(masked, path)))
    return masked


async def _get_platform_settings_raw(
    session: AsyncSession,
    tenant_id: Optional[str] = None,
) -> Dict[str, Any]:
    await _ensure_schema(session)
    if tenant_id:
        result = await session.execute(
            text(
                """
                SELECT settings
                FROM platform_settings
                WHERE tenant_id = :tenant_id
                ORDER BY updated_at DESC NULLS LAST, id DESC
                LIMIT 1
                """
            ),
            {"tenant_id": str(tenant_id)},
        )
        row = result.first()
        if row:
            try:
                data = json.loads(row[0])
            except Exception:
                data = deepcopy(DEFAULT_SETTINGS)
            return _merge(DEFAULT_SETTINGS, data or {})

    result = await session.execute(
        text(
            """
            SELECT settings
            FROM platform_settings
            WHERE tenant_id IS NULL
            ORDER BY CASE WHEN id = 1 THEN 0 ELSE 1 END, updated_at DESC NULLS LAST, id ASC
            LIMIT 1
            """
        )
    )
    row = result.first()
    if not row:
        return deepcopy(DEFAULT_SETTINGS)
    try:
        data = json.loads(row[0])
    except Exception:
        data = deepcopy(DEFAULT_SETTINGS)
    return _merge(DEFAULT_SETTINGS, data or {})


async def get_platform_settings(
    session: AsyncSession,
    tenant_id: Optional[str] = None,
) -> Dict[str, Any]:
    raw = await _get_platform_settings_raw(session, tenant_id=tenant_id)
    return _mask_secrets_for_output(raw)


async def update_platform_settings(
    session: AsyncSession,
    incoming: Dict[str, Any],
    updated_by: Optional[str] = None,
    tenant_id: Optional[str] = None,
    tenant_type: Optional[str] = None,
) -> Dict[str, Any]:
    async def _persist(target_session: AsyncSession) -> Dict[str, Any]:
        await _ensure_schema(target_session)
        current = await _get_platform_settings_raw(target_session, tenant_id=tenant_id)
        merged = _apply_secret_handling(incoming or {}, current)
        settings_json = json.dumps(merged)
        if tenant_id:
            existing = await target_session.execute(
                text("SELECT id FROM platform_settings WHERE tenant_id = :tenant_id LIMIT 1"),
                {"tenant_id": str(tenant_id)},
            )
            existing_id = existing.scalar_one_or_none()
            if existing_id is None:
                await target_session.execute(
                    text(
                        """
                        INSERT INTO platform_settings
                            (tenant_id, tenant_type, settings, updated_at, updated_by, created_by)
                        VALUES
                            (:tenant_id, :tenant_type, :settings, NOW(), :updated_by, :created_by)
                        """
                    ),
                    {
                        "tenant_id": str(tenant_id),
                        "tenant_type": str(tenant_type or "company"),
                        "settings": settings_json,
                        "updated_by": updated_by,
                        "created_by": updated_by,
                    },
                )
            else:
                await target_session.execute(
                    text(
                        """
                        UPDATE platform_settings
                        SET settings = :settings,
                            tenant_type = COALESCE(:tenant_type, tenant_type),
                            updated_at = NOW(),
                            updated_by = :updated_by
                        WHERE id = :id
                        """
                    ),
                    {
                        "id": int(existing_id),
                        "tenant_type": str(tenant_type or "company"),
                        "settings": settings_json,
                        "updated_by": updated_by,
                    },
                )
        else:
            await target_session.execute(
                text(
                    """
                    INSERT INTO platform_settings (id, tenant_id, tenant_type, settings, updated_at, updated_by)
                    VALUES (1, NULL, NULL, :settings, NOW(), :updated_by)
                    ON CONFLICT (id)
                    DO UPDATE SET settings = :settings, updated_at = NOW(), updated_by = :updated_by
                    """
                ),
                {"settings": settings_json, "updated_by": updated_by},
            )
        await target_session.commit()
        return _mask_secrets_for_output(merged)

    def _is_transient_connection_drop(exc: DBAPIError) -> bool:
        message = str(exc).lower()
        return bool(
            getattr(exc, "connection_invalidated", False)
            or "connectiondoesnotexisterror" in message
            or "connection was closed in the middle of operation" in message
            or "terminating connection" in message
        )

    await _ensure_schema(session)
    try:
        return await _persist(session)
    except DBAPIError as exc:
        try:
            await session.rollback()
        except Exception:
            pass

        if not _is_transient_connection_drop(exc):
            raise

        logger.warning("Transient DB connection drop while saving platform settings; retrying once")
        async with wrap_session_factory(async_session) as retry_session:
            return await _persist(retry_session)
