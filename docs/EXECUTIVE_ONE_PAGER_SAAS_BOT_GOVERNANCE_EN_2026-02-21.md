# Executive One-Pager
## GTS Internal Platform Readiness + Bot Governance
**Date:** 2026-02-21

## Executive Decision
- **Approved operating model:** Internal platform for company team only.
- **Current state:** Good readiness for internal operation after targeted governance hardening.
- **Not recommended** to open as public SaaS before closing policy gaps listed below.

## Overall Picture (Traffic Light)
- **Security baseline:** 🟢 Good
- **Roles and permissions:** 🟡 Good, needs stricter server-side unification
- **Bot governance:** 🟡 Partially advanced, needs one central source of truth
- **Internal-only compliance:** 🟡 Requires complete closure of public-facing routes

## Key Strengths
1. Existing authentication and role framework is scalable.
2. Registration disablement is supported and enforced server-side.
3. Important production security controls are in place (keys/CORS/security options).
4. Bot email identity was improved with bot-specific sender mapping.

## Key Weaknesses/Risks
1. Some public SaaS surfaces are still visible (UI/API).
2. Bot definitions and policies are distributed across multiple sources.
3. Some access outcomes are affected by stale session state (`token staleness`).
4. Bot subscription routes must derive `role/tier` from server identity only.

## Critical Risks (Top 3)
1. **Policy Enforcement Drift:** client-supplied `tier/role` in some bot flows.
2. **Stale Authorization:** role changes are not always reflected immediately without token/session refresh.
3. **Internal-Only Gap:** incomplete closure of public routes for internal-only operating model.

## Bot Status (Operational Release)
- **Total bots:** 18
- **Active:** 15
- **Intelligence Mode:** 2
- **Stopped:** 1
- **Email policy:** Enabled by bot identity with documented shared/fallback cases.

## Proposed Operating Decision
- **Continue internal operation** with formal Internal-Only Mode (technical + operational).
- **Block any external opening** until phased hardening plan is complete.

## 30-Day Plan (Condensed)
### First 7 days
- Enforce server-side role/tier derivation in bot APIs.
- Fully close/hide public `register/upgrade` flows.
- Enforce 2FA for `Admin/Super Admin` accounts.

### Days 8–30
- Build centralized Bot Registry (`id/state/email/owner/permissions`).
- Unify access policy across frontend and backend.
- Enable comprehensive audit trail for sensitive bot actions.

## Management KPIs
- Sensitive routes protected server-side = **100%** (target).
- Admin accounts with 2FA enabled = **100%** (target).
- Bot state-policy violations = **0** per month (target).

---
**Detailed report reference:**
- `docs/DETAILED_SAAS_BOT_GOVERNANCE_REPORT_EN_2026-02-21.md`
