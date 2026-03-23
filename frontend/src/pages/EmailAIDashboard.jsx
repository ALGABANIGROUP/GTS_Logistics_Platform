/* eslint-disable react/prop-types */
import { useEffect, useState } from "react";
import StatsCards from "../components/email/StatsCards.jsx";
import {
  getEmailBotStats,
  getEmailDecisionStats,
  getEmailSentimentTrends,
} from "../api/emailStatsApi.js";

const panelClass =
  "rounded-2xl border border-white/10 bg-white/5 p-4 shadow-[0_12px_40px_rgba(15,23,42,0.18)]";

export default function EmailAIDashboard({ embedded = false }) {
  const [botStats, setBotStats] = useState(null);
  const [trends, setTrends] = useState(null);
  const [decisions, setDecisions] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    const load = async () => {
      try {
        setLoading(true);
        setError("");
        const [botsPayload, trendsPayload, decisionsPayload] = await Promise.all([
          getEmailBotStats(),
          getEmailSentimentTrends(),
          getEmailDecisionStats(),
        ]);
        if (!active) return;
        setBotStats(botsPayload);
        setTrends(trendsPayload);
        setDecisions(decisionsPayload);
      } catch (err) {
        if (!active) return;
        setError(err?.response?.data?.detail || err?.message || "Failed to load AI dashboard.");
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    };
    load();
    return () => {
      active = false;
    };
  }, []);

  if (loading) {
    return (
      <div className={panelClass}>
        <div className="text-sm text-slate-300">Loading AI routing dashboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-2xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-100">
        {error}
      </div>
    );
  }

  return (
    <div className={`space-y-4 ${embedded ? "" : "p-4"}`}>
      {!embedded ? (
        <div>
          <div className="text-2xl font-semibold text-white">Email AI Dashboard</div>
          <div className="text-sm text-slate-300">
            Monitor routing quality, sentiment trends, and learning signals.
          </div>
        </div>
      ) : null}

      <StatsCards botStats={botStats} trends={trends} decisions={decisions} />

      <div className="grid gap-4 xl:grid-cols-[1.2fr_0.8fr]">
        <section className={panelClass}>
          <div className="flex items-center justify-between">
            <div>
              <div className="text-lg font-semibold text-white">Bot Performance</div>
              <div className="text-xs text-slate-400">Accuracy, volume, and confidence per bot.</div>
            </div>
          </div>
          <div className="mt-4 overflow-x-auto">
            <table className="min-w-full text-left text-sm text-slate-200">
              <thead className="text-xs uppercase tracking-[0.16em] text-slate-400">
                <tr>
                  <th className="pb-2 pr-3">Bot</th>
                  <th className="pb-2 pr-3">Feedback</th>
                  <th className="pb-2 pr-3">Accuracy</th>
                  <th className="pb-2 pr-3">Avg Rating</th>
                  <th className="pb-2">Confidence</th>
                </tr>
              </thead>
              <tbody>
                {(botStats?.bots || []).map((item) => (
                  <tr key={item.bot_key} className="border-t border-white/5">
                    <td className="py-3 pr-3 font-medium text-white">{item.bot_key}</td>
                    <td className="py-3 pr-3">{item.feedback_count}</td>
                    <td className="py-3 pr-3">{Math.round((item.accuracy_rate || 0) * 100)}%</td>
                    <td className="py-3 pr-3">{item.average_rating?.toFixed?.(2) || item.average_rating}</td>
                    <td className="py-3">{Math.round((item.average_routing_confidence || 0) * 100)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className={panelClass}>
          <div className="text-lg font-semibold text-white">Sentiment Trends</div>
          <div className="mt-4 grid gap-3">
            {Object.entries(trends?.sentiment || {}).map(([label, count]) => (
              <div key={label} className="flex items-center justify-between rounded-xl border border-white/10 bg-slate-900/50 px-3 py-2">
                <span className="text-sm capitalize text-slate-200">{label}</span>
                <span className="text-sm font-semibold text-white">{count}</span>
              </div>
            ))}
          </div>
          <div className="mt-5 text-xs text-slate-400">
            Dominant category: <span className="text-slate-200">{trends?.summary?.dominant_category || "general"}</span>
          </div>
        </section>
      </div>

      <div className="grid gap-4 xl:grid-cols-[0.9fr_1.1fr]">
        <section className={panelClass}>
          <div className="text-lg font-semibold text-white">Decision Matrix</div>
          <div className="mt-4 space-y-2">
            {Object.entries(decisions?.decision_counts || {}).map(([source, count]) => (
              <div key={source} className="flex items-center justify-between rounded-xl border border-white/10 bg-slate-900/50 px-3 py-2">
                <span className="text-sm text-slate-200">{source}</span>
                <span className="text-sm font-semibold text-white">{count}</span>
              </div>
            ))}
          </div>
          <div className="mt-5 grid gap-2 md:grid-cols-3">
            {Object.entries(decisions?.confidence_buckets || {}).map(([bucket, count]) => (
              <div key={bucket} className="rounded-xl border border-white/10 bg-slate-900/50 px-3 py-2 text-center">
                <div className="text-xs uppercase tracking-[0.14em] text-slate-400">{bucket}</div>
                <div className="mt-1 text-xl font-semibold text-white">{count}</div>
              </div>
            ))}
          </div>
        </section>

        <section className={panelClass}>
          <div className="text-lg font-semibold text-white">Recommendations</div>
          <div className="mt-4 space-y-3">
            {(decisions?.recommendations || []).map((item) => (
              <div key={item} className="rounded-xl border border-sky-400/20 bg-sky-500/10 px-3 py-3 text-sm text-sky-100">
                {item}
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
