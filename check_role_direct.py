#!/usr/bin/env python
"""Check user role directly from database"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def check_user_role():
    """Check specific user role in database"""
    try:
        # Import after env is loaded
        from backend.database.config import get_sessionmaker
        from sqlalchemy import text
        
        sessionmaker = get_sessionmaker()
        async with sessionmaker() as session:
            # Check specific user
            result = await session.execute(
                text("""
                    SELECT id, email, role, is_active, created_at, last_login
                    FROM users 
                    WHERE email = :email
                """),
                {"email": "enjoy983@hotmail.com"}
            )
            user = result.fetchone()
            
            if user:
                print("\n=== User Found in Database ===")
                print(f"ID: {user[0]}")
                print(f"Email: {user[1]}")
                print(f"Role (DB): {user[2]}")
                print(f"Is Active: {user[3]}")
                print(f"Created At: {user[4]}")
                print(f"Last Login: {user[5]}")
            else:
                print(f"\n❌ User not found: enjoy983@hotmail.com")
            
            # List all super_admins
            print("\n=== All Super Admin Users ===")
            result = await session.execute(
                text("""
                    SELECT id, email, role, is_active
                    FROM users 
                    WHERE role = 'super_admin'
                    ORDER BY created_at DESC
                """)
            )
            admins = result.fetchall()
            if admins:
                for admin in admins:
                    print(f"  - ID: {admin[0]}, Email: {admin[1]}, Role: {admin[2]}, Active: {admin[3]}")
            else:
                print("  No super_admin users found")
                
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_user_role())
