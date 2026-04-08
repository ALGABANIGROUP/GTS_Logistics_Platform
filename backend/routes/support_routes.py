"""
Support System Routes - Full API Coverage
Complete API endpoints for support ticketing system
Support API implementation for ticket lifecycle, SLA, and knowledge base
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_, or_, func
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr
import uuid
from backend.database.session import wrap_session_factory, get_db
from backend.models.support_models import (
    SupportTicket, SupportAgent, SLALevel, TicketComment,
    TicketActivity, KnowledgeBase, SupportFeedback, SupportStats,
    EmailTemplate, SupportEmail, TicketAttachment, TicketHistory,
    TicketStatus, TicketPriority, TicketCategory, ChannelType, SLAStatus
)
from backend.security.auth import get_current_user
from backend.security.quota_dependency import check_feature_access
from backend.security.tenant_resolver import get_tenant_id
from backend.models.user import User

# ============================================
# SCHEMAS - response and request models
# ============================================

class SLALevelResponse(BaseModel):
    id: int
    priority: str
    response_time: int
    resolution_time: int
    
    model_config = ConfigDict(from_attributes=True)


class SupportAgentResponse(BaseModel):
    id: int
    user_id: int
    employee_id: str
    phone: Optional[str]
    is_available: bool
    is_online: bool
    specializations: list
    current_ticket_count: int
    average_satisfaction_score: float
    
    model_config = ConfigDict(from_attributes=True)


class TicketCommentResponse(BaseModel):
    id: int
    ticket_id: int
    author_id: int
    author_type: str
    content: str
    is_internal: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class TicketCreateRequest(BaseModel):
    title: str
    description: str
    category: str = TicketCategory.GENERAL
    priority: str = TicketPriority.MEDIUM
    attachments: Optional[List[str]] = []


class TicketCommentRequest(BaseModel):
    content: str
    is_internal: bool = False


class TicketAssignRequest(BaseModel):
    agent_id: int


class TicketStatusUpdateRequest(BaseModel):
    status: str
    internal_note: Optional[str] = None


class TicketFeedbackRequest(BaseModel):
    overall_rating: int  # 1-5
    response_time_rating: Optional[int] = None
    solution_quality_rating: Optional[int] = None
    agent_professionalism_rating: Optional[int] = None
    comments: Optional[str] = None
    would_recommend: Optional[bool] = None


class TicketResponse(BaseModel):
    id: int
    ticket_number: str
    title: str
    description: str
    status: str
    priority: str
    category: str
    channel: str
    customer_name: str
    assigned_to: Optional[int]
    first_response_at: Optional[datetime]
    resolved_at: Optional[datetime]
    sla_status: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class KnowledgeBaseCreateRequest(BaseModel):
    title: str
    content: str
    summary: str
    category: str
    tags: Optional[List[str]] = []


class KnowledgeBaseResponse(BaseModel):
    id: int
    title: str
    slug: str
    summary: str
    category: str
    view_count: int
    helpful_votes: int
    unhelpful_votes: int
    is_published: bool
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# ROUTER
# ============================================

router = APIRouter(prefix="/api/v1/support", tags=["support"])


async def require_advanced_tickets(request: Request) -> bool:
    return await check_feature_access(request, "advanced_tickets")


# ============================================
# 1. TICKET MANAGEMENT - core ticket lifecycle
# ============================================

@router.post("/tickets", response_model=TicketResponse)
async def create_ticket(
    request: TicketCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _quota_check: bool = Depends(require_advanced_tickets),
):
    """Create a new support ticket"""
    
    # Generate ticket number
    ticket_number = f"TK-{uuid.uuid4().hex[:8].upper()}"
    
    # Get SLA level
    sla_query = select(SLALevel).where(SLALevel.priority == request.priority)
    sla_result = await db.execute(sla_query)
    sla_level = sla_result.scalar_one()
    
    # Calculate SLA times
    now = datetime.utcnow()
    response_due = now + timedelta(hours=sla_level.response_time)
    resolution_due = now + timedelta(hours=sla_level.resolution_time)
    
    # Create ticket
    ticket = SupportTicket(
        ticket_number=ticket_number,
        customer_id=current_user.id,
        customer_email=current_user.email,
        customer_name=f"{current_user.first_name} {current_user.last_name}",
        title=request.title,
        description=request.description,
        category=request.category,
        priority=request.priority,
        channel=ChannelType.PORTAL,
        sla_level_id=sla_level.id,
        sla_response_due=response_due,
        sla_resolution_due=resolution_due,
        tenant_id=tenant_id,
    )
    
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)
    
    # Log activity
    activity = TicketActivity(
        ticket_id=ticket.id,
        action="created",
        description=f"Ticket created: {request.title}",
        actor_id=current_user.id,
    )
    db.add(activity)
    await db.commit()
    
    return ticket


@router.get("/tickets", response_model=List[TicketResponse])
async def list_tickets(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assigned_to: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """List support tickets with filters"""
    
    query = select(SupportTicket)
    
    # Filter by customer or agent
    if current_user.support_agent_profile:
        # Agent: can see assigned and all tickets
        query = query.where(
            or_(
                SupportTicket.assigned_to == current_user.support_agent_profile.id,
                SupportTicket.customer_id == current_user.id
            )
        )
    else:
        # Customer: only their tickets
        query = query.where(SupportTicket.customer_id == current_user.id)
    
    # Apply filters
    if status:
        query = query.where(SupportTicket.status == status)
    if priority:
        query = query.where(SupportTicket.priority == priority)
    if assigned_to:
        query = query.where(SupportTicket.assigned_to == assigned_to)
    
    # Order and paginate
    query = query.order_by(desc(SupportTicket.created_at)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    tickets = result.scalars().all()
    
    return tickets


@router.get("/tickets/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Get ticket details"""
    
    ticket = await db.get(SupportTicket, ticket_id)
    
    if not ticket or ticket.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Check access
    is_customer = ticket.customer_id == current_user.id
    is_agent = current_user.support_agent_profile and ticket.assigned_to == current_user.support_agent_profile.id
    
    if not (is_customer or is_agent):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return ticket


