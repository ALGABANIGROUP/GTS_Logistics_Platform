#!/usr/bin/env python3
import asyncio
import sys
sys.path.insert(0, '.')

async def test_admin_endpoints():
    try:
        from backend.database.config import get_sessionmaker
        from backend.models.user import User
        from sqlalchemy import select, func
        
        sessionmaker = get_sessionmaker()
        async with sessionmaker() as session:
            # Test user count
            total = await session.scalar(select(func.count(User.id)))
            active = await session.scalar(select(func.count(User.id)).where(User.is_active == True))
            
            print(f"✓ Database connection working")
            print(f"  Total users: {total or 0}")
            print(f"  Active users: {active or 0}")
            
            # Get sample users
            result = await session.execute(select(User).limit(3))
            users = result.scalars().all()
            
            print(f"\n✓ Sample users (first 3):")
            for u in users:
                print(f"  - {u.email} ({u.role}) - Active: {u.is_active}")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test_admin_endpoints())
