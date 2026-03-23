#!/usr/bin/env python3
"""
Setup secure environment variables
Run this ONCE after cloning to generate new secrets
"""

import os
import secrets
import json
from pathlib import Path

def generate_secret(length=32):
    """Generate cryptographically secure random string"""
    return secrets.token_urlsafe(length)

def setup_env():
    """Setup secure environment"""
    
    print("\n" + "="*70)
    print("🔐 GTS SECURE ENVIRONMENT SETUP")
    print("="*70 + "\n")
    
    env_file = Path(".env")
    
    if env_file.exists():
        print("⚠️ .env file already exists")
        response = input("Overwrite? (yes/no): ").strip().lower()
        if response != "yes":
            print("Setup cancelled")
            return
    
    # Collect credentials
    print("📝 Enter your configuration:\n")
    
    config = {
        "ENVIRONMENT": "development",
        "INTERNAL_BASE_URL": input("Internal Base URL (default: http://localhost:8000): ") or "http://localhost:8000",
        "DATABASE_URL": input("PostgreSQL Connection String: ").strip(),
        "JWT_SECRET": generate_secret(),
        "ENCRYPTION_KEY": generate_secret(),
        "OPENAI_API_KEY": input("OpenAI API Key: ").strip(),
        "OPENAI_MODEL": "gpt-4o-mini",
        "OPENAI_TIMEOUT": "30",
        "OPENAI_MAX_RETRIES": "2",
        "OPENAI_ENABLED": "true",
        "HCAPTCHA_SITEKEY": input("hCaptcha Site Key: ").strip(),
        "HCAPTCHA_SECRET": input("hCaptcha Secret: ").strip(),
        "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
        "REFRESH_TOKEN_EXPIRE_DAYS": "7"
    }
    
    # Write .env file
    with open(".env", "w") as f:
        f.write("# GTS Logistics Platform - Secure Environment\n")
        f.write(f"# Generated: {os.popen('date').read().strip()}\n")
        f.write("# ⚠️ NEVER COMMIT THIS FILE\n\n")
        
        for key, value in config.items():
            if key in ["JWT_SECRET", "ENCRYPTION_KEY"]:
                f.write(f"{key}={value}\n")
            else:
                f.write(f"{key}={value}\n")
    
    # Set file permissions (Unix-like systems)
    if os.name != "nt":  # if not Windows
        os.chmod(".env", 0o600)  # Read/write for owner only
    
    print("\n✅ Environment configured successfully")
    print(f"📄 .env file created with secure secrets")
    print(f"🔑 JWT_SECRET: {config['JWT_SECRET'][:15]}...")
    print(f"🔑 ENCRYPTION_KEY: {config['ENCRYPTION_KEY'][:15]}...")
    print("\n⚠️ IMPORTANT:")
    print("  - Never commit .env to git")
    print("  - Share credentials securely with team (use 1Password, LastPass, etc.)")
    print("  - Rotate secrets regularly in production")
    print("="*70 + "\n")

if __name__ == "__main__":
    setup_env()