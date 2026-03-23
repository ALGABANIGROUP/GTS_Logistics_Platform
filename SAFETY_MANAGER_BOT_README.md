"""
AI Safety Manager Bot - Intelligent Safety Manager
GTS Logistics Safety Management System
"""

# AI Safety Manager Bot Documentation

## 📋 Overview

**AI Safety Manager Bot** is a comprehensive AI-powered safety management system integrated into GTS Logistics. It provides real-time monitoring, incident management, compliance tracking, and automated safety protocols.

### Key Features

- 🚨 **Incident Management**: Track and investigate workplace incidents
- ✅ **Compliance Monitoring**: Monitor adherence to OSHA, ISO 45001, and UAE regulations
- 🎯 **Risk Assessment**: Predict and assess potential hazards
- 🔍 **Inspection Management**: Schedule and conduct safety inspections
- 🚑 **Emergency Response**: Automated emergency response protocols
- 📚 **Training Management**: Track and manage safety training programs
- 📊 **Analytics & Reporting**: Comprehensive safety metrics and reports
- 🔔 **Real-time Alerts**: Immediate notifications for critical events

## 🏗️ System Architecture

### Core Components

1. **IncidentManager** - Handles incident reporting, investigation, and analysis
2. **ComplianceMonitor** - Monitors compliance with safety standards
3. **RiskPredictor** - Performs risk assessment and prediction
4. **InspectionManager** - Manages safety inspections and schedules
5. **EmergencyResponder** - Handles emergency situations
6. **TrainingManager** - Manages safety training programs

### Directory Structure

```
backend/safety/
├── __init__.py
├── main.py                          # Main safety bot orchestrator
├── core/                            # Core components
│   ├── incident_manager.py
│   ├── compliance_monitor.py
│   ├── risk_predictor.py
│   ├── inspection_manager.py
│   ├── emergency_responder.py
│   └── training_manager.py
├── models/                          # Data models
├── services/                        # Support services
├── routes/                          # API routes
├── utils/                           # Utility functions
└── data/                            # Configuration data
```

## 🚀 Startup & Integration

### Auto-initialization via BOS

The Safety Manager Bot is automatically initialized with the BOS (Bot Operating System):

```python
# In backend/main.py
safety_router = _try_import_router("backend.routes.safety", "routes.safety")
# Routes are automatically mounted
```

### Manual Initialization

```python
from backend.safety.main import safety_manager, AISafetyManagerBot

# Auto-created instance
safety_manager

# Or create custom instance
from backend.safety.main import SafetyConfig

config = SafetyConfig(
    incident_reporting_enabled=True,
    real_time_monitoring=True,
    compliance_check_interval=3600,
)
bot = AISafetyManagerBot(config)
await bot.start()
```

## 📡 API Endpoints

### Safety Status & Configuration

```
GET  /api/v1/safety/status              - Get safety system status
GET  /api/v1/safety/config              - Get safety system configuration
GET  /api/v1/safety/dashboard           - Get safety dashboard
```

### Incident Management

```
POST /api/v1/safety/incidents/report        - Report new incident
GET  /api/v1/safety/incidents/statistics    - Get incident statistics
```

### Compliance Management

```
GET  /api/v1/safety/compliance/check        - Check compliance status
POST /api/v1/safety/audit/schedule          - Schedule compliance audit
```

### Risk Management

```
GET  /api/v1/safety/risks/assess            - Assess current risks
POST /api/v1/safety/risks/detailed-assessment - Perform detailed risk assessment
```

### Inspection Management

```
GET  /api/v1/safety/inspections/schedule    - Get inspection schedule
POST /api/v1/safety/inspections/conduct     - Conduct inspection
```

### Training Management

```
GET  /api/v1/safety/training/requirements   - Check training requirements
POST /api/v1/safety/training/schedule       - Schedule training course
```

### Alerts & Notifications

```
GET  /api/v1/safety/alerts/recent           - Get recent alerts
```

## 📝 Usage Examples

### Report an Incident

