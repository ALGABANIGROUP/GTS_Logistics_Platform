from __future__ import annotations

import asyncio
import logging
import os
import secrets
import string
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Sequence

import httpx
from sqlalchemy import func, select

from backend.admin_control.models import Role
from backend.database.config import get_sessionmaker
from backend.models.user import User
from backend.security.passwords import hash_password

logger = logging.getLogger("rbac_seed")
logging.basicConfig(level=logging.INFO, format="%(message)s")


@dataclass
class SeedUser:
    role: str
    email: str
    full_name: str
    company: str = "GTS Logistics"
    user_type: str = "user"


CANONICAL_ROLES = [
    "general_manager",
    "operations_manager",
    "finance",
    "freight_broker",
    "documents_manager",
    "customer_service",
    "system_admin",
    "information_coordinator",
    "strategy_advisor",
    "marketing_manager",
    "partner_manager",
    "dev_maintenance_cto",
    "safety_manager",
    "security_manager",
    "sales",
    "ai_dispatcher",
]

BASELINE_ROLES = ["user", "manager", "viewer"]

ROLE_USER_MAP = [
    SeedUser(role="operations_manager", email="operations@gabanilogistics.com", full_name="Operations Manager"),
    SeedUser(role="finance", email="finance@gabanilogistics.com", full_name="Finance"),
    SeedUser(role="freight_broker", email="freight@gabanilogistics.com", full_name="Freight Broker"),
    SeedUser(role="documents_manager", email="doccontrol@gabanilogistics.com", full_name="Documents Manager"),
    SeedUser(role="customer_service", email="customers@gabanilogistics.com", full_name="Customer Service"),
    SeedUser(role="system_admin", email="admin@gabanilogistics.com", full_name="System Administrator"),
    SeedUser(role="information_coordinator", email="intel@gabanilogistics.com", full_name="Information Coordinator"),
    SeedUser(role="strategy_advisor", email="strategy@gabanilogistics.com", full_name="Strategy Advisor"),
    SeedUser(role="marketing_manager", email="marketing@gabanilogistics.com", full_name="Marketing Manager"),
    SeedUser(role="partner_manager", email="investments@gabanilogistics.com", full_name="Partner Manager"),
    SeedUser(role="safety_manager", email="safety@gabanilogistics.com", full_name="Safety Manager"),
    SeedUser(role="security_manager", email="security@gabanistore.com", full_name="Security Manager"),
    SeedUser(role="sales", email="sales@gabanilogistics.com", full_name="Sales"),
    SeedUser(role="ai_dispatcher", email="aidispatcher@gtsdispatcher.com", full_name="AI Dispatcher"),
    SeedUser(role="general_manager", email="gm@gabanilogistics.com", full_name="General Manager"),
    SeedUser(role="dev_maintenance_cto", email="cto@gabanilogistics.com", full_name="Dev Maintenance CTO"),
]


def _random_password(length: int = 18) -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    return "".join(secrets.choice(alphabet) for _ in range(length))


async def _ensure_roles(session) -> None:
    names = {*CANONICAL_ROLES, *BASELINE_ROLES}
    for name in sorted(names):
        lower = name.strip().lower()
        stmt = select(Role).where(func.lower(Role.name) == lower)
        existing = await session.execute(stmt)
        role = existing.scalar_one_or_none()
        if role:
            continue
        new_role = Role(name=lower, description=f"Seeded role for {lower}")
        session.add(new_role)
        logger.info(f"Created role {lower}")
    await session.flush()


async def _seed_users(session) -> List[Dict[str, str]]:
    now = datetime.now(timezone.utc)
    expires = now + timedelta(days=7)
    seeded: List[Dict[str, str]] = []

    for entry in ROLE_USER_MAP:
        email = entry.email.lower().strip()
        if not email:
            continue
        password = _random_password()
        stmt = select(User).where(func.lower(User.email) == email)
        existing = await session.execute(stmt)
        user = existing.scalar_one_or_none()
        hashed = hash_password(password)

        if user is None:
            user = User(
                email=email,
                full_name=entry.full_name,
                company=entry.company,
                user_type=entry.user_type,
                hashed_password=hashed,
                role=entry.role,
                is_active=True,
                is_banned=False,
                is_deleted=False,
                activation_token=secrets.token_urlsafe(32),
                activation_expires_at=expires,
            )
            session.add(user)
            action = "created"
        else:
            user.full_name = entry.full_name
            user.company = entry.company
            user.user_type = entry.user_type
            user.role = entry.role
            user.hashed_password = hashed
            user.is_active = True
            user.is_banned = False
            user.is_deleted = False
            user.activation_token = secrets.token_urlsafe(32)
            user.activation_expires_at = expires
            action = "updated"

        await session.flush()
        seeded.append(
            {
                "role": entry.role,
                "email": email,
                "password": password,
                "action": action,
                "user_id": str(user.id),
            }
        )

    await session.commit()
    return seeded


