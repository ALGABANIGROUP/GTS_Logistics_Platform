import React, { useMemo } from "react";
import { useAuth } from "../contexts/AuthContext.jsx";

const LoadingMessage = () => (
  <div className="flex justify-center items-center h-32">
    <div className="text-sm text-slate-300">Checking feature access...</div>
  </div>
);

export default function RequireFeature({
  children,
  featureKey,
  featureKeys,
  mode = "any",
  fallback,
}) {
  const { loading, features, authMeta, role, user } = useAuth();

  const required = useMemo(() => {
    const list = Array.isArray(featureKeys) ? [...featureKeys] : [];
    if (featureKey) {
      list.push(featureKey);
    }
    return list.filter(Boolean);
  }, [featureKey, featureKeys]);

  if (loading) {
    return <LoadingMessage />;
  }

  if (required.length === 0) {
    return <>{children}</>;
  }

  const effectiveRole = (role || user?.role || "").toString().toLowerCase();
  if (effectiveRole === "super_admin") {
    return <>{children}</>;
  }

  // Combine features and bots for checking
  const featureSet = new Set(features || []);
  const bots = authMeta?.bots || [];
  bots.forEach(bot => featureSet.add(bot));

  const allowed =
    mode === "all"
      ? required.every((key) => featureSet.has(key))
      : required.some((key) => featureSet.has(key));

  if (!allowed) {
    if (fallback) return fallback;
    return null;
  }

  return <>{children}</>;
}
