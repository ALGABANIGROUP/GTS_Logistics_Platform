import asyncio
from backend.models.subscription import Role
from backend.database.session import wrap_session_factory, async_session
from sqlalchemy.future import select

async def test_roles_query():
    try:
        async with wrap_session_factory(async_session) as session:
            # Test the new query format
            stmt = select(
                Role.key,
                Role.name,
                Role.name_ar,
                Role.name_en,
                Role.permissions,
                Role.is_system
            )
            result = await session.execute(stmt)
            roles_data = result.all()
            
            print(f"✓ Successfully queried {len(roles_data)} roles:")
            for r in roles_data:
                print(f"  - {r.key}: {r.name_en} (AR: {r.name_ar})")
                
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_roles_query())
