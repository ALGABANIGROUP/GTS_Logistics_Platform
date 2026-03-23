# backend/tools/test_fixed_bots.py
import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def test_fixed_bots():
    """Test the two bots that were recently fixed"""
    print("🧪 Testing the two fixed bots")
    print("=" * 50)

    # Wait a little to ensure the server has fully started
    time.sleep(2)

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

    # The bots that were fixed
    fixed_bots = [
        {
            "id": "operations_manager",
            "name": "Operations Manager",
            "test_cases": [
                "How can workflow efficiency be improved?",
                "What are the best practices in operations management?",
                "How can we reduce shipment cycle time?"
            ]
        },
        {
            "id": "finance_bot",
            "name": "Finance Assistant",
            "test_cases": [
                "What is the expense report for this month?",
                "How can cash flow be improved?",
                "What are the monthly operating costs?"
            ]
        }
    ]

    for bot in fixed_bots:
        print(f"\n🤖 {bot['name']} ({bot['id']}):")
        print("-" * 40)

        for i, test_message in enumerate(bot['test_cases'], 1):
            print(f"   {i}. 💬 {test_message}")

            payload = {
                "message": test_message,
                "context": {"test_case": i, "bot": bot['id']}
            }

            try:
                response = requests.post(
                    f"{BASE_URL}/ai/{bot['id']}/run",
                    json=payload,
                    headers=headers
                )

                if response.status_code == 200:
                    result = response.json()
                    response_text = result.get('response', '')
                    print(f"      ✅ {response_text}")
                elif response.status_code == 500:
                    print(f"      ❌ Error 500 - bot still needs fixing")
                else:
                    print(f"      ❌ Unexpected status: {response.status_code}")

            except Exception as e:
                print(f"      💥 Exception: {e}")

def test_all_6_bots_quick():
    """Quick test for all 6 bots"""
    print("\n🚀 Quick test for all 6 bots")
    print("=" * 50)

    auth_data = {"username": "admin", "password": "admin"}
    token_resp = requests.post(f"{BASE_URL}/auth/token", data=auth_data)
    token = token_resp.json().get('access_token')
    headers = {"Authorization": f"Bearer {token}"}

    all_bots = [
        ("general_manager", "General Manager"),
        ("freight_broker", "Freight Broker"),
        ("operations_manager", "Operations Manager"),
        ("finance_bot", "Finance Assistant"),
        ("documents_manager", "Documents Manager"),
        ("maintenance_dev", "Maintenance Assistant")
    ]

    results = []

    for bot_id, bot_name in all_bots:
        payload = {"message": f"Running test for {bot_name}", "context": {"quick_test": True}}

        try:
            response = requests.post(f"{BASE_URL}/ai/{bot_id}/run", json=payload, headers=headers)

            if response.status_code == 200:
                print(f"✅ {bot_name} - working")
                results.append(True)
            else:
                print(f"❌ {bot_name} - error {response.status_code}")
                results.append(False)

        except Exception as e:
            print(f"❌ {bot_name} - exception: {e}")
            results.append(False)

    successful = sum(results)
    print(f"\n📊 Result: {successful}/6 bots working")

    if successful == 6:
        print("🎉🎉🎉 All 6 bots are running successfully! 🎉🎉🎉")
    else:
        print(f"⚠️  {6 - successful} bots need inspection")

if __name__ == "__main__":
    test_fixed_bots()
    test_all_6_bots_quick()

    print("\n" + "=" * 50)
    print("🌐 Open the interface: http://127.0.0.1:8000/docs")
    print("🔐 Use: admin / admin")
    print("=" * 50)
