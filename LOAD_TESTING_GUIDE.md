# Load Testing Quick Start Guide

## Prerequisites
- Backend running on `http://localhost:8000`
- Test users created in database
- Locust installed: `pip install locust`

## Running Load Tests

### Option 1: Web UI (Recommended)
```bash
cd C:\Users\enjoy\dev\GTS
locust -f tests/locustfile.py --host=http://localhost:8000
```

Then open: http://localhost:8089

**Configure test:**
- Number of users: 100
- Spawn rate: 10 users/second
- Host: http://localhost:8000

### Option 2: Headless Mode
```bash
# Light load (10 users)
locust -f tests/locustfile.py --host=http://localhost:8000 --users 10 --spawn-rate 1 --run-time 1m --headless

# Normal load (100 users)
locust -f tests/locustfile.py --host=http://localhost:8000 --users 100 --spawn-rate 10 --run-time 2m --headless

# Heavy load (500 users)
locust -f tests/locustfile.py --host=http://localhost:8000 --users 500 --spawn-rate 50 --run-time 3m --headless

# Stress test (1000 users)
locust -f tests/locustfile.py --host=http://localhost:8000 --users 1000 --spawn-rate 100 --run-time 5m --headless
```

## Test Scenarios Included

### GTSUser (Regular User - 60% of traffic)
- Health checks (weight: 5 - most frequent)
- Get user info (weight: 3)
- List bots (weight: 4)
- Get bot stats (weight: 2)
- Get bot history (weight: 1)
- Execute bot commands (weight: 1 - rate limited)

### AdminUser (Admin - 10% of traffic)
- All GTSUser tasks
- Bot management (pause/resume)

### OperatorUser (Operator - 30% of traffic)
- All GTSUser tasks  
- Check available loads

## Understanding Results

### Key Metrics
- **Request/s**: Throughput (target: > 10 req/s)
- **Response Time**: Latency (target: < 500ms for p95)
- **Failure Rate**: Errors (target: < 1%)

### Good Performance Indicators
✅ Avg response time < 200ms  
✅ P95 response time < 500ms  
✅ P99 response time < 1000ms  
✅ Failure rate < 1%  
✅ No memory leaks over 5 minutes

### Warning Signs
⚠️ Response time increasing over time (memory leak)  
⚠️ Failure rate > 5% (capacity issue)  
⚠️ 429 errors dominating (rate limit too strict)

## Test User Credentials

**Regular User:**
- Email: tester@gts.com
- Password: 123456

**Admin User:**
- Email: admin@gts.com  
- Password: admin123

**Operator Users:**
- Email: operator1@gts.com - operator5@gts.com
- Password: operator123

## Expected Baseline Performance

| Metric | Light (10) | Normal (100) | Heavy (500) | Stress (1000) |
|--------|------------|--------------|-------------|---------------|
| Avg Response | < 100ms | < 200ms | < 500ms | < 1000ms |
| P95 Response | < 200ms | < 500ms | < 1000ms | < 2000ms |
| Throughput | 10-50/s | 50-200/s | 100-500/s | 200-1000/s |
| Failure Rate | 0% | < 0.1% | < 1% | < 5% |

## Troubleshooting

### Issue: All requests fail immediately
**Solution:** Check backend is running on port 8000

### Issue: 401 Unauthorized errors  
**Solution:** Verify test users exist in database

### Issue: 429 Rate Limit errors dominate
**Solution:** Expected for bot commands (rate limited), adjust test weights if needed

### Issue: Response times steadily increase
**Solution:** Possible memory leak, check backend logs

### Issue: Database connection errors
**Solution:** Check ASYNC_DATABASE_URL is set correctly

## Analyzing Results

After test completes, Locust provides:
- **Charts**: Response times, RPS, user count over time
- **Statistics Table**: Per-endpoint breakdown
- **Failures**: Detailed error information  
- **CSV Export**: Download data for further analysis

## Next Steps After Load Testing

1. Document baseline metrics
2. Identify performance bottlenecks
3. Optimize slow endpoints
4. Re-test to verify improvements
5. Set up monitoring alerts based on baselines

---

**Quick Reference:**
```bash
# Start web UI
locust -f tests/locustfile.py --host=http://localhost:8000

# Quick 1-minute test (100 users)
locust -f tests/locustfile.py --host=http://localhost:8000 --users 100 --spawn-rate 10 --run-time 1m --headless --html report.html
```
