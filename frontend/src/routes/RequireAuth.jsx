import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext.jsx";

/**
 * Route-guard for React Router v6 nested routes.
 * Usage:
 * <Route element={<RequireAuth roles={["admin"]} />}>
 *   <Route path="/dashboard" element={<Dashboard />} />
 * </Route>
 */
export default function RequireAuth({ roles }) {
  const { user, loading, isAuthenticated, accountStatus } = useAuth();
  const location = useLocation();

  if (loading) return null; // or Spinner

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  if (accountStatus && accountStatus !== "active") {
    return <Navigate to="/account-inactive" replace />;
  }

  // Optional roles guard
  if (roles?.length) {
    const userRole = user?.effective_role || user?.role;
    const userRoles = user?.roles || (userRole ? [userRole] : []);
    const allowed = roles.some((r) => userRoles.includes(r));
    if (!allowed) return <Navigate to="/403" replace />;
  }

  return <Outlet />;
}
