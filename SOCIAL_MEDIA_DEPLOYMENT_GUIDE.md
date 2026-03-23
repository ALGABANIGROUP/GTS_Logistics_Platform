# Social Media System - Next Steps Deployment Guide

## ✅ Completed Integration Tasks

### 1. ✅ Database Migration
- **Migration File Created**: `backend/alembic/versions/sm_001_add_social_media_tables.py`
- **Status**: Ready to apply
- **Tables**: 5 main tables + indexes
  - `social_media_accounts` - Platform connections
  - `social_media_posts` - Content and scheduling
  - `social_media_analytics` - Performance metrics
  - `social_media_templates` - Content templates
  - `social_media_settings` - Global configuration

**To Apply Migration**:
```bash
cd d:\GTS
python -m alembic -c backend\alembic.ini upgrade head
```

### 2. ✅ Backend Routes Registered
- **Admin Routes**: `/api/v1/admin/social-media/*` (Admin-only)
- **Public Routes**: `/api/v1/social-media/*` (Open access)
- **Endpoints Configured**: 18 total
  - 16 Admin endpoints (connect, disconnect, CRUD posts, analytics, settings)
  - 2 Public endpoints (social links, recent posts)

**Status**: Routes imported and mounted in `backend/main.py`

### 3. ✅ Frontend Components Integrated
- **Admin Dashboard**: `/admin/social-media`
  - File: `frontend/src/pages/admin/SocialMedia.jsx`
  - Component: `frontend/src/components/admin/SocialMediaDashboard.jsx`
  - Styling: `frontend/src/components/admin/SocialMediaDashboard.css`
  - Features: 5 tabs (Overview, Accounts, Scheduler, Analytics, Settings)

- **Public Footer**: Site-wide footer on all pages
  - File: `frontend/src/components/layout/SocialMediaFooter.jsx`
  - Styling: `frontend/src/components/layout/SocialMediaFooter.css`
  - Features: Social links modal, newsletter signup
  - Integrated into: `frontend/src/components/AppShell.jsx`

**Status**: Components created and integrated into routing

### 4. ✅ System Testing
- **Database Models**: ✓ Validated (5 tables, all columns)
- **API Clients**: ✓ Validated (LinkedIn, Twitter, Facebook)
- **Business Logic**: ✓ Validated (AutoPoster, Analytics)
- **Frontend Components**: ✓ All 5 files present and integrated
- **Backend Integration**: ✓ Routes imported and mounted
- **Frontend Integration**: ✓ Routes and components wired

**Status**: All components are syntactically correct and properly integrated

---

## 🚀 Remaining Tasks for Full Deployment

### Step 1: Apply Database Migration (5 minutes)
```powershell
# Windows PowerShell
cd d:\GTS
python -m alembic -c backend\alembic.ini upgrade head
```

**What happens**:
- Creates 5 new tables in PostgreSQL
- Creates 8 indexes for performance
- Adds foreign key relationships
- Registers migration in alembic_version

**Verification**:
```bash
python -m alembic -c backend\alembic.ini current
# Should show: sm_002_social_media (head)
```

---

### Step 2: Start Backend Server (2 minutes)
```powershell
# Activate environment if not already done
.\run-dev.ps1
# Or manually:
cd backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**Expected Output**:
```
[main] social_media_admin router mounted at /api/v1/admin/social-media (admin-only)
[main] social_media_public router mounted at /api/v1/social-media
```

---

### Step 3: Start Frontend Development Server (2 minutes)
```powershell
cd frontend
npm run dev
```

**Expected**: Frontend runs on http://localhost:5173

---

### Step 4: Test System (5 minutes)

#### Test 1: Public Footer
1. Navigate to http://localhost:5173
2. Scroll to bottom of any page
3. Should see social media footer with icons
4. Click "More Platforms →" to open modal

#### Test 2: Admin Dashboard
1. Login as admin user
2. Navigate to http://localhost:5173/admin/social-media
3. Should see 5-tab dashboard (Overview, Accounts, Scheduler, Analytics, Settings)

#### Test 3: API Endpoints (without authentication setup)
```bash
# Public endpoint (no auth needed)
curl http://127.0.0.1:8000/api/v1/social-media/settings/social-links

