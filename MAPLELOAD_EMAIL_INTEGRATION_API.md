# MapleLoad Canada Bot v4.0.0 - Email Integration & Learning Database API

## Overview

The enhanced MapleLoad Canada Bot now integrates with incoming email shipments, automatically processes them, and builds a machine learning database from historical shipment data. This document specifies all required backend API endpoints.

---

## 1. Email Processing Endpoints

### 1.1 Get Incoming Emails
**Endpoint:** `GET /api/v1/ai/bots/mapleload-canada/incoming-emails`

**Purpose:** Retrieve list of unprocessed incoming shipment emails

**Response:**
```json
{
    "emails": [
        {
            "id": "EMAIL-001",
            "from": "Jean Fortin <jfortin@multiaction.ca>",
            "subject": "PICKUP",
            "content": "GOOD MORNING\n\nI HAVE 1 SKID TO PICKUP FOR\nSHELF2CART SOLUTIONS\n5 ELECTRONICS AVENUE\nDANVERS, MA 01923\n\n1 SKID\n830 PDS\n48X40X36\n\nSHIPPING HOUR\n7AM TO 4PM\nCLOSE BETWEEN 12 TO 13 HRE",
            "received_at": "2026-01-20T20:57:00Z",
            "processed": false
        },
        ...
    ]
}
```

**Notes:**
- Returns unprocessed emails only
- Includes full email content for parsing
- Timestamps in ISO 8601 format

---

### 1.2 Process Email Shipment
**Endpoint:** `POST /api/v1/ai/bots/mapleload-canada/process-email-shipment`

**Purpose:** Extract shipment data from email and search for matching carriers

**Request Body:**
```json
{
    "email_id": "EMAIL-001",
    "sender": "Jean Fortin <jfortin@multiaction.ca>",
    "subject": "PICKUP",
    "parsed_data": {
        "weight": "830",
        "dimensions": "48X40X36",
        "pickup_location": "MA 01923",
        "company": "SHELF2CART SOLUTIONS",
        "address": "5 ELECTRONICS AVENUE, DANVERS, MA 01923",
        "email_content": "GOOD MORNING I HAVE 1 SKID TO PICKUP FOR SHELF2CART SOLUTIONS..."
    },
    "auto_search": true
}
```

**Response:**
```json
{
    "success": true,
    "record_id": "REC-001-20260120",
    "status": "pending",
    "matched_carriers": [
        {
            "id": 1,
            "name": "TransCanada Logistics",
            "email": "dispatch@transcanada.com",
            "match_score": 0.95,
            "rate_estimate": 1850,
            "capacity": 150
        },
        {
            "id": 2,
            "name": "Maple Freight Solutions",
            "email": "rates@maplefreight.com",
            "match_score": 0.92,
            "rate_estimate": 1750,
            "capacity": 200
        },
        {
            "id": 3,
            "name": "Northern Dispatch",
            "email": "carriers@northerndispatch.com",
            "match_score": 0.88,
            "rate_estimate": 1650,
            "capacity": 180
        }
    ],
    "learning_score": 0.90,
    "message": "Email processed successfully! Found 3 potential carriers."
}
```

**Processing Logic:**
1. Parse email content using regex patterns for:
   - Weight (PDS, lbs, kg)
   - Dimensions (WxHxD)
   - Location (address, city, state, ZIP)
   - Company name
   - Pickup/delivery dates and times

2. Create database record with parsed data

3. Search carrier database using:
   - Weight capacity matching
   - Service area coverage
   - Historical success rate
   - Current load capacity

4. Calculate match scores (0-1.0) based on:
   - Historical similar shipment matches
   - Carrier performance metrics
   - Cost optimization
   - Delivery timeline fit

5. Store results with learning metrics

---

### 1.3 Mark Email as Processed
**Endpoint:** `PUT /api/v1/ai/bots/mapleload-canada/email/{email_id}`

**Purpose:** Mark email as processed and store final status

**Request Body:**
```json
{
    "status": "processed",
    "record_id": "REC-001-20260120",
    "selected_carrier_id": 1,
    "notes": "Matched with TransCanada Logistics - rate $1850"
}
```

