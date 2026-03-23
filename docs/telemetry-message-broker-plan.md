# Telemetry Message Broker Plan

## Goal
Before the national rollout, the telemetry ingestion path must be re-architected so that GPS/Smart WIM producers remain "producer-only" while autonomously scaling processing, caching, and reporting.

## 1. Processing boundary
- Introduce **Telemetry Workers** that consume from the message broker instead of allowing the ingest APIs to perform heavy work.
- Each worker is responsible for:
  - Rate limiting by device/tenant so bursty WIM feeds cannot overwhelm the pipeline.
  - Burst batching for high frequency updates (1–2 second WIM reports, GPS every 5s).
  - Stream processing (validation, enrichment, tagging, persistence).
  - Event-triggered reporting (load violation, compliance, digitally signed notifications).
- The ingest APIs simply push to the broker. Business logic, persistence, and reporting run asynchronously within the workers.

## 2. Redis Pub/Sub for live dashboard
- Replace the current `WebSocket → Postgres` read path with:

  ```
  Message Broker → Telemetry Workers → Redis Pub/Sub (live cache) → WebSocket Dashboard
  ```

- Dashboards subscribe to Redis channels instead of hitting Postgres directly.
- Historical writes persist asynchronously to PostgreSQL once workers validate/enrich the payloads.
- This separation reduces latency and database pressure while keeping WebSocket channels stable under load.

## 3. Message broker readiness
- A broker (Kafka or RabbitMQ) should sit between producers and consumers:
  ```
  Producer APIs
        ↓
  Message Broker
        ↓
  Telemetry Workers
        ↓
  Redis Cache + PostgreSQL
        ↓
  WebSocket Dashboard
  ```
- FastAPI's asynchronous framework and the existing logical separation (API | Processing | Storage | WebSocket) mean this broker can be added without a full system rebuild.
- ORM writes can be rerouted through the workers; WebSockets can switch to Redis Pub/Sub.
- The new workers will incorporate:
  - Rate Limiting
  - Batching
  - Stream Processing
  - Event-driven reporting (e.g., signed weight violations)

## 4. Action items before national approval
1. Implement producer-only ingest APIs so no heavy processing occurs before enqueuing.
2. Deploy Message Broker (Kafka/RabbitMQ) and connect Telemetry Workers.
3. Add Redis Pub/Sub for caching live telemetry; update WebSocket consumers to subscribe to it.
4. Build worker logic for rate limiting, batching, validation, enrichment, persistence, and event-triggered reporting.
5. Persist historical data to PostgreSQL asynchronously.

## 5. Monitoring & validation
- Capture metrics for rate limiting, worker throughput, Redis Pub/Sub latency, and PostgreSQL write lag.
- Run the ≥10,000 msg/sec load test (50,000 simulated devices at 5s intervals) after the worker/broker pipeline exists.

## 6. Deliverables
- Updated architecture diagram showing the broker + worker + Redis flow.
- Message broker implementation plan (timeline, resources, cost).
- WebSocket load test report covering the required KPIs.
- IoT throughput benchmark before/after the broker.
- Telemetry worker separation plan (producer-only ingestion, asynchronous processing).
- Schema/isolation migration plan for government tenants.

