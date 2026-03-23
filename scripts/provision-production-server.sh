#!/bin/bash

################################################################################
# Production Server Provisioning Script for GTS
################################################################################

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[!]${NC} $1"; }
log_error() { echo -e "${RED}[✗]${NC} $1"; }

################################################################################
# CONFIGURATION
################################################################################

APP_USER="gts"
APP_GROUP="gts"
APP_HOME="/opt/gts"
APP_PORT=8000
ENVIRONMENT="${ENVIRONMENT:-production}"
DOMAIN="${DOMAIN:-gts.example.com}"
EMAIL="${EMAIL:-admin@gts.example.com}"

################################################################################
# STEP 1: SYSTEM UPDATES
################################################################################

provision_step_updates() {
    log_info "Step 1/10: Updating system packages..."
    
    apt-get update > /dev/null 2>&1
    apt-get upgrade -y > /dev/null 2>&1
    apt-get install -y \
        curl wget git vim htop nano \
        build-essential libssl-dev libffi-dev \
        postgresql-client \
        > /dev/null 2>&1
    
    log_success "System packages updated"
}

################################################################################
# STEP 2: INSTALL RUNTIME DEPENDENCIES
################################################################################

provision_step_runtime() {
    log_info "Step 2/10: Installing runtime dependencies..."
    
    apt-get install -y \
        python3.11 python3.11-venv python3.11-dev \
        nodejs npm \
        nginx \
        certbot python3-certbot-nginx \
        redis-server \
        postgresql \
        supervisor \
        > /dev/null 2>&1
    
    log_success "Runtime dependencies installed"
}

################################################################################
# STEP 3: CREATE APPLICATION USER
################################################################################

provision_step_user() {
    log_info "Step 3/10: Creating application user..."
    
    # Create user if doesn't exist
    if ! id "$APP_USER" &>/dev/null; then
        useradd -m -s /bin/bash -d "$APP_HOME" "$APP_USER"
        log_success "User $APP_USER created"
    else
        log_warning "User $APP_USER already exists"
    fi
}

################################################################################
# STEP 4: CREATE APPLICATION DIRECTORIES
################################################################################

provision_step_directories() {
    log_info "Step 4/10: Creating application directories..."
    
    mkdir -p "$APP_HOME"/{app,logs,data,backups,config}
    mkdir -p /var/log/gts
    mkdir -p /var/cache/nginx/gts
    mkdir -p /opt/certbot
    
    chown -R "$APP_USER:$APP_GROUP" "$APP_HOME"
    chown -R "$APP_USER:$APP_GROUP" /var/log/gts
    chown -R www-data:www-data /var/cache/nginx/gts
    
    log_success "Application directories created"
}

################################################################################
# STEP 5: INSTALL PYTHON DEPENDENCIES
################################################################################

provision_step_python() {
    log_info "Step 5/10: Installing Python dependencies..."
    
    # Create virtual environment
    python3.11 -m venv "$APP_HOME/venv"
    
    # Activate and upgrade pip
    source "$APP_HOME/venv/bin/activate"
    pip install --upgrade pip setuptools wheel > /dev/null 2>&1
    
    log_success "Python virtual environment created"
}

################################################################################
# STEP 6: CONFIGURE DATABASE
################################################################################

provision_step_database() {
    log_info "Step 6/10: Configuring PostgreSQL..."
    
    # Ensure PostgreSQL is running
    systemctl start postgresql > /dev/null 2>&1
    systemctl enable postgresql > /dev/null 2>&1
    
    # Create database user (if not exists)
    sudo -u postgres psql -c "CREATE USER gts WITH PASSWORD 'change_me_in_env';" 2>/dev/null || true
    
    # Create database
    sudo -u postgres psql -c "CREATE DATABASE gts_production OWNER gts;" 2>/dev/null || true
    
    # Grant permissions
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE gts_production TO gts;" 2>/dev/null || true
    
    log_success "PostgreSQL configured"
    log_warning "Update DATABASE_URL in .env.production with actual password"
}

################################################################################
# STEP 7: CONFIGURE REDIS
################################################################################

provision_step_redis() {
    log_info "Step 7/10: Configuring Redis..."
    
    systemctl start redis-server > /dev/null 2>&1
    systemctl enable redis-server > /dev/null 2>&1
    
    log_success "Redis configured"
}

