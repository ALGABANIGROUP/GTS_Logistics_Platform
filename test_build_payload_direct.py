"""Direct test of build_auth_me_payload"""
import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

os.environ.setdefault("ENABLE_OPENAPI", "0")
os.environ.setdefault("ENVIRONMENT", "development")


async def test_build_payload():
    from backend.database.config import init_engines, get_db_async
    from backend.security.access_context import build_auth_me_payload
    from fastapi import Request
    
    # Initialize DB
    init_engines()
    
    # Fake request
    class FakeRequest:
        def __init__(self):
            self.headers = {}
    
    request = FakeRequest()
    
    # Claims from token
    claims = {
        "sub": "344",
        "email": "enjoy983@hotmail.com",
        "role": "super_admin",
        "iat": 1771768189,
        "exp": 1803304189,
        "tv": 1
    }
    
    # Get DB session
    async for db in get_db_async():
        try:
            print("\n=== Testing build_auth_me_payload ===")
            print(f"Claims: {claims}")
            
            payload = await build_auth_me_payload(request, db, claims)
            
            print("\n✅ Success!")
            print(f"User: {payload['user']}")
            print(f"Role: {payload['user']['role']}")
            print(f"Permissions: {len(payload['user']['permissions'])} total")
            print(f"Features: {len(payload['entitlements']['features'])} total")
            print(f"Modules: {payload['entitlements']['modules']}")
            
        except Exception as e:
            print("\n❌ Error!")
            print(f"Exception: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
        finally:
            break


if __name__ == "__main__":
    asyncio.run(test_build_payload())
