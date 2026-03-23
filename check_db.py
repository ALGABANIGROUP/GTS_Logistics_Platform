from backend.database.session import get_async_session
from sqlalchemy import text
import asyncio

async def check_db():
    async for session in get_async_session():
        try:
            # Check if token_version column exists
            result = await session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'token_version'"))
            token_version_exists = result.fetchone() is not None
            print(f'token_version column exists: {token_version_exists}')

            # Check if audit_logs table exists
            result = await session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_name = 'audit_logs'"))
            audit_logs_exists = result.fetchone() is not None
            print(f'audit_logs table exists: {audit_logs_exists}')

            # Check current migration status
            result = await session.execute(text('SELECT version_num FROM alembic_version'))
            current_version = result.fetchone()
            print(f'Current alembic version: {current_version[0] if current_version else "None"}')

        except Exception as e:
            print(f'Error: {e}')
        finally:
            break

if __name__ == "__main__":
    asyncio.run(check_db())