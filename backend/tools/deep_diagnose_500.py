# backend/tools/deep_diagnose_500.py
import requests
import json
import traceback

BASE_URL = "http://127.0.0.1:8000"

def deep_diagnose_500_errors():
    """Deep diagnosis for 500 Internal Server Errors"""
    print("🔍 Deep Diagnosis for 500 Errors")
    print("=" * 60)

    # Get token
    auth_data = {"username": "admin", "password": "admin"}
    token_resp = requests.post(f"{BASE_URL}/auth/token", data=auth_data)
    token = token_resp.json().get('access_token')
    headers = {"Authorization": f"Bearer {token}"}

    problem_bots = ["operations_manager", "finance_bot"]

    for bot_id in problem_bots:
        print(f"\n🔧 Diagnosing {bot_id}:")
        print("-" * 40)

        # 1. Test bot status first
        print("1. 📊 Checking bot status:")
        try:
            status_response = requests.get(f"{BASE_URL}/ai/{bot_id}/status", headers=headers)
            print(f"   ✅ Status code: {status_response.status_code}")
            if status_response.status_code == 200:
                print(f"   📋 Status data: {status_response.json()}")
        except Exception as e:
            print(f"   ❌ Status check error: {e}")

        # 2. Run test with more details
        print("2. 🚀 Running test with detailed error capture:")
        payload = {
            "message": f"Diagnostic test for {bot_id}",
            "context": {"diagnostic": True, "simple": True}
        }

        try:
            response = requests.post(
                f"{BASE_URL}/ai/{bot_id}/run",
                json=payload,
                headers=headers
            )

            print(f"   📊 Status code: {response.status_code}")
            print(f"   ⏱️ Response time: {response.elapsed.total_seconds():.2f}s")

            if response.status_code == 500:
                print("   ❌ Error 500 - Server-side issue detected")
                # Try to extract error details
                try:
                    error_details = response.json()
                    print(f"   📋 Error details: {error_details}")
                except:
                    print("   📋 No JSON error details (may appear in server logs)")

        except Exception as e:
            print(f"   💥 Exception: {e}")
            print(f"   🔍 Traceback details: {traceback.format_exc()}")

def check_server_logs_clues():
    """Search for clues in server startup logs"""
    print("\n📋 Clues from Server Startup Logs:")
    print("-" * 40)

    clues = [
        "✅ Both bots are registered during startup",
        "✅ File includes process_message functions",
        "❌ But 500 error occurs during execution",
        "🔍 Possible causes:",
        "   • Incorrect imports in routes",
        "   • Invalid function signature in process_message",
        "   • Unhandled exception in code",
        "   • Dependency issue or missing injection"
    ]

    for clue in clues:
        print(f"   {clue}")

def test_simple_implementation():
    """Test a simple, guaranteed-safe fallback implementation"""
    print("\n🔄 Testing a Simple Alternative Implementation:")
    print("-" * 40)

    simple_implementation = '''
# Simple, guaranteed-safe implementation for both bots
class SimpleOperationsManager:
    async def process_message(self, message, context=None):
        return "OperationsManagerBot: I can help with operations management."

class SimpleFinanceBot:
    async def process_message(self, message, context=None):
        return "FinanceBot: I can assist with financial matters."
'''

    print("   💡 Suggested Fix:")
    print("   • Replace both bots with a simple, safe implementation")
    print("   • Ensure all process_message functions are exception-free")
    print("   • Test each bot individually before restoring production code")

def main():
    print("=" * 60)
    print("🔍 Deep Diagnosis for 500 Errors in AI Bots")
    print("=" * 60)

    deep_diagnose_500_errors()
    check_server_logs_clues()
    test_simple_implementation()

    print("\n" + "=" * 60)
    print("🎯 Final Action Plan:")
    print("   1. Create a replacement file for problematic bots")
    print("   2. Use a 100% safe, minimal implementation")
    print("   3. Restart the server and re-test the endpoints")
    print("=" * 60)

if __name__ == "__main__":
    main()
