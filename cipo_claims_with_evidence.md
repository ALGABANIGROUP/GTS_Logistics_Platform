# Claims With Code Evidence

## Internal Use Only
This memo is an internal support document for prosecution strategy and claim drafting. It is not intended to be filed with CIPO. The evidence ratings below are conservative and reflect code currently located in the repository on 2026-03-25.

## Evidence Ratings
- `strong`: directly supported by multiple code locations
- `partial`: some implementation support exists, but the full claim scope is broader than the code found
- `not clearly evidenced`: little or no direct implementation support was located for the specific limitation

## Claim 1
**Summary:** Multi-bot system with registry, shared state, orchestration, and runtime execution.

**Rating:** `strong`

**Evidence**
- `backend/main.py:966-980` defines `_AIRegistry` with bot registration and lookup methods.
- `backend/main.py:1263-1265` shows coordinated concurrent execution of multiple bots via `asyncio.create_task(...)`.
- `backend/main.py:1342-1529` registers multiple specialized bots and aliases into the runtime registry.
- `backend/ai/registry_fill.py:94-131` bulk-registers bots from `BOTS_REGISTRY`, including aliases and unavailable placeholders.
- `backend/bots/information_coordinator.py:3`, `backend/bots/information_coordinator.py:17` describe shared coordination and cross-bot data consistency.

## Claim 2
**Summary:** Registry manages registration, discovery, health monitoring, suspension, restart, or termination.

**Rating:** `partial`

**Evidence**
- `backend/main.py:970` exposes runtime registration.
- `backend/ai/registry_fill.py:94-131` performs registry population and alias mapping.
- `backend/models/bot_os.py:10-17` defines persisted `bot_registry` fields including `enabled` and `automation_level`.

**Gap Note**
- Registration and enablement are evidenced. Full restart, suspension, and termination lifecycle handling was not clearly located as first-class registry logic.

## Claim 3
**Summary:** Shared memory system with task outputs, workflow state, transaction logging, version history, or concurrency control.

**Rating:** `partial`

**Evidence**
- `backend/bots/information_coordinator.py:3` states "Single source of truth, conflict detection, and cross-bot data coordination."
- `backend/bots/information_coordinator.py:17` describes shared data quality and consistency across the AI bot system.
- `backend/bots/information_coordinator.py:190` exposes a shared-runtime entrypoint.
- `backend/unified_bot_system.py:5` describes unified registry and communication helpers.

**Gap Note**
- Shared coordination is strong. Explicit transaction logging, version history, and locking semantics are broader than what was directly confirmed in code.

## Claim 4
**Summary:** Orchestration engine generates dependency graphs and handles retries or dead-letter processing.

**Rating:** `partial`

**Evidence**
- `backend/routes/orchestration.py:41` exposes orchestration routes.
- `backend/routes/orchestration.py:391` assigns bots to operations.
- `backend/routes/orchestration.py:686-694` contains `_assign_bots_to_operation(...)`.

**Gap Note**
- Task assignment is evidenced. Directed acyclic graph generation, retries, and dead-letter handling were not clearly identified in implementation.

## Claim 5
**Summary:** Freight matching using route information, market data, or carrier scoring.

**Rating:** `strong`

**Evidence**
- `backend/routes/freight_broker_canada.py:89-177` exposes Canadian loads, booking, and market-rate related routes.
- `backend/bots/freight_broker.py:131-132`, `backend/bots/freight_broker.py:206-219` implement rate comparison logic.
- `backend/routes/freight_market_rates.py:94-168` provides Canadian market-rate endpoints and corridor-specific pricing.

## Claim 6
**Summary:** Predicted rate data using historical lane information and current market conditions.

**Rating:** `strong`

**Evidence**
- `backend/routes/freight_market_rates.py:87` defines `confidence_score`.
- `backend/routes/freight_market_rates.py:333` computes a confidence score from scored corridor analysis.
- `backend/routes/freight_market_rates.py:467-521` generates historical and market-rate outputs.

## Claim 7
**Summary:** Carrier scoring combines performance, safety, and capacity data.

**Rating:** `partial`

