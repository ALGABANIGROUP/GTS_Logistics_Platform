# AI Safety Manager Bot - Quick Reference Guide

## ⚡ Quick Start

### View Safety Dashboard
```bash
GET /api/v1/safety/dashboard
```

**Response:**
```json
{
  "system_status": "operational",
  "safety_score": 85,
  "total_incidents": 24,
  "incidents_today": 0,
  "incidents_this_month": 3,
  "days_without_accident": 15,
  "compliance_rate": 92,
  "risk_level": "medium",
  "active_alerts": 2,
  "recent_incidents": [...]
}
```

### Report Incident
```bash
POST /api/v1/safety/incidents/report
{
  "incident_type": "slip_trip_fall",
  "severity": "moderate",
  "description": "Slip on wet floor",
  "location": "Warehouse A",
  "reporter": "John Doe",
  "injured_persons": [...],
  "witnesses": [...]
}
```

## 📊 Core Endpoints at a Glance

| Operation | Endpoint | Method | Purpose |
|-----------|----------|--------|---------|
| Status | `/api/v1/safety/status` | GET | System status |
| Dashboard | `/api/v1/safety/dashboard` | GET | Full safety overview |
| Report Incident | `/api/v1/safety/incidents/report` | POST | Log new incident |
| Incident Stats | `/api/v1/safety/incidents/statistics` | GET | Historical analysis |
| Check Compliance | `/api/v1/safety/compliance/check` | GET | Regulatory compliance |
| Schedule Audit | `/api/v1/safety/audit/schedule` | POST | Plan audit |
| Assess Risks | `/api/v1/safety/risks/assess` | GET | Current risk levels |
| Detailed Assessment | `/api/v1/safety/risks/detailed-assessment` | POST | In-depth risk analysis |
| Get Inspections | `/api/v1/safety/inspections/schedule` | GET | Inspection schedule |
| Conduct Inspection | `/api/v1/safety/inspections/conduct` | POST | Execute inspection |
| Training Needs | `/api/v1/safety/training/requirements` | GET | Expired certifications |
| Schedule Training | `/api/v1/safety/training/schedule` | POST | Book training session |
| Recent Alerts | `/api/v1/safety/alerts/recent` | GET | Last 24h alerts |

## 🎯 Common Tasks

### Report Employee Injury
```bash
POST /api/v1/safety/incidents/report
{
  "incident_type": "slip_trip_fall",
  "severity": "moderate",
  "description": "Employee slipped on wet floor",
  "location": "Warehouse Section A",
  "reporter": "John Doe",
  "injured_persons": [{
    "name": "Jane Smith",
    "injury": "minor bruise",
    "treated": "yes",
    "medical_facility": "On-site First Aid"
  }],
  "witnesses": ["Alex Johnson"]
}
```

### Check OSHA Compliance
```bash
GET /api/v1/safety/compliance/check
```
Returns compliance rate across all OSHA standards

### Identify High-Risk Areas
```bash
GET /api/v1/safety/risks/assess
```
Returns current high-risk locations with mitigation strategies

### Schedule Monthly Inspection
```bash
POST /api/v1/safety/inspections/schedule
{
  "inspection_type": "weekly",
  "date": "2026-01-15",
  "facility": "Warehouse A"
}
```

### Check Training Expiration
```bash
GET /api/v1/safety/training/requirements
```
Shows employees with expired certifications

### Schedule First Aid Course
```bash
POST /api/v1/safety/training/schedule
{
  "course": "first_aid",
  "date": "2026-01-20",
  "participants": ["John Doe", "Jane Smith"]
}
```

## 🚨 Emergency Response

### Fire Emergency
- **Endpoint**: Automatic or manual activation
- **Response**: Evacuation plan + Fire department contact
- **Timeout**: 5 minutes to complete evacuation

### Chemical Spill
- **Actions**: Evacuate → Isolate → Contact Hazmat
- **Safety Protocols**: Use protective equipment
- **Containment**: Isolate affected area

### Medical Emergency
- **Actions**: Call 911 → First Aid → Transport to hospital
- **Available Help**: On-site medical staff
- **Follow-up**: Incident investigation

