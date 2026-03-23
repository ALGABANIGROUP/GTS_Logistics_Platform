# AI Safety Manager Bot - Testing Guide

## 🧪 Testing Overview

Complete testing guide for the AI Safety Manager Bot including unit tests, integration tests, and end-to-end scenarios.

## 📋 Test Categories

1. **Unit Tests**: Individual component testing
2. **Integration Tests**: Component interaction testing
3. **API Tests**: REST endpoint testing
4. **End-to-End Tests**: Full workflow testing

## 🚀 Running Tests

### Run All Safety Tests
```bash
pytest backend/tests/test_safety/ -v
```

### Run Specific Component Tests
```bash
# Test Incident Manager
pytest backend/tests/test_safety/test_incident_manager.py -v

# Test Compliance Monitor
pytest backend/tests/test_safety/test_compliance_monitor.py -v

# Test API Routes
pytest backend/tests/test_safety/test_safety_routes.py -v
```

### Run with Coverage
```bash
pytest backend/tests/test_safety/ --cov=backend.safety --cov-report=html
```

## 🔧 Unit Tests

### Test Incident Manager

**File**: `backend/tests/test_safety/test_incident_manager.py`

```python
import pytest
from backend.safety.core.incident_manager import IncidentManager

@pytest.fixture
def incident_manager():
    return IncidentManager()

@pytest.mark.asyncio
async def test_record_incident(incident_manager):
    """Test recording a new incident"""
    result = await incident_manager.record_incident(
        incident_type="slip_trip_fall",
        severity="moderate",
        description="Slip on wet floor",
        location="Warehouse A",
        reporter="John Doe"
    )
    assert result["ok"] is True
    assert result["incident_id"]

@pytest.mark.asyncio
async def test_incident_investigation(incident_manager):
    """Test automatic investigation initiation"""
    result = await incident_manager.record_incident(
        incident_type="equipment_accident",
        severity="critical",
        description="Equipment failure",
        location="Warehouse A",
        reporter="John Doe"
    )
    assert result["investigation_initiated"] is True

@pytest.mark.asyncio
async def test_get_incident_statistics(incident_manager):
    """Test incident statistics retrieval"""
    # Record test incidents
    for i in range(3):
        await incident_manager.record_incident(
            incident_type="slip_trip_fall",
            severity="minor",
            description="Test incident",
            location="Warehouse A",
            reporter="Test Reporter"
        )
    
    stats = await incident_manager.get_incident_statistics(
        start_date="2026-01-01",
        end_date="2026-01-31"
    )
    
    assert stats["total_incidents"] >= 3
    assert "by_type" in stats
    assert "by_severity" in stats

@pytest.mark.asyncio
async def test_incident_report_generation(incident_manager):
    """Test incident report generation"""
    result = await incident_manager.record_incident(
        incident_type="slip_trip_fall",
        severity="moderate",
        description="Slip on wet floor",
        location="Warehouse A",
        reporter="John Doe"
    )
    
    report = await incident_manager.generate_incident_report(result["incident_id"])
    
    assert report["incident_id"]
    assert report["investigation_summary"]
    assert report["recommendations"]
```

### Test Compliance Monitor

**File**: `backend/tests/test_safety/test_compliance_monitor.py`

```python
import pytest
from backend.safety.core.compliance_monitor import ComplianceMonitor

@pytest.fixture
def compliance_monitor():
    return ComplianceMonitor()

@pytest.mark.asyncio
async def test_check_osha_compliance(compliance_monitor):
    """Test OSHA compliance checking"""
    result = await compliance_monitor.check_safety_compliance()
    
    assert result["ok"] is True
    assert "compliance_rate" in result
    assert result["compliance_rate"] >= 0 and result["compliance_rate"] <= 100

@pytest.mark.asyncio
async def test_iso_compliance_checking(compliance_monitor):
    """Test ISO 45001 compliance"""
    result = await compliance_monitor.check_safety_compliance()
    
    frameworks = result["compliance_by_framework"]
    assert "ISO 45001" in frameworks
    
    iso_compliance = frameworks["ISO 45001"]
    assert iso_compliance["compliant"] + iso_compliance["non_compliant"] > 0

@pytest.mark.asyncio
async def test_uae_compliance_checking(compliance_monitor):
    """Test UAE regulation compliance"""
    result = await compliance_monitor.check_safety_compliance()
    
    frameworks = result["compliance_by_framework"]
    assert "UAE Regulations" in frameworks

@pytest.mark.asyncio
async def test_schedule_audit(compliance_monitor):
    """Test audit scheduling"""
    audit_result = await compliance_monitor.schedule_compliance_audit(
        audit_type="internal",
        scope="full_facility"
    )
    
    assert audit_result["ok"] is True
    assert audit_result["audit_id"]
    assert audit_result["scheduled_date"]
```

### Test Risk Predictor

**File**: `backend/tests/test_safety/test_risk_predictor.py`

