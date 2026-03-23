import React, { useEffect, useState } from "react";
import RequireAuth from "../../components/RequireAuth.jsx";
import axiosClient from "../../api/axiosClient";
import TMSRequestsPanel from "../../components/admin/TMSRequestsPanel";
import "./UnifiedAdminDashboard.css";

export default function UnifiedAdminDashboard() {
  return (
    <RequireAuth roles={["admin", "owner", "super_admin"]}>
      <UnifiedAdminDashboardContent />
    </RequireAuth>
  );
}

function UnifiedAdminDashboardContent() {
  const [activeTab, setActiveTab] = useState("overview");
  const [overview, setOverview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const normalizeUsersPayload = (payload) => {
    if (Array.isArray(payload)) return payload;
    if (Array.isArray(payload?.users)) return payload.users;
    if (Array.isArray(payload?.data?.users)) return payload.data.users;
    return [];
  };

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        const [healthRes, metricsRes, usersRes] = await Promise.all([
          axiosClient.get("/api/v1/system/health"),
          axiosClient.get("/api/v1/system/metrics"),
          axiosClient.get("/api/v1/admin/users?limit=200"),
        ]);
        setOverview({
          system: healthRes.data || {},
          metrics: metricsRes.data?.metrics || metricsRes.data || {},
          users: normalizeUsersPayload(usersRes.data),
        });
        setError("");
      } catch (err) {
        setError(err?.response?.data?.detail || err?.message || "Failed to fetch data");
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="admin-dashboard-loading">
        <div className="spinner"></div>
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div className="unified-admin-dashboard">
      <header className="admin-header">
        <div className="header-content">
          <h1>Unified Admin Dashboard</h1>
          <p>Manage the full GTS platform</p>
        </div>
      </header>

      <nav className="admin-tabs">
        {["overview", "users", "bots", "tms-requests", "health"].map((tab) => (
          <button
            key={tab}
            className={`tab ${activeTab === tab ? "active" : ""}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab}
          </button>
        ))}
      </nav>

      <main className="admin-content">
        {error ? (
          <div className="error-banner">
            <span>Warning</span>
            <p>{error}</p>
          </div>
        ) : null}

        {activeTab === "overview" && overview ? (
          <div className="tab-content">
            <h2>System Overview</h2>
            <div className="stats-grid">
              <div className="stat-card overall-card">
                <h3>Users</h3>
                <div className="stat-row">
                  <span>Total users:</span>
                  <strong>{overview.users.length}</strong>
                </div>
              </div>
              <div className="stat-card gts-card">
                <h3>System Health</h3>
                <div className="stat-row">
                  <span>Status:</span>
                  <strong>{overview.system.status || (overview.system.ok ? "ok" : "unknown")}</strong>
                </div>
              </div>
              <div className="stat-card tms-card">
                <h3>Metrics</h3>
                <div className="stat-row">
                  <span>Keys:</span>
                  <strong>{Object.keys(overview.metrics || {}).length}</strong>
                </div>
              </div>
            </div>
          </div>
        ) : null}

        {activeTab === "users" ? (
          <div className="tab-content">
            <h2>User Management</h2>
            <p>{overview?.users?.length || 0} users loaded from the admin API.</p>
          </div>
        ) : null}

        {activeTab === "bots" ? (
          <div className="tab-content">
            <h2>Bots Management</h2>
            <p>Use the main admin bot dashboards for detailed controls.</p>
          </div>
        ) : null}

        {activeTab === "tms-requests" ? (
          <div className="tab-content">
            <TMSRequestsPanel />
          </div>
        ) : null}

        {activeTab === "health" ? (
          <div className="tab-content">
            <h2>System Health</h2>
            <pre>{JSON.stringify(overview?.system || {}, null, 2)}</pre>
          </div>
        ) : null}
      </main>
    </div>
  );
}
