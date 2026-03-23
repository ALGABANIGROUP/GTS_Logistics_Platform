import asyncio
from backend.database.connection import SessionLocal
from sqlalchemy import text

async def check_roles():
    async with SessionLocal() as session:
        result = await session.execute(text('SELECT DISTINCT role FROM users ORDER BY role'))
        roles = [r[0] for r in result.fetchall()]
        print("\n=== Roles in Database ===")
        for role in roles:
            print(f"  - {role}")
        print(f"\nTotal: {len(roles)} distinct roles")
        return roles

if __name__ == "__main__":
    roles = asyncio.run(check_roles())