```bash
curl -X POST http://localhost:8000/api/v1/safety/incidents/report \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d {
    "incident_type": "slip_trip_fall",
    "severity": "moderate",
    "description": "Employee slipped on wet floor in warehouse",
    "location": "Warehouse Section A",
    "reporter": "John Doe",
    "injured_persons": [
      {"name": "Jane Smith", "injury": "minor bruise", "treated": "yes"}
    ],
    "witnesses": ["Alex Johnson", "Maria Garcia"]
  }
```

### Check Compliance Status

```bash
curl -X GET http://localhost:8000/api/v1/safety/compliance/check \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Assess Current Risks

```bash
curl -X GET http://localhost:8000/api/v1/safety/risks/assess \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Safety Dashboard

```bash
curl -X GET http://localhost:8000/api/v1/safety/dashboard \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🔧 Configuration

### SafetyConfig Parameters

```python
@dataclass
class SafetyConfig:
    incident_reporting_enabled: bool = True      # Enable incident reporting
    real_time_monitoring: bool = True            # Real-time monitoring
    predictive_analytics: bool = True            # Use predictive analytics
    compliance_check_interval: int = 3600        # Check compliance every hour
    inspection_schedule_interval: int = 86400    # Schedule inspections daily
    risk_assessment_interval: int = 7200         # Assess risks every 2 hours
    alert_threshold_risk: RiskLevel = HIGH       # Alert threshold
    emergency_response_timeout: int = 300        # 5-minute emergency timeout
```

## 📊 Incident Severity Levels

- **MINOR**: No injury
- **MODERATE**: Minor injury requiring first aid
- **MAJOR**: Serious injury requiring medical treatment
- **CRITICAL**: Severe injury or multiple casualties
- **FATAL**: Death

## 🎯 Incident Types

- Slip, trip, fall
- Equipment accident
- Vehicle accident
- Fire
- Chemical spill
- Electrical accident
- Manual handling injury
- Other

## 📈 Safety Metrics

The system tracks:

- Total incidents
- Incidents today
- Incidents this month
- Days without accident
- Compliance rate (%)
- Overall risk level

## 🔒 Security & Authentication

All API endpoints require:

- Valid JWT token in Authorization header
- User authentication via `get_current_user` dependency
- Role-based access control (RBAC)

```bash
Authorization: Bearer <jwt_token>
```

## 🚨 Emergency Response Protocols

### Fire Emergency

**Activation Conditions**: Fire detected, fire alarm triggered

**Immediate Actions**:
1. Activate fire alarm
2. Evacuate building immediately
3. Contact fire department (911)
4. Use fire extinguishers if safe

### Chemical Spill Emergency

**Activation Conditions**: Chemical spill detected, gas leak

**Immediate Actions**:
1. Evacuate area immediately
2. Isolate the area
3. Contact hazmat team
4. Use appropriate protective equipment

### Medical Emergency

**Activation Conditions**: Employee injury, medical emergency

**Immediate Actions**:
1. Call emergency services
2. Evacuate injured person
3. Administer first aid
4. Transport to hospital

## 📚 Compliance Standards

### OSHA Standards

- OSHA-1910.132: Personal Protective Equipment
- OSHA-1910.1200: Hazard Communication
- OSHA-1910.38: Emergency Action Plans

### ISO Standards

- ISO 45001: Occupational Health & Safety Management System

### UAE Safety Regulations

- UAE-WHS-001: Warehouse Safety
- UAE-FIRE-001: Fire Safety Requirements

## 🛠️ Troubleshooting

### Safety Router Not Mounting

**Check**:
1. Ensure `backend/routes/safety.py` exists
2. Verify safety module imports correctly
3. Check logs for import errors

### Incidents Not Recording

**Check**:
1. Verify incident manager is initialized
2. Ensure incident_reporting_enabled is True
3. Check database connectivity

### Compliance Checks Failing

**Check**:
1. Ensure compliance standards are loaded
2. Verify audit schedule exists
3. Check for database issues

## 📞 Support & Feedback

For issues or feedback regarding the Safety Manager Bot:

1. Check logs in `safety_bot.log`
2. Review error messages in API responses
3. Contact GTS Safety Team

## 📄 License

Part of GTS Logistics Platform - All rights reserved.

---

**Last Updated**: January 7, 2026
**Version**: 1.0.0
