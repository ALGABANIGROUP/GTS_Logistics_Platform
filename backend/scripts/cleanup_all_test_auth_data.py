from __future__ import annotations

import asyncio
import contextlib
import io
import os
import sys
from pathlib import Path

from sqlalchemy import delete, select, or_, func

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


async def main() -> None:
    AsyncSessionLocal = _load_async_session_local()

    # ✅ E2E cleanup patterns
    email_like_patterns = [
        "refresh-%@gabanistore.com",   # refresh-YYYY...@gabanistore.com
    ]
    full_name_like_patterns = [
        "REFRESH TEST %",              # REFRESH TEST YYYY...
    ]
    exact_emails = [
        "refresh-test@example.com",    # explicit test account
    ]

    # ⚠️ Optionally include this account if needed:
    # exact_emails.append("driver@gabanistore.com")

    def user_match_clause():
        clauses = []
        for p in email_like_patterns:
            clauses.append(User.email.like(p))
        for p in full_name_like_patterns:
            clauses.append(User.full_name.like(p))
        if exact_emails:
            clauses.append(User.email.in_(exact_emails))
        return or_(*clauses)

    # 1) DRY RUN
    async with AsyncSessionLocal() as s:
        rows = (await s.execute(
            select(User.id, User.email, User.full_name).where(user_match_clause())
        )).all()

    print(f"[dry-run] matched_users={len(rows)}")
    for uid, email, full_name in rows[:200]:
        print(f" - id={uid} email={email} full_name={full_name}")

    if not rows:
        # 2) Cleanup orphan refresh tokens only
        async with AsyncSessionLocal() as s:
            async with s.begin():
                # Find refresh tokens with no matching user
                orphan_ids = (await s.execute(
                    select(RefreshToken.id).outerjoin(User, User.id == RefreshToken.user_id).where(User.id.is_(None))
                )).scalars().all()

                if orphan_ids:
                    res_orphans = await s.execute(delete(RefreshToken).where(RefreshToken.id.in_(orphan_ids)))
                    print(f"[cleanup] deleted_orphan_refresh_tokens={int(res_orphans.rowcount or 0)}")
                else:
                    print("[cleanup] no orphan refresh tokens found")

        print("[done] nothing else to delete")
        return

    user_ids = [r[0] for r in rows]

    # 3) DELETE in transaction (tokens then users)
    async with AsyncSessionLocal() as s:
        async with s.begin():
            res_tokens = await s.execute(
                delete(RefreshToken).where(RefreshToken.user_id.in_(user_ids))
            )
            res_users = await s.execute(
                delete(User).where(User.id.in_(user_ids))
            )

    deleted_refresh_tokens = int(res_tokens.rowcount or 0)
    deleted_users = int(res_users.rowcount or 0)
    print(f"[cleanup] deleted_refresh_tokens={deleted_refresh_tokens} deleted_users={deleted_users}")

    # 4) Cleanup any remaining orphan tokens
    async with AsyncSessionLocal() as s:
        async with s.begin():
            orphan_ids = (await s.execute(
                select(RefreshToken.id).outerjoin(User, User.id == RefreshToken.user_id).where(User.id.is_(None))
            )).scalars().all()

            if orphan_ids:
                res_orphans = await s.execute(delete(RefreshToken).where(RefreshToken.id.in_(orphan_ids)))
                print(f"[cleanup] deleted_orphan_refresh_tokens={int(res_orphans.rowcount or 0)}")
            else:
                print("[cleanup] no orphan refresh tokens found")

    # 5) VERIFY
    async with AsyncSessionLocal() as s:
        remaining = (await s.execute(
            select(func.count()).select_from(User).where(user_match_clause())
        )).scalar_one()
        print(f"[verify] remaining_test_users={int(remaining)}")


if __name__ == "__main__":
    asyncio.run(main())

