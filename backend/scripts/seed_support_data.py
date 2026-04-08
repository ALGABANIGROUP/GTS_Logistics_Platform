#!/usr/bin/env python3
"""
Seed Support Data Script
Creates sample support tickets and agents for testing the dashboard
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path (like run_server.py does)
repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(repo_root))

print(f"Python path: {sys.path[:3]}")
print(f"Repo root: {repo_root}")

try:
    from backend.database.session import get_async_session
    print("Database session import successful")
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models.support_models import (
    SupportTicket, SupportAgent, SLALevel,
    TicketStatus, TicketPriority, TicketCategory
)
from backend.models.user import User
from datetime import datetime, timedelta
import random

async def seed_support_data():
    """Create sample support data for testing"""

    async for session in get_async_session():
        try:
            # Check if data already exists
            stmt = select(SupportTicket).limit(1)
            result = await session.execute(stmt)
            if result.scalar():
                print("Support data already exists, skipping seed")
                return

            # Get a test user
            stmt = select(User).limit(1)
            result = await session.execute(stmt)
            user = result.scalar()
            if not user:
                print("No users found, cannot create support data")
                return

            # Create SLA levels
            sla_levels = [
                SLALevel(
                    priority='critical',
                    response_time_hours=1,
                    resolution_time_hours=4,
                    escalation_after_hours=2
                ),
                SLALevel(
                    priority='high',
                    response_time_hours=2,
                    resolution_time_hours=8,
                    escalation_after_hours=4
                ),
                SLALevel(
                    priority='medium',
                    response_time_hours=4,
                    resolution_time_hours=24,
                    escalation_after_hours=12
                ),
                SLALevel(
                    priority='low',
                    response_time_hours=8,
                    resolution_time_hours=48,
                    escalation_after_hours=24
                ),
            ]
            session.add_all(sla_levels)
            await session.flush()

            # Create support agents
            agents = []
            for i in range(3):
                agent = SupportAgent(
                    user_id=user.id,
                    employee_id=f"AGT{i+1:03d}",
                    phone=f"+1-555-01{i+1}-0000",
                    is_available=True,
                    is_online=random.choice([True, False]),
                    specializations=["technical", "billing", "general"][:random.randint(1, 3)],
                    current_ticket_count=random.randint(0, 5),
                    average_satisfaction_score=round(random.uniform(3.5, 5.0), 1)
                )
                agents.append(agent)
                session.add(agent)

            await session.flush()

            # Create sample tickets
            statuses = [TicketStatus.open, TicketStatus.in_progress, TicketStatus.resolved, TicketStatus.closed]
            priorities = [TicketPriority.low, TicketPriority.medium, TicketPriority.high, TicketPriority.critical]
            categories = [TicketCategory.technical, TicketCategory.billing, TicketCategory.general, TicketCategory.feature_request]

            tickets = []
            for i in range(20):
                # Create tickets over the last 30 days
                days_ago = random.randint(0, 30)
                created_at = datetime.utcnow() - timedelta(days=days_ago)

                ticket = SupportTicket(
                    title=f"Sample Ticket {i+1}",
                    description=f"This is a sample support ticket #{i+1} for testing purposes.",
                    status=random.choice(statuses),
                    priority=random.choice(priorities),
                    category=random.choice(categories),
                    customer_id=user.id,
                    assigned_agent_id=random.choice(agents).id if random.random() > 0.3 else None,
                    created_at=created_at,
                    updated_at=created_at + timedelta(hours=random.randint(1, 48))
                )
                tickets.append(ticket)
                session.add(ticket)

            await session.commit()
            print(f"Created {len(sla_levels)} SLA levels, {len(agents)} agents, and {len(tickets)} tickets")

        except Exception as e:
            print(f"Error seeding support data: {e}")
            await session.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(seed_support_data())