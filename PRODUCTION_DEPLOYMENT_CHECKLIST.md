# Production Deployment Checklist

## 🚀 Pre-Deployment Verification

### 1. Code Quality ✅
- [x] All Phase 1 code review completed
- [x] Security vulnerabilities patched (jspdf, httpx, etc.)
- [x] Package versions updated to stable releases
- [ ] Final code review by senior developer
- [ ] All TODO comments addressed

### 2. Testing ✅
- [x] Health checks passing
- [ ] Integration tests passing (pending auth fix)
- [ ] Load testing completed with baselines
- [ ] Performance benchmarks established
- [ ] Frontend E2E tests passing
- [ ] Security testing (OWASP top 10)

### 3. Configuration 📋
- [ ] Environment variables documented in .env.example
- [ ] Production DATABASE_URL configured
- [ ] JWT_SECRET set to strong random value (min 32 chars)
- [ ] ALLOWED_ORIGINS configured for CORS
- [ ] LOG_LEVEL set to "warning" or "error"
- [ ] DEBUG_MODE = false
- [ ] SECRET_KEY rotated for production

### 4. Database 🗄️
- [x] Alembic migrations tested
- [x] 61+ migration revisions verified
- [ ] Database backup strategy configured
- [ ] Connection pooling optimized
- [ ] Indexes verified on critical tables
- [ ] Database credentials secured in secrets manager

### 5. Security 🔐
- [x] HTTPS/TLS certificates ready
- [x] JWT authentication configured
- [x] RBAC policies tested
- [ ] Rate limiting configured for all endpoints
- [ ] SQL injection prevention verified
- [ ] XSS protection enabled
- [ ] CSRF tokens implemented (if needed)
- [ ] Security headers configured (CSP, HSTS, etc.)

### 6. Monitoring & Logging 📊
- [ ] Prometheus metrics exposed at /metrics
- [ ] Structured logging configured (JSON format)
- [ ] Error tracking (Sentry) configured
- [ ] APM tool integrated (optional: New Relic, Datadog)
- [ ] Health check endpoints tested
- [ ] Uptime monitoring configured

### 7. Infrastructure 🏗️
- [ ] Hosting provider selected (Render, AWS, etc.)
- [ ] Domain name configured
- [ ] DNS records updated
- [ ] CDN configured (optional: Cloudflare, Fastly)
- [ ] Load balancer configured (if multi-instance)
- [ ] Auto-scaling policies set (if applicable)

---

## 🎯 Deployment Steps

### Phase 1: Staging Deployment

#### 1.1 Prepare Staging Environment
```bash
# Create staging branch
git checkout -b staging/v1.0

# Update version in package.json / pyproject.toml
# Version: 1.0.0-staging

# Build frontend
cd frontend
npm run build

# Verify build
ls -la dist/
```

#### 1.2 Database Migration (Staging)
```bash
# Backup staging database first
pg_dump $STAGING_DATABASE_URL > staging_backup_$(date +%Y%m%d).sql

# Run migrations
cd backend
alembic -c alembic.ini upgrade head

# Verify migrations
alembic -c alembic.ini current
```

#### 1.3 Deploy Backend (Staging)
```bash
# Option A: Render.com
# - Push to staging branch
# - Render auto-deploys from GitHub

# Option B: Manual deployment
# Install dependencies
pip install -r backend/requirements.txt

# Start with Gunicorn
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### 1.4 Deploy Frontend (Staging)
```bash
# Option A: Render Static Site
# - Point to frontend/dist/ folder
# - Configure rewrites for SPA routing

# Option B: Vercel/Netlify
# Build command: npm run build
# Publish directory: dist
# Redirects: /* /index.html 200
```

#### 1.5 Staging Smoke Tests
```bash
# Health check
curl https://staging-api.gts.com/healthz

# API docs accessible
curl https://staging-api.gts.com/docs

# Frontend loads
curl https://staging.gts.com

# Login flow
curl -X POST https://staging-api.gts.com/api/v1/auth/token \
  -d "username=test@example.com&password=test123"

# Run automated tests against staging
pytest tests/ --base-url=https://staging-api.gts.com
```

### Phase 2: Production Deployment

#### 2.1 Pre-Production Checklist
- [ ] All staging tests passed
- [ ] Load testing completed (500+ concurrent users)
- [ ] Security scan completed (no high/critical issues)
- [ ] Database backup verified (can restore successfully)
- [ ] Rollback plan documented
- [ ] Monitoring dashboards ready
- [ ] Incident response team notified

#### 2.2 Production Database Migration
```bash
# Create production database backup
pg_dump $PROD_DATABASE_URL > prod_backup_$(date +%Y%m%d_%H%M%S).sql

# Upload backup to S3 (or secure storage)
aws s3 cp prod_backup_*.sql s3://gts-backups/

# Run migrations with backup verification
alembic -c alembic.ini upgrade head

# Verify migration
alembic -c alembic.ini current
# Expected output: [current revision ID]
```

#### 2.3 Deploy Backend (Production)
```bash
# Set production environment variables
export ENV=production
export LOG_LEVEL=warning
export DEBUG_MODE=false

