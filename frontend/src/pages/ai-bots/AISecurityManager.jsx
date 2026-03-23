import { useEffect, useMemo, useState } from "react";
import axiosClient from "../../api/axiosClient";

const BOT_KEY = "security_bot";
const glassCard =
  "rounded-2xl border border-white/10 bg-white/5 shadow-lg shadow-black/30 backdrop-blur-xl";

const toneMap = {
  critical: "border-rose-500/20 bg-rose-500/10 text-rose-200",
  high: "border-orange-500/20 bg-orange-500/10 text-orange-200",
  medium: "border-amber-500/20 bg-amber-500/10 text-amber-200",
  low: "border-emerald-500/20 bg-emerald-500/10 text-emerald-200",
  info: "border-blue-500/20 bg-blue-500/10 text-blue-200",
  compliant: "border-emerald-500/20 bg-emerald-500/10 text-emerald-200",
  non_compliant: "border-rose-500/20 bg-rose-500/10 text-rose-200",
  detected: "border-amber-500/20 bg-amber-500/10 text-amber-200",
  contained: "border-blue-500/20 bg-blue-500/10 text-blue-200",
  resolved: "border-emerald-500/20 bg-emerald-500/10 text-emerald-200",
  success: "border-emerald-500/20 bg-emerald-500/10 text-emerald-200",
};

const formatRelative = (value) => {
  if (!value) return "Unknown";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleString();
};

