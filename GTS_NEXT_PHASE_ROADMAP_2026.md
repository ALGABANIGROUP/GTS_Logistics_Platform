# GTS Next Phase Roadmap (2026)

Date: 2026-03-16  
Status: Planned (Post Phase 2 Completion)

---

## 1) Context and Scope

This roadmap is the official next-phase plan after completing the Email AI system (Phase 2d) and production readiness milestones.

Confirmed completed baseline:
- Email Command Center with AI-assisted routing
- Feedback learning loop and AI dashboard
- Backend and frontend test coverage improvements

This document defines what comes next, in priority order.

---

## 2) Priority Order (Approved)

1. Driver Lightweight App (highest priority)
2. Accounting Integration (QuickBooks, Xero)
3. AI Performance Optimization (fine-tuning and evaluation)
4. Full Mobile App (customers, drivers, admins)
5. Additional Languages (EN first, then FR)
6. Additional External Integrations (carriers, ERP, payments, navigation)

---

## 3) Track A: Driver Lightweight App (4-6 weeks)

### Goals
- Replace dedicated GPS hardware with phone-based location sharing where feasible.
- Provide direct communication channel between operations and drivers.
- Enable task updates and proof-of-delivery from the field.

### MVP Features
- Live location tracking with battery-aware background updates (30-60s)
- Driver-operations chat and priority notifications
- Task list and shipment status updates
- POD uploads (photos, signatures)
- Deep links to Google Maps/Waze for turn-by-turn navigation

### Technical Direction
- App: React Native (or Flutter if team decides)
- Location: background geolocation package with power constraints
- Messaging: WebSocket + push notifications (FCM/APNS)
- Auth: JWT + optional biometric unlock

### Backend Dependencies
- Driver location ingestion endpoint(s)
- Driver WS channel stability and reconnect strategy
- Message delivery tracking and retry policy
- Device registration and push token management

### Acceptance Criteria
- >95% successful location pings in pilot routes
- Message delivery latency <5s in normal network conditions
- Battery usage within acceptable daily threshold during active shift

---

## 4) Track B: Accounting Integration (QuickBooks + Xero) (3-4 weeks)

### Goals
- Automate invoice creation/sync from shipments
- Reconcile payment statuses and reduce manual bookkeeping effort
- Improve financial reporting consistency

### Scope
- OAuth connection flow for each provider
- Invoice create/update sync jobs
- Payment status reconciliation mapping
- Error queue and retry workflow

### Data/Mapping Notes
- Shipment -> Accounting Invoice schema mapping
- Customer identifiers and tax fields normalization
- Idempotency keys for safe retries

### Acceptance Criteria
- 100% idempotent sync operations
- Reconciliation mismatch rate <2%
- Full audit log for accounting sync actions

---

## 5) Track C: AI Optimization (4-6 weeks, parallel-capable)

### Goals
- Increase routing accuracy and confidence calibration
- Improve entity extraction quality for logistics and finance emails
- Reduce false-positive classifications

### Scope
- Curate labeled dataset from production feedback
- Add offline evaluation set and benchmark pipeline
- Tune thresholds and fallback policy
- A/B test model/prompt strategies

### KPIs
- Routing accuracy uplift target: +8% or better
- Reduction in manual reassignment rate
- Improvement in entity extraction precision/recall

---

## 6) Track D: Full Mobile App (8-10 weeks)

### Audience
- Customers: shipment tracking, requests, billing status
- Drivers: extends lightweight app capabilities
- Admins: operational overview and approvals

### Approach
- Start with shared mobile design system
- Reuse APIs from web portal where possible
- Add role-specific navigation and permission guards

---

## 7) Track E: Multilingual Expansion (2-3 weeks)

### Order
1. Arabic (existing baseline)
2. English (high priority)
3. French (optional based on market need)

### Scope
- i18n framework standardization
- Translation key coverage for priority modules
- Locale-aware formatting (dates, numbers, currencies)

---

## 8) Track F: External Integrations (phased)

### Candidate Integrations
- Carrier APIs: DHL, FedEx, UPS
- Payment methods: PayPal, Apple Pay, Google Pay
- ERP: SAP, Oracle, Microsoft Dynamics
- Navigation/traffic enhancements

### Delivery Model
- One integration per mini-phase with separate readiness checklist
- Shared connector framework and observability for retries/failures

---

## 9) Timeline Proposal (High-Level)

- Month 1: Track A (Driver App MVP) + Track C kickoff
- Month 2: Track B (Accounting) + Track C iteration
- Month 3: Track D planning and MVP foundation
- Month 4: Track E rollout + selective Track F pilots

---

## 10) Governance and Delivery Controls

For each track before production:
- Architecture review
- Security checklist sign-off
- Performance baseline and regression checks
- Rollback playbook
- Post-launch metrics dashboard

---

## 11) Immediate Next Action

Start Track A (Driver Lightweight App) immediately with:
- Week 1: Architecture and prototype
- Week 2-3: Core tracking + messaging
- Week 4: Pilot and hardening
- Week 5-6: Production rollout (if pilot KPIs pass)

---

## 12) Notes

- This roadmap intentionally prioritizes practical ROI: tracking visibility, communication, and accounting automation.
- AI optimization runs in parallel where possible to avoid blocking operational delivery.
