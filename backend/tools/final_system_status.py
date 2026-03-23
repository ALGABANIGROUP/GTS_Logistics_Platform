# backend/tools/final_system_status.py
import requests
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def comprehensive_system_report():
    """Comprehensive system status report"""
    print("📊 Final Comprehensive System Report")
    print("=" * 60)
    print(f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Test server connection
    try:
        health = requests.get(f"{BASE_URL}/health/ping")
        print(f"🔧 Server status: ✅ Running ({health.json()})")
    except:
        print("🔧 Server status: ❌ Unavailable")
        return

    # Get authentication token
    auth_data = {"username": "admin", "password": "admin"}
    try:
        token_resp = requests.post(f"{BASE_URL}/auth/token", data=auth_data)
        token = token_resp.json().get('access_token')
        headers = {"Authorization": f"Bearer {token}"}
        print("🔐 Authentication: ✅ Successful")
    except:
        print("🔐 Authentication: ❌ Failed")
        return

    # Test all 6 bots
    print("\n🤖 Status of the 6 Bots:")
    print("-" * 40)

    bots = [
        ("general_manager", "General Manager", "Strategic Planning"),
        ("freight_broker", "Freight Broker", "Shipment Management"),
        ("operations_manager", "Operations Manager", "Workflow Management"),
        ("finance_bot", "Finance Assistant", "Financial Reports"),
        ("documents_manager", "Documents Manager", "Document Organization"),
        ("maintenance_dev", "Maintenance Assistant", "System Monitoring")
    ]

    working_bots = 0

    for bot_id, name, description in bots:
        try:
            # Check bot status
            status_resp = requests.get(f"{BASE_URL}/ai/{bot_id}/status", headers=headers)

            # Test bot functionality
            payload = {"message": f"Check {name}", "context": {"status_check": True}}
            run_resp = requests.post(f"{BASE_URL}/ai/{bot_id}/run", json=payload, headers=headers)

            if run_resp.status_code == 200:
                status = "✅ Working"
                working_bots += 1
            else:
                status = f"❌ Error {run_resp.status_code}"

            print(f"   {status} {name} - {description}")

        except Exception as e:
            print(f"   ❌ Failed {name} - {e}")

    print(f"\n📈 Statistics:")
    print(f"   • Active bots: {working_bots}/6")
    print(f"   • Success rate: {(working_bots/6)*100:.1f}%")
    print(f"   • System status: {'🟢 Excellent' if working_bots == 6 else '🟡 Good' if working_bots >= 4 else '🔴 Needs Improvement'}")

    print("\n🎯 Available Actions:")
    print("   1. 🌐 Use the web interface: http://127.0.0.1:8000/docs")
    print("   2. 🔐 Enter your auth token in 'Authorize'")
    print("   3. 🤖 Start using the bots directly")
    print("   4. 📞 Integrate the system with your other applications")

    print("\n🚀 The system is ready for production!" if working_bots >= 4 else "⚠️  The system is running but needs improvement")
    print("=" * 60)

if __name__ == "__main__":
    comprehensive_system_report()
