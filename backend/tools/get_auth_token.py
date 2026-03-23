# backend/tools/get_auth_token.py
import requests

BASE_URL = "http://127.0.0.1:8000"

def get_auth_token():
    """Obtain an authentication token"""
    print("🔐 Attempting to obtain authentication token...")

    # Try different authentication credentials
    auth_attempts = [
        {"username": "admin", "password": "admin"},
        {"username": "test", "password": "test"},
        {"username": "user", "password": "user"},
        {"username": "gts", "password": "gts"},
    ]

    for auth_data in auth_attempts:
        try:
            print(f"   🔑 Trying: {auth_data}")
            response = requests.post(
                f"{BASE_URL}/auth/token",
                data=auth_data
            )

            if response.status_code == 200:
                token_info = response.json()
                print(f"   ✅ Authentication successful!")
                print(f"      Token type: {token_info.get('token_type')}")
                print(f"      Access token: {token_info.get('access_token')}")
                return token_info.get('access_token')
            else:
                print(f"   ❌ Failed: {response.status_code}")

        except Exception as e:
            print(f"   💥 Error: {e}")

    print("   🤔 All authentication attempts failed")
    return None

def test_with_token(token):
    """Test the bots using the authentication token"""
    if not token:
        return

    headers = {"Authorization": f"Bearer {token}"}

    print(f"\n🚀 Testing the 6 bots with authentication:")
    print("=" * 50)

    bots = [
        "general_manager",
        "freight_broker",
        "operations_manager",
        "finance_bot",
        "documents_manager",
        "maintenance_dev"
    ]

    for bot_id in bots:
        print(f"\n🔧 {bot_id}:")

        # Test bot status
        try:
            status_response = requests.get(
                f"{BASE_URL}/ai/{bot_id}/status",
                headers=headers
            )
            if status_response.status_code == 200:
                print(f"   ✅ Status: {status_response.json()}")
            else:
                print(f"   ❌ Status: {status_response.status_code}")
                continue
        except Exception as e:
            print(f"   💥 Error checking status: {e}")
            continue

        # Test bot execution
        try:
            payload = {
                "message": f"Hello {bot_id}, how can you assist me?",
                "context": {"test": True}
            }
            run_response = requests.post(
                f"{BASE_URL}/ai/{bot_id}/run",
                json=payload,
                headers=headers
            )
            if run_response.status_code == 200:
                result = run_response.json()
                print(f"   ✅ Execution: {result.get('response', 'Success')[:60]}...")
            else:
                print(f"   ❌ Execution: {run_response.status_code}")
        except Exception as e:
            print(f"   💥 Error during execution: {e}")

if __name__ == "__main__":
    token = get_auth_token()
    if token:
        test_with_token(token)
    else:
        print("\n💡 Suggested Solutions:")
        print("   1. Check authentication settings in backend/core/config.py")
        print("   2. Try adding a default user to the system")
        print("   3. Review routes files for authentication requirements")
