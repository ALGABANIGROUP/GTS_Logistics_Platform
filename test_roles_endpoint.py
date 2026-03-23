import asyncio
from backend.database.session import wrap_session_factory, async_session
from backend.models.subscription import Role
from sqlalchemy.future import select

async def test_roles():
    try:
        async with wrap_session_factory(async_session) as session:
            stmt = select(Role)
            result = await session.execute(stmt)
            roles = result.scalars().all()
            print(f"Found {len(roles)} roles:")
            for r in roles:
                print(f"- {r.key}: {r.name_en} (AR: {r.name_ar})")
                print(f"  Permissions: {r.permissions}")
                print(f"  Features: {r.features}")
                print(f"  Is System: {r.is_system}")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_roles())
