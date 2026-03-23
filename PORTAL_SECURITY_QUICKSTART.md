# Portal Security - Quick Start & Deployment Guide

## ⚡ 5-Minute Setup

### Step 1: Get hCaptcha Keys (2 minutes)
1. Visit https://www.hcaptcha.com/
2. Sign up for a free account
3. Create a new site for your domain
4. Copy the **Sitekey** and **Secret Key**

### Step 2: Update .env (1 minute)
```bash
# Add to d:\GTS\.env

HCAPTCHA_SECRET=<paste-secret-key-here>
HCAPTCHA_SITEKEY=<paste-sitekey-here>

FRONTEND_URL=http://localhost:5173  # or your deployed frontend URL
ADMIN_URL=http://localhost:5173     # or your deployed admin URL
```

### Step 3: Update Frontend .env (30 seconds)
```bash
# Add to d:\GTS\frontend\.env

VITE_HCAPTCHA_SITEKEY=<paste-sitekey-here>
```

### Step 4: Run Migrations (1 minute)
```powershell
# From repository root
python -m alembic -c backend\alembic.ini upgrade head
```

### Step 5: Restart Backend
```powershell
# Stop existing uvicorn process
# Run:
.\run-dev.ps1
```

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Backend starts without errors
- [ ] Frontend loads at http://localhost:5173
- [ ] Register page shows CAPTCHA box
- [ ] Can submit registration form (with valid CAPTCHA)
- [ ] Check email inbox for verification link
- [ ] Click verification link → redirects to login
- [ ] Admin can see notifications at `/admin/notifications`
- [ ] Admin can view audit log at `/admin/portal-requests`

## 🔧 Production Deployment

### Environment-Specific Settings

**Development** (.env.development):
```bash
HCAPTCHA_SECRET=10000000-ffff-ffff-ffff-000000000001
HCAPTCHA_SITEKEY=10000000-ffff-ffff-ffff-000000000001
FRONTEND_URL=http://localhost:5173
ADMIN_URL=http://localhost:5173
```

**Staging** (.env.staging):
```bash
HCAPTCHA_SECRET=<your-staging-secret>
HCAPTCHA_SITEKEY=<your-staging-sitekey>
FRONTEND_URL=https://staging.yourcompany.com
ADMIN_URL=https://staging.yourcompany.com/admin
```

**Production** (.env.production):
```bash
HCAPTCHA_SECRET=<your-production-secret>
HCAPTCHA_SITEKEY=<your-production-sitekey>
FRONTEND_URL=https://yourcompany.com
ADMIN_URL=https://yourcompany.com/admin
```

## 🧰 Troubleshooting

### CAPTCHA Not Showing
**Problem**: CAPTCHA box is missing from register page  
**Check**:
1. Is `VITE_HCAPTCHA_SITEKEY` set in frontend .env?
2. Did you restart frontend dev server after changing .env?
3. Check browser console for errors

**Solution**:
```bash
# Frontend .env must have:
VITE_HCAPTCHA_SITEKEY=10000000-ffff-ffff-ffff-000000000001

# Then restart:
cd frontend
npm run dev
```

### CAPTCHA Verification Failing
**Problem**: "CAPTCHA verification failed" error  
**Check**:
1. Is `HCAPTCHA_SECRET` set in backend .env?
2. Is the secret/sitekey mismatch? (must be from same site)
3. Is hCaptcha API reachable from your network?

**Solution**:
```bash
# Verify in backend logs that it's trying to verify:
# [Portal] CAPTCHA verification failed for IP: ...

# Check hCaptcha account in browser console:
# Network tab → POST to hcaptcha.com/siteverify
```

### Rate Limit Too Strict
**Problem**: Can't submit multiple test requests  
**Explanation**: 5 requests per hour per IP is by design  
**Workaround for testing**: Use different IPs or wait 1 hour between tests

### Email Verification Not Received
**Problem**: Verification email not arriving  
**Check**:
1. Is `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD` configured?
2. Check backend logs for email sending errors
3. Check spam/junk folder

**Solution**:
```bash
# Test email sending directly:
python -c "
from backend.utils.email_utils import send_email
send_email('Test', 'Test body', ['your-test-email@example.com'])
"
```

### Audit Log Not Showing
**Problem**: No entries in `/admin/requests/:id/audit-log`  
**Check**:
1. Did migrations run successfully? (`audit_log` table exists)
2. Is `log_audit_action()` being called?

**Solution**:
```bash
# Verify table exists:
psql $DATABASE_URL -c "SELECT * FROM audit_log LIMIT 1;"

# Re-run migrations:
python -m alembic -c backend\alembic.ini upgrade head
```

## 📊 Monitoring

