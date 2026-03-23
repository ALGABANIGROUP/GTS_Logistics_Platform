# Quick Start - Freight Broker System

## ⚡ 5-Minute Setup

### 1. Initialize Database Tables

```bash
# Navigate to project folder
cd c:\Users\enjoy\dev\GTS

# Apply database migrations
alembic upgrade head
```

### 2. Create Commission Tiers

```bash
# Create a standard LTL tier
curl -X POST http://localhost:8000/api/v1/broker/commission-tiers \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "Standard LTL",
    "shipment_type": "ltl",
    "commission_percentage": 5.0,
    "minimum_commission": 25.0,
    "maximum_commission": 500.0
  }'

# Create FTL tier
curl -X POST http://localhost:8000/api/v1/broker/commission-tiers \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "Premium FTL",
    "shipment_type": "ftl",
    "commission_percentage": 3.5,
    "minimum_commission": 50.0,
    "maximum_commission": 1000.0
  }'
```

### 3. Process a Shipment

```bash
# Step 1: Create customer invoice
curl -X POST http://localhost:8000/api/v1/broker/invoices \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "number": "INV-CUST-20250210-001",
    "invoice_type": "client",
    "from_party": "GTS Logistics",
    "to_party": "ABC Corporation",
    "amount_usd": 2000.00,
    "shipment_id": 1,
    "shipment_number": "SHIP-2025-001"
  }'

# Step 2: Record carrier cost
curl -X POST http://localhost:8000/api/v1/broker/invoices \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "number": "INV-CAR-20250210-001",
    "invoice_type": "carrier",
    "from_party": "Interstate Carriers",
    "amount_usd": 1500.00,
    "shipment_id": 1,
    "shipment_number": "SHIP-2025-001"
  }'

# Step 3: Calculate commission
curl -X POST http://localhost:8000/api/v1/broker/calculate-commission \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "shipment_id": 1,
    "shipment_number": "SHIP-2025-001",
    "client_invoice_amount": 2000.00,
    "carrier_cost": 1500.00,
    "commission_tier_id": 1
  }'
```

### 4. View Reports

```bash
# Commission summary
curl http://localhost:8000/api/v1/broker/reports/commission-summary \
  -H "Authorization: Bearer YOUR_TOKEN"

# Profit breakdown
curl http://localhost:8000/api/v1/broker/reports/profit-breakdown \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📊 Key Metrics

After processing shipments:

| Metric | Value | Formula |
|--------|-------|---------|
| **Revenue** | $2,000 | Customer invoice amount |
| **Cost** | $1,500 | Carrier payment |
| **Gross Profit** | $500 | Revenue - Cost |
| **Commission** | $17.50 | Gross Profit × 5% |
| **Net Profit** | $482.50 | Gross Profit - Commission |
| **Margin %** | 25% | (Gross Profit / Revenue) × 100 |

---

## 🛠️ Admin APIs

### List All Commissions
```bash
GET /api/v1/broker/commissions
```

Filter options:
- `?status=paid`
- `?shipment_id=123`
- `?status=pending`

### List All Invoices
```bash
GET /api/v1/broker/invoices
```

Filter options:
- `?invoice_type=client`
- `?status=sent`
- `?shipment_id=123`

### Update Invoice Status
```bash
PATCH /api/v1/broker/invoices/{id}
{
  "status": "paid",
  "payment_date": "2025-02-10"
}
```

---

## 📈 Sample Reports

### Monthly Commission Report
```bash
GET /api/v1/broker/reports/commission-summary?start_date=2025-02-01&end_date=2025-02-28
```

Returns:
```json
{
  "total_commissions": 8750.00,
  "total_invoices": 250,
  "average_commission_percentage": 4.8,
  "total_gross_profit": 175000.00,
  "total_net_profit": 166250.00,
  "average_profit_margin": 18.5,
  "paid_commissions": 5000.00,
  "pending_commissions": 3750.00
}
```

### Profit by Shipment Type
```bash
GET /api/v1/broker/reports/profit-breakdown?shipment_type=ltl
```

Returns breakdown by type with KPIs.

---

## ✅ Checklist

- [ ] Database tables created (alembic upgrade head)
- [ ] Commission tiers configured
- [ ] First shipment processed
- [ ] Invoices generated
- [ ] Commission calculated
- [ ] Reports viewed

---

## 🚀 Ready to Go!

Your freight broker system is now operational. Start processing shipments and track commissions in real-time!

For detailed documentation, see: **FREIGHT_BROKER_SYSTEM.md**
