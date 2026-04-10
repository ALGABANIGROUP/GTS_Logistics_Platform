import { useEffect, useMemo, useState } from "react";
import axiosClient from "../../api/axiosClient";
import { useAuth } from "../../contexts/AuthContext.jsx";
import { getUserRole, isAdminRole } from "../../utils/userRole.js";

const BOT_KEY = "system_bot";
const glassCard =
  "rounded-2xl border border-white/10 bg-white/5 shadow-lg shadow-black/30 backdrop-blur-xl";

const emptyForm = {
  id: null,
  email: "",
  password: "",
  full_name: "",
  role: "user",
  is_active: true,
  assigned_bots: [],
  features: [],
};

const toneMap = {
  healthy: "border-emerald-500/20 bg-emerald-500/10 text-emerald-200",
  warning: "border-amber-500/20 bg-amber-500/10 text-amber-200",
  critical: "border-rose-500/20 bg-rose-500/10 text-rose-200",
  degraded: "border-orange-500/20 bg-orange-500/10 text-orange-200",
  running: "border-emerald-500/20 bg-emerald-500/10 text-emerald-200",
  info: "border-blue-500/20 bg-blue-500/10 text-blue-200",
  active: "border-cyan-500/20 bg-cyan-500/10 text-cyan-200",
};

function formatDate(value) {
  if (!value) return "Unknown";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleString();
}

function pct(value) {
  const num = Number(value || 0);
  return `${Math.round(num)}%`;
}

function compactList(items, limit = 3) {
  if (!Array.isArray(items) || !items.length) return "None";
  if (items.includes("*")) return "All bots";
  if (items.length <= limit) return items.join(", ");
  return `${items.slice(0, limit).join(", ")} +${items.length - limit}`;
}

function settledData(result, fallback = {}) {
  if (result.status !== "fulfilled") return fallback;
  return result.value?.data ?? result.value ?? fallback;
}

function extractBotPayload(data, fallback = {}) {
  return data?.data || data?.result || data || fallback;
}

function bytesToGb(value) {
  const num = Number(value);
  if (!Number.isFinite(num) || num <= 0) return 0;
  return Number((num / (1024 ** 3)).toFixed(1));
}

function formatUptimeFromSeconds(value) {
  const seconds = Number(value);
  if (!Number.isFinite(seconds) || seconds <= 0) return "unknown";
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  if (days > 0) return `${days}d ${hours}h`;
  const minutes = Math.floor((seconds % 3600) / 60);
  return hours > 0 ? `${hours}h ${minutes}m` : `${minutes}m`;
}

function normalizeRoles(data) {
  const rawRoles = data?.data?.roles || data?.roles || [];
  return rawRoles.map((role) => ({
    key: role.key || role.value || role.role || "user",
    name: role.name_en || role.label || role.name || role.value || role.key || "User",
    permissions: Array.isArray(role.permissions) ? role.permissions : [],
  }));
}

function normalizeBotCatalog(data) {
  const rawBots = data?.data?.bots || data?.bots || [];
  return rawBots.map((bot) => ({
    key: bot.bot_key || bot.bot_code || bot.key || bot.name,
    name: bot.display_name || bot.name || bot.bot_key || bot.bot_code || "Bot",
    category: bot.category || "general",
    status: bot.status || {},
  }));
}

function normalizeFeatureFlags(data) {
  const flags = data?.flags || {};
  if (Array.isArray(flags)) {
    return flags;
  }
  if (Array.isArray(flags.enabled)) {
    return flags.enabled;
  }
  if (Array.isArray(data?.enabled)) {
    return data.enabled;
  }
  return [];
}

function normalizeSystemHealth(metricsData, healthData, botCatalog) {
  const host = metricsData?.host || {};
  const cpu = host.cpu || {};
  const memory = host.memory || {};
  const disk = host.disk || {};
  const health = healthData?.health || {};
  const activeBots = botCatalog.filter((bot) => {
    const statusValue = String(bot.status?.status || "").toLowerCase();
    return statusValue && statusValue !== "stopped" && statusValue !== "disabled" && statusValue !== "error";
  }).length;

  return {
    status: health.overall_status || healthData?.status || "unknown",
    system: {
      cpu: {
        percent: Number(cpu.percent || 0),
        cores: Number(cpu.cores || 0),
        cores_physical: Number(cpu.cores || 0),
      },
      memory: {
        percent: Number(memory.percent || 0),
        total_gb: bytesToGb(memory.total),
        available_gb: Math.max(0, bytesToGb(memory.total) - bytesToGb(memory.used)),
        used_gb: bytesToGb(memory.used),
      },
      disk: {
        percent: Number(disk.percent || 0),
        total_gb: bytesToGb(disk.total),
        free_gb: Math.max(0, bytesToGb(disk.total) - bytesToGb(disk.used)),
        used_gb: bytesToGb(disk.used),
      },
      uptime: formatUptimeFromSeconds(metricsData?.uptime_seconds),
    },
    system_health: {
      running_bots: activeBots,
      total_bots: botCatalog.length,
    },
  };
}

