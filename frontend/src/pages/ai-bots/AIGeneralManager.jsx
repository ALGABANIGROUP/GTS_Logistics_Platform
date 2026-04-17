import { useEffect, useMemo, useState } from "react";
import axiosClient from "../../api/axiosClient";

const BOT_KEY = "general_manager";
const glassCard =
  "rounded-2xl border border-white/10 bg-white/5 shadow-lg shadow-black/30 backdrop-blur-xl";

const monitoredBots = [
  "partner_bot",
  "customer_service",
  "dispatcher",
  "documents_manager",
  "sales_bot",
  "safety_bot",
  "intelligence_bot",
  "mapleload_bot",
  "operations_manager_bot",
  "freight_broker",
  "information_coordinator",
  "legal_bot",
  "security_bot",
  "system_bot",
  "maintenance_dev",
  "marketing_manager",
  "trainer_bot",
];

const toneMap = {
  excellent: "border-emerald-500/20 bg-emerald-500/10 text-emerald-200",
  good: "border-blue-500/20 bg-blue-500/10 text-blue-200",
  warning: "border-amber-500/20 bg-amber-500/10 text-amber-200",
  improving: "border-cyan-500/20 bg-cyan-500/10 text-cyan-200",
  high: "border-rose-500/20 bg-rose-500/10 text-rose-200",
  medium: "border-amber-500/20 bg-amber-500/10 text-amber-200",
  active: "border-emerald-500/20 bg-emerald-500/10 text-emerald-200",
  planned: "border-slate-500/20 bg-slate-500/10 text-slate-300",
  approved: "border-emerald-500/20 bg-emerald-500/10 text-emerald-200",
  pending: "border-amber-500/20 bg-amber-500/10 text-amber-200",
  recommended: "border-emerald-500/20 bg-emerald-500/10 text-emerald-200",
  proceed_with_caution:
    "border-orange-500/20 bg-orange-500/10 text-orange-200",
};

function formatDate(value) {
  if (!value) return "Unknown";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleString();
}

