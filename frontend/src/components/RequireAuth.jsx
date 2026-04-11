/* eslint-disable react/prop-types */

import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext.jsx';
import { CircularProgress, Box } from '@mui/material';

const RequireAuth = ({ roles = [] }) => {
  const { user, role, isLoading, authReady, isAuthenticated, accountStatus } = useAuth();
  const location = useLocation();

  // Support both authReady (preferred) and isLoading (legacy)
  const loading = authReady !== undefined ? !authReady : !!isLoading;

  const resolvedRole =
    role ||
    user?.effective_role ||
    user?.role ||
    user?.db_role ||
    user?.token_role ||
    null;

  // Show loading indicator while fetching user info
  if (loading) {
    return (
      <Box aria-busy="true" sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated || !user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Redirect inactive accounts
  if (accountStatus === 'inactive') {
    return <Navigate to="/account-inactive" replace />;
  }

  if (resolvedRole === 'super_admin') {
    return <Outlet />;
  }

  // Check if current user role is permitted
  if (roles.length > 0) {
    const userRoles = Array.isArray(user?.roles) ? user.roles : [];
    const hasRole = resolvedRole
      ? roles.includes(resolvedRole)
      : userRoles.some((r) => roles.includes(r));

    if (!hasRole) {
      return <Navigate to="/unauthorized" replace />;
    }
  }

  return <Outlet />;
};

export default RequireAuth;
