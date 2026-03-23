# GTS Tracking System Webhook Integration Specification

## Overview
This document defines the webhook architecture for real-time shipment tracking integration in the GTS platform. Webhooks enable automatic invoice generation and updates based on shipment lifecycle events.

---

## Webhook Event Types

### 1. Shipment Created
**Event:** `shipment.created`  
**Trigger:** New shipment is booked in tracking system  
**Action:** Create draft invoice with shipment details

**Payload:**
```json
{
  "event": "shipment.created",
  "timestamp": "2024-01-20T10:30:00Z",
  "shipment_id": "BL-789456",
  "data": {
    "shipper": {
      "company_id": "001",
      "company_name": "ABC Logistics",
      "contact": "John Smith",
      "email": "john@abclogistics.com"
    },
    "consignee": {
      "company_id": "002",
      "company_name": "XYZ Manufacturing",
      "contact": "Jane Doe",
      "address": "123 Main St, Toronto, ON"
    },
    "carrier": {
      "company_id": "003",
      "company_name": "FastTrack Trucking",
      "driver_name": "Mike Johnson",
      "truck_id": "TRK-456"
    },
    "route": {
      "origin": "Toronto, ON",
      "destination": "Vancouver, BC",
      "distance_km": 2100,
      "estimated_transit_days": 3
    },
    "cargo": {
      "weight_kg": 5000,
      "volume_cbm": 15.5,
      "cargo_type": "general_freight",
      "special_handling": []
    },
    "scheduled_pickup": "2024-01-21T08:00:00Z",
    "estimated_delivery": "2024-01-24T17:00:00Z"
  }
}
```

**System Response:**
- Create invoice in `draft` status
- Generate invoice number
- Calculate initial pricing estimate
- Link invoice to shipment_id

---

### 2. Shipment Picked Up
**Event:** `shipment.picked_up`  
**Trigger:** Driver confirms pickup with signature/photo  
**Action:** Confirm invoice, update status to `sent`

**Payload:**
```json
{
  "event": "shipment.picked_up",
  "timestamp": "2024-01-21T08:15:00Z",
  "shipment_id": "BL-789456",
  "data": {
    "actual_pickup_time": "2024-01-21T08:15:00Z",
    "pickup_location": {
      "address": "100 Industrial Pkwy, Toronto, ON",
      "latitude": 43.7184,
      "longitude": -79.5181
    },
    "driver_info": {
      "name": "Mike Johnson",
      "license": "D12345678",
      "phone": "+1-416-555-0123"
    },
    "pickup_confirmation": {
      "signature_url": "https://storage.gts.com/signatures/abc123.png",
      "photo_urls": [
        "https://storage.gts.com/photos/load1.jpg",
        "https://storage.gts.com/photos/load2.jpg"
      ]
    },
    "cargo_actual": {
      "weight_kg": 5050,
      "pieces": 25,
      "condition": "good"
    }
  }
}
```

**System Response:**
- Update invoice status: `draft` → `sent`
- Attach pickup proof documents
- Send invoice email to client
- Update cargo weight if different
- Start tracking timer for delivery

---

### 3. Shipment In Transit
**Event:** `shipment.in_transit`  
**Trigger:** GPS updates every 15-60 minutes  
**Action:** Update tracking info, no invoice change (unless delay)

**Payload:**
```json
{
  "event": "shipment.in_transit",
  "timestamp": "2024-01-22T14:30:00Z",
  "shipment_id": "BL-789456",
  "data": {
    "current_location": {
      "city": "Winnipeg, MB",
      "latitude": 49.8951,
      "longitude": -97.1384
    },
    "progress": {
      "distance_completed_km": 850,
      "distance_remaining_km": 1250,
      "percent_complete": 40.5
    },
    "status": "on_schedule",
    "estimated_arrival": "2024-01-24T17:00:00Z",
    "next_checkpoint": "Calgary, AB"
  }
}
```

