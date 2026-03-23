"""Quick password check for enjoy983@hotmail.com"""
import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

os.environ["DATABASE_URL"] = "postgresql://gabani_transport_solutions_user:8yCHEOG5yRgwzpihA3ocDu6Cc13v4lLv@dpg-cuicq2qj1k6c73asm5c0-a.oregon-postgres.render.com:5432/gabani_transport_solutions?sslmode=require"

async def check():
    import asyncpg
    
    conn = await asyncpg.connect(os.environ["DATABASE_URL"])
    
    row = await conn.fetchrow(
        "SELECT id, email, hashed_password, role FROM users WHERE email = $1",
        "enjoy983@hotmail.com"
    )
    
    if row:
        print(f"\n=== User Found ===")
        print(f"ID: {row['id']}")
        print(f"Email: {row['email']}")
        print(f"Role: {row['role']}")
        print(f"Password Hash: {row['hashed_password'][:50]}...")
        
        # Test password verification
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        test_passwords = ["Super@dmin123", "admin123", "Admin123", "password"]
        for pwd in test_passwords:
            verified = pwd_context.verify(pwd, row['hashed_password'])
            print(f"Password '{pwd}': {'✅ MATCH' if verified else '❌ no match'}")
    else:
        print("User not found!")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(check())
