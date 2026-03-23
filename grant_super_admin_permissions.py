import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import update, select
from backend.models.subscription import Role

DATABASE_URL = "postgresql+asyncpg://gabani_transport_solutions_user:__SET_IN_SECRET_MANAGER__@dpg-cuicq2qj1k6c73asm5c0-a.oregon-postgres.render.com:5432/gabani_transport_solutions"

ALL_PERMISSIONS = [
    'shipments.view', 'shipments.create', 'shipments.update', 'shipments.delete',
    'tms', 'tms.core', 'tms.shipments',
    'drivers.view', 'drivers.manage',
    'dispatch.assign', 'users.update',
    # Preferred features
    'ad_free',
    'unlimited_views',
    'toll_charge_estimate',
    'fuel_surcharge_calculator',
    'driving_time',
    'backhaul',
    'days_to_pay_credit_score',
    '30_day_rate_check',
    'rate_check_1_7_15_day',
    'load_density_report',
    'capacity_indicator',
    'historical_trend'
]

async def main():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        result = await conn.execute(select(Role.permissions).where(Role.key == 'super_admin'))
        perms = set()
        for row in result:
            perms.update(row[0] or [])
        all_perms = perms | set(ALL_PERMISSIONS)
        await conn.execute(update(Role).where(Role.key == 'super_admin').values(permissions=list(all_perms)))
        await conn.commit()
        print(f"EN super_admin EN. EN: {list(all_perms)}")

if __name__ == "__main__":
    asyncio.run(main())
