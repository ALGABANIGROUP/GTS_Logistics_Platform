"""Local authentication and authorization contract tests."""

import pytest


def _login(client, email: str, password: str):
    return client.post(
        "/api/v1/auth/token",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )


class TestAuthentication:
    def test_login_success(self, client):
        response = _login(client, "admin@gts.com", "admin123")
        assert response.status_code == 200, response.text
        data = response.json()
        assert data.get("access_token"), data
        assert data.get("token_type") == "bearer"

    def test_login_invalid_password(self, client):
        response = _login(client, "admin@gts.com", "wrongpassword")
        assert response.status_code in (400, 401, 403), response.text

    def test_login_nonexistent_user(self, client):
        response = _login(client, "nonexistent@test.com", "password")
        assert response.status_code in (400, 401, 403), response.text

    def test_get_current_user(self, client):
        login_response = _login(client, "admin@gts.com", "admin123")
        assert login_response.status_code == 200, login_response.text
        token = login_response.json()["access_token"]
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200, response.text
        user = response.json()
        assert user.get("email") == "admin@gts.com"

    def test_get_current_user_unauthorized(self, client):
        response = client.get("/api/v1/auth/me")
        assert response.status_code in (401, 403), response.text


class TestAuthorization:
    def test_admin_access_allowed(self, client):
        login_response = _login(client, "admin@gts.com", "admin123")
        assert login_response.status_code == 200, login_response.text
        token = login_response.json()["access_token"]
        response = client.get(
            "/api/v1/admin/users",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200, response.text

    def test_user_access_denied_to_admin(self, client):
        login_response = _login(client, "user@gts.com", "user123")
        assert login_response.status_code == 200, login_response.text
        token = login_response.json()["access_token"]
        response = client.get(
            "/api/v1/admin/users",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code in (401, 403), response.text

    def test_unauthenticated_access_denied(self, client):
        response = client.get("/api/v1/admin/users")
        assert response.status_code in (401, 403), response.text
