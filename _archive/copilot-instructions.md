# 🧭 Single Source of Truth

> ⚠️ CRITICAL: These rules are based on the current codebase and are NOT optional. Violating them has previously caused production-blocking bugs (blank screens, broken auth flow, unstable routing, and invalid hook call crashes). If a rule conflicts with the code, mark it as `Known gap / TODO`—do not assume or invent behavior.

- **Router EN:**
  - Backend: `backend/main.py` (EN `_try_import_router`)
  - Frontend: EN Router EN `frontend/src/routes/AppRoutes.jsx` EN.
- **AuthContext EN:**
  - `frontend/src/context/AuthContext.jsx` (EN)
- **axiosClient EN:**
  - `frontend/src/api/axiosClient.js` (EN HTTP EN)

# ⚠️ Known Pitfalls

### Hard rules (must never be violated)
- Never call any React Hook outside a React function component or a custom hook (a function whose name starts with `use*`).
- Never create or introduce a second Router, AuthContext, or Provider for the same purpose. Always use the documented Single Source of Truth.
- Never load or use entitlements before authentication is fully resolved (token persisted + `/auth/me` completed successfully).


- **Invalid hook call:**
  - EN: EN hook EN React component EN AuthContext/Provider.
  - EN AuthContext EN Provider EN.

**Invalid hook call prevention**
- Hooks must only run inside components or custom hooks.
- Do not call `useAuth()` (or any hook) inside service files, axios client, router config factories, or `init()` functions.
- If you need auth data in a utility function, pass it as an argument (e.g., `token`, `userId`) instead of using hooks.

#
# Pitfall: Loading entitlements too early
If entitlements are requested before auth is resolved, the UI can flicker, route guards can misfire, and React can crash during initialization.

**Rule**
- Entitlements must only load after `isAuthenticated === true` AND after `/auth/me` has completed and user state is set.
- **React duplicate:**
  - EN: EN React EN node_modules (EN npm link EN).
  - EN: EN ReactEN symlink/local package usage.
- **Vite Fast refresh export incompatibility:**
  - EN export default/EN React component EN.
  - EN: EN dev server EN.

# 🔐 Auth Contract
#
## Auth Flow Timeline (Frontend)
1) User submits login form
2) `POST /auth/token` (Content-Type: `application/x-www-form-urlencoded`)
3) Persist `access_token` (storage per project rules)
4) `GET /auth/me` using `Authorization: Bearer <token>`
5) Set auth state (`user`, `isAuthenticated`, `isLoading=false`)
6) Load entitlements (only after step 5 succeeds)
7) Route guards allow access to protected routes

- **Request Example:**
  - Endpoint: `POST /auth/token`
  - Content-Type: `application/x-www-form-urlencoded`
  - Payload:
    ```
    email=tester@gts.com&password=123456
    ```
- **Response Example:**
    ```json
    {
      "access_token": "eyJhbGciOi...",
      "token_type": "bearer",
      "user": {
        "id": 1,
        "email": "tester@gts.com",
        "role": "admin",
        "full_name": "Test User"
      }
    }
    ```
- **Content-Type:**
  - EN `application/x-www-form-urlencoded` EN`application/json` EN.

# ✅ Do / 🚫 Don’t for Agents

### Handling uncertainty
- If you are not 100% sure a behavior exists in the code, mark it as `Known gap / TODO` and do not document it as a fact.

**Do:**
- EN.
- EN AuthContext ENaxiosClient ENRouter EN).
- EN: EN AuthContextEN).

**Don’t:**
- EN Context EN Router EN Folder EN.
- EN.
- EN.

# GTS Logistics – AI Coding Agent Instructions

## 🚚 Big Picture

- **Modular FastAPI backend** (see `backend/`) and **React (Vite) frontend** (`frontend/`)
- **Bot Operating System (BOS):** Orchestrates AI bots for freight, finance, docs, and support
- **Real-time**: WebSocket `/api/v1/ws/live` for live bot/command events (see `backend/routes/ws_routes.py`)
- **Database**: PostgreSQL, async SQLAlchemy, migrations via Alembic

## 🏗️ Key Patterns & Conventions

