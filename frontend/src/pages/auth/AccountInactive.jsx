import React from "react";
import { Navigate, useNavigate } from "react-router-dom";
import AuthLayout from "../../layouts/AuthLayout.jsx";
import GlassCard from "../../components/ui/GlassCard.jsx";
import { useAuth } from "../../contexts/AuthContext.jsx";

export default function AccountInactive() {
  const navigate = useNavigate();
  const { authReady, isAuthenticated, accountStatus } = useAuth();

  if (!authReady) return <div className="min-h-screen" aria-busy="true" />;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (accountStatus === "active") return <Navigate to="/dashboard" replace />;

  const title =
    accountStatus === "suspended"
      ? "Account suspended"
      : "Request received";
  const message =
    accountStatus === "suspended"
      ? "Your account has been suspended. Please contact support."
      : "Your access request is pending approval. We'll notify you by email.";

  return (
    <AuthLayout>
      <div className="w-full max-w-xl px-4">
        <GlassCard className="w-full text-center bg-[#0f0f0f]/85 border-white/15 backdrop-blur-none shadow-[0_20px_50px_rgba(0,0,0,0.45)]">
          <h1 className="text-white text-xl font-semibold">{title}</h1>
          <p className="text-white/70 text-sm mt-2">{message}</p>
          <button
            type="button"
            className="mt-6 w-full rounded-xl bg-black/30 hover:bg-black/40 text-white font-semibold py-3 border border-white/20 transition"
            onClick={() => navigate("/")}
          >
            Back to Portal
          </button>
        </GlassCard>
      </div>
    </AuthLayout>
  );
}
