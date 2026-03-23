import React, { useEffect, useMemo, useState, useCallback } from "react";
import {
  Search,
  Filter,
  Download,
  Eye,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Clock,
  User,
  Server,
  BarChart3,
} from "lucide-react";
import axiosClient from "@/api/axiosClient";
import "./AuditLogs.css";

const normalizeText = (value) => String(value || "").trim();

const formatLabel = (value) =>
  normalizeText(value)
    .replaceAll("_", " ")
    .replaceAll("-", " ")
    .replace(/\s+/g, " ")
    .trim();

const titleCase = (value) =>
  formatLabel(value)
    .split(" ")
    .filter(Boolean)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(" ");

const formatActionLabel = (action) => {
  const key = normalizeText(action);
  if (!key) return "Unknown Action";
  return titleCase(key);
};

const statusFromSeverity = (severity) => {
  const s = normalizeText(severity).toLowerCase();
  if (!s) return "pending";
  if (["info", "ok", "success"].includes(s)) return "success";
  if (["warning", "warn"].includes(s)) return "pending";
  if (["error", "critical", "failed"].includes(s)) return "failed";
  return "pending";
};

const severityFromStatus = (status) => {
  if (status === "success") return "info";
  if (status === "pending") return "warning";
  if (status === "failed") return "error";
  return "";
};

const buildDescription = (actionName, moduleLabel, targetId) => {
  if (moduleLabel && targetId !== null && targetId !== undefined) {
    return `${actionName} on ${moduleLabel} #${targetId}`;
  }
  if (moduleLabel) return `${actionName} on ${moduleLabel}`;
  return actionName || "Activity";
};

const normalizeLog = (log, index) => {
  const actionRaw = normalizeText(log.action || log.action_type || log.type || log.event);
  const actionType = actionRaw ? actionRaw.toUpperCase() : "UNKNOWN";

  const moduleKey = normalizeText(log.target_type || log.module || "system").toLowerCase();
  const moduleLabel = moduleKey ? titleCase(moduleKey) : "System";

  const actorId = log.actor_user_id ?? log.user_id ?? log.actor_id ?? null;
  const actorName =
    normalizeText(log.actor_name || log.user_name || log.user) || (actorId ? `User ${actorId}` : "System");
  const actorEmail = normalizeText(log.actor_email || log.user_email);

  const timestamp = log.created_at || log.timestamp || log.createdAt || new Date().toISOString();
  const severity = normalizeText(log.severity || log.level || log.status || "info").toLowerCase();
  const status = statusFromSeverity(severity);

  const actionName = formatActionLabel(actionRaw || actionType);
  const description =
    normalizeText(log.description || log.message) ||
    buildDescription(actionName, moduleLabel, log.target_id);

  return {
    id: String(log.id ?? log.log_id ?? `log-${index}`),
    timestamp,
    userId: actorId ? String(actorId) : "system",
    userName: actorName || "System",
    userEmail: actorEmail,
    actionType,
    actionName,
    module: moduleLabel,
    moduleKey: moduleKey || "system",
    description,
    ipAddress: normalizeText(log.ip || log.ip_address || "N/A"),
    userAgent: normalizeText(log.user_agent || log.ua || "N/A"),
    status,
    severity,
    details: log.diff_json || log.details || null,
  };
};

