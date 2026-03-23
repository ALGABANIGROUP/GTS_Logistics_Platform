import React, { useMemo, useState, useRef, useEffect } from "react";
import { useLocation, Link, useNavigate } from "react-router-dom";
import AuthLayout from "@/components/AuthLayout";
import axiosClient from "../api/axiosClient.js";

const ResetPassword = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const redirectTimerRef = useRef(null);
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);

  const token = useMemo(() => {
    const params = new URLSearchParams(location.search);
    const rawHash = location.hash?.startsWith("#")
      ? location.hash.slice(1)
      : location.hash;
    const hashParams = new URLSearchParams(rawHash || "");
    return (
      params.get("token") ||
      params.get("reset_token") ||
      params.get("reset") ||
      hashParams.get("token") ||
      hashParams.get("reset_token") ||
      hashParams.get("reset") ||
      ""
    );
  }, [location.search, location.hash]);

  useEffect(() => {
    return () => {
      if (redirectTimerRef.current) {
        clearTimeout(redirectTimerRef.current);
      }
    };
  }, []);

  const PASSWORD_POLICY_REGEX =
    /^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+=\[\]{};':",.<>/?\\|`~\-]).{8,}$/;
  const PASSWORD_POLICY_HINT =
    "Password must be at least 8 characters and include an uppercase letter, a number, and a symbol.";

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setStatus("");

    if (done || loading) {
      return;
    }

    if (!token) {
      setError("Reset token is missing.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    if (!PASSWORD_POLICY_REGEX.test(password)) {
      setError(PASSWORD_POLICY_HINT);
      return;
    }

    try {
      setLoading(true);
      await axiosClient.post("/api/v1/auth/reset-password", {
        token,
        new_password: password,
      });
      setDone(true);
      setStatus("Password reset successfully. Redirecting to login...");
      setPassword("");
      setConfirmPassword("");
      redirectTimerRef.current = setTimeout(() => {
        navigate("/login", { replace: true });
      }, 1500);
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          err?.message ||
          "Failed to reset password."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout
      title="Create a new password"
      subtitle="Enter a new secure password for your GTS account."
      footer="Reset links expire after a short period. If yours expired, request a new one from the forgot password page."
    >
      <div className="max-w-md space-y-5">
        {status && (
          <div className="rounded-lg border border-emerald-500/60 bg-emerald-500/10 px-3.5 py-2.5 text-xs text-emerald-100 shadow-sm">
            {status}
          </div>
        )}
        {error && (
          <div className="rounded-lg border border-rose-500/60 bg-rose-500/10 px-3.5 py-2.5 text-xs text-rose-100 shadow-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-slate-200">
              New password
            </label>
            <input
              type="password"
              value={password}
              required
              minLength={8}
              onChange={(e) => setPassword(e.target.value)}
              disabled={done || loading}
              className="w-full rounded-lg border border-slate-500/60 bg-slate-900/60 px-3.5 py-2.5 text-sm text-slate-50 placeholder:text-slate-400 focus:border-sky-400 focus:outline-none focus:ring-2 focus:ring-sky-500/60"
              placeholder="********"
            />
          </div>
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-slate-200">
              Confirm password
            </label>
            <input
              type="password"
              value={confirmPassword}
              required
              minLength={8}
              onChange={(e) => setConfirmPassword(e.target.value)}
              disabled={done || loading}
              className="w-full rounded-lg border border-slate-500/60 bg-slate-900/60 px-3.5 py-2.5 text-sm text-slate-50 placeholder:text-slate-400 focus:border-sky-400 focus:outline-none focus:ring-2 focus:ring-sky-500/60"
              placeholder="********"
            />
          </div>
          <div className="rounded-lg border border-slate-700/60 bg-slate-900/60 px-3.5 py-2.5 text-[11px] text-slate-300">
            {PASSWORD_POLICY_HINT}
          </div>

          <button
            type="submit"
            disabled={done || loading}
            className="flex w-full items-center justify-center rounded-lg bg-sky-500 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-sky-500/40 transition hover:bg-sky-600 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? "Resetting..." : "Reset password"}
          </button>
        </form>

        <p className="text-[11px] text-slate-300/90">
          Back to{" "}
          <Link to="/login" className="text-sky-300 hover:text-sky-200">
            login
          </Link>
          .
        </p>
      </div>
    </AuthLayout>
  );
};

export default ResetPassword;
