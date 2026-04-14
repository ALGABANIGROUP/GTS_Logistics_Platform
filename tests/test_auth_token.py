"""Local auth token contract tests."""


def _login(client, username: str, password: str):
    return client.post(
        "/api/v1/auth/token",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )


def test_auth_token_success(client):
    response = _login(client, "admin@gts.com", "admin123")
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload.get("access_token"), payload

    me = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {payload['access_token']}"},
    )
    assert me.status_code == 200, me.text
    assert me.json().get("email") == "admin@gts.com"


def test_auth_token_invalid_credentials(client):
    response = _login(client, "invalid@example.com", "wrong")
    assert response.status_code in (400, 401, 403), response.text


def test_auth_me_requires_token(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code in (401, 403), response.text


def test_admin_route_accepts_valid_token(client):
    login = _login(client, "admin@gts.com", "admin123")
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]
    response = client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
