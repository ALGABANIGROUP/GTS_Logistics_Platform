# 🔐 SECURITY HARDENING IMPLEMENTATION GUIDE

## Overview

Complete security hardening implementation including HTTPS enforcement, security headers, rate limiting, and production validation.

---

## ✅ What Was Implemented

### 1. Security Configuration Validation

**File:** `backend/config.py`

**Features:**
- ✅ **SECRET_KEY Validation** - Forces strong SECRET_KEY in production
- ✅ **Minimum Key Length** - Enforces 32+ character keys
- ✅ **CORS Validation** - Requires CORS configuration in production
- ✅ **Environment-based Defaults** - Different settings for dev/prod
- ✅ **Increased Rate Limiting** - 1000 req/min in production vs 120 in dev

**Critical Validations:**
```python
# Main.py will CRASH if these are not set in production:
✓ SECRET_KEY must be changed from default
✓ SECRET_KEY must be 32+ characters
✓ CORS origins must be configured
```

---

### 2. Security Headers Middleware

**File:** `backend/middleware/security_headers.py`

**Implemented Headers:**

#### 🔒 HSTS (HTTP Strict Transport Security)
```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```
Forces HTTPS for 1 year, includes all subdomains

#### 🛡️ X-Content-Type-Options
```
X-Content-Type-Options: nosniff
```
Prevents MIME-sniffing attacks

#### 🚫 X-Frame-Options
```
X-Frame-Options: DENY
```
Prevents clickjacking by blocking iframe embedding

#### ⚡ X-XSS-Protection
```
X-XSS-Protection: 1; mode=block
```
Legacy XSS filter (still useful for older browsers)

#### 🔐 Content-Security-Policy (CSP)
```
Content-Security-Policy: default-src 'self'; ...
```
Comprehensive CSP policy:
- Blocks inline scripts (except marked safe)
- Allows specific CDNs (jsdelivr, unpkg)
- Restricts external resources
- Prevents object/embed abuse

#### 🔍 Referrer-Policy
```
Referrer-Policy: strict-origin-when-cross-origin
```
Controls referrer information leakage

#### 🎛️ Permissions-Policy
```
Permissions-Policy: geolocation=(), camera=(), ...
```
Blocks unnecessary browser features

#### 🚮 Server Header Removal
Removes identifying headers:
- Server
- X-Powered-By

#### 💾 Cache Control (Sensitive Endpoints)
```
Cache-Control: no-store, no-cache, must-revalidate, private
```
For /auth/, /admin/, /user/ endpoints

---

### 3. HTTPS Redirect Middleware

**File:** `backend/middleware/security_headers.py`

**Features:**
- ✅ Automatic HTTP → HTTPS redirect in production
- ✅ 301 permanent redirect
- ✅ Configurable via ENFORCE_HTTPS env var
- ✅ Skips redirect in development

---

### 4. Enhanced Rate Limiting

**File:** `backend/middleware/security_headers.py`

**Features:**
- ✅ In-memory rate limiting (upgradeable to Redis)
- ✅ Per-IP tracking
- ✅ Configurable limits (1000/min default in production)
- ✅ 429 Too Many Requests response
- ✅ Retry-After header
- ✅ Health check exemptions
- ✅ Automatic cleanup of old entries

**Production Note:** Replace with Redis-based rate limiting for horizontal scaling

---

## 🚀 Setup Instructions

### Step 1: Update Environment Variables

Create or update `.env` file:

```bash
# CRITICAL: Production Security Settings
APP_ENV=production
SECRET_KEY=your-strong-secret-key-at-least-32-characters-long
ALGORITHM=HS256

# CORS Configuration (REQUIRED in production)
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
GTS_CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# HTTPS Enforcement
ENFORCE_HTTPS=true
ENABLE_SECURITY_HEADERS=true

# Rate Limiting
RATE_LIMIT_REQUESTS_PER_MINUTE=1000

# Database
PG_HOST=your-db-host
PG_PORT=5432
PG_DB=gts
PG_USER=your-db-user
PG_PASSWORD=your-db-password

# Email Alerts
ADMIN_EMAIL=admin@yourdomain.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Step 2: Generate Strong SECRET_KEY

**Option 1: Python**
```python
import secrets
secret_key = secrets.token_urlsafe(32)
print(f"SECRET_KEY={secret_key}")
```

**Option 2: OpenSSL**
```bash
openssl rand -base64 32
```

**Option 3: PowerShell**
```powershell
$bytes = New-Object byte[] 32
[System.Security.Cryptography.RNGCryptoServiceProvider]::Create().GetBytes($bytes)
[Convert]::ToBase64String($bytes)
```

Copy the output and set as SECRET_KEY in .env

### Step 3: Update main.py

Add security middleware to your FastAPI application:

```python
from backend.middleware.security_headers import (
    SecurityHeadersMiddleware,
    HTTPSRedirectMiddleware,
    RateLimitMiddleware
)
from backend.config import Settings

settings = Settings()

# Add middleware (order matters - added in reverse order of execution)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=settings.RATE_LIMIT_REQUESTS_PER_MINUTE
)
```

### Step 4: Test Security Configuration

**Development Test:**
```bash
# Should work fine with default SECRET_KEY
APP_ENV=development python -m uvicorn backend.main:app --reload
```

**Production Test (will fail if not configured):**
```bash
# Should CRASH with error if SECRET_KEY not changed
APP_ENV=production python -m uvicorn backend.main:app