ENDPOINTS = [
    {"label": "Auth /auth/me", "method": "GET", "path": "/api/v1/auth/me"},
    {"label": "Admin users", "method": "GET", "path": "/api/v1/admin/users"},
    {"label": "Portal requests", "method": "GET", "path": "/api/v1/admin/portal/requests"},
    {"label": "Orchestration bots", "method": "GET", "path": "/api/v1/orchestration/bots"},
    {"label": "Finance expenses", "method": "GET", "path": "/finance/expenses"},
    {"label": "Documents health", "method": "GET", "path": "/documents/healthz"},
]


async def _test_endpoint(client: httpx.AsyncClient, method: str, path: str) -> Dict[str, str]:
    try:
        response = await client.request(method, path)
        status = response.status_code
        allowed = "ALLOW" if status < 400 else "DENY"
        return {"status": str(status), "result": allowed}
    except Exception as exc:
        return {"status": "error", "result": f"DENY ({exc})"}


async def _run_verification(seed_info: List[Dict[str, str]]) -> Dict[str, Sequence[Dict[str, str]]]:
    api_url = os.getenv("RBAC_API_URL") or os.getenv("API_BASE_URL") or "http://127.0.0.1:8000"
    report: Dict[str, List[Dict[str, str]]] = {}
    async with httpx.AsyncClient(base_url=api_url, timeout=10.0) as client:
        for entry in seed_info:
            email = entry["email"]
            password = entry["password"]
            try:
                token_resp = await client.post("/auth/token", data={"username": email, "password": password})
                token_resp.raise_for_status()
            except Exception as exc:
                logger.warning("Token request failed for %s: %s", email, exc)
                continue
            token = token_resp.json().get("access_token")
            if not token:
                logger.warning("No token returned for %s", email)
                continue

            headers = {"Authorization": f"Bearer {token}"}
            scans = []
            for endpoint in ENDPOINTS:
                result = await _test_endpoint(
                    client,
                    endpoint["method"],
                    endpoint["path"],
                )
                scans.append({**endpoint, **result})

            report[email] = scans
    return report


def _format_report(report: Dict[str, Sequence[Dict[str, str]]]) -> str:
    header = ["Role (email)"] + [ep["label"] for ep in ENDPOINTS]
    rows = []
    for email, scans in report.items():
        role = next((entry["role"] for entry in ROLE_USER_MAP if entry.email.lower() == email), email)
        cells = []
        for scan in scans:
            cells.append(f"{scan['result']} ({scan['status']})")
        rows.append([f"{role} ({email})", *cells])

    widths = []
    for idx in range(len(header)):
        column_vals = [row[idx] for row in rows] if rows else []
        column_vals.append(header[idx])
        widths.append(max(len(val) for val in column_vals))
    lines = []
    lines.append(" | ".join(h.ljust(w) for h, w in zip(header, widths)))
    lines.append("-+-".join("-" * w for w in widths))
    for row in rows:
        lines.append(" | ".join(val.ljust(widths[idx]) for idx, val in enumerate(row)))
    return "\n".join(lines)


async def main() -> None:
    maker = get_sessionmaker()
    if maker is None:
        raise RuntimeError("Database session factory is not configured")

    async with maker() as session:
        await _ensure_roles(session)
        seed_info = await _seed_users(session)

    logger.info("Seeded users:")
    for info in seed_info:
        logger.info("  %s: %s (%s)", info["role"], info["email"], info["action"])

    logger.info("Running RBAC verification...")
    report = await _run_verification(seed_info)
    matrix = _format_report(report)
    logger.info("RBAC Verification Report\n%s", matrix)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as exc:
        logger.exception("RBAC seeding failed: %s", exc)