**Response:**
```json
{
    "success": true,
    "email_id": "EMAIL-001",
    "status": "processed",
    "updated_at": "2026-01-21T08:30:00Z"
}
```

---

## 2. Learning Database Endpoints

### 2.1 Get Database Records
**Endpoint:** `GET /api/v1/ai/bots/mapleload-canada/database-records`

**Query Parameters:**
- `limit`: Number of records to return (default: 50)
- `offset`: Pagination offset (default: 0)
- `status`: Filter by status (pending, matched, failed, delivered)
- `source`: Filter by source (email, manual, api)

**Response:**
```json
{
    "records": [
        {
            "id": "REC-001-20260120",
            "source": "email",
            "email_from": "jfortin@multiaction.ca",
            "weight": "830",
            "commodity": "Electronics",
            "location": "Danvers, MA 01923",
            "company": "SHELF2CART SOLUTIONS",
            "address": "5 ELECTRONICS AVENUE",
            "matched_carriers": [
                {
                    "id": 1,
                    "name": "TransCanada Logistics",
                    "email": "dispatch@transcanada.com",
                    "match_score": 0.95,
                    "selected": true
                }
            ],
            "status": "pending",
            "created_at": "2026-01-20T20:57:00Z",
            "learning_score": 0.90,
            "notes": "830 lbs, 48x40x36 dimensions, pickup 7AM-4PM (closed 12-1PM)"
        },
        {
            "id": "REC-002-20260119",
            "source": "email",
            "email_from": "shipping@warehouse.ca",
            "weight": "2400",
            "commodity": "Machinery",
            "location": "Toronto, ON",
            "company": "Industrial Manufacturing Co",
            "matched_carriers": [
                {
                    "id": 2,
                    "name": "Maple Freight Solutions",
                    "match_score": 0.94,
                    "selected": true
                }
            ],
            "status": "delivered",
            "created_at": "2026-01-19T14:30:00Z",
            "delivery_date": "2026-01-22T16:45:00Z",
            "learning_score": 0.88
        }
    ],
    "total": 142,
    "limit": 50,
    "offset": 0
}
```

---

### 2.2 Get Learning Statistics
**Endpoint:** `GET /api/v1/ai/bots/mapleload-canada/learning-stats`

**Purpose:** Retrieve AI learning metrics and system performance

**Response:**
```json
{
    "stats": {
        "total_processed": 142,
        "successful_matches": 131,
        "failed_matches": 11,
        "avg_match_rate": 0.924,
        "system_learning": 0.876,
        "accuracy_trend": [
            {"period": "Week 1", "accuracy": 0.78},
            {"period": "Week 2", "accuracy": 0.82},
            {"period": "Week 3", "accuracy": 0.86},
            {"period": "Week 4", "accuracy": 0.92}
        ],
        "carrier_performance": [
            {
                "carrier_id": 1,
                "name": "TransCanada Logistics",
                "successful_shipments": 35,
                "failed_shipments": 2,
                "success_rate": 0.946,
                "avg_delivery_time_hours": 72,
                "customer_satisfaction": 4.8
            },
            {
                "carrier_id": 2,
                "name": "Maple Freight Solutions",
                "successful_shipments": 42,
                "failed_shipments": 3,
                "success_rate": 0.933,
                "avg_delivery_time_hours": 68,
                "customer_satisfaction": 4.7
            }
        ],
        "commodity_insights": [
            {
                "commodity": "Electronics",
                "total_shipments": 25,
                "avg_weight": 650,
                "best_carrier": "TransCanada Logistics",
                "avg_cost": 1450
            },
            {
                "commodity": "Machinery",
                "total_shipments": 18,
                "avg_weight": 2800,
                "best_carrier": "Canadian Carriers Network",
                "avg_cost": 2150
            }
        ]
    }
}
```

---

### 2.3 Get Record Details
**Endpoint:** `GET /api/v1/ai/bots/mapleload-canada/records/{record_id}`

**Purpose:** Get detailed information about a specific shipment record

