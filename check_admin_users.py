#!/usr/bin/env python
"""Check users and their roles"""
import sys
import os
import asyncio
sys.path.insert(0, os.path.dirname(__file__))

# Try to check users
async def main():
    try:
        from backend.models.user import User
        from backend.database.config import get_sessionmaker, init_engines
        from sqlalchemy import select
        
        # Initialize engines
        init_engines()
        
        # Get sessionmaker
        maker = get_sessionmaker()
        if not maker:
            print("Error: Failed to initialize database")
            return
        
        # Create session
        async with maker() as session:
            # Get all users
            stmt = select(User).limit(10)
            result = await session.execute(stmt)
            users = result.scalars().all()
            
            print("=" * 60)
            print("Users in Database:")
            print("=" * 60)
            for user in users:
                print(f"ID: {user.id} | Email: {user.email} | Role: {user.role} | Active: {user.is_active}")
            
            print("\n" + "=" * 60)
            print("Summary:")
            print("=" * 60)
            admin_count = sum(1 for u in users if u.role in ['admin', 'super_admin', 'system_admin'])
            print(f"Total Users: {len(users)}")
            print(f"Admin Users: {admin_count}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
