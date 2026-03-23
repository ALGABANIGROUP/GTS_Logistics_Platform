from dotenv import load_dotenv
load_dotenv()
import os
import psycopg2

db_url = os.getenv("DATABASE_URL")
conn = psycopg2.connect(db_url)
cursor = conn.cursor()

# Check if tables exist
cursor.execute("""
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('broker_commission_tiers', 'broker_commissions', 'invoices_enhanced')
ORDER BY table_name
""")

tables = cursor.fetchall()
print("✅ Created Tables:")
for table in tables:
    print(f"  • {table[0]}")

if len(tables) == 3:
    print("\n✅ All 3 broker tables exist in database!")
    
    # Get table details
    for table_name in ['broker_commission_tiers', 'broker_commissions', 'invoices_enhanced']:
        cursor.execute(f"""
        SELECT COUNT(*) FROM information_schema.columns 
        WHERE table_name = '{table_name}'
        """)
        col_count = cursor.fetchone()[0]
        print(f"   {table_name}: {col_count} columns")
else:
    print(f"\n⚠️  Only {len(tables)} of 3 tables found")

cursor.close()
conn.close()
