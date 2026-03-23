# Email Settings Integration - Complete Documentation

## Overview
The GTS Platform email system now has full integration between Platform Settings and the Email Command Center.

## Architecture

### 1. **Platform Settings (Frontend)**
Location: `frontend/src/pages/admin/PlatformSettings.jsx`

Configuration fields:
- SMTP Server (hostname)
- SMTP Port (default: 587)
- SMTP Password (encrypted)
- From Email (default sender)
- From Name (display name)
- Use SSL (checkbox)
- Use TLS (checkbox)

### 2. **Backend Storage**
Location: `backend/services/platform_settings_store.py`

- Email settings stored in `platform_settings` table
- Password is encrypted using crypto module
- Settings merged with defaults on retrieval

### 3. **Email Settings Provider**
Location: `backend/services/email_settings_provider.py`

Service functions:
- `get_email_settings(session)` - Get config with env fallbacks
- `is_email_configured(session)` - Check if email is ready
- `update_email_settings(...)` - Update email config
- `get_smtp_config_for_mailbox(...)` - Get mailbox-specific config

### 4. **API Endpoints**
Location: `backend/routes/admin_platform_settings.py`

Endpoints:
- `GET /api/v1/admin/platform-settings` - Get all settings
- `PUT /api/v1/admin/platform-settings` - Update settings
- `POST /api/v1/admin/platform-settings/test-email` - Test email config

### 5. **Email Command Center Integration**
Location: `backend/routes/email_center.py`

The Email Command Center can now:
- Use platform settings for default SMTP config
- Create mailboxes with platform defaults
- Send emails using configured settings

## How It Works

### Setting Up Email (User Flow)

1. **Navigate to Platform Settings**
   - Go to `localhost:5173/admin/settings`
   - Click on "Email" tab

2. **Configure SMTP Settings**
   - Enter SMTP server (e.g., `smtp.gmail.com`)
   - Enter SMTP port (e.g., `587`)
   - Enter SMTP password (encrypted automatically)
   - Enter from email (e.g., `noreply@company.com`)
   - Enter from name (e.g., `GTS Logistics`)
   - Check SSL/TLS options as needed

3. **Test Configuration**
   - Enter a test email address
   - Click "Send Test Email"
   - Check inbox for test message

4. **Save Settings**
   - Click "Save Email Settings"
   - Settings are encrypted and stored

### Backend Data Flow

```
User Input → Frontend (PlatformSettings.jsx)
    ↓
PUT /api/v1/admin/platform-settings
    ↓
platform_settings_store.py
    ↓ (encrypts smtpPassword)
platform_settings table (PostgreSQL)
    ↓
email_settings_provider.py
    ↓
Email Command Center / SMTP Services
```

### Test Email Flow

```
User clicks "Send Test Email"
    ↓
POST /api/v1/admin/platform-settings/test-email
    ↓
email_settings_provider.get_email_settings()
    ↓
Decrypt password from platform_settings
    ↓
Connect to SMTP server
    ↓
Send test email with HTML template
    ↓
Return success/failure to user
```

## Security Features

1. **Password Encryption**
   - SMTP passwords encrypted before storage
   - Uses platform crypto module
   - Decrypted only when needed

2. **Masked Secrets**
   - Passwords shown as `********` in API responses
   - Only raw values used during save/send operations

3. **Fallback to Environment**
   - If settings not configured, falls back to env vars
   - Support for legacy configurations

## Email Command Center Integration

### Mailbox Configuration
When creating a bot mailbox, the system:
1. Reads platform email settings
2. Uses SMTP config as defaults
3. Allows per-mailbox overrides
4. Encrypts mailbox-specific credentials

### Sending Emails
Email Command Center bots can:
1. Use platform SMTP settings
2. Send from configured "from email"
3. Use encrypted credentials
4. Log all email activity

## Testing

### Test Email Configuration
```bash
curl -X POST http://localhost:8000/api/v1/admin/platform-settings/test-email \
  -H "Content-Type: application/json" \
  -d '{"test_email": "test@example.com"}'
```

### Check Email Settings
```bash
curl http://localhost:8000/api/v1/admin/platform-settings
```

## Environment Variables (Optional Fallbacks)

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_PASSWORD=your-password
MAIL_FROM=noreply@company.com
MAIL_FROM_NAME=GTS Platform
EMAIL_SHARED_PASSWORD=shared-password
```

## Troubleshooting

### Email not sending
1. Check SMTP credentials in Platform Settings
2. Verify SMTP server allows connections
3. Check firewall/network settings
4. Test with "Send Test Email" button
5. Check backend logs for SMTP errors

### Password not working
1. Ensure password is saved correctly
2. Check if 2FA/App Password required (Gmail)
3. Verify SMTP authentication enabled
4. Check password special characters

### Settings not saving
1. Check database connection
2. Verify `platform_settings` table exists
3. Check backend logs for errors
4. Ensure user has admin role

## Files Modified/Created

### Created
- `backend/services/email_settings_provider.py` - Email config service
- `EMAIL_SETTINGS_INTEGRATION.md` - This documentation

### Modified
- `backend/services/platform_settings_store.py` - Added email defaults and password encryption
- `backend/routes/admin_platform_settings.py` - Added test email endpoint
- `frontend/src/pages/admin/PlatformSettings.jsx` - Added password field and test email integration

## Future Enhancements

1. **Email Templates** - Allow custom email templates
2. **Multiple SMTP Profiles** - Support multiple email providers
3. **Email Queue** - Background email sending with retry
4. **Email Analytics** - Track delivery rates and bounces
5. **Email Logs** - View sent/failed emails in UI

## Support

For issues or questions:
- Check backend logs: `backend/logs/`
- Check Email Center: `localhost:8000/docs#/Email%20Center`
- Email Support: support@gabanistore.com
- Operations: operations@gabanilogistics.com
