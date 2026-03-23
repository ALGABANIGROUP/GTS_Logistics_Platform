import React from "react";
import { useEntitlements } from "../stores/useEntitlements";
import { REGISTRATION_DISABLED_FLAG, REGISTRATION_CONTACT } from "../config/registration";
import { hasRequiredRole, normalizeUserRole } from "../utils/userRole";

// Sidebar items with access conditions
export const sidebarItems = [
    { to: "/dashboard", label: "Dashboard", module: "dashboard" },
    { to: "/ai-bots", label: "AI Bots", module: "ai-bots" },
    { to: "/emails", label: "Email Logs", module: "email-logs" },
    { to: "/admin", label: "Admin Panel", module: "admin" },
    // Add more as needed
];

// Function to check whether an item can be displayed
export function canShow(item, ent) {
    if (!ent) return true;
    if (ent.isSuperAdmin?.()) return true;
    if (item.plan && ent.hasPlan && !ent.hasPlan(item.plan)) return false;
    if (item.subscription && ent.hasSubscription && !ent.hasSubscription(item.subscription)) return false;
    if (item.module && ent.hasModule && !ent.hasModule(item.module)) return false;
    if (item.modules && ent.hasModule && !item.modules.some((mod) => ent.hasModule(mod))) return false;
    if (item.feature && ent.hasFeature && !ent.hasFeature(item.feature)) return false;
    if (item.roles && ent.role_key && !item.roles.includes(ent.role_key)) return false;
    return true;
}

// Route Guard Component
export default function Require({ feature, roles, permission, plan, subscription, children }) {
    const loaded = useEntitlements((s) => s.loaded);
    const role = useEntitlements((s) => s.role_key);
    const hasFeature = useEntitlements((s) => s.hasFeature);
    const hasPermission = useEntitlements((s) => s.hasPermission);
    const isSuperAdmin = useEntitlements((s) => s.isSuperAdmin);
    const hasPlan = useEntitlements((s) => s.hasPlan);
    const hasSubscription = useEntitlements((s) => s.hasSubscription);

    if (!loaded) return <div className="p-6 text-center">Loading...</div>;

    if (isSuperAdmin()) return children;

    if (plan && !hasPlan(plan)) {
        if (REGISTRATION_DISABLED_FLAG) {
            return <div className="p-6 text-center text-red-400">Internal access is managed by admin. Contact: {REGISTRATION_CONTACT}</div>;
        }
        return <div className="p-6 text-center text-red-400">Upgrade Required: {plan}</div>;
    }
    if (subscription && !hasSubscription(subscription)) {
        if (REGISTRATION_DISABLED_FLAG) {
            return <div className="p-6 text-center text-red-400">Access policy is managed internally by admin.</div>;
        }
        return <div className="p-6 text-center text-red-400">Subscription Required</div>;
    }
    if (feature && !hasFeature(feature)) {
        if (REGISTRATION_DISABLED_FLAG) {
            return <div className="p-6 text-center text-red-400">Feature access is managed internally by admin.</div>;
        }
        return <div className="p-6 text-center text-red-400">Upgrade Required: {feature}</div>;
    }
    if (roles && role) {
        const normalizedRole = normalizeUserRole(role);
        const normalizedAllowedRoles = roles.map(normalizeUserRole);
        const hasRole = hasRequiredRole(normalizedRole, normalizedAllowedRoles);
        console.log("[Require] Role check:", { userRole: normalizedRole, allowedRoles: normalizedAllowedRoles, hasRole });
        if (!hasRole) return <div className="p-6 text-center text-red-400">No Access (Your role: {role})</div>;
    }
    if (permission && !hasPermission(permission)) return <div className="p-6 text-center text-red-400">No Access</div>;

    return children;
}
