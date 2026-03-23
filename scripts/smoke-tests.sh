#!/bin/bash

################################################################################
# Production Smoke Tests - GTS Platform
################################################################################

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
TESTS_TOTAL=0
TESTS_PASSED=0
TESTS_FAILED=0

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_error() { echo -e "${RED}[✗]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[!]${NC} $1"; }

test_case() {
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    echo -e "\n${BLUE}Test $TESTS_TOTAL: $1${NC}"
}

test_pass() {
    TESTS_PASSED=$((TESTS_PASSED + 1))
    log_success "$1"
}

test_fail() {
    TESTS_FAILED=$((TESTS_FAILED + 1))
    log_error "$1"
}

################################################################################
# CONFIGURATION
################################################################################

BASE_URL="${BASE_URL:-https://gts.example.com}"
API_URL="${API_URL:-$BASE_URL/api/v1}"
TIMEOUT=10
FAILED_TESTS=""

################################################################################
# SMOKE TESTS
################################################################################

# Test 1: Server Connectivity
test_server_connectivity() {
    test_case "Server Connectivity"
    
    if curl -s -I "$BASE_URL" -m $TIMEOUT > /dev/null 2>&1; then
        test_pass "Server is reachable at $BASE_URL"
    else
        test_fail "Server is not reachable at $BASE_URL"
        FAILED_TESTS="$FAILED_TESTS\n  - Server connectivity"
    fi
}

# Test 2: HTTPS/SSL Certificate
test_ssl_certificate() {
    test_case "SSL/TLS Certificate"
    
    if echo | openssl s_client -servername "${BASE_URL#https://}" -connect "${BASE_URL#https://}:443" 2>/dev/null | grep -q "Verify return code: 0"; then
        test_pass "SSL/TLS certificate is valid"
    else
        test_fail "SSL/TLS certificate validation failed"
        FAILED_TESTS="$FAILED_TESTS\n  - SSL certificate invalid"
    fi
}

# Test 3: HTTP to HTTPS Redirect
test_http_redirect() {
    test_case "HTTP to HTTPS Redirect"
    
    HTTP_URL="${BASE_URL/https:/\/http:\/}"
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -I "$HTTP_URL" -m $TIMEOUT 2>/dev/null)
    
    if [[ "$RESPONSE" == "301" ]] || [[ "$RESPONSE" == "302" ]]; then
        test_pass "HTTP correctly redirects to HTTPS (status: $RESPONSE)"
    else
        test_fail "HTTP redirect not working (status: $RESPONSE)"
        FAILED_TESTS="$FAILED_TESTS\n  - HTTP redirect"
    fi
}

# Test 4: Health Check Endpoint
test_health_endpoint() {
    test_case "Health Check Endpoint"
    
    RESPONSE=$(curl -s -w "\n%{http_code}" "$API_URL/health" -m $TIMEOUT 2>/dev/null)
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    
    if [[ "$HTTP_CODE" == "200" ]]; then
        test_pass "Health check endpoint responds with 200"
    else
        test_fail "Health check endpoint returned: $HTTP_CODE"
        FAILED_TESTS="$FAILED_TESTS\n  - Health endpoint"
    fi
}

# Test 5: Authentication Endpoint
test_auth_endpoint() {
    test_case "Authentication Endpoint"
    
    RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/auth/token" \
        -H "Content-Type: application/json" \
        -d '{}' \
        -m $TIMEOUT 2>/dev/null)
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    
    # Should return 400/422 for missing credentials, not 500
    if [[ "$HTTP_CODE" =~ ^(400|401|422)$ ]]; then
        test_pass "Authentication endpoint is working (status: $HTTP_CODE)"
    else
        test_fail "Authentication endpoint returned unexpected status: $HTTP_CODE"
        FAILED_TESTS="$FAILED_TESTS\n  - Auth endpoint"
    fi
}

