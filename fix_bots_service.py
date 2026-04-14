# File: fix_bots_service.py
import psycopg2
import os
from datetime import datetime

class BotFixer:
    def __init__(self):
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'gabani_bots'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'password')
        }
        self.required_bots = [
            ('general_manager', 'AI General Manager', 'General Manager', None, 'management'),
            ('operations_manager', 'AI Operations Manager', 'Operations Manager', 'operations@gabanilogistics.com', 'operations'),
            ('finance_bot', 'AI Finance Bot', 'Finance Bot', 'finance@gabanilogistics.com', 'finance'),
            ('freight_broker', 'AI Freight Broker', 'Freight Broker', 'freight@gabanilogistics.com', 'operations'),
            ('documents_manager', 'AI Documents Manager', 'Documents Manager', 'doccontrol@gabanilogistics.com', 'operations'),
            ('customer_service', 'AI Customer Service', 'Customer Service', 'customers@gabanilogistics.com', 'services'),
            ('system_admin', 'AI System Admin', 'System Admin', 'admin@gabanilogistics.com', 'operations'),
            ('information_coordinator', 'AI Information Coordinator', 'Information Coordinator', 'intel@gabanilogistics.com', 'intelligence'),
            ('strategy_advisor', 'AI Strategy Advisor', 'Strategy Advisor', 'marketing@gabanilogistics.com', 'intelligence'),
            ('maintenance_dev', 'AI Dev Maintenance', 'Dev Maintenance', None, 'maintenance'),
            ('legal_consultant', 'AI Legal Consultant', 'Legal Consultant', 'operations@gabanilogistics.com', 'legal'),
            ('safety_manager', 'AI Safety Manager', 'Safety Manager', 'safety@gabanilogistics.com', 'safety'),
            ('sales', 'AI Sales Team', 'Sales Team', 'sales@gabanilogistics.com', 'sales'),
            ('security', 'AI Security Manager', 'Security Manager', 'security@gabanilogistics.com', 'security'),
            ('mapleload_canada', 'MapleLoad Canada', 'MapleLoad Canada', 'freight@gabanilogistics.com', 'operations'),
            ('freight_bookings', 'AI Freight Bookings', 'Freight Bookings', 'freight@gabanilogistics.com', 'operations'),
            ('legal_counsel', 'AI Legal Counsel', 'Legal Counsel', 'operations@gabanilogistics.com', 'legal'),
            ('safety', 'AI Safety', 'Safety', 'safety@gabanilogistics.com', 'safety'),
            ('security_bot', 'AI Security Bot', 'Security Bot', 'security@gabanilogistics.com', 'security'),
            ('sales_intelligence', 'AI Sales Intelligence', 'Sales Intelligence', 'sales@gabanilogistics.com', 'sales'),
            ('finance_intelligence', 'AI Finance Intelligence', 'Finance Intelligence', 'finance@gabanilogistics.com', 'finance'),
            ('executive_intelligence', 'AI Executive Intelligence', 'Executive Intelligence', None, 'management'),
            ('system_intelligence', 'AI System Intelligence', 'System Intelligence', 'admin@gabanilogistics.com', 'operations'),
            ('operations_management', 'AI Operations Management', 'Operations Management', 'operations@gabanilogistics.com', 'operations'),
            ('partner_manager', 'AI Partner Manager', 'Partner Manager', 'investments@gabanigroup.com', 'management'),
            ('partner_management', 'AI Partner Management', 'Partner Management', 'investments@gabanigroup.com', 'management'),
            ('partner', 'AI Partner', 'Partner', 'investments@gabanigroup.com', 'management'),
            ('mapleload', 'MapleLoad', 'MapleLoad', 'freight@gabanilogistics.com', 'operations')
        ]
    def check_database_connection(self):
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'bots'
                );
            """)
            table_exists = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            return {'connected': True, 'bots_table_exists': table_exists}
        except Exception as e:
            return {'connected': False, 'error': str(e)}
    def check_missing_bots(self):
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            cursor.execute("SELECT key FROM bots")
            existing_keys = {row[0] for row in cursor.fetchall()}
            required_keys = {bot[0] for bot in self.required_bots}
            missing_keys = required_keys - existing_keys
            cursor.close()
            conn.close()
            return {
                'total_required': len(required_keys),
                'existing': len(existing_keys),
                'missing': len(missing_keys),
                'missing_keys': list(missing_keys)
            }
        except Exception as e:
            return {'error': str(e)}
    def fix_missing_bots(self):
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bots (
                    id SERIAL PRIMARY KEY,
                    key VARCHAR(50) UNIQUE NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    display_name VARCHAR(100) NOT NULL,
                    email VARCHAR(100),
                    status VARCHAR(20) DEFAULT 'active',
                    category VARCHAR(50),
                    description TEXT,
                    icon VARCHAR(10),
                    automation_level VARCHAR(20) DEFAULT 'full',
                    health VARCHAR(20) DEFAULT 'good',
                    reports_to VARCHAR(50),
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            inserted_count = 0
            updated_count = 0
            for key, name, display_name, email, category in self.required_bots:
                icon = self.get_icon_for_category(category)
                description = self.get_description_for_bot(key, name)
                status = 'paused' if 'partner' in key else 'active'
                cursor.execute("""
                    INSERT INTO bots (key, name, display_name, email, status, category, description, icon)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (key) DO UPDATE SET
                        name = EXCLUDED.name,
                        display_name = EXCLUDED.display_name,
                        status = EXCLUDED.status,
                        updated_at = CURRENT_TIMESTAMP
                    RETURNING (xmax = 0) AS inserted;
                """, (key, name, display_name, email, status, category, description, icon))
                result = cursor.fetchone()
                if result[0]:
                    inserted_count += 1
                else:
                    updated_count += 1
            conn.commit()
            cursor.close()
            conn.close()
            return {
                'success': True,
                'inserted': inserted_count,
                'updated': updated_count,
                'total': len(self.required_bots)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    def get_icon_for_category(self, category):
        icons = {
            'management': '👑',
            'operations': '⚙️',
            'finance': '💰',
            'services': '👨💼',
            'intelligence': '🧠',
            'maintenance': '🔧',
            'legal': '⚖️',
            'safety': '🛡️',
            'sales': '💼',
            'security': '🔒'
        }
        return icons.get(category, '🤖')
    def get_description_for_bot(self, key, name):
        descriptions = {
            'general_manager': 'Guides company strategy and integrates executive reports.',
            'operations_manager': 'Coordinates daily operations and unifies bot execution.',
            'finance_bot': 'Tracks finances, invoices, and profitability analysis.',
            'freight_broker': 'Manages freight sourcing, pricing, and carrier coordination.',
            'documents_manager': 'Archives, validates, and manages operational documents.',
            'customer_service': 'Automates customer support and issue resolution.',
            'system_admin': 'Manages system configuration, users, and infrastructure.',
            'information_coordinator': 'Transforms data into actionable insights and dashboards.',
            'strategy_advisor': 'Analyzes market trends and provides strategic recommendations.',
            'maintenance_dev': 'Maintains system health and suggests engineering improvements.',
            'legal_consultant': 'Reviews legal documents and ensures compliance.',
            'safety_manager': 'Tracks safety incidents and monitors compliance across operations.',
            'sales': 'Manages customer relationships and revenue growth.',
            'security': 'Protects the platform from threats and suspicious activity.',
            'mapleload_canada': 'Specialized in Canadian logistics for carrier discovery and market intelligence.'
        }
        return descriptions.get(key, f'Automated system for {name} operations.')
def main():
    print("Starting bot system fix...")
    print("=" * 50)
    fixer = BotFixer()
    print("1. Checking database connection...")
    db_status = fixer.check_database_connection()
    if not db_status['connected']:
        print(f"Database connection error: {db_status.get('error')}")
        return
    print(f"Database connected: {db_status['connected']}")
    print(f"Bots table exists: {db_status['bots_table_exists']}")
    print()
    print("2. Checking missing bots...")
    missing_status = fixer.check_missing_bots()
    if 'error' in missing_status:
        print(f"Check error: {missing_status['error']}")
        return
    print(f"Required bots: {missing_status['total_required']}")
    print(f"Existing bots: {missing_status['existing']}")
    print(f"Missing bots: {missing_status['missing']}")
    if missing_status['missing'] > 0:
        print(f"Missing bots: {', '.join(missing_status['missing_keys'])}")
        print()
        print("3. Fixing missing bots...")
        fix_result = fixer.fix_missing_bots()
        if fix_result['success']:
            print(f"Inserted {fix_result['inserted']} new bots")
            print(f"Updated {fix_result['updated']} existing bots")
            print(f"Total: {fix_result['total']} bots")
        else:
            print(f"Fix failed: {fix_result['error']}")
    else:
        print("All bots present - no fix needed")
    print()
    print("=" * 50)
    print("Bot system fix complete!")
if __name__ == "__main__":
    main()