### Check Key Metrics

```bash
# CAPTCHA failure rate (from logs)
grep "CAPTCHA verification failed" backend.log | wc -l

# Rate limit hits
grep "Rate limit exceeded" backend.log | wc -l

# Duplicate submissions
grep "Duplicate submission" backend.log | wc -l

# Email verification success rate
psql $DATABASE_URL -c "
  SELECT 
    COUNT(*) as total,
    COUNT(verified_at) as verified,
    ROUND(100.0 * COUNT(verified_at) / COUNT(*), 2) as verification_rate
  FROM email_verifications;"
```

### Database Queries for Debugging

```sql
-- Show recent requests with IP
SELECT id, email, company, ip_address, created_at 
FROM portal_requests 
ORDER BY created_at DESC 
LIMIT 10;

-- Show rate limit status
SELECT ip_address, request_count, first_request_at 
FROM portal_request_ip_limits 
WHERE request_count > 3;

-- Show unverified emails
SELECT COUNT(*) 
FROM email_verifications 
WHERE verified_at IS NULL AND expires_at > NOW();

-- Show admin notification counts
SELECT notification_type, COUNT(*) 
FROM admin_notifications 
GROUP BY notification_type;
```

## 📝 Configuration Details

### CAPTCHA Configuration

**hCaptcha vs Google reCAPTCHA**:
- Currently using hCaptcha (privacy-focused, free tier)
- Easy to switch: just change sitekey/secret and imports

**If you want to use Google reCAPTCHA instead**:
```bash
# Install dependency
pip install google-recaptcha

# Update backend code to verify with Google API instead
# Update frontend component to google-recaptcha library
```

### IP-Based Rate Limiting

**Current Settings**:
- 5 requests per hour per IP
- Stored in `portal_request_ip_limits` table
- Auto-expires entries after 1 hour

**To adjust**:
```python
# In backend/routes/portal_requests.py
if await check_ip_rate_limit(client_ip, requests_per_hour=10):  # Change to 10
```

### Email Configuration

The system uses standard SMTP for sending emails.

**Required Settings**:
```bash
SMTP_HOST=mail.example.com
SMTP_PORT=465
SMTP_USER=noreply@example.com
SMTP_PASSWORD=your-password
SMTP_FROM=noreply@example.com
SMTP_SECURE=true
```

**Gmail Configuration** (if using Gmail):
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password  # NOT your gmail password!
SMTP_FROM=your-email@gmail.com
SMTP_SECURE=false  # Gmail uses STARTTLS, not SSL
```

## 🔐 Security Hardening (Advanced)

### Add HTTPS Enforcement
```python
# backend/main.py
@app.middleware("http")
async def https_redirect(request: Request, call_next):
    if request.url.scheme == "http" and ENV == "production":
        return RedirectResponse(url=request.url.replace("http", "https"), status_code=301)
    return await call_next(request)
```

### Add CORS Restrictions
```python
# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Add Rate Limiting to All Endpoints
```python
# Already implemented for /portal/requests
# Consider extending to admin endpoints
```

### Log Security Events
```bash
# Monitor for suspicious patterns
tail -f backend.log | grep -E "CAPTCHA|Rate limit|Duplicate"
```

## 🚀 Performance Optimization

### Caching
The system already uses efficient queries:
- Rate limit check: O(1) index lookup
- Duplicate check: O(1) index lookup
- IP extraction: No DB hit

### Database Indexing
All critical columns are indexed:
- `email_verifications.token` (for verification)
- `admin_notifications.request_id` (for lookups)
- `audit_log.request_id` (for audit history)
- `portal_request_ip_limits.ip_address` (for rate limiting)

### Async Operations
- All database operations use async/await
- No blocking operations in request handlers
- Email sending is non-blocking

## 📞 Support & Issues

### Common Questions

**Q: Can I disable CAPTCHA in development?**  
A: Yes, it auto-skips if `HCAPTCHA_SECRET` is not set.

**Q: Can I change the rate limit?**  
A: Yes, modify `requests_per_hour` parameter in `check_ip_rate_limit()` call.

**Q: How long are audit logs kept?**  
A: Permanently (for compliance). Archive to cold storage as needed.

**Q: Can admins be notified of new requests via email?**  
A: Yes, modify `send_admin_notification()` call to send email too.

**Q: Is LoadBoard country restriction enforceable?**  
A: Frontend enforces it, but validate on backend too (add check in request handler).

---

**For more details, see**: [PORTAL_SECURITY_IMPLEMENTATION.md](./PORTAL_SECURITY_IMPLEMENTATION.md)

**Last Updated**: 2025-01-20  
**Status**: ✅ Ready for Production
