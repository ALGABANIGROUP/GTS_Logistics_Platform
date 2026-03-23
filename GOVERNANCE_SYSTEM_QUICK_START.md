# Bot Governance System - Quick Start Guide

## Overview
The Bot Governance System provides approval workflows, security validation, and lifecycle management for all bots in GTS. Data persists to PostgreSQL with real-time WebSocket updates to the admin UI.

## Architecture
- **Backend**: FastAPI routes at `/api/v1/governance/*` (admin-only)
- **Database**: PostgreSQL tables (`governance_bots`, `governance_approvals`, `governance_activity`)
- **Frontend**: Admin UI at `/admin/governance` with live WebSocket updates
- **Migration**: Alembic revision `a1c9e3f0`

## API Endpoints

### Register Bot
```http
POST /api/v1/governance/bots/register
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "bot_id": "sales_bot_001",
  "name": "sales_bot",
  "version": "1.0.0",
  "description": "Sales automation bot",
  "author": "system",
  "created_at": "2026-01-07T18:00:00.000Z",
  "updated_at": "2026-01-07T18:00:00.000Z",
  "required_permissions": [
    {
      "id": "perm_001",
      "name": "read_customers",
      "description": "Read customer data",
      "resource": "customers",
      "action": "read",
      "risk_level": 2
    }
  ],
  "external_apis": [],
  "database_access": ["customers", "leads"],
  "constraints": {},
  "code_hash": "abc123def456",
  "config_hash": "xyz789uvw012",
  "signature": null
}
```

**Response:**
```json
{
  "success": true,
  "bot_id": "sales_bot_001",
  "status": "under_review",
  "next_step": "waiting for security team review"
}
```

### Approve Bot
```http
POST /api/v1/governance/bots/{bot_id}/approve
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "approver": "admin@gts.local",
  "comments": "Approved after security review"
}
```

**Response (after 2 approvals):**
```json
{
  "success": true,
  "message": "bot approved",
  "status": "approved",
  "activation_keys": {
    "key_id": "ad008d62d9269741ad66bc551a9d9836"
  },
  "next_steps": [
    "activate bot",
    "configure monitoring",
    "production testing"
  ]
}
```

### Activate Bot
```http
POST /api/v1/governance/bots/{bot_id}/activate
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "environment": "production"
}
```

**Response:**
```json
{
  "success": true,
  "message": "bot activated in production",
  "activation_id": "84f1903aff22e54f2699517687c7efe5",
  "monitoring_dashboard": "https://monitoring.company.com/bots/sales_bot_001",
  "access_credentials": {
    "token": "e9bb17e2ab0c4387a43d18f12ad8d95a6d3e9c25e90d2fb7a468dcb0973ef528"
  }
}
```

### Get Bot Status
```http
GET /api/v1/governance/bots/{bot_id}
Authorization: Bearer {admin_token}
```

**Response:**
```json
{
  "ok": true,
  "bot_id": "sales_bot_001",
  "name": "sales_bot",
  "status": "active",
  "approvals": [
    {
      "approver": "operations@gts.local",
      "role": "security_team",
      "decision": "approved",
      "comments": "Second approval",
      "timestamp": "2026-01-07T18:59:40.618739Z"
    }
  ],
  "activity_log": [
    {
      "action": "activation",
      "environment": "production",
      "timestamp": "2026-01-07T19:00:06.280278Z",
      "details": {
        "message": "bot activated in production"
      }
    }
  ]
}
```

### List All Bots
```http
GET /api/v1/governance/bots
Authorization: Bearer {admin_token}
```

**Response:**
```json
{
  "ok": true,
  "count": 1,
  "bots": [
    {
      "bot_id": "sales_bot_001",
      "name": "sales_bot",
      "status": "active",
      "registered_at": "2026-01-07T18:58:14.837528Z",
      "approvals": 2
    }
  ]
}
```

## PowerShell Quick Test

```powershell
# Get admin dev token
$base='http://127.0.0.1:8000'
$dev="$base/auth/dev-token?role=admin`&secret=dev-secret"
$token=(Invoke-RestMethod -Uri $dev).access_token