const resolveDateRange = (dateRange, customDateRange) => {
  const now = new Date();
  if (dateRange === "today") {
    const start = new Date();
    start.setHours(0, 0, 0, 0);
    return { startAt: start.toISOString(), endAt: now.toISOString() };
  }
  if (dateRange === "yesterday") {
    const start = new Date();
    start.setDate(start.getDate() - 1);
    start.setHours(0, 0, 0, 0);
    const end = new Date(start);
    end.setHours(23, 59, 59, 999);
    return { startAt: start.toISOString(), endAt: end.toISOString() };
  }
  if (dateRange === "last7days") {
    const start = new Date();
    start.setDate(start.getDate() - 7);
    return { startAt: start.toISOString(), endAt: now.toISOString() };
  }
  if (dateRange === "last30days") {
    const start = new Date();
    start.setDate(start.getDate() - 30);
    return { startAt: start.toISOString(), endAt: now.toISOString() };
  }
  if (dateRange === "custom" && customDateRange.start && customDateRange.end) {
    const start = new Date(customDateRange.start);
    start.setHours(0, 0, 0, 0);
    const end = new Date(customDateRange.end);
    end.setHours(23, 59, 59, 999);
    return { startAt: start.toISOString(), endAt: end.toISOString() };
  }
  return { startAt: "", endAt: "" };
};

