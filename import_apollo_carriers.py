#!/usr/bin/env python3
"""
Import Apollo Accounts Export CSV into Carriers Table
"""
import os
import asyncio
import csv
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

load_dotenv()

# CSV File Path
CSV_FILE = r"c:\Users\enjoy\OneDrive\Documents\apollo-accounts-export.csv"

def parse_address(address_str):
    """Parse address string into components"""
    if not address_str or address_str.strip() == "":
        return {}, {}

    # Split by comma
    parts = [p.strip() for p in address_str.split(',')]
    if len(parts) < 4:
        return {"address_line1": address_str}, {}

    # Assume format: street, city, state/province, country, postal
    address = {
        "address_line1": parts[0] if len(parts) > 0 else "",
        "city": parts[1] if len(parts) > 1 else "",
        "state": parts[2] if len(parts) > 2 else "",
        "country": parts[3] if len(parts) > 3 else "",
        "zip_code": parts[4] if len(parts) > 4 else "",
    }
    return address, {}

async def import_csv_to_carriers():
    # Use the local SQLite database
    db_url = "sqlite+aiosqlite:///c:/Users/enjoy/dev/GTS-new/backend/gts.db"
    
    engine = create_async_engine(db_url, echo=False)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            # Create carriers table if it doesn't exist
            create_table_query = text("""
                CREATE TABLE IF NOT EXISTS carriers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255),
                    phone VARCHAR(20),
                    website VARCHAR(255),
                    address_line1 VARCHAR(255),
                    city VARCHAR(100),
                    state VARCHAR(50),
                    zip_code VARCHAR(20),
                    country VARCHAR(100) DEFAULT 'USA',
                    carrier_type VARCHAR(50) DEFAULT 'common',
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    tenant_id INTEGER
                )
            """)
            await session.execute(create_table_query)
            await session.commit()

            print("📊 Importing Apollo accounts to carriers table...\n")

            with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                for row in reader:
                    company_name = row.get('Company Name', '').strip()
                    if not company_name:
                        continue

                    # Check if carrier already exists
                    result = await session.execute(
                        text("SELECT id FROM carriers WHERE name = :name"),
                        {"name": company_name}
                    )
                    existing = result.scalar()

                    if existing:
                        print(f"⏭️  {company_name} already exists (ID: {existing})")
                        continue

                    # Parse address
                    address_str = row.get('Company Address', '')
                    address, _ = parse_address(address_str)

                    # Prepare data
                    carrier_data = {
                        "name": company_name,
                        "email": row.get('Company Name for Emails', '').strip() or None,
                        "phone": row.get('Company Phone', '').strip() or None,
                        "website": row.get('Website', '').strip() or None,
                        "address_line1": address.get('address_line1', ''),
                        "city": address.get('city', ''),
                        "state": address.get('state', ''),
                        "zip_code": address.get('zip_code', ''),
                        "country": address.get('country', 'Canada'),  # Default to Canada since all are Canadian
                        "carrier_type": "common",  # Default
                        "is_active": True,
                        "created_at": datetime.utcnow(),
                        "tenant_id": None,
                    }

                    # Insert new carrier
                    insert_query = text("""
                        INSERT INTO carriers (name, email, phone, website, address_line1, city, state, zip_code, country, carrier_type, is_active, created_at, tenant_id)
                        VALUES (:name, :email, :phone, :website, :address_line1, :city, :state, :zip_code, :country, :carrier_type, :is_active, :created_at, :tenant_id)
                        RETURNING id
                    """)

                    result = await session.execute(insert_query, carrier_data)
                    new_id = result.scalar()

                    print(f"✅ {company_name}")
                    print(f"   🌐 Website: {carrier_data['website']}")
                    print(f"   📧 Email: {carrier_data['email']}")
                    print(f"   📞 Phone: {carrier_data['phone']}")
                    print(f"   📍 Address: {address_str}")
                    print(f"   🆔 ID: {new_id}")
                    print()

            await session.commit()
            print("✅ All carriers imported successfully!")

        except Exception as e:
            print(f"❌ Error: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(import_csv_to_carriers())