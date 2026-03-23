# Quick Implementation Checklist
**Date:** January 8, 2026  
**Status:** Ready for continuation

## ✅ Completed (Completed - 2/8)

1. ✅ **Tenant Model Updated** 
   - Added: `plan`, `trial_ends_at`, `billing_status`, `status`, `quotas`, `owner_email`
   - File: `backend/models/tenant.py`

2. ✅ **Migration Generated** (NOT applied yet)
   - File: `backend/alembic_migrations/versions/faab766d1a0f_add_tenant_subscription_and_quotas.py`
   - ⚠️ Large migration - review before applying

## 🚧 Remaining (Remaining - 6/8)

### 3. ⏳ Create Quotas System
**Files to create:**
- `backend/security/quotas.py` - Default quotas + QuotaChecker class
- `backend/security/quota_dependency.py` - FastAPI dependencies for enforcement

**See:** `MULTI_TENANT_SECURITY_IMPLEMENTATION_PLAN.md` § Task 3

---

### 4. ⏳ Update Tenant Resolver - FAIL CLOSED
**File to modify:** `backend/security/tenant_resolver.py`

**Key Changes:**
1. Remove default tenant fallback
2. Add conflict detection
3. Return `None` if no clear tenant
4. Raise `HTTPException(400)` in `get_tenant()` dependency

**See:** `MULTI_TENANT_SECURITY_IMPLEMENTATION_PLAN.md` § Task 4

---

### 5. ⏳ Create Public Signup Endpoint
**File to create:** `backend/routes/public_signup.py`

**Features:**
- IP rate limiting (3 signups/day)
- Subdomain validation + uniqueness check
- Email verification flow
- Auto-create tenant + owner user
- FREE_TRIAL auto-assigned

**Mount in main.py:**
```python
from backend.routes.public_signup import router as signup_router
app.include_router(signup_router)
```

**See:** `MULTI_TENANT_SECURITY_IMPLEMENTATION_PLAN.md` § Task 5

---

### 6. ⏳ Add Rate Limiting Middleware
**File to create:** `backend/middleware/rate_limit.py`

**Add to main.py:**
```python
from backend.middleware.rate_limit import RateLimitMiddleware
app.add_middleware(RateLimitMiddleware, requests_per_minute=60)
```

**See:** `MULTI_TENANT_SECURITY_IMPLEMENTATION_PLAN.md` § Task 6

---

### 7. ⏳ Add Quota Enforcement to Routes
**Files to modify:** ALL tenant-scoped routes in `backend/routes/`

**Pattern to apply:**
```python
from backend.security.quota_dependency import enforce_quota
from backend.security.tenant_resolver import get_tenant_id

@router.post("/tickets")
async def create_ticket(
    ticket_data: TicketCreate,
    tenant_id: str = Depends(get_tenant_id),  # ← ADD
    _quota = Depends(lambda r: enforce_quota(r, "tickets")),  # ← ADD
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    # Now guaranteed: tenant_id exists, quota ok
    ...
```

**Routes to update:**
- `support_routes.py` - tickets
- `dispatch_routes.py` - shipments (when model exists)
- `user_routes.py` - user creation
- Any route creating/modifying tenant data

---

### 8. ⏳ Create & Run Smoke Tests
**File to create:** `tests/smoke_test_multi_tenant.py`

**Tests:**
1. `test_tenant_isolation_tickets()` - Verify no cross-tenant data leakage
2. `test_tenant_quota_enforcement()` - Verify FREE_TRIAL limits work

**Run:**
```bash
pytest tests/smoke_test_multi_tenant.py -v -s
```

**Expected:**
```
✅ Ticket isolation verified: No cross-tenant data leakage
✅ Quota enforcement verified: Limits working correctly
```

---

## 🚀 Final Steps (Final Steps Before Launch)

### A. Apply Migration
```bash
# REVIEW FIRST!
code backend/alembic_migrations/versions/faab766d1a0f_add_tenant_subscription_and_quotas.py

# Apply
python -m alembic -c backend/alembic.ini upgrade head
```

### B. Update Existing Data
```sql
-- Set defaults for existing tenants
UPDATE tenants 
SET 
    plan = 'free_trial',
    billing_status = 'not_required',
    status = 'active',
    trial_ends_at = NOW() + INTERVAL '30 days',
    quotas = '{"max_users": 10, "max_tickets_per_day": 100}'::jsonb
WHERE plan IS NULL;
```

