import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

const PageTitleUpdater = () => {
    const location = useLocation();

    // Mapping of paths to page titles
    const pathToTitle = {
        '/': 'GTS Logistics - Freight Broker & Load Board Platform',
        '/login': 'Login | GTS',
        '/logout': 'Logout | GTS',
        '/dashboard': 'Dashboard | GTS',
        '/verify-email': 'Verify Email | GTS',
        '/forgot-password': 'Forgot Password | GTS',
        '/reset-password': 'Reset Password | GTS',

        // AI Bots
        '/ai-bots': 'AI Bots | GTS',
        '/ai-bots/general-manager': 'General Manager | GTS',
        '/ai-bots/operations': 'Operations Manager | GTS',
        '/ai-bots/finance': 'Finance Bot | GTS',
        '/ai-bots/freight-broker': 'Freight Broker | GTS',
        '/ai-bots/documents': 'Documents Manager | GTS',
        '/ai-bots/customer-service': 'Customer Service | GTS',
        '/ai-bots/system-admin': 'System Admin | GTS',
        '/ai-bots/information-coordinator': 'Information Coordinator | GTS',
        '/ai-bots/legal': 'Legal Consultant | GTS',
        '/ai-bots/safety': 'Safety Manager | GTS',
        '/ai-bots/safety/dashboard': 'Safety Manager Dashboard | GTS',
        '/ai-bots/safety/incidents': 'Safety Incident Log | GTS',
        '/ai-bots/safety/drivers/monitor': 'Safety Driver Monitor | GTS',
        '/ai-bots/safety/vehicles/sensors': 'Safety Vehicle Sensors | GTS',
        '/ai-bots/sales': 'Sales Team | GTS',
        '/ai-bots/security': 'Security Manager | GTS',
        '/ai-bots/partner-manager': 'Partner Manager | GTS',
        '/ai-bots/strategy': 'Strategy Advisor | GTS',
        '/ai-bots/dispatcher': 'Dispatcher Dashboard | GTS',
        '/ai-bots/bookings': 'Freight Bookings | GTS',
        '/ai-bots/maintenance': 'Maintenance & Dev | GTS',
        '/ai-bots/bot-os': 'Bot OS | GTS',
        '/ai-bots/hub': 'AI Bots Hub | GTS',
        '/ai-bots/control': 'AI Bots Control | GTS',
        '/ai-bots/freight_broker': 'Freight Broker Dashboard | GTS',
        '/ai-bots/freight_broker/dashboard': 'Freight Broker Dashboard | GTS',
        '/ai-bots/freight_broker/shipments': 'Freight Shipments | GTS',
        '/ai-bots/freight_broker/map': 'Freight Map | GTS',
        '/ai-bots/freight_broker/live-map': 'Fleet Live Map | GTS',
        '/ai-bots/freight_broker/vehicles': 'Fleet Vehicles | GTS',
        '/ai-bots/freight_broker/drivers': 'Fleet Drivers | GTS',
        '/ai-bots/freight_broker/assignments': 'Fleet Assignments | GTS',
        '/ai-bots/freight_broker/fleet': 'Fleet Management | GTS',
        '/ai-bots/freight_broker/fleet/vehicles': 'Fleet Vehicles | GTS',
        '/ai-bots/freight_broker/fleet/drivers': 'Fleet Drivers | GTS',
        '/ai-bots/freight_broker/fleet/assignments': 'Fleet Assignments | GTS',
        '/ai-bots/freight_broker/fleet/incidents': 'Safety Incident Log | GTS',

        // Freight Broker
        '/freight-broker': 'Freight Broker | GTS',
        '/freight-broker/dashboard': 'Freight Broker Dashboard | GTS',
        '/freight-broker/shipments': 'Shipments | GTS',
        '/freight-broker/map': 'Freight Map | GTS',
        '/freight': 'Freight Broker | GTS',
        '/freight/dashboard': 'Freight Broker Dashboard | GTS',
        '/freight/shipments': 'Shipments | GTS',
        '/freight/map': 'Freight Map | GTS',
        '/freight/live-map': 'Fleet Live Map | GTS',

        // Admin
        '/admin': 'Admin Panel | GTS',
        '/admin/overview': 'Admin Overview | GTS',
        '/admin/users': 'User Management | GTS',
        '/admin/settings': 'Platform Settings | GTS',
        '/admin/subscriptions': 'Subscriptions | GTS',
        '/admin/tenants': 'Tenant Management | GTS',
        '/admin/audit-logs': 'Audit Logs | GTS',
        '/admin/feature-flags': 'Feature Flags | GTS',
        '/admin/portal-requests': 'Portal Requests | GTS',
        '/admin/notifications': 'Notifications | GTS',
        '/admin/platform-expenses': 'Platform Expenses | GTS',
        '/admin/TheVIZION': 'TheVIZION | GTS',
        '/admin/TheVIZION/task-manager': 'Task Manager | TheVIZION | GTS',

        // Support & Community
        '/support': 'Support | GTS',
        '/community': 'Community | GTS',
    };

    useEffect(() => {
        const pathname = location.pathname;

        // Try to find exact match
        let title = pathToTitle[pathname];

        // If no exact match, try to find by prefix/pattern
        if (!title) {
            if (pathname.startsWith('/ai-bots/')) {
                const botName = pathname.replace('/ai-bots/', '').replace(/-/g, ' ').toUpperCase();
                title = `${botName} | GTS`;
            } else if (pathname.startsWith('/admin/')) {
                const adminPage = pathname.replace('/admin/', '').replace(/-/g, ' ').toUpperCase();
                title = `${adminPage} | GTS`;
            } else if (pathname.startsWith('/freight-broker/')) {
                const page = pathname.replace('/freight-broker/', '').replace(/-/g, ' ').toUpperCase();
                title = `${page} | GTS`;
            } else if (pathname.startsWith('/freight/')) {
                const page = pathname.replace('/freight/', '').replace(/-/g, ' ').toUpperCase();
                title = `${page} | GTS`;
            } else {
                // Default title
                title = 'Gabani Transport Solutions';
            }
        }

        document.title = title;
    }, [location.pathname]);

    return null; // This component doesn't render anything
};

export default PageTitleUpdater;
