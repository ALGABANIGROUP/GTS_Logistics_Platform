# backend/tools/simple_bot_test_no_auth.py
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_accessible_routes():
    """Test routes that do not require authentication"""
    print("🧪 Testing routes accessible without authentication")
    print("=" * 50)

    # Routes that work without authentication
    test_cases = [
        {
            "url": "/ai/status",
            "method": "GET",
            "payload": None,
            "description": "AI system status"
        },
        {
            "url": "/health/ping",
            "method": "GET",
            "payload": None,
            "description": "System health check"
        },
        {
            "url": "/ai/ask",
            "method": "POST",
            "payload": {
                "message": "Hello, what bots are available in the system?",
                "bot_type": "general"
            },
            "description": "General AI question"
        }
    ]

    for test in test_cases:
        print(f"\n🔍 {test['description']}:")
        print(f"   📍 {test['method']} {test['url']}")

        try:
            if test['method'] == 'GET':
                response = requests.get(BASE_URL + test['url'])
            else:
                response = requests.post(
                    BASE_URL + test['url'],
                    json=test['payload']
                )

            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success - {data}")
            else:
                print(f"   ❌ Failed - {response.status_code}")

        except Exception as e:
            print(f"   💥 Error - {e}")

def test_bots_directly():
    """Test the six AI bots directly"""
    print("\n" + "=" * 50)
    print("🤖 Testing the 6 core AI bots directly")
    print("=" * 50)

    bots = [
        "general_manager",
        "freight_broker",
        "operations_manager",
        "finance_bot",
        "documents_manager",
        "maintenance_dev"
    ]

    for bot_name in bots:
        print(f"\n🔧 Testing {bot_name}:")

        # Test bot status
        try:
            status_response = requests.get(f"{BASE_URL}/ai/{bot_name}/status")
            if status_response.status_code == 200:
                print(f"   ✅ Status: {status_response.json()}")
            else:
                print(f"   ❌ Status: {status_response.status_code} (may require authentication)")
        except Exception as e:
            print(f"   💥 Status error: {e}")

        # Test bot run
        try:
            payload = {
                "message": f"Hello {bot_name}, how can you assist me?",
                "context": {"test": True}
            }
            run_response = requests.post(
                f"{BASE_URL}/ai/{bot_name}/run",
                json=payload
            )
            if run_response.status_code == 200:
                result = run_response.json()
                print(f"   ✅ Run: {result.get('response', 'Success')[:50]}...")
            else:
                print(f"   ❌ Run: {run_response.status_code} (may require authentication)")
        except Exception as e:
            print(f"   💥 Run error: {e}")

def main():
    """Main test function"""
    print("🚀 Starting test for the 6 AI bots")
    print("Note: Make sure the server is running on port 8000")
    print("=" * 60)

    try:
        # Test server connection first
        response = requests.get(f"{BASE_URL}/health/ping", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and ready for testing")
        else:
            print("❌ Server is not responding properly")
            return
    except:
        print("❌ Cannot reach the server - make sure it’s running:")
        print("   python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload")
        return

    # Run tests
    test_accessible_routes()
    test_bots_directly()

    print("\n" + "=" * 60)
    print("💡 Notes:")
    print("   • Routes showing 401 require authentication")
    print("   • Use /docs for the interactive API: http://127.0.0.1:8000/docs")
    print("   • Use /auth/token to obtain an authentication token")
    print("=" * 60)

if __name__ == "__main__":
    main()
