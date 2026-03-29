from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
import importlib
import logging
import os
import re
import sys
import time
import tracemalloc
from datetime import timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol

def _alias_backend_package(alias: str) -> None:
    if alias in sys.modules:
        return
    try:
        sys.modules[alias] = importlib.import_module(f"backend.{alias}")
    except Exception:
        return


for _pkg_alias in (
    "routes",
    "services",
    "bots",
    "ai",
    "core",
    "billing",
    "middleware",
    "monitoring",
    "webhooks",
    "api",
    "util",
    "utils",
    "maintenance",
    "notifications",
    "auth",
    "data",
    "database",
    "models",
    "security",
    "training_center",
    "social_media",
    "schedulers",
    "tms",
):
    _alias_backend_package(_pkg_alias)

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args: Any, **kwargs: Any) -> None:  # type: ignore
        return None
else:
    load_dotenv()

if not logging.getLogger().handlers:
    logging.basicConfig(level=os.getenv("GTS_LOG_LEVEL", "INFO"))
log = logging.getLogger("gts.main")
tracemalloc.start()


# Mount coordinator_analytics router for /coordinator endpoints (after app is defined)
coordinator_analytics_router = None
try:
    from routes.coordinator_analytics import router as coordinator_analytics_router
except Exception as e:
    log.warning("[main] coordinator_analytics router import failed: %s", e)

# Mount email_command_center router for /api/v1/email endpoints
email_command_center_router = None
try:
    from routes.email_command_center import router as email_command_center_router
except Exception as e:
    log.warning("[main] email_command_center router import failed: %s", e)

"""GTS backend entrypoint."""

try:
    import psycopg
    from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

    _orig_connect = psycopg.connect

    def _sanitize_conninfo(s: str) -> str:
        if not s or not isinstance(s, str):
            return s
        # URL style
        if s.startswith(("postgresql://", "postgres://", "postgresql+psycopg://")):
            try:
                sch, netloc, path, query, frag = urlsplit(s)
                # Drop legacy "ssl=" if present
                items = [(k, v) for (k, v) in parse_qsl(query, keep_blank_values=True) if k.lower() != "ssl"]
                # Ensure single sslmode=require and remove duplicates
                lower_keys = {k.lower() for k, _ in items}
                if "sslmode" not in lower_keys:
                    items.append(("sslmode", "require"))
                    items = [(k, ("require" if k.lower() == "sslmode" else v)) for k, v in items]
                return urlunsplit((sch, netloc, path, urlencode(items, doseq=True), frag))
            except Exception:
                pass
        # DSN key=val style
        s2 = re.sub(r'(?i)(^|\s)ssl\s*=\s*(true|false)\b', ' ', s)
        # normalize existing sslmode to require
        if re.search(r'(?i)\bsslmode\s*=', s2):
            s2 = re.sub(r'(?i)\bsslmode\s*=\s*\w+', 'sslmode=require', s2)
            s2 = (s2.strip() + " sslmode=require").strip()
        return s2

    def _connect_patched(*args, **kwargs):
        if args and isinstance(args[0], str):
            args = (_sanitize_conninfo(args[0]),) + args[1:]
        for key in ("conninfo", "dsn"):
            if key in kwargs and isinstance(kwargs[key], str):
                kwargs[key] = _sanitize_conninfo(kwargs[key])
        # psycopg3 does not accept 'ssl' kw; drop if present
        kwargs.pop("ssl", None)
        os.environ.setdefault("PGSSLMODE", "require")
        return _orig_connect(*args, **kwargs)

    psycopg.connect = _connect_patched
    log.info("[psycopg_dsn_hotfix] enabled")
except Exception as _e:
    log.warning("[psycopg_dsn_hotfix] skipped: %s", _e)
# ========= /Hotfix =========


# ========= Hotfix: optional finance env normalization =========
try:
    from util.finance_env_fix import apply as _gts_fin_env_fix  # type: ignore
    _gts_fin_env_fix()
except Exception as _e:
    log.info("[finance_env_fix] skipped: %s", _e)
# ========= /Hotfix =========


# ========= App & deps =========

from fastapi import FastAPI, Request, APIRouter, HTTPException, Depends
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.routing import APIRoute
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles

try:
    load_dotenv(override=False)
except Exception:
    pass


# ---------------- DB URL helpers (ensure async driver + sslmode=require) ----------------
CANDIDATE_DB_KEYS = [
    "ASYNC_DATABASE_URL",
    "DATABASE_URL",
    "SQLALCHEMY_DATABASE_URL",
    "DB_URL",
]


def _ensure_ssl_qs(url: str) -> str:
    if "sslmode=" in url or re.search(r'(?i)[?&]ssl=', url):
        # normalize any sslmode to require
        url = re.sub(r'(?i)sslmode=\w+', 'sslmode=require', url)
        # drop legacy ssl=true/false from query if present
        url = re.sub(r'(?i)([?&])ssl=(true|false)(&|$)', r'\1', url)
        url = re.sub(r'\?&', '?', url).rstrip('&')
        return url
    sep = '&' if '?' in url else '?'
    return f"{url}{sep}sslmode=require"


def _mk_async(url: str) -> str:
    # Upgrade postgresql:// to postgresql+asyncpg://
    if url.startswith("postgresql+asyncpg://"):
        return _ensure_ssl_qs(url)
    if url.startswith(("postgresql://", "postgres://")):
        url = "postgresql+asyncpg://" + url.split("://", 1)[1]
        return _ensure_ssl_qs(url)
    return url


def _resolve_db_url() -> Optional[str]:
    db_url: Optional[str] = None
    for k in CANDIDATE_DB_KEYS:
        v = os.getenv(k)
        if v and v.strip():
            db_url = v.strip()
            break
    if not db_url:
        return None
    if db_url.startswith(("postgresql", "postgres")):
        db_url = _mk_async(db_url)
    return db_url


def _normalize_db_env() -> None:
    """Make sure ASYNC_DATABASE_URL exists and all URLs enforce sslmode=require."""
    async_url = os.getenv("ASYNC_DATABASE_URL", "").strip()
    sync_url = os.getenv("DATABASE_URL", "").strip()
    if not async_url and sync_url.startswith(("postgresql://", "postgres://")):
        os.environ["ASYNC_DATABASE_URL"] = _mk_async(sync_url)
    # Normalize if already set
    if os.getenv("ASYNC_DATABASE_URL", ""):
        os.environ["ASYNC_DATABASE_URL"] = _mk_async(os.environ["ASYNC_DATABASE_URL"])
    if os.getenv("DATABASE_URL", ""):
        os.environ["DATABASE_URL"] = _ensure_ssl_qs(os.environ["DATABASE_URL"])


MEM_SNAPSHOT_ENABLED = os.getenv("ENABLE_MEM_SNAPSHOT", "false").lower() in ("1", "true", "yes")

def dump_memory_snapshot(path: Optional[str] = None, top: int = 50) -> str:
    """Take a tracemalloc snapshot and write the top allocations to a file."""
    file_path = path or f"mem_snapshot_{int(time.time())}.txt"
    snapshot = tracemalloc.take_snapshot()
    stats = snapshot.statistics("lineno")
    with open(file_path, "w", encoding="utf-8") as fh:
        fh.write(f"Top {top} memory allocations by line:\n")
        for stat in stats[:top]:
            fh.write(str(stat) + "\n")
    log.info("[memory] snapshot saved to %s (top=%d)", file_path, top)
    return file_path


