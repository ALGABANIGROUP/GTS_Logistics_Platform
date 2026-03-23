# backend/tools/test_restarted_bots.py
import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def wait_for_server():
    """Wait for the server to start"""
    print("⏳ Waiting for the server to start...")
    for i in range(10):
        try:
            response = requests.get(f"{BASE_URL}/health/ping", timeout=5)
            if response.status_code == 200:
                print("✅ Server is running!")
                return True
        except:
            if i < 9:
                print(f"   Attempt {i+1}/10...")
                time.sleep(2)
            else:
                print("❌ Failed to start the server")
                return False
    return False

def test_restarted_bots():
    """Test the two bots after server restart"""
    print("\n🧪 Testing bots after server restart")
    print("=" * 50)

    # Get authentication token
    auth_data = {"username": "admin", "password": "admin"}
    try:
        token_resp = requests.post(f"{BASE_URL}/auth/token", data=auth_data)
        token = token_resp.json().get('access_token')
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Authentication successful")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return

    # The two bots we were fixing
    fixed_bots = [
        {
            "id": "operations_manager",
            "name": "Operations Manager",
            "test_message": "How can workflow efficiency be improved?"
        },
        {
            "id": "finance_bot",
            "name": "Finance Assistant",
            "test_message": "What is the expense report for this month?"
        }
    ]

    for bot in fixed_bots:
        print(f"\n🔧 {bot['name']}:")
        print(f"   💬 Question: {bot['test_message']}")

        # Run the test
        payload = {
            "message": bot["test_message"],
            "context": {"after_restart": True}
        }

        try:
            response = requests.post(
                f"{BASE_URL}/ai/{bot['id']}/run",
                json=payload,
                headers=headers
            )

            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Success! Response: {result.get('response', 'Processed successfully')}")
            elif response.status_code == 500:
                print(f"   ❌ Still 500 error - needs file inspection")
            else:
                print(f"   ❌ Unexpected status: {response.status_code}")

        except Exception as e:
            print(f"   💥 Error: {e}")

def main():
    print("=" * 60)
    print("🔄 Testing bots after server restart")
    print("=" * 60)

    if not wait_for_server():
        return

    test_restarted_bots()

    print("\n" + "=" * 60)
    print("🎯 If ❌ appears, try this final fix:")
    print("   1. Stop the server (Ctrl+C)")
    print("   2. Run: python backend/tools/complete_bot_fix.py")
    print("   3. Restart the server")
    print("=" * 60)

if __name__ == "__main__":
    main()
