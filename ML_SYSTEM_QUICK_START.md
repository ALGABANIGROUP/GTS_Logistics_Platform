# ML System - Quick Start Guide

## 🚀 Getting Started with Machine Learning Features

### What's Available

The GTS ML System provides:
1. **Customer Intelligence** - AI scoring and recommendations
2. **Driver Analytics** - Performance tracking and optimization
3. **Demand Forecasting** - Predictive shipment volume
4. **Smart Communications** - Automated, personalized messages
5. **AI Chatbot** - ChatGPT-powered customer support
6. **Safety Monitoring** - Real-time weather and traffic alerts

---

## 📊 Accessing the ML Dashboard

### Step 1: Navigate to ML Dashboard
```
URL: http://localhost:5173/ml-dashboard
Or: Admin Menu → ML Insights
```

### Step 2: Dashboard Overview
The dashboard displays 4 main sections:

#### Overview Tab
- Total top customers tracked
- Monthly revenue
- System health (95%)
- Active alerts (3)

#### Customer Analytics Tab
- Table of top 10 customers with ML scores
- Recommended actions:
  - VIP Program
  - Loyalty Rewards
  - Churn Prevention

#### Driver Performance Tab
- Bar chart: On-time rates vs ratings
- Driver statistics cards:
  - On-time delivery %
  - Customer rating (stars)
  - Monthly revenue

#### Demand Forecast Tab
- 30-day shipment volume prediction
- Peak demand weeks
- Staffing recommendations
- Confidence level (94%)

---

## 🎯 Key Features

### 1. Customer Scoring System
**How it works:**
- Analyzes customer order history
- Calculates ML score (0-100):
  - 40% Revenue contribution
  - 30% Order frequency
  - 30% Reliability metrics

**Example:**
```
Customer: John Corp
ML Score: 95
Total Orders: 45
Revenue: $125,000
Status: VIP
Recommendation: Assign dedicated account manager
```

### 2. Driver Performance Metrics
**Tracked metrics:**
- On-time delivery rate (target: 95%+)
- Customer satisfaction rating (target: 4.8+/5.0)
- Monthly revenue generated
- Safety incidents

**Top Performers:**
Top drivers automatically identified and ranked for incentives/bonuses.

### 3. Demand Forecasting
**How it works:**
- Analyzes 90 days of historical shipment data
- AI predicts next 30 days volume
- Confidence level: 94%+

**Uses:**
- Staffing level planning
- Equipment procurement
- Driver scheduling
- Warehouse operations

**Example Output:**
```
Week 1: 2,000 shipments (Low)
Week 2: 2,500 shipments (Medium)
Week 3: 3,200 shipments (Peak - HIRE 8-10 DRIVERS)
Week 4: 2,100 shipments (Low)
```

### 4. Personalized Offers
**How it works:**
- ML recommends offers based on customer segment
- System sends personalized campaigns
- Offers include promo codes and expiry dates

**Channels:**
- Email (HTML formatted)
- SMS (text message)
- In-app notifications

**Example:**
```
Subject: Special Offer Just for You!
Body: As a VIP customer, enjoy 5% off your next 10 shipments
Code: LOYALTY2026
Valid until: March 4, 2026
```

### 5. AI Chatbot
**Capabilities:**
- Track shipments
- Generate quotes
- Answer FAQs
- Escalate urgent issues

**Usage:**
```
Customer: "Where is my shipment #12345?"
Bot: "Your shipment is in transit in Toronto, ON.
      Current location: Highway 401
      Expected delivery: Tomorrow 2:00 PM
      Track live: [link]"
```

**Sentiment Detection:**
- Positive: Routine inquiry
- Negative: Issue/complaint (escalate to human)
- Urgent: Critical issue (immediate response)

### 6. Safety Alerts
**Monitored Hazards:**
- Severe weather (snow, storms, fog)
- High winds (>50 km/h)
- Heavy rain (reduced visibility)
- Traffic incidents/construction
- Road hazards

**Alert Severity:**
```
🔴 CRITICAL - Pull over immediately
🟡 WARNING - Reduce speed, take precautions
🟢 INFO - Be aware of conditions
```

---

## 🔌 API Usage Examples

### Get Top Customers
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/ml/customers/top?limit=10
```

**Response:**
```json
{
  "status": "success",
  "count": 10,
  "customers": [
    {
      "id": "cust_001",
      "name": "John Corporation",
      "score": 95,
      "orders": 45,
      "revenue": 125000
    }
  ]
}
```

### Send Personalized Offer
```bash
curl -X POST \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  http://localhost:8000/api/v1/ml/communications/send-personalized-offer \
  -d '{
    "customer_id": "cust_001",
    "offer_details": {
      "description": "5% discount on next 10 shipments",
      "summary": "VIP Loyalty Offer",
      "expiry": "2026-03-04",
      "promo_code": "LOYALTY2026"
    }
  }'
