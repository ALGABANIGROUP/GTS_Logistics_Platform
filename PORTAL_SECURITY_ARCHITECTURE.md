# 📊 Portal Security - Visual Flow & Architecture

## 🔄 Request Processing Flow

```
USER SUBMITS REGISTRATION
        |
        v
┌─────────────────────────────────┐
│  Frontend Validation            │
│  - Required fields              │
│  - Email format                 │
│  - CAPTCHA completed            │
└─────────────────────────────────┘
        |
        v (with captcha_token)
POST /portal/requests
        |
        v
┌─────────────────────────────────┐
│  Backend Security Gates         │
│  (in order)                     │
└─────────────────────────────────┘
        |
        v
   GATE 1: CAPTCHA
┌─────────────────────────────────┐
│  verify_hcaptcha(token)         │
│  └─> HTTP 400 if invalid        │
└─────────────────────────────────┘
        |
        v (if passes)
   GATE 2: RATE LIMIT
┌─────────────────────────────────┐
│  check_ip_rate_limit(ip)        │
│  └─> HTTP 429 if exceeded (>5)  │
└─────────────────────────────────┘
        |
        v (if passes)
   GATE 3: DUPLICATE
┌─────────────────────────────────┐
│  check_duplicate_today(email,   │
│                      company)   │
│  └─> HTTP 400 if found (24h)    │
└─────────────────────────────────┘
        |
        v (if all pass)
  CREATE RECORD
┌─────────────────────────────────┐
│  create_portal_request()        │
│  - Insert into portal_requests  │
│  - Record ID generated          │
└─────────────────────────────────┘
        |
        v
STEP 1: EMAIL VERIFICATION
┌─────────────────────────────────┐
│  create_verification_token()    │
│  - Generate random token       │
│  - Save to email_verifications │
│  - Send email with link        │
└─────────────────────────────────┘
        |
        v
STEP 2: ADMIN NOTIFICATION
┌─────────────────────────────────┐
│  create_admin_notification()    │
│  - Create notification record  │
│  - Mark as unread              │
│  - Admin sees in dashboard     │
└─────────────────────────────────┘
        |
        v
STEP 3: AUDIT LOG
┌─────────────────────────────────┐
│  log_audit_action()            │
│  - Action: "request_created"   │
│  - Actor: "system"             │
│  - Details: JSONB with info    │
│  - IP address recorded         │
└─────────────────────────────────┘
        |
        v
RESPONSE TO USER
┌─────────────────────────────────┐
│  HTTP 201 Created              │
│  {                              │
│    "id": 1,                     │
│    "status": "pending",         │
│    "message": "Check email"     │
│  }                              │
└─────────────────────────────────┘
        |
        v
USER RECEIVES EMAIL
        |
        v
USER CLICKS LINK
GET /portal/verify-email?token=...
        |
        v
┌─────────────────────────────────┐
│  verify_email(token)           │
│  - Check if valid              │
│  - Check if expired            │
│  - Update verified_at          │
│  - Log action (audit)          │
└─────────────────────────────────┘
        |
        v
FRONTEND SHOWS SUCCESS
        |
        v
REDIRECT TO LOGIN
        |
        v
USER LOGS IN & USES PORTAL ✓
```

---

## 🏗️ Architecture Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                         │
├────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────┐                                       │
│  │  /register           │  ← User Registration Form             │
│  │  ├─ System selection  │    └─ CAPTCHA component (dark theme) │
│  │  ├─ Country dropdown  │    └─ Conditional filtering          │
│  │  │  (TMS vs LoadBoard)│                                       │
│  │  ├─ Email field       │                                       │
│  │  └─ CAPTCHA field     │                                       │
│  └──────────────────────┘                                       │
│           |                                                      │
│           | POST /portal/requests                               │
│           | (with captcha_token)                                │
│           v                                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  /verify-email                                            │   │
│  │  ├─ Gets token from URL params                            │   │
│  │  ├─ Shows spinner while verifying                         │   │
│  │  ├─ On success: green checkmark + redirect               │   │
│  │  └─ On error: red X + error message                      │   │
│  └──────────────────────────────────────────────────────────┘   │
│           ^                                                      │
│           |                                                      │
│  /admin/notifications                 /admin/audit-log/:id      │
│  ├─ Real-time notification list       ├─ Timeline view         │
│  ├─ Unread count                      ├─ Action details        │
│  ├─ Filter (all/unread/read)          ├─ IP addresses          │
│  ├─ Auto-refresh 30s                  └─ Export option         │
│  └─ Direct links to details                                     │
│                                                                  │
└────────────────────────────────────────────────────────────────┘
                                |
                                | HTTP/REST API
                                |