**Response:**
```json
{
    "record": {
        "id": "REC-001-20260120",
        "source": "email",
        "email_from": "jfortin@multiaction.ca",
        "weight": "830",
        "dimensions": "48X40X36",
        "commodity": "Electronics",
        "location": "Danvers, MA 01923",
        "company": "SHELF2CART SOLUTIONS",
        "address": "5 ELECTRONICS AVENUE",
        "pickup_time_start": "07:00",
        "pickup_time_end": "16:00",
        "pickup_break_start": "12:00",
        "pickup_break_end": "13:00",
        "created_at": "2026-01-20T20:57:00Z",
        "matched_carriers": [
            {
                "id": 1,
                "name": "TransCanada Logistics",
                "email": "dispatch@transcanada.com",
                "match_score": 0.95,
                "rate_estimate": 1850,
                "capacity": 150,
                "success_rate": 0.946,
                "avg_delivery_hours": 72,
                "selected": true,
                "outreach_sent": true,
                "outreach_sent_at": "2026-01-20T21:30:00Z",
                "response_received": true,
                "response_at": "2026-01-20T22:15:00Z",
                "response_message": "We can pick this up tomorrow morning at 9 AM"
            }
        ],
        "status": "pending",
        "learning_score": 0.90,
        "estimated_value": 1850,
        "historical_similar_shipments": [
            {
                "id": "REC-123",
                "weight": 820,
                "commodity": "Electronics",
                "location": "Boston, MA",
                "matched_carrier": "TransCanada Logistics",
                "success": true,
                "actual_cost": 1825
            }
        ]
    }
}
```

---

### 2.4 Update Record Status
**Endpoint:** `PUT /api/v1/ai/bots/mapleload-canada/records/{record_id}`

**Purpose:** Update shipment status as it progresses through lifecycle

**Request Body:**
```json
{
    "status": "delivered",
    "delivery_date": "2026-01-22T16:45:00Z",
    "actual_cost": 1850,
    "carrier_feedback": 4.9,
    "customer_feedback": 4.8,
    "notes": "Successful delivery. Carrier was professional and on-time."
}
```

**Response:**
```json
{
    "success": true,
    "record_id": "REC-001-20260120",
    "status": "delivered",
    "learning_feedback_recorded": true,
    "system_learning_updated": true,
    "new_learning_score": 0.94
}
```

---

## 3. Email Shipment Parsing Specification

### 3.1 Regular Expression Patterns

The system uses the following patterns to extract data from email text:

```javascript
// Weight patterns (PDS, lbs, kg, pounds)
weight: /(\d+)\s*(?:PDS|lbs|kg|pounds)/i

// Dimensions patterns (WxHxD)
dimensions: /(\d+)\s*x\s*(\d+)\s*x\s*(\d+)/i

// Location patterns (City, State, ZIP)
location: /([A-Z]{2})\s*(\d{5})/

// Company/Location patterns
company_for: /PICKUP FOR\s+(.+?)(?:\n|$)/i

// Full address pattern
address: /(\d+)\s+([^,]+),\s+([^,]+),\s+([A-Z]{2})/

// Time patterns
time_start: /(\d{1,2})[:\s]+AM/i
time_end: /(\d{1,2})[:\s]+PM/i
time_range: /(\d{1,2})[:\s]*(\d{2})?\s*[AaPp][Mm]\s*[TtOo]\s*(\d{1,2})[:\s]*(\d{2})?\s*[AaPp][Mm]/i

// Break/Close time
break_time: /CLOSE BETWEEN\s+(\d{1,2})[:\s]*(\d{2})?\s*[AaPp][Mm]?\s*[TtOo]\s*(\d{1,2})[:\s]*(\d{2})?\s*[AaPp][Mm]?/i
```

### 3.2 Parsed Data Structure

After extraction, create the following structure:

```python
{
    "weight": str,  # in lbs
    "dimensions": str,  # format: "WxHxD"
    "pickup_location": str,  # city, state, ZIP
    "company": str,  # shipper company name
    "address": str,  # full address
    "pickup_time_start": str,  # HH:MM format
    "pickup_time_end": str,  # HH:MM format
    "pickup_break_start": str,  # HH:MM format (optional)
    "pickup_break_end": str,  # HH:MM format (optional)
    "email_content": str,  # original email text
    "extracted_at": ISO8601,  # timestamp
    "confidence": float  # 0-1.0, extraction confidence
}
```

