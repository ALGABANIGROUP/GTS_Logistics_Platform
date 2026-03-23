import React, { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import paymentApi from "../../api/paymentApi";

function formatCurrency(value, currency = "SDG") {
  try {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency,
      maximumFractionDigits: 2,
    }).format(Number(value || 0));
  } catch {
    return `${currency} ${Number(value || 0).toFixed(2)}`;
  }
}

export default function SUDAPayBotDashboard() {
  const navigate = useNavigate();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    const loadHistory = async () => {
      setLoading(true);
      setError("");
      try {
        const response = await paymentApi.getUserHistory({ limit: 50, offset: 0 });
        if (!cancelled) {
          setHistory(Array.isArray(response?.items) ? response.items : []);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err?.response?.data?.detail || err?.message || "Failed to load payment history.");
          setHistory([]);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    loadHistory();
    return () => {
      cancelled = true;
    };
  }, []);

  const stats = useMemo(() => {
    const totalAmount = history.reduce((sum, item) => sum + Number(item.amount || 0), 0);
    const completed = history.filter((item) => item.status === "completed");
    const pending = history.filter((item) => item.status === "pending" || item.status === "processing");
    const successRate = history.length ? ((completed.length / history.length) * 100).toFixed(1) : "0.0";
    const defaultCurrency = history[0]?.currency || "SDG";

    return {
      totalAmount,
      totalPayments: history.length,
      pendingPayments: pending.length,
      successRate,
      currency: defaultCurrency,
    };
  }, [history]);

  return (
    <div className="min-h-screen bg-gray-50 p-6 dark:bg-gray-900">
      <div className="mx-auto max-w-7xl">
        <h1 className="mb-2 text-3xl font-bold text-gray-900 dark:text-white">
          💳 SUDAPAY Payment Gateway
        </h1>
        <p className="mb-8 text-gray-600 dark:text-gray-400">
          Secure payment processing, invoice management, and transaction tracking
        </p>

        <div className="mb-8 grid grid-cols-1 gap-6 md:grid-cols-4">
          <div className="rounded-lg bg-white p-6 shadow dark:bg-gray-800">
            <div className="mb-2 text-sm text-gray-500 dark:text-gray-400">Total Processed</div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {formatCurrency(stats.totalAmount, stats.currency)}
            </div>
          </div>
          <div className="rounded-lg bg-white p-6 shadow dark:bg-gray-800">
            <div className="mb-2 text-sm text-gray-500 dark:text-gray-400">Total Payments</div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white">{stats.totalPayments}</div>
          </div>
          <div className="rounded-lg bg-white p-6 shadow dark:bg-gray-800">
            <div className="mb-2 text-sm text-gray-500 dark:text-gray-400">Pending Payments</div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white">{stats.pendingPayments}</div>
          </div>
          <div className="rounded-lg bg-white p-6 shadow dark:bg-gray-800">
            <div className="mb-2 text-sm text-gray-500 dark:text-gray-400">Success Rate</div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white">{stats.successRate}%</div>
          </div>
        </div>

        <div className="mb-8 grid grid-cols-1 gap-6 md:grid-cols-3">
          <button
            onClick={() => navigate("/payments/history")}
            className="rounded-lg bg-blue-600 p-6 text-center text-white transition hover:bg-blue-700"
          >
            <div className="mb-2 text-2xl">📜</div>
            <div className="font-semibold">Transaction History</div>
            <div className="text-sm opacity-90">Review payment activity</div>
          </button>
          <button
            onClick={() => navigate("/ai-bots/finance")}
            className="rounded-lg bg-green-600 p-6 text-center text-white transition hover:bg-green-700"
          >
            <div className="mb-2 text-2xl">💰</div>
            <div className="font-semibold">Finance Bot</div>
            <div className="text-sm opacity-90">Open finance operations</div>
          </button>
          <button
            onClick={() => navigate("/finance/reports")}
            className="rounded-lg bg-purple-600 p-6 text-center text-white transition hover:bg-purple-700"
          >
            <div className="mb-2 text-2xl">📄</div>
            <div className="font-semibold">Finance Reports</div>
            <div className="text-sm opacity-90">View financial reporting</div>
          </button>
        </div>

        <div className="overflow-hidden rounded-lg bg-white shadow dark:bg-gray-800">
          <div className="border-b border-gray-200 px-6 py-4 dark:border-gray-700">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Recent Transactions</h2>
          </div>

          {loading ? (
            <div className="px-6 py-10 text-center text-gray-500 dark:text-gray-400">Loading payment history...</div>
          ) : error ? (
            <div className="px-6 py-10 text-center text-red-500">{error}</div>
          ) : history.length === 0 ? (
            <div className="px-6 py-10 text-center text-gray-500 dark:text-gray-400">
              No payment history found.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-900/40">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Reference</th>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Amount</th>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Gateway</th>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Created</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                  {history.slice(0, 10).map((item) => (
                    <tr key={item.id}>
                      <td className="px-6 py-4 text-sm text-gray-900 dark:text-white">{item.reference_id}</td>
                      <td className="px-6 py-4 text-sm text-gray-700 dark:text-gray-300">
                        {formatCurrency(item.amount, item.currency)}
                      </td>
                      <td className="px-6 py-4 text-sm capitalize text-gray-700 dark:text-gray-300">{item.status}</td>
                      <td className="px-6 py-4 text-sm uppercase text-gray-700 dark:text-gray-300">{item.payment_gateway}</td>
                      <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">{item.created_at}</td>
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
