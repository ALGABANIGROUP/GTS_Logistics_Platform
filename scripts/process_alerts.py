#!/usr/bin/env python3
"""
Alert processing script for incident notifications
"""

import asyncio
import sys
import os
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import json

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.incident_tracker import IncidentTracker
from backend.services.telegram_service import telegram_service
from backend.services.chat_service import chat_service

async def send_email_alert(incident, recipient):
    """Send email alert for critical incident"""
    try:
        # Email configuration from environment
        smtp_host = os.getenv('SMTP_HOST', 'mail.gabanilogistics.com')
        smtp_port = int(os.getenv('SMTP_PORT', '465'))
        smtp_user = os.getenv('SMTP_USER', 'no-reply@gabanilogistics.com')
        smtp_pass = os.getenv('SMTP_PASSWORD', 'Y84@m90.2026')
        smtp_from = os.getenv('SMTP_FROM', 'no-reply@gabanilogistics.com')

        # Create message
        msg = MIMEMultipart()
        msg['From'] = smtp_from
        msg['To'] = recipient
        msg['Subject'] = f"🚨 CRITICAL INCIDENT: {incident.title}"

        body = f"""
CRITICAL INCIDENT ALERT

Incident ID: {incident.id}
Service: {incident.service}
Severity: {incident.severity.value.upper()}
Status: {incident.status.value.upper()}

Description: {incident.description}

Error: {incident.error_message}

Affected Users: {incident.affected_users}

Detected: {incident.detected_at.isoformat()}

Please investigate immediately!

GTS Incident Response System
        """.strip()

        msg.attach(MIMEText(body, 'plain'))

        # Send email
        server = smtplib.SMTP_SSL(smtp_host, smtp_port)
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()

        print(f"✅ Email alert sent to {recipient}")

    except Exception as e:
        print(f"❌ Failed to send email alert: {e}")

async def send_slack_alert(incident, webhook_url):
    """Send Slack alert for incident"""
    try:
        payload = {
            "text": f"🚨 *CRITICAL INCIDENT*\n\n*{incident.title}*\nService: {incident.service}\nSeverity: {incident.severity.value.upper()}\nStatus: {incident.status.value.upper()}\nAffected Users: {incident.affected_users}",
            "attachments": [
                {
                    "color": "danger",
                    "fields": [
                        {"title": "Incident ID", "value": incident.id, "short": True},
                        {"title": "Detected", "value": incident.detected_at.isoformat(), "short": True}
                    ]
                }
            ]
        }

        response = requests.post(webhook_url, json=payload)
        if response.status_code == 200:
            print("✅ Slack alert sent")
        else:
            print(f"❌ Slack alert failed: {response.status_code}")

    except Exception as e:
        print(f"❌ Failed to send Slack alert: {e}")

async def send_telegram_alert(incident):
    """Send Telegram alert for incident"""
    try:
        # Convert incident object to dictionary for Telegram service
        incident_data = {
            'id': incident.id,
            'severity': incident.severity.value,
            'service': incident.service,
            'error_message': incident.error_message,
            'timestamp': incident.detected_at.isoformat() if hasattr(incident, 'detected_at') else 'Unknown',
            'title': incident.title if hasattr(incident, 'title') else f'Incident {incident.id}',
            'status': incident.status.value if hasattr(incident, 'status') else 'unknown',
            'affected_users': incident.affected_users if hasattr(incident, 'affected_users') else 'Unknown'
        }

        success = telegram_service.send_incident_alert(incident_data)
        if success:
            print("✅ Telegram alert sent")
        else:
            print("❌ Telegram alert failed")

    except Exception as e:
        print(f"❌ Failed to send Telegram alert: {e}")

async def send_dashboard_alert(incident):
    """Send dashboard chat alert for incident"""
    try:
        # Convert incident object to dictionary for chat service
        incident_data = {
            'id': incident.id,
            'severity': incident.severity.value,
            'service': incident.service,
            'error_message': incident.error_message[:200] + '...' if len(incident.error_message) > 200 else incident.error_message,
            'timestamp': incident.detected_at.isoformat() if hasattr(incident, 'detected_at') else 'Unknown'
        }

        # Send to incidents channel
        result = chat_service.send_incident_notification(incident_data)
        print("✅ Dashboard alert sent to #incidents channel")

    except Exception as e:
        print(f"❌ Failed to send dashboard alert: {e}")

async def process_alerts():
    """
    Process and send alerts for new critical incidents
    """
    tracker = IncidentTracker()

    print("📢 Alert processor started...")

    # Get alert recipients from environment
    alert_email = os.getenv('ALERT_EMAIL')
    slack_webhook = os.getenv('SLACK_WEBHOOK_URL')

    print("📢 Alert processor started...")
    print(f"📧 Email alerts: {'✅' if alert_email else '❌'}")
    print(f"💬 Slack alerts: {'✅' if slack_webhook else '❌'}")
    print(f"📱 Telegram alerts: {'✅' if telegram_service.is_configured() else '❌'}")
    print(f"💬 Dashboard alerts: ✅ (always enabled)")

    if not alert_email and not slack_webhook and not telegram_service.is_configured():
        print("⚠️  No external alert destinations configured (but dashboard alerts are active)")

    try:
        while True:
            # Check for new critical incidents
            active_incidents = tracker.get_active_incidents()

            for incident in active_incidents:
                if incident.severity.value == 'critical':
                    print(f"🚨 Processing alert for incident: {incident.id}")

                    # Send email alert
                    if alert_email:
                        await send_email_alert(incident, alert_email)

                    # Send Slack alert
                    if slack_webhook:
                        await send_slack_alert(incident, slack_webhook)

                    # Send Telegram alert
                    if telegram_service.is_configured():
                        await send_telegram_alert(incident)

                    # Send Dashboard alert (always active)
                    await send_dashboard_alert(incident)

                    # Mark as alerted (you might want to add this to the incident model)
                    # incident.alerted = True

            # Wait before checking again
            await asyncio.sleep(60)  # Check every minute

    except KeyboardInterrupt:
        print("\n👋 Alert processor stopped")
    except Exception as e:
        print(f"❌ Alert processor error: {e}")

if __name__ == "__main__":
    asyncio.run(process_alerts())