# Production Server Architecture & Configuration

**Version:** 1.0  
**Status:** ✅ Production Ready  
**Last Updated:** February 3, 2026

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        GTS Production Stack                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                      Internet Users                           │  │
│  │               (HTTPS / TLS 1.2+)                             │  │
│  └──────────────────────┬───────────────────────────────────────┘  │
│                         │                                           │
│  ┌──────────────────────▼───────────────────────────────────────┐  │
│  │                    Firewall (UFW)                             │  │
│  │  • Port 80: HTTP (redirects to HTTPS)                       │  │
│  │  • Port 443: HTTPS (SSL/TLS)                                │  │
│  │  • Port 22: SSH (key-only auth)                             │  │
│  └──────────────────────┬───────────────────────────────────────┘  │
│                         │                                           │
│  ┌──────────────────────▼───────────────────────────────────────┐  │
│  │                 Nginx Reverse Proxy                           │  │
│  │                                                               │  │
│  │  • SSL/TLS Termination                                       │  │
│  │  • HTTP/2 Support                                            │  │
│  │  • Security Headers (HSTS, CSP, X-Frame-Options)            │  │
│  │  • Gzip Compression                                          │  │
│  │  • Load Balancing (to multiple app instances)               │  │
│  │  • Static File Caching                                       │  │
│  │  • Request Logging                                           │  │
│  │                                                               │  │
│  └──────────────────────┬───────────────────────────────────────┘  │
│                         │                                           │
│         ┌───────────────┼───────────────┐                         │
│         │               │               │                         │
│  ┌──────▼──────┐  ┌────▼─────┐  ┌─────▼──────┐                │
│  │   App       │  │   App    │  │   App      │                │
│  │ Instance 1  │  │ Instance │  │ Instance 3 │  (Optional)    │
│  │ Port 8000   │  │ Instance │  │ Port 8002  │                │
│  │ (Uvicorn)   │  │ Port 8001│  │ (Uvicorn)  │                │
│  └──────┬──────┘  └────┬─────┘  └─────┬──────┘                │
│         │               │               │                         │
│         └───────────────┼───────────────┘                         │
│                         │                                           │
│  ┌──────────────────────▼───────────────────────────────────────┐  │
│  │                  Supervisor                                   │  │
│  │  • Process Management                                        │  │
│  │  • Auto-restart on failure                                   │  │
│  │  • Logging to /var/log/gts/                                 │  │
│  │  • Health monitoring                                         │  │
│  └──────────────────────┬───────────────────────────────────────┘  │
│                         │                                           │
│         ┌───────────────┼───────────────┐                         │
│         │               │               │                         │
│  ┌──────▼──────┐  ┌────▼─────┐  ┌─────▼──────┐                │
│  │ PostgreSQL  │  │  Redis    │  │  Logging   │                │
│  │ Database    │  │  Cache    │  │  System    │                │
│  │ Port 5432   │  │  Port 6379│  │  /var/log/ │                │
│  │             │  │           │  │            │                │
│  │ • Backups   │  │ • Sessions│  │ • Rotation │                │
│  │ • Replication│ │ • Cache   │  │ • Archive  │                │
│  │ • SSL       │  │ • Tokens  │  │ • Analysis │                │
│  └─────────────┘  └───────────┘  └────────────┘                │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                  Monitoring & Alerts                         │  │
│  │  • Sentry: Error tracking                                   │  │
│  │  • Prometheus: Metrics collection                           │  │
│  │  • Grafana: Dashboards                                      │  │
│  │  • Health checks: Every 30 seconds                          │  │
│  │  • Slack notifications: Critical alerts                     │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🖥️ Server Specifications

### Recommended Hardware
```
CPU:        4+ cores (2.0+ GHz)
RAM:        8GB minimum (16GB recommended)
Storage:    50GB+ SSD (100GB+ with backups)
Bandwidth:  Unlimited or 10Mbps+
Network:    Public IP with stable connectivity
```

### Operating System
```
Distribution:    Ubuntu 20.04 LTS or 22.04 LTS
Kernel:          5.4+
Compiler:        GCC 9+
Python:          3.11
Node.js:         18+ (for frontend assets)
```

---

## 📋 Installation Order

### 1. System Setup (30 min)
```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install essential tools
sudo apt-get install -y curl wget git vim htop build-essential

# Configure timezone
sudo timedatectl set-timezone UTC
```

### 2. Database (30 min)
```bash
# Install PostgreSQL
sudo apt-get install -y postgresql postgresql-contrib

# Create database and user
sudo -u postgres createdb gts_production
sudo -u postgres createuser gts
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE gts_production TO gts;"
```

### 3. Cache (10 min)
```bash
# Install Redis
sudo apt-get install -y redis-server

# Enable and start
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

### 4. Reverse Proxy (20 min)
```bash
# Install Nginx
sudo apt-get install -y nginx

# Copy configuration
sudo cp nginx.conf /etc/nginx/nginx.conf

# Test and enable
sudo nginx -t
sudo systemctl enable nginx
sudo systemctl start nginx
```

### 5. Runtime (20 min)
```bash
# Install Python
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev

# Install Node.js
sudo apt-get install -y nodejs npm

# Install Supervisor
sudo apt-get install -y supervisor
```

### 6. Application (20 min)
```bash
# Create app user
sudo useradd -m -s /bin/bash gts

# Create directories
sudo mkdir -p /opt/gts/{app,logs,data,backups}
sudo chown -R gts:gts /opt/gts

# Clone application
cd /opt/gts/app
sudo -u gts git clone <repo> .
```

### 7. SSL/TLS (15 min)
```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Create certificate
sudo certbot certonly --nginx -d gts.example.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

