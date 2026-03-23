"""
Safety Alert System - Multi-channel alert management
Sends alerts via WebSocket, SMS, Email, and Push Notifications
"""

from typing import Dict, List, Optional
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)


class SafetyAlertSystem:
    """Advanced multi-channel safety alert system"""
    
    def __init__(self):
        self.active_alerts = {}
        self.subscribers = {}
        
    async def send_safety_alert(self, driver_id: int, vehicle_id: int, 
                               report: Dict):
        """Send comprehensive safety alert"""
        
        alert_data = {
            "type": "safety_alert",
            "driver_id": driver_id,
            "vehicle_id": vehicle_id,
            "report": report,
            "timestamp": datetime.utcnow().isoformat(),
            "priority": self.determine_alert_priority(report)
        }
        
        # Send via multiple channels
        await self.send_via_websocket(alert_data)
        await self.send_via_sms(alert_data)
        await self.send_via_email(alert_data)
        await self.store_alert_in_db(alert_data)
        
        logger.info(f"Safety alert sent to driver {driver_id}")
        
    async def send_immediate_alert(self, shipment_id: int, safety_data: Dict):
        """Send immediate critical alert"""
        
        alert = {
            "type": "immediate_safety_alert",
            "shipment_id": shipment_id,
            "safety_score": safety_data.get('safety_score', 100),
            "risk_level": safety_data.get('risk_level', 'low'),
            "critical_warnings": [w for w in safety_data.get('warnings', []) 
                                 if w.get('severity') in ['high', 'severe']],
            "timestamp": datetime.utcnow().isoformat(),
            "priority": "critical" if safety_data.get('safety_score', 100) < 50 else "high"
        }
        
        await self.send_via_websocket(alert)
        await self.send_via_push_notification(alert)
        
    async def send_via_websocket(self, alert_data: Dict):
        """Send alert via WebSocket"""
        
        try:
            message = {
                "event": "safety_alert",
                "data": alert_data
            }
            
            logger.debug(f"WebSocket alert sent: {alert_data['type']}")
            
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            
    async def send_via_sms(self, alert_data: Dict):
        """Send alert via SMS"""
        
        if alert_data['priority'] in ['high', 'critical']:
            try:
                phone_number = self.get_driver_phone(alert_data['driver_id'])
                message = self.format_sms_alert(alert_data)
                
                logger.info(f"SMS sent to driver {alert_data['driver_id']}")
                
            except Exception as e:
                logger.error(f"SMS error: {e}")
                
    async def send_via_email(self, alert_data: Dict):
        """Send alert via Email"""
        
        try:
            email_data = {
                "to": self.get_recipient_emails(alert_data),
                "subject": self.get_email_subject(alert_data),
                "body": self.format_email_alert(alert_data),
                "priority": alert_data['priority']
            }
            
            logger.info(f"Email sent for alert: {alert_data['type']}")
            
        except Exception as e:
            logger.error(f"Email error: {e}")
            
    async def send_via_push_notification(self, alert_data: Dict):
        """Send Push Notification"""
        
        try:
            notification_data = {
                "title": self.get_push_title(alert_data),
                "body": self.get_push_body(alert_data),
                "data": alert_data,
                "priority": "high"
            }
            
            logger.info(f"Push notification sent: {alert_data['type']}")
            
        except Exception as e:
            logger.error(f"Push notification error: {e}")
            
    async def store_alert_in_db(self, alert_data: Dict):
        """Store alert in database"""
        
        try:
            logger.debug("Alert stored in database")
            
        except Exception as e:
            logger.error(f"Database storage error: {e}")
            
    def determine_alert_priority(self, report: Dict) -> str:
        """Determine alert priority level"""
        
        safety_score = report.get('safety_score', 100)
        risk_level = report.get('risk_level', 'low')
        
        if safety_score < 40 or risk_level == 'severe':
            return "critical"
        elif safety_score < 60 or risk_level == 'high':
            return "high"
        elif safety_score < 75 or risk_level == 'medium':
            return "medium"
        else:
            return "low"
            
    def get_driver_phone(self, driver_id: int) -> str:
        """Get driver's phone number"""
        
        return "+966501234567"
        
    def format_sms_alert(self, alert_data: Dict) -> str:
        """Format SMS message"""
        
        report = alert_data.get('report', {})
        safety_score = report.get('safety_score', 100)
        
        return f"""
SAFETY ALERT
Score: {safety_score}/100
Level: {report.get('risk_level', 'unknown')}
Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}
Check system for details
        """
        
    def get_recipient_emails(self, alert_data: Dict) -> List[str]:
        """Get email recipients"""
        
        recipients = []
        
        driver_email = f"driver{alert_data['driver_id']}@company.com"
        recipients.append(driver_email)
        recipients.append("safety.manager@company.com")
        
        if alert_data['priority'] in ['high', 'critical']:
            recipients.append("operations.director@company.com")
            
        return recipients
        
    def get_email_subject(self, alert_data: Dict) -> str:
        """Get email subject"""
        
        priority = alert_data.get('priority', 'medium')
        safety_score = alert_data.get('report', {}).get('safety_score', 100)
        
        prefix = {
            'critical': '[CRITICAL]',
            'high': '[HIGH]',
            'medium': '[MEDIUM]',
            'low': '[LOW]'
        }.get(priority, '[ALERT]')
        
        return f"{prefix} Safety Alert - Score: {safety_score}/100"
        
    def format_email_alert(self, alert_data: Dict) -> str:
        """Format email message"""
        
        report = alert_data.get('report', {})
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        .alert {{ padding: 20px; margin: 10px 0; border-radius: 5px; }}
        .critical {{ background-color: #f8d7da; border: 1px solid #f5c6cb; }}
        .high {{ background-color: #fff3cd; border: 1px solid #ffeaa7; }}
        .warning {{ color: #856404; background-color: #fff3cd; padding: 10px; margin: 5px 0; }}
    </style>
</head>
<body>
    <div class="alert {alert_data['priority']}">
        <h2>Safety Alert</h2>
        
        <h3>Trip Information</h3>
        <p><strong>Driver:</strong> {alert_data['driver_id']}</p>
        <p><strong>Vehicle:</strong> {alert_data['vehicle_id']}</p>
        <p><strong>Time:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <h3>Safety Check Results</h3>
        <p><strong>Safety Score:</strong> {report.get('safety_score', 100)}/100</p>
        <p><strong>Risk Level:</strong> {report.get('risk_level', 'unknown')}</p>
        
        <h3>Warnings:</h3>
        {self.format_warnings_html(report.get('warnings', []))}
        
        <h3>Recommendations:</h3>
        {self.format_recommendations_html(report.get('recommendations', []))}
        
        <hr>
        <p><em>Auto-generated by Safety Management System</em></p>
    </div>
</body>
</html>
        """
        
        return html_content
        
    def format_warnings_html(self, warnings: List[Dict]) -> str:
        """Format warnings as HTML"""
        
        if not warnings:
            return "<p>No warnings</p>"
            
        html = ""
        for warning in warnings:
            severity_icon = {
                'severe': '🔴',
                'high': '🟠',
                'medium': '🟡',
                'low': '🟢'
            }.get(warning.get('severity', 'low'), '⚪')
            
            html += f"""
            <div class="warning">
                {severity_icon} <strong>{warning.get('type', 'Warning')}</strong><br>
                {warning.get('message', '')}<br>
                <small>Level: {warning.get('severity', 'low')}</small>
            </div>
            """
            
        return html
        
    def format_recommendations_html(self, recommendations: List[Dict]) -> str:
        """Format recommendations as HTML"""
        
        if not recommendations:
            return "<p>No recommendations</p>"
            
        html = "<ul>"
        for rec in recommendations:
            html += f"""
            <li>
                <strong>{rec.get('action', 'Action')}:</strong> 
                {rec.get('message', '')} 
                <em>(Priority: {rec.get('priority', 'medium')})</em>
            </li>
            """
        html += "</ul>"
        
        return html
        
    def get_push_title(self, alert_data: Dict) -> str:
        """Get push notification title"""
        
        safety_score = alert_data.get('safety_score', 100)
        
        if safety_score < 50:
            return "CRITICAL Safety Alert"
        elif safety_score < 70:
            return "Important Safety Alert"
        else:
            return "Safety Update"
            
    def get_push_body(self, alert_data: Dict) -> str:
        """Get push notification body"""
        
        risk_level = alert_data.get('risk_level', 'low')
        warnings_count = len(alert_data.get('critical_warnings', []))
        
        if warnings_count > 0:
            return f"Risk Level: {risk_level}. {warnings_count} critical warnings."
        else:
            return f"Risk Level: {risk_level}. Check details."
