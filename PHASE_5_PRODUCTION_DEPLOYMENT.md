# Phase 5: Production Deployment & Infrastructure Setup

## 🎯 Phase Overview

**Objective:** Deploy the GTS application to production with full infrastructure, security hardening, and monitoring.

**Timeline:** 2-3 days  
**Status:** ⏳ In Progress  
**Previous Phase:** Phase 4 ✅ Complete (Security Grade: A-)

---

## 📊 Phase 5 Roadmap

### Part 1: Environment Configuration (2 hours)
- [ ] Create `.env.production` configuration
- [ ] Set up environment-specific database URL
- [ ] Configure CORS for production domain
- [ ] Enable HTTPS enforcement
- [ ] Add production secrets (keys, API tokens)

### Part 2: SSL/TLS Certificate Setup (1 hour)
- [ ] Generate or obtain SSL certificate
  - Option A: Let's Encrypt (free, automated)
  - Option B: Self-signed (development only)
  - Option C: AWS/Azure managed certificate
- [ ] Configure HTTPS on production server
- [ ] Enable HSTS (HTTP Strict Transport Security)
- [ ] Test certificate installation

### Part 3: CI/CD Pipeline (3 hours)
- [ ] Set up GitHub Actions workflow
  - Test on every push
  - Build Docker image
  - Deploy to staging
  - Manual approval for production
- [ ] Create deployment scripts
- [ ] Configure secrets in CI/CD
- [ ] Test workflow end-to-end

### Part 4: Monitoring & Observability (3 hours)
- [ ] Set up error tracking (Sentry)
- [ ] Configure metrics collection (Prometheus)
- [ ] Set up log aggregation
- [ ] Create monitoring dashboard (Grafana)
- [ ] Configure alerting rules

### Part 5: Database Management (1.5 hours)
- [ ] Create production database backups
- [ ] Test backup restoration
- [ ] Set up automated daily backups
- [ ] Configure database access controls
- [ ] Document recovery procedures

### Part 6: Security Hardening (2 hours)
- [ ] Restrict CORS origins
- [ ] Enable rate limiting
- [ ] Configure security headers
- [ ] Set up Web Application Firewall (WAF)
- [ ] Final security audit

### Part 7: Documentation & Runbooks (2 hours)
- [ ] Create deployment runbook
- [ ] Document incident response procedures
- [ ] Create troubleshooting guide
- [ ] API documentation updates
- [ ] User guides

**Total Estimated Time:** 14.5 hours (~2 days)

---

## 📋 Detailed Task Breakdown

### PART 1: Environment Configuration

#### Task 1.1: Create Production Configuration

**File:** `backend/.env.production`

```env
# Django/FastAPI Environment
DEBUG=False
ENVIRONMENT=production
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql+asyncpg://[user]:[password]@[host]:5432/gts_production?ssl=require

# Security
SECRET_KEY=[generate-new-key]
CORS_ORIGINS=https://gts.example.com,https://www.gts.example.com
ALLOWED_HOSTS=gts.example.com,www.gts.example.com

# JWT
JWT_ALGORITHM=HS256
JWT_SECRET=[generate-new-key]
JWT_EXPIRATION_HOURS=24

# API Keys (get from third-party services)
STRIPE_API_KEY=[production-key]
AWS_ACCESS_KEY_ID=[production-key]
AWS_SECRET_ACCESS_KEY=[production-secret]

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=[production-email]
SMTP_PASSWORD=[production-password]

# Monitoring
SENTRY_DSN=[sentry-production-dsn]
SLACK_WEBHOOK_URL=[slack-webhook]

# Redis (for caching)
REDIS_URL=redis://[host]:6379/0

# Domain Configuration
FRONTEND_URL=https://gts.example.com
API_URL=https://api.gts.example.com
```

**Actions:**
1. [ ] Generate secure SECRET_KEY: `python -c "import secrets; print(secrets.token_hex(32))"`
2. [ ] Update database URL with production credentials
3. [ ] Set appropriate CORS_ORIGINS
4. [ ] Obtain API keys from third-party services
5. [ ] Store in secure location (not in git)

---

#### Task 1.2: Configure CORS for Production

**File:** `backend/main.py`

```python
# Current (wildcard):
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ❌ Too permissive
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Production fix:
allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # ✅ Specific domains
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Explicit methods
    allow_headers=["*"],
)
```

---

#### Task 1.3: Enable HTTPS Enforcement

**File:** `backend/middleware/security.py` (new)

