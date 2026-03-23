# Phase 5: Final Deployment Procedures

**Status:** 📋 Ready for Production  
**Last Updated:** February 3, 2026  
**Target Launch:** February 6, 2026

---

## 🎯 4-Step Production Launch Plan

This document outlines the final steps to deploy GTS to production.

---

## Step 1: SSL/TLS Certificate Setup (1-2 hours)

### ✅ Before You Start

- [ ] Domain DNS is pointing to production server
- [ ] Production server is running Ubuntu 20.04+
- [ ] Port 80 and 443 are open
- [ ] You have SSH access to the server
- [ ] Email for Let's Encrypt certificate recovery

### 📋 Procedure

```bash
# 1. Connect to production server
ssh ubuntu@production.example.com

# 2. Download SSL setup script
wget https://your-repo/scripts/setup-ssl-letsencrypt.sh
chmod +x setup-ssl-letsencrypt.sh

# 3. Run SSL setup (replace with your domain and email)
sudo ./setup-ssl-letsencrypt.sh gts.example.com admin@gts.example.com

# 4. The script will:
#    - Install Certbot
#    - Create Let's Encrypt certificate
#    - Configure Nginx with SSL
#    - Enable automatic renewal
#    - Test HTTPS connectivity
```

### ✅ Verification

```bash
# Check certificate is installed
curl https://gts.example.com/health

# Verify certificate details
openssl x509 -in /etc/letsencrypt/live/gts.example.com/fullchain.pem -noout -text

# Check SSL score (should be A or A+)
curl https://ssl-test-server.com/api/analyze?host=gts.example.com
```

### ⏱️ Expected Time: 10-15 minutes

---

## Step 2: Nginx Reverse Proxy Setup (30 minutes)

### ✅ Prerequisites

- [ ] SSL certificate from Step 1 is installed
- [ ] Backend application will run on port 8000
- [ ] Nginx is installed

### 📋 Procedure

```bash
# 1. Copy Nginx configuration
sudo cp nginx.conf /etc/nginx/nginx.conf

# 2. Update domain in Nginx config
sudo sed -i 's/gts.example.com/your-domain.com/g' /etc/nginx/nginx.conf

# 3. Test Nginx configuration
sudo nginx -t

# 4. Reload Nginx
sudo systemctl reload nginx

# 5. Verify Nginx is running
sudo systemctl status nginx
```

### ✅ Verification

```bash
# Check Nginx is proxying correctly
curl -v https://gts.example.com/api/v1/health

# Check for security headers
curl -I https://gts.example.com | grep -i "strict-transport-security"
```

### ⏱️ Expected Time: 5-10 minutes

---

## Step 3: Production Server Provisioning (1-2 hours)

### ✅ Prerequisites

- [ ] Fresh Ubuntu 20.04+ server (4GB RAM minimum)
- [ ] Root or sudo access
- [ ] Domain is set up from Step 1
- [ ] Nginx from Step 2 is running

### 📋 Procedure

```bash
# 1. Connect to production server as root
ssh root@production.example.com

# 2. Download provisioning script
wget https://your-repo/scripts/provision-production-server.sh
chmod +x provision-production-server.sh

# 3. Run provisioning
./provision-production-server.sh

# The script will:
#    - Update system packages
#    - Install Python, Node.js, PostgreSQL, Redis
#    - Create application user
#    - Create directories
#    - Configure services
#    - Generate provisioning report
```

### 📋 After Provisioning

```bash
# 1. Navigate to app directory
cd /opt/gts/app

# 2. Clone or copy GTS repository
git clone https://github.com/your-org/gts.git .

# 3. Activate virtual environment
source ../venv/bin/activate

# 4. Install Python dependencies
pip install -r requirements.txt

# 5. Copy production environment file
cp backend/.env.production /opt/gts/app/
# Edit with actual values:
# - SECRET_KEY (generate with: python -c 'import secrets; print(secrets.token_urlsafe(32))')
# - DATABASE_URL (with actual password)
# - STRIPE_KEY, AWS_KEY, etc.

# 6. Run database migrations
alembic upgrade head

# 7. Start application via Supervisor
supervisorctl start gts
```

### ✅ Verification

```bash
# Check application is running
supervisorctl status gts

# Check logs
tail -f /var/log/gts/app.log

# Test health endpoint
curl https://gts.example.com/api/v1/health
```

### ⏱️ Expected Time: 45 minutes - 2 hours

---

## Step 4: Final Smoke Tests (30 minutes)

### ✅ Before Running Tests

- [ ] All 3 previous steps completed
- [ ] Application is running
- [ ] HTTPS certificate is valid

### 📋 Procedure

```bash
# 1. Download smoke tests script
wget https://your-repo/scripts/smoke-tests.sh
chmod +x smoke-tests.sh

# 2. Run smoke tests (update domain)
BASE_URL=https://gts.example.com ./smoke-tests.sh

# Tests performed:
#    ✓ Server connectivity
#    ✓ SSL/TLS certificate validity
#    ✓ HTTP to HTTPS redirect
#    ✓ Health endpoint
#    ✓ Authentication endpoint
#    ✓ Security headers
#    ✓ Response time
#    ✓ Database connectivity
#    ✓ WebSocket support
#    ✓ CORS configuration
#    ✓ API response format
#    ✓ Rate limiting
#    ✓ Nginx status
#    ✓ Application logs
#    ✓ Database backups
```