- **Session Management:** Always use `wrap_session_factory()` from `backend/database/session.py` for DB sessions (never use async generators directly)
- **Router Mounting:** Use `_try_import_router()` in `backend/main.py` for optional/conditional routers
- **Role-based Rate Limiting:** `/api/v1/commands/human` is rate-limited by user role (see `backend/bots/rate_limit.py`)
- **Bot Registration:** Add new bots in `backend/bots/`, register in `config/bots.yaml`, and expose via `/api/v1/bots` endpoints
- **Frontend Auth:** JWT stored in `localStorage` as `access_token`/`token`, injected by `frontend/src/api/axiosClient.js`
- **Role Normalization:** Keep frontend (`utils/authStorage.js`) and backend (`backend/ai/policy.py`) role logic in sync
- **WebSocket Subscriptions:** Subscribe to `bots.*` and `commands.*` channels for live updates

## 🔑 Auth & Security

- **Login:** POST `/auth/token` with `email` + `password` (not `username`)
- **Token Storage:** JWT in `localStorage` (`access_token`/`token`)
- **AuthContext:** Use `useAuth()` from `frontend/src/context/AuthContext.jsx` for user/session state
- **RequireAuth:** Protect pages/components with `<RequireAuth requiredRole="admin" />`

## 🤖 BOS (Bot Operating System)

- **Endpoints:**
  - `GET /api/v1/bots` – List bots
  - `GET /api/v1/bots/history` – Execution history
  - `GET /api/v1/bots/stats` – Aggregate stats
  - `POST /api/v1/commands/human` – Run NL command (rate-limited)
  - `POST /api/v1/bots/{name}/pause` – Pause automation
- **Bot Example:** See `backend/bots/os.py` and `backend/routes/bot_os.py` for orchestration logic
- **Frontend Dashboard:** `frontend/src/pages/admin/BotOS.jsx` (real-time, WebSocket-driven)

## 🗄️ Database & Migrations

- **Session:** Use `wrap_session_factory()` for all DB access
- **Migrations:**
  - `python -m alembic -c backend\alembic.ini heads`
  - `python -m alembic -c backend\alembic.ini merge -m "merge heads" <head1> <head2>`
  - `python -m alembic -c backend\alembic.ini upgrade head`
- **URL Normalization:** All DB URLs auto-converted to `postgresql+asyncpg://...` with SSL (see `backend/database/config.py`)

## ⚡ Developer Workflows

- **Start backend:** `uvicorn backend.main:app --reload`
- **Start frontend:** `npm run dev --prefix frontend`
- **Run tests:** `pytest backend/tests/test_bots_os.py -v`
- **Debug:** Check logs for `[startup] bot_os started` and DB DSN

## 🧩 File Reference

| Purpose                | Path                                      |
|------------------------|-------------------------------------------|
| Main app entry         | backend/main.py                           |
| BOS orchestrator       | backend/bots/os.py                        |
| BOS API routes         | backend/routes/bot_os.py                  |
| WebSocket hub          | backend/routes/ws_routes.py               |
| WS manager             | backend/bots/ws_manager.py                |
| DB session wrapper     | backend/database/session.py               |
| Rate limiting          | backend/bots/rate_limit.py                |
| Frontend API client    | frontend/src/api/axiosClient.js           |
| Auth context           | frontend/src/context/AuthContext.jsx      |
| BOS dashboard (UI)     | frontend/src/pages/admin/BotOS.jsx        |

## 📝 Onboarding Checklist

1. Read: `README.md`, `BOS_SYSTEM_INDEX.md`, `BOS_DEPLOYMENT_VERIFICATION.md`
2. Explore: `backend/main.py`, `backend/bots/os.py`, `frontend/src/pages/admin/BotOS.jsx`
3. Test: `pytest backend/tests/test_bots_os.py`
4. Extend: Add new bot via `backend/bots/` + `config/bots.yaml`

---
For more, see `BOS_IMPLEMENTATION_SUMMARY.md` and `BOS_QUICK_REFERENCE.md`.
| BOS routes | `backend/routes/bot_os.py` | `/api/v1/bots`, `/api/v1/commands/human` |

| WebSocket hub | `backend/routes/ws_routes.py` | `/api/v1/ws/live` endpoint |

