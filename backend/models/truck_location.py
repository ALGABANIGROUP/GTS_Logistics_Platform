"""
Truck Location and Transport Models
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database.base import Base


class TruckLocation(Base):
    """Model for storing real-time truck location data"""
    __tablename__ = "truck_locations"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    license_plate = Column(String(20), nullable=False, index=True)
    truck_number = Column(String(50), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    speed = Column(Float, default=0)  # in mph
    heading = Column(Float, nullable=True)  # 0-360 degrees
    status = Column(String(50), default='moving')  # moving, stopped, loading, unloading
    driver_name = Column(String(100), nullable=True)
    driver_id = Column(Integer, nullable=True)
    current_shipment_id = Column(Integer, nullable=True)
    fuel_level = Column(Float, nullable=True)  # percentage
    engine_hours = Column(Float, nullable=True)
    odometer_km = Column(Float, nullable=True)
    temperature_celsius = Column(Float, nullable=True)
    last_update = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'license_plate': self.license_plate,
            'truck_number': self.truck_number,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'speed': self.speed,
            'heading': self.heading,
            'status': self.status,
            'driver_name': self.driver_name,
            'driver_id': self.driver_id,
            'current_shipment_id': self.current_shipment_id,
            'fuel_level': self.fuel_level,
            'engine_hours': self.engine_hours,
            'odometer_km': self.odometer_km,
            'temperature_celsius': self.temperature_celsius,
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ShipmentTracking(Base):
    """Model for detailed shipment tracking information"""
    __tablename__ = "shipment_tracking"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(Integer, index=True, nullable=False)
    truck_id = Column(Integer, nullable=True)
    current_latitude = Column(Float, nullable=False)
    current_longitude = Column(Float, nullable=False)
    origin_latitude = Column(Float, nullable=False)
    origin_longitude = Column(Float, nullable=False)
    destination_latitude = Column(Float, nullable=False)
    destination_longitude = Column(Float, nullable=False)
    distance_traveled_km = Column(Float, default=0)
    distance_remaining_km = Column(Float, nullable=True)
    estimated_arrival = Column(DateTime, nullable=True)
    progress_percentage = Column(Float, default=0)
    status = Column(String(50), default='in_transit')
    last_location_update = Column(DateTime, default=datetime.utcnow)
    estimated_delivery_date = Column(DateTime, nullable=True)
    actual_delivery_date = Column(DateTime, nullable=True)
    delay_minutes = Column(Integer, default=0)
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class TransportRoute(Base):
    """Model for planned transport routes"""
    __tablename__ = "transport_routes"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    route_name = Column(String(100), nullable=False)
    origin_latitude = Column(Float, nullable=False)
    origin_longitude = Column(Float, nullable=False)
    destination_latitude = Column(Float, nullable=False)
    destination_longitude = Column(Float, nullable=False)
    distance_km = Column(Float, nullable=False)
    estimated_duration_hours = Column(Float, nullable=False)
    waypoints = Column(String, nullable=True)  # JSON string of waypoints
    priority = Column(String(20), default='normal')  # urgent, high, normal, low
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class DriverLocation(Base):
    """Model for driver app location data"""
    __tablename__ = "driver_locations"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, nullable=False, index=True)
    truck_id = Column(Integer, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    accuracy_meters = Column(Float, nullable=True)
    speed = Column(Float, default=0)
    heading = Column(Float, nullable=True)
    altitude = Column(Float, nullable=True)
    on_duty = Column(Boolean, default=False)
    logged_in = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    battery_percentage = Column(Float, nullable=True)
    network_type = Column(String(20), nullable=True)  # wifi, 4g, 5g, etc.
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'driver_id': self.driver_id,
            'truck_id': self.truck_id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'accuracy_meters': self.accuracy_meters,
            'speed': self.speed,
            'heading': self.heading,
            'altitude': self.altitude,
            'on_duty': self.on_duty,
            'logged_in': self.logged_in,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'battery_percentage': self.battery_percentage,
            'network_type': self.network_type
        }


class TransportAlert(Base):
    """Model for transport-related alerts and notifications"""
    __tablename__ = "transport_alerts"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(Integer, nullable=True, index=True)
    truck_id = Column(Integer, nullable=True)
    driver_id = Column(Integer, nullable=True)
    alert_type = Column(String(50), nullable=False)  # delay, accident, speeding, deviation, etc.
    severity = Column(String(20), default='info')  # critical, high, medium, low, info
    title = Column(String(200), nullable=False)
    description = Column(String(1000), nullable=False)
    location_latitude = Column(Float, nullable=True)
    location_longitude = Column(Float, nullable=True)
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'shipment_id': self.shipment_id,
            'truck_id': self.truck_id,
            'driver_id': self.driver_id,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'title': self.title,
            'description': self.description,
            'location_latitude': self.location_latitude,
            'location_longitude': self.location_longitude,
            'is_resolved': self.is_resolved,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
