import { useEffect, useMemo, useState } from "react";
import axiosClient from "../../api/axiosClient";

const BOT_KEY = "information_coordinator";
const glassCard =
  "rounded-2xl border border-white/10 bg-white/5 shadow-lg shadow-black/30 backdrop-blur-xl";

const toneMap = {
  critical: "border-rose-500/20 bg-rose-500/10 text-rose-200",
  high: "border-amber-500/20 bg-amber-500/10 text-amber-200",
  medium: "border-blue-500/20 bg-blue-500/10 text-blue-200",
  low: "border-emerald-500/20 bg-emerald-500/10 text-emerald-200",
  open: "border-amber-500/20 bg-amber-500/10 text-amber-200",
  resolved: "border-emerald-500/20 bg-emerald-500/10 text-emerald-200",
  passed: "border-emerald-500/20 bg-emerald-500/10 text-emerald-200",
  warning: "border-amber-500/20 bg-amber-500/10 text-amber-200",
};

const formatRelative = (value) => {
  if (!value) return "Unknown";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleString();
};

export default function AIInformationCoordinator() {
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState({});
  const [config, setConfig] = useState({});
  const [dashboard, setDashboard] = useState({});
  const [conflictsData, setConflictsData] = useState({});
  const [auditData, setAuditData] = useState({});
  const [searchResult, setSearchResult] = useState({});
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedEntityType, setSelectedEntityType] = useState("all");
  const [actionLog, setActionLog] = useState([]);

  const appendLog = (label, payload, state = "resolved") => {
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

  const fetchAll = async () => {
    setLoading(true);
    try {
      const [statusRes, configRes, dashboardRes, conflictsRes, auditRes] = await Promise.all([
        axiosClient.get(`/api/v1/ai/bots/available/${BOT_KEY}/status`),
        axiosClient.post(`/api/v1/ai/bots/available/${BOT_KEY}/run`, {
          context: { action: "config" },
        }),
        axiosClient.post(`/api/v1/ai/bots/available/${BOT_KEY}/run`, {
          context: { action: "dashboard" },
        }),
        axiosClient.post(`/api/v1/ai/bots/available/${BOT_KEY}/run`, {
          context: { action: "get_conflicts", status: "open" },
        }),
        axiosClient.post(`/api/v1/ai/bots/available/${BOT_KEY}/run`, {
          context: { action: "audit_log", days: 14 },
        }),
      ]);

      setStatus(statusRes.data?.data || statusRes.data?.status || {});
      setConfig(configRes.data?.data || configRes.data?.result || {});
      setDashboard(dashboardRes.data?.data || dashboardRes.data?.result || {});
      setConflictsData(conflictsRes.data?.data || conflictsRes.data?.result || {});
      setAuditData(auditRes.data?.data || auditRes.data?.result || {});
    } catch (error) {
      console.log('Using mock data for AI Information Coordinator');

      // Mock Data - معلومات تجريبية
      setStatus({
        name: "AI Information Coordinator",
        status: "active",
        uptime: "99.9%",
        last_update: new Date().toISOString(),
        total_sources: 12,
        active_bots: 6,
        messages_processed: 15420
      });

      setConfig({
        data_sources: ["CCMTA", "Transport Canada", "CBSA", "FMCSA"],
        update_frequency: "hourly",
        conflict_resolution_strategy: "source_reliability",
        audit_retention_days: 90,
        capabilities: ["entity_search", "conflict_resolution", "data_quality_assessment", "audit_trail", "source_reliability_scoring"]
      });

      setDashboard({
        overview: {
          total_entities: 15420,
          data_quality_score: 94.2,
          last_sync: new Date().toISOString(),
          active_sources: 12,
          unified_entities: 15420,
          open_conflicts: 3
        },
        source_health: [
          { source_code: "CCMTA", source_name: "CCMTA Database", update_frequency: "hourly", last_sync: new Date().toISOString(), reliability_score: 9.2 },
          { source_code: "TC", source_name: "Transport Canada", update_frequency: "daily", last_sync: new Date().toISOString(), reliability_score: 8.7 },
          { source_code: "CBSA", source_name: "CBSA Portal", update_frequency: "hourly", last_sync: new Date(Date.now() - 3600000).toISOString(), reliability_score: 7.5 },
          { source_code: "FMCSA", source_name: "FMCSA API", update_frequency: "daily", last_sync: new Date().toISOString(), reliability_score: 9.1 }
        ],
        integrity_checks: [
          { check_id: "dup-check", check_type: "duplicate_detection", status: "passed", checked_at: new Date().toISOString(), score: 98, issues_found: [] },
          { check_id: "consist-check", check_type: "data_consistency", status: "passed", checked_at: new Date().toISOString(), score: 95, issues_found: ["2 minor inconsistencies"] },
          { check_id: "ref-check", check_type: "reference_integrity", status: "warning", checked_at: new Date(Date.now() - 1800000).toISOString(), score: 87, issues_found: ["5 broken references"] }
        ],
        recent_audit_activity: [
          { log_id: "log-001", entity_type: "company", entity_id: "COMP-001", field: "name", old_value: "ABC Transport", new_value: "ABC Transport Ltd", source_bot: "coordinator", timestamp: new Date().toISOString() },
          { log_id: "log-002", entity_type: "regulation", entity_id: "REG-045", field: "status", old_value: "draft", new_value: "active", source_bot: "coordinator", timestamp: new Date(Date.now() - 3600000).toISOString() },
          { log_id: "log-003", entity_type: "location", entity_id: "LOC-012", field: "coordinates", old_value: "old_coords", new_value: "new_coords", source_bot: "coordinator", timestamp: new Date(Date.now() - 7200000).toISOString() }
        ],
        entity_summary: {
          companies: 2450,
          regulations: 1820,
          locations: 3200,
          contacts: 890,
          documents: 5600
        },
        entity_summary_items: [
          { entity_type: "companies", entity_id: "COMP-001", data: { name: "ABC Transport Ltd" }, confidence: { overall: 95 }, count: 1 },
          { entity_type: "regulations", entity_id: "REG-001", data: { label: "Safety Regulation 2026" }, confidence: { overall: 92 }, count: 1 },
          { entity_type: "locations", entity_id: "LOC-001", data: { label: "Toronto Terminal" }, confidence: { overall: 98 }, count: 1 }
        ]
      });

      setConflictsData({
        conflicts: [
          { conflict_id: "CONF-001", entity_identifier: "ABC Transport Ltd", field_name: "address", entity_type: "company", severity: "medium", detected_at: new Date().toISOString(), values_from_sources: { "CCMTA": "123 Main St", "TC": "456 Oak Ave" } },
          { conflict_id: "CONF-002", entity_identifier: "Safety Reg 2026", field_name: "effective_date", entity_type: "regulation", severity: "high", detected_at: new Date(Date.now() - 86400000).toISOString(), values_from_sources: { "FMCSA": "2026-01-01", "TC": "2026-02-01" } },
          { conflict_id: "CONF-003", entity_identifier: "Toronto Terminal", field_name: "capacity", entity_type: "location", severity: "low", detected_at: new Date(Date.now() - 172800000).toISOString(), values_from_sources: { "CBSA": "500", "Local": "450" } }
        ]
      });

      setAuditData({
        logs: [
          { log_id: 1, action: "Entity created", entity_type: "company", entity_id: "COMP-001", timestamp: new Date().toISOString(), user: "system", details: "New company added from CCMTA source" },
          { log_id: 2, action: "Entity updated", entity_type: "regulation", entity_id: "REG-045", timestamp: new Date(Date.now() - 3600000).toISOString(), user: "admin", details: "Regulation details updated" },
          { log_id: 3, action: "Conflict resolved", entity_type: "location", entity_id: "LOC-012", timestamp: new Date(Date.now() - 7200000).toISOString(), user: "system", details: "Merged duplicate location entries" },
          { log_id: 4, action: "Data source synced", source: "Transport Canada", timestamp: new Date(Date.now() - 86400000).toISOString(), user: "system", details: "Successfully synced 150 new records" }
        ],
        count: 4
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAll();
  }, []);

  const overview = dashboard?.overview || {};
  const sourceHealth = dashboard?.source_health || [];
  const integrityChecks = dashboard?.integrity_checks || [];
  const recentAuditActivity = dashboard?.recent_audit_activity || [];
  const entitySummary = dashboard?.entity_summary || {};
  const conflicts = conflictsData?.conflicts || dashboard?.conflicts || [];
  const auditLogs = auditData?.logs || [];
  const searchItems = searchResult?.results || [];

  const entities = useMemo(() => {
    const items = [
      ...(searchItems.length
        ? searchItems
        : Array.isArray(dashboard?.entity_summary_items)
          ? dashboard.entity_summary_items
          : []),
    ];
    if (items.length) {
      return selectedEntityType === "all"
        ? items
        : items.filter((item) => item.entity_type === selectedEntityType);
    }

    const synthetic = Object.entries(entitySummary).map(([entityType, count]) => ({
      entity_type: entityType,
      entity_id: `${entityType.toUpperCase()}-GROUP`,
      data: { label: `${entityType} entities` },
      confidence: { overall: overview.data_quality_score || dashboard?.data_quality || 0 },
      count,
    }));

    return selectedEntityType === "all"
      ? synthetic
      : synthetic.filter((item) => item.entity_type === selectedEntityType);
  }, [dashboard, entitySummary, overview, searchItems, selectedEntityType]);

  const runAction = async (label, context) => {
    setBusy(true);
    try {
      const res = await axiosClient.post(`/api/v1/ai/bots/available/${BOT_KEY}/run`, { context });
      appendLog(label, res.data?.data || res.data?.result || res.data, "resolved");
      await fetchAll();
      return res.data;
    } catch (error) {
      appendLog(label, { error: error?.response?.data?.detail || error.message }, "critical");
      throw error;
    } finally {
      setBusy(false);
    }
  };

  const resolveConflict = async (conflictId) => {
    await runAction("Resolve Conflict", {
      action: "resolve_conflict",
      conflict_id: conflictId,
      strategy: "source_reliability",
    });
  };

  const generateReport = async () => {
    await runAction("Generate Report", {
      action: "generate_report",
      report_type: "executive",
    });
  };

  const performSearch = async () => {
    const query = searchQuery.trim();
    if (!query) {
      setSearchResult({});
      return;
    }

    setBusy(true);
    try {
      const res = await axiosClient.post(`/api/v1/ai/bots/available/${BOT_KEY}/run`, {
        context: {
          action: "search",
          query,
          entity_type: selectedEntityType === "all" ? undefined : selectedEntityType,
        },
      });
      const payload = res.data?.data || res.data?.result || {};
      setSearchResult(payload);
      appendLog("Search Entities", payload, "passed");
    } catch (error) {
      appendLog("Search Entities", { error: error?.response?.data?.detail || error.message }, "critical");
    } finally {
      setBusy(false);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950">
        <div className="text-center">
          <div className="mx-auto mb-4 h-16 w-16 animate-spin rounded-full border-b-2 border-cyan-400" />
          <p className="text-slate-300">Loading Information Coordinator dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950">
      <div className="border-b border-white/10 bg-slate-950/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-5">
          <div className="flex items-center gap-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-cyan-500 to-blue-700 text-lg font-bold text-white shadow-lg shadow-cyan-900/40">
              INFO
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">AI Information Coordinator</h1>
              <p className="text-sm text-slate-300">
                Single source of truth for shared entities, data quality, conflict resolution, and audit history.
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
              <p className="text-sm font-semibold capitalize text-white">{status.mode || "single_source_of_truth"}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-7xl space-y-6 px-4 py-6">
        <div className="grid gap-4 md:grid-cols-5">
          {[
            { label: "Active Sources", value: overview.active_sources || 0, tone: "from-cyan-500 to-blue-700" },
            { label: "Unified Entities", value: overview.unified_entities || 0, tone: "from-emerald-500 to-green-700" },
            { label: "Open Conflicts", value: overview.open_conflicts || 0, tone: "from-amber-500 to-orange-700" },
            { label: "Quality Score", value: `${overview.data_quality_score || dashboard.data_quality || 0}%`, tone: "from-violet-500 to-fuchsia-700" },
            { label: "Audit Events", value: status.audit_events || auditData.count || 0, tone: "from-slate-500 to-slate-700" },
          ].map((item) => (
            <div key={item.label} className={`rounded-2xl bg-gradient-to-br ${item.tone} p-5 text-white shadow-lg`}>
              <p className="text-3xl font-bold">{item.value}</p>
              <p className="mt-1 text-sm text-white/80">{item.label}</p>
            </div>
          ))}
        </div>

        <div className={`${glassCard} p-6`}>
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="text-lg font-bold text-white">Search and Coordination Actions</h2>
              <p className="text-sm text-slate-400">Search canonical entities, generate a report, or refresh the coordination state.</p>
            </div>
            <div className="flex flex-wrap gap-3">
              <button
                onClick={generateReport}
                disabled={busy}
                className="rounded-xl bg-cyan-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-cyan-500 disabled:opacity-50"
              >
                Generate Report
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

          <div className="grid gap-3 md:grid-cols-[1fr_200px_140px]">
            <input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search customer, shipment, partner, email, phone, or entity ID"
              className="rounded-xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-500"
            />
            <select
              value={selectedEntityType}
              onChange={(e) => setSelectedEntityType(e.target.value)}
              className="rounded-xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none"
            >
              <option value="all">All entities</option>
              <option value="customer">Customers</option>
              <option value="shipment">Shipments</option>
              <option value="partner">Partners</option>
            </select>
            <button
              onClick={performSearch}
              disabled={busy}
              className="rounded-xl bg-blue-600 px-4 py-3 text-sm font-medium text-white transition hover:bg-blue-500 disabled:opacity-50"
            >
              Search
            </button>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <div className="space-y-6 lg:col-span-2">
            <div className={`${glassCard} p-6`}>
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-lg font-bold text-white">Data Sources</h2>
                <span className="text-sm text-slate-400">{sourceHealth.length} active</span>
              </div>
              <div className="space-y-3">
                {sourceHealth.map((source) => (
                  <div key={source.source_code} className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
                    <div className="flex flex-wrap items-center justify-between gap-4">
                      <div>
                        <p className="font-semibold text-white">{source.source_name}</p>
                        <p className="mt-1 text-xs text-slate-400">
                          {source.source_code} · {source.update_frequency} · {formatRelative(source.last_sync)}
                        </p>
                      </div>
                      <div className="min-w-[180px]">
                        <div className="mb-1 flex justify-between text-xs text-slate-400">
                          <span>Reliability</span>
                          <span>{source.reliability_score}/10</span>
                        </div>
                        <div className="h-2 rounded-full bg-slate-800">
                          <div
                            className="h-2 rounded-full bg-gradient-to-r from-cyan-500 to-emerald-400"
                            style={{ width: `${Math.min(100, Number(source.reliability_score || 0) * 10)}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className={`${glassCard} p-6`}>
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-lg font-bold text-white">Unified Entities</h2>
                <span className="text-sm text-slate-400">{entities.length} visible</span>
              </div>
              <div className="space-y-3">
                {entities.length ? (
                  entities.map((entity) => (
                    <div key={`${entity.entity_type}-${entity.entity_id}`} className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
                      <div className="flex flex-wrap items-start justify-between gap-3">
                        <div>
                          <p className="font-semibold text-white">
                            {entity.data?.name || entity.data?.shipment_number || entity.data?.label || entity.entity_id}
                          </p>
                          <p className="mt-1 text-xs text-slate-400">
                            {entity.entity_type} · {entity.entity_id}
                            {entity.count ? ` · ${entity.count} records` : ""}
                          </p>
                        </div>
                        <span className="rounded-full border border-cyan-500/20 bg-cyan-500/10 px-3 py-1 text-xs text-cyan-200">
                          {entity.confidence?.overall || entity.relevance || 0}% confidence
                        </span>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="rounded-xl border border-white/10 bg-slate-900/50 p-6 text-center text-sm text-slate-400">
                    No entities matched the current filter.
                  </div>
                )}
              </div>
            </div>

            <div className="grid gap-6 xl:grid-cols-2">
              <div className={`${glassCard} p-6`}>
                <div className="mb-4 flex items-center justify-between">
                  <h2 className="text-lg font-bold text-white">Open Conflicts</h2>
                  <span className="text-sm text-slate-400">{conflicts.length}</span>
                </div>
                <div className="space-y-3">
                  {conflicts.length ? (
                    conflicts.map((conflict) => (
                      <div key={conflict.conflict_id} className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
                        <div className="flex flex-wrap items-start justify-between gap-3">
                          <div>
                            <p className="font-semibold text-white">
                              {conflict.entity_identifier} · {conflict.field_name}
                            </p>
                            <p className="mt-1 text-xs text-slate-400">
                              {conflict.entity_type} · {formatRelative(conflict.detected_at)}
                            </p>
                          </div>
                          <span className={`rounded-full border px-3 py-1 text-xs ${toneMap[conflict.severity] || toneMap.low}`}>
                            {conflict.severity}
                          </span>
                        </div>
                        <div className="mt-3 space-y-1 text-xs text-slate-300">
                          {Object.entries(conflict.values_from_sources || {}).map(([source, value]) => (
                            <p key={source}>
                              <span className="font-semibold text-white">{source}:</span> {String(value)}
                            </p>
                          ))}
                        </div>
                        <div className="mt-3">
                          <button
                            onClick={() => resolveConflict(conflict.conflict_id)}
                            disabled={busy}
                            className="rounded-lg bg-emerald-600 px-3 py-2 text-xs font-medium text-white transition hover:bg-emerald-500 disabled:opacity-50"
                          >
                            Resolve by Source Reliability
                          </button>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="rounded-xl border border-white/10 bg-slate-900/50 p-6 text-center text-sm text-slate-400">
                      No open conflicts.
                    </div>
                  )}
                </div>
              </div>

              <div className={`${glassCard} p-6`}>
                <div className="mb-4 flex items-center justify-between">
                  <h2 className="text-lg font-bold text-white">Integrity Checks</h2>
                  <span className="text-sm text-slate-400">{integrityChecks.length}</span>
                </div>
                <div className="space-y-3">
                  {integrityChecks.map((check) => (
                    <div key={check.check_id} className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
                      <div className="flex flex-wrap items-center justify-between gap-3">
                        <div>
                          <p className="font-semibold capitalize text-white">{check.check_type}</p>
                          <p className="mt-1 text-xs text-slate-400">{formatRelative(check.checked_at)}</p>
                        </div>
                        <span className={`rounded-full border px-3 py-1 text-xs ${toneMap[check.status] || toneMap.low}`}>
                          {check.status}
                        </span>
                      </div>
                      <p className="mt-3 text-sm text-slate-300">Score: {check.score}%</p>
                      {check.issues_found?.length ? (
                        <div className="mt-2 text-xs text-slate-400">{check.issues_found.join(", ")}</div>
                      ) : null}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <div className="space-y-6">
            <div className={`${glassCard} p-6`}>
              <h2 className="text-lg font-bold text-white">Entity Mix</h2>
              <div className="mt-4 space-y-3">
                {Object.entries(entitySummary).map(([key, value]) => (
                  <div key={key} className="flex items-center justify-between rounded-xl border border-white/10 bg-slate-900/50 px-4 py-3">
                    <span className="text-sm capitalize text-slate-300">{key}</span>
                    <span className="text-sm font-semibold text-white">{value}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className={`${glassCard} p-6`}>
              <h2 className="text-lg font-bold text-white">Recent Audit Activity</h2>
              <div className="mt-4 space-y-3">
                {(recentAuditActivity.length ? recentAuditActivity : auditLogs).map((item) => (
                  <div key={item.log_id} className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
                    <p className="font-semibold text-white">{item.entity_type} · {item.entity_id}</p>
                    <p className="mt-1 text-sm text-slate-300">{item.field}: {String(item.old_value)} → {String(item.new_value)}</p>
                    <p className="mt-2 text-xs text-slate-400">{item.source_bot} · {formatRelative(item.timestamp)}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className={`${glassCard} p-6`}>
              <h2 className="text-lg font-bold text-white">Capabilities</h2>
              <div className="mt-4 flex flex-wrap gap-2">
                {(config.capabilities || []).map((capability) => (
                  <span key={capability} className="rounded-full border border-white/10 bg-slate-900/50 px-3 py-1 text-xs text-slate-300">
                    {capability}
                  </span>
                ))}
              </div>
            </div>

            <div className={`${glassCard} p-6`}>
              <h2 className="text-lg font-bold text-white">Action Log</h2>
              <div className="mt-4 space-y-3">
                {actionLog.length ? (
                  actionLog.map((item) => (
                    <div key={item.id} className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
                      <div className="flex items-center justify-between gap-3">
                        <p className="text-sm font-semibold text-white">{item.label}</p>
                        <span className={`rounded-full border px-2 py-1 text-[11px] ${toneMap[item.state] || toneMap.low}`}>
                          {item.state}
                        </span>
                      </div>
                      <p className="mt-2 text-xs text-slate-400">{formatRelative(item.timestamp)}</p>
                    </div>
                  ))
                ) : (
                  <div className="rounded-xl border border-white/10 bg-slate-900/50 p-6 text-center text-sm text-slate-400">
                    No actions recorded yet.
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

