from __future__ import annotations

import asyncio
import os
import smtplib
from typing import Any, Dict, Optional

import aiohttp
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

try:
    import redis.asyncio as redis
except Exception:
    redis = None  # type: ignore

router = APIRouter(prefix="/health", tags=["Health"])

_session_import_error: Optional[str] = None


def _try_import_async_session():
    global _session_import_error
    try:
        from backend.database.session import get_async_session  # type: ignore

        _session_import_error = None
        return get_async_session
    except Exception as exc:
        _session_import_error = str(exc)
        return None


_session_dep = _try_import_async_session()
if _session_dep is None:
    async def _missing_session() -> Optional[AsyncSession]:
        return None

    _session_dep = _missing_session


def _mask_url(url: str) -> str:
    if not url:
        return url
    return url.replace("redis://", "redis://***:***@") if "@" in url else url


async def _check_redis() -> Dict[str, Any]:
    if redis is None:
        return {"ok": False, "available": False, "error": "redis library not installed"}

    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    try:
        client = redis.Redis.from_url(redis_url, socket_timeout=5, socket_connect_timeout=5)
        pong = await asyncio.wait_for(client.ping(), timeout=5.0)
        await client.aclose()
        return {
            "ok": bool(pong),
            "available": True,
            "url": _mask_url(redis_url),
        }
    except asyncio.TimeoutError:
        return {"ok": False, "available": True, "error": "Redis ping timeout"}
    except Exception as exc:
        return {"ok": False, "available": True, "error": f"Redis connection failed: {exc}"}


async def _check_external_services() -> Dict[str, Any]:
    services: Dict[str, Any] = {}

    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "465"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    if smtp_host and smtp_user and smtp_password:
        try:
            server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10)
            server.login(smtp_user, smtp_password)
            server.quit()
            services["smtp"] = {"ok": True, "host": smtp_host, "port": smtp_port}
        except Exception as exc:
            services["smtp"] = {
                "ok": False,
                "host": smtp_host,
                "port": smtp_port,
                "error": f"SMTP connection failed: {exc}",
            }
    else:
        services["smtp"] = {"ok": False, "configured": False, "error": "SMTP credentials not configured"}

    quo_api_key = os.getenv("QUO_API_KEY")
    if quo_api_key:
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                headers = {"Authorization": f"Bearer {quo_api_key}"}
                async with session.get("https://api.quo.audio/health", headers=headers) as response:
                    services["quo_api"] = {"ok": response.status == 200, "status_code": response.status}
        except Exception as exc:
            services["quo_api"] = {"ok": False, "error": f"QUO API check failed: {exc}"}
    else:
        services["quo_api"] = {"ok": False, "configured": False, "error": "QUO_API_KEY not configured"}

    return services


@router.get("/ping")
async def ping() -> Dict[str, Any]:
    return {"ok": True, "service": "gts-backend"}


@router.get("/db")
async def health_db(db: Optional[AsyncSession] = Depends(_session_dep)) -> Dict[str, Any]:
    if db is None:
        db_url = os.getenv("DATABASE_URL") or os.getenv("ASYNC_DATABASE_URL")
        detail: Dict[str, Any] = {
            "ok": False,
            "service": "database",
            "error": "session unavailable",
            "configured": bool(db_url),
        }
        if not db_url:
            detail["hint"] = "Set DATABASE_URL (or ASYNC_DATABASE_URL) in environment variables"
        if _session_import_error:
            detail["import_error"] = _session_import_error
        raise HTTPException(status_code=503, detail=detail)

    try:
        result = await asyncio.wait_for(
            db.execute(text("SELECT 1 as health_check, NOW() as current_time")),
            timeout=10.0,
        )
        row = result.first()
        if not row or row[0] != 1:
            raise HTTPException(status_code=503, detail={"ok": False, "service": "database", "error": "unexpected_result"})
        return {"ok": True, "service": "database", "current_time": str(row[1]) if row[1] else None}
    except asyncio.TimeoutError as exc:
        raise HTTPException(status_code=503, detail={"ok": False, "service": "database", "error": "timeout"}) from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail={"ok": False, "service": "database", "error": str(exc)}) from exc


@router.get("/redis")
async def health_redis() -> Dict[str, Any]:
    result = await _check_redis()
    if not result["ok"]:
        raise HTTPException(status_code=503 if result.get("available") else 501, detail=result)
    return result


@router.get("/external")
async def health_external() -> Dict[str, Any]:
    services = await _check_external_services()
    all_ok = all(service.get("ok", False) for service in services.values())
    payload = {"ok": all_ok, "service": "external_dependencies", "services": services}
    if not all_ok:
        raise HTTPException(status_code=207, detail=payload)
    return payload


@router.get("/full")
async def full_health(db: Optional[AsyncSession] = Depends(_session_dep)) -> Dict[str, Any]:
    finance: Dict[str, Any]
    if db is None:
        db_url = os.getenv("DATABASE_URL") or os.getenv("ASYNC_DATABASE_URL")
        finance = {
            "ok": False,
            "error": "session unavailable",
            "configured": bool(db_url),
        }
        if _session_import_error:
            finance["import_error"] = _session_import_error
    else:
        try:
            res = await db.execute(text("SELECT 1"))
            finance = {"ok": res.scalar() == 1}
        except Exception as exc:
            finance = {"ok": False, "error": str(exc)}

    services = {
        "finance": finance,
        "redis": await _check_redis(),
        "external": await _check_external_services(),
    }
    overall_ok = bool(services["finance"].get("ok")) and bool(services["redis"].get("ok"))
    return {"ok": overall_ok, "services": services}
