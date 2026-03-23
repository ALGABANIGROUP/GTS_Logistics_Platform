import { useEffect, useMemo, useState } from "react";
import axiosClient from "../../api/axiosClient";

const BOT_KEY = "intelligence_bot";
const glassCard =
  "rounded-2xl border border-white/10 bg-white/5 shadow-lg shadow-black/30 backdrop-blur-xl";

const toneMap = {
  high: "border-rose-500/20 bg-rose-500/10 text-rose-200",
  medium: "border-amber-500/20 bg-amber-500/10 text-amber-200",
  low: "border-emerald-500/20 bg-emerald-500/10 text-emerald-200",
  expanding: "border-cyan-500/20 bg-cyan-500/10 text-cyan-200",
  stable: "border-emerald-500/20 bg-emerald-500/10 text-emerald-200",
  improving: "border-blue-500/20 bg-blue-500/10 text-blue-200",
  watch: "border-orange-500/20 bg-orange-500/10 text-orange-200",
  pilot: "border-violet-500/20 bg-violet-500/10 text-violet-200",
  recommended: "border-emerald-500/20 bg-emerald-500/10 text-emerald-200",
};

function pct(value) {
  const num = Number(value || 0);
  return `${Math.round(num)}%`;
}

function formatDate(value) {
  if (!value) return "Unknown";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleString();
}