```python
import pytest
from backend.safety.core.risk_predictor import RiskPredictor

@pytest.fixture
def risk_predictor():
    return RiskPredictor()

@pytest.mark.asyncio
async def test_assess_current_risks(risk_predictor):
    """Test current risk assessment"""
    risks = await risk_predictor.assess_current_risks()
    
    assert risks["ok"] is True
    assert "high_risk_areas" in risks
    assert isinstance(risks["high_risk_areas"], list)

@pytest.mark.asyncio
async def test_detailed_risk_assessment(risk_predictor):
    """Test detailed risk assessment"""
    detailed = await risk_predictor.perform_detailed_assessment(
        location="Warehouse A",
        hazard_type="chemical_exposure"
    )
    
    assert detailed["ok"] is True
    assert "probability" in detailed
    assert "severity" in detailed
    assert "risk_score" in detailed

@pytest.mark.asyncio
async def test_risk_level_calculation(risk_predictor):
    """Test risk level calculation"""
    risks = await risk_predictor.assess_current_risks()
    
    for area in risks["high_risk_areas"]:
        risk_level = area["risk_level"]
        assert risk_level in ["HIGH", "MEDIUM", "LOW"]
```

### Test Inspection Manager

**File**: `backend/tests/test_safety/test_inspection_manager.py`

```python
import pytest
from backend.safety.core.inspection_manager import InspectionManager

@pytest.fixture
def inspection_manager():
    return InspectionManager()

@pytest.mark.asyncio
async def test_schedule_inspections(inspection_manager):
    """Test inspection scheduling"""
    result = await inspection_manager.schedule_inspections(
        inspection_type="daily",
        start_date="2026-01-15"
    )
    
    assert result["ok"] is True
    assert result["scheduled_count"] > 0

@pytest.mark.asyncio
async def test_conduct_inspection(inspection_manager):
    """Test conducting inspection"""
    result = await inspection_manager.conduct_inspection(
        inspection_id="daily_warehouse_a",
        findings={"checkpoints_passed": 5, "checkpoints_failed": 0}
    )
    
    assert result["ok"] is True
    assert "inspection_score" in result
    assert result["inspection_score"] >= 0 and result["inspection_score"] <= 100
```

### Test Emergency Responder

**File**: `backend/tests/test_safety/test_emergency_responder.py`

```python
import pytest
from backend.safety.core.emergency_responder import EmergencyResponder

@pytest.fixture
def emergency_responder():
    return EmergencyResponder()

@pytest.mark.asyncio
async def test_get_fire_emergency_plan(emergency_responder):
    """Test fire emergency plan retrieval"""
    plan = await emergency_responder.get_emergency_plan("fire")
    
    assert plan["ok"] is True
    assert plan["plan_type"] == "fire"
    assert "immediate_actions" in plan

@pytest.mark.asyncio
async def test_get_chemical_spill_plan(emergency_responder):
    """Test chemical spill emergency plan"""
    plan = await emergency_responder.get_emergency_plan("chemical_spill")
    
    assert plan["ok"] is True
    assert len(plan["immediate_actions"]) > 0

@pytest.mark.asyncio
async def test_execute_emergency_response(emergency_responder):
    """Test emergency response execution"""
    result = await emergency_responder.execute_emergency_response(
        incident_type="fire",
        location="Warehouse A"
    )
    
    assert result["ok"] is True
    assert result["response_logged"] is True
```

### Test Training Manager

**File**: `backend/tests/test_safety/test_training_manager.py`

```python
import pytest
from backend.safety.core.training_manager import TrainingManager

@pytest.fixture
def training_manager():
    return TrainingManager()

@pytest.mark.asyncio
async def test_check_training_requirements(training_manager):
    """Test training requirements checking"""
    result = await training_manager.check_training_requirements()
    
    assert result["ok"] is True
    assert "expired_trainings" in result
    assert "expiring_soon" in result

@pytest.mark.asyncio
async def test_schedule_training_course(training_manager):
    """Test training course scheduling"""
    result = await training_manager.schedule_training_course(
        course="first_aid",
        date="2026-01-20",
        participants=["John Doe", "Jane Smith"]
    )
    
    assert result["ok"] is True
    assert result["course_scheduled"] is True

@pytest.mark.asyncio
async def test_complete_training_course(training_manager):
    """Test training course completion"""
    result = await training_manager.complete_training_course(
        course="first_aid",
        participant="John Doe"
    )
    
    assert result["ok"] is True
    assert result["certificate_issued"] is True
```

## 🌐 API Integration Tests

### Test Safety Routes

**File**: `backend/tests/test_safety/test_safety_routes.py`

