from __future__ import annotations

import os
from pathlib import Path


def _load_env() -> None:
    """
    Deterministic env loading strategy for Backend.

    Priority:
      1) Explicit path via GTS_ENV_PATH (if set)
      2) Repo root .env (D:\\GTS Logistics\\.env)
      3) backend/.env only if root .env is missing (fallback for local dev templates)

    Notes:
      - Root .env is treated as single source of truth.
      - backend/.env will NOT override root values.
    """
    try:
        from dotenv import load_dotenv
    except Exception:
        return

    # 1) Explicit override path
    explicit = os.getenv("GTS_ENV_PATH", "").strip()
    if explicit:
        p = Path(explicit).expanduser().resolve()
        if p.exists():
            load_dotenv(dotenv_path=p, override=True)
            return

    # 2) Repo root .env
    root_env = Path(__file__).resolve().parents[1] / ".env"
    if root_env.exists():
        load_dotenv(dotenv_path=root_env, override=True)
        return

    # 3) Fallback: backend/.env (no override)
    backend_env = Path(__file__).resolve().parent / ".env"
    if backend_env.exists():
        load_dotenv(dotenv_path=backend_env, override=False)


_load_env()
