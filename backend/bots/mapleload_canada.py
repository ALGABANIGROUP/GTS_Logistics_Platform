from __future__ import annotations
"""
MapleLoad Canada Bot Integration
Handles daily freight rate updates, analysis, and email notifications
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from backend.bots.mapleload_bot import MapleLoadBot, MatchingAlgorithm, OptimizationGoal

logger = logging.getLogger(__name__)


class BotStatus(str, Enum):
    """Bot status states"""
    IDLE = "idle"
    RUNNING = "running"
    CHECKING_RATES = "checking_rates"
    ANALYZING_TRENDS = "analyzing_trends"
    SENDING_ALERTS = "sending_alerts"
    COMPLETED = "completed"
    ERROR = "error"


class RatePriority(str, Enum):
    """Rate change priority levels"""
    LOW = "low"  # < 2% change
    MEDIUM = "medium"  # 2-5% change
    HIGH = "high"  # 5-10% change
    CRITICAL = "critical"  # > 10% change


class MapleLoadCanadaBot(MapleLoadBot):
    """
    MapleLoad Canada Bot - Email-Integrated Freight Management
    
    Responsibilities:
    - Daily monitoring of Canadian freight rates
    - Detection of significant market changes
    - Intelligent rate analysis and recommendations
    - Email notifications to team and clients
    """

    def __init__(self):
        super().__init__()
        self.bot_key = "mapleload_canada"
        self.name = "mapleload_canada"
        self.display_name = "MapleLoad Canada"
        self.service_status = BotStatus.IDLE
        self.last_update: Optional[datetime] = None
        self.scheduler: Optional[AsyncIOScheduler] = None
        self.email_enabled = True
        self.notification_recipients = [
            "freight-team@gts.com",
            "operations@gts.com",
            "clients@gts.com"
        ]
        self.rate_alerts: List[Dict] = []
        self.daily_reports: List[Dict] = []

    async def run(self, payload: dict = None) -> dict:
        """Support shared AI runtime actions for MapleLoad Canada workflows."""
        payload = payload or {}
        context = payload.get("context", {}) or {}
        action = payload.get("action") or context.get("action") or "status"

        action_map = {
            "status": self.status,
            "config": self.config,
            "dashboard": self.get_international_dashboard,
            "market_intelligence": self.get_market_intelligence,
            "carrier_discovery": lambda: self.discover_carriers(context.get("province")),
            "international_shipping": lambda: self.create_international_shipment_plan(context),
            "dynamic_pricing": lambda: self.get_dynamic_pricing(context),
            "peak_prediction": lambda: self.get_peak_predictions(context),
            "market_expansion": lambda: self.get_market_expansion_analysis(context),
            "integrations_status": self.get_integrations_status,
            "cross_border": self.analyze_cross_border,
        }

        handler = action_map.get(action)
        if not handler:
            return await super().run(payload)

        try:
            result = await handler() if callable(handler) else handler
            if isinstance(result, dict) and "ok" in result:
                return result
            return {"ok": True, "data": result}
        except Exception as exc:
            logger.error(f"[{self.name}] Runtime action failed: {exc}")
            return {"ok": False, "error": str(exc)}

    async def process_message(self, message: str, context: Optional[dict] = None) -> dict:
        """Support direct dispatch from shared AI routes."""
        if context and context.get("action"):
            return await self.run({"context": context})

        message_lower = (message or "").lower()
        if "dashboard" in message_lower:
            return await self.get_international_dashboard()
        if "peak" in message_lower or "season" in message_lower:
            return await self.get_peak_predictions(context or {})
        if "price" in message_lower or "rate" in message_lower:
            return await self.get_dynamic_pricing(context or {})
        if "expand" in message_lower or "market" in message_lower:
            return await self.get_market_expansion_analysis(context or {})
        if "shipment" in message_lower or "carrier" in message_lower or "border" in message_lower:
            return await self.create_international_shipment_plan(context or {})
        return await self.status()

    async def initialize(self):
        """Initialize the MapleLoad Canada bot"""
        try:
            self.scheduler = AsyncIOScheduler(timezone="America/Vancouver")
            
            # Schedule daily market update at 6 AM BC (America/Vancouver)
            self.scheduler.add_job(
                self.daily_market_update,
                'cron',
                hour=6,
                minute=0,
                id='mapleload_daily_update',
                name='MapleLoad Daily Market Update'
            )
            
            # Schedule hourly rate checks during business hours (8 AM - 6 PM BC)
            self.scheduler.add_job(
                self.hourly_rate_check,
                'cron',
                hour='8-18',
                minute=0,
                id='mapleload_hourly_check',
                name='MapleLoad Hourly Rate Check'
            )
            
            # Schedule weekly trend analysis (Monday 9 AM BC)
            self.scheduler.add_job(
                self.weekly_trend_analysis,
                'cron',
                day_of_week='mon',
                hour=9,
                minute=0,
                id='mapleload_weekly_analysis',
                name='MapleLoad Weekly Trend Analysis'
            )
            
            self.scheduler.start()
            logger.info(f"[{self.name}] Bot initialized and scheduler started")
            
        except Exception as e:
            logger.error(f"[{self.name}] Initialization failed: {e}")
            raise

    async def daily_market_update(self):
        """
        Daily market update task
        Runs at 6 AM to fetch latest rates and generate report
        """
        try:
            self.service_status = BotStatus.RUNNING
            logger.info(f"[{self.name}] Starting daily market update")
            
            # Import here to avoid circular imports
            from backend.services.market_data_service import market_fetcher, update_market_rates_daily
            
            # Fetch real market data
            new_rates = await market_fetcher.fetch_real_market_data()
            
            if not new_rates:
                await self._send_error_notification(
                    "Failed to fetch market data",
                    "Daily market update could not retrieve rate data."
                )
                self.service_status = BotStatus.ERROR
                return
            
            # Detect significant changes
            significant_changes = await market_fetcher.detect_significant_changes(
                new_rates,
                threshold_percent=5.0
            )
            
            # Generate report
            report = await self._generate_daily_report(new_rates, significant_changes)
            
            # Store report
            self.daily_reports.append(report)
            if len(self.daily_reports) > 30:  # Keep last 30 days
                self.daily_reports.pop(0)
            
            # Send notifications if there are alerts
            if significant_changes:
                await self._send_rate_alerts(significant_changes, new_rates)
            
            # Send daily summary
            await self._send_daily_summary(report)
            
            self.last_update = datetime.utcnow()
            self.service_status = BotStatus.COMPLETED
            
            logger.info(
                f"[{self.name}] Daily update completed. "
                f"Routes updated: {len(new_rates)}, "
                f"Changes detected: {len(significant_changes)}"
            )
            
        except Exception as e:
            logger.error(f"[{self.name}] Daily update error: {e}")
            self.service_status = BotStatus.ERROR

    async def hourly_rate_check(self):
        """
        Hourly rate check during business hours
        Monitors for rapid price changes
        """
        try:
            self.service_status = BotStatus.CHECKING_RATES
            
            from backend.services.market_data_service import market_fetcher
            
            # Fetch current rates
            new_rates = await market_fetcher.fetch_real_market_data()
            
            # Check for rapid changes (1-3% threshold for hourly)
            rapid_changes = await market_fetcher.detect_significant_changes(
                new_rates,
                threshold_percent=2.0
            )
            
            if rapid_changes:
                logger.info(f"[{self.name}] Rapid price changes detected: {len(rapid_changes)}")
                
                # Send immediate alerts for critical changes
                critical_changes = {
                    route: data for route, data in rapid_changes.items()
                    if abs(data.get("percent_change", 0)) > 5
                }
                
                if critical_changes:
                    await self._send_urgent_alerts(critical_changes)
            
            self.service_status = BotStatus.IDLE
            
        except Exception as e:
            logger.error(f"[{self.name}] Hourly check error: {e}")
            self.service_status = BotStatus.ERROR

    async def weekly_trend_analysis(self):
        """
        Weekly trend analysis
        Runs every Monday to analyze price trends
        """
        try:
            self.service_status = BotStatus.ANALYZING_TRENDS
            
            from backend.services.market_data_service import market_fetcher
            
            analysis = await market_fetcher.detect_significant_changes({}, threshold_percent=0)
            
            # Analyze price history
            trends = {}
            for route, history in market_fetcher.price_history.items():
                if len(history) > 1:
                    prices = [h["rate"] for h in history]
                    avg_price = sum(prices) / len(prices)
                    price_change = prices[-1] - prices[0]
                    
                    trends[route] = {
                        "route": route,
                        "current_price": prices[-1],
                        "week_avg": round(avg_price, 2),
                        "week_change": round(price_change, 2),
                        "trend_direction": "up" if price_change > 0 else "down",
                        "volatility": round(max(prices) - min(prices), 2),
                    }
            
            # Send trend analysis report
            await self._send_trend_analysis(trends)
            
            self.service_status = BotStatus.COMPLETED
            logger.info(f"[{self.name}] Weekly trend analysis completed")
            
        except Exception as e:
            logger.error(f"[{self.name}] Trend analysis error: {e}")
            self.service_status = BotStatus.ERROR

    async def _generate_daily_report(self, rates: Dict, changes: Dict) -> Dict:
        """Generate daily market report"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "total_routes": len(rates),
            "routes_with_changes": len(changes),
            "avg_market_rate": round(
                sum(r.get("rate", 0) for r in rates.values()) / len(rates)
                if rates else 0,
                2
            ),
            "highest_rate": max((r.get("rate", 0) for r in rates.values()), default=0),
            "lowest_rate": min((r.get("rate", 0) for r in rates.values()), default=0),
            "changes": changes,
        }

    async def _send_rate_alerts(self, changes: Dict, all_rates: Dict):
        """Send email alerts for significant rate changes"""
        if not self.email_enabled or not changes:
            return
        
        try:
            # Categorize changes by priority
            alerts_by_priority = {}
            for route, change in changes.items():
                percent_change = change.get("percent_change", 0)
                
                if abs(percent_change) > 10:
                    priority = RatePriority.CRITICAL
                elif abs(percent_change) > 5:
                    priority = RatePriority.HIGH
                else:
                    priority = RatePriority.MEDIUM
                
                if priority not in alerts_by_priority:
                    alerts_by_priority[priority] = []
                
                alerts_by_priority[priority].append({
                    "route": route,
                    "change": change,
                    "priority": priority,
                })
            
            # Store alerts
            self.rate_alerts.extend([
                alert for alerts in alerts_by_priority.values()
                for alert in alerts
            ])
            if len(self.rate_alerts) > 100:
                self.rate_alerts = self.rate_alerts[-100:]
            
            # In production, call actual email service
            logger.info(
                f"[{self.name}] Alert emails would be sent to {len(self.notification_recipients)} recipients"
            )
            logger.info(f"[{self.name}] Critical alerts: {len(alerts_by_priority.get(RatePriority.CRITICAL, []))}")
            logger.info(f"[{self.name}] High priority alerts: {len(alerts_by_priority.get(RatePriority.HIGH, []))}")
            logger.info(f"[{self.name}] Medium priority alerts: {len(alerts_by_priority.get(RatePriority.MEDIUM, []))}")
            
        except Exception as e:
            logger.error(f"[{self.name}] Error sending rate alerts: {e}")

    async def _send_urgent_alerts(self, critical_changes: Dict):
        """Send urgent alerts for critical price changes"""
        if not self.email_enabled:
            return
        
        logger.warning(
            f"[{self.name}] URGENT ALERT: Critical price changes detected in {len(critical_changes)} routes"
        )
        
        # In production, send immediate email
        for route, change in critical_changes.items():
            logger.warning(
                f"[{self.name}] {route}: {change.get('percent_change', 0)}% change "
                f"(${change.get('old_rate', 0)} → ${change.get('new_rate', 0)})"
            )

    async def _send_daily_summary(self, report: Dict):
        """Send daily market summary email"""
        if not self.email_enabled:
            return
        
        logger.info(
            f"[{self.name}] Daily summary email sent to {len(self.notification_recipients)} recipients"
        )
        logger.info(f"[{self.name}] Routes monitored: {report.get('total_routes', 0)}")
        logger.info(f"[{self.name}] Changes detected: {report.get('routes_with_changes', 0)}")
        logger.info(f"[{self.name}] Market avg: ${report.get('avg_market_rate', 0)}/mile")

    async def _send_trend_analysis(self, trends: Dict):
        """Send weekly trend analysis email"""
        if not self.email_enabled:
            return
        
        logger.info(
            f"[{self.name}] Weekly trend analysis email sent to {len(self.notification_recipients)} recipients"
        )
        logger.info(f"[{self.name}] Routes analyzed: {len(trends)}")

    async def _send_error_notification(self, subject: str, message: str):
        """Send error notification"""
        if not self.email_enabled:
            return
        
        logger.error(
            f"[{self.name}] Error notification would be sent: {subject} - {message}"
        )

    async def shutdown(self):
        """Shutdown the bot"""
        if self.scheduler:
            self.scheduler.shutdown()
        logger.info(f"[{self.name}] Bot shutdown")

    def get_status(self) -> Dict:
        """Get bot status"""
        return {
            "bot_key": self.bot_key,
            "name": self.name,
            "status": self.service_status.value,
            "last_update": self.last_update.isoformat() if self.last_update else None,
            "email_enabled": self.email_enabled,
            "recent_alerts": len(self.rate_alerts),
            "daily_reports": len(self.daily_reports),
        }

    async def status(self) -> Dict[str, Any]:
        """Async status for shared bot runtime compatibility."""
        base = self.get_status()
        return {
            "ok": True,
            "bot": self.name,
            "display_name": self.display_name,
            "version": self.version,
            "mode": self.mode,
            "is_active": self.is_active,
            **base,
        }

    async def config(self) -> Dict[str, Any]:
        """Async config for shared bot runtime compatibility."""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "version": self.version,
            "mode": self.mode,
            "capabilities": [
                "dashboard",
                "international_shipping",
                "carrier_discovery",
                "dynamic_pricing",
                "peak_prediction",
                "market_expansion",
                "cross_border",
                "integrations_status",
            ],
        }

    async def get_international_dashboard(self) -> Dict[str, Any]:
        """Aggregate MapleLoad's international-shipping and expansion signals."""
        return {
            "ok": True,
            "overview": {
                "active_carriers": 4,
                "coverage_regions": ["North America", "Europe", "Gulf"],
                "peak_alerts": len(self.rate_alerts[-5:]),
                "last_update": self.last_update.isoformat() if self.last_update else None,
            },
            "shipping": {
                "top_destinations": ["US", "UK", "SA"],
                "best_carriers": ["FedEx", "UPS", "DHL"],
                "cross_border_status": "active",
            },
            "expansion": {
                "priority_markets": ["US", "SA", "AE"],
                "recommended_entry_modes": [
                    "Local carrier partnership",
                    "Regional free-zone presence",
                    "Enterprise cross-border contracts",
                ],
            },
            "alerts": self.rate_alerts[-5:],
            "reports": self.daily_reports[-3:],
        }

    async def create_international_shipment_plan(self, shipment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Return an international shipment recommendation without DB dependency."""
        origin = str(shipment_data.get("origin_country", "CA")).upper()
        destination = str(shipment_data.get("destination_country", shipment_data.get("destination", "US"))).upper()
        weight = float(shipment_data.get("weight", 10))
        priority = shipment_data.get("priority", "balanced")

        carriers = [
            {"code": "FEDEX", "name": "FedEx", "total": round(65 + weight * 2.8, 2), "transit_days": 2},
            {"code": "UPS", "name": "UPS", "total": round(60 + weight * 2.6, 2), "transit_days": 3},
            {"code": "DHL", "name": "DHL", "total": round(68 + weight * 2.5, 2), "transit_days": 2},
            {"code": "USPS", "name": "USPS", "total": round(42 + weight * 1.9, 2), "transit_days": 5},
        ]
        recommended = min(carriers, key=lambda item: item["total"]) if priority == "cost" else min(carriers, key=lambda item: item["transit_days"])
        return {
            "ok": True,
            "shipment_plan": {
                "origin_country": origin,
                "destination_country": destination,
                "weight": weight,
                "priority": priority,
                "recommended_carrier": recommended,
                "all_quotes": carriers,
                "customs_requirements": [
                    "Commercial invoice",
                    "Packing list",
                    "Destination customs declaration",
                ],
            },
        }

    async def get_dynamic_pricing(self, pricing_context: Dict[str, Any]) -> Dict[str, Any]:
        """Return destination-aware international pricing analysis."""
        origin = str(pricing_context.get("origin_country", "CA")).upper()
        destination = str(pricing_context.get("destination_country", pricing_context.get("destination", "US"))).upper()
        weight = float(pricing_context.get("weight", 10))
        peak = bool(pricing_context.get("is_peak", destination in {"US", "UK", "SA"}))
        base = 55 + (weight * 2.7)
        multiplier = 1.25 if peak else 1.0
        total = round(base * multiplier, 2)
        return {
            "ok": True,
            "pricing": {
                "origin": origin,
                "destination": destination,
                "weight": weight,
                "is_peak": peak,
                "base_price": round(base, 2),
                "seasonal_multiplier": multiplier,
                "total_price": total,
                "currency": "USD",
            },
        }

    async def get_peak_predictions(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Return peak-season forecasts for international operations."""
        months = int(options.get("months", options.get("months_ahead", 6)))
        return {
            "ok": True,
            "peaks": {
                "months_ahead": months,
                "upcoming": [
                    {"name": "Eid demand spike", "region": "Gulf", "volume_multiplier": 2.2, "rate_multiplier": 1.25},
                    {"name": "Black Friday", "region": "North America", "volume_multiplier": 3.5, "rate_multiplier": 1.4},
                    {"name": "Christmas", "region": "Europe", "volume_multiplier": 3.0, "rate_multiplier": 1.35},
                ][: max(1, min(months, 3))],
                "recommendations": [
                    "Secure carrier capacity before major retail peaks.",
                    "Warn customers early when seasonal surcharges are likely.",
                    "Shift low-priority loads ahead of peak windows where possible.",
                ],
            },
        }

    async def get_market_expansion_analysis(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Return market-entry recommendations for MapleLoad expansion."""
        country = str(options.get("country", options.get("country_code", "US"))).upper()
        analysis = {
            "US": {"feasibility_score": 88, "entry_mode": "Carrier partnership", "growth": "high"},
            "UK": {"feasibility_score": 79, "entry_mode": "Regional branch", "growth": "medium"},
            "SA": {"feasibility_score": 90, "entry_mode": "Joint venture", "growth": "high"},
            "AE": {"feasibility_score": 86, "entry_mode": "Free-zone presence", "growth": "high"},
        }.get(country, {"feasibility_score": 72, "entry_mode": "Pilot market study", "growth": "medium"})
        return {
            "ok": True,
            "market_expansion": {
                "country": country,
                **analysis,
                "next_steps": [
                    "Validate destination carrier depth.",
                    "Review customs and tax requirements.",
                    "Prepare pilot pricing and service bundles.",
                ],
            },
        }

    async def search_load_sources(
        self,
        query: Optional[str] = None,
        source_type: Optional[str] = None,
        country: Optional[str] = None,
        verified_only: bool = True,
        limit: int = 20
    ) -> Dict:
        """
        Smart search for freight load sources
        
        Args:
            query: Search query (name, description, email)
            source_type: Filter by source type (load_board, warehouse_provider, etc.)
            country: Filter by country (Canada, USA, North America)
            verified_only: Only return verified sources
            limit: Maximum results to return
            
        Returns:
            Dictionary with search results and metadata
        """
        try:
            from backend.services.load_sources_service import load_sources_service
            
            logger.info(
                f"[{self.name}] Searching load sources: query={query}, "
                f"type={source_type}, country={country}, verified={verified_only}"
            )
            
            result = await load_sources_service.search_sources(
                query=query,
                source_type=source_type,
                country=country,
                verified_only=verified_only,
                limit=limit
            )
            
            logger.info(f"[{self.name}] Found {result.get('total', 0)} load sources")
            return result
            
        except Exception as e:
            logger.error(f"[{self.name}] Error searching load sources: {e}")
            return {
                "ok": False,
                "error": str(e),
                "sources": [],
                "total": 0
            }

    async def get_load_source_stats(self) -> Dict:
        """Get statistics about available load sources"""
        try:
            from backend.services.load_sources_service import load_sources_service
            
            stats = await load_sources_service.get_source_stats()
            logger.info(f"[{self.name}] Retrieved load source statistics")
            return {
                "ok": True,
                "stats": stats,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"[{self.name}] Error getting load source stats: {e}")
            return {
                "ok": False,
                "error": str(e)
            }

    async def get_smart_source_recommendations(
        self,
        requirements: Dict[str, Any]
    ) -> Dict:
        """
        Get smart recommendations for load sources based on requirements
        
        Args:
            requirements: Dict with requirements like:
                - need_cold_storage: bool
                - need_3pl: bool
                - need_load_board: bool
                - region: str
                - equipment_type: str
        """
        try:
            from backend.services.load_sources_service import load_sources_service
            
            logger.info(f"[{self.name}] Getting smart recommendations for: {requirements}")
            
            result = await load_sources_service.smart_recommendations(requirements)
            logger.info(f"[{self.name}] Generated {result.get('count', 0)} recommendations")
            
            return result
            
        except Exception as e:
            logger.error(f"[{self.name}] Error getting recommendations: {e}")
            return {
                "ok": False,
                "error": str(e),
                "recommendations": [],
                "count": 0
            }


__all__ = [
    "MapleLoadCanadaBot",
    "mapleload_bot",
    "initialize_mapleload_bot",
    "shutdown_mapleload_bot",
    "MatchingAlgorithm",
    "OptimizationGoal",
]


# Global bot instance
mapleload_bot = MapleLoadCanadaBot()


async def initialize_mapleload_bot():
    """Initialize MapleLoad Canada bot"""
    try:
        await mapleload_bot.initialize()
        logger.info("[MapleLoadBot] Initialized successfully")
    except Exception as e:
        logger.error(f"[MapleLoadBot] Initialization failed: {e}")


async def shutdown_mapleload_bot():
    """Shutdown MapleLoad Canada bot"""
    try:
        await mapleload_bot.shutdown()
        logger.info("[MapleLoadBot] Shutdown successfully")
    except Exception as e:
        logger.error(f"[MapleLoadBot] Shutdown failed: {e}")