```python
import pytest
from httpx import AsyncClient
from backend.main import app
from backend.security.auth import create_access_token

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def token():
    return create_access_token(data={"sub": "test@test.com", "role": "admin"})

@pytest.mark.asyncio
async def test_get_safety_dashboard(client, token):
    """Test GET /api/v1/safety/dashboard"""
    response = await client.get(
        "/api/v1/safety/dashboard",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "system_status" in data
    assert "safety_score" in data
    assert "total_incidents" in data

@pytest.mark.asyncio
async def test_report_incident(client, token):
    """Test POST /api/v1/safety/incidents/report"""
    payload = {
        "incident_type": "slip_trip_fall",
        "severity": "moderate",
        "description": "Test incident",
        "location": "Warehouse A",
        "reporter": "Test User"
    }
    
    response = await client.post(
        "/api/v1/safety/incidents/report",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True

@pytest.mark.asyncio
async def test_get_incident_statistics(client, token):
    """Test GET /api/v1/safety/incidents/statistics"""
    response = await client.get(
        "/api/v1/safety/incidents/statistics",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "total_incidents" in data
    assert "by_type" in data

@pytest.mark.asyncio
async def test_check_compliance(client, token):
    """Test GET /api/v1/safety/compliance/check"""
    response = await client.get(
        "/api/v1/safety/compliance/check",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "compliance_rate" in data

@pytest.mark.asyncio
async def test_assess_risks(client, token):
    """Test GET /api/v1/safety/risks/assess"""
    response = await client.get(
        "/api/v1/safety/risks/assess",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "high_risk_areas" in data

@pytest.mark.asyncio
async def test_unauthorized_access(client):
    """Test unauthorized access without token"""
    response = await client.get("/api/v1/safety/dashboard")
    
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_invalid_token(client):
    """Test access with invalid token"""
    response = await client.get(
        "/api/v1/safety/dashboard",
        headers={"Authorization": "Bearer invalid_token"}
    )
    
    assert response.status_code == 401
```

## 🔄 End-to-End Test Scenarios

### Scenario 1: Complete Incident Workflow

```python
@pytest.mark.asyncio
async def test_complete_incident_workflow(client, token):
    """
    E2E Test: Report incident → Investigate → Generate report → Check compliance impact
    """
    
    # Step 1: Report incident
    incident_payload = {
        "incident_type": "equipment_accident",
        "severity": "critical",
        "description": "Equipment malfunction causing worker injury",
        "location": "Manufacturing Unit A",
        "reporter": "Safety Officer",
        "injured_persons": [{
            "name": "John Smith",
            "injury": "laceration",
            "treated": "no"
        }]
    }
    
    response = await client.post(
        "/api/v1/safety/incidents/report",
        json=incident_payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    incident = response.json()
    incident_id = incident["incident_id"]
    
    # Step 2: Verify incident recorded
    response = await client.get(
        "/api/v1/safety/incidents/statistics",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    stats = response.json()
    assert stats["total_incidents"] > 0
    
    # Step 3: Check compliance impact
    response = await client.get(
        "/api/v1/safety/compliance/check",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    compliance = response.json()
    # Compliance should potentially be affected by critical incident
    
    # Step 4: Get updated dashboard
    response = await client.get(
        "/api/v1/safety/dashboard",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    dashboard = response.json()
    assert dashboard["total_incidents"] > 0
```

### Scenario 2: Compliance Audit Workflow

```python
@pytest.mark.asyncio
async def test_compliance_audit_workflow(client, token):
    """
    E2E Test: Schedule audit → Run compliance check → Generate audit report
    """
    
    # Step 1: Schedule audit
    audit_payload = {
        "audit_type": "internal",
        "scope": "full_facility"
    }
    
    response = await client.post(
        "/api/v1/safety/audit/schedule",
        json=audit_payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    
    # Step 2: Check compliance
    response = await client.get(
        "/api/v1/safety/compliance/check",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    compliance = response.json()
    assert "compliance_rate" in compliance
```

### Scenario 3: Inspection Workflow

```python
@pytest.mark.asyncio
async def test_inspection_workflow(client, token):
    """
    E2E Test: Schedule inspection → Conduct inspection → Record findings
    """
    
    # Step 1: Schedule inspections
    response = await client.get(
        "/api/v1/safety/inspections/schedule",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    
    # Step 2: Conduct inspection
    conduct_payload = {
        "inspection_id": "daily_warehouse_a",
        "findings": {"checkpoints_passed": 5, "checkpoints_failed": 0}
    }
    
    response = await client.post(
        "/api/v1/safety/inspections/conduct",
        json=conduct_payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    result = response.json()
    assert "inspection_score" in result
```

## 📊 Load Testing

```bash
# Install locust
pip install locust

# Run load test
locust -f backend/tests/test_safety/locustfile.py
```

**File**: `backend/tests/test_safety/locustfile.py`

```python
from locust import HttpUser, task, between

class SafetyUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login and get token
        response = self.client.post("/auth/token", data={
            "email": "test@test.com",
            "password": "password"
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task
    def get_dashboard(self):
        self.client.get("/api/v1/safety/dashboard", headers=self.headers)
    
    @task
    def check_compliance(self):
        self.client.get("/api/v1/safety/compliance/check", headers=self.headers)
    
    @task
    def assess_risks(self):
        self.client.get("/api/v1/safety/risks/assess", headers=self.headers)
```

## ✅ Test Checklist

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] API tests pass
- [ ] End-to-end workflows succeed
- [ ] Load testing complete
- [ ] Code coverage > 80%
- [ ] No security vulnerabilities
- [ ] Performance acceptable

---

**Last Updated**: January 7, 2026
**Testing Guide v1.0**
