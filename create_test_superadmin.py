"""Create a fresh test super_admin user"""
import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

os.environ["DATABASE_URL"] = "postgresql://gabani_transport_solutions_user:__SET_IN_SECRET_MANAGER__@dpg-cuicq2qj1k6c73asm5c0-a.oregon-postgres.render.com:5432/gabani_transport_solutions?sslmode=require"

async def create_test_user():
    import asyncpg
    from passlib.hash import bcrypt
    
    conn = await asyncpg.connect(os.environ["DATABASE_URL"])
    
    # Simple password hash
    password = "test123"
    hashed = bcrypt.hash(password)
    email = "test_super_admin@test.com"
    
    # Check if exists
    existing = await conn.fetchval("SELECT id FROM users WHERE email = $1", email)
    if existing:
        print(f"User {email} already exists (ID: {existing})")
        # Update password
        await conn.execute("UPDATE users SET hashed_password = $1, role = $2 WHERE email = $3", 
                          hashed, "super_admin", email)
        print(f"Updated password to: {password}")
    else:
        # Insert
        await conn.execute(
            "INSERT INTO users (email, hashed_password, role, is_active, full_name) VALUES ($1, $2, $3, $4, $5)",
            email, hashed, "super_admin", True, "Test Super Admin"
        )
        print(f"Created user: {email}")
        print(f"Password: {password}")
    
    print(f"\n✅ Test credentials:")
    print(f"   Email: {email}")
    print(f"   Password: {password}")
    print(f"   Role: super_admin")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(create_test_user())
