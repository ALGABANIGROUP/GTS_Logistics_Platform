# GTS Communication Setup Guide
## Telegram Bot + Dashboard Chat Integration

### 🎯 Communication Solutions Implemented

Your GTS system now supports two communication methods:

#### 1. 📱 Telegram Bot (Recommended for Individual Use)
- **Perfect for**: Single user, immediate mobile notifications
- **Setup Time**: 5 minutes
- **Cost**: Free
- **Features**: Instant alerts, mobile notifications, simple setup

#### 2. 💬 Dashboard Chat (Integrated)
- **Perfect for**: Team communication, incident discussions
- **Setup Time**: Already configured
- **Cost**: No additional cost
- **Features**: Real-time chat, incident linking, message history

---

## 🚀 Quick Setup: Telegram Bot

### Step 1: Create Your Bot
1. Open Telegram and search for `@BotFather`
2. Send: `/newbot`
3. Bot Name: `GTS Incident Bot`
4. Username: `@GTSIncidentBot` (or choose your own)
5. Copy the **BOT TOKEN** provided

### Step 2: Get Your Chat ID
1. Search for your bot: `@GTSIncidentBot`
2. Send: `/start`
3. Go to: `https://t.me/userinfobot`
4. Send: `/start`
5. Copy your **Chat ID** (numeric value)

### Step 3: Configure Environment
Add to your `.env` file:
```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
TELEGRAM_ENABLED=true
```

### Step 4: Test Configuration
```bash
# Run the test script
python test_telegram_bot.py
```

### Step 5: Restart Services
```bash
# Restart the incident system
./start_incident_system.bat
```

---

## 💬 Dashboard Chat Usage

The Dashboard Chat is already integrated and ready to use:

### Features:
- **Real-time messaging** in multiple channels
- **Incident notifications** automatically posted
- **Message history** preserved
- **User authentication** required
- **Admin controls** for system messages

### Channels Available:
- **#general**: General team communication
- **#incidents**: Incident discussions and updates
- **#alerts**: System alerts and notifications

### API Endpoints:
```
GET  /api/v1/chat/channels          # List channels
GET  /api/v1/chat/{channel}/messages # Get messages
POST /api/v1/chat/send               # Send message
POST /api/v1/chat/mark-read          # Mark as read
```

---

## 🔧 Integration with Incident System

Both communication methods are integrated with your incident response system:

### Automatic Alerts:
- **Critical incidents** → Telegram + Dashboard notifications
- **System status changes** → Telegram alerts
- **Incident updates** → Dashboard chat posts

### Manual Communication:
- **Team discussions** → Dashboard Chat
- **Quick notifications** → Telegram Bot
- **Status updates** → Both systems

---

## 📊 Comparison Summary

| Feature | Telegram Bot | Dashboard Chat | Slack |
|---------|-------------|----------------|-------|
| Setup Time | 5 minutes | Ready now | 15+ minutes |
| Cost | Free | Free | Limited free tier |
| Mobile Alerts | ✅ Instant | ❌ Web only | ✅ |
| Team Chat | ❌ Single user | ✅ Multi-user | ✅ |
| Message History | ✅ | ✅ | ✅ |
| Incident Integration | ✅ | ✅ | ⚠️ Requires setup |
| External Dependencies | ✅ Telegram API | ❌ None | ✅ Slack API |

---

## 🎯 Recommendation for Your Stage

**Current Stage**: Individual developer/maintainer

### ✅ Recommended Approach:
1. **Primary**: Telegram Bot for instant mobile alerts
2. **Secondary**: Dashboard Chat for detailed incident discussions
3. **Future**: Slack when you have a team

### Why This Setup?
- **Immediate alerts** on your phone for critical incidents
- **Detailed discussions** within the system
- **Scalable** - easy to add team members later
- **No complex setup** required now

---

## 🧪 Testing Your Setup

### Test Telegram Bot:
```bash
python test_telegram_bot.py
```

### Test Dashboard Chat:
1. Access your GTS dashboard
2. Look for the chat component
3. Send a test message

### Test Incident Integration:
1. Create a test incident
2. Check both Telegram and Dashboard for notifications

---

## 🔄 Switching Between Solutions

### To Enable Telegram:
```env
TELEGRAM_ENABLED=true
```

### To Disable Telegram:
```env
TELEGRAM_ENABLED=false
```

### Dashboard Chat:
- Always available
- No configuration needed
- Automatically enabled

---

## 📞 Support

If you need help with setup:
1. Check the test script output
2. Verify your `.env` configuration
3. Ensure bot token and chat ID are correct
4. Test with the provided scripts

Both communication systems are now fully integrated and ready for production use! 🚀