┌────────────────────────────────────────────────────────────────┐
│                       BACKEND (FastAPI)                         │
├────────────────────────────────────────────────────────────────┤
│                                                                  │
│  API Routes:                                                     │
│  ├─ POST /portal/requests (with security gates)                │
│  ├─ GET /portal/verify-email                                   │
│  ├─ GET /admin/portal/notifications                            │
│  └─ GET /admin/portal/requests/:id/audit-log                   │
│                                                                  │
│  Security Functions:                                            │
│  ├─ verify_hcaptcha()           (hCaptcha API call)           │
│  ├─ check_ip_rate_limit()       (IP-based limiting)           │
│  ├─ check_duplicate_today()     (Email/company check)         │
│  ├─ create_verification_token() (Token generation)            │
│  ├─ verify_email()              (Token validation)            │
│  ├─ create_admin_notification() (Notification creation)       │
│  └─ log_audit_action()          (Audit recording)             │
│                                                                  │
│  External Services:                                             │
│  ├─ hCaptcha API (token verification)                          │
│  ├─ SMTP Email (send verification emails)                      │
│  └─ PostgreSQL Database (data persistence)                     │
│                                                                  │
└────────────────────────────────────────────────────────────────┘
                                |
                                | SQL Queries
                                |
┌────────────────────────────────────────────────────────────────┐
│                    DATABASE (PostgreSQL)                        │
├────────────────────────────────────────────────────────────────┤
│                                                                  │
│  portal_requests (existing)                                      │
│  ├─ id (PK)                                                     │
│  ├─ email, company, full_name                                   │
│  ├─ [NEW] email_verified (bool)                                │
│  ├─ [NEW] verification_token (varchar)                         │
│  ├─ [NEW] ip_address (varchar)                                 │
│  └─ created_at                                                  │
│     └─ Indexes on: email, company, ip_address                  │
│                                                                  │
│  [NEW] email_verifications                                      │
│  ├─ id (PK)                                                     │
│  ├─ email (unique)                                              │
│  ├─ verification_token (indexed)                                │
│  ├─ verified_at (NULL = unverified)                            │
│  ├─ expires_at (24h from creation)                             │
│  └─ created_at                                                  │
│                                                                  │
│  [NEW] admin_notifications                                      │
│  ├─ id (PK)                                                     │
│  ├─ request_id (FK)                                             │
│  ├─ notification_type (new_request, approved, etc)             │
│  ├─ title, message                                              │
│  ├─ read_at (NULL = unread)                                    │
│  └─ created_at                                                  │
│                                                                  │
│  [NEW] audit_log                                                │
│  ├─ id (PK)                                                     │
│  ├─ request_id (FK)                                             │
│  ├─ action (request_created, email_verified, etc)              │
│  ├─ actor (email or "system")                                   │
│  ├─ details (JSONB flexible storage)                            │
│  ├─ ip_address (varchar)                                        │
│  └─ created_at                                                  │
│     └─ Indexes on: request_id, action, created_at              │
│                                                                  │
│  [NEW] portal_request_ip_limits                                 │
│  ├─ id (PK)                                                     │
│  ├─ ip_address (unique)                                         │
│  ├─ request_count (incremented)                                 │
│  ├─ first_request_at (time window start)                        │
│  └─ updated_at                                                  │
│                                                                  │
└────────────────────────────────────────────────────────────────┘
```

---

## 🔐 Security Layers

```
Request arrives at /portal/requests
        ↓
     LAYER 1: CAPTCHA
    ┌──────────────────┐
    │ hCaptcha token   │ ← Prevents bots/automation
    │ validation       │    - No token = 400 error
    │                  │    - Invalid = 400 error
    └──────────────────┘
        ↓ (if passes)
     LAYER 2: RATE LIMITING
    ┌──────────────────┐
    │ 5 requests       │ ← Prevents volume attacks
    │ per hour per IP  │    - Tracks IP in DB
    │                  │    - Counts requests
    │                  │    - Blocks on 6th request (429)
    └──────────────────┘
        ↓ (if passes)
     LAYER 3: DUPLICATE PREVENTION
    ┌──────────────────┐
    │ Check if email   │ ← Prevents spam resubmission
    │ or company       │    - Looks back 24 hours
    │ already submitted│    - Blocks duplicate (400)
    │ in 24 hours      │
    └──────────────────┘
        ↓ (if passes)
     LAYER 4: DATABASE INSERT
    ┌──────────────────┐
    │ Save request     │ ← Data persistence
    │ to portal_requests
    │                  │
    └──────────────────┘
        ↓
     LAYER 5: EMAIL VERIFICATION TOKEN
    ┌──────────────────┐
    │ Generate token   │ ← Confirms valid email
    │ Save to DB       │    - User clicks link
    │ Send via email   │    - Token verified
    │                  │    - Email marked verified
    └──────────────────┘
        ↓
     LAYER 6: ADMIN NOTIFICATION
    ┌──────────────────┐
    │ Create alert     │ ← Human review enabled
    │ for admins       │    - Admin sees notification
    │ in dashboard     │    - Can approve/deny
    │                  │    - Can review audit trail
    └──────────────────┘
        ↓
     LAYER 7: AUDIT LOG
    ┌──────────────────┐
    │ Record action    │ ← Compliance & investigation
    │ with actor, IP   │    - Complete history
    │ timestamp, details
    │                  │    - IP tracking for abuse
    └──────────────────┘
        ↓
    REQUEST ACCEPTED ✓