# Install production dependencies only
pip install -r backend/requirements.txt --no-dev

# Start with production settings (4 workers for 2 CPU cores)
gunicorn backend.main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log \
  --log-level warning
```

#### 2.4 Deploy Frontend (Production)
```bash
# Build with production settings
cd frontend
npm run build

# Verify build size (should be optimized)
du -sh dist/
# Target: < 5 MB

# Deploy to CDN/static hosting
# Render: Auto-deploy from main branch
# Vercel: vercel --prod
# Netlify: netlify deploy --prod
```

#### 2.5 Post-Deployment Verification
```bash
# 1. Health check
curl https://api.gts.com/healthz
# Expected: {"status":"ok"}

# 2. API documentation
curl https://api.gts.com/docs
# Expected: 200 OK

# 3. Frontend loads
curl https://gts.com
# Expected: 200 OK, React app loads

# 4. WebSocket connection
wscat -c wss://api.gts.com/api/v1/ws/live
# Expected: Connection established

# 5. Bot system operational
curl https://api.gts.com/api/v1/bots -H "Authorization: Bearer $TOKEN"
# Expected: List of 15+ bots

# 6. Metrics endpoint
curl https://api.gts.com/metrics
# Expected: Prometheus metrics
```

#### 2.6 Monitoring Setup
```bash
# Verify Prometheus scraping metrics
curl https://api.gts.com/metrics | grep gts_http_requests_total

# Check logs aggregation
tail -f logs/error.log | jq .

# Verify Sentry error tracking
# Send test error and verify it appears in Sentry dashboard

# Check uptime monitoring
# Verify UptimeRobot/Pingdom receives health check responses
```

---

## 🔄 Rollback Procedure

If deployment fails or critical issues discovered:

### Immediate Rollback (< 5 minutes)
```bash
# 1. Revert to previous deployment
# Render: Rollback via dashboard or API
# Manual: 
git checkout [previous-commit]
git push -f origin production

# 2. Restore database if migrations failed
psql $PROD_DATABASE_URL < prod_backup_[timestamp].sql

# 3. Verify rollback successful
curl https://api.gts.com/healthz
```

### Partial Rollback
```bash
# Rollback only backend OR frontend
# Keep whichever component is working

# Backend only:
git revert [failed-backend-commit]

# Frontend only:
cd frontend && git revert [failed-frontend-commit]
```

---

## 📋 Post-Deployment Tasks

### Immediate (< 1 hour)
- [ ] Monitor error rates (target: < 0.1%)
- [ ] Monitor response times (target: p95 < 500ms)
- [ ] Check database connection pool (no exhaustion)
- [ ] Verify WebSocket connections stable
- [ ] Test critical user flows manually

### First 24 Hours
- [ ] Monitor memory usage trends
- [ ] Check for any error spikes
- [ ] Verify backup job runs successfully
- [ ] Monitor bot execution rates
- [ ] Review access logs for anomalies

### First Week
- [ ] Analyze performance baselines
- [ ] Adjust auto-scaling thresholds if needed
- [ ] Review and tune rate limits
- [ ] Optimize slow database queries
- [ ] Gather user feedback

---

## 🚨 Incident Response

### Critical Issues (P0)
**Symptoms:** Site down, database unavailable, data loss
**Response Time:** < 15 minutes
**Actions:**
1. Page on-call engineer
2. Check health endpoints
3. Review error logs
4. Rollback if necessary
5. Escalate to senior team

### High Priority (P1)
**Symptoms:** Degraded performance, elevated errors, key feature broken
**Response Time:** < 1 hour
**Actions:**
1. Notify team via Slack/Discord
2. Investigate logs and metrics
3. Apply hotfix if possible
4. Schedule rollback if no quick fix

### Medium Priority (P2)
**Symptoms:** Minor bugs, cosmetic issues, non-critical feature broken
**Response Time:** < 4 hours
**Actions:**
1. Create ticket in issue tracker
2. Investigate during business hours
3. Schedule fix in next sprint

---

## 📞 Contact Information

**Production Deployment Lead:** [Name]  
**On-Call Engineer:** [Name]  
**Database Admin:** [Name]  
**Security Team:** [Email]  
**Incident Channel:** #prod-incidents (Slack/Discord)

---

## 📚 Additional Resources

- [BOS System Index](BOS_SYSTEM_INDEX.md)
- [API Reference](API_REFERENCE_COMPLETE.md)
- [Phase 1 Audit Report](PHASE_1_AUDIT_REPORT.md)
- [Phase 2 Testing Summary](PHASE_2_TESTING_SUMMARY.md)
- [Load Testing Guide](LOAD_TESTING_GUIDE.md)

---

**Deployment Version:** 1.0.0  
**Target Date:** [To be scheduled]  
**Deployment Window:** [Preferred: Saturday 2-6 AM UTC]  
**Expected Downtime:** 0 minutes (rolling deployment)

**Last Updated:** February 3, 2026