## 📈 Key Metrics Explained

| Metric | Formula | Target |
|--------|---------|--------|
| Safety Score | (100 - (incidents/month)) | > 90 |
| Compliance Rate | (compliant_reqs / total_reqs × 100) | > 95% |
| Days Without Accident | Count of injury-free days | > 30 |
| Risk Level | HIGH\|MEDIUM\|LOW | LOW |
| Incident Rate | (incidents / months) | < 1/month |

## 🔐 Authentication

All endpoints require:
```bash
Authorization: Bearer <your_jwt_token>
```

Get token:
```bash
POST /auth/token
Content-Type: application/x-www-form-urlencoded

email=user@gts.com&password=your_password
```

## 🛠️ Configuration

### Enable/Disable Features

Edit `backend/safety/main.py`:

```python
config = SafetyConfig(
    incident_reporting_enabled=True,      # Enable incident reporting
    real_time_monitoring=True,            # Real-time dashboard updates
    predictive_analytics=True,            # Risk prediction
    compliance_check_interval=3600,       # Check compliance every hour
    inspection_schedule_interval=86400,   # Schedule inspections daily
)
```

### Change Check Intervals

```python
SafetyConfig(
    compliance_check_interval=1800,       # Every 30 minutes
    risk_assessment_interval=3600,        # Every hour
    inspection_schedule_interval=172800,  # Every 2 days
)
```

## 📞 Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| "Safety manager not initialized" | Bot not started | Call `await safety_manager.start()` |
| 401 Unauthorized | Invalid token | Check JWT token validity |
| Empty incident history | No incidents recorded | Report incident first |
| Compliance rate 0% | No audit scheduled | POST to `/api/v1/safety/audit/schedule` |
| Inspections not scheduled | Loop not running | Verify safety manager started |

## 🎓 Training Programs Available

| Program | Duration | Frequency | Cost |
|---------|----------|-----------|------|
| Basic Safety | 8 hours | Annual | Included |
| Fire Safety | 4 hours | Biannual | Included |
| First Aid | 6 hours | Biannual | $50 |
| Equipment Operation | 12 hours | Annual | $75 |

## 📱 Response Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Request processed |
| 201 | Created | Resource created |
| 400 | Bad Request | Check payload format |
| 401 | Unauthorized | Provide valid token |
| 403 | Forbidden | Insufficient permissions |
| 500 | Server Error | Check backend logs |

## 📚 Regulatory Reference

### OSHA Standards Monitored
- 1910.132 (PPE)
- 1910.1200 (Hazard Communication)
- 1910.38 (Emergency Plans)

### ISO 45001 Requirements
- Leadership & Commitment
- Risk Assessment
- Emergency Planning

### UAE Regulations
- Warehouse Safety Standards
- Fire Safety Requirements

## 🔄 Integration Points

The Safety Manager Bot integrates with:

- **BOS**: Part of Bot Operating System
- **Database**: PostgreSQL for persistence
- **WebSocket**: Real-time alerts (ws://localhost:8000/api/v1/ws/live)
- **Frontend**: React dashboard available
- **Authentication**: JWT tokens via `/auth/token`

## 💡 Pro Tips

1. **Enable Alerts**: Subscribe to WebSocket `safety.*` channel for real-time notifications
2. **Batch Reporting**: Use `/incidents/statistics` to analyze trends
3. **Proactive Inspections**: Schedule inspections before high-risk periods
4. **Training Calendar**: Track expiration dates in advance
5. **Compliance Audits**: Schedule quarterly audits for comprehensive review
6. **Risk Mitigation**: Use `/risks/detailed-assessment` for in-depth analysis

## 🚀 Next Steps

1. ✅ Explore `/api/v1/safety/dashboard` for overview
2. ✅ Test incident reporting with `/incidents/report`
3. ✅ Review compliance status via `/compliance/check`
4. ✅ Schedule first inspection with `/inspections/schedule`
5. ✅ Enable WebSocket for real-time updates

---

**Last Updated**: January 7, 2026
**Quick Reference v1.0**
