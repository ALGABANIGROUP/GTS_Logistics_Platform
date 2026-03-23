import requests
import json

# Get token
resp = requests.post('http://127.0.0.1:8000/api/v1/auth/token', data={'username': 'admin@gts.local', 'password': 'admin123'})
token =resp.json()['access_token']
print(f"✓ Got authentication token")

# Get available bots
res = requests.get('http://127.0.0.1:8000/api/v1/bots/available', headers={'Authorization': f'Bearer {token}'})
bots = res.json()['bots']
print(f"\n✓ Found {len(bots)} available bots:")
for bot in bots[:5]:
    print(f"  - {bot['bot_key']}: {bot['display_name']}")

# Check for general_manager
gm_exists = any(b['bot_key'] == 'general_manager' for b in bots)
print(f"\n{'✓' if gm_exists else '✗'} general_manager is {'available' if gm_exists else 'NOT found'}")

# Get general_manager status
print("\n📊 Testing /api/v1/bots/general_manager/status endpoint:")
status_res = requests.get('http://127.0.0.1:8000/api/v1/bots/general_manager/status', headers={'Authorization': f'Bearer {token}'})
print(f"Status: {status_res.status_code}")
print(json.dumps(status_res.json(), indent=2))

# Also test the shim endpoint
print("\n📊 Testing /api/v1/ai/bots/available/general_manager/status endpoint (shim):")
shim_res = requests.get('http://127.0.0.1:8000/api/v1/ai/bots/available/general_manager/status', headers={'Authorization': f'Bearer {token}'})
print(f"Status: {shim_res.status_code}")
print(json.dumps(shim_res.json(), indent=2))
