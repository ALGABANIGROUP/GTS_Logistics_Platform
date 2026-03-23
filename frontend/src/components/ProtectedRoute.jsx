import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const ProtectedRoute = ({ children, allowedSystems = [] }) => {
  const { user, authReady, isAuthenticated, accountStatus } = useAuth();
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

  // Check system authorization
  if (allowedSystems.length > 0 && !allowedSystems.includes(user.system)) {
    return <Navigate to="/" replace />;
  }

  return children;
};

export default ProtectedRoute;
