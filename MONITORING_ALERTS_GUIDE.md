# 📊 MONITORING & ALERTS IMPLEMENTATION GUIDE

## Overview

Complete monitoring solution with Sentry error tracking, email alerts, and health checks for production readiness.

---

## ✅ What Was Implemented

### 1. Sentry Integration (Error Tracking)

**File:** `backend/monitoring/sentry_integration.py`

**Features:**
- ✅ Real-time error tracking
- ✅ Performance monitoring (traces)
- ✅ FastAPI integration
- ✅ SQLAlchemy query monitoring
- ✅ Logging integration
- ✅ Release tracking
- ✅ User context tracking
- ✅ Custom tags and context
- ✅ Error filtering
- ✅ PII protection

---

### 2. Email Alert System

**File:** `backend/monitoring/email_alerts.py`

**Features:**
- ✅ 4 severity levels (INFO, WARNING, ERROR, CRITICAL)
- ✅ Multiple recipients support
- ✅ HTML and plain text formatting
- ✅ Pre-built alert templates:
  - Database backup failures
  - Security events
  - High error rates
  - Database connection failures
  - Low disk space
  - Deployment notifications

---

### 3. Enhanced Health Checks

**Existing:** `backend/routes/health_routes.py`

**Available Endpoints:**
- `/api/v1/health` - Basic health check
- `/api/v1/monitoring/health` - Comprehensive health check
- `/api/v1/monitoring/metrics` - System metrics
- `/api/v1/monitoring/performance` - Performance metrics

---

## 🚀 Setup Instructions

### Step 1: Create Sentry Account

1. Go to https://sentry.io/
2. Create free account (up to 5,000 errors/month free)
3. Create new project → Select **FastAPI**
4. Copy your DSN (looks like: `https://...@...ingest.sentry.io/...`)

### Step 2: Configure Environment Variables

Add to `.env`:

```bash
# Sentry Configuration
SENTRY_DSN=https://your-sentry-dsn-here@sentry.io/project-id
SENTRY_ENVIRONMENT=production  # or development, staging
SENTRY_TRACES_SAMPLE_RATE=0.1  # 10% of transactions (increase for more detail)
ENABLE_SENTRY=true

# Email Alerts Configuration
ADMIN_EMAIL=admin@yourdomain.com,ops@yourdomain.com
SUPPORT_EMAIL=support@yourdomain.com

# SMTP Configuration (Gmail example)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
MAIL_FROM=noreply@yourdomain.com

# System Configuration
APP_ENV=production
GIT_COMMIT=commit-sha-here  # For release tracking
```

### Step 3: Gmail App Password Setup

1. Enable 2FA on Gmail account
2. Go to: https://myaccount.google.com/apppasswords
3. Create app password for "Mail"
4. Copy 16-character password
5. Use as SMTP_PASSWORD

### Step 4: Install Sentry SDK

```bash
pip install sentry-sdk[fastapi]
```

Add to `requirements.txt`:
```
sentry-sdk[fastapi]==1.40.0
```

### Step 5: Initialize in main.py

Add at the top of `backend/main.py`:

```python
from backend.config import Settings
from backend.monitoring.sentry_integration import init_sentry

settings = Settings()

# Initialize Sentry
init_sentry(
    dsn=settings.SENTRY_DSN,
    environment=settings.SENTRY_ENVIRONMENT,
    traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
    enable=settings.ENABLE_SENTRY
)
```

---

## 📧 Email Alert Usage

### Basic Usage:

```python
from backend.monitoring.email_alerts import get_alerter, AlertLevel

alerter = get_alerter()

# Send basic alert
alerter.send_alert(
    subject="Test Alert",
    message="This is a test alert",
    level=AlertLevel.WARNING
)

# Or use convenience methods
alerter.info("Info Alert", "Everything is working fine")
alerter.warning("Warning Alert", "Something seems unusual")
alerter.error("Error Alert", "An error occurred")
alerter.critical("Critical Alert", "Immediate action required!")
```

### Pre-built Alert Templates:

```python
from backend.monitoring.email_alerts import get_alerter

alerter = get_alerter()

# Database backup failed
alerter.database_backup_failed(
    error_details="Connection timeout after 30 seconds"
)

# Security alert
alerter.security_alert(
    event_type="Failed Login Attempt",
    details="10 failed attempts from IP: 192.168.1.100"
)

# High error rate
alerter.high_error_rate(
    error_count=150,
    time_period="last 5 minutes"
)

# Database connection failed
alerter.database_connection_failed(
    error_details="Could not connect to PostgreSQL at host:5432"
)

# Low disk space
alerter.disk_space_low(
    disk_usage=92.5,
    threshold=90.0
)

# Deployment notification
alerter.deployment_notification(
    version="v1.5.0",
    deployed_by="John Doe"
)
```