---

## 4. Carrier Matching Algorithm

### 4.1 Matching Criteria

The system calculates match scores based on:

1. **Weight Capacity** (weight 0.25)
   - Carrier truck capacity >= shipment weight
   - Preferred: carrier regularly handles this weight
   - Score: 0-1.0

2. **Service Area** (weight 0.20)
   - Carrier serves origin and destination
   - Historical data from successful shipments
   - Score: 0-1.0

3. **Commodity Fit** (weight 0.20)
   - Carrier experience with commodity type
   - From historical successful shipments
   - Score: 0-1.0

4. **Historical Performance** (weight 0.20)
   - Carrier success rate from database
   - Average delivery time
   - Customer satisfaction scores
   - Score: 0-1.0

5. **Current Capacity** (weight 0.15)
   - Available trucks at pickup time
   - Current load utilization
   - Score: 0-1.0

### 4.2 Match Score Formula

```
match_score = (
    weight_capacity * 0.25 +
    service_area * 0.20 +
    commodity_fit * 0.20 +
    historical_performance * 0.20 +
    current_capacity * 0.15
)
```

Results sorted by match_score in descending order.

---

## 5. Learning Database Schema

### 5.1 Shipment Records Table

```sql
CREATE TABLE shipment_records (
    id VARCHAR(20) PRIMARY KEY,  -- REC-NNN-YYYYMMDD
    source ENUM('email', 'manual', 'api'),
    email_id VARCHAR(50),  -- Foreign key to emails table
    email_from VARCHAR(255),
    weight INTEGER,  -- in lbs
    dimensions VARCHAR(50),  -- WxHxD
    commodity VARCHAR(100),
    pickup_location VARCHAR(255),
    pickup_address VARCHAR(255),
    company_name VARCHAR(255),
    pickup_time_start TIME,
    pickup_time_end TIME,
    pickup_break_start TIME NULL,
    pickup_break_end TIME NULL,
    status ENUM('pending', 'matched', 'outreach_sent', 'accepted', 'picked_up', 'in_transit', 'delivered', 'failed'),
    created_at TIMESTAMP,
    processed_at TIMESTAMP NULL,
    delivery_date TIMESTAMP NULL,
    selected_carrier_id INT,  -- Foreign key
    learning_score FLOAT,  -- 0-1.0
    estimated_value DECIMAL(10,2),
    actual_cost DECIMAL(10,2) NULL,
    carrier_feedback FLOAT NULL,  -- 0-5.0
    customer_feedback FLOAT NULL,  -- 0-5.0
    notes TEXT,
    FOREIGN KEY (selected_carrier_id) REFERENCES suppliers(id)
);

CREATE TABLE carrier_matches (
    id INT PRIMARY KEY AUTO_INCREMENT,
    record_id VARCHAR(20),
    carrier_id INT,
    match_score FLOAT,  -- 0-1.0
    rate_estimate DECIMAL(10,2),
    created_at TIMESTAMP,
    FOREIGN KEY (record_id) REFERENCES shipment_records(id),
    FOREIGN KEY (carrier_id) REFERENCES suppliers(id)
);

CREATE TABLE learning_insights (
    id INT PRIMARY KEY AUTO_INCREMENT,
    metric_type ENUM('carrier_performance', 'commodity_trend', 'accuracy', 'cost'),
    carrier_id INT NULL,
    commodity VARCHAR(100) NULL,
    metric_value FLOAT,
    data_points INT,
    updated_at TIMESTAMP,
    FOREIGN KEY (carrier_id) REFERENCES suppliers(id)
);
```

---

## 6. Example: Processing Email

