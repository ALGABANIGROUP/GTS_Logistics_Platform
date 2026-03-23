import { Navigate } from "react-router-dom";
import AdminOverview from "../pages/admin/AdminOverview";
import AdminUsers from "../pages/admin/AdminUsers";
import PortalRequests from "../pages/admin/PortalRequests";
import AdminUsersLayout from "../pages/admin/AdminUsersLayout";
import PlatformSettings from "../pages/admin/PlatformSettings";
import TenantManagement from "../pages/admin/TenantManagement";
import PlatformExpenses from "../pages/admin/PlatformExpenses";
import AuditLogs from "../components/AuditLogs";
import SystemHealth from "../pages/admin/SystemHealth";
import OrchestrationDashboard from "../pages/admin/OrchestrationDashboard";
import SupportCenter from "../pages/admin/SupportCenter";

export const adminRoutes = [
    { path: "/admin", element: <Navigate to="/admin/overview" replace /> },
    { path: "/admin/overview", element: <AdminOverview /> },
    {
        path: "/admin",
        element: <AdminUsersLayout />,
        children: [
            { path: "users", element: <AdminUsers /> },
            { path: "portal-requests", element: <PortalRequests /> },
            { path: "Admin-Users", element: <Navigate to="/admin/users" replace /> },
        ],
    },
    { path: "/admin/settings", element: <PlatformSettings /> },
    { path: "/admin/tenants", element: <TenantManagement /> },
    { path: "/admin/platform-expenses", element: <PlatformExpenses /> },
    { path: "/admin/audit-logs", element: <AuditLogs /> },
    { path: "/admin/system-health", element: <SystemHealth /> },
    { path: "/admin/orchestration", element: <OrchestrationDashboard /> },
    { path: "/admin/support", element: <SupportCenter /> },
    // Removed: Branding, Social, Security routes
];