const AuditLogs = () => {
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");

  const [selectedLog, setSelectedLog] = useState(null);
  const [showDetails, setShowDetails] = useState(false);

  const [searchTerm, setSearchTerm] = useState("");
  const [filters, setFilters] = useState({
    dateRange: "today",
    actionType: "all",
    status: "all",
    module: "all",
  });

  const [customDateRange, setCustomDateRange] = useState({ start: "", end: "" });

  const [stats, setStats] = useState({
    totalEvents: 0,
    todayEvents: 0,
    userActions: 0,
    systemActions: 0,
    suspiciousActivities: 0,
    successRate: 0,
    failureRate: 0,
  });

  const fetchAuditLogs = useCallback(async () => {
    setLoading(true);
    setLoadError("");
    try {
      const params = {};
      const { startAt, endAt } = resolveDateRange(filters.dateRange, customDateRange);

      if (filters.actionType !== "all") params.action = filters.actionType;
      if (filters.module !== "all") params.target_type = filters.module;
      if (filters.status !== "all") {
        const severity = severityFromStatus(filters.status);
        if (severity) params.severity = severity;
      }
      if (startAt) params.start_at = startAt;
      if (endAt) params.end_at = endAt;

      const res = await axiosClient.get("/api/v1/admin/audit", { params });
      const payload = res?.data?.data || res?.data || {};
      const list = payload.logs || payload.data?.logs || [];
      const normalized = Array.isArray(list) ? list.map((log, index) => normalizeLog(log, index)) : [];
      setAuditLogs(normalized);
    } catch (err) {
      setLoadError(
        err?.normalized?.detail ||
          err?.response?.data?.detail ||
          err?.message ||
          "Failed to load audit logs."
      );
      setAuditLogs([]);
    } finally {
      setLoading(false);
    }
  }, [customDateRange, filters]);

  useEffect(() => {
    fetchAuditLogs();
  }, [fetchAuditLogs]);

  useEffect(() => {
    const logs = auditLogs;

    const today = new Date().toISOString().split("T")[0];
    const todayEvents = logs.filter((l) => String(l.timestamp).startsWith(today)).length;

    const isUserAction = (t) =>
      t.startsWith("USER_") || t.startsWith("ROLE_") || t.startsWith("PERMISSION_");

    const userActions = logs.filter((l) => isUserAction(l.actionType)).length;
    const systemActions = logs.filter((l) => !isUserAction(l.actionType)).length;

    const suspiciousActivities = logs.filter(
      (l) => l.status === "failed" || l.severity === "warning" || l.actionType.includes("DENY")
    ).length;

    const successEvents = logs.filter((l) => l.status === "success").length;
    const failedEvents = logs.filter((l) => l.status === "failed").length;

    const successRate = logs.length ? Math.round((successEvents / logs.length) * 100) : 0;
    const failureRate = logs.length ? Math.round((failedEvents / logs.length) * 100) : 0;

    setStats({
      totalEvents: logs.length,
      todayEvents,
      userActions,
      systemActions,
      suspiciousActivities,
      successRate,
      failureRate,
    });
  }, [auditLogs]);

  const handleFilterChange = (name, value) => setFilters((p) => ({ ...p, [name]: value }));

  const actionOptions = useMemo(() => {
    const map = new Map();
    auditLogs.forEach((log) => {
      if (log.actionType && !map.has(log.actionType)) {
        map.set(log.actionType, log.actionName || formatActionLabel(log.actionType));
      }
    });

    const entries = Array.from(map.entries()).sort((a, b) => a[0].localeCompare(b[0]));
    return [
      { value: "all", label: "All Actions" },
      ...entries.map(([value, label]) => ({ value, label: `${value} - ${label}` })),
    ];
  }, [auditLogs]);

  const moduleOptions = useMemo(() => {
    const map = new Map();
    auditLogs.forEach((log) => {
      if (log.moduleKey && !map.has(log.moduleKey)) {
        map.set(log.moduleKey, log.module || titleCase(log.moduleKey));
      }
    });

    const entries = Array.from(map.entries()).sort((a, b) => a[0].localeCompare(b[0]));
    return [
      { value: "all", label: "All Modules" },
      ...entries.map(([value, label]) => ({ value, label })),
    ];
  }, [auditLogs]);

  const filteredLogs = useMemo(() => {
    return auditLogs.filter((log) => {
      const s = searchTerm.trim().toLowerCase();

      const matchesSearch =
        !s ||
        log.userName.toLowerCase().includes(s) ||
        log.userEmail.toLowerCase().includes(s) ||
        log.description.toLowerCase().includes(s) ||
        log.ipAddress.toLowerCase().includes(s) ||
        log.id.toLowerCase().includes(s) ||
        log.module.toLowerCase().includes(s) ||
        log.actionType.toLowerCase().includes(s);

      const matchesAction = filters.actionType === "all" || log.actionType === filters.actionType;
      const matchesStatus = filters.status === "all" || log.status === filters.status;
      const matchesModule = filters.module === "all" || log.moduleKey === filters.module;

      let matchesDate = true;
      const logDate = new Date(log.timestamp);

      switch (filters.dateRange) {
        case "today": {
          const t = new Date();
          t.setHours(0, 0, 0, 0);
          matchesDate = logDate >= t;
          break;
        }
        case "yesterday": {
          const y = new Date();
          y.setDate(y.getDate() - 1);
          y.setHours(0, 0, 0, 0);
          const end = new Date(y);
          end.setHours(23, 59, 59, 999);
          matchesDate = logDate >= y && logDate <= end;
          break;
        }
        case "last7days": {
          const d = new Date();
          d.setDate(d.getDate() - 7);
          matchesDate = logDate >= d;
          break;
        }
        case "last30days": {
          const d = new Date();
          d.setDate(d.getDate() - 30);
          matchesDate = logDate >= d;
          break;
        }
        case "custom": {
          if (customDateRange.start && customDateRange.end) {
            const start = new Date(customDateRange.start);
            start.setHours(0, 0, 0, 0);
            const end = new Date(customDateRange.end);
            end.setHours(23, 59, 59, 999);
            matchesDate = logDate >= start && logDate <= end;
          }
          break;
        }
        default:
          matchesDate = true;
      }

      return matchesSearch && matchesAction && matchesStatus && matchesModule && matchesDate;
    });
  }, [auditLogs, searchTerm, filters, customDateRange]);

  const clearFilters = () => {
    setSearchTerm("");
    setFilters({ dateRange: "today", actionType: "all", status: "all", module: "all" });
    setCustomDateRange({ start: "", end: "" });
  };

  const handleViewDetails = (log) => {
    setSelectedLog(log);
    setShowDetails(true);
  };

  const handleExportJSON = () => {
    const dataStr = JSON.stringify(filteredLogs, null, 2);
    const dataUri = "data:application/json;charset=utf-8," + encodeURIComponent(dataStr);
    const a = document.createElement("a");
    a.setAttribute("href", dataUri);
    a.setAttribute("download", `audit-logs-${new Date().toISOString().split("T")[0]}.json`);
    a.click();
  };

  const handleExportCSV = () => {
    const headers = ["ID", "Timestamp", "Actor", "Action", "Module", "Description", "IP Address", "Status"];
    const csvRows = filteredLogs.map((log) => [
      log.id,
      log.timestamp,
      log.userName,
      log.actionName,
      log.module,
      log.description,
      log.ipAddress,
      log.status,
    ]);

    const csv = [
      headers.join(","),
      ...csvRows.map((r) => r.map((c) => `"${String(c).replaceAll('"', '""')}"`).join(",")),
    ].join("\n");
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `audit-logs-${new Date().toISOString().split("T")[0]}.csv`;
    a.click();
  };

  const formatDateTime = (ts) => {
    const d = new Date(ts);
    if (Number.isNaN(d.getTime())) return "Unknown time";
    return d.toLocaleString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  };

  const statusMeta = (status) => {
    switch (status) {
      case "success":
        return { label: "SUCCESS", icon: <CheckCircle2 size={16} />, tone: "success" };
      case "failed":
        return { label: "FAILED", icon: <XCircle size={16} />, tone: "failed" };
      case "pending":
        return { label: "WARNING", icon: <Clock size={16} />, tone: "pending" };
      default:
        return { label: String(status).toUpperCase(), icon: null, tone: "neutral" };
    }
  };

  const actionIcon = (t) => {
    if (t.startsWith("USER_") || t.startsWith("ROLE_") || t.startsWith("PERMISSION_")) return "USER";
    if (t.startsWith("DATA_") || t.includes("TABLE")) return "DATA";
    if (t.includes("SETTINGS") || t.includes("CONFIG")) return "CFG";
    if (t.includes("ACCESS") || t.includes("DENY") || t.includes("BRUTE")) return "SEC";
    if (t.startsWith("BACKUP_")) return "BACKUP";
    if (t.startsWith("FILE_")) return "FILE";
    if (t.includes("API")) return "API";
    return "LOG";
  };

  return (
    <div className="al-container">
      <div className="al-header">
        <div>
          <h1 className="al-title">Audit Logs</h1>
          <p className="al-subtitle">Monitor and track system activities and user actions</p>
        </div>
      </div>

      <div className="al-stats">
        <div className="al-card al-stat">
          <div className="al-stat-icon">
            <BarChart3 size={22} />
          </div>
          <div>
            <div className="al-stat-label">Total Events</div>
            <div className="al-stat-value">{stats.totalEvents}</div>
          </div>
        </div>

        <div className="al-card al-stat">
          <div className="al-stat-icon">
            <Clock size={22} />
          </div>
          <div>
            <div className="al-stat-label">Events Today</div>
            <div className="al-stat-value">{stats.todayEvents}</div>
          </div>
        </div>

        <div className="al-card al-stat">
          <div className="al-stat-icon">
            <User size={22} />
          </div>
          <div>
            <div className="al-stat-label">User Actions</div>
            <div className="al-stat-value">{stats.userActions}</div>
          </div>
        </div>

        <div className="al-card al-stat">
          <div className="al-stat-icon">
            <Server size={22} />
          </div>
          <div>
            <div className="al-stat-label">System Actions</div>
            <div className="al-stat-value">{stats.systemActions}</div>
          </div>
        </div>

        <div className="al-card al-stat">
          <div className="al-stat-icon">
            <AlertTriangle size={22} />
          </div>
          <div>
            <div className="al-stat-label">Suspicious</div>
            <div className="al-stat-value">{stats.suspiciousActivities}</div>
          </div>
        </div>

        <div className="al-card al-stat">
          <div className="al-stat-icon">
            <CheckCircle2 size={22} />
          </div>
          <div>
            <div className="al-stat-label">Success / Fail</div>
            <div className="al-stat-value">
              {stats.successRate}% <span className="al-muted">/</span> {stats.failureRate}%
            </div>
          </div>
        </div>
      </div>

      {loadError ? (
        <div className="al-card al-error">
          <strong>Failed to load audit logs.</strong>
          <div className="al-muted">{loadError}</div>
        </div>
      ) : null}

      <div className="al-card al-controls">
        <div className="al-search">
          <Search size={18} />
          <input
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by actor, action, module, description, IP, or ID..."
          />
        </div>

        <div className="al-filters">
          <div className="al-filter">
            <Filter size={16} />
            <select value={filters.dateRange} onChange={(e) => handleFilterChange("dateRange", e.target.value)}>
              <option value="today">Today</option>
              <option value="yesterday">Yesterday</option>
              <option value="last7days">Last 7 Days</option>
              <option value="last30days">Last 30 Days</option>
              <option value="custom">Custom Range</option>
            </select>
          </div>

          {filters.dateRange === "custom" && (
            <div className="al-date-range">
              <input
                type="date"
                value={customDateRange.start}
                onChange={(e) => setCustomDateRange((p) => ({ ...p, start: e.target.value }))}
              />
              <span className="al-muted">to</span>
              <input
                type="date"
                value={customDateRange.end}
                onChange={(e) => setCustomDateRange((p) => ({ ...p, end: e.target.value }))}
              />
            </div>
          )}

          <div className="al-filter">
            <select value={filters.actionType} onChange={(e) => handleFilterChange("actionType", e.target.value)}>
              {actionOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div className="al-filter">
            <select value={filters.status} onChange={(e) => handleFilterChange("status", e.target.value)}>
              <option value="all">All Status</option>
              <option value="success">Info</option>
              <option value="pending">Warning</option>
              <option value="failed">Error</option>
            </select>
          </div>

          <div className="al-filter">
            <select value={filters.module} onChange={(e) => handleFilterChange("module", e.target.value)}>
              {moduleOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div className="al-actions">
            <button className="al-btn al-btn-ghost" onClick={clearFilters}>
              Clear Filters
            </button>

            <button className="al-btn al-btn-primary" onClick={handleExportCSV}>
              <Download size={16} /> Export CSV
            </button>

            <button className="al-btn al-btn-primary" onClick={handleExportJSON}>
              <Download size={16} /> Export JSON
            </button>
          </div>
        </div>
      </div>

      <div className="al-card al-table-wrap">
        {loading ? (
          <div className="al-loading">
            <div className="al-spinner" />
            <p className="al-muted">Loading audit logs...</p>
          </div>
        ) : filteredLogs.length ? (
          <div className="al-table-scroll">
            <table className="al-table">
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Actor</th>
                  <th>Action</th>
                  <th>Module</th>
                  <th>Description</th>
                  <th>IP</th>
                  <th>Status</th>
                  <th></th>
                </tr>
              </thead>

              <tbody>
                {filteredLogs.map((log) => {
                  const st = statusMeta(log.status);
                  return (
                    <tr key={log.id} className="al-row">
                      <td className="al-col-time">
                        <div className="al-strong">{formatDateTime(log.timestamp)}</div>
                        <div className="al-code al-muted">{log.id}</div>
                      </td>

                      <td className="al-col-actor">
                        <div className="al-strong">{log.userName}</div>
                        <div className="al-muted">{log.userEmail || "N/A"}</div>
                      </td>

                      <td className="al-col-action">
                        <span className="al-action-emoji">{actionIcon(log.actionType)}</span>
                        <div>
                          <div className="al-strong">{log.actionName}</div>
                          <div className="al-code al-muted">{log.actionType}</div>
                        </div>
                      </td>

                      <td>
                        <span className="al-chip">{log.module}</span>
                      </td>

                      <td className="al-col-desc">{log.description}</td>

                      <td>
                        <span className="al-chip al-chip-mono">{log.ipAddress}</span>
                      </td>

                      <td>
                        <span className={`al-badge al-badge-${st.tone}`}>
                          {st.icon}
                          {st.label}
                        </span>
                      </td>

                      <td className="al-col-btn">
                        <button className="al-icon-btn" onClick={() => handleViewDetails(log)} title="View Details">
                          <Eye size={18} />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="al-empty">
            <div className="al-empty-icon">Logs</div>
            <h3>No audit logs found</h3>
            <p className="al-muted">Try adjusting your search or filters.</p>
            <button className="al-btn al-btn-primary" onClick={clearFilters}>
              Clear All Filters
            </button>
          </div>
        )}

        {!loading && (
          <div className="al-footer">
            <div className="al-muted">
              Showing <b className="al-strong">{filteredLogs.length}</b> of <b className="al-strong">{auditLogs.length}</b> logs
            </div>
          </div>
        )}
      </div>

      {showDetails && selectedLog && (
        <div className="al-modal-overlay" onClick={() => setShowDetails(false)}>
          <div className="al-modal al-card" onClick={(e) => e.stopPropagation()}>
            <div className="al-modal-head">
              <div>
                <h2>Audit Log Details</h2>
                <p className="al-muted">Reference: {selectedLog.id}</p>
              </div>
              <button className="al-icon-btn" onClick={() => setShowDetails(false)} aria-label="Close">
                Close
              </button>
            </div>

            <div className="al-modal-body">
              <div className="al-details-grid">
                <div className="al-details-section">
                  <h3>Basic</h3>
                  <div className="al-kv">
                    <span className="al-muted">Timestamp</span>
                    <b className="al-strong">{formatDateTime(selectedLog.timestamp)}</b>
                  </div>
                  <div className="al-kv">
                    <span className="al-muted">Module</span>
                    <b className="al-strong">{selectedLog.module}</b>
                  </div>
                  <div className="al-kv">
                    <span className="al-muted">Action</span>
                    <b className="al-strong">
                      {actionIcon(selectedLog.actionType)} {selectedLog.actionName}
                    </b>
                  </div>
                  <div className="al-kv">
                    <span className="al-muted">Action Type</span>
                    <span className="al-code">{selectedLog.actionType}</span>
                  </div>
                </div>

                <div className="al-details-section">
                  <h3>Actor</h3>
                  <div className="al-kv">
                    <span className="al-muted">Name</span>
                    <b className="al-strong">{selectedLog.userName}</b>
                  </div>
                  <div className="al-kv">
                    <span className="al-muted">Email</span>
                    <span className="al-code">{selectedLog.userEmail || "N/A"}</span>
                  </div>
                  <div className="al-kv">
                    <span className="al-muted">User ID</span>
                    <span className="al-code">{selectedLog.userId}</span>
                  </div>
                </div>

                <div className="al-details-section">
                  <h3>Technical</h3>
                  <div className="al-kv">
                    <span className="al-muted">IP</span>
                    <span className="al-code">{selectedLog.ipAddress}</span>
                  </div>
                  <div className="al-kv">
                    <span className="al-muted">User Agent</span>
                    <span className="al-code">{selectedLog.userAgent || "N/A"}</span>
                  </div>
                  <div className="al-kv">
                    <span className="al-muted">Status</span>
                    <span className={`al-badge al-badge-${statusMeta(selectedLog.status).tone}`}>
                      {statusMeta(selectedLog.status).icon}
                      {statusMeta(selectedLog.status).label}
                    </span>
                  </div>
                </div>

                <div className="al-details-section al-details-wide">
                  <h3>Description</h3>
                  <p className="al-desc">{selectedLog.description}</p>

                  {selectedLog.details && (
                    <>
                      <h3 style={{ marginTop: 14 }}>Details (JSON)</h3>
                      <pre className="al-json">{JSON.stringify(selectedLog.details, null, 2)}</pre>
                    </>
                  )}
                </div>
              </div>

              <div className="al-modal-actions">
                <button className="al-btn al-btn-ghost" onClick={() => setShowDetails(false)}>
                  Close
                </button>

                {selectedLog.status === "failed" && (
                  <button className="al-btn al-btn-warn">
                    <AlertTriangle size={16} /> Mark as Investigated
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AuditLogs;
