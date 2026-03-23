# backend/tools/quick_start_guide.py
import requests

BASE_URL = "http://127.0.0.1:8000"

def quick_start_examples():
    """Quick start examples to get started immediately"""
    print("🚀 Quick Start Guide")
    print("=" * 50)

    # Get authentication token
    auth_data = {"username": "admin", "password": "admin"}
    token_resp = requests.post(f"{BASE_URL}/auth/token", data=auth_data)
    token = token_resp.json().get('access_token')
    headers = {"Authorization": f"Bearer {token}"}

    print("🔐 Authentication token retrieved")
    print("🤖 Ready-to-use bots:")

    # Instant examples
    examples = [
        {
            "bot": "general_manager",
            "question": "What are the company’s priorities this month?",
            "use_case": "Monthly Planning"
        },
        {
            "bot": "freight_broker",
            "question": "What’s the best way to manage an urgent shipment?",
            "use_case": "Express Shipping"
        },
        {
            "bot": "documents_manager",
            "question": "What are the essential documents required for export?",
            "use_case": "Documentation"
        },
        {
            "bot": "maintenance_dev",
            "question": "How can I monitor system performance?",
            "use_case": "Monitoring"
        }
    ]

    for example in examples:
        print(f"\n📍 {example['use_case']}:")
        print(f"   Question: {example['question']}")

        payload = {
            "message": example["question"],
            "context": {"quick_start": True}
        }

        response = requests.post(
            f"{BASE_URL}/ai/{example['bot']}/run",
            json=payload,
            headers=headers
        )

        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Response: {result.get('response', 'Processed successfully')}")
        else:
            print(f"   ❌ Error: {response.status_code}")

def show_api_endpoints():
    """Display available API endpoints"""
    print("\n🌐 Available API Endpoints:")
    print("-" * 30)

    endpoints = [
        "POST /ai/general_manager/run - General Manager",
        "POST /ai/freight_broker/run - Freight Broker",
        "POST /ai/documents_manager/run - Documents Manager",
        "POST /ai/maintenance_dev/run - Maintenance Assistant",
        "GET /ai/{bot_name}/status - Bot status",
        "GET /health/ping - System health check"
    ]

    for endpoint in endpoints:
        print(f"   🔗 {endpoint}")

if __name__ == "__main__":
    quick_start_examples()
    show_api_endpoints()
    print("\n🎯 You’re all set! Start using the system:")
    print("   1. Open http://127.0.0.1:8000/docs")
    print("   2. Use the Authorize button (top right)")
    print("   3. Enter: Bearer YOUR_TOKEN_HERE")
    print("   4. Start experimenting with the bots!")
