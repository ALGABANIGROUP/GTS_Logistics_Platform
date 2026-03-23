import React, { useEffect, useMemo, useState, useCallback } from "react";
import {
  Activity,
  Server,
  Database,
  Cpu,
  HardDrive,
  Network,
  AlertTriangle,
  RefreshCw,
  Play,
  StopCircle,
  BarChart3,
  Clock,
  Shield,
  CheckCircle,
  Zap,
  MessageSquare,
  Wrench,
  FileText,
  TrendingUp,
} from "lucide-react";
import axiosClient from "@/api/axiosClient";
import "./SystemHealth.css";

const clamp = (n, min, max) => Math.max(min, Math.min(max, n));

const formatUptime = (seconds) => {
  if (!Number.isFinite(seconds)) return "N/A";
  const total = Math.max(0, Math.floor(seconds));
  const days = Math.floor(total / 86400);
  const hours = Math.floor((total % 86400) / 3600);
  const minutes = Math.floor((total % 3600) / 60);
  return `${days}d ${hours}h ${minutes}m`;
};

const normalizeCheckStatus = (check) => {
  if (check === null || check === undefined) return "warning";
  if (typeof check === "string") {
    const val = check.toLowerCase();
    if (["ok", "healthy", "connected", "running"].includes(val)) return "running";
    if (["degraded", "warning"].includes(val)) return "warning";
    return "stopped";
  }
  if (typeof check.ok === "boolean") return check.ok ? "running" : "stopped";
  if (typeof check.status === "string") return normalizeCheckStatus(check.status);
  return "warning";
};

const extractResponseTime = (check) => {
  if (!check || typeof check !== "object") return null;
  const value =
    check.latency_ms ??
    check.response_time_ms ??
    check.responseTimeMs ??
    check.response_time ??
    null;
  return Number.isFinite(value) ? Number(value) : null;
};

const buildServicesFromChecks = (checks) => {
  const mapping = [
    { key: "database", name: "Database", port: 5432 },
    { key: "redis", name: "Redis", port: 6379 },
    { key: "storage", name: "Storage", port: 9000 },
    { key: "email", name: "Email", port: 587 },
    { key: "bots_health", name: "Bots Health", port: "N/A" },
  ];

  return mapping
    .filter((item) => checks[item.key] !== undefined)
    .map((item, index) => {
      const check = checks[item.key];
      const responseTime = extractResponseTime(check);
      return {
        id: index + 1,
        name: item.name,
        status: normalizeCheckStatus(check),
        uptime: "N/A",
        port: item.port,
        responseTime,
        responseTimeAvailable: responseTime !== null,
      };
    });
};

const buildAlertsFromChecks = (checks, connected, nowIso) => {
  const alerts = [];
  const critical = new Set(["database", "redis", "storage"]);

  if (!connected) {
    alerts.push({
      id: `connection-${nowIso}`,
      type: "critical",
      title: "Connection Lost",
      message: "System health endpoint is not reachable",
      time: nowIso,
    });
  }

  Object.entries(checks || {}).forEach(([key, value]) => {
    const status = normalizeCheckStatus(value);
    if (status === "running") return;

    const detail = value?.error || value?.detail || value?.message || "Check failed";
    alerts.push({
      id: `${key}-${nowIso}`,
      type: critical.has(key) ? "critical" : "warning",
      title: `${key.replaceAll("_", " ").toUpperCase()} Check`,
      message: detail,
      time: nowIso,
    });
  });

  return alerts.slice(0, 6);
};

