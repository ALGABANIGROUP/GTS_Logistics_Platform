#!/usr/bin/env python3
"""
Script to seed test data for Audit Logs and Portal Requests using raw SQL
Run with: python seed_audit_and_portal_data.py
"""

import asyncio
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Add backend to path
current_dir = Path(__file__).parent
backend_path = current_dir / "backend"
sys.path.insert(0, str(backend_path))
sys.path.insert(0, str(current_dir))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import text
from backend.config import Settings

async def seed_audit_logs(db: AsyncSession):
    """Add sample audit logs using raw SQL"""
    print("Seeding audit logs...")

    audit_logs_sql = """
    INSERT INTO auth_audit_logs (user_id, action, ip_address, user_agent, details, created_at)
    VALUES
    (1, 'LOGIN', '192.168.1.100', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 'Successful login from admin panel', :time1),
    (1, 'CREATE_USER', '192.168.1.100', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 'Created new user: manager@gts.com', :time2),
    (2, 'UPDATE_SHIPMENT', '192.168.1.101', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36', 'Updated shipment LD-001 status to delivered', :time3),
    (1, 'DELETE_PARTNER', '192.168.1.100', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 'Removed partner: Old Carrier Inc.', :time4),
    (1, 'CREATE_PARTNER', '192.168.1.100', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 'Added new logistics partner: Fast Transport LLC', :time5),
    (2, 'VIEW_REPORT', '192.168.1.101', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36', 'Accessed financial report for Q4 2024', :time6),
    (1, 'CHANGE_PASSWORD', '192.168.1.100', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 'Password changed successfully', :time7),
    (1, 'LOGOUT', '192.168.1.100', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 'User logged out', :time8)
    """

    now = datetime.now(timezone.utc)
    params = {
        "time1": now,
        "time2": now - timedelta(hours=1),
        "time3": now - timedelta(hours=2),
        "time4": now - timedelta(hours=3),
        "time5": now - timedelta(hours=4),
        "time6": now - timedelta(hours=5),
        "time7": now - timedelta(hours=6),
        "time8": now - timedelta(hours=7)
    }

    await db.execute(text(audit_logs_sql), params)
    await db.commit()
    print("Added 8 audit logs")

async def seed_portal_requests(db: AsyncSession):
    """Add sample portal access requests using raw SQL"""
    print("Seeding portal requests...")

    portal_requests_sql = """
    INSERT INTO portal_access_requests (
        full_name, company, email, mobile, comment, country, user_type,
        us_state, dot_number, mc_number, us_business_address,
        ca_province, ca_registered_address, ca_company_number,
        status, approved_by, approved_at, rejected_by, rejected_at, created_at
    ) VALUES
    ('John Smith', 'Smith Logistics Inc.', 'john@smithlogistics.com', '+1-555-0101', 'Interested in carrier partnership', 'US', 'carrier',
     'TX', '1234567', 'MC-789012', '123 Main St, Austin, TX 78701',
     NULL, NULL, NULL,
     'pending', NULL, NULL, NULL, NULL, :time1),
    ('Sarah Johnson', 'Johnson Freight Services', 'sarah@johnsonfreight.com', '+1-555-0102', 'Need access for brokerage operations', 'US', 'broker',
     'CA', '2345678', 'MC-890123', '456 Oak Ave, Los Angeles, CA 90210',
     NULL, NULL, NULL,
     'approved', 'admin@gts.com', :approved_at, NULL, NULL, :time2),
    ('Mike Wilson', 'Wilson Transport Ltd', 'mike@wilsontransport.ca', '+1-555-0103', 'Canadian carrier looking to join network', 'CA', 'carrier',
     NULL, NULL, NULL, NULL,
     'ON', '789 Queen St, Toronto, ON M5H 2N2', '1234567890',
     'processing', NULL, NULL, NULL, NULL, :time3),
    ('Lisa Brown', 'Brown Brokerage Co.', 'lisa@brownbrokerage.com', '+1-555-0104', 'Small brokerage firm seeking partnership', 'US', 'broker',
     'FL', '3456789', 'MC-901234', '321 Pine Rd, Miami, FL 33101',
     NULL, NULL, NULL,
     'rejected', NULL, NULL, 'admin@gts.com', :rejected_at, :time4),
    ('David Lee', 'Lee Express Delivery', 'david@leeexpress.com', '+1-555-0105', 'Express delivery service expansion', 'US', 'carrier',
     'NY', '4567890', 'MC-012345', '654 Broadway, New York, NY 10012',
     NULL, NULL, NULL,
     'pending', NULL, NULL, NULL, NULL, :time5)
    """

    now = datetime.now(timezone.utc)
    params = {
        "time1": now,
        "approved_at": now - timedelta(days=1),
        "time2": now - timedelta(days=1),
        "time3": now - timedelta(hours=12),
        "rejected_at": now - timedelta(hours=6),
        "time4": now - timedelta(hours=8),
        "time5": now - timedelta(hours=2)
    }

    await db.execute(text(portal_requests_sql), params)
    await db.commit()
    print("Added 5 portal requests")

async def main():
    """Main seeding function"""
    print("Starting database seeding...")

    # Get database URL from settings
    settings = Settings()
    database_url = settings.DATABASE_URL or settings.ASYNC_DATABASE_URL
    if not database_url:
        raise ValueError("No DATABASE_URL found in environment")

    # Convert to async URL if needed
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif "psycopg2" in database_url:
        database_url = database_url.replace("psycopg2", "asyncpg")

    print(f"Using database URL: {database_url.replace(database_url.split('@')[0].split('//')[1].split(':')[1], '****')}")

    # Create async engine
    engine = create_async_engine(database_url, echo=False)

    # Create session
    async with AsyncSession(engine) as db:
        try:
            await seed_audit_logs(db)
            await seed_portal_requests(db)
            print("✅ Seeding completed successfully!")
        except Exception as e:
            print(f"❌ Error during seeding: {e}")
            await db.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(main())