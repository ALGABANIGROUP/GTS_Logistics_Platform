# tests/test_partner_manager_http.py
# NOTE: ASCII only.
import os
import pytest
import requests

BASE_URL = os.environ.get("GTS_BASE_URL", "http://127.0.0.1:8010")


def _dev_token(role: str) -> str:
    try:
        resp = requests.get(f"{BASE_URL}/api/v1/auth/dev-token?role={role}", timeout=10)
    except requests.RequestException as exc:
        pytest.skip(f"Live partner manager backend unavailable at {BASE_URL}: {exc}")
    resp.raise_for_status()
    return resp.json()["access_token"]


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_partner_manager_run_denies_non_admin():
    token = _dev_token("customer")
    payload = {"action": "create_agreement", "partner_id": "p-101", "inputs": {"term": "net30"}}
    resp = requests.post(
        f"{BASE_URL}/api/v1/ai/bots/partner_manager/run",
        json=payload,
        headers=_auth_header(token),
        timeout=10,
    )
    assert resp.status_code in (401, 403), resp.text


def test_partner_manager_run_allows_admin():
    token = _dev_token("admin")
    payload = {"action": "create_agreement", "partner_id": "p-102", "inputs": {"term": "net30"}}
    resp = requests.post(
        f"{BASE_URL}/api/v1/ai/bots/partner_manager/run",
        json=payload,
        headers=_auth_header(token),
        timeout=10,
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    for key in ("ok", "action", "partner_id", "data", "warnings", "next_steps"):
        assert key in data, data
