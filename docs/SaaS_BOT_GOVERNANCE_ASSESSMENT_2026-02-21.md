# GTS SaaS Readiness & Bot Governance Assessment
**Date:** 2026-02-21
**Scope:** Internal codebase and runtime configuration snapshot
**Operating model:** Private/internal platform (not public self-service SaaS)

## 1) Executive Assessment
- **Current maturity (private SaaS mode):** Medium
- **Readiness for internal-team-only usage:** Good, with hardening actions
- **Readiness for public/open SaaS:** Not recommended in current state

## 2) Strengths
- Strong baseline auth and role model in backend with role hierarchy and guards.
- Registration disable mechanism exists and is enforced in auth register endpoint.
- Production guardrails exist for critical secret validation and CORS checks.
- Bot/email infrastructure is now centralized enough to support governance by bot identity.
- Password reset/login notification flows are implemented and operational.

## 3) Weaknesses
- Frontend still exposes public auth routes (`/register`, `/forgot-password`) even when operating as internal-only.
- Access control logic is partly fragmented between frontend guards and backend guards.
- Bot subscription endpoints allow caller-provided role/tier parameters in some routes (design risk).
- Route duplication/inconsistency in bot pages can create operational confusion and governance drift.

## 4) Security Vulnerabilities / Risk Items

### High
1. **Potential privilege/entitlement inference risk** in bot subscription APIs
   - Endpoints accept user-supplied `subscription_tier` and `user_role` in query for availability checks.
   - Impact: information disclosure about higher-tier bot availability and policy bypass in UI decisions.
   - Recommendation: ignore client-supplied role/tier and derive only from authenticated user profile server-side.

2. **Session staleness for role changes**
   - Role updates can require token refresh/re-login to apply immediately.
   - Impact: operational lockouts or stale authorization state.
   - Recommendation: enforce token version checks consistently and refresh auth meta on app bootstrap.

### Medium
3. **Internal-only mode not fully sealed in UX/API surface**
   - Public routes remain visible and some upgrade/subscription related endpoints remain available.
   - Recommendation: hide/disable non-internal flows at both frontend and backend layers.

4. **Governance definitions are distributed**
   - Bot states, routes, and identities are defined in multiple places.
   - Recommendation: single source of truth (registry) for bot metadata, status, ownership, and email identity.

## 5) Bot Governance Policy (Recommended)

### 5.1 Governance Principles
- **Least privilege:** every bot gets minimum required permissions only.
- **Identity clarity:** each bot has one canonical ID, owner, and mailbox policy.
- **Traceability:** all bot actions are auditable (who/what/when/result).
- **Human override:** high-risk actions require admin confirmation.
- **Fail-safe defaults:** unknown bot state => blocked execution.

### 5.2 Bot Lifecycle Policy
- States: `active`, `intelligence_mode`, `stopped`, `retired`.
- Only `active` can execute autonomous actions.
- `intelligence_mode` can analyze/recommend but no destructive write actions.
- `stopped` visible in panel but execution blocked.

### 5.3 Email Policy by Bot
- Use per-bot sender identity where configured.
- Shared mailbox only when explicitly documented (e.g., freight + mapleload).
- For bots without mailbox (e.g., GM, CTO maintenance), use controlled fallback and label source bot in message headers/body.

### 5.4 Access Policy
- Admin and super-admin privileges must be backend-enforced only (frontend is UX gate, not security gate).
- Periodic recertification of privileged users.
- Mandatory 2FA for all admin/super-admin accounts.

## 6) Internal-Only Operation Mode (Your Requirement)
Because subscriptions and open registration are frozen, platform should run as **Private Team Platform**:

1. Keep registration disabled in environment and backend enforcement.
2. Remove/disable upgrade/subscription self-service APIs from non-admin access.
3. Restrict CORS to internal domains only.
4. Restrict admin area to allowlisted team accounts/roles.
5. Keep invitation/provisioning user creation as admin-only workflow.

## 7) Priority Action Plan

### 0–7 days (Critical)
- Enforce server-side derivation of role/tier in bot subscription routes.
- Hide/remove public registration and upgrade UX for non-admin users.
- Enforce admin 2FA.
- Add explicit "internal-only mode" flag and centralized middleware behavior.

### 8–30 days (Stabilization)
- Build centralized Bot Registry (ID, owner, state, mailbox, permissions).
- Add immutable audit trail for bot actions and admin overrides.
- Add policy tests for role/tier access and bot-state enforcement.

### 30+ days (Governance Maturity)
- Add periodic governance review checklist.
- Add security scorecard dashboard (auth, bot state drift, failed access, email policy compliance).

## 8) References in Codebase
- Backend settings and production checks: `backend/config.py`
- Registration enforcement and auth flow: `backend/routes/auth.py`
- RBAC hierarchy helpers: `backend/security/rbac.py`
- Permission/role middleware: `backend/auth/rbac_middleware.py`
- Frontend feature gate behavior: `frontend/src/components/RequireFeature.jsx`
- Frontend route exposure (public auth pages): `frontend/src/App.jsx`
- Bot subscription API surface: `backend/routes/bots_subscription.py`

---
**Conclusion:** With your current decision (internal-team-only operation), the platform is viable after a focused hardening pass. Main gap is governance consistency and server-side policy enforcement on bot availability and entitlement logic.