function formatCompactNumber(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) return String(value ?? "0");
  return new Intl.NumberFormat("en", {
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(number);
}

function pctFromTarget(current, target) {
  const safeTarget = Number(target) || 1;
  return Math.max(0, Math.min(100, (Number(current || 0) / safeTarget) * 100));
}

export default function AIGeneralManager({ botKey = BOT_KEY }) {
  const resolvedBotKey = botKey || BOT_KEY;
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [status, setStatus] = useState({});
  const [config, setConfig] = useState({});
  const [dashboard, setDashboard] = useState({});
  const [forecast, setForecast] = useState({});
  const [recommendations, setRecommendations] = useState({});
  const [initiatives, setInitiatives] = useState([]);
  const [decisions, setDecisions] = useState([]);
  const [botStatuses, setBotStatuses] = useState([]);
  const [scenarioType, setScenarioType] = useState("expansion");
  const [scenarioTitle, setScenarioTitle] = useState("US lane expansion");
  const [scenarioDescription, setScenarioDescription] = useState(
    "Launch a new cross-border growth initiative with phased hiring and carrier onboarding."
  );
  const [scenarioResult, setScenarioResult] = useState(null);
  const [actionLog, setActionLog] = useState([]);

  const appendLog = (label, payload, state = "good") => {
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

  const runAction = async (label, context) => {
    setBusy(true);
    try {
      const res = await axiosClient.post(
        `/api/v1/ai/bots/available/${resolvedBotKey}/run`,
        { context }
      );
      const payload = res.data?.data || res.data?.result || res.data || {};
      appendLog(label, payload, "good");
      return payload;
    } catch (actionError) {
      const message =
        actionError?.response?.data?.detail || actionError.message || "Action failed";
      appendLog(label, { error: message }, "high");
      throw actionError;
    } finally {
      setBusy(false);
    }
  };

  const loadDashboard = async () => {
    setLoading(true);
    setError("");
    try {
      const [
        statusRes,
        configRes,
        dashboardRes,
        forecastRes,
        recommendationRes,
        initiativesRes,
        decisionsRes,
        botStatusResults,
      ] = await Promise.all([
        axiosClient.get(`/api/v1/ai/bots/available/${resolvedBotKey}/status`),
        axiosClient.post(`/api/v1/ai/bots/available/${resolvedBotKey}/run`, {
          context: { action: "config" },
        }),
        axiosClient.post(`/api/v1/ai/bots/available/${resolvedBotKey}/run`, {
          context: { action: "dashboard" },
        }),
        axiosClient.post(`/api/v1/ai/bots/available/${resolvedBotKey}/run`, {
          context: { action: "forecast", months: 6 },
        }),
        axiosClient.post(`/api/v1/ai/bots/available/${resolvedBotKey}/run`, {
          context: { action: "strategic_recommendations" },
        }),
        axiosClient.post(`/api/v1/ai/bots/available/${resolvedBotKey}/run`, {
          context: { action: "get_initiatives" },
        }),
        axiosClient.post(`/api/v1/ai/bots/available/${resolvedBotKey}/run`, {
          context: { action: "get_decisions" },
        }),
        Promise.allSettled(
          monitoredBots.map((name) =>
            axiosClient.get(`/api/v1/ai/bots/available/${name}/status`)
          )
        ),
      ]);

      setStatus(statusRes.data?.data || statusRes.data?.status || statusRes.data || {});
      setConfig(configRes.data?.data || configRes.data?.result || configRes.data || {});
      setDashboard(
        dashboardRes.data?.data || dashboardRes.data?.result || dashboardRes.data || {}
      );
      setForecast(
        forecastRes.data?.data || forecastRes.data?.result || forecastRes.data || {}
      );
      setRecommendations(
        recommendationRes.data?.data ||
          recommendationRes.data?.result ||
          recommendationRes.data ||
          {}
      );
      setInitiatives(
        initiativesRes.data?.data?.initiatives ||
          initiativesRes.data?.result?.initiatives ||
          initiativesRes.data?.initiatives ||
          []
      );
      setDecisions(
        decisionsRes.data?.data?.decisions ||
          decisionsRes.data?.result?.decisions ||
          decisionsRes.data?.decisions ||
          []
      );

      const normalizedStatuses = botStatusResults.map((result, index) => {
        const key = monitoredBots[index];
        if (result.status === "fulfilled") {
          const payload =
            result.value.data?.data ||
            result.value.data?.status ||
            result.value.data ||
            {};
          return {
            key,
            online: true,
            name: payload.display_name || key,
            mode: payload.mode || "runtime",
            version: payload.version || "n/a",
            payload,
          };
        }
        return {
          key,
          online: false,
          name: key,
          mode: "unreachable",
          version: "n/a",
          payload: {},
        };
      });
      setBotStatuses(normalizedStatuses);
    } catch (loadError) {
      setError(
        loadError?.response?.data?.detail ||
          loadError.message ||
          "Failed to load General Manager dashboard."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, [resolvedBotKey]);

  const runScenario = async () => {
    try {
      const payload = await runAction("Evaluate Decision", {
        action: "evaluate_decision",
        decision: {
          type: scenarioType,
          title: scenarioTitle,
          description: scenarioDescription,
        },
      });
      setScenarioResult(payload);
    } catch (scenarioError) {
      setError(
        scenarioError?.response?.data?.detail ||
          scenarioError.message ||
          "Unable to evaluate scenario."
      );
    }
  };

  const unifiedKpi = dashboard.unified_kpi || {};
  const departmentPerformance = dashboard.department_performance || {};
  const criticalAlerts = dashboard.critical_alerts || [];
  const strategicRecommendations = dashboard.strategic_recommendations || [];
  const financialSnapshot = dashboard.financial_snapshot || {};
  const operationalSnapshot = dashboard.operational_snapshot || {};
  const customerSnapshot = dashboard.customer_snapshot || {};
  const expansionSnapshot = dashboard.expansion_snapshot || {};
  const intelligenceSnapshot = dashboard.intelligence_snapshot || {};
  const forecastRows = forecast.forecasts || [];

  const onlineCount = useMemo(
    () => botStatuses.filter((item) => item.online).length,
    [botStatuses]
  );

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950">
        <div className="text-center">
          <div className="mx-auto mb-4 h-16 w-16 animate-spin rounded-full border-b-2 border-indigo-400" />
          <p className="text-slate-300">Loading General Manager dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950">
      <div className="border-b border-white/10 bg-slate-950/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-5">
          <div className="flex items-center gap-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-500 to-violet-800 text-lg font-bold text-white shadow-lg shadow-indigo-950/40">
              GM
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">AI General Manager</h1>
              <p className="text-sm text-slate-300">
                Unified executive oversight, strategic forecasting, live alerts, and cross-bot command visibility.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className={`${glassCard} px-4 py-2`}>
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Version</p>
              <p className="text-sm font-semibold text-white">
                {status.version || config.version || "2.0.0"}
              </p>
            </div>
            <div className={`${glassCard} px-4 py-2`}>
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Connected Bots</p>
              <p className="text-sm font-semibold text-white">
                {onlineCount}/{botStatuses.length}
              </p>
            </div>
            <button
              onClick={loadDashboard}
              disabled={busy}
              className="rounded-xl border border-white/10 px-4 py-2 text-sm font-medium text-slate-200 transition hover:bg-white/5 disabled:opacity-50"
            >
              Refresh
            </button>
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-7xl space-y-6 px-4 py-6">
        {error ? (
          <div className="rounded-2xl border border-rose-500/20 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">
            {error}
          </div>
        ) : null}

        <div className="overflow-hidden rounded-3xl bg-gradient-to-br from-indigo-600 via-violet-700 to-slate-900 p-6 text-white shadow-2xl shadow-indigo-950/30">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-[0.24em] text-indigo-100/70">Unified KPI</p>
              <h2 className="mt-2 text-6xl font-bold">{unifiedKpi.current || 0}</h2>
              <p className="mt-2 text-sm text-indigo-100/80">
                Target {unifiedKpi.target || 90} • Change {unifiedKpi.change || "0"}
              </p>
            </div>
            <span
              className={`rounded-full border px-3 py-1 text-xs font-semibold ${
                toneMap[unifiedKpi.status] || toneMap.improving
              }`}
            >
              {unifiedKpi.status || "improving"}
            </span>
          </div>

          <div className="mt-5 h-3 overflow-hidden rounded-full bg-white/20">
            <div
              className="h-full rounded-full bg-white"
              style={{
                width: `${pctFromTarget(unifiedKpi.current, unifiedKpi.target)}%`,
              }}
            />
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-5">
            {[
              { label: "Revenue", value: formatCompactNumber(financialSnapshot.revenue) },
              { label: "Profit Margin", value: `${financialSnapshot.profit_margin || 0}%` },
              { label: "On-Time Delivery", value: `${operationalSnapshot.on_time_delivery || 0}%` },
              { label: "Customer Satisfaction", value: customerSnapshot.customer_satisfaction || 0 },
              { label: "Opportunity Signals", value: intelligenceSnapshot.new_opportunities || 0 },
            ].map((item) => (
              <div
                key={item.label}
                className="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur"
              >
                <p className="text-xs uppercase tracking-[0.16em] text-indigo-100/70">{item.label}</p>
                <p className="mt-3 text-2xl font-bold">{item.value}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-4">
          {[
            {
              label: "Revenue",
              value: formatCompactNumber(financialSnapshot.revenue || 0),
              detail: `Growth ${financialSnapshot.monthly_growth || 0}%`,
              tone: "from-fuchsia-500 to-rose-700",
            },
            {
              label: "Shipments",
              value: formatCompactNumber(operationalSnapshot.total_shipments || 0),
              detail: `${operationalSnapshot.active_drivers || 0} active drivers`,
              tone: "from-cyan-500 to-blue-700",
            },
            {
              label: "Open Tickets",
              value: customerSnapshot.open_tickets || 0,
              detail: `${customerSnapshot.new_customers || 0} new customers`,
              tone: "from-amber-500 to-orange-700",
            },
            {
              label: "International Markets",
              value: expansionSnapshot.active_markets?.length || 0,
              detail: `${expansionSnapshot.planned_markets?.length || 0} planned`,
              tone: "from-emerald-500 to-teal-700",
            },
          ].map((item) => (
            <div
              key={item.label}
              className={`rounded-2xl bg-gradient-to-br ${item.tone} p-5 text-white shadow-lg`}
            >
              <p className="text-3xl font-bold">{item.value}</p>
              <p className="mt-1 text-sm text-white/80">{item.label}</p>
              <p className="mt-2 text-xs text-white/70">{item.detail}</p>
            </div>
          ))}
        </div>

        <div className="grid gap-6 xl:grid-cols-[1.35fr_0.95fr]">
          <div className={`${glassCard} p-6`}>
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold text-white">Unified Bot Command View</h2>
                <p className="text-sm text-slate-400">
                  Live status snapshots for the cross-functional bot network.
                </p>
              </div>
              <span className="text-sm text-slate-300">
                {onlineCount}/{botStatuses.length} online
              </span>
            </div>

            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
              {botStatuses.map((bot) => (
                <div
                  key={bot.key}
                  className="rounded-xl border border-white/10 bg-slate-900/50 p-4"
                >
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-semibold text-white">
                      {String(bot.name).replaceAll("_", " ")}
                    </p>
                    <span
                      className={`h-2.5 w-2.5 rounded-full ${
                        bot.online ? "bg-emerald-400" : "bg-rose-400"
                      }`}
                    />
                  </div>
                  <p className="mt-2 text-xs uppercase tracking-[0.16em] text-slate-500">
                    {bot.mode}
                  </p>
                  <p className="mt-3 text-sm text-slate-300">Version {bot.version}</p>
                </div>
              ))}
            </div>
          </div>

          <div className={`${glassCard} p-6`}>
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold text-white">Active Alerts</h2>
                <p className="text-sm text-slate-400">
                  Issues that require executive follow-up now.
                </p>
              </div>
              <span className="text-sm text-slate-300">{criticalAlerts.length} open</span>
            </div>
            <div className="space-y-3">
              {criticalAlerts.map((alert) => (
                <div
                  key={alert.id}
                  className="rounded-xl border border-white/10 bg-slate-900/50 p-4"
                >
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-semibold text-white">{alert.title}</p>
                    <span
                      className={`rounded-full border px-2 py-1 text-[11px] ${
                        toneMap[alert.severity] || toneMap.medium
                      }`}
                    >
                      {alert.severity}
                    </span>
                  </div>
                  <p className="mt-2 text-sm text-slate-400">Source: {alert.source}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <div className={`${glassCard} p-6 lg:col-span-2`}>
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold text-white">Strategic Forecast</h2>
                <p className="text-sm text-slate-400">
                  Six-month forward view from the General Manager bot.
                </p>
              </div>
              <span className="text-sm text-slate-300">{forecast.growth_rate || ""}</span>
            </div>

            <div className="grid gap-3">
              {forecastRows.map((row) => (
                <div
                  key={row.month}
                  className="rounded-xl border border-white/10 bg-slate-900/50 p-4"
                >
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <p className="font-semibold text-white">{row.month}</p>
                    <span
                      className={`rounded-full border px-2 py-1 text-[11px] ${
                        toneMap[row.confidence] || toneMap.good
                      }`}
                    >
                      {row.confidence}
                    </span>
                  </div>
                  <div className="mt-3 grid gap-3 md:grid-cols-3 text-sm">
                    <div className="rounded-lg bg-slate-950/70 px-3 py-2 text-slate-300">
                      Revenue:{" "}
                      <span className="font-semibold text-white">
                        {formatCompactNumber(row.predicted_revenue)}
                      </span>
                    </div>
                    <div className="rounded-lg bg-slate-950/70 px-3 py-2 text-slate-300">
                      Customers:{" "}
                      <span className="font-semibold text-white">
                        {row.predicted_customers}
                      </span>
                    </div>
                    <div className="rounded-lg bg-slate-950/70 px-3 py-2 text-slate-300">
                      Shipments:{" "}
                      <span className="font-semibold text-white">
                        {row.predicted_shipments}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className={`${glassCard} p-6`}>
            <h2 className="text-lg font-bold text-white">Department Scores</h2>
            <div className="mt-4 space-y-3">
              {Object.entries(departmentPerformance).map(([key, value]) => (
                <div
                  key={key}
                  className="rounded-xl border border-white/10 bg-slate-900/50 p-4"
                >
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-semibold capitalize text-white">
                      {key.replaceAll("_", " ")}
                    </p>
                    <span
                      className={`rounded-full border px-2 py-1 text-[11px] ${
                        toneMap[value.status] || toneMap.good
                      }`}
                    >
                      {value.status}
                    </span>
                  </div>
                  <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-800">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-indigo-400 to-violet-500"
                      style={{ width: `${Math.min(Number(value.score || 0), 100)}%` }}
                    />
                  </div>
                  <p className="mt-2 text-sm text-slate-300">
                    {value.score}% • Change {value.change}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="grid gap-6 xl:grid-cols-[1.2fr_1fr]">
          <div className={`${glassCard} p-6`}>
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold text-white">What-If Scenario Simulator</h2>
                <p className="text-sm text-slate-400">
                  Evaluate a leadership decision before committing budget or operational change.
                </p>
              </div>
              <button
                onClick={runScenario}
                disabled={busy}
                className="rounded-xl bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-indigo-500 disabled:opacity-50"
              >
                Run Scenario
              </button>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <label className="space-y-2">
                <span className="text-sm text-slate-300">Scenario Type</span>
                <select
                  value={scenarioType}
                  onChange={(event) => setScenarioType(event.target.value)}
                  className="w-full rounded-xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none"
                >
                  <option value="expansion">Expansion</option>
                  <option value="hiring">Hiring</option>
                  <option value="technology">Technology</option>
                </select>
              </label>
              <label className="space-y-2">
                <span className="text-sm text-slate-300">Scenario Title</span>
                <input
                  value={scenarioTitle}
                  onChange={(event) => setScenarioTitle(event.target.value)}
                  className="w-full rounded-xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none"
                />
              </label>
            </div>

            <label className="mt-4 block space-y-2">
              <span className="text-sm text-slate-300">Scenario Description</span>
              <textarea
                value={scenarioDescription}
                onChange={(event) => setScenarioDescription(event.target.value)}
                className="min-h-[120px] w-full rounded-xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none"
              />
            </label>

            {scenarioResult ? (
              <div className="mt-4 space-y-3 rounded-2xl border border-white/10 bg-slate-900/50 p-4">
                <div className="flex items-center justify-between">
                  <p className="font-semibold text-white">Scenario Assessment</p>
                  <span
                    className={`rounded-full border px-2 py-1 text-[11px] ${
                      toneMap[scenarioResult.analysis?.recommendation] ||
                      toneMap.warning
                    }`}
                  >
                    {scenarioResult.analysis?.recommendation || "review"}
                  </span>
                </div>
                <p className="text-sm text-slate-300">
                  Success probability:{" "}
                  <span className="font-semibold text-white">
                    {scenarioResult.analysis?.success_probability || 0}%
                  </span>
                </p>
                <p className="text-sm text-slate-300">
                  Time to impact:{" "}
                  <span className="font-semibold text-white">
                    {scenarioResult.analysis?.time_to_realize || "Unknown"}
                  </span>
                </p>
                <div className="grid gap-3 md:grid-cols-2">
                  <div className="rounded-xl bg-slate-950/70 p-3">
                    <p className="mb-2 text-xs uppercase tracking-[0.16em] text-slate-500">
                      Positive Impacts
                    </p>
                    <ul className="space-y-2 text-sm text-slate-300">
                      {(scenarioResult.analysis?.expected_positive_impacts || []).map(
                        (item) => (
                          <li key={item}>{item}</li>
                        )
                      )}
                    </ul>
                  </div>
                  <div className="rounded-xl bg-slate-950/70 p-3">
                    <p className="mb-2 text-xs uppercase tracking-[0.16em] text-slate-500">
                      Risks
                    </p>
                    <ul className="space-y-2 text-sm text-slate-300">
                      {(scenarioResult.risk_factors || []).map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            ) : null}
          </div>

          <div className="space-y-6">
            <div className={`${glassCard} p-6`}>
              <h2 className="text-lg font-bold text-white">Strategic Initiatives</h2>
              <div className="mt-4 space-y-3">
                {initiatives.map((initiative) => (
                  <div
                    key={initiative.id}
                    className="rounded-xl border border-white/10 bg-slate-900/50 p-4"
                  >
                    <div className="flex items-center justify-between gap-3">
                      <p className="font-semibold text-white">{initiative.title}</p>
                      <span
                        className={`rounded-full border px-2 py-1 text-[11px] ${
                          toneMap[initiative.status] || toneMap.good
                        }`}
                      >
                        {initiative.status}
                      </span>
                    </div>
                    <p className="mt-2 text-sm text-slate-400">
                      {initiative.owner} • {initiative.target_completion}
                    </p>
                    <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-800">
                      <div
                        className="h-full rounded-full bg-gradient-to-r from-emerald-400 to-cyan-500"
                        style={{ width: `${initiative.progress || 0}%` }}
                      />
                    </div>
                    <p className="mt-2 text-xs text-slate-300">
                      {initiative.progress || 0}% complete
                    </p>
                  </div>
                ))}
              </div>
            </div>

            <div className={`${glassCard} p-6`}>
              <h2 className="text-lg font-bold text-white">Decision Log</h2>
              <div className="mt-4 space-y-3">
                {decisions.map((decision) => (
                  <div
                    key={decision.id}
                    className="rounded-xl border border-white/10 bg-slate-900/50 p-4"
                  >
                    <div className="flex items-center justify-between gap-3">
                      <p className="font-semibold text-white">{decision.title}</p>
                      <span
                        className={`rounded-full border px-2 py-1 text-[11px] ${
                          toneMap[decision.outcome] || toneMap.warning
                        }`}
                      >
                        {decision.outcome}
                      </span>
                    </div>
                    <p className="mt-2 text-sm text-slate-400">
                      {decision.description}
                    </p>
                    <p className="mt-2 text-xs text-slate-500">
                      {formatDate(decision.logged_at)}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            <div className={`${glassCard} p-6`}>
              <h2 className="text-lg font-bold text-white">Action Log</h2>
              <div className="mt-4 space-y-3">
                {actionLog.length ? (
                  actionLog.map((entry) => (
                    <div
                      key={entry.id}
                      className="rounded-xl border border-white/10 bg-slate-900/50 p-4"
                    >
                      <div className="flex items-center justify-between gap-3">
                        <p className="font-semibold text-white">{entry.label}</p>
                        <span
                          className={`rounded-full border px-2 py-1 text-[11px] ${
                            toneMap[entry.state] || toneMap.good
                          }`}
                        >
                          {entry.state}
                        </span>
                      </div>
                      <p className="mt-2 text-xs text-slate-500">
                        {formatDate(entry.timestamp)}
                      </p>
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-slate-400">
                    No executive actions captured yet.
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>

        <div className={`${glassCard} p-6`}>
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold text-white">
                Strategic Recommendations
              </h2>
              <p className="text-sm text-slate-400">
                Current SWOT-driven actions proposed by the General Manager bot.
              </p>
            </div>
          </div>
          <div className="grid gap-4 md:grid-cols-3">
            {strategicRecommendations.map((item) => (
              <div
                key={item.id}
                className="rounded-xl border border-white/10 bg-slate-900/50 p-4"
              >
                <div className="flex items-center justify-between gap-3">
                  <p className="font-semibold text-white">{item.title}</p>
                  <span
                    className={`rounded-full border px-2 py-1 text-[11px] ${
                      toneMap[item.priority] || toneMap.medium
                    }`}
                  >
                    {item.priority}
                  </span>
                </div>
                <p className="mt-2 text-sm text-slate-400">{item.impact}</p>
                <p className="mt-3 text-xs text-slate-500">
                  {item.owner} • {item.deadline}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