```python
from fastapi import Request
from fastapi.responses import RedirectResponse
from backend.config import settings

@app.middleware("http")
async def https_redirect(request: Request, call_next):
    """Redirect HTTP to HTTPS in production"""
    if (not request.url.scheme == "https" and 
        not settings.DEBUG and 
        request.headers.get("x-forwarded-proto") != "https"):
        
        url = request.url.replace(scheme="https")
        return RedirectResponse(url, status_code=301)
    
    response = await call_next(request)
    
    # Add security headers
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    return response
```

---

### PART 2: SSL/TLS Certificate Setup

#### Option A: Let's Encrypt (Recommended)

**Tools:** Certbot + Nginx/Apache

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Generate certificate
sudo certbot certonly --nginx -d gts.example.com -d www.gts.example.com

# Auto-renewal (runs daily)
sudo systemctl enable certbot.timer
```

**Files Generated:**
- `/etc/letsencrypt/live/gts.example.com/fullchain.pem` (certificate)
- `/etc/letsencrypt/live/gts.example.com/privkey.pem` (private key)

---

#### Option B: AWS Certificate Manager (If using AWS)

```bash
# Create certificate via AWS CLI
aws acm request-certificate \
  --domain-name gts.example.com \
  --subject-alternative-names www.gts.example.com \
  --validation-method DNS
```

---

#### Option C: Self-signed (Development Only)

```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365
```

---

### PART 3: CI/CD Pipeline Setup

#### Step 1: Create GitHub Actions Workflow

**File:** `.github/workflows/deploy.yml`

```yaml
name: Deploy to Production

on:
  push:
    branches: [main, production]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r backend/requirements.txt
      
      - name: Run tests
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost/test_gts
        run: |
          pytest backend/tests/ -v --tb=short
      
      - name: Security tests
        run: |
          pytest tests/test_security.py -v
  
  build:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Log in to Container Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
      
      - name: Build and push Docker image
        uses: docker/build-push-action@v4
        with:
          context: .
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Staging
        env:
          DEPLOY_KEY: ${{ secrets.DEPLOY_KEY_STAGING }}
          DEPLOY_HOST: staging.gts.example.com
        run: |
          mkdir -p ~/.ssh
          echo "$DEPLOY_KEY" > ~/.ssh/deploy_key
          chmod 600 ~/.ssh/deploy_key
          ssh-keyscan -H $DEPLOY_HOST >> ~/.ssh/known_hosts
          ssh -i ~/.ssh/deploy_key deploy@$DEPLOY_HOST 'cd /app && ./deploy.sh staging'

  deploy-production:
    needs: build
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/production'
    environment:
      name: production
      url: https://gts.example.com
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Production
        env:
          DEPLOY_KEY: ${{ secrets.DEPLOY_KEY_PRODUCTION }}
          DEPLOY_HOST: gts.example.com
        run: |
          mkdir -p ~/.ssh
          echo "$DEPLOY_KEY" > ~/.ssh/deploy_key
          chmod 600 ~/.ssh/deploy_key
          ssh-keyscan -H $DEPLOY_HOST >> ~/.ssh/known_hosts
          ssh -i ~/.ssh/deploy_key deploy@$DEPLOY_HOST 'cd /app && ./deploy.sh production'
      
      - name: Notify Slack
        if: success()
        uses: slackapi/slack-github-action@v1.24.0
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK }}
          payload: |
            {
              "text": "✅ Production deployment successful",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*✅ GTS Production Deployment*\n${{ github.event.head_commit.message }}\nBy: ${{ github.actor }}"
                  }
                }
              ]
            }
```

---

#### Step 2: Create Deployment Script

**File:** `scripts/deploy.sh`

```bash
#!/bin/bash
set -e

ENVIRONMENT=$1
LOG_FILE="/var/log/gts/deploy-${ENVIRONMENT}-$(date +%Y%m%d-%H%M%S).log"

log() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

log "Starting $ENVIRONMENT deployment..."

# 1. Pull latest code
log "Pulling latest code..."
cd /app
git pull origin $([ "$ENVIRONMENT" = "production" ] && echo "production" || echo "main")

# 2. Install dependencies
log "Installing dependencies..."
python -m pip install -r backend/requirements.txt

# 3. Run database migrations
log "Running database migrations..."
alembic -c backend/alembic.ini upgrade head

# 4. Run security tests
log "Running security tests..."
pytest tests/test_security.py -v

# 5. Build/start services
log "Building Docker image..."
docker build -t gts:${ENVIRONMENT} \
  --build-arg ENVIRONMENT=$ENVIRONMENT \
  --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
  .

