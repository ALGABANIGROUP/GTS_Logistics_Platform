import React, { useEffect, useMemo, useState } from "react";
import axiosClient from "../api/axiosClient";
import { useRefreshSubscription } from "../contexts/UiActionsContext.jsx";

function formatDate(value) {
  if (!value) return "";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return String(value);
  return d.toLocaleDateString();
}

export default function PlatformExpenses() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const loadExpenses = async () => {
    setLoading(true);
    setError("");

    try {
      const res = await axiosClient.get("/finance/expenses");
      const data = res.data;

      const list = Array.isArray(data) ? data : Array.isArray(data?.items) ? data.items : [];
      setItems(list);
    } catch (err) {
      const n = err?.normalized;
      const status = n?.status;

      if (status === 401) {
        setError("Unauthorized (401). Token is missing or invalid in axiosClient.");
        setItems([]);
      } else if (status === 403) {
        setError("Forbidden (403). Role does not allow access to expenses.");
        setItems([]);
      } else if (status === 404) {
        setItems([]);
      } else if (status >= 500) {
        setError(`Server error (${status || "500"}). Please check backend logs.`);
        setItems([]);
      } else {
        setError(n?.detail || "Failed to load expenses.");
        setItems([]);
      }

    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadExpenses();
  }, []);

  useRefreshSubscription(() => {
    loadExpenses();
  });

  const total = useMemo(() => {
    if (!Array.isArray(items)) return 0;
    return items.reduce((sum, x) => sum + Number(x?.amount || 0), 0);
  }, [items]);

  return (
    <div className="px-8 py-6 max-w-6xl mx-auto">
      <div className="flex items-start justify-between gap-4 mb-5">
        <div>
          <h1 className="text-2xl font-semibold text-white">Platform Expenses</h1>
          <p className="text-sm text-slate-200 mt-1">
            Operational and platform-level expenses pulled from /finance/expenses.
          </p>
        </div>

        <button
          type="button"
          onClick={loadExpenses}
          disabled={loading}
          className="px-3 py-2 rounded-lg text-xs font-medium border border-slate-600 text-slate-100 hover:bg-white/10 disabled:opacity-60"
        >
          {loading ? "Refreshing…" : "Refresh"}
        </button>
      </div>

      {error && (
        <div className="mb-4 rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-5">
        <div className="rounded-xl border border-slate-200 bg-white shadow-sm px-4 py-3">
          <p className="text-xs text-slate-500 mb-1">Records</p>
          <p className="text-2xl font-semibold text-slate-900">
            {loading ? "…" : Array.isArray(items) ? items.length : 0}
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white shadow-sm px-4 py-3">
          <p className="text-xs text-slate-500 mb-1">Total Amount</p>
          <p className="text-2xl font-semibold text-slate-900">
            {loading ? "…" : total.toFixed(2)}
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white shadow-sm px-4 py-3">
          <p className="text-xs text-slate-500 mb-1">Status</p>
          <p className="text-sm font-semibold text-slate-700">
            {loading ? "Loading…" : error ? "Error" : "OK"}
          </p>
        </div>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-200">
          <h2 className="text-sm font-semibold text-slate-900">Expenses</h2>
          <p className="text-xs text-slate-500 mt-0.5">Latest records from the finance service.</p>
        </div>

        <div className="p-5">
          {loading ? (
            <div className="text-sm text-slate-500">Loading…</div>
          ) : !items.length ? (
            <div className="text-sm text-slate-500">No expenses found.</div>
          ) : (
            <div className="overflow-auto">
              <table className="min-w-full text-sm">
                <thead>
                  <tr className="text-left text-xs text-slate-500 border-b">
                    <th className="py-2 pr-4">ID</th>
                    <th className="py-2 pr-4">Category</th>
                    <th className="py-2 pr-4">Vendor</th>
                    <th className="py-2 pr-4">Description</th>
                    <th className="py-2 pr-4">Amount</th>
                    <th className="py-2 pr-4">Status</th>
                    <th className="py-2 pr-0">Created</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {items.map((x) => (
                    <tr key={x.id} className="text-slate-700">
                      <td className="py-2 pr-4 font-mono text-xs">{x.id}</td>
                      <td className="py-2 pr-4">{x.category || "-"}</td>
                      <td className="py-2 pr-4">{x.vendor || "-"}</td>
                      <td className="py-2 pr-4">{x.description || "-"}</td>
                      <td className="py-2 pr-4 font-semibold">{Number(x.amount || 0).toFixed(2)}</td>
                      <td className="py-2 pr-4">{x.status || "-"}</td>
                      <td className="py-2 pr-0 text-xs text-slate-500">{formatDate(x.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
