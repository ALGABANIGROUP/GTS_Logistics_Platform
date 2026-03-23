#!/usr/bin/env python3
"""
Render Environment Variables Sync Script
Adds environment variables to Render service via API
"""

import requests
import json
import sys
import os
from typing import Dict, List

# ============================================================================
# Configuration
# ============================================================================
RENDER_API_BASE = "https://api.render.com/v1"
SERVICE_ID = "srv-d6ckst94tr6s73c8elvg"  # GTS-Logistics-API

# Replace with your Render API key from: https://dashboard.render.com/account/api-keys
RENDER_API_KEY = "YOUR_RENDER_API_KEY_HERE"  # ⚠️ GET THIS FROM RENDER

# ============================================================================
# Environment Variables to Add
# ============================================================================
ENV_VARS: Dict[str, str] = {
    # Database
    "DATABASE_URL": "postgresql+asyncpg://gabani_transport_solutions_user:__SET_IN_SECRET_MANAGER__@dpg-cuicq2qj1k6c73asm5c0-a.oregon-postgres.render.com:5432/gabani_transport_solutions?sslmode=require",
    "SYNC_DATABASE_URL": "postgresql://gabani_transport_solutions_user:__SET_IN_SECRET_MANAGER__@dpg-cuicq2qj1k6c73asm5c0-a.oregon-postgres.render.com:5432/gabani_transport_solutions",
    
    # Security
    "SECRET_KEY": "__SET_IN_RENDER_SECRETS__",
    "JWT_SECRET_KEY": "__SET_IN_RENDER_SECRETS__",
    "JWT_ALGORITHM": "HS256",
    "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
    "REFRESH_TOKEN_EXPIRE_DAYS": "30",
    
    # Application
    "ENVIRONMENT": "production",
    "DEBUG": "false",
    "ENABLE_OPENAPI": "0",
    "GTS_LOG_LEVEL": "INFO",
    
    # Email
    "ADMIN_EMAIL": "admin@gabanilogistics.com",
    "SUPPORT_EMAIL": "support@gabanistore.com",
    "MAIL_FROM": "no-reply@gabanilogistics.com",
    
    "SMTP_HOST": "mail.gabanilogistics.com",
    "SMTP_PORT": "465",
    "SMTP_SECURE": "true",
    "SMTP_USER": "noreply@gabanilogistics.com",
    "SMTP_FROM": "no-reply@gabanilogistics.com",
    
    "IMAP_HOST": "mail.gabanilogistics.com",
    "IMAP_PORT": "993",
    "IMAP_SSL": "true",
    "IMAP_USER": "noreply@gabanilogistics.com",
    
    "POP3_HOST": "mail.gabanilogistics.com",
    "POP3_PORT": "995",
    "POP3_SSL": "true",
    "POP3_USER": "noreply@gabanilogistics.com",
    
    "EMAIL_MAILBOXES": "accounts@gabanilogistics.com,admin@gabanilogistics.com,customers@gabanilogistics.com,doccontrol@gabanilogistics.com,finance@gabanilogistics.com,freight@gabanilogistics.com,intel@gabanilogistics.com,investments@gabanilogistics.com,marketing@gabanilogistics.com,no-reply@gabanilogistics.com,operations@gabanilogistics.com,safety@gabanilogistics.com,sales@gabanilogistics.com,strategy@gabanilogistics.com,aidispatcher@gtsdispatcher.com,driver@gabanistore.com,security@gabanistore.com,support@gabanistore.com",
    
    # CORS
    "FRONTEND_URL": "https://api.gtsdispatcher.com",
    "ADMIN_URL": "https://api.gtsdispatcher.com",
    "ALLOWED_ORIGINS": "https://api.gtsdispatcher.com,https://gabanilogistics.com",
    
    # Health Check
    "HEALTHCHECK_DB_TIMEOUT_SECONDS": "10",
    "HEALTHCHECK_REDIS_TIMEOUT_SECONDS": "5",
    "HEALTHCHECK_EXTERNAL_TIMEOUT_SECONDS": "10",
    "HEALTHCHECK_INCLUDE_DETAILS": "false",
    
    # Registration
    "REGISTRATION_DISABLED": "false",
    "REGISTRATION_REOPEN_DATE": "2026-08-09",
    "REGISTRATION_CONTACT_EMAIL": "admin@gabanilogistics.com",
    "DEFAULT_SIGNUP_TENANT_ID": "01014c0f-cc06-44e4-a27a-8275adf901d6",
}

