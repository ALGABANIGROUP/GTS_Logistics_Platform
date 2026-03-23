// frontend/src/utils/RoleProtectedRoute.jsx

import { Navigate } from "react-router-dom";
import PropTypes from "prop-types";
import { readAuthToken } from "./authStorage";
import { getUserRole } from "./userRole";

const RoleProtectedRoute = ({ children, allowedRoles }) => {
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
  const normalizedAllowed = (allowedRoles || []).map((r) =>
    String(r || "").toLowerCase()
  );
  const isAdmin = role.includes("admin") || role.includes("super");
  const allowsAdmin =
    normalizedAllowed.includes("admin") ||
    normalizedAllowed.includes("super_admin") ||
    normalizedAllowed.includes("super");

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  if (normalizedAllowed.length === 0) {
    return children;
  }

  if (normalizedAllowed.includes(role)) {
    return children;
  }

  if (isAdmin && allowsAdmin) {
    return children;
  }

  return <Navigate to="/unauthorized" replace />;
};

RoleProtectedRoute.propTypes = {
  children: PropTypes.node.isRequired,
  allowedRoles: PropTypes.arrayOf(PropTypes.string).isRequired,
};

export default RoleProtectedRoute;
