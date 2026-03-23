import asyncio
from backend.database.session import async_session
from sqlalchemy import text

async def add_columns():
    async with async_session() as db:
        try:
            columns_to_add = [
                'scac_code VARCHAR(10) UNIQUE',
                'tax_id VARCHAR(50)',
                'website VARCHAR(255)',
                'address_line1 VARCHAR(255)',
                'address_line2 VARCHAR(255)',
                'city VARCHAR(100)',
                'state VARCHAR(50)',
                'zip_code VARCHAR(20)',
                "country VARCHAR(100) DEFAULT 'USA'",
                'contact_person VARCHAR(255)',
                'contact_phone VARCHAR(20)',
                'contact_email VARCHAR(255)',
                'insurance_provider VARCHAR(255)',
                'insurance_policy_number VARCHAR(100)',
                'insurance_expiry_date DATE',
                'bonding_company VARCHAR(255)',
                'bonding_amount DECIMAL(15, 2)',
                'bonding_expiry_date DATE',
                "carrier_type VARCHAR(50) DEFAULT 'common'",
                'equipment_types TEXT[]',
                'operating_areas TEXT[]',
                'preferred_lanes TEXT[]',
                'credit_score INTEGER',
                "payment_terms VARCHAR(100) DEFAULT 'net_30'",
                'rating DECIMAL(3, 2)',
                'total_loads INTEGER DEFAULT 0',
                'on_time_delivery_rate DECIMAL(5, 2)',
                'incident_rate DECIMAL(5, 2)',
                'is_verified BOOLEAN DEFAULT FALSE',
                'verification_date TIMESTAMP WITH TIME ZONE',
                'notes TEXT',
                'updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()'
            ]

            for col_def in columns_to_add:
                sql = f'ALTER TABLE carriers ADD COLUMN IF NOT EXISTS {col_def}'
                print(f'Adding: {col_def.split()[0]}')
                await db.execute(text(sql))

            await db.commit()
            print('All columns added successfully')
        except Exception as e:
            print(f'Error: {e}')
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(add_columns())