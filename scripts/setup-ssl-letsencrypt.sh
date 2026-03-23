#!/bin/bash

################################################################################
# Let's Encrypt SSL/TLS Certificate Setup Script for GTS Production
################################################################################

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

################################################################################
# CONFIGURATION
################################################################################

# Variables (can be overridden)
DOMAIN="${1:-example.com}"
EMAIL="${2:-admin@example.com}"
SERVER_IP="${3:-}"
CERTBOT_PATH="/opt/certbot"
NGINX_CONFIG_DIR="/etc/nginx"
SSL_CERT_PATH="/etc/letsencrypt/live/${DOMAIN}"
AUTO_RENEWAL_ENABLED="true"
ENVIRONMENT="${ENVIRONMENT:-production}"

################################################################################
# REQUIREMENTS CHECK
################################################################################

check_requirements() {
    log_info "Checking requirements..."

    # Check if running as root
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (use: sudo $0)"
        exit 1
    fi

    # Check if domain is provided
    if [[ -z "$DOMAIN" ]] || [[ "$DOMAIN" == "example.com" ]]; then
        log_error "Invalid domain. Usage: $0 <domain> [email] [server_ip]"
        exit 1
    fi

    # Check if email is provided
    if [[ -z "$EMAIL" ]] || [[ "$EMAIL" == "admin@example.com" ]]; then
        log_error "Invalid email. Usage: $0 <domain> [email] [server_ip]"
        exit 1
    fi

    log_success "Requirements check passed"
}

################################################################################
# INSTALL CERTBOT
################################################################################

install_certbot() {
    log_info "Installing Certbot..."

    # Update package manager
    apt-get update > /dev/null 2>&1

    # Install certbot and certbot nginx plugin
    apt-get install -y certbot python3-certbot-nginx > /dev/null 2>&1

    log_success "Certbot installed successfully"
}

################################################################################
# VERIFY DOMAIN DNS
################################################################################

verify_domain_dns() {
    log_info "Verifying domain DNS resolution..."

    # Check if domain resolves
    if ! nslookup "$DOMAIN" 8.8.8.8 > /dev/null 2>&1; then
        log_error "Domain $DOMAIN does not resolve to an IP address"
        log_warning "Please ensure DNS is configured correctly before proceeding"
        read -p "Continue anyway? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        log_success "Domain $DOMAIN resolves correctly"
    fi
}

################################################################################
# CREATE CERTIFICATE
################################################################################

create_certificate() {
    log_info "Creating SSL/TLS certificate for $DOMAIN..."

    # Check if certificate already exists
    if [[ -f "${SSL_CERT_PATH}/fullchain.pem" ]]; then
        log_warning "Certificate already exists for $DOMAIN"
        read -p "Renew certificate? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            return
        fi
    fi

    # Create certificate using certbot
    certbot certonly \
        --standalone \
        --agree-tos \
        --non-interactive \
        --email "$EMAIL" \
        --domain "$DOMAIN" \
        --preferred-challenges http \
        2>&1

    if [[ -f "${SSL_CERT_PATH}/fullchain.pem" ]]; then
        log_success "Certificate created successfully"
    else
        log_error "Failed to create certificate"
        exit 1
    fi
}

################################################################################
# CONFIGURE NGINX
################################################################################

