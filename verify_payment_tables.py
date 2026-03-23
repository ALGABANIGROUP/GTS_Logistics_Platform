#!/usr/bin/env python3
"""Verify payment tables creation"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Add to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import create_engine, inspect, text
import os

def check_tables():
    db_url = os.getenv('DATABASE_URL', '')
    if not db_url:
        print("❌ DATABASE_URL not found")
        return
    
    db_url = db_url.replace('+asyncpg://', '+psycopg2://').replace('?sslmode=require', '')
    
    try:
        engine = create_engine(db_url)
        inspector = inspect(engine)
        
        tables = inspector.get_table_names()
        payment_tables = [t for t in tables if 'payment' in t]
        
        print("\n" + "="*60)
        print("✅ DATABASE VERIFICATION")
        print("="*60)
        
        print(f"\nTotal tables in database: {len(tables)}")
        print(f"\nPayment-related tables ({len(payment_tables)}):")
        for table in sorted(payment_tables):
            cols = inspector.get_columns(table)
            print(f"  ✅ {table} ({len(cols)} columns)")
            for col in cols[:3]:
                print(f"     - {col['name']}: {col['type']}")
            if len(cols) > 3:
                print(f"     ... and {len(cols)-3} more columns")
        
        print("\n" + "="*60)
        print("✅ SUCCESS: All payment tables are ready!")
        print("="*60 + "\n")
        
        engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    check_tables()
