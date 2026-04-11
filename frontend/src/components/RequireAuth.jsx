/* eslint-disable react/prop-types */

import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext.jsx';

const RequireAuth = ({ roles }) => {
  const { user, authReady, isAuthenticated, accountStatus } = useAuth();
  const location = useLocation();

  if (!authReady) {
    return <div aria-busy="true" />;
  }

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (accountStatus === 'inactive') {
    return <Navigate to="/account-inactive" replace />;
  }

  if (roles && roles.length > 0) {
    const userRoles = [
      user.effective_role,
      user.role,
      user.db_role,
      user.token_role,
      ...(Array.isArray(user.roles) ? user.roles : []),
    ].filter(Boolean);

    const hasRole = roles.some((r) => userRoles.includes(r));
    if (!hasRole) {
      return <Navigate to="/unauthorized" replace />;
    }
  }

  return <Outlet />;
};

export default RequireAuth;