```

---

## 📊 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interaction                          │
│                                                              │
│  1. Register Form Submitted                                 │
│     └─ Includes: email, company, system, CAPTCHA token      │
│                                                              │
│  2. Email Verification                                      │
│     └─ Clicks link in email                                 │
│                                                              │
│  3. Admin Review                                            │
│     └─ Views notification in dashboard                      │
│                                                              │
│  4. Portal Access                                           │
│     └─ User logs in after approval                          │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    Backend Processing                        │
│                                                              │
│  Security Gate 1: CAPTCHA Verification                      │
│  ├─ Input: captcha_token from form                          │
│  ├─ Call: verify_hcaptcha(token)                            │
│  └─ Output: true/false                                      │
│                                                              │
│  Security Gate 2: Rate Limiting                             │
│  ├─ Input: client IP address                                │
│  ├─ Call: check_ip_rate_limit(ip)                           │
│  └─ Output: true (limit exceeded) or false                  │
│                                                              │
│  Security Gate 3: Duplicate Prevention                      │
│  ├─ Input: email, company name                              │
│  ├─ Call: check_duplicate_today(email, company)             │
│  └─ Output: true (found duplicate) or false                 │
│                                                              │
│  Data Creation                                              │
│  ├─ Input: form data                                        │
│  ├─ Call: create_portal_request(...)                        │
│  └─ Output: request_id                                      │
│                                                              │
│  Email Verification Setup                                   │
│  ├─ Input: email                                            │
│  ├─ Call: create_verification_token(email)                  │
│  │         Generate random token                            │
│  │         Save to email_verifications table                │
│  │         Send email with verification link               │
│  └─ Output: verification token created                      │
│                                                              │
│  Admin Notification                                         │
│  ├─ Input: request_id                                       │
│  ├─ Call: create_admin_notification(request_id, ...)        │
│  └─ Output: notification created in DB                      │
│                                                              │
│  Audit Logging                                              │
│  ├─ Input: request_id, action, ip_address                   │
│  ├─ Call: log_audit_action(...)                             │
│  └─ Output: audit entry created in DB                       │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                     Database Storage                         │
│                                                              │
│  portal_requests table                                      │
│  └─ Stores: Complete registration information               │
│     └─ Plus: email_verified flag, ip_address                │
│                                                              │
│  email_verifications table                                  │
│  └─ Stores: Verification tokens linked to emails            │
│     └─ Tracks: verified_at timestamp for each email         │
│                                                              │
│  admin_notifications table                                  │
│  └─ Stores: Notifications for admins                        │
│     └─ Tracks: read_at status for each notification         │
│                                                              │
│  audit_log table                                            │
│  └─ Stores: Complete action history                         │
│     └─ Includes: actor, IP, action, timestamp, details      │
│                                                              │
│  portal_request_ip_limits table                             │
│  └─ Stores: Rate limiting state per IP                      │
│     └─ Tracks: request count and time window                │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Email Verification Flow

```
User Submits Registration
        ↓
Backend checks all security gates
        ↓ (all pass)
Backend sends verification email
        ↓
┌───────────────────────────────────────┐
│ Email Received by User                │
│ Subject: "Verify your email..."       │
│ Body: Includes verification link      │
│ Link: https://.../verify-email?token= │
└───────────────────────────────────────┘
        ↓
User clicks verification link
        ↓
GET /portal/verify-email?token=abc123def456
        ↓
Backend processes:
├─ Extract token from URL
├─ Look up in email_verifications table
├─ Check if token exists
├─ Check if not expired (24h)
├─ Check if not already verified
├─ If all OK: Update verified_at = NOW()
└─ If error: Return error message
        ↓
Frontend shows result:
├─ If success: Green checkmark + "Email verified"
├─ If error: Red X + error message
└─ Auto-redirect to login after 3s
        ↓
Backend logs action:
├─ log_audit_action(..., action="email_verified", ...)
└─ Entry appears in audit trail
        ↓
Admin can see:
├─ In notifications dashboard: "Email verified"
├─ In audit log: Timestamp of verification
└─ Status: Portal request now has email_verified=true
```

---

## 👥 Admin Workflow

```
┌────────────────────────────────────┐
│     Admin Dashboard                │
│  /admin/portal-requests            │
└────────────────────────────────────┘
        ↓