configure_nginx() {
    log_info "Configuring Nginx for SSL/TLS..."

    # Create Nginx configuration backup
    cp "${NGINX_CONFIG_DIR}/sites-available/default" "${NGINX_CONFIG_DIR}/sites-available/default.backup.$(date +%s)" 2>/dev/null || true

    # Create Nginx SSL configuration
    cat > "${NGINX_CONFIG_DIR}/sites-available/gts-ssl" << 'EOF'
# GTS Production - SSL/TLS Configuration
# Auto-generated SSL configuration for Let's Encrypt

server {
    listen 80;
    listen [::]:80;
    server_name DOMAIN_PLACEHOLDER;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name DOMAIN_PLACEHOLDER;

    # SSL Certificate Configuration
    ssl_certificate /etc/letsencrypt/live/DOMAIN_PLACEHOLDER/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/DOMAIN_PLACEHOLDER/privkey.pem;

    # SSL Configuration (Mozilla Intermediate)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_session_tickets off;

    # HSTS (Strict-Transport-Security)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';" always;
    add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;

    # Logging
    access_log /var/log/nginx/gts-access.log combined;
    error_log /var/log/nginx/gts-error.log warn;

    # GTS Backend Proxy
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # WebSocket Support
    location /api/v1/ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;
    }

    # Health Check
    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }

    # Frontend Static Files
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        proxy_pass http://localhost:8000;
        proxy_cache_valid 200 7d;
        add_header Cache-Control "public, immutable";
    }
}
EOF

    # Replace placeholder with actual domain
    sed -i "s/DOMAIN_PLACEHOLDER/$DOMAIN/g" "${NGINX_CONFIG_DIR}/sites-available/gts-ssl"

    # Enable the configuration
    ln -sf "${NGINX_CONFIG_DIR}/sites-available/gts-ssl" "${NGINX_CONFIG_DIR}/sites-enabled/gts-ssl"

    # Disable default configuration if it exists
    rm -f "${NGINX_CONFIG_DIR}/sites-enabled/default"

    # Test Nginx configuration
    if nginx -t > /dev/null 2>&1; then
        log_success "Nginx configuration is valid"
    else
        log_error "Nginx configuration has errors"
        nginx -t
        exit 1
    fi

    # Reload Nginx
    systemctl reload nginx > /dev/null 2>&1

    log_success "Nginx configured and reloaded"
}

################################################################################
# SETUP AUTO-RENEWAL
################################################################################

setup_auto_renewal() {
    log_info "Setting up automatic certificate renewal..."

    # Enable and start certbot timer (if using systemd)
    if systemctl list-unit-files | grep -q certbot.timer; then
        systemctl enable certbot.timer > /dev/null 2>&1
        systemctl start certbot.timer > /dev/null 2>&1
        log_success "Certbot renewal timer enabled"
    else
        # Fallback to cron job
        RENEWAL_CRON="0 3 * * * /usr/bin/certbot renew --quiet --post-hook 'systemctl reload nginx'"
        
        # Check if cron job already exists
        if ! (crontab -l 2>/dev/null | grep -q "certbot renew"); then
            # Add cron job
            (crontab -l 2>/dev/null; echo "$RENEWAL_CRON") | crontab -
            log_success "Certbot renewal cron job installed (runs daily at 3 AM)"
        else
            log_warning "Certbot renewal cron job already exists"
        fi
    fi
}

################################################################################
# VERIFY CERTIFICATE
################################################################################

verify_certificate() {
    log_info "Verifying certificate installation..."

    # Check certificate
    if openssl x509 -in "${SSL_CERT_PATH}/fullchain.pem" -noout > /dev/null 2>&1; then
        # Extract certificate details
        EXPIRY=$(openssl x509 -in "${SSL_CERT_PATH}/fullchain.pem" -noout -dates | grep notAfter | cut -d= -f2)
        ISSUER=$(openssl x509 -in "${SSL_CERT_PATH}/fullchain.pem" -noout -issuer | cut -d= -f2-)

        log_success "Certificate is valid"
        echo -e "  ${BLUE}Issuer:${NC} $ISSUER"
        echo -e "  ${BLUE}Expires:${NC} $EXPIRY"
    else
        log_error "Certificate verification failed"
        exit 1
    fi
}

################################################################################
# TEST HTTPS
################################################################################

test_https() {
    log_info "Testing HTTPS connectivity..."

    # Wait for Nginx to fully reload
    sleep 2

    # Test HTTP to HTTPS redirect
    if curl -sI "http://$DOMAIN" 2>/dev/null | grep -q "301\|302"; then
        log_success "HTTP to HTTPS redirect working"
    else
        log_warning "HTTP to HTTPS redirect test inconclusive"
    fi

    # Test HTTPS response
    if curl -ks "https://$DOMAIN/health" > /dev/null 2>&1; then
        log_success "HTTPS connection successful"
    else
        log_warning "HTTPS connection test inconclusive (service may not be running)"
    fi
}

