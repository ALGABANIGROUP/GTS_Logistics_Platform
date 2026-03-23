# backend/_bootstrap_psycopg.py
"""
Small helper to safely import a PostgreSQL driver.

It tries to import psycopg (v3) first, then psycopg2 as a fallback.
Other modules can call load_psycopg() to get the loaded module.
"""

from __future__ import annotations

from typing import Any, Optional

_psycopg: Optional[Any] = None
_psycopg_error: Optional[BaseException] = None


def load_psycopg() -> Any:
    """
    Return a loaded psycopg driver module.

    Priority:
    1. psycopg  (v3)
    2. psycopg2

    Raises:
        RuntimeError if neither is available.
    """
    global _psycopg, _psycopg_error

    # If already initialized, just reuse the result
    if _psycopg is not None:
        return _psycopg
    if _psycopg_error is not None:
        raise RuntimeError("psycopg driver is not available") from _psycopg_error

    # Try psycopg (v3)
    try:
        import psycopg  # type: ignore[import]

        _psycopg = psycopg
        _psycopg_error = None
        return psycopg
    except Exception as exc:  # noqa: BLE001
        _psycopg_error = exc

    # Try psycopg2
    try:
        import psycopg2  # type: ignore[import]

        _psycopg = psycopg2
        _psycopg_error = None
        return psycopg2
    except Exception as exc:  # noqa: BLE001
        _psycopg_error = exc
        raise RuntimeError(
            "Neither psycopg (v3) nor psycopg2 could be imported. "
            "Install one of them, e.g.: "
            "'pip install psycopg[binary]' or 'pip install psycopg2-binary'."
        ) from exc
