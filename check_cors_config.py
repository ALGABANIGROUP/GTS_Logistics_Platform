#!/usr/bin/env python3
"""CORS Configuration Verification Script
Checks if CORS is properly configured with explicit Authorization header
"""

import re
import sys
from pathlib import Path


def check_cors_config():
    """Verify CORS configuration in backend/main.py"""
    print("🔍 Checking CORS Configuration...\n")

    backend_main = Path("backend/main.py")
    if not backend_main.exists():
        print("❌ backend/main.py not found!")
        return False

    content = backend_main.read_text(encoding="utf-8")
    results = {
        "has_cors_middleware": False,
        "has_explicit_headers": False,
        "has_authorization": False,
        "no_wildcard_headers": False,
        "has_allow_credentials": False,
        "has_expose_headers": False,
        "has_max_age": False,
    }

    if "app.add_middleware(" in content and "CORSMiddleware" in content:
        results["has_cors_middleware"] = True
        print("✅ CORSMiddleware is added to app")
    else:
        print("❌ CORSMiddleware not found or not added to app")

    headers_pattern = r"allow_headers\s*=\s*\[(.*?)\]"
    headers_match = re.search(headers_pattern, content, re.DOTALL)
    if headers_match:
        headers_content = headers_match.group(1)
        if '"*"' not in headers_content or len(headers_content.strip()) > 10:
            results["has_explicit_headers"] = True
            print("✅ Explicit allow_headers list defined (not wildcard)")
        else:
            print("❌ allow_headers still uses wildcard [\"*\"]")
        if '"Authorization"' in headers_content or "'Authorization'" in headers_content:
            results["has_authorization"] = True
            print("✅ 'Authorization' header explicitly listed")
        else:
            print("❌ 'Authorization' header NOT explicitly listed")
    else:
        print("⚠️  Could not find allow_headers configuration")

    middleware_pattern = r"add_middleware\(\s*CORSMiddleware.*?allow_headers\s*=\s*\[\"?\*\"?\]"
    if re.search(middleware_pattern, content, re.DOTALL):
        print("❌ WARNING: Wildcard [\"*\"] used in allow_headers")
    else:
        results["no_wildcard_headers"] = True
        print("✅ No wildcard in allow_headers")

    if "allow_credentials=True" in content or "allow_credentials = True" in content:
        results["has_allow_credentials"] = True
        print("✅ allow_credentials=True is set")
    else:
        print("❌ allow_credentials not set to True")

    if "expose_headers" in content:
        results["has_expose_headers"] = True
        print("✅ expose_headers is configured")
    else:
        print("⚠️  expose_headers not configured (optional)")

    if "max_age" in content:
        results["has_max_age"] = True
        print("✅ max_age is configured (caches preflight)")
    else:
        print("⚠️  max_age not configured (optional)")

    print("\n" + "=" * 60)
    print("SUMMARY:")
    print("=" * 60)

    critical_checks = [
        results["has_cors_middleware"],
        results["has_explicit_headers"],
        results["has_authorization"],
        results["no_wildcard_headers"],
        results["has_allow_credentials"],
    ]
    passed = sum(critical_checks)
    total = len(critical_checks)
    if passed == total:
        print(f"✅ All {total} critical checks PASSED")
        print("\n🎉 CORS configuration is correct!")
        print("\n📝 Next steps:")
        print("   1. Restart backend: python -m uvicorn backend.main:app --reload")
        print("   2. Test at: http://localhost:5173/test-connection.html")
        print("   3. Look for 'Access-Control-Allow-Origin' in test results")
        return True
    print(f"❌ {total - passed} critical check(s) FAILED")
    print("\n⚠️  CORS configuration needs fixes!")
    print("\n📝 Required fixes:")
    if not results["has_cors_middleware"]:
        print("   • Add CORSMiddleware to app")
    if not results["has_explicit_headers"]:
        print("   • Define explicit allow_headers list")
    if not results["has_authorization"]:
        print("   • Add 'Authorization' to allow_headers")
    if not results["no_wildcard_headers"]:
        print("   • Remove wildcard [\"*\"] from allow_headers")
    if not results["has_allow_credentials"]:
        print("   • Set allow_credentials=True")
    return False


def show_recommended_config():
    """Show the recommended CORS configuration"""
    print("\n" + "=" * 60)
    print("RECOMMENDED CORS CONFIGURATION:")
    print("=" * 60)
    print("""allow_credentials = True
# Explicit headers list for credentialed requests
allow_headers = [
    "Accept",
    "Accept-Language",
    "Content-Type",
    "Content-Language",
    "Authorization",  # ⚠️ CRITICAL for Bearer tokens
    "X-Requested-With",
    "X-CSRF-Token",
    "Cache-Control",
    "Pragma",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=allow_credentials,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=allow_headers,
    expose_headers=["*"],
    max_age=600,)
log.info(f"[CORS] ✅ Configured with origins: {allow_origins}")
log.info(f"[CORS] ✅ Explicit headers: {allow_headers}")""")


if __name__ == "__main__":
    print("🔧 GTS Logistics - CORS Configuration Checker")
    print("=" * 60 + "\n")
    success = check_cors_config()
    if not success:
        show_recommended_config()
        sys.exit(1)
    sys.exit(0)
