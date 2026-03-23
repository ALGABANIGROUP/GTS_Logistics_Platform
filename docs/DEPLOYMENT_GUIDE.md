# Phase 5: Production Deployment Guide

## 📋 Table of Contents
1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Environment Setup](#environment-setup)
3. [SSL/TLS Configuration](#ssltls-configuration)
4. [Deployment Process](#deployment-process)
5. [Post-Deployment Verification](#post-deployment-verification)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Troubleshooting](#troubleshooting)
8. [Rollback Procedures](#rollback-procedures)

---

## Pre-Deployment Checklist

### Code Quality ✅
- [ ] All tests pass locally
- [ ] Security tests pass (13/24)
- [ ] Code reviewed and approved
- [ ] No console errors or warnings
- [ ] No deprecated functions used

### Database ✅
- [ ] Database migration tested
- [ ] Backup strategy verified
- [ ] Connection pooling configured
- [ ] All migrations in version control

### Security ✅
- [ ] Secrets not in code
- [ ] Environment configuration created
- [ ] SSL/TLS certificate ready
- [ ] Security headers configured
- [ ] Rate limiting enabled

### Infrastructure ✅
- [ ] Production server ready
- [ ] Docker daemon running
- [ ] Network configuration complete
- [ ] Storage volumes mounted
- [ ] Backup storage available

### Monitoring ✅
- [ ] Sentry DSN configured
- [ ] Slack webhook configured
- [ ] Log collection setup
- [ ] Metrics collection ready
- [ ] Alert thresholds defined

---

## Environment Setup

### Step 1: Create Production .env File

```bash
# On production server
mkdir -p /app/config
nano /app/config/.env.production
```

Required variables:
```env
DEBUG=False
ENVIRONMENT=production
DATABASE_URL=postgresql+asyncpg://...@...?ssl=require
SECRET_KEY=<generate-new-key>
JWT_SECRET=<generate-new-key>
CORS_ORIGINS=https://gts.example.com
SENTRY_DSN=<sentry-production-dsn>
SLACK_WEBHOOK_URL=<slack-webhook>
```

**Security Note:** Store secrets in secure location, not in git:
```bash
# Proper secret management
chmod 600 /app/config/.env.production
export $(cat /app/config/.env.production | xargs)
```

### Step 2: Create Required Directories

```bash
# Create necessary directories
mkdir -p /data/gts
mkdir -p /var/log/gts
mkdir -p /backups/gts

# Set proper permissions
chown -R appuser:appuser /data/gts
chown -R appuser:appuser /var/log/gts
chown -R appuser:appuser /backups/gts

chmod 755 /data/gts
chmod 755 /var/log/gts
chmod 755 /backups/gts
```

### Step 3: Set Up Docker Network

```bash
# Create custom network for services
docker network create prod-network

# Verify network
docker network ls
```

### Step 4: Start Redis (for caching)

```bash
docker run -d \
  --name gts-redis \
  --network prod-network \
  -v /data/redis:/data \
  --restart=unless-stopped \
  redis:7-alpine \
  redis-server --appendonly yes
```

### Step 5: Start PostgreSQL (if not using managed database)

```bash
docker run -d \
  --name gts-postgres \
  --network prod-network \
  -e POSTGRES_DB=gts_production \
  -e POSTGRES_USER=gts_user \
  -e POSTGRES_PASSWORD=<strong-password> \
  -v /data/postgres:/var/lib/postgresql/data \
  --restart=unless-stopped \
  postgres:15-alpine
```

---

## SSL/TLS Configuration

### Option A: Let's Encrypt (Recommended)

```bash
# Install certbot and nginx
sudo apt-get install certbot python3-certbot-nginx nginx

# Generate certificate
sudo certbot certonly --nginx \
  -d gts.example.com \
  -d www.gts.example.com \
  --email admin@gts.example.com \
  --agree-tos \
  --non-interactive

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### Option B: AWS Certificate Manager

```bash
# If using AWS ALB
aws acm request-certificate \
  --domain-name gts.example.com \
  --subject-alternative-names www.gts.example.com \
  --validation-method DNS
```

### Nginx Configuration

```bash
# Create Nginx config
sudo nano /etc/nginx/sites-available/gts.conf
```

```nginx
upstream gts_backend {
    server localhost:8000;
}

server {
    listen 80;
    server_name gts.example.com www.gts.example.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name gts.example.com www.gts.example.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/gts.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/gts.example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Logging
    access_log /var/log/nginx/gts_access.log;
    error_log /var/log/nginx/gts_error.log;
    
    # Proxy configuration
    location / {
        proxy_pass http://gts_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
    
    # WebSocket support
    location /api/v1/ws/live {
        proxy_pass http://gts_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        proxy_pass http://gts_backend;
    }
}
```

Enable and restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/gts.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Deployment Process

### Automated CI/CD Deployment

**Trigger:** Push to `production` branch

```bash
# 1. Local development
git checkout -b feature/new-feature
# ... make changes and test ...

# 2. Push to staging
git push origin main  # Triggers staging deployment

# 3. Verify in staging
# Test at https://staging.gts.example.com

# 4. Merge to production
git checkout production
git merge main

# 5. Push to production
git push origin production  # Triggers production deployment
# GitHub Actions workflow runs automatically

# 6. Manual approval in GitHub
# Visit: https://github.com/your-org/gts/actions
# Review and approve production deployment

# 7. Deployment executes
# - Tests run
# - Docker image built and pushed
# - Application deployed
# - Health checks performed
# - Slack notification sent
```

### Manual Deployment (if needed)

```bash
# SSH to production server
ssh deploy@gts.example.com

# Run deployment script
cd /app
bash scripts/deploy.sh production deploy

# Monitor logs
docker logs -f gts-production

# Check health
curl https://gts.example.com/health
```

---

## Post-Deployment Verification

### Immediate Checks (First 5 minutes)

```bash
# 1. Application health
curl https://gts.example.com/health
# Expected: {"status": "healthy"}

# 2. Check logs for errors
docker logs gts-production | tail -50

# 3. API availability
curl -H "Authorization: Bearer test" https://gts.example.com/api/v1/health
# Expected: 200 OK or 401 Unauthorized (but no 500 errors)

# 4. Database connectivity
docker exec gts-postgres psql -U gts_user -d gts_production -c "SELECT COUNT(*) FROM users;"
# Expected: positive number

# 5. WebSocket connection
curl -i -N -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  https://gts.example.com/api/v1/ws/live
# Expected: 101 Switching Protocols
```

### First Hour Checks

```bash
# 1. Error tracking
# Visit Sentry dashboard
# Check for new errors

# 2. Performance metrics
# Visit Grafana dashboard
# Check response times and error rates

# 3. Logs
# Check log aggregation system
# Verify no unusual patterns

# 4. User activity
# Monitor active users
# Check transaction processing
```

### First Day Checks

```bash
# 1. Security scan
# Run security header checks
curl -I https://gts.example.com
# Verify all security headers present

# 2. Performance baseline
# Compare against Phase 3 load test results
# Ensure no degradation

# 3. Database backup
# Verify daily backup completed
# Test backup restoration (in staging)

# 4. Team feedback
# Gather feedback from team
# Check for user-reported issues
```

---

## Monitoring & Maintenance

### Daily Tasks

```bash
# Check application health
docker ps -a | grep gts-production

# Review logs for errors
docker logs gts-production | grep ERROR

# Check disk usage
df -h /data/gts

# Verify backup completed
ls -lh /backups/gts/gts_backup_*.sql.gz | head -1
```

### Weekly Tasks

```bash
# Update dependencies
pip install --upgrade -r backend/requirements.txt

# Database optimization
docker exec gts-postgres \
  psql -U gts_user -d gts_production -c "VACUUM ANALYZE;"

# Review security logs
docker logs gts-production | grep -i "failed\|error\|unauthorized"

# Test backup restoration (staging only)
bash scripts/backup.sh /backups/gts 30  # Run backup
# Then restore in staging and verify
```

### Monthly Tasks

```bash
# Full security audit
pytest tests/test_security.py

# Database maintenance
# - Check index performance
# - Analyze table sizes
# - Review query logs

# Certificate verification
# Let's Encrypt auto-renews, but verify
sudo certbot renew --dry-run

# Update dependencies
# - Review security updates
# - Test in staging first
# - Deploy if no issues
```

---

## Troubleshooting

### Application Won't Start

```bash
# 1. Check logs
docker logs gts-production

# 2. Check environment variables
docker inspect gts-production | grep Env

# 3. Check database connection
docker exec gts-production python -c \
  "from backend.database.session import AsyncSessionLocal; print('✅ DB connection OK')"

# 4. Check migrations
docker exec gts-production alembic -c backend/alembic.ini current

# 5. Rollback if needed
bash scripts/deploy.sh production rollback
```

### High Error Rate

```bash
# 1. Check Sentry for error patterns
# Visit sentry.io dashboard

# 2. Check logs
docker logs gts-production | grep ERROR | tail -20

# 3. Check database
docker exec gts-postgres \
  psql -U gts_user -d gts_production -c "SELECT COUNT(*) FROM users;"

# 4. Check resource usage
docker stats gts-production

# 5. Potential fixes
# - Restart application: docker restart gts-production
# - Clear cache: docker exec gts-redis redis-cli FLUSHDB
# - Rollback: bash scripts/deploy.sh production rollback
```

### Slow Response Times

```bash
# 1. Check metrics
# Visit Grafana dashboard

# 2. Check database connections
docker exec gts-postgres \
  psql -U gts_user -d gts_production -c "SELECT COUNT(*) FROM pg_stat_activity;"

# 3. Check query performance
docker exec gts-postgres \
  psql -U gts_user -d gts_production -c "SELECT * FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"

# 4. Check cache
docker exec gts-redis redis-cli INFO stats

# 5. Scale if needed
# Add more workers in Docker container
```

### Database Connection Issues

```bash
# 1. Verify database is running
docker ps | grep postgres

# 2. Test connection
docker exec gts-postgres \
  psql -U gts_user -d gts_production -c "SELECT version();"

# 3. Check connection pool
# DATABASE_URL shows pool parameters
grep DATABASE_URL /app/config/.env.production

# 4. Restart database if needed
docker restart gts-postgres

# 5. Check firewall/network
docker network inspect prod-network
```

---

## Rollback Procedures

### Quick Rollback (Last 1-2 Versions)

```bash
# Get list of recent images
docker image ls gts:production-* --format "table {{.Repository}}:{{.Tag}}\t{{.CreatedAt}}"

# Rollback to previous version
bash scripts/deploy.sh production rollback

# Verify
curl https://gts.example.com/health
```

### Full Rollback (if needed)

```bash
# 1. Stop current container
docker stop gts-production
docker rm gts-production

# 2. Restore database from backup
cd /backups/gts
zcat gts_backup_<date>.sql.gz | \
  docker exec -i gts-postgres \
  psql -U gts_user -d gts_production

# 3. Start previous application version
docker run -d \
  --name gts-production \
  --env-file /app/config/.env.production \
  --volume /data/gts:/data \
  --volume /var/log/gts:/app/logs \
  --network prod-network \
  -p 8000:8000 \
  --restart=unless-stopped \
  gts:production-previous

# 4. Verify
curl https://gts.example.com/health
docker logs gts-production
```

---

## Disaster Recovery

### Complete Disaster Recovery

```bash
# 1. Restore from backup (latest good state)
bash scripts/backup-restore.sh /backups/gts latest

# 2. Restart services
docker-compose -f docker-compose.production.yml up -d

# 3. Run data integrity checks
docker exec gts-postgres psql -U gts_user -d gts_production -c "SELECT COUNT(*) FROM users;"

# 4. Verify application
curl https://gts.example.com/health

# 5. Notify team
# Send Slack message about recovery
```

---

## Performance Baseline (from Phase 3)

Expected metrics after deployment:

| Metric | Value | Status |
|--------|-------|--------|
| Throughput | 17.6 req/s | ✅ Target |
| Avg Response | 1,298ms | ✅ Target |
| Login Time | 5,560ms | ✅ Target |
| Success Rate | 100% | ✅ Target |
| Errors | 0% | ✅ Target |

**If metrics degrade, initiate troubleshooting procedure above.**

---

## Success Criteria

Deployment is successful when:

✅ Application starts without errors  
✅ Health check returns 200 OK  
✅ All tests pass  
✅ No increase in error rate  
✅ Performance metrics stable  
✅ Slack notification received  
✅ Team confirms working correctly  

---

## Contact & Escalation

**Deployment Issues:** Post in #deployments Slack channel  
**Database Issues:** Contact DBA or database administrator  
**Security Issues:** Contact security team immediately  
**Production Down:** Initiate incident response procedure  

---

**Phase 5 Status:** ✅ **DEPLOYMENT GUIDE COMPLETE**  
**Next Step:** Execute Part 2-7 of Phase 5 deployment  
**Target Launch:** February 6, 2026 🚀
