# 📧 Email Bot v1.0.0 - AI Bots Panel Integration

## Overview
Intelligent Email Bot for automated email-to-bot routing and processing. Designed as a specialized bot within the AI Bots Panel that monitors emails, routes them to appropriate AI bots, and executes intelligent workflows.

## Location & Access
- **Page**: `/ai-bots/email`
- **Role Access**: All authenticated users (Basic subscription+)
- **Integration**: Listed in AI Bots Panel as "Email Bot"

## Key Features

### 1. 📧 Real-Time Email Monitoring
**Capabilities**:
- Monitor multiple email accounts simultaneously
- Automatic email classification by sender
- Priority queue management
- Real-time delivery tracking

**Supported Email Providers**:
- Gabani Logistics (gabanilogistics.com)
- Gabani Store (gabanistore.com)
- Gmail (custom configuration)
- Outlook (custom configuration)

### 2. 🤖 Intelligent Bot Routing
**AI Bot Assignment**:
- **Supplier Emails** → MapleLoad Canada Bot
  - Automatically detects carrier/supplier inquiries
  - Extracts load details and requirements
  - Triggers load matching workflow

- **Customer Service** → Customer Service Bot
  - Complaint handling
  - Inquiry responses
  - Service escalation

- **Finance Inquiries** → Finance Bot
  - Invoice processing
  - Payment tracking
  - Rate negotiations

- **Technical Issues** → System Admin Bot
  - Platform issues
  - Account problems
  - Integration errors

- **General Inquiries** → General Manager Bot
  - Default routing
  - Unclassified emails
  - Multi-topic requests

### 3. 📊 Real-Time Monitoring Dashboard
**Live Metrics**:
- **Total Processed** - Cumulative emails handled
- **Successful** - Correctly routed and processed
- **Pending** - Currently being processed
- **Failed** - Failed processing attempts

**Visual Elements**:
- Success rate trend chart
- Bot performance distribution (pie chart)
- Processing rate analytics (bar chart)
- Live connection status indicator

### 4. 🔗 Email-to-Bot Mappings
**View Current Mappings**:
- Email patterns matched to specific bots
- Workflow assignments per bot
- Active/Inactive status
- Response time metrics

**Example Mappings**:
```
Pattern                          Bot Name                Workflow
supplier@*trucking.com          MapleLoad Canada        Load Matching
dispatch@*carrier.ca            MapleLoad Canada        Fleet Assignment
sales@*shipping.com             Sales Bot               Quote Generation
support@company.com             Customer Service        Ticket Creation
invoice@*                       Finance Bot             Invoice Processor
admin@*                         System Admin            Infrastructure
```

### 5. 📜 Execution History
**Tracked Information**:
- Sender email address
- Subject line
- Assigned bot
- Processing status (success/pending/failed)
- Timestamp of processing
- Response details (if applicable)

**History Actions**:
- View full email details
- Resend to different bot
- Mark as spam/delete
- Add to whitelist/blacklist
- Manual intervention

---

## Integration with Other Bots

### MapleLoad Canada Bot Integration
When Email Bot receives supplier communications:

1. **Email Detection**
   - Identifies sender as carrier/supplier
   - Extracts key information:
     - Available capacity
     - Service area
     - Rate quotes
     - Equipment details

2. **Bot Routing**
   - Sends to MapleLoad Canada Bot
   - Attaches parsed load/freight data
   - Includes supplier contact info

3. **Workflow Execution**
   - MapleLoad matches with available loads
   - Generates response email
   - Email Bot sends reply to supplier
   - Logs interaction in history

### Example Flow: Supplier Inquiry

```
1. Supplier Email Received
   ↓
2. Email Bot Classification
   (Identifies as MapleLoad supplier)
   ↓
3. Route to MapleLoad Canada Bot
   ↓
4. Load Matching
   (Find matching freight)
   ↓
5. Response Generation
   (Prepare load details)
   ↓
6. Email Bot Sends Reply
   ↓
7. History Logged
   (Track response)
```

---

## Dashboard Sections

### Overview Tab
**Display**:
- Performance metrics cards (4 total)
- Success rate chart (20-point trend)
- Bot performance distribution (pie chart)
- Active/Offline connection status

