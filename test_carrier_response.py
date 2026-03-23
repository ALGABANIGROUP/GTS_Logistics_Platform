import asyncio
from backend.database.session import async_session
from backend.models.carrier import Carrier
from backend.models.carrier_models import CarrierResponse
from sqlalchemy import select

async def test_carrier_response():
    async with async_session() as db:
        try:
            # Get first carrier
            result = await db.execute(select(Carrier).limit(1))
            carrier = result.scalar_one_or_none()

            if carrier:
                print(f'Carrier found: {carrier.name}')
                # Try to create CarrierResponse
                response = CarrierResponse.model_validate(carrier)
                print('CarrierResponse created successfully')
                print(f'ID: {response.id}, Name: {response.name}')
            else:
                print('No carriers found')
        except Exception as e:
            print(f'Error: {e}')
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_carrier_response())