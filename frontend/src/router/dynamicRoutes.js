const menuTemplates = {
    super_admin: [
        {
            id: "overview",
            title: "Dashboard",
            path: "/admin/overview",
            permission: "dashboard.view",
        },
        {
            id: "users",
            title: "Users",
            path: "/admin/users",
            permission: "users.view",
            children: [
                { id: "users_list", title: "Manage Users", path: "/admin/users", permission: "users.view" },
                { id: "tenants", title: "Manage Tenants", path: "/admin/tenants", permission: "tenants.view" },
            ],
        },
        {
            id: "reports",
            title: "Reports",
            path: "/admin/reports",
            permission: "reports.view",
        },
        {
            id: "market_intelligence",
            title: "Market Intelligence",
            path: "/admin/market-intelligence",
            permission: "reports.analytics",
        },
        {
            id: "system",
            title: "System",
            path: "/admin/system-health",
            permission: "system.view",
            children: [
                { id: "system_health", title: "System Health", path: "/admin/system-health", permission: "system.view" },
                { id: "settings", title: "Platform Settings", path: "/admin/settings", permission: "system.settings" },
                { id: "subscriptions", title: "Subscriptions", path: "/admin/subscriptions", permission: "system.settings" },
                { id: "api_connections", title: "API Connections", path: "/admin/api-connections", permission: "system.integrations" },
                { id: "feature_flags", title: "Feature Flags", path: "/admin/feature-flags", permission: "system.flags" },
            ],
        },
        {
            id: "platform_expenses",
            title: "Platform Expenses",
            path: "/admin/platform-expenses",
        },
        {
            id: "the_vizion",
            title: "TheVIZION",
            path: "/admin/TheVIZION",
            permission: "vizion.view",
            children: [
                { id: "vizion_overview", title: "Observability Hub", path: "/admin/TheVIZION", permission: "vizion.view" },
                { id: "task_manager", title: "Task Manager", path: "/admin/TheVIZION/task-manager", permission: "vizion.tasks" },
            ],
        },
        {
            id: "partners",
            title: "Partners",
            path: "/admin/partners",
        },
        {
            id: "audit",
            title: "Audit Logs",
            path: "/admin/audit-logs",
            permission: "system.logs",
        },
        {
            id: "portal_requests",
            title: "Portal Requests",
            path: "/admin/portal-requests",
            permission: "portal.requests",
        },
        {
            id: "support",
            title: "Support",
            path: "/admin/support",
            permission: "support.view",
            children: [
                { id: "support_center", title: "Support Center", path: "/admin/support", permission: "support.view" },
                { id: "support_tickets", title: "Support Tickets", path: "/admin/support/tickets", permission: "support.view" },
            ],
        },
    ],
    admin: [
        {
            id: "overview",
            title: "Dashboard",
            path: "/admin/overview",
            permission: "dashboard.view",
        },
        {
            id: "users",
            title: "Users",
            path: "/admin/users",
            permission: "users.view",
        },
        {
            id: "reports",
            title: "Reports",
            path: "/admin/reports",
            permission: "reports.view",
        },
        {
            id: "market_intelligence",
            title: "Market Intelligence",
            path: "/admin/market-intelligence",
            permission: "reports.analytics",
        },
        {
            id: "system_health",
            title: "System Health",
            path: "/admin/system-health",
            permission: "system.view",
        },
        {
            id: "settings",
            title: "Platform Settings",
            path: "/admin/settings",
            permission: "system.settings",
        },
        {
            id: "subscriptions",
            title: "Subscriptions",
            path: "/admin/subscriptions",
            permission: "system.settings",
        },
        {
            id: "platform_expenses",
            title: "Platform Expenses",
            path: "/admin/platform-expenses",
        },
        {
            id: "the_vizion",
            title: "TheVIZION",
            path: "/admin/TheVIZION",
            permission: "vizion.view",
            children: [
                { id: "vizion_overview", title: "Observability Hub", path: "/admin/TheVIZION", permission: "vizion.view" },
                { id: "task_manager", title: "Task Manager", path: "/admin/TheVIZION/task-manager", permission: "vizion.tasks" },
            ],
        },
        {
            id: "partners",
            title: "Partners",
            path: "/admin/partners",
        },
        {
            id: "support",
            title: "Support Center",
            path: "/admin/support",
            permission: "support.view",
        },
    ],
};

const ROLE_INFO = {
    super_admin: { name: "Super Admin", color: "#DC2626", icon: "crown" },
    owner: { name: "Owner", color: "#DC2626", icon: "crown" },
    admin: { name: "Admin", color: "#059669", icon: "shield" },
    manager: { name: "Manager", color: "#2563EB", icon: "briefcase" },
    user: { name: "User", color: "#6B7280", icon: "user" },
};

const normalizeRole = (role) => {
    const normalized = (role || "").toLowerCase().trim();
    if (["super_admin", "superadmin", "super-admin", "owner"].includes(normalized)) return "super_admin";
    if (["admin", "administrator"].includes(normalized)) return "admin";
    if (normalized === "manager") return "manager";
    return normalized || "admin";
};

export const getRoleInfo = (role) => {
    const normalized = normalizeRole(role);
    return ROLE_INFO[normalized] || ROLE_INFO.user;
};

const hasPermission = (permissions, permission) => {
    // If no specific permission required, allow access
    if (!permission) return true;
    // If no permissions array provided, allow access (backward compatibility)
    if (!Array.isArray(permissions) || permissions.length === 0) return true;
    // If wildcard permission exists, allow access
    if (permissions.includes("*")) return true;
    // Check if specific permission exists
    return permissions.includes(permission);
};

const filterMenuByPermissions = (menu, permissions) =>
    (menu || [])
        .map((item) => {
            if (!hasPermission(permissions, item.permission)) return null;
            if (!item.children?.length) return item;
            const children = filterMenuByPermissions(item.children, permissions);
            if (children.length === 0) return null;
            return { ...item, children };
        })
        .filter(Boolean);

export const generateSidebarMenu = (userRole, permissions = []) => {
    const normalized = normalizeRole(userRole);
    const template = menuTemplates[normalized] || menuTemplates.admin;
    if (normalized === "super_admin") {
        return template;
    }
    // If no permissions provided, show full menu for the role
    const permissionsToUse = Array.isArray(permissions) && permissions.length > 0 ? permissions : ["*"];
    return filterMenuByPermissions(template, permissionsToUse);
};


// Carriers routes
export const carriersRoutes = [
  { path: '/ai-bots/carriers/dashboard', title: 'Carriers Dashboard', icon: '📊' },
  { path: '/ai-bots/carriers/list', title: 'Carriers List', icon: '🚛' },
  { path: '/ai-bots/carriers/rates', title: 'Rates & Pricing', icon: '💰' },
  { path: '/ai-bots/carriers/contracts', title: 'Contracts', icon: '📄' },
];

// Shippers routes
export const shippersRoutes = [
  { path: '/ai-bots/shippers/dashboard', title: 'Shippers Dashboard', icon: '📊' },
  { path: '/ai-bots/shippers/list', title: 'Shippers List', icon: '👥' },
  { path: '/ai-bots/shippers/shipments', title: 'Shipments', icon: '📦' },
  { path: '/ai-bots/shippers/invoices', title: 'Invoices', icon: '💰' },
];