### Input Email
```
From: Jean Fortin <JFortin@multiaction.ca>
Sent: Tuesday, January 20, 2026 8:57 PM
To: CUSTOMERS@GABANILOGISTICS.COM
Subject: PICKUP

GOOD MORNING

I HAVE 1 SKID TO PICKUP FOR

SHELF2CART SOLUTIONS

5 ELECTRONICS AVENUE

DANVERS, MA

01923

1 SKID

830 PDS

48X40X36

SHIPPING HOUR

7AM TO 4PM

CLOSE BETWEEN 12 TO 13 HRE

THANK YOU

Jean Fortin
Département de l'expédition
Shipping Department

b: (418) 660-1180, poste 237
e:  jfortin@multiaction.ca
w: https://www.multiaction.ca
a: 6890 boulevard Ste-Anne, L'Ange-Gardien, QC G0A 2K0 Canada
```

### Parsed Output
```json
{
    "weight": "830",
    "dimensions": "48X40X36",
    "pickup_location": "MA 01923",
    "company": "SHELF2CART SOLUTIONS",
    "address": "5 ELECTRONICS AVENUE, DANVERS, MA",
    "pickup_time_start": "07:00",
    "pickup_time_end": "16:00",
    "pickup_break_start": "12:00",
    "pickup_break_end": "13:00",
    "email_content": "GOOD MORNING I HAVE 1 SKID...",
    "extracted_at": "2026-01-20T20:57:00Z",
    "confidence": 0.94
}
```

### Created Record
```json
{
    "id": "REC-001-20260120",
    "source": "email",
    "email_from": "JFortin@multiaction.ca",
    "weight": 830,
    "commodity": "General Freight",
    "location": "Danvers, MA 01923",
    "company": "SHELF2CART SOLUTIONS",
    "status": "pending",
    "created_at": "2026-01-20T20:57:00Z",
    "learning_score": 0.85
}
```

### Matched Carriers (Top 3)
1. **TransCanada Logistics** - Match: 0.95
   - Weight: 830 lbs ✓ (capacity 24,000)
   - Service area: MA ✓
   - Success rate: 94.6%
   - Est. cost: $1,850

2. **Maple Freight Solutions** - Match: 0.92
   - Weight: 830 lbs ✓ (capacity 26,000)
   - Service area: Northeast US ✓
   - Success rate: 93.3%
   - Est. cost: $1,750

3. **Northern Dispatch** - Match: 0.88
   - Weight: 830 lbs ✓ (capacity 22,000)
   - Service area: Northeast ✓
   - Success rate: 89.5%
   - Est. cost: $1,650

---

## 7. Integration Checklist

- [ ] Create shipment_records table
- [ ] Create carrier_matches table
- [ ] Create learning_insights table
- [ ] Implement email parsing logic
- [ ] Implement carrier matching algorithm
- [ ] Create GET /incoming-emails endpoint
- [ ] Create POST /process-email-shipment endpoint
- [ ] Create PUT /email/{email_id} endpoint
- [ ] Create GET /database-records endpoint
- [ ] Create GET /learning-stats endpoint
- [ ] Create GET /records/{record_id} endpoint
- [ ] Create PUT /records/{record_id} endpoint
- [ ] Add email monitoring/polling service
- [ ] Add learning calculation background job
- [ ] Set up logging and monitoring
- [ ] Create admin dashboard for stats
- [ ] Add email delivery verification
- [ ] Implement feedback collection system

---

## 8. Performance Considerations

- **Database Indexing:**
  - Index on `created_at` for time-based queries
  - Index on `status` for filtering
  - Index on `source` for source filtering
  - Composite index on (status, created_at)

- **Caching:**
  - Cache learning_stats (update every 1 hour)
  - Cache carrier performance metrics (update every 30 mins)
  - Cache commodity insights (update every 1 hour)

- **Background Jobs:**
  - Process emails every 5 minutes
  - Update learning scores every hour
  - Calculate insights every 6 hours
  - Archive old records (>90 days) monthly

---

## 9. Security Considerations

- Sanitize email content before storing
- Mask PII in logs and statistics
- Validate all input data
- Rate limit API endpoints
- Require authentication for all endpoints
- Log all modifications with user/timestamp
- Encrypt sensitive data in transit and at rest
- Regular backup of learning database

---

**Version:** 4.0.0  
**Last Updated:** February 5, 2026  
**Status:** Ready for Implementation
