import asyncio
from backend.database.session import get_async_session
from sqlalchemy import text

async def check_auth_audit_logs():
    async for session in get_async_session():
        result = await session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_name = 'auth_audit_logs'"))
        if result.fetchone():
            print('✅ auth_audit_logs table exists')

            # Check columns
            result = await session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'auth_audit_logs' ORDER BY column_name"))
            columns = [row[0] for row in result.fetchall()]
            print(f'Columns: {columns}')
        else:
            print('❌ auth_audit_logs table does not exist')
        break

asyncio.run(check_auth_audit_logs())