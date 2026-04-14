# Freight Broker System - Implementation Guide

## Overview

The GTS platform now includes a comprehensive **Freight Broker Commission Management System** designed specifically for operating as a freight broker. This system automatically calculates commissions, tracks profits, and generates detailed financial reports.

---

## 🚀 New Features Implemented

### 1. Commission Tier Management
Define multiple commission tiers for different shipment types:

```bash
POST /api/v1/broker/commission-tiers
{
  "name": "Standard LTL",
  "shipment_type": "ltl",
  "commission_percentage": 5.0,
  "minimum_commission": 25.0,
  "maximum_commission": 500.0,
  "is_active": true
}
```

**Tiers Support:**
- Less Than Truckload (LTL)
- Full Truckload (FTL)
- Parcel / Small package
- Special / Hazmat

### 2. Automatic Commission Calculation

Calculate broker earnings automatically when shipment is delivered:

```bash
POST /api/v1/broker/calculate-commission
{
  "shipment_id": 123,
  "shipment_number": "SHIP-2025-001",
  "client_invoice_amount": 1500.00,    # What you charge customer
  "carrier_cost": 1200.00,              # What you pay carrier
  "commission_tier_id": 5               # Optional: use tier's percentage
}
```

**Response includes:**
```json
{
  "id": 42,
  "gross_profit": 300.00,              # (1500 - 1200)
  "commission_percentage": 5.0,        # From tier or custom
  "commission_amount": 15.00,          # (300 * 5%)
  "net_profit": 285.00,                # (300 - 15)
  "profit_margin_percentage": 20.0,    # (300 / 1500) * 100
  "status": "calculated"
}
```

### 3. Enhanced Invoice Generation

Create separate invoices for different parties:

```bash
POST /api/v1/broker/invoices
{
  "number": "INV-2025-CLIENT-001",
  "invoice_type": "client",            # "client", "carrier", "commission"
  "from_party": "GTS Logistics Inc",
  "to_party": "ABC Shipping Corp",
  "amount_usd": 1500.00,
  "shipment_id": 123,
  "notes": "Cross-country shipment"
}
```

**Invoice Types:**
- **client**: Invoice to customer/shipper
- **carrier**: Invoice from carrier (record of payment)
- **commission**: Internal commission tracking

### 4. Multi-Invoice Workflow

For each shipment, create multiple invoices:

1. **Customer Invoice** - What to bill customer
2. **Carrier Invoice** - Cost from carrier
3. **Commission Record** - Your profit tracking

```bash
# Step 1: Create customer invoice
POST /api/v1/broker/invoices
{
  "number": "INV-CUST-001",
  "invoice_type": "client",
  "to_party": "Customer Name",
  "amount_usd": 1500.00,
  "shipment_id": 123
}

# Step 2: Record carrier invoice
POST /api/v1/broker/invoices
{
  "number": "INV-CARRIER-001",
  "invoice_type": "carrier",
  "from_party": "Carrier Name",
  "amount_usd": 1200.00,
  "shipment_id": 123
}

# Step 3: Calculate commission
POST /api/v1/broker/calculate-commission
{
  "shipment_id": 123,
  "shipment_number": "SHIP-001",
  "client_invoice_amount": 1500.00,
  "carrier_cost": 1200.00,
  "commission_percentage": 5.0
}
```

### 5. Commission Reports & Analytics

**Get Commission Summary:**
```bash
GET /api/v1/broker/reports/commission-summary?start_date=2025-01-01&end_date=2025-01-31
```

Response:
```json
{
  "total_commissions": 4500.00,
  "total_invoices": 120,
  "average_commission_percentage": 5.2,
  "total_gross_profit": 90000.00,
  "total_net_profit": 85500.00,
  "average_profit_margin": 19.5,
  "paid_commissions": 2000.00,
  "pending_commissions": 2500.00
}
```

**Get Profit Breakdown:**
```bash
GET /api/v1/broker/reports/profit-breakdown?shipment_type=ltl
```

Response:
```json
{
  "summary": {
    "total_shipments": 50,
    "total_revenue": 75000.00,
    "total_costs": 60000.00,
    "total_gross_profit": 15000.00,
    "total_commissions": 750.00,
    "total_net_profit": 14250.00
  },
  "statistics": {
    "avg_revenue_per_shipment": 1500.00,
    "avg_profit_margin": 20.0,
    "avg_commission_percentage": 5.0
  }
}
```

---

## 📊 Database Models

### CommissionTier
Stores commission tier configurations for different shipment types.

**Fields:**
- `id` - Primary key
- `name` - Tier name (e.g., "Standard LTL")
- `shipment_type` - Shipment type (ltl, ftl, parcel, special)
- `commission_percentage` - Percentage to charge
- `minimum_commission` - Minimum commission amount
- `maximum_commission` - Maximum commission amount (or NULL for unlimited)
- `is_active` - Active/inactive toggle

### BrokerCommission
Tracks every broker commission earned on shipments.

