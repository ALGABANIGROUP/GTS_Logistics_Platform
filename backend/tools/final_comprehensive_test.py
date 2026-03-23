# backend/tools/final_comprehensive_test.py
import requests
import time
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def wait_for_server():
    """Wait for the server to start"""
    print("⏳ Waiting for the server to start...")
    for i in range(8):
        try:
            response = requests.get(f"{BASE_URL}/health/ping", timeout=5)
            if response.status_code == 200:
                print("✅ Server is running and ready for testing!")
                return True
        except:
            if i < 7:
                print(f"   Attempt {i+1}/8...")
                time.sleep(2)
            else:
                print("❌ Server failed to start")
                return False
    return False

def get_auth_token():
    """Obtain authentication token"""
    print("\n🔐 Getting authentication token...")
    auth_data = {"username": "admin", "password": "admin"}
    try:
        response = requests.post(f"{BASE_URL}/auth/token", data=auth_data)
        if response.status_code == 200:
            token_info = response.json()
            print("✅ Authentication successful!")
            return token_info.get('access_token')
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

def test_all_6_bots_comprehensive(token):
    """Comprehensive test for all 6 bots"""
    print("\n🤖 Comprehensive test for all 6 bots")
    print("=" * 60)

    headers = {"Authorization": f"Bearer {token}"}

    # Define all bots
    all_bots = [
        {
            "id": "general_manager",
            "name": "General Manager",
            "description": "Strategic planning and business management",
            "test_messages": [
                "What is the company’s growth strategy for this year?",
                "How can we improve team productivity?",
                "What are the company’s priorities for the next quarter?"
            ]
        },
        {
            "id": "freight_broker",
            "name": "Freight Broker",
            "description": "Shipment and logistics management",
            "test_messages": [
                "How can I manage a shipment from Riyadh to Dubai?",
                "What’s the best way to track shipment status?",
                "How can we negotiate better freight rates?"
            ]
        },
        {
            "id": "operations_manager",
            "name": "Operations Manager",
            "description": "Workflow and operations management",
            "test_messages": [
                "How can we improve workflow efficiency?",
                "What are the best practices for operations management?",
                "How can we reduce shipment cycle time?"
            ]
        },
        {
            "id": "finance_bot",
            "name": "Finance Assistant",
            "description": "Financial reporting and analysis",
            "test_messages": [
                "What is this month’s expense report?",
                "How can we improve cash flow?",
                "What are the monthly operating costs?"
            ]
        },
        {
            "id": "documents_manager",
            "name": "Documents Manager",
            "description": "Document organization and management",
            "test_messages": [
                "How can I organize shipping documents?",
                "What documents are required for export?",
                "How can we manage contracts more efficiently?"
            ]
        },
        {
            "id": "maintenance_dev",
            "name": "Maintenance Assistant",
            "description": "System monitoring and maintenance",
            "test_messages": [
                "What’s the current system status?",
                "How can we monitor database performance?",
                "What are the latest system updates?"
            ]
        }
    ]

    results = {}

    for bot in all_bots:
        print(f"\n🔧 {bot['name']} ({bot['description']}):")
        print("-" * 50)

        bot_results = []

        for i, test_message in enumerate(bot['test_messages'], 1):
            print(f"   {i}. 💬 {test_message}")

            payload = {
                "message": test_message,
                "context": {
                    "test_case": i,
                    "bot": bot['id'],
                    "timestamp": datetime.now().isoformat()
                }
            }

            try:
                start_time = time.time()
                response = requests.post(
                    f"{BASE_URL}/ai/{bot['id']}/run",
                    json=payload,
                    headers=headers
                )
                response_time = time.time() - start_time

                if response.status_code == 200:
                    result = response.json()
                    response_text = result.get('response', '')
                    print(f"      ✅ ({response_time:.2f}s) {response_text[:60]}...")
                    bot_results.append(True)
                else:
                    print(f"      ❌ Error {response.status_code} (Time: {response_time:.2f}s)")
                    bot_results.append(False)

            except Exception as e:
                print(f"      💥 Exception: {e}")
                bot_results.append(False)

        # Calculate bot success rate
        success_rate = sum(bot_results) / len(bot_results) * 100
        status = "✅" if success_rate == 100 else "⚠️" if success_rate >= 50 else "❌"
        results[bot['id']] = {
            "success_rate": success_rate,
            "status": status,
            "tests_passed": sum(bot_results),
            "total_tests": len(bot_results)
        }

        print(f"   📊 Bot Result: {status} {success_rate:.1f}% ({sum(bot_results)}/{len(bot_results)})")

    return results

