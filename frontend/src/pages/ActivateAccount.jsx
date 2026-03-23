import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axiosClient from "../api/axiosClient";

export default function ActivateAccount() {
  const { token } = useParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState("pending"); // pending | success | error
  const [message, setMessage] = useState("Activating your account...");

  useEffect(() => {
    const verify = async () => {
      try {
        await axiosClient.post(`/api/v1/auth/verify/${token}`);
        setStatus("success");
        setMessage("Account activated successfully! You can now sign in.");
        setTimeout(() => navigate("/login"), 1500);
      } catch (err) {
        setStatus("error");
        if (err?.response?.data?.detail) {
          setMessage(err.response.data.detail);
        } else {
          setMessage("An error occurred while verifying your account.");
        }
      }
    };
    if (token) verify();
  }, [token, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-950 text-white px-4">
      <div className="max-w-md w-full rounded-2xl border border-white/15 bg-white/5 backdrop-blur-xl p-6 text-center space-y-3">
        <h1 className="text-xl font-semibold">Account Activation</h1>
        <p className={status === "success" ? "text-emerald-300" : status === "error" ? "text-rose-300" : "text-slate-200"}>
          {message}
        </p>
        {status === "error" && (
          <button
            onClick={() => navigate("/login")}
            className="mt-2 inline-flex items-center justify-center rounded-lg border border-white/20 bg-white/10 px-4 py-2 text-sm font-semibold hover:bg-white/15"
          >
            Back to Login
          </button>
        )}
      </div>
    </div>
  );
}
