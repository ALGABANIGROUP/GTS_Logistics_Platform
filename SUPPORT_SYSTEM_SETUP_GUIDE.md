# Support System Configuration Guide
# Support System Configuration Guide

## 1. Environment Variables (Environment variables)

Add to your `.env` file:

```bash
# ========================================
# Support System Email Configuration
# ========================================

# SMTP Configuration (for sending)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=support@yourdomain.com
SMTP_FROM_NAME=GTS Support

# IMAP Configuration (for receiving mail)
IMAP_HOST=imap.gmail.com
IMAP_PORT=993
IMAP_USER=your-email@gmail.com
IMAP_PASSWORD=your-app-password
IMAP_FOLDER=INBOX

# Support System Configuration
SUPPORT_EMAIL=support@yourdomain.com
SUPPORT_PHONE=+1-800-SUPPORT
FRONTEND_URL=http://localhost:5173
```

### Important Notes:
- **Gmail**: use App Password (application password) not the main password
- **SendGrid/Mailgun**: use API keys instead of username/password
- **Security**: do not put passwords in Git, use `.env.local`

## 2. Database Migration (database migration)

Run migration:

```powershell
# Apply migration
python -m alembic -c backend\alembic.ini upgrade head

# Check created tables
python -c "from backend.database.config import engine; print(engine)"
```

### Alembic Merge (if there are multiple heads)

```powershell
python -m alembic -c backend\alembic.ini heads
python -m alembic -c backend\alembic.ini merge -m "merge support heads"
python -m alembic -c backend\alembic.ini upgrade head
```

## 3. Database Seed Data (seed data)

```python
# backend/scripts/seed_support_data.py
from backend.database.config import AsyncSessionLocal
from backend.models.support_models import SLALevel
from sqlalchemy import select

async def seed_sla_levels():
    """Create default service levels"""
    async with AsyncSessionLocal() as session:
        # check if data already exists
        stmt = select(SLALevel).limit(1)
        result = await session.execute(stmt)
        if result.scalar():
            return
        
        levels = [
            SLALevel(priority='critical', response_time_hours=1, resolution_time_hours=4, escalation_after_hours=2),
            SLALevel(priority='high', response_time_hours=2, resolution_time_hours=8, escalation_after_hours=4),
            SLALevel(priority='medium', response_time_hours=4, resolution_time_hours=24, escalation_after_hours=12),
            SLALevel(priority='low', response_time_hours=8, resolution_time_hours=48, escalation_after_hours=24),
        ]
        session.add_all(levels)
        await session.commit()

# run seeding
if __name__ == '__main__':
    import asyncio
    asyncio.run(seed_sla_levels())
```

## 4. Register Routes in Backend (register routes)

Make sure that `support_routes.py` is registered in `backend/main.py`:

```python
# backend/main.py

# import the route
from backend.routes.support_routes import router as support_router

# register the route
app.include_router(support_router, prefix="/api/v1/support", tags=["Support"])
```

## 5. Create Email Templates (create email templates)

```python
# backend/scripts/create_email_templates.py
from backend.database.config import AsyncSessionLocal
from backend.models.support_models import EmailTemplate

templates = [
    EmailTemplate(
        name='ticket_created',
        subject='Ticket #{ticket_number} Created',
        body_html='''
        <h2>Hello {customer_name},</h2>
        <p>Thank you for contacting us. Your support ticket has been created.</p>
        <p><strong>Ticket Number:</strong> {ticket_number}</p>
        <p><strong>Priority:</strong> {priority}</p>
        <p><strong>Expected Response Time:</strong> {response_time}</p>
        <p>You can track your ticket at: <a href="{ticket_url}">View Ticket</a></p>
        '''
    ),
    # more templates...
]
```

## 6. Test Email Integration (test email integration)

```python
# test_support_email.py
import asyncio
from backend.services.support_email_service import SupportEmailService

async def test():
    service = SupportEmailService()
    
    # test sending email
    await service.send_ticket_created_email(
        ticket_number="TK-00001",
        customer_email="test@example.com",
        customer_name="Ahmed",
        priority="high",
        response_due="2024-01-15 14:00:00"
    )
    print("Email sent successfully!")

asyncio.run(test())
```

## 7. Frontend Configuration (frontend configuration)

Make sure that `VITE_API_BASE_URL` is correct in `frontend/.env`:

```
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## 8. Enable Support Features in Sidebar (enable features in sidebar)

In `frontend/src/components/Layout.jsx` add:

```jsx
{isAdmin && (
  <>
    <NavLink to="/support/tickets" label="Support Tickets" />
    <NavLink to="/admin/support" label="Support Admin" />
    <NavLink to="/support/knowledge-base" label="Knowledge Base" />
  </>
)}
```

## 9. Email Polling Setup (email polling setup)

In `backend/main.py` startup:

```python
@app.on_event("startup")
async def startup_email_polling():
    """Start email polling"""
    scheduler.add_job(
        SupportEmailService().check_support_mailbox,
        "interval",
        minutes=5,
        id="support_email_polling"
    )
    
    scheduler.add_job(
        SupportEmailService().check_sla_breaches,
        "interval",
        minutes=15,
        id="support_sla_check"
    )
```

## 10. SSL Certificate for SMTP (SSL certificate)

Some mail servers require SSL:

```python
# in support_email_service.py
async with aiosmtplib.SMTP(hostname=SMTP_HOST, port=SMTP_PORT, use_tls=True) as smtp:
    await smtp.login(SMTP_USER, SMTP_PASSWORD)
```

## Common Issues (common issues)

### ❌ "Module not found: support_models"
```powershell
# check that the file exists
ls backend/models/support_models.py
```

### ❌ "Database connection error"
```powershell
# check environment variables
python -c "import os; print(os.getenv('DATABASE_URL'))"
```

### ❌ "Email failed to send"
```python
# try direct connection
import smtplib
smtp = smtplib.SMTP("smtp.gmail.com", 587)
smtp.starttls()
smtp.login("your-email@gmail.com", "app-password")
```

### ❌ "SLA times not calculating"
Make sure that `SLALevel` contains data:
```sql
SELECT * FROM sla_levels;
```

## Monitoring (monitoring)

```python
# Check support metrics
GET /api/v1/support/stats

# Check SLA compliance
GET /api/v1/support/stats/agent/me

# Check email status
SELECT status, COUNT(*) FROM support_emails GROUP BY status;
```

## Performance Tips (performance tips)

1. **Index on frequently queried columns**: `status`, `sla_status`, `customer_id`
2. **Archive old tickets**: Move resolved tickets > 90 days to archive table
3. **Email batching**: Send emails in batches instead of one-by-one
4. **Cache knowledge base**: Cache popular articles

## Security (security)

1. ✅ **JWT Authentication**: all routes are protected by JWT
2. ✅ **Role-based Access**: customers don't see internal notes
3. ✅ **Rate Limiting**: applied to `/commands/human`
4. ✅ **Email Validation**: email address validation
5. ✅ **Audit Logging**: logging all actions in `ticket_activities`

---

**Next Steps** (next steps):
1. ✅ apply migration (Database Migration)
2. ✅ set environment variables (Environment Variables)
3. ✅ test email integration (Email Integration)
4. ✅ enable routes in frontend (Frontend Routes)
5. ⏳ create live chat dashboard (Live Chat Dashboard)
