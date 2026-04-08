/* eslint-disable react/prop-types */

import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext.jsx';
import { CircularProgress, Box } from '@mui/material';

const RequireAuth = ({ children, allowedRoles = [] }) => {
  const { user, role, isLoading, isAuthenticated } = useAuth();
  const location = useLocation();
  const resolvedRole =
    role ||
    user?.effective_role ||
    user?.role ||
    user?.db_role ||
    user?.token_role ||
    null;

  // Debug logs for troubleshooting access
  console.log('[RequireAuth] State:', { isLoading, isAuthenticated, userRole: resolvedRole, allowedRoles });

  // Show loading indicator while fetching user info
  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated || !user) {
    console.warn('[RequireAuth] Access denied: User not authenticated. Redirecting to login.');
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (resolvedRole === 'super_admin') {
    console.log('[RequireAuth] Super admin granted access.');
    return children;
  }

  // Check if current user role is permitted
  if (allowedRoles.length > 0 && !allowedRoles.includes(resolvedRole)) {
    console.error(`[RequireAuth] Access denied: Role "${resolvedRole}" not in allowed list [${allowedRoles.join(', ')}]`);
    return <Navigate to="/unauthorized" replace />;
  }

  console.log('[RequireAuth] Access granted.');
  return children;
};

export default RequireAuth;
