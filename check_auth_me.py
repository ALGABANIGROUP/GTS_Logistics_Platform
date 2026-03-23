import json
import urllib.request
import urllib.parse
import urllib.error

base = "http://127.0.0.1:8000"

data = urllib.parse.urlencode({
    "username": "enjoy983@hotmail.com",
    "password": "password123",
    "grant_type": "password",
}).encode()

req = urllib.request.Request(
    base + "/api/v1/auth/token",
    data=data,
    headers={"Content-Type": "application/x-www-form-urlencoded"},
)
with urllib.request.urlopen(req) as resp:
    token_data = json.loads(resp.read().decode())

access_token = token_data["access_token"]

req = urllib.request.Request(
    base + "/api/v1/auth/me",
    headers={"Authorization": f"Bearer {access_token}"},
)
try:
    with urllib.request.urlopen(req) as resp:
        body = resp.read().decode()
        print("STATUS", resp.status)
        print(body)
except urllib.error.HTTPError as e:
    print("STATUS", e.code)
    print(e.read().decode())