def generate_final_report(results):
    """Generate the final report"""
    print("\n" + "=" * 60)
    print("📊 Final Comprehensive Report")
    print("=" * 60)

    total_bots = len(results)
    fully_working = sum(1 for r in results.values() if r['success_rate'] == 100)
    partially_working = sum(1 for r in results.values() if 50 <= r['success_rate'] < 100)
    not_working = sum(1 for r in results.values() if r['success_rate'] < 50)

    print(f"🤖 Bot Statistics:")
    print(f"   • ✅ Fully operational: {fully_working}/{total_bots}")
    print(f"   • ⚠️  Partially working: {partially_working}/{total_bots}")
    print(f"   • ❌ Not working: {not_working}/{total_bots}")

    print(f"\n📈 Overall success rate: {(fully_working/total_bots)*100:.1f}%")

    print(f"\n🎯 System Status: ", end="")
    if fully_working == 6:
        print("🟢 Excellent - all 6 bots are fully operational!")
    elif fully_working >= 4:
        print("🟡 Very Good - system is production-ready")
    elif fully_working >= 2:
        print("🟠 Acceptable - can be used with some limitations")
    else:
        print("🔴 Needs improvement")

    print(f"\n📋 Bot Details:")
    for bot_id, result in results.items():
        status_icon = result['status']
        print(f"   {status_icon} {bot_id}: {result['success_rate']:.1f}% ({result['tests_passed']}/{result['total_tests']})")

def test_api_endpoints(token):
    """Test additional API endpoints"""
    print("\n🌐 Testing additional API endpoints:")
    print("-" * 40)

    headers = {"Authorization": f"Bearer {token}"}

    endpoints = [
        ("GET /ai/bots", "List of bots"),
        ("GET /health/ping", "System health"),
        ("GET /ai/status", "AI system status")
    ]

    for endpoint, description in endpoints:
        try:
            if endpoint.startswith("GET"):
                response = requests.get(f"{BASE_URL}{endpoint.split(' ')[1]}", headers=headers)
            else:
                response = requests.post(f"{BASE_URL}{endpoint.split(' ')[1]}", headers=headers)

            status = "✅" if response.status_code == 200 else "❌"
            print(f"   {status} {endpoint} - {description} ({response.status_code})")

        except Exception as e:
            print(f"   ❌ {endpoint} - {description} (Error: {e})")

def main():
    print("=" * 60)
    print("🎯 Final Comprehensive System Test")
    print("=" * 60)

    # Wait until the server is ready
    if not wait_for_server():
        return

    # Get authentication token
    token = get_auth_token()
    if not token:
        return

    # Test all bots
    results = test_all_6_bots_comprehensive(token)

    # Test API endpoints
    test_api_endpoints(token)

    # Generate the final report
    generate_final_report(results)

    print("\n" + "=" * 60)
    print("🚀 Next Steps:")
    print("   1. 🌐 Open http://127.0.0.1:8000/docs for the interactive API UI")
    print("   2. 🔐 Click Authorize (top right) and paste your authentication token")
    print("   3. 🤖 Start using the bots practically")
    print("   4. 📞 Integrate the system with your other applications")

    if sum(1 for r in results.values() if r['success_rate'] == 100) == 6:
        print("\n🎉🎉🎉 Congratulations! The system is fully functional! 🎉🎉🎉")
    else:
        print("\n✅ The system is ready for use with partially working bots")

    print("=" * 60)

if __name__ == "__main__":
    main()
