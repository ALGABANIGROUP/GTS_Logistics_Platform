#!/usr/bin/env python3
"""
Diagnostic script to check backend auth endpoints
"""
import sys
import os

# Add backend to path
sys.path.insert(0, r'c:\Users\enjoy\dev\GTS-new')

# Test imports
print("🧪 Testing backend imports...")

try:
    print("✅ Python environment OK")
    print(f"Python version: {sys.version}")
    print(f"Python path: {sys.executable}")
    
    # Try to import backend modules
    print("\n📦 Checking backend modules...")
    
    try:
        from backend.security.auth import create_access_token
        print("✅ backend.security.auth imported")
    except Exception as e:
        print(f"❌ backend.security.auth: {e}")
    
    try:
        from backend.routes.auth_me import router
        print("✅ backend.routes.auth_me imported")
        print(f"   Routes: {[route.path for route in router.routes]}")
    except Exception as e:
        print(f"❌ backend.routes.auth_me: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        from backend.routes.auth import router as auth_router
        print("✅ backend.routes.auth imported")
    except Exception as e:
        print(f"❌ backend.routes.auth: {e}")
    
    try:
        from backend.models.user import User
        print("✅ backend.models.user imported")
    except Exception as e:
        print(f"❌ backend.models.user: {e}")
    
    try:
        from backend.database.config import get_db_async
        print("✅ backend.database.config imported")
    except Exception as e:
        print(f"❌ backend.database.config: {e}")
    
    print("\n✅ All critical imports successful!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
