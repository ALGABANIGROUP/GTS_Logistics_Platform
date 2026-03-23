# backend/tools/use_working_bots.py
import requests

BASE_URL = "http://127.0.0.1:8000"

def demonstrate_working_system():
    """Show capabilities of the working system"""
    print("🚀 Demonstrating the working system capabilities")
    print("=" * 50)

    # Get authentication token
    auth_data = {"username": "admin", "password": "admin"}
    token_resp = requests.post(f"{BASE_URL}/auth/token", data=auth_data)
    token = token_resp.json().get('access_token')
    headers = {"Authorization": f"Bearer {token}"}

    # Active bots
    working_bots = [
        {
            "id": "general_manager",
            "name": "General Manager",
            "scenarios": [
                "Strategic planning for the next quarter",
                "Team performance analysis",
                "Productivity improvement suggestions"
            ]
        },
        {
            "id": "freight_broker",
            "name": "Freight Broker",
            "scenarios": [
                "Manage an international shipment",
                "Track shipment status",
                "Negotiate freight rates"
            ]
        },
        {
            "id": "documents_manager",
            "name": "Documents Manager",
            "scenarios": [
                "Organize shipment documents",
                "Review contracts",
                "Manage documentation"
            ]
        },
        {
            "id": "maintenance_dev",
            "name": "Maintenance Assistant",
            "scenarios": [
                "System health check",
                "Monitor database performance",
                "System updates"
            ]
        }
    ]

    for bot in working_bots:
        print(f"\n🤖 {bot['name']}:")
        print(f"   📋 Available scenarios: {', '.join(bot['scenarios'])}")

        # Test one scenario
        test_message = bot['scenarios'][0]
        payload = {"message": test_message, "context": {"demo": True}}

        try:
            response = requests.post(
                f"{BASE_URL}/ai/{bot['id']}/run",
                json=payload,
                headers=headers
            )

            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Test success: {result.get('response', 'Success')[:60]}...")
            else:
                print(f"   ❌ Error: {response.status_code}")

        except Exception as e:
            print(f"   💥 Exception: {e}")

    print("\n" + "=" * 50)
    print("🎉 The system is ready to use!")
    print("🌐 Interface: http://127.0.0.1:8000/docs")
    print("🔐 Use credentials: admin / admin")

if __name__ == "__main__":
    demonstrate_working_system()
