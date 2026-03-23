import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext.jsx";
import { getUserRole, hasRequiredRole, normalizeUserRole } from "../../utils/userRole";

const RoleProtectedRoute = ({ children, allowedRoles = [] }) => {
  const { authReady, isAuthenticated, user, accountStatus } = useAuth();
  const location = useLocation();

  if (!authReady) {
    return <div className="min-h-screen" aria-busy="true" />;
  }

  if (!isAuthenticated) {
    const next = encodeURIComponent(location.pathname + location.search);
    return <Navigate to={`/login?next=${next}`} replace />;
  }

  if (accountStatus && accountStatus !== "active") {
    return <Navigate to="/account-inactive" replace />;
  }

  const role = getUserRole(user);
  const normalizedAllowed = allowedRoles.map(normalizeUserRole);

  if (normalizedAllowed.length === 0) {
    return children;
  }

  if (hasRequiredRole(role, normalizedAllowed)) {
    return children;
  }

  return <Navigate to="/unauthorized" replace />;
};

export default RoleProtectedRoute;
