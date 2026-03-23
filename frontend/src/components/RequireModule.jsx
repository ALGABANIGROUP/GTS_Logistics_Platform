import React from "react";
import { useAuth } from "../contexts/AuthContext.jsx";

const defaultMessage =
  "Module not available for your plan. Please contact your administrator.";

const LoadingMessage = () => (
  <div className="flex justify-center items-center h-32">
    <div className="text-sm text-slate-300">Checking module access...</div>
  </div>
);

export default function RequireModule({ children, moduleKey, fallback }) {
  const { loading, modules } = useAuth();

  if (loading) {
    return <LoadingMessage />;
  }

  if (!moduleKey) {
    return <>{children}</>;
  }

  const allowed = Boolean(modules && modules[moduleKey]);
  if (!allowed) {
    return (
      fallback || (
        <div className="rounded-2xl border border-amber-400/30 bg-amber-500/10 px-5 py-4 text-sm text-amber-100">
          {defaultMessage}
        </div>
      )
    );
  }

  return <>{children}</>;
}
