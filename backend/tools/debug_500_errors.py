# backend/tools/debug_500_errors.py
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def get_auth_token():
    """Obtain an authentication token"""
    auth_data = {"username": "admin", "password": "admin"}
    response = requests.post(f"{BASE_URL}/auth/token", data=auth_data)
    return response.json().get('access_token')


def debug_operations_manager(token):
    """Diagnose the Operations Manager bot"""
    print("🔧 Diagnosing Operations Manager...")

    headers = {"Authorization": f"Bearer {token}"}

    # Detailed test payload
    payload = {
        "message": "How can workflow efficiency be improved?",
        "context": {"test": True, "debug": True}
    }

    try:
        response = requests.post(
            f"{BASE_URL}/ai/operations_manager/run",
            json=payload,
            headers=headers
        )
        print(f"   📊 Response status: {response.status_code}")

        if response.status_code == 500:
            print("   ❌ Internal Server Error")
            # Try to extract error details
            try:
                error_details = response.json()
                print(f"   📋 Error details: {error_details}")
            except:
                print("   📋 No error details available")

    except Exception as e:
        print(f"   💥 Exception: {e}")


def debug_finance_bot(token):
    """Diagnose the Finance Bot"""
    print("\n💰 Diagnosing Finance Bot...")

    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "message": "What is this month’s expense report?",
        "context": {"test": True, "debug": True}
    }

    try:
        response = requests.post(
            f"{BASE_URL}/ai/finance_bot/run",
            json=payload,
            headers=headers
        )
        print(f"   📊 Response status: {response.status_code}")

        if response.status_code == 500:
            print("   ❌ Internal Server Error")

    except Exception as e:
        print(f"   💥 Exception: {e}")


def test_alternative_routes(token):
    """Test alternative routes for AI endpoints"""
    print("\n🔄 Testing alternative routes...")

    headers = {"Authorization": f"Bearer {token}"}

    # General AI endpoint test directing to specific bots
    test_cases = [
        {
            "message": "How can we improve operational and shipping efficiency?",
            "bot_type": "operations_manager",
            "description": "Operations via general AI"
        },
        {
            "message": "I need financial analysis and expense reports",
            "bot_type": "finance_bot",
            "description": "Finance via general AI"
        }
    ]

    for test in test_cases:
        print(f"\n   🔄 {test['description']}:")
        try:
            response = requests.post(
                f"{BASE_URL}/ai/ask",
                json=test,
                headers=headers
            )
            if response.status_code == 200:
                result = response.json()
                print(f"      ✅ {result.get('response', 'Success')[:60]}...")
            else:
                print(f"      ❌ {response.status_code}")
        except Exception as e:
            print(f"      💥 {e}")


def main():
    print("=" * 60)
    print("🔍 Diagnosing 500 Errors for AI Bots")
    print("=" * 60)

    token = get_auth_token()
    if not token:
        print("❌ Failed to obtain authentication token")
        return

    debug_operations_manager(token)
    debug_finance_bot(token)
    test_alternative_routes(token)

    print("\n" + "=" * 60)
    print("💡 Suggested Solutions:")
    print("   • Check the bot files in backend/core/ai_core.py")
    print("   • Review module imports under routes/")
    print("   • Ensure each bot has a complete process_message() method")
    print("=" * 60)


if __name__ == "__main__":
    main()
