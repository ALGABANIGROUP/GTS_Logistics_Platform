import { Navigate } from "react-router-dom";
import PropTypes from "prop-types";
import { readAuthToken } from "./authStorage";
import { getUserRole } from "./userRole";

// ✅ Protected Route: Prevents access unless token exists
const ProtectedRoute = ({ children }) => {
  const token = readAuthToken();
  const storedUserRaw =
    typeof window !== "undefined" ? localStorage.getItem("user") : null;
  let storedUser = null;
  if (storedUserRaw) {
    try {
      storedUser = JSON.parse(storedUserRaw);
    } catch {
      storedUser = null;
    }
  }
  const role = getUserRole(storedUser);

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  // ❗ Only admins can access the Dev & Maintenance area
  const currentPath = window.location.pathname;
  const isAdmin = role.includes("admin") || role.includes("super");
  if (currentPath.startsWith("/dev") && !isAdmin) {
    return <Navigate to="/unauthorized" replace />;
  }

  return children;
};

ProtectedRoute.propTypes = {
  children: PropTypes.node.isRequired,
};

export default ProtectedRoute;