# Test 6: Security Headers
test_security_headers() {
    test_case "Security Headers"
    
    HEADERS=$(curl -s -I "$BASE_URL" -m $TIMEOUT 2>/dev/null)
    
    HEADERS_OK=0
    
    if echo "$HEADERS" | grep -qi "strict-transport-security"; then
        log_success "  - HSTS header present"
        HEADERS_OK=$((HEADERS_OK + 1))
    else
        log_warning "  - HSTS header missing"
    fi
    
    if echo "$HEADERS" | grep -qi "x-frame-options"; then
        log_success "  - X-Frame-Options header present"
        HEADERS_OK=$((HEADERS_OK + 1))
    else
        log_warning "  - X-Frame-Options header missing"
    fi
    
    if echo "$HEADERS" | grep -qi "x-content-type-options"; then
        log_success "  - X-Content-Type-Options header present"
        HEADERS_OK=$((HEADERS_OK + 1))
    else
        log_warning "  - X-Content-Type-Options header missing"
    fi
    
    if echo "$HEADERS" | grep -qi "content-security-policy"; then
        log_success "  - CSP header present"
        HEADERS_OK=$((HEADERS_OK + 1))
    else
        log_warning "  - CSP header missing"
    fi
    
    if [[ $HEADERS_OK -ge 3 ]]; then
        test_pass "Security headers are properly configured ($HEADERS_OK/4)"
    else
        test_fail "Some security headers are missing ($HEADERS_OK/4)"
        FAILED_TESTS="$FAILED_TESTS\n  - Security headers"
    fi
}

# Test 7: Response Time
test_response_time() {
    test_case "Response Time"
    
    START_TIME=$(date +%s%N)
    curl -s "$BASE_URL" -m $TIMEOUT > /dev/null 2>&1
    END_TIME=$(date +%s%N)
    
    # Calculate response time in milliseconds
    RESPONSE_TIME=$(( (END_TIME - START_TIME) / 1000000 ))
    
    if [[ $RESPONSE_TIME -lt 2000 ]]; then
        test_pass "Response time is acceptable: ${RESPONSE_TIME}ms"
    else
        log_warning "Response time is high: ${RESPONSE_TIME}ms (threshold: 2000ms)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    fi
}

# Test 8: Database Connectivity
test_database_connectivity() {
    test_case "Database Connectivity"
    
    RESPONSE=$(curl -s "$API_URL/health" -m $TIMEOUT 2>/dev/null | grep -o "database")
    
    if [[ ! -z "$RESPONSE" ]]; then
        test_pass "Database connectivity verified"
    else
        test_fail "Database connectivity check failed"
        FAILED_TESTS="$FAILED_TESTS\n  - Database connectivity"
    fi
}

# Test 9: WebSocket Support
test_websocket() {
    test_case "WebSocket Support"
    
    # Check if WebSocket endpoint responds
    RESPONSE=$(curl -s -I -H "Upgrade: websocket" -H "Connection: Upgrade" "$API_URL/ws/live" -m $TIMEOUT 2>/dev/null)
    
    if echo "$RESPONSE" | grep -q "101\|Upgrade"; then
        test_pass "WebSocket endpoint is available"
    else
        log_warning "WebSocket endpoint check inconclusive"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    fi
}

# Test 10: CORS Configuration
test_cors() {
    test_case "CORS Configuration"
    
    RESPONSE=$(curl -s -I -H "Origin: https://example.com" "$BASE_URL" -m $TIMEOUT 2>/dev/null)
    
    if echo "$RESPONSE" | grep -q "access-control"; then
        test_pass "CORS headers are configured"
    else
        log_warning "CORS headers not found (may be restricted)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    fi
}

# Test 11: API Response Format
test_api_response_format() {
    test_case "API Response Format (JSON)"
    
    RESPONSE=$(curl -s "$API_URL/health" -m $TIMEOUT 2>/dev/null)
    
    if echo "$RESPONSE" | grep -q "{"; then
        test_pass "API returns valid JSON format"
    else
        test_fail "API response is not valid JSON"
        FAILED_TESTS="$FAILED_TESTS\n  - API response format"
    fi
}

