import React, { useState, useEffect, useCallback, useMemo } from "react";
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
} from "lucide-react";
import "./SystemHealth.css";

const clamp = (n, min, max) => Math.max(min, Math.min(max, n));

const SystemHealth = () => {
  const [systemStatus, setSystemStatus] = useState("disconnected");
  const [connectionStatus, setConnectionStatus] = useState({
    connected: false,
    lastCheck: null,
    responseTime: 0,
  });

  const [resources, setResources] = useState({
    cpu: { usage: 0, cores: 8, temperature: 45 },
    memory: { used: 0, total: 32, percentage: 0 },
    disk: { used: 0, total: 500, percentage: 0 },
    network: { in: 0, out: 0, connections: 0 },
  });

  const [services, setServices] = useState([
    { id: 1, name: "Web Server", status: "running", uptime: "15d 6h", port: 80, responseTime: 45 },
    { id: 2, name: "Database Server", status: "running", uptime: "15d 6h", port: 5432, responseTime: 12 },
    { id: 3, name: "Email Service", status: "warning", uptime: "2d 18h", port: 587, responseTime: 120 },
    { id: 4, name: "Storage Service", status: "running", uptime: "8d 12h", port: 9000, responseTime: 25 },
    { id: 5, name: "Authentication Service", status: "running", uptime: "15d 6h", port: 3000, responseTime: 8 },
    { id: 6, name: "Backup Service", status: "stopped", uptime: "0d 0h", port: 8080, responseTime: 0 },
  ]);

  const [systemLogs, setSystemLogs] = useState([]);
  const [alerts, setAlerts] = useState([]);

  const [performance, setPerformance] = useState({
    responseTime: 0,
    requestsPerMinute: 0,
    errorRate: 0,
    pageLoadTime: 0,
    apiUsage: 0,
  });

  const [systemInfo, setSystemInfo] = useState({
    uptime: "0d 0h 0m",
    version: "v2.5.1",
    lastBackup: "N/A",
    os: "Ubuntu 22.04 LTS",
    timezone: "UTC+3",
  });

  const [historicalData, setHistoricalData] = useState({
    cpu: [],
    memory: [],
    requests: [],
    responseTimes: [],
  });

  const [loading, setLoading] = useState(true);
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
    const avg = (arr) => (arr.length ? arr.reduce((a, b) => a + b.value, 0) / arr.length : 0);
    return {
      cpu: avg(historicalData.cpu).toFixed(1),
      memory: avg(historicalData.memory).toFixed(1),
      requests: avg(historicalData.requests).toFixed(0),
      responseTime: avg(historicalData.responseTimes).toFixed(0),
    };
  }, [historicalData]);

  const simulateSystemData = useCallback(() => {
    const nowIso = new Date().toISOString();
    const nowTs = Date.now();

    const isConnected = Math.random() > 0.1;
    const nextConn = {
      connected: isConnected,
      lastCheck: nowIso,
      responseTime: Math.floor(Math.random() * 100) + 10,
    };
    setConnectionStatus(nextConn);
    setSystemStatus(isConnected ? "connected" : "disconnected");

    const nextCpuUsage = clamp(resources.cpu.usage + (Math.random() * 10 - 5), 5, 100);
    const nextCpuTemp = 40 + Math.random() * 15;

    const nextMemUsed = 12 + Math.random() * 8;
    const nextMemPct = (nextMemUsed / resources.memory.total) * 100;

    const nextDiskUsed = 280 + Math.random() * 40;
    const nextDiskPct = (nextDiskUsed / resources.disk.total) * 100;

    const nextNetIn = Math.random() * 50;
    const nextNetOut = Math.random() * 30;
    const nextNetConn = Math.floor(Math.random() * 1000) + 100;

    const nextResources = {
      cpu: { ...resources.cpu, usage: nextCpuUsage, temperature: nextCpuTemp },
      memory: { ...resources.memory, used: nextMemUsed, percentage: nextMemPct },
      disk: { ...resources.disk, used: nextDiskUsed, percentage: nextDiskPct },
      network: { in: nextNetIn, out: nextNetOut, connections: nextNetConn },
    };
    setResources(nextResources);

    const nextPerf = {
      responseTime: Math.floor(Math.random() * 200) + 50,
      requestsPerMinute: Math.floor(Math.random() * 500) + 100,
      errorRate: Math.random() * 2,
      pageLoadTime: Math.floor(Math.random() * 1000) + 200,
      apiUsage: clamp(Math.random() * 100, 0, 100),
    };
    setPerformance(nextPerf);

    const nextServices = services.map((service) => {
      if (Math.random() < 0.05) {
        const statuses = ["running", "warning", "stopped"];
        const newStatus = statuses[Math.floor(Math.random() * statuses.length)];
        return {
          ...service,
          status: newStatus,
          responseTime: newStatus === "stopped" ? 0 : Math.floor(Math.random() * 150) + 10,
        };
      }
      return service;
    });
    setServices(nextServices);

    const logTypes = ["INFO", "WARNING", "ERROR"];
    const logMessages = [
      "System health check completed",
      "Database connection pool refreshed",
      "Cache cleared successfully",
      "API request processed",
      "Backup job scheduled",
      "Security scan completed",
      "Memory usage optimization executed",
      "Network traffic analyzed",
      "Service status updated",
      "Storage sync completed",
    ];

    if (Math.random() < 0.3) {
      const newLog = {
        id: nowTs,
        timestamp: nowIso,
        type: logTypes[Math.floor(Math.random() * logTypes.length)],
        message: logMessages[Math.floor(Math.random() * logMessages.length)],
        source: ["System", "Database", "API", "Security", "Network", "Storage"][
          Math.floor(Math.random() * 6)
        ],
      };
      setSystemLogs((prev) => [newLog, ...prev.slice(0, 9)]);
    }

    setHistoricalData((prev) => ({
      cpu: [...prev.cpu.slice(-29), { time: nowTs, value: nextCpuUsage }],
      memory: [...prev.memory.slice(-29), { time: nowTs, value: nextMemPct }],
      requests: [...prev.requests.slice(-29), { time: nowTs, value: nextPerf.requestsPerMinute }],
      responseTimes: [...prev.responseTimes.slice(-29), { time: nowTs, value: nextPerf.responseTime }],
    }));

    const newAlerts = [];

    if (nextCpuUsage > 85) {
      newAlerts.push({
        id: nowTs + 1,
        type: "critical",
        title: "High CPU Usage",
        message: `CPU usage is at ${nextCpuUsage.toFixed(1)}%`,
        time: nowIso,
      });
    }

    if (nextMemPct > 90) {
      newAlerts.push({
        id: nowTs + 2,
        type: "warning",
        title: "High Memory Usage",
        message: `Memory usage is at ${nextMemPct.toFixed(1)}%`,
        time: nowIso,
      });
    }

    if (nextPerf.responseTime > 500) {
      newAlerts.push({
        id: nowTs + 3,
        type: "warning",
        title: "Slow Response Time",
        message: `Average response time is ${nextPerf.responseTime}ms`,
        time: nowIso,
      });
    }

    if (nextPerf.errorRate > 5) {
      newAlerts.push({
        id: nowTs + 4,
        type: "critical",
        title: "High Error Rate",
        message: `Error rate is ${nextPerf.errorRate.toFixed(1)}%`,
        time: nowIso,
      });
    }

    const stopped = nextServices.filter((s) => s.status === "stopped");
    if (stopped.length > 0) {
      newAlerts.push({
        id: nowTs + 5,
        type: "critical",
        title: "Service Stopped",
        message: `${stopped[0].name} service is stopped`,
        time: nowIso,
      });
    }

    if (!isConnected) {
      newAlerts.push({
        id: nowTs + 6,
        type: "critical",
        title: "Connection Lost",
        message: "System health endpoint is not reachable",
        time: nowIso,
      });
    }

    if (newAlerts.length) {
      setAlerts((prev) => [...newAlerts, ...prev].slice(0, 6));
    }
  }, [resources, services]);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        await new Promise((r) => setTimeout(r, 900));

        setSystemInfo({
          uptime: "15d 6h 32m",
          version: "v2.5.1",
          lastBackup: "2024-01-14 23:00",
          os: "Ubuntu 22.04 LTS",
          timezone: "UTC+3",
        });

        const initialLogs = [
          {
            id: 1,
            timestamp: new Date(Date.now() - 300000).toISOString(),
            type: "INFO",
            message: "System health dashboard initialized",
            source: "System",
          },
          {
            id: 2,
            timestamp: new Date(Date.now() - 600000).toISOString(),
            type: "INFO",
            message: "Database connection established",
            source: "Database",
          },
          {
            id: 3,
            timestamp: new Date(Date.now() - 900000).toISOString(),
            type: "INFO",
            message: "All services started successfully",
            source: "System",
          },
          {
            id: 4,
            timestamp: new Date(Date.now() - 1200000).toISOString(),
            type: "INFO",
            message: "Security scan completed - no threats found",
            source: "Security",
          },
          {
            id: 5,
            timestamp: new Date(Date.now() - 1500000).toISOString(),
            type: "WARNING",
            message: "High network traffic detected",
            source: "Network",
          },
        ];
        setSystemLogs(initialLogs);

        const now = Date.now();
        setHistoricalData({
          cpu: Array.from({ length: 30 }, (_, i) => ({
            time: now - (30 - i) * 10000,
            value: 20 + Math.random() * 50,
          })),
          memory: Array.from({ length: 30 }, (_, i) => ({
            time: now - (30 - i) * 10000,
            value: 40 + Math.random() * 40,
          })),
          requests: Array.from({ length: 30 }, (_, i) => ({
            time: now - (30 - i) * 10000,
            value: 100 + Math.random() * 400,
          })),
          responseTimes: Array.from({ length: 30 }, (_, i) => ({
            time: now - (30 - i) * 10000,
            value: 50 + Math.random() * 150,
          })),
        });

        simulateSystemData();
      } finally {
        setLoading(false);
      }
    };

    load();
  }, [simulateSystemData]);

  useEffect(() => {
    let id;
    if (autoRefresh && !loading) {
      id = setInterval(simulateSystemData, refreshInterval);
    }
    return () => id && clearInterval(id);
  }, [autoRefresh, refreshInterval, loading, simulateSystemData]);

  const handleRefresh = () => {
    setLoading(true);
    setTimeout(() => {
      simulateSystemData();
      setLoading(false);
    }, 500);
  };

  const handleServiceAction = (serviceId, action) => {
    setServices((prev) =>
      prev.map((service) => {
        if (service.id !== serviceId) return service;

        const newStatus = action === "start" ? "running" : action === "stop" ? "stopped" : "warning";
        return {
          ...service,
          status: newStatus,
          responseTime: newStatus === "stopped" ? 0 : Math.floor(Math.random() * 100) + 10,
          uptime: newStatus === "running" ? "0d 0h" : service.uptime,
        };
      })
    );
  };

  const clearAlerts = () => setAlerts([]);

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
            <div
              className={`sh-status-dot ${systemStatus}`}
              style={{ backgroundColor: getStatusColor(systemStatus) }}
            />
            <span className="sh-status-text">
              Status: {systemStatus === "connected" ? "Connected" : "Disconnected"}
              {connectionStatus.lastCheck ? ` | Last check: ${formatTime(connectionStatus.lastCheck)}` : ""}
              {connectionStatus.connected ? ` | ${connectionStatus.responseTime}ms` : ""}
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

          <button className="sh-btn sh-btn-primary" onClick={handleRefresh} disabled={loading}>
            <RefreshCw size={18} className={loading ? "sh-spinning" : ""} />
            {loading ? "Refreshing..." : "Refresh Now"}
          </button>
        </div>
      </div>

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
                className={`sh-badge ${
                  resources.cpu.usage > 85 ? "critical" : resources.cpu.usage > 70 ? "warning" : "normal"
                }`}
              >
                {resources.cpu.usage.toFixed(1)}%
              </span>
            </div>

            <div className="sh-progress">
              <div className="sh-progress-bar">
                <div className="sh-progress-fill" style={{ width: `${resources.cpu.usage}%` }} />
              </div>
              <div className="sh-meta">
                <span>{resources.cpu.cores} cores</span>
                <span>{resources.cpu.temperature.toFixed(1)}C</span>
                <span>Avg: {averages.cpu}%</span>
              </div>
            </div>
          </div>

          <div className="sh-card">
            <div className="sh-card-header">
              <HardDrive size={20} />
              <h3>Memory Usage</h3>
              <span
                className={`sh-badge ${
                  resources.memory.percentage > 90
                    ? "critical"
                    : resources.memory.percentage > 80
                      ? "warning"
                      : "normal"
                }`}
              >
                {resources.memory.percentage.toFixed(1)}%
              </span>
            </div>

            <div className="sh-progress">
              <div className="sh-progress-bar">
                <div className="sh-progress-fill" style={{ width: `${resources.memory.percentage}%` }} />
              </div>
              <div className="sh-meta">
                <span>{resources.memory.used.toFixed(1)} GB used</span>
                <span>{resources.memory.total} GB total</span>
                <span>Avg: {averages.memory}%</span>
              </div>
            </div>
          </div>

          <div className="sh-card">
            <div className="sh-card-header">
              <Database size={20} />
              <h3>Disk Usage</h3>
              <span
                className={`sh-badge ${
                  resources.disk.percentage > 90
                    ? "critical"
                    : resources.disk.percentage > 80
                      ? "warning"
                      : "normal"
                }`}
              >
                {resources.disk.percentage.toFixed(1)}%
              </span>
            </div>

            <div className="sh-progress">
              <div className="sh-progress-bar">
                <div className="sh-progress-fill" style={{ width: `${resources.disk.percentage}%` }} />
              </div>
              <div className="sh-meta">
                <span>{resources.disk.used.toFixed(1)} GB used</span>
                <span>{resources.disk.total} GB total</span>
                <span>
                  {formatBytes((resources.disk.total - resources.disk.used) * 1024 * 1024 * 1024)} free
                </span>
              </div>
            </div>
          </div>

          <div className="sh-card">
            <div className="sh-card-header">
              <Network size={20} />
              <h3>Network Usage</h3>
              <span className="sh-badge normal">{resources.network.connections} connections</span>
            </div>

            <div className="sh-network">
              <div className="sh-net-row">
                <span>Inbound</span>
                <b>{resources.network.in.toFixed(1)} MB/s</b>
              </div>
              <div className="sh-net-row">
                <span>Outbound</span>
                <b>{resources.network.out.toFixed(1)} MB/s</b>
              </div>
              <div className="sh-meta">
                <span>Total: {(resources.network.in + resources.network.out).toFixed(1)} MB/s</span>
                <span>{resources.network.connections} active connections</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="sh-section">
        <div className="sh-section-title">
          <h2>Services Status</h2>
        </div>

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
                  <b>{service.responseTime}ms</b>
                </div>
              </div>

              <div className="sh-service-actions">
                <button
                  className={`sh-btn ${service.status === "running" ? "sh-btn-danger" : "sh-btn-success"}`}
                  onClick={() => handleServiceAction(service.id, service.status === "running" ? "stop" : "start")}
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

                <button className="sh-btn sh-btn-warn" onClick={() => handleServiceAction(service.id, "restart")}>
                  <RefreshCw size={16} /> Restart
                </button>
              </div>
            </div>
          ))}
        </div>
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
              <div className="sh-metric-value">{performance.responseTime}ms</div>
              <div className="sh-metric-sub">Avg: {averages.responseTime}ms</div>
            </div>
          </div>

          <div className="sh-metric-card">
            <div className="sh-metric-head">
              <Activity size={20} />
              <h3>Requests / Minute</h3>
            </div>
            <div className="sh-metric-body">
              <div className="sh-metric-value">{performance.requestsPerMinute}</div>
              <div className="sh-metric-sub">Avg: {averages.requests} req/min</div>
            </div>
          </div>

          <div className="sh-metric-card">
            <div className="sh-metric-head">
              <AlertTriangle size={20} />
              <h3>Error Rate</h3>
            </div>
            <div className="sh-metric-body">
              <div className="sh-metric-value">{performance.errorRate.toFixed(2)}%</div>
              <div className={`sh-metric-sub ${performance.errorRate > 5 ? "critical" : "ok"}`}>
                {performance.errorRate > 5 ? "High" : "Normal"}
              </div>
            </div>
          </div>

          <div className="sh-metric-card">
            <div className="sh-metric-head">
              <Clock size={20} />
              <h3>Page Load</h3>
            </div>
            <div className="sh-metric-body">
              <div className="sh-metric-value">{performance.pageLoadTime}ms</div>
              <div className="sh-metric-sub">{performance.pageLoadTime > 1000 ? "Slow" : "Fast"}</div>
            </div>
          </div>

          <div className="sh-metric-card">
            <div className="sh-metric-head">
              <Server size={20} />
              <h3>API Usage</h3>
            </div>
            <div className="sh-metric-body">
              <div className="sh-metric-value">{performance.apiUsage.toFixed(0)}%</div>
              <div className="sh-metric-sub">Rate-limit utilization</div>
            </div>
          </div>
        </div>
      </div>

      {alerts.length > 0 && (
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
      )}

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
          </div>

          <div className="sh-chart-card">
            <h3>Memory Trend</h3>
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
          </div>
        </div>
      </div>
    </div>
  );
};

export default SystemHealth;