### Mappings Tab
**Display**:
- All email→bot mappings in table format
- Email pattern, Bot name, Workflow, Status
- Sortable and filterable
- Add/Edit/Delete mapping capability

### History Tab
**Display**:
- Execution history cards (clickable)
- 50 most recent executions
- Sender, Subject, Bot, Status, Timestamp
- Real-time updates via WebSocket

### Performance Tab
**Display**:
- Processing rate bar chart (last 10 periods)
- Success vs failed vs pending breakdown
- Rate trends over time
- Performance comparison by bot

---

## Technical Specifications

### Frontend Component
- **File**: `AIEmailBot.jsx` (new)
- **Location**: `/frontend/src/pages/ai-bots/`
- **Size**: ~700 lines
- **Dependencies**:
  - React 18+
  - Lucide React (icons)
  - Recharts (charts)
  - Axios (API)

### Component State
```javascript
{
  stats: {
    total_processed: number,
    successful: number,
    pending: number,
    failed: number,
    bot_performance: Record<string, number>
  },
  mappings: Array<{
    email_pattern: string,
    bot_name: string,
    workflow: string,
    status: string
  }>,
  history: Array<{
    email_from: string,
    subject: string,
    bot_name: string,
    status: 'success|pending|failed',
    timestamp: date,
    response?: string
  }>,
  wsConnected: boolean
}
```

### API Endpoints (Required)

```javascript
// Get monitoring statistics
GET /api/v1/email/monitoring/stats
Response: {
  total_processed: number,
  successful: number,
  pending: number,
  failed: number,
  bot_performance: Record<string, number>
}

// Get email→bot mappings
GET /api/v1/email/mappings
Response: {
  mappings: Array<Mapping>
}

// Get execution history
GET /api/v1/email/execution-history?limit=50
Response: {
  history: Array<Execution>
}

// WebSocket connection
WS /ws/email-bot
Events:
  - execution_update: New email processed
  - stats_update: Stats refreshed
```