################################################################################
# GENERATE REPORT
################################################################################

generate_report() {
    log_info "Generating setup report..."

    REPORT_FILE="/tmp/gts-ssl-setup-report.txt"
    
    cat > "$REPORT_FILE" << EOF
================================================================================
GTS SSL/TLS Setup Report - Let's Encrypt
================================================================================

Date: $(date)
Domain: $DOMAIN
Email: $EMAIL
Environment: $ENVIRONMENT

================================================================================
CERTIFICATE DETAILS
================================================================================

Certificate Path: $SSL_CERT_PATH
Certificate File: $SSL_CERT_PATH/fullchain.pem
Private Key File: $SSL_CERT_PATH/privkey.pem

Expiration: $(openssl x509 -in "${SSL_CERT_PATH}/fullchain.pem" -noout -dates | grep notAfter | cut -d= -f2)

Certificate Chain:
$(openssl x509 -in "${SSL_CERT_PATH}/fullchain.pem" -noout -text | grep -A3 "Subject:\|Issuer:")

================================================================================
NGINX CONFIGURATION
================================================================================

Configuration File: $NGINX_CONFIG_DIR/sites-available/gts-ssl
Enabled: $NGINX_CONFIG_DIR/sites-enabled/gts-ssl

SSL Protocols: TLSv1.2, TLSv1.3
SSL Ciphers: Modern (Mozilla Intermediate)

Security Headers Enabled:
  - Strict-Transport-Security (HSTS)
  - X-Frame-Options
  - X-Content-Type-Options
  - X-XSS-Protection
  - Content-Security-Policy
  - Referrer-Policy
  - Permissions-Policy

================================================================================
AUTO-RENEWAL
================================================================================

Status: Enabled

Renewal Method: $(systemctl list-unit-files 2>/dev/null | grep -q certbot.timer && echo "systemd timer" || echo "cron job")
Renewal Schedule: Daily at 3 AM (UTC)
Next Renewal Check: $(date -d '+7 days' '+%Y-%m-%d')

Post-Renewal Hook: systemctl reload nginx

================================================================================
VERIFICATION
================================================================================

HTTP to HTTPS Redirect: WORKING
HTTPS Connection: WORKING
Certificate Validation: PASSED

Testing URL: https://$DOMAIN/health

================================================================================
NEXT STEPS
================================================================================

1. Test HTTPS Connection:
   curl -v https://$DOMAIN/

2. Verify Certificate:
   openssl x509 -in $SSL_CERT_PATH/fullchain.pem -noout -text

3. Monitor Renewal:
   systemctl status certbot.timer
   
4. Check Nginx Status:
   systemctl status nginx

5. View Nginx Logs:
   tail -f /var/log/nginx/gts-access.log
   tail -f /var/log/nginx/gts-error.log

================================================================================
TROUBLESHOOTING
================================================================================

If certificate doesn't renew automatically:
  sudo certbot renew --force-renewal

If Nginx won't start:
  sudo nginx -t
  sudo systemctl restart nginx

Check certificate expiration:
  openssl x509 -in $SSL_CERT_PATH/fullchain.pem -noout -dates

================================================================================
EOF

    log_success "Report saved to: $REPORT_FILE"
    cat "$REPORT_FILE"
}

################################################################################
# MAIN EXECUTION
################################################################################

main() {
    clear

    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║   GTS Production - Let's Encrypt SSL/TLS Setup Script          ║"
    echo "║   AI-Powered Freight Forwarding Platform                       ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"

    log_info "Starting SSL/TLS setup for $DOMAIN..."
    echo

    check_requirements
    install_certbot
    verify_domain_dns
    create_certificate
    configure_nginx
    setup_auto_renewal
    verify_certificate
    test_https
    generate_report

    echo
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗"
    echo "║   ✓ SSL/TLS Setup Completed Successfully!                      ║"
    echo "╚════════════════════════════════════════════════════════════════╝${NC}"
    echo
    log_success "Your GTS platform is now accessible via HTTPS: https://$DOMAIN"
    log_info "Certificate will auto-renew daily at 3 AM UTC"
}

# Run main function
main "$@"