function normalizeDatabaseHealth(data) {
  return {
    status: data?.connected ? "healthy" : data?.status || "unknown",
    database: {
      size_gb: null,
      response_time_ms: data?.response_time_ms ?? null,
    },
  };
}

export default function AISystemAdmin({ botKey = BOT_KEY }) {
  const resolvedBotKey = botKey || BOT_KEY;
  const { user } = useAuth();
  const userRole = getUserRole(user);
  const canAccessSystemManager = isAdminRole(userRole);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [savingUser, setSavingUser] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [status, setStatus] = useState({});
  const [config, setConfig] = useState({});
  const [systemHealth, setSystemHealth] = useState({});
  const [databaseHealth, setDatabaseHealth] = useState({});
  const [dashboard, setDashboard] = useState({});
  const [alerts, setAlerts] = useState([]);
  const [bottlenecks, setBottlenecks] = useState({});
  const [forecast, setForecast] = useState({});
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [botCatalog, setBotCatalog] = useState([]);
  const [availableFeatures, setAvailableFeatures] = useState([]);
  const [userStats, setUserStats] = useState({});
  const [queryText, setQueryText] = useState(
    "SELECT * FROM shipments WHERE customer_id NOT IN (SELECT id FROM customers)"
  );
  const [queryReview, setQueryReview] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [form, setForm] = useState(emptyForm);
  const [actionLog, setActionLog] = useState([]);

  const appendLog = (label, payload, state = "info") => {
    setActionLog((prev) => [
      {
        id: Date.now() + Math.random(),
        label,
        payload,
        state,
        timestamp: new Date().toISOString(),
      },
      ...prev.slice(0, 7),
    ]);
  };

  const runBotAction = async (label, context) => {
    setBusy(true);
    try {
      const res = await axiosClient.post(
        `/api/v1/ai/bots/available/${resolvedBotKey}/run`,
        { context }
      );
      const payload = res.data?.data || res.data?.result || res.data || {};
      appendLog(label, payload, "healthy");
      return payload;
    } catch (actionError) {
      const message =
        actionError?.response?.data?.detail || actionError.message || "Action failed";
      appendLog(label, { error: message }, "critical");
      throw actionError;
    } finally {
      setBusy(false);
    }
  };

  const loadAll = async () => {
    if (!canAccessSystemManager) {
      setError("Admin access required.");
      setLoading(false);
      return;
    }

    setLoading(true);
    setError("");
    try {
      const [
        statusRes,
        configRes,
        dashboardRes,
        systemMetricsRes,
        systemStatusRes,
        databaseStatsRes,
        usersRes,
        rolesRes,
        botCatalogRes,
        featureFlagsRes,
        userStatsRes,
        alertsRes,
        bottlenecksRes,
        forecastRes,
      ] = await Promise.allSettled([
        axiosClient.get(`/api/v1/ai/bots/available/${resolvedBotKey}/status`),
        axiosClient.post(`/api/v1/ai/bots/available/${resolvedBotKey}/run`, { context: { action: "config" } }),
        axiosClient.post(`/api/v1/ai/bots/available/${resolvedBotKey}/run`, { context: { action: "dashboard" } }),
        axiosClient.get("/api/v1/system/metrics"),
        axiosClient.get("/api/v1/system/health"),
        axiosClient.get("/api/v1/system/database/stats"),
        axiosClient.get("/api/v1/admin/users-unified/management", { params: { limit: 200 } }),
        axiosClient.get("/api/v1/admin/roles"),
        axiosClient.get("/api/v1/bots/catalog"),
        axiosClient.get("/api/v1/system/feature-flags"),
        axiosClient.get("/api/v1/admin/users/stats"),
        axiosClient.post(`/api/v1/ai/bots/available/${resolvedBotKey}/run`, { context: { action: "get_active_alerts" } }),
        axiosClient.post(`/api/v1/ai/bots/available/${resolvedBotKey}/run`, { context: { action: "check_bottlenecks" } }),
        axiosClient.post(`/api/v1/ai/bots/available/${resolvedBotKey}/run`, { context: { action: "predict_resources", days: 30 } }),
      ]);

      const statusData = settledData(statusRes);
      const configData = extractBotPayload(settledData(configRes));
      const dashboardData = extractBotPayload(settledData(dashboardRes));
      const botCatalogData = normalizeBotCatalog(settledData(botCatalogRes));
      const usersData = settledData(usersRes)?.users || [];
      const normalizedUsers = usersData.map((entry) => ({
        ...entry,
        assigned_bots: Array.isArray(entry.assigned_bots) ? entry.assigned_bots : [],
        features: Array.isArray(entry.features) ? entry.features : [],
      }));
      const userStatsData = settledData(userStatsRes);
      const normalizedUserStats = {
        ...userStatsData,
        active_users:
          userStatsData?.active_users ??
          userStatsData?.active ??
          normalizedUsers.filter((entry) => entry.is_active).length,
      };

      setStatus(statusData?.data || statusData?.status || statusData || {});
      setConfig(configData);
      setDashboard(dashboardData);
      setBotCatalog(botCatalogData);
      setSystemHealth(
        normalizeSystemHealth(
          settledData(systemMetricsRes),
          settledData(systemStatusRes),
          botCatalogData
        )
      );
      setDatabaseHealth(normalizeDatabaseHealth(settledData(databaseStatsRes)));
      setUsers(normalizedUsers);
      setRoles(normalizeRoles(settledData(rolesRes)));
      setAvailableFeatures(normalizeFeatureFlags(settledData(featureFlagsRes)));
      setUserStats(normalizedUserStats);
      setAlerts(extractBotPayload(settledData(alertsRes)).alerts || []);
      setBottlenecks(extractBotPayload(settledData(bottlenecksRes)));
      setForecast(extractBotPayload(settledData(forecastRes)));
    } catch (loadError) {
      setError(loadError?.response?.data?.detail || loadError.message || "Failed to load System Manager");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!canAccessSystemManager) {
      setLoading(false);
      return;
    }
    loadAll();
  }, [canAccessSystemManager, resolvedBotKey]);

  const dashboardStats = dashboard?.stats || {};
  const dashboardAlerts = dashboard?.alerts || [];
  const combinedAlerts = alerts.length ? alerts : dashboardAlerts;
  const topBots = dashboard?.bots?.length
    ? dashboard.bots
    : botCatalog.slice(0, 8).map((bot) => ({
        bot_name: bot.name,
        status: bot.status?.status || "unknown",
        response_time_ms: bot.status?.response_time_ms ?? "N/A",
        cpu_usage: bot.status?.cpu_usage ?? "N/A",
        memory_usage_mb: bot.status?.memory_usage_mb ?? "N/A",
      }));
  const summary = status?.system_health || systemHealth?.system_health || {};
  const system = systemHealth?.system || {};
  const roleBreakdown = Object.keys(userStats?.users_by_role || {}).length
    ? userStats.users_by_role
    : users.reduce((acc, entry) => {
        const key = String(entry.role || "user");
        acc[key] = (acc[key] || 0) + 1;
        return acc;
      }, {});
  const roleCards = roles.length ? roles : [];

  const accessCoverage = useMemo(() => {
    const botAssignments = users.reduce((count, user) => count + (user.assigned_bots?.includes("*") ? botCatalog.length : user.assigned_bots?.length || 0), 0);
    const featureAssignments = users.reduce((count, user) => count + (user.features?.length || 0), 0);
    return {
      botAssignments,
      featureAssignments,
      protectedUsers: users.filter((user) => (user.assigned_bots?.length || 0) > 0 || (user.features?.length || 0) > 0).length,
    };
  }, [botCatalog.length, users]);

  const openCreateModal = () => {
    setEditingUser(null);
    setForm(emptyForm);
    setShowModal(true);
  };

  const openEditModal = (user) => {
    setEditingUser(user);
    setForm({
      id: user.id,
      email: user.email || "",
      password: "",
      full_name: user.full_name || "",
      role: user.role || "user",
      is_active: Boolean(user.is_active),
      assigned_bots: Array.isArray(user.assigned_bots) ? user.assigned_bots : [],
      features: Array.isArray(user.features) ? user.features : [],
    });
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingUser(null);
    setForm(emptyForm);
  };

  const toggleChoice = (key, value) => {
    setForm((prev) => {
      const current = Array.isArray(prev[key]) ? prev[key] : [];
      const hasValue = current.includes(value);
      let next;
      if (value === "*") {
        next = hasValue ? [] : ["*"];
      } else {
        next = hasValue ? current.filter((item) => item !== value) : [...current.filter((item) => item !== "*"), value];
      }
      return { ...prev, [key]: next };
    });
  };

  const saveUser = async () => {
    if (!form.email.trim()) {
      setError("Email is required.");
      return;
    }
    if (!editingUser && !form.password.trim()) {
      setError("Password is required for new users.");
      return;
    }

    setSavingUser(true);
    setError("");
    try {
      const payload = {
        email: form.email.trim(),
        full_name: form.full_name.trim(),
        role: form.role,
        is_active: form.is_active,
        assigned_bots: form.assigned_bots,
        features: form.features,
      };
      if (form.password.trim()) payload.password = form.password;

      if (editingUser) {
        await axiosClient.patch(`/api/v1/admin/users-unified/${editingUser.id}`, payload);
        appendLog("User Updated", { id: editingUser.id, email: form.email, role: form.role }, "healthy");
        setNotice(`Updated ${form.email}.`);
      } else {
        await axiosClient.post("/api/v1/admin/users-unified", payload);
        appendLog("User Created", { email: form.email, role: form.role }, "healthy");
        setNotice(`Created ${form.email}.`);
      }

      closeModal();
      await loadAll();
    } catch (saveError) {
      setError(saveError?.response?.data?.detail || saveError.message || "Unable to save user.");
    } finally {
      setSavingUser(false);
    }
  };

  const deleteUser = async (user) => {
    const confirmed = window.confirm(`Deactivate ${user.email}?`);
    if (!confirmed) return;
    setBusy(true);
    setError("");
    try {
      await axiosClient.delete(`/api/v1/admin/users-unified/${user.id}`);
      appendLog("User Deactivated", { id: user.id, email: user.email }, "warning");
      setNotice(`Deactivated ${user.email}.`);
      await loadAll();
    } catch (deleteError) {
      setError(deleteError?.response?.data?.detail || deleteError.message || "Unable to deactivate user.");
    } finally {
      setBusy(false);
    }
  };

  const resolveAlert = async (alertId) => {
    try {
      await runBotAction("Resolve Alert", { action: "resolve_alert", alert_id: alertId });
      setNotice(`Resolved alert ${alertId}.`);
      await loadAll();
    } catch (resolveError) {
      setError(resolveError?.response?.data?.detail || resolveError.message || "Unable to resolve alert.");
    }
  };

  const analyzeQuery = async () => {
    try {
      const payload = await runBotAction("Analyze SQL", {
        action: "rewrite_query",
        query: queryText,
      });
      setQueryReview(payload);
      setNotice("SQL analysis completed.");
    } catch (queryError) {
      setError(queryError?.response?.data?.detail || queryError.message || "Unable to analyze SQL.");
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950">
        <div className="text-center">
          <div className="mx-auto mb-4 h-16 w-16 animate-spin rounded-full border-b-2 border-emerald-400" />
          <p className="text-slate-300">Loading System Manager dashboard...</p>
        </div>
      </div>
    );
  }

  if (!canAccessSystemManager) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950 px-4">
        <div className="max-w-lg rounded-3xl border border-rose-500/20 bg-rose-500/10 p-6 text-center shadow-xl shadow-black/30">
          <h1 className="text-xl font-bold text-white">Access Restricted</h1>
          <p className="mt-3 text-sm text-rose-100">
            AI System Manager is available only to admin roles. This page no longer shows placeholder zeros for non-admin users.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950">
      <div className="border-b border-white/10 bg-slate-950/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-5">
          <div className="flex items-center gap-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-emerald-500 to-cyan-800 text-lg font-bold text-white shadow-lg shadow-emerald-950/40">
              SYS
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">AI System Manager</h1>
              <p className="text-sm text-slate-300">
                Platform health, RBAC governance, bot assignment, and operational tuning.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className={`${glassCard} px-4 py-2`}>
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Version</p>
              <p className="text-sm font-semibold text-white">{status.version || config.version || "2.0.0"}</p>
            </div>
            <div className={`${glassCard} px-4 py-2`}>
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Mode</p>
              <p className="text-sm font-semibold capitalize text-white">{status.mode || config.mode || "infrastructure"}</p>
            </div>
            <button
              onClick={loadAll}
              disabled={busy || savingUser}
              className="rounded-xl border border-white/10 px-4 py-2 text-sm font-medium text-slate-200 transition hover:bg-white/5 disabled:opacity-50"
            >
              Refresh
            </button>
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-7xl space-y-6 px-4 py-6">
        {error ? <div className="rounded-2xl border border-rose-500/20 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">{error}</div> : null}
        {notice ? <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-200">{notice}</div> : null}

        <div className="grid gap-4 md:grid-cols-5">
          {[
            { label: "System Health", value: `${Math.round(((summary.running_bots || 0) / Math.max(summary.total_bots || 1, 1)) * 100)}%`, note: `${summary.running_bots || 0}/${summary.total_bots || 0} bots running`, tone: "from-emerald-500 to-teal-700" },
            { label: "CPU Usage", value: pct(system.cpu?.percent), note: `${system.cpu?.cores || 0} logical cores`, tone: "from-cyan-500 to-blue-700" },
            { label: "Memory Usage", value: pct(system.memory?.percent), note: `${system.memory?.used_gb || 0} GB used`, tone: "from-violet-500 to-fuchsia-700" },
            { label: "Protected Users", value: accessCoverage.protectedUsers, note: `${accessCoverage.protectedUsers} users with bot or feature scopes`, tone: "from-amber-500 to-orange-700" },
            { label: "Bot Assignments", value: accessCoverage.botAssignments, note: `${availableFeatures.length} available feature flags`, tone: "from-slate-500 to-slate-700" },
          ].map((item) => (
            <div key={item.label} className={`rounded-2xl bg-gradient-to-br ${item.tone} p-5 text-white shadow-lg`}>
              <p className="text-3xl font-bold">{item.value}</p>
              <p className="mt-1 text-sm text-white/80">{item.label}</p>
              <p className="mt-2 text-xs text-white/70">{item.note}</p>
            </div>
          ))}
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <div className={`${glassCard} p-6 lg:col-span-2`}>
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold text-white">Platform Health</h2>
                <p className="text-sm text-slate-400">Live infrastructure metrics from the admin runtime and the system bot.</p>
              </div>
              <span className={`rounded-full border px-3 py-1 text-xs font-semibold ${toneMap[systemHealth.status] || toneMap.info}`}>
                {systemHealth.status || "unknown"}
              </span>
            </div>

            <div className="grid gap-4 md:grid-cols-3">
              {[
                { label: "CPU", value: pct(system.cpu?.percent), detail: `${system.cpu?.cores_physical || 0} physical cores`, percent: Number(system.cpu?.percent || 0) },
                { label: "Memory", value: pct(system.memory?.percent), detail: `${system.memory?.available_gb || 0} GB available`, percent: Number(system.memory?.percent || 0) },
                { label: "Disk", value: pct(system.disk?.percent), detail: `${system.disk?.free_gb || 0} GB free`, percent: Number(system.disk?.percent || 0) },
              ].map((item) => (
                <div key={item.label} className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
                  <p className="text-xs uppercase tracking-[0.18em] text-slate-400">{item.label}</p>
                  <p className="mt-3 text-3xl font-bold text-white">{item.value}</p>
                  <p className="mt-2 text-sm text-slate-400">{item.detail}</p>
                  <div className="mt-4 h-2 overflow-hidden rounded-full bg-slate-800">
                    <div
                      className={`h-full rounded-full ${item.percent >= 85 ? "bg-rose-500" : item.percent >= 70 ? "bg-amber-400" : "bg-emerald-400"}`}
                      style={{ width: `${Math.min(item.percent, 100)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-4 grid gap-4 md:grid-cols-2">
              <div className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
                <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Database</p>
                <p className="mt-3 text-2xl font-bold text-white">
                  {databaseHealth.database?.size_gb != null ? `${databaseHealth.database.size_gb} GB` : "Unknown"}
                </p>
                <p className="mt-2 text-sm text-slate-400">
                  Response time: {databaseHealth.database?.response_time_ms ?? "Unknown"} ms
                </p>
              </div>
              <div className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
                <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Uptime</p>
                <p className="mt-3 text-2xl font-bold text-white">{system.uptime || "Unknown"}</p>
                <p className="mt-2 text-sm text-slate-400">
                  Managed bots: {summary.total_bots || dashboardStats.total_bots || topBots.length || 0}
                </p>
              </div>
            </div>
          </div>

          <div className={`${glassCard} p-6`}>
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold text-white">Access Control Summary</h2>
                <p className="text-sm text-slate-400">Role distribution and assignment coverage.</p>
              </div>
            </div>
            <div className="space-y-3">
              {Object.entries(roleBreakdown).length ? (
                Object.entries(roleBreakdown).map(([role, count]) => (
                  <div key={role} className="rounded-xl border border-white/10 bg-slate-900/50 p-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-semibold capitalize text-white">{role.replaceAll("_", " ")}</span>
                      <span className="text-sm text-slate-300">{count}</span>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-sm text-slate-400">No role breakdown available.</p>
              )}
            </div>
            <div className="mt-4 rounded-xl border border-white/10 bg-slate-900/50 p-4 text-sm text-slate-300">
              <p>Users with direct bot scopes: <span className="font-semibold text-white">{accessCoverage.protectedUsers}</span></p>
              <p className="mt-2">Feature grants assigned: <span className="font-semibold text-white">{accessCoverage.featureAssignments}</span></p>
              <p className="mt-2">Bot catalog size: <span className="font-semibold text-white">{botCatalog.length}</span></p>
            </div>
          </div>
        </div>

        <div className="grid gap-6 xl:grid-cols-[1.55fr_0.95fr]">
          <div className={`${glassCard} p-6`}>
            <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
              <div>
                <h2 className="text-lg font-bold text-white">User Access Directory</h2>
                <p className="text-sm text-slate-400">Manage users, roles, bot assignments, and feature flags in one place.</p>
              </div>
              <button
                onClick={openCreateModal}
                className="rounded-xl bg-emerald-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-emerald-500"
              >
                Create User
              </button>
            </div>

            <div className="overflow-x-auto">
              <table className="min-w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-white/10 text-slate-400">
                    <th className="pb-3 pr-4 font-medium">Identity</th>
                    <th className="pb-3 pr-4 font-medium">Role</th>
                    <th className="pb-3 pr-4 font-medium">Assigned Bots</th>
                    <th className="pb-3 pr-4 font-medium">Features</th>
                    <th className="pb-3 pr-4 font-medium">Last Login</th>
                    <th className="pb-3 pr-4 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user) => (
                    <tr key={user.id} className="border-b border-white/5 text-slate-200">
                      <td className="py-4 pr-4">
                        <div className="font-semibold text-white">{user.full_name || "Unnamed user"}</div>
                        <div className="text-xs text-slate-400">{user.email}</div>
                      </td>
                      <td className="py-4 pr-4">
                        <span className={`rounded-full border px-2 py-1 text-[11px] ${user.is_active ? toneMap.active : toneMap.warning}`}>
                          {(user.role || "user").replaceAll("_", " ")}
                        </span>
                      </td>
                      <td className="py-4 pr-4 text-xs text-slate-300">{compactList(user.assigned_bots, 2)}</td>
                      <td className="py-4 pr-4 text-xs text-slate-300">{compactList(user.features, 2)}</td>
                      <td className="py-4 pr-4 text-xs text-slate-400">{formatDate(user.last_login)}</td>
                      <td className="py-4 pr-4">
                        <div className="flex flex-wrap gap-2">
                          <button
                            onClick={() => openEditModal(user)}
                            className="rounded-lg border border-white/10 px-3 py-1.5 text-xs text-slate-200 transition hover:bg-white/5"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => deleteUser(user)}
                            className="rounded-lg border border-rose-500/20 px-3 py-1.5 text-xs text-rose-200 transition hover:bg-rose-500/10"
                          >
                            Deactivate
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="space-y-6">
            <div className={`${glassCard} p-6`}>
              <h2 className="text-lg font-bold text-white">Roles</h2>
              <div className="mt-4 space-y-3">
                {roleCards.map((role) => (
                  <div key={role.key} className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <p className="font-semibold text-white">{role.name_en || role.name || role.key}</p>
                        <p className="text-xs uppercase tracking-[0.16em] text-slate-500">{role.key}</p>
                      </div>
                      <span className="text-xs text-slate-400">{(role.permissions || []).length} permissions</span>
                    </div>
                    <p className="mt-3 text-xs leading-6 text-slate-300">{(role.permissions || []).slice(0, 4).join(" • ") || "No permissions listed"}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className={`${glassCard} p-6`}>
              <h2 className="text-lg font-bold text-white">Feature Flags</h2>
              <div className="mt-4 flex flex-wrap gap-2">
                {availableFeatures.length ? (
                  availableFeatures.map((feature) => (
                    <span key={feature} className="rounded-full border border-cyan-500/20 bg-cyan-500/10 px-3 py-1 text-xs font-medium text-cyan-200">
                      {feature}
                    </span>
                  ))
                ) : (
                  <span className="text-sm text-slate-400">No feature flags exposed.</span>
                )}
              </div>
            </div>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <div className={`${glassCard} p-6 lg:col-span-2`}>
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold text-white">System Actions</h2>
                <p className="text-sm text-slate-400">Check active alerts, bottlenecks, and SQL improvements from the live bot runtime.</p>
              </div>
            </div>

            <div className="grid gap-4 xl:grid-cols-2">
              <div className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
                <div className="mb-3 flex items-center justify-between">
                  <p className="text-sm font-semibold text-white">Active Alerts</p>
                  <span className="text-xs text-slate-400">{combinedAlerts.length} open</span>
                </div>
                <div className="space-y-3">
                  {combinedAlerts.length ? (
                    combinedAlerts.map((alert) => (
                      <div key={alert.alert_id || alert.message} className="rounded-xl border border-white/10 bg-slate-950/70 p-3">
                        <div className="flex items-center justify-between gap-3">
                          <p className="font-semibold text-white">{alert.alert_type || alert.type || "Alert"}</p>
                          <span className={`rounded-full border px-2 py-1 text-[11px] ${toneMap[alert.severity || alert.type] || toneMap.warning}`}>
                            {alert.severity || alert.type || "warning"}
                          </span>
                        </div>
                        <p className="mt-2 text-sm text-slate-300">{alert.description || alert.message || "No details provided."}</p>
                        <div className="mt-3 flex items-center justify-between text-xs text-slate-500">
                          <span>{formatDate(alert.detected_at || alert.time)}</span>
                          {alert.alert_id ? (
                            <button
                              onClick={() => resolveAlert(alert.alert_id)}
                              className="rounded-lg border border-white/10 px-3 py-1 text-slate-200 transition hover:bg-white/5"
                            >
                              Resolve
                            </button>
                          ) : null}
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-slate-400">No active alerts.</p>
                  )}
                </div>
              </div>

              <div className="space-y-4">
                <div className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
                  <p className="text-sm font-semibold text-white">Bottlenecks</p>
                  <div className="mt-3 space-y-2 text-sm text-slate-300">
                    {(bottlenecks.bottlenecks || []).length ? (
                      (bottlenecks.bottlenecks || []).map((item, index) => (
                        <div key={`${item.bot_name || "bottleneck"}-${index}`} className="rounded-lg border border-white/10 bg-slate-950/70 p-3">
                          <p className="font-semibold text-white">{item.bot_name || item.component || "System component"}</p>
                          <p className="mt-1 text-slate-400">{item.reason || item.description || "Performance constraint detected."}</p>
                        </div>
                      ))
                    ) : (
                      <p className="text-slate-400">No bottlenecks flagged.</p>
                    )}
                  </div>
                </div>

                <div className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
                  <p className="text-sm font-semibold text-white">Resource Forecast</p>
                  <div className="mt-3 space-y-2 text-sm text-slate-300">
                    {Object.entries(forecast.forecast || {}).length ? (
                      Object.entries(forecast.forecast || {}).map(([key, value]) => (
                        <div key={key} className="flex items-center justify-between rounded-lg border border-white/10 bg-slate-950/70 px-3 py-2">
                          <span className="capitalize text-slate-400">{key.replaceAll("_", " ")}</span>
                          <span className="font-semibold text-white">{typeof value === "number" ? value.toFixed(1) : String(value)}</span>
                        </div>
                      ))
                    ) : (
                      <p className="text-slate-400">No forecast data available.</p>
                    )}
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-4 rounded-xl border border-white/10 bg-slate-900/50 p-4">
              <div className="mb-3 flex items-center justify-between">
                <p className="text-sm font-semibold text-white">SQL Rewrite Workbench</p>
                <button
                  onClick={analyzeQuery}
                  disabled={busy}
                  className="rounded-lg bg-cyan-600 px-3 py-2 text-xs font-medium text-white transition hover:bg-cyan-500 disabled:opacity-50"
                >
                  Analyze Query
                </button>
              </div>
              <textarea
                value={queryText}
                onChange={(event) => setQueryText(event.target.value)}
                className="min-h-[120px] w-full rounded-xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none"
              />
              {queryReview ? (
                <div className="mt-4 grid gap-4 xl:grid-cols-2">
                  <div className="rounded-xl border border-white/10 bg-slate-950/70 p-4">
                    <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Optimized Query</p>
                    <pre className="mt-3 overflow-x-auto whitespace-pre-wrap text-sm text-slate-200">{queryReview.optimized_query || queryReview.rewritten_query || "No rewritten SQL returned."}</pre>
                  </div>
                  <div className="rounded-xl border border-white/10 bg-slate-950/70 p-4">
                    <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Recommendations</p>
                    <ul className="mt-3 space-y-2 text-sm text-slate-300">
                      {(queryReview.recommendations || queryReview.suggestions || []).map((item, index) => (
                        <li key={`${item}-${index}`} className="rounded-lg border border-white/10 bg-slate-900/60 px-3 py-2">
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ) : null}
            </div>
          </div>

          <div className="space-y-6">
            <div className={`${glassCard} p-6`}>
              <h2 className="text-lg font-bold text-white">Monitored Bots</h2>
              <div className="mt-4 space-y-3">
                {topBots.length ? (
                  topBots.map((bot) => (
                    <div key={bot.bot_name} className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
                      <div className="flex items-center justify-between gap-3">
                        <p className="font-semibold text-white">{bot.bot_name}</p>
                        <span className={`rounded-full border px-2 py-1 text-[11px] ${toneMap[bot.status] || toneMap.info}`}>
                          {bot.status}
                        </span>
                      </div>
                      <p className="mt-2 text-xs text-slate-400">
                        {bot.response_time_ms} ms • {bot.cpu_usage}% CPU • {bot.memory_usage_mb} MB
                      </p>
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-slate-400">No bot health preview available.</p>
                )}
              </div>
            </div>

            <div className={`${glassCard} p-6`}>
              <h2 className="text-lg font-bold text-white">Action Log</h2>
              <div className="mt-4 space-y-3">
                {actionLog.length ? (
                  actionLog.map((entry) => (
                    <div key={entry.id} className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
                      <div className="flex items-center justify-between gap-3">
                        <p className="font-semibold text-white">{entry.label}</p>
                        <span className={`rounded-full border px-2 py-1 text-[11px] ${toneMap[entry.state] || toneMap.info}`}>
                          {entry.state}
                        </span>
                      </div>
                      <p className="mt-2 text-xs text-slate-500">{formatDate(entry.timestamp)}</p>
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-slate-400">No control actions captured yet.</p>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {showModal ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 px-4 backdrop-blur-sm">
          <div className="max-h-[90vh] w-full max-w-4xl overflow-y-auto rounded-3xl border border-white/10 bg-slate-900 p-6 shadow-2xl shadow-black/40">
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-white">{editingUser ? "Edit User Access" : "Create User Access"}</h2>
                <p className="text-sm text-slate-400">Manage role, bot visibility, and feature grants in English only.</p>
              </div>
              <button
                onClick={closeModal}
                className="rounded-xl border border-white/10 px-4 py-2 text-sm text-slate-200 transition hover:bg-white/5"
              >
                Close
              </button>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <label className="space-y-2">
                <span className="text-sm text-slate-300">Email</span>
                <input
                  value={form.email}
                  onChange={(event) => setForm((prev) => ({ ...prev, email: event.target.value }))}
                  className="w-full rounded-xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none"
                />
              </label>
              <label className="space-y-2">
                <span className="text-sm text-slate-300">Full name</span>
                <input
                  value={form.full_name}
                  onChange={(event) => setForm((prev) => ({ ...prev, full_name: event.target.value }))}
                  className="w-full rounded-xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none"
                />
              </label>
              <label className="space-y-2">
                <span className="text-sm text-slate-300">{editingUser ? "Reset password" : "Password"}</span>
                <input
                  type="password"
                  value={form.password}
                  onChange={(event) => setForm((prev) => ({ ...prev, password: event.target.value }))}
                  className="w-full rounded-xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none"
                />
              </label>
              <label className="space-y-2">
                <span className="text-sm text-slate-300">Role</span>
                <select
                  value={form.role}
                  onChange={(event) => setForm((prev) => ({ ...prev, role: event.target.value }))}
                  className="w-full rounded-xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none"
                >
                  {roleCards.map((role) => (
                    <option key={role.key} value={role.key}>
                      {role.name_en || role.name || role.key}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            <label className="mt-4 flex items-center gap-3 text-sm text-slate-300">
              <input
                type="checkbox"
                checked={form.is_active}
                onChange={(event) => setForm((prev) => ({ ...prev, is_active: event.target.checked }))}
              />
              Keep account active
            </label>

            <div className="mt-6 grid gap-6 lg:grid-cols-2">
              <div className="rounded-2xl border border-white/10 bg-slate-950/60 p-4">
                <div className="mb-3 flex items-center justify-between">
                  <h3 className="text-base font-semibold text-white">Assigned Bots</h3>
                  <button
                    onClick={() => toggleChoice("assigned_bots", "*")}
                    className={`rounded-full border px-3 py-1 text-xs ${form.assigned_bots.includes("*") ? "border-emerald-500/20 bg-emerald-500/10 text-emerald-200" : "border-white/10 text-slate-300"}`}
                  >
                    All bots
                  </button>
                </div>
                <div className="grid max-h-80 gap-2 overflow-y-auto pr-1">
                  {botCatalog.map((bot) => (
                    <label key={bot.key} className="flex items-start gap-3 rounded-xl border border-white/10 bg-slate-900/70 px-3 py-3 text-sm text-slate-300">
                      <input
                        type="checkbox"
                        checked={form.assigned_bots.includes("*") || form.assigned_bots.includes(bot.key)}
                        onChange={() => toggleChoice("assigned_bots", bot.key)}
                      />
                      <span>
                        <span className="block font-medium text-white">{bot.name}</span>
                        <span className="block text-xs text-slate-500">{bot.category}</span>
                      </span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="rounded-2xl border border-white/10 bg-slate-950/60 p-4">
                <h3 className="mb-3 text-base font-semibold text-white">Feature Flags</h3>
                <div className="grid max-h-80 gap-2 overflow-y-auto pr-1">
                  {availableFeatures.map((feature) => (
                    <label key={feature} className="flex items-center gap-3 rounded-xl border border-white/10 bg-slate-900/70 px-3 py-3 text-sm text-slate-300">
                      <input
                        type="checkbox"
                        checked={form.features.includes(feature)}
                        onChange={() => toggleChoice("features", feature)}
                      />
                      <span>{feature}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>

            <div className="mt-6 flex justify-end gap-3">
              <button
                onClick={closeModal}
                className="rounded-xl border border-white/10 px-4 py-2 text-sm text-slate-200 transition hover:bg-white/5"
              >
                Cancel
              </button>
              <button
                onClick={saveUser}
                disabled={savingUser}
                className="rounded-xl bg-emerald-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-emerald-500 disabled:opacity-50"
              >
                {savingUser ? "Saving..." : editingUser ? "Save Changes" : "Create User"}
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