**Evidence**
- `backend/routes/freight_market_rates.py:333` shows weighted scoring output through corridor analysis confidence.
- `backend/routes/freight_broker_canada.py:89-177` and `backend/bots/freight_broker.py:206-219` support market comparison and booking flows.

**Gap Note**
- The general concept of composite freight scoring is supported, but the exact performance-safety-capacity formulation was not located in a single explicit scoring module.

## Claim 8
**Summary:** Payment management through a gateway abstraction layer that normalizes multiple payment gateways.

**Rating:** `strong`

**Evidence**
- `backend/services/payment_service.py:73-172` provides a unified payment service with normalized gateway and currency handling.
- `backend/services/stripe_service.py:20-86` implements Stripe gateway operations.
- `backend/services/wise_service.py:14-46`, `backend/services/wise_service.py:144-165` implement Wise functions and currency-related balance retrieval.
- `backend/services/sudapay_service.py:73-220` implements SUDAPAY payment creation and confirmation flows.

## Claim 9
**Summary:** Multi-currency processing and asynchronous payment confirmation handling.

**Rating:** `strong`

**Evidence**
- `backend/services/payment_service.py:91-99` normalizes currency codes.
- `backend/services/payment_service.py:303`, `backend/services/payment_service.py:346-347`, `backend/services/payment_service.py:472-502` track and confirm `gateway_transaction_id`.
- `backend/webhooks/payment_webhooks.py:121-137` validates webhook payment identity, currency, and amounts.
- `backend/webhooks/payment_webhooks.py:170-336` processes SUDAPAY webhook events.
- `backend/webhooks/payment_webhooks.py:357-458` processes Stripe webhook events.

## Claim 10
**Summary:** Incident detection from telemetry or external data and automated response actions.

**Rating:** `partial`

**Evidence**
- `backend/services/incident_tracker.py:47-77` creates incidents and determines severity.
- `backend/services/incident_tracker.py:244-269` aggregates incident severity and applies severity determination rules.
- `backend/routes/safety_api.py:112` invokes current risk assessment.
- `backend/routes/safety_api.py:164-166` exposes weather alert access.
- `backend/services/weather_service.py:26-130` gathers current and forecast weather and analyzes weather risks.

**Gap Note**
- Detection and classification are supported. Fully autonomous downstream operational actions are broader than the code directly confirmed.

## Claim 11
**Summary:** Automated response actions include notification, route recalculation, ETA update, escalation, or reassignment.

**Rating:** `partial`

**Evidence**
- `backend/services/incident_tracker.py:281` triggers alert logging by severity.
- `backend/services/weather_service.py:112-130` analyzes forecast risks that can feed response decisions.

**Gap Note**
- Alerting and risk generation are present. Specific automated ETA, reassignment, or route recalculation flows were not clearly confirmed as end-to-end implementations.

## Claim 12
**Summary:** OCR-based extraction of structured information from transport documents.

**Rating:** `partial`

**Evidence**
- `backend/app/api/v1/endpoints/documents.py:216-245` exposes OCR processing endpoints.
- `backend/bots/documents_manager.py:4`, `backend/bots/documents_manager.py:18` describe OCR and document classification support.
- `backend/routes/ocr_invoice_extract.py:36-60` implements OCR invoice extraction using `easyocr`.

**Gap Note**
- OCR endpoints exist, but parts of the generic document manager still use simulated OCR results.

## Claim 13
**Summary:** Document classification, validation, or expiration tracking.

**Rating:** `partial`

**Evidence**
- `backend/bots/documents_manager.py:87-120` supports document classification and extracted-text handling.
- `backend/models/document.py:25` defines `expires_at`.
- `backend/routes/documents_upload_routes.py:376-377`, `backend/routes/documents_upload_routes.py:441-445`, `backend/routes/documents_upload_routes.py:485` process expiration metadata and expiry checks.

## Claim 14
**Summary:** Predictive maintenance outputs from vehicle telemetry.

**Rating:** `partial`

**Evidence**
- `backend/bots/maintenance_dev.py:15` describes maintenance and auto-repair support.
- `backend/bots/maintenance_dev.py:88-89`, `backend/bots/maintenance_dev.py:192-227` implement `predict_failures`.
- `backend/routes/maintenance_dev_enhanced.py:24-64` exposes diagnostics, auto-repair, health history, and repair summary data.

