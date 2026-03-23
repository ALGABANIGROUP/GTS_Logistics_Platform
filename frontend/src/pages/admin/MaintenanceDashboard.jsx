import React, { useCallback, useEffect, useState } from "react";
import axiosClient from "../../api/axiosClient";
import TruckOrbitLoader from "../../components/loaders/TruckOrbitLoader";

function buildHealthScore(healthPayload) {
  const checks = healthPayload?.details || healthPayload?.checks || {};
  const values = Object.values(checks);
  if (values.length === 0) return 0;
  const running = values.filter((value) => {
    const raw = typeof value === "string" ? value : value?.status || value?.ok;
    const normalized = String(raw).toLowerCase();
    return normalized === "true" || normalized === "ok" || normalized === "healthy" || normalized === "running";
  }).length;
  return Math.round((running / values.length) * 100);
}

function StatCard({ title, value, tone }) {
  return (
    <div className="glass-card p-6">
      <h3 className="mb-2 text-lg font-semibold text-white">{title}</h3>
      <div className={`text-2xl font-bold ${tone}`}>{value}</div>
    </div>
  );
}

export default function MaintenanceDashboard() {
  const [health, setHealth] = useState(null);
  const [reports, setReports] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [remediations, setRemediations] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [stats, setStats] = useState(null);
  const [systemStatus, setSystemStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("overview");
  const [error, setError] = useState(null);
  const [actionMessage, setActionMessage] = useState(null);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const [healthRes, reportsRes, developmentsRes, ticketsRes, statusRes] = await Promise.all([
        axiosClient.get("/api/v1/system/health").catch(() => ({ data: {} })),
        axiosClient.get("/api/v1/maintenance/reports").catch(() => ({ data: { reports: [] } })),
        axiosClient.get("/api/v1/maintenance/suggested-developments").catch(() => ({ data: { developments: [] } })),
        axiosClient.get("/api/v1/maintenance/support-tickets").catch(() => ({ data: { tickets: [] } })),
        axiosClient.get("/api/v1/system/status").catch(() => ({ data: {} })),
      ]);

      const nextHealth = healthRes.data || {};
      const nextReports = reportsRes.data?.reports || [];
      const nextRecommendations = developmentsRes.data?.developments || [];
      const tickets = ticketsRes.data?.tickets || [];
      const nextIncidents = tickets.map((ticket) => ({
        ...ticket,
        title: ticket.issue,
        severity: ticket.priority || "warning",
        auto_remediated: ticket.status === "resolved",
      }));

      setHealth(nextHealth);
      setReports(nextReports);
      setRecommendations(
        nextRecommendations.map((item) => ({
          ...item,
          description: item.description || (item.benefits || []).join(", "),
        }))
      );
      setIncidents(nextIncidents);
      setRemediations(
        nextReports.map((report) => ({
          id: report.id,
          success: report.status === "completed",
          summary: `${report.issues || 0} issues found across ${report.checks || 0} checks`,
          timestamp: report.date,
        }))
      );
      setStats({
        incidents: {
          open: tickets.filter((ticket) => ticket.status === "open").length,
          in_progress: tickets.filter((ticket) => ticket.status === "in_progress").length,
        },
        reports: nextReports.length,
      });
      setSystemStatus({
        ...(statusRes.data || {}),
        health_score: buildHealthScore(nextHealth),
      });
    } catch (err) {
      console.error("Failed to load maintenance data:", err);
      setError("Failed to load maintenance data");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleSendMessage = useCallback(async () => {
    if (!chatInput.trim()) return;
    const userMessage = { role: "user", content: chatInput, timestamp: new Date().toISOString() };
    setChatMessages((prev) => [...prev, userMessage]);
    setChatInput("");
    setChatLoading(true);
    try {
      const response = await axiosClient.post("/ai/maintenance/chat/ask", { message: chatInput });
      setChatMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: response.data.response,
          timestamp: new Date().toISOString(),
        },
      ]);
    } catch (err) {
      console.error("Chat failed:", err);
      setChatMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Maintenance chat endpoint is unavailable right now.",
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setChatLoading(false);
    }
  }, [chatInput]);

  const triggerMaintenanceCycle = useCallback(async () => {
    await loadData();
    setActionMessage("Maintenance snapshot refreshed from current live routes.");
  }, [loadData]);

  const applyAutoFix = useCallback(
    async (incidentId) => {
      try {
        await axiosClient.post(`/api/v1/maintenance/support-tickets/${incidentId}/resolve`);
        setActionMessage(`Ticket ${incidentId} marked as resolved.`);
        await loadData();
      } catch (err) {
        console.error("Auto-fix failed:", err);
        setActionMessage("Auto-fix failed.");
      }
    },
    [loadData]
  );

  const getStatusColor = (status) => {
    const colors = { healthy: "text-green-400", degraded: "text-yellow-400", critical: "text-red-400" };
    return colors[status] || "text-gray-400";
  };

  const getSeverityColor = (severity) => {
    const colors = {
      critical: "bg-red-500/20 text-red-400 border-red-500/30",
      high: "bg-orange-500/20 text-orange-400 border-orange-500/30",
      medium: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
      low: "bg-blue-500/20 text-blue-400 border-blue-500/30",
    };
    return colors[severity] || "bg-gray-500/20 text-gray-400 border-gray-500/30";
  };

  if (loading) {
    return (
      <div className="p-6">
        <TruckOrbitLoader text="Loading maintenance dashboard..." />
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">System Maintenance</h1>
          <p className="text-slate-400">Monitor current health, MA reports, support incidents, and recommendations.</p>
        </div>
        <button onClick={loadData} className="glass-btn-secondary">
          Refresh
        </button>
      </div>

      {error && (
        <div className="glass-card border border-red-500/30 bg-red-500/10 p-4">
          <p className="text-sm text-red-400">{error}</p>
        </div>
      )}
      {actionMessage && (
        <div className="glass-card border border-emerald-500/30 bg-emerald-500/10 p-4">
          <p className="text-sm text-emerald-300">{actionMessage}</p>
        </div>
      )}

      <div className="flex space-x-1 overflow-x-auto rounded-xl bg-slate-800/50 p-1">
        {["overview", "chat", "health", "incidents", "recommendations", "remediation", "reports"].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`whitespace-nowrap rounded-lg px-4 py-2 text-sm font-medium transition-all ${
              activeTab === tab ? "bg-blue-600 text-white shadow-lg" : "text-slate-400 hover:bg-slate-700/50 hover:text-white"
            }`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {activeTab === "overview" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
            <StatCard title="System Status" value={health?.status?.toUpperCase() || "UNKNOWN"} tone={getStatusColor(health?.status)} />
            <StatCard title="Active Incidents" value={stats?.incidents?.open || 0} tone="text-red-400" />
            <StatCard title="Remediations" value={remediations.filter((item) => item.success).length} tone="text-green-400" />
            <StatCard title="Health Score" value={`${systemStatus?.health_score || 0}%`} tone="text-blue-400" />
          </div>
          <div className="glass-card p-6">
            <h3 className="mb-4 text-lg font-semibold text-white">Quick Actions</h3>
            <div className="flex flex-wrap gap-3">
              <button onClick={triggerMaintenanceCycle} className="glass-btn-primary">
                Refresh Maintenance Snapshot
              </button>
              <button onClick={() => setActiveTab("chat")} className="glass-btn-secondary">
                Open AI Assistant
              </button>
            </div>
          </div>
        </div>
      )}

      {activeTab === "chat" && (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="glass-card flex h-[600px] flex-col p-6 lg:col-span-2">
            <h3 className="mb-4 text-lg font-semibold text-white">AI Maintenance Assistant</h3>
            <div className="mb-4 flex-1 space-y-3 overflow-y-auto">
              {chatMessages.length === 0 && <p className="mt-8 text-center text-slate-400">Ask about health, performance, deployment, or security.</p>}
              {chatMessages.map((msg, idx) => (
                <div key={idx} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                  <div className={`max-w-[80%] rounded-lg p-3 ${msg.role === "user" ? "bg-blue-600 text-white" : "border border-slate-700 bg-slate-800/50 text-slate-200"}`}>
                    <p className="text-sm">{msg.content}</p>
                    <p className="mt-1 text-xs opacity-70">{new Date(msg.timestamp).toLocaleTimeString()}</p>
                  </div>
                </div>
              ))}
            </div>
            <div className="flex space-x-2">
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
                placeholder="Describe your issue..."
                className="flex-1 rounded-lg border border-slate-700 bg-slate-800/50 px-4 py-2 text-white"
                disabled={chatLoading}
              />
              <button
                onClick={handleSendMessage}
                disabled={chatLoading || !chatInput.trim()}
                className="rounded-lg bg-blue-600 px-6 py-2 text-white disabled:bg-slate-700"
              >
                Send
              </button>
            </div>
          </div>
          <div className="space-y-4">
            <div className="glass-card p-4">
              <h4 className="mb-3 font-semibold text-white">System Status</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-400">Health Score</span>
                  <span className="text-white">{systemStatus?.health_score || 0}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === "health" && (
        <div className="glass-card p-6">
          <h3 className="mb-4 text-lg font-semibold text-white">Current System Health</h3>
          <pre className="overflow-x-auto rounded-lg bg-slate-900/60 p-4 text-xs text-slate-300">
            {JSON.stringify(health || {}, null, 2)}
          </pre>
        </div>
      )}

      {activeTab === "incidents" && (
        <div className="glass-card p-6">
          <h3 className="mb-4 text-lg font-semibold text-white">Support Incidents</h3>
          <div className="space-y-3">
            {incidents.length === 0 ? (
              <p className="text-slate-400">No incidents.</p>
            ) : (
              incidents.map((incident) => (
                <div key={incident.id} className="rounded-lg border border-slate-700/50 p-4">
                  <div className="mb-2 flex items-center gap-2">
                    <span className={`rounded px-2 py-1 text-xs font-medium ${getSeverityColor(incident.severity)}`}>{String(incident.severity).toUpperCase()}</span>
                    <span className="text-slate-400">{incident.status}</span>
                  </div>
                  <h4 className="font-medium text-white">{incident.title}</h4>
                  {incident.description && <p className="mt-1 text-sm text-slate-400">{incident.description}</p>}
                  {incident.status === "open" && !incident.auto_remediated && (
                    <button onClick={() => applyAutoFix(incident.id)} className="mt-2 rounded bg-blue-600 px-3 py-1 text-xs text-white">
                      Resolve Ticket
                    </button>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {activeTab === "recommendations" && (
        <div className="glass-card p-6">
          <h3 className="mb-4 text-lg font-semibold text-white">Smart Recommendations</h3>
          {recommendations.length === 0 ? (
            <p className="text-slate-400">No recommendations available.</p>
          ) : (
            <div className="space-y-4">
              {recommendations.map((rec) => (
                <div key={rec.id} className="rounded-lg border border-slate-700/50 p-4">
                  <div className="mb-2">
                    <span className="rounded bg-blue-500/20 px-2 py-1 text-xs font-medium text-blue-400">{rec.priority}</span>
                  </div>
                  <h4 className="font-medium text-white">{rec.title}</h4>
                  <p className="text-sm text-slate-400">{rec.description}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === "remediation" && (
        <div className="glass-card p-6">
          <h3 className="mb-4 text-lg font-semibold text-white">Remediation History</h3>
          {remediations.length === 0 ? (
            <p className="text-slate-400">No remediation history available.</p>
          ) : (
            <div className="space-y-3">
              {remediations.map((item) => (
                <div key={item.id} className="rounded-lg border border-slate-700/50 p-4">
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-white">Report #{item.id}</span>
                    <span className={item.success ? "text-emerald-400" : "text-amber-400"}>{item.success ? "Completed" : "Pending"}</span>
                  </div>
                  <p className="mt-1 text-sm text-slate-400">{item.summary}</p>
                  <p className="mt-1 text-xs text-slate-500">{item.timestamp}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === "reports" && (
        <div className="glass-card p-6">
          <h3 className="mb-4 text-lg font-semibold text-white">Maintenance Reports</h3>
          {reports.length === 0 ? (
            <p className="text-slate-400">No reports available.</p>
          ) : (
            <div className="space-y-3">
              {reports.map((report) => (
                <div key={report.id} className="rounded-lg border border-slate-700/50 p-4">
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-white">{report.date}</span>
                    <span className="text-slate-300">{report.status}</span>
                  </div>
                  <p className="mt-1 text-sm text-slate-400">Checks: {report.checks || 0} | Issues: {report.issues || 0}</p>
                  {Array.isArray(report.recommendations) && report.recommendations.length > 0 && (
                    <p className="mt-1 text-sm text-slate-500">{report.recommendations[0]}</p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
