#!/usr/bin/env python3
"""
Get database connection info to check users
"""
import os
import sys

print("🔍 Checking database configuration...\n")

# Load environment or default connection string
db_url = os.getenv("DATABASE_URL") or os.getenv("SQLALCHEMY_DATABASE_URL")

if db_url:
    print(f"📦 Database URL found: {db_url[:50]}...")
    # Parse connection string
    if "postgresql" in db_url or "postgres" in db_url:
        print("   Type: PostgreSQL ✅")
        # Extract connection details
        parts = db_url.split("://")[1].split("/")
        creds = parts[0]
        db_name = parts[1] if len(parts) > 1 else "unknown"
        print(f"   Database: {db_name}")
else:
    print("❌ DATABASE_URL environment variable not set")
    print("\n📝 You can query the database directly:")
    print("   psql postgresql://user:password@localhost/gts_platform")
    print("   SELECT email, role, is_active FROM users LIMIT 10;")

print("\nTry logging in with these common credentials:")
print("  1. admin@example.com / admin123")
print("  2. test@example.com / Test123!")
print("  3. User email from SignUp process")