# Register bot
$manifest = @{
  bot_id = "sales_bot_001"
  name = "sales_bot"
  version = "1.0.0"
  description = "Sales automation bot"
  author = "system"
  created_at = (Get-Date).ToUniversalTime().ToString("o")
  updated_at = (Get-Date).ToUniversalTime().ToString("o")
  required_permissions = @(
    @{
      id = "perm_001"
      name = "read_customers"
      description = "Read customer data"
      resource = "customers"
      action = "read"
      risk_level = 2
    }
  )
  external_apis = @()
  database_access = @("customers", "leads")
  constraints = @{}
  code_hash = "abc123def456"
  config_hash = "xyz789uvw012"
  signature = $null
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri ($base + '/api/v1/governance/bots/register') `
  -Method Post `
  -Headers @{ Authorization=("Bearer " + $token); 'Content-Type'='application/json' } `
  -Body $manifest

# Approve bot (first approval)
$payload1 = @{ approver = "admin@gts.local"; comments = "First approval" } | ConvertTo-Json
Invoke-RestMethod -Uri ($base + '/api/v1/governance/bots/sales_bot_001/approve') `
  -Method Post `
  -Headers @{ Authorization=("Bearer " + $token); 'Content-Type'='application/json' } `
  -Body $payload1

# Approve bot (second approval - meets threshold)
$payload2 = @{ approver = "operations@gts.local"; comments = "Second approval" } | ConvertTo-Json
Invoke-RestMethod -Uri ($base + '/api/v1/governance/bots/sales_bot_001/approve') `
  -Method Post `
  -Headers @{ Authorization=("Bearer " + $token); 'Content-Type'='application/json' } `
  -Body $payload2

# Activate bot
$activate = @{ environment = "production" } | ConvertTo-Json
Invoke-RestMethod -Uri ($base + '/api/v1/governance/bots/sales_bot_001/activate') `
  -Method Post `
  -Headers @{ Authorization=("Bearer " + $token); 'Content-Type'='application/json' } `
  -Body $activate

# List all bots
Invoke-RestMethod -Uri ($base + '/api/v1/governance/bots') `
  -Headers @{ Authorization=("Bearer " + $token) } | ConvertTo-Json -Depth 5

# Get bot details
Invoke-RestMethod -Uri ($base + '/api/v1/governance/bots/sales_bot_001') `
  -Headers @{ Authorization=("Bearer " + $token) } | ConvertTo-Json -Depth 5
```

## Bot Lifecycle States

1. **under_review** → Bot registered, awaiting approvals
2. **approved** → Minimum approvals received (default: 2)
3. **active** → Activated in production environment
4. **suspended** → Temporarily disabled
5. **deprecated** → Marked for retirement
6. **archived** → Historical record only

## Permission Matrix

Bots must match a registered name in the permission matrix (`backend/core/governance/bot_governance.py`):

- `sales_bot`: customers, leads, deals, products (read, create, update)
- `security_bot`: logs, users, sessions, alerts (read, monitor, alert)
- `finance_bot`: invoices, payments, transactions (read, create, update, export)

**Note**: Bots not in the matrix will be rejected at registration with "bot not found in matrix" error.

## Frontend Admin UI

Navigate to `/admin/governance` (requires admin role):

- View all bots with status badges
- Approve bots (increments approval count)
- Activate approved bots
- Real-time updates via WebSocket subscription to `governance.*` channels
- Connection status indicator

## Database Schema

### governance_bots
- `bot_id` (PK): Unique bot identifier
- `name`: Bot name (must match permission matrix)
- `version`: Semantic version
- `status`: Current lifecycle state
- `approvals_count`: Number of approvals received
- `manifest_json`: Permissions, APIs, DB access (JSON)
- `code_hash`, `config_hash`, `signature`: Integrity verification
- `created_at`, `updated_at`: Timestamps

### governance_approvals
- `id` (PK): Auto-increment
- `bot_id` (FK): References governance_bots
- `approver`: Email or identifier
- `role`: Approver role (security_team, operations, etc.)
- `decision`: "approved" (or future: "rejected")
- `comments`: Free text notes
- `created_at`: Approval timestamp

### governance_activity
- `id` (PK): Auto-increment
- `bot_id` (FK): References governance_bots
- `action`: "activation", "suspension", etc.
- `environment`: "development", "staging", "production"
- `details`: JSON metadata
- `created_at`: Action timestamp

## WebSocket Events

The governance system broadcasts events on these channels:

- `governance.bots.register` → Bot registered
- `governance.bots.approve` → Bot approval recorded
- `governance.bots.activate` → Bot activated

Frontend subscribes via:
```javascript
ws.send(JSON.stringify({
  type: "subscribe",
  channel: "governance.*"
}));
```

## Migration

Apply the governance tables migration:
```bash
python -m alembic -c backend\alembic.ini upgrade a1c9e3f0
```

If multiple heads exist, merge first:
```bash
python -m alembic -c backend\alembic.ini heads
python -m alembic -c backend\alembic.ini merge -m "merge heads" <head1> <head2>
python -m alembic -c backend\alembic.ini upgrade head
```

## Security Notes

- All governance endpoints require admin role (`admin`, `super_admin`, `system_admin`, `owner`)
- Dev tokens in development mode use `.invalid` TLD email to bypass user checks
- Production tokens must map to active, non-deleted admin users
- WebSocket events are broadcast globally; RBAC on subscription recommended for future

## Troubleshooting

### "User is deleted" error
- Development: Use dev token endpoint with `.invalid` email (fixed in main.py)
- Production: Ensure admin user exists and is_deleted=false

### "bot not found in matrix" error
- Bot name must match a key in `BotGovernanceSystem._load_permission_matrix()`
- Currently supported: `sales_bot`, `security_bot`, `finance_bot`

### Timeout on API calls
- Check backend logs for DB connection issues
- Verify PostgreSQL is reachable (see DATABASE_URL in .env)
- Increase `-TimeoutSec` in PowerShell or axios timeout

### Migration conflicts
- Multiple heads are normal in this repo; merge them instead of forcing single head
- Avoid `alembic stamp head` unless DB state is known-good

## Related Files

- Backend core: `backend/core/governance/bot_governance.py`
- API routes: `backend/routes/bot_governance_routes.py`
- Models: `backend/models/governance.py`
- Migration: `backend/alembic_migrations/versions/a1c9e3f0_add_governance_tables.py`
- Frontend client: `frontend/src/api/governanceClient.js`
- Frontend UI: `frontend/src/pages/admin/Governance.jsx`
- Documentation: `docs/operations/bot_governance_and_deployment.md`

---

**Last Updated**: 2026-01-07  
**Status**: Production-ready with DB persistence and WebSocket live updates
