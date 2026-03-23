# backend/tools/test_with_auth.py
import requests

BASE_URL = "http://127.0.0.1:8000"

def get_token():
    """Get authentication token"""
    # These are default credentials – adjust them based on your auth settings
    auth_data = {
        "username": "admin",
        "password": "admin"
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/token", data=auth_data)
        if response.status_code == 200:
            token_data = response.json()
            print(f"✅ Token obtained successfully: {token_data.get('token_type')}")
            return token_data.get('access_token')
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

# Test with token
token = get_token()
if token:
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/ai/bots", headers=headers)
    print(f"Bot list with authentication: {response.status_code}")
