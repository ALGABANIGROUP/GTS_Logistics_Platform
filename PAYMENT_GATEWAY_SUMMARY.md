# Payment Gateway Summary

        Updated: **2026-03-21**
        Documentation version: **2026.03.21-docs**

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

        ## Payment System Scope

The payment system now has three distinct layers:

1. `AI Finance Bot` for finance workflows and invoice operations
2. `SUDAPAY Payment Gateway` for gateway-specific payment history and gateway state
3. `Payment Gateway Dashboard` for integrated payment operations and bot navigation

## Current Payment Facts

- Payments are invoice-driven and use `/payments/:invoiceId`
- Payment history is exposed through `/api/v1/payments/user/history`
- The frontend derives dashboard statistics from live payment history and invoice data
- Payment and finance dashboards are intentionally separate views

## Current Security Position

- Encrypted transport is assumed in deployment
- Gateway tokenization is expected at the provider boundary
- Webhook verification remains part of the production readiness checklist

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

        This document was refreshed in English to match the latest confirmed project changes as of **2026-03-21**.
