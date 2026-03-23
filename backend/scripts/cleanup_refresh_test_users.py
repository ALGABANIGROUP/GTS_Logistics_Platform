from __future__ import annotations

import asyncio
import contextlib
import io
import sys
from pathlib import Path
from typing import Iterable, Sequence

from sqlalchemy import delete, or_, select

from backend.models.user import User  # type: ignore
from backend.models.refresh_token import RefreshToken  # type: ignore

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _load_async_session_local():
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        from backend.core import db_config  # type: ignore
    return db_config.AsyncSessionLocal


async def _fetch_targets(session) -> Sequence[tuple[int, str, str | None]]:

    stmt = select(User.id, User.email, User.full_name).where(
        or_(
            User.email.like("refresh-%@gabanistore.com"),
            User.full_name.like("REFRESH TEST %"),
        )
    )
    res = await session.execute(stmt)
    return res.all()


def _print_targets(rows: Iterable[tuple[int, str, str | None]]) -> None:
    for user_id, email, full_name in rows:
        print(f"- id={user_id} email={email} full_name={full_name}")


async def main() -> None:
    AsyncSessionLocal = _load_async_session_local()
    if AsyncSessionLocal is None:
        print("Database is not configured")
        return

    async with AsyncSessionLocal() as session:
        targets = await _fetch_targets(session)

    print(f"dry-run: matched users={len(targets)}")
    if targets:
        _print_targets(targets)

    if not targets:
        print("nothing to delete")
        print("deleted_users=0, deleted_refresh_tokens=0")
        return

    user_ids = [row[0] for row in targets]

    async with AsyncSessionLocal() as session:
        async with session.begin():

            res_tokens = await session.execute(
                delete(RefreshToken).where(RefreshToken.user_id.in_(user_ids))
            )
            res_users = await session.execute(
                delete(User).where(User.id.in_(user_ids))
            )

    deleted_refresh_tokens = int(res_tokens.rowcount or 0)
    deleted_users = int(res_users.rowcount or 0)
    print(f"deleted_users={deleted_users}, deleted_refresh_tokens={deleted_refresh_tokens}")


if __name__ == "__main__":
    asyncio.run(main())

