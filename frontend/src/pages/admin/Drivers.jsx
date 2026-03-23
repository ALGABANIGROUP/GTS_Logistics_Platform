import React from "react";
import RequireAuth from "../../components/RequireAuth.jsx";
import DriversPage from "../Drivers.jsx";

export default function AdminDrivers() {
  return (
    <RequireAuth roles={["admin", "owner", "super_admin"]}>
      <DriversPage />
    </RequireAuth>
  );
}