# ---------------- Optional tracking provider (Vizion Eye shim) ----------------
class _SQLiteProviderShim:
    def __init__(self, conn: Any) -> None:
        self.db = conn

    def connect(self) -> Any:
        return self.db

    def log_event(
        self,
        name: str = "",
        message: str = "",
        meta: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        meta = (meta or {}) | (kwargs.get("meta", {}) if isinstance(kwargs.get("meta"), dict) else {})
        event = kwargs.get("event") or kwargs.get("name") or name
        try:
            cur = self.db.cursor()
            cur.execute(
                """CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY,
                    event TEXT, task_id INTEGER, task_title TEXT,
                    meta TEXT, ts TEXT DEFAULT (datetime('now'))
                )"""
            )
            import json
            cur.execute(
                "INSERT INTO events(event, task_id, task_title, meta) VALUES (?, ?, ?, ?)",
                (event, None, None, json.dumps({**(meta or {}), "message": message})),
            )
            self.db.commit()
        except Exception as e:
            log.debug("[SQLiteShim][%s] %s | %s (err=%s)", event, message, meta, e)


def _try_import_vizion_db() -> Optional[Any]:
    enable = os.getenv("VIZION_EYE_ENABLE", "0").lower() in ("1", "true", "yes")
    if not enable:
        log.info("[main] vizion_eye disabled via VIZION_EYE_ENABLE")
        return None
    try:
        from vizion_eye import db as _db  # type: ignore
        log.info("[main] vizion_eye provider found")
        return _db
    except Exception as e:
        log.warning("[main] vizion_eye provider not available: %s", e)
        try:
            import sqlite3
            sqlite_path = os.getenv("VIZION_EYE_SQLITE_PATH", "").strip()
            if sqlite_path:
                conn = sqlite3.connect(sqlite_path)
                shim = _SQLiteProviderShim(conn)
                log.info("[main] using SQLite shim for vizion_eye")
                return shim
        except Exception as e2:
            log.warning("[main] SQLite shim unavailable: %s", e2)
        return None


vizion_db = _try_import_vizion_db()
_vdb: Optional[Any] = None


# ---------------- Routers import helpers ----------------
def _try_import_router(abs_mod: str, rel_mod: str):
    try:
        mod = __import__(abs_mod, fromlist=["router"])
        return getattr(mod, "router")
    except Exception as e_abs:
        try:
            mod = __import__(rel_mod, fromlist=["router"])
            return getattr(mod, "router")
        except Exception as e_rel:
            log.warning("[main] failed to import %s / %s: %s | %s", abs_mod, rel_mod, e_abs, e_rel)
            return None

# Import marketing_router after helper is defined to avoid recursion
marketing_router = None
try:
    from routes.marketing import router as marketing_router
except Exception as e:
    log.warning("[main] failed to import marketing_router: %s", e)


def _try_import_attr(abs_mod: str, rel_mod: str, attr: str):
    try:
        mod = __import__(abs_mod, fromlist=[attr])
        return getattr(mod, attr)
    except Exception as e_abs:
        try:
            mod = __import__(rel_mod, fromlist=[attr])
            return getattr(mod, attr)
        except Exception as e_rel:
            log.warning("[main] failed to import attr '%s' from %s / %s: %s | %s", attr, abs_mod, rel_mod, e_abs, e_rel)
            return None


vizion_router      = _try_import_router("routes.vizion_routes", "routes.vizion_routes")
health_router      = _try_import_router("routes.health_routes", "routes.health_routes")
shipments_router   = _try_import_router("routes.shipments_pg_api", "routes.shipments_pg_api")
reports_router     = _try_import_router("routes.reports", "routes.reports")
reports_real_data_router = _try_import_router("routes.reports_real_data", "routes.reports_real_data")
bots_mock_api_router = _try_import_router("routes.bots_mock_api", "routes.bots_mock_api")
ai_reports_router  = _try_import_router("routes.ai_reports", "routes.ai_reports")
loadboards_router  = _try_import_router("routes.loadboards_routes", "routes.loadboards_routes")
truckerpath_router = _try_import_router("routes.truckerpath_routes", "routes.truckerpath_routes")
tp_webhook_router  = _try_import_router("routes.truckerpath_webhook", "routes.truckerpath_webhook")
users_router       = _try_import_router("routes.users_routes", "routes.users_routes")
email_center_router = _try_import_router("routes.email_center", "routes.email_center")
email_ai_stats_router = _try_import_router("routes.email_ai_stats", "routes.email_ai_stats")
email_bot_router = _try_import_router("routes.email_bot_routes", "routes.email_bot_routes")
admin_users_router  = _try_import_router("routes.admin_users", "routes.admin_users")
admin_unified_router = _try_import_router("routes.admin_unified", "routes.admin_unified")
# Bots availability (v1) - Legacy
try:
    from routes.bots_available import router as bots_available_router
    log.info("[main] bots_available imported successfully")
except Exception as e:
    log.warning(f"[main] bots_available import failed: {e}")
    bots_available_router = None

# Bots availability enhanced (v1) - Returns all available bots
try:
    from routes.bots_available_enhanced import router as bots_available_enhanced_router
    log.info("[main] bots_available_enhanced imported successfully")
except Exception as e:
    log.warning(f"[main] bots_available_enhanced import failed: {e}")
    bots_available_enhanced_router = None

# Customer service API (v1)
try:
    from routes.customer_service_api import router as customer_service_router
    log.info("[main] customer_service_router imported successfully")
except Exception as e:
    log.warning(f"[main] customer_service_router import failed: {e}")
    customer_service_router = None

# Policy Context router
try:
    from routes.policy_context import router as policy_context_router
    log.info("[main] policy_context_router imported successfully")
except Exception as e:
    log.warning(f"[main] policy_context_router import failed: {e}")
    policy_context_router = None
dispatch_router = _try_import_router("routes.dispatch_routes", "routes.dispatch_routes")
driver_router = _try_import_router("routes.driver_routes", "routes.driver_routes")
drivers_management_router = _try_import_router("routes.drivers_management_routes", "routes.drivers_management_routes")
safety_fleet_router = _try_import_router("routes.fleet_management_routes", "routes.fleet_management_routes")
fleet_live_router = _try_import_router("routes.fleet_live_routes", "routes.fleet_live_routes")
documents_upload_router = _try_import_router("routes.documents_upload_routes", "routes.documents_upload_routes")
safety_router = _try_import_router("routes.safety_api", "routes.safety_api")
frontend_compat_router = _try_import_router("routes.frontend_compat_routes", "routes.frontend_compat_routes")
ai_maintenance_chat_router = _try_import_router("routes.ai_maintenance_chat", "routes.ai_maintenance_chat")
bot_os_router = _try_import_router("routes.bot_os", "routes.bot_os")
transport_laws_router = _try_import_router("routes.transport_laws", "routes.transport_laws")
ai_bots_router = _try_import_router("routes.ai_bots_routes", "routes.ai_bots_routes")
bot_learning_router = _try_import_router("routes.bot_learning_routes", "routes.bot_learning_routes")
ws_live_router = _try_import_router("routes.ws_routes", "routes.ws_routes")
weather_router = _try_import_router("routes.weather", "routes.weather")
notifications_router = _try_import_router("routes.notifications_api", "routes.notifications_api")
freight_market_rates_router = _try_import_router("routes.freight_market_rates", "routes.freight_market_rates")
webhooks_router = _try_import_router("routes.webhooks", "routes.webhooks")
quo_webhook_router = _try_import_router("routes.quo_webhooks", "routes.quo_webhooks")
wise_webhooks_router = _try_import_router("routes.wise_webhooks", "routes.wise_webhooks")
stripe_webhooks_router = _try_import_router("routes.stripe_webhooks", "routes.stripe_webhooks")
ai_calls_router = _try_import_router("routes.ai_calls_api", "routes.ai_calls_api")
enhanced_call_router = _try_import_router("routes.call_webhooks", "routes.call_webhooks")
payment_webhooks_router = _try_import_router("webhooks.payment_webhooks", "webhooks.payment_webhooks")
billing_router = _try_import_router("billing.routes", "billing.routes")
admin_billing_router = _try_import_attr("billing.routes", "billing.routes", "admin_router")
portal_requests_router = _try_import_router("routes.portal_requests", "routes.portal_requests")
admin_portal_requests_router = _try_import_router("routes.admin_portal_requests", "routes.admin_portal_requests")
tms_requests_admin_router = _try_import_router("routes.tms_requests_admin", "routes.tms_requests_admin")
payment_gateway_router = _try_import_router("routes.payment_gateway", "routes.payment_gateway")
payment_routes_router = _try_import_router("routes.payment_routes", "routes.payment_routes")
seo_public_router = _try_import_router("routes.seo_public", "routes.seo_public")
channels_webhooks_router = _try_import_router("routes.channels_webhooks", "routes.channels_webhooks")
call_ai_router = _try_import_router("routes.call_ai_routes", "routes.call_ai_routes")
communications_router = _try_import_router("routes.communications", "routes.communications")
training_center_router = _try_import_router("routes.training_center", "routes.training_center")
bot_collaboration_router = _try_import_router("routes.bot_collaboration", "routes.bot_collaboration")
mapleload_canada_router = _try_import_router("routes.mapleload_canada_routes", "routes.mapleload_canada_routes")
freight_broker_canada_router = _try_import_router("routes.freight_broker_canada", "routes.freight_broker_canada")
freight_broker_learning_router = _try_import_router("routes.freight_broker_learning", "routes.freight_broker_learning")
finance_bot_learning_router = _try_import_router("routes.finance_bot_learning", "routes.finance_bot_learning")
operations_manager_learning_router = _try_import_router("routes.operations_manager_learning", "routes.operations_manager_learning")
documents_manager_learning_router = _try_import_router("routes.documents_manager_learning", "routes.documents_manager_learning")
safety_manager_learning_router = _try_import_router("routes.safety_manager_learning", "routes.safety_manager_learning")
general_manager_learning_router = _try_import_router("routes.general_manager_learning", "routes.general_manager_learning")
strategy_advisor_learning_router = _try_import_router("routes.strategy_advisor_learning", "routes.strategy_advisor_learning")
maintenance_dev_learning_router = _try_import_router("routes.maintenance_dev_learning", "routes.maintenance_dev_learning")
legal_consultant_learning_router = _try_import_router("routes.legal_consultant_learning", "routes.legal_consultant_learning")
information_coordinator_learning_router = _try_import_router("routes.information_coordinator_learning", "routes.information_coordinator_learning")
sales_team_learning_router = _try_import_router("routes.sales_team_learning", "routes.sales_team_learning")
system_admin_learning_router = _try_import_router("routes.system_admin_learning", "routes.system_admin_learning")
security_manager_learning_router = _try_import_router("routes.security_manager_learning", "routes.security_manager_learning")
mapleload_canada_learning_router = _try_import_router("routes.mapleload_canada_learning", "routes.mapleload_canada_learning")
partner_manager_learning_router = _try_import_router("routes.partner_manager_learning", "routes.partner_manager_learning")
maintenance_dev_enhanced_router = _try_import_router("routes.maintenance_dev_enhanced", "routes.maintenance_dev_enhanced")
executive_intelligence_router = _try_import_router(
    "routes.executive_intelligence_routes",
    "routes.executive_intelligence_routes",
)
partners_admin_router = _try_import_attr("api.routes.v1.partners", "api.routes.v1.partners", "admin_router")
partners_router = _try_import_attr("api.routes.v1.partners", "api.routes.v1.partners", "partner_router")

# Live Support Routes
live_support_router = _try_import_router("api.routes.live_support", "api.routes.live_support")

# Social Media Routes
try:
    from routes.social_media_routes import router as social_media_router, public_router as social_media_public_router
except Exception as e:
    log.warning("[main] failed to import social media routers: %s", e)
    social_media_router = None
    social_media_public_router = None

# Incident Response Routes
try:
    from api.routes.incident_routes import router as incident_routes_router
except Exception as e:
    log.warning("[main] failed to import incident routes: %s", e)
    incident_routes_router = None

# Chat Routes
try:
    from api.routes.chat_routes import router as chat_routes_router
except Exception as e:
    log.warning("[main] failed to import chat routes: %s", e)
    chat_routes_router = None

# System readiness + /api/v1/auth/me (optional)
try:
    from routes.system_readiness import router as system_readiness_router
except Exception:
    system_readiness_router = APIRouter()

    @system_readiness_router.get("/api/v1/system/readiness", include_in_schema=False)
    async def system_readiness():
        return {"ok": True, "status": "ok"}

try:
    from routes.auth_me import router as auth_me_router
except Exception as e_auth_me:
    log.error("[main] auth_me_router import failed: %s", e_auth_me)
    auth_me_router = None

try:
    from routes.auth_reset import router as auth_reset_router
except Exception as e_auth_reset:
    log.warning("[main] auth_reset routes unavailable: %s", e_auth_reset)
    auth_reset_router = None  # type: ignore

try:
    from routes.auth_routes import router as auth_users_router
except Exception as e_auth_users:
    log.warning("[main] auth_users routes unavailable: %s", e_auth_users)
    auth_users_router = None  # type: ignore

try:
    from routes.auth_extended import router as auth_extended_router
except Exception as e_auth_ext:
    log.warning("[main] auth_extended routes unavailable: %s", e_auth_ext)
    auth_extended_router = None  # type: ignore

try:
    from routes.auth import router as auth_router  # type: ignore
except Exception as e_auth:
    log.warning("[main] auth routes unavailable: %s", e_auth)
    auth_router = None  # type: ignore

# documents + auth with safe fallback
try:
    from routes.documents_routes import (  # type: ignore
        router as documents_router,
        ai_router as documents_ai_router,
    )
except Exception as e_docs_abs:
    try:
        from routes.documents_routes import (  # type: ignore
            router as documents_router,
            ai_router as documents_ai_router,
        )
    except Exception as e_docs_rel:
        log.warning("[main] documents routes unavailable: %s | %s", e_docs_abs, e_docs_rel)
        documents_router = None  # type: ignore
        documents_ai_router = None  # type: ignore

try:
    from api import api_router as public_api_router  # type: ignore
except Exception as e_public_api:
    log.warning("[main] public api router unavailable: %s", e_public_api)
    public_api_router = None  # type: ignore

ai_gateway_router = _try_import_router("routes.ai_gateway", "routes.ai_gateway")

# Finance routers
finance_router    = _try_import_router("routes.finance_routes", "routes.finance_routes")
finance_reports   = _try_import_router("routes.finance_reports", "routes.finance_reports")
finance_ai_router = _try_import_router("routes.finance_ai_routes", "routes.finance_ai_routes")
accounting_router = _try_import_router("routes.accounting_routes", "routes.accounting_routes")
unified_finance_router = _try_import_router("routes.unified_finance_routes", "routes.unified_finance_routes")

# Maintenance & Development routes
maintenance_ai_router = _try_import_router("routes.maintenance_ai", "routes.maintenance_ai")
maintenance_center_router = _try_import_router("routes.maintenance_center", "routes.maintenance_center")
dev_maintenance_router = _try_import_router("routes.dev_maintenance", "routes.dev_maintenance")
maintenance_router = _try_import_router("maintenance.router", "maintenance.router")

# System routes (health, metrics, status endpoints)
system_routes_router = _try_import_router("routes.system_routes", "routes.system_routes")

# Admin System routes
admin_system_router = _try_import_router("routes.admin_system", "routes.admin_system")
admin_data_sources_router = _try_import_router("routes.admin_data_sources", "routes.admin_data_sources")
admin_platform_settings_router = _try_import_router("routes.admin_platform_settings", "routes.admin_platform_settings")

# Try to import public platform settings router
try:
    from routes.admin_platform_settings import public_router as platform_public_router
except Exception:
    try:
        from routes.admin_platform_settings import public_router as platform_public_router  # type: ignore
    except Exception:
        platform_public_router = None

# Import Maintenance Mode middleware
try:
    from middleware.maintenance_mode import MaintenanceModeMiddleware
except Exception as e:
    log.warning("[main] MaintenanceModeMiddleware import failed: %s", e)
    MaintenanceModeMiddleware = None

# Import Max Upload Size middleware
try:
    from middleware.max_upload_size import MaxUploadSizeMiddleware
except Exception as e:
    log.warning("[main] MaxUploadSizeMiddleware import failed: %s", e)
    MaxUploadSizeMiddleware = None

# -------- Priority 1: Security Headers Middleware --------
try:
    from middleware.security_headers import (
        SecurityHeadersMiddleware,
        HTTPSRedirectMiddleware,
        RateLimitMiddleware as Priority1RateLimitMiddleware,
    )
except Exception as e:
    log.warning("[main] Priority 1 security middleware import failed: %s", e)
    SecurityHeadersMiddleware = None
    HTTPSRedirectMiddleware = None
    Priority1RateLimitMiddleware = None

# -------- Priority 1: Sentry Integration --------
try:
    from monitoring.sentry_integration import init_sentry
except Exception as e:
    log.warning("[main] Sentry integration import failed: %s", e)
    init_sentry = None

admin_tenants_router = _try_import_router("routes.admin_tenants", "routes.admin_tenants")
admin_audit_router = _try_import_router("routes.admin_audit", "routes.admin_audit")
admin_api_connections_router = _try_import_router("routes.admin_api_connections", "routes.admin_api_connections")
integrations_router = _try_import_router("routes.integrations_api", "routes.integrations_api")

# Machine Learning & Advanced Analytics routes
ml_router = _try_import_router("routes.ml_routes", "routes.ml_routes")
map_entities_router = _try_import_router("routes.map_entities", "routes.map_entities")

FINANCE_REPORTS_TOGGLE = os.getenv("ENABLE_FINANCE_REPORTS")
if FINANCE_REPORTS_TOGGLE is not None:
    log.info("[config] ENABLE_FINANCE_REPORTS=%s", FINANCE_REPORTS_TOGGLE)

# Import security helpers (note: provide a shim to accept list OR varargs)
try:
    from security.auth import (  # type: ignore
        require_roles as _require_roles_native,
        create_access_token,
        get_current_user,
    )
except Exception:
    _require_roles_native = None
    create_access_token = None  # type: ignore
    get_current_user = None  # type: ignore


def require_roles(*roles_or_list):
    """
    Compatibility shim:
    - allow require_roles("admin", "manager") OR require_roles(["admin","manager"])
    """
    if len(roles_or_list) == 1 and isinstance(roles_or_list[0], (list, tuple, set)):
        roles = list(roles_or_list[0])
    else:
        roles = list(roles_or_list)
    if _require_roles_native:
        return _require_roles_native(roles) if _takes_list(_require_roles_native) else _require_roles_native(*roles)  # type: ignore
    # fallback to permissive (dev) if no native
    from fastapi import Depends
    def _noop(user: dict = Depends(lambda: {"roles": roles})):  # noqa: ARG001
        return user
    return _noop


def _takes_list(fn) -> bool:
    try:
        import inspect
        ps = list(inspect.signature(fn).parameters.values())
        # Heuristic: native decorator might accept a single param 'roles'
        return len(ps) == 1
    except Exception:
        return False


# ---------------- Rate Limiting (slowapi) ----------------
try:
    from slowapi import Limiter
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    from slowapi.middleware import SlowAPIMiddleware
    from slowapi import _rate_limit_exceeded_handler  # type: ignore
except Exception:
    Limiter = None  # type: ignore


# ---------------- App / CORS ----------------
def generate_unique_id(route: APIRoute) -> str:
    tag = route.tags[0] if route.tags else "default"
    methods = "-".join(sorted((route.methods or [])))
    return f"{tag}:{route.name}:{methods}:{route.path}".replace("/", "_").replace("{", "").replace("}", "")


ENABLE_OPENAPI = os.getenv("ENABLE_OPENAPI", "false").lower() in ("1", "true", "yes")

@asynccontextmanager
async def app_lifespan(_app: FastAPI):
    late_lifespan = globals().get("_resolved_app_lifespan")
    if late_lifespan is None:
        yield
        return
    async with late_lifespan(_app):
        yield


app = FastAPI(
    title="Gabani Transport Solutions (GTS) Backend",
    version="1.7.2",
    lifespan=app_lifespan,
    description="""
    ## GTS Logistics SaaS Platform API
    
    Multi-tenant logistics platform with comprehensive features:
    
    ### 🚀 Core Features
    * **Multi-Tenancy**: Complete tenant isolation with subscription management
    * **Authentication**: JWT + RBAC + OAuth2 + 2FA support
    * **Bot Operating System (BOS)**: AI-powered automation and orchestration
    * **Real-time Communication**: WebSocket support for live updates
    * **Finance Module**: Expense tracking, reporting, and AI analytics
    * **Email Integration**: Advanced email center with bot workflows
    
    ### 🔐 Authentication
    All protected endpoints require JWT bearer token:
    ```
    Authorization: Bearer <your_access_token>
    ```
    
    To authenticate:
    1. POST `/auth/token` with credentials to get access token
    2. Use token in Authorization header for all requests
    3. Token includes user role and tenant context
    
    ### 📊 API Sections
    * **Auth**: Login, registration, profile, 2FA
    * **Admin**: User management, system configuration
    * **Bot OS**: Bot execution, commands, monitoring
    * **Finance**: Expenses, reports, AI analytics
    * **Email**: Email management, workflows, automation
    * **Real-time**: WebSocket endpoints for live data
    
    ### 🌍 Multi-Tenant Architecture
    All API requests automatically scope to authenticated user's tenant.
    Tenant context is derived from JWT token.
    
    ### ⚡ Performance
    * Async/await throughout for maximum concurrency
    * Redis caching on frequently accessed endpoints
    * Database connection pooling
    * Rate limiting on sensitive operations
    
    ### 📝 Documentation
    * **Swagger UI**: This interactive documentation (current page)
    * **ReDoc**: Alternative documentation at `/redoc`
    * **OpenAPI Schema**: JSON schema at `/openapi.json`
    
    For support and integration assistance, contact: support@gabanistore.com
    
    ## Contact
    * **Technical Support**: support@gabanistore.com
    * **Operations Team**: operations@gabanilogistics.com
    * **Website**: https://www.gabanilogistics.com
    """,
    generate_unique_id_function=generate_unique_id,
    docs_url="/docs" if ENABLE_OPENAPI else None,
    redoc_url="/redoc" if ENABLE_OPENAPI else None,
    openapi_url="/openapi.json" if ENABLE_OPENAPI else None,
    contact={
        "name": "GTS Support Team",
        "email": "support@gabanistore.com",
        "url": "https://gts-logistics.com"
    },
    license_info={
        "name": "Proprietary",
        "url": "https://gts-logistics.com/license"
    },
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,  # Hide schemas by default
        "docExpansion": "none",  # Collapse all endpoints
        "filter": True,  # Enable search
        "showRequestHeaders": True,
        "syntaxHighlight.theme": "monokai"
    }
)

UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

# ---------------- Sentry Integration ----------------
def _init_sentry():
    """Initialize Sentry for error tracking and performance monitoring."""
    sentry_dsn = os.getenv("SENTRY_DSN")
    if not sentry_dsn:
        log.info("[sentry] disabled - no SENTRY_DSN configured")
        return

    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        from sentry_sdk.integrations.logging import LoggingIntegration

        # Configure Sentry
        sentry_sdk.init(
            dsn=sentry_dsn,
            environment=os.getenv("SENTRY_ENVIRONMENT", "development"),
            traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
            integrations=[
                FastApiIntegration(
                    transaction_style="endpoint",
                ),
                SqlalchemyIntegration(),
                LoggingIntegration(
                    level=logging.INFO,  # Capture info and above as breadcrumbs
                    event_level=logging.ERROR,  # Send errors as events
                ),
            ],
            # Don't send events for health endpoints
            before_send=before_send_filter,
            # Tag events with user/tenant context
            before_breadcrumb=before_breadcrumb_filter,
        )

        # Set global tags
        sentry_sdk.set_tag("service", "gts-backend")
        sentry_sdk.set_tag("version", "1.7.2")

        log.info("[sentry] initialized with environment=%s, traces_sample_rate=%s",
                os.getenv("SENTRY_ENVIRONMENT", "development"),
                os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1"))

    except ImportError:
        log.warning("[sentry] sentry-sdk not installed, skipping initialization")
    except Exception as e:
        log.error("[sentry] initialization failed: %s", e)

def before_send_filter(event, hint):
    """Filter out health endpoint noise and sensitive data."""
    try:
        # Skip health check endpoints
        if event.get("request", {}).get("url", "").endswith(("/health", "/health/", "/health/sentry")):
            return None

        # Remove sensitive data from request
        if "request" in event:
            request = event["request"]
            # Remove auth headers
            if "headers" in request:
                headers = request["headers"]
                sensitive_headers = ["authorization", "cookie", "x-api-key", "x-auth-token"]
                for header in sensitive_headers:
                    headers.pop(header, None)
            # Remove sensitive query params
            if "query_string" in request:
                # Could filter out sensitive query params here if needed
                pass

        # Remove sensitive data from extra context
        if "extra" in event:
            extra = event["extra"]
            sensitive_keys = ["password", "token", "secret", "key", "dsn", "database_url"]
            for key in sensitive_keys:
                if key in extra:
                    extra[key] = "[FILTERED]"

        return event
    except Exception:
        # If filtering fails, still send the event
        return event

def before_breadcrumb_filter(crumb, hint):
    """Add user/tenant context to breadcrumbs."""
    try:
        # This will be enhanced by middleware to add user/tenant context
        return crumb
    except Exception:
        return crumb

# Initialize Sentry
_init_sentry()

# CORS: explicit known origins (dev + prod)
DEFAULT_CORS_ORIGINS = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "http://127.0.0.1:5174",
    "http://localhost:5174",
    "http://127.0.0.1:3000",
    "http://localhost:3000",
    "https://gabanilogistics.com",
    "https://www.gabanilogistics.com",
    "https://gtsdispatcher.com",
    "https://www.gtsdispatcher.com",
    "https://gts-logistics-platform.onrender.com",
]

_allowed = os.getenv("GTS_CORS_ORIGINS") or os.getenv("ALLOWED_ORIGINS") or ""
extra_origins = [o.strip() for o in _allowed.split(",") if o.strip()]
allow_origins = list(DEFAULT_CORS_ORIGINS)

for origin in extra_origins:
    if origin not in allow_origins:
        allow_origins.append(origin)

if "*" in allow_origins:
    allow_origins = [o for o in allow_origins if o != "*"]
    log.warning("[CORS] '*' origin is not allowed with credentials; removing '*'")

allow_credentials = True

# Explicit headers list for credentialed requests
# Authorization MUST be explicit when allow_credentials=True
# Wildcard (*) for headers does NOT work properly with credentials
allow_headers = [
    "Accept",
    "Accept-Language",
    "Content-Type",
    "Content-Language",
    "Authorization",  # ⚠️ CRITICAL: Must be explicit for Bearer tokens
    "X-Access-Token",
    "X-Requested-With",
    "X-CSRF-Token",
    "Cache-Control",
    "Pragma",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=allow_credentials,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=allow_headers,
    expose_headers=["*"],  # Allows frontend to read response headers
    max_age=600,  # Cache preflight responses for 10 minutes
)
log.info(f"[CORS] ✅ Configured with {len(allow_origins)} origins: {allow_origins}")
log.info(f"[CORS] ✅ Explicit headers (Authorization included): {allow_headers}")

# -------- Priority 1: Security Headers Middleware --------
if SecurityHeadersMiddleware is not None:
    app.add_middleware(SecurityHeadersMiddleware)
    log.info("[main] 🔐 Priority 1: SecurityHeadersMiddleware activated (11 OWASP headers)")

if HTTPSRedirectMiddleware is not None:
    app.add_middleware(HTTPSRedirectMiddleware)
    log.info("[main] 🔐 Priority 1: HTTPSRedirectMiddleware activated")

if Priority1RateLimitMiddleware is not None:
    app.add_middleware(Priority1RateLimitMiddleware)
    log.info("[main] 🔐 Priority 1: RateLimitMiddleware activated (1000 req/min)")

# -------- /Priority 1 --------

# ---------------- Maintenance Mode Middleware ----------------
if MaintenanceModeMiddleware is not None:
    app.add_middleware(MaintenanceModeMiddleware)
    log.info("[main] Maintenance Mode Middleware activated")

# ---------------- Max Upload Size Middleware ----------------
if MaxUploadSizeMiddleware is not None:
    app.add_middleware(MaxUploadSizeMiddleware)
    log.info("[main] Max Upload Size Middleware activated")

# ---------------- Sentry Context Middleware ----------------
    # from monitoring.sentry_context_middleware import SentryContextMiddleware
    # app.add_middleware(SentryContextMiddleware)

# ---------------- Rate limit wiring ----------------
if Limiter is not None:
    RATE_LIMIT = os.getenv("GTS_RATE_LIMIT", "60/minute").strip()
    limiter = Limiter(key_func=get_remote_address, default_limits=[RATE_LIMIT])
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore
    app.add_middleware(SlowAPIMiddleware)
else:
    log.warning("[main] slowapi not installed; rate limiting disabled")

# Public API router (register/verify)
if public_api_router:
    app.include_router(public_api_router, prefix="/api/v1")

OFFLINE = os.getenv("OFFLINE", "true").lower() in ("1", "true", "yes")
HEARTBEAT_INTERVAL_SEC = int(os.getenv("VIZION_HEARTBEAT_SEC", "30"))
INTERNAL_BASE_URL = os.getenv("INTERNAL_BASE_URL", "http://localhost:8000").rstrip("/")

OPS_MONITOR_ENABLED = os.getenv("OPS_MONITOR_ENABLED", "0").lower() in ("1", "true", "yes")
OPS_MONITOR_INTERVAL_SEC = max(5, int(os.getenv("OPS_MONITOR_INTERVAL_SEC", "120")))

DOCS_SCHEDULER_DISABLED = os.getenv("DISABLE_SCHEDULER", "false").lower() in ("1", "true", "yes")
DOCS_SCHEDULER_INTERVAL_SEC = max(60, int(os.getenv("DOCS_SCHEDULER_INTERVAL_SEC", "86400")))


# ---------------- Helpers ----------------
async def _vdb_call(func_name: str, *args, **kwargs):
    if not _vdb or not hasattr(_vdb, func_name):
        return None
    fn = getattr(_vdb, func_name)
    if asyncio.iscoroutinefunction(fn):
        return await fn(*args, **kwargs)
    return fn(*args, **kwargs)


async def vizion_log_event(event: str, message: str = "", **extra: Any) -> None:
    try:
        if _vdb and hasattr(_vdb, "log_event"):
            fn = getattr(_vdb, "log_event")
            for call in (
                lambda: fn(event, message, extra),
                lambda: fn(name=event, message=message, meta=extra),
                lambda: fn(event=event, message=message, meta=extra),
                lambda: fn(event),
            ):
                try:
                    return call()
                except TypeError:
                    continue
    except Exception as e:
        log.debug("[VIZION][ERR] failed to log event '%s': %s", event, e)


# ---------------- AI bots and registry ----------------
class AIBot(Protocol):
    name: str
    async def run(self, payload: dict) -> dict: ...
    async def status(self) -> dict: ...
    async def config(self) -> dict: ...


class _AIRegistry:
    def __init__(self) -> None:
        self._bots: Dict[str, AIBot] = {}

    def register(self, bot: AIBot) -> None:
        self._bots[bot.name] = bot

    def get(self, name: str) -> AIBot:
        if name not in self._bots:
            raise KeyError(name)
        return self._bots[name]

    def list(self) -> Dict[str, str]:
        return {k: v.__class__.__name__ for k, v in self._bots.items()}


ai_registry = _AIRegistry()

from sqlalchemy import select as _select, func as _func
try:
    from database.session import get_async_session as _get_session  # type: ignore
except Exception:
    try:
        from database.session import get_async_session as _get_session  # type: ignore
    except Exception:
        _get_session = None  # type: ignore

try:
    from models.financial import Expense, ExpenseStatus  # type: ignore
except Exception:
    try:
        from models.financial import Expense, ExpenseStatus  # type: ignore
    except Exception:
        Expense = None
        ExpenseStatus = None


class FinanceBot:
    name = "finance_bot"

    async def run(self, payload: dict) -> dict:
        if _get_session is None or Expense is None:
            return {"ok": True, "summary": {"total_expenses": 0.0, "total_revenue": 120000.0, "net_profit": 120000.0}}

        # safe session handling
        async with _get_session() as session:
            total_q = await session.execute(_select(_func.coalesce(_func.sum(Expense.amount), 0.0)))
            total_expenses = float(total_q.scalar() or 0.0)

            by_status_q = await session.execute(
                _select(Expense.status, _func.coalesce(_func.sum(Expense.amount), 0.0)).group_by(Expense.status)
            )
            by_status = {str(s): float(a) for (s, a) in by_status_q.all()}

            by_vendor_q = await session.execute(
                _select(Expense.vendor, _func.coalesce(_func.sum(Expense.amount), 0.0)).group_by(Expense.vendor)
            )
            by_vendor = {str(v or "Unknown"): float(a) for (v, a) in by_vendor_q.all()}

            total_revenue = 120000.0
            net_profit = total_revenue - total_expenses

        return {
            "ok": True,
            "summary": {
                "total_expenses": round(total_expenses, 2),
                "total_revenue": round(total_revenue, 2),
                "net_profit": round(net_profit, 2),
                "by_status": by_status,
                "by_vendor": by_vendor,
            },
        }

    async def status(self) -> dict:
        return {"ok": True, "role": "finance_bot"}

    async def config(self) -> dict:
        return {"source": "db/expenses", "routes": ["/finance/summary", "/finance/reports/summary"]}


