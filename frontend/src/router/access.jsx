import React from 'react';
import { Navigate } from 'react-router-dom';

// Feature flags from environment or API
const REGISTRATION_DISABLED = import.meta.env.VITE_REGISTRATION_DISABLED === 'true';
const REGISTRATION_REOPEN_DATE = import.meta.env.VITE_REGISTRATION_REOPEN_DATE || 'August 9, 2026';

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
