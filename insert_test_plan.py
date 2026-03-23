import asyncio
from backend.database.session import wrap_session_factory
from backend.database.config import get_db_async
from backend.models.billing import Plan, Subscription, Invoice

async def insert_test_data():
    async with wrap_session_factory(get_db_async) as session:
        # Insert test plan
        plan = Plan(
            key="starter_monthly",
            name_ar="Starter Plan",
            name_en="Starter Plan",
            description="Basic plan for small businesses",
            price_monthly=29.99,
            price_yearly=299.99,
            features='["Basic features", "5 users"]',
            limits='{"users": 5, "storage": "10GB"}',
            is_active=True
        )
        session.add(plan)
        await session.commit()
        print("Test plan inserted successfully")

if __name__ == "__main__":
    asyncio.run(insert_test_data())