**System Response:**
- Update tracking dashboard
- Send notification to client (if subscribed)
- No invoice modification

---

### 4. Shipment Delayed
**Event:** `shipment.delayed`  
**Trigger:** ETA pushed back by >2 hours  
**Action:** Update invoice with delay charges (if applicable)

**Payload:**
```json
{
  "event": "shipment.delayed",
  "timestamp": "2024-01-23T10:00:00Z",
  "shipment_id": "BL-789456",
  "data": {
    "delay_reason": "weather_conditions",
    "delay_category": "force_majeure",
    "original_eta": "2024-01-24T17:00:00Z",
    "new_eta": "2024-01-25T12:00:00Z",
    "delay_hours": 19,
    "current_location": {
      "city": "Regina, SK",
      "latitude": 50.4452,
      "longitude": -104.6189
    },
    "notes": "Severe snowstorm in Saskatchewan. Road closures on Hwy 1."
  }
}
```

**System Response:**
- Send alert to client and carrier
- Check contract for delay penalties/credits
- Add line item if delay charges apply
- Update estimated delivery date
- Log delay incident for analytics

---

### 5. Shipment Delivered
**Event:** `shipment.delivered`  
**Trigger:** Driver confirms delivery with POD signature  
**Action:** Finalize invoice, add POD, mark as `due`

**Payload:**
```json
{
  "event": "shipment.delivered",
  "timestamp": "2024-01-24T16:45:00Z",
  "shipment_id": "BL-789456",
  "data": {
    "actual_delivery_time": "2024-01-24T16:45:00Z",
    "delivery_location": {
      "address": "5678 Pacific Ave, Vancouver, BC",
      "latitude": 49.2827,
      "longitude": -123.1207
    },
    "recipient": {
      "name": "Sarah Chen",
      "title": "Receiving Manager",
      "contact": "sarah@xyzmanufacturing.com"
    },
    "proof_of_delivery": {
      "signature_url": "https://storage.gts.com/pod/xyz789.png",
      "photo_urls": [
        "https://storage.gts.com/photos/delivery1.jpg",
        "https://storage.gts.com/photos/delivery2.jpg"
      ],
      "timestamp": "2024-01-24T16:45:00Z"
    },
    "delivery_notes": "All 25 pieces delivered in good condition. No damages.",
    "cargo_condition": "excellent",
    "on_time": true
  }
}
```

**System Response:**
- Update invoice status: `sent` → `due`
- Attach POD documents to invoice
- Set payment due date (e.g., Net 30 from delivery)
- Send invoice reminder to client
- Update shipment status to `completed`
- Trigger carrier payment process
- Calculate final costs and margin
- Update analytics (on-time %, customer satisfaction)

---

### 6. Exception / Incident
**Event:** `shipment.exception`  
**Trigger:** Damage, theft, customs hold, accident  
**Action:** Flag invoice for review, may require credit note

**Payload:**
```json
{
  "event": "shipment.exception",
  "timestamp": "2024-01-23T11:30:00Z",
  "shipment_id": "BL-789456",
  "data": {
    "exception_type": "cargo_damage",
    "severity": "medium",
    "location": {
      "city": "Calgary, AB",
      "latitude": 51.0447,
      "longitude": -114.0719
    },
    "description": "Minor water damage to 3 pallets due to truck leak during rainstorm.",
    "affected_items": [
      "Pallet #23",
      "Pallet #24",
      "Pallet #25"
    ],
    "estimated_loss": 1500.00,
    "photos": [
      "https://storage.gts.com/incidents/damage1.jpg",
      "https://storage.gts.com/incidents/damage2.jpg"
    ],
    "insurance_claim": {
      "claim_number": "INS-2024-001",
      "status": "filed",
      "insured_value": 15000.00
    },
    "actions_taken": "Cargo transferred to dry truck. Continued transit.",
    "customer_notified": true
  }
}
```

