# backend/database/base.py
from __future__ import annotations

"""
Declarative Base and shared SQLAlchemy metadata for the project.

- Provides a single Declarative Base (`Base`) that all ORM models should inherit from.
- Applies naming conventions to constraints and indexes so Alembic autogenerate stays stable.
- Includes an optional dev-only helper to create all tables quickly without Alembic.
"""

from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy import MetaData

# ---------------------------------------------------------------------------
# Naming conventions help Alembic generate stable, portable migrations.
# ---------------------------------------------------------------------------
NAMING_CONVENTIONS = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
metadata = MetaData(naming_convention=NAMING_CONVENTIONS)


class Base(DeclarativeBase):
    metadata = metadata

    # Optional: give each table a default __tablename__ = class name in snake_case
    @declared_attr.directive
    def __tablename__(cls) -> str:  # type: ignore[override]
        # Convert CamelCase -> snake_case (very basic)
        name: list[str] = []
        prev_lower = False
        for ch in cls.__name__:
            if ch.isupper() and prev_lower:
                name.append("_")
            name.append(ch.lower())
            prev_lower = ch.islower()
        return "".join(name)


# ---------------------------------------------------------------------------
# Dev-only helper: create tables without Alembic (local development).
# ---------------------------------------------------------------------------
async def create_all_for_dev(async_engine, *, drop_first: bool = False) -> None:
    """
    Create all tables using the current models mapped to `Base`.
    - Only for local/dev usage. Prefer Alembic for production environments.
    """
    from sqlalchemy.ext.asyncio import AsyncEngine

    if not isinstance(async_engine, AsyncEngine):
        raise TypeError("create_all_for_dev expects an AsyncEngine")

    async with async_engine.begin() as conn:
        if drop_first:
            await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


__all__ = [
    "Base",
    "metadata",
    "create_all_for_dev",
]