### Styling
- **Theme**: Dark mode (#0f1419 base)
- **Accent Color**: Blue (#3b82f6) and Green (#10b981)
- **Responsive**: Mobile-first design
- **Charts**: Recharts with custom styling

---

## Bot Interaction Workflow

### Step 1: Email Arrival
- Email received at monitored inbox
- Subject and sender parsed
- Classified by pattern matching

### Step 2: Bot Assignment
- Email pattern matched to bot mapping
- AI recommendation engine considers:
  - Sender domain
  - Subject keywords
  - Content analysis
  - Historical patterns

### Step 3: Workflow Execution
- Assigned bot processes email
- Data extracted and validated
- Actions taken (respond, create ticket, match load)
- Results logged

### Step 4: Response Generation
- Bot creates response email
- Email Bot formats and validates
- Sends via outbound mailbox
- Tracks delivery status

### Step 5: History Logging
- Execution recorded with full details
- Performance metrics updated
- WebSocket notification sent
- Available in history view

---

## Configuration

### Email Account Setup
Each email account requires:
- **IMAP Settings**
  - Host: mail.gabanilogistics.com (default)
  - Port: 993
  - SSL: Enabled
  - Username: account email

- **SMTP Settings**
  - Host: mail.gabanilogistics.com (default)
  - Port: 465
  - SSL: Enabled
  - Username: account email
  - Password: shared managed password

### Bot Mapping Configuration
Add custom mappings via API:
```javascript
POST /api/v1/email/mappings
Request: {
  email_pattern: "pattern@domain.com",
  bot_name: "Target Bot Name",
  workflow: "workflow_key",
  enabled: true
}
```

### Feature Flags
- `ENABLE_EMAIL_BOT` - Activate email monitoring
- `ENABLE_AUTO_ROUTING` - Automatic bot assignment
- `ENABLE_RESPONSE_GENERATION` - Auto-reply capability
- `ENABLE_INBOUND` - Allow receiving emails
- `ENABLE_OUTBOUND` - Allow sending responses

---

## Monitoring & Alerts

### Health Checks
- Email account connectivity
- IMAP/SMTP availability
- Bot response time
- Failure rate threshold (> 5%)

### Alert Conditions
- ⚠️ High failure rate
- ⚠️ Bot offline/unresponsive
- ⚠️ Email account connection lost
- ⚠️ Queue overflow (> 100 pending)

### Notifications
- Dashboard banner alerts
- Email to admin on critical issues
- WebSocket real-time updates
- Slack integration (optional)

---

## Use Cases

### Use Case 1: Automated Supplier Communication
**Scenario**: Supplier sends availability notification
- Email arrives with truck capacity info
- Bot identifies as supplier (sender domain)
- Routes to MapleLoad Canada Bot
- Bot matches with pending loads
- Automated quote sent to supplier
- History tracked for follow-up

### Use Case 2: Customer Support Routing
**Scenario**: Customer asks about shipment status
- Email received with tracking number
- System Admin Bot extracts tracking data
- Looks up shipment status
- Responds with current location
- Escalates if issue detected

### Use Case 3: Invoice Processing
**Scenario**: Vendor submits invoice for payment
- Email detected with invoice attachment
- Finance Bot extracts invoice details
- Validates against purchase order
- Routes to accounting system
- Confirmation email sent

### Use Case 4: Customer Service Tickets
**Scenario**: Customer reports delivery issue
- Customer email parsed by Customer Service Bot
- Ticket created automatically
- Assigned to support team
- Auto-response sent to customer
- Tracked in support dashboard

---

## Performance Metrics

### Key Performance Indicators
- **Processing Rate**: Emails/minute
- **Success Rate**: Successfully routed/total
- **Response Time**: Seconds from receipt to response
- **Error Rate**: Failed processing %
- **Uptime**: System availability %

### Targets
- ✅ 99.9% uptime
- ✅ 95%+ success rate
- ✅ <30s average response time
- ✅ <1% error rate
- ✅ 1000+ emails/hour capacity

### Optimization
- Caching frequent patterns
- Parallel processing
- Rate limiting
- Connection pooling
- Query optimization

---

## Security & Privacy

### Data Protection
- Email content encryption
- Secure credential storage
- RBAC for email account access
- Audit logging for all actions

### Compliance
- GDPR email handling
- PCI-DSS for payment data
- SOC 2 compliance ready
- HIPAA considerations (if applicable)

### Access Control
- Admin-only email account management
- User can only view own emails
- Selective bot assignment per user
- History retention policies

---

## Troubleshooting

### Issue: Emails Not Being Processed
**Debug Steps**:
1. Check email account connectivity (Settings)
2. Verify IMAP/SMTP credentials
3. Check firewall/network settings
4. Review bot mapping configuration
5. Check bot status in AI Bots Panel

### Issue: Wrong Bot Assignment
**Solution**:
1. Review email pattern in mappings
2. Check pattern specificity
3. Add more specific pattern if needed
4. Test with similar email subject

### Issue: Bot Response Not Sent
**Solution**:
1. Check SMTP account credentials
2. Verify outbound email enablement
3. Check bot response generation
4. Review delivery logs

### Issue: High Error Rate
**Solution**:
1. Check email format/encoding
2. Verify bot capacity not exceeded
3. Review bot error logs
4. Consider rate limiting adjustments

---

## Future Enhancements

### Phase 2 (Planned)
- [ ] Natural language processing (NLP) for better classification
- [ ] Sentiment analysis for priority routing
- [ ] Custom email templates for responses
- [ ] Email attachment processing
- [ ] Calendar integration for scheduling

### Phase 3 (Roadmap)
- [ ] Slack/Teams integration
- [ ] Mobile push notifications
- [ ] Predictive email routing (ML model)
- [ ] Email thread context analysis
- [ ] Bulk email processing
- [ ] Multilingual support

---

## Documentation References
- **Quick Start**: See EMAIL_BOT_QUICK_START.md
- **System Details**: See EMAIL_BOT_PROCESSING_SYSTEM.md
- **Deployment**: See EMAIL_BOT_DEPLOYMENT_CHECKLIST.md
- **AI Bots Panel**: See AI_BOTS_PANEL_IMPLEMENTATION.md

---

**Version**: 1.0.0  
**Component**: AIEmailBot.jsx  
**Route**: `/ai-bots/email`  
**Status**: Production Ready  
**Last Updated**: January 2025  
**Subscription Level**: Basic+
