# FIGURES CAPTIONS

## CANADIAN PATENT APPLICATION
**Title:** AI-POWERED MULTI-BOT ORCHESTRATION SYSTEM FOR LOGISTICS AUTOMATION  
**Applicant:** GABANI TRANSPORT SOLUTIONS (GTS) CORP.

---

## Figure 1: System Architecture Diagram

**Caption:**  
Figure 1 illustrates the overall system architecture comprising a Bot Registry for managing bot lifecycle, a Shared Memory System providing inter-bot communication through a distributed database, a Task Orchestration Engine for workflow coordination, and a Self-Learning Module enabling performance improvement. Specialized bots including Freight Matching Bot, Payment Bot, Incident Bot, Document Bot, Maintenance Bot, and Carrier Verification Bot communicate via the Shared Memory System to execute logistics operations autonomously.

**Elements:**
- Bot Registry (manages registration, monitoring, termination)
- Shared Memory System (distributed database, unified state)
- Task Orchestration Engine (DAG creation, task assignment)
- Self-Learning Module (reinforcement learning, feedback loops)
- Freight Matching Bot (load matching, rate prediction)
- Payment Bot (gateway abstraction, currency conversion)
- Incident Bot (detection, classification, response)
- Document Bot (OCR, validation, expiry tracking)
- Maintenance Bot (telemetry, prediction, optimization)
- Carrier Verification Bot (validation, monitoring, risk scoring)

---

## Figure 2: Freight Matching Workflow

**Caption:**  
Figure 2 is a flowchart showing the intelligent freight matching process comprising: (1) load ingestion from multiple sources including load boards and direct shipper integrations, (2) load enrichment with geographic coordinates, route calculations, and commodity classification, (3) carrier scoring based on performance, safety, and capacity metrics, (4) predictive rate analysis forecasting optimal rates using machine learning algorithms, and (5) automatic load matching with optional human review when confidence score falls below a configured threshold.

**Flow Steps:**
1. Load Ingestion → DAT, Truckstop, Direct Shipper APIs
2. Load Enrichment → Coordinates, Routes, Commodity
3. Carrier Scoring → Performance (70%) + Safety (20%) + Capacity (10%)
4. Predictive Rate Analysis → Market rates + Seasonal adjustments + Fuel surcharge
5. Automatic Matching → Score ≥ Threshold → Auto-assign | Score < Threshold → Human review

---

## Figure 3: Payment Processing Architecture

**Caption:**  
Figure 3 depicts the unified payment processing architecture comprising a payment gateway abstraction layer providing a unified API interface to Stripe, Wise, and SUDAPAY gateways. The system includes multi-currency support for USD, CAD, and SDG with automatic currency conversion based on real-time exchange rates, unified transaction history aggregation across all gateways, and webhook-based payment confirmation for automated reconciliation.

**Components:**
- Payment Gateway Abstraction Layer
  - Unified API: create_payment(), confirm_payment(), refund_payment(), get_exchange_rate()
- Gateways:
  - Stripe (credit/debit cards, subscriptions)
  - Wise (international wires, multi-currency)
  - SUDAPAY (Sudanese payment network)
- Core Features:
  - Multi-currency support (USD, CAD, SDG)
  - Automatic currency conversion (real-time rates)
  - Unified transaction history
  - Webhook-based confirmation

---

## Figure 4: Incident Detection and Response Flowchart

**Caption:**  
Figure 4 is a flowchart illustrating autonomous incident detection and response comprising: (1) real-time telemetry ingestion from vehicles, weather services, and traffic systems, (2) incident classification by type and severity using machine learning models and rule-based filters, (3) automated response workflows executing carrier notifications, route recalculation, and customer alerts, and (4) route optimization generating alternative routes based on incident data.

**Flow Steps:**
1. Telemetry Ingestion → Vehicles + Weather + Traffic
2. Incident Classification → Type (delay, weather, accident, mechanical) + Severity (critical, high, medium, low)
3. Automated Response → Carrier notifications + Route recalculation + Customer alerts
4. Route Optimization → Alternative routes + Updated ETA

---

## Figure 5: Document Processing Pipeline

**Caption:**  
Figure 5 illustrates the AI-powered document processing pipeline comprising: (1) OCR-based text extraction from transportation documents including bills of lading, customs forms, and insurance certificates, (2) document classification engine categorizing documents by type, (3) data validation system verifying extracted information against regulatory requirements and business rules, and (4) expiration tracking and alert generation for time-sensitive documents.

**Pipeline Stages:**
1. OCR Extraction → Tesseract OCR + Custom models + Barcode/QR reading
2. Document Classification → Bill of Lading, Customs, Insurance, License, Permit
3. Data Validation → Regulatory compliance + Business rules + Anomaly detection
4. Expiration Tracking → Alerts at 90, 60, 30, 7, 1 days + Block operations on expiry

---

## Figure 6: Predictive Maintenance System Diagram

**Caption:**  
Figure 6 depicts the predictive fleet maintenance system comprising: (1) real-time telemetry ingestion from vehicle sensors including engine diagnostics, fuel consumption, location, and driver behavior, (2) predictive maintenance algorithms forecasting component failures using historical and operational data, (3) fuel consumption optimization analyzing driving behavior and route efficiency, and (4) driver behavior analysis monitoring performance metrics with automated alert generation.

**Components:**
- Telemetry Ingestion → Engine diagnostics + Fuel consumption + Location + Driver behavior
- Predictive Maintenance → Failure probability (7d, 30d, 90d) + Optimal service schedules
- Fuel Optimization → Idle time reduction + Speed optimization + Route efficiency scoring
- Driver Analysis → Speed + Braking + Idling + Cornering + Automated coaching

---

## Figure 7: Carrier Verification Workflow

**Caption:**  
Figure 7 is a flowchart showing carrier onboarding and continuous verification comprising: (1) automated carrier data verification against FMCSA and equivalent data sources, (2) insurance certificate validation confirming coverage and expiration dates, (3) continuous monitoring detecting changes in carrier status, safety ratings, or compliance indicators, (4) risk scoring algorithm calculating composite risk scores, and (5) document expiration alerts for time-sensitive credentials.

**Flow Steps:**
1. Automated Verification → FMCSA/CVOR databases + Operating authority + Safety ratings
2. Insurance Validation → Coverage confirmation + Policy verification + Expiration tracking
3. Continuous Monitoring → Daily authority checks + Weekly insurance checks + Monthly safety checks
4. Risk Scoring → Performance (on-time, claims) + Safety (accidents, violations) + Financial + Compliance
5. Expiration Alerts → Real-time alerts + Operational blocking on expiry

---

## DRAWING REQUIREMENTS

| Requirement | Specification |
|-------------|---------------|
| Paper Size | 8.5 x 11 inches (Letter) or A4 |
| Margins | Top: 2.5 cm, Bottom: 2.5 cm, Left: 2.5 cm, Right: 1.5 cm |
| Line Quality | Black ink, clear and durable |
| Numbering | Each figure numbered consecutively |
| Numbering | Each figure numbered consecutively (Fig. 1, Fig. 2, etc.) |
| File Format | PDF or high-resolution images embedded in PDF |

---

**End of Figures Captions**
