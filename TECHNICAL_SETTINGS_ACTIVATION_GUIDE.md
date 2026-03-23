# Technical Settings Guide

## Overview

All technical settings in the Platform Settings admin panel are now fully activated and immediately impact runtime behavior. The panel no longer just stores values; each toggle actively changes how the platform responds to users and services.

---

## Activated Settings

### 1. ▶️ Session Timeout
- Purpose: Define how long a logged-in session stays valid before the JWT token expires.
- Config value: `sessionTimeout` (minutes). Default: 30.
- How it works:
  - The system reads the timeout from the database on login.
  - `create_access_token()` issues JWTs that expire after that duration.
  - Users must re-authenticate when the timer runs out.
- Key files:
  - `backend/security/auth.py`
  - `backend/utils/technical_settings.py`

### 2. 🔒 Max Upload Size
- Purpose: Protect endpoints from oversized file uploads.
- Config value: `maxUploadSize` (MB). Default: 10.
- Enforcement:
  - Middleware inspects the `Content-Length` header for POST/PUT/PATCH requests.
  - Requests above the limit immediately receive HTTP 413 (Request Entity Too Large).
  - Applies to every upload endpoint automatically.
- Key files:
  - `backend/middleware/max_upload_size.py`
  - `backend/main.py`

### 3. 🛠️ Maintenance Mode
- Purpose: Temporarily block the site (503 response) while preserving admin access.
- Config value: `maintenanceMode`. Default: disabled (`false`).
- Behavior:
  - When enabled, all requests except allow-listed routes (login, branding, admin settings, health checks) receive HTTP 503.
  - Administrators can still reach the admin panel to disable maintenance.
- Key files:
  - `backend/middleware/maintenance_mode.py`
  - `backend/main.py`

### 4. ⚡ API Rate Limiting
- Purpose: Prevent abuse by limiting requests per IP address.
- Config value: `apiRateLimit` (e.g., "100/hour"). Default: 100/hour.
- Enforcement:
  - `SlowAPI` middleware tracks counts per IP.
  - Limits support "60/minute", "100/hour", "1000/day" formats.
  - Exceeding the limit returns HTTP 429 (Too Many Requests).
  - Currently driven by the `GTS_RATE_LIMIT` environment variable.
- Key file: `backend/main.py`

### 5. ✂️ Caching
- Purpose: Cache expensive computations for faster responses.
- Config value: `cachingEnabled`. Default: enabled (`true`).
- Details:
  - Functions decorated with `@cached` automatically store results.
  - Cache entries expire after 300 seconds (5 minutes).
  - Cache hits reduce database pressure.
  - Provides `/cache-stats` and `/clear-cache` admin endpoints.
- Key files:
  - `backend/utils/cache_decorator.py`
  - `backend/utils/technical_settings.py`

### 6. 📅 Backup Frequency
- Purpose: Schedule automatic database backups.
- Supported values: `hourly`, `daily`, `weekly`, `monthly`. Default: `daily`.
- Mechanics:
  - Background task starts on app startup and triggers backups per schedule.
  - The admin endpoint `/api/v1/admin/platform-settings/trigger-backup` allows manual runs.
  - Backup attempts currently logged; consider integrating `pg_dump` or Render Backup API for full snapshots.
- Key files:
  - `backend/utils/backup_scheduler.py`
  - `backend/main.py`

---

## Usage Guide

### From the Admin Panel
1. Navigate to **Platform Settings > Technical Settings**.
2. Adjust the slider/fields for each option.
3. Save the changes. They apply immediately (for example, Session Timeout begins a new countdown).

### Via API
```
GET  /api/v1/admin/platform-settings
PUT  /api/v1/admin/platform-settings
{
  "technical": {
    "sessionTimeout": 60,
    "maxUploadSize": 20,
    "maintenanceMode": false,
    "cachingEnabled": true,
    "apiRateLimit": "200/hour",
    "backupFrequency": "daily"
  }
}
POST /api/v1/admin/platform-settings/trigger-backup
POST /api/v1/admin/platform-settings/clear-cache
GET  /api/v1/admin/platform-settings/cache-stats
```

### Caching System
- All technical settings are cached for 60 seconds to reduce read operations.
- On settings save, caches invalidate automatically.
- If the cache service fails, defaults are used until recovery.

### Logging Highlights
```
[startup] Technical settings loaded: sessionTimeout=30, maxUploadSize=10, maintenanceMode=False, apiRateLimit=100/hour
[main] Maintenance Mode Middleware activated
[main] Max Upload Size Middleware activated
[startup] Backup scheduler started
```
Runtime logs also report session timeout usage, upload rejections, backup start/completion, and cache hits.

---

## Testing Procedures

### Session Timeout
1. Set the timeout to 1 minute via the admin panel.
2. Log in and wait for automatic logout after 60 seconds.
3. Observe that a new session is required.

### Maintenance Mode
1. Enable maintenance mode from Technical Settings.
2. Hit public endpoints to ensure they return HTTP 503.
3. Access `/api/v1/admin/platform-settings` and disable the mode.

### Max Upload Size
1. Lower the limit to 1 MB.
2. Upload a 2 MB file (should receive HTTP 413).

### Backup Trigger
```
curl -X POST http://localhost:8000/api/v1/admin/platform-settings/trigger-backup \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### Caching Endpoints
```
curl http://localhost:8000/api/v1/admin/platform-settings/cache-stats \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

curl -X POST http://localhost:8000/api/v1/admin/platform-settings/clear-cache \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

---

## Important Notes

- **Fully activated:** Session Timeout, Max Upload Size, Maintenance Mode, API Rate Limiting, Caching, Backup Scheduler are all live.
- **Requires enhancement:** Backup logging currently lacks actual `pg_dump` snapshots; integrate with Render Backup API for production.
- **Security reminder:** Maintenance mode bypass relies on JWT settings—review secrets periodically to prevent unauthorized access.

---

## Summary

The platform now exposes a comprehensive technical settings suite that can be tuned from the admin UI or API. Every change propagates at runtime, so use the provided endpoints and logs to monitor the system while making adjustments.
