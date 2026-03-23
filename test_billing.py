import requests

BASE_URL = "http://127.0.0.1:8000"

login_response = requests.post(
    f"{BASE_URL}/api/v1/auth/token",
    data={"username": "admin@gabanilogistics.com", "password": "Admin@2026"},
    timeout=20,
)

if login_response.status_code != 200:
    print("Failed to get token:", login_response.status_code, login_response.text)
    raise SystemExit(1)

token = login_response.json().get("access_token")
print("Token obtained successfully")

headers = {"Authorization": f"Bearer {token}"}

plans_response = requests.get(f"{BASE_URL}/api/v1/billing/plans", timeout=20)
print("Public plans response:", plans_response.status_code)
print("Public plans preview:", plans_response.text[:300])

catalog_response = requests.get(
    f"{BASE_URL}/api/v1/admin/billing/catalog",
    headers=headers,
    timeout=20,
)
print("Admin catalog response:", catalog_response.status_code)
print("Admin catalog preview:", catalog_response.text[:300])
