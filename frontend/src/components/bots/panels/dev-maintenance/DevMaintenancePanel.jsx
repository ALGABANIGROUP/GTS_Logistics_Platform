import React, { useEffect, useState } from "react";
import axiosClient from "../../../../api/axiosClient";
import DevMaintenanceLiveChat from "./DevMaintenanceLiveChat";
import DevMaintenanceControlPanel from "../../DevMaintenanceControlPanel";
import "./DevMaintenancePanel.css";

const SystemMonitoringView = ({ health, loading, error }) => (
    <div style={{ padding: "24px", color: "white" }}>
        <h2>System Monitoring</h2>
        {error ? <p style={{ color: "#fca5a5" }}>{error}</p> : null}
        {loading ? (
            <p>Loading system metrics...</p>
        ) : (
            <div style={{ display: "grid", gap: "12px", maxWidth: "760px" }}>
                <div>Status: {health?.status || "unknown"}</div>
                <div>Database: {health?.database?.status || health?.checks?.database?.status || "unknown"}</div>
                <div>Environment: {health?.environment || "unknown"}</div>
            </div>
        )}
    </div>
);

const BugTrackerView = ({ tickets, loading }) => (
    <div style={{ padding: "24px", color: "white" }}>
        <h2>Bug Tracker</h2>
        {loading ? (
            <p>Loading support tickets...</p>
        ) : tickets.length === 0 ? (
            <p>No open maintenance tickets.</p>
        ) : (
            <div style={{ display: "grid", gap: "12px" }}>
                {tickets.map((ticket) => (
                    <div key={ticket.id} style={{ border: "1px solid rgba(148, 163, 184, 0.2)", borderRadius: "12px", padding: "14px" }}>
                        <div style={{ fontWeight: 700 }}>{ticket.issue}</div>
                        <div style={{ color: "#94a3b8", fontSize: "14px" }}>{ticket.user} • {ticket.priority}</div>
                        <div style={{ marginTop: "8px" }}>{ticket.description}</div>
                    </div>
                ))}
            </div>
        )}
    </div>
);

const DeploymentsView = ({ developments, loading }) => (
    <div style={{ padding: "24px", color: "white" }}>
        <h2>Deployment Pipeline</h2>
        {loading ? (
            <p>Loading development queue...</p>
        ) : developments.length === 0 ? (
            <p>No pending development items.</p>
        ) : (
            <div style={{ display: "grid", gap: "12px" }}>
                {developments.map((dev) => (
                    <div key={dev.id} style={{ border: "1px solid rgba(148, 163, 184, 0.2)", borderRadius: "12px", padding: "14px" }}>
                        <div style={{ fontWeight: 700 }}>{dev.title}</div>
                        <div style={{ color: "#94a3b8", fontSize: "14px" }}>{dev.status} • {dev.priority}</div>
                        <div style={{ marginTop: "8px" }}>{dev.description}</div>
                    </div>
                ))}
            </div>
        )}
    </div>
);

