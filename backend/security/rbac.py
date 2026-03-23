# backend/security/rbac.py
"""
Role-Based Access Control (RBAC) helpers for GTS Logistics.

Design goals:
- Single source of truth for role normalization and hierarchy.
- Safe "effective role" computation when both token_role and db_role exist.
- Simple helpers for route dependencies (require_roles / require_permissions).

Notes:
- Internal roles follow a hierarchy: user < manager < admin < system_admin < super_admin < owner
- "partner" is treated as a separate domain role (not part of internal hierarchy).
"""

from __future__ import annotations

from typing import Iterable, Optional, Set

INTERNAL_ROLE_ORDER = ["user", "manager", "admin", "system_admin", "super_admin", "owner"]
INTERNAL_ROLE_RANK = {r: i for i, r in enumerate(INTERNAL_ROLE_ORDER)}

# Partner is intentionally NOT in INTERNAL_ROLE_RANK.
PARTNER_ROLE = "partner"

# Optional alias normalization (keep minimal; expand as needed).
ROLE_ALIASES = {
    "superadmin": "super_admin",
    "super-admin": "super_admin",
    "super admin": "super_admin",
    "system-admin": "system_admin",
    "system admin": "system_admin",
    "administrator": "admin",
    "ops": "manager",
}


def normalize_role(role: Optional[str]) -> str:
    if not role:
        return "user"
    r = str(role).strip().lower()
    r = ROLE_ALIASES.get(r, r)
    return r


def is_internal_role(role: Optional[str]) -> bool:
    r = normalize_role(role)
    return r in INTERNAL_ROLE_RANK


def is_partner_role(role: Optional[str]) -> bool:
    return normalize_role(role) == PARTNER_ROLE


def role_rank(role: Optional[str]) -> int:
    """
    Return rank for internal roles only. Lower is less privileged.
    Unknown roles default to "user".
    """
    r = normalize_role(role)
    return INTERNAL_ROLE_RANK.get(r, INTERNAL_ROLE_RANK["user"])


def min_privilege_role(a: Optional[str], b: Optional[str]) -> str:
    """
    Return the *less privileged* internal role between a and b.
    If either side is not an internal role, fall back to normalized a.
    """
    ra = normalize_role(a)
    rb = normalize_role(b)
    if not (is_internal_role(ra) and is_internal_role(rb)):
        return ra
    return ra if role_rank(ra) <= role_rank(rb) else rb


def compute_effective_role(token_role: Optional[str], db_role: Optional[str]) -> str:
    """
    DB is the source of truth for role state.
    - If db_role exists: effective = db_role
    - If db_role is missing: effective = token_role
    """
    tr = normalize_role(token_role)
    dr = normalize_role(db_role) if db_role else None

    if dr:
        return dr
    return tr


def expand_required_roles(required: Iterable[str]) -> Set[str]:
    """
    Expand required roles with hierarchy:
    - required=["manager"] should allow manager/admin/super_admin
    - required=["admin"] should allow admin/super_admin
    - required=["user"] should allow user/manager/admin/super_admin
    - required includes "partner": partner only (unless other roles also present)
    """
    req = {normalize_role(r) for r in required if r}
    expanded: Set[str] = set()

    if PARTNER_ROLE in req:
        # partner is isolated unless explicitly combined
        expanded.add(PARTNER_ROLE)

    internal_req = [r for r in req if r in INTERNAL_ROLE_RANK]
    if internal_req:
        # pick the lowest privilege among required internal roles,
        # then allow everything above it.
        min_rank = min(role_rank(r) for r in internal_req)
        for r, rk in INTERNAL_ROLE_RANK.items():
            if rk >= min_rank:
                expanded.add(r)

    return expanded


def has_required_role(effective_role: str, required: Iterable[str]) -> bool:
    allowed = expand_required_roles(required)
    return normalize_role(effective_role) in allowed
