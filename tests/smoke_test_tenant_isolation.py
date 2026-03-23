"""Multi-tenant isolation smoke test (external API-level).

This test suite verifies data isolation between tenants by exercising
critical endpoints. It is designed for a deployed environment and
requires BASE_URL and tokens to be configured.
"""

import os
import requests

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")
SUPER_ADMIN_TOKEN = os.getenv("SUPER_ADMIN_TOKEN", "")


def _auth_headers(token: str, tenant_id: str | None = None) -> dict:
    h = {"Authorization": f"Bearer {token}"}
    if tenant_id:
        h["X-Tenant-ID"] = tenant_id
    return h


def test_smoke_tenant_isolation():
    assert SUPER_ADMIN_TOKEN, "SUPER_ADMIN_TOKEN must be set"

    # 1) Create two tenants (admin-only)
    tenants = []
    for sub, name in [("company-a", "Company A"), ("company-b", "Company B")]:
        payload = {"id": sub, "subdomain": sub, "name": name}
        r = requests.post(f"{BASE_URL}/api/admin/tenants", json=payload, headers=_auth_headers(SUPER_ADMIN_TOKEN))
        assert r.status_code in (200, 201), r.text
        tenants.append(r.json()["id"])  # expect the created id

    tenant_a, tenant_b = tenants

    # 2) Create users under each tenant (simplified; depends on implementation)
    user_a_payload = {"email": "user.a@test.com", "password": "Test123!", "tenant_id": tenant_a}
    r = requests.post(f"{BASE_URL}/api/users", json=user_a_payload)
    assert r.status_code in (200, 201), r.text
    user_a_token = r.json().get("token") or r.json().get("access_token")

    user_b_payload = {"email": "user.b@test.com", "password": "Test123!", "tenant_id": tenant_b}
    r = requests.post(f"{BASE_URL}/api/users", json=user_b_payload)
    assert r.status_code in (200, 201), r.text
    user_b_token = r.json().get("token") or r.json().get("access_token")

    # 3) Ticket isolation (illustrative endpoints)
    r = requests.post(
        f"{BASE_URL}/api/tickets",
        json={"subject": "Ticket from A", "description": "Test"},
        headers=_auth_headers(user_a_token, tenant_a),
    )
    assert r.status_code in (200, 201), r.text
    ticket_a_id = r.json()["id"]

    r = requests.get(
        f"{BASE_URL}/api/tickets/{ticket_a_id}",
        headers=_auth_headers(user_b_token, tenant_b),
    )
    assert r.status_code in (403, 404), r.text

    # 4) Shipment isolation (illustrative endpoints)
    r = requests.post(
        f"{BASE_URL}/api/shipments",
        json={"tracking_number": "TRACK-A-001", "destination": "NYC"},
        headers=_auth_headers(user_a_token, tenant_a),
    )
    assert r.status_code in (200, 201), r.text
    shipment_a_id = r.json()["id"]

    r = requests.get(
        f"{BASE_URL}/api/shipments/{shipment_a_id}",
        headers=_auth_headers(user_b_token, tenant_b),
    )
    assert r.status_code in (403, 404), r.text

    # 5) Admin visibility (super admin should see all tenants' tickets)
    r = requests.get(f"{BASE_URL}/api/admin/tickets", headers=_auth_headers(SUPER_ADMIN_TOKEN))
    assert r.status_code == 200, r.text
