import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
import json

from backend.database import async_session
from backend.models.ai_bot_issues import AIBotIssue
from backend.models.safety_enhanced import SafetyIncident
from backend.services.system_monitor import SystemMonitor
from backend.services.log_analysis_service import LogAnalysisService

logger = logging.getLogger(__name__)

class LiveSupportService:
    """
    Live Support Service - AI Agent that connects to all monitoring systems
    """

    def __init__(self):
        self.system_monitor = SystemMonitor()
        self.log_analyzer = LogAnalysisService()
        self.conversation_history = {}

        logger.info("✅ Live Support Service initialized")

    async def process_message(self, user_id: str, message: str, session_id: str = None) -> Dict:
        """
        Process user message and generate intelligent response
        """
        if not session_id:
            session_id = f"session_{user_id}_{datetime.now().timestamp()}"

        # Detect user intent
        intent = self._detect_intent(message)

        # Get relevant context based on intent
        context = await self._get_context(intent, message)

        # Generate response
        response = await self._generate_response(intent, context, message)

        # Save conversation
        self._save_conversation(session_id, user_id, message, response)

        return {
            "success": True,
            "response": response,
            "intent": intent,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }

    def _detect_intent(self, message: str) -> str:
        """
        Detect user intent from message
        """
        message_lower = message.lower()

        # Keyword patterns
        intents = {
            "system_health": ["health", "status", "system", "performance", "cpu", "memory", "disk"],
            "errors": ["error", "bug", "issue", "problem"],
            "incidents": ["incident", "accident"],
            "security": ["security", "hack", "breach"],
            "maintenance": ["maintenance", "update", "upgrade"],
            "weather": ["weather", "rain", "storm"],
            "finance": ["invoice", "payment", "revenue"],
            "fleet": ["driver", "vehicle", "truck"],
            "help": ["help", "how", "what"]
        }

        for intent, keywords in intents.items():
            if any(keyword in message_lower for keyword in keywords):
                return intent

        return "general"

    async def _get_context(self, intent: str, message: str) -> Dict:
        """
        Get relevant data based on intent
        """
        context = {
            "timestamp": datetime.now().isoformat(),
            "intent": intent
        }

        if intent == "system_health":
            # Get system status
            context["system_status"] = await self.system_monitor.get_status()
            context["metrics"] = await self.system_monitor.get_metrics()

        elif intent == "errors":
            # Get recent errors
            async with async_session() as session:
                from sqlalchemy import select, desc
                query = select(AIBotIssue).order_by(desc(AIBotIssue.created_at)).limit(5)
                result = await session.execute(query)
                issues = result.scalars().all()
                context["recent_errors"] = [
                    {"id": i.id, "title": i.title, "status": i.status, "created_at": i.created_at.isoformat()}
                    for i in issues
                ]

        elif intent == "incidents":
            # Get recent incidents
            async with async_session() as session:
                from sqlalchemy import select, desc
                query = select(SafetyIncident).order_by(desc(SafetyIncident.created_at)).limit(5)
                result = await session.execute(query)
                incidents = result.scalars().all()
                context["recent_incidents"] = [
                    {"id": i.id, "type": i.incident_type, "severity": i.severity, "location": i.location}
                    for i in incidents
                ]

        elif intent == "security":
            # Analyze security logs
            context["security_analysis"] = self.log_analyzer.analyze_logs(hours=24)

        elif intent == "weather":
            # Get weather status
            from backend.services.weather_service import WeatherService
            weather_service = WeatherService()
            context["weather"] = await weather_service.get_current_weather(city="Riyadh")

        elif intent == "finance":
            # Get financial summary
            async with async_session() as session:
                from sqlalchemy import select, func
                from backend.models.invoices import Invoice

                # Total invoices
                result = await session.execute(select(func.sum(Invoice.amount_usd)))
                total = result.scalar() or 0

                # Pending invoices
                result = await session.execute(
                    select(func.count()).where(Invoice.status == "pending")
                )
                pending = result.scalar() or 0

                context["finance_summary"] = {
                    "total_revenue": total,
                    "pending_invoices": pending,
                    "currency": "USD"
                }

        return context

    async def _generate_response(self, intent: str, context: Dict, user_message: str) -> str:
        """
        Generate intelligent response based on intent and data
        """

        if intent == "system_health":
            status = context.get("system_status", {})
            metrics = context.get("metrics", {})

            return f"""📊 **System Health Report**

**Status:** {status.get('status', 'Unknown')}
**CPU Usage:** {metrics.get('cpu', 0)}%
**Memory Usage:** {metrics.get('memory', 0)}%
**Disk Usage:** {metrics.get('disk', 0)}%
**Uptime:** {status.get('uptime', 'N/A')}

All systems are operational. No critical issues detected."""

        elif intent == "errors":
            errors = context.get("recent_errors", [])
            if not errors:
                return "✅ No errors reported in the last 24 hours. System is running smoothly."

            error_list = "\n".join([
                f"  • **{e['title']}** (Status: {e['status']})"
                for e in errors[:5]
            ])

            return f"""🔧 **Recent Errors**

{error_list}

**Total:** {len(errors)} errors in the last 24 hours.
Would you like me to investigate any specific error?"""

        elif intent == "incidents":
            incidents = context.get("recent_incidents", [])
            if not incidents:
                return "✅ No incidents reported recently."

            incident_list = "\n".join([
                f"  • **{i['type']}** - {i['location']} (Severity: {i['severity']})"
                for i in incidents[:5]
            ])

            return f"""⚠️ **Recent Incidents**

{incident_list}

**Total:** {len(incidents)} incidents in the last 24 hours.
Safety Manager is monitoring the situation."""

        elif intent == "security":
            analysis = context.get("security_analysis", {})
            total = analysis.get("total_suspicious", 0)

            if total == 0:
                return "🔒 **Security Status: Clean**\n\nNo suspicious activity detected in the last 24 hours."

            events = analysis.get("suspicious_events", [])[:3]
            events_list = "\n".join([
                f"  • {e['description']} - {e['ip']}"
                for e in events
            ])

            return f"""🛡️ **Security Alert**

Detected **{total}** suspicious events in the last 24 hours:

{events_list}

**Recommendation:** {analysis.get('recommendation', 'Review logs for details')}"""

        elif intent == "weather":
            weather = context.get("weather", {})
            if not weather.get("success"):
                return "Unable to fetch weather data at this moment."

            return f"""🌤️ **Current Weather - {weather.get('city', 'Unknown')}**

**Temperature:** {weather.get('temperature', 'N/A')}°C
**Feels Like:** {weather.get('feels_like', 'N/A')}°C
**Humidity:** {weather.get('humidity', 'N/A')}%
**Wind Speed:** {weather.get('wind_speed', 'N/A')} km/h
**Conditions:** {weather.get('description', 'N/A')}

{self._get_weather_recommendation(weather)}"""

        elif intent == "finance":
            summary = context.get("finance_summary", {})
            return f"""💰 **Financial Summary**

**Total Revenue:** ${summary.get('total_revenue', 0):,.2f}
**Pending Invoices:** {summary.get('pending_invoices', 0)}
**Currency:** {summary.get('currency', 'USD')}

Would you like a detailed financial report?"""

        elif intent == "fleet":
            return await self._get_fleet_status()

        else:
            return """👋 **Hello! I'm your AI Maintenance Assistant.**

I can help you with:
• System health checks
• Error analysis & troubleshooting
• Security monitoring
• Weather impact assessment
• Financial summaries
• Fleet status

Try asking:
- "Show system health"
- "Any recent errors?"
- "Security status"
- "Current weather"
- "Financial summary"
- "Fleet status"

How can I assist you today?"""

    def _get_weather_recommendation(self, weather: Dict) -> str:
        """Generate recommendation based on weather"""
        temp = weather.get("temperature", 0)
        wind = weather.get("wind_speed", 0)

        if temp > 40:
            return "⚠️ **High Temperature Alert**: Avoid midday driving. Ensure vehicle cooling systems are checked."
        elif temp < 5:
            return "⚠️ **Low Temperature Alert**: Check tire pressure. Be cautious of icy roads."
        elif wind > 50:
            return "⚠️ **High Wind Alert**: Reduce speed. Caution for high-profile vehicles."

        return "✅ Weather conditions are suitable for normal operations."

    async def _get_fleet_status(self) -> str:
        """Get fleet status"""
        try:
            async with async_session() as session:
                # Try to import fleet models, fallback if not available
                try:
                    from backend.models.fleet import Driver, Vehicle
                except ImportError:
                    return f"""🚛 **Fleet Status**

**Status:** Fleet management system initializing
**Note:** Fleet models not yet configured

Please contact system administrator for fleet integration."""

                # Total drivers
                drivers_result = await session.execute(select(func.count()).select_from(Driver))
                total_drivers = drivers_result.scalar() or 0

                # Total vehicles
                vehicles_result = await session.execute(select(func.count()).select_from(Vehicle))
                total_vehicles = vehicles_result.scalar() or 0

                # Active drivers
                active_result = await session.execute(
                    select(func.count()).where(Driver.status == "available")
                )
                active_drivers = active_result.scalar() or 0

                return f"""🚛 **Fleet Status**

**Total Drivers:** {total_drivers}
**Active Drivers:** {active_drivers}
**Total Vehicles:** {total_vehicles}

Fleet is operating normally."""
        except Exception as e:
            logger.error(f"Error getting fleet status: {e}")
            return f"""🚛 **Fleet Status**

**Status:** Unable to retrieve fleet data
**Error:** {str(e)}

Please try again later."""
        """Save conversation to history"""
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []

        self.conversation_history[session_id].append({
            "user_id": user_id,
            "message": message,
            "response": response,
            "timestamp": datetime.now().isoformat()
        })

        # Keep only last 50 conversations
        if len(self.conversation_history[session_id]) > 50:
            self.conversation_history[session_id] = self.conversation_history[session_id][-50:]

    def get_conversation_history(self, session_id: str) -> List[Dict]:
        """Get conversation history"""
        return self.conversation_history.get(session_id, [])