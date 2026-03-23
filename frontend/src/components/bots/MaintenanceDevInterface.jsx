/**
 * Maintenance Dev Bot Interface
 * System maintenance, diagnostics, and development support
 */
import { useCallback, useMemo, useState } from "react";
import axiosClient from "../../api/axiosClient";
import BotControlInterface from "./BotControlInterface";

const BOT_KEY = "maintenance_dev";

const QUICK_ACTIONS = [
  { id: "health_check", label: "Run Health Check", command: "health_check" },
  { id: "optimize", label: "Optimize Performance", command: "optimize_system" },
  { id: "clear_cache", label: "Clear Cache", command: "clear_cache" },
  { id: "restart_bots", label: "Restart Bots", command: "restart_all_bots" },
  { id: "report", label: "Generate Report", command: "generate_report" },
  { id: "backup_status", label: "Backup Status", command: "backup_status" },
];

const SYSTEM_CHECKS = [
  { name: "Database Connection", status: "healthy", lastCheck: "2 min ago" },
  { name: "API Response Time", status: "healthy", lastCheck: "1 min ago" },
  { name: "Memory Usage", status: "warning", lastCheck: "3 min ago" },
  { name: "Disk Space", status: "healthy", lastCheck: "5 min ago" },
  { name: "Background Jobs", status: "healthy", lastCheck: "1 min ago" },
  { name: "External Integrations", status: "healthy", lastCheck: "4 min ago" },
];

const RESOURCE_USAGE = [
  { label: "CPU", value: 45 },
  { label: "Memory", value: 72 },
  { label: "Disk", value: 58 },
  { label: "Network", value: 23 },
];

const INITIAL_ACTIVITY = [
  { id: 1, type: "warning", message: "High memory usage detected", time: "15 min ago" },
  { id: 2, type: "info", message: "Scheduled maintenance completed", time: "2h ago" },
  { id: 3, type: "success", message: "API response time improved", time: "1d ago" },
];

