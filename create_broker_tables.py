import os
import psycopg2

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment
db_url = os.getenv("DATABASE_URL", "")
if not db_url:
    db_url = os.getenv("SQLALCHEMY_DATABASE_URL", "")

print(f"Database URL found: {bool(db_url)}")

if db_url:
    try:
        # Parse and connect
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        sql_statements = [
            '''
            CREATE TABLE IF NOT EXISTS broker_commission_tiers (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                shipment_type VARCHAR(50) NOT NULL,
                commission_percentage FLOAT NOT NULL,
                minimum_commission FLOAT NOT NULL DEFAULT 0.0,
                maximum_commission FLOAT,
                is_active BOOLEAN NOT NULL DEFAULT true,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP
            )
            ''',
            'CREATE INDEX IF NOT EXISTS ix_broker_commission_tiers_id ON broker_commission_tiers(id)',
            '''
            CREATE TABLE IF NOT EXISTS broker_commissions (
                id SERIAL PRIMARY KEY,
                shipment_id INTEGER NOT NULL,
                shipment_number VARCHAR(50) NOT NULL,
                client_invoice_amount FLOAT NOT NULL,
                carrier_cost FLOAT NOT NULL,
                commission_tier_id INTEGER REFERENCES broker_commission_tiers(id),
                commission_percentage FLOAT NOT NULL DEFAULT 5.0,
                commission_amount FLOAT NOT NULL,
                gross_profit FLOAT NOT NULL,
                net_profit FLOAT NOT NULL,
                profit_margin_percentage FLOAT NOT NULL,
                status VARCHAR(50) NOT NULL DEFAULT 'pending',
                shipment_date TIMESTAMP,
                delivery_date TIMESTAMP,
                commission_payment_date TIMESTAMP,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP,
                notes TEXT
            )
            ''',
            'CREATE INDEX IF NOT EXISTS ix_broker_commissions_id ON broker_commissions(id)',
            'CREATE INDEX IF NOT EXISTS ix_broker_commissions_shipment_id ON broker_commissions(shipment_id)',
            '''
            CREATE TABLE IF NOT EXISTS invoices_enhanced (
                id SERIAL PRIMARY KEY,
                number VARCHAR(100) NOT NULL UNIQUE,
                invoice_type VARCHAR(50) NOT NULL,
                date TIMESTAMP NOT NULL DEFAULT NOW(),
                due_date TIMESTAMP,
                shipment_id INTEGER,
                shipment_number VARCHAR(50),
                from_party VARCHAR(200),
                to_party VARCHAR(200),
                amount_usd FLOAT NOT NULL,
                commission_percentage FLOAT,
                commission_amount FLOAT,
                carrier_cost FLOAT,
                profit_margin FLOAT,
                profit_margin_percentage FLOAT,
                status VARCHAR(50) NOT NULL DEFAULT 'draft',
                payment_method VARCHAR(50),
                payment_date TIMESTAMP,
                currency VARCHAR(10) NOT NULL DEFAULT 'USD',
                notes TEXT,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP
            )
            ''',
            'CREATE INDEX IF NOT EXISTS ix_invoices_enhanced_id ON invoices_enhanced(id)',
            'CREATE INDEX IF NOT EXISTS ix_invoices_enhanced_number ON invoices_enhanced(number)',
            'CREATE INDEX IF NOT EXISTS ix_invoices_enhanced_shipment_id ON invoices_enhanced(shipment_id)',
        ]
        
        for sql in sql_statements:
            if sql.strip():
                try:
                    cursor.execute(sql)
                    print(f"✅ Executed: {sql[:50]}...")
                except Exception as e:
                    if "already exists" in str(e):
                        print(f"⏭️  Already exists: {sql[:50]}...")
                    else:
                        print(f"⚠️  Error: {e}")
        
        conn.commit()
        cursor.close()
        conn.close()
        print("\n✅ All broker tables created/verified successfully!")
        
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
else:
    print("❌ Database URL not found in environment variables")