```

### Chat with AI
```bash
curl -X POST http://localhost:8000/api/v1/ml/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How much to ship from Toronto to Vancouver?",
    "conversation_id": "conv_001",
    "conversation_type": "customer_support"
  }'
```

### Check Weather Alert
```bash
curl -H "Authorization: Bearer TOKEN" \
  "http://localhost:8000/api/v1/ml/safety/weather-alert?latitude=43.6532&longitude=-79.3832&route_name=Highway_401"
```

**Response:**
```json
{
  "status": "success",
  "weather_alert": {
    "type": "weather",
    "status": "clear",
    "message": "Weather conditions are favorable"
  }
}
```

---

## ⚙️ Configuration

### Environment Variables to Set

```bash
# Add to .env file

# ChatGPT Integration
OPENAI_API_KEY=sk-your-api-key

# Weather Monitoring
WEATHER_API_KEY=your-weather-api-key

# SMS/Phone (Twilio)
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token

# Email (SendGrid)
SENDGRID_API_KEY=your-sendgrid-key
MAIL_FROM_ADDRESS=noreply@gabanitransport.com

# ML System
ENABLE_ML_FEATURES=true
ML_DATA_COLLECTION_INTERVAL=300
```

### Obtaining API Keys

**OpenAI (ChatGPT):**
1. Go to https://platform.openai.com
2. Create account or sign in
3. Go to API keys section
4. Create new secret key
5. Copy and set as `OPENAI_API_KEY`

**Weather API:**
1. Go to https://openweathermap.org/api
2. Sign up for free tier
3. Get API key from dashboard
4. Set as `WEATHER_API_KEY`

**Twilio (SMS/Voice):**
1. Go to https://www.twilio.com
2. Create account
3. Get Account SID and Auth Token
4. Set as `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN`

**SendGrid (Email):**
1. Go to https://sendgrid.com
2. Create account
3. Create API key with Mail Send access
4. Set as `SENDGRID_API_KEY`

---

## 📈 Real-World Scenarios

### Scenario 1: VIP Customer Retention
**Situation:** Customer #001 hasn't shipped in 30 days

**ML Action:**
1. ML system identifies customer as high-value (score: 92)
2. Automatically generates retention offer:
   - "We miss you! Enjoy 10% off your next 5 shipments"
   - Sends via email and SMS
3. Chatbot ready if customer responds
4. Dashboard alerts manager to follow up

**Result:** Reengagement and retained revenue

### Scenario 2: Peak Season Staffing
**Situation:** Q4 holiday season approaching

**ML Action:**
1. Demand forecast predicts 40% volume increase
2. Dashboard shows: "HIRE 12 DRIVERS + 8 WAREHOUSE STAFF"
3. Recommends hiring 2 weeks in advance
4. Provides shift schedule optimization

**Result:** No service delays, maintained on-time rate

### Scenario 3: Safety Alert - Severe Weather
**Situation:** Winter storm approaching Toronto routes

**ML Action:**
1. Safety bot detects heavy snow warning
2. Automatically sends alerts to 8 active drivers:
   - "SEVERE WEATHER: Heavy snow on Highway 401"
   - "RECOMMENDATIONS: Reduce speed to 40 km/h, increase stopping distance"
3. Offers alternate route optimization
4. Tracks driver acknowledgements

**Result:** Zero accidents, all drivers safe

### Scenario 4: Driver Performance Recognition
**Situation:** Driver #042 reaches 500 on-time deliveries

**ML Action:**
1. System identifies top performer milestone
2. Sends recognition message to manager
3. Recommends: "$500 bonus, promotion to Lead Driver"
4. Suggests for training/mentoring roles

**Result:** Driver retention, team morale boost

---

## 📊 Understanding ML Scores

### Customer ML Score (0-100)
```
Score 90-100: 🟢 VIP
  - High revenue + frequent orders + reliable
  - Action: Premium service, dedicated support

Score 70-89: 🟢 HIGH VALUE
  - Good revenue + moderate frequency
  - Action: Loyalty program, regular engagement

Score 50-69: 🟡 STANDARD
  - Moderate usage
  - Action: Routine service, occasional offers

Score 30-49: 🟡 AT RISK
  - Lower engagement, declining orders
  - Action: Re-engagement campaign, special offer

Score 0-29: 🔴 DORMANT
  - Little activity, may have churned
  - Action: Win-back campaign, direct outreach
