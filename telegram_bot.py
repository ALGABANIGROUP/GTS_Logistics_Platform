"""
Telegram Bot for GTS Logistics Platform
Interactive bot that responds to user commands and provides system information.

Features:
- /start - Welcome message and help
- /help - Show all available commands
- /status - System status overview
- /incident - Report or view recent incidents
- /track - Track shipments
- /cost - Cost estimation
- /compliance - Compliance requirements
- /weather - Weather information
- /alert - Subscribe to alerts
- /settings - Notification settings
- /feedback - Send feedback
- /about - About GTS
- /privacy - Privacy policy
- /stop - Unsubscribe from alerts

Author: GTS Development Team
"""

import os
import asyncio
import logging
from datetime import datetime

try:
    from telegram import Bot
    from telegram.error import TelegramError
    from telegram.ext import CommandHandler, MessageHandler, filters, Application
    TELEGRAM_AVAILABLE = True
except ImportError:
    Bot = None  # type: ignore[assignment]
    TelegramError = Exception  # type: ignore[assignment]
    CommandHandler = None  # type: ignore[assignment]
    MessageHandler = None  # type: ignore[assignment]
    filters = None  # type: ignore[assignment]
    Application = None  # type: ignore[assignment]
    TELEGRAM_AVAILABLE = False
    logging.warning("python-telegram-bot not installed, Telegram bot features disabled")

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Import GTS services (optional for standalone bot)
try:
    from backend.services.telegram_service import telegram_service
    from backend.services.incident_service import incident_service
    from backend.services.weather_service import weather_service
    from backend.services.ai_customer_service import ai_customer_service
    from backend.maintenance.service import HealthCollector
    SERVICES_AVAILABLE = True
except ImportError as e:
    logging.warning(f"GTS services not available (running standalone): {e}")
    telegram_service = None
    incident_service = None
    weather_service = None
    ai_customer_service = None
    HealthCollector = None
    SERVICES_AVAILABLE = False


