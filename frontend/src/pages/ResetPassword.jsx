import React, { useMemo, useState, useRef, useEffect } from "react";
import { useLocation, Link, useNavigate } from "react-router-dom";
import AuthLayout from "@/components/AuthLayout";
import { useAuth } from "../contexts/AuthContext";

const ResetPassword = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const redirectTimerRef = useRef(null);
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const [done, setDone] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const { resetPassword, loading } = useAuth();

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
      const result = await resetPassword(token, password);
      if (result.success) {
        setDone(true);
        setStatus("Password reset successfully. Redirecting to login...");
        setPassword("");
        setConfirmPassword("");
        redirectTimerRef.current = setTimeout(() => {
          navigate("/login", { replace: true });
        }, 1500);
      }
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
        err?.message ||
        "Failed to reset password."
      );
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
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                value={password}
                required
                minLength={8}
                onChange={(e) => setPassword(e.target.value)}
                disabled={done || loading}
                className="w-full rounded-lg border border-slate-500/60 bg-slate-900/60 px-3.5 py-2.5 text-sm text-slate-50 placeholder:text-slate-400 focus:border-sky-400 focus:outline-none focus:ring-2 focus:ring-sky-500/60 pr-12"
                placeholder="********"
              />
              <button
                type="button"
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200 text-xs"
                tabIndex={-1}
                onClick={() => setShowPassword((v) => !v)}
              >
                {showPassword ? "Hide" : "Show"}
              </button>
            </div>
          </div>
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-slate-200">
              Confirm password
            </label>
            <div className="relative">
              <input
                type={showConfirm ? "text" : "password"}
                value={confirmPassword}
                required
                minLength={8}
                onChange={(e) => setConfirmPassword(e.target.value)}
                disabled={done || loading}
                className="w-full rounded-lg border border-slate-500/60 bg-slate-900/60 px-3.5 py-2.5 text-sm text-slate-50 placeholder:text-slate-400 focus:border-sky-400 focus:outline-none focus:ring-2 focus:ring-sky-500/60 pr-12"
                placeholder="********"
              />
              <button
                type="button"
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200 text-xs"
                tabIndex={-1}
                onClick={() => setShowConfirm((v) => !v)}
              >
                {showConfirm ? "Hide" : "Show"}
              </button>
            </div>
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
