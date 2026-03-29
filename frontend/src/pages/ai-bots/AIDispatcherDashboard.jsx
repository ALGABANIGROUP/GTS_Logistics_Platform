import React, { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Activity,
  AlertTriangle,
  Bot,
  ChevronRight,
  MapPinned,
  PlayCircle,
  RefreshCcw,
  ShieldCheck,
  Truck,
  UserRound,
  Wrench,
} from "lucide-react";
import axiosClient from "../../api/axiosClient";
import "./AIDispatcherDashboard.css";

const formatTimestamp = (value) => {
  if (!value) return "N/A";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" });
};

export default function AIDispatcherDashboard() {
  const navigate = useNavigate();
  const [now, setNow] = useState(new Date());
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchMetrics = useCallback(async () => {
    try {
      const res = await axiosClient.get("/api/v1/ai/bots/available/ai_dispatcher/status");
      const payload = res?.data?.status || res?.data?.data || res?.data;
      setMetrics(payload || null);
      setError("");
    } catch (err) {
      setError("Unable to load dispatcher metrics.");
    } finally {
      setLoading(false);
    }
  }, []);

  const demandLabels = metrics?.demand?.labels || [];
  const demandActual = metrics?.demand?.counts || [];
  const demandPredicted = metrics?.demand?.predicted || demandActual;
  const utilization = metrics?.utilization || [];
  const updates = metrics?.updates || [];

  const demandMax = useMemo(() => {
    const values = [...demandActual, ...demandPredicted];
    return Math.max(1, ...values);
  }, [demandActual, demandPredicted]);

  const stats = useMemo(() => {
    const shipments = metrics?.shipments || {};
    const assignments = metrics?.assignments || {};
    const total = shipments.total || 0;
    const activeAssignments = assignments.active || 0;
    const queue = shipments.unassigned || 0;
    const delivered = shipments.delivered || 0;
    const activeDrivers = assignments.active_drivers || 0;
    const successRate = total ? Number(((delivered / total) * 100).toFixed(1)) : 0;
    return {
      totalShipments: total,
      activeAssignments,
      dispatchQueue: queue,
      successRate,
      activeDrivers,
    };
  }, [metrics]);

  useEffect(() => {
    const tick = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(tick);
  }, []);

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 15000);
    return () => clearInterval(interval);
  }, [fetchMetrics]);

  const openDispatcherControl = useCallback(() => {
    navigate("/ai-bots/control?bot=ai_dispatcher");
  }, [navigate]);

  const openAlertsView = useCallback(() => {
    navigate("/dispatch");
  }, [navigate]);

  return (
    <div className="aid-dashboard">
      <header className="aid-header">
        <div>
          <p className="aid-kicker">AID - AI Dispatcher</p>
          <h1>AI Dispatcher Dashboard</h1>
          <p className="aid-subtitle">
            Real-time dispatch management and AI-driven optimization.
          </p>
          {error ? <p className="aid-error">{error}</p> : null}
        </div>
        <div className="aid-header-actions">
          <div className="aid-chip">
            <span>{loading ? "Loading" : "Live"}</span>
            <strong>{now.toLocaleString("en-US")}</strong>
          </div>
          <div className="aid-profile">
            <div className="aid-avatar">AD</div>
            <div>
              <div className="aid-profile-name">Admin User</div>
              <div className="aid-profile-role">System Administrator</div>
            </div>
          </div>
        </div>
      </header>

      <section className="aid-stats">
        <div className="aid-card aid-stat-card">
          <div>
            <p>Total Shipments</p>
            <h2>{stats.totalShipments.toLocaleString()}</h2>
            <span className="aid-trend neutral">Live database count</span>
          </div>
          <div className="aid-stat-icon primary">
            <Truck size={28} />
          </div>
        </div>
        <div className="aid-card aid-stat-card">
          <div>
            <p>Active Assignments</p>
            <h2>{stats.activeAssignments}</h2>
            <span className="aid-trend neutral">Current dispatch workload</span>
          </div>
          <div className="aid-stat-icon secondary">
            <UserRound size={28} />
          </div>
        </div>
        <div className="aid-card aid-stat-card">
          <div>
            <p>Dispatch Queue</p>
            <h2>{stats.dispatchQueue}</h2>
            <span className="aid-trend neutral">Unassigned shipments</span>
          </div>
          <div className="aid-stat-icon success">
            <Activity size={28} />
          </div>
        </div>
        <div className="aid-card aid-stat-card">
          <div>
            <p>Delivery Success Rate</p>
            <h2>{stats.successRate}%</h2>
            <span className="aid-trend neutral">Delivered / total shipments</span>
          </div>
          <div className="aid-stat-icon warning">
            <MapPinned size={28} />
          </div>
        </div>
      </section>

      <section className="aid-actions">
        <button className="aid-action primary" onClick={openDispatcherControl}>
          <PlayCircle size={18} /> Start AI Optimization
        </button>
        <button className="aid-action ghost" onClick={fetchMetrics}>
          <RefreshCcw size={18} /> Refresh Data
        </button>
        <button className="aid-action success" onClick={openDispatcherControl}>
          <Bot size={18} /> Run AI Models
        </button>
        <button className="aid-action ghost" onClick={openDispatcherControl}>
          <MapPinned size={18} /> View Heatmap
        </button>
        <button className="aid-action warning" onClick={openAlertsView}>
          <AlertTriangle size={18} /> Alerts
        </button>
      </section>

      <section className="aid-grid two-col">
        <div className="aid-card aid-chart-card">
          <div className="aid-card-header">
            <h3>Demand Forecasting</h3>
            <span className="aid-pill">Last 24 Hours</span>
          </div>
          <div className="aid-chart">
            {demandLabels.length ? (
              demandLabels.map((label, index) => (
                <div className="aid-chart-col" key={label}>
                  <div className="aid-chart-bars">
                    <span
                      className="aid-chart-bar actual"
                      style={{
                        height: `${(demandActual[index] / demandMax) * 100}%`,
                      }}
                    />
                    <span
                      className="aid-chart-bar predicted"
                      style={{
                        height: `${(demandPredicted[index] / demandMax) * 100}%`,
                      }}
                    />
                  </div>
                  <span className="aid-chart-label">{label}</span>
                </div>
              ))
            ) : (
              <div className="aid-empty">No demand data available.</div>
            )}
          </div>
          {demandLabels.length ? (
            <div className="aid-legend">
              <span><i className="aid-dot actual" /> Actual Demand</span>
              <span><i className="aid-dot predicted" /> AI Predicted</span>
            </div>
          ) : null}
        </div>

        <div className="aid-card aid-chart-card">
          <div className="aid-card-header">
            <h3>Driver Utilization</h3>
            <span className="aid-pill">By City</span>
          </div>
          <div className="aid-utilization">
            {utilization.length ? (
              utilization.map((item) => (
                <div key={item.city} className="aid-util-row">
                  <span className="aid-util-label">{item.city}</span>
                  <div className="aid-util-bar">
                    <span style={{ width: `${item.value}%` }} />
                  </div>
                  <span className="aid-util-value">{item.value}%</span>
                </div>
              ))
            ) : (
              <div className="aid-empty">No utilization data available.</div>
            )}
          </div>
        </div>
      </section>

      <section className="aid-grid two-col">
        <div className="aid-card">
          <div className="aid-card-header">
            <h3>
              <ShieldCheck size={18} /> AI Models Status
            </h3>
          </div>
          <ul className="aid-list">
            <li>
              <div className="aid-list-left">
                <span className="aid-status active" />
                <span>Dispatcher Core</span>
              </div>
              <strong>{metrics?.system_load || "unknown"}</strong>
            </li>
            <li>
              <div className="aid-list-left">
                <span className="aid-status active" />
                <span>Active Drivers</span>
              </div>
              <strong>{stats.activeDrivers}</strong>
            </li>
            <li>
              <div className="aid-list-left">
                <span className="aid-status active" />
                <span>Recent Location Pings</span>
              </div>
              <strong>{metrics?.telemetry?.recent_location_pings ?? 0}</strong>
            </li>
          </ul>
        </div>
        <div className="aid-card">
          <div className="aid-card-header">
            <h3>
              <Wrench size={18} /> System Infrastructure
            </h3>
          </div>
          <ul className="aid-list">
            <li>
              <div className="aid-list-left">
                <span className="aid-status active" />
                <span>Last Assignment</span>
              </div>
              <strong>{metrics?.assignments?.last_assigned_at || "N/A"}</strong>
            </li>
            <li>
              <div className="aid-list-left">
                <span className="aid-status active" />
                <span>Last Updated</span>
              </div>
              <strong>{metrics?.last_updated || "N/A"}</strong>
            </li>
          </ul>
        </div>
      </section>

      <section className="aid-card aid-updates">
        <div className="aid-card-header">
          <h3>Live Dispatch Updates</h3>
          <span className="aid-live">
            <i /> Real-time
          </span>
        </div>
        <div className="aid-updates-list">
          {updates.length ? (
            updates.map((update) => (
              <div key={update.id} className="aid-update-item">
                <div className={`aid-update-icon ${update.type}`}>
                  {update.type === "assignment" ? <Truck size={18} /> : null}
                  {update.type === "driver" ? <UserRound size={18} /> : null}
                  {update.type === "system" ? <Activity size={18} /> : null}
                </div>
                <div className="aid-update-content">
                  <div className="aid-update-title">{update.title}</div>
                  <div className="aid-update-time">{formatTimestamp(update.time)}</div>
                </div>
                <ChevronRight size={18} className="aid-update-arrow" />
              </div>
            ))
          ) : (
            <div className="aid-empty">No updates available.</div>
          )}
        </div>
      </section>

      <footer className="aid-footer">
        <p>AID - AI Dispatcher System v2.4.1 | Smart Transportation Platform</p>
        <p>
          Active Drivers: {stats.activeDrivers} | Active Assignments: {stats.activeAssignments} | Queue: {stats.dispatchQueue}
        </p>
      </footer>
    </div>
  );
}
