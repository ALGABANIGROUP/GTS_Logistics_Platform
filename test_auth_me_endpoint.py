"""Test /api/v1/auth/me endpoint"""
import asyncio
import httpx

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzNDQiLCJlbWFpbCI6ImVuam95OTgzQGhvdG1haWwuY29tIiwicm9sZSI6InN1cGVyX2FkbWluIiwiaWF0IjoxNzcxNzY4MTg5LCJleHAiOjE4MDMzMDQxODksInR2IjoxfQ.rHU80SIUpE-RoiOUW6I_IFLCH8KvO61_LEpkqZw5R8A"


async def main():
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {TOKEN}"}
        
        # Test /quick first
        try:
            resp = await client.get("http://127.0.0.1:8000/api/v1/auth/me/quick", headers=headers, timeout=5.0)
            print("\n=== /api/v1/auth/me/quick ===")
            print(f"Status: {resp.status_code}")
            print(f"Response: {resp.text}")
        except Exception as e:
            print(f"\n=== /api/v1/auth/me/quick ===")
            print(f"Error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
        
        # Test /me
        try:
            resp = await client.get("http://127.0.0.1:8000/api/v1/auth/me", headers=headers, timeout=5.0)
            print("\n=== /api/v1/auth/me ===")
            print(f"Status: {resp.status_code}")
            print(f"Response: {resp.text[:500] if len(resp.text) > 500 else resp.text}")
        except Exception as e:
            print(f"\n=== /api/v1/auth/me ===")
            print(f"Error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
