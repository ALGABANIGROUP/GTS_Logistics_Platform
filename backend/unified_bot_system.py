from datetime import datetime
from backend.utils.email_utils import send_email

class UnifiedBotSystem:
    """Unified registry and communication helpers for platform AI bots."""

    # Bot key normalization aliases (legacy -> canonical)
    BOT_UNIFICATION_MAP = {
        # Dev maintenance aliases
        'dev_maintenance': 'dev_maintenance',
        'maintenance_dev': 'dev_maintenance',
        'cto': 'dev_maintenance',

        # Safety aliases
        'safety': 'safety_manager',
        'safety_manager': 'safety_manager',

        # Sales aliases
        'sales': 'sales_team',
        'sales_team': 'sales_team',

        # Security aliases
        'security': 'security_manager',
        'security_manager': 'security_manager',

        # Partner aliases
        'partner': 'partner_manager',
        'partner_manager': 'partner_manager',

        # Freight aliases
        'mapleload': 'freight_broker',
        'mapleload_canada': 'freight_broker',
        'freight_broker': 'freight_broker',

        # Executive aliases
        'executive_intelligence': 'general_manager',
        'general_manager': 'general_manager',

        # Marketing aliases
        'marketing': 'marketing_manager',
        'marketing_manager': 'marketing_manager',
    }

    # Canonical bot definitions
    UNIFIED_BOTS = {
        'general_manager': {
            'name': 'AI General Manager',
            'email_local_part': None,
            'status': 'active',
            'description': 'Executive oversight and strategic coordination',
            'reports_to': None
        },
        'operations_manager': {
            'name': 'AI Operations Manager',
            'email_local_part': 'operations',
            'status': 'active',
            'description': 'Oversees operations and workflow orchestration',
            'reports_to': 'general_manager'
        },
        'finance_bot': {
            'name': 'AI Finance Bot',
            'email_local_part': 'finance',
            'secondary_email_local_part': 'accounts',
            'status': 'active',
            'description': 'Financial reporting and billing workflows',
            'reports_to': 'operations_manager'
        },
        'freight_broker': {
            'name': 'AI Freight Broker',
            'email_local_part': 'freight',
            'status': 'active',
            'description': 'Shipment brokerage and MapleLoad Canada coordination',
            'reports_to': 'operations_manager'
        },
        'documents_manager': {
            'name': 'AI Documents Manager',
            'email_local_part': 'doccontrol',
            'status': 'active',
            'description': 'Document lifecycle and compliance management',
            'reports_to': 'operations_manager'
        },
        'customer_service': {
            'name': 'AI Customer Service',
            'email_local_part': 'customers',
            'status': 'active',
            'description': 'Customer communication and support automation',
            'reports_to': 'operations_manager'
        },
        'system_admin': {
            'name': 'AI System Admin',
            'email_local_part': 'admin',
            'no_reply_email_local_part': 'no-reply',
            'status': 'active',
            'description': 'Platform administration and system maintenance',
            'reports_to': 'operations_manager'
        },
        'information_coordinator': {
            'name': 'AI Information Coordinator',
            'email_local_part': 'intel',
            'status': 'active',
            'description': 'Cross-team information routing and insights sharing',
            'reports_to': 'operations_manager'
        },
        'strategy_advisor': {
            'name': 'AI Strategy Advisor',
            'email_local_part': None,
            'status': 'premium',
            'description': 'Strategic planning and executive recommendations',
            'reports_to': 'general_manager'
        },
        'marketing_manager': {
            'name': 'AI Marketing Manager',
            'email_local_part': 'marketing',
            'status': 'active',
            'description': 'Marketing planning and campaign support',
            'reports_to': 'general_manager'
        },
        'partner_manager': {
            'name': 'AI Partner Manager',
            'email_local_part': 'investments',
            'status': 'paused',
            'description': 'Partnership management and investor coordination',
            'reports_to': 'general_manager'
        },
        'dev_maintenance': {
            'name': 'AI Dev Maintenance Bot (CTO)',
            'email_local_part': None,
            'status': 'active',
            'description': 'Engineering maintenance, monitoring, and fixes',
            'reports_to': 'operations_manager'
        },
        'safety_manager': {
            'name': 'AI Safety Manager',
            'email_local_part': 'safety',
            'status': 'intelligence_mode',
            'description': 'Safety compliance and incident intelligence',
            'reports_to': 'operations_manager'
        },
        'security_manager': {
            'name': 'AI Security Manager',
            'email_local_part': 'security',
            'status': 'active',
            'description': 'Security monitoring and risk protection',
            'reports_to': 'operations_manager'
        },
        'sales_team': {
            'name': 'AI Sales Team',
            'email_local_part': 'sales',
            'status': 'intelligence_mode',
            'description': 'Sales operations and lead management',
            'reports_to': 'marketing_manager'
        }
    }

    def __init__(self):
        self.email_system = EmailSystem()
        self.active_bots = self.get_active_bots()

    def unify_bot_key(self, bot_key):
        """Map an alias key to its canonical bot key."""
        return self.BOT_UNIFICATION_MAP.get(bot_key, bot_key)

    def get_bot_info(self, bot_key):
        """Return bot metadata for a bot key or alias."""
        unified_key = self.unify_bot_key(bot_key)
        return self.UNIFIED_BOTS.get(unified_key, None)

    def get_active_bots(self):
        """Return bots that are currently active or in intelligence mode."""
        active_bots = []
        for key, info in self.UNIFIED_BOTS.items():
            if info['status'] in ['active', 'intelligence_mode']:
                active_bots.append({
                    'key': key,
                    **info
                })
        return active_bots

    def send_bot_report(self, from_bot_key, to_bot_key, subject, body):
        """Send a report between bots through email or internal fallback."""
        from_info = self.get_bot_info(from_bot_key)
        to_info = self.get_bot_info(to_bot_key)

        if not from_info or not to_info:
            return {"success": False, "error": "Invalid source or target bot"}

        # Use internal reports when one of the bots has no email identity
        if not from_info.get('email_local_part') or not to_info.get('email_local_part'):
            return self.send_internal_report(from_bot_key, to_bot_key, subject, body)

        # Send via SMTP
        return self.email_system.send_email(
            from_email_local_part=from_info['email_local_part'],
            to_email_local_part=to_info['email_local_part'],
            subject=f"[{from_info['name']}] {subject}",
            body=body
        )

    def send_internal_report(self, from_bot_key, to_bot_key, subject, body):
        """Create an internal report record for non-email bot communication."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report_data = {
            'from_bot': from_bot_key,
            'to_bot': to_bot_key,
            'subject': subject,
            'body': body,
            'timestamp': timestamp,
            'type': 'internal_report'
        }

        # Console audit output
        print(f"📄 Internal report: {from_bot_key} -> {to_bot_key}")
        print(f"📝 Subject: {subject}")

        return {"success": True, "report_id": f"INT_{timestamp}"}

    def get_bot_hierarchy(self):
        """Build manager-to-subordinate mapping from bot definitions."""
        hierarchy = {}
        for key, info in self.UNIFIED_BOTS.items():
            if info['reports_to']:
                if info['reports_to'] not in hierarchy:
                    hierarchy[info['reports_to']] = []
                hierarchy[info['reports_to']].append(key)
        return hierarchy


class EmailSystem:
    """SMTP email delivery helper for bot communication."""

    def __init__(self):
        self.smtp_server = "smtp.gabanilogistics.com"
        self.smtp_port = 587
        self.username = "system"
        self.password = "password"  # Placeholder credential

    def send_email(self, from_email_local_part, to_email_local_part, subject, body, tenant_domain=None):
        """Send an email using tenant domain if provided, otherwise default domain."""
        try:
            # Resolve sender/receiver domain
            if tenant_domain:
                from_email = f"{from_email_local_part}@{tenant_domain}"
                to_email = f"{to_email_local_part}@{tenant_domain}"
            else:
                from_email = f"{from_email_local_part}@gabanilogistics.com"
                to_email = f"{to_email_local_part}@gabanilogistics.com"

            sent = send_email(
                subject=subject,
                body=body,
                to=[to_email],
                html=False,
                from_email=from_email,
                smtp_user=self.username,
                smtp_password=self.password,
                smtp_host=self.smtp_server,
                smtp_port=self.smtp_port,
                smtp_secure=True,
            )
            if not sent:
                raise RuntimeError("send_email returned False")

            print(f"✅ Email sent from {from_email} to {to_email}")
            return {"success": True, "message": "Email sent successfully"}

        except Exception as e:
            print(f"❌ Email send failed: {str(e)}")
            return {"success": False, "error": str(e)}


# Demo execution
if __name__ == "__main__":
    # Initialize system
    bot_system = UnifiedBotSystem()

    # Print active bots
    print("=" * 50)
    print("🤖 Active bots:")
    print("=" * 50)

    for bot in bot_system.active_bots:
        status_icon = "🟢" if bot['status'] == 'active' else "🟡"
        email_display = bot.get('email_local_part', 'N/A')
        print(f"{status_icon} {bot['name']}")
        print(f"   📧 Email identity: {email_display}")
        print(f"   📝 Description: {bot['description']}")
        print()

    # Print hierarchy
    print("=" * 50)
    print("🏢 Reporting hierarchy:")
    print("=" * 50)

    hierarchy = bot_system.get_bot_hierarchy()
    for manager, subordinates in hierarchy.items():
        manager_info = bot_system.get_bot_info(manager)
        print(f"\n{manager_info['name']} manages:")
        for sub in subordinates:
            sub_info = bot_system.get_bot_info(sub)
            print(f"  • {sub_info['name']}")

    # Send sample report
    print("\n" + "=" * 50)
    print("📤 Sample report:")
    print("=" * 50)

    result = bot_system.send_bot_report(
        from_bot_key="finance_bot",
        to_bot_key="operations_manager",
        subject="Weekly finance update",
        body="Summary prepared and delivered to operations management."
    )

    print(f"Result: {result}")
