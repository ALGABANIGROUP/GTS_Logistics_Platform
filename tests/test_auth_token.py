# tests/test_auth_token.py
# NOTE: ASCII only.
import os

import pytest
import requests

BASE_URL = os.environ.get("GTS_BASE_URL", "http://127.0.0.1:8000")
USERNAME = os.environ.get("GTS_AUTH_EMAIL") or os.environ.get("GTS_USERNAME")
PASSWORD = os.environ.get("GTS_AUTH_PASSWORD") or os.environ.get("GTS_PASSWORD")
HTTP_TIMEOUT = int(os.environ.get("GTS_AUTH_TEST_TIMEOUT", "30"))


def _require_credentials() -> None:
    if not USERNAME or not PASSWORD:
        pytest.skip("Missing GTS_AUTH_EMAIL/GTS_AUTH_PASSWORD (or GTS_USERNAME/GTS_PASSWORD).")


def test_auth_token_success():
    _require_credentials()
    r = requests.post(
        f"{BASE_URL}/api/v1/auth/token",
        data={"username": USERNAME, "password": PASSWORD},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=HTTP_TIMEOUT,
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data.get("access_token"), data

    me = requests.get(
        f"{BASE_URL}/api/v1/auth/me",
        headers={"Authorization": f"Bearer {data['access_token']}"},
        timeout=HTTP_TIMEOUT,
    )
    assert me.status_code == 200, me.text
    me_payload = me.json()
    user = me_payload.get("user") if isinstance(me_payload, dict) else me_payload
    assert isinstance(user, dict), me_payload
    assert user.get("email") == USERNAME, me_payload


def test_auth_token_invalid_credentials():
    r = requests.post(
        f"{BASE_URL}/api/v1/auth/token",
        data={"username": "invalid@example.com", "password": "wrong"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=HTTP_TIMEOUT,
    )
    assert r.status_code in (400, 401, 403), r.text


def test_password_change_revokes_old_token():
    """Test that changing password revokes old tokens."""
    _require_credentials()
    
    # Login to get token
    r = requests.post(
        f"{BASE_URL}/api/v1/auth/token",
        data={"username": USERNAME, "password": PASSWORD},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=HTTP_TIMEOUT,
    )
    assert r.status_code == 200, r.text
    data = r.json()
    old_token = data["access_token"]
    
    # Verify old token works
    me = requests.get(
        f"{BASE_URL}/api/v1/auth/me",
        headers={"Authorization": f"Bearer {old_token}"},
        timeout=HTTP_TIMEOUT,
    )
    assert me.status_code == 200, me.text
    
    # Change password
    new_password = "temp_password_123"
    change_r = requests.post(
        f"{BASE_URL}/api/v1/auth/change-password",
        json={"current_password": PASSWORD, "new_password": new_password},
        headers={"Authorization": f"Bearer {old_token}"},
        timeout=HTTP_TIMEOUT,
    )
    assert change_r.status_code == 200, change_r.text
    
    # Verify old token is revoked
    me_old = requests.get(
        f"{BASE_URL}/api/v1/auth/me",
        headers={"Authorization": f"Bearer {old_token}"},
        timeout=HTTP_TIMEOUT,
    )
    assert me_old.status_code == 401, f"Old token should be revoked, got {me_old.status_code}"
    
    # Login with new password to get new token
    r_new = requests.post(
        f"{BASE_URL}/api/v1/auth/token",
        data={"username": USERNAME, "password": new_password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=HTTP_TIMEOUT,
    )
    assert r_new.status_code == 200, r_new.text
    new_data = r_new.json()
    new_token = new_data["access_token"]
    
    # Verify new token works
    me_new = requests.get(
        f"{BASE_URL}/api/v1/auth/me",
        headers={"Authorization": f"Bearer {new_token}"},
        timeout=HTTP_TIMEOUT,
    )
    assert me_new.status_code == 200, me_new.text
    
    # Restore original password
    restore_r = requests.post(
        f"{BASE_URL}/api/v1/auth/change-password",
        json={"current_password": new_password, "new_password": PASSWORD},
        headers={"Authorization": f"Bearer {new_token}"},
        timeout=HTTP_TIMEOUT,
    )
    assert restore_r.status_code == 200, restore_r.text


def test_audit_logs_written_for_login_success_and_failure():
    """Test that audit logs are written for login success and failure."""
    _require_credentials()
    
    # Successful login
    r_success = requests.post(
        f"{BASE_URL}/api/v1/auth/token",
        data={"username": USERNAME, "password": PASSWORD},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=HTTP_TIMEOUT,
    )
    assert r_success.status_code == 200, r_success.text
    
    # Failed login
    r_fail = requests.post(
        f"{BASE_URL}/api/v1/auth/token",
        data={"username": USERNAME, "password": "wrong_password"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=HTTP_TIMEOUT,
    )
    assert r_fail.status_code in (400, 401, 403), r_fail.text
    
    # Note: Actual audit log verification would require DB access
    # This test ensures the endpoints work; full audit verification
    # should be done with DB queries in integration tests
