import React from "react";
import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext.jsx";
import { hasRequiredRole, normalizeUserRole } from "../utils/userRole";

export default function RequireAuth({ children, roles, requiredRole }) {
  const { authReady, isAuthenticated, accountStatus, user } = useAuth();
  const location = useLocation();

  if (!authReady) return <div className="min-h-screen" aria-busy="true" />;
  if (!isAuthenticated) {
    const next = encodeURIComponent(location.pathname + location.search);
    return <Navigate to={`/login?next=${next}`} replace />;
  }
  if (accountStatus && accountStatus !== "active") {
    return <Navigate to="/account-inactive" replace />;
  }

  // Check if roles are required
  const allowedRoles = roles || (requiredRole ? [requiredRole] : null);
  if (allowedRoles && user?.role) {
    const userRole = normalizeUserRole(user.role);
    const allowed = allowedRoles.map(normalizeUserRole);

    if (!hasRequiredRole(userRole, allowed)) {
      console.warn(`[RequireAuth] User role '${userRole}' not in allowed roles:`, allowedRoles);
      return <Navigate to="/unauthorized" replace />;
    }
  }

  if (children) return children;
  return <Outlet />;
}
