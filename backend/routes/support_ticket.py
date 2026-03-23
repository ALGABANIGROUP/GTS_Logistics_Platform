from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.models.support_ticket import SupportTicket, TicketStatus
from backend.models.message_log import MessageLog
from backend.database.config import get_db
from datetime import datetime
from pydantic import BaseModel
from typing import List
router = APIRouter(prefix='/customer_service', tags=['Customer Service'])

class TicketCreate(BaseModel):
    customer_email: str
    subject: str
    description: str

class TicketOut(BaseModel):
    id: int
    customer_email: str
    subject: str
    description: str
    status: TicketStatus
    created_at: datetime

    class Config:
        from_attributes = True

@router.get('/tickets', response_model=List[TicketOut])
async def get_all_tickets(db: AsyncSession=Depends(get_db)):
    try:
        result = await db.execute(select(SupportTicket))
        return result.scalars().all()
    except Exception as e:
        print('❌ Error while fetching tickets:', e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/tickets/{ticket_id}', response_model=TicketOut)
async def get_ticket_by_id(ticket_id: int, db: AsyncSession=Depends(get_db)):
    result = await db.execute(select(SupportTicket).where(SupportTicket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail='Ticket not found')
    return ticket

@router.post('/tickets', response_model=TicketOut)
async def create_ticket(data: TicketCreate, db: AsyncSession=Depends(get_db)):
    ticket = SupportTicket(customer_email=data.customer_email, subject=data.subject, description=data.description, created_at=datetime.utcnow())
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)
    log = MessageLog(sender='Customer', message=data.description, context=f'ticket:{ticket.id}')
    db.add(log)
    await db.commit()
    return ticket

@router.get('/stats')
async def get_ticket_stats(db: AsyncSession=Depends(get_db)):
    result = await db.execute(select(SupportTicket))
    tickets = result.scalars().all()
    total = len(tickets)
    resolved = len([t for t in tickets if t.status == TicketStatus.resolved])
    open_ = len([t for t in tickets if t.status == TicketStatus.open])
    return {'totalTickets': total, 'resolvedTickets': resolved, 'openTickets': open_}
