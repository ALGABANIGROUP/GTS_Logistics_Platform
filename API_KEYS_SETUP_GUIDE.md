# Fixing the ai_bot_issues issue - Repair guide

##Problem
The `ai_bot_issues` table in the database does not contain the required `title` column, causing a 500 Internal Server Error when accessing:
- `GET /api/v1/dev_maintenance/issues`
- `GET /api/v1/maintenance/issues`

##Solution

### Step 1: Run SQL to repair the database

1. Get the database connection string from the `.env` file

2. Run the following SQL script:

```bash
# Use psql or any PostgreSQL tool
psql "your_connection_string" -f fix_ai_bot_issues_table.sql

```

Or run the commands manually:

```sql
-- Run the contents of the fix_ai_bot_issues_table.sql file

```

### Step 2: Reset Server Startup

```bash
# Restart Backend Server
cd backend
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Step 3: Verify Fix

```bash
# Test Endpoint
curl http://127.0.0.1:8000/api/v1/dev_maintenance/issues\
-H "Authorization: Bearer YOUR_TOKEN"
```

## Expected Outcome

After the fix, the endpoints will be working again and the data issue will be restored:

```json
{
"success": true,

"issues": [
{
"id": 1,

"title": "Issue title",

"description": "Issue description",

"severity": "high",

"status": "open",

"bot_name": "bot_name",

"reported_by": "system",

"created_at": "2026-03-22T10:00:00"

}

]
}
```

## Updated Files

- `fix_ai_bot_issues_table.sql` - SQL script to fix database

- `backend/alembic_migrations/versions/20260322_add_title_to_ai_bot_issues.py` - New Migration

## Success Verification

1. ✅ No 500 errors in records

2. ✅ Endpoints return HTTP 200

3. ✅ Data rendered correctly

4. ✅ Form compatible with database
<parameter name="filePath">c:\Users\enjoy\dev\\GTS\AI_BOT_ISSUES_FIX_README.md