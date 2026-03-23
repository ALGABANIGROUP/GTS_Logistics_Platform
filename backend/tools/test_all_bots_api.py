# backend/tools/test_all_bots_api.py
import requests
import json
import asyncio

BASE_URL = "http://127.0.0.1:8000"

def test_all_bots():
    """Test all 6 AI bots via API"""
    print("🧪 Testing the 6 AI bots through API")
    print("=" * 50)

    # 1. Get the list of bots
    print("1. 📋 Fetching the list of bots...")
    try:
        response = requests.get(f"{BASE_URL}/ai/bots")
        if response.status_code == 200:
            bots = response.json()
            print(f"✅ Found {len(bots)} bots")
            for bot in bots:
                print(f"   🤖 {bot}")
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    print("\n2. 🔧 Testing bot execution...")

    # Expected 6 core bots
    expected_bots = [
        "general_manager",
        "freight_broker",
        "operations_manager",
        "finance_bot",
        "documents_manager",
        "maintenance_dev"
    ]

    successful_tests = 0

    for bot_name in expected_bots:
        print(f"\n   Testing bot: {bot_name}")

        # Test bot status
        try:
            status_response = requests.get(f"{BASE_URL}/ai/{bot_name}/status")
            if status_response.status_code == 200:
                print(f"      ✅ Status: {status_response.json()}")
            else:
                print(f"      ❌ Bot status failed: {status_response.status_code}")
                continue
        except Exception as e:
            print(f"      ❌ Error fetching bot status: {e}")
            continue

        # Test bot execution
        try:
            run_payload = {
                "message": f"Hello {bot_name}, how can you assist me today?",
                "context": {"test": True}
            }

            run_response = requests.post(
                f"{BASE_URL}/ai/{bot_name}/run",
                json=run_payload
            )

            if run_response.status_code == 200:
                result = run_response.json()
                print(f"      ✅ Execution: {result.get('response', 'Success')[:60]}...")
                successful_tests += 1
            else:
                print(f"      ❌ Execution failed: {run_response.status_code}")

        except Exception as e:
            print(f"      ❌ Error during execution: {e}")

    print(f"\n📊 Results: {successful_tests}/6 bots passed the test")

    if successful_tests == 6:
        print("🎉 All 6 bots are working perfectly through the API!")
        return True
    else:
        print("⚠️ Some bots need to be checked")
        return False

def test_ai_gateway():
    """Test the general AI Gateway"""
    print("\n3. 🌐 Testing the general AI Gateway...")

    try:
        payload = {
            "query": "I need help managing shipments and finance."
        }

        response = requests.post(f"{BASE_URL}/ai/ask", json=payload)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ AI Gateway: {result.get('answer', 'Success')[:80]}...")
            return True
        else:
            print(f"❌ AI Gateway failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error in AI Gateway: {e}")
        return False

def test_finance_ai():
    """Test the Financial AI Analysis"""
    print("\n4. 💰 Testing financial analysis...")

    try:
        response = requests.get(f"{BASE_URL}/ai/finance-analysis")

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Financial Analysis: {result.get('analysis', 'Available')}")
            return True
        else:
            print(f"❌ Financial Analysis failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error in financial analysis: {e}")
        return False

def main():
    """Main test runner"""
    print("=" * 60)
    print("🚀 Comprehensive test for all 6 AI bots")
    print("=" * 60)

    # Check system health first
    try:
        health_response = requests.get(f"{BASE_URL}/health/ping")
        if health_response.status_code == 200:
            print("✅ System is healthy and ready for testing")
        else:
            print("❌ System health check failed")
            return
    except:
        print("❌ Cannot reach the system - make sure the server is running")
        return

    # Run all tests
    bots_ok = test_all_bots()
    gateway_ok = test_ai_gateway()
    finance_ok = test_finance_ai()

    print("\n" + "=" * 60)
    print("📋 Final Report:")
    print(f"   • 6 Bots: {'✅' if bots_ok else '❌'}")
    print(f"   • AI Gateway: {'✅' if gateway_ok else '❌'}")
    print(f"   • Financial Analysis: {'✅' if finance_ok else '❌'}")

    if bots_ok and gateway_ok and finance_ok:
        print("🎉🎉🎉 All systems operational! 🎉🎉🎉")
        print("\n🌐 Available Endpoints:")
        print("   • 📚 API Docs: http://127.0.0.1:8000/docs")
        print("   • 🔍 Bots: http://127.0.0.1:8000/ai/bots")
        print("   • 💰 Finance: http://127.0.0.1:8000/finance/health")
    else:
        print("⚠️ Some issues require attention")

    print("=" * 60)

if __name__ == "__main__":
    main()
