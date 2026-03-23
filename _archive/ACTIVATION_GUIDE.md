# 🚀 EN - GTS Logistics

## 📋 EN **7 EN** EN GTS Logistics SaaS. EN.

---

## 1️⃣ EN

### EN:
```bash
pip install -r requirements.enhanced.txt
```

### EN:
```bash
# Redis for caching
pip install redis[hiredis]>=5.0.0

# Async file operations
pip install aiofiles>=23.0.0

# 2FA/TOTP
pip install pyotp>=2.9.0 qrcode[pil]>=7.4.0

# Testing
pip install pytest>=8.0.0 pytest-asyncio>=0.23.0 pytest-cov>=4.1.0

# Monitoring (optional)
pip install sentry-sdk[fastapi]>=1.40.0

# OAuth2 (optional)
pip install authlib>=1.3.0 httpx>=0.27.0
```

---

## 2️⃣ EN Redis Caching

### EN Redis EN:
```bash
# EN Docker
docker run -d -p 6379:6379 --name gts-redis redis:alpine
```

### EN Redis Cloud:
- EN [Redis Cloud](https://redis.com/try-free/)
- EN URL EN

### EN:
EN `.env`:
```env
REDIS_URL=redis://localhost:6379/0
CACHE_ENABLED=true
CACHE_TTL=300
```

### EN:
EN `backend/main.py` EN:
```python
from backend.utils.cache import cache

@app.on_event("startup")
async def startup_cache():
    await cache.connect()
    log.info("✅ Redis cache connected")

@app.on_event("shutdown")
async def shutdown_cache():
    await cache.disconnect()
    log.info("Redis cache disconnected")
```

---

## 3️⃣ EN Structured Logging

### EN `backend/main.py` EN:
```python
from backend.utils.logging_config import setup_logging

@app.on_event("startup")
async def startup_logging():
    setup_logging(
        app_name="gts",
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        enable_json=True,
        enable_file=True
    )
    log.info("✅ Structured logging initialized")
```

### EN:
```python
from backend.utils.logging_config import SecurityLogger, RequestLogger

# Log authentication
SecurityLogger.log_auth_attempt(
    email="user@gts.com",
    success=True,
    ip_address="1.2.3.4"
)

# Log HTTP request
RequestLogger.log_request(
    method="GET",
    path="/api/v1/users",
    status_code=200,
    duration_ms=45.2,
    user_id="user123"
)
```

---

## 4️⃣ EN 2FA (Two-Factor Authentication)

### EN Users:
```sql
ALTER TABLE users ADD COLUMN tfa_secret VARCHAR(255);
ALTER TABLE users ADD COLUMN tfa_enabled BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN tfa_backup_codes TEXT[];
```

### EN Endpoints EN `backend/routes/auth_routes.py`:
```python
from backend.security.two_factor_auth import TwoFactorAuth, TwoFactorSetup

@router.post("/auth/2fa/setup", response_model=TwoFactorSetup)
async def setup_2fa(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Enable 2FA for current user"""
    tfa = TwoFactorAuth()
    secret = tfa.generate_secret()
    qr_code = tfa.generate_qr_code(current_user.email, secret)
    backup_codes = tfa.generate_backup_codes()
    
    # Store in database (hash backup codes)
    current_user.tfa_secret = secret
    current_user.tfa_backup_codes = backup_codes  # Hash these!
    current_user.tfa_enabled = True
    await db.commit()
    
    return TwoFactorSetup(
        secret=secret,
        qr_code=qr_code,
        backup_codes=backup_codes,
        manual_entry_key=secret
    )

@router.post("/auth/2fa/verify")
async def verify_2fa(
    token: str,
    current_user: User = Depends(get_current_user)
):
    """Verify 2FA token"""
    tfa = TwoFactorAuth()
    
    if not current_user.tfa_secret:
        raise HTTPException(400, "2FA not enabled")
    
    if not tfa.verify_token(current_user.tfa_secret, token):
        raise HTTPException(401, "Invalid 2FA code")
    
    return {"verified": True}
```

---

## 5️⃣ EN OAuth2 (Google/Microsoft/GitHub)

### EN OAuth2 Credentials:

#### Google:
1. EN [Google Cloud Console](https://console.cloud.google.com/)
2. EN OAuth2 Client ID
3. EN Redirect URI: `http://localhost:8000/auth/oauth/google/callback`

#### Microsoft:
1. EN [Azure Portal](https://portal.azure.com/)
2. EN
3. EN Redirect URI

#### GitHub:
1. EN [GitHub Settings > Developer settings](https://github.com/settings/developers)
2. EN OAuth App EN

### EN:
```env
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

MICROSOFT_CLIENT_ID=your_microsoft_client_id
MICROSOFT_CLIENT_SECRET=your_microsoft_client_secret

GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
```

### EN Endpoints:
```python
from backend.security.two_factor_auth import build_authorization_url
import secrets

@router.get("/auth/oauth/{provider}")
async def oauth_login(provider: str, request: Request):
    """Start OAuth2 flow"""
    state = secrets.token_urlsafe(32)
    
    # Store state in session/cache for verification
    # ...
    
    auth_url = build_authorization_url(
        provider=provider,
        client_id=os.getenv(f"{provider.upper()}_CLIENT_ID"),
        redirect_uri=f"{request.base_url}auth/oauth/{provider}/callback",
        state=state
    )
    
    return RedirectResponse(auth_url)

@router.get("/auth/oauth/{provider}/callback")
async def oauth_callback(
    provider: str,
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db)
):
    """OAuth2 callback handler"""
    # 1. Verify state
    # 2. Exchange code for access token
    # 3. Fetch user info
    # 4. Create or login user
    # 5. Issue JWT
    pass
```

---

## 6️⃣ EN

### EN:
```bash
pytest tests/test_complete_system.py -v
```

### EN Coverage:
```bash
pytest tests/test_complete_system.py --cov=backend --cov-report=html
```

### EN:
```bash
pytest tests/test_complete_system.py::test_create_access_token -v
```

---

## 7️⃣ EN Sentry Monitoring (EN)

### EN Sentry DSN:
1. EN [Sentry.io](https://sentry.io/)
2. EN
3. EN DSN

### EN:
```env
SENTRY_DSN=https://your-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1
```

### EN:
EN `backend/main.py` - EN `SENTRY_DSN`

---

## 8️⃣ EN

### EN Async Endpoints:
```bash
curl http://localhost:8000/api/emails
curl http://localhost:8000/dashboard/summary
curl http://localhost:8000/financial/summary
```

### EN Cache:
```python
from backend.utils.cache import cache
await cache.connect()
await cache.set("test", {"hello": "world"})
result = await cache.get("test")
print(result)  # Should print: {'hello': 'world'}
```

### EN API Documentation:
EN: http://localhost:8000/docs

EN:
- ✅ EN
- ✅ EN (Auth, Admin, Bot OS, Finance, etc.)
- ✅ EN

---

## 9️⃣ EN:

### Backend:
- ✅ EN
- ✅ Redis EN)
- ✅ Logging EN
- ✅ EN
- ✅ EN

### Database:
- ✅ Migrations EN
- ✅ EN 2FA EN)
- ✅ Backup EN

### Security:
- ✅ JWT_SECRET EN
- ✅ CORS EN
- ✅ SSL/TLS EN
- ✅ Rate limiting EN

### Monitoring:
- ✅ Sentry DSN EN)
- ✅ Logs directory EN
- ✅ Log rotation EN

---

## 🆘 EN

### Redis EN:
```python
# EN
redis-cli ping
# EN: PONG
```

### 2FA EN:
```python
# EN
pip list | grep pyotp
pip list | grep qrcode
```

### Logging EN:
```python
# EN
mkdir -p logs
chmod 755 logs
```

---

## 📞 EN:
- 📧 Email: support@gts-logistics.com
- 📚 Documentation: http://localhost:8000/docs
- 🐛 Issues: GitHub Issues

---

## 🎉 EN!

EN. EN **98% EN** EN! 🚀
