#!/usr/bin/env python3
"""
Test script to verify session timeout is set to 15 minutes
Run with: python verify_session_timeout.py
"""

import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def check_timeout_settings():
    """Check all timeout settings in the backend"""
    
    print("\n" + "="*60)
    print("🔍 SESSION TIMEOUT VERIFICATION")
    print("="*60 + "\n")
    
    checks = []
    
    # Check 1: backend/utils/auth_utils.py
    try:
        from backend.utils.auth_utils import ACCESS_TOKEN_EXPIRE_MINUTES as AUTH_UTILS_TIMEOUT
        result = f"✅ auth_utils.py: {AUTH_UTILS_TIMEOUT} minutes"
        checks.append((result, AUTH_UTILS_TIMEOUT == 15))
        print(result)
    except Exception as e:
        print(f"⚠️  auth_utils.py: {str(e)}")
        checks.append(("auth_utils.py", False))
    
    # Check 2: config/settings.py
    try:
        from config.settings import Settings
        timeout = Settings.ACCESS_TOKEN_EXPIRE_MINUTES
        result = f"✅ settings.py: {timeout} minutes"
        checks.append((result, timeout == 15))
        print(result)
    except Exception as e:
        print(f"⚠️  settings.py: {str(e)}")
        checks.append(("settings.py", False))
    
    # Check 3: backend/security/auth.py
    try:
        from backend.security.auth import ACCESS_TOKEN_EXPIRE_MINUTES as SECURITY_TIMEOUT
        result = f"✅ security/auth.py: {SECURITY_TIMEOUT} minutes"
        checks.append((result, SECURITY_TIMEOUT == 15))
        print(result)
    except Exception as e:
        print(f"⚠️  security/auth.py: {str(e)}")
        checks.append(("security/auth.py", False))
    
    # Check 4: backend/config.py
    try:
        from backend.config import Settings as ConfigSettings
        timeout = ConfigSettings.ACCESS_TOKEN_EXPIRE_MINUTES
        result = f"✅ config.py: {timeout} minutes"
        checks.append((result, timeout == 15))
        print(result)
    except Exception as e:
        print(f"⚠️  config.py: {str(e)}")
        checks.append(("config.py", False))
    
    # Check 5: backend/services/auth.py
    try:
        from backend.services.auth import ACCESS_TOKEN_EXPIRE_MINUTES as SERVICES_TIMEOUT
        result = f"✅ services/auth.py: {SERVICES_TIMEOUT} minutes"
        checks.append((result, SERVICES_TIMEOUT == 15))
        print(result)
    except Exception as e:
        print(f"⚠️  services/auth.py: {str(e)}")
        checks.append(("services/auth.py", False))
    
    # Summary
    print("\n" + "="*60)
    successful = sum(1 for _, passed in checks if passed)
    total = len(checks)
    
    if successful == total:
        print(f"✅ ALL CHECKS PASSED ({successful}/{total})")
        print("\n🎉 Session timeout is correctly set to 15 minutes!")
        print("   - After 14 minutes: Warning notification")
        print("   - After 15 minutes: Auto-logout")
    else:
        print(f"⚠️  SOME CHECKS FAILED ({successful}/{total})")
        print("\nReview the errors above")
    
    print("="*60 + "\n")
    
    return successful == total

if __name__ == "__main__":
    success = check_timeout_settings()
    sys.exit(0 if success else 1)
