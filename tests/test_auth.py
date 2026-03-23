"""
Live authentication and authorization smoke tests for the unified backend.
"""
import os

import pytest
import requests


BASE_URL = os.environ.get("GTS_BASE_URL", "http://127.0.0.1:8000")
ADMIN_EMAIL = os.environ.get("GTS_AUTH_EMAIL") or os.environ.get("GTS_USERNAME")
ADMIN_PASSWORD = os.environ.get("GTS_AUTH_PASSWORD") or os.environ.get("GTS_PASSWORD")
USER_EMAIL = os.environ.get("GTS_USER_EMAIL")
USER_PASSWORD = os.environ.get("GTS_USER_PASSWORD")
HTTP_TIMEOUT = int(os.environ.get("GTS_AUTH_TEST_TIMEOUT", "30"))


def _login(email: str, password: str):
    return requests.post(
        f"{BASE_URL}/api/v1/auth/token",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=HTTP_TIMEOUT,
    )


def _require_admin_credentials() -> None:
    if not ADMIN_EMAIL or not ADMIN_PASSWORD:
        pytest.skip("Missing GTS_AUTH_EMAIL/GTS_AUTH_PASSWORD (or GTS_USERNAME/GTS_PASSWORD).")


class TestAuthentication:
    def test_login_success(self):
        _require_admin_credentials()
        response = _login(ADMIN_EMAIL, ADMIN_PASSWORD)
        assert response.status_code == 200, response.text
        data = response.json()
        assert data.get("access_token"), data
        assert data.get("token_type") == "bearer"

    def test_login_invalid_password(self):
        _require_admin_credentials()
        response = _login(ADMIN_EMAIL, "wrongpassword")
        assert response.status_code in (400, 401, 403), response.text

    def test_login_nonexistent_user(self):
        response = _login("nonexistent@test.com", "password")
        assert response.status_code in (400, 401, 403), response.text

    def test_get_current_user(self):
        _require_admin_credentials()
        login_response = _login(ADMIN_EMAIL, ADMIN_PASSWORD)
        assert login_response.status_code == 200, login_response.text
        token = login_response.json()["access_token"]
        response = requests.get(
            f"{BASE_URL}/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=HTTP_TIMEOUT,
        )
        assert response.status_code == 200, response.text
        payload = response.json()
        user = payload.get("user", payload)
        assert user.get("email") == ADMIN_EMAIL

    def test_get_current_user_unauthorized(self):
        response = requests.get(f"{BASE_URL}/api/v1/auth/me", timeout=HTTP_TIMEOUT)
        assert response.status_code in (401, 403), response.text


class TestAuthorization:
    def test_admin_access_allowed(self):
        _require_admin_credentials()
        login_response = _login(ADMIN_EMAIL, ADMIN_PASSWORD)
        assert login_response.status_code == 200, login_response.text
        token = login_response.json()["access_token"]
        response = requests.get(
            f"{BASE_URL}/api/v1/admin/users",
            headers={"Authorization": f"Bearer {token}"},
            timeout=HTTP_TIMEOUT,
        )
        assert response.status_code != 403, response.text

    def test_user_access_denied_to_admin(self):
        if not USER_EMAIL or not USER_PASSWORD:
            pytest.skip("Missing GTS_USER_EMAIL/GTS_USER_PASSWORD for non-admin authorization check.")
        login_response = _login(USER_EMAIL, USER_PASSWORD)
        assert login_response.status_code == 200, login_response.text
        token = login_response.json()["access_token"]
        response = requests.get(
            f"{BASE_URL}/api/v1/admin/users",
            headers={"Authorization": f"Bearer {token}"},
            timeout=HTTP_TIMEOUT,
        )
        assert response.status_code in (401, 403), response.text

    def test_unauthenticated_access_denied(self):
        response = requests.get(f"{BASE_URL}/api/v1/admin/users", timeout=HTTP_TIMEOUT)
        assert response.status_code in (401, 403), response.text
