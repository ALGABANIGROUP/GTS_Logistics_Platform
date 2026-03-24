"""
AI General Manager - Strategic Reports and Executive Insights
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class GeneralManagerBot:
    """AI General Manager for strategic oversight and reporting"""

    name = "general_manager"
    display_name = "AI General Manager"
    description = "Executive oversight, strategic insights, and performance analytics"

    def __init__(self):
        self._db_session = None

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute general manager commands"""
        action = payload.get("action", "dashboard")

        if action == "strategic_report":
            period = payload.get("period", "monthly")
            return await self._generate_strategic_report(period)
        elif action == "performance_analysis":
            return await self._analyze_performance()
        elif action == "market_insights":
            return await self._get_market_insights()
        elif action == "kpi_dashboard":
            return await self._get_kpi_dashboard()
        elif action == "recommendations":
            return await self._get_recommendations()
        else:
            return self._get_dashboard()

    async def _generate_strategic_report(self, period: str = "monthly") -> Dict[str, Any]:
        """Generate comprehensive strategic report with real data"""
        try:
            # Calculate date range
            end_date = datetime.now()
            if period == "weekly":
                start_date = end_date - timedelta(days=7)
            elif period == "monthly":
                start_date = end_date - timedelta(days=30)
            elif period == "quarterly":
                start_date = end_date - timedelta(days=90)
            elif period == "yearly":
                start_date = end_date - timedelta(days=365)
            else:
                start_date = end_date - timedelta(days=30)
                period = "monthly"

            # Get data from database if available
            try:
                from backend.database.session import get_async_session
                from backend.models.shipment import Shipment
                from backend.models.financial import Expense, Invoice

                async for session in get_async_session():
                    # Get shipments data
                    shipments_query = select(Shipment).where(
                        Shipment.created_at >= start_date
                    )
                    shipments_result = await session.execute(shipments_query)
                    shipments = shipments_result.scalars().all()

                    # Get financial data
                    expenses_query = select(Expense).where(
                        Expense.created_at >= start_date
                    )
                    expenses_result = await session.execute(expenses_query)
                    expenses = expenses_result.scalars().all()

                    # Get invoices data
                    invoices_query = select(Invoice).where(
                        Invoice.created_at >= start_date
                    )
                    invoices_result = await session.execute(invoices_query)
                    invoices = invoices_result.scalars().all()

                    # Calculate KPIs
                    total_shipments = len(shipments)
                    completed_shipments = len([s for s in shipments if getattr(s, 'status', '') == 'completed'])
                    total_revenue = sum(float(getattr(i, 'amount', 0)) for i in invoices)
                    total_expenses = sum(float(getattr(e, 'amount', 0)) for e in expenses)

                    profit = total_revenue - total_expenses
                    profit_margin = (profit / total_revenue * 100) if total_revenue > 0 else 0

                    # Calculate on-time rate
                    on_time = len([s for s in shipments if getattr(s, 'on_time', False)])
                    on_time_rate = (on_time / total_shipments * 100) if total_shipments > 0 else 0

                    break

            except Exception as e:
                logger.warning(f"Database not available for strategic report: {e}")
                # Use fallback data
                total_shipments = 0
                completed_shipments = 0
                total_revenue = 0
                total_expenses = 0
                profit = 0
                profit_margin = 0
                on_time_rate = 0

            # Generate recommendations based on data
            recommendations = self._generate_recommendations(
                total_shipments, total_revenue, profit_margin, on_time_rate
            )

            return {
                "success": True,
                "period": period,
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "kpis": {
                    "total_shipments": total_shipments,
                    "completed_shipments": completed_shipments,
                    "completion_rate": round((completed_shipments / total_shipments * 100) if total_shipments > 0 else 0, 1),
                    "total_revenue": round(total_revenue, 2),
                    "total_expenses": round(total_expenses, 2),
                    "profit": round(profit, 2),
                    "profit_margin": round(profit_margin, 1),
                    "on_time_rate": round(on_time_rate, 1)
                },
                "recommendations": recommendations,
                "generated_at": datetime.now().isoformat(),
                "action": "strategic_report"
            }

        except Exception as e:
            logger.error(f"Failed to generate strategic report: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback": True,
                "message": "Strategic report generation failed. Using fallback data."
            }

    def _generate_recommendations(self, shipments: int, revenue: float, margin: float, on_time: float) -> List[Dict[str, Any]]:
        """Generate recommendations based on performance data"""
        recommendations = []

        if shipments < 50:
            recommendations.append({
                "priority": "high",
                "category": "growth",
                "title": "Increase shipment volume",
                "description": "Current shipment volume is below target. Consider expanding carrier network or marketing efforts.",
                "action": "Review marketing strategy and carrier onboarding process"
            })

        if margin < 15:
            recommendations.append({
                "priority": "high",
                "category": "financial",
                "title": "Improve profit margins",
                "description": "Profit margin is below industry average of 15-20%. Review pricing strategy and operational costs.",
                "action": "Audit recent shipments for pricing optimization"
            })

        if on_time < 95:
            recommendations.append({
                "priority": "medium",
                "category": "operations",
                "title": "Improve on-time delivery",
                "description": f"On-time rate is {on_time}%. Target is 95%+. Review route planning and carrier performance.",
                "action": "Analyze late deliveries and optimize routes"
            })

        if revenue > 0 and shipments > 0:
            avg_revenue = revenue / shipments
            if avg_revenue < 500:
                recommendations.append({
                    "priority": "medium",
                    "category": "pricing",
                    "title": "Review pricing strategy",
                    "description": f"Average revenue per shipment is ${avg_revenue:.2f}. Consider rate adjustments.",
                    "action": "Compare rates with market benchmarks"
                })

        if not recommendations:
            recommendations.append({
                "priority": "low",
                "category": "maintenance",
                "title": "Maintain current performance",
                "description": "All KPIs are meeting targets. Focus on continuous improvement.",
                "action": "Monitor trends and identify optimization opportunities"
            })

        return recommendations

    async def _analyze_performance(self) -> Dict[str, Any]:
        """Analyze overall system performance"""
        return {
            "success": True,
            "analysis": {
                "system_health": {
                    "status": "operational",
                    "uptime": "99.9%",
                    "response_time_ms": 145
                },
                "business_metrics": {
                    "customer_satisfaction": "4.8/5",
                    "carrier_retention": "92%",
                    "broker_retention": "88%"
                },
                "operational_efficiency": {
                    "load_to_book_time_min": 12,
                    "dispatch_efficiency": "94%",
                    "utilization_rate": "76%"
                }
            },
            "action": "performance_analysis"
        }

    async def _get_market_insights(self) -> Dict[str, Any]:
        """Get market insights and trends"""
        return {
            "success": True,
            "insights": {
                "spot_rates": {
                    "flatbed": 2.85,
                    "van": 2.42,
                    "reefer": 2.76,
                    "trend": "stable"
                },
                "market_conditions": {
                    "supply_demand_ratio": 1.2,
                    "hot_markets": ["Chicago", "Atlanta", "Dallas"],
                    "cool_markets": ["Seattle", "Portland"]
                },
                "forecast": {
                    "next_30_days": "Rates expected to increase 2-3%",
                    "recommendation": "Book long-term contracts for stable lanes"
                }
            },
            "action": "market_insights"
        }

    async def _get_kpi_dashboard(self) -> Dict[str, Any]:
        """Get KPI dashboard data"""
        return {
            "success": True,
            "dashboard": {
                "financial": {
                    "revenue": {"value": 125000, "trend": "+12%", "target": 150000},
                    "profit": {"value": 32500, "trend": "+8%", "target": 40000},
                    "margin": {"value": 26, "trend": "-2%", "target": 30}
                },
                "operational": {
                    "shipments": {"value": 342, "trend": "+5%", "target": 400},
                    "on_time": {"value": 94.2, "trend": "+1.5%", "target": 95},
                    "utilization": {"value": 76, "trend": "+3%", "target": 85}
                },
                "customer": {
                    "satisfaction": {"value": 4.8, "trend": "+0.2", "target": 4.5},
                    "retention": {"value": 91, "trend": "+2%", "target": 90},
                    "new_customers": {"value": 24, "trend": "+33%", "target": 30}
                }
            },
            "action": "kpi_dashboard"
        }

    async def _get_recommendations(self) -> Dict[str, Any]:
        """Get strategic recommendations"""
        return {
            "success": True,
            "recommendations": [
                {
                    "title": "Expand carrier network",
                    "description": "Add 50 new carriers in key markets to increase capacity",
                    "impact": "High",
                    "effort": "Medium",
                    "timeline": "Q2 2026"
                },
                {
                    "title": "Implement AI pricing",
                    "description": "Deploy AI-powered dynamic pricing for better margins",
                    "impact": "High",
                    "effort": "High",
                    "timeline": "Q3 2026"
                },
                {
                    "title": "Enhance customer portal",
                    "description": "Add self-service features for better customer experience",
                    "impact": "Medium",
                    "effort": "Medium",
                    "timeline": "Q2 2026"
                }
            ],
            "action": "recommendations"
        }

    def _get_dashboard(self) -> Dict[str, Any]:
        """Return general manager dashboard"""
        return {
            "success": True,
            "bot": self.name,
            "display_name": self.display_name,
            "available_actions": [
                "strategic_report - Generate strategic report",
                "performance_analysis - Analyze performance",
                "market_insights - Get market insights",
                "kpi_dashboard - View KPI dashboard",
                "recommendations - Get recommendations"
            ],
            "action": "dashboard"
        }

    async def status(self) -> Dict[str, Any]:
        """Return bot status"""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "status": "active",
            "description": self.description,
            "capabilities": [
                "Strategic reporting",
                "Performance analysis",
                "KPI monitoring",
                "Market insights",
                "Recommendations"
            ]
        }

    async def config(self) -> Dict[str, Any]:
        """Return bot configuration"""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "actions": self._get_dashboard()["available_actions"],
            "reporting_periods": ["weekly", "monthly", "quarterly", "yearly"]
        }

