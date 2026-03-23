import React, { useEffect, useRef, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import axiosClient from "../../api/axiosClient";

const EMPTY_STATS = {
  summary: {
    total_emails: 0,
    success_rate: 0,
    auto_resolution_rate: 0,
  },
  bot_performance: {},
};

export default function EmailBotDashboard() {
  const [stats, setStats] = useState(EMPTY_STATS);
  const [mappings, setMappings] = useState([]);
  const [history, setHistory] = useState([]);
  const [botStats, setBotStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [warning, setWarning] = useState(null);
  const [wsConnected, setWsConnected] = useState(false);
  const wsRef = useRef(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, mappingsRes, historyRes] = await Promise.allSettled([
          axiosClient.get("/api/v1/email/monitoring/stats"),
          axiosClient.get("/api/v1/email/mappings"),
          axiosClient.get("/api/v1/email/execution-history?limit=50"),
        ]);

        const statsPayload = statsRes.status === "fulfilled" ? statsRes.value.data : EMPTY_STATS;
        const mappingsPayload = mappingsRes.status === "fulfilled" ? mappingsRes.value.data : {};
        const historyPayload = historyRes.status === "fulfilled" ? historyRes.value.data : {};

        setStats(statsPayload || EMPTY_STATS);
        setMappings(mappingsPayload?.mappings || []);
        setHistory(historyPayload?.history || []);
        setBotStats(statsPayload?.bot_performance || {});

        setWarning(
          [statsRes, mappingsRes, historyRes].every((res) => res.status !== "fulfilled")
            ? "Email monitoring endpoints are not mounted in this environment."
            : [statsRes, mappingsRes, historyRes].some((res) => res.status !== "fulfilled")
            ? "Some email monitoring endpoints are unavailable."
            : null
        );
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const connectWebSocket = () => {
      const wsUrl = `${window.location.protocol === "https:" ? "wss:" : "ws:"}//${window.location.host}/api/v1/ws/live`;
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        setWsConnected(true);
        wsRef.current.send(JSON.stringify({ type: "subscribe", channel: "emails.*" }));
      };

      wsRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.channel === "emails.processed") {
            setHistory((prev) => [data.payload || data.data, ...prev].slice(0, 50));
          }
        } catch {
          // ignore bad payloads
        }
      };

      wsRef.current.onclose = () => {
        setWsConnected(false);
        setTimeout(connectWebSocket, 3000);
      };
    };

    connectWebSocket();
    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="h-12 w-12 animate-spin rounded-full border-b-2 border-blue-600" />
      </div>
    );
  }

  const successRate = Number(stats?.summary?.success_rate || 0);
  const autoResolutionRate = Number(stats?.summary?.auto_resolution_rate || 0);
  const totalEmails = Number(stats?.summary?.total_emails || 0);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-8">
      <div className="mb-8">
        <h1 className="mb-2 text-4xl font-bold text-white">Email Bot Processing System</h1>
        <div className="flex items-center gap-2">
          <div className={`h-3 w-3 rounded-full ${wsConnected ? "bg-green-500" : "bg-red-500"}`} />
          <p className="text-slate-300">{wsConnected ? "Live monitoring active" : "Connecting..."}</p>
        </div>
      </div>

      {warning && (
        <div className="mb-6 rounded-lg border border-amber-500/30 bg-amber-500/10 p-4 text-sm text-amber-200">
          {warning}
        </div>
      )}

      <div className="mb-8 grid grid-cols-1 gap-6 md:grid-cols-4">
        <MetricCard label="Total Emails Processed" value={totalEmails.toLocaleString()} />
        <MetricCard label="Success Rate" value={`${successRate.toFixed(1)}%`} />
        <MetricCard label="Auto-Resolution" value={`${autoResolutionRate.toFixed(1)}%`} />
        <MetricCard label="Bot Mappings" value={mappings.length.toString()} />
      </div>

      <div className="mb-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-slate-700 bg-slate-800 p-6">
          <h3 className="mb-4 text-lg font-semibold text-white">Performance Metrics</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart
              data={[
                { name: "Success", value: totalEmails * (successRate / 100) },
                { name: "Failed", value: totalEmails * ((100 - successRate) / 100) },
                { name: "Auto-Resolved", value: totalEmails * (autoResolutionRate / 100) },
              ]}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="name" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #475569" }} />
              <Bar dataKey="value" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="rounded-xl border border-slate-700 bg-slate-800 p-6">
          <h3 className="mb-4 text-lg font-semibold text-white">Bot Distribution</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={Object.entries(botStats).map(([bot, data]) => ({
                  name: bot.replace(/_/g, " "),
                  value: data.processed || 0,
                }))}
                cx="50%"
                cy="50%"
                outerRadius={80}
                labelLine={false}
                label={(entry) => `${entry.name}: ${entry.value}`}
                dataKey="value"
              >
                {["#3b82f6", "#ef4444", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899"].map((color, idx) => (
                  <Cell key={idx} fill={color} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="mb-8 rounded-xl border border-slate-700 bg-slate-800 p-6">
        <h3 className="mb-4 text-lg font-semibold text-white">Email-to-Bot Mappings</h3>
        {mappings.length === 0 ? (
          <p className="text-sm text-slate-400">No email mappings available.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-600">
                  <th className="px-4 py-3 text-left text-slate-300">Email Account</th>
                  <th className="px-4 py-3 text-left text-slate-300">Primary Bot</th>
                  <th className="px-4 py-3 text-left text-slate-300">Backup Bot</th>
                  <th className="px-4 py-3 text-left text-slate-300">Priority</th>
                </tr>
              </thead>
              <tbody>
                {mappings.map((mapping, idx) => (
                  <tr key={idx} className="border-b border-slate-700">
                    <td className="px-4 py-3 text-blue-300">{mapping.email}</td>
                    <td className="px-4 py-3 text-slate-200">{mapping.primary_bot}</td>
                    <td className="px-4 py-3 text-slate-400">{mapping.backup_bot || "-"}</td>
                    <td className="px-4 py-3 text-slate-300">{mapping.priority || "medium"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="rounded-xl border border-slate-700 bg-slate-800 p-6">
        <h3 className="mb-4 text-lg font-semibold text-white">Recent Executions</h3>
        <div className="space-y-3">
          {history.length === 0 ? (
            <p className="text-sm text-slate-400">No recent executions.</p>
          ) : (
            history.map((execution, idx) => <ExecutionItem key={idx} execution={execution} />)
          )}
        </div>
      </div>
    </div>
  );
}

function MetricCard({ label, value }) {
  return (
    <div className="rounded-xl border border-slate-700 bg-gradient-to-br from-slate-800 to-slate-900 p-6">
      <p className="text-sm text-slate-400">{label}</p>
      <h3 className="mt-1 text-3xl font-bold text-white">{value}</h3>
    </div>
  );
}

function ExecutionItem({ execution }) {
  const success = Boolean(execution?.success);
  return (
    <div className="rounded-lg border border-slate-600 bg-slate-700/50 p-3">
      <div className="mb-1 flex items-center gap-2">
        <span className={success ? "text-green-400" : "text-red-400"}>{success ? "OK" : "ERR"}</span>
        <span className="text-xs text-slate-300">{execution.email_id || execution.id || "unknown"}</span>
        <span className="rounded bg-blue-900/30 px-2 py-0.5 text-xs text-blue-300">{execution.bot || execution.bot_name || "bot"}</span>
      </div>
      <div className="grid grid-cols-2 gap-2 text-xs">
        <p className="text-slate-400">Workflow: <span className="text-slate-300">{execution.workflow || "-"}</span></p>
        <p className="text-slate-400">Executed: <span className="text-slate-300">{execution.executed ? "Yes" : "No"}</span></p>
      </div>
    </div>
  );
}
