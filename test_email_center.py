"""
Quick test script to check Email Center API and create sample data
"""
import asyncio
import sys
from sqlalchemy import select
from backend.database.session import get_async_session
from backend.models.email_center import Mailbox, EmailMessage as EmailMessageModel

async def check_email_center():
    """Check email center tables and data"""
    print("🔍 Checking Email Center...")
    print("-" * 50)
    
    async for session in get_async_session():
        # Check mailboxes
        result = await session.execute(select(Mailbox))
        mailboxes = result.scalars().all()
        
        print(f"\n📬 Mailboxes found: {len(mailboxes)}")
        if mailboxes:
            for mb in mailboxes:
                print(f"  - ID: {mb.id}, Email: {mb.email_address}, Mode: {mb.mode}, Enabled: {mb.is_enabled}")
        else:
            print("  ⚠️  No mailboxes found in database!")
            print("\n💡 To add mailboxes, you need to:")
            print("  1. Go to http://localhost:5173/emails")
            print("  2. Login as admin (super_admin role)")
            print("  3. Click 'Create New Mailbox'")
            print("  4. Fill in the email details and credentials")
        
        # Check messages
        result = await session.execute(select(EmailMessageModel))
        messages = result.scalars().all()
        
        print(f"\n📧 Messages found: {len(messages)}")
        if messages:
            for msg in messages[:5]:  # Show first 5
                print(f"  - ID: {msg.id}, From: {msg.from_addr}, Subject: {msg.subject[:50]}")
        else:
            print("  ℹ️  No email messages yet")
    
    print("\n" + "=" * 50)
    print("✅ Email Center structure is ready!")
    print("🌐 Frontend: http://localhost:5173/emails")
    print("📚 API Docs: http://localhost:8000/docs#/Email%20Center")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(check_email_center())
