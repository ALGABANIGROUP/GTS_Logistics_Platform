from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.routing import APIRoute

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.routes import admin_users, platform_infrastructure_routes


def _has_route(router, path: str, method: str) -> bool:
    normalized_method = method.upper()
    for route in router.routes:
        if isinstance(route, APIRoute) and route.path == path and normalized_method in route.methods:
            return True
    return False


def test_admin_users_router_supports_patch_updates() -> None:
    assert _has_route(admin_users.router, "/api/v1/admin/users/{user_id}", "PATCH")
    assert _has_route(admin_users.router, "/api/v1/admin/users/{user_id}", "PUT")


def test_platform_expenses_router_supports_attachment_delete_paths() -> None:
    assert _has_route(platform_infrastructure_routes.router, "/api/v1/platform/expenses/{expense_id}/attachment", "DELETE")
    assert _has_route(platform_infrastructure_routes.router, "/api/v1/platform/expenses/{expense_id}/delete-file", "DELETE")


def test_admin_platform_expenses_page_uses_attachment_delete_endpoint() -> None:
    page = PROJECT_ROOT / "frontend" / "src" / "pages" / "admin" / "PlatformExpenses.jsx"
    source = page.read_text(encoding="utf-8")

    assert "/api/v1/platform/expenses/${expenseId}/attachment" in source
    assert "/api/v1/platform/expenses/${expenseId}/delete-file" not in source


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