const SecurityView = ({ reports, loading }) => {
    const latest = reports[0] || null;
    return (
        <div style={{ padding: "24px", color: "white" }}>
            <h2>Security Dashboard</h2>
            {loading ? (
                <p>Loading maintenance reports...</p>
            ) : !latest ? (
                <p>No security-related maintenance report available.</p>
            ) : (
                <div style={{ border: "1px solid rgba(148, 163, 184, 0.2)", borderRadius: "12px", padding: "14px", maxWidth: "760px" }}>
                    <div style={{ fontWeight: 700 }}>Latest report: {latest.date}</div>
                    <div style={{ color: "#94a3b8", fontSize: "14px" }}>Status: {latest.status} • Uptime: {latest.uptime}</div>
                    <ul style={{ marginTop: "10px", paddingLeft: "18px" }}>
                        {(latest.recommendations || []).map((item, index) => (
                            <li key={index}>{item}</li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
};

const DevMaintenancePanel = () => {
    const [activeTab, setActiveTab] = useState("dashboard");
    const [botConfig, setBotConfig] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [health, setHealth] = useState(null);
    const [tickets, setTickets] = useState([]);
    const [developments, setDevelopments] = useState([]);
    const [reports, setReports] = useState([]);

    useEffect(() => {
        setBotConfig({
            name: "AI Development & Maintenance Bot",
            description: "Technical support, bug tracking, and system monitoring",
            status: "active",
            version: "2.4.1",
            tabs: [
                { id: "dashboard", name: "Control Panel" },
                { id: "livechat", name: "Live Support" },
                { id: "monitoring", name: "System Monitor" },
                { id: "bugs", name: "Bug Tracker" },
                { id: "deployments", name: "Deployments" },
                { id: "security", name: "Security" },
            ],
        });
    }, []);

    useEffect(() => {
        let mounted = true;
        const load = async () => {
            setLoading(true);
            setError("");
            try {
                const [healthRes, reportsRes, devRes, ticketsRes] = await Promise.all([
                    axiosClient.get("/api/v1/system/health"),
                    axiosClient.get("/api/v1/maintenance/reports"),
                    axiosClient.get("/api/v1/maintenance/suggested-developments"),
                    axiosClient.get("/api/v1/maintenance/support-tickets"),
                ]);
                if (!mounted) return;
                setHealth(healthRes?.data || null);
                setReports(reportsRes?.data?.reports || []);
                setDevelopments(devRes?.data?.developments || []);
                setTickets(ticketsRes?.data?.tickets || []);
            } catch (err) {
                if (!mounted) return;
                setError(err?.response?.data?.detail || err?.message || "Failed to load maintenance telemetry.");
            } finally {
                if (mounted) setLoading(false);
            }
        };
        load();
        return () => {
            mounted = false;
        };
    }, []);

    const renderTabContent = () => {
        switch (activeTab) {
            case "dashboard":
                return <DevMaintenanceControlPanel mode="active" />;
            case "livechat":
                return <DevMaintenanceLiveChat />;
            case "monitoring":
                return <SystemMonitoringView health={health} loading={loading} error={error} />;
            case "bugs":
                return <BugTrackerView tickets={tickets} loading={loading} />;
            case "deployments":
                return <DeploymentsView developments={developments} loading={loading} />;
            case "security":
                return <SecurityView reports={reports} loading={loading} />;
            default:
                return <DevMaintenanceControlPanel mode="active" />;
        }
    };

    if (!botConfig) return <div className="loading-panel">Loading Dev & Maintenance Bot...</div>;

    return (
        <div className="dev-maintenance-panel" style={{ background: "#0f172a", minHeight: "100vh" }}>
            <div style={{ background: "rgba(15, 23, 42, 0.8)", backdropFilter: "blur(20px)", borderBottom: "1px solid rgba(148, 163, 184, 0.2)", padding: "16px 24px" }}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "16px", flexWrap: "wrap" }}>
                    <div>
                        <h1 style={{ color: "white", fontSize: "20px", fontWeight: "bold", margin: 0 }}>{botConfig.name}</h1>
                        <p style={{ color: "#94a3b8", fontSize: "14px", margin: "4px 0 0 0" }}>{botConfig.description}</p>
                    </div>
                    <div style={{ color: "#94a3b8", fontSize: "14px" }}>
                        {loading ? "Loading..." : `Reports: ${reports.length} • Tickets: ${tickets.length} • Suggestions: ${developments.length}`}
                    </div>
                </div>
            </div>

            <div style={{ background: "rgba(15, 23, 42, 0.6)", borderBottom: "1px solid rgba(148, 163, 184, 0.2)", padding: "0 24px", display: "flex", gap: "8px", overflowX: "auto" }}>
                {botConfig.tabs.map((tab) => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        style={{
                            background: activeTab === tab.id ? "rgba(59, 130, 246, 0.15)" : "transparent",
                            border: "none",
                            borderBottom: activeTab === tab.id ? "2px solid #3b82f6" : "2px solid transparent",
                            color: activeTab === tab.id ? "white" : "#94a3b8",
                            padding: "16px 20px",
                            cursor: "pointer",
                            fontSize: "14px",
                            fontWeight: 600,
                            whiteSpace: "nowrap",
                        }}
                    >
                        {tab.name}
                    </button>
                ))}
            </div>

            <div>{renderTabContent()}</div>
        </div>
    );
};

export default DevMaintenancePanel;
