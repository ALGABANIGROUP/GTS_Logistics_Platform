import React from "react";
import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext.jsx";

export default function PublicOnly() {
  const { isAuthenticated, authReady, accountStatus } = useAuth();
  const location = useLocation();

  if (!authReady) return <Outlet />;

  if (!isAuthenticated) {
    if (location.pathname === "/account-inactive") {
      return <Navigate to="/login" replace />;
    }
    return <Outlet />;
  }

  if (accountStatus && accountStatus !== "active") {
    if (location.pathname !== "/account-inactive") {
      return <Navigate to="/account-inactive" replace />;
    }
    return <Outlet />;
  }

  const params = new URLSearchParams(location.search);
  const next = params.get("next");
  return <Navigate to={next || "/dashboard"} replace />;
}
