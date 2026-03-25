"""
Create newsletter subscribers table
Run: python -m backend.scripts.create_newsletter_table
"""

import asyncio
from sqlalchemy import text
from backend.database.session import get_async_session


async def create_newsletter_table():
    """Create newsletter_subscribers table"""
    async for session in get_async_session():
        try:
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS newsletter_subscribers (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    name VARCHAR(100),
                    source VARCHAR(50) DEFAULT 'website',
                    consent_given BOOLEAN DEFAULT TRUE,
                    is_active BOOLEAN DEFAULT TRUE,
                    unsubscribe_token VARCHAR(100),
                    subscribed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    unsubscribed_at TIMESTAMP WITH TIME ZONE,
                    last_sent_at TIMESTAMP WITH TIME ZONE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE
                )
            """))
            await session.commit()
            print("✅ Newsletter subscribers table created successfully")
        except Exception as e:
            print(f"❌ Failed to create table: {e}")
            await session.rollback()


async def main():
    await create_newsletter_table()


if __name__ == "__main__":
    asyncio.run(main())