class FreightBrokerBot:
    name = "freight_broker"

    def __init__(self) -> None:
        self.base_url = INTERNAL_BASE_URL

    async def _fetch_loads(self, limit: int, prefs: Dict[str, Any]) -> List[Dict[str, Any]]:
        params = {"limit": limit}
        if prefs.get("origin"): params["origin"] = prefs["origin"]
        if prefs.get("destination"): params["destination"] = prefs["destination"]
        if prefs.get("equipment"): params["equipment"] = prefs["equipment"]
        import httpx
        url = f"{self.base_url}/truckerpath/loads"
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.get(url, params=params)
            if r.status_code // 100 != 2:
                raise HTTPException(status_code=502, detail=f"/truckerpath/loads -> {r.status_code}")
            data = r.json()
            return list(data.get("loads") or [])

    async def _create_shipment(self, payload: Dict[str, Any]) -> Optional[int]:
        import httpx
        urls = [f"{self.base_url}/api/v1/shipments/shipments/", f"{self.base_url}/shipments/"]
        async with httpx.AsyncClient(timeout=30) as client:
            for url in urls:
                try:
                    r = await client.post(url, json=payload)
                    if r.status_code // 100 == 2:
                        data = r.json()
                        sid = data.get("id") or data.get("shipment_id") or data.get("data", {}).get("id")
                        if sid:
                            return int(sid)
                except Exception:
                    continue
        return None

    def _payload_from_load(self, load: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        def _s(v): return str(v or "").strip()
        def _f(v):
            if v is None: return None
            try: return float(str(v).replace(",", "").strip())
            except Exception: return None

        pickup = _s(load.get("origin") or load.get("pickup") or load.get("pickup_location") or load.get("pickup_city") or "Unknown Pickup")
        dropoff= _s(load.get("destination") or load.get("dropoff") or load.get("dropoff_location") or load.get("dropoff_city") or "Unknown Dropoff")
        equip  = _s(load.get("equipment_type") or load.get("equipment") or load.get("trailer_type") or "")
        notes  = _s(load.get("description") or load.get("notes") or "")
        price  = _f(load.get("rate") or load.get("price") or load.get("rate_usd"))
        weight = _s(load.get("weight") or "")
        length = _s(load.get("length") or "")
        lat = load.get("pickup_latitude") or load.get("latitude")
        lng = load.get("pickup_longitude") or load.get("longitude")
        try:
            lat = float(lat) if lat not in (None, "") else None
            lng = float(lng) if lng not in (None, "") else None
        except Exception:
            lat, lng = None, None

        return {
            "user_id": int(user_id),
            "pickup_location": pickup,
            "dropoff_location": dropoff,
            "trailer_type": (equip or None),
            "rate": price,
            "weight": (weight or None),
            "length": (length or None),
            "load_size": _s(load.get("load_size") or ""),
            "description": (notes or None),
            "status": "Imported",
            "latitude": lat,
            "longitude": lng,
            "recurring_type": None,
            "days": None,
        }

    async def _post_to_truckerpath(self, load_payload: Dict[str, Any]) -> bool:
        import httpx
        url = f"{self.base_url}/truckerpath/post-load"
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(url, json=load_payload)
            if r.status_code // 100 != 2:
                return False
            data = r.json()
            return bool(data.get("ok"))

    async def run(self, payload: dict) -> dict:
        user_id = int((payload or {}).get("user_id") or 1)
        limit = int((payload or {}).get("max_loads") or 10)
        prefs = (payload or {}).get("preferences", {}) or {}
        auto_post = bool((payload or {}).get("auto_post_truckerpath", False))
        loads = await self._fetch_loads(limit=limit, prefs=prefs)
        if not loads:
            return {"ok": False, "message": "No loads returned", "shipment_ids": []}
        created_ids: List[int] = []
        posted_ok = 0
        posted_fail = 0
        for item in loads:
            shipment_payload = self._payload_from_load(item, user_id=user_id)
            sid = await self._create_shipment(shipment_payload)
            if sid:
                created_ids.append(sid)
                if auto_post:
                    ok = await self._post_to_truckerpath({
                        "company_id": os.getenv("TRUCKERPATH_COMPANY_ID"),
                        "contact_info": {
                            "contact_email": os.getenv("TRUCKERPATH_CONTACT_EMAIL"),
                            "contact_first_name": os.getenv("TRUCKERPATH_CONTACT_FIRST", "Ops"),
                            "contact_last_name": os.getenv("TRUCKERPATH_CONTACT_LAST", "Team"),
                            "contact_phone_number": os.getenv("TRUCKERPATH_CONTACT_PHONE"),
                            "contact_phone_ext": os.getenv("TRUCKERPATH_CONTACT_EXT", ""),
                        },
                        "shipment_info": {
                            "equipment": [shipment_payload.get("trailer_type") or "Dry Van"],
                            "load_size": shipment_payload.get("load_size") or "FULL",
                            "description": shipment_payload.get("description"),
                            "shipment_weight": shipment_payload.get("weight"),
                            "shipment_dimensions": {},
                            "requirements": None,
                            "stop_list": [
                                {"type": "PICKUP", "city": shipment_payload.get("pickup_location"), "lat": shipment_payload.get("latitude"), "lng": shipment_payload.get("longitude")},
                                {"type": "DROPOFF","city": shipment_payload.get("dropoff_location")},
                            ],
                        },
                    })
                    if ok: posted_ok += 1
                    else:  posted_fail += 1
        return {
            "ok": True,
            "message": f"Created {len(created_ids)} shipments. Posted {posted_ok} to TruckerPath ({posted_fail} failed).",
            "shipment_ids": created_ids,
            "posted_to_truckerpath": posted_ok,
            "failed_postings": posted_fail,
            "preferences": prefs,
        }

    async def status(self) -> dict:
        return {"ok": True, "role": "freight_broker", "source": "truckerpath_routes"}

    async def config(self) -> dict:
        return {"routes": ["/truckerpath/loads", "/truckerpath/post-load"], "default_limit": 10}


DocsClient = None
_parse_command = None
try:
    from ai.roles.bot_documents import DocsClient as _DocsClient, _parse_command as _CMD  # type: ignore
    DocsClient = _DocsClient
    _parse_command = _CMD
except Exception:
    try:
        from ai.roles.bot_documents import DocsClient as _DocsClient, _parse_command as _CMD  # type: ignore
        DocsClient = _DocsClient
        _parse_command = _CMD
    except Exception:
        DocsClient = None
        _parse_command = None


class DocumentsManagerBot:
    name = "documents_manager"

    async def run(self, payload: dict) -> dict:
        import traceback
        try:
            if DocsClient is None:
                return {"ok": False, "error": "DocsClient not available", "hint": "backend/ai/roles/bot_documents.py"}
            api = DocsClient(base_url=INTERNAL_BASE_URL)
            text_cmd = (payload or {}).get("command")
            if isinstance(text_cmd, str) and text_cmd.strip() and _parse_command is not None:
                cmd, args = _parse_command(text_cmd)
                if cmd == "status": return {"ok": True, "data": await api.get_status()}
                if cmd == "list_expiring": return {"ok": True, "data": await api.list_expiring()}
                if cmd == "extend":
                    rid_val = args.get("id");  days_val = args.get("days")
                    if rid_val is None: raise HTTPException(status_code=400, detail="extend requires 'id' argument")
                    if days_val is None: raise HTTPException(status_code=400, detail="extend requires 'days' argument")
                    return {"ok": True, "data": await api.extend(int(rid_val), int(days_val))}
                if cmd == "notify": return {"ok": True, "data": await api.notify_expiring()}
                return {"ok": True, "help": ["status", "list expiring", "extend <id> <days>", "notify"]}
            action = (payload or {}).get("action")
            if action == "status": return {"ok": True, "data": await api.get_status()}
            if action == "list_expiring": return {"ok": True, "data": await api.list_expiring()}
            if action == "extend":
                rid = int((payload or {}).get("id") or 0)
                days = int((payload or {}).get("days") or 0)
                if rid <= 0 or days <= 0:
                    raise HTTPException(status_code=400, detail="extend requires id > 0 and days > 0")
                return {"ok": True, "data": await api.extend(rid, days)}
            if action == "notify": return {"ok": True, "data": await api.notify_expiring()}
            return {"ok": True, "data": await api.get_status()}
        except Exception as e:
            print("[DocumentsManagerBot][run] Exception:")
            traceback.print_exc()
            return {"ok": False, "error": str(e), "traceback": traceback.format_exc()}

    async def status(self) -> dict:
        return {"ok": True, "role": "documents_manager", "client": bool(DocsClient)}

    async def config(self) -> dict:
        return {"expiring_endpoint": "/documents/expiring-soon/", "notify_endpoint": "/documents/notify-expiring/"}


import inspect
try:
    from services.report_service import compile_system_report  # type: ignore
except Exception:
    try:
        from services.report_service import compile_system_report  # type: ignore
    except Exception:
        compile_system_report = None  # type: ignore


class GeneralManagerBot:
    name = "general_manager"

    async def run(self, payload: dict) -> dict:
        if compile_system_report is None:
            freight_task = asyncio.create_task(ai_registry.get("freight_broker").run({"max_loads": int((payload or {}).get("max_loads") or 3)}))
            finance_task = asyncio.create_task(ai_registry.get("finance_bot").run({}))
            docs_task = asyncio.create_task(ai_registry.get("documents_manager").run({"action": "status"}))
            freight, finance, docs = await asyncio.gather(freight_task, finance_task, docs_task)
            return {"ok": True, "report": {"freight": freight, "finance": finance, "documents": docs}, "fallback": True}

        period = (payload or {}).get("period", "week")
        start_date = (payload or {}).get("start_date")
        end_date = (payload or {}).get("end_date")
        fmt = (payload or {}).get("format", "json")
        include_kpis = bool((payload or {}).get("include_kpis", True))
        kwargs: Dict[str, Any] = {}
        try:
            sig = inspect.signature(compile_system_report)  # type: ignore
            supported = set(sig.parameters.keys())
            candidate = {"period": period, "start_date": start_date, "end_date": end_date, "fmt": fmt, "format": fmt, "include_kpis": include_kpis}
            for k, v in candidate.items():
                if k in supported: kwargs[k] = v
        except Exception:
            kwargs = {"period": period, "format": fmt}
        try:
            result = await compile_system_report(**kwargs)  # type: ignore
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Report generation failed: {e}")
        return {"ok": True, "report": result, "period": period, "format": fmt}

    async def status(self) -> dict:
        return {
            "ok": True,
            "role": "general_manager",
            "report_service": compile_system_report is not None,
            "metrics": {
                "activeTeams": {"value": 3, "target": 5, "status": "active"},
                "totalEmployees": {"value": 42, "target": 50, "status": "active"},
                "operationsStatus": {"value": "92%", "trend": "positive"},
                "responseTime": {"value": "0.5h", "trend": "neutral"},
            },
            "teams": [
                {"name": "Operations", "lead": "Ahmed", "status": "active"},
                {"name": "Finance", "lead": "Sara", "status": "active"},
                {"name": "HR", "lead": "Mona", "status": "active"}
            ],
            "pending": [],
            "activities": [],
            "reports": [],
        }

    async def config(self) -> dict:
        return {"inputs": ["period", "start_date", "end_date", "format", "include_kpis"]}


class OperationsManagerBot:
    name = "operations_manager"

    async def run(self, payload: dict) -> dict:
        import traceback
        try:
            steps = []
            prefs = (payload or {}).get("freight_preferences", {}) or {}
            steps.append({"step": "fetch_loads", "status": "started"})
            fb = await ai_registry.get("freight_broker").run({"source": (payload or {}).get("source", "mock"), "preferences": prefs, "max_loads": int((payload or {}).get("max_loads") or 5)})
            steps[-1]["status"] = "done"
            steps.append({"step": "finance_snapshot", "status": "started"})
            fin = await ai_registry.get("finance_bot").run({})
            steps[-1]["status"] = "done"
            await vizion_log_event("ops_orchestration", "ran ops manager", loads=fb.get("count", 0), expenses=fin.get("summary", {}).get("total_expenses", 0))
            return {"ok": True, "steps": steps, "loads_taken": fb.get("count", 0), "finance": fin.get("summary", {})}
        except Exception as e:
            print("[OperationsManagerBot][run] Exception:")
            traceback.print_exc()
            return {"ok": False, "error": str(e), "traceback": traceback.format_exc()}

def register_core_bots() -> None:
    try:
        from backend.bots.general_manager import GeneralManagerBot as RuntimeGeneralManagerBot

        gm_bot = RuntimeGeneralManagerBot()
        gm_bot.name = "general_manager"
        gm_bot.display_name = "AI General Manager"
        ai_registry.register(gm_bot)
        log.info("[register] General Manager bot registered from dedicated module")
    except Exception as e:
        log.warning(f"[register] Failed to register dedicated General Manager bot, using fallback: {e}")
        ai_registry.register(GeneralManagerBot())
    try:
        from backend.bots.freight_broker import FreightBrokerBot as RuntimeFreightBrokerBot
        from backend.ai.registry_fill import AliasBot

        freight_bot = RuntimeFreightBrokerBot()
        freight_bot.name = "freight_broker"
        freight_bot.display_name = "AI Freight Broker"
        ai_registry.register(freight_bot)
        ai_registry.register(AliasBot(name="freight_bot", target_key="freight_broker"))
        log.info("[register] Freight Broker bot registered with alias")
    except Exception as e:
        log.warning(f"[register] Failed to register dedicated Freight Broker bot, using fallback: {e}")
        ai_registry.register(FreightBrokerBot())
    try:
        from backend.bots.operations_manager import OperationsManagerBot as RuntimeOperationsManagerBot
        from backend.ai.registry_fill import AliasBot

        ops_bot = RuntimeOperationsManagerBot()
        ops_bot.name = "operations_manager"
        ops_bot.display_name = "AI Operations Manager"
        ai_registry.register(ops_bot)
        ai_registry.register(AliasBot(name="operations_bot", target_key="operations_manager"))
        ai_registry.register(AliasBot(name="operations_manager_bot", target_key="operations_manager"))
        log.info("[register] Operations Manager bot registered with aliases")
    except Exception as e:
        log.warning(f"[register] Failed to register dedicated Operations Manager bot, using fallback: {e}")
        ai_registry.register(OperationsManagerBot())
    try:
        from backend.bots.information_coordinator import InformationCoordinatorBot as RuntimeInformationCoordinatorBot

        info_bot = RuntimeInformationCoordinatorBot()
        info_bot.name = "information_coordinator"
        info_bot.display_name = "AI Information Coordinator"
        ai_registry.register(info_bot)
        log.info("[register] Information Coordinator bot registered from dedicated module")
    except Exception as e:
        log.warning(f"[register] Failed to register dedicated Information Coordinator bot: {e}")
    try:
        from backend.bots.legal_bot import LegalBot as RuntimeLegalBot
        from backend.ai.registry_fill import AliasBot

        legal_bot = RuntimeLegalBot()
        legal_bot.name = "legal_bot"
        legal_bot.display_name = "AI Legal Consultant"
        ai_registry.register(legal_bot)
        ai_registry.register(AliasBot(name="legal_consultant", target_key="legal_bot"))
        ai_registry.register(AliasBot(name="legal_counsel", target_key="legal_bot"))
        log.info("[register] Legal Consultant bot registered with aliases")
    except Exception as e:
        log.warning(f"[register] Failed to register dedicated Legal Consultant bot: {e}")
    try:
        from backend.bots.security_manager import SecurityManagerBot as RuntimeSecurityManagerBot
        from backend.ai.registry_fill import AliasBot

        security_bot = RuntimeSecurityManagerBot()
        security_bot.name = "security_bot"
        security_bot.display_name = "AI Security Manager"
        ai_registry.register(security_bot)
        ai_registry.register(AliasBot(name="security_manager", target_key="security_bot"))
        ai_registry.register(AliasBot(name="security_manager_bot", target_key="security_bot"))
        log.info("[register] Security Manager bot registered with aliases")
    except Exception as e:
        log.warning(f"[register] Failed to register dedicated Security Manager bot, using fallback: {e}")
        from backend.bots.security_bot import SecurityBot as RuntimeSecurityBot
        ai_registry.register(RuntimeSecurityBot())
    try:
        from backend.bots.system_manager import SystemManagerBot as RuntimeSystemManagerBot
        from backend.ai.registry_fill import AliasBot

        system_bot = RuntimeSystemManagerBot()
        system_bot.name = "system_bot"
        system_bot.display_name = "AI System Manager"
        ai_registry.register(system_bot)
        ai_registry.register(AliasBot(name="system_manager", target_key="system_bot"))
        ai_registry.register(AliasBot(name="system_manager_bot", target_key="system_bot"))
        ai_registry.register(AliasBot(name="system_admin", target_key="system_bot"))
        log.info("[register] System Manager bot registered with aliases")
    except Exception as e:
        log.warning(f"[register] Failed to register dedicated System Manager bot, using fallback: {e}")
        ai_registry.register(SystemBot())
    try:
        from backend.bots.maintenance_dev import MaintenanceDevBot as RuntimeMaintenanceDevBot
        from backend.ai.registry_fill import AliasBot

        maintenance_bot = RuntimeMaintenanceDevBot()
        maintenance_bot.name = "maintenance_dev"
        maintenance_bot.display_name = "AI Maintenance Dev"
        ai_registry.register(maintenance_bot)
        ai_registry.register(AliasBot(name="dev_maintenance", target_key="maintenance_dev"))
        ai_registry.register(AliasBot(name="maintenance_dev_bot", target_key="maintenance_dev"))
        log.info("[register] Maintenance Dev bot registered with aliases")
    except Exception as e:
        log.warning(f"[register] Failed to register dedicated Maintenance Dev bot: {e}")
    ai_registry.register(FinanceBot())
    ai_registry.register(DocumentsManagerBot())
    try:
        from backend.bots.sales_intelligence import SalesIntelligenceBot
        from backend.ai.registry_fill import AliasBot

        sales_bot = SalesIntelligenceBot()
        sales_bot.name = "sales_bot"
        sales_bot.display_name = "Sales Bot"
        ai_registry.register(sales_bot)
        ai_registry.register(AliasBot(name="sales", target_key="sales_bot"))
        ai_registry.register(AliasBot(name="sales_intelligence", target_key="sales_bot"))
        ai_registry.register(AliasBot(name="sales_team", target_key="sales_bot"))
        log.info("[register] Sales bot registered with aliases")
    except Exception as e:
        log.warning(f"[register] Failed to register Sales bot: {e}")
    try:
        from backend.bots.marketing_manager import MarketingManagerBot as RuntimeMarketingManagerBot
        from backend.ai.registry_fill import AliasBot

        marketing_bot = RuntimeMarketingManagerBot()
        marketing_bot.name = "marketing_manager"
        marketing_bot.display_name = "AI Marketing Manager"
        ai_registry.register(marketing_bot)
        ai_registry.register(AliasBot(name="marketing_manager_bot", target_key="marketing_manager"))
        ai_registry.register(AliasBot(name="marketing_bot", target_key="marketing_manager"))
        log.info("[register] Marketing Manager bot registered with aliases")
    except Exception as e:
        log.warning(f"[register] Failed to register Marketing Manager bot: {e}")
    try:
        from backend.bots.intelligence_bot import IntelligenceBot
        from backend.ai.registry_fill import AliasBot

        intelligence_bot = IntelligenceBot()
        intelligence_bot.name = "intelligence_bot"
        intelligence_bot.display_name = "AI Intelligence Bot"
        ai_registry.register(intelligence_bot)
        ai_registry.register(AliasBot(name="intelligence", target_key="intelligence_bot"))
        ai_registry.register(AliasBot(name="executive_intelligence", target_key="intelligence_bot"))
        log.info("[register] Intelligence bot registered with aliases")
    except Exception as e:
        log.warning(f"[register] Failed to register Intelligence bot: {e}")
    try:
        from backend.bots.trainer_bot import TrainerBotRuntime
        from backend.ai.registry_fill import AliasBot

        trainer_bot = TrainerBotRuntime()
        trainer_bot.name = "trainer_bot"
        trainer_bot.display_name = "AI Trainer Bot"
        ai_registry.register(trainer_bot)
        ai_registry.register(AliasBot(name="trainer", target_key="trainer_bot"))
        ai_registry.register(AliasBot(name="training_bot", target_key="trainer_bot"))
        log.info("[register] Trainer bot registered with aliases")
    except Exception as e:
        log.warning(f"[register] Failed to register Trainer bot: {e}")
    try:
        from backend.safety.main import AISafetyManagerBot
        from backend.ai.registry_fill import AliasBot

        safety_bot = AISafetyManagerBot()
        safety_bot.name = "safety_bot"
        safety_bot.display_name = "Safety Bot"
        ai_registry.register(safety_bot)
        ai_registry.register(AliasBot(name="safety_manager", target_key="safety_bot"))
        ai_registry.register(AliasBot(name="safety", target_key="safety_bot"))
        log.info("[register] Safety bot registered with aliases")
    except Exception as e:
        log.warning(f"[register] Failed to register Safety bot from safety manager runtime, using fallback: {e}")
        try:
            from backend.bots.safety_bot import SafetyBot
            from backend.ai.registry_fill import AliasBot

            safety_bot = SafetyBot()
            safety_bot.name = "safety_bot"
            safety_bot.display_name = "Safety Bot"
            ai_registry.register(safety_bot)
            ai_registry.register(AliasBot(name="safety_manager", target_key="safety_bot"))
            ai_registry.register(AliasBot(name="safety", target_key="safety_bot"))
            log.info("[register] Fallback Safety bot registered with aliases")
        except Exception as fallback_exc:
            log.warning(f"[register] Failed to register Safety bot fallback: {fallback_exc}")
    try:
        from backend.bots.ai_dispatcher import AIDispatcherBot
        ai_registry.register(AIDispatcherBot())
        log.info("[register] AI Dispatcher bot registered")
    except Exception as e:
        log.warning(f"[register] Failed to register AI Dispatcher bot: {e}")
    
    # Register MapleLoad Canada bot
    try:
        from backend.bots.mapleload_canada import MapleLoadCanadaBot
        from backend.ai.registry_fill import AliasBot

        mapleload_bot = MapleLoadCanadaBot()
        mapleload_bot.name = "mapleload_bot"
        mapleload_bot.bot_key = "mapleload_bot"
        mapleload_bot.display_name = "AI MapleLoad Canada"
        ai_registry.register(mapleload_bot)
        ai_registry.register(AliasBot(name="mapleload", target_key="mapleload_bot"))
        ai_registry.register(AliasBot(name="mapleload_canada", target_key="mapleload_bot"))
        log.info("[register] MapleLoad Canada bot registered with aliases")
    except Exception as e:
        log.warning(f"[register] Failed to register MapleLoad Canada bot: {e}")


ai_router = APIRouter(prefix="/ai", tags=["AI"])


@ai_router.get("/bots")
async def list_bots():
    return {"bots": ai_registry.list()}


def _get_bot_or_404(name: str) -> AIBot:
    try:
        return ai_registry.get(name)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Bot '{name}' not found")


@ai_router.post("/{name}/run")
async def run_bot(name: str, payload: dict):
    bot = _get_bot_or_404(name)
    result = bot.run(payload or {})
    # Handle both sync and async run methods
    if hasattr(result, '__await__'):
        return await result
    return result


@ai_router.get("/{name}/status")
async def bot_status(name: str):
    bot = _get_bot_or_404(name)
    if hasattr(bot, 'status') and callable(bot.status):
        result = bot.status()
        if hasattr(result, '__await__'):
            return await result
        return result
    return {
        "name": name,
        "status": "active",
        "ready": True,
    }


@ai_router.get("/{name}/config")
async def bot_config(name: str):
    bot = _get_bot_or_404(name)
    if hasattr(bot, 'config') and callable(bot.config):
        result = bot.config()
        if hasattr(result, '__await__'):
            return await result
        return result
    return {
        "name": name,
        "description": getattr(bot, 'description', ''),
        "capabilities": ["run"],
    }


# ---------------- Optional background monitor & scheduler ----------------
_ops_task: Optional[asyncio.Task] = None
_docs_task: Optional[asyncio.Task] = None
_legal_updates_task: Optional[asyncio.Task] = None
_learning_scheduler_task: Optional[asyncio.Task] = None
_maintenance_auto_repair_task: Optional[asyncio.Task] = None
_telegram_task: Optional[asyncio.Task] = None


async def _ops_monitor_loop():
    await vizion_log_event("ops_monitor_started", "Ops monitor loop started", enabled=OPS_MONITOR_ENABLED)
    while True:
        try:
            payload = {"max_loads": 5, "source": "mock"}
            res = await ai_registry.get("operations_manager").run(payload)
            await vizion_log_event("ops_monitor_tick", "Ops run completed", created=res.get("loads_taken", 0))
        except Exception as e:
            await vizion_log_event("ops_monitor_error", f"loop error: {e}")
        await asyncio.sleep(OPS_MONITOR_INTERVAL_SEC)


async def _docs_scheduler_loop():
    import httpx
    while True:
        try:
            if create_access_token is None:
                raise RuntimeError("create_access_token not available")
            token = create_access_token(
                subject="scheduler",
                email="scheduler@gts.local",
                role="admin",
                expires_delta=timedelta(minutes=1440),
            )
            headers = {"Authorization": f"Bearer {token}"}
            url = f"{INTERNAL_BASE_URL}/documents/notify-expiring/"
            async with httpx.AsyncClient(timeout=30) as client:
                await client.post(url, headers=headers)
            await vizion_log_event("docs_scheduler", "notified expiring documents", endpoint=url)
        except Exception as e:
            await vizion_log_event("docs_scheduler_error", f"loop error: {e}")
        await asyncio.sleep(DOCS_SCHEDULER_INTERVAL_SEC)


# ---------------- Startup/Shutdown ----------------
async def on_startup():
    global _vdb, _ops_task, _docs_task, _legal_updates_task, _learning_scheduler_task, _maintenance_auto_repair_task, _telegram_task
    
    # -------- Priority 1: Initialize Sentry --------
    if init_sentry is not None:
        try:
            from backend.config import Settings
            settings = Settings()
            init_sentry(
                dsn=getattr(settings, 'SENTRY_DSN', None),
                environment=getattr(settings, 'SENTRY_ENVIRONMENT', 'development'),
                traces_sample_rate=getattr(settings, 'SENTRY_TRACES_SAMPLE_RATE', 0.1),
                enable=getattr(settings, 'ENABLE_SENTRY', False),
            )
            log.info("[startup] 🎯 Priority 1: Sentry error tracking initialized")
        except Exception as e:
            log.warning("[startup] Failed to initialize Sentry: %s", e)
    # -------- /Priority 1 --------
    
    _normalize_db_env()
    db_url = _resolve_db_url()
    if db_url:
        os.environ["ASYNC_DATABASE_URL"] = db_url  # normalized
    log.info("[startup] ASYNC_DATABASE_URL set: %s", "SET" if os.getenv("ASYNC_DATABASE_URL") else "NOT SET")

    # Load technical settings into cache at startup
    try:
        from database.session import get_async_session
        from utils.technical_settings import get_technical_settings
        
        async for db in get_async_session():
            settings = await get_technical_settings(db)
            log.info("[startup] Technical settings loaded: sessionTimeout=%s, maxUploadSize=%s, maintenanceMode=%s, apiRateLimit=%s",
                     settings.get("sessionTimeout"), settings.get("maxUploadSize"), 
                     settings.get("maintenanceMode"), settings.get("apiRateLimit"))
            break
    except Exception as e:
        log.warning("[startup] Failed to preload technical settings: %s", e)

    async def _ensure_user_columns() -> None:
        try:
            from core.db_config import engine as core_engine

            if core_engine is None:
                log.warning("[startup] DB engine not configured; skipping column checks")
                return

            async with core_engine.begin() as conn:
                result = await conn.execute(
                    text(
                        """
                        SELECT EXISTS (
                            SELECT 1 FROM information_schema.columns
                            WHERE table_name = 'users' AND column_name = 'system_type'
                        )
                        """
                    )
                )
                system_type_exists = bool(result.scalar())

                result = await conn.execute(
                    text(
                        """
                        SELECT EXISTS (
                            SELECT 1 FROM information_schema.columns
                            WHERE table_name = 'users' AND column_name = 'subscription_tier'
                        )
                        """
                    )
                )
                subscription_tier_exists = bool(result.scalar())

                result = await conn.execute(
                    text(
                        """
                        SELECT EXISTS (
                            SELECT 1 FROM information_schema.columns
                            WHERE table_name = 'users' AND column_name = 'last_login'
                        )
                        """
                    )
                )
                last_login_exists = bool(result.scalar())

                result = await conn.execute(
                    text(
                        """
                        SELECT EXISTS (
                            SELECT 1 FROM information_schema.columns
                            WHERE table_name = 'users' AND column_name = 'assigned_bots'
                        )
                        """
                    )
                )
                assigned_bots_exists = bool(result.scalar())

                result = await conn.execute(
                    text(
                        """
                        SELECT EXISTS (
                            SELECT 1 FROM information_schema.columns
                            WHERE table_name = 'users' AND column_name = 'features'
                        )
                        """
                    )
                )
                features_exists = bool(result.scalar())

                if not system_type_exists:
                    await conn.execute(text("ALTER TABLE users ADD COLUMN system_type VARCHAR(50) NULL"))
                    log.info("[startup] Added users.system_type column")

                if not subscription_tier_exists:
                    await conn.execute(
                        text("ALTER TABLE users ADD COLUMN subscription_tier VARCHAR(50) NULL DEFAULT 'demo'")
                    )
                    log.info("[startup] Added users.subscription_tier column")

                if not last_login_exists:
                    await conn.execute(text("ALTER TABLE users ADD COLUMN last_login TIMESTAMP WITH TIME ZONE NULL"))
                    log.info("[startup] Added users.last_login column")

                if not assigned_bots_exists:
                    await conn.execute(text("ALTER TABLE users ADD COLUMN assigned_bots JSON NULL"))
                    log.info("[startup] Added users.assigned_bots column")

                if not features_exists:
                    await conn.execute(text("ALTER TABLE users ADD COLUMN features JSON NULL"))
                    log.info("[startup] Added users.features column")
        except Exception as exc:
            log.warning("[startup] Skipped user column auto-migration (core): %s", exc)

        # Also ensure columns for database.config engine (auth/session path)
        try:
            from database.config import get_sessionmaker, init_engines

            init_engines()
            maker = get_sessionmaker()
            async with maker() as session:
                result = await session.execute(
                    text(
                        """
                        SELECT EXISTS (
                            SELECT 1 FROM information_schema.columns
                            WHERE table_name = 'users' AND column_name = 'system_type'
                        )
                        """
                    )
                )
                system_type_exists = bool(result.scalar())

                result = await session.execute(
                    text(
                        """
                        SELECT EXISTS (
                            SELECT 1 FROM information_schema.columns
                            WHERE table_name = 'users' AND column_name = 'subscription_tier'
                        )
                        """
                    )
                )
                subscription_tier_exists = bool(result.scalar())

                result = await session.execute(
                    text(
                        """
                        SELECT EXISTS (
                            SELECT 1 FROM information_schema.columns
                            WHERE table_name = 'users' AND column_name = 'assigned_bots'
                        )
                        """
                    )
                )
                assigned_bots_exists = bool(result.scalar())

                result = await session.execute(
                    text(
                        """
                        SELECT EXISTS (
                            SELECT 1 FROM information_schema.columns
                            WHERE table_name = 'users' AND column_name = 'features'
                        )
                        """
                    )
                )
                features_exists = bool(result.scalar())

                if not system_type_exists:
                    await session.execute(text("ALTER TABLE users ADD COLUMN system_type VARCHAR(50) NULL"))
                    log.info("[startup] Added users.system_type column (config)")

                if not subscription_tier_exists:
                    await session.execute(
                        text("ALTER TABLE users ADD COLUMN subscription_tier VARCHAR(50) NULL DEFAULT 'demo'")
                    )
                    log.info("[startup] Added users.subscription_tier column (config)")

                if not assigned_bots_exists:
                    await session.execute(text("ALTER TABLE users ADD COLUMN assigned_bots JSON NULL"))
                    log.info("[startup] Added users.assigned_bots column (config)")

                if not features_exists:
                    await session.execute(text("ALTER TABLE users ADD COLUMN features JSON NULL"))
                    log.info("[startup] Added users.features column (config)")

                await session.commit()
        except Exception as exc:
            log.warning("[startup] Skipped user column auto-migration (config): %s", exc)

    provider = _try_import_vizion_db()
    if provider is not None:
        prov = provider
        try:
            if hasattr(prov, "connect") and callable(getattr(prov, "connect")):
                maybe_conn = prov.connect()
                conn = await maybe_conn if asyncio.iscoroutine(maybe_conn) else maybe_conn
                try:
                    setattr(prov, "db", conn)
                except Exception:
                    pass
                _vdb = prov
                app.state.vdb = prov
                # await vizion_log_event("vizion_eye", "connected", enabled=True, provider="vizion_eye.module")
            elif hasattr(prov, "db"):
                _vdb = prov
                app.state.vdb = prov
                # await vizion_log_event("vizion_eye", "connected (shim)", enabled=True, provider="vizion_eye.shim")
        except Exception as e:
            log.warning("[startup] provider.connect() failed: %s", e)

    try:
        register_core_bots()
    except Exception as e:
        log.warning("[startup] register_core_bots failed: %s", e)

    try:
        await _ensure_user_columns()
    except Exception as e:
        log.warning("[startup] user column check failed: %s", e)
    try:
        from backend.ai.registry_fill import ensure_all_bots_registered

        ensure_all_bots_registered(ai_registry)
    except Exception as e:
        log.warning("[startup] ensure_all_bots_registered failed: %s", e)
    log.info("[startup] AI core bots registered: %s", ai_registry.list())

    try:
        await _start_bot_os()
    except Exception as e:
        log.warning("[startup] BotOS initialization failed: %s", e)

    try:
        from services.learning_bootstrap import register_default_learning_bots, learning_scheduler_loop

        learning_result = register_default_learning_bots()
        log.info(
            "[startup] Learning bots registered: total=%s enabled=%s",
            learning_result.get("stats", {}).get("total_bots_registered"),
            learning_result.get("stats", {}).get("enabled_bots"),
        )
        _learning_scheduler_task = asyncio.create_task(learning_scheduler_loop(interval_hours=6))
        log.info("[startup] learning scheduler started (every 6 hours)")
    except Exception as e:
        log.warning("[startup] learning bootstrap failed: %s", e)

    try:
        from services.db_maintenance import ensure_maintenance_indexes
        maintenance_result = await ensure_maintenance_indexes()
        log.info(
            "[startup] maintenance indexes ensured: executed=%s skipped=%s",
            len(maintenance_result.get("executed", [])),
            len(maintenance_result.get("skipped", [])),
        )
    except Exception as e:
        log.warning("[startup] maintenance index bootstrap failed: %s", e)

    try:
        from ai.maintenance_dev_enhanced import maintenance_auto_repair_loop
        _maintenance_auto_repair_task = asyncio.create_task(maintenance_auto_repair_loop(interval_hours=6))
        log.info("[startup] maintenance auto-repair scheduler started (every 6 hours)")
    except Exception as e:
        log.warning("[startup] maintenance auto-repair scheduler failed: %s", e)

    try:
        email_polling_enabled = os.getenv("EMAIL_POLLING_ENABLED", "0").lower() in ("1", "true", "yes")
        if email_polling_enabled:
            from services.email_scheduler import start_email_polling_task

            start_email_polling_task()
            log.info("[startup] email polling scheduler started")
        else:
            log.info("[startup] email polling scheduler disabled")
    except Exception as e:
        log.warning("[startup] email polling scheduler failed: %s", e)
    
    # Start backup scheduler
    try:
        from utils.backup_scheduler import start_backup_scheduler
        await start_backup_scheduler()
        log.info("[startup] Backup scheduler started")
    except Exception as e:
        log.warning("[startup] Failed to start backup scheduler: %s", e)
    
    try:
        log.info("[main] Mounted routes: %s", [str(r.path) for r in app.router.routes])
    except Exception as e:
        log.warning("[main] failed to list routes: %s", e)

    if False:  # OPS_MONITOR_ENABLED:
        _ops_task = asyncio.create_task(_ops_monitor_loop())

    if False:  # not DOCS_SCHEDULER_DISABLED:
        _docs_task = asyncio.create_task(_docs_scheduler_loop())

    try:
        legal_enabled = os.getenv("LEGAL_UPDATES_ENABLED", "1").lower() in ("1", "true", "yes")
        if legal_enabled:
            from services.legal_updates_monitor import legal_updates_scheduler_loop

            _legal_updates_task = asyncio.create_task(legal_updates_scheduler_loop())
            log.info("[startup] legal updates scheduler started")
    except Exception as e:
        log.warning("[startup] legal updates scheduler failed: %s", e)

    # Initialize Market Data Service and MapleLoad Canada Bot
    try:
        from backend.services.market_data_service import initialize_market_data_service
        from backend.bots.mapleload_canada import initialize_mapleload_bot
        
        await initialize_market_data_service()
        await initialize_mapleload_bot()
        log.info("[startup] Market data service and MapleLoad bot initialized")
    except Exception as e:
        log.warning("[startup] Failed to initialize market services: %s", e)

    # Initialize Telegram Bot
    try:
        telegram_enabled = os.getenv("TELEGRAM_ENABLED", "false").lower() in ("1", "true", "yes")
        if telegram_enabled:
            from telegram_bot import start_telegram_bot
            _telegram_task = asyncio.create_task(start_telegram_bot())
            log.info("[startup] Telegram bot started")
        else:
            log.info("[startup] Telegram bot disabled")
    except Exception as e:
        log.warning("[startup] Failed to start Telegram bot: %s", e)

    # Startup route logging for Render / debugging
    # try:
    #     log.info("[startup] ========== REGISTERED ROUTES ==========")
    #     count = 0
    #     for r in app.router.routes:
    #         methods = ",".join(sorted(getattr(r, "methods", []) or []))
    #         path = getattr(r, "path", "")
    #         name = getattr(r, "name", "")
    #         log.info("[startup]   %-10s %-40s (%s)", methods or "-", path, name)
    #         count += 1
    #     log.info("[startup] Total routes registered: %d", count)
    # except Exception as e:
    #     log.warning("[startup] route logging failed: %s", e)


async def on_shutdown():
    global _ops_task, _docs_task, _legal_updates_task, _learning_scheduler_task, _maintenance_auto_repair_task
    for task in (_ops_task, _docs_task, _legal_updates_task, _learning_scheduler_task, _maintenance_auto_repair_task):
        if task:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            except Exception:
                pass
    try:
        from services.email_scheduler import stop_email_polling_task

        await stop_email_polling_task()
    except Exception:
        pass
    try:
        bot_os = getattr(app.state, "bot_os", None)
        if bot_os is not None:
            await bot_os.shutdown()
            log.info("[shutdown] BotOS stopped")
    except Exception as exc:
        log.warning("[shutdown] BotOS shutdown failed: %s", exc)


async def _start_bot_os() -> None:
    session_factory = _get_session
    if session_factory is None:
        raise RuntimeError("async session factory is unavailable")

    from backend.bots import init_bot_os

    bot_os = init_bot_os(
        bot_names_provider=lambda: list(ai_registry.list().keys()),
        bot_getter=ai_registry.get,
        session_factory=session_factory,
    )
    await bot_os.start()
    app.state.bot_os = bot_os
    log.info("[startup] BotOS initialized successfully")


@asynccontextmanager
async def _resolved_app_lifespan(_app: FastAPI):
    await on_startup()
    try:
        yield
    finally:
        await on_shutdown()
    
    # Shutdown Market Data Service and MapleLoad Canada Bot
    try:
        from backend.services.market_data_service import shutdown_market_data_service
        from backend.bots.mapleload_canada import shutdown_mapleload_bot
        
        await shutdown_market_data_service()
        await shutdown_mapleload_bot()
        log.info("[shutdown] Market data service and MapleLoad bot shut down")
    except Exception as e:
        log.warning("[shutdown] Error shutting down market services: %s", e)


# ---------------- Routers mounting ----------------
try:
    from routes.ai_bots_backend import router as ai_bots_backend_router
    app.include_router(ai_bots_backend_router)
    log.info("[main] ai_bots_backend router mounted at /ai/*")
except Exception as e:
    log.warning("[main] ai_bots_backend router mount failed: %s", e)
if system_readiness_router:
    app.include_router(system_readiness_router)
try:
    if auth_router and not auth_me_router:
        # Mount legacy auth routes only when the modern /api/v1/auth router is unavailable.
        app.include_router(auth_router, prefix="/api/v1")
    elif auth_router and auth_me_router:
        log.info("[main] legacy auth_router skipped to avoid /api/v1/auth route shadowing")
except Exception as e:
    log.warning("[router] auth mount failed: %s", e)

if auth_me_router:
    app.include_router(auth_me_router)
    log.info("[main] auth_me_router mounted at /api/v1/auth")
else:
    log.warning("[main] auth_me_router disabled")

if live_support_router:
    app.include_router(live_support_router)
    log.info("[main] live_support_router mounted at /api/v1/support")
else:
    log.warning("[main] live_support_router not available")

if incident_routes_router:
    app.include_router(incident_routes_router)
    log.info("[main] incident_routes_router mounted at /api/v1/incidents")
else:
    log.warning("[main] incident_routes_router not available")

if chat_routes_router:
    app.include_router(chat_routes_router)
    log.info("[main] chat_routes_router mounted at /api/v1/chat")
else:
    log.warning("[main] chat_routes_router not available")

if auth_reset_router:
    app.include_router(auth_reset_router)

# auth_users_router duplicates /users/me surface; users_routes is the canonical source.
# Keep the module importable for legacy code, but do not mount it.
if auth_users_router:
    log.info("[main] auth_users_router skipped to avoid duplicate /users/* routes")

if auth_extended_router:
    app.include_router(auth_extended_router)

# MapleLoad Canada Bot - Mount early to avoid route conflict with bots_available_enhanced
if mapleload_canada_router:
    try:
        app.include_router(mapleload_canada_router)
        log.info("[main] mapleload_canada bot routes mounted at /api/v1/ai/bots/mapleload-canada/*")
        log.info(f"[main] mapleload_canada router has {len(mapleload_canada_router.routes)} routes")
    except Exception as e:
        log.error(f"[main] FAILED to mount mapleload_canada router: {e}", exc_info=True)

# Freight Broker Canada - Canadian logistics load board
if freight_broker_canada_router:
    try:
        app.include_router(freight_broker_canada_router)
        log.info("[main] freight_broker_canada routes mounted at /api/v1/freight/*")
    except Exception as e:
        log.error(f"[main] FAILED to mount freight_broker_canada router: {e}", exc_info=True)

if freight_broker_learning_router:
    app.include_router(freight_broker_learning_router)
    log.info("[main] freight_broker_learning mounted at /api/v1/freight-broker/*")

if finance_bot_learning_router:
    app.include_router(finance_bot_learning_router)
    log.info("[main] finance_bot_learning mounted at /api/v1/finance-bot/*")

if operations_manager_learning_router:
    app.include_router(operations_manager_learning_router)
    log.info("[main] operations_manager_learning mounted at /api/v1/operations-manager/*")

if documents_manager_learning_router:
    app.include_router(documents_manager_learning_router)
    log.info("[main] documents_manager_learning mounted at /api/v1/documents-manager/*")

if safety_manager_learning_router:
    app.include_router(safety_manager_learning_router)
    log.info("[main] safety_manager_learning mounted at /api/v1/safety-manager/*")

if general_manager_learning_router:
    app.include_router(general_manager_learning_router)
    log.info("[main] general_manager_learning mounted at /api/v1/general-manager/*")

if strategy_advisor_learning_router:
    app.include_router(strategy_advisor_learning_router)
    log.info("[main] strategy_advisor_learning mounted at /api/v1/strategy-advisor/*")

if maintenance_dev_learning_router:
    app.include_router(maintenance_dev_learning_router)
    log.info("[main] maintenance_dev_learning mounted at /api/v1/maintenance-dev/*")

if legal_consultant_learning_router:
    app.include_router(legal_consultant_learning_router)
    log.info("[main] legal_consultant_learning mounted at /api/v1/legal-consultant/*")

if information_coordinator_learning_router:
    app.include_router(information_coordinator_learning_router)
    log.info("[main] information_coordinator_learning mounted at /api/v1/information-coordinator/*")

if sales_team_learning_router:
    app.include_router(sales_team_learning_router)
    log.info("[main] sales_team_learning mounted at /api/v1/sales-team/*")

if system_admin_learning_router:
    app.include_router(system_admin_learning_router)
    log.info("[main] system_admin_learning mounted at /api/v1/system-admin/*")

if security_manager_learning_router:
    app.include_router(security_manager_learning_router)
    log.info("[main] security_manager_learning mounted at /api/v1/security-manager/*")

if mapleload_canada_learning_router:
    app.include_router(mapleload_canada_learning_router)
    log.info("[main] mapleload_canada_learning mounted at /api/v1/mapleload-canada/*")

if partner_manager_learning_router:
    app.include_router(partner_manager_learning_router)
    log.info("[main] partner_manager_learning mounted at /api/v1/partner-manager/*")

if partners_admin_router:
    app.include_router(
        partners_admin_router,
        dependencies=[Depends(require_roles(["admin", "super_admin"]))],
    )
    log.info("[main] partners admin routes mounted at /api/v1/partners/*")

if partners_router:
    app.include_router(
        partners_router,
        dependencies=[Depends(require_roles(["partner", "admin", "super_admin"]))],
    )
    log.info("[main] partner self-service routes mounted at /api/v1/partner/*")

if maintenance_dev_enhanced_router:
    app.include_router(maintenance_dev_enhanced_router)
    log.info("[main] maintenance_dev_enhanced mounted at /api/v1/maintenance-dev/*")

# Bots availability (v1)
if bots_available_router:
    app.include_router(bots_available_router)
    log.info("[main] bots_available mounted at /api/v1/bots/*")

# Bots availability enhanced (v1) - Returns all available bots
log.info(f"[main] bots_available_enhanced_router is {bots_available_enhanced_router}")
if bots_available_enhanced_router:
    log.info("[main] mounting bots_available_enhanced_router...")
    app.include_router(bots_available_enhanced_router)
    log.info("[main] bots_available_enhanced mounted at /api/v1/ai/bots")

# Bots Mock API (v1) - Mock data for bot operating system
if bots_mock_api_router:
    app.include_router(bots_mock_api_router)
    log.info("[main] bots_mock_api mounted at /api/v1/bots")

# Customer service API (v1)
if customer_service_router:
    app.include_router(customer_service_router)
    log.info("[main] customer_service_api mounted at /api/v1/customer-service")

# Dispatch APIs
if dispatch_router:
    app.include_router(dispatch_router)
    log.info("[main] dispatch_routes mounted at /api/v1/dispatch/*")

if driver_router:
    app.include_router(driver_router)
    log.info("[main] driver_routes mounted at /api/v1/driver/*")

if drivers_management_router:
    app.include_router(drivers_management_router)
    log.info("[main] drivers_management_routes mounted at /api/v1/drivers/*")

if safety_fleet_router:
    app.include_router(safety_fleet_router)
    log.info("[main] fleet_management_routes mounted at /api/v1/fleet/*")

if fleet_live_router:
    app.include_router(fleet_live_router)
    log.info("[main] fleet_live_routes mounted at /api/v1/fleet/live/*")

# Safety API (v1)
if safety_router:
    app.include_router(safety_router)
    log.info("[main] safety_api mounted at /api/v1/safety")

# Information Coordinator analytics routes
if coordinator_analytics_router:
    try:
        app.include_router(coordinator_analytics_router)
        log.info("[main] coordinator_analytics router mounted at /coordinator/*")
    except Exception as e:
        log.warning("[main] coordinator_analytics router mount failed: %s", e)
else:
    log.warning("[main] coordinator_analytics router not available")

# Email Command Center router (DISABLED - using real email_center_router instead)
# if email_command_center_router:
#     try:
#         app.include_router(email_command_center_router)
#         log.info("[main] email_command_center router mounted at /api/v1/email/*")
#     except Exception as e:
#         log.warning("[main] email_command_center router mount failed: %s", e)
# else:
#     log.warning("[main] email_command_center router not available")

# Platform Infrastructure Expenses router (CRUD operations)
platform_infrastructure_router = None
try:
    from routes.platform_infrastructure_routes import router as platform_infrastructure_router
    app.include_router(platform_infrastructure_router)
    log.info("[main] platform_infrastructure router mounted at /api/v1/platform/*")
except Exception as e:
    log.warning("[main] platform_infrastructure router mount failed: %s", e)

# Invoice Extractor router (AI-powered invoice data extraction)
try:
    from routes.invoice_extractor import router as invoice_extractor_router
    app.include_router(invoice_extractor_router, prefix="/api/v1/platform/expenses")
    log.info("[main] invoice_extractor router mounted at /api/v1/platform/expenses/extract-invoice")
except Exception as e:
    log.warning("[main] invoice_extractor router mount failed: %s", e)

# Invoices router (CRUD + webhook events)
try:
    from routes.invoices import router as invoices_router
    app.include_router(invoices_router)
    log.info("[main] invoices router mounted at /api/v1/invoices")
except Exception as e:
    log.warning("[main] invoices router mount failed: %s", e)

# Freight Broker router (commission calculation, profit tracking, analytics)
try:
    from routes.broker_invoices import router as broker_invoices_router
    app.include_router(broker_invoices_router)
    log.info("[main] broker_invoices router mounted at /api/v1/broker")
except Exception as e:
    log.warning("[main] broker_invoices router mount failed: %s", e)

# Legacy Platform Expenses router (kept for backward compatibility)
try:
    from routes.platform_expenses import router as platform_expenses_legacy_router
    app.include_router(platform_expenses_legacy_router)
    log.info("[main] platform_expenses_legacy router mounted at /finance/expenses")
except Exception as e:
    log.warning("[main] platform_expenses_legacy router mount failed: %s", e)

# Bots subscription manager (v1)
try:
    from routes.bots_subscription import router as bots_subscription_router
    app.include_router(bots_subscription_router)
    log.info("[main] bots_subscription mounted at /api/v1/ai/bots/*")
except Exception as e:
    log.warning("[main] bots_subscription not mounted: %s", e)

# Frontend compatibility routes (system status, bots status)
if frontend_compat_router:
    app.include_router(frontend_compat_router)
    log.info("[main] frontend_compat routes mounted")

# AI Maintenance Chat (intelligent responses)
if ai_maintenance_chat_router:
    app.include_router(ai_maintenance_chat_router, prefix="/api/v1")
    log.info("[main] AI maintenance chat routes mounted at /api/v1/ai/maintenance/chat/*")

# Bot OS (v1)
if bot_os_router:
    app.include_router(bot_os_router)
    log.info("[main] bot_os routes mounted at /api/v1/bots/*")

# Live WebSocket (v1)
if ws_live_router:
    app.include_router(ws_live_router, prefix="/api/v1/ws")
    log.info("[main] ws live routes mounted at /api/v1/ws/*")

# Transport laws
if transport_laws_router:
    app.include_router(transport_laws_router)
    log.info("[main] transport_laws routes mounted at /api/transport-laws/*")

# AI Bots Routes (v1)
if ai_bots_router:
    app.include_router(
        ai_bots_router,
        prefix="/api/v1",
        dependencies=[Depends(require_roles(["user", "manager", "admin", "super_admin"]))]
    )
    log.info("[main] ai_bots routes mounted at /api/v1/bots/*")
else:
    log.warning("[main] ai_bots routes not available")

if executive_intelligence_router:
    app.include_router(executive_intelligence_router)
    log.info("[main] executive_intelligence routes mounted at /api/v1/ai/bots/executive_intelligence")
else:
    log.warning("[main] executive_intelligence router not available")

# Users
if users_router:
    try:
        app.include_router(users_router)
        log.info("[main] users_routes mounted at /users/*")
    except Exception as e:
        log.warning("[router] users mount failed: %s", e)
else:
    log.warning("[main] users_routes not available")

# Admin Users (super_admin only)
if admin_users_router:
    try:
        app.include_router(admin_users_router)
        log.info("[main] admin_users mounted at /admin/*")
    except Exception as e:
        log.warning("[router] admin_users mount failed: %s", e)
else:
    log.warning("[main] admin_users not available")

# Admin Unified Portal (admin dashboard)
if admin_unified_router:
    try:
        app.include_router(admin_unified_router)
        log.info("[main] admin_unified mounted at /api/v1/admin/*")
    except Exception as e:
        log.warning("[router] admin_unified mount failed: %s", e)
else:
    log.warning("[main] admin_unified not available")

if policy_context_router:
    try:
        app.include_router(policy_context_router)
        log.info("[main] policy_context routes mounted at /api/v1/policy/*")
    except Exception as e:
        log.warning("[router] policy_context mount failed: %s", e)
else:
    log.warning("[main] policy_context router not available")

# Vizion
if vizion_router:
    app.include_router(vizion_router, prefix="/vizion", tags=["VIZION"])

# Health
if health_router:
    app.include_router(health_router, tags=["health"])

if bot_learning_router:
    app.include_router(bot_learning_router)
    log.info("[main] bot learning routes mounted at /ai/learning/*")

# AI Marketing Specialist
if marketing_router:
    app.include_router(marketing_router)
    log.info("[main] marketing routes mounted at /ai/marketing/*")
else:
    log.warning("[main] marketing_router not available")

# Shipments + shims
if shipments_router:
    app.include_router(shipments_router)
    @app.api_route(
        "/api/v1/shipments/shipments/{rest:path}",
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        include_in_schema=False,
    )
    async def _shim_v1_double(rest: str, request: Request):
        target = request.url.path.replace("/api/v1/shipments/shipments", "/api/v1/shipments", 1)
        qs = request.url.query
        return RedirectResponse(url=target + (("?" + qs) if qs else ""), status_code=307)

    @app.api_route(
        "/shipments/shipments/{rest:path}",
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        include_in_schema=False,
    )
    async def _shim_double(rest: str, request: Request):
        target = request.url.path.replace("/shipments/shipments", "/shipments", 1)
        qs = request.url.query
        return RedirectResponse(url=target + (("?" + qs) if qs else ""), status_code=307)

# Reports
if reports_router:
    app.include_router(reports_router)
if reports_real_data_router:
    app.include_router(reports_real_data_router)
if ai_reports_router:
    app.include_router(ai_reports_router)

# Loadboards / TruckerPath
if loadboards_router:
    app.include_router(loadboards_router)
if truckerpath_router:
    app.include_router(truckerpath_router)
if tp_webhook_router:
    app.include_router(tp_webhook_router)

# Documents (protected)
if documents_router:
    app.include_router(documents_router, dependencies=[Depends(require_roles(["manager", "admin"]))])
if documents_ai_router:
    app.include_router(documents_ai_router, dependencies=[Depends(require_roles(["manager", "admin"]))])
if documents_upload_router:
    app.include_router(documents_upload_router, dependencies=[Depends(require_roles(["manager", "admin"]))])
    log.info("[main] documents upload routes mounted at /api/v1/documents/*")

# AI gateway
if ai_gateway_router:
    app.include_router(ai_gateway_router)

# Email center (v1)
if email_center_router:
    try:
        app.include_router(email_center_router)
        log.info("[main] email center mounted at /api/v1/email/*")
    except Exception as e:
        log.warning("[router] email center mount failed: %s", e)

if email_ai_stats_router:
    try:
        app.include_router(email_ai_stats_router)
        log.info("[main] email AI stats mounted at /api/v1/email/ai/stats/*")
    except Exception as e:
        log.warning("[router] email AI stats mount failed: %s", e)

# Email Bot routes (intelligent email processing)
if email_bot_router:
    try:
        app.include_router(email_bot_router)
        log.info("[main] email bot routes mounted at /api/v1/email/*")
    except Exception as e:
        log.warning("[router] email bot routes mount failed: %s", e)

# Finance
if finance_router:
    app.include_router(
        finance_router,
        prefix="/finance",
        tags=["finance"],
        dependencies=[Depends(require_roles(["manager", "admin"]))],
    )
    log.info("[main] finance_routes mounted at /finance/*")
else:
    log.warning("[main] finance_routes not available")

# Weather
if weather_router:
    app.include_router(weather_router)
    log.info("[main] weather routes mounted at /api/v1/weather/*")

# Notifications
if notifications_router:
    app.include_router(notifications_router)
    log.info("[main] notifications routes mounted at /api/v1/notifications/*")

# Freight Market Rates
if freight_market_rates_router:
    app.include_router(freight_market_rates_router)
    log.info("[main] freight market rates routes mounted at /api/v1/freight/*")

if webhooks_router:
    app.include_router(webhooks_router)
    log.info("[main] webhooks routes mounted at /api/v1/webhooks/*")

# Carriers Management
try:
    from routes.carriers import router as carriers_router
    app.include_router(carriers_router)
    log.info("[main] carriers routes mounted at /api/v1/carriers/*")
except Exception as e:
    log.warning("[main] carriers routes mount failed: %s", e)

# Shippers Management
try:
    from routes.shippers import router as shippers_router
    app.include_router(shippers_router)
    log.info("[main] shippers routes mounted at /api/v1/shippers/*")
except Exception as e:
    log.warning("[main] shippers routes mount failed: %s", e)

if quo_webhook_router:
    app.include_router(quo_webhook_router, prefix="/api/v1/webhooks/quo")
    log.info("[main] quo webhooks mounted at /api/v1/webhooks/quo/*")

if ai_calls_router:
    app.include_router(
        ai_calls_router,
        prefix="/api/v1/ai-calls",
        dependencies=[Depends(require_roles(["admin", "manager"]))],
    )
    log.info("[main] ai calls routes mounted at /api/v1/ai-calls/*")

if enhanced_call_router:
    app.include_router(
        enhanced_call_router,
        dependencies=[Depends(require_roles(["admin", "manager"]))],
    )
    log.info("[main] enhanced call routes mounted at /api/v1/calls/*")

if payment_webhooks_router:
    app.include_router(payment_webhooks_router)
    log.info("[main] legacy sudapay webhook endpoint disabled at /api/v1/webhooks/sudapay/*")

if wise_webhooks_router:
    app.include_router(wise_webhooks_router)
    log.info("[main] wise webhooks routes mounted at /api/webhooks/wise/*")

if stripe_webhooks_router:
    app.include_router(stripe_webhooks_router)
    log.info("[main] stripe webhooks routes mounted at /api/webhooks/stripe/*")

if portal_requests_router:
    app.include_router(portal_requests_router)
    log.info("[main] portal requests routes mounted at /portal/*")

if admin_portal_requests_router:
    app.include_router(admin_portal_requests_router)
    log.info("[main] admin portal request routes mounted at /api/v1/admin/portal/*")

if tms_requests_admin_router:
    app.include_router(tms_requests_admin_router)
    log.info("[main] TMS request admin routes mounted at /api/v1/admin/tms-requests/*")

if payment_gateway_router:
    app.include_router(payment_gateway_router)
    log.info("[main] payment gateway routes mounted at /api/v1/payments/*")

if payment_routes_router:
    app.include_router(payment_routes_router)
    log.info("[main] payment routes mounted at /api/payments/*")

if seo_public_router:
    app.include_router(seo_public_router)
    log.info("[main] SEO public routes mounted at /robots.txt and /sitemap.xml")

if unified_finance_router:
    app.include_router(
        unified_finance_router,
        dependencies=[Depends(require_roles(["manager", "admin"]))],
    )
    log.info("[main] unified finance routes mounted at /api/v1/finance/*")

if accounting_router:
    try:
        app.include_router(
            accounting_router,
            dependencies=[Depends(require_roles(["manager", "admin"]))],
        )
        log.info("[main] accounting routes mounted at /api/v1/accounting/*")
    except Exception as e:
        log.warning("[main] accounting router mount failed: %s", e)

if channels_webhooks_router:
    try:
        app.include_router(channels_webhooks_router)
        log.info("[main] channels webhooks routes mounted at /api/v1/webhooks/channels/*")
    except Exception as e:
        log.warning("[main] channels webhooks router mount failed: %s", e)

# Telegram Webhook Router - Force reload test
telegram_webhook_router = _try_import_router("routes.telegram_webhook", "routes.telegram_webhook")
if telegram_webhook_router:
    try:
        app.include_router(telegram_webhook_router)
        log.info("[main] Telegram webhook router mounted at /api/v1/telegram/*")
    except Exception as e:
        log.warning("[main] Telegram webhook router mount failed: %s", e)

# Force reload trigger

if call_ai_router:
    app.include_router(
        call_ai_router,
        dependencies=[Depends(require_roles(["admin", "manager"]))],
    )
    log.info("[main] call AI routes mounted at /api/v1/call-ai/*")

if communications_router:
    app.include_router(
        communications_router,
        dependencies=[Depends(require_roles(["admin", "manager"]))],
    )
    log.info("[main] communications routes mounted at /api/v1/communications/*")

if training_center_router:
    app.include_router(
        training_center_router,
        dependencies=[Depends(require_roles(["admin", "manager"]))],
    )
    log.info("[main] training center routes mounted at /api/v1/training-center/*")

if bot_collaboration_router:
    app.include_router(
        bot_collaboration_router,
        dependencies=[Depends(require_roles(["admin", "manager"]))],
    )
    log.info("[main] bot collaboration routes mounted at /api/v1/bot-collaboration/*")

if billing_router:
    app.include_router(billing_router)
    log.info("[main] billing routes mounted at /api/v1/billing/*")

if admin_billing_router:
    app.include_router(admin_billing_router)
    log.info("[main] admin billing routes mounted at /api/v1/admin/billing/*")

# MapleLoad Canada Bot - Already mounted earlier to avoid route conflicts

if finance_reports:
    app.include_router(
        finance_reports,
        prefix="/finance/reports",
        tags=["finance"],
        dependencies=[Depends(require_roles(["manager", "admin"]))],
    )
    log.info("[main] finance_reports mounted at /finance/reports/*")
else:
    log.warning("[main] finance_reports not available")

if finance_ai_router:
    app.include_router(
        finance_ai_router,
        prefix="/finance/ai",
        tags=["finance"],
        dependencies=[Depends(require_roles(["manager", "admin"]))],
    )
    log.info("[main] finance_ai_routes mounted at /finance/ai/*")
else:
    log.warning("[main] finance_ai_routes not available")

# Maintenance & Development routes
if maintenance_ai_router:
    app.include_router(
        maintenance_ai_router,
        dependencies=[Depends(require_roles(["admin", "manager"]))],
    )
    log.info("[main] maintenance_ai_routes mounted at /api/v1/maintenance/*")

if maintenance_center_router:
    app.include_router(
        maintenance_center_router,
        prefix="/api/v1",
        dependencies=[Depends(require_roles(["admin", "manager"]))],
    )
    log.info("[main] maintenance_center_routes mounted at /api/v1/maintenance_center/*")

if dev_maintenance_router:
    app.include_router(
        dev_maintenance_router,
        prefix="/api/v1",
        dependencies=[Depends(require_roles(["admin", "manager"]))],
    )
    log.info("[main] dev_maintenance_routes mounted at /api/v1/dev_maintenance/*")

if maintenance_router:
    app.include_router(
        maintenance_router,
        prefix="/api/v1",
        tags=["maintenance"],
    )
    log.info("[main] maintenance_routes mounted at /api/v1/maintenance/*")

# Admin System routes
if system_routes_router:
    app.include_router(
        system_routes_router,
        prefix="/api/v1",
    )
    log.info("[main] system_routes mounted at /api/v1/system/*")

if admin_system_router:
    app.include_router(
        admin_system_router,
        dependencies=[Depends(require_roles(["admin"]))],
    )
    log.info("[main] admin_system_routes mounted at /api/v1/admin/*")

# Admin Data Sources routes (health, users, security from different sources)
if admin_data_sources_router:
    app.include_router(
        admin_data_sources_router,
        dependencies=[Depends(require_roles(["admin"]))],
    )
    log.info("[main] admin_data_sources_routes mounted at /api/v1/admin/data-sources/*")

# Admin Platform Settings routes
if admin_platform_settings_router:
    app.include_router(
        admin_platform_settings_router,
        dependencies=[Depends(require_roles(["admin"]))],
    )
    log.info("[main] admin_platform_settings routes mounted at /api/v1/admin/platform-settings/*")

# Public Platform Settings routes (no auth required)
if platform_public_router:
    app.include_router(platform_public_router)
    log.info("[main] platform_settings public routes mounted at /api/v1/platform-settings/*")

# Admin Tenants routes
if admin_tenants_router:
    app.include_router(
        admin_tenants_router,
        dependencies=[Depends(require_roles(["admin"]))],
    )
    log.info("[main] admin_tenants routes mounted at /api/v1/admin/tenants/*")

# Admin API Connections routes  
if admin_api_connections_router:
    app.include_router(
        admin_api_connections_router,
        prefix="/api/v1/admin/api-connections",
        dependencies=[Depends(require_roles(["super_admin", "admin"]))],
    )
    log.info("[main] admin_api_connections routes mounted at /api/v1/admin/api-connections/*")


# Admin Audit routes
if admin_audit_router:
    app.include_router(
        admin_audit_router,
        dependencies=[Depends(require_roles(["admin"]))],
    )
    log.info("[main] admin_audit routes mounted at /api/v1/admin/audit/*")

# Integrations routes
if integrations_router:
    app.include_router(
        integrations_router,
        dependencies=[Depends(get_current_user)],
    )
    log.info("[main] integrations routes mounted at /api/v1/integrations/*")

# Machine Learning & Advanced Analytics routes
if ml_router:
    app.include_router(
        ml_router,
        prefix="/api/v1",
    )
    log.info("[main] ml routes mounted at /api/v1/ml/*")

# Unified map entities routes
if map_entities_router:
    app.include_router(
        map_entities_router,
        dependencies=[Depends(get_current_user)],
    )
    log.info("[main] map_entities routes mounted at /api/v1/map/*")

# Social Media Routes
if social_media_router:
    app.include_router(
        social_media_router,
        prefix="/api/v1/admin/social-media",
        dependencies=[Depends(require_roles(["admin"]))],
        tags=["Social Media Admin"]
    )
    log.info("[main] social_media_admin router mounted at /api/v1/admin/social-media")

if social_media_public_router:
    app.include_router(
        social_media_public_router,
        prefix="/api/v1/social-media",
        tags=["Social Media Public"]
    )
    log.info("[main] social_media_public router mounted at /api/v1/social-media")

# Backward-compat shim for legacy /finance/ai/ai/* paths
@app.api_route(
    "/finance/ai/ai/{rest:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    include_in_schema=False,
)
async def _shim_fin_ai_double(rest: str, request: Request):
    target = request.url.path.replace("/finance/ai/ai", "/finance/ai", 1)
    qs = request.url.query
    return RedirectResponse(url=target + (("?" + qs) if qs else ""), status_code=307)

# Public API router mounted earlier with /api/v1 prefix

# Core AI router (no auth for now to test)

# Meta Data API router (trailer types, locations)
try:
    from routes.meta_data_api import router as meta_data_api_router
    app.include_router(meta_data_api_router, prefix="/api/v1/meta", tags=["Meta Data"])
    log.info("[main] meta_data_api router mounted at /api/v1/meta/*")
except Exception as e:
    log.warning("[main] meta_data_api router import failed: %s", e)

app.include_router(ai_router)

# ---- Compat shims for frontend roles endpoints ----
@app.get("/test/roles2", include_in_schema=False)
async def test_roles_v2():
    """Test endpoint - absolutely no auth needed - v2"""
    try:
        from database.session import wrap_session_factory, async_session
        from sqlalchemy import text
        
        async with wrap_session_factory(async_session) as session:
            result = await session.execute(
                text("SELECT key, name_en, name_ar, permissions, is_system FROM roles ORDER BY key")
            )
            rows = result.all()
            return {
                "status": "success",
                "count": len(rows),
                "roles": [
                    {
                        "key": r[0],
                        "name_en": r[1],
                        "name_ar": r[2],
                        "permissions": r[3] or [],
                        "is_system": bool(r[4]),
                    }
                    for r in rows
                ]
            }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc()
        }


