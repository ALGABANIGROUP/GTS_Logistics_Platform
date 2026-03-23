// frontend/src/pages/ForgotPassword.jsx
import React, { useState } from "react";
import { Link } from "react-router-dom";
import AuthLayout from "@/components/AuthLayout";
import { useAuth } from "../contexts/AuthContext";

const ForgotPassword = () => {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState("");
  const { forgotPassword, loading } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus("");

    try {
      const result = await forgotPassword(email);
      if (result.success) {
        setStatus(
          "If this email is registered, you will receive reset instructions shortly."
        );
      }
    } catch (err) {
      setStatus(
        "If this email is registered, you will receive reset instructions shortly."
      );
    }
  };

  return (
    <AuthLayout
      title="Reset your password"
      subtitle="Enter the email associated with your GTS account. We will send you a secure link to reset your password."
      footer="For security reasons, password reset links expire after a short period. If your link expires, you can always request a new one from this page."
    >
      <div className="max-w-md space-y-5">
        {status && (
          <div className="rounded-lg border border-emerald-500/60 bg-emerald-500/10 px-3.5 py-2.5 text-xs text-emerald-100 shadow-sm">
            {status}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-slate-200">
              Registered email
            </label>
            <input
              type="email"
              value={email}
              required
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-lg border border-slate-500/60 bg-slate-900/60 px-3.5 py-2.5 text-sm text-slate-50 placeholder:text-slate-400 focus:border-sky-400 focus:outline-none focus:ring-2 focus:ring-sky-500/60"
              placeholder="you@company.com"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="flex w-full items-center justify-center rounded-lg bg-sky-500 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-sky-500/40 transition hover:bg-sky-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? "Sending..." : "Send reset link"}
          </button>
        </form>

        <p className="text-[11px] text-slate-300/90">
          Remembered your password?{" "}
          <Link to="/login" className="text-sky-300 hover:text-sky-200">
            Back to login
          </Link>
        </p>
      </div>
    </AuthLayout>
  );
};

export default ForgotPassword;
