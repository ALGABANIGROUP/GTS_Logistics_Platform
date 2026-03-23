# backend/tools/test_bots_with_auth.py
import requests
import json

BASE_URL = "http://127.0.0.1:8000"


class BotTester:
    def __init__(self):
        self.token = None
        self.bots = [
            "general_manager",
            "freight_broker",
            "operations_manager",
            "finance_bot",
            "documents_manager",
            "maintenance_dev"
        ]

    def get_auth_headers(self):
        """Get authentication headers"""
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}

    def get_bots_list(self):
        """Fetch the list of bots"""
        print("📋 Fetching bot list...")
        try:
            response = requests.get(
                f"{BASE_URL}/ai/bots",
                headers=self.get_auth_headers()
            )
            if response.status_code == 200:
                bots = response.json()
                print(f"✅ Found {len(bots)} bots")
                return bots
            else:
                print(f"⚠️  Could not fetch bots (may require auth): {response.status_code}")
                return self.bots  # use default list
        except Exception as e:
            print(f"❌ Error: {e}")
            return self.bots

    def test_bot_status(self, bot_name):
        """Test bot status"""
        try:
            response = requests.get(
                f"{BASE_URL}/ai/{bot_name}/status",
                headers=self.get_auth_headers()
            )
            if response.status_code == 200:
                status = response.json()
                return f"✅ {status}"
            else:
                return f"❌ {response.status_code}"
        except Exception as e:
            return f"❌ {e}"

    def test_bot_run(self, bot_name):
        """Test bot execution"""
        payload = {
            "message": f"Hello {bot_name}, how can you assist in managing operations?",
            "context": {"test": True, "department": bot_name.split('_')[0]}
        }

        try:
            response = requests.post(
                f"{BASE_URL}/ai/{bot_name}/run",
                json=payload,
                headers=self.get_auth_headers()
            )
            if response.status_code == 200:
                result = response.json()
                return f"✅ {result.get('response', 'Success')[:60]}..."
            else:
                return f"❌ {response.status_code}"
        except Exception as e:
            return f"❌ {e}"

    def test_ai_status(self):
        """Check overall AI system status"""
        print("\n🌐 AI System Status:")
        try:
            response = requests.get(f"{BASE_URL}/ai/status")
            if response.status_code == 200:
                status = response.json()
                print(f"   ✅ {status}")
                return True
            else:
                print(f"   ❌ {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ {e}")
            return False

    def test_ai_ask(self):
        """Test general AI question"""
        print("\n🤔 Testing general AI question:")
        payload = {
            "message": "How many bots are available in the system and what are their roles?",
            "bot_type": "general"
        }

        try:
            response = requests.post(f"{BASE_URL}/ai/ask", json=payload)
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ {result.get('response', 'Success')[:80]}...")
                return True
            else:
                print(f"   ❌ {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ {e}")
            return False

    def run_comprehensive_test(self):
        """Run comprehensive bot test"""
        print("=" * 60)
        print("🚀 Comprehensive Test for 6 Core Bots")
        print("=" * 60)

        # Test overall AI status and response
        self.test_ai_status()
        self.test_ai_ask()

        # Retrieve bot list
        available_bots = self.get_bots_list()

        print(f"\n🤖 Testing all 6 bots:")
        print("-" * 50)

        results = []
        for bot_name in self.bots:
            print(f"\n🔧 {bot_name}:")

            # Test status
            status_result = self.test_bot_status(bot_name)
            print(f"   📊 Status: {status_result}")

            # Test run
            run_result = self.test_bot_run(bot_name)
            print(f"   🚀 Run: {run_result}")

            # Log result
            success = "✅" in status_result and "✅" in run_result
            results.append((bot_name, success))

        # Display summary
        print("\n" + "=" * 50)
        print("📊 Final Results:")
        successful_bots = [name for name, success in results if success]

        for bot_name, success in results:
            status = "✅" if success else "❌"
            print(f"   {status} {bot_name}")

        print(f"\n🎯 Result: {len(successful_bots)}/6 bots working successfully")

        if len(successful_bots) == 6:
            print("🎉🎉🎉 All 6 core bots are running perfectly! 🎉🎉🎉")
        else:
            print("⚠️  Some bots need inspection")

        return len(successful_bots) == 6


def main():
    tester = BotTester()
    success = tester.run_comprehensive_test()

    print("\n" + "=" * 60)
    print("💡 Usage Tips:")
    print("   • 🔐 Some routes require authentication (check /auth/token)")
    print("   • 📚 Use /docs for the interactive Swagger UI")
    print("   • 🔍 Use /_debug/routes to view all available endpoints")
    print("=" * 60)


if __name__ == "__main__":
    main()
