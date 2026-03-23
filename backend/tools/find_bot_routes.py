# backend/tools/find_bot_routes.py
import requests

BASE_URL = "http://127.0.0.1:8000"

def find_ai_routes():
    """Search for actual AI routes"""
    print("🔍 Searching for AI routes...")

    try:
        # Get all routes
        response = requests.get(f"{BASE_URL}/_debug/routes")
        if response.status_code == 200:
            routes = response.json()
            print("✅ Available routes:")

            ai_routes = []
            for route in routes:
                if '/ai/' in route['path']:
                    ai_routes.append(route)
                    print(f"   🌐 {route['path']} - {route['methods']}")

            if not ai_routes:
                print("   ❌ No AI routes found")

            return ai_routes
        else:
            print(f"❌ Unable to fetch routes: {response.status_code}")
            return []

    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def test_available_routes():
    """Test available routes"""
    print("\n🧪 Testing routes...")

    # Possible routes
    possible_routes = [
        "/ai/bots",
        "/ai/status",
        "/ai/ask",
        "/ai/finance-analysis",
        "/health/ping",
        "/finance/health"
    ]

    for route in possible_routes:
        try:
            response = requests.get(f"{BASE_URL}{route}")
            print(f"   {route}: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
        except:
            print(f"   {route}: ❌ Unavailable")

if __name__ == "__main__":
    print("=" * 50)
    print("🔎 Exploring system routes")
    print("=" * 50)

    find_ai_routes()
    test_available_routes()
