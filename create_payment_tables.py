#!/usr/bin/env python3
"""
Direct Payment Tables Creation Script
Creates payment-related tables directly in PostgreSQL
without using Alembic migration system
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import create_engine, text
from backend.config import settings

def create_payment_tables():
    """Create payment tables directly in database"""
    
    # Get database URL and convert to synchronous
    db_url = os.getenv('DATABASE_URL', '')
    if not db_url:
        print("❌ DATABASE_URL not set in environment")
        return False
    
    # Convert asyncpg to psycopg2 for synchronous connection
    db_url = db_url.replace('+asyncpg://', '+psycopg2://')
    db_url = db_url.replace('?sslmode=require', '')
    
    print(f"🔌 Connecting to: postgresql://...")
    
    try:
        engine = create_engine(db_url, echo=True)
        
        with engine.connect() as conn:
            trans = conn.begin()
            
            try:
                # Create payment_methods table
                print("\n📋 Creating payment_methods table...")
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS payment_methods (
                        id BIGSERIAL PRIMARY KEY,
                        user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        method_type VARCHAR(20) NOT NULL,
                        token VARCHAR(200) NOT NULL,
                        display_name VARCHAR(100),
                        brand VARCHAR(50),
                        is_active BOOLEAN DEFAULT true,
                        is_default BOOLEAN DEFAULT false,
                        gateway VARCHAR(20) NOT NULL,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        UNIQUE(token, user_id)
                    )
                """))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_payment_methods_user_id ON payment_methods(user_id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_payment_methods_is_default ON payment_methods(is_default)"))
                print("✅ payment_methods table created")
                
                # Create payments table
                print("\n📋 Creating payments table...")
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS payments (
                        id BIGSERIAL PRIMARY KEY,
                        reference_id VARCHAR(50) UNIQUE NOT NULL,
                        invoice_id BIGINT NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
                        payment_method_id BIGINT REFERENCES payment_methods(id) ON DELETE SET NULL,
                        user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        amount DECIMAL(10, 2) NOT NULL,
                        currency VARCHAR(3) DEFAULT 'SDG',
                        status VARCHAR(20) DEFAULT 'pending',
                        payment_gateway VARCHAR(20) NOT NULL,
                        gateway_transaction_id VARCHAR(100),
                        description TEXT,
                        notes TEXT,
                        metadata JSONB,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_payments_reference_id ON payments(reference_id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_payments_invoice_id ON payments(invoice_id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_payments_user_id ON payments(user_id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_payments_status ON payments(status)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_payments_payment_gateway ON payments(payment_gateway)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_payments_gateway_transaction_id ON payments(gateway_transaction_id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_payments_created_at ON payments(created_at)"))
                print("✅ payments table created")
                
                # Create payment_transactions table
                print("\n📋 Creating payment_transactions table...")
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS payment_transactions (
                        id BIGSERIAL PRIMARY KEY,
                        payment_id BIGINT NOT NULL REFERENCES payments(id) ON DELETE CASCADE,
                        transaction_type VARCHAR(20) NOT NULL,
                        amount DECIMAL(10, 2) NOT NULL,
                        status VARCHAR(20) NOT NULL,
                        error_code VARCHAR(50),
                        error_message VARCHAR(500),
                        gateway_response JSONB,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_payment_transactions_payment_id ON payment_transactions(payment_id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_payment_transactions_transaction_type ON payment_transactions(transaction_type)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_payment_transactions_status ON payment_transactions(status)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_payment_transactions_created_at ON payment_transactions(created_at)"))
                print("✅ payment_transactions table created")
                
                # Create refunds table
                print("\n📋 Creating refunds table...")
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS refunds (
                        id BIGSERIAL PRIMARY KEY,
                        reference_id VARCHAR(50) UNIQUE NOT NULL,
                        payment_id BIGINT NOT NULL REFERENCES payments(id) ON DELETE CASCADE,
                        amount DECIMAL(10, 2) NOT NULL,
                        reason VARCHAR(200),
                        status VARCHAR(20) DEFAULT 'pending',
                        gateway_refund_id VARCHAR(100),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        completed_at TIMESTAMP WITH TIME ZONE
                    )
                """))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_refunds_reference_id ON refunds(reference_id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_refunds_payment_id ON refunds(payment_id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_refunds_status ON refunds(status)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_refunds_created_at ON refunds(created_at)"))
                print("✅ refunds table created")
                
                trans.commit()
                print("\n✅ All payment tables created successfully!")
                return True
                
            except Exception as e:
                trans.rollback()
                print(f"\n❌ Error creating tables: {e}")
                return False
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False
    finally:
        engine.dispose()

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Payment Tables Creation Script")
    print("=" * 60)
    
    success = create_payment_tables()
    
    if success:
        print("\n🎉 SUCCESS: All payment tables are now ready!")
        sys.exit(0)
    else:
        print("\n❌ FAILED: Could not create payment tables")
        sys.exit(1)
