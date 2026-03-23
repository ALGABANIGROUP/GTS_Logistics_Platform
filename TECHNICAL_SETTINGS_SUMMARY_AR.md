# ✅ Platform Technical Settings Activation

## Activation Status

All technical settings inside the Platform Settings admin panel are now **fully functional** and influence the live system rather than just storing configuration values.

### 1. ▶️ Session Timeout
- JWT session token lifetime enforcement
- Default expiration: 30 minutes
- Enforced automatically after each login

### 2. 🔒 Max Upload Size
- Middleware blocks any file that exceeds the limit
- Default and enforced limit: 10 MB
- Applies globally to all upload endpoints
- Returns HTTP 413 when the limit is exceeded

### 3. 🛠️ Maintenance Mode
- Blocks general traffic unless explicitly allowed
- Default state: disabled
- Platform administrators can toggle from the admin panel
- Returns HTTP 503 for blocked clients

### 4. ⚡ API Rate Limiting
- Limits the number of requests per IP
- Default rate: 100 requests/hour
- Powered by SlowAPI
- Violations return HTTP 429

### 5. ✂️ Caching
- Dynamic caches can be enabled/disabled
- Reduces repeated database hits
- Cache entries expire after 5 minutes
- Provides `/cache-stats` and `/clear-cache`

### 6. 📅 Backup Frequency
- Background tasks automatically create backups
- Supported schedules: hourly, daily, weekly, monthly
- Default frequency: daily
- Includes an admin endpoint to trigger on demand

## Key Files

### Middleware
- `backend/middleware/maintenance_mode.py`
- `backend/middleware/max_upload_size.py`

### Utilities
- `backend/utils/technical_settings.py`
- `backend/utils/cache_decorator.py`
- `backend/utils/backup_scheduler.py`

### Core Services
- `backend/main.py` – middleware registration and startup hooks
- `backend/security/auth.py` – session timeout enforcement
- `backend/routes/admin_platform_settings.py` – platform-level endpoints
- `backend/services/platform_settings_store.py` – setting persistence

## How to Access

### Admin Panel
1. Visit **Platform Settings**
2. Open **Technical Settings**
3. Adjust desired values
4. Save to persist (changes take effect immediately, e.g., Session Timeout begins new countdown)

### APIs
```
GET  /api/v1/admin/platform-settings
PUT  /api/v1/admin/platform-settings
POST /api/v1/admin/platform-settings/trigger-backup
POST /api/v1/admin/platform-settings/clear-cache
GET  /api/v1/admin/platform-settings/cache-stats
```

## Notifications

### Logging Examples
```
[startup] Technical settings loaded: sessionTimeout=30, maxUploadSize=10, ...
[main] Maintenance Mode Middleware activated
[main] Max Upload Size Middleware activated
[startup] Backup scheduler started
```

### Monitoring Notes
- Session Timeout enforcement logs the active timeout per login
- Upload rejections log the attempted size
- Backup attempts produce timestamped entries
- Cache hits/misses surface through `/cache-stats`

## Testing Checklist

### Session Timeout
1. Set the timeout to 1 minute
2. Log in and wait for automatic logout
3. Observe the new expiration countdown

### Maintenance Mode
1. Enable maintenance mode
2. Access a standard endpoint (should receive 503)
3. Disable it from the admin panel

### Max Upload Size
1. Lower the limit to 1 MB
2. Attempt to upload a 2 MB file (expect 413)

### Backup Trigger
```
curl -X POST http://localhost:8000/api/v1/admin/platform-settings/trigger-backup \\
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### Caching
```
curl http://localhost:8000/api/v1/admin/platform-settings/cache-stats \\
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

curl -X POST http://localhost:8000/api/v1/admin/platform-settings/clear-cache \\
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

## Final Notes

### Fully Activated
- Session Timeout — enforced per login
- Max Upload Size — file uploads limited globally
- Maintenance Mode — blocks requests outside allowed paths
- API Rate Limiting — throttles heavy consumers
- Caching System — caches expensive operations
- Backup Scheduler — periodic database backups

### Requires Follow-up
- Backup currently only logs attempts; consider running `pg_dump` or the Render Backup API for production snapshots
- Rate limits are read from the `GTS_RATE_LIMIT` env var; extend to database-driven values if needed
- Maintenance mode bypass relies on JWT secrets; audit periodically