# Admin endpoint (requires auth token)
curl -H "Authorization: Bearer <your_token>" http://127.0.0.1:8000/api/v1/admin/social-media/accounts
```

---

### Step 5: Configure API Credentials (Optional - for Full Features)

To enable full auto-posting and analytics, set up platform API credentials:

#### LinkedIn Setup
1. Go to https://www.linkedin.com/developers
2. Create new app in your organization
3. Get: Client ID, Client Secret
4. Set environment variables:
   ```
   LINKEDIN_CLIENT_ID=your_client_id
   LINKEDIN_CLIENT_SECRET=your_client_secret
   LINKEDIN_ACCESS_TOKEN=your_access_token
   ```

#### Twitter Setup
1. Go to https://developer.twitter.com/
2. Create new app (elevated access required)
3. Get: Bearer Token, API Key, API Secret
4. Set environment variables:
   ```
   TWITTER_BEARER_TOKEN=your_bearer_token
   TWITTER_API_KEY=your_api_key
   TWITTER_API_SECRET=your_api_secret
   ```

#### Facebook Setup
1. Go to https://developers.facebook.com/
2. Create new app
3. Get: Page Access Token, Page ID
4. Set environment variables:
   ```
   FACEBOOK_PAGE_ACCESS_TOKEN=your_page_token
   FACEBOOK_PAGE_ID=your_page_id
   ```

---

## 📋 Pre-Deployment Checklist

Before deploying to production:

- [ ] Database migration applied successfully
- [ ] Backend server starts without errors
- [ ] Frontend builds without errors
- [ ] Admin dashboard loads at `/admin/social-media`
- [ ] Public footer visible on all pages
- [ ] API endpoints respond (test with curl)
- [ ] Environment variables set (if using API credentials)
- [ ] SSL/HTTPS configured
- [ ] Database backups created
- [ ] Admin users have access rights
- [ ] Error logs monitored
- [ ] Performance tested under load

---

## 🐛 Troubleshooting

### Database Migration Issues
**Problem**: "Can't locate revision identified by 'sm_002_social_media'"

**Solution**:
```bash
# Check current migrations
python -m alembic -c backend\alembic.ini history

# Ensure migration file has correct down_revision
# Should be: down_revision = 'c1c4546306e6'
```

### Import Errors in Routes
**Problem**: "cannot import name 'X' from backend.Y"

**Solution**:
1. Verify import paths match your setup
2. Check that all modules are properly initialized
3. Look at similar routes for correct import patterns

### Frontend Component Not Loading
**Problem**: "SocialMedia route not found"

**Solution**:
1. Check App.jsx has the import: `import SocialMedia from "./pages/admin/SocialMedia"`
2. Check route is registered: `path="/admin/social-media"`
3. Verify RequireAuth roles allow access

### API Endpoints Returning 404
**Problem**: Routes not found when calling `/api/v1/admin/social-media/*`

**Solution**:
1. Verify backend server is running
2. Check main.py mounted the routers
3. Look at server startup logs for mount messages
4. Test with correct prefix in curl

---

## 📚 Related Documentation

- **SOCIAL_MEDIA_SYSTEM_COMPLETE.md** - Full architecture and API reference
- **SOCIAL_MEDIA_QUICK_START.md** - 5-minute setup guide
- **SOCIAL_MEDIA_IMPLEMENTATION_SUMMARY.md** - Project overview

---

## 🎯 Next Phase: Full Features

Once basic integration is complete, these features are ready to enable:

1. **Auto-Posting**: Schedule posts to multiple platforms
2. **Analytics Dashboard**: Track performance metrics
3. **Content Templates**: Reusable post templates
4. **Rate Limiting**: Platform-specific posting limits
5. **Engagement Tracking**: Monitor likes, comments, shares
6. **Recommendations Engine**: AI-powered posting suggestions

---

## ✨ Production Deployment

For production deployment to Render/AWS:

```bash
# 1. Push code to repository
git add backend/routes/social_media_routes.py backend/models/social_media.py
git add backend/social_media/
git add backend/alembic/versions/sm_*.py
git add frontend/src/pages/admin/SocialMedia.jsx
git add frontend/src/components/admin/SocialMediaDashboard.*
git add frontend/src/components/layout/SocialMediaFooter.*
git commit -m "feat: add social media management system"
git push

# 2. Trigger deployment pipeline
# (Render will automatically run migrations and deploy)

# 3. Monitor deployment
# Check server logs for migration status and route registration
```

---

**Status**: ✅ Ready for deployment!

**Last Updated**: January 8, 2026
**Version**: 1.0.0
**Maintainer**: AI Team