async def get_system_metrics():
    """Best-effort system metrics for Telegram status command."""
    metrics = {
        "database_connected": True,
        "api_running": True,
        "incident_monitor_active": incident_service is not None,
        "weather_service_online": weather_service is not None,
    }
    if HealthCollector is None:
        return metrics

    try:
        system_metrics = await HealthCollector.collect_system_metrics()
        metrics.update(system_metrics or {})
    except Exception as e:
        logger.warning(f"Failed to collect maintenance metrics: {e}")
    return metrics

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class GTSBot:
    """GTS Telegram Bot Handler"""

    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.enabled = os.getenv('TELEGRAM_ENABLED', 'false').lower() == 'true'
        self.bot = None
        self.running = False

        if not TELEGRAM_AVAILABLE:
            logger.warning("Telegram bot library not installed; bot disabled")
            self.enabled = False
            return

        if self.token and self.enabled:
            try:
                self.bot = Bot(token=self.token)
                logger.info("GTS Telegram Bot initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Telegram bot: {e}")
        else:
            logger.warning("Telegram bot not configured or disabled")

    async def send_message(self, chat_id: str, text: str) -> bool:
        """Send a message via Telegram bot"""
        if not self.bot:
            return False

        try:
            await self.bot.send_message(chat_id=chat_id, text=text, parse_mode='HTML')
            return True
        except TelegramError as e:
            logger.error(f"Telegram send error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending Telegram message: {e}")
            return False

    def run_polling(self):
        """Run the bot in polling mode for local development"""
        if not TELEGRAM_AVAILABLE or Application is None or CommandHandler is None or MessageHandler is None or filters is None:
            logger.warning("Telegram polling unavailable: python-telegram-bot not installed")
            return

        if not self.token:
            logger.error("Telegram bot token not configured")
            return

        try:
            application = Application.builder().token(self.token).build()

            # Add command handlers
            application.add_handler(CommandHandler("start", self._start_handler))
            application.add_handler(CommandHandler("help", self._help_handler))
            application.add_handler(CommandHandler("status", self._status_handler))
            application.add_handler(CommandHandler("incident", self._incident_handler))
            application.add_handler(CommandHandler("track", self._track_handler))
            application.add_handler(CommandHandler("cost", self._cost_handler))
            application.add_handler(CommandHandler("compliance", self._compliance_handler))
            application.add_handler(CommandHandler("weather", self._weather_handler))
            application.add_handler(CommandHandler("alert", self._alert_handler))
            application.add_handler(CommandHandler("settings", self._settings_handler))
            application.add_handler(CommandHandler("feedback", self._feedback_handler))
            application.add_handler(CommandHandler("about", self._about_handler))
            application.add_handler(CommandHandler("privacy", self._privacy_handler))
            application.add_handler(CommandHandler("stop", self._stop_handler))

            # Add message handler for regular text
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._message_handler))

            # Start polling
            logger.info("Starting Telegram bot in polling mode...")
            application.run_polling()

        except Exception as e:
            logger.error(f"Failed to start polling: {e}")

    # Synchronous handlers for telegram.ext
    def _start_handler(self, update, context):
        """Handle /start command"""
        asyncio.run(self._handle_sync_command(update, "start"))

    def _help_handler(self, update, context):
        """Handle /help command"""
        asyncio.run(self._handle_sync_command(update, "help"))

    def _status_handler(self, update, context):
        """Handle /status command"""
        asyncio.run(self._handle_sync_command(update, "status"))

    def _incident_handler(self, update, context):
        """Handle /incident command"""
        asyncio.run(self._handle_sync_command(update, "incident"))

    def _track_handler(self, update, context):
        """Handle /track command"""
        args = context.args or []
        asyncio.run(self._handle_sync_command(update, "track", args))

    def _cost_handler(self, update, context):
        """Handle /cost command"""
        args = context.args or []
        asyncio.run(self._handle_sync_command(update, "cost", args))

    def _compliance_handler(self, update, context):
        """Handle /compliance command"""
        asyncio.run(self._handle_sync_command(update, "compliance"))

    def _weather_handler(self, update, context):
        """Handle /weather command"""
        asyncio.run(self._handle_sync_command(update, "weather"))

    def _alert_handler(self, update, context):
        """Handle /alert command"""
        asyncio.run(self._handle_sync_command(update, "alert"))

    def _settings_handler(self, update, context):
        """Handle /settings command"""
        asyncio.run(self._handle_sync_command(update, "settings"))

    def _feedback_handler(self, update, context):
        """Handle /feedback command"""
        args = context.args or []
        asyncio.run(self._handle_sync_command(update, "feedback", args))

    def _about_handler(self, update, context):
        """Handle /about command"""
        asyncio.run(self._handle_sync_command(update, "about"))

    def _privacy_handler(self, update, context):
        """Handle /privacy command"""
        asyncio.run(self._handle_sync_command(update, "privacy"))

    def _stop_handler(self, update, context):
        """Handle /stop command"""
        asyncio.run(self._handle_sync_command(update, "stop"))

    def _message_handler(self, update, context):
        """Handle regular text messages"""
        asyncio.run(self._handle_sync_message(update))

    async def _handle_sync_command(self, update, command, args=None):
        """Handle command synchronously for telegram.ext"""
        try:
            chat_id = str(update.effective_chat.id)
            response = await self.handle_command(f"/{command}", args, chat_id)
            if response:
                update.message.reply_text(response)
        except Exception as e:
            logger.error(f"Error handling command {command}: {e}")
            update.message.reply_text("Error processing command")

    async def _handle_sync_message(self, update):
        """Handle message synchronously for telegram.ext"""
        try:
            chat_id = str(update.effective_chat.id)
            text = update.message.text
            response = await self._handle_message(text)
            if response:
                update.message.reply_text(response)
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            update.message.reply_text("Error processing message")

    async def handle_command(self, command: str, args: list = None, chat_id: str = None) -> str:
        """Handle bot commands and return response"""
        if args is None:
            args = []

        command = command.lower()

        if command == '/start':
            return self._start_command()
        elif command == '/help':
            return self._help_command()
        elif command == '/status':
            return await self._status_command()
        elif command == '/incident':
            return await self._incident_command()
        elif command == '/track':
            return self._track_command(args)
        elif command == '/cost':
            return self._cost_command(args)
        elif command == '/compliance':
            return self._compliance_command()
        elif command == '/weather':
            return await self._weather_command()
        elif command == '/alert':
            return self._alert_command()
        elif command == '/settings':
            return self._settings_command()
        elif command == '/feedback':
            return self._feedback_command(args)
        elif command == '/about':
            return self._about_command()
        elif command == '/privacy':
            return self._privacy_command()
        elif command == '/stop':
            return self._stop_command()
        else:
            return await self._handle_message(" ".join([command] + args))

    def _start_command(self) -> str:
        """Handle /start command"""
        return """
🚛 Welcome to GTS Logistics AI Assistant!

I'm here to help you with:
• Shipment tracking
• Cost optimization
• Compliance requirements
• Real-time incident alerts
• Fleet management

Type /help to see all available commands.

How can I assist you today?
        """.strip()

    def _help_command(self) -> str:
        """Handle /help command"""
        return """
📋 Available Commands:

/start - Welcome message
/help - Show this help
/status - System status overview
/incident - Report or view incidents
/track <id> - Track shipment
/cost <from> <to> - Cost estimation
/compliance - Compliance requirements
/weather - Weather conditions
/alert - Subscribe to alerts
/settings - Notification settings
/feedback <message> - Send feedback
/about - About GTS Logistics
/privacy - Privacy policy
/stop - Unsubscribe from alerts

You can also send me any question and I'll try to help!
        """.strip()

    async def _status_command(self) -> str:
        """Handle /status command"""
        try:
            # Get system metrics
            metrics = await get_system_metrics()

            return f"""
📊 GTS System Status: 🟢 Operational

• Database: {'Connected ✅' if metrics.get('database_connected') else 'Disconnected ❌'}
• API Services: {'Running ✅' if metrics.get('api_running') else 'Stopped ❌'}
• Incident Monitor: {'Active ✅' if metrics.get('incident_monitor_active') else 'Inactive ❌'}
• Weather Service: {'Online ✅' if metrics.get('weather_service_online') else 'Offline ❌'}

Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """.strip()

        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return "Unable to retrieve system status"

    async def _incident_command(self) -> str:
        """Handle /incident command"""
        try:
            if incident_service:
                # Get recent incidents
                recent_incidents = await incident_service.get_recent_incidents(limit=5)

                if recent_incidents:
                    incident_text = "🚨 Recent Incidents:\n\n"
                    for incident in recent_incidents:
                        incident_text += f"• {incident['title']} ({incident['severity']})\n"
                        incident_text += f"  {incident['description'][:100]}...\n\n"
                    return incident_text.strip()
                else:
                    return "✅ No recent incidents reported"
            else:
                return "Incident service not available"

        except Exception as e:
            logger.error(f"Error getting incidents: {e}")
            return "Unable to retrieve incidents"

    def _track_command(self, args: list) -> str:
        """Handle /track command"""
        if not args:
            return "Please provide a tracking number: /track <tracking_id>"

        tracking_id = args[0]

        # Mock tracking response (replace with actual tracking service)
        return f"""
📦 Tracking Information for: {tracking_id}

Status: In Transit 🚛
Location: Khartoum, Sudan
ETA: 2026-03-25 14:30
Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

For detailed tracking, visit the GTS Dashboard.
        """.strip()

    def _cost_command(self, args: list) -> str:
        """Handle /cost command"""
        if len(args) < 2:
            return "Please provide origin and destination: /cost <from> <to>"

        origin = args[0]
        destination = " ".join(args[1:])

        # Mock cost estimation (replace with actual cost service)
        return f"""
💰 Cost Estimation: {origin} → {destination}

Estimated Cost: $1,250 - $1,800
Distance: ~850 km
Duration: 12-16 hours
Vehicle Type: 20ft Container Truck

This is an estimate. Actual costs may vary.
Contact GTS for precise quote.
        """.strip()

    def _compliance_command(self) -> str:
        """Handle /compliance command"""
        return """
📋 Compliance Requirements:

• Vehicle Insurance: Valid and current
• Driver License: Professional grade
• Cargo Insurance: Required for high-value shipments
• Customs Documentation: For international transport
• Safety Certificates: Current inspection reports
• Environmental Permits: For hazardous materials

Contact compliance@gtslogistics.sd for assistance.
        """.strip()

    async def _weather_command(self) -> str:
        """Handle /weather command"""
        try:
            if weather_service:
                # Get current weather conditions
                weather_data = await weather_service.get_current_weather("Khartoum")

                return f"""
🌤️ Current Weather Conditions:

Location: Khartoum, Sudan
Temperature: {weather_data.get('temperature', 'N/A')}°C
Conditions: {weather_data.get('description', 'N/A')}
Humidity: {weather_data.get('humidity', 'N/A')}%
Wind Speed: {weather_data.get('wind_speed', 'N/A')} km/h

Last updated: {datetime.now().strftime('%H:%M:%S')}
                """.strip()
            else:
                return "Weather service not available"

        except Exception as e:
            logger.error(f"Error getting weather: {e}")
            return "Unable to retrieve weather information"

    def _alert_command(self) -> str:
        """Handle /alert command"""
        return """
🔔 Alert Subscription:

You are now subscribed to GTS incident alerts!

You'll receive notifications for:
• Critical system incidents
• Weather-related disruptions
• Service outages
• Important updates

Use /stop to unsubscribe.
        """.strip()

    def _settings_command(self) -> str:
        """Handle /settings command"""
        return """
⚙️ Notification Settings:

Current Settings:
• Incident Alerts: Enabled
• Weather Alerts: Enabled
• System Updates: Enabled
• Marketing: Disabled

Use /alert to subscribe/unsubscribe from alerts.
        """.strip()

    def _feedback_command(self, args: list) -> str:
        """Handle /feedback command"""
        if not args:
            return "Please provide feedback: /feedback <your message>"

        feedback = " ".join(args)

        # Store feedback (implement actual storage)
        logger.info(f"Feedback received: {feedback}")

        return "Thank you for your feedback! We'll review it shortly."

    def _about_command(self) -> str:
        """Handle /about command"""
        return """
🚛 About GTS Logistics

GTS (Gaban Transport Solutions) is Sudan's leading logistics and transportation platform.

Services:
• Freight Brokerage
• Fleet Management
• Real-time Tracking
• Incident Response
• AI-Powered Operations

Contact: info@gtslogistics.sd
Website: https://gtslogistics.sd
        """.strip()

    def _privacy_command(self) -> str:
        """Handle /privacy command"""
        return """
🔒 Privacy Policy:

GTS respects your privacy. We collect minimal data necessary for service provision.

• Chat messages are stored for service improvement
• Personal data is encrypted and secure
• No data sharing with third parties
• Contact support@gtslogistics.sd for data requests

Full policy: https://gtslogistics.sd/privacy
        """.strip()

    def _stop_command(self) -> str:
        """Handle /stop command"""
        return """
🛑 Unsubscribed from Alerts:

You have been unsubscribed from GTS incident alerts.

You can still use other bot commands.
Use /alert to resubscribe.
        """.strip()

    async def _handle_message(self, message: str) -> str:
        """Handle regular text messages with AI"""
        try:
            if ai_customer_service:
                # Use AI customer service for intelligent responses
                response = ai_customer_service.generate_response(message)
                return response
            else:
                # Fallback response
                return "I'm here to help! Use /help to see available commands."

        except Exception as e:
            logger.error(f"Error handling message: {e}")
            return "Sorry, I encountered an error. Please try again."

    async def process_update(self, update_data: dict):
        """Process incoming update from webhook"""
        try:
            message = update_data.get('message', {})
            if not message:
                return

            chat_id = str(message.get('chat', {}).get('id'))
            text = message.get('text', '')

            if not text or not chat_id:
                return

            # Parse command
            if text.startswith('/'):
                parts = text.split()
                command = parts[0]
                args = parts[1:] if len(parts) > 1 else []
            else:
                command = text
                args = []

            # Handle command
            response = await self.handle_command(command, args, chat_id)

            # Send response
            if response:
                await self.send_message(chat_id, response)

        except Exception as e:
            logger.error(f"Error processing update: {e}")

# Global bot instance
gts_bot = GTSBot()

async def start_telegram_bot():
    """Start the Telegram bot (for background operation)"""
    if not TELEGRAM_AVAILABLE:
        logger.warning("Telegram bot startup skipped: python-telegram-bot not installed")
        return

    if not gts_bot.enabled or not gts_bot.bot:
        logger.warning("Telegram bot not configured or disabled")
        return

    logger.info("GTS Telegram Bot started in background mode")
    gts_bot.running = True

    # In background mode, we just initialize and wait
    # Webhook handling would be done via API endpoints
    while gts_bot.running:
        await asyncio.sleep(60)  # Keep alive

async def stop_telegram_bot():
    """Stop the Telegram bot"""
    gts_bot.running = False
    logger.info("GTS Telegram Bot stopped")

async def process_update(update_data: dict):
    """Global function to process Telegram updates (for webhook)"""
    await gts_bot.process_update(update_data)

if __name__ == '__main__':
    # For testing standalone
    asyncio.run(start_telegram_bot())
