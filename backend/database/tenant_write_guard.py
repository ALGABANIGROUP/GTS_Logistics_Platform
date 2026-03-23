"""
DEV NO-OP tenant_write_guard

This project references backend.database.tenant_write_guard from database/config.py.
Provide minimal stubs so imports succeed in local dev.
Replace with real tenant write protection later.
"""

from __future__ import annotations

from contextlib import contextmanager, asynccontextmanager
from typing import Any, AsyncIterator, Iterator

def install_tenant_write_guard(*args: Any, **kwargs: Any) -> None:
    """
    Called by backend/database/config.py at startup.
    In dev, this is a no-op so imports succeed.
    """
    return

@contextmanager
def tenant_write_guard(*args: Any, **kwargs: Any) -> Iterator[None]:
    yield

@asynccontextmanager
async def tenant_write_guard_async(*args: Any, **kwargs: Any) -> AsyncIterator[None]:
    yield

def require_tenant_write_guard(*args: Any, **kwargs: Any) -> None:
    return