# ---- Compat shims for frontend AI endpoints ----
@app.api_route(
    "/api/v1/ai/bots/available/{bot_key}/run",
    methods=["POST"],
    include_in_schema=False,
)
async def _shim_ai_bots_run(bot_key: str, request: Request):
    target = request.url.path.replace("/api/v1/ai/bots/available", "/api/v1/bots", 1)
    qs = request.url.query
    return RedirectResponse(url=target + (("?" + qs) if qs else ""), status_code=307)

@app.api_route(
    "/api/v1/ai/bots/available/{bot_key}/status",
    methods=["GET"],
    include_in_schema=False,
)
async def _shim_ai_bots_status(bot_key: str, request: Request):
    target = f"/api/v1/bots/{bot_key}/status"
    qs = request.url.query
    return RedirectResponse(url=target + (("?" + qs) if qs else ""), status_code=307)

@app.api_route(
    "/api/v1/ai/bots/available/{bot_key}/config",
    methods=["GET"],
    include_in_schema=False,
)
async def _shim_ai_bots_config(bot_key: str, request: Request):
    target = f"/api/v1/bots/{bot_key}/config"
    qs = request.url.query
    return RedirectResponse(url=target + (("?" + qs) if qs else ""), status_code=307)

# ---- Compat shims for frontend admin endpoints ----
@app.api_route(
    "/admin",
    methods=["GET"],
    include_in_schema=False,
)
async def _shim_admin_root(request: Request):
    target = "/api/v1/admin"
    qs = request.url.query
    return RedirectResponse(url=target + (("?" + qs) if qs else ""), status_code=307)