Admin sees list of pending requests
├─ Request ID: 123
├─ Applicant: John Doe
├─ Company: Acme Corp
├─ Status: Pending (needs review)
└─ [View Details] button
        ↓ (Admin clicks "View Details")
┌────────────────────────────────────┐
│     Request Detail Page            │
│  Shows full information            │
└────────────────────────────────────┘
        ↓
Admin can:
├─ [View Audit Log] - See history
├─ [Approve] - Grant access
├─ [Deny] - Reject request
└─ [View Notifications] - See all alerts
        ↓ (Admin clicks "View Audit Log")
┌────────────────────────────────────┐
│     Audit Log Timeline             │
│  /admin/requests/123/audit-log     │
│                                    │
│  Entry 1:                          │
│  ├─ Action: "request_created"     │
│  ├─ Time: 2025-01-20 10:00 AM     │
│  ├─ Actor: "system"                │
│  ├─ IP: 203.0.113.45              │
│  └─ Details: {user_type: ..., system: ...}
│                                    │
│  Entry 2:                          │
│  ├─ Action: "email_verified"      │
│  ├─ Time: 2025-01-20 10:05 AM     │
│  ├─ Actor: "system"                │
│  ├─ IP: 203.0.113.45              │
│  └─ Details: {}                    │
│                                    │
│  [Export to PDF] button            │
└────────────────────────────────────┘
        ↓ (Admin goes back to approve)
┌────────────────────────────────────┐
│     Admin Approves Request         │
│                                    │
│  [Approve] button clicked          │
│  └─ Backend action: "approved"    │
│  └─ Audit logged                   │
│  └─ Email sent to user             │
│  └─ TMS access granted (if requested)
│  └─ Status changed to "approved"   │
└────────────────────────────────────┘
        ↓
Admin sees confirmation:
├─ Success message
├─ Request moved to "Approved" tab
└─ New notification: "Request approved"
        ↓
User receives email:
├─ Subject: "Your portal access has been approved"
├─ Instructions for next steps
└─ If TMS: Includes TMS onboarding link
```

---

## 📱 Country Selection Logic

```
User selects System Type:

IF System = "standard"
   └─ Shows: COUNTRIES_TMS (all 34 countries)
      └─ US, CA, MX, BR, AU, NZ, EU, Asia...
        
IF System = "tms"
   └─ Shows: COUNTRIES_TMS (all 34 countries)
      └─ US, CA, MX, BR, AU, NZ, EU, Asia...
        
IF System = "loadboard"
   └─ Shows: COUNTRIES_LOADBOARD (only 2)
      └─ US
      └─ Canada
        
IF System = "both"
   └─ Shows: COUNTRIES_TMS (all 34 countries)
      └─ US, CA, MX, BR, AU, NZ, EU, Asia...

Frontend filtering logic:
    const countriesList = form.system === "loadboard" 
        ? COUNTRIES_LOADBOARD 
        : COUNTRIES_TMS;

Backend validation (should add):
    if request.system == "loadboard":
        if request.country not in ["US", "CA"]:
            return 400 error
```

---

## ⏱️ Timing & Performance

```
Request Timeline:
├─ 0-100ms: CAPTCHA token received
├─ 100-200ms: Backend validates CAPTCHA with hCaptcha API
├─ 200-300ms: Rate limit check (DB query <1ms)
├─ 300-400ms: Duplicate check (DB query <5ms)
├─ 400-500ms: Create portal request (DB insert <2ms)
├─ 500-600ms: Create verification token (DB insert <2ms)
├─ 600-1500ms: Send verification email (SMTP call)
├─ 1500-1600ms: Create admin notification (DB insert <2ms)
├─ 1600-1700ms: Log audit action (DB insert <3ms)
└─ 1700ms: Response sent to user

Total: ~1.7 seconds (98% is CAPTCHA validation + email sending)
```

---

## 🎯 Summary

```
┌─────────────────────────────────────────────────┐
│  7 Layers of Security                           │
├─────────────────────────────────────────────────┤
│  1. hCaptcha        → Block bots                │
│  2. Rate Limit      → Block volume attacks      │
│  3. Dedup           → Block spam                │
│  4. Email Verify    → Confirm valid email       │
│  5. Notifications   → Enable human review       │
│  6. Audit Log       → Compliance trail          │
│  7. Regional Limits → Enforce business rules    │
└─────────────────────────────────────────────────┘

Result: Enterprise-grade portal security ✓
```

---

For more information, see the comprehensive documentation files listed in [PORTAL_SECURITY_GUIDE.md](./PORTAL_SECURITY_GUIDE.md)