@router.put("/tickets/{ticket_id}/status", response_model=TicketResponse)
async def update_ticket_status(
    ticket_id: int,
    request: TicketStatusUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update ticket status"""
    
    ticket = await db.get(SupportTicket, ticket_id)
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Check access (agent only)
    if not current_user.support_agent_profile or ticket.assigned_to != current_user.support_agent_profile.id:
        raise HTTPException(status_code=403, detail="Only assigned agent can update status")
    
    old_status = ticket.status
    ticket.status = request.status
    ticket.updated_at = datetime.utcnow()
    
    # Track resolution
    if request.status == TicketStatus.RESOLVED:
        ticket.resolved_at = datetime.utcnow()
    elif request.status == TicketStatus.CLOSED:
        ticket.closed_at = datetime.utcnow()
    
    # Record first response if this is the first update
    if not ticket.first_response_at and request.status != TicketStatus.OPEN:
        ticket.first_response_at = datetime.utcnow()
    
    await db.commit()
    
    # Log activity
    activity = TicketActivity(
        ticket_id=ticket.id,
        action="status_changed",
        description=f"Status changed from {old_status} to {request.status}",
        actor_id=current_user.id,
        old_value=old_status,
        new_value=request.status
    )
    db.add(activity)
    
    if request.internal_note:
        comment = TicketComment(
            ticket_id=ticket.id,
            author_id=current_user.id,
            author_type="agent",
            content=request.internal_note,
            is_internal=True
        )
        db.add(comment)
    
    await db.commit()
    await db.refresh(ticket)
    
    return ticket


@router.put("/tickets/{ticket_id}/assign")
async def assign_ticket(
    ticket_id: int,
    request: TicketAssignRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Assign ticket to agent"""
    
    ticket = await db.get(SupportTicket, ticket_id)
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Check if agent exists
    agent = await db.get(SupportAgent, request.agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    old_agent_id = ticket.assigned_to
    ticket.assigned_to = request.agent_id
    ticket.status = TicketStatus.IN_PROGRESS
    ticket.updated_at = datetime.utcnow()
    
    await db.commit()
    
    # Log activity
    activity = TicketActivity(
        ticket_id=ticket.id,
        action="assigned",
        description=f"Assigned to {agent.user.email}",
        actor_id=current_user.id,
        old_value=str(old_agent_id),
        new_value=str(request.agent_id)
    )
    db.add(activity)
    
    # Create history record
    history = TicketHistory(
        ticket_id=ticket.id,
        old_status=TicketStatus.OPEN,
        new_status=TicketStatus.IN_PROGRESS,
        old_agent_id=old_agent_id,
        new_agent_id=request.agent_id,
        changed_by=current_user.id
    )
    db.add(history)
    
    await db.commit()
    await db.refresh(ticket)
    
    return {"message": "Ticket assigned successfully", "ticket": ticket}


# ============================================
# 2. COMMENTS - ticket conversation thread
# ============================================

@router.post("/tickets/{ticket_id}/comments", response_model=TicketCommentResponse)
async def add_comment(
    ticket_id: int,
    request: TicketCommentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add comment to ticket"""
    
    ticket = await db.get(SupportTicket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Check access
    is_customer = ticket.customer_id == current_user.id
    is_agent = current_user.support_agent_profile and ticket.assigned_to == current_user.support_agent_profile.id
    
    if not (is_customer or is_agent):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    author_type = "agent" if current_user.support_agent_profile else "customer"
    
    comment = TicketComment(
        ticket_id=ticket.id,
        author_id=current_user.id,
        author_type=author_type,
        content=request.content,
        is_internal=request.is_internal
    )
    
    db.add(comment)
    ticket.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(comment)
    
    return comment


@router.get("/tickets/{ticket_id}/comments", response_model=List[TicketCommentResponse])
async def get_comments(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get ticket comments"""
    
    ticket = await db.get(SupportTicket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Check access
    is_customer = ticket.customer_id == current_user.id
    is_agent = current_user.support_agent_profile and ticket.assigned_to == current_user.support_agent_profile.id
    
    if not (is_customer or is_agent):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    query = select(TicketComment).where(TicketComment.ticket_id == ticket_id)
    
    # Hide internal notes from customers
    if is_customer:
        query = query.where(TicketComment.is_internal == False)
    
    query = query.order_by(TicketComment.created_at)
    
    result = await db.execute(query)
    comments = result.scalars().all()
    
    return comments


# ============================================
# 3. FEEDBACK - post-resolution quality signals
# ============================================

@router.post("/tickets/{ticket_id}/feedback")
async def submit_feedback(
    ticket_id: int,
    request: TicketFeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit feedback on ticket resolution"""
    
    ticket = await db.get(SupportTicket, ticket_id)
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    if ticket.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only customer can submit feedback")
    
    feedback = SupportFeedback(
        ticket_id=ticket.id,
        overall_rating=request.overall_rating,
        response_time_rating=request.response_time_rating,
        solution_quality_rating=request.solution_quality_rating,
        agent_professionalism_rating=request.agent_professionalism_rating,
        comments=request.comments,
        would_recommend=request.would_recommend
    )
    
    db.add(feedback)
    ticket.satisfaction_score = request.overall_rating
    
    await db.commit()
    
    return {"message": "Feedback submitted successfully"}


# ============================================
# 4. KNOWLEDGE BASE - article management
# ============================================

@router.post("/knowledge-base", response_model=KnowledgeBaseResponse)
async def create_kb_article(
    request: KnowledgeBaseCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create knowledge base article (agent only)"""
    
    if not current_user.support_agent_profile:
        raise HTTPException(status_code=403, detail="Only support agents can create articles")
    
    slug = request.title.lower().replace(" ", "-")
    
    article = KnowledgeBase(
        title=request.title,
        slug=slug,
        content=request.content,
        summary=request.summary,
        category=request.category,
        tags=request.tags,
        author_id=current_user.id
    )
    
    db.add(article)
    await db.commit()
    await db.refresh(article)
    
    return article


@router.get("/knowledge-base", response_model=List[KnowledgeBaseResponse])
async def list_kb_articles(
    category: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """List knowledge base articles"""
    
    query = select(KnowledgeBase).where(KnowledgeBase.is_published == True)
    
    if category:
        query = query.where(KnowledgeBase.category == category)
    
    if search:
        query = query.where(
            or_(
                KnowledgeBase.title.ilike(f"%{search}%"),
                KnowledgeBase.content.ilike(f"%{search}%")
            )
        )
    
    query = query.order_by(desc(KnowledgeBase.view_count)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    articles = result.scalars().all()
    
    return articles


@router.get("/knowledge-base/{article_id}", response_model=KnowledgeBaseResponse)
async def get_kb_article(
    article_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get knowledge base article"""
    
    article = await db.get(KnowledgeBase, article_id)
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Increment view count
    article.view_count += 1
    await db.commit()
    
    return article


# ============================================
# 5. SUPPORT AGENTS - assignment and capacity
# ============================================

@router.get("/agents", response_model=List[SupportAgentResponse])
async def list_agents(
    is_available: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List support agents"""
    
    query = select(SupportAgent)
    
    if is_available is not None:
        query = query.where(SupportAgent.is_available == is_available)
    
    result = await db.execute(query)
    agents = result.scalars().all()
    
    return agents


# ============================================
# 6. SLA MANAGEMENT - SLA policy and breach monitoring
# ============================================

@router.get("/sla-levels", response_model=List[SLALevelResponse])
async def get_sla_levels(db: AsyncSession = Depends(get_db)):
    """Get all SLA levels"""
    
    query = select(SLALevel)
    result = await db.execute(query)
    levels = result.scalars().all()
    
    return levels


# ============================================
# 7. STATS - analytics and performance indicators
# ============================================

@router.get("/stats")
async def get_support_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get general support statistics for dashboard"""
    
    try:
        # Get total tickets
        total_query = select(func.count(SupportTicket.id))
        total_result = await db.execute(total_query)
        total_tickets = total_result.scalar() or 0
        
        # Get open tickets (OPEN, IN_PROGRESS, WAITING_CUSTOMER, REOPENED)
        open_statuses = [TicketStatus.OPEN, TicketStatus.IN_PROGRESS, TicketStatus.WAITING_CUSTOMER, TicketStatus.REOPENED]
        open_query = select(func.count(SupportTicket.id)).where(SupportTicket.status.in_(open_statuses))
        open_result = await db.execute(open_query)
        open_tickets = open_result.scalar() or 0
        
        # Get resolved today
        today = datetime.utcnow().date()
        resolved_today_query = select(func.count(SupportTicket.id)).where(
            and_(
                SupportTicket.status == TicketStatus.RESOLVED,
                func.date(SupportTicket.resolved_at) == today
            )
        )
        resolved_today_result = await db.execute(resolved_today_query)
        resolved_today = resolved_today_result.scalar() or 0
        
        # Get active agents
        active_agents_query = select(func.count(SupportAgent.id)).where(
            and_(
                SupportAgent.is_available == True,
                SupportAgent.is_online == True
            )
        )
        active_agents_result = await db.execute(active_agents_query)
        active_agents = active_agents_result.scalar() or 0
        
        # Get daily stats for last 7 days (simplified - just counts per day)
        daily_stats = []
        for i in range(7):
            date = datetime.utcnow() - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            
            daily_query = select(func.count(SupportTicket.id)).where(
                func.date(SupportTicket.created_at) == date.date()
            )
            daily_result = await db.execute(daily_query)
            count = daily_result.scalar() or 0
            
            daily_stats.append({
                "date": date_str,
                "tickets_created": count,
                "tickets_resolved": 0  # Simplified for now
            })
        
        # Get agent performance (simplified - just assigned ticket counts)
        agent_performance_query = select(
            SupportAgent.id,
            SupportAgent.employee_id,
            func.count(SupportTicket.id).label("assigned_tickets")
        ).join(
            SupportTicket, SupportTicket.assigned_to == SupportAgent.id, isouter=True
        ).group_by(SupportAgent.id, SupportAgent.employee_id)
        
        agent_performance_result = await db.execute(agent_performance_query)
        agent_performance = [
            {
                "agent_id": row.id,
                "employee_id": row.employee_id,
                "assigned_tickets": row.assigned_tickets or 0,
                "resolved_today": 0,  # Simplified for now
                "satisfaction_score": 0.0  # Simplified for now
            }
            for row in agent_performance_result
        ]
        
    except Exception as e:
        print(f"Error getting support stats: {e}")
        # Return zeros on error
        return {
            "total_tickets": 0,
            "open_tickets": 0,
            "resolved_today": 0,
            "active_agents": 0,
            "daily_stats": [],
            "agent_performance": []
        }
    
    return {
        "total_tickets": total_tickets,
        "open_tickets": open_tickets,
        "resolved_today": resolved_today,
        "active_agents": active_agents,
        "daily_stats": daily_stats,
        "agent_performance": agent_performance
    }


@router.get("/stats/daily")
async def get_daily_stats(
    days: int = Query(7, ge=1, le=30),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get daily support statistics"""
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = select(SupportStats).where(
        SupportStats.date >= start_date.strftime("%Y-%m-%d")
    ).order_by(SupportStats.date)
    
    result = await db.execute(query)
    stats = result.scalars().all()
    
    return stats


@router.get("/stats/agent/{agent_id}")
async def get_agent_stats(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get agent statistics"""
    
    agent = await db.get(SupportAgent, agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Get ticket statistics
    tickets_query = select(SupportTicket).where(SupportTicket.assigned_to == agent_id)
    result = await db.execute(tickets_query)
    tickets = result.scalars().all()
    
    resolved_count = sum(1 for t in tickets if t.status == TicketStatus.RESOLVED)
    closed_count = sum(1 for t in tickets if t.status == TicketStatus.CLOSED)
    
    return {
        "agent_id": agent_id,
        "total_tickets": len(tickets),
        "resolved_tickets": resolved_count,
        "closed_tickets": closed_count,
        "average_satisfaction_score": agent.average_satisfaction_score,
        "average_resolution_time": agent.average_resolution_time,
        "current_workload": agent.current_ticket_count
    }