### In FastAPI Endpoints:

```python
from fastapi import APIRouter, HTTPException
from backend.monitoring.email_alerts import alert_error

router = APIRouter()

@router.post("/critical-operation")
async def critical_operation():
    try:
        # Your operation
        result = perform_critical_task()
        return result
    except Exception as e:
        # Send alert
        alert_error(
            subject="Critical Operation Failed",
            message=f"Operation failed with error: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Operation failed")
```

---

## 🔍 Sentry Error Tracking Usage

### Automatic Error Capture:

Sentry automatically captures:
- ✅ Unhandled exceptions
- ✅ FastAPI errors
- ✅ Database query errors
- ✅ Logging errors (ERROR level+)

No code changes needed - it just works!

### Manual Error Capture:

```python
from backend.monitoring.sentry_integration import (
    capture_exception,
    capture_message,
    set_user_context,
    set_custom_context,
    set_tag,
    start_transaction
)

# Capture exception with context
try:
    risky_operation()
except Exception as e:
    capture_exception(e, extra_context={
        "operation": "payment_processing",
        "user_id": user_id,
        "amount": amount
    })
    raise

# Send custom message
capture_message(
    "Unusual activity detected",
    level="warning",
    extra_context={"ip_address": "192.168.1.100"}
)

# Set user context (for authenticated requests)
set_user_context(
    user_id=str(current_user["id"]),
    email=current_user.get("email"),
    username=current_user.get("username")
)

# Add custom context
set_custom_context("payment_details", {
    "amount": 100.00,
    "currency": "USD",
    "method": "stripe"
})

# Add searchable tags
set_tag("environment", "production")
set_tag("feature", "checkout")
```

### Performance Monitoring:

```python
from backend.monitoring.sentry_integration import start_transaction

@router.post("/process-order")
async def process_order(order_data: OrderData):
    # Start performance transaction
    with start_transaction("process_order", "function"):
        # Your code - Sentry will track duration
        result = await process_order_logic(order_data)
        return result
```

---

## 📊 Health Check Endpoints

### 1. Basic Health Check

```bash
curl http://localhost:8000/api/v1/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2026-02-10T15:30:00Z",
  "version": "1.0.0"
}
```

### 2. Comprehensive Health Check

```bash
curl http://localhost:8000/api/v1/monitoring/health
```

Response:
```json
{
  "status": "healthy",
  "checks": {
    "database": {
      "status": "healthy",
      "latency_ms": 2.5
    },
    "redis": {
      "status": "not_configured"
    },
    "disk_space": {
      "total_gb": 100,
      "used_gb": 65,
      "free_gb": 35,
      "usage_percent": 65.0
    }
  },
  "timestamp": "2026-02-10T15:30:00Z"
}
```

### 3. System Metrics

```bash
curl http://localhost:8000/api/v1/monitoring/metrics
```

Response:
```json
{
  "system": {
    "cpu_percent": 45.2,
    "memory_percent": 68.5,
    "disk_percent": 65.0
  },
  "database": {
    "active_connections": 5,
    "pool_size": 20
  },
  "application": {
    "uptime_seconds": 86400,
    "requests_total": 150000
  }
}
```

---

## 🎯 Monitoring Best Practices

### 1. Error Alerting Thresholds

```python
# In your monitoring code
ERROR_THRESHOLD = 10  # errors per minute
CRITICAL_THRESHOLD = 50  # errors per minute

if error_count_per_minute > CRITICAL_THRESHOLD:
    alerter.critical("Critical Error Rate", 
                     f"{error_count_per_minute} errors/min")
elif error_count_per_minute > ERROR_THRESHOLD:
    alerter.error("High Error Rate",
                  f"{error_count_per_minute} errors/min")
```

### 2. Disk Space Monitoring

```python
import psutil

def check_disk_space():
    usage = psutil.disk_usage('/')
    percent = usage.percent
    
    if percent > 90:
        alerter.critical("Disk Space Critical", 
                        f"Disk usage: {percent}%")
    elif percent > 80:
        alerter.warning("Disk Space Low",
                       f"Disk usage: {percent}%")
```

### 3. Database Connection Monitoring

```python
from sqlalchemy.exc import OperationalError

async def check_database_health():
    try:
        # Test database connection
        await session.execute("SELECT 1")
        return True
    except OperationalError as e:
        alerter.critical("Database Connection Failed",
                        f"Error: {str(e)}")
        return False
```

---

## 🔔 Uptime Monitoring (External)

### Recommended Services:

#### 1. UptimeRobot (Free)
- https://uptimerobot.com/
- Free: 50 monitors, 5-minute interval
- Monitor: https://yourdomain.com/api/v1/health