export default function MaintenanceDevInterface({ mode = "active" }) {
  const isPreview = mode === "preview";
  const [activityLog, setActivityLog] = useState(INITIAL_ACTIVITY);
  const [actionError, setActionError] = useState("");
  const [runningAction, setRunningAction] = useState(null);

  const botConfig = useMemo(
    () => ({
      displayName: "Maintenance Dev Bot",
      type: "System Maintenance",
      mode: isPreview ? "preview" : "active",
      capabilities: [
        "System Health Monitoring",
        "Diagnostics and Root Cause Analysis",
        "Performance Optimization",
        "Log Review and Reporting",
        "Automated Cleanup",
        "Backup Verification",
      ],
      commands: QUICK_ACTIONS,
    }),
    [isPreview]
  );

  const addLogEntry = useCallback((entry) => {
    setActivityLog((prev) => [entry, ...prev].slice(0, 12));
  }, []);

  const handleQuickAction = useCallback(
    async (action) => {
      if (isPreview) {
        setActionError("Preview mode - backend execution is disabled.");
        return;
      }

      setActionError("");
      setRunningAction(action.id);
      addLogEntry({
        id: Date.now(),
        type: "info",
        message: `Requested: ${action.label}`,
        time: "just now",
      });

      try {
        const res = await axiosClient.post(
          `/api/v1/ai/bots/available/${encodeURIComponent(BOT_KEY)}/run`,
          {
            message: action.command,
            context: { action: action.id },
            meta: { source: "maintenance_quick_action" },
          }
        );

        addLogEntry({
          id: Date.now() + 1,
          type: "success",
          message: `${action.label} completed`,
          time: "just now",
          details: res?.data,
        });
      } catch (err) {
        addLogEntry({
          id: Date.now() + 2,
          type: "error",
          message: `${action.label} failed`,
          time: "just now",
        });
        setActionError(err?.message || "Action failed.");
      } finally {
        setRunningAction(null);
      }
    },
    [addLogEntry, isPreview]
  );

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-white/10 bg-gradient-to-br from-slate-800/90 via-slate-900/90 to-zinc-900/90 p-5 backdrop-blur">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-slate-700 text-sm font-semibold text-white">
            MD
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">Maintenance Dev Bot</h1>
            <p className="text-sm text-slate-400">
              System maintenance, diagnostics, and development operations
            </p>
          </div>
          <div className="ml-auto">
            <span
              className={`rounded-full px-3 py-1 text-xs font-semibold ${
                isPreview
                  ? "bg-amber-500/20 text-amber-300"
                  : "bg-emerald-500/20 text-emerald-300"
              }`}
            >
              {isPreview ? "Preview Mode" : "Active"}
            </span>
          </div>
        </div>

        <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
          <SystemStat label="System Health" value="96%" status="good" />
          <SystemStat label="Uptime" value="99.9%" status="good" />
          <SystemStat label="Open Incidents" value="2" status="warning" />
          <SystemStat label="Last Backup" value="1h ago" status="good" />
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <div className="rounded-xl border border-white/10 bg-white/5 p-4 lg:col-span-2">
          <h3 className="mb-3 text-sm font-semibold text-white">System Health Checks</h3>
          <div className="grid gap-2 sm:grid-cols-2">
            {SYSTEM_CHECKS.map((check) => (
              <div
                key={check.name}
                className="flex items-center justify-between rounded-lg bg-white/5 p-3"
              >
                <div className="flex items-center gap-2">
                  <span
                    className={`h-2 w-2 rounded-full ${
                      check.status === "healthy"
                        ? "bg-emerald-500"
                        : check.status === "warning"
                        ? "bg-amber-500"
                        : "bg-rose-500"
                    }`}
                  />
                  <span className="text-xs text-white">{check.name}</span>
                </div>
                <span className="text-xs text-slate-500">{check.lastCheck}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-xl border border-white/10 bg-white/5 p-4">
          <h3 className="mb-3 text-sm font-semibold text-white">Resource Usage</h3>
          <div className="space-y-3">
            {RESOURCE_USAGE.map((metric) => (
              <ResourceBar key={metric.label} label={metric.label} value={metric.value} />
            ))}
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-white/10 bg-white/5 p-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h3 className="text-sm font-semibold text-white">Maintenance Actions</h3>
          <span className="text-xs text-slate-400">Runs commands on the maintenance bot</span>
        </div>
        <div className="mt-3 flex flex-wrap gap-2">
          {QUICK_ACTIONS.map((action) => (
            <button
              key={action.id}
              disabled={isPreview || runningAction === action.id}
              onClick={() => handleQuickAction(action)}
              className={`rounded-lg px-4 py-2 text-sm font-medium transition ${
                isPreview || runningAction === action.id
                  ? "bg-slate-700/50 text-slate-500 cursor-not-allowed"
                  : "bg-gradient-to-r from-slate-600/80 to-zinc-600/80 text-white shadow hover:from-slate-500/80 hover:to-zinc-500/80"
              }`}
            >
              {runningAction === action.id ? "Running..." : action.label}
            </button>
          ))}
        </div>
        {actionError ? (
          <div className="mt-3 rounded-lg border border-rose-500/30 bg-rose-500/10 px-3 py-2 text-xs text-rose-200">
            {actionError}
          </div>
        ) : null}
      </div>

      <div className="rounded-xl border border-white/10 bg-white/5 p-4">
        <h3 className="mb-3 text-sm font-semibold text-white">Recent Activity</h3>
        <div className="space-y-2">
          {activityLog.map((entry) => (
            <ActivityRow key={entry.id} entry={entry} />
          ))}
        </div>
      </div>

      <BotControlInterface botKey={BOT_KEY} botConfig={botConfig} mode={mode} />
    </div>
  );
}

function SystemStat({ label, value, status }) {
  const statusColors = {
    good: "text-emerald-400",
    warning: "text-amber-400",
    error: "text-rose-400",
  };

  return (
    <div className="rounded-xl bg-white/5 p-3">
      <div className="text-xs font-medium text-slate-400">{label}</div>
      <div className={`mt-1 text-sm font-bold ${statusColors[status] || "text-white"}`}>
        {value}
      </div>
    </div>
  );
}

function ResourceBar({ label, value }) {
  const color = value > 80 ? "bg-rose-500" : value > 60 ? "bg-amber-500" : "bg-emerald-500";

  return (
    <div>
      <div className="mb-1 flex justify-between text-xs">
        <span className="text-slate-400">{label}</span>
        <span className="text-white">{value}%</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-slate-700">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${value}%` }} />
      </div>
    </div>
  );
}

function ActivityRow({ entry }) {
  const typeStyles = {
    success: "bg-emerald-500/20 text-emerald-300",
    info: "bg-blue-500/20 text-blue-300",
    warning: "bg-amber-500/20 text-amber-300",
    error: "bg-rose-500/20 text-rose-300",
  };

  return (
    <div className="flex items-center justify-between rounded-lg bg-white/5 p-3">
      <div>
        <div className="text-sm text-white">{entry.message}</div>
        <div className="text-xs text-slate-500">{entry.time}</div>
      </div>
      <span
        className={`rounded-full px-2 py-0.5 text-xs ${
          typeStyles[entry.type] || "bg-white/10 text-slate-200"
        }`}
      >
        {entry.type}
      </span>
    </div>
  );
}
