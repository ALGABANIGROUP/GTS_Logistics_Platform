import asyncio
from backend.database.session import get_async_session
from sqlalchemy import text

async def check_audit_logs():
    async for session in get_async_session():
        result = await session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'audit_logs' ORDER BY column_name"))
        columns = [row[0] for row in result.fetchall()]
        print('Actual audit_logs columns:', columns)
        break

asyncio.run(check_audit_logs())