### ✅ Expected Results

```
Smoke Test Summary Report
════════════════════════════════════════
Total Tests: 15
Passed: 15
Failed: 0

Pass Rate: 100%

✓ All smoke tests passed! Application is ready for use.
```

### 🚨 If Tests Fail

1. Check logs: `tail -f /var/log/gts/app.log`
2. Verify Nginx: `sudo nginx -t && sudo systemctl restart nginx`
3. Check database: `psql -U gts -d gts_production`
4. Restart app: `sudo supervisorctl restart gts`

### ⏱️ Expected Time: 15-20 minutes

---

## 📊 Complete Launch Timeline

```
┌─────────────────────────────────────────────────────────────┐
│ Phase 5: Production Launch Timeline                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Step 1: SSL/TLS Setup             ████████ 15 min         │
│ Step 2: Nginx Configuration       ██████ 10 min           │
│ Step 3: Server Provisioning       ████████████ 90 min     │
│ Step 4: Smoke Tests               ██████ 20 min           │
│                                                             │
│ Total Time: ~2-3 hours                                    │
│ Status: 🟢 READY                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ Pre-Launch Checklist

### Infrastructure
- [ ] Production server provisioned
- [ ] Database configured and tested
- [ ] Redis cache working
- [ ] SSL/TLS certificate installed
- [ ] Nginx reverse proxy configured
- [ ] Health endpoint responds (200)

### Application
- [ ] Code deployed to production
- [ ] Environment variables configured
- [ ] Database migrations run
- [ ] Secret keys generated and stored
- [ ] API keys configured (Stripe, AWS, etc.)
- [ ] Logging configured

### Security
- [ ] HTTPS enforced (HTTP redirects to HTTPS)
- [ ] Security headers present
- [ ] CORS properly configured
- [ ] Rate limiting active
- [ ] Firewall rules set
- [ ] SSH hardened (key-only auth)

### Monitoring
- [ ] Application logs accessible
- [ ] Error tracking configured
- [ ] Performance metrics setup
- [ ] Alerts configured
- [ ] Backup script running
- [ ] Certificate renewal set

### Testing
- [ ] Unit tests pass (95%+)
- [ ] Security tests pass (54%+)
- [ ] Load tests verify 10.4x performance
- [ ] Smoke tests all pass (15/15)
- [ ] Manual testing complete

### Operations
- [ ] On-call schedule setup
- [ ] Escalation procedures documented
- [ ] Runbooks available
- [ ] Incident response plan ready
- [ ] Team trained
- [ ] Communication channels active

---

## 🎯 Success Criteria

### Immediate (First 5 minutes)
- [ ] Application accessible at https://gts.example.com
- [ ] Health endpoint returns 200 OK
- [ ] No 500 errors in logs
- [ ] HTTPS certificate valid

### First Hour
- [ ] All 15 smoke tests passing
- [ ] Response times < 2000ms
- [ ] Error rate < 0.1%
- [ ] Database operations normal
- [ ] WebSocket connections stable

### First Day
- [ ] Performance stable (17.6 req/s maintained)
- [ ] No critical errors
- [ ] User feedback positive
- [ ] Monitoring dashboards updated
- [ ] Backup completed

### Ongoing
- [ ] Uptime > 99.9%
- [ ] Certificate auto-renews successfully
- [ ] Security patches applied
- [ ] Backups run automatically
- [ ] Team responds to issues < 5 min

---

## 📞 Support Resources

### During Launch
- **Production Server**: [IP/Domain]
- **SSH Access**: `ssh ubuntu@gts.example.com`
- **Application Logs**: `/var/log/gts/app.log`
- **Nginx Logs**: `/var/log/nginx/gts-error.log`

### Quick Commands
```bash
# Check app status
sudo supervisorctl status gts

# View app logs
sudo tail -f /var/log/gts/app.log

# Restart application
sudo supervisorctl restart gts

# Check SSL certificate expiration
openssl x509 -in /etc/letsencrypt/live/gts.example.com/fullchain.pem -noout -dates

# Check system resources
htop

# Backup database manually
sudo -u postgres pg_dump gts_production > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Troubleshooting
- **App won't start**: Check logs, verify database connection, check env vars
- **HTTPS errors**: Verify certificate, check Nginx config, test with curl
- **Slow response**: Check database, monitor CPU/RAM, check logs for errors
- **High error rate**: Check external API connectivity, verify database, check logs

---

## 🚀 Launch Go/No-Go Decision

**Decision Date**: February 6, 2026, 9:00 AM UTC

| Component | Status | Owner | Sign-off |
|-----------|--------|-------|----------|
| Infrastructure | ✅ Ready | DevOps | _____ |
| Application | ✅ Ready | Backend | _____ |
| Security | ✅ Ready | Security | _____ |
| Monitoring | ✅ Ready | Operations | _____ |
| Documentation | ✅ Ready | Technical | _____ |
| Team Readiness | ✅ Ready | Team Lead | _____ |

**Final Decision**: 
- [ ] **GO** - Proceed with production launch
- [ ] **NO-GO** - Postpone launch and document issues

---

## 📝 Post-Launch Notes

After launch, update this section with actual results:

```
Launch Date/Time: _________________
Completed By: _________________
Duration: _________________
Issues Encountered: _________________
Resolution: _________________
Final Status: _________________
```

---

**GTS Production Launch Complete! 🎉**

Next: Monitor application and respond to any issues.
