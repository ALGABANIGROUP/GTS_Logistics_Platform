#!/usr/bin/env python3
"""
Quick test script for Priority 1 implementations
Tests backup, security, and monitoring systems
"""
import os
import sys
from pathlib import Path
import subprocess

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("🧪 GTS Priority 1 Systems Test")
print("=" * 70)
print()

# Test 1: Backup System
print("1️⃣ Testing Backup System...")
try:
    from scripts.backup_database import BACKUP_DIR
    
    # Check if backup directory exists
    if BACKUP_DIR.exists():
        print("   ✅ Backup directory exists")
        
        # Check for existing backups
        backups = list(BACKUP_DIR.glob("gts_backup_*.sql.gz"))
        if backups:
            print(f"   ✅ Found {len(backups)} existing backup(s)")
        else:
            print("   ⚠️  No backups found - run: python scripts/backup_database.py")
    else:
        print("   ⚠️  Backup directory not created yet")
    
    print("   ✅ Backup module imports successfully")
except Exception as e:
    print(f"   ❌ Backup system error: {e}")

print()

# Test 2: Security Configuration
print("2️⃣ Testing Security Configuration...")
try:
    from backend.config import Settings
    
    settings = Settings()
    
    # Check SECRET_KEY
    if settings.SECRET_KEY == "dev-secret-change-me":
        if settings.APP_ENV == "production":
            print("   ❌ DEFAULT SECRET_KEY in production - APPLICATION WILL CRASH!")
        else:
            print("   ⚠️  Using default SECRET_KEY (OK for development)")
    else:
        print(f"   ✅ Custom SECRET_KEY configured ({len(settings.SECRET_KEY)} chars)")
    
    # Check CORS
    if settings.ALLOWED_ORIGINS or settings.GTS_CORS_ORIGINS:
        print("   ✅ CORS origins configured")
    else:
        if settings.APP_ENV == "production":
            print("   ❌ CORS not configured - required in production")
        else:
            print("   ⚠️  CORS not configured (OK for development)")
    
    # Check rate limiting
    print(f"   ✅ Rate limit: {settings.RATE_LIMIT_REQUESTS_PER_MINUTE} req/min")
    
    # Check security features
    if hasattr(settings, 'ENFORCE_HTTPS'):
        print(f"   ✅ HTTPS enforcement: {settings.ENFORCE_HTTPS}")
    
    if hasattr(settings, 'ENABLE_SECURITY_HEADERS'):
        print(f"   ✅ Security headers: {settings.ENABLE_SECURITY_HEADERS}")
    
except Exception as e:
    print(f"   ❌ Security configuration error: {e}")

print()

# Test 3: Security Middleware
print("3️⃣ Testing Security Middleware...")
try:
    from backend.middleware.security_headers import (
        SecurityHeadersMiddleware,
        HTTPSRedirectMiddleware,
        RateLimitMiddleware
    )
    
    print("   ✅ SecurityHeadersMiddleware loaded")
    print("   ✅ HTTPSRedirectMiddleware loaded")
    print("   ✅ RateLimitMiddleware loaded")
    
except Exception as e:
    print(f"   ❌ Middleware import error: {e}")

print()

# Test 4: Monitoring - Sentry
print("4️⃣ Testing Sentry Integration...")
try:
    from backend.monitoring.sentry_integration import init_sentry
    from backend.config import Settings
    
    settings = Settings()
    
    if hasattr(settings, 'SENTRY_DSN') and settings.SENTRY_DSN:
        print(f"   ✅ Sentry DSN configured")
        print(f"   ✅ Environment: {settings.SENTRY_ENVIRONMENT if hasattr(settings, 'SENTRY_ENVIRONMENT') else 'not set'}")
        
        if hasattr(settings, 'ENABLE_SENTRY') and settings.ENABLE_SENTRY:
            print("   ✅ Sentry enabled")
        else:
            print("   ⚠️  Sentry disabled (set ENABLE_SENTRY=true)")
    else:
        print("   ⚠️  Sentry DSN not configured")
        print("   💡 Get DSN from: https://sentry.io/")
    
    print("   ✅ Sentry integration module loaded")
    
except Exception as e:
    print(f"   ❌ Sentry integration error: {e}")

print()

# Test 5: Email Alerts
print("5️⃣ Testing Email Alerts...")
try:
    from backend.monitoring.email_alerts import get_alerter, EmailAlerter
    
    alerter = get_alerter()
    
    if alerter.enabled:
        print(f"   ✅ Email alerts configured")
        print(f"   ✅ SMTP Host: {alerter.smtp_host}")
        print(f"   ✅ Admin emails: {len(alerter.admin_emails)} recipient(s)")
    else:
        print("   ⚠️  Email alerts not fully configured")
        print("   💡 Set: SMTP_HOST, SMTP_USER, SMTP_PASSWORD, ADMIN_EMAIL")
    
    print("   ✅ Email alerter module loaded")
    
except Exception as e:
    print(f"   ❌ Email alerts error: {e}")

print()

# Test 6: Check Dependencies
print("6️⃣ Checking Python Dependencies...")
dependencies = [
    ("psutil", "System monitoring"),
    ("sentry-sdk", "Error tracking (install: pip install sentry-sdk[fastapi])"),
]

for package, description in dependencies:
    try:
        __import__(package.replace("-", "_"))
        print(f"   ✅ {package} - {description}")
    except ImportError:
        print(f"   ❌ {package} - NOT INSTALLED - {description}")

print()

# Summary
print("=" * 70)
print("📊 Test Summary")
print("=" * 70)
print()
print("✅ = Working correctly")
print("⚠️  = Needs configuration (optional for development)")
print("❌ = Critical issue (must fix for production)")
print()

# Recommendations
print("💡 Next Steps:")
print()
print("1. For Development:")
print("   - Current configuration is OK")
print("   - Run first backup: python scripts/backup_database.py")
print("   - Configure email alerts (optional)")
print()
print("2. For Production:")
print("   - Generate strong SECRET_KEY (32+ characters)")
print("   - Configure CORS origins")
print("   - Setup Sentry account and add DSN")
print("   - Configure email SMTP settings")
print("   - Setup automated backups (bash scripts/backup_cron_setup.sh)")
print("   - Run security scan: https://securityheaders.com/")
print()
print("3. Install Missing Dependencies:")
print("   pip install sentry-sdk[fastapi]")
print()
print("=" * 70)
print()
print("📚 Documentation:")
print("   - Backup: BACKUP_RESTORE_GUIDE.md")
print("   - Security: SECURITY_HARDENING_GUIDE.md")
print("   - Monitoring: MONITORING_ALERTS_GUIDE.md")
print("   - Summary: PRIORITY_1_IMPLEMENTATION_SUMMARY.md")
print()
print("=" * 70)