```

### Driver Efficiency Score
```
95-100%: ⭐⭐⭐⭐⭐ Exceptional
  - Consistent on-time, high ratings, safe
  - Incentive: Bonus, Lead Driver role

85-94%: ⭐⭐⭐⭐ Excellent
  - Good on-time rate, positive feedback
  - Incentive: Recognition, training opportunities

75-84%: ⭐⭐⭐ Good
  - Meets standards
  - Action: Regular coaching, support

65-74%: ⭐⭐ Needs Improvement
  - Below expectations
  - Action: Performance improvement plan

<65%: ⭐ Critical
  - Performance concerns
  - Action: Immediate intervention, retraining
```

---

## 🔔 Alert Types & Actions

### Weather Alerts
```
CRITICAL: Tornado/Hurricane/Blizzard
  → PULL OVER IMMEDIATELY
  → DO NOT CONTINUE DRIVING
  → Wait for all-clear from dispatch

WARNING: Heavy snow/rain/wind
  → Reduce speed 10-15%
  → Increase stopping distance
  → Use hazard lights
  → Consider alternate route

INFO: Minor weather
  → Monitor conditions
  → Proceed normally
  → Be weather aware
```

### Traffic Alerts
```
CRITICAL: Major accident/closure
  → Immediate reroute
  → Notify customer of potential delay
  → Coordinate with dispatch

WARNING: Heavy congestion
  → Use alternate route if available
  → Add 15-30 minutes to ETA
  → Update customer tracking

INFO: Minor congestion
  → Proceed as normal
  → Monitor for updates
```

---

## 🎓 Best Practices

### For Administrators
1. **Review ML Dashboard Daily**
   - Check for high-priority alerts
   - Review new recommendations
   - Monitor system health

2. **Use Demand Forecasts for Planning**
   - Adjust staffing 2 weeks in advance
   - Prepare peak-season resources
   - Avoid over-hiring in slow periods

3. **Act on Customer Recommendations**
   - Implement VIP program suggestions
   - Send retention offers timely
   - Track offer success rate

4. **Monitor Driver Performance**
   - Recognize top performers monthly
   - Address performance issues quickly
   - Use data for fair evaluations

### For Drivers
1. **Acknowledge Safety Alerts Immediately**
   - Don't ignore weather/traffic warnings
   - Follow recommended actions
   - Communicate with dispatch

2. **Monitor Performance Metrics**
   - Review your dashboard weekly
   - Aim for 95%+ on-time rate
   - Maintain 4.8+/5.0 rating

3. **Use Route Recommendations**
   - Follow ML-optimized routes
   - Save time and fuel
   - Improve customer satisfaction

### For Customers
1. **Enable Communication Preferences**
   - Choose email/SMS/phone
   - Set frequency preferences
   - Opt-in to personalized offers

2. **Use Chatbot for Quick Help**
   - Ask about shipment status
   - Get instant quotes
   - Resolve common issues

3. **Leverage Loyalty Program**
   - Accept personalized offers
   - Accumulate rewards
   - Enjoy VIP benefits

---

## 🆘 Troubleshooting

### ML Dashboard Not Loading
```
Solution:
1. Clear browser cache (Ctrl+Shift+Del)
2. Check if backend is running
3. Verify API connectivity
4. Check browser console for errors
```

### Chatbot Not Responding
```
Solution:
1. Verify OPENAI_API_KEY is set
2. Check OpenAI account quota
3. Review API rate limits
4. Check network connectivity
```

### Weather Alerts Not Working
```
Solution:
1. Verify WEATHER_API_KEY configuration
2. Check latitude/longitude coordinates
3. Verify weather service is online
4. Check API response times
```

### Communications Not Sending
```
Solution:
1. Verify SENDGRID_API_KEY for emails
2. Verify TWILIO credentials for SMS
3. Check phone number format (E.164)
4. Verify sender email/number authorized
```

---

## 📞 Support

**Need Help?**
- Documentation: See ML_SYSTEM_COMPLETE_GUIDE.md
- API Docs: http://localhost:8000/api/v1/docs
- Email: support@gabanitransport.com
- Emergency: ops-team@gabanitransport.com

**Report Issues:**
- Backend: Check logs in Docker container
- Frontend: Check browser console (F12)
- API: Test endpoints in Postman

---

## 🎉 Next Steps

1. **Configure API Keys** - Set all environment variables
2. **Access ML Dashboard** - Navigate to /ml-dashboard
3. **Review Recommendations** - Check customer and driver insights
4. **Send First Campaign** - Use personalized offer feature
5. **Monitor Results** - Track ROI and engagement metrics

---

**Happy Learning!** 🚀

For more details, see **ML_SYSTEM_COMPLETE_GUIDE.md**

Version: 1.0.0 | Updated: February 4, 2026
