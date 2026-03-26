"""Data source persistence service."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

_TABLE_READY = False


def _serialize_timestamp(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def _parse_config(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return value
    if not value:
        return {}
    try:
        return json.loads(value)
    except Exception:
        return {}


class DataSourceService:
    """Service for managing persisted data sources."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def _ensure_table(self) -> None:
        global _TABLE_READY
        if _TABLE_READY:
            return

        await self.session.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS admin_data_sources (
                    id VARCHAR(64) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    type VARCHAR(100) NOT NULL,
                    status VARCHAR(50) NOT NULL DEFAULT 'pending',
                    config TEXT NOT NULL DEFAULT '{}',
                    last_sync TIMESTAMP NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NULL,
                    deleted_at TIMESTAMP NULL
                )
                """
            )
        )
        await self.session.commit()
        _TABLE_READY = True

    @staticmethod
    def _row_to_source(row: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": row["id"],
            "name": row["name"],
            "type": row["type"],
            "status": row["status"],
            "config": _parse_config(row.get("config")),
            "last_sync": _serialize_timestamp(row.get("last_sync")),
            "created_at": _serialize_timestamp(row.get("created_at")),
            "updated_at": _serialize_timestamp(row.get("updated_at")),
        }

    async def list_sources(self) -> List[Dict[str, Any]]:
        """List all persisted data sources."""
        await self._ensure_table()
        result = await self.session.execute(
            text(
                """
                SELECT id, name, type, status, config, last_sync, created_at, updated_at
                FROM admin_data_sources
                WHERE deleted_at IS NULL
                ORDER BY created_at DESC, id DESC
                """
            )
        )
        return [self._row_to_source(dict(row)) for row in result.mappings().all()]

    async def get_source(self, source_id: str) -> Optional[Dict[str, Any]]:
        """Get a single data source by ID."""
        await self._ensure_table()
        result = await self.session.execute(
            text(
                """
                SELECT id, name, type, status, config, last_sync, created_at, updated_at
                FROM admin_data_sources
                WHERE id = :source_id AND deleted_at IS NULL
                LIMIT 1
                """
            ),
            {"source_id": source_id},
        )
        row = result.mappings().first()
        return self._row_to_source(dict(row)) if row else None

    async def create_source(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new persisted data source."""
        await self._ensure_table()
        now = datetime.utcnow()
        source_id = str(data.get("id") or uuid4().hex[:16])
        payload = {
            "id": source_id,
            "name": str(data.get("name") or source_id),
            "type": str(data.get("type") or "custom"),
            "status": str(data.get("status") or "pending"),
            "config": json.dumps(data.get("config") or {}),
            "last_sync": data.get("last_sync"),
            "created_at": now,
            "updated_at": now,
        }
        await self.session.execute(
            text(
                """
                INSERT INTO admin_data_sources (id, name, type, status, config, last_sync, created_at, updated_at)
                VALUES (:id, :name, :type, :status, :config, :last_sync, :created_at, :updated_at)
                """
            ),
            payload,
        )
        await self.session.commit()
        logger.info("Created data source: %s", source_id)
        return (await self.get_source(source_id)) or {
            "id": source_id,
            "name": payload["name"],
            "type": payload["type"],
            "status": payload["status"],
            "config": data.get("config") or {},
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "last_sync": _serialize_timestamp(payload["last_sync"]),
        }

    async def update_source(self, source_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing persisted data source."""
        current = await self.get_source(source_id)
        if not current:
            return None

        now = datetime.utcnow()
        await self.session.execute(
            text(
                """
                UPDATE admin_data_sources
                SET
                    name = :name,
                    type = :type,
                    status = :status,
                    config = :config,
                    last_sync = :last_sync,
                    updated_at = :updated_at
                WHERE id = :source_id AND deleted_at IS NULL
                """
            ),
            {
                "source_id": source_id,
                "name": str(data.get("name") or current["name"]),
                "type": str(data.get("type") or current["type"]),
                "status": str(data.get("status") or current["status"]),
                "config": json.dumps(data.get("config", current.get("config") or {})),
                "last_sync": data.get("last_sync"),
                "updated_at": now,
            },
        )
        await self.session.commit()
        return await self.get_source(source_id)

    async def delete_source(self, source_id: str) -> bool:
        """Soft-delete a data source."""
        await self._ensure_table()
        result = await self.session.execute(
            text(
                """
                UPDATE admin_data_sources
                SET deleted_at = :deleted_at, updated_at = :deleted_at
                WHERE id = :source_id AND deleted_at IS NULL
                """
            ),
            {"source_id": source_id, "deleted_at": datetime.utcnow()},
        )
        await self.session.commit()
        deleted = (result.rowcount or 0) > 0
        if deleted:
            logger.info("Deleted data source: %s", source_id)
        return deleted

    async def test_connection(self, source_id: str) -> Dict[str, Any]:
        """Test whether the data source is configured enough to use."""
        source = await self.get_source(source_id)
        if not source:
            return {"success": False, "message": "Data source not found"}

        config = source.get("config") or {}
        if source.get("status") not in {"active", "pending"}:
            return {"success": False, "message": f"Data source {source['name']} is inactive"}

        return {
            "success": True,
            "message": f"Connection to {source['name']} is configured",
            "checked_at": datetime.utcnow().isoformat(),
            "has_config": bool(config),
        }

    async def check_health(self) -> Dict[str, Any]:
        """Check health of all configured data sources."""
        sources = await self.list_sources()
        active_sources = [source for source in sources if source.get("status") == "active"]
        return {
            "total": len(sources),
            "active": len(active_sources),
            "healthy": len(sources) == len(active_sources) if sources else True,
            "sources": sources,
        }


def get_data_source_service(session: AsyncSession) -> DataSourceService:
    """Get a data source service instance."""
    return DataSourceService(session)
