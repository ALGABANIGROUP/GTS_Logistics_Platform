"""
Shipment models
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database.base import Base


class Shipment(Base):
    """Enhanced Shipment model for transport tracking"""
    __tablename__ = "shipments_enhanced"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    shipment_number = Column(String(50), nullable=False, unique=True, index=True)
    
    # Locations
    origin_latitude = Column(Float, nullable=False)
    origin_longitude = Column(Float, nullable=False)
    origin_address = Column(String(500), nullable=True)
    origin_city = Column(String(100), nullable=True)
    origin_state = Column(String(50), nullable=True)
    origin_zip = Column(String(20), nullable=True)
    
    destination_latitude = Column(Float, nullable=False)
    destination_longitude = Column(Float, nullable=False)
    destination_address = Column(String(500), nullable=True)
    destination_city = Column(String(100), nullable=True)
    destination_state = Column(String(50), nullable=True)
    destination_zip = Column(String(20), nullable=True)
    
    # Tracking
    current_latitude = Column(Float, nullable=True)
    current_longitude = Column(Float, nullable=True)
    current_location_description = Column(String(500), nullable=True)
    
    # Status
    status = Column(String(50), default='pending')  # pending, assigned, in_transit, delivered, cancelled, delayed
    status_updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Shipment Details
    shipment_type = Column(String(50), nullable=True)  # full_truckload, ltl, parcel, etc.
    weight_kg = Column(Float, nullable=True)
    dimensions_meter = Column(String(50), nullable=True)  # LxWxH format
    goods_description = Column(Text, nullable=True)
    hazmat = Column(Boolean, default=False)
    temperature_controlled = Column(Boolean, default=False)
    target_temperature = Column(Float, nullable=True)
    
    # Financial
    base_price = Column(Float, nullable=True)
    total_price = Column(Float, nullable=True)
    currency = Column(String(3), default='USD')
    payment_status = Column(String(50), default='pending')  # pending, paid, failed
    
    # Dates and Times
    pickup_scheduled = Column(DateTime, nullable=True)
    pickup_actual = Column(DateTime, nullable=True)
    delivery_scheduled = Column(DateTime, nullable=True)
    delivery_actual = Column(DateTime, nullable=True)
    delivery_deadline = Column(DateTime, nullable=True)
    
    # Assignments
    truck_id = Column(Integer, nullable=True, index=True)
    driver_id = Column(Integer, nullable=True, index=True)
    driver_name = Column(String(100), nullable=True)
    driver_phone = Column(String(20), nullable=True)
    
    # Progress
    distance_total_km = Column(Float, nullable=True)
    distance_traveled_km = Column(Float, default=0)
    distance_remaining_km = Column(Float, nullable=True)
    progress_percentage = Column(Float, default=0)
    
    # Metadata
    reference_number = Column(String(100), nullable=True)
    special_instructions = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    delay_reason = Column(String(500), nullable=True)
    signature_image_url = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'shipment_number': self.shipment_number,
            'origin': {
                'latitude': self.origin_latitude,
                'longitude': self.origin_longitude,
                'address': self.origin_address,
                'city': self.origin_city,
                'state': self.origin_state,
                'zip': self.origin_zip
            },
            'destination': {
                'latitude': self.destination_latitude,
                'longitude': self.destination_longitude,
                'address': self.destination_address,
                'city': self.destination_city,
                'state': self.destination_state,
                'zip': self.destination_zip
            },
            'current_location': {
                'latitude': self.current_latitude,
                'longitude': self.current_longitude,
                'description': self.current_location_description
            },
            'status': self.status,
            'status_updated_at': self.status_updated_at.isoformat() if self.status_updated_at else None,
            'shipment_type': self.shipment_type,
            'weight_kg': self.weight_kg,
            'goods_description': self.goods_description,
            'hazmat': self.hazmat,
            'temperature_controlled': self.temperature_controlled,
            'price': {
                'base': self.base_price,
                'total': self.total_price,
                'currency': self.currency,
                'status': self.payment_status
            },
            'dates': {
                'pickup_scheduled': self.pickup_scheduled.isoformat() if self.pickup_scheduled else None,
                'pickup_actual': self.pickup_actual.isoformat() if self.pickup_actual else None,
                'delivery_scheduled': self.delivery_scheduled.isoformat() if self.delivery_scheduled else None,
                'delivery_actual': self.delivery_actual.isoformat() if self.delivery_actual else None,
                'delivery_deadline': self.delivery_deadline.isoformat() if self.delivery_deadline else None
            },
            'assignment': {
                'truck_id': self.truck_id,
                'driver_id': self.driver_id,
                'driver_name': self.driver_name,
                'driver_phone': self.driver_phone
            },
            'progress': {
                'distance_total_km': self.distance_total_km,
                'distance_traveled_km': self.distance_traveled_km,
                'distance_remaining_km': self.distance_remaining_km,
                'percentage': self.progress_percentage
            },
            'reference_number': self.reference_number,
            'special_instructions': self.special_instructions,
            'notes': self.notes,
            'delay_reason': self.delay_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
