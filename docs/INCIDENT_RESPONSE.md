# Incident Response Plan - GTS Logistics

## 📋 Incident Response Workflow
DETECTION → 2. TRIAGE → 3. INVESTIGATION → 4. CONTAINMENT → 5. RESOLUTION → 6. POST-MORTEM

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  DETECTION  │ -> │   TRIAGE    │ -> │INVESTIGATION│ -> │CONTAINMENT │ -> │ RESOLUTION  │ -> │ POST-MORTEM │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

## 🚨 Step 1: Detection

### Automatic Detection
- System monitors logs for errors
- API health checks every 30 seconds
- Database connection monitoring
- Performance anomaly detection

### Manual Reporting
- Users report issues via Support Chat
- Team members report via Admin Dashboard
- Email alerts to on-call engineers

## 🔍 Step 2: Triage

### Severity Classification

| Severity | Description | Response Time | Example |
|----------|-------------|---------------|---------|
| **CRITICAL** | Service down, data loss | Immediate | Database down, API 500 errors |
| **HIGH** | Major feature broken | < 15 min | Payment gateway failure |
| **MEDIUM** | Minor feature broken | < 1 hour | UI glitch, slow response |
| **LOW** | Cosmetic issues | < 1 day | Typo, styling issue |

### Initial Assessment
1. Check if incident is already tracked
2. Determine affected services and users
3. Assign severity level
4. Create incident ticket

## 🕵️ Step 3: Investigation

### Log Analysis
```bash
# Check application logs
tail -100 logs/app.log | grep ERROR

# Check API logs
tail -100 logs/api.log | grep "5[0-9][0-9]"

# Check database logs
tail -100 logs/db.log
```

### API Endpoints
```bash
# Check system health
curl http://localhost:8000/api/v1/support/health

# Check database connectivity
curl http://localhost:8000/health/db

# Check recent incidents
curl http://localhost:8000/api/v1/incidents/active
```

### Database Check
```sql
-- Check active connections
SELECT count(*) FROM pg_stat_activity;

-- Check slow queries
SELECT query, duration FROM pg_stat_statements ORDER BY duration DESC LIMIT 10;

-- Check table sizes
SELECT pg_size_pretty(pg_total_relation_size('table_name'));
```

## 🛡️ Step 4: Containment

### Immediate Actions
- Isolate affected service - Redirect traffic if possible
- Kill long-running queries - Prevent database overload
- Restart service - Clear temporary issues
- Rollback deployment - If recent deployment caused issue

### Quick Fix Commands
```bash
# Restart backend service
systemctl restart gts-backend

# Restart database
systemctl restart postgresql

# Clear cache
redis-cli FLUSHALL

# Rollback to previous deployment
git checkout <previous-tag>
```

## ✅ Step 5: Resolution

### Fix Implementation
- Apply hotfix (if urgent)
- Deploy proper fix
- Verify fix in staging
- Deploy to production
- Monitor for recurrence

### Verification Checklist
- Service responding normally
- Error rate back to baseline
- User impact resolved
- Monitoring confirms stability

## 📝 Step 6: Post-Mortem

### Documentation
- What happened? - Timeline of events
- Why did it happen? - Root cause analysis
- How was it fixed? - Resolution steps
- How to prevent? - Preventive measures

### Post-Mortem Template
```markdown
# Incident Report: INC-YYYYMMDD-XXX

## Overview
- **Date:** YYYY-MM-DD
- **Duration:** X hours
- **Severity:** [CRITICAL/HIGH/MEDIUM/LOW]
- **Impact:** X users affected

## Timeline
- HH:MM - Incident detected
- HH:MM - Investigation started
- HH:MM - Root cause identified
- HH:MM - Fix applied
- HH:MM - Service restored

## Root Cause
[Detailed explanation]

## Resolution
[Steps taken to fix]

## Preventive Measures
[Actions to prevent recurrence]

## Action Items
- [ ] Item 1
- [ ] Item 2
```

## 📊 Monitoring Dashboard

### Key Metrics
- Error rate (target: <0.1%)
- Response time (target: <200ms)
- Uptime (target: 99.9%)
- Active incidents (target: 0)

### Alert Thresholds
| Metric | Warning | Critical |
|--------|---------|----------|
| Error Rate | >1% | >5% |
| Response Time | >500ms | >2000ms |
| CPU Usage | >70% | >90% |
| Memory Usage | >80% | >95% |

## 📞 Contact List
| Role | Name | Phone | Email |
|------|------|-------|-------|
| On-Call Engineer | - | - | oncall@gts.com |
| Database Admin | - | - | dba@gts.com |
| Security Lead | - | - | security@gts.com |
| DevOps Lead | - | - | devops@gts.com |

## 🔧 Tools & Resources
- **Logs:** /var/log/gts/
- **Metrics:** Grafana dashboard
- **Alerts:** PagerDuty
- **Chat:** Slack #incident-response
- **Docs:** Incident runbooks

---

## 🧪 Testing Incident System

```bash
# Test incident capture
curl -X POST http://localhost:8000/api/v1/incidents/capture \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service": "api",
    "error": "Database connection timeout after 30 seconds",
    "description": "Unable to connect to PostgreSQL",
    "affected_users": 150
  }'

# Test active incidents
curl http://localhost:8000/api/v1/incidents/active \
  -H "Authorization: Bearer YOUR_TOKEN"

# Test incident report
curl http://localhost:8000/api/v1/incidents/report?days=7 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 📈 Incident Statistics

### Monthly Report
- Total incidents: X
- Critical: X (XX%)
- High: X (XX%)
- Medium: X (XX%)
- Low: X (XX%)
- Average resolution time: X minutes
- Most affected service: [Service Name]

### Trends
- Incident rate: [up/down/stable]
- Resolution time: [improving/declining/stable]
- Common root causes: [List top 3]

## 🎯 Continuous Improvement

### Regular Reviews
- Weekly incident review meetings
- Monthly trend analysis
- Quarterly process improvements

### Training
- Incident response training for all engineers
- Regular drills and simulations
- Documentation updates

### Automation
- Automated incident detection
- Auto-remediation for common issues
- Improved monitoring and alerting

---

*This document is living and should be updated based on lessons learned from each incident.*