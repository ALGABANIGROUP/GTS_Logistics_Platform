import { useEffect, useRef, useState } from "react";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import axiosClient from "../api/axiosClient";
import SystemReadinessGate from "../components/SystemReadinessGate";
import DevMaintenanceControlPanel from "../components/bots/DevMaintenanceControlPanel";
import DevMaintenanceLiveChat from "../components/bots/panels/dev-maintenance/DevMaintenanceLiveChat";

const DevMaintenanceDashboard = () => {
  const [activeTab, setActiveTab] = useState("overview");
  const [loading, setLoading] = useState(false);

  const [bots, setBots] = useState([]);
  const [systemMetrics, setSystemMetrics] = useState(null);
  const [issues, setIssues] = useState([]);
  const [devIssues, setDevIssues] = useState([]);
  const [maintenanceReports, setMaintenanceReports] = useState([]);
  const [suggestedDevelopments, setSuggestedDevelopments] = useState([]);
  const [supportTickets, setSupportTickets] = useState([]);
  const [diagnosticSummary, setDiagnosticSummary] = useState(null);
  const [diagnosticHistory, setDiagnosticHistory] = useState(null);
  const [diagnosticRunning, setDiagnosticRunning] = useState(false);
  const [repairRunning, setRepairRunning] = useState(false);
  const [lastRepairResult, setLastRepairResult] = useState(null);

  const wsRef = useRef(null);
  const wsEnabled = String(import.meta.env.VITE_ENABLE_LIVE_WS || "").toLowerCase() === "true";
  const wsUrl =
    import.meta.env.VITE_WS_LIVE_URL ||
    `${window.location.protocol === "https:" ? "wss" : "ws"}://127.0.0.1:8000/api/v1/ws/live`;

  const isCanceledError = (err) =>
    err?.name === "CanceledError" || err?.code === "ERR_CANCELED";

  const getWithFallback = async (paths) => {
    let lastError;
    for (const path of paths) {
      try {
        return await axiosClient.get(path);
      } catch (err) {
        if (isCanceledError(err)) throw err;
        if (err?.response?.status === 404) {
          lastError = err;
          continue;
        }
        throw err;
      }
    }
    throw lastError || new Error("No endpoint available");
  };

  const fetchBots = async () => {
    try {
      const resp = await getWithFallback([
        "/api/v1/system/bots/status",
        "/system/bots/status",
      ]);
      const data = resp?.data;
      setBots(Array.isArray(data) ? data : data?.bots ?? []);
    } catch (err) {
      if (!isCanceledError(err)) {
        setBots([]);
      }
    }
  };

  const fetchSystemMetrics = async () => {
    try {
      const resp = await getWithFallback([
        "/api/v1/system/metrics",
        "/system/metrics",
      ]);
      setSystemMetrics(resp?.data ?? null);
    } catch (err) {
      if (!isCanceledError(err)) {
        setSystemMetrics(null);
      }
    }
  };

  const fetchIssues = async () => {
    try {
      const resp = await getWithFallback([
        "/api/v1/system/issues",
        "/system/issues",
      ]);
      const data = resp?.data;
      setIssues(Array.isArray(data) ? data : data?.issues ?? []);
    } catch (err) {
      if (isCanceledError(err)) return;
      setIssues([]);
    }
  };

  const fetchDevMaintenanceIssues = async () => {
    try {
      const resp = await getWithFallback([
        "/api/v1/dev_maintenance/issues",
        "/dev_maintenance/issues",
      ]);
      const data = resp?.data;
      setDevIssues(Array.isArray(data) ? data : data?.issues ?? []);
    } catch (err) {
      if (isCanceledError(err)) return;
      setDevIssues([]);
    }
  };

  const fetchMaintenanceAI = async () => {
    try {
      const [reportsRes, devsRes, ticketsRes] = await Promise.all([
        axiosClient.get("/api/v1/maintenance/reports").catch(() => null),
        axiosClient.get("/api/v1/maintenance/suggested-developments").catch(() => null),
        axiosClient.get("/api/v1/maintenance/support-tickets").catch(() => null),
      ]);

      setMaintenanceReports(reportsRes?.data?.reports ?? []);
      setSuggestedDevelopments(devsRes?.data?.developments ?? []);
      setSupportTickets(ticketsRes?.data?.tickets ?? []);
    } catch (err) {
      if (isCanceledError(err)) return;
      setMaintenanceReports([]);
      setSuggestedDevelopments([]);
      setSupportTickets([]);
    }
  };

  const fetchMaintenanceDiagnostics = async () => {
    try {
      const [summaryRes, historyRes] = await Promise.all([
        axiosClient.get("/api/v1/maintenance-dev/health-summary").catch(() => null),
        axiosClient.get("/api/v1/maintenance-dev/history").catch(() => null),
      ]);
      setDiagnosticSummary(summaryRes?.data ?? null);
      setDiagnosticHistory(historyRes?.data ?? null);
      setLastRepairResult(historyRes?.data?.last_repair ?? summaryRes?.data?.last_repair ?? null);
    } catch (err) {
      if (isCanceledError(err)) return;
      setDiagnosticSummary(null);
      setDiagnosticHistory(null);
      setLastRepairResult(null);
    }
  };

  const runDiagnostic = async (type = "full") => {
    setDiagnosticRunning(true);
    try {
      const response = await axiosClient.post("/api/v1/maintenance-dev/diagnostic", { type });
      setDiagnosticSummary({
        status: response.data?.status,
        issues_found: response.data?.issues_found ?? 0,
        components_checked: response.data?.components_checked ?? 0,
        last_scan: response.data?.scanned_at,
        recommendations: response.data?.recommendations ?? [],
      });
      await fetchMaintenanceDiagnostics();
      toast.success(`Diagnostic completed: ${type}`);
    } catch (err) {
      toast.error("Diagnostic failed");
    } finally {
      setDiagnosticRunning(false);
    }
  };

  const runAutoRepair = async () => {
    setRepairRunning(true);
    try {
      const response = await axiosClient.post("/api/v1/maintenance-dev/auto-repair", {});
      setLastRepairResult(response?.data ?? null);
      await fetchMaintenanceDiagnostics();
      toast.success("Auto-repair completed");
    } catch (err) {
      toast.error("Auto-repair failed");
    } finally {
      setRepairRunning(false);
    }
  };

  const refreshAll = async () => {
    setLoading(true);
    try {
      await Promise.all([
        fetchBots(),
        fetchSystemMetrics(),
        fetchIssues(),
        fetchDevMaintenanceIssues(),
        fetchMaintenanceAI(),
        fetchMaintenanceDiagnostics(),
      ]);
    } catch (err) {
      if (isCanceledError(err)) return;
      toast.error("Failed to refresh system data");
    } finally {
      setLoading(false);
    }
  };

  const connectWs = () => {
    if (!wsEnabled || !wsUrl) return;
    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        ws.send(JSON.stringify({ type: "subscribe", channels: ["bots.*", "commands.*"] }));
        toast.success("Live updates connected");
      };

      ws.onmessage = (ev) => {
        try {
          const msg = JSON.parse(ev.data);
          if (typeof msg?.channel === "string" && (msg.channel.startsWith("bots.") || msg.channel.startsWith("commands."))) {
            fetchBots();
          }
        } catch {
          // ignore
        }
      };

      ws.onerror = () => {
        // Silent fail if WS isn't enabled on backend
      };
      ws.onclose = () => {
        wsRef.current = null;
      };
    } catch {
      // ignore
    }
  };

  useEffect(() => {
    refreshAll();
    connectWs();

    return () => {
      try {
        wsRef.current?.close();
      } catch {
        // ignore
      }
      wsRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const scanTrend = diagnosticHistory?.health_history ?? [];
  const trendMaxIssues = Math.max(...scanTrend.map((item) => item?.issues_found ?? 0), 1);

  return (
    <SystemReadinessGate>
      <div className="glass-page p-6 max-w-7xl mx-auto space-y-6">
        <ToastContainer position="top-right" autoClose={2500} />

        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-white">Dev Maintenance</h1>
            <p className="text-white/70 text-sm">System health, bots status, and dev utilities.</p>
          </div>

          <button
            type="button"
            className="glass-card px-4 py-2 text-white hover:bg-white/10"
            onClick={refreshAll}
            disabled={loading}
          >
            {loading ? "Refreshing..." : "Refresh"}
          </button>
        </div>

        <div className="glass-card p-2 inline-flex flex-wrap gap-2">
          {[
            { id: "control-panel", label: "Control Panel" },
            { id: "live-support", label: "Live Support" },
            { id: "overview", label: "Overview" },
            { id: "bots", label: "Bots" },
            { id: "issues", label: "Issues" },
            { id: "maintenance", label: "Diagnostics" },
            { id: "reports", label: "Reports" },
            { id: "tickets", label: "Support Tickets" },
            { id: "developments", label: "Suggested Developments" },
          ].map((tab) => (
            <button
              key={tab.id}
              type="button"
              className={`px-3 py-1.5 rounded text-sm ${activeTab === tab.id ? "bg-white/15 text-white" : "text-white/70 hover:text-white"
                }`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {activeTab === "control-panel" && (
          <DevMaintenanceControlPanel mode="active" />
        )}

        {activeTab === "live-support" && (
          <DevMaintenanceLiveChat />
        )}

        {activeTab === "overview" && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="glass-card p-4">
              <div className="text-white/70 text-xs">Bots registered</div>
              <div className="text-white text-2xl font-semibold">{bots.length}</div>
            </div>

            <div className="glass-card p-4">
              <div className="text-white/70 text-xs">Issues</div>
              <div className="text-white text-2xl font-semibold">{issues.length + devIssues.length}</div>
            </div>

            <div className="glass-card p-4">
              <div className="text-white/70 text-xs">Metrics</div>
              <div className="text-white text-sm">{systemMetrics ? "Loaded" : "Not available"}</div>
            </div>

            <div className="glass-card p-4">
              <div className="text-white/70 text-xs">Reports</div>
              <div className="text-white text-2xl font-semibold">{maintenanceReports.length}</div>
            </div>

            <div className="glass-card p-4">
              <div className="text-white/70 text-xs">Support Tickets</div>
              <div className="text-white text-2xl font-semibold">{supportTickets.length}</div>
            </div>

            <div className="glass-card p-4">
              <div className="text-white/70 text-xs">Suggested Developments</div>
              <div className="text-white text-2xl font-semibold">{suggestedDevelopments.length}</div>
            </div>
          </div>
        )}

        {activeTab === "bots" && (
          <div className="glass-card p-4 overflow-x-auto">
            <div className="text-white font-medium mb-3">Bots</div>
            <table className="w-full text-sm">
              <thead className="text-white/70">
                <tr className="border-b border-white/10">
                  <th className="text-left py-2 pr-3">Name</th>
                  <th className="text-left py-2 pr-3">Status</th>
                  <th className="text-left py-2 pr-3">Automation</th>
                </tr>
              </thead>
              <tbody className="text-white/90">
                {bots.map((b) => (
                  <tr key={b.bot_name ?? b.name ?? JSON.stringify(b)} className="border-b border-white/5">
                    <td className="py-2 pr-3">{b.bot_name ?? b.name ?? "-"}</td>
                    <td className="py-2 pr-3">{b.status ?? (b.enabled ? "enabled" : "disabled") ?? "-"}</td>
                    <td className="py-2 pr-3">{b.automation_level ?? "-"}</td>
                  </tr>
                ))}

                {!bots.length && (
                  <tr>
                    <td className="py-3 text-white/60" colSpan={3}>
                      No bots data.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === "issues" && (
          <div className="glass-card p-4">
            <div className="text-white font-medium mb-3">Issues</div>
            {!issues.length && !devIssues.length ? (
              <div className="text-white/60 text-sm">No issues reported.</div>
            ) : (
              <ul className="space-y-2">
                {issues.map((it) => (
                  <li key={it.id ?? it.key ?? JSON.stringify(it)} className="border border-white/10 rounded p-3">
                    <div className="text-white">{it.title ?? it.name ?? "Issue"}</div>
                    {it.detail && <div className="text-white/70 text-sm mt-1">{it.detail}</div>}
                  </li>
                ))}
                {devIssues.map((it) => (
                  <li key={it.id ?? it.key ?? JSON.stringify(it)} className="border border-white/10 rounded p-3">
                    <div className="text-white">{it.title ?? it.name ?? "Issue"}</div>
                    {it.description && <div className="text-white/70 text-sm mt-1">{it.description}</div>}
                    {it.severity && <div className="text-white/60 text-xs mt-1">Severity: {it.severity}</div>}
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}

        {activeTab === "maintenance" && (
          <div className="space-y-4">
            <div className="glass-card p-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <div className="text-white font-medium">Maintenance Diagnostics</div>
                  <div className="text-white/60 text-sm">Run full scans, trigger auto-repair, and review repair history.</div>
                </div>
                <div className="flex flex-wrap gap-2">
                  <button
                    type="button"
                    className="glass-card px-4 py-2 text-white hover:bg-white/10"
                    onClick={() => runDiagnostic("full")}
                    disabled={diagnosticRunning}
                  >
                    {diagnosticRunning ? "Running..." : "Run Full Diagnostic"}
                  </button>
                  <button
                    type="button"
                    className="glass-card px-4 py-2 text-white hover:bg-white/10"
                    onClick={runAutoRepair}
                    disabled={repairRunning}
                  >
                    {repairRunning ? "Repairing..." : "Run Auto-Repair"}
                  </button>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="glass-card p-4">
                <div className="text-white/70 text-xs">Status</div>
                <div className="text-white text-lg font-semibold">{diagnosticSummary?.status ?? "Unknown"}</div>
              </div>
              <div className="glass-card p-4">
                <div className="text-white/70 text-xs">Issues Found</div>
                <div className="text-white text-2xl font-semibold">{diagnosticSummary?.issues_found ?? 0}</div>
              </div>
              <div className="glass-card p-4">
                <div className="text-white/70 text-xs">Components Checked</div>
                <div className="text-white text-2xl font-semibold">{diagnosticSummary?.components_checked ?? 0}</div>
              </div>
              <div className="glass-card p-4">
                <div className="text-white/70 text-xs">Last Scan</div>
                <div className="text-white text-sm">{diagnosticSummary?.last_scan ? new Date(diagnosticSummary.last_scan).toLocaleString() : "Never"}</div>
              </div>
              <div className="glass-card p-4">
                <div className="text-white/70 text-xs">Repair Success Rate</div>
                <div className="text-white text-2xl font-semibold">{diagnosticSummary?.repair_success_rate ?? 0}%</div>
              </div>
              <div className="glass-card p-4">
                <div className="text-white/70 text-xs">Repair Attempts</div>
                <div className="text-white text-2xl font-semibold">{diagnosticSummary?.repair_attempts ?? diagnosticHistory?.repair_attempts ?? 0}</div>
              </div>
              <div className="glass-card p-4">
                <div className="text-white/70 text-xs">Actions Attempted</div>
                <div className="text-white text-2xl font-semibold">{diagnosticHistory?.repair_actions_attempted ?? lastRepairResult?.actions_attempted ?? 0}</div>
              </div>
              <div className="glass-card p-4">
                <div className="text-white/70 text-xs">Actions Succeeded</div>
                <div className="text-white text-2xl font-semibold">{diagnosticHistory?.repair_actions_succeeded ?? lastRepairResult?.issues_repaired ?? 0}</div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <div className="glass-card p-4">
                <div className="text-white font-medium mb-3">Recommendations</div>
                {!diagnosticSummary?.recommendations?.length ? (
                  <div className="text-white/60 text-sm">No recommendations available.</div>
                ) : (
                  <ul className="space-y-2 text-sm">
                    {diagnosticSummary.recommendations.map((item) => (
                      <li key={item} className="text-white/80 border border-white/10 rounded p-3">{item}</li>
                    ))}
                  </ul>
                )}
              </div>

              <div className="glass-card p-4">
                <div className="text-white font-medium mb-3">Latest Repair</div>
                {!lastRepairResult ? (
                  <div className="text-white/60 text-sm">No repair has been executed yet.</div>
                ) : (
                  <div className="space-y-3 text-sm">
                    <div className="grid grid-cols-2 gap-3">
                      <div className="border border-white/10 rounded p-3">
                        <div className="text-white/60 text-xs">Status</div>
                        <div className="text-white font-medium">{lastRepairResult.status ?? "Unknown"}</div>
                      </div>
                      <div className="border border-white/10 rounded p-3">
                        <div className="text-white/60 text-xs">Duration</div>
                        <div className="text-white font-medium">{lastRepairResult.repair_time_seconds ?? 0}s</div>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <div className="border border-white/10 rounded p-3">
                        <div className="text-white/60 text-xs">Issues Found</div>
                        <div className="text-white font-medium">{lastRepairResult.issues_found ?? 0}</div>
                      </div>
                      <div className="border border-white/10 rounded p-3">
                        <div className="text-white/60 text-xs">Issues Repaired</div>
                        <div className="text-white font-medium">{lastRepairResult.issues_repaired ?? 0}</div>
                      </div>
                    </div>
                    <div className="border border-white/10 rounded p-3">
                      <div className="text-white/60 text-xs mb-2">Actions</div>
                      {!Object.keys(lastRepairResult.actions_taken ?? {}).length ? (
                        <div className="text-white/60">No repair actions recorded.</div>
                      ) : (
                        <ul className="space-y-2">
                          {Object.entries(lastRepairResult.actions_taken ?? {}).map(([key, value]) => (
                            <li key={key} className="flex items-start justify-between gap-3 border border-white/10 rounded p-2">
                              <span className="text-white/80">{key}</span>
                              <span className="text-white/60 text-right">{value}</span>
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <div className="glass-card p-4">
                <div className="text-white font-medium mb-3">Repair History</div>
                {!diagnosticHistory?.fixed_issues?.length ? (
                  <div className="text-white/60 text-sm">No repair history available.</div>
                ) : (
                  <ul className="space-y-2 text-sm">
                    {diagnosticHistory.fixed_issues.map((item) => (
                      <li key={`${item.timestamp}-${item.issue_id}`} className="border border-white/10 rounded p-3">
                        <div className="text-white">{item.issue_id}</div>
                        <div className="text-white/70 mt-1">{item.action}</div>
                        <div className="text-white/50 text-xs mt-1">{item.timestamp}</div>
                      </li>
                    ))}
                  </ul>
                )}
              </div>

              <div className="glass-card p-4">
                <div className="text-white font-medium mb-3">Issue Trend</div>
                {!scanTrend.length ? (
                  <div className="text-white/60 text-sm">No trend data available.</div>
                ) : (
                  <div className="space-y-3">
                    <div className="flex items-end gap-2 h-36">
                      {scanTrend.map((item) => {
                        const issuesCount = item?.issues_found ?? 0;
                        const height = `${Math.max(10, Math.round((issuesCount / trendMaxIssues) * 100))}%`;
                        return (
                          <div key={`${item.timestamp}-${item.status}`} className="flex-1 flex flex-col items-center gap-2">
                            <div className="w-full rounded-t bg-sky-400/70 border border-sky-300/30" style={{ height }} />
                            <div className="text-[10px] text-white/50">{issuesCount}</div>
                          </div>
                        );
                      })}
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <div className="border border-white/10 rounded p-3">
                        <div className="text-white/60 text-xs">Latest Scan Status</div>
                        <div className="text-white font-medium">{scanTrend.at(-1)?.status ?? "Unknown"}</div>
                      </div>
                      <div className="border border-white/10 rounded p-3">
                        <div className="text-white/60 text-xs">Average Issues</div>
                        <div className="text-white font-medium">
                          {(
                            scanTrend.reduce((sum, item) => sum + (item?.issues_found ?? 0), 0) /
                            Math.max(scanTrend.length, 1)
                          ).toFixed(1)}
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            <div className="glass-card p-4">
              <div className="text-white font-medium mb-3">Scan History</div>
              {!diagnosticHistory?.health_history?.length ? (
                <div className="text-white/60 text-sm">No scan history available.</div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="text-white/70">
                      <tr className="border-b border-white/10">
                        <th className="text-left py-2 pr-3">Timestamp</th>
                        <th className="text-left py-2 pr-3">Status</th>
                        <th className="text-left py-2 pr-3">Issues</th>
                        <th className="text-left py-2 pr-3">Components</th>
                      </tr>
                    </thead>
                    <tbody className="text-white/90">
                      {diagnosticHistory.health_history.map((item) => (
                        <tr key={`${item.timestamp}-${item.status}`} className="border-b border-white/5">
                          <td className="py-2 pr-3">{item.timestamp}</td>
                          <td className="py-2 pr-3">{item.status}</td>
                          <td className="py-2 pr-3">{item.issues_found}</td>
                          <td className="py-2 pr-3">{item.components_checked ?? "-"}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === "reports" && (
          <div className="glass-card p-4">
            <div className="text-white font-medium mb-3">Maintenance Reports</div>
            {!maintenanceReports.length ? (
              <div className="text-white/60 text-sm">No reports available.</div>
            ) : (
              <ul className="space-y-2">
                {maintenanceReports.map((report) => (
                  <li key={report.id ?? report.date ?? JSON.stringify(report)} className="border border-white/10 rounded p-3">
                    <div className="text-white font-medium">{report.date ?? "Report"}</div>
                    <div className="text-white/70 text-sm">Status: {report.status ?? "unknown"}</div>
                    {Array.isArray(report.recommendations) && report.recommendations.length > 0 && (
                      <ul className="mt-2 list-disc pl-5 text-white/60 text-sm">
                        {report.recommendations.map((rec) => (
                          <li key={rec}>{rec}</li>
                        ))}
                      </ul>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}

        {activeTab === "tickets" && (
          <div className="glass-card p-4">
            <div className="text-white font-medium mb-3">Support Tickets</div>
            {!supportTickets.length ? (
              <div className="text-white/60 text-sm">No tickets available.</div>
            ) : (
              <ul className="space-y-2">
                {supportTickets.map((ticket) => (
                  <li key={ticket.id ?? JSON.stringify(ticket)} className="border border-white/10 rounded p-3">
                    <div className="text-white font-medium">{ticket.issue ?? "Support Ticket"}</div>
                    <div className="text-white/70 text-sm">Status: {ticket.status ?? "unknown"}</div>
                    {ticket.description && <div className="text-white/60 text-sm mt-1">{ticket.description}</div>}
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}

        {activeTab === "developments" && (
          <div className="glass-card p-4">
            <div className="text-white font-medium mb-3">Suggested Developments</div>
            {!suggestedDevelopments.length ? (
              <div className="text-white/60 text-sm">No development suggestions available.</div>
            ) : (
              <ul className="space-y-2">
                {suggestedDevelopments.map((dev) => (
                  <li key={dev.id ?? JSON.stringify(dev)} className="border border-white/10 rounded p-3">
                    <div className="text-white font-medium">{dev.title ?? "Suggestion"}</div>
                    {dev.description && <div className="text-white/60 text-sm mt-1">{dev.description}</div>}
                    {dev.priority && <div className="text-white/60 text-xs mt-1">Priority: {dev.priority}</div>}
                    {dev.status && <div className="text-white/60 text-xs mt-1">Status: {dev.status}</div>}
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </div>
    </SystemReadinessGate>
  );
};

export default DevMaintenanceDashboard;