@app.api_route(
    "/admin/{rest:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    include_in_schema=False,
)
async def _shim_admin_routes(rest: str, request: Request):
    target = f"/api/v1/admin/{rest}"
    qs = request.url.query
    return RedirectResponse(url=target + (("?" + qs) if qs else ""), status_code=307)


# Auth router mount handled elsewhere


# Billing router (/billing/*) placeholder
# billing_router = _try_import_router("routes.billing", "billing")
# if billing_router:
#     app.include_router(billing_router, dependencies=[Depends(require_roles(["user", "manager", "admin"]))])
#     log.info("[main] billing router mounted at /billing/*")
# else:
#     log.warning("[main] billing router not available")


@app.get("/healthz", include_in_schema=False)
async def healthz_alias():
    return {"status": "ok"}

@app.get("/test/roles", include_in_schema=False)
async def test_roles():
    """Test endpoint - absolutely no auth needed"""
    try:
        from database.session import wrap_session_factory, async_session
        from sqlalchemy import text
        
        async with wrap_session_factory(async_session) as session:
            result = await session.execute(
                text("SELECT key, name_en, name_ar, permissions, is_system FROM roles ORDER BY key")
            )
            rows = result.all()
            return {
                "status": "success",
                "count": len(rows),
                "roles": [
                    {
                        "key": r[0],
                        "name_en": r[1],
                        "name_ar": r[2],
                        "permissions": r[3] or [],
                        "is_system": bool(r[4]),
                    }
                    for r in rows
                ]
            }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }

@app.get("/health/sentry", include_in_schema=False)
async def health_sentry_test():
    """Test endpoint to trigger a Sentry error for testing purposes."""
    # Security: Only allow if explicitly enabled or in development
    sentry_test_enabled = os.getenv("SENTRY_TEST_ENDPOINT_ENABLED", "false").lower() == "true"
    is_dev = os.getenv("GTS_DEV_MODE", "false").lower() == "true"

    if not sentry_test_enabled and not is_dev:
        raise HTTPException(
            status_code=403,
            detail="Sentry test endpoint disabled in production. Set SENTRY_TEST_ENDPOINT_ENABLED=true to enable."
        )

    try:
        # This will trigger an error that Sentry should capture
        result = 1 / 0  # ZeroDivisionError
        return {"status": "ok", "result": result}
    except ZeroDivisionError as e:
        # Log the error with context
        log.error("[health_sentry] intentional test error: %s", e)
        # Re-raise to let Sentry capture it
        raise HTTPException(status_code=500, detail="Test error for Sentry monitoring")


# ---------------- Debug + Root ----------------
@app.get("/_debug/routes")
async def _list_routes(_user: dict = Depends(require_roles(["super_admin"]))):
    routes: List[Dict[str, Any]] = []
    for r in app.router.routes:
        try:
            routes.append(
                {
                    "path": getattr(r, "path", ""),
                    "name": getattr(r, "name", ""),
                    "methods": list(getattr(r, "methods", [])),
                }
            )
        except Exception:
            pass
    return JSONResponse({"count": len(routes), "routes": routes})


@app.post("/_debug/memory-snapshot")
async def _debug_memory_snapshot(
    top: int = 50,
    _user: dict = Depends(require_roles(["super_admin"])),
):
    if not MEM_SNAPSHOT_ENABLED:
        raise HTTPException(status_code=403, detail="Memory snapshot endpoint disabled")
    snap_path = dump_memory_snapshot(path=None, top=top)
    return {"ok": True, "snapshot": snap_path, "top": top}


@app.get("/_debug/admin-users")
async def _debug_admin_users(_user: dict = Depends(require_roles(["super_admin"]))):
    try:
        from routes import admin_users as admin_users_mod
        router = getattr(admin_users_mod, "router", None)
        return {
            "module_file": getattr(admin_users_mod, "__file__", None),
            "router_prefix": getattr(router, "prefix", None),
            "routes": [
                {
                    "path": getattr(r, "path", ""),
                    "methods": list(getattr(r, "methods", [])),
                    "name": getattr(r, "name", ""),
                }
                for r in (getattr(router, "routes", []) or [])
            ],
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/")
async def root():
    return {"ok": True, "name": "Gabani Transport Solutions (GTS) Backend", "offline": OFFLINE}