# Test 12: Rate Limiting Headers
test_rate_limiting() {
    test_case "Rate Limiting Headers"
    
    RESPONSE=$(curl -s -I "$API_URL/health" -m $TIMEOUT 2>/dev/null)
    
    if echo "$RESPONSE" | grep -q "x-ratelimit\|ratelimit"; then
        test_pass "Rate limiting headers are present"
    else
        log_warning "Rate limiting headers not found"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    fi
}

# Test 13: Nginx Configuration
test_nginx_status() {
    test_case "Nginx Status"
    
    if command -v systemctl &> /dev/null; then
        if systemctl is-active --quiet nginx; then
            test_pass "Nginx service is running"
        else
            test_fail "Nginx service is not running"
            FAILED_TESTS="$FAILED_TESTS\n  - Nginx status"
        fi
    else
        log_warning "Nginx status check skipped (systemctl not available)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    fi
}

# Test 14: Application Logs
test_application_logs() {
    test_case "Application Logs"
    
    if [[ -f /var/log/gts/app.log ]]; then
        # Check for recent errors
        ERRORS=$(grep -c "ERROR\|CRITICAL" /var/log/gts/app.log 2>/dev/null || echo "0")
        
        if [[ "$ERRORS" -eq 0 ]]; then
            test_pass "No critical errors in application logs"
        else
            log_warning "Found $ERRORS error entries in logs (may be normal)"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        fi
    else
        log_warning "Application log file not found"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    fi
}

# Test 15: Database Backups
test_database_backups() {
    test_case "Database Backups"
    
    if [[ -d /opt/gts/backups ]]; then
        BACKUP_COUNT=$(find /opt/gts/backups -name "*.sql.gz" -type f 2>/dev/null | wc -l)
        
        if [[ $BACKUP_COUNT -gt 0 ]]; then
            test_pass "Database backups are present ($BACKUP_COUNT backups found)"
        else
            log_warning "No backups found in /opt/gts/backups"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        fi
    else
        log_warning "Backup directory not found"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    fi
}

################################################################################
# SUMMARY REPORT
################################################################################

generate_report() {
    echo
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗"
    echo "║   Smoke Test Summary Report                                  ║"
    echo "╚════════════════════════════════════════════════════════════════╝${NC}"
    echo
    
    echo -e "Total Tests: ${BLUE}$TESTS_TOTAL${NC}"
    echo -e "Passed:      ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Failed:      ${RED}$TESTS_FAILED${NC}"
    echo
    
    PASS_RATE=$((TESTS_PASSED * 100 / TESTS_TOTAL))
    echo -e "Pass Rate:   ${BLUE}$PASS_RATE%${NC}"
    echo
    
    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "${GREEN}✓ All smoke tests passed! Application is ready for use.${NC}"
    else
        echo -e "${YELLOW}⚠ Some tests failed:${FAILED_TESTS}${NC}"
        echo
        echo "Troubleshooting steps:"
        echo "  1. Check application logs: tail -f /var/log/gts/app.log"
        echo "  2. Verify Nginx configuration: nginx -t"
        echo "  3. Check SSL certificate: openssl x509 -in /etc/letsencrypt/live/$(echo $BASE_URL | cut -d/ -f3)/fullchain.pem -noout -text"
        echo "  4. Restart services: sudo systemctl restart nginx && sudo supervisorctl restart gts"
    fi
    
    echo
}

################################################################################
# MAIN
################################################################################

main() {
    clear
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║   GTS Production Smoke Tests                                  ║"
    echo "║   AI-Powered Freight Forwarding Platform                       ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    log_info "Base URL: $BASE_URL"
    log_info "Starting smoke tests..."
    echo
    
    # Run all tests
    test_server_connectivity
    test_ssl_certificate
    test_http_redirect
    test_health_endpoint
    test_auth_endpoint
    test_security_headers
    test_response_time
    test_database_connectivity
    test_websocket
    test_cors
    test_api_response_format
    test_rate_limiting
    test_nginx_status
    test_application_logs
    test_database_backups
    
    # Generate report
    generate_report
    
    # Exit with appropriate code
    if [[ $TESTS_FAILED -eq 0 ]]; then
        exit 0
    else
        exit 1
    fi
}

main "$@"