---

## 🔐 Security Configuration

### Firewall Rules
```bash
# Enable UFW
sudo ufw enable

# SSH
sudo ufw allow 22/tcp

# HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Verify
sudo ufw status
```

### SSH Hardening
```bash
# Edit /etc/ssh/sshd_config
PermitRootLogin no
PubkeyAuthentication yes
PasswordAuthentication no
PermitEmptyPasswords no
X11Forwarding no
MaxAuthTries 3
MaxSessions 5

# Restart SSH
sudo systemctl restart sshd
```

### System Hardening
```bash
# Install fail2ban
sudo apt-get install -y fail2ban

# Enable unattended security updates
sudo apt-get install -y unattended-upgrades

# Configure automatic security updates
sudo dpkg-reconfigure -plow unattended-upgrades
```

---

## 📊 Performance Tuning

### Nginx Configuration
```nginx
# /etc/nginx/nginx.conf
worker_processes auto;
worker_connections 4096;
keepalive_timeout 65;
gzip on;
gzip_comp_level 6;
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=gts:10m;
```

### PostgreSQL Configuration
```sql
-- /etc/postgresql/*/main/postgresql.conf
max_connections = 200
shared_buffers = 256MB
effective_cache_size = 2GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
```

### Redis Configuration
```conf
# /etc/redis/redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
appendonly yes
appendfsync everysec
```

### Application (Uvicorn)
```bash
# Supervisor configuration
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
worker_timeout = 120
timeout_keep_alive = 65
```

---

## 📈 Monitoring Setup

### Logging
```bash
# Application logs
/var/log/gts/app.log

# Nginx logs
/var/log/nginx/gts-access.log
/var/log/nginx/gts-error.log

# System logs
journalctl -u supervisor
journalctl -u nginx
journalctl -u postgresql
```

### Health Checks
```bash
# Application health
curl https://gts.example.com/api/v1/health

# Database health
psql -U gts -d gts_production -c "SELECT 1;"

# Redis health
redis-cli ping

# Nginx health
systemctl status nginx
```

### Metrics to Track
```
Application:
  - Request rate (req/s)
  - Response time (ms)
  - Error rate (%)
  - Success rate (%)

System:
  - CPU usage (%)
  - Memory usage (GB)
  - Disk usage (%)
  - Network I/O (Mbps)

Database:
  - Connection count
  - Query time (ms)
  - Cache hit ratio (%)
  - Replication lag (ms)
```

---

## 🔄 Backup & Recovery

### Automated Backups
```bash
# Database backups (daily at 2 AM)
0 2 * * * pg_dump -U gts gts_production | gzip > /opt/gts/backups/db_$(date +\%Y\%m\%d).sql.gz

# Application files (daily)
0 3 * * * tar -czf /opt/gts/backups/app_$(date +\%Y\%m\%d).tar.gz /opt/gts/app

# Config files (daily)
0 4 * * * tar -czf /opt/gts/backups/config_$(date +\%Y\%m\%d).tar.gz /etc/nginx /etc/postgresql
```

### Backup Retention
```
Daily backups: Keep last 30 days
Weekly backups: Keep last 12 weeks
Monthly backups: Keep last 12 months
```

### Recovery Procedure
```bash
# 1. Restore database
gunzip < /opt/gts/backups/db_20260206.sql.gz | psql -U gts gts_production

# 2. Restore application
tar -xzf /opt/gts/backups/app_20260206.tar.gz -C /opt/gts/

# 3. Restore configuration
tar -xzf /opt/gts/backups/config_20260206.tar.gz -C /

# 4. Restart services
sudo systemctl restart nginx postgresql redis-server supervisor
```

---

## ⚠️ Disaster Recovery

### RTO & RPO Targets
```
Recovery Time Objective (RTO):    1 hour
Recovery Point Objective (RPO):   15 minutes
```

### Failover Procedure
```bash
# 1. Assess impact
  - Check monitoring dashboards
  - Review error logs
  - Assess database integrity

# 2. Prepare recovery
  - SSH to standby server
  - Verify backup availability
  - Start recovery services

# 3. Restore from backup
  - Restore database
  - Restore application
  - Restore configuration

# 4. Verify recovery
  - Run smoke tests
  - Check health endpoints
  - Monitor error rates

# 5. Update DNS (if needed)
  - Point domain to new IP
  - Wait for DNS propagation
  - Verify connectivity
```

---

## 📞 Operations Contacts

### Primary Contacts
- **Lead Engineer**: [Name/Contact]
- **DevOps Engineer**: [Name/Contact]
- **On-Call Rotation**: [Schedule Link]

### Escalation
- **P1 (Critical)**: Page on-call engineer
- **P2 (High)**: Notify team lead within 15 min
- **P3 (Medium)**: Notify team within 1 hour
- **P4 (Low)**: Log ticket for next review

---

## ✅ Deployment Verification

Run after deployment:

```bash
# 1. System Check
hostnamectl
uname -r
df -h

# 2. Services Check
systemctl status nginx postgresql redis-server supervisor

# 3. Application Check
curl -v https://gts.example.com/api/v1/health

# 4. Security Check
openssl x509 -in /etc/letsencrypt/live/gts.example.com/fullchain.pem -noout

# 5. Database Check
psql -U gts -d gts_production -c "SELECT version();"

# 6. Monitoring Check
curl http://localhost:9090/api/v1/query?query=up

# 7. Logs Check
tail -20 /var/log/gts/app.log
tail -20 /var/log/nginx/gts-error.log
```

---

**Production Server Configuration Complete! ✅**

Next: Deploy application and run smoke tests.
