# GTS Logistics Platform

GTS Logistics is a modular freight operations platform with AI-assisted workflows for finance, payment processing, partner management, carrier operations, shipper operations, safety, and orchestration.

## Current Project Snapshot

- Documentation refresh date: **2026-03-21**
- Documentation version: **2026.03.21-docs**
- Frontend bot registry: **21 bots**, **21 active**
- New payment surfaces: **Payment Gateway Dashboard**, **SUDAPAY Payment Gateway**, **AI Finance Bot**
- Partner Manager status: **Active** and routed through `/ai-bots/partner-management`
- Operations additions: **Carriers** and **Shippers** workspaces with integrated frontend services
- Verified frontend build: **`npm run build` passed**
- Verified backend doc-related syntax checks: **`python -m py_compile backend/ai/bot_subscription_manager.py` passed**

## Key Active Routes

- `/ai-bots/hub`
- `/ai-bots/payment`
- `/ai-bots/sudapay`
- `/ai-bots/finance`
- `/ai-bots/partner-management`
- `/ai-bots/carriers/*`
- `/ai-bots/shippers/*`
- `/payments/:invoiceId`
- `/payments/history`

## Latest Confirmed Changes Included In This Refresh

- Added the shared frontend bot registry and cleaned the hub display.
- Added and activated **Payment Gateway Dashboard** as a distinct bot entry.
- Kept **SUDAPAY** as its own payment-focused bot view.
- Activated **AI Partner Manager** across registries, dashboards, and routing.
- Added payment and finance summary helpers used by the dashboard.
- Added/update carrier and shipper frontend workspaces and service integrations.
- Updated bot alias handling so payment and partner routes resolve consistently.

## Platform Highlights

- Unified AI bot hub and routed bot control pages
- Active payment stack with `Payment Gateway Dashboard`, `SUDAPAY`, and `AI Finance Bot`
- Active `AI Partner Manager`
- Carriers and Shippers workspaces with connected frontend services
- Finance and payment summaries derived from real invoice and payment feeds

## Where To Start

- `00_READ_ME_FIRST.md`
- `AI_BOTS_PANEL_INDEX.md`
- `PAYMENT_GATEWAY_INDEX.md`
- `API_CONNECTIONS_DOCUMENTATION_INDEX.md`

## Standard Local Commands

```bash
# frontend
cd frontend
npm install
npm run dev
npm run build

# backend
python -m uvicorn backend.main:app --reload
```

## Maintainer Note

This README was refreshed to match the current codebase state on **2026-03-21**.
