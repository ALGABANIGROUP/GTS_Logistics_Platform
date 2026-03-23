from __future__ import annotations

import os
import sys
import importlib
from logging.config import fileConfig
from pathlib import Path
from typing import Iterable

from alembic import context
from sqlalchemy import create_engine, pool

# =====================================================================
# PATH SETUP: Ensure Python can see the backend package from project root
# Example path:
#   D:\GTS Logistics\backend\alembic_migrations\env.py
# =====================================================================
THIS_FILE = Path(__file__).resolve()
ALEMBIC_DIR = THIS_FILE.parent            # ...\backend\alembic_migrations
BACKEND_ROOT = ALEMBIC_DIR.parent         # ...\backend
PROJECT_ROOT = BACKEND_ROOT.parent        # ...\GTS Logistics

# The key point: inject PROJECT_ROOT only,
# so "backend" resolves to D:\GTS Logistics\backend
project_root_str = str(PROJECT_ROOT)
if project_root_str not in sys.path:
    sys.path.insert(0, project_root_str)

# =====================================================================
# Load environment variables from .env at the project root
# =====================================================================
try:
    from dotenv import load_dotenv

    load_dotenv(PROJECT_ROOT / ".env")
except Exception:
    # If dotenv is missing or raises an error, continue without breaking
    pass

# =====================================================================
# Alembic config & logging
# =====================================================================
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def _first(*values: str | None) -> str:
    for v in values:
        if v and str(v).strip():
            return str(v).strip()
    return ""


def _mask_url(url: str) -> str:
    """Hide password in connection URL for safe printing."""
    try:
        if "://" in url and "@" in url:
            scheme_user, host_part = url.split("://", 1)[1].split("@", 1)
            if ":" in scheme_user:
                user, _ = scheme_user.split(":", 1)
                return url.replace(f"{user}:", f"{user}:****")
        return url
    except Exception:
        return url


# =====================================================================
# Determine the sync DB URL for Alembic
# =====================================================================
SYNC_DB_URL = _first(
    os.getenv("ALEMBIC_SYNC_DATABASE_URL"),
    os.getenv("DATABASE_URL"),
    os.getenv("SQLALCHEMY_DATABASE_URI"),
    config.get_main_option("sqlalchemy.url"),
)

if not SYNC_DB_URL:
    raise RuntimeError(
        "Alembic sync database URL is not set. "
        "Set ALEMBIC_SYNC_DATABASE_URL or DATABASE_URL in .env "
        "or sqlalchemy.url in alembic.ini."
    )

# Convert asyncpg URL to psycopg2 (synchronous) for Alembic
# This is necessary because Alembic requires a synchronous connection
if "+asyncpg://" in SYNC_DB_URL:
    SYNC_DB_URL = SYNC_DB_URL.replace("+asyncpg://", "+psycopg2://")

# Remove sslmode parameter which is incompatible with psycopg2
SYNC_DB_URL = SYNC_DB_URL.replace("?sslmode=require", "")
SYNC_DB_URL = SYNC_DB_URL.replace("&sslmode=require", "")

config.set_main_option("sqlalchemy.url", SYNC_DB_URL)
print(f"[alembic] sqlalchemy.url -> {_mask_url(SYNC_DB_URL)}")

# =====================================================================
# Import Base from SQLAlchemy models
# =====================================================================
from backend.database.base import Base  # noqa: E402
# Load the Open Web Leads model so it gets registered in Base.metadata
import backend.tools.open_web_leads.models  # noqa: F401
import backend.admin_control.models  # noqa: F401


def _import_all_models(models_root: Path, package_prefix: str = "backend.models") -> None:
    """
    Recursively import all Python modules under models_root so that
    declarative mappings are registered on Base.metadata.
    """
    if not models_root.exists():
        print(f"[alembic] warn: models dir not found: {models_root}")
        return

    skip_modules = {
        # Legacy aggregate modules that redeclare tables already defined in canonical model files.
        # Skipping them avoids duplicate-table warnings during Alembic metadata loading.
        "backend.models.models",
        "backend.models.support_models",
        # These modules duplicate tables already registered via legacy aggregate imports.
        "backend.models.shipment",
        "backend.models.message_log",
    }

    for path in models_root.rglob("*.py"):
        if path.name == "__init__.py":
            continue

        try:
            rel = path.relative_to(models_root)
        except ValueError:
            # Not actually under models_root
            continue

        rel_module = rel.with_suffix("")
        parts = rel_module.parts
        if not parts:
            continue

        mod = package_prefix + "." + ".".join(parts)

        if mod in skip_modules:
            continue

        try:
            importlib.import_module(mod)
        except Exception as exc:
            print(f"[alembic] warn: failed to import {mod}: {exc}")


MODELS_DIR = BACKEND_ROOT / "models"
_import_all_models(MODELS_DIR, "backend.models")

target_metadata = Base.metadata

# =====================================================================
# Offline / Online migration runners
# =====================================================================


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=SYNC_DB_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        include_schemas=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = create_engine(
        SYNC_DB_URL,
        poolclass=pool.NullPool,
        future=True,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            include_schemas=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