SENSITIVE_VARS = {
    # ⚠️ These must be set manually in Render dashboard (for security)
    "SMTP_PASSWORD": "YOUR_SMTP_PASSWORD_HERE",
    "IMAP_PASSWORD": "YOUR_IMAP_PASSWORD_HERE",
    "POP3_PASSWORD": "YOUR_POP3_PASSWORD_HERE",
}

# ============================================================================
# Functions
# ============================================================================

def get_headers() -> Dict[str, str]:
    """Get API headers with authorization"""
    return {
        "Authorization": f"Bearer {RENDER_API_KEY}",
        "Content-Type": "application/json",
    }

def get_sensitive_var(key: str) -> str:
    """Get sensitive variable from environment or fallback"""
    env_value = os.getenv(key)
    if env_value and env_value != "YOUR_RENDER_API_KEY_HERE":
        return env_value
    return SENSITIVE_VARS.get(key, "")

def add_env_var(key: str, value: str) -> bool:
    """Add a single environment variable via Render API"""
    url = f"{RENDER_API_BASE}/services/{SERVICE_ID}/env-vars"
    
    payload = {
        "key": key,
        "value": value,
        "scope": "build"  # Scope: build, deploy, or both
    }
    
    try:
        response = requests.post(url, json=payload, headers=get_headers(), timeout=10)
        
        if response.status_code == 201:
            print(f"✅ Added: {key}")
            return True
        elif response.status_code == 409:
            print(f"⚠️ Already exists: {key} (update manually if needed)")
            return True
        else:
            print(f"❌ Failed {key}: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.Timeout:
        print(f"❌ Timeout adding {key}: Request took too long")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error adding {key}: {e}")
        return False
    except Exception as e:
        print(f"❌ Error adding {key}: {e}")
        return False

def sync_env_vars() -> None:
    """Sync all environment variables"""
    if not RENDER_API_KEY or RENDER_API_KEY == "YOUR_RENDER_API_KEY_HERE":
        print("❌ ERROR: Set RENDER_API_KEY first!")
        print("   Get your API key from: https://dashboard.render.com/account/api-keys")
        sys.exit(1)
    
    print("🚀 Starting Render Environment Variables Sync...\n")
    
    added = 0
    failed = 0
    
    # Add non-sensitive vars
    for key, value in ENV_VARS.items():
        if add_env_var(key, value):
            added += 1
        else:
            failed += 1
    
    # Sensitive vars - try to get from environment first
    print(f"\n⚠️ SENSITIVE VARIABLES:")
    for key in SENSITIVE_VARS:
        env_value = get_sensitive_var(key)
        if env_value and env_value != SENSITIVE_VARS.get(key):
            success = add_env_var(key, env_value)
            if success:
                added += 1
        else:
            print(f"   - {key} (set manually in Render Dashboard or via environment variable)")
    
    print(f"\n📊 Summary:")
    print(f"   ✅ Added: {added}")
    print(f"   ❌ Failed: {failed}")
    
    if failed == 0:
        print("\n✨ All environment variables synced successfully!")
    else:
        print(f"\n⚠️ {failed} variables failed. Check your API key and service ID.")

# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════════╗
║    Render Environment Variables Synchronization Tool              ║
║    GTS Logistics Platform                                          ║
╚════════════════════════════════════════════════════════════════════╝
    """)
    
    print("\n📋 Prerequisites:")
    print("   1. Get your Render API key from:")
    print("      https://dashboard.render.com/account/api-keys")
    print("   2. Set RENDER_API_KEY in this script")
    print("   3. Verify SERVICE_ID matches your service")
    
    print(f"\n🔧 Current Configuration:")
    print(f"   Service ID: {SERVICE_ID}")
    print(f"   API Key Set: {'✅' if RENDER_API_KEY != 'YOUR_RENDER_API_KEY_HERE' else '❌'}")
    print(f"   Variables: {len(ENV_VARS)} auto + {len(SENSITIVE_VARS)} manual")
    
    input("\nPress Enter to continue or Ctrl+C to cancel...")
    
    sync_env_vars()
