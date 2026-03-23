export const adminNav = [
    {
        key: "admin_overview",
        label: "Admin Overview",
        path: "/admin/overview",
        children: [
            { key: "admin_users", label: "Users & Roles", path: "/admin/users" },
            { key: "admin_settings", label: "Platform Settings", path: "/admin/settings" },
            { key: "admin_api_connections", label: "API Connections", path: "/admin/api-connections" },
            { key: "admin_tenants", label: "Tenants Management", path: "/admin/tenants" },
            { key: "admin_platform_expenses", label: "Platform Expenses", path: "/admin/platform-expenses" },
            { key: "admin_audit", label: "Audit Logs", path: "/admin/audit-logs" },
            { key: "admin_health", label: "System Health", path: "/admin/system-health" },
        ],
    },
];
