from sqlalchemy.orm import Session
from backend.models.models import Shipment

def create_shipment(db: Session, tracking_number: str, origin: str, destination: str, weight: float, cost: float):
    shipment = Shipment(tracking_number=tracking_number, origin=origin, destination=destination, weight=weight, cost=cost)
    db.add(shipment)
    db.commit()
    db.refresh(shipment)
    return shipment

def get_all_shipments(db: Session):
    return db.query(Shipment).all()

def get_shipment_by_tracking_number(db: Session, tracking_number: str):
    return db.query(Shipment).filter(Shipment.tracking_number == tracking_number).first()