# 6. Stop old container
log "Stopping old container..."
docker stop gts-${ENVIRONMENT} || true
docker rm gts-${ENVIRONMENT} || true

# 7. Start new container
log "Starting new container..."
docker run -d \
  --name gts-${ENVIRONMENT} \
  --env-file /app/.env.${ENVIRONMENT} \
  --volume /data/gts:/data \
  --volume /var/log/gts:/app/logs \
  --network prod-network \
  -p $([ "$ENVIRONMENT" = "production" ] && echo "8000" || echo "8001"):8000 \
  gts:${ENVIRONMENT}

# 8. Health check
log "Performing health check..."
for i in {1..30}; do
  if curl -sf http://localhost:$([ "$ENVIRONMENT" = "production" ] && echo "8000" || echo "8001")/health > /dev/null; then
    log "✅ Health check passed!"
    break
  fi
  log "Health check attempt $i/30..."
  sleep 2
done

log "✅ $ENVIRONMENT deployment completed successfully!"
```

---

### PART 4: Monitoring & Observability

#### Step 1: Set up Sentry (Error Tracking)

**File:** `backend/config.py` (add)

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

if not DEBUG:
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
        ],
        traces_sample_rate=0.1,  # 10% of requests
        environment=ENVIRONMENT,
        release=os.getenv("APP_VERSION", "unknown"),
    )
```

**Features:**
- ✅ Automatic error tracking
- ✅ Performance monitoring
- ✅ Session replay (paid feature)
- ✅ Release tracking
- ✅ Team alerts

---

#### Step 2: Set up Prometheus Metrics

**File:** `backend/middleware/metrics.py` (new)

```python
from prometheus_client import Counter, Histogram, Gauge
import time

# Request metrics
request_count = Counter(
    'gts_requests_total',
    'Total requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'gts_request_duration_seconds',
    'Request duration',
    ['method', 'endpoint']
)

# Business metrics
active_users = Gauge(
    'gts_active_users',
    'Number of active users'
)

database_connections = Gauge(
    'gts_database_connections',
    'Active database connections'
)

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Record request metrics"""
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    request_count.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    request_duration.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    return response

@app.get("/metrics")
async def metrics():
    """Expose Prometheus metrics"""
    from prometheus_client import generate_latest
    return Response(generate_latest(), media_type="text/plain")
```

---

#### Step 3: Set up Grafana Dashboard

**File:** `infrastructure/grafana/dashboard.json`

```json
{
  "dashboard": {
    "title": "GTS Production Dashboard",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(gts_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Response Time (P95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, gts_request_duration_seconds)"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(gts_requests_total{status=~\"5..\"}[5m])"
          }
        ]
      },
      {
        "title": "Active Users",
        "targets": [
          {
            "expr": "gts_active_users"
          }
        ]
      },
      {
        "title": "Database Connections",
        "targets": [
          {
            "expr": "gts_database_connections"
          }
        ]
      }
    ]
  }
}
```

---

### PART 5: Database Management

#### Step 1: Automated Backups

**File:** `scripts/backup.sh`

```bash
#!/bin/bash

BACKUP_DIR="/backups/gts"
RETENTION_DAYS=30
DATABASE_URL=$1

mkdir -p $BACKUP_DIR

# Create backup
BACKUP_FILE="$BACKUP_DIR/gts_$(date +%Y%m%d_%H%M%S).sql"
pg_dump $DATABASE_URL > $BACKUP_FILE
gzip $BACKUP_FILE

log "✅ Backup created: ${BACKUP_FILE}.gz"

# Retain last N days
find $BACKUP_DIR -name "gts_*.sql.gz" -mtime +$RETENTION_DAYS -delete

log "✅ Old backups cleaned (retention: $RETENTION_DAYS days)"
```

**Cron job (daily 2 AM):**
```bash
0 2 * * * /app/scripts/backup.sh $DATABASE_URL >> /var/log/gts/backup.log 2>&1
```

---

### PART 6: Security Hardening

#### Final Checklist

- [ ] CORS restricted to specific origin
- [ ] HTTPS enforced (HTTP redirects)
- [ ] HSTS header enabled (1 year)
- [ ] Rate limiting configured
- [ ] Security headers all present
- [ ] Database password changed
- [ ] API keys rotated
- [ ] Secrets not in code/git
- [ ] Database backups tested
- [ ] Disaster recovery plan ready

---

### PART 7: Documentation

#### Deployment Runbook

**File:** `docs/DEPLOYMENT_RUNBOOK.md`

