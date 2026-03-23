import React from "react";
import CustomerServiceChat from "../components/CustomerServiceChat";
import { useAuth } from "../contexts/AuthContext";

const CustomerServiceDemo = () => {
  const { user } = useAuth();

  return (
    <div className="mx-auto max-w-5xl p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-white">Customer Service Learning Demo</h1>
        <p className="mt-2 text-slate-400">
          This chat records response performance, errors, and user feedback for the
          `customer_service` learning profile.
        </p>
      </div>

      <CustomerServiceChat userId={user?.id || "guest"} />

      <div className="mt-6 rounded-2xl border border-slate-700 bg-slate-800/50 p-4 text-sm text-slate-300">
        Each reply can produce learning samples in three categories: performance,
        error handling, and explicit user feedback.
      </div>
    </div>
  );
};

export default CustomerServiceDemo;
