import { useEffect, useMemo, useState } from "react";
import axiosClient from "../../api/axiosClient";

const BOT_KEY = "operations_manager";
const glassCard =
  "rounded-2xl border border-white/10 bg-white/5 shadow-lg shadow-black/30 backdrop-blur-xl";

const toneMap = {
  critical: "border-rose-500/20 bg-rose-500/10 text-rose-200",
  high: "border-amber-500/20 bg-amber-500/10 text-amber-200",
  medium: "border-blue-500/20 bg-blue-500/10 text-blue-200",
  low: "border-white/10 bg-slate-900/50 text-slate-200",
  active: "border-emerald-500/20 bg-emerald-500/10 text-emerald-200",
  queued: "border-amber-500/20 bg-amber-500/10 text-amber-200",
  in_progress: "border-blue-500/20 bg-blue-500/10 text-blue-200",
  executed: "border-emerald-500/20 bg-emerald-500/10 text-emerald-200",
  completed: "border-emerald-500/20 bg-emerald-500/10 text-emerald-200",
};

const formatRelative = (value) => {
  if (!value) return "Unknown";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleString();
};

export default function AIOperationsManager() {
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState({});
  const [config, setConfig] = useState({});
  const [dashboard, setDashboard] = useState({});
  const [learningStats, setLearningStats] = useState({});
  const [selectedWorkflow, setSelectedWorkflow] = useState("incident_response");
  const [actionLog, setActionLog] = useState([]);

  const appendLog = (label, payload, state = "active") => {
    setActionLog((prev) => [
      {
        id: Date.now() + performance.now(),
        label,
        payload,
        state,
        timestamp: new Date().toISOString(),
      },
      ...prev.slice(0, 7),
    ]);
  };

  const fetchAll = async () => {
    setLoading(true);
    try {
      const [statusRes, configRes, dashboardRes, learningRes] = await Promise.all([
        axiosClient.get(`/api/v1/ai/bots/available/${BOT_KEY}/status`),
        axiosClient.post(`/api/v1/ai/bots/available/${BOT_KEY}/run`, {
          context: { action: "config" },
        }),
        axiosClient.post(`/api/v1/ai/bots/available/${BOT_KEY}/run`, {
          context: { action: "dashboard" },
        }),
        axiosClient.get("/api/v1/operations-manager/stats").catch(() => ({ data: {} })),
      ]);

      setStatus(statusRes.data?.data || statusRes.data?.status || {});
      setConfig(configRes.data?.data || configRes.data?.result || {});
      setDashboard(dashboardRes.data?.data || dashboardRes.data?.result || {});
      setLearningStats(learningRes.data || {});
    } catch (error) {
      console.log('Using seed data - Backend not available');
      // Test data
      setStatus({
        status: "active",
        uptime: "2h 15m",
        last_activity: new Date().toISOString(),
        version: "2.0.0"
      });
      setConfig({
        capabilities: ["dispatch", "monitoring", "optimization"],
        automation_level: "high",
        active_workflows: 3
      });
      setDashboard({
        quick_stats: {
          active_shipments: 12,
          pending_tasks: 5,
          completed_today: 28,
          alerts_count: 2
        },
        reports: {
          recent: [
            { report_id: 1, summary: "Dispatch shipment LD-001", source_bot: "dispatcher", report_type: "dispatch", severity: "high", received_at: new Date().toISOString() },
            { report_id: 2, summary: "Optimize route for LD-002", source_bot: "optimizer", report_type: "route", severity: "medium", received_at: new Date().toISOString() },
            { report_id: 3, summary: "Schedule maintenance", source_bot: "scheduler", report_type: "maintenance", severity: "medium", received_at: new Date().toISOString() }
          ],
          daily_summary: {
            total_reports: 45,
            by_severity: { critical: 2, high: 8, medium: 15, low: 20 },
            patterns: ["route_optimization", "maintenance_scheduling"]
          }
        },
        alerts: [
          { alert_id: 1, description: "High traffic expected in Toronto area", severity: "warning", correlation_score: 0.85, created_at: new Date().toISOString() },
          { alert_id: 2, description: "New carrier partnership activated", severity: "info", correlation_score: 0.92, created_at: new Date().toISOString() }
        ],
        command_queue: {
          recent: [
            { command_id: 1, command_type: "optimize_routes", target_bot: "route_optimizer", status: "completed", issued_at: new Date().toISOString() },
            { command_id: 2, command_type: "update_shipment_status", target_bot: "dispatcher", status: "in_progress", issued_at: new Date().toISOString() }
          ]
        },
        workflows: {
          recent: [
            { task_id: 1, workflow_name: "Emergency Response", current_step: "assessment", steps: 5, status: "active", progress: 40 },
            { task_id: 2, workflow_name: "Load Optimization", current_step: "analysis", steps: 3, status: "idle", progress: 0 }
          ]
        },
        recent_activity: [
          { reference_id: "LD-001", description: "Shipment dispatched to Toronto", log_type: "dispatch", created_at: new Date().toISOString() },
          { reference_id: "ROUTE-001", description: "Route optimized - saved 45 minutes", log_type: "optimization", created_at: new Date().toISOString() }
        ]
      });
      setLearningStats({
        total_learned: 156,
        accuracy_rate: 94.2,
        last_training: new Date().toISOString()
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAll();
  }, []);

  const quickStats = dashboard?.quick_stats || status?.quick_stats || {};
  const reports = dashboard?.reports?.recent || [];
  const dailySummary = dashboard?.reports?.daily_summary || {};
  const alerts = dashboard?.alerts || [];
  const recentCommands = dashboard?.command_queue?.recent || [];
  const workflows = dashboard?.workflows?.recent || [];
  const workflowTemplates = useMemo(
    () => (config?.capabilities ? ["new_customer", "new_shipment", "incident_response"] : []),
    [config]
  );
  const recentActivity = dashboard?.recent_activity || [];

  const runAction = async (label, context) => {
    setBusy(true);
    try {
      const res = await axiosClient.post(`/api/v1/ai/bots/available/${BOT_KEY}/run`, { context });
      appendLog(label, res.data?.data || res.data?.result || res.data, "completed");
      await fetchAll();
      return res.data;
    } catch (error) {
      appendLog(label, { error: error?.response?.data?.detail || error.message }, "critical");
      throw error;
    } finally {
      setBusy(false);
    }
  };

  const executeWorkflow = async () => {
    await runAction("Execute Workflow", {
      action: "execute_workflow",
      workflow_name: selectedWorkflow,
      data: {
        initiated_from: "operations_dashboard",
        requested_at: new Date().toISOString(),
      },
    });
  };

  const createCompositeAlert = async () => {
    const alertIds = reports.slice(0, 2).map((item) => item.report_id);
    if (alertIds.length < 2) return;
    await runAction("Create Composite Alert", {
      action: "create_composite_alert",
      alert_ids: alertIds,
    });
  };

  const refreshCommands = async () => {
    await runAction("Refresh Command Queue", { action: "command_queue" });
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950">
        <div className="text-center">
          <div className="mx-auto mb-4 h-16 w-16 animate-spin rounded-full border-b-2 border-sky-400" />
          <p className="text-slate-300">Loading Operations Manager dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950">
      <div className="border-b border-white/10 bg-slate-950/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-5">
          <div className="flex items-center gap-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-sky-500 to-blue-700 text-lg font-bold text-white shadow-lg shadow-blue-900/40">
              OPS
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">AI Operations Manager</h1>
              <p className="text-sm text-slate-300">
                Cross-bot command center for reports, alerts, workflows, and orchestration.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className={`${glassCard} px-4 py-2`}>
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Version</p>
              <p className="text-sm font-semibold text-white">{status.version || "2.0.0"}</p>
            </div>
            <div className={`${glassCard} px-4 py-2`}>
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Mode</p>
              <p className="text-sm font-semibold text-white">{status.mode || "orchestration"}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-7xl space-y-6 px-4 py-6">
        <div className="grid gap-4 md:grid-cols-5">
          {[
            { label: "Reports Today", value: quickStats.reports_today || 0, tone: "from-sky-500 to-blue-700" },
            { label: "Critical Today", value: quickStats.critical_today || 0, tone: "from-rose-500 to-red-700" },
            { label: "Pending Commands", value: quickStats.pending_commands || 0, tone: "from-amber-500 to-orange-700" },
            { label: "Active Alerts", value: quickStats.active_alerts || 0, tone: "from-violet-500 to-fuchsia-700" },
            { label: "Active Workflows", value: quickStats.active_workflows || 0, tone: "from-emerald-500 to-green-700" },
          ].map((item) => (
            <div key={item.label} className={`rounded-2xl bg-gradient-to-br ${item.tone} p-5 text-white shadow-lg`}>
              <p className="text-3xl font-bold">{item.value}</p>
              <p className="mt-1 text-sm text-white/80">{item.label}</p>
            </div>
          ))}
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <div className="space-y-6 lg:col-span-2">
            <div className={`${glassCard} p-6`}>
              <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h2 className="text-lg font-bold text-white">Operations Control</h2>
                  <p className="text-sm text-slate-400">Trigger workflows and build correlated alerts from incoming signals.</p>
                </div>
                <div className="flex flex-wrap gap-3">
                  <select
                    value={selectedWorkflow}
                    onChange={(e) => setSelectedWorkflow(e.target.value)}
                    className="rounded-xl border border-white/10 bg-slate-950/70 px-4 py-2 text-sm text-white outline-none"
                  >
                    {workflowTemplates.map((workflow) => (
                      <option key={workflow} value={workflow}>
                        {workflow}
                      </option>
                    ))}
                  </select>
                  <button
                    onClick={executeWorkflow}
                    disabled={busy}
                    className="rounded-xl bg-sky-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-sky-500 disabled:opacity-50"
                  >
                    Execute Workflow
                  </button>
                  <button
                    onClick={createCompositeAlert}
                    disabled={busy || reports.length < 2}
                    className="rounded-xl bg-violet-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-violet-500 disabled:opacity-50"
                  >
                    Create Composite Alert
                  </button>
                  <button
                    onClick={fetchAll}
                    disabled={busy}
                    className="rounded-xl border border-white/10 px-4 py-2 text-sm font-medium text-slate-200 transition hover:bg-white/5 disabled:opacity-50"
                  >
                    Refresh
                  </button>
                </div>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Daily Summary</p>
                  <div className="mt-3 space-y-2 text-sm text-slate-300">
                    <p>Total Reports: <span className="font-semibold text-white">{dailySummary.total_reports || 0}</span></p>
                    <p>Critical: <span className="font-semibold text-white">{dailySummary.by_severity?.critical || 0}</span></p>
                    <p>High: <span className="font-semibold text-white">{dailySummary.by_severity?.high || 0}</span></p>
                    <p>Patterns: <span className="font-semibold text-white">{(dailySummary.patterns || []).length}</span></p>
                  </div>
                </div>

                <div className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Learning Stats</p>
                  <div className="mt-3 space-y-2 text-sm text-slate-300">
                    <p>Assignments: <span className="font-semibold text-white">{learningStats.total_assignments ?? "-"}</span></p>
                    <p>Avg Rating: <span className="font-semibold text-white">{learningStats.average_rating ?? "-"}</span></p>
                    <p>Successful: <span className="font-semibold text-white">{learningStats.successful_assignments ?? "-"}</span></p>
                  </div>
                </div>
              </div>
            </div>

            <div className={`${glassCard} p-6`}>
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-lg font-bold text-white">Incoming Reports</h2>
                <span className="text-sm text-slate-400">{reports.length} recent</span>
              </div>
              <div className="space-y-3">
                {reports.map((report) => (
                  <div key={report.report_id} className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
                    <div className="flex flex-wrap items-start justify-between gap-3">
                      <div>
                        <p className="font-semibold text-white">{report.summary}</p>
                        <p className="mt-1 text-xs text-slate-400">
                          {report.source_bot} · {report.report_type} · {formatRelative(report.received_at)}
                        </p>
                      </div>
                      <span className={`rounded-full border px-3 py-1 text-xs ${toneMap[report.severity] || toneMap.low}`}>
                        {report.severity}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="grid gap-6 xl:grid-cols-2">
              <div className={`${glassCard} p-6`}>
                <div className="mb-4 flex items-center justify-between">
                  <h2 className="text-lg font-bold text-white">Active Alerts</h2>
                  <span className="text-sm text-slate-400">{alerts.length}</span>
                </div>
                <div className="space-y-3">
                  {alerts.length ? (
                    alerts.map((alert) => (
                      <div key={alert.alert_id} className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
                        <div className="flex flex-wrap items-start justify-between gap-3">
                          <p className="font-semibold text-white">{alert.description}</p>
                          <span className={`rounded-full border px-3 py-1 text-xs ${toneMap[alert.severity] || toneMap.low}`}>
                            {alert.severity}
                          </span>
                        </div>
                        <p className="mt-2 text-xs text-slate-400">
                          Correlation score: {alert.correlation_score} · {formatRelative(alert.created_at)}
                        </p>
                      </div>
                    ))
                  ) : (
                    <div className="rounded-xl border border-white/10 bg-slate-900/50 p-6 text-center text-sm text-slate-400">
                      No active alerts.
                    </div>
                  )}
                </div>
              </div>

              <div className={`${glassCard} p-6`}>
                <div className="mb-4 flex items-center justify-between">
                  <h2 className="text-lg font-bold text-white">Command Queue</h2>
                  <button
                    onClick={refreshCommands}
                    disabled={busy}
                    className="rounded-lg border border-white/10 px-3 py-1 text-xs text-slate-200 hover:bg-white/5 disabled:opacity-50"
                  >
                    Refresh Queue
                  </button>
                </div>
                <div className="space-y-3">
                  {recentCommands.length ? (
                    recentCommands.map((command) => (
                      <div key={command.command_id} className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
                        <div className="flex flex-wrap items-start justify-between gap-3">
                          <div>
                            <p className="font-semibold text-white">{command.command_type}</p>
                            <p className="mt-1 text-xs text-slate-400">
                              {command.target_bot} · {formatRelative(command.issued_at)}
                            </p>
                          </div>
                          <span className={`rounded-full border px-3 py-1 text-xs ${toneMap[command.status] || toneMap.low}`}>
                            {command.status}
                          </span>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="rounded-xl border border-white/10 bg-slate-900/50 p-6 text-center text-sm text-slate-400">
                      No recent commands.
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          <div className="space-y-6">
            <div className={`${glassCard} p-6`}>
              <h2 className="mb-4 text-lg font-bold text-white">Workflow Activity</h2>
              <div className="space-y-3">
                {workflows.length ? (
                  workflows.map((workflow) => (
                    <div key={workflow.task_id} className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <p className="font-semibold text-white">{workflow.workflow_name}</p>
                          <p className="mt-1 text-xs text-slate-400">
                            {workflow.current_step} · {workflow.steps} steps
                          </p>
                        </div>
                        <span className={`rounded-full border px-3 py-1 text-xs ${toneMap[workflow.status] || toneMap.low}`}>
                          {workflow.status}
                        </span>
                      </div>
                      <div className="mt-3 h-2 overflow-hidden rounded-full bg-white/10">
                        <div className="h-full rounded-full bg-sky-500" style={{ width: `${workflow.progress || 0}%` }} />
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-slate-400">No workflow activity.</p>
                )}
              </div>
            </div>

            <div className={`${glassCard} p-6`}>
              <h2 className="mb-4 text-lg font-bold text-white">Recent Activity</h2>
              <div className="space-y-3">
                {recentActivity.length ? (
                  recentActivity.map((item, index) => (
                    <div key={`${item.reference_id}-${index}`} className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
                      <p className="font-semibold text-white">{item.description}</p>
                      <p className="mt-1 text-xs uppercase tracking-[0.2em] text-slate-500">
                        {item.log_type} · {formatRelative(item.created_at)}
                      </p>
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-slate-400">No recent activity.</p>
                )}
              </div>
            </div>

            <div className={`${glassCard} p-6`}>
              <h2 className="mb-4 text-lg font-bold text-white">Config Snapshot</h2>
              <pre className="overflow-x-auto rounded-xl border border-white/10 bg-slate-950/70 p-4 text-xs text-slate-200">
                {JSON.stringify(config, null, 2)}
              </pre>
            </div>

            <div className={`${glassCard} p-6`}>
              <h2 className="mb-4 text-lg font-bold text-white">Action Log</h2>
              <div className="space-y-3">
                {actionLog.length ? (
                  actionLog.map((entry) => (
                    <div key={entry.id} className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
                      <div className="flex items-center justify-between gap-3">
                        <p className="font-semibold text-white">{entry.label}</p>
                        <span className={`rounded px-2 py-1 text-[10px] uppercase ${toneMap[entry.state] || toneMap.low}`}>
                          {entry.state}
                        </span>
                      </div>
                      <p className="mt-2 text-xs text-slate-400">{formatRelative(entry.timestamp)}</p>
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-slate-400">No actions yet.</p>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

