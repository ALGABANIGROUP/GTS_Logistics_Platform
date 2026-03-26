"""
AI Sales Team Bot - Complete English Implementation
Handles lead management, deal pipeline, revenue forecasting, and customer intelligence
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any
import asyncio
from dataclasses import dataclass, field


class LeadStatus(Enum):
    """Lead lifecycle stages"""
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"
    NURTURING = "nurturing"


class CustomerSegment(Enum):
    """Customer categorization"""
    VIP = "vip"
    REGULAR = "regular"
    NEW = "new"
    AT_RISK = "at_risk"
    CHURNED = "churned"
    POTENTIAL = "potential"


class DealStage(Enum):
    """Sales pipeline stages"""
    DISCOVERY = "discovery"
    QUALIFICATION = "qualification"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSURE = "closure"
    FOLLOW_UP = "follow_up"


@dataclass
class Customer:
    """Customer entity with full profile"""
    id: int
    name: str
    email: str
    phone: str
    company: str
    segment: CustomerSegment
    total_value: float = 0.0
    lifetime_value: float = 0.0
    satisfaction_score: float = 0.0
    last_interaction: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Lead:
    """Lead entity with tracking info"""
    id: int
    customer_name: str
    email: str
    phone: str
    company: str
    status: LeadStatus
    source: str
    score: float = 0.0
    estimated_value: float = 0.0
    next_action: Optional[str] = None
    assigned_to: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_contact: Optional[datetime] = None


@dataclass
class Deal:
    """Deal entity with pipeline tracking"""
    id: int
    lead_id: int
    customer_name: str
    stage: DealStage
    value: float
    probability: float
    expected_close_date: datetime
    products: List[str] = field(default_factory=list)
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SalesActivity:
    """Sales activity log"""
    id: int
    activity_type: str  # call, email, meeting, walkthrough, proposal
    lead_id: Optional[int] = None
    deal_id: Optional[int] = None
    description: str = ""
    outcome: str = ""
    scheduled_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)


class SalesBot:
    """
    AI Sales Team Bot - Intelligent Sales Automation
    
    Features:
    - Lead capture and scoring
    - Deal pipeline management
    - Revenue forecasting
    - Customer needs prediction
    - Automated proposal generation
    - Meeting scheduling optimization
    - Performance analytics
    """
    
    def __init__(self):
        self.name = "sales_bot"
        self.display_name = "AI Sales Team Bot"
        self.description = "Intelligent sales automation and customer relationship management"
        self.version = "1.0.0"
        self.is_running = False
        
        # Data storage
        self.customers: Dict[int, Customer] = {}
        self.leads: Dict[int, Lead] = {}
        self.deals: Dict[int, Deal] = {}
        self.activities: List[SalesActivity] = []
        
        # Counters
        self._next_customer_id = 1
        self._next_lead_id = 1
        self._next_deal_id = 1
        self._next_activity_id = 1
        
        # Configuration
        self.config = {
            "auto_lead_scoring": True,
            "auto_follow_up": True,
            "forecast_horizon_days": 90,
            "high_value_threshold": 50000,
            "qualification_threshold": 70,
        }
    
    async def run(self) -> Dict[str, Any]:
        """Start the Sales Bot"""
        self.is_running = True
        await self._initialize_seed_data()
        
        return {
            "status": "success",
            "message": "Sales Bot started successfully",
            "bot": self.name,
            "leads_count": len(self.leads),
            "deals_count": len(self.deals),
            "customers_count": len(self.customers)
        }
    
    async def stop(self) -> Dict[str, Any]:
        """Stop the Sales Bot"""
        self.is_running = False
        return {
            "status": "success",
            "message": "Sales Bot stopped",
            "bot": self.name
        }
    
    def status(self) -> Dict[str, Any]:
        """Get bot status"""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "version": self.version,
            "is_running": self.is_running,
            "description": self.description
        }
    
    def get_config(self) -> Dict[str, Any]:
        """Get bot configuration"""
        return self.config.copy()
    
    async def _initialize_seed_data(self):
        """Initialize with starter leads and deals"""
        # Starter leads
        seed_leads = [
            {
                "customer_name": "ABC Logistics",
                "email": "contact@abclogistics.com",
                "phone": "+1-555-0101",
                "company": "ABC Logistics",
                "source": "website",
                "status": LeadStatus.QUALIFIED,
                "score": 85,
                "estimated_value": 75000
            },
            {
                "customer_name": "XYZ Freight",
                "email": "info@xyzfreight.com",
                "phone": "+1-555-0102",
                "company": "XYZ Freight",
                "source": "referral",
                "status": LeadStatus.PROPOSAL,
                "score": 92,
                "estimated_value": 120000
            },
            {
                "customer_name": "Global Shipping Co",
                "email": "sales@globalship.com",
                "phone": "+1-555-0103",
                "company": "Global Shipping Co",
                "source": "cold_call",
                "status": LeadStatus.NEW,
                "score": 65,
                "estimated_value": 45000
            }
        ]
        
        for lead_data in seed_leads:
            await self.capture_lead(lead_data)
    
    async def capture_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Capture new lead with automatic scoring
        
        Args:
            lead_data: Dictionary with lead information
        
        Returns:
            Created lead details
        """
        lead_id = self._next_lead_id
        self._next_lead_id += 1
        
        # Auto-calculate lead score if not provided
        score = lead_data.get("score", 0)
        if not score and self.config["auto_lead_scoring"]:
            score = await self._calculate_lead_score(lead_data)
        
        lead = Lead(
            id=lead_id,
            customer_name=lead_data["customer_name"],
            email=lead_data["email"],
            phone=lead_data["phone"],
            company=lead_data["company"],
            source=lead_data.get("source", "unknown"),
            status=lead_data.get("status", LeadStatus.NEW),
            score=score,
            estimated_value=lead_data.get("estimated_value", 0),
            assigned_to=lead_data.get("assigned_to"),
            next_action=lead_data.get("next_action", "Initial contact required")
        )
        
        self.leads[lead_id] = lead
        
        # Log activity
        activity = SalesActivity(
            id=self._next_activity_id,
            activity_type="lead_capture",
            lead_id=lead_id,
            description=f"New lead captured: {lead.customer_name}",
            outcome="success"
        )
        self._next_activity_id += 1
        self.activities.append(activity)
        
        return {
            "status": "success",
            "message": "Lead captured successfully",
            "lead_id": lead_id,
            "lead": {
                "id": lead.id,
                "name": lead.customer_name,
                "email": lead.email,
                "score": lead.score,
                "status": lead.status.value,
                "estimated_value": lead.estimated_value
            }
        }
    
    async def _calculate_lead_score(self, lead_data: Dict[str, Any]) -> float:
        """Calculate lead score based on various factors"""
        score = 50.0  # Base score
        
        # Source quality scoring
        source_scores = {
            "referral": 30,
            "website": 20,
            "event": 25,
            "cold_call": 10,
            "email_campaign": 15
        }
        score += source_scores.get(lead_data.get("source", ""), 5)
        
        # Company size indicator (basic heuristic)
        if lead_data.get("estimated_value", 0) > self.config["high_value_threshold"]:
            score += 20
        
        # Ensure score is between 0-100
        return min(max(score, 0), 100)
    
    async def qualify_lead(self, lead_id: int, qualification_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Qualify a lead based on criteria
        
        Args:
            lead_id: Lead identifier
            qualification_data: Qualification criteria and notes
        
        Returns:
            Qualification result
        """
        if lead_id not in self.leads:
            return {"status": "error", "message": "Lead not found"}
        
        lead = self.leads[lead_id]
        
        # Update lead status based on qualification
        is_qualified = qualification_data.get("is_qualified", True)
        
        if is_qualified:
            lead.status = LeadStatus.QUALIFIED
            lead.score = max(lead.score, self.config["qualification_threshold"])
            lead.next_action = "Prepare proposal"
        else:
            lead.status = LeadStatus.NURTURING
            lead.next_action = "Follow up in 30 days"
        
        # Log activity
        activity = SalesActivity(
            id=self._next_activity_id,
            activity_type="qualification",
            lead_id=lead_id,
            description=f"Lead qualification: {lead.customer_name}",
            outcome="qualified" if is_qualified else "not_qualified"
        )
        self._next_activity_id += 1
        self.activities.append(activity)
        
        return {
            "status": "success",
            "message": "Lead qualified successfully",
            "lead_id": lead_id,
            "is_qualified": is_qualified,
            "next_action": lead.next_action
        }
    
    async def create_deal(self, lead_id: int, deal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a deal from a qualified lead
        
        Args:
            lead_id: Source lead identifier
            deal_data: Deal information
        
        Returns:
            Created deal details
        """
        if lead_id not in self.leads:
            return {"status": "error", "message": "Lead not found"}
        
        lead = self.leads[lead_id]
        
        deal_id = self._next_deal_id
        self._next_deal_id += 1
        
        # Calculate expected close date
        days_to_close = deal_data.get("days_to_close", 30)
        expected_close = datetime.now() + timedelta(days=days_to_close)
        
        deal = Deal(
            id=deal_id,
            lead_id=lead_id,
            customer_name=lead.customer_name,
            stage=deal_data.get("stage", DealStage.DISCOVERY),
            value=deal_data.get("value", lead.estimated_value),
            probability=deal_data.get("probability", 50.0),
            expected_close_date=expected_close,
            products=deal_data.get("products", []),
            notes=deal_data.get("notes", "")
        )
        
        self.deals[deal_id] = deal
        
        # Update lead status
        lead.status = LeadStatus.PROPOSAL
        
        # Log activity
        activity = SalesActivity(
            id=self._next_activity_id,
            activity_type="deal_creation",
            lead_id=lead_id,
            deal_id=deal_id,
            description=f"Deal created: {deal.customer_name} - ${deal.value:,.2f}",
            outcome="success"
        )
        self._next_activity_id += 1
        self.activities.append(activity)
        
        return {
            "status": "success",
            "message": "Deal created successfully",
            "deal_id": deal_id,
            "deal": {
                "id": deal.id,
                "customer": deal.customer_name,
                "value": deal.value,
                "stage": deal.stage.value,
                "probability": deal.probability,
                "expected_close": deal.expected_close_date.strftime("%Y-%m-%d")
            }
        }
    
    async def update_deal_stage(self, deal_id: int, new_stage: DealStage, probability: Optional[float] = None) -> Dict[str, Any]:
        """Update deal pipeline stage"""
        if deal_id not in self.deals:
            return {"status": "error", "message": "Deal not found"}
        
        deal = self.deals[deal_id]
        old_stage = deal.stage
        
        deal.stage = new_stage
        if probability is not None:
            deal.probability = probability
        
        # Log activity
        activity = SalesActivity(
            id=self._next_activity_id,
            activity_type="stage_update",
            deal_id=deal_id,
            description=f"Deal moved: {old_stage.value} → {new_stage.value}",
            outcome="success"
        )
        self._next_activity_id += 1
        self.activities.append(activity)
        
        return {
            "status": "success",
            "message": "Deal stage updated",
            "deal_id": deal_id,
            "old_stage": old_stage.value,
            "new_stage": new_stage.value,
            "probability": deal.probability
        }
    
    async def forecast_revenue(self, days: Optional[int] = None) -> Dict[str, Any]:
        """
        Forecast revenue based on deal pipeline
        
        Args:
            days: Forecast horizon in days (default from config)
        
        Returns:
            Revenue forecast breakdown
        """
        if days is None:
            days = self.config["forecast_horizon_days"]
        
        forecast_date = datetime.now() + timedelta(days=days)
        
        # Calculate weighted pipeline
        total_pipeline = 0.0
        weighted_pipeline = 0.0
        deals_in_forecast = []
        
        for deal in self.deals.values():
            if deal.expected_close_date <= forecast_date:
                total_pipeline += deal.value
                weighted_value = deal.value * (deal.probability / 100)
                weighted_pipeline += weighted_value
                
                deals_in_forecast.append({
                    "id": deal.id,
                    "customer": deal.customer_name,
                    "value": deal.value,
                    "probability": deal.probability,
                    "weighted_value": weighted_value,
                    "expected_close": deal.expected_close_date.strftime("%Y-%m-%d"),
                    "stage": deal.stage.value
                })
        
        # Calculate by stage
        stage_breakdown = {}
        for stage in DealStage:
            stage_deals = [d for d in self.deals.values() if d.stage == stage]
            stage_value = sum(d.value for d in stage_deals)
            stage_weighted = sum(d.value * (d.probability / 100) for d in stage_deals)
            
            stage_breakdown[stage.value] = {
                "count": len(stage_deals),
                "total_value": stage_value,
                "weighted_value": stage_weighted
            }
        
        return {
            "status": "success",
            "forecast_period_days": days,
            "forecast_end_date": forecast_date.strftime("%Y-%m-%d"),
            "total_pipeline": total_pipeline,
            "weighted_forecast": weighted_pipeline,
            "deals_count": len(deals_in_forecast),
            "deals": deals_in_forecast,
            "by_stage": stage_breakdown
        }
    
    async def predict_customer_needs(self, customer_id: Optional[int] = None) -> Dict[str, Any]:
        """Predict customer needs based on history and patterns"""
        predictions = []
        
        # Analyze all customers or specific one
        customers_to_analyze = [self.customers[customer_id]] if customer_id and customer_id in self.customers else self.customers.values()
        
        for customer in customers_to_analyze:
            needs = []
            
            # Predict based on segment
            if customer.segment == CustomerSegment.VIP:
                needs.append("Premium service package")
                needs.append("Dedicated account manager")
            elif customer.segment == CustomerSegment.AT_RISK:
                needs.append("Retention offer")
                needs.append("Service improvement plan")
            elif customer.segment == CustomerSegment.NEW:
                needs.append("Onboarding support")
                needs.append("Product training")
            
            # Value-based predictions
            if customer.lifetime_value > self.config["high_value_threshold"]:
                needs.append("Volume discount opportunity")
                needs.append("Strategic partnership proposal")
            
            predictions.append({
                "customer_id": customer.id,
                "customer_name": customer.name,
                "segment": customer.segment.value,
                "predicted_needs": needs,
                "confidence": 0.75
            })
        
        return {
            "status": "success",
            "predictions_count": len(predictions),
            "predictions": predictions
        }
    
    async def generate_proposal(self, deal_id: int, template: str = "standard") -> Dict[str, Any]:
        """Generate automated proposal for a deal"""
        if deal_id not in self.deals:
            return {"status": "error", "message": "Deal not found"}
        
        deal = self.deals[deal_id]
        
        proposal = {
            "deal_id": deal_id,
            "customer": deal.customer_name,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "template": template,
            "sections": [
                {
                    "title": "Executive Summary",
                    "content": f"Proposal for {deal.customer_name} - Total Value: ${deal.value:,.2f}"
                },
                {
                    "title": "Proposed Solution",
                    "content": f"Products/Services: {', '.join(deal.products) if deal.products else 'Custom solution'}"
                },
                {
                    "title": "Pricing",
                    "content": f"Total Investment: ${deal.value:,.2f}"
                },
                {
                    "title": "Terms & Conditions",
                    "content": "Standard terms apply"
                }
            ],
            "generated_at": datetime.now().isoformat()
        }
        
        # Log activity
        activity = SalesActivity(
            id=self._next_activity_id,
            activity_type="proposal",
            deal_id=deal_id,
            description=f"Proposal generated for {deal.customer_name}",
            outcome="success"
        )
        self._next_activity_id += 1
        self.activities.append(activity)
        
        return {
            "status": "success",
            "message": "Proposal generated successfully",
            "proposal": proposal
        }
    
    async def schedule_meeting(self, lead_id: Optional[int] = None, deal_id: Optional[int] = None, 
                              meeting_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Schedule sales meeting with optimal timing"""
        if not meeting_data:
            meeting_data = {}
        
        # Find optimal time (simplified - in production, check calendars)
        suggested_time = datetime.now() + timedelta(days=2, hours=10)  # Default: day after tomorrow at 10 AM
        
        activity = SalesActivity(
            id=self._next_activity_id,
            activity_type="meeting",
            lead_id=lead_id,
            deal_id=deal_id,
            description=meeting_data.get("description", "Sales meeting"),
            scheduled_at=suggested_time
        )
        self._next_activity_id += 1
        self.activities.append(activity)
        
        return {
            "status": "success",
            "message": "Meeting scheduled successfully",
            "activity_id": activity.id,
            "scheduled_at": suggested_time.strftime("%Y-%m-%d %H:%M"),
            "attendees": meeting_data.get("attendees", []),
            "agenda": meeting_data.get("agenda", "Sales discussion")
        }
    
    async def calculate_pipeline_health(self) -> Dict[str, Any]:
        """Calculate overall pipeline health metrics"""
        if not self.deals:
            return {
                "status": "success",
                "health_score": 0,
                "message": "No deals in pipeline"
            }
        
        # Metrics calculation
        total_deals = len(self.deals)
        total_value = sum(d.value for d in self.deals.values())
        avg_probability = sum(d.probability for d in self.deals.values()) / total_deals if total_deals > 0 else 0
        
        # Stage distribution
        stage_counts = {}
        for stage in DealStage:
            count = len([d for d in self.deals.values() if d.stage == stage])
            stage_counts[stage.value] = count
        
        # Health score calculation (0-100)
        health_score = 50  # Base score
        
        # More deals = healthier
        if total_deals >= 10:
            health_score += 20
        elif total_deals >= 5:
            health_score += 10
        
        # Higher average probability = healthier
        if avg_probability >= 70:
            health_score += 20
        elif avg_probability >= 50:
            health_score += 10
        
        # Balanced stage distribution = healthier
        early_stage = stage_counts.get(DealStage.DISCOVERY.value, 0) + stage_counts.get(DealStage.QUALIFICATION.value, 0)
        if early_stage >= total_deals * 0.3:  # At least 30% in early stages
            health_score += 10
        
        health_score = min(health_score, 100)
        
        return {
            "status": "success",
            "health_score": health_score,
            "total_deals": total_deals,
            "total_pipeline_value": total_value,
            "average_probability": avg_probability,
            "stage_distribution": stage_counts,
            "recommendation": self._get_health_recommendation(health_score)
        }
    
    def _get_health_recommendation(self, health_score: float) -> str:
        """Get recommendation based on health score"""
        if health_score >= 80:
            return "Excellent pipeline health. Maintain current momentum."
        elif health_score >= 60:
            return "Good pipeline. Focus on converting high-probability deals."
        elif health_score >= 40:
            return "Average pipeline. Increase lead generation and qualification efforts."
        else:
            return "Pipeline needs attention. Prioritize new lead capture and qualification."
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        # Pipeline health
        health = await self.calculate_pipeline_health()
        
        # Revenue forecast
        forecast = await self.forecast_revenue()
        
        # Lead statistics
        lead_stats = {
            "total": len(self.leads),
            "by_status": {}
        }
        for status in LeadStatus:
            count = len([l for l in self.leads.values() if l.status == status])
            lead_stats["by_status"][status.value] = count
        
        # Recent activities
        recent_activities = sorted(self.activities, key=lambda a: a.created_at, reverse=True)[:10]
        
        return {
            "status": "success",
            "dashboard": {
                "pipeline_health": health,
                "revenue_forecast": forecast,
                "lead_statistics": lead_stats,
                "deal_count": len(self.deals),
                "customer_count": len(self.customers),
                "recent_activities": [
                    {
                        "id": a.id,
                        "type": a.activity_type,
                        "description": a.description,
                        "outcome": a.outcome,
                        "created_at": a.created_at.strftime("%Y-%m-%d %H:%M")
                    }
                    for a in recent_activities
                ]
            }
        }


# Bot instance for registration
bot = SalesBot()


# Export for bot registry
async def get_bot_instance():
    """Get bot instance for registry"""
    return bot
