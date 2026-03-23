import React, { useEffect, useMemo, useState } from "react";
import axiosClient from "../api/axiosClient";
import { useCurrencyStore } from "../stores/useCurrencyStore";

const FinanceAIAnalysis = () => {
  const [aiSummary, setAiSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    runAIAnalysis();
  }, []);

  const runAIAnalysis = async () => {
    setLoading(true);
    setError("");
    setAiSummary(null);
    try {
      const res = await axiosClient.post("/api/v1/ai/bots/available/finance_bot/run", {});
      if (res.data && res.data.ok && res.data.summary) {
        setAiSummary(res.data.summary);
      } else {
        setError("AI response did not contain a summary.");
      }
    } catch (err) {
      console.error("AI analysis error:", err);
      setError("Failed to run AI finance analysis.");
    } finally {
      setLoading(false);
    }
  };

  const formatAmount = (value) => {
    if (value === null || value === undefined || Number.isNaN(Number(value))) {
      return "-";
    }
    const store = useCurrencyStore.getState();
    return store.formatAmount(Number(value));
  };

  const computed = useMemo(() => {
    const totalRevenue = aiSummary?.total_revenue ?? aiSummary?.totalRevenue ?? 0;
    const totalExpenses = aiSummary?.total_expenses ?? aiSummary?.totalExpenses ?? 0;
    const netProfit = aiSummary?.net_profit ?? aiSummary?.netProfit ?? 0;
    return {
      totalRevenue: Number(totalRevenue || 0),
      totalExpenses: Number(totalExpenses || 0),
      netProfit: Number(netProfit || 0),
    };
  }, [aiSummary]);

  const cardClass =
    "bg-white rounded-xl border border-slate-200 shadow-sm p-5 text-slate-900";
  const cardTitleClass = "text-sm font-semibold text-slate-900 mb-2";
  const labelClass = "text-xs text-slate-500";
  const valueClass = "text-xl font-semibold text-slate-900";

  return (
    <div className="px-8 py-6 max-w-6xl mx-auto space-y-4">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-white">AI Finance Analysis</h1>
          <p className="text-sm text-slate-200 mt-1">
            AI-generated summary and breakdowns from finance bot.
          </p>
        </div>

        <button
          onClick={runAIAnalysis}
          disabled={loading}
          className="px-4 py-2 rounded-lg bg-sky-700 text-white text-sm hover:bg-sky-800 disabled:opacity-60 transition"
        >
          {loading ? "Running..." : "Run Again"}
        </button>
      </div>

      <div className={cardClass}>
        {loading && <p className="text-slate-500 text-sm">Running AI analysis...</p>}

        {error && <p className="text-rose-700 text-sm mb-2">{error}</p>}

        {!loading && !error && !aiSummary && (
          <p className="text-slate-500 text-sm">No AI summary available yet.</p>
        )}

        {aiSummary && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
                <p className={labelClass}>Total Revenue</p>
                <p className={valueClass}>
                  ${formatAmount(computed.totalRevenue)}
                </p>
              </div>

              <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
                <p className={labelClass}>Total Expenses</p>
                <p className={valueClass}>
                  ${formatAmount(computed.totalExpenses)}
                </p>
              </div>

              <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
                <p className={labelClass}>Net Profit</p>
                <p
                  className={`text-xl font-semibold ${computed.netProfit >= 0 ? "text-emerald-700" : "text-rose-700"
                    }`}
                >
                  ${formatAmount(computed.netProfit)}
                </p>
              </div>
            </div>

            {aiSummary.by_category && (
              <div>
                <h2 className={cardTitleClass}>Breakdown by Category</h2>
                <ul className="list-disc pl-5 text-sm text-slate-700">
                  {Object.entries(aiSummary.by_category).map(([cat, amt]) => (
                    <li key={cat}>
                      <span className="font-medium text-slate-900">{cat}:</span>{" "}
                      ${formatAmount(amt)}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {aiSummary.note && (
              <p className="text-xs text-slate-500 italic">{aiSummary.note}</p>
            )}

            <div>
              <h2 className="text-xs font-semibold mb-1 text-slate-700">
                Raw AI Summary (JSON)
              </h2>
              <pre className="text-xs bg-slate-50 p-3 rounded-xl border border-slate-200 overflow-auto max-h-60 text-slate-800">
                {JSON.stringify(aiSummary, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FinanceAIAnalysis;
