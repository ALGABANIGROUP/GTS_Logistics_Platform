# MapleLoad Canada Bot v4.0.0 - User Guide

## Quick Start

The MapleLoad Canada Bot v4.0.0 now includes **Email-Integrated Shipment Processing** and an **AI Learning Database** that automatically discovers carriers and learns from historical data.

### What's New
- 📧 **Email Shipment Processing** - Automatically parse incoming shipment emails
- 🧠 **Learning Database** - AI learns from historical shipments
- 📊 **Smart Analytics** - Real-time insights into carrier performance
- 🔄 **Continuous Improvement** - System accuracy increases with each shipment

---

## Overview

### How It Works

```
Incoming Email → Bot Parses Content → Extracts Shipment Data
                                           ↓
                                    Searches Carrier Database
                                           ↓
                                    Calculates Match Scores
                                           ↓
                                    Suggests Top 3 Carriers
                                           ↓
                                    Sends Outreach Messages
                                           ↓
                                    Tracks Responses & Results
                                           ↓
                                    Updates Learning Database
```

---

## Tab Guide

### 1. 🔍 Freight Search Tab

**Purpose:** Manually search for freight loads using specific criteria

**How to Use:**
1. Enter **Origin City** (e.g., "Toronto, ON")
2. Enter **Destination City** (e.g., "Vancouver, BC")
3. Enter **Weight** in pounds (e.g., "20000")
4. Enter **Commodity Type** (e.g., "Electronics", "Machinery")
5. Set **Pickup Date** using date picker
6. Enter **Max Rate** (maximum cost you'll pay)
7. Click **"Search Freight Loads"** button

**Results:**
- System returns available loads matching criteria
- Each load shows:
  - Load ID (LOAD-001, etc.)
  - Rate (cost per load)
  - Route (origin → destination)
  - Weight and commodity
  - Pickup and delivery dates
  - Posted by (shipper company)
  - Distance

**What to Do Next:**
- ✓ Check boxes to select loads you want to pursue
- ✓ Selection counter shows "X of Y loads selected"
- ✓ Move to **"Supplier Outreach"** tab to send to carriers

**Tip:** Use searches to find high-value loads, then use the Supplier Outreach to get them matched with carriers.

---

### 2. 📧 Email Shipments Tab

**Purpose:** Process incoming shipment requests from email

**How It Works Automatically:**
1. System monitors for incoming shipment emails
2. Extracts key information:
   - Weight and dimensions
   - Pickup location and time
   - Company name
   - Address details
3. Automatically searches for matching carriers
4. Suggests top 3 best-fit carriers
5. Can send outreach automatically

**How to Process Manually:**

Each incoming email card shows:
- **From:** Sender's email address
- **Subject:** Email subject line
- **Time:** When received (exact date/time)
- **Extracted Data:**
  - Weight in lbs
  - Dimensions (W×H×D)
  - Company name
- **Preview:** First 150 characters of email content

**Actions:**
1. Review the extracted information
2. Click **"Process & Search"** button (green, with ⚡ icon)
3. System will:
   - Parse full email content
   - Extract detailed shipment info
   - Search carrier database
   - Create database record
   - Display results

**What Happens Next:**
- Email moves to Learning Database (as a record)
- Matching carriers are identified
- You can send outreach to carriers
- Results are tracked for AI learning

**Example Email Processed:**
```
From: Jean Fortin <jfortin@multiaction.ca>
Subject: PICKUP

Weight: 830 lbs
Dimensions: 48×40×36
Company: SHELF2CART SOLUTIONS
Location: Danvers, MA 01923

↓ (Click "Process & Search")

Results: 3 carriers found
- TransCanada Logistics (95% match)
- Maple Freight Solutions (92% match)  
- Northern Dispatch (88% match)
```

**Success Indicator:**
- Green success message = Email processed successfully
- Shows number of potential carriers found
- Red error message = Something went wrong (check email content)

---

### 3. 🧠 Learning Database Tab

**Purpose:** View historical shipment records and AI learning metrics

**Learning Statistics (Top Cards):**
- **📦 Total Processed:** Total shipments the system has handled
- **✅ Successful Matches:** Shipments successfully delivered
- **⚠️ Failed Matches:** Shipments that didn't work out
- **🎯 Match Accuracy:** Percentage accuracy of carrier matching
- **🧠 System Learning:** AI improvement level (0-100%)

**Example Stats:**
- Total Processed: 142 shipments
- Successful Matches: 131 (92.4%)
- Failed Matches: 11 (7.6%)
- Match Accuracy: 92.4%
- System Learning: 87.6% (AI is improving!)

**Historical Records Table:**

Shows all past shipments with columns:
- **Record ID:** Unique identifier (REC-001-20260120)
- **Source:** Email, Manual, or API
- **Company:** Shipper company name
- **Weight:** Shipment weight in lbs
- **Location:** Pickup location
- **Status:** Current shipment status
  - **Pending** 🟡 - Awaiting carrier acceptance
  - **Matched** 🟢 - Carrier assigned
  - **In Transit** 🔵 - Shipment on the way
  - **Delivered** ✅ - Successfully delivered
  - **Failed** ❌ - Did not complete
- **Learning Score:** AI confidence percentage

**What the Learning Score Means:**
- 90-100% = System is very confident in this match
- 80-89% = Good confidence, based on similar shipments
- 70-79% = Reasonable confidence, some uncertainty
- Below 70% = Low confidence, unique shipment type

**AI Learning in Action:**
```
Week 1: Match accuracy 78% - System is new
Week 2: Match accuracy 82% - Learning from data
Week 3: Match accuracy 86% - Better recommendations
Week 4: Match accuracy 92% - High confidence predictions
```

The system learns from:
- Which carriers successfully complete shipments
- What conditions lead to success/failure
- Best carriers for specific commodities
- Optimal pricing and timing
- Customer satisfaction patterns

**Tip:** Historical data helps the system make better decisions. The more shipments processed, the smarter the system becomes.

---

### 4. 📱 Supplier Outreach Tab

**Purpose:** Send selected freight loads to carriers for pickup

**Prerequisites:**
- Must have at least one load selected from Freight Search OR Email Shipments tab

**How to Use:**

1. **Optional - Add Custom Message:**
   - Edit the "Outreach Message" text area
   - Default message: "We have quality freight available for your network. Please review the attached loads."
   - Your message will be sent in email to carriers

2. **Select Suppliers:**
   - Check boxes next to carrier names you want to contact
   - Shows for each carrier:
     - Company name
     - Email address
     - Rate range per mile (e.g., $1.50-$2.50)
     - Fleet size (number of trucks)
   
   Example suppliers:
   - TransCanada Logistics - dispatch@transcanada.com
   - Maple Freight Solutions - rates@maplefreight.com
   - Northern Dispatch - carriers@northerndispatch.com
   - Canadian Carriers Network - booking@ccnetwork.ca
   - Express Logistics Canada - quotes@expresslogistics.ca

3. **Send Outreach:**
   - Click **"Send X Loads to Y Suppliers"** button (green, with ✉️ icon)
   - Button only appears when loads AND suppliers are selected
   - System will send detailed email to each selected carrier

4. **Track Status:**
   - While sending:
     - Spinner icon appears (⏳ loading)
     - "Sending..." appears on button
   - After sent:
     - ✅ Green checkmark = Successfully sent
     - ❌ Red error = Failed to send
   - Selection counter shows: "X of Y suppliers selected"

**What Carriers Receive:**
- Detailed load information:
  - Load ID
  - Weight
  - Route (pickup → delivery)
  - Commodity type
  - Pickup and delivery dates
  - Expected rate
- Your custom message
- Contact information for follow-up

**Results Tracking:**
- All outreach is automatically logged
- System tracks which carriers respond
- Records show if loads were accepted
- AI uses this data to improve future matches

**Best Practices:**
1. Select multiple carriers to increase chances
2. Personalize message if possible
3. Send to carriers with high success rates
4. Review feedback after shipment completes

---

### 5. 📊 Analytics Tab

**Purpose:** View overall performance metrics

**Key Metrics:**
- **📦 Total Loads Searched:** How many loads you've searched for
- **🎯 Average Match Score:** System's average confidence level
- **💵 Avg Rate Per Load:** Average cost per shipment
- **✅ Delivery Success Rate:** Percentage of successful deliveries

**Use This For:**
- Monitoring operational efficiency
- Understanding cost trends
- Tracking success rates
- Identifying best performing time periods

---

### 6. 📜 History Tab

**Purpose:** View recent activities and actions

**Activity Types:**
- 🔍 Freight searches performed
- 📧 Emails processed
- 📤 Outreach messages sent
- ✅ Successful deliveries
- ⚠️ Failed deliveries

**Information Shown:**
- Action description
- Number of items affected
- Timestamp (relative and absolute)
- Status (success/failure)

**Example History:**
```
🔍 Freight Search: Toronto → Vancouver
   8 loads found • 5 sent to suppliers
   2 hours ago

📤 Outreach Sent to TransCanada Logistics
   6 loads sent • 3 responses received
   4 hours ago

✅ Load Matched & Accepted
   LOAD-001 matched with Maple Freight Solutions
   Yesterday
```

---

## Email Processing Details

### Automatic Parsing

The system automatically extracts from email:

```
PARSE → Weight     (830 PDS, 20000 lbs, 5 kg, etc.)
        Dimensions (48X40X36, etc.)
        Location   (City, State, ZIP)
        Company    (Shipper name)
        Address    (Full street address)
        Time       (Pickup hours, breaks)
```

### Confidence Levels

- **95-100%** - Crystal clear extraction
- **85-94%** - Very high confidence
- **75-84%** - Good extraction
- **Below 75%** - May need manual review

### What If Parsing Fails?

- ❌ Email content unclear?
- ❌ Missing required information?
- ❌ Unable to extract location?

**Solution:**
1. Check email format is clear
2. Ensure weight/dimensions are in email
3. Include full address with city/state/ZIP
4. Add company name clearly
5. Specify pickup time window

**Best Email Format Example:**
```
COMPANY: Shelf2Cart Solutions
ADDRESS: 5 Electronics Avenue, Danvers, MA 01923

SHIPMENT:
Weight: 830 lbs
Dimensions: 48×40×36
Commodity: Electronics

PICKUP:
Start: 7:00 AM
End: 4:00 PM
Break: 12:00 PM - 1:00 PM
```

---

## System Features

### 🤖 AI Learning

The system improves automatically through:
1. **Historical Data** - Past shipments inform decisions
2. **Success Tracking** - Recording what worked
3. **Continuous Improvement** - Each shipment increases accuracy
4. **Predictive Matching** - Anticipating successful outcomes

### 📊 Analytics & Insights

Tracks performance by:
- **Carrier Performance** - Success rates per carrier
- **Commodity Type** - Best carriers for electronics, machinery, etc.
- **Geography** - Success rates by region
- **Pricing** - Cost trends and optimization
- **Time Patterns** - Seasonal variations

### 🔄 Automated Workflow

Complete automation includes:
- Email monitoring and parsing
- Carrier matching
- Outreach message sending
- Response tracking
- Shipment status updates
- AI learning calculations

### 📱 Multi-Channel Input

Accept shipments from:
- 📧 Incoming emails (automatic)
- 🔍 Manual freight search
- 📝 Form submissions
- 🔌 API integrations

---

## Tips & Best Practices

### For Maximum Efficiency

1. **Process Emails Promptly**
   - The sooner you process emails, the faster shipments move
   - Early processing helps AI make better decisions

2. **Select Multiple Carriers**
   - Don't rely on one carrier
   - Spread risk across 3-5 options
   - Some carriers may be unavailable

3. **Use Custom Messages**
   - Personalize outreach when possible
   - Mention special requirements
   - Build relationships with carriers

4. **Monitor Results**
   - Check success rates regularly
   - Note which carriers perform best
   - Adjust future selections based on data

5. **Provide Feedback**
   - Complete delivery information
   - Add notes about performance
   - Rate carrier satisfaction
   - Help AI learn faster

### For Better Matching

- Be specific with commodity types (not just "freight")
- Include accurate weights and dimensions
- Specify time windows clearly
- Mention special handling requirements
- Note any restrictions or preferences

### For Cost Optimization

- Compare rates from multiple carriers
- Watch for seasonal pricing changes
- Negotiate with high-performing carriers
- Monitor your average cost per load
- Use analytics to identify savings opportunities

---

## Troubleshooting

### Email Not Processing?

**Issue:** Email not appearing in Email Shipments tab
- **Solution:** Check if email was received by system
- **Check:** Email format and required fields
- **Try:** Re-send email with clearer format

**Issue:** Extracted data is wrong
- **Solution:** Email content may be unclear
- **Try:** Manually verify and correct if needed
- **Note:** System learns from corrections

### No Carriers Found?

**Issue:** Email processed but no matching carriers
- **Reason:** Shipment parameters outside service areas
- **Try:** Check weight limits, origin, destination
- **Solution:** May need to manually contact carriers

### Outreach Not Sending?

**Issue:** Send button disabled or sending fails
- **Check:** At least one load selected ✓
- **Check:** At least one carrier selected ✓
- **Check:** Network connection active
- **Try:** Refresh page and try again

### Low Match Accuracy?

**Issue:** Suggested carriers not responding
- **Reason:** New system (needs historical data)
- **Solution:** Provide more feedback on results
- **Help:** Complete each shipment record
- **Note:** Accuracy improves over time

---

## Data Security & Privacy

- ✅ Email content processed securely
- ✅ Personal information protected
- ✅ Data encrypted in transit
- ✅ Regular backups maintained
- ✅ PII masking in logs
- ✅ Authentication required

---

## Getting Help

For additional support:
- Check the documentation in AI Bots Panel
- Review historical records for similar shipments
- Check Analytics for performance insights
- Contact support with record ID for investigation

---

## Version History

- **v4.0.0** (Feb 5, 2026) - Email integration & learning database
- **v3.0.0** (Jan 25, 2026) - Freight search & supplier outreach
- **v2.0.0** (Jan 15, 2026) - Initial MapleLoad Canada Bot
- **v1.0.0** (Jan 1, 2026) - AI Bots Framework

---

**Last Updated:** February 5, 2026  
**Status:** Active & Learning  
**Support:** Available 24/7
