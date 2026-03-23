// frontend/src/utils/RoleProtectedRoute.jsx

import { Navigate } from "react-router-dom";
import { useLocation } from "react-router-dom";
import PropTypes from "prop-types";
import { useAuth } from "../contexts/AuthContext.jsx";
import { getUserRole, hasRequiredRole, normalizeUserRole } from "./userRole";

const RoleProtectedRoute = ({ children, allowedRoles }) => {
  const { authReady, isAuthenticated, user, accountStatus } = useAuth();
  const location = useLocation();
  const role = getUserRole(user);
  const normalizedAllowed = (allowedRoles || []).map(normalizeUserRole);

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

  if (normalizedAllowed.length === 0) {
    return children;
  }

  if (hasRequiredRole(role, normalizedAllowed)) {
    return children;
  }

  return <Navigate to="/unauthorized" replace />;
};

RoleProtectedRoute.propTypes = {
  children: PropTypes.node.isRequired,
  allowedRoles: PropTypes.arrayOf(PropTypes.string).isRequired,
};

export default RoleProtectedRoute;
