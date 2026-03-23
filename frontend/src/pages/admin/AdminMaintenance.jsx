import React from "react";
import RequireAuth from "../../components/RequireAuth.jsx";
import MaintenanceDashboard from "./MaintenanceDashboard";

export default function AdminMaintenance() {
  return (
    <RequireAuth roles={["admin", "owner", "super_admin"]}>
      <MaintenanceDashboard />
    </RequireAuth>
  );
}