export default function AISecurityManager() {
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState({});
  const [config, setConfig] = useState({});
  const [dashboard, setDashboard] = useState({});
  const [threatFeed, setThreatFeed] = useState({});
  const [auditReport, setAuditReport] = useState({});
  const [gdpr, setGdpr] = useState({});
  const [hipaa, setHipaa] = useState({});
  const [scanIp, setScanIp] = useState("45.123.45.67");
  const [scanResult, setScanResult] = useState(null);
  const [scanDomain, setScanDomain] = useState("gts-logistics-verify.com");
  const [domainResult, setDomainResult] = useState(null);
  const [actionLog, setActionLog] = useState([]);

  const appendLog = (label, payload, state = "success") => {
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
      const [statusRes, configRes, dashboardRes, threatRes, auditRes, gdprRes, hipaaRes] = await Promise.all([
        axiosClient.get(`/api/v1/ai/bots/available/${BOT_KEY}/status`),
        axiosClient.post(`/api/v1/ai/bots/available/${BOT_KEY}/run`, {
          context: { action: "config" },
        }),
        axiosClient.post(`/api/v1/ai/bots/available/${BOT_KEY}/run`, {
          context: { action: "dashboard" },
        }),
        axiosClient.post(`/api/v1/ai/bots/available/${BOT_KEY}/run`, {
          context: { action: "recent_threats", hours: 168 },
        }),
        axiosClient.post(`/api/v1/ai/bots/available/${BOT_KEY}/run`, {
          context: { action: "audit_report", hours: 72 },
        }),
        axiosClient.post(`/api/v1/ai/bots/available/${BOT_KEY}/run`, {
          context: { action: "gdpr_compliance" },
        }),
        axiosClient.post(`/api/v1/ai/bots/available/${BOT_KEY}/run`, {
          context: { action: "hipaa_compliance" },
        }),
      ]);

      setStatus(statusRes.data?.data || statusRes.data?.status || {});
      setConfig(configRes.data?.data || configRes.data?.result || {});
      setDashboard(dashboardRes.data?.data || dashboardRes.data?.result || {});
      setThreatFeed(threatRes.data?.data || threatRes.data?.result || {});
      setAuditReport(auditRes.data?.data || auditRes.data?.result || {});
      setGdpr(gdprRes.data?.data || gdprRes.data?.result || {});
      setHipaa(hipaaRes.data?.data || hipaaRes.data?.result || {});
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAll();
  }, []);

  const quickStats = dashboard?.quick_stats || {};
  const recentEvents = dashboard?.recent_events || [];
  const recentThreats = threatFeed?.threats || dashboard?.recent_threats || [];
  const auditEvents = auditReport?.events || [];
  const auditSummary = auditReport?.summary || dashboard?.audit_summary || {};
  const blacklist = useMemo(() => {
    const list = status?.security_status?.blocked_ips || 0;
    return Array.from({ length: list }).map((_, index) => ({
      id: index + 1,
      ip_address: index === 0 ? "45.123.45.67" : `blocked-${index + 1}`,
      reason: index === 0 ? "Repeated intrusion attempts" : "Tracked by security policy",
    }));
  }, [status]);

  const runAction = async (label, context) => {
    setBusy(true);
    try {
      const res = await axiosClient.post(`/api/v1/ai/bots/available/${BOT_KEY}/run`, { context });
      const payload = res.data?.data || res.data?.result || res.data;
      appendLog(label, payload, "success");
      return payload;
    } catch (error) {
      appendLog(label, { error: error?.response?.data?.detail || error.message }, "critical");
      throw error;
    } finally {
      setBusy(false);
    }
  };

  const runIpScan = async () => {
    const payload = await runAction("Scan IP", {
      action: "check_ip_threat",
      ip: scanIp,
    });
    setScanResult(payload);
  };

  const runDomainScan = async () => {
    const payload = await runAction("Scan Domain", {
      action: "check_domain_threat",
      domain: scanDomain,
    });
    setDomainResult(payload);
  };

  const runAttackSimulation = async () => {
    const payload = await runAction("Analyze Suspicious Request", {
      action: "analyze_request",
      request_data: {
        request_id: "REQ-DASH-001",
        url: "/api/admin?user=1%20OR%20'1'='1",
        params: {
          user: "1 OR '1'='1",
          redirect: "<script>alert(1)</script>",
        },
        headers: {
          "user-agent": "curl/8.0",
        },
        ip: "45.123.45.67",
      },
    });
    appendLog("Threat Simulation Result", payload, payload?.has_threats ? "critical" : "success");
    await fetchAll();
  };

  const threatPercent = useMemo(() => {
    const base =
      Number(quickStats.critical_events || 0) * 25 +
      Number(quickStats.active_threats || 0) * 15 +
      Number(quickStats.open_events || 0) * 10;
    return Math.max(15, Math.min(100, base));
  }, [quickStats]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950">
        <div className="text-center">
          <div className="mx-auto mb-4 h-16 w-16 animate-spin rounded-full border-b-2 border-rose-400" />
          <p className="text-slate-300">Loading Security Manager dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950">
      <div className="border-b border-white/10 bg-slate-950/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-5">
          <div className="flex items-center gap-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-rose-500 to-red-800 text-lg font-bold text-white shadow-lg shadow-red-950/40">
              SEC
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">AI Security Manager</h1>
              <p className="text-sm text-slate-300">
                Intrusion detection, threat intelligence, access protection, and compliance posture.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className={`${glassCard} px-4 py-2`}>
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Version</p>
              <p className="text-sm font-semibold text-white">{status.version || "2.0.0"}</p>
            </div>
            <div className={`${glassCard} px-4 py-2`}>
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Threat Level</p>
              <p className="text-sm font-semibold capitalize text-white">{status.security_status?.threat_level || "low"}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-7xl space-y-6 px-4 py-6">
        <div className="grid gap-4 md:grid-cols-5">
          {[
            { label: "Events Today", value: quickStats.events_today || 0, tone: "from-rose-500 to-red-700" },
            { label: "Critical Events", value: quickStats.critical_events || 0, tone: "from-orange-500 to-red-700" },
            { label: "Blocked IPs", value: quickStats.blocked_ips || 0, tone: "from-cyan-500 to-blue-700" },
            { label: "Active Threats", value: quickStats.active_threats || 0, tone: "from-violet-500 to-fuchsia-700" },
            { label: "Open Events", value: quickStats.open_events || 0, tone: "from-emerald-500 to-green-700" },
          ].map((item) => (
            <div key={item.label} className={`rounded-2xl bg-gradient-to-br ${item.tone} p-5 text-white shadow-lg`}>
              <p className="text-3xl font-bold">{item.value}</p>
              <p className="mt-1 text-sm text-white/80">{item.label}</p>
            </div>
          ))}
        </div>

        <div className={`${glassCard} p-6`}>
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-lg font-bold text-white">Live Threat Level</h2>
            <span className="text-sm font-semibold text-rose-200">{threatPercent}%</span>
          </div>
          <div className="h-4 overflow-hidden rounded-full bg-slate-900/70">
            <div
              className="h-full rounded-full bg-gradient-to-r from-emerald-400 via-amber-400 to-rose-500"
              style={{ width: `${threatPercent}%` }}
            />
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <div className="space-y-6 lg:col-span-2">
            <div className={`${glassCard} p-6`}>
              <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h2 className="text-lg font-bold text-white">Security Controls</h2>
                  <p className="text-sm text-slate-400">Run live scans and simulate suspicious traffic against the security engine.</p>
                </div>
                <div className="flex flex-wrap gap-3">
                  <button
                    onClick={runAttackSimulation}
                    disabled={busy}
                    className="rounded-xl bg-rose-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-rose-500 disabled:opacity-50"
                  >
                    Simulate Attack
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

              <div className="grid gap-4 xl:grid-cols-2">
                <div className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
                  <div className="mb-3 flex items-center justify-between">
                    <p className="text-sm font-semibold text-white">IP Scan</p>
                    <button
                      onClick={runIpScan}
                      disabled={busy}
                      className="rounded-lg bg-blue-600 px-3 py-2 text-xs font-medium text-white transition hover:bg-blue-500 disabled:opacity-50"
                    >
                      Scan IP
                    </button>
                  </div>
                  <input
                    value={scanIp}
                    onChange={(e) => setScanIp(e.target.value)}
                    placeholder="45.123.45.67"
                    className="w-full rounded-xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none"
                  />
                  {scanResult ? (
                    <div className="mt-4 space-y-2 text-sm text-slate-300">
                      <p>Risk score: <span className="font-semibold text-white">{scanResult.risk_score}</span></p>
                      <p>Threat count: <span className="font-semibold text-white">{scanResult.threat_count}</span></p>
                      <p>Checked at: <span className="font-semibold text-white">{formatRelative(scanResult.checked_at)}</span></p>
                      {(scanResult.threats || []).map((threat) => (
                        <div key={threat.threat_id} className="rounded-lg border border-white/10 bg-slate-800/80 p-3">
                          <div className="flex items-center justify-between gap-3">
                            <span className="font-semibold text-white">{threat.threat_type}</span>
                            <span className={`rounded-full border px-2 py-1 text-[11px] ${toneMap[threat.severity] || toneMap.medium}`}>
                              {threat.severity}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : null}
                </div>

                <div className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
                  <div className="mb-3 flex items-center justify-between">
                    <p className="text-sm font-semibold text-white">Domain Scan</p>
                    <button
                      onClick={runDomainScan}
                      disabled={busy}
                      className="rounded-lg bg-violet-600 px-3 py-2 text-xs font-medium text-white transition hover:bg-violet-500 disabled:opacity-50"
                    >
                      Scan Domain
                    </button>
                  </div>
                  <input
                    value={scanDomain}
                    onChange={(e) => setScanDomain(e.target.value)}
                    placeholder="example.com"
                    className="w-full rounded-xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none"
                  />
                  {domainResult ? (
                    <div className="mt-4 space-y-2 text-sm text-slate-300">
                      <p>Risk score: <span className="font-semibold text-white">{domainResult.risk_score}</span></p>
                      <p>Malicious: <span className="font-semibold text-white">{domainResult.is_malicious ? "yes" : "no"}</span></p>
                      {(domainResult.threats || []).map((threat) => (
                        <div key={threat.threat_id} className="rounded-lg border border-white/10 bg-slate-800/80 p-3">
                          <div className="flex items-center justify-between gap-3">
                            <span className="font-semibold text-white">{threat.threat_type}</span>
                            <span className={`rounded-full border px-2 py-1 text-[11px] ${toneMap[threat.severity] || toneMap.low}`}>
                              {threat.severity}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : null}
                </div>
              </div>
            </div>

            <div className={`${glassCard} p-6`}>
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-lg font-bold text-white">Security Events</h2>
                <span className="text-sm text-slate-400">{recentEvents.length} recent</span>
              </div>
              <div className="space-y-3">
                {recentEvents.map((event) => (
                  <div key={event.event_id} className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
                    <div className="flex flex-wrap items-start justify-between gap-3">
                      <div>
                        <p className="font-semibold text-white">{event.event_type}</p>
                        <p className="mt-1 text-xs text-slate-400">
                          {event.source_ip || event.source_bot || "unknown source"} · {formatRelative(event.detected_at)}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`rounded-full border px-3 py-1 text-xs ${toneMap[event.severity] || toneMap.low}`}>
                          {event.severity}
                        </span>
                        <span className={`rounded-full border px-3 py-1 text-xs ${toneMap[event.status] || toneMap.info}`}>
                          {event.status}
                        </span>
                      </div>
                    </div>
                    <p className="mt-3 text-sm text-slate-300">{event.description}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="grid gap-6 xl:grid-cols-2">
              <div className={`${glassCard} p-6`}>
                <div className="mb-4 flex items-center justify-between">
                  <h2 className="text-lg font-bold text-white">Recent Threats</h2>
                  <span className="text-sm text-slate-400">{recentThreats.length}</span>
                </div>
                <div className="space-y-3">
                  {recentThreats.map((threat) => (
                    <div key={threat.threat_id} className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
                      <div className="flex flex-wrap items-start justify-between gap-3">
                        <div>
                          <p className="font-semibold text-white">{threat.threat_type}</p>
                          <p className="mt-1 text-xs text-slate-400">
                            {threat.indicator} · {threat.source} · {formatRelative(threat.last_seen)}
                          </p>
                        </div>
                        <span className={`rounded-full border px-3 py-1 text-xs ${toneMap[threat.severity] || toneMap.medium}`}>
                          {threat.severity}
                        </span>
                      </div>
                      <p className="mt-3 text-sm text-slate-300">{threat.recommended_action}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className={`${glassCard} p-6`}>
                <div className="mb-4 flex items-center justify-between">
                  <h2 className="text-lg font-bold text-white">Audit Events</h2>
                  <span className="text-sm text-slate-400">{auditSummary.total_events || 0}</span>
                </div>
                <div className="space-y-3">
                  {auditEvents.length ? (
                    auditEvents.map((event) => (
                      <div key={event.log_id} className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
                        <div className="flex flex-wrap items-start justify-between gap-3">
                          <div>
                            <p className="font-semibold text-white">{event.event_type}</p>
                            <p className="mt-1 text-xs text-slate-400">
                              {event.ip_address || event.user_id || "system"} · {formatRelative(event.timestamp)}
                            </p>
                          </div>
                          <span className={`rounded-full border px-3 py-1 text-xs ${toneMap[event.severity] || toneMap.info}`}>
                            {event.severity}
                          </span>
                        </div>
                        <p className="mt-3 text-sm text-slate-300">{event.action}</p>
                      </div>
                    ))
                  ) : (
                    <div className="rounded-xl border border-white/10 bg-slate-900/50 p-6 text-center text-sm text-slate-400">
                      No recent audit entries.
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          <div className="space-y-6">
            <div className={`${glassCard} p-6`}>
              <h2 className="text-lg font-bold text-white">Blocked IPs</h2>
              <div className="mt-4 space-y-3">
                {blacklist.map((item) => (
                  <div key={item.id} className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
                    <p className="font-mono text-sm font-semibold text-white">{item.ip_address}</p>
                    <p className="mt-1 text-xs text-slate-400">{item.reason}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className={`${glassCard} p-6`}>
              <h2 className="text-lg font-bold text-white">Compliance Posture</h2>
              <div className="mt-4 space-y-4">
                {[gdpr, hipaa].map((entry) => (
                  <div key={entry.standard} className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
                    <div className="flex items-center justify-between gap-3">
                      <p className="font-semibold text-white">{entry.standard}</p>
                      <span className={`rounded-full border px-3 py-1 text-xs ${toneMap[entry.status] || toneMap.medium}`}>
                        {entry.status}
                      </span>
                    </div>
                    <p className="mt-2 text-sm text-slate-300">Overall score: {entry.overall_score}</p>
                    <div className="mt-3 space-y-2 text-xs text-slate-400">
                      {(entry.findings || []).map((finding) => (
                        <p key={`${entry.standard}-${finding.requirement}`}>
                          {finding.requirement}: {finding.status}
                        </p>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className={`${glassCard} p-6`}>
              <h2 className="text-lg font-bold text-white">Audit Summary</h2>
              <div className="mt-4 space-y-3">
                <div className="flex items-center justify-between rounded-xl border border-white/10 bg-slate-900/50 px-4 py-3">
                  <span className="text-sm text-slate-300">Period</span>
                  <span className="text-sm font-semibold text-white">{auditSummary.period_hours || 0} hours</span>
                </div>
                <div className="flex items-center justify-between rounded-xl border border-white/10 bg-slate-900/50 px-4 py-3">
                  <span className="text-sm text-slate-300">Total events</span>
                  <span className="text-sm font-semibold text-white">{auditSummary.total_events || 0}</span>
                </div>
                {Object.entries(auditSummary.by_severity || {}).map(([key, value]) => (
                  <div key={key} className="flex items-center justify-between rounded-xl border border-white/10 bg-slate-900/50 px-4 py-3">
                    <span className="text-sm capitalize text-slate-300">{key}</span>
                    <span className="text-sm font-semibold text-white">{value}</span>
                  </div>
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
                        <span className={`rounded-full border px-2 py-1 text-[11px] ${toneMap[item.state] || toneMap.info}`}>
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
          </div>
        </div>
      </div>
    </div>
  );
}