# Expected error:
# ValueError: CRITICAL SECURITY ERROR: SECRET_KEY must be changed in production!
```

**Correct Production Start:**
```bash
APP_ENV=production SECRET_KEY=your-strong-key-here python -m uvicorn backend.main:app
```

---

## 🔍 Verification

### 1. Check Security Headers

```bash
curl -I https://yourdomain.com/api/v1/health
```

Expected headers:
```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'; ...
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), ...
```

### 2. Test HTTPS Redirect

```bash
curl -I http://yourdomain.com/api/v1/health
```

Expected: 301 redirect to HTTPS

### 3. Test Rate Limiting

```bash
# Rapid requests
for i in {1..150}; do curl -I https://yourdomain.com/api/v1/health; done
```

Expected: 429 after exceeding limit

### 4. Security Scan

Use SecurityHeaders.com:
```
https://securityheaders.com/?q=yourdomain.com
```

Target score: **A** or **A+**

---

## 📊 Security Checklist

### Pre-Production:
- [ ] SECRET_KEY changed from default
- [ ] SECRET_KEY is 32+ characters
- [ ] CORS origins configured
- [ ] HTTPS certificate installed
- [ ] ENFORCE_HTTPS=true
- [ ] Rate limiting configured
- [ ] Admin email configured for alerts
- [ ] Tested security headers
- [ ] Ran security scan

### Production Operations:
- [ ] Monitor rate limit hits
- [ ] Review security logs weekly
- [ ] Rotate SECRET_KEY annually
- [ ] Update security headers as needed
- [ ] Test HTTPS enforcement monthly

---

## 🛡️ Security Best Practices

### 1. Secret Management

**❌ Never:**
- Commit secrets to git
- Use default SECRET_KEY
- Share SECRET_KEY across environments
- Store plaintext passwords

**✅ Always:**
- Use environment variables
- Rotate secrets regularly
- Use different keys for dev/staging/prod
- Use secret management service (AWS Secrets Manager, etc.)

### 2. CORS Configuration

**❌ Avoid:**
```python
ALLOWED_ORIGINS="*"  # Allows any origin - DANGEROUS!
```

**✅ Use:**
```python
ALLOWED_ORIGINS="https://yourdomain.com,https://app.yourdomain.com"
```

### 3. Rate Limiting

**Production Recommendations:**
- API endpoints: 1000 requests/minute
- Auth endpoints: 20 requests/minute
- Public endpoints: 100 requests/minute

**Upgrade to Redis:**
```python
# For horizontal scaling
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter

@app.on_event("startup")
async def startup():
    redis_client = redis.from_url("redis://localhost")
    await FastAPILimiter.init(redis_client)
```

### 4. HTTPS Configuration

**Nginx Reverse Proxy:**
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 🚨 Incident Response

### If Secret Key Compromised:

1. **Immediate:**
   ```bash
   # Generate new key
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   
   # Update environment
   export SECRET_KEY=new-key-here
   
   # Restart application
   systemctl restart gts-backend
   ```

2. **Follow-up:**
   - Invalidate all existing JWT tokens
   - Force all users to re-login
   - Review access logs for suspicious activity
   - Update secret in all environments

### If DDoS Attack:

1. **Check rate limiting:**
   ```bash
   tail -f logs/api.log | grep "Rate limit"
   ```

2. **Enable Cloudflare DDoS protection**

3. **Temporarily lower rate limits:**
   ```bash
   export RATE_LIMIT_REQUESTS_PER_MINUTE=100
   systemctl restart gts-backend
   ```

---

## 📚 Additional Resources

### Tools:
- **SecurityHeaders.com** - Test security headers
- **SSL Labs** - Test SSL/TLS configuration
- **OWASP ZAP** - Security vulnerability scanner
- **Qualys SSL Server Test** - SSL configuration test

### Documentation:
- OWASP Security Headers: https://owasp.org/www-project-secure-headers/
- Mozilla Web Security: https://infosec.mozilla.org/guidelines/web_security
- CSP Evaluator: https://csp-evaluator.withgoogle.com/

---

## ✅ Summary

### What's Protected:

✅ **Injection Attacks** - CSP, input validation  
✅ **XSS Attacks** - CSP, XSS filter, content type sniffing  
✅ **Clickjacking** - X-Frame-Options  
✅ **MIME Sniffing** - X-Content-Type-Options  
✅ **MITM Attacks** - HSTS, HTTPS enforcement  
✅ **DDoS** - Rate limiting  
✅ **Information Leakage** - Server header removal

### Security Score Target:

🎯 **Grade A** on SecurityHeaders.com  
🎯 **Grade A+** on SSL Labs  
🎯 **0 Critical Vulnerabilities** on OWASP ZAP

---

**✅ Security Hardening Complete!**

Your application is now protected with industry-standard security measures.

**Next Steps:**
1. Generate strong SECRET_KEY
2. Configure CORS origins
3. Test in staging environment
4. Deploy to production
5. Run security scans