```markdown
# Deployment Runbook

## Pre-Deployment Checklist
- [ ] All tests pass locally
- [ ] Security tests pass
- [ ] Code reviewed and approved
- [ ] Database migration tested
- [ ] No breaking changes

## Deployment Process

### 1. Staging Deployment (Automatic on main branch)
```
1. Tests run automatically
2. Docker image built
3. Deployed to staging automatically
4. Manual smoke tests performed
```

### 2. Production Deployment (Manual trigger)
```
1. Push to production branch
2. CI/CD pipeline runs all checks
3. Manual approval required in GitHub
4. Deployment executed
5. Slack notification sent
```

## Post-Deployment Steps
1. [ ] Verify application health: `curl https://gts.example.com/health`
2. [ ] Check logs: `docker logs gts-production`
3. [ ] Monitor error tracking: Sentry dashboard
4. [ ] Monitor metrics: Grafana dashboard
5. [ ] Run smoke tests

## Rollback Procedure
```bash
# Identify previous version
docker image ls gts

# Stop current container
docker stop gts-production

# Start previous version
docker run -d --name gts-production-rollback \
  --env-file /app/.env.production \
  gts:previous-version

# Verify
curl https://gts.example.com/health
```

## Troubleshooting

### High Error Rate
1. Check logs: `docker logs gts-production | tail -100`
2. Check database: `psql -c "SELECT COUNT(*) FROM users;"`
3. Rollback if needed

### Slow Response Times
1. Check metrics: Grafana dashboard
2. Check database connections: `docker exec gts-production psql -c "SELECT COUNT(*) FROM pg_stat_activity;"`
3. Clear cache if needed

### Database Connection Issues
1. Check database URL in .env
2. Test connection: `psql -c "SELECT 1;"`
3. Restart database if needed
```

---

## 🚀 Getting Started with Phase 5

### Week 1: Foundation
- [ ] Part 1: Environment configuration (2 hours)
- [ ] Part 2: SSL/TLS setup (1 hour)
- [ ] Part 3: CI/CD pipeline (3 hours)

### Week 2: Observability & Hardening
- [ ] Part 4: Monitoring setup (3 hours)
- [ ] Part 5: Database management (1.5 hours)
- [ ] Part 6: Security hardening (2 hours)

### Week 3: Documentation & Testing
- [ ] Part 7: Documentation (2 hours)
- [ ] Full end-to-end testing
- [ ] Final security audit
- [ ] Launch! 🎉

---

## Success Criteria for Phase 5

### Infrastructure ✅
- [ ] Application deployed to production server
- [ ] SSL/TLS certificate installed and working
- [ ] HTTPS enforced for all traffic
- [ ] Domain DNS pointing to production server

### CI/CD ✅
- [ ] GitHub Actions pipeline created
- [ ] Tests run automatically on push
- [ ] Staging deployment automatic
- [ ] Production deployment requires manual approval
- [ ] Rollback procedure tested

### Monitoring ✅
- [ ] Sentry tracking errors
- [ ] Prometheus collecting metrics
- [ ] Grafana dashboard displaying data
- [ ] Alerts configured for critical issues
- [ ] Log aggregation working

### Security ✅
- [ ] CORS restricted to production domain
- [ ] All security headers present
- [ ] Rate limiting active
- [ ] Database backups automated
- [ ] Disaster recovery tested

### Documentation ✅
- [ ] Deployment runbook complete
- [ ] Incident response procedures documented
- [ ] Troubleshooting guide created
- [ ] API documentation updated
- [ ] User guides available

**Overall Phase 5 Success:** All criteria met → **READY FOR PRODUCTION** 🚀

---

## Estimated Timeline

| Phase | Duration | Status |
|-------|----------|--------|
| Phase 1: Smart Agent Prep | 1 day | ✅ Complete |
| Phase 2: Testing & Readiness | 1 day | ✅ Complete |
| Phase 3: Load Test & Optimize | 1 day | ✅ Complete (10.4x improvement) |
| Phase 4: Security Testing | 1 day | ✅ Complete (Grade A-) |
| Phase 5: Production Deployment | 2-3 days | ⏳ **IN PROGRESS** |
| **TOTAL** | **~1 week** | 80% Complete |

---

## Next Steps

1. ✅ Review Phase 5 roadmap above
2. ⏳ Start with Part 1: Environment Configuration
3. Continue through each part sequentially
4. Test each part before moving to next
5. Final security audit before launch

---

**Phase 5 Status:** ⏳ **IN PROGRESS**  
**Target Completion:** February 5-6, 2026  
**Production Launch:** February 6, 2026 🚀