**System Response:**
- Flag invoice for manual review
- Send urgent alert to operations team
- Notify client of exception
- Prepare documentation for credit note
- Link insurance claim to invoice
- Update risk profile for carrier/lane
- Create incident report

---

## Webhook Endpoint Configuration

### GTS Webhook Receiver
**URL:** `https://api.gts.com/api/v1/webhooks/tracking`  
**Method:** `POST`  
**Authentication:** HMAC signature or Bearer token

**Headers:**
```
Content-Type: application/json
X-Webhook-Signature: sha256=<signature>
X-Webhook-ID: <unique_webhook_id>
X-Webhook-Timestamp: <unix_timestamp>
```

### Signature Verification
```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    computed = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(computed, signature)
```

---

## Response Format

### Success Response
```json
{
  "status": "success",
  "received_at": "2024-01-20T10:30:05Z",
  "event_id": "evt_abc123",
  "processed": true,
  "actions_taken": [
    "invoice_created",
    "notification_sent"
  ]
}
```

### Error Response
```json
{
  "status": "error",
  "error_code": "INVALID_SHIPMENT_ID",
  "message": "Shipment BL-789456 not found in system",
  "received_at": "2024-01-20T10:30:05Z",
  "retry": false
}
```

---

## Retry Logic

- **Timeout:** 30 seconds per webhook attempt
- **Retries:** 3 attempts with exponential backoff (1min, 5min, 15min)
- **Failure Handling:** Alert operations team after 3 failures

---

## Integration Workflow

### Phase 1: Setup (Week 1)
1. Register webhook endpoints with tracking system
2. Implement signature verification
3. Set up event routing to invoice system
4. Test with sandbox data

### Phase 2: Event Handling (Week 2)
1. Implement handlers for each event type
2. Build invoice automation workflows
3. Add error handling and logging
4. Test end-to-end flows

### Phase 3: Monitoring (Week 3)
1. Set up webhook monitoring dashboard
2. Add alerting for failures
3. Implement retry queue
4. Performance optimization

---

## Security Considerations

1. **Signature Verification:** Always verify HMAC signature
2. **IP Whitelisting:** Restrict webhooks to known IPs
3. **Rate Limiting:** Max 100 webhooks/minute per source
4. **Idempotency:** Use `X-Webhook-ID` to prevent duplicate processing
5. **Encryption:** TLS 1.3 required for all webhook traffic

---

## Monitoring & Alerting

### Metrics to Track
- Webhook success rate (target: >99%)
- Average processing time (target: <500ms)
- Queue depth (target: <10)
- Failed webhook count (alert if >5/hour)

### Alerts
- **Critical:** 3 consecutive webhook failures
- **Warning:** Processing time >2 seconds
- **Info:** New webhook source detected

---

## Testing Strategy

### Unit Tests
- Signature verification
- Event parsing
- Invoice state transitions

### Integration Tests
- End-to-end shipment lifecycle
- Error scenarios (invalid data, network failures)
- Concurrent webhook processing

### Load Tests
- 1000 webhooks/minute sustained
- Spike handling (5000 webhooks in 10 seconds)

---

## Maintenance & Support

### Webhook Logs
- Retain for 90 days
- Store: event type, timestamp, processing time, result
- Searchable by shipment_id, event type, date range

### Troubleshooting
1. Check webhook signature
2. Verify shipment exists in system
3. Review event processing logs
4. Check invoice state machine
5. Test webhook endpoint manually

---

## Future Enhancements

1. **Bi-directional Sync:** Push invoice status back to tracking system
2. **ML Predictions:** Predict delays before they happen
3. **Smart Routing:** Auto-select best carrier based on lane/history
4. **Blockchain POD:** Immutable proof of delivery records
5. **IoT Integration:** Temperature sensors, shock detectors for cargo

---

## Contact & Support

**Integration Team:** integrations@gts.com  
**Technical Support:** support@gts.com  
**Documentation:** https://docs.gts.com/webhooks  
**Status Page:** https://status.gts.com