**Fields:**
- `shipment_id` - Link to shipment
- `shipment_number` - Reference number
- `client_invoice_amount` - Amount charged to customer
- `carrier_cost` - Amount paid to carrier
- `commission_percentage` - Commission rate applied
- `commission_amount` - Calculated commission
- `gross_profit` - client_amount - carrier_cost
- `net_profit` - gross_profit - commission
- `profit_margin_percentage` - Percentage profit margin
- `status` - pending, calculated, approved, paid
- `shipment_date` - When shipment was sent
- `delivery_date` - When shipment was delivered
- `commission_payment_date` - When commission was paid

### EnhancedInvoice
Extended invoice model with broker-specific fields.

**New Fields:**
- `invoice_type` - Type of invoice (client, carrier, commission)
- `from_party` - Issuing party
- `to_party` - Receiving party
- `carrier_cost` - Cost to pay carrier
- `profit_margin` - Profit amount
- `profit_margin_percentage` - Profit percentage
- `payment_method` - How payment was made
- `payment_date` - When payment was received

---

## 🛠️ API Endpoints

### Commission Tiers
- `POST /api/v1/broker/commission-tiers` - Create tier
- `GET /api/v1/broker/commission-tiers` - List tiers
- `GET /api/v1/broker/commission-tiers?shipment_type=ltl` - Filter by type

### Commission Calculation
- `POST /api/v1/broker/calculate-commission` - Calculate & create
- `GET /api/v1/broker/commissions` - List all commissions
- `GET /api/v1/broker/commissions/{id}` - Get specific commission
- `GET /api/v1/broker/commissions?status=paid` - Filter by status
- `GET /api/v1/broker/commissions?shipment_id=123` - Filter by shipment

### Enhanced Invoices
- `POST /api/v1/broker/invoices` - Create invoice
- `GET /api/v1/broker/invoices` - List invoices
- `GET /api/v1/broker/invoices?invoice_type=client` - Filter by type
- `PATCH /api/v1/broker/invoices/{id}` - Update status

### Reports
- `GET /api/v1/broker/reports/commission-summary` - Commission summary
- `GET /api/v1/broker/reports/profit-breakdown` - Profit breakdown

---

## 💼 Usage Example: Complete Shipment Workflow

### 1. Shipment Delivered
```bash
# A shipment has been delivered, now create invoices
POST /api/v1/broker/invoices
{
  "number": "INV-CLT-20250210-001",
  "invoice_type": "client",
  "from_party": "GTS Logistics",
  "to_party": "ABC Corporation",
  "amount_usd": 2500.00,
  "shipment_id": 456,
  "shipment_number": "SHIP-2025-456"
}
```

### 2. Record Carrier Cost
```bash
POST /api/v1/broker/invoices
{
  "number": "INV-CAR-20250210-001",
  "invoice_type": "carrier",
  "from_party": "Interstate Carriers",
  "amount_usd": 1900.00,
  "shipment_id": 456,
  "shipment_number": "SHIP-2025-456"
}
```

### 3. Calculate Commission
```bash
POST /api/v1/broker/calculate-commission
{
  "shipment_id": 456,
  "shipment_number": "SHIP-2025-456",
  "client_invoice_amount": 2500.00,
  "carrier_cost": 1900.00,
  "commission_tier_id": 1  # "Standard LTL"
}
```

**Result:**
- Gross Profit: $600 (2500 - 1900)
- Commission: $30 (600 * 5%)
- Net Profit: $570
- Profit Margin: 24%

### 4. Track Commission Status
```bash
# Mark invoice as sent
PATCH /api/v1/broker/invoices/789
{
  "status": "sent"
}

# When payment received
PATCH /api/v1/broker/invoices/789
{
  "status": "paid",
  "payment_date": "2025-02-10"
}
```

---

## 📈 Monthly Reporting

Generate monthly profit reports:

```bash
GET /api/v1/broker/reports/profit-breakdown?start_date=2025-02-01&end_date=2025-02-28
```

**Track KPIs:**
- Total revenue
- Total commissions paid
- Average profit margin
- Number of shipments
- Average commission percentage

---

## 🔧 Configuration

**Set Default Commission Percentage:**
```python
# In config or environment
DEFAULT_BROKER_COMMISSION = 5.0  # 5%
DEFAULT_MIN_COMMISSION = 25.00   # $25 minimum
```

---

## ✅ Testing

Test the broker system:

```bash
# Create a commission tier
curl -X POST http://localhost:8000/api/v1/broker/commission-tiers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Standard LTL",
    "shipment_type": "ltl",
    "commission_percentage": 5.0
  }'

# Calculate commission
curl -X POST http://localhost:8000/api/v1/broker/calculate-commission \
  -H "Content-Type: application/json" \
  -d '{
    "shipment_id": 1,
    "shipment_number": "SHIP-001",
    "client_invoice_amount": 1500,
    "carrier_cost": 1200
  }'

# Get reports
curl http://localhost:8000/api/v1/broker/reports/commission-summary
```

---

## 🎯 Next Steps

1. ✅ Create commission tiers for your shipment types
2. ✅ Configure minimum/maximum commission amounts
3. ✅ Start tracking commissions on each shipment
4. ✅ Generate monthly profit reports
5. ✅ Integrate with accounting system

---

## 📞 Support

For issues or questions about the freight broker system, contact:
- **Operations:** operations@gabanilogistics.com
- **Support:** support@gabanilogistics.com
