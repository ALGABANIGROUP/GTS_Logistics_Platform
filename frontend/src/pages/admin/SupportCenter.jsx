import React, { useEffect, useState } from "react";
import axiosClient from "../../api/axiosClient";

const cardClass =
  "rounded-2xl border border-slate-700/60 bg-slate-900/60 p-5 shadow-2xl shadow-black/40 backdrop-blur-xl";

export default function SupportCenter() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    const loadStats = async () => {
      setLoading(true);
      setError("");
      try {
        const response = await axiosClient.get("/api/v1/support/stats");
        if (!active) return;
        setStats(response.data || null);
      } catch (err) {
        if (!active) return;
        setError(err?.response?.data?.detail || "Failed to load support statistics.");
      } finally {
        if (active) setLoading(false);
      }
    };

    loadStats();
    return () => {
      active = false;
    };
  }, []);

  return (
    <div className="space-y-6 p-6">
      <div className="rounded-2xl border border-blue-500/40 bg-gradient-to-r from-blue-900/60 to-cyan-900/60 p-6 shadow-2xl shadow-black/40 backdrop-blur-xl">
        <h1 className="text-3xl font-bold text-white">Support Center</h1>
        <p className="mt-2 max-w-3xl text-sm text-slate-200">
          Centralized support visibility for ticket flow, response pace, and agent performance.
        </p>
      </div>

      {error ? (
        <div className="rounded-2xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-100">
          {error}
        </div>
      ) : null}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
        {[
          ["Total Tickets", stats?.total_tickets ?? 0],
          ["Open Tickets", stats?.open_tickets ?? 0],
          ["Resolved Today", stats?.resolved_today ?? 0],
          ["Active Agents", stats?.active_agents ?? 0],
        ].map(([label, value]) => (
          <div key={label} className={cardClass}>
            <div className="text-sm text-slate-400">{label}</div>
            <div className="mt-2 text-3xl font-bold text-white">
              {loading ? "..." : value}
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
        <div className={cardClass}>
          <h2 className="text-lg font-semibold text-white">Daily Trend</h2>
          <div className="mt-4 space-y-3">
            {(stats?.daily_stats || []).map((row) => (
              <div
                key={row.date}
                className="flex items-center justify-between rounded-xl border border-white/5 bg-white/5 px-4 py-3 text-sm"
              >
                <div className="text-slate-300">{row.date}</div>
                <div className="flex gap-4 text-slate-200">
                  <span>Created: {row.tickets_created}</span>
                  <span>Resolved: {row.tickets_resolved}</span>
                  <span>Avg: {row.avg_response_time}s</span>
                </div>
              </div>
            ))}
            {!loading && !(stats?.daily_stats || []).length ? (
              <div className="text-sm text-slate-400">No daily support data available.</div>
            ) : null}
          </div>
        </div>

        <div className={cardClass}>
          <h2 className="text-lg font-semibold text-white">Agent Performance</h2>
          <div className="mt-4 space-y-3">
            {(stats?.agent_performance || []).map((agent) => (
              <div
                key={agent.name}
                className="rounded-xl border border-white/5 bg-white/5 px-4 py-3"
              >
                <div className="flex items-center justify-between">
                  <div className="font-medium text-white">{agent.name}</div>
                  <div className="text-sm text-emerald-300">{agent.satisfaction}% satisfaction</div>
                </div>
                <div className="mt-2 text-sm text-slate-300">
                  Tickets handled: {agent.tickets_handled} | Avg response: {agent.avg_response}s
                </div>
              </div>
            ))}
            {!loading && !(stats?.agent_performance || []).length ? (
              <div className="text-sm text-slate-400">No agent performance data available.</div>
            ) : null}
          </div>
        </div>
      </div>

      <div className={cardClass}>
        <h2 className="text-lg font-semibold text-white">Quick Links</h2>
        <div className="mt-4 flex flex-wrap gap-3">
          <a
            href="/admin/support/tickets"
            className="rounded-xl bg-blue-500/20 px-4 py-2 text-sm font-medium text-blue-200 transition hover:bg-blue-500/30"
          >
            Support Tickets
          </a>
          <a
            href="/ai-bots/customer-service"
            className="rounded-xl bg-cyan-500/20 px-4 py-2 text-sm font-medium text-cyan-200 transition hover:bg-cyan-500/30"
          >
            Customer Service Bot
          </a>
          <a
            href="/admin/system-health"
            className="rounded-xl bg-white/10 px-4 py-2 text-sm font-medium text-slate-100 transition hover:bg-white/15"
          >
            System Health
          </a>
        </div>
      </div>
    </div>
  );
}
