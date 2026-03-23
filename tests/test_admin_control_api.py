# tests/test_admin_control_api.py
# NOTE: ASCII only.
import os
import requests

from backend.security import auth as auth_module

JWT_SECRET = auth_module.JWT_SECRET
JWT_ALGORITHM = auth_module.JWT_ALGORITHM


BASE_URL = os.environ.get("GTS_BASE_URL", "http://127.0.0.1:8010")


def _dev_token(role: str) -> str:
    resp = requests.get(f"{BASE_URL}/api/v1/auth/dev-token?role={role}", timeout=10)
    resp.raise_for_status()
    return resp.json()["access_token"]


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _decode_token(token: str) -> dict:
    return auth_module.jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])


def test_admin_rbac_blocks_non_admin():
    token = _dev_token("user")
    resp = requests.get(
        f"{BASE_URL}/api/v1/admin/org/tree",
        headers=_auth_header(token),
        timeout=10,
    )
    assert resp.status_code in (401, 403), resp.text


def test_org_tree_structure_admin():
    token = _dev_token("admin")
    resp = requests.get(
        f"{BASE_URL}/api/v1/admin/org/tree",
        headers=_auth_header(token),
        timeout=10,
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data.get("ok") is True
    assert isinstance(data.get("data", {}).get("tree"), list)


def test_user_list_excludes_hashed_password():
    token = _dev_token("admin")
    resp = requests.get(
        f"{BASE_URL}/api/v1/admin/users",
        headers=_auth_header(token),
        timeout=10,
    )
    assert resp.status_code == 200, resp.text
    users = resp.json().get("data", {}).get("users", [])
    for user in users:
        assert "hashed_password" not in user


def test_session_revoke_blocks_token():
    token = _dev_token("admin")
    payload = _decode_token(token)
    session_id = payload.get("sid")
    assert session_id is not None

    revoke_resp = requests.post(
        f"{BASE_URL}/api/v1/admin/sessions/{session_id}/revoke",
        json={"reason": "test_revoke"},
        headers=_auth_header(token),
        timeout=10,
    )
    assert revoke_resp.status_code == 200, revoke_resp.text

    denied = requests.get(
        f"{BASE_URL}/api/v1/admin/org/tree",
        headers=_auth_header(token),
        timeout=10,
    )
    assert denied.status_code in (401, 403), denied.text

    bot_denied = requests.post(
        f"{BASE_URL}/api/v1/ai/bots/system_admin/run",
        json={"action": "org_chart_get", "data": {}},
        headers=_auth_header(token),
        timeout=10,
    )
    assert bot_denied.status_code in (401, 403), bot_denied.text


def test_audit_log_created_on_user_deactivate():
    token = _dev_token("admin")
    create_resp = requests.post(
        f"{BASE_URL}/api/v1/admin/users",
        json={"email": "audit_test@example.com", "full_name": "Audit Test", "role": "user"},
        headers=_auth_header(token),
        timeout=10,
    )
    assert create_resp.status_code == 200, create_resp.text
    user_id = create_resp.json().get("data", {}).get("id")

    deact_resp = requests.post(
        f"{BASE_URL}/api/v1/admin/users/{user_id}/deactivate",
        json={"reason": "test_deactivate"},
        headers=_auth_header(token),
        timeout=10,
    )
    assert deact_resp.status_code == 200, deact_resp.text

    audit_resp = requests.get(
        f"{BASE_URL}/api/v1/admin/audit",
        params={"action": "user_deactivate", "target_type": "user"},
        headers=_auth_header(token),
        timeout=10,
    )
    assert audit_resp.status_code == 200, audit_resp.text
    logs = audit_resp.json().get("data", {}).get("logs", [])
    assert any(str(log.get("target_id")) == str(user_id) for log in logs)


def test_system_admin_action_creates_audit_log():
    token = _dev_token("admin")
    create_resp = requests.post(
        f"{BASE_URL}/api/v1/admin/users",
        json={"email": "audit_bot@example.com", "full_name": "Audit Bot", "role": "user"},
        headers=_auth_header(token),
        timeout=10,
    )
    assert create_resp.status_code == 200, create_resp.text
    user_id = create_resp.json().get("data", {}).get("id")

    bot_resp = requests.post(
        f"{BASE_URL}/api/v1/ai/bots/system_admin/run",
        json={"action": "user_deactivate", "data": {"user_id": user_id}},
        headers=_auth_header(token),
        timeout=10,
    )
    assert bot_resp.status_code == 200, bot_resp.text
    assert bot_resp.json().get("ok") is True

    audit_resp = requests.get(
        f"{BASE_URL}/api/v1/admin/audit",
        params={"action": "user_deactivate", "target_type": "user"},
        headers=_auth_header(token),
        timeout=10,
    )
    assert audit_resp.status_code == 200, audit_resp.text
    logs = audit_resp.json().get("data", {}).get("logs", [])
    assert any(str(log.get("target_id")) == str(user_id) for log in logs)
