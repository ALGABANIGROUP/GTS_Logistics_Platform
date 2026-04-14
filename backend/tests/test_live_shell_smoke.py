from __future__ import annotations

import os
from typing import Iterable

import pytest
import requests


BACKEND_BASE_URL = os.getenv("GTS_BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")
FRONTEND_BASE_URL = os.getenv("GTS_FRONTEND_URL", "http://127.0.0.1:5173").rstrip("/")
ENABLE_OPENAPI = os.getenv("ENABLE_OPENAPI", "false").lower() in {"1", "true", "yes"}


def _require_live_url(url: str) -> None:
    try:
        response = requests.get(url, timeout=5)
    except requests.RequestException as exc:
        pytest.skip(f"Live service unavailable for smoke test: {url} ({exc})")
    if response.status_code >= 500:
        pytest.fail(f"Live service returned {response.status_code} for {url}")


def _assert_live_ok(url: str, expected_codes: Iterable[int] = (200,)) -> None:
    response = requests.get(url, timeout=10)
    assert response.status_code in set(expected_codes), f"{url} returned {response.status_code}"


def test_live_backend_public_routes() -> None:
    _require_live_url(f"{BACKEND_BASE_URL}/healthz")

    _assert_live_ok(f"{BACKEND_BASE_URL}/")
    _assert_live_ok(f"{BACKEND_BASE_URL}/healthz")
    if ENABLE_OPENAPI:
        _assert_live_ok(f"{BACKEND_BASE_URL}/docs")
    _assert_live_ok(f"{BACKEND_BASE_URL}/test/roles", expected_codes=(200,))
    _assert_live_ok(f"{BACKEND_BASE_URL}/api/v1/admin/users/roles/public", expected_codes=(200,))


def test_live_frontend_shell_routes() -> None:
    _require_live_url(f"{FRONTEND_BASE_URL}/")

    _assert_live_ok(f"{FRONTEND_BASE_URL}/")
    _assert_live_ok(f"{FRONTEND_BASE_URL}/ai-bots/system-admin")
    _assert_live_ok(f"{FRONTEND_BASE_URL}/ai-bots/general-manager")
