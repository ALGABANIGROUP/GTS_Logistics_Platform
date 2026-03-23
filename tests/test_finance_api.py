# tests/test_finance_api.py
# NOTE: ASCII only.
import os
import requests

BASE_URL = os.environ.get("GTS_BASE_URL", "http://127.0.0.1:8001")
USERNAME = os.environ.get("GTS_USERNAME", "yassir")
ROLE = os.environ.get("GTS_ROLE", "admin")
EXPIRES_MIN = int(os.environ.get("GTS_TOKEN_MIN", "60"))

def _token():
    r = requests.post(f"{BASE_URL}/auth/token",
                      json={"username": USERNAME, "role": ROLE, "expires_minutes": EXPIRES_MIN},
                      timeout=10)
    r.raise_for_status()
    return r.json()["access_token"]

def _h(tok: str):
    return {"Authorization": f"Bearer {tok}"}

def test_finance_health_ok():
    tok = _token()
    r = requests.get(f"{BASE_URL}/finance/health", headers=_h(tok), timeout=10)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data.get("ok") is True
    assert data.get("db_ok") is True

def test_expense_crud_flow():
    tok = _token()
    h = _h(tok)

    # Create
    body = {"category": "fuel", "amount": 25.75, "description": "pytest", "vendor": "cli", "status": "PENDING"}
    r = requests.post(f"{BASE_URL}/finance/expenses", headers=h, json=body, timeout=10)
    assert r.status_code in (200, 201), r.text
    exp_id = r.json()["id"]

    # List
    r = requests.get(f"{BASE_URL}/finance/expenses", headers=h, timeout=10)
    assert r.status_code == 200, r.text

    # Toggle
    r = requests.put(f"{BASE_URL}/finance/expenses/{exp_id}/status", headers=h, timeout=10)
    assert r.status_code == 200, r.text
    assert r.json()["status"] in ("PENDING", "PAID")

    # Summary
    r = requests.get(f"{BASE_URL}/finance/summary", headers=h, timeout=10)
    assert r.status_code == 200, r.text

    # Delete
    r = requests.delete(f"{BASE_URL}/finance/expenses/{exp_id}", headers=h, timeout=10)
    assert r.status_code in (200, 202, 204), r.text
