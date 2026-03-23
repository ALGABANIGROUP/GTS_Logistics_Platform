"""Test MapleLoad Canada endpoints"""
import requests

base_url = "http://localhost:8000/api/v1/ai/bots/mapleload-canada"

endpoints = [
    "/status",
    "/load-sources/canadian",
    "/load-sources/load-boards",
    "/load-sources/warehouses",
    "/load-sources/search",
    "/load-sources/stats"
]

print("Testing MapleLoad Canada endpoints...\n")

for ep in endpoints:
    url = base_url + ep
    try:
        response = requests.get(url, timeout=5)
        print(f"✓ {ep:40} -> {response.status_code}")
        if response.status_code != 200:
            print(f"  Error: {response.text[:100]}")
    except Exception as e:
        print(f"✗ {ep:40} -> ERROR: {e}")

print("\nDone!")