#### 2. Pingdom
- https://www.pingdom.com/
- Professional monitoring
- Detailed analytics

#### 3. StatusCake
- https://www.statuscake.com/
- Free: Unlimited tests
- Global monitoring

### Setup Example (UptimeRobot):

1. Create account at https://uptimerobot.com/
2. Add New Monitor:
   - Type: HTTP(s)
   - URL: https://yourdomain.com/api/v1/health
   - Interval: 5 minutes
   - Alert Contacts: Your email
3. Webhook Integration:
   ```python
   @router.post("/webhooks/uptime")
   async def uptime_webhook(data: dict):
       if data["status"] == "down":
           alerter.critical("Service Down",
                          f"Service is unreachable: {data['monitor']}")
   ```

---

## 📈 Monitoring Dashboard (Optional)

### Option 1: Grafana + Prometheus

```bash
# Install Prometheus
docker run -d -p 9090:9090 prom/prometheus

# Install Grafana
docker run -d -p 3000:3000 grafana/grafana

# Add to requirements.txt
prometheus-fastapi-instrumentator==6.1.0
```

Add to `main.py`:
```python
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

Access metrics: http://localhost:8000/metrics

### Option 2: Datadog

```bash
pip install ddtrace

# Run with Datadog tracing
ddtrace-run python -m uvicorn backend.main:app
```

---

## ✅ Testing Monitoring System

### 1. Test Sentry Error Capture

```python
# Add temporary test endpoint
@router.get("/test-sentry")
async def test_sentry():
    1 / 0  # Causes error - will be sent to Sentry
```

Visit: http://localhost:8000/test-sentry  
Check Sentry dashboard - error should appear within seconds

### 2. Test Email Alerts

```bash
python -c "
from backend.monitoring.email_alerts import get_alerter
alerter = get_alerter()
alerter.info('Test Alert', 'This is a test email from GTS Platform')
"
```

Check your email inbox

### 3. Test Health Checks

```bash
# Test all health endpoints
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/monitoring/health
curl http://localhost:8000/api/v1/monitoring/metrics
```

---

## 🚨 Alert Escalation Policy

### Level 1: INFO
- **Action:** Log only, no immediate action
- **Example:** Deployment notification
- **Escalation:** None

### Level 2: WARNING
- **Action:** Email to operations team
- **Response Time:** 1 hour
- **Example:** Disk space 80%+
- **Escalation:** After 3 hours → ERROR

### Level 3: ERROR
- **Action:** Email + Slack notification
- **Response Time:** 30 minutes
- **Example:** High error rate
- **Escalation:** After 1 hour → CRITICAL

### Level 4: CRITICAL
- **Action:** Email + SMS + Phone call
- **Response Time:** Immediate (5 minutes)
- **Example:** Database down, service unreachable
- **Escalation:** After 15 minutes → Executive team

---

## 📚 Sentry Tips & Tricks

### 1. Filter Noise

```python
# In sentry_integration.py before_send_hook
def before_send_hook(event, hint):
    # Ignore health check 404s
    if event.get("request", {}).get("url", "").endswith("/health"):
        return None
    
    # Ignore specific errors
    if "ConnectionError" in str(hint.get("exc_info")):
        # Only send if it happens repeatedly
        return event if event.get("level") == "critical" else None
    
    return event
```

### 2. Set Environment Context

```python
# Add deployment info
set_custom_context("deployment", {
    "version": os.getenv("GIT_COMMIT", "unknown"),
    "deployed_at": deployment_time,
    "deployed_by": deployer_name
})
```

### 3. Performance Budget

```python
# Alert on slow transactions
@router.get("/slow-endpoint")
async def slow_endpoint():
    with start_transaction("slow_check", "http") as transaction:
        result = slow_operation()
        
        # Alert if too slow
        if transaction.duration > 5.0:  # 5 seconds
            alerter.warning("Slow Operation",
                           f"Operation took {transaction.duration}s")
        
        return result
```

---

## ✅ Monitoring Checklist

### Initial Setup:
- [ ] Sentry account created
- [ ] Sentry DSN configured
- [ ] Email SMTP configured
- [ ] Test error sent to Sentry
- [ ] Test email alert sent
- [ ] Health check endpoints tested
- [ ] Uptime monitoring configured

### Production:
- [ ] Monitor Sentry dashboard daily
- [ ] Review error trends weekly
- [ ] Check alert emails
- [ ] Verify uptime monitoring
- [ ] Review performance traces
- [ ] Update alert thresholds as needed

---

**✅ Monitoring System Ready!**

Test it now:
```bash
# Test Sentry
python test_sentry.py

# Test email alerts
python -m backend.monitoring.email_alerts

# Test health checks
curl http://localhost:8000/api/v1/monitoring/health
```
