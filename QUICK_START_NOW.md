# Quick Start Now

Use this guide if you need the fastest path to running and validating the current project state.

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

## First Validation Steps

1. Open `/ai-bots/hub`
2. Open `/ai-bots/payment`
3. Open `/ai-bots/sudapay`
4. Open `/ai-bots/finance`
5. Open `/ai-bots/partner-management`

## Expected Current State

- Bot hub renders from the shared frontend registry
- Payment Gateway Dashboard opens as its own bot
- SUDAPAY opens as a distinct payment-focused view
- Partner Manager is active
- Frontend build succeeds
