from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.config import get_db
from backend.models.models import Shipment
from backend.models.financial import FinancialTransaction
from backend.models.ai_reports import AIReport
from datetime import datetime
router = APIRouter()

@router.post('/test/seed')
async def seed_test_data(db: AsyncSession=Depends(get_db)):
    shipment1 = Shipment(tracking_number='GTS1001', status='in_transit', origin='Austin, TX', destination='Dallas, TX', weight=6000.0, cost=2000.0)
    shipment2 = Shipment(tracking_number='GTS1002', status='delivered', origin='Houston, TX', destination='New York, NY', weight=8000.0, cost=4500.0)
    transaction1 = FinancialTransaction(type='INCOME', amount=7000.0, created_at=datetime.utcnow())
    transaction2 = FinancialTransaction(type='EXPENSE', amount=3200.0, created_at=datetime.utcnow())
    ai_report = AIReport(bot_name='FinanceBot', report_type='financial_summary', status='completed', summary='AI Financial Summary Report', details={'revenue': 7000, 'expenses': 3200, 'net_profit': 3800})
    db.add_all([shipment1, shipment2, transaction1, transaction2, ai_report])
    await db.commit()
    return {'message': 'Test data seeded successfully'}
