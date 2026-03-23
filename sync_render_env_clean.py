#!/usr/bin/env python3
"""
Render Environment Variables Sync Script - Clean Version
Adds only essential environment variables to Render service
"""

import requests
import json
import sys
import os

# Configuration
RENDER_API_KEY = os.getenv("RENDER_API_KEY", "YOUR_RENDER_API_KEY_HERE")
SERVICE_ID = "srv-d6ckst94tr6s73c8elvg"
RENDER_API_URL = "https://api.render.com/v1"

# Essential Environment Variables Only
ENVIRONMENT_VARIABLES = {
    # ============================================================
    # DATABASE (Essential)
    # ============================================================
    "DATABASE_URL": {
        "value": "postgresql+asyncpg://gabani_transport_solutions_user:__SET_IN_SECRET_MANAGER__@dpg-cuicq2qj1k6c73asm5c0-a.oregon-postgres.render.com:5432/gabani_transport_solutions?sslmode=require",
        "description": "AsyncPG connection string for async database operations"
    },
    "SYNC_DATABASE_URL": {
        "value": "postgresql+psycopg://gabani_transport_solutions_user:__SET_IN_SECRET_MANAGER__@dpg-cuicq2qj1k6c73asm5c0-a.oregon-postgres.render.com:5432/gabani_transport_solutions?sslmode=require",
        "description": "Sync connection string for Alembic migrations"
    },

    # ============================================================
    # SECURITY - JWT (Critical!)
    # ============================================================
    "SECRET_KEY": {
        "value": "__SET_IN_RENDER_SECRETS__",
        "description": "General application secret key (64+ chars recommended)"
    },
    "JWT_SECRET_KEY": {
        "value": "__SET_IN_RENDER_SECRETS__",
        "description": "JWT token signing/verification secret (HS256)"
    },
    "JWT_ALGORITHM": {
        "value": "HS256",
        "description": "JWT algorithm (must be HS256)"
    },
    "ACCESS_TOKEN_EXPIRE_MINUTES": {
        "value": "30",
        "description": "JWT access token expiration (minutes)"
    },
    "REFRESH_TOKEN_EXPIRE_DAYS": {
        "value": "30",
        "description": "JWT refresh token expiration (days)"
    },

    # ============================================================
    # APPLICATION SETTINGS
    # ============================================================
    "ENVIRONMENT": {
        "value": "production",
        "description": "Deployment environment"
    },
    "DEBUG": {
        "value": "false",
        "description": "Debug mode (false in production)"
    },
    "ENABLE_OPENAPI": {
        "value": "false",
        "description": "Enable OpenAPI/Swagger (disable in production)"
    },
    "GTS_LOG_LEVEL": {
        "value": "INFO",
        "description": "Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    },

    # ============================================================
    # EMAIL - SMTP
    # ============================================================
    "SMTP_HOST": {
        "value": "mail.gabanilogistics.com",
        "description": "SMTP server hostname"
    },
    "SMTP_PORT": {
        "value": "465",
        "description": "SMTP port (465 for SSL)"
    },
    "SMTP_USER": {
        "value": "noreply@gabanilogistics.com",
        "description": "SMTP authentication user"
    },
    "SMTP_FROM": {
        "value": "noreply@gabanilogistics.com",
        "description": "Default From email address"
    },
    "SMTP_PASSWORD": {
        "value": "__SET_IN_RENDER_SECRETS__",
        "description": "SMTP password - SET MANUALLY in Render Dashboard (Secrets)"
    },

    # ============================================================
    # EMAIL - IMAP
    # ============================================================
    "IMAP_HOST": {
        "value": "mail.gabanilogistics.com",
        "description": "IMAP server hostname"
    },
    "IMAP_PORT": {
        "value": "993",
        "description": "IMAP port (993 for SSL)"
    },
    "IMAP_USER": {
        "value": "monitoring@gabanilogistics.com",
        "description": "IMAP authentication user"
    },
    "IMAP_PASSWORD": {
        "value": "__SET_IN_RENDER_SECRETS__",
        "description": "IMAP password - SET MANUALLY in Render Dashboard (Secrets)"
    },

    # ============================================================
    # EMAIL - POP3
    # ============================================================
    "POP3_HOST": {
        "value": "mail.gabanilogistics.com",
        "description": "POP3 server hostname"
    },
    "POP3_PORT": {
        "value": "995",
        "description": "POP3 port (995 for SSL)"
    },
    "POP3_USER": {
        "value": "monitoring@gabanilogistics.com",
        "description": "POP3 authentication user"
    },
    "POP3_PASSWORD": {
        "value": "__SET_IN_RENDER_SECRETS__",
        "description": "POP3 password - SET MANUALLY in Render Dashboard (Secrets)"
    },

    # ============================================================
    # EMAIL MAILBOXES (18 AI Bots - Updated)
    # ============================================================
    "EMAIL_ACCOUNTS_OPERATIONS": {
        "value": "operations@gabanilogistics.com",
        "description": "AI Operations Manager"
    },
    "EMAIL_ACCOUNTS_FREIGHT": {
        "value": "freight@gabanilogistics.com",
        "description": "AI Freight Broker + MapleLoad Canada Bot"
    },
    "EMAIL_ACCOUNTS_DISPATCHER": {
        "value": "aidispatcher@gtsdispatcher.com",
        "description": "AI Dispatcher"
    },
    "EMAIL_ACCOUNTS_INTEL": {
        "value": "intel@gabanilogistics.com",
        "description": "AI Information Coordinator"
    },
    "EMAIL_ACCOUNTS_STRATEGY": {
        "value": "strategy@gabanilogistics.com",
        "description": "Executive Intelligence"
    },
    "EMAIL_ACCOUNTS_DOCUMENTS": {
        "value": "doccontrol@gabanilogistics.com",
        "description": "AI Documents Manager"
    },
    "EMAIL_ACCOUNTS_CUSTOMERS": {
        "value": "customers@gabanilogistics.com",
        "description": "AI Customer Service"
    },
    "EMAIL_ACCOUNTS_SAFETY": {
        "value": "safety@gabanilogistics.com",
        "description": "AI Safety Manager"
    },
    "EMAIL_ACCOUNTS_SALES": {
        "value": "sales@gabanilogistics.com",
        "description": "AI Sales Bot"
    },
    "EMAIL_ACCOUNTS_ADMIN": {
        "value": "admin@gabanilogistics.com",
        "description": "AI System Admin"
    },
    "EMAIL_ACCOUNTS_FINANCE": {
        "value": "finance@gabanilogistics.com",
        "description": "AI Finance Bot"
    },
    "EMAIL_ACCOUNTS_ACCOUNTS": {
        "value": "accounts@gabanilogistics.com",
        "description": "AI Finance Bot - Expenses"
    },
    "EMAIL_ACCOUNTS_MARKETING": {
        "value": "marketing@gabanilogistics.com",
        "description": "AI Marketing Manager"
    },
    "EMAIL_ACCOUNTS_INVESTMENTS": {
        "value": "investments@gabanilogistics.com",
        "description": "AI Partner Manager"
    },
    "EMAIL_ACCOUNTS_SECURITY": {
        "value": "security@gabanistore.com",
        "description": "AI Security Manager"
    },
    "EMAIL_ACCOUNTS_NOREPLY": {
        "value": "noreply@gabanilogistics.com",
        "description": "System No-Reply email"
    },
    "EMAIL_ACCOUNTS_ALERTS": {
        "value": "alerts@gabanilogistics.com",
        "description": "System Alerts"
    },
    "EMAIL_ACCOUNTS_INFO": {
        "value": "info@gabanilogistics.com",
        "description": "General Info email"
    },

    # ============================================================
    # CORS & Frontend
    # ============================================================
    "GTS_CORS_ORIGINS": {
        "value": "*",
        "description": "CORS allowed origins"
    },
    "FRONTEND_URL": {
        "value": "https://app.gtsdispatcher.com",
        "description": "Frontend application URL"
    },

    # ============================================================
    # OPTIONAL: AI & Integrations (set if needed)
    # ============================================================
    "OPENAI_API_KEY": {
        "value": os.getenv("OPENAI_API_KEY", ""),
        "description": "OpenAI API key for AI features (optional)"
    },
    "STRIPE_PUBLISHABLE_KEY": {
        "value": os.getenv("STRIPE_PUBLISHABLE_KEY", ""),
        "description": "Stripe publishable key (optional)"
    },
    "STRIPE_SECRET_KEY": {
        "value": os.getenv("STRIPE_SECRET_KEY", ""),
        "description": "Stripe secret key (optional)"
    },
    "REDIS_URL": {
        "value": "redis://red-d5q5b9f5r7bs738cim10:6379",
        "description": "Redis connection URL (optional)"
    },
    "PIESOCKET_API_KEY": {
        "value": os.getenv("PIESOCKET_API_KEY", ""),
        "description": "PieSocket API key for real-time updates (optional)"
    },
    "PIESOCKET_CLUSTER_ID": {
        "value": "s1",
        "description": "PieSocket cluster ID (optional)"
    },
    "BILLING_ENABLED": {
        "value": "false",
        "description": "Enable billing features"
    },
}

# Manual Password Variables (set separately in Render Dashboard)
MANUAL_SECRETS = [
    ("SECRET_KEY", "application secret key"),
    ("JWT_SECRET_KEY", "JWT signing secret"),
    ("SMTP_PASSWORD", "SMTP server password"),
    ("IMAP_PASSWORD", "IMAP server password"),
    ("POP3_PASSWORD", "POP3 server password"),
    ("STRIPE_SECRET_KEY", "Stripe secret key"),
]

def set_environment_variable(key, value):
    """Set a single environment variable in Render"""
    headers = {
        "Authorization": f"Bearer {RENDER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "key": key,
        "value": value
    }
    
    url = f"{RENDER_API_URL}/services/{SERVICE_ID}/env-vars"
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 201:
            return True, "✅ Added"
        elif response.status_code == 409:
            return True, "⚠️  Already exists"
        else:
            return False, f"❌ Error: {response.status_code} - {response.text}"
    except Exception as e:
        return False, f"❌ Exception: {str(e)}"

def main():
    print("=" * 70)
    print("Render Environment Variables Sync - Clean Version")
    print("=" * 70)
    print()
    
    # Validate API key
    if RENDER_API_KEY == "YOUR_RENDER_API_KEY_HERE":
        print("❌ ERROR: Replace RENDER_API_KEY with your actual key!")
        print("   Get it from: https://dashboard.render.com/account/api-keys")
        sys.exit(1)
    
    print(f"🔧 Service ID: {SERVICE_ID}")
    print(f"📝 Total variables to add: {len(ENVIRONMENT_VARIABLES)}")
    print()
    
    added = 0
    failed = 0
    skipped = 0
    
    # Set each environment variable
    for key, config in ENVIRONMENT_VARIABLES.items():
        value = config["value"]
        description = config["description"]
        
        # Skip manual secrets
        if value == "__SET_IN_RENDER_SECRETS__":
            print(f"⏭️  {key:30} → Manual setup (Set in Render Dashboard)")
            skipped += 1
            continue
        
        success, message = set_environment_variable(key, value)
        
        if success:
            print(f"✅ {key:30} → {message}")
            added += 1
        else:
            print(f"❌ {key:30} → {message}")
            failed += 1
    
    print()
    print("=" * 70)
    print("Summary:")
    print(f"  ✅ Added/Exists: {added}")
    print(f"  ⏭️  Manual Setup:  {skipped}")
    print(f"  ❌ Failed:        {failed}")
    print("=" * 70)
    print()
    
    # Manual instructions
    print("📋 MANUAL SETUP REQUIRED:")
    print()
    print("1. Go to Render Dashboard → Services → api.gtsdispatcher.com")
    print("2. Click 'Settings' → 'Environment'")
    print("3. Add these 3 passwords manually (for security):")
    print()
    for key, desc in MANUAL_SECRETS:
        print(f"   • {key:20} = [Your actual {desc}]")
    print()
    print("4. Click 'Save' after entering all passwords")
    print()
    
    if failed > 0:
        print(f"⚠️  {failed} variables failed. Check API key and permissions.")
        sys.exit(1)
    else:
        print("✅ All variables synced successfully!")
        print()

if __name__ == "__main__":
    main()