### C. Test Locally
```bash
# Terminal 1: Start backend
python -m uvicorn backend.main:app --reload

# Terminal 2: Test signup
curl -X POST http://localhost:8000/api/v1/signup/register \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Test Co",
    "subdomain": "testco",
    "owner_email": "test@example.com",
    "owner_name": "Test User",
    "owner_password": "password123"
  }'

# Terminal 3: Run smoke tests
pytest tests/smoke_test_multi_tenant.py -v
```

### D. Deploy to Staging
```bash
# Push to git
git add .
git commit -m "feat: Multi-tenant security system with quotas"
git push origin main

# Deploy (Render auto-deploys from main)
# Watch logs for migrations

# Test on staging subdomain
curl https://testco.gtsdispatcher.com/api/v1/health
```

### E. Pre-Production Checklist
- [ ] All smoke tests pass on staging
- [ ] Try cross-tenant access - should fail with 400/403
- [ ] Try exceeding quota - should fail with 429
- [ ] Email verification works
- [ ] Subdomain routing works
- [ ] Existing tenants still functional

---

## 📱 Frontend Integration (Bonus)

### Update Signup Page
**File:** `frontend/src/pages/Signup.jsx`

```jsx
import { useState } from 'react';
import axios from 'axios';

export default function Signup() {
    const [formData, setFormData] = useState({
        company_name: '',
        subdomain: '',
        owner_email: '',
        owner_name: '',
        owner_password: ''
    });
    
    const handleSubmit = async (e) => {
        e.preventDefault();
        
        try {
            const response = await axios.post(
                `${import.meta.env.VITE_API_BASE_URL}/api/v1/signup/register`,
                formData
            );
            
            alert(`Success! Check ${formData.owner_email} to verify your account.`);
            window.location.href = '/check-email';
            
        } catch (error) {
            alert(error.response?.data?.detail || 'Signup failed');
        }
    };
    
    return (
        <form onSubmit={handleSubmit}>
            <input
                placeholder="Company Name"
                value={formData.company_name}
                onChange={e => setFormData({...formData, company_name: e.target.value})}
                required
            />
            <input
                placeholder="Subdomain (e.g. mycompany)"
                value={formData.subdomain}
                onChange={e => setFormData({...formData, subdomain: e.target.value})}
                pattern="[a-z0-9]{3,20}"
                required
            />
            <input
                type="email"
                placeholder="Your Email"
                value={formData.owner_email}
                onChange={e => setFormData({...formData, owner_email: e.target.value})}
                required
            />
            <input
                placeholder="Your Name"
                value={formData.owner_name}
                onChange={e => setFormData({...formData, owner_name: e.target.value})}
                required
            />
            <input
                type="password"
                placeholder="Password (8+ chars)"
                value={formData.owner_password}
                onChange={e => setFormData({...formData, owner_password: e.target.value})}
                minLength={8}
                required
            />
            <button type="submit">Create Account</button>
            
            <p>
                Your site will be: <strong>{formData.subdomain || 'yourcompany'}.gtsdispatcher.com</strong>
            </p>
        </form>
    );
}
```

---

## 🔥 Implementation Priorities (Priority Order)

### Day 1 (Day 1):
1. Task 3: Quotas system
2. Task 4: Tenant resolver FAIL CLOSED
3. Test locally

### Day 2 (Day 2):
4. Task 5: Public signup
5. Task 6: Rate limiting
6. Task 7: Quota enforcement in routes

### Day 3 (Day 3):
7. Task 8: Smoke tests
8. Apply migration
9. Deploy to staging
10. Final testing

---

## 📞 If You Encounter a Problem

### Error: "Tenant not identified"
- Check: `backend/security/tenant_resolver.py` - is FAIL CLOSED active?
- Check: Request has subdomain OR X-API-Key OR valid JWT?

### Error: "Quota limit reached"
- Expected! Working correctly
- Check: `backend/security/quotas.py` - DEFAULT_QUOTAS values
- Upgrade tenant plan to increase limits

### Error: Migration fails
- Review migration file first
- Check for FK constraints
- Apply in staging before production

---

**Next Steps:** Start with Task 3 (Quotas system) from `MULTI_TENANT_SECURITY_IMPLEMENTATION_PLAN.md`

**Estimated Time:** 2-3 days for full implementation + testing
