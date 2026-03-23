from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.database.config import SessionLocal
import random
router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get('/overview')
def get_support_overview(db: Session=Depends(get_db)):
    """Fetch support ticket statistics and response performance"""
    try:
        support_data = {'total_tickets': random.randint(500, 2000), 'open_tickets': random.randint(50, 300), 'resolved_tickets': random.randint(400, 1800), 'average_response_time': f'{random.randint(2, 24)} hours', 'ai_analysis': 'Most support issues are related to shipment tracking and billing.'}
        return support_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error fetching support data: {str(e)}')

@router.get('/tickets')
def get_support_tickets():
    """Fetch detailed support ticket records"""
    try:
        support_tickets = [{'ticket_id': f'TKT{random.randint(1000, 9999)}', 'status': 'Open', 'issue': 'Shipment delayed'}, {'ticket_id': f'TKT{random.randint(1000, 9999)}', 'status': 'Resolved', 'issue': 'Billing discrepancy'}, {'ticket_id': f'TKT{random.randint(1000, 9999)}', 'status': 'In Progress', 'issue': 'Damaged goods claim'}]
        return support_tickets
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error fetching support ticket details: {str(e)}')
