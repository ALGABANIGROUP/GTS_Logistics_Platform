# backend/tools/comprehensive_bot_test.py
try:
    import requests  # type: ignore
except Exception:
    requests = None
import time

BASE_URL = "http://127.0.0.1:8000"

def test_all_bots_comprehensive():
    if requests is None:
        print("requests is not installed. Install requests to run this test.")
        return
    print("🎯 Comprehensive Test for All 6 AI Bots")
    print("=" * 60)

    # Define bots and their test messages
    bot_tests = [
        {
            "id": "general_manager",
            "name": "General Manager",
            "message": "What is the proposed growth strategy for the company this quarter?",
            "expected_keywords": ["strategy", "growth", "management"]
        },
        {
            "id": "freight_broker",
            "name": "Freight Broker",
            "message": "I need to deliver a shipment from Riyadh to Dubai next week.",
            "expected_keywords": ["shipment", "delivery", "freight"]
        },
        {
            "id": "operations_manager",
            "name": "Operations Manager",
            "message": "How can we improve supply chain efficiency?",
            "expected_keywords": ["operations", "efficiency", "improvement"]
        },
        {
            "id": "finance_bot",
            "name": "Finance Assistant",
            "message": "What is the cost and revenue analysis for this month?",
            "expected_keywords": ["financial", "cost", "revenue"]
        },
        {
            "id": "documents_manager",
            "name": "Documents Manager",
            "message": "How can I organize shipping documents and contracts?",
            "expected_keywords": ["documents", "organization", "contracts"]
        },
        {
            "id": "maintenance_dev",
            "name": "Maintenance Assistant",
            "message": "What are the latest system updates and how can performance be improved?",
            "expected_keywords": ["system", "updates", "performance"]
        }
    ]

    successful_tests = 0

    for test in bot_tests:
        print(f"\n🧪 Testing {test['name']} ({test['id']}):")
        print(f"   💬 Question: {test['message']}")

        payload = {
            "message": test["message"],
            "bot_type": test["id"]
        }

        try:
            start_time = time.time()
            response = requests.post(f"{BASE_URL}/ai/ask", json=payload)
            response_time = time.time() - start_time

            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '')

                # Check for expected keywords
                found_keywords = [kw for kw in test['expected_keywords'] if kw in response_text]

                print(f"   ✅ Response: {response_text[:80]}...")
                print(f"   ⏱️  Response Time: {response_time:.2f} seconds")
                print(f"   🔍 Found Keywords: {found_keywords}")

                if len(found_keywords) >= 1:
                    successful_tests += 1
                    print(f"   🎯 Result: Passed")
                else:
                    print(f"   ⚠️  Result: Unexpected Response")
            else:
                print(f"   ❌ Error: {response.status_code}")

        except Exception as e:
            print(f"   💥 Exception: {e}")

    print("\n" + "=" * 60)
    print(f"📊 Final Results: {successful_tests}/6 bots passed")

    if successful_tests == 6:
        print("🎉🎉🎉 All 6 bots are working perfectly! 🎉🎉🎉")
    elif successful_tests >= 4:
        print("✅ Most bots are functioning well.")
    else:
        print("⚠️  Some bots need further inspection.")

    print("=" * 60)

if __name__ == "__main__":
    test_all_bots_comprehensive()
# backend/tools/comprehensive_bot_test.py
