# EN 3: EN (50 Users)
**Phase 3: Initial Load Test Results (50 Users)**

## EN | Test Date
**2026-02-03** | **10:55 - 10:56** (EN | 2 minutes)

---

## 📊 EN | Results Summary

### EN | General Statistics
| Metric | Value |
|--------|-------|
| **EN** \| Total Requests | 759 |
| **EN** \| Failed Requests | 90 (11.86%) |
| **EN** \| Requests/sec | 6.35 req/s |
| **EN** \| Avg Response Time | **1017.47ms** |
| **EN** \| Max Response Time | **4252ms** |
| **EN** \| Min Response Time | 0ms |

---

## 🔴 EN | Critical Issues

### 1. EN 100% EN | 100% Login Failures
**EN (90/90)** | **All login attempts failed (90/90)**

| Endpoint | Attempts | Failures | Failure Rate | Error Code |
|----------|----------|----------|--------------|------------|
| `POST /auth/token` (Regular Users) | 50 | 50 | **100%** | **422 Unprocessable Entity** |
| `POST /auth/token` (Admin) | 10 | 10 | **100%** | **422 Unprocessable Entity** |
| `POST /auth/token` (Operator) | 30 | 30 | **100%** | **422 Unprocessable Entity** |

**EN | Analysis:**
```
Error: HTTPError('422 Client Error: Unprocessable Entity')
```

**EN | Root Cause:**
- ❌ EN `username`/`password` EN)
- ❌ EN `locustfile.py` EN
- ❌ EN `application/x-www-form-urlencoded` EN Locust EN `application/json`
- ❌ EN `tenant_id` EN `role`)

**EN | Action Required:**
1. EN `tests/locustfile.py` - EN `/auth/token`
2. EN (`tester@gts.com`, `admin@gts.com`, `operator@gts.com`)
3. EN `Content-Type` header - EN `application/x-www-form-urlencoded`

---

### 2. EN | Very Slow Response Times

**Health Check Endpoint:**
```
Average: 1001ms
90th percentile: 2000ms  ⚠️ 
95th percentile: 2100ms  ⚠️ 
99th percentile: 2400ms  🔴
Max: 4252ms  🔴🔴🔴
```

**EN | Performance Distribution:**
- ⚡ **EN (< 100ms):** ~33% EN
- ⚠️ **EN (2000-2100ms):** ~50% EN
- 🔴 **EN (> 2000ms):** ~17% EN
- 🔴🔴 **EN (> 4000ms):** 0.1% EN

**EN | Potential Causes:**
1. **EN** | Slow database queries
   - EN (indexes)
   - EN N+1
   - EN Connection Pooling EN

2. **EN Backend** | Backend overload
   - EN Workers EN
   - CPU EN Memory bottleneck
   - Blocking I/O operations

3. **EN (Cold Start)** | Initial cold start
   - EN

---

## 📈 EN | Performance Details

### EN | Request Distribution
```
Health Check:    669 requests (88.14%)  ✅ Success Rate: 100%
Login:           50 requests  (6.58%)   🔴 Success Rate: 0%
Operator Login:  30 requests  (3.95%)   🔴 Success Rate: 0%
Admin Login:     10 requests  (1.32%)   🔴 Success Rate: 0%
```

### EN | Request Rate Over Time
```
Initial (0-10s):   4.30 req/s
Ramp-up (10-30s):  5.60-7.00 req/s
Steady (30-90s):   5.20-7.10 req/s
Final (90-120s):   4.50-6.50 req/s

Average: 6.35 req/s
```

---

## 🔧 EN | Immediate Investigations

### ✅ EN | What Works
- ✅ **Health Check endpoint:** EN 100% EN (669/669)
- ✅ **Backend EN:** EN 500
- ✅ **EN:** 5-7 EN

### 🔴 EN | What Doesn't Work
- 🔴 **EN:** 422 Unprocessable Entity
- 🔴 **EN:** 2-4 EN)
- 🔴 **EN:** EN APIs EN

---

## 📋 EN | Next Steps

### **Priority 1: EN Login (EN) | Fix Login (Critical)**
1. EN `tests/locustfile.py` - EN
2. EN `/auth/token` EN curl/Postman
3. EN DB:
   ```sql
   SELECT email, role FROM users WHERE email IN (
     'tester@gts.com', 
     'admin@gts.com', 
     'operator@gts.com'
   );
   ```
4. EN `Content-Type` header EN Locust EN `application/x-www-form-urlencoded`

### **Priority 2: EN | Performance Optimization**
1. EN:
   ```sql
   SELECT query, calls, mean_exec_time, max_exec_time
   FROM pg_stat_statements
   WHERE mean_exec_time > 100
   ORDER BY mean_exec_time DESC
   LIMIT 10;
   ```
2. EN Indexes EN
3. EN Database Connection Pooling (EN 10EN 50)
4. EN Uvicorn workers count (EN: EN)

### **Priority 3: EN | Re-test**
EN:
```bash
.venv\Scripts\python.exe -m locust -f tests/locustfile.py \
  --host=http://localhost:8000 \
  --users 50 --spawn-rate 5 --run-time 2m --headless \
  --html reports/load_test_50users_fixed.html
```

---

## 📊 Response Time Percentiles

| Percentile | Health Check | Login | Admin Login | Operator Login |
|------------|--------------|-------|-------------|----------------|
| **50%** | 2ms | 3ms | 2000ms | 2000ms |
| **75%** | 2000ms | 4ms | 2000ms | 2000ms |
| **90%** | 2000ms | 2000ms | 2100ms | 2100ms |
| **95%** | 2100ms | 2000ms | 2100ms | 2100ms |
| **99%** | 2400ms | 2100ms | 2100ms | 2100ms |
| **99.9%** | **4300ms** | 2100ms | 2100ms | 2100ms |
| **Max** | **4252ms** | 2053ms | 2058ms | 2054ms |

---

## 🚨 EN Locust | Locust Warnings

**Slow Request Warnings:** 500+ EN
```
[WARNING] Slow request: Health Check took 2000-4252ms
```

**EN | Observation:**
EN Health Check EN ~2 EN. EN < 50ms.

---

## 🎯 EN | Target Goals

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| **Average Response Time** | 1017ms | < 200ms | 🔴 **508% slower** |
| **95th Percentile** | 2100ms | < 500ms | 🔴 **420% slower** |
| **Success Rate** | 88.14% | > 99% | 🔴 **Login: 0%** |
| **Requests/sec** | 6.35 | > 20 | 🔴 **68% below target** |
| **Error Rate** | 11.86% | < 1% | 🔴 **1186% higher** |

---

## 📝 EN | Additional Notes

1. **EN:** Locust EN
2. **Backend EN:** EN 500/503
3. **EN Login EN:** Health Check EN
4. **EN Login EN 100-200 EN:** EN

---

## 📚 EN | References

- **HTML Report:** [load_test_50users.html](load_test_50users.html)
- **CSV Data:** `load_test_50users_stats.csv`, `load_test_50users_failures.csv`
- **Locust File:** [tests/locustfile.py](../tests/locustfile.py)
- **Backend URL:** http://localhost:8000

---

**EN | Generated:** 2026-02-03T10:56:48  
**EN | Total Duration:** 120 seconds (2 minutes)  
**EN | Test Status:** ⚠️ **Completed with Critical Issues**
