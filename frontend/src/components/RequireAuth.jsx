/* eslint-disable react/prop-types */

import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext.jsx';

const RequireAuth = ({ roles, allowedRoles }) => {
  const { user, authReady, isAuthenticated, accountStatus } = useAuth();
  const location = useLocation();

  const allowedList = roles ?? allowedRoles ?? [];

  // Show a pending shell while auth state is being determined
  if (!authReady) {
    return <div aria-busy="true" />;
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated || !user) {
    console.warn('[RequireAuth] Access denied: User not authenticated. Redirecting to login.');
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Redirect inactive accounts
  if (accountStatus === 'inactive') {
    console.warn('[RequireAuth] Account inactive. Redirecting to account-inactive.');
    return <Navigate to="/account-inactive" replace />;
  }

  // Resolve the user's roles
  const userRolesArray = Array.isArray(user?.roles) ? user.roles : [];
  const singleRole =
    user?.effective_role ||
    user?.role ||
    user?.db_role ||
    user?.token_role ||
    null;

  // Super admin bypass
  if (singleRole === 'super_admin' || userRolesArray.includes('super_admin')) {
    console.log('[RequireAuth] Super admin granted access.');
    return <Outlet />;
  }

  // Check if current user role is permitted
  if (allowedList.length > 0) {
    const hasRole =
      (singleRole && allowedList.includes(singleRole)) ||
      userRolesArray.some((r) => allowedList.includes(r));

    if (!hasRole) {
      console.error(`[RequireAuth] Access denied: role not in allowed list [${allowedList.join(', ')}]`);
      return <Navigate to="/unauthorized" replace />;
    }
  }

  console.log('[RequireAuth] Access granted.');
  return <Outlet />;
};

export default RequireAuth;
