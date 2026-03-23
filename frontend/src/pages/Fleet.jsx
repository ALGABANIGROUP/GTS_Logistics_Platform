import React, { useEffect, useState } from "react";
import axiosClient from "../api/axiosClient";
import { Link } from "react-router-dom";
import { useCurrencyStore } from "../stores/useCurrencyStore";

const Finance = () => {
  const [summary, setSummary] = useState(null);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [summaryError, setSummaryError] = useState("");

  const [recentExpenses, setRecentExpenses] = useState([]);
  const [expensesLoading, setExpensesLoading] = useState(false);
  const [expensesError, setExpensesError] = useState("");

  useEffect(() => {
    fetchSummary();
    fetchRecentExpenses();
  }, []);

  const fetchSummary = async () => {
    setSummaryLoading(true);
    setSummaryError("");
    try {
      const res = await axiosClient.get("/finance/summary");
      setSummary(res.data);
    } catch (err) {
      console.error("Failed to fetch finance summary:", err);
      setSummary(null);
      setSummaryError("Failed to load finance summary.");
    } finally {
      setSummaryLoading(false);
    }
  };

  const fetchRecentExpenses = async () => {
    setExpensesLoading(true);
    setExpensesError("");
    try {
      const res = await axiosClient.get("/finance/expenses");
      if (Array.isArray(res.data)) {
        const sorted = [...res.data].sort((a, b) => {
          const da = new Date(a.created_at || a.createdAt || 0).getTime();
          const db = new Date(b.created_at || b.createdAt || 0).getTime();
          return db - da;
        });
        setRecentExpenses(sorted.slice(0, 10));
      } else {
        setRecentExpenses([]);
      }
    } catch (err) {
      console.error("Failed to fetch expenses:", err);
      setRecentExpenses([]);
      setExpensesError("Failed to load expenses.");
    } finally {
      setExpensesLoading(false);
    }
  };

  const formatAmount = (value) => {
    if (value === null || value === undefined || Number.isNaN(Number(value))) {
      return "-";
    }
    const store = useCurrencyStore.getState();
    return store.formatAmount(Number(value));
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between gap-4">
        <h1 className="text-2xl font-bold">Finance Overview</h1>
        <div className="flex gap-2 text-sm">
          <Link
            to="/finance/platform-expenses"
            className="px-3 py-1.5 rounded border border-gray-300 hover:bg-gray-50"
          >
            Manage Expenses
          </Link>
          <Link
            to="/finance/ai-analysis"
            className="px-3 py-1.5 rounded bg-blue-600 text-white hover:bg-blue-700"
          >
            AI Finance Analysis
          </Link>
        </div>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="text-sm text-gray-500 mb-1">Total Revenue</h2>
          {summaryLoading ? (
            <p className="text-gray-400 text-sm">Loading...</p>
          ) : summaryError ? (
            <p className="text-red-500 text-sm">{summaryError}</p>
          ) : (
            <p className="text-2xl font-semibold">
              ${formatAmount(summary?.total_revenue ?? summary?.totalRevenue)}
            </p>
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="text-sm text-gray-500 mb-1">Total Expenses</h2>
          {summaryLoading ? (
            <p className="text-gray-400 text-sm">Loading...</p>
          ) : summaryError ? (
            <p className="text-red-500 text-sm">{summaryError}</p>
          ) : (
            <p className="text-2xl font-semibold">
              ${formatAmount(summary?.total_expenses ?? summary?.totalExpenses)}
            </p>
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="text-sm text-gray-500 mb-1">Net Profit</h2>
          {summaryLoading ? (
            <p className="text-gray-400 text-sm">Loading...</p>
          ) : summaryError ? (
            <p className="text-red-500 text-sm">{summaryError}</p>
          ) : (
            <p
              className={`text-2xl font-semibold ${(summary?.net_profit ?? summary?.netProfit ?? 0) >= 0
                ? "text-green-600"
                : "text-red-600"
                }`}
            >
              $
              {formatAmount(summary?.net_profit ?? summary?.netProfit ?? 0)}
            </p>
          )}
        </div>
      </div>

      {/* Raw summary box (debug / advanced) */}
      {summary && (
        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="text-sm font-semibold mb-2">Raw Summary (JSON)</h2>
          <pre className="text-xs bg-gray-50 p-3 rounded overflow-auto max-h-60">
            {JSON.stringify(summary, null, 2)}
          </pre>
        </div>
      )}

      {/* Recent expenses */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold">Recent Expenses</h2>
          <button
            onClick={fetchRecentExpenses}
            className="text-xs px-2 py-1 rounded border border-gray-300 hover:bg-gray-50"
          >
            Refresh
          </button>
        </div>

        {expensesLoading ? (
          <p className="text-gray-400 text-sm">Loading expenses...</p>
        ) : expensesError ? (
          <p className="text-red-500 text-sm">{expensesError}</p>
        ) : recentExpenses.length === 0 ? (
          <p className="text-gray-500 text-sm">No expenses found.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full border text-sm">
              <thead className="bg-gray-100">
                <tr>
                  <th className="border px-3 py-1 text-left">Vendor</th>
                  <th className="border px-3 py-1 text-left">Description</th>
                  <th className="border px-3 py-1 text-left">Category</th>
                  <th className="border px-3 py-1 text-left">Created At</th>
                  <th className="border px-3 py-1 text-right">Amount</th>
                  <th className="border px-3 py-1 text-center">Status</th>
                </tr>
              </thead>
              <tbody>
                {recentExpenses.map((exp) => (
                  <tr key={exp.id}>
                    <td className="border px-3 py-1">{exp.vendor}</td>
                    <td className="border px-3 py-1">
                      {exp.description || "-"}
                    </td>
                    <td className="border px-3 py-1">
                      {exp.category || "misc"}
                    </td>
                    <td className="border px-3 py-1">
                      {exp.created_at
                        ? exp.created_at.slice(0, 10)
                        : "-"}
                    </td>
                    <td className="border px-3 py-1 text-right">
                      ${formatAmount(exp.amount)}
                    </td>
                    <td className="border px-3 py-1 text-center">
                      <span
                        className={`px-2 py-0.5 rounded text-xs ${exp.status === "PAID"
                          ? "bg-green-100 text-green-700"
                          : "bg-yellow-100 text-yellow-800"
                          }`}
                      >
                        {exp.status || "PENDING"}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="mt-3 text-right text-xs text-gray-500">
          For full editing, go to{" "}
          <Link to="/finance/platform-expenses" className="underline">
            Platform Expenses
          </Link>
          .
        </div>
      </div>
    </div>
  );
};

export default Finance;