**Gap Note**
- Predictive maintenance logic exists, but direct vehicle telemetry ingestion was not clearly confirmed in these files.

## Claim 15
**Summary:** Maintenance recommendations, fault-risk estimates, or fuel-efficiency analysis.

**Rating:** `partial`

**Evidence**
- `backend/bots/maintenance_dev.py:192-227` provides failure prediction outputs.
- `backend/routes/maintenance_dev_enhanced.py:34-64` exposes health and repair metrics.
- `backend/services/dispatch_service.py:325-335` calculates maintenance-oriented `risk_score` values and recommendations.

## Claim 16
**Summary:** Carrier credential verification using external data sources and carrier risk scoring.

**Rating:** `partial`

**Evidence**
- `backend/routes/carriers.py:61`, `backend/routes/carriers.py:157-158`, `backend/routes/carriers.py:319` expose verified-carrier status and verified filtering.
- `backend/models/carrier.py:29`, `backend/models/carrier.py:44` store insurance expiry and verification status.
- `backend/models/carrier_models.py:25-27`, `backend/models/carrier_models.py:42` model insurance and verification fields.
- `backend/services/dispatch_service.py:325-335` produces `risk_score` outputs and recommendations.

**Gap Note**
- Verification state and risk scoring exist, but direct external authority verification was not clearly located in the cited files.

## Claim 17
**Summary:** Carrier verification is repeated after onboarding.

**Rating:** `not clearly evidenced`

**Evidence**
- `backend/routes/carriers.py:157-158` supports repeated querying and filtering of verification state.
- `backend/models/carrier.py:29`, `backend/models/carrier.py:44` support persistent verification and expiry tracking.

**Gap Note**
- Re-verification cadence or scheduled post-onboarding checks were not clearly identified in code.

## Claim 18
**Summary:** Method of operating the logistics platform by decomposing workflows, assigning bots, storing intermediate results, and completing workflows through coordinated execution.

**Rating:** `partial`

**Evidence**
- `backend/routes/orchestration.py:41` exposes orchestration interfaces.
- `backend/routes/orchestration.py:391` assigns bots to operations.
- `backend/main.py:1263-1265` executes coordinated multi-bot tasks concurrently.
- `backend/bots/information_coordinator.py:3`, `backend/bots/information_coordinator.py:17` support shared intermediate coordination state.

## Claim 19
**Summary:** Coordinated execution includes freight matching, payments, documents, incidents, maintenance, or carrier verification.

**Rating:** `partial`

**Evidence**
- Freight: `backend/routes/freight_market_rates.py:94-168`, `backend/routes/freight_broker_canada.py:89-177`
- Payments: `backend/services/payment_service.py:73-172`, `backend/webhooks/payment_webhooks.py:170-458`
- Documents: `backend/app/api/v1/endpoints/documents.py:216-245`, `backend/routes/ocr_invoice_extract.py:36-60`
- Incidents: `backend/services/incident_tracker.py:47-77`, `backend/routes/safety_api.py:112-166`
- Maintenance: `backend/bots/maintenance_dev.py:192-227`, `backend/routes/maintenance_dev_enhanced.py:24-64`
- Carrier verification: `backend/routes/carriers.py:61-64`, `backend/models/carrier.py:29`, `backend/models/carrier.py:44`

## Claim 20
**Summary:** Non-transitory computer-readable medium storing instructions to perform the workflow method.

**Rating:** `strong`

**Evidence**
- The repository implements the claimed system as executable software modules and route handlers, including `backend/main.py`, `backend/services/payment_service.py`, `backend/routes/orchestration.py`, and related bot modules.

## Drafting Guidance
- Claims 1, 5, 6, 8, 9, and 20 currently have the strongest software support.
- Claims 2, 3, 4, 7, 10, 11, 12, 13, 14, 15, 16, 18, and 19 are supportable but broader than the code currently confirmed.
- Claim 17 should be narrowed or supported with additional implementation evidence before relying on it heavily.