const SystemHealth = () => {
  const [systemStatus, setSystemStatus] = useState("disconnected");
  const [connectionStatus, setConnectionStatus] = useState({
    connected: false,
    lastCheck: null,
    responseTime: 0,
  });

  const [resources, setResources] = useState({
    cpu: { usage: 0, cores: 0, temperature: 0, available: false },
    memory: { used: 0, total: 0, percentage: 0, available: false },
    disk: { used: 0, total: 0, percentage: 0, available: false },
    network: { in: 0, out: 0, connections: 0, available: false },
  });

  const [services, setServices] = useState([]);
  const [systemLogs, setSystemLogs] = useState([]);
  const [alerts, setAlerts] = useState([]);

  const [perfStats, setPerfStats] = useState({
    responseTime: 0,
    requestsPerMinute: 0,
    errorRate: 0,
    pageLoadTime: 0,
    apiUsage: 0,
  });

  const [perfAvailable, setPerfAvailable] = useState({
    responseTime: false,
    requestsPerMinute: false,
    errorRate: false,
    pageLoadTime: false,
    apiUsage: false,
  });

  const [systemInfo, setSystemInfo] = useState({
    uptime: "N/A",
    version: "N/A",
    lastBackup: "N/A",
    os: "N/A",
    timezone: "UTC",
  });

  // Maintenance & Development Reports
  const [maintenanceReports, setMaintenanceReports] = useState([
    {
      id: 1,
      date: new Date(Date.now() - 86400000).toLocaleDateString(),
      status: "completed",
      checks: 12,
      issues: 2,
      recommendations: ["Optimize database queries", "Update dependencies"],
    },
    {
      id: 2,
      date: new Date(Date.now() - 172800000).toLocaleDateString(),
      status: "completed",
      checks: 12,
      issues: 1,
      recommendations: ["Monitor API rate limits"],
    },
  ]);

  const [suggestedDevelopments, setSuggestedDevelopments] = useState([
    { id: 1, title: "Database Query Optimization", priority: "high", status: "pending_approval", date: "2026-02-01" },
    { id: 2, title: "API Caching Layer", priority: "medium", status: "pending_approval", date: "2026-02-02" },
    { id: 3, title: "User Dashboard Redesign", priority: "low", status: "approved", date: "2026-01-30" },
  ]);

  const [supportTickets, setSupportTickets] = useState([
    { id: 101, user: "Ahmed Salem", issue: "Cannot access reports", status: "open", created: "2 hours ago" },
    { id: 102, user: "Fatima Ahmed", issue: "Slow shipment tracking", status: "in_progress", created: "1 hour ago" },
    { id: 103, user: "Mohamed Ibrahim", issue: "Missing invoice data", status: "open", created: "30 minutes ago" },
  ]);

  const [selectedTicket, setSelectedTicket] = useState(null);

  const [historicalData, setHistoricalData] = useState({
    cpu: [],
    memory: [],
    requests: [],
    responseTimes: [],
  });

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(5000);

  const getStatusColor = (status) => {
    switch (status) {
      case "connected":
      case "running":
        return "#10b981";
      case "warning":
        return "#f59e0b";
      case "disconnected":
      case "stopped":
        return "#ef4444";
      default:
        return "#6b7280";
    }
  };

  const getAlertColor = (type) => {
    switch (type) {
      case "critical":
        return "#ef4444";
      case "warning":
        return "#f59e0b";
      case "info":
        return "#3b82f6";
      default:
        return "#6b7280";
    }
  };

  const formatTime = (timestamp) =>
    new Date(timestamp).toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });

  const formatBytes = (bytes) => {
    const sizes = ["Bytes", "KB", "MB", "GB", "TB"];
    if (!bytes) return "0 Bytes";
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return `${Math.round(bytes / Math.pow(1024, i))} ${sizes[i]}`;
  };

  const averages = useMemo(() => {
    const avg = (arr) => (arr.length ? arr.reduce((a, b) => a + b.value, 0) / arr.length : null);
    return {
      cpu: avg(historicalData.cpu),
      memory: avg(historicalData.memory),
      requests: avg(historicalData.requests),
      responseTime: avg(historicalData.responseTimes),
    };
  }, [historicalData]);

  const formatAverage = (value, digits = 1) => (value === null ? "N/A" : value.toFixed(digits));

  const fetchSystemHealth = useCallback(
    async ({ refresh = false } = {}) => {
      const start = globalThis.performance ? globalThis.performance.now() : Date.now();
      if (refresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      setError("");

      const nowIso = new Date().toISOString();

      try {
        const [statusRes, healthRes, metricsRes, dbRes] = await Promise.allSettled([
          axiosClient.get("/api/v1/system/status"),
          axiosClient.get("/api/v1/system/health"),
          axiosClient.get("/api/v1/system/metrics"),
          axiosClient.get("/api/v1/system/database/stats"),
        ]);

        const allFailed = [statusRes, healthRes, metricsRes, dbRes].every((res) => res.status !== "fulfilled");
        if (allFailed) {
          throw new Error("System endpoints are unavailable.");
        }

        const responseTime = Math.round((globalThis.performance ? globalThis.performance.now() : Date.now()) - start);
        const statusPayload = statusRes.status === "fulfilled" ? statusRes.value?.data : null;
        const healthPayload = healthRes.status === "fulfilled" ? healthRes.value?.data : null;
        const metricsPayload = metricsRes.status === "fulfilled" ? metricsRes.value?.data : null;
        const dbPayload = dbRes.status === "fulfilled" ? dbRes.value?.data : null;

        const connected = Boolean(healthPayload || statusPayload || metricsPayload || dbPayload);
        setConnectionStatus({ connected, lastCheck: nowIso, responseTime });
        setSystemStatus(connected ? "connected" : "disconnected");

        const uptimeSeconds = statusPayload?.uptime_seconds ?? metricsPayload?.uptime_seconds;
        const version = statusPayload?.app?.version || statusPayload?.version || "N/A";
        const environment = statusPayload?.app?.environment || statusPayload?.environment || "N/A";
        const host = metricsPayload?.host || {};

        setSystemInfo({
          uptime: formatUptime(uptimeSeconds),
          version,
          lastBackup: statusPayload?.last_backup || "N/A",
          os: host.platform ? `${host.platform} ${host.platform_release || ""}`.trim() : environment,
          timezone: statusPayload?.timezone || "UTC",
        });

        const checks = healthPayload?.details || healthPayload?.checks || {};
        if (!Object.keys(checks).length && healthPayload?.database) {
          checks.database = healthPayload.database;
        }
        if (dbPayload && checks.database === undefined) {
          checks.database = dbPayload;
        }

        const nextServices = buildServicesFromChecks(checks);
        setServices(nextServices);

        const memory = host.memory || null;
        const memoryAvailable = memory && Number.isFinite(memory.percent);
        const memoryTotal = memoryAvailable ? memory.total / (1024 * 1024 * 1024) : 0;
        const memoryUsed = memoryAvailable ? memory.used / (1024 * 1024 * 1024) : 0;
        const memoryPct = memoryAvailable ? clamp(memory.percent, 0, 100) : 0;

        const cpu = host.cpu || null;
        const cpuAvailable = cpu && Number.isFinite(cpu.percent);
        const cpuUsage = cpuAvailable ? clamp(cpu.percent, 0, 100) : 0;
        const cpuCores = cpuAvailable ? cpu.cores || 0 : 0;

        const disk = host.disk || null;
        const diskAvailable = disk && Number.isFinite(disk.percent);
        const diskTotal = diskAvailable ? disk.total / (1024 * 1024 * 1024) : 0;
        const diskUsed = diskAvailable ? disk.used / (1024 * 1024 * 1024) : 0;
        const diskPct = diskAvailable ? clamp(disk.percent, 0, 100) : 0;

        setResources({
          cpu: { usage: cpuUsage, cores: cpuCores, temperature: 0, available: Boolean(cpuAvailable) },
          memory: { used: memoryUsed, total: memoryTotal, percentage: memoryPct, available: Boolean(memoryAvailable) },
          disk: { used: diskUsed, total: diskTotal, percentage: diskPct, available: Boolean(diskAvailable) },
          network: { in: 0, out: 0, connections: 0, available: false },
        });

        const apiRequests = metricsPayload?.api_requests_last_24h;
        const errorRate = metricsPayload?.error_rate;
        const requestsPerMinute = Number.isFinite(apiRequests) ? Math.round(apiRequests / 1440) : 0;

        setPerfStats({
          responseTime: 0,
          requestsPerMinute,
          errorRate: Number.isFinite(errorRate) ? errorRate : 0,
          pageLoadTime: 0,
          apiUsage: 0,
        });

        setPerfAvailable({
          responseTime: false,
          requestsPerMinute: Number.isFinite(apiRequests),
          errorRate: Number.isFinite(errorRate),
          pageLoadTime: false,
          apiUsage: false,
        });

        setHistoricalData((prev) => {
          const nowTs = Date.now();
          return {
            cpu: prev.cpu,
            memory: memoryAvailable
              ? [...prev.memory.slice(-29), { time: nowTs, value: memoryPct }]
              : prev.memory,
            requests: Number.isFinite(apiRequests)
              ? [...prev.requests.slice(-29), { time: nowTs, value: requestsPerMinute }]
              : prev.requests,
            responseTimes: prev.responseTimes,
          };
        });

        setAlerts(buildAlertsFromChecks(checks, connected, nowIso));
        setSystemLogs([]);
      } catch (err) {
        setError(
          err?.normalized?.detail || err?.response?.data?.detail || err?.message || "Failed to load system health."
        );
        setConnectionStatus({ connected: false, lastCheck: nowIso, responseTime: 0 });
        setSystemStatus("disconnected");
        setServices([]);
        setAlerts([]);
      } finally {
        if (refresh) {
          setRefreshing(false);
        } else {
          setLoading(false);
        }
      }
    },
    []
  );

  useEffect(() => {
    fetchSystemHealth();
  }, [fetchSystemHealth]);

  useEffect(() => {
    if (!autoRefresh) return undefined;
    const id = setInterval(() => fetchSystemHealth({ refresh: true }), refreshInterval);
    return () => clearInterval(id);
  }, [autoRefresh, refreshInterval, fetchSystemHealth]);

  // Fetch maintenance reports
  useEffect(() => {
    const fetchMaintenanceData = async () => {
      try {
        const [reportsRes, devsRes, ticketsRes] = await Promise.allSettled([
          axiosClient.get("/api/v1/maintenance/reports"),
          axiosClient.get("/api/v1/maintenance/suggested-developments"),
          axiosClient.get("/api/v1/maintenance/support-tickets"),
        ]);

        if (reportsRes.status === "fulfilled" && reportsRes.value?.data?.reports) {
          setMaintenanceReports(reportsRes.value.data.reports);
        }

        if (devsRes.status === "fulfilled" && devsRes.value?.data?.developments) {
          setSuggestedDevelopments(devsRes.value.data.developments);
        }

        if (ticketsRes.status === "fulfilled" && ticketsRes.value?.data?.tickets) {
          setSupportTickets(ticketsRes.value.data.tickets);
        }
      } catch (err) {
        console.error("Error fetching maintenance data:", err);
      }
    };

    fetchMaintenanceData();
    const id = setInterval(fetchMaintenanceData, 30000); // Refresh every 30 seconds
    return () => clearInterval(id);
  }, []);

  const handleRefresh = () => fetchSystemHealth({ refresh: true });

  const clearAlerts = () => setAlerts([]);

  const handleApproveDevlopment = async (devId) => {
    try {
      const response = await axiosClient.post(`/api/v1/maintenance/approve/${devId}`);
      if (response.data?.ok) {
        setSuggestedDevelopments((prev) =>
          prev.map((dev) =>
            dev.id === devId ? { ...dev, status: "approved" } : dev
          )
        );
      }
    } catch (err) {
      console.error("Error approving development:", err);
    }
  };

  const handleRejectDevlopment = async (devId) => {
    try {
      setSuggestedDevelopments((prev) =>
        prev.map((dev) =>
          dev.id === devId ? { ...dev, status: "rejected" } : dev
        )
      );
    } catch (err) {
      console.error("Error rejecting development:", err);
    }
  };

  const handleAIResponse = async (ticketId) => {
    try {
      const response = await axiosClient.post(`/api/v1/maintenance/support-tickets/${ticketId}/respond-ai`);
      if (response.data?.ai_response) {
        setSupportTickets((prev) =>
          prev.map((ticket) =>
            ticket.id === ticketId ? { ...ticket, ai_response: response.data.ai_response } : ticket
          )
        );
        setSelectedTicket((prev) =>
          prev ? { ...prev, ai_response: response.data.ai_response } : null
        );
      }
    } catch (err) {
      console.error("Error generating AI response:", err);
    }
  };

  const handleResolveTicket = async (ticketId) => {
    try {
      await axiosClient.post(`/api/v1/maintenance/support-tickets/${ticketId}/resolve`);
      setSupportTickets((prev) =>
        prev.map((t) =>
          t.id === ticketId ? { ...t, status: "resolved" } : t
        )
      );
      setSelectedTicket((prev) =>
        prev && prev.id === ticketId ? { ...prev, status: "resolved" } : prev
      );
    } catch (err) {
      console.error("Error resolving ticket:", err);
    }
  };

  const handleEscalateTicket = async (ticketId) => {
    try {
      await axiosClient.post(`/api/v1/maintenance/support-tickets/${ticketId}/escalate`);
      setSupportTickets((prev) =>
        prev.map((t) =>
          t.id === ticketId ? { ...t, status: "escalated" } : t
        )
      );
      setSelectedTicket((prev) =>
        prev && prev.id === ticketId ? { ...prev, status: "escalated" } : prev
      );
    } catch (err) {
      console.error("Error escalating ticket:", err);
    }
  };

  if (loading) {
    return (
      <div className="system-health-container">
        <div className="sh-loading">
          <div className="sh-spinner" />
          <p>Loading system health...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="system-health-container">
      <div className="sh-page-header">
        <div className="sh-header-left">
          <h1 className="sh-title">
            <Activity size={28} />
            System Health
          </h1>

          <div className="sh-status-indicator">
            <div className={`sh-status-dot ${systemStatus}`} style={{ backgroundColor: getStatusColor(systemStatus) }} />
            <span className="sh-status-text">
              Status: {systemStatus === "connected" ? "Connected" : "Disconnected"}
              {connectionStatus.lastCheck ? ` | Last check: ${formatTime(connectionStatus.lastCheck)}` : ""}
              {connectionStatus.connected && connectionStatus.responseTime
                ? ` | ${connectionStatus.responseTime}ms`
                : ""}
            </span>
          </div>
        </div>

        <div className="sh-header-actions">
          <div className="sh-auto-refresh">
            <label className="sh-toggle">
              <input type="checkbox" checked={autoRefresh} onChange={(e) => setAutoRefresh(e.target.checked)} />
              Auto Refresh
            </label>

            <select
              value={refreshInterval}
              onChange={(e) => setRefreshInterval(Number(e.target.value))}
              disabled={!autoRefresh}
            >
              <option value="2000">2 seconds</option>
              <option value="5000">5 seconds</option>
              <option value="10000">10 seconds</option>
              <option value="30000">30 seconds</option>
            </select>
          </div>

          <button className="sh-btn sh-btn-primary" onClick={handleRefresh} disabled={refreshing}>
            <RefreshCw size={18} className={refreshing ? "sh-spinning" : ""} />
            {refreshing ? "Refreshing..." : "Refresh Now"}
          </button>
        </div>
      </div>

      {error ? (
        <div className="sh-error">
          <strong>System health failed to load.</strong>
          <div>{error}</div>
        </div>
      ) : null}

      <div className="sh-info-cards">
        <div className="sh-info-card">
          <div className="sh-info-icon">
            <Clock size={24} />
          </div>
          <div className="sh-info-content">
            <h3>Uptime</h3>
            <p>{systemInfo.uptime}</p>
          </div>
        </div>

        <div className="sh-info-card">
          <div className="sh-info-icon">
            <Server size={24} />
          </div>
          <div className="sh-info-content">
            <h3>System Version</h3>
            <p>{systemInfo.version}</p>
          </div>
        </div>

        <div className="sh-info-card">
          <div className="sh-info-icon">
            <Shield size={24} />
          </div>
          <div className="sh-info-content">
            <h3>Last Backup</h3>
            <p>{systemInfo.lastBackup}</p>
          </div>
        </div>

        <div className="sh-info-card">
          <div className="sh-info-icon">
            <Database size={24} />
          </div>
          <div className="sh-info-content">
            <h3>Environment</h3>
            <p>{systemInfo.os}</p>
          </div>
        </div>
      </div>

      <div className="sh-section">
        <div className="sh-section-title">
          <h2>Resource Utilization</h2>
        </div>

        <div className="sh-grid resources">
          <div className="sh-card">
            <div className="sh-card-header">
              <Cpu size={20} />
              <h3>CPU Usage</h3>
              <span
                className={`sh-badge ${!resources.cpu.available
                  ? "na"
                  : resources.cpu.usage > 85
                    ? "critical"
                    : resources.cpu.usage > 70
                      ? "warning"
                      : "normal"
                  }`}
              >
                {resources.cpu.available ? `${resources.cpu.usage.toFixed(1)}%` : "N/A"}
              </span>
            </div>

            <div className="sh-progress">
              <div className="sh-progress-bar">
                <div className="sh-progress-fill" style={{ width: `${resources.cpu.available ? resources.cpu.usage : 0}%` }} />
              </div>
              <div className="sh-meta">
                <span>{resources.cpu.available ? `${resources.cpu.cores} cores` : "N/A"}</span>
                <span>{resources.cpu.available ? `${resources.cpu.temperature.toFixed(1)}C` : "N/A"}</span>
                <span>Avg: {resources.cpu.available ? `${formatAverage(averages.cpu)}%` : "N/A"}</span>
              </div>
            </div>
          </div>

          <div className="sh-card">
            <div className="sh-card-header">
              <HardDrive size={20} />
              <h3>Memory Usage</h3>
              <span
                className={`sh-badge ${!resources.memory.available
                  ? "na"
                  : resources.memory.percentage > 90
                    ? "critical"
                    : resources.memory.percentage > 80
                      ? "warning"
                      : "normal"
                  }`}
              >
                {resources.memory.available ? `${resources.memory.percentage.toFixed(1)}%` : "N/A"}
              </span>
            </div>

            <div className="sh-progress">
              <div className="sh-progress-bar">
                <div
                  className="sh-progress-fill"
                  style={{ width: `${resources.memory.available ? resources.memory.percentage : 0}%` }}
                />
              </div>
              <div className="sh-meta">
                <span>
                  {resources.memory.available ? `${resources.memory.used.toFixed(1)} GB used` : "N/A"}
                </span>
                <span>
                  {resources.memory.available ? `${resources.memory.total.toFixed(1)} GB total` : "N/A"}
                </span>
                <span>Avg: {resources.memory.available ? `${formatAverage(averages.memory)}%` : "N/A"}</span>
              </div>
            </div>
          </div>

          <div className="sh-card">
            <div className="sh-card-header">
              <Database size={20} />
              <h3>Disk Usage</h3>
              <span
                className={`sh-badge ${!resources.disk.available
                  ? "na"
                  : resources.disk.percentage > 90
                    ? "critical"
                    : resources.disk.percentage > 80
                      ? "warning"
                      : "normal"
                  }`}
              >
                {resources.disk.available ? `${resources.disk.percentage.toFixed(1)}%` : "N/A"}
              </span>
            </div>

            <div className="sh-progress">
              <div className="sh-progress-bar">
                <div
                  className="sh-progress-fill"
                  style={{ width: `${resources.disk.available ? resources.disk.percentage : 0}%` }}
                />
              </div>
              <div className="sh-meta">
                <span>{resources.disk.available ? `${resources.disk.used.toFixed(1)} GB used` : "N/A"}</span>
                <span>{resources.disk.available ? `${resources.disk.total.toFixed(1)} GB total` : "N/A"}</span>
                <span>
                  {resources.disk.available
                    ? `${formatBytes((resources.disk.total - resources.disk.used) * 1024 * 1024 * 1024)} free`
                    : "N/A"}
                </span>
              </div>
            </div>
          </div>

          <div className="sh-card">
            <div className="sh-card-header">
              <Network size={20} />
              <h3>Network Usage</h3>
              <span className={`sh-badge ${resources.network.available ? "normal" : "na"}`}>
                {resources.network.available ? `${resources.network.connections} connections` : "N/A"}
              </span>
            </div>

            <div className="sh-network">
              <div className="sh-net-row">
                <span>Inbound</span>
                <b>{resources.network.available ? `${resources.network.in.toFixed(1)} MB/s` : "N/A"}</b>
              </div>
              <div className="sh-net-row">
                <span>Outbound</span>
                <b>{resources.network.available ? `${resources.network.out.toFixed(1)} MB/s` : "N/A"}</b>
              </div>
              <div className="sh-meta">
                <span>
                  {resources.network.available
                    ? `Total: ${(resources.network.in + resources.network.out).toFixed(1)} MB/s`
                    : "N/A"}
                </span>
                <span>
                  {resources.network.available ? `${resources.network.connections} active connections` : "N/A"}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="sh-section">
        <div className="sh-section-title">
          <h2>Services Status</h2>
        </div>

        {services.length ? (
          <div className="sh-grid services">
            {services.map((service) => (
              <div key={service.id} className={`sh-service-card ${service.status}`}>
                <div className="sh-service-head">
                  <div>
                    <h3>{service.name}</h3>
                    <span className="sh-port">Port: {service.port}</span>
                  </div>
                  <div className="sh-service-state">
                    <div className="sh-mini-dot" style={{ backgroundColor: getStatusColor(service.status) }} />
                    <span>{service.status}</span>
                  </div>
                </div>

                <div className="sh-service-meta">
                  <div>
                    <span>Uptime</span>
                    <b>{service.uptime}</b>
                  </div>
                  <div>
                    <span>Response</span>
                    <b>{service.responseTimeAvailable ? `${service.responseTime}ms` : "N/A"}</b>
                  </div>
                </div>

                <div className="sh-service-actions">
                  <button
                    className={`sh-btn ${service.status === "running" ? "sh-btn-danger" : "sh-btn-success"}`}
                    disabled
                    title="Service actions are not configured"
                  >
                    {service.status === "running" ? (
                      <>
                        <StopCircle size={16} /> Stop
                      </>
                    ) : (
                      <>
                        <Play size={16} /> Start
                      </>
                    )}
                  </button>

                  <button className="sh-btn sh-btn-warn" disabled title="Service actions are not configured">
                    <RefreshCw size={16} /> Restart
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="sh-empty">No service data available.</div>
        )}
      </div>

      <div className="sh-section">
        <div className="sh-section-title">
          <h2>Performance Metrics</h2>
        </div>

        <div className="sh-grid metrics">
          <div className="sh-metric-card">
            <div className="sh-metric-head">
              <BarChart3 size={20} />
              <h3>Response Time</h3>
            </div>
            <div className="sh-metric-body">
              <div className="sh-metric-value">
                {perfAvailable.responseTime ? `${perfStats.responseTime}ms` : "N/A"}
              </div>
              <div className="sh-metric-sub">Avg: {perfAvailable.responseTime ? `${formatAverage(averages.responseTime, 0)}ms` : "N/A"}</div>
            </div>
          </div>

          <div className="sh-metric-card">
            <div className="sh-metric-head">
              <Activity size={20} />
              <h3>Requests / Minute</h3>
            </div>
            <div className="sh-metric-body">
              <div className="sh-metric-value">
                {perfAvailable.requestsPerMinute ? perfStats.requestsPerMinute : "N/A"}
              </div>
              <div className="sh-metric-sub">
                Avg: {perfAvailable.requestsPerMinute ? `${formatAverage(averages.requests, 0)} req/min` : "N/A"}
              </div>
            </div>
          </div>

          <div className="sh-metric-card">
            <div className="sh-metric-head">
              <AlertTriangle size={20} />
              <h3>Error Rate</h3>
            </div>
            <div className="sh-metric-body">
              <div className="sh-metric-value">
                {perfAvailable.errorRate ? `${perfStats.errorRate.toFixed(2)}%` : "N/A"}
              </div>
              <div className={`sh-metric-sub ${perfAvailable.errorRate && perfStats.errorRate > 5 ? "critical" : "ok"}`}>
                {perfAvailable.errorRate ? (perfStats.errorRate > 5 ? "High" : "Normal") : "N/A"}
              </div>
            </div>
          </div>

          <div className="sh-metric-card">
            <div className="sh-metric-head">
              <Clock size={20} />
              <h3>Page Load</h3>
            </div>
            <div className="sh-metric-body">
              <div className="sh-metric-value">{perfAvailable.pageLoadTime ? `${perfStats.pageLoadTime}ms` : "N/A"}</div>
              <div className="sh-metric-sub">
                {perfAvailable.pageLoadTime ? (perfStats.pageLoadTime > 1000 ? "Slow" : "Fast") : "N/A"}
              </div>
            </div>
          </div>

          <div className="sh-metric-card">
            <div className="sh-metric-head">
              <Server size={20} />
              <h3>API Usage</h3>
            </div>
            <div className="sh-metric-body">
              <div className="sh-metric-value">{perfAvailable.apiUsage ? `${perfStats.apiUsage.toFixed(0)}%` : "N/A"}</div>
              <div className="sh-metric-sub">Rate-limit utilization</div>
            </div>
          </div>
        </div>
      </div>

      <div className="sh-section">
        <div className="sh-section-title">
          <h2>
            <Wrench size={22} /> Maintenance & Development Reports
          </h2>
          <span className="sh-subtitle">MA - Maintenance & Development Team</span>
        </div>

        <div className="sh-grid maintenance-reports">
          {maintenanceReports.map((report) => (
            <div key={report.id} className="sh-report-card">
              <div className="sh-report-header">
                <div>
                  <h4>{report.date}</h4>
                  <span className={`sh-status-badge ${report.status}`}>{report.status}</span>
                </div>
                <CheckCircle size={20} color="#10b981" />
              </div>
              <div className="sh-report-stats">
                <div className="sh-stat">
                  <span className="sh-stat-label">Health Checks</span>
                  <span className="sh-stat-value">{report.checks}</span>
                </div>
                <div className="sh-stat">
                  <span className="sh-stat-label">Issues Found</span>
                  <span className="sh-stat-value" style={{ color: report.issues > 0 ? "#ef4444" : "#10b981" }}>
                    {report.issues}
                  </span>
                </div>
              </div>
              <div className="sh-report-recommendations">
                <span className="sh-label">Recommendations:</span>
                {report.recommendations.map((rec, i) => (
                  <div key={i} className="sh-rec-item">
                    <TrendingUp size={14} /> {rec}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="sh-section">
        <div className="sh-section-title">
          <h2>
            <Zap size={22} /> Suggested Developments
          </h2>
          <span className="sh-subtitle">Pending Admin Approval</span>
        </div>

        <div className="sh-developments-table">
          <table>
            <thead>
              <tr>
                <th>Title</th>
                <th>Priority</th>
                <th>Status</th>
                <th>Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {suggestedDevelopments.map((dev) => (
                <tr key={dev.id}>
                  <td className="sh-dev-title">{dev.title}</td>
                  <td>
                    <span
                      className={`sh-priority-badge ${dev.priority}`}
                      style={{
                        backgroundColor:
                          dev.priority === "high"
                            ? "#fca5a5"
                            : dev.priority === "medium"
                              ? "#fed7aa"
                              : "#cffafe",
                      }}
                    >
                      {dev.priority.toUpperCase()}
                    </span>
                  </td>
                  <td>
                    <span
                      className={`sh-dev-status ${dev.status}`}
                      style={{
                        backgroundColor:
                          dev.status === "approved"
                            ? "#d1fae5"
                            : dev.status === "pending_approval"
                              ? "#fef3c7"
                              : "#f3f4f6",
                      }}
                    >
                      {dev.status.replace("_", " ").toUpperCase()}
                    </span>
                  </td>
                  <td className="sh-dev-date">{dev.date}</td>
                  <td>
                    <div className="sh-dev-actions">
                      {dev.status === "pending_approval" && (
                        <>
                          <button
                            className="sh-mini-btn sh-approve"
                            title="Approve"
                            onClick={() => handleApproveDevlopment(dev.id)}
                          >
                            <CheckCircle size={16} />
                          </button>
                          <button
                            className="sh-mini-btn sh-reject"
                            title="Reject"
                            onClick={() => handleRejectDevlopment(dev.id)}
                          >
                            <AlertTriangle size={16} />
                          </button>
                        </>
                      )}
                      <button className="sh-mini-btn sh-view" title="View Details">
                        <FileText size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="sh-section">
        <div className="sh-section-title">
          <h2>
            <MessageSquare size={22} /> Support Center
          </h2>
          <span className="sh-subtitle">User Issues & AI-Powered Help</span>
        </div>

        <div className="sh-support-container">
          <div className="sh-tickets-list">
            <h3 className="sh-tickets-title">Open Tickets</h3>
            {supportTickets.map((ticket) => (
              <div
                key={ticket.id}
                className={`sh-ticket-item ${selectedTicket?.id === ticket.id ? "active" : ""}`}
                onClick={() => setSelectedTicket(ticket)}
              >
                <div className="sh-ticket-head">
                  <span className="sh-ticket-id">#{ticket.id}</span>
                  <span className={`sh-ticket-status ${ticket.status}`}>{ticket.status.replace("_", " ")}</span>
                </div>
                <div className="sh-ticket-user">{ticket.user}</div>
                <div className="sh-ticket-issue">{ticket.issue}</div>
                <div className="sh-ticket-time">{ticket.created}</div>
              </div>
            ))}
          </div>

          {selectedTicket ? (
            <div className="sh-ticket-detail">
              <div className="sh-detail-header">
                <h3>Ticket #{selectedTicket.id}</h3>
                <span className={`sh-status-badge ${selectedTicket.status}`}>{selectedTicket.status}</span>
              </div>

              <div className="sh-detail-body">
                <div className="sh-detail-section">
                  <h4>User</h4>
                  <p>{selectedTicket.user}</p>
                </div>

                <div className="sh-detail-section">
                  <h4>Issue</h4>
                  <p>{selectedTicket.issue}</p>
                </div>

                <div className="sh-detail-section">
                  <h4>AI Assistant Response</h4>
                  <div className="sh-ai-response">
                    <div className="sh-ai-message assistant">
                      <p>
                        {selectedTicket.ai_response
                          ? selectedTicket.ai_response.split("\n").map((line, i) => (
                            <React.Fragment key={i}>
                              {line}
                              <br />
                            </React.Fragment>
                          ))
                          : `I've analyzed the issue. Based on your report about "${selectedTicket.issue}", here are the potential causes and solutions:\n\n• Check database connection status\n• Clear browser cache and cookies\n• Verify user permissions\n• Review API logs for errors\n\nPlease try these steps and let me know if the issue persists.`}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="sh-detail-actions">
                  <button className="sh-btn sh-btn-primary" onClick={() => handleAIResponse(selectedTicket.id)}>
                    Generate AI Response
                  </button>
                  <button className="sh-btn sh-btn-secondary" onClick={() => handleResolveTicket(selectedTicket.id)}>
                    Mark as Resolved
                  </button>
                  <button className="sh-btn sh-btn-secondary" onClick={() => handleEscalateTicket(selectedTicket.id)}>
                    Escalate to MA Team
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="sh-empty-detail">
              <p>Select a ticket to view details</p>
            </div>
          )}
        </div>
      </div>
      <div className="sh-section">
        <div className="sh-alerts-head">
          <h2 className="sh-alerts-title">
            <AlertTriangle size={22} /> System Alerts
          </h2>
          <button className="sh-btn sh-btn-secondary" onClick={clearAlerts}>
            Clear All
          </button>
        </div>

        <div className="sh-grid alerts">
          {alerts.map((a) => (
            <div key={a.id} className={`sh-alert ${a.type}`} style={{ borderLeftColor: getAlertColor(a.type) }}>
              <h4>{a.title}</h4>
              <p>{a.message}</p>
              <span className="sh-alert-time">{formatTime(a.time)}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="sh-section">
        <div className="sh-section-title">
          <h2>Recent System Logs</h2>
        </div>

        <div className="sh-logs">
          {systemLogs.length ? (
            <div className="sh-logs-list">
              {systemLogs.map((log) => (
                <div key={log.id} className={`sh-log ${log.type.toLowerCase()}`}>
                  <div className="sh-log-time">{formatTime(log.timestamp)}</div>
                  <div className="sh-log-type">
                    <span className={`sh-pill ${log.type.toLowerCase()}`}>{log.type}</span>
                  </div>
                  <div className="sh-log-source">{log.source}</div>
                  <div className="sh-log-msg">{log.message}</div>
                </div>
              ))}
            </div>
          ) : (
            <div className="sh-empty">No recent logs available.</div>
          )}
        </div>
      </div>

      <div className="sh-section">
        <div className="sh-section-title">
          <h2>Trends (Last ~5 Minutes)</h2>
        </div>

        <div className="sh-grid charts">
          <div className="sh-chart-card">
            <h3>CPU Trend</h3>
            {historicalData.cpu.length ? (
              <div className="sh-chart">
                {historicalData.cpu.map((p, i) => (
                  <div
                    key={i}
                    className="sh-bar"
                    style={{ height: `${p.value}%`, width: `${100 / historicalData.cpu.length}%` }}
                    title={`${p.value.toFixed(1)}%`}
                  />
                ))}
              </div>
            ) : (
              <div className="sh-empty">No CPU metrics available.</div>
            )}
          </div>

          <div className="sh-chart-card">
            <h3>Memory Trend</h3>
            {historicalData.memory.length ? (
              <div className="sh-chart">
                {historicalData.memory.map((p, i) => (
                  <div
                    key={i}
                    className="sh-bar"
                    style={{ height: `${p.value}%`, width: `${100 / historicalData.memory.length}%` }}
                    title={`${p.value.toFixed(1)}%`}
                  />
                ))}
              </div>
            ) : (
              <div className="sh-empty">No memory metrics available.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SystemHealth;
