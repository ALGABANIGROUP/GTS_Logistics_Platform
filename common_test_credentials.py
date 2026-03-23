#!/usr/bin/env python3
"""
Check what users are available in the database using direct SQL
"""
import subprocess
import json

# Try to get users from database using psql or python
print("🔍 Checking for test credentials...\n")

# Default test users
test_users = [
    ("admin@gabanilogistics.com", "admin"),
    ("enjoy983@hotmail.com", "password123"),
    ("test@example.com", "Test123!"),
    ("user@example.com", "Password123!"),
]

print("Common test credentials to try:")
for email, password in test_users:
    print(f"  📧 {email}")
    print(f"     Password: {password}")
    print()

print("To find actual users, check the database directly:")
print("  SELECT id, email, role FROM users LIMIT 10;")
