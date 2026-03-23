"""
Enhanced Safety Models - Comprehensive safety data structures
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from backend.database.base import Base


class SafetyIncident(Base):
    """Safety incident report"""
    
    __tablename__ = "safety_incidents_v2"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    incident_type = Column(String(100))  # accident, near_miss, violation, hazard
    severity = Column(String(50))  # minor, moderate, severe, critical
    location = Column(JSON)  # latitude, longitude
    description = Column(Text)
    
    # Relationships
    driver_id = Column(Integer)
    vehicle_id = Column(Integer)
    shipment_id = Column(Integer)
    
    # Environmental conditions
    weather_conditions = Column(JSON)
    traffic_conditions = Column(JSON)
    road_conditions = Column(JSON)
    
    # Analysis
    root_cause = Column(String(200))
    contributing_factors = Column(JSON)
    corrective_actions = Column(JSON)
    
    # Financial impact
    estimated_cost = Column(Float, default=0)
    downtime_hours = Column(Float, default=0)
    safety_score_impact = Column(Integer, default=0)
    
    # Status
    investigation_status = Column(String(50), default="pending")
    resolved_at = Column(DateTime, nullable=True)
    
    # Timestamps
    incident_date = Column(DateTime, default=func.now())
    reported_at = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class DriverBehavior(Base):
    """Driver behavior monitoring"""
    
    __tablename__ = "driver_behaviors_v2"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, index=True)
    behavior_type = Column(String(100))  # speeding, harsh_braking, lane_drift, distraction
    severity = Column(String(50))
    
    # Location and time
    location = Column(JSON)
    timestamp = Column(DateTime)
    duration_seconds = Column(Integer)
    
    # Measurements
    speed_kph = Column(Float)
    speed_limit_kph = Column(Float)
    acceleration_g = Column(Float)
    deceleration_g = Column(Float)
    
    # Risk assessment
    risk_score = Column(Integer)  # 0-100
    fatigue_level = Column(Integer)  # 0-100
    distraction_level = Column(Integer)  # 0-100
    
    # Context
    weather_conditions = Column(String(100))
    traffic_conditions = Column(String(100))
    road_type = Column(String(50))
    
    # Response
    alert_sent = Column(Boolean, default=False)
    reviewed = Column(Boolean, default=False)
    coaching_recommended = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=func.now())


class VehicleInspection(Base):
    """Vehicle inspection and maintenance tracking"""
    
    __tablename__ = "vehicle_inspections_v2"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, index=True)
    inspector_id = Column(Integer)
    
    # Inspection details
    inspection_type = Column(String(50))  # daily, weekly, monthly, pre_trip
    overall_status = Column(String(50))  # safe, needs_attention, unsafe
    inspection_score = Column(Integer)  # 0-100
    
    # System checks
    brakes_status = Column(String(50), default="good")
    tires_status = Column(String(50), default="good")
    lights_status = Column(String(50), default="good")
    engine_status = Column(String(50), default="good")
    transmission_status = Column(String(50), default="good")
    steering_status = Column(String(50), default="good")
    suspension_status = Column(String(50), default="good")
    electrical_status = Column(String(50), default="good")
    
    # Measurements
    tire_pressure = Column(JSON)
    tread_depth_mm = Column(JSON)
    brake_pad_thickness_mm = Column(JSON)
    
    # Fluids
    oil_level = Column(String(50))
    coolant_level = Column(String(50))
    brake_fluid_level = Column(String(50))
    transmission_fluid_level = Column(String(50))
    
    # Safety equipment
    seatbelts_status = Column(String(50), default="good")
    fire_extinguisher = Column(Boolean, default=True)
    first_aid_kit = Column(Boolean, default=True)
    warning_triangle = Column(Boolean, default=True)
    
    # Issues and recommendations
    issues_found = Column(JSON, default={})
    recommendations = Column(JSON, default={})
    
    # Documents
    photos = Column(JSON)
    notes = Column(Text)
    
    # Scheduling
    inspection_date = Column(DateTime, default=func.now())
    next_inspection_due = Column(DateTime)
    created_at = Column(DateTime, default=func.now())


class SafetyReport(Base):
    """Comprehensive safety reports"""
    
    __tablename__ = "safety_reports_v2"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    report_type = Column(String(50))  # daily, weekly, monthly, custom
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    
    # Metrics
    safety_score = Column(Integer)  # 0-100
    previous_safety_score = Column(Integer)
    trend = Column(String(50))  # improving, stable, deteriorating
    
    # Statistics
    total_incidents = Column(Integer, default=0)
    total_near_misses = Column(Integer, default=0)
    total_violations = Column(Integer, default=0)
    
    # Detailed analysis
    incident_by_severity = Column(JSON)
    incident_by_type = Column(JSON)
    incident_by_location = Column(JSON)
    
    # Performance analysis
    driver_performance = Column(JSON)
    top_risky_drivers = Column(JSON)
    driver_training_needs = Column(JSON)
    
    vehicle_performance = Column(JSON)
    maintenance_issues = Column(JSON)
    inspection_compliance = Column(JSON)
    
    # Route analysis
    route_safety_analysis = Column(JSON)
    high_risk_routes = Column(JSON)
    weather_impact = Column(JSON)
    
    # Actions
    recommendations = Column(JSON)
    action_items = Column(JSON)
    priority_levels = Column(JSON)
    
    # File and metadata
    report_file_url = Column(String(500))
    generated_by = Column(String(100))
    generated_at = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())


class SafetyAlert(Base):
    """Safety alert log"""
    
    __tablename__ = "safety_alerts_v2"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String(100))
    priority = Column(String(50))  # low, medium, high, critical
    
    # Reference
    driver_id = Column(Integer, index=True)
    vehicle_id = Column(Integer)
    shipment_id = Column(Integer)
    
    # Content
    title = Column(String(200))
    message = Column(Text)
    details = Column(JSON)
    
    # Status
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime, nullable=True)
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    
    # Channels sent
    sent_via_websocket = Column(Boolean, default=False)
    sent_via_sms = Column(Boolean, default=False)
    sent_via_email = Column(Boolean, default=False)
    sent_via_push = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class RouteRiskAssessment(Base):
    """Route-level safety risk assessment"""
    
    __tablename__ = "route_risk_assessments"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(String(100))
    origin = Column(JSON)
    destination = Column(JSON)
    
    # Risk metrics
    overall_risk_score = Column(Integer)  # 0-100
    traffic_risk = Column(Integer)
    weather_risk = Column(Integer)
    road_condition_risk = Column(Integer)
    accident_frequency = Column(Integer)
    
    # History
    past_incidents_count = Column(Integer, default=0)
    past_near_misses_count = Column(Integer, default=0)
    
    # Recommendations
    recommended_speed_limit = Column(Integer)
    recommended_departure_time = Column(String(50))
    hazard_zones = Column(JSON)
    
    # Assessment date
    assessment_date = Column(DateTime, default=func.now())
    next_assessment_due = Column(DateTime)
    created_at = Column(DateTime, default=func.now())


class ComplianceAudit(Base):
    """Compliance audit records"""
    
    __tablename__ = "compliance_audits"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    audit_type = Column(String(100))
    audit_date = Column(DateTime, default=func.now())
    auditor = Column(String(100))
    
    # Subjects
    driver_id = Column(Integer, nullable=True)
    vehicle_id = Column(Integer, nullable=True)
    facility_id = Column(Integer, nullable=True)
    
    # Results
    compliance_score = Column(Integer)  # 0-100
    findings = Column(JSON)
    non_conformities = Column(JSON)
    
    # Follow-up
    corrective_actions = Column(JSON)
    target_completion_date = Column(DateTime)
    completed_date = Column(DateTime, nullable=True)
    
    # Documentation
    audit_report_url = Column(String(500))
    evidence_files = Column(JSON)
    
    created_at = Column(DateTime, default=func.now())

