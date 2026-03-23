# File: backend/tools/init_db_tables.py

from __future__ import annotations

import asyncio
from backend.database.base import Base, create_all_for_dev
from backend.database.connection import get_async_engine_from_env

# Import all ORM models here so that they are registered on Base.metadata
# (important: include User and any other models you want to make sure are created)
from backend.models.user import User  # noqa: F401
import backend.models.accounting_models  # noqa: F401
import backend.admin_control.models  # noqa: F401


async def main() -> None:
    """
    One-shot script to create all ORM tables (if they do not exist)
    in the current PostgreSQL database.

    It uses:
    - get_async_engine_from_env() -> reads ASYNC_DATABASE_URL / DATABASE_URL
    - create_all_for_dev() -> runs Base.metadata.create_all(bind=engine)
    """
    engine = get_async_engine_from_env()
    await create_all_for_dev(engine, drop_first=False)
    print("[init_db_tables] All ORM tables are ensured in the database.")


if __name__ == "__main__":
    asyncio.run(main())

