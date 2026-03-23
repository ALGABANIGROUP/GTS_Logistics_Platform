# backend/tools/quick_bot_test.py
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def quick_test():
    print("🚀 Quick Test for the 6 AI Bots")
    print("=" * 50)

    # Server health check
    try:
        health = requests.get(f"{BASE_URL}/health/ping")
        print(f"✅ Server health: {health.json()}")
    except:
        print("❌ Server not available")
        return

    # AI status check
    ai_status = requests.get(f"{BASE_URL}/ai/status")
    print(f"✅ AI status: {ai_status.json()}")

    # The 6 AI bots
    bots = [
        ("general_manager", "General Manager"),
        ("freight_broker", "Freight Broker"),
        ("operations_manager", "Operations Manager"),
        ("finance_bot", "Finance Assistant"),
        ("documents_manager", "Documents Manager"),
        ("maintenance_dev", "Maintenance Assistant")
    ]

    print("\n🤖 Testing the 6 AI Bots:")
    print("-" * 40)

    for bot_id, bot_name in bots:
        print(f"\n🔧 {bot_name} ({bot_id}):")

        # Test using AI ask endpoint
        payload = {
            "message": f"Hello {bot_name}, how can you help me with my work?",
            "bot_type": bot_id
        }

        try:
            response = requests.post(f"{BASE_URL}/ai/ask", json=payload)
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ {result.get('response', 'Success')[:70]}...")
            else:
                print(f"   ❌ Error: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")

if __name__ == "__main__":
    quick_test()
