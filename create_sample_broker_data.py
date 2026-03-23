"""
Create sample broker data for testing
"""
from dotenv import load_dotenv
load_dotenv()

import os
import psycopg2
from datetime import datetime, timedelta

db_url = os.getenv("DATABASE_URL")
conn = psycopg2.connect(db_url)
cursor = conn.cursor()

# Sample commission tiers
tiers_data = [
    ('Standard FTL', 'FTL', 12.5, 0, 500),
    ('Premium FTL', 'FTL', 15.0, 500, None),
    ('Standard LTL', 'LTL', 8.0, 0, 200),
    ('Premium LTL', 'LTL', 10.0, 200, None),
    ('Parcel Service', 'PARCEL', 5.0, 0, 100),
    ('Special Handling', 'SPECIAL', 20.0, 0, None),
]

print("📝 Creating commission tiers...")
for name, shipment_type, commission_pct, min_comm, max_comm in tiers_data:
    try:
        cursor.execute(
            '''INSERT INTO broker_commission_tiers 
               (name, shipment_type, commission_percentage, minimum_commission, maximum_commission, is_active)
               VALUES (%s, %s, %s, %s, %s, true)
               ON CONFLICT DO NOTHING
            ''',
            (name, shipment_type, commission_pct, min_comm, max_comm)
        )
        print(f"  ✅ {name}")
    except Exception as e:
        print(f"  ⚠️  {name}: {e}")

# Sample commissions
commissions_data = [
    (1001, 'SHP-001', 5000, 3500, 1, 12.5),
    (1002, 'SHP-002', 3500, 2200, 3, 8.0),
    (1003, 'SHP-003', 7500, 5000, 2, 15.0),
    (1004, 'SHP-004', 4000, 2800, 4, 10.0),
    (1005, 'SHP-005', 2500, 1800, 5, 5.0),
]

print("\n📝 Creating sample commissions...")
for shipment_id, shipment_num, client_amount, carrier_cost, tier_id, comm_pct in commissions_data:
    gross_profit = client_amount - carrier_cost
    comm_amount = gross_profit * (comm_pct / 100)
    net_profit = gross_profit - comm_amount
    margin_pct = (gross_profit / client_amount) * 100
    
    try:
        cursor.execute(
            '''INSERT INTO broker_commissions 
               (shipment_id, shipment_number, client_invoice_amount, carrier_cost,
                commission_tier_id, commission_percentage, commission_amount,
                gross_profit, net_profit, profit_margin_percentage, status)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'calculated')
               ON CONFLICT DO NOTHING
            ''',
            (shipment_id, shipment_num, client_amount, carrier_cost, tier_id, 
             comm_pct, comm_amount, gross_profit, net_profit, margin_pct)
        )
        print(f"  ✅ {shipment_num}: ${gross_profit:.2f} profit (${comm_amount:.2f} commission)")
    except Exception as e:
        print(f"  ⚠️  {shipment_num}: {e}")

# Sample enhanced invoices
invoices_data = [
    ('INV-20260210-001', 'client', 1001, 'SHP-001', 'ABC Corp', 'XYZ Logistics', 5000),
    ('INV-20260210-002', 'carrier', 1002, 'SHP-002', 'XYZ Logistics', 'National Carrier', 2200),
    ('INV-20260210-003', 'commission', 1003, 'SHP-003', 'Broker', 'Internal', 937.50),
]

print("\n📝 Creating sample invoices...")
for inv_num, inv_type, shipment_id, shipment_num, from_party, to_party, amount in invoices_data:
    try:
        cursor.execute(
            '''INSERT INTO invoices_enhanced 
               (number, invoice_type, shipment_id, shipment_number, from_party, to_party, 
                amount_usd, status, currency)
               VALUES (%s, %s, %s, %s, %s, %s, %s, 'draft', 'USD')
               ON CONFLICT DO NOTHING
            ''',
            (inv_num, inv_type, shipment_id, shipment_num, from_party, to_party, amount)
        )
        print(f"  ✅ {inv_num}: {inv_type.upper()} (${amount:.2f})")
    except Exception as e:
        print(f"  ⚠️  {inv_num}: {e}")

conn.commit()
cursor.close()
conn.close()

print("\n✅ Sample data created successfully!")
print("\nSample Data Summary:")
print(f"  • {len(tiers_data)} commission tiers")
print(f"  • {len(commissions_data)} sample commissions")
print(f"  • {len(invoices_data)} sample invoices")
