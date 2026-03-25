import React from 'react';
import { Navigate } from 'react-router-dom';

// Feature flags from environment or API
const REGISTRATION_DISABLED = import.meta.env.VITE_REGISTRATION_DISABLED === 'true';
const REGISTRATION_REOPEN_DATE = import.meta.env.VITE_REGISTRATION_REOPEN_DATE || 'August 9, 2026';

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

export const RegistrationGate = ({ children }) => {
    if (REGISTRATION_DISABLED) {
        return (
            <Navigate
                to="/contact"
                state={{
                    message: 'Registration is temporarily paused. Please contact us for access.',
                    reopenDate: REGISTRATION_REOPEN_DATE
                }}
                replace
            />
        );
    }
    return children;
};

export const LoginGate = ({ children }) => {
    // Check if user is logged in
    const token = localStorage.getItem('access_token');
    if (!token) {
        return children;
    }
    return <Navigate to="/dashboard" replace />;
};

export const RequireActiveAccount = ({ children }) => {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    if (user.is_active === false) {
        return <Navigate to="/account-inactive" replace />;
    }
    return children;
};
