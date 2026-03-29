# GTS Integration Profile

Last updated: 2026-03-28
Owner team: Integrations and Operations
Status: Draft

## Purpose
This profile defines a standard integration contract for external systems connected to GTS.
Use it for load boards, carriers, payment gateways, tracking providers, and webhook partners.

## Integration Identity
- Integration name: GTS External Integration
- Integration id: gts-external-integration
- Provider type: loadboard | carrier | payment | tracking | webhook
- Business owner: Operations Manager
- Technical owner: Backend Integrations Team
- Support contact: support@gabanistore.com
- Escalation contact: operations@gabanilogistics.com

## Scope and Use Cases
- Primary use case: Load discovery and shipment lifecycle synchronization
- Secondary use case: Finance and invoice lifecycle updates
- Inbound data flow: Provider -> GTS webhook/API
- Outbound data flow: GTS -> Provider API
- Critical entities:
  - Loads
  - Shipments
  - Tracking events
  - Invoices
  - Carrier updates

## Environments
| Environment | Base URL | Auth method | Notes |
|---|---|---|---|
| dev | https://dev-api.gtsdispatcher.com | API key or OAuth2 | Sandbox for internal testing |
| staging | https://staging-api.gtsdispatcher.com | API key or OAuth2 | Pre-production validation |
| prod | https://api.gtsdispatcher.com | API key or OAuth2 | Live production traffic |

## Authentication and Security
- Authentication type: API key or OAuth2 Client Credentials
- Credential storage: environment variables or secret manager
- Required secrets:
  - PROVIDER_API_KEY
  - PROVIDER_API_SECRET
  - PROVIDER_CLIENT_ID
  - PROVIDER_CLIENT_SECRET
  - PROVIDER_WEBHOOK_SECRET
- Token refresh strategy:
  - Refresh 5 minutes before expiry
  - Retry once on 401 then force refresh
- Transport security:
  - HTTPS only
  - TLS 1.2+
- Request integrity:
  - HMAC signature verification for webhooks
  - Timestamp replay window: 5 minutes

## API Contract
### Core Endpoints
- Health check: `GET /health`
- List loads: `GET /loads`
- Get shipment: `GET /shipments/{id}`
- Update shipment: `PATCH /shipments/{id}`
- Acknowledge webhook: `POST /webhooks/ack`

### Request Policy
- Timeout:
  - connect timeout: 5s
  - read timeout: 30s
- Retry policy:
  - max retries: 3
  - backoff: exponential
  - retry on: 429, 500, 502, 503, 504
- Idempotency:
  - send idempotency key for create/update operations

### Rate Limits
| Provider Type | Default Rate Limit | Notes |
|---|---|---|
| loadboard | 60 req/min | 1 request per second |
| carrier | 120 req/min | Burst up to 2 requests per second |
| payment | 30 req/min | Lower limit for financial operations |
| tracking | 300 req/min | Higher limit for real-time updates |
| webhook | 500 req/min | High volume from external systems |

- Internal safety limit: 80 percent of provider limit
- Throttling strategy: token bucket with per-route caps

## Webhook Profile
- Webhook endpoint: `/api/v1/integrations/webhook/{provider}`
- Event types:
  - shipment.created
  - shipment.picked_up
  - shipment.in_transit
  - shipment.delayed
  - shipment.delivered
  - shipment.exception
- Validation checks:
  - signature required
  - timestamp required
  - unique event id required
- Dead letter strategy:
  - after 3 failed retries send to DLQ
  - alert on DLQ size > threshold

## Data Mapping
- External load id -> internal shipment external_ref
- External carrier id -> internal carrier.external_id
- External event timestamp -> internal event_time_utc
- External location payload -> internal tracking_points

## Reliability and SLA
- Availability target: 99.9 percent
- Maximum event lag: 2 minutes
- Maximum API sync lag: 5 minutes
- Recovery target:
  - RTO: 30 minutes
  - RPO: 5 minutes

## Monitoring and Alerts
- Required metrics:
  - request_count
  - error_rate
  - p95_latency
  - webhook_success_rate
  - retry_count
  - dlq_depth
- Alert thresholds:
  - error_rate > 3 percent for 5 minutes
  - p95_latency > 2 seconds for 10 minutes
  - webhook_success_rate < 98 percent for 15 minutes
  - dlq_depth > 50 messages

## Compliance and Audit
- Log retention: 90 days minimum
- PII handling: mask sensitive fields in logs
- Audit trail fields:
  - integration_id
  - request_id
  - event_id
  - actor
  - timestamp
  - action

## Change Management
- Versioning strategy: semantic versioning for integration adapters
- Breaking changes process:
  - publish change notice
  - provide migration window
  - run dual-write or compatibility mode if possible
- Rollback plan:
  - feature flag per provider
  - fallback to previous adapter version

## Go-Live Checklist
- [ ] Credentials configured for target environment
- [ ] Health endpoint validated
- [ ] API auth validated
- [ ] Webhook signature validation tested
- [ ] Retry and timeout behavior tested
- [ ] Rate-limit handling tested
- [ ] Data mapping validated with sample payloads
- [ ] Monitoring dashboards created
- [ ] Alert rules enabled
- [ ] Runbook documented and shared

## Provider-Specific Block
Copy and complete this block for each provider.

### Provider Profile Template
- Provider name:
- Provider id:
- Base URL:
- Auth type:
- Supported endpoints:
- Supported webhook events:
- Rate limits:
- Known constraints:
- Required fields:
- Optional fields:
- Data freshness expectation:
- Test account details:
- Production cutover date:
- Rollback owner:
- Additional notes: 