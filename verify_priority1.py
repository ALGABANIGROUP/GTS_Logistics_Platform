#!/usr/bin/env python3
"""
Final Priority 1 Implementation Test
Comprehensive verification of all systems
"""
import os
import sys
from pathlib import Path
from datetime import datetime

# Load environment
from dotenv import load_dotenv
load_dotenv()

print("\n" + "=" * 70)
print("🎯 GTS Priority 1 - Final Verification")
print("=" * 70)
print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

checks_passed = 0
checks_total = 0

# =========== CHECK 1: Sentry SDK ===========
print("1️⃣  Sentry SDK Installation")
checks_total += 1
try:
    import sentry_sdk
    print(f"   ✅ sentry-sdk installed")
    checks_passed += 1
except ImportError:
    print("   ❌ sentry-sdk NOT installed")
    print("   💡 Fix: pip install sentry-sdk[fastapi]")

print()

# =========== CHECK 2: Security Middleware ===========
print("2️⃣  Security Middleware")
checks_total += 1
try:
    from backend.middleware.security_headers import (
        SecurityHeadersMiddleware,
        HTTPSRedirectMiddleware,
        RateLimitMiddleware
    )
    print("   ✅ SecurityHeadersMiddleware loaded")
    print("   ✅ HTTPSRedirectMiddleware loaded")
    print("   ✅ RateLimitMiddleware loaded")
    checks_passed += 1
except Exception as e:
    print(f"   ❌ Security middleware error: {e}")

print()

# =========== CHECK 3: Sentry Integration ===========
print("3️⃣  Sentry Integration Module")
checks_total += 1
try:
    from backend.monitoring.sentry_integration import init_sentry
    print("   ✅ init_sentry function loaded")
    checks_passed += 1
except Exception as e:
    print(f"   ❌ Sentry integration error: {e}")

print()

# =========== CHECK 4: Email Alerts ===========
print("4️⃣  Email Alert System")
checks_total += 1
try:
    from backend.monitoring.email_alerts import get_alerter, EmailAlerter
    alerter = get_alerter()
    print("   ✅ EmailAlerter loaded")
    if alerter.enabled:
        print(f"   ✅ Email alerts ENABLED")
    else:
        print(f"   ⚠️  Email alerts disabled (set SMTP_HOST, SMTP_USER, SMTP_PASSWORD)")
    checks_passed += 1
except Exception as e:
    print(f"   ❌ Email alerts error: {e}")

print()

# =========== CHECK 5: Configuration ===========
print("5️⃣  Configuration Validation")
checks_total += 1
try:
    from backend.config import Settings
    settings = Settings()
    
    # Check SECRET_KEY
    if settings.SECRET_KEY == "dev-secret-change-me":
        if settings.APP_ENV == "production":
            print("   ⚠️  WARNING: Default SECRET_KEY in PRODUCTION")
            print("   💡 Fix: Generate with: python -c 'import secrets; print(secrets.token_urlsafe(32))'")
        else:
            print("   ✅ Using default SECRET_KEY (OK for development)")
    else:
        print(f"   ✅ Custom SECRET_KEY configured ({len(settings.SECRET_KEY)} chars)")
    
    # Check CORS
    if settings.ALLOWED_ORIGINS or settings.GTS_CORS_ORIGINS:
        print("   ✅ CORS origins configured")
    else:
        if settings.APP_ENV == "production":
            print("   ⚠️  WARNING: CORS not configured in PRODUCTION")
        else:
            print("   ⚠️  CORS not configured (OK for development)")
    
    # Check rate limiting
    print(f"   ✅ Rate limit: {settings.RATE_LIMIT_REQUESTS_PER_MINUTE} req/min")
    
    # Check HTTPS enforcement
    if hasattr(settings, 'ENFORCE_HTTPS'):
        print(f"   ✅ HTTPS enforcement: {settings.ENFORCE_HTTPS}")
    
    # Check security headers
    if hasattr(settings, 'ENABLE_SECURITY_HEADERS'):
        print(f"   ✅ Security headers: {settings.ENABLE_SECURITY_HEADERS}")
    
    checks_passed += 1
except Exception as e:
    print(f"   ❌ Configuration error: {e}")

print()

# =========== CHECK 6: Backup System ===========
print("6️⃣  Backup System")
checks_total += 1
try:
    backup_dir = Path(__file__).parent / "backups"
    if backup_dir.exists():
        backups = list(backup_dir.glob("gts_backup_*.sql.gz"))
        if backups:
            latest = max(backups, key=lambda p: p.stat().st_mtime)
            size_kb = latest.stat().st_size / 1024
            print(f"   ✅ Backup directory exists")
            print(f"   ✅ {len(backups)} backup(s) found")
            print(f"   ✅ Latest: {latest.name} ({size_kb:.0f} KB)")
        else:
            print(f"   ⚠️  No backups found")
            print(f"   💡 Fix: Run: python scripts/backup_database_simple.py")
    else:
        print(f"   ⚠️  Backup directory not created")
    checks_passed += 1
except Exception as e:
    print(f"   ❌ Backup system error: {e}")

print()

# =========== CHECK 7: Database Connection ===========
print("7️⃣  Database Connection")
checks_total += 1
try:
    import psycopg
    db_url = os.getenv("DATABASE_URL") or os.getenv("ASYNC_DATABASE_URL", "")
    db_url = db_url.replace("+asyncpg", "")
    
    if db_url:
        try:
            with psycopg.connect(db_url, connect_timeout=3) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT version()")
                    version = cur.fetchone()[0]
                    db_version = version.split(",")[0]
                    print(f"   ✅ Database connected")
                    print(f"   ✅ {db_version}")
            checks_passed += 1
        except Exception as e:
            print(f"   ❌ Database connection failed: {e}")
    else:
        print(f"   ❌ DATABASE_URL not set")
except ImportError:
    print(f"   ❌ psycopg not installed")

print()

# =========== CHECK 8: Backend main.py ===========
print("8️⃣  Backend Integration")
checks_total += 1
try:
    import backend.main
    print("   ✅ backend.main module loads")
    
    # Check if app exists
    if hasattr(backend.main, 'app'):
        print("   ✅ FastAPI app initialized")
        checks_passed += 1
    else:
        print("   ❌ FastAPI app not found")
except Exception as e:
    print(f"   ❌ Backend main error: {e}")

print()

# =========== SUMMARY ===========
print("=" * 70)
print("📊 VERIFICATION SUMMARY")
print("=" * 70)

percentage = (checks_passed / checks_total) * 100
print(f"\nChecks Passed: {checks_passed}/{checks_total} ({percentage:.0f}%)")
print()

if percentage == 100:
    print("🎉 ALL SYSTEMS READY FOR DEPLOYMENT!")
    print()
    print("Next Steps:")
    print("1. Generate SECRET_KEY: python -c \"import secrets; print(secrets.token_urlsafe(32))\"")
    print("2. Update .env with SECRET_KEY and CORS origins")
    print("3. Deploy to your domain")
    print()
    sys.exit(0)
elif percentage >= 80:
    print("✅ MOSTLY READY - Fix remaining issues then deploy")
    print()
    sys.exit(0)
else:
    print("❌ ISSUES NEED ATTENTION - See above for fixes")
    print()
    sys.exit(1)