function compactCurrency(value) {
  const num = Number(value || 0);
  return new Intl.NumberFormat("en", {
    style: "currency",
    currency: "USD",
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(num);
}

export default function AIIntelligenceBot({ botKey = BOT_KEY }) {
  const resolvedBotKey = botKey || BOT_KEY;
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [status, setStatus] = useState({});
  const [config, setConfig] = useState({});
  const [dashboard, setDashboard] = useState({});
  const [executiveReport, setExecutiveReport] = useState({});
  const [customReport, setCustomReport] = useState(null);
  const [actionLog, setActionLog] = useState([]);

  const appendLog = (label, payload, state = "stable") => {
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

  const runAction = async (label, context) => {
    setBusy(true);
    setNotice("");
    try {
      const res = await axiosClient.post(
        `/api/v1/ai/bots/available/${resolvedBotKey}/run`,
        { context }
      );
      const payload = res.data?.data || res.data?.result || res.data || {};
      appendLog(label, payload, "stable");
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
      const [statusRes, configRes, dashboardRes, executiveRes] = await Promise.all([
        axiosClient.get(`/api/v1/ai/bots/available/${resolvedBotKey}/status`),
        axiosClient.post(`/api/v1/ai/bots/available/${resolvedBotKey}/run`, {
          context: { action: "config" },
        }),
        axiosClient.post(`/api/v1/ai/bots/available/${resolvedBotKey}/run`, {
          context: { action: "dashboard" },
        }),
        axiosClient.post(`/api/v1/ai/bots/available/${resolvedBotKey}/run`, {
          context: { action: "executive_report", report_type: "weekly" },
        }),
      ]);

      setStatus(statusRes.data?.data || statusRes.data?.status || statusRes.data || {});
      setConfig(configRes.data?.data || configRes.data?.result || configRes.data || {});
      setDashboard(dashboardRes.data?.data || dashboardRes.data?.result || dashboardRes.data || {});
      setExecutiveReport(
        executiveRes.data?.data || executiveRes.data?.result || executiveRes.data || {}
      );
    } catch (loadError) {
      setError(
        loadError?.response?.data?.detail ||
          loadError.message ||
          "Failed to load Intelligence dashboard."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, [resolvedBotKey]);

  const buildBoardReport = async () => {
    try {
      const payload = await runAction("Generate Monthly Executive Report", {
        action: "executive_report",
        report_type: "monthly",
      });
      setExecutiveReport(payload);
      setNotice("Monthly executive report generated.");
    } catch (actionError) {
      setError(
        actionError?.response?.data?.detail ||
          actionError.message ||
          "Unable to generate executive report."
      );
    }
  };

  const buildCustomReport = async () => {
    try {
      const payload = await runAction("Generate Custom Report", {
        action: "custom_report",
        sections: ["executive_summary", "churn", "forecast", "kpis", "geo"],
      });
      setCustomReport(payload);
      setNotice("Custom report generated.");
    } catch (actionError) {
      setError(
        actionError?.response?.data?.detail ||
          actionError.message ||
          "Unable to generate custom report."
      );
    }
  };

  const overview = dashboard.overview || {};
  const aiEnhancements = dashboard.ai_enhancements || {};
  const advancedReports = dashboard.advanced_reports || {};
  const churn = aiEnhancements.churn || {};
  const demand = aiEnhancements.demand || {};
  const pricing = aiEnhancements.pricing || {};
  const routes = aiEnhancements.routes || {};
  const anomalies = aiEnhancements.anomalies || {};
  const sentiment = aiEnhancements.sentiment || {};
  const geo = advancedReports.geo_analytics || {};
  const finance = advancedReports.financial_analytics || {};
  const kpis = dashboard.kpis || {};

  const topKpiRows = useMemo(
    () => [...(kpis.financial || []), ...(kpis.operational || []), ...(kpis.customer || [])].slice(0, 6),
    [kpis]
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 px-6 py-8 text-slate-100">
        <div className="mx-auto max-w-7xl">
          <div className={`${glassCard} p-8 text-sm text-slate-300`}>Loading intelligence dashboard...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(56,189,248,0.14),_transparent_32%),linear-gradient(180deg,_#020617_0%,_#111827_100%)] px-6 py-8 text-slate-100">
      <div className="mx-auto flex max-w-7xl flex-col gap-6">
        <section className={`${glassCard} overflow-hidden p-8`}>
          <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-3xl">
              <span className="inline-flex rounded-full border border-cyan-400/30 bg-cyan-400/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.3em] text-cyan-200">
                AI Intelligence Bot
              </span>
              <h1 className="mt-4 text-4xl font-semibold tracking-tight text-white">
                Predictive Analytics and Advanced Reporting
              </h1>
              <p className="mt-3 text-sm leading-6 text-slate-300">
                Unified visibility for churn risk, demand forecasting, pricing opportunities,
                anomaly detection, sentiment monitoring, geo analytics, and executive reports.
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <button
                type="button"
                onClick={loadDashboard}
                disabled={busy}
                className="rounded-full border border-white/15 bg-white/10 px-4 py-2 text-sm text-white transition hover:bg-white/15 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Refresh Intelligence
              </button>
              <button
                type="button"
                onClick={buildBoardReport}
                disabled={busy}
                className="rounded-full border border-cyan-400/30 bg-cyan-400/15 px-4 py-2 text-sm font-medium text-cyan-100 transition hover:bg-cyan-400/20 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Generate Executive Report
              </button>
              <button
                type="button"
                onClick={buildCustomReport}
                disabled={busy}
                className="rounded-full border border-violet-400/30 bg-violet-400/15 px-4 py-2 text-sm font-medium text-violet-100 transition hover:bg-violet-400/20 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Build Custom Report
              </button>
            </div>
          </div>
          <div className="mt-6 flex flex-wrap items-center gap-4 text-xs text-slate-400">
            <span>Status: {status.message || "Active"}</span>
            <span>Mode: {status.mode || config.mode || "analytics"}</span>
            <span>Version: {status.version || config.version || "n/a"}</span>
          </div>
          {notice ? <p className="mt-4 text-sm text-cyan-200">{notice}</p> : null}
          {error ? <p className="mt-4 text-sm text-rose-200">{error}</p> : null}
        </section>

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {[
            { label: "Forecast Accuracy", value: pct(overview.forecast_accuracy), detail: "Model confidence across tracked signals" },
            { label: "At-Risk Customers", value: String(overview.at_risk_customers || 0), detail: "High-priority retention cases" },
            { label: "Active Anomalies", value: String(overview.active_anomalies || 0), detail: "Signals requiring operational review" },
            { label: "Overall Score", value: pct(overview.overall_score), detail: "Unified analytics performance score" },
          ].map((item) => (
            <article key={item.label} className={`${glassCard} p-5`}>
              <p className="text-xs uppercase tracking-[0.24em] text-slate-400">{item.label}</p>
              <p className="mt-4 text-3xl font-semibold text-white">{item.value}</p>
              <p className="mt-2 text-sm text-slate-400">{item.detail}</p>
            </article>
          ))}
        </section>

        <section className="grid gap-6 xl:grid-cols-[1.2fr,0.8fr]">
          <article className={`${glassCard} p-6`}>
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-white">Customer Churn Watchlist</h2>
              <span className="text-sm text-slate-400">{churn.at_risk_count || 0} at risk</span>
            </div>
            <div className="mt-5 space-y-3">
              {(churn.customers || []).map((customer) => (
                <div key={customer.customer_id} className="rounded-2xl border border-white/8 bg-black/20 p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="font-medium text-white">{customer.name}</p>
                      <p className="text-sm text-slate-400">
                        {customer.customer_id} · {customer.segment}
                      </p>
                    </div>
                    <span className={`rounded-full px-3 py-1 text-xs font-medium ${toneMap[customer.risk_level?.toLowerCase()] || toneMap.medium}`}>
                      {customer.churn_probability}% {customer.risk_level}
                    </span>
                  </div>
                  <ul className="mt-3 space-y-1 text-sm text-slate-300">
                    {(customer.drivers || []).slice(0, 3).map((driver) => (
                      <li key={driver}>• {driver}</li>
                    ))}
                  </ul>
                  <p className="mt-3 text-sm text-cyan-200">{customer.recommended_action}</p>
                </div>
              ))}
            </div>
          </article>

          <article className={`${glassCard} p-6`}>
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-white">Demand Forecast</h2>
              <span className="text-sm text-slate-400">{demand.trend || "stable"}</span>
            </div>
            <div className="mt-5 rounded-2xl border border-white/8 bg-black/20 p-4">
              <p className="text-sm text-slate-400">Total predicted shipments</p>
              <p className="mt-2 text-3xl font-semibold text-white">
                {demand.total_predicted_shipments || 0}
              </p>
              <p className="mt-2 text-sm text-cyan-200">
                Peak period: {demand.peak_period?.period || "Unknown"} ·{" "}
                {demand.peak_period?.predicted_shipments || 0} shipments
              </p>
            </div>
            <div className="mt-4 space-y-3">
              {(demand.periods || []).slice(0, 5).map((period) => (
                <div key={period.period} className="flex items-center justify-between rounded-xl border border-white/8 bg-white/[0.03] px-4 py-3">
                  <div>
                    <p className="text-sm font-medium text-white">{period.period}</p>
                    <p className="text-xs text-slate-400">{period.top_region}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-cyan-200">{period.predicted_shipments}</p>
                    <p className="text-xs text-slate-400">{period.confidence}% confidence</p>
                  </div>
                </div>
              ))}
            </div>
          </article>
        </section>

        <section className="grid gap-6 xl:grid-cols-3">
          <article className={`${glassCard} p-6`}>
            <h2 className="text-lg font-semibold text-white">Dynamic Pricing</h2>
            <div className="mt-5 space-y-3">
              {(pricing.lanes || []).map((lane) => (
                <div key={lane.lane} className="rounded-2xl border border-white/8 bg-black/20 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-medium text-white">{lane.lane}</p>
                    <span className="text-sm text-emerald-200">+{lane.uplift_percent}%</span>
                  </div>
                  <p className="mt-2 text-sm text-slate-300">
                    {compactCurrency(lane.current_rate)} → {compactCurrency(lane.recommended_rate)}
                  </p>
                  <p className="mt-2 text-sm text-slate-400">{lane.reason}</p>
                </div>
              ))}
            </div>
          </article>

          <article className={`${glassCard} p-6`}>
            <h2 className="text-lg font-semibold text-white">Route Optimization</h2>
            <div className="mt-5 space-y-3">
              {(routes.routes || []).map((route) => (
                <div key={route.route} className="rounded-2xl border border-white/8 bg-black/20 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-medium text-white">{route.route}</p>
                    <span className={`rounded-full px-3 py-1 text-xs ${toneMap[route.status] || toneMap.improving}`}>
                      {route.status}
                    </span>
                  </div>
                  <div className="mt-3 grid grid-cols-3 gap-2 text-sm text-slate-300">
                    <span>{route.distance_saved_km} km saved</span>
                    <span>{route.time_saved_minutes} min saved</span>
                    <span>{route.fuel_saved_percent}% fuel</span>
                  </div>
                </div>
              ))}
            </div>
          </article>

          <article className={`${glassCard} p-6`}>
            <h2 className="text-lg font-semibold text-white">Anomaly Watch</h2>
            <div className="mt-5 space-y-3">
              {(anomalies.anomalies || []).map((item) => (
                <div key={item.metric} className="rounded-2xl border border-white/8 bg-black/20 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-medium text-white">{item.metric.replaceAll("_", " ")}</p>
                    <span className={`rounded-full px-3 py-1 text-xs ${toneMap[item.severity] || toneMap.medium}`}>
                      {item.severity}
                    </span>
                  </div>
                  <p className="mt-2 text-sm text-slate-300">
                    Expected {item.expected} · Actual {item.actual} · {item.deviation_percent}% deviation
                  </p>
                  <p className="mt-2 text-sm text-slate-400">{item.recommendation}</p>
                </div>
              ))}
            </div>
          </article>
        </section>

        <section className="grid gap-6 xl:grid-cols-[0.9fr,1.1fr]">
          <article className={`${glassCard} p-6`}>
            <h2 className="text-lg font-semibold text-white">Sentiment Monitor</h2>
            <div className="mt-5 rounded-2xl border border-white/8 bg-black/20 p-4">
              <p className="text-sm text-slate-400">Overall sentiment</p>
              <p className="mt-2 text-2xl font-semibold text-white">
                {sentiment.summary?.overall_sentiment || "unknown"}
              </p>
              <p className="mt-2 text-sm text-cyan-200">
                Score {sentiment.summary?.score ?? 0} · {sentiment.summary?.urgent_threads ?? 0} urgent threads
              </p>
            </div>
            <div className="mt-4 space-y-3">
              {Object.entries(sentiment.distribution || {}).map(([key, value]) => (
                <div key={key} className="flex items-center justify-between rounded-xl border border-white/8 bg-white/[0.03] px-4 py-3">
                  <span className="text-sm capitalize text-white">{key}</span>
                  <span className="text-sm text-slate-300">{value}%</span>
                </div>
              ))}
            </div>
          </article>

          <article className={`${glassCard} p-6`}>
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-white">Advanced KPI Summary</h2>
              <span className="text-sm text-slate-400">{pct(dashboard.overview?.overall_score)}</span>
            </div>
            <div className="mt-5 grid gap-3 md:grid-cols-2">
              {topKpiRows.map((kpi) => (
                <div key={kpi.name} className="rounded-2xl border border-white/8 bg-black/20 p-4">
                  <p className="text-sm font-medium text-white">{kpi.name}</p>
                  <p className="mt-2 text-2xl font-semibold text-cyan-200">
                    {kpi.current}
                    {kpi.unit}
                  </p>
                  <p className="mt-1 text-xs text-slate-400">
                    Target {kpi.target}
                    {kpi.unit}
                  </p>
                  <div className="mt-3 h-2 overflow-hidden rounded-full bg-white/10">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-cyan-400 to-violet-400"
                      style={{ width: `${Math.min(Number(kpi.progress || 0), 100)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </article>
        </section>

        <section className="grid gap-6 xl:grid-cols-[1fr,1fr]">
          <article className={`${glassCard} p-6`}>
            <h2 className="text-lg font-semibold text-white">Executive Report</h2>
            <div className="mt-5 rounded-2xl border border-white/8 bg-black/20 p-4">
              <p className="text-sm text-slate-400">
                {executiveReport.type || advancedReports.executive_report?.type || "weekly"} report
              </p>
              <p className="mt-2 text-2xl font-semibold text-white">
                {(executiveReport.financial_highlights || advancedReports.executive_report?.financial_highlights)?.revenue || "n/a"}
              </p>
              <p className="mt-2 text-sm text-cyan-200">
                {(executiveReport.financial_highlights || advancedReports.executive_report?.financial_highlights)?.revenue_growth || "n/a"} revenue growth
              </p>
            </div>
            <div className="mt-4 space-y-3">
              {((executiveReport.summary_points ||
                advancedReports.executive_report?.summary_points) || []).map((item) => (
                <div key={item} className="rounded-xl border border-white/8 bg-white/[0.03] px-4 py-3 text-sm text-slate-300">
                  {item}
                </div>
              ))}
            </div>
          </article>

          <article className={`${glassCard} p-6`}>
            <h2 className="text-lg font-semibold text-white">Geo and Financial Analytics</h2>
            <div className="mt-5 space-y-3">
              {(geo.regions || []).map((region) => (
                <div key={region.region} className="rounded-2xl border border-white/8 bg-black/20 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-medium text-white">{region.region}</p>
                    <span className={`rounded-full px-3 py-1 text-xs ${toneMap[region.status] || toneMap.stable}`}>
                      {region.status}
                    </span>
                  </div>
                  <div className="mt-3 grid grid-cols-2 gap-2 text-sm text-slate-300">
                    <span>Demand index {region.demand_index}</span>
                    <span>Margin index {region.margin_index}</span>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-5 rounded-2xl border border-white/8 bg-white/[0.03] p-4">
              <p className="text-sm text-slate-400">Revenue outlook</p>
              <p className="mt-2 text-2xl font-semibold text-white">
                {compactCurrency(finance.revenue?.current)}
              </p>
              <p className="mt-2 text-sm text-cyan-200">
                Next period {compactCurrency(finance.revenue?.forecast_next_period)} ·{" "}
                {finance.revenue?.growth_percent || 0}% growth
              </p>
            </div>
          </article>
        </section>

        {customReport ? (
          <section className={`${glassCard} p-6`}>
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-white">Custom Report Snapshot</h2>
              <span className="text-xs text-slate-400">{formatDate(customReport.generated_at)}</span>
            </div>
            <p className="mt-3 text-sm text-slate-300">{customReport.summary}</p>
            <p className="mt-2 text-xs uppercase tracking-[0.24em] text-slate-500">
              Sections: {(customReport.sections || []).join(", ")}
            </p>
          </section>
        ) : null}

        <section className={`${glassCard} p-6`}>
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">Action Log</h2>
            <span className="text-sm text-slate-400">{actionLog.length} recent actions</span>
          </div>
          <div className="mt-5 space-y-3">
            {actionLog.length ? (
              actionLog.map((item) => (
                <div key={item.id} className="rounded-2xl border border-white/8 bg-black/20 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-medium text-white">{item.label}</p>
                    <span className={`rounded-full px-3 py-1 text-xs ${toneMap[item.state] || toneMap.stable}`}>
                      {item.state}
                    </span>
                  </div>
                  <p className="mt-2 text-xs text-slate-400">{formatDate(item.timestamp)}</p>
                </div>
              ))
            ) : (
              <div className="rounded-2xl border border-dashed border-white/10 bg-white/[0.03] px-4 py-8 text-center text-sm text-slate-400">
                No actions logged yet.
              </div>
            )}
          </div>
        </section>
      </div>
    </div>
  );
}
