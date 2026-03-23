# Subscription System and Bot/Email Division

## Overview

A comprehensive system has been developed for dividing bots and emails based on subscription plans, with support for two email options:
- **BYOD (Bring Your Own Domain)**: The client uses their own domain
- **Managed Domain**: The platform manages emails from its domain

## Added Files

### 1. `config/plans.json`
Contains definitions for the four subscription plans:
- `loadboard_basic`: Basic load board
- `tms_pro`: Advanced transport management system
- `unified_pro`: Advanced unified system
- `enterprise`: Enterprises

### 2. `config/roles.json`
Contains role definitions with permissions:
- `owner`: Owner (all permissions)
- `admin`: System administrator
- `operations_manager`: Operations manager
- `dispatcher`: Transport coordinator
- `finance`: Finance
- `viewer`: Viewer
- `system_admin`: Technical system administrator

### 3. `backend/modules/ai-bots/registry/bots-registry.js`
Unified bot registry with:
- 10 user bots
- 7 system bots
- 1 specialized bot (MapleLoad AI)
- using `email_local_part` instead of fixed email

### 4. `backend/unified_bot_system.py`
Unified system for managing Bots with key unification and report management.

### 5. `scripts/create_subscription_tables.sql`
Complete database schema with tables:
- `tenants`: tenants
- `plans`: subscription plans
- `users`: users
- `roles`: roles
- `ai_bots`: Bots
- `bot_policies`: bot policies
- `bot_runs`: bot run logs
- `tenant_email_config`: email settings
- `bot_email_identities`: bot email identities
- `email_logs`: email logs

### 6. `scripts/seed_subscription_data.py`
Script to load initial data.

## How to Divide

### Bots by Plans

| The Bot | Loadboard Basic | TMS Pro | Unified Pro | Enterprise |
|-------|----------------|---------|-------------|------------|
| Finance Bot | ❌ | ✅ | ✅ | ✅ |
| Freight Broker | ✅ | ✅ | ✅ | ✅ |
| Documents Manager | ✅ | ✅ | ✅ | ✅ |
| Customer Service | ✅ | ✅ | ✅ | ✅ |
| Strategy Advisor | ❌ | ❌ | ✅ | ✅ |
| Marketing Manager | ✅ | ✅ | ✅ | ✅ |
| Safety Manager | ❌ | ✅ | ✅ | ✅ |
| Sales Team | ✅ | ✅ | ✅ | ✅ |
| Dispatcher | ❌ | ✅ | ✅ | ✅ |
| Operations Manager | ❌ | ✅ | ✅ | ✅ |
| General Manager | ❌ | ❌ | ❌ | ✅ |
| System Admin | ❌ | ❌ | ❌ | ✅ |
| Dev Maintenance | ❌ | ❌ | ❌ | ✅ |
| Security Manager | ❌ | ❌ | ❌ | ✅ |
| Partner Manager | ❌ | ❌ | ❌ | ✅ |
| Information Coordinator | ❌ | ❌ | ❌ | ✅ |
| MapleLoad AI | ❌ | ❌ | ✅ | ✅ |

### Email by Plans

| The Feature | Loadboard Basic | TMS Pro | Unified Pro | Enterprise |
|--------|----------------|---------|-------------|------------|
| Email Core (Logs) | ✅ | ✅ | ✅ | ✅ |
| Email Outbound | ✅ | ✅ | ✅ | ✅ |
| Email Inbound | ❌ | ✅ | ✅ | ✅ |
| BYOD SMTP | ❌ | ✅ | ✅ | ✅ |
| Managed Domain | ❌ | ❌ | ✅ | ✅ |
| Email Aliases | ❌ | ❌ | ✅ | ✅ |
| Email Mailboxes | ❌ | ❌ | ❌ | ✅ |
| Custom Domain | ❌ | ❌ | ❌ | ✅ |

## Email Options

### 1. BYOD (Bring Your Own Domain)
- Client provides their own SMTP/IMAP
- Platform sends from client's domain
- Suitable for large companies and compliance

### 2. Managed Domain
- Platform manages emails from `gabanilogistics.com`
- Create aliases or mailboxes
- Faster setup

## Email Generation

### For Bots
```javascript
// in bots-registry.js
email_local_part: "finance"

// Generate final email
if (tenant.email_mode === 'byod') {
  email = `finance@${tenant.domain}`;
} else {
  email = `finance@${tenant.slug}.gabanilogistics.com`;
}
```

### For Users
```javascript
// Aliases for basic plans
user@${tenant.slug}.gabanilogistics.com

// Mailboxes for advanced plans
user@gabanilogistics.com
```

## Implementation

### 1. Run Database
```bash
psql -d gts_db -f scripts/create_subscription_tables.sql
```

### 2. Load Initial Data
```bash
cd scripts
python seed_subscription_data.py
```

### 3. Update Application
- Update `auth-middleware.js` to check features
- Update `router.js` to check permissions
- Update `PortalDashboard.vue` to display available Bots

## Permission Verification

### In Backend
```javascript
// Check features
if (!req.tenant.features.includes('finance_bot.access')) {
  return res.status(403).json({ error: 'Feature not available in your plan' });
}

// Check roles
if (!req.user.permissions.includes('manage_shipments')) {
  return res.status(403).json({ error: 'Insufficient permissions' });
}
```

### In Frontend
```javascript
// Check features
const hasFeature = tenantStore.hasFeature('finance_bot.access');

// Check permissions
const hasPermission = authStore.hasPermission('manage_shipments');
```

## Next Steps

1. **Test System**: Run tests to ensure segmentation works
2. **Update Interface**: Modify UI to show Bots according to plan
3. **Setup Email**: Configure SMTP for managed emails
4. **Documentation**: Add user guide for plans and features
5. **Support**: Add plan upgrade system

## Important Notes

- Bots work even without email (shows "Email not configured")
- Emails are generated dynamically based on tenant settings
- Segmentation relies on `required_features` in bot_policies
- Limits are enforced at tenant and user level
- Records are saved for review and audit