################################################################################
# STEP 8: CONFIGURE NGINX
################################################################################

provision_step_nginx() {
    log_info "Step 8/10: Configuring Nginx..."
    
    # Copy nginx configuration
    if [[ -f /tmp/nginx.conf ]]; then
        cp /tmp/nginx.conf /etc/nginx/nginx.conf
    fi
    
    # Test Nginx configuration
    if nginx -t > /dev/null 2>&1; then
        systemctl enable nginx > /dev/null 2>&1
        systemctl start nginx > /dev/null 2>&1
        log_success "Nginx configured and started"
    else
        log_error "Nginx configuration invalid"
        nginx -t
    fi
}

################################################################################
# STEP 9: CONFIGURE SUPERVISOR
################################################################################

provision_step_supervisor() {
    log_info "Step 9/10: Configuring Supervisor for application management..."
    
    # Create supervisor configuration
    cat > /etc/supervisor/conf.d/gts.conf << 'EOF'
[program:gts]
command=/opt/gts/venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
directory=/opt/gts/app
user=gts
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/gts/app.log
environment=PYTHONUNBUFFERED=1,ENVIRONMENT=production

[group:gts]
programs=gts
priority=999
EOF

    systemctl enable supervisor > /dev/null 2>&1
    systemctl start supervisor > /dev/null 2>&1
    
    log_success "Supervisor configured"
}

################################################################################
# STEP 10: CONFIGURE MONITORING
################################################################################

provision_step_monitoring() {
    log_info "Step 10/10: Setting up monitoring and logging..."
    
    # Create log rotation configuration
    cat > /etc/logrotate.d/gts << 'EOF'
/var/log/gts/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 gts gts
    sharedscripts
    postrotate
        systemctl reload supervisor > /dev/null 2>&1 || true
    endscript
}
EOF

    # Create monitoring script
    cat > "$APP_HOME/scripts/health-check.sh" << 'EOF'
#!/bin/bash
# Health check script

HEALTH_ENDPOINT="http://localhost:$APP_PORT/health"
TIMEOUT=5

response=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout $TIMEOUT "$HEALTH_ENDPOINT")

if [[ "$response" == "200" ]]; then
    exit 0
else
    exit 1
fi
EOF

    chmod +x "$APP_HOME/scripts/health-check.sh"
    chown "$APP_USER:$APP_GROUP" "$APP_HOME/scripts/health-check.sh"
    
    log_success "Monitoring and logging configured"
}

################################################################################
# FINAL CONFIGURATION FILE
################################################################################

create_provisioning_report() {
    log_info "Generating provisioning report..."
    
    REPORT_FILE="$APP_HOME/PROVISIONING_REPORT.txt"
    
    cat > "$REPORT_FILE" << EOF
================================================================================
GTS Production Server Provisioning Report
================================================================================

Date: $(date)
Environment: $ENVIRONMENT
Domain: $DOMAIN
Application User: $APP_USER
Application Home: $APP_HOME

================================================================================
SYSTEM INFORMATION
================================================================================

OS: $(lsb_release -ds)
Kernel: $(uname -r)
CPU Cores: $(nproc)
RAM: $(free -h | awk '/^Mem:/ {print $2}')
Disk Space: $(df -h / | awk 'NR==2 {print $2}')

================================================================================
INSTALLED SERVICES
================================================================================

✓ Python 3.11
✓ Node.js $(node --version)
✓ Nginx $(nginx -v 2>&1 | cut -d' ' -f3)
✓ PostgreSQL
✓ Redis
✓ Supervisor
✓ Certbot

================================================================================
DIRECTORIES
================================================================================

Application Home: $APP_HOME
  - app: $APP_HOME/app
  - logs: $APP_HOME/logs
  - data: $APP_HOME/data
  - backups: $APP_HOME/backups
  - config: $APP_HOME/config

System Logs: /var/log/gts/
Nginx Cache: /var/cache/nginx/gts/

================================================================================
CONFIGURATION CHECKLIST
================================================================================

Before launching the application:

1. Database Configuration
   [ ] Update DATABASE_URL in /opt/gts/app/.env.production
   [ ] Test database connection: psql -U gts -d gts_production

2. Environment Variables
   [ ] Copy .env.production to $APP_HOME/app/
   [ ] Set SECRET_KEY and other secrets
   [ ] Configure API keys (Stripe, AWS, etc.)

3. SSL/TLS Certificate
   [ ] Run: sudo /scripts/setup-ssl-letsencrypt.sh $DOMAIN $EMAIL
   [ ] Verify certificate: openssl x509 -in /etc/letsencrypt/live/$DOMAIN/fullchain.pem -noout

4. Application Deployment
   [ ] Clone/copy GTS application to $APP_HOME/app/
   [ ] Install Python dependencies: pip install -r requirements.txt
   [ ] Run database migrations: alembic upgrade head
   [ ] Collect static files: python manage.py collectstatic

5. Service Verification
   [ ] Check Nginx: systemctl status nginx
   [ ] Check Supervisor: systemctl status supervisor
   [ ] Check Redis: redis-cli ping
   [ ] Check PostgreSQL: sudo -u postgres psql -l

6. Application Testing
   [ ] Test health endpoint: curl http://localhost:8000/health
   [ ] Test HTTPS: curl https://$DOMAIN/health
   [ ] Check logs: tail -f /var/log/gts/app.log

================================================================================
NEXT STEPS
================================================================================

1. SSH into production server:
   ssh $APP_USER@$DOMAIN

2. Set up SSL/TLS:
   sudo /opt/gts/scripts/setup-ssl-letsencrypt.sh $DOMAIN $EMAIL

3. Deploy application:
   cd $APP_HOME/app
   git clone <repo> .
   source ../venv/bin/activate
   pip install -r requirements.txt

4. Configure environment:
   cp backend/.env.production $APP_HOME/app/
   # Edit with actual values

5. Run migrations:
   alembic upgrade head

6. Start application:
   supervisorctl start gts

7. Monitor application:
   tail -f /var/log/gts/app.log

================================================================================
SECURITY HARDENING
================================================================================

Run after deployment:

1. Configure firewall:
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable

2. Disable SSH password auth:
   Edit /etc/ssh/sshd_config:
   PasswordAuthentication no
   PubkeyAuthentication yes

3. Enable automatic security updates:
   sudo apt-get install -y unattended-upgrades

4. Set up fail2ban (optional):
   sudo apt-get install -y fail2ban
   sudo systemctl enable fail2ban

================================================================================
MONITORING AND MAINTENANCE
================================================================================

Daily Tasks:
- Check application logs: tail -f /var/log/gts/app.log
- Monitor system resources: htop
- Verify HTTPS certificate: echo | openssl s_client -servername $DOMAIN -connect $DOMAIN:443

Weekly Tasks:
- Check disk space: df -h
- Backup database: pg_dump gts_production > backup.sql
- Review error logs: grep ERROR /var/log/gts/app.log

Monthly Tasks:
- Update system packages: apt-get update && apt-get upgrade
- Test backup restoration
- Review security logs

================================================================================
CONTACT & SUPPORT
================================================================================

For issues:
- Check logs: /var/log/gts/app.log
- Check Nginx: /var/log/nginx/error.log
- Check Supervisor status: supervisorctl status
- Restart application: supervisorctl restart gts

================================================================================
EOF

    log_success "Report saved to: $REPORT_FILE"
    cat "$REPORT_FILE"
}

################################################################################
# MAIN
################################################################################

main() {
    clear
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║   GTS Production Server Provisioning Script                    ║"
    echo "║   AI-Powered Freight Forwarding Platform                       ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"

    # Check if running as root
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (use: sudo $0)"
        exit 1
    fi

    log_info "Starting production server provisioning..."
    echo

    provision_step_updates
    provision_step_runtime
    provision_step_user
    provision_step_directories
    provision_step_python
    provision_step_database
    provision_step_redis
    provision_step_nginx
    provision_step_supervisor
    provision_step_monitoring
    
    echo
    create_provisioning_report
    
    echo
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗"
    echo "║   ✓ Server Provisioning Completed Successfully!                ║"
    echo "╚════════════════════════════════════════════════════════════════╝${NC}"
}

main "$@"
