import React from "react";
import RequireAuth from "../../components/RequireAuth.jsx";
import StrategyAdvisorPanel from "../../components/bots/panels/strategy-advisor/StrategyAdvisor";

export default function StrategyAdvisor() {
  return (
    <RequireAuth roles={["admin", "owner", "super_admin"]}>
      <StrategyAdvisorPanel />
    </RequireAuth>
  );
}
