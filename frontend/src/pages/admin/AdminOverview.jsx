import React, { useEffect, useMemo, useState } from "react";
import axiosClient from "@/api/axiosClient";
import RequireAuth from "../../components/RequireAuth.jsx";
import "./AdminOverview.css";

const emptyState = {
  loading: true,
  error: "",
  health: null,
  metrics: null,
  database: null,
  bots: null,
  usersCount: null,
};

const isHealthyStatus = (payload) => {
  if (!payload) return false;
  const status = String(payload.status || payload.ok || "").toLowerCase();
  return payload.ok === true || status === "ok" || status === "healthy" || status === "true";
};

const extractUsersCount = (payload) => {
  if (Array.isArray(payload)) return payload.length;
  if (Array.isArray(payload?.users)) return payload.users.length;
  if (Array.isArray(payload?.items)) return payload.items.length;
  if (typeof payload?.total === "number") return payload.total;
  return null;
};

const AdminOverview = () => {
  const [state, setState] = useState(emptyState);

  useEffect(() => {
    let active = true;

    const load = async () => {
      setState((prev) => ({ ...prev, loading: true, error: "" }));
      const [healthRes, metricsRes, databaseRes, botsRes, usersRes] = await Promise.allSettled([
        axiosClient.get("/api/v1/system/health"),
        axiosClient.get("/api/v1/system/metrics"),
        axiosClient.get("/api/v1/system/database/stats"),
        axiosClient.get("/api/v1/system/bots/status"),
        axiosClient.get("/api/v1/admin/users?limit=500"),
      ]);

      if (!active) return;

      const next = {
        loading: false,
        error: "",
        health: healthRes.status === "fulfilled" ? healthRes.value.data : null,
        metrics: metricsRes.status === "fulfilled" ? metricsRes.value.data : null,
        database: databaseRes.status === "fulfilled" ? databaseRes.value.data : null,
        bots: botsRes.status === "fulfilled" ? botsRes.value.data : null,
        usersCount: usersRes.status === "fulfilled" ? extractUsersCount(usersRes.value.data) : null,
      };

      const errors = [healthRes, metricsRes, databaseRes, botsRes, usersRes]
        .filter((item) => item.status === "rejected")
        .map((item) => item.reason?.response?.data?.detail || item.reason?.message)
        .filter(Boolean);

      next.error = errors[0] || "";
      setState(next);
    };

    load();
    return () => {
      active = false;
    };
  }, []);

  const botSummary = useMemo(() => {
    const raw = state.bots?.bots || state.bots;
    if (!raw || typeof raw !== "object") {
      return { total: 0, online: 0, entries: [] };
    }

    const entries = Object.entries(raw);
    const online = entries.filter(([, info]) => {
      const status =
        typeof info === "object" && info !== null ? info.status || info.role || "ok" : String(info);
      const normalized = String(status).toLowerCase();
      return normalized.includes("ok") || normalized.includes("online") || normalized.includes("active");
    }).length;

    return { total: entries.length, online, entries: entries.slice(0, 4) };
  }, [state.bots]);

  const metricsSummary = useMemo(() => {
    const raw = state.metrics?.metrics || state.metrics || {};
    const entries = Object.entries(raw || {});
    return entries.slice(0, 4);
  }, [state.metrics]);

  const dbSummary = useMemo(() => {
    const raw = state.database || {};
    const nestedStats = raw?.stats || null;
    const nestedDatabase = raw?.database || null;
    const tableCounts = nestedDatabase?.table_counts || raw?.table_counts || {};
    const totalTables =
      nestedStats?.total_tables ??
      raw?.total_tables ??
      (tableCounts && typeof tableCounts === "object" ? Object.keys(tableCounts).length : null);
    const totalRows =
      nestedStats?.total_rows ??
      raw?.total_rows ??
      (tableCounts && typeof tableCounts === "object"
        ? Object.values(tableCounts).reduce(
            (sum, value) => sum + (typeof value === "number" ? value : 0),
            0
          )
        : null);
    const responseTimeMs =
      raw?.response_time_ms ??
      nestedDatabase?.response_time_ms ??
      nestedStats?.response_time_ms ??
      null;

    return {
      totalTables,
      totalRows,
      responseTimeMs,
      connected:
        raw?.connected ??
        (String(raw?.status || nestedDatabase?.connection || "").toLowerCase() === "connected"),
      status:
        raw?.status ||
        nestedDatabase?.connection ||
        (raw?.connected ? "connected" : null),
      tableCounts,
    };
  }, [state.database]);

  const statsCards = [
    {
      title: "System Health",
      value: state.health ? (isHealthyStatus(state.health) ? "Healthy" : "Attention") : "Unavailable",
      tone: state.health ? (isHealthyStatus(state.health) ? "ok" : "warn") : "muted",
      meta: state.health?.status || state.health?.message || "Health endpoint",
    },
    {
      title: "Database",
      value:
        typeof dbSummary.totalTables === "number"
          ? `${dbSummary.totalTables} tables`
          : dbSummary.connected
            ? "Connected"
            : "Unavailable",
      tone: dbSummary.connected || typeof dbSummary.totalTables === "number" ? "ok" : "muted",
      meta:
        typeof dbSummary.responseTimeMs === "number"
          ? `${dbSummary.responseTimeMs} ms response`
          : "Database stats endpoint",
    },
    {
      title: "AI Bots",
      value: botSummary.total ? `${botSummary.online}/${botSummary.total} online` : "Unavailable",
      tone: botSummary.total ? "ok" : "muted",
      meta: "System bot registry",
    },
    {
      title: "Users",
      value: state.usersCount != null ? String(state.usersCount) : "Unavailable",
      tone: state.usersCount != null ? "ok" : "muted",
      meta: "Admin users listing",
    },
  ];

  return (
    <RequireAuth roles={["admin", "owner", "super_admin"]}>
      <div className="admin-overview-container">
        <div className="page-header">
          <h1>Admin Overview</h1>
          <div className="breadcrumb">Admin / Overview</div>
        </div>

        {state.error ? (
          <div className="overview-banner overview-banner-warn">
            Some admin signals could not be loaded. Showing available data only.
          </div>
        ) : null}

        {state.loading ? (
          <div className="overview-banner">Loading live admin signals...</div>
        ) : null}

        <div className="stats-cards">
          {statsCards.map((card) => (
            <div key={card.title} className="stat-card">
              <h3>{card.title}</h3>
              <p className={`stat-number stat-number-${card.tone}`}>{card.value}</p>
              <p className="stat-meta">{card.meta}</p>
            </div>
          ))}
        </div>

        <section>
          <div className="section-header">
            <h2>Live Monitoring</h2>
          </div>

          <div className="grid-two">
            <div className="panel">
              <h3>System Health</h3>
              <p>
                {state.health?.message ||
                  state.health?.status ||
                  "No system health details returned."}
              </p>
            </div>

            <div className="panel">
              <h3>Database</h3>
              <p>
                {typeof dbSummary.totalRows === "number"
                  ? `Approx. ${dbSummary.totalRows.toLocaleString()} rows across the current database snapshot.`
                  : dbSummary.connected
                    ? "Database is connected, but row count is not exposed by this endpoint."
                    : "Database row count is not available."}
              </p>
            </div>

            <div className="panel">
              <h3>AI Bots</h3>
              <ul className="overview-list">
                {botSummary.entries.length ? (
                  botSummary.entries.map(([name, info]) => (
                    <li key={name}>
                      <span>{name}</span>
                      <span>
                        {typeof info === "object" && info !== null
                          ? info.status || info.role || "ok"
                          : String(info)}
                      </span>
                    </li>
                  ))
                ) : (
                  <li>
                    <span>No bot telemetry available.</span>
                  </li>
                )}
              </ul>
            </div>

            <div className="panel">
              <h3>Metrics Snapshot</h3>
              <ul className="overview-list">
                {metricsSummary.length ? (
                  metricsSummary.map(([key, value]) => (
                    <li key={key}>
                      <span>{key}</span>
                      <span>{typeof value === "number" ? value.toLocaleString() : String(value)}</span>
                    </li>
                  ))
                ) : (
                  <li>
                    <span>No metric values returned.</span>
                  </li>
                )}
              </ul>
            </div>
          </div>
        </section>
      </div>
    </RequireAuth>
  );
};

export default AdminOverview;
