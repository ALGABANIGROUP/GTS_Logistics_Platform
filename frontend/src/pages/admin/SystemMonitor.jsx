import React, { useState, useEffect } from "react";
import { AlertCircle, RefreshCw, Activity, Cpu, Database, Server } from "lucide-react";
import "./SystemHealth.css";

const SystemMonitor = () => {
    const [metrics, setMetrics] = useState(null);
    const [alerts, setAlerts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [retryCount, setRetryCount] = useState(0);

    const fetchSystemMetrics = async () => {
        setLoading(true);
        setError(null);

        try {
            const metricsResponse = await fetch("/api/v1/system/metrics");
            if (!metricsResponse.ok) {
                if (metricsResponse.status === 503) {
                    throw new Error("System metrics service temporarily unavailable");
                }
                throw new Error(`Failed to fetch metrics: ${metricsResponse.status}`);
            }

            const metricsData = await metricsResponse.json();
            setMetrics(metricsData);

            const alertsResponse = await fetch("/api/v1/system/alerts?active=true");
            if (!alertsResponse.ok) {
                throw new Error(`Failed to fetch alerts: ${alertsResponse.status}`);
            }

            const alertsData = await alertsResponse.json();
            setAlerts(alertsData.alerts || []);
        } catch (err) {
            console.error("Error fetching system data:", err);
            setError(err.message);
            setMetrics(null);
            setAlerts([]);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchSystemMetrics();
        const interval = setInterval(fetchSystemMetrics, 30000);
        return () => clearInterval(interval);
    }, [retryCount]);

    const handleRetry = () => {
        setRetryCount((prev) => prev + 1);
    };

    if (loading) {
        return (
            <div className="system-monitor-loading">
                <div className="spinner"></div>
                <p>Loading system metrics...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="system-monitor-error">
                <AlertCircle size={48} className="error-icon" />
                <h3>System Monitor Unavailable</h3>
                <p>{error}</p>
                <button onClick={handleRetry} className="retry-button">
                    <RefreshCw size={16} />
                    Retry
                </button>
            </div>
        );
    }

    if (!metrics) {
        return (
            <div className="system-monitor-empty">
                <p>No system metrics available</p>
                <button onClick={handleRetry}>Refresh</button>
            </div>
        );
    }

    return (
        <div className="system-monitor-container">
            <div className="metrics-grid">
                <div className="metric-card">
                    <Activity className="metric-icon" />
                    <h4>CPU Usage</h4>
                    <p className="metric-value">{metrics.cpu?.usage || "N/A"}%</p>
                </div>

                <div className="metric-card">
                    <Database className="metric-icon" />
                    <h4>Memory Usage</h4>
                    <p className="metric-value">
                        {metrics.memory?.used || "N/A"} / {metrics.memory?.total || "N/A"} MB
                    </p>
                </div>

                <div className="metric-card">
                    <Server className="metric-icon" />
                    <h4>Active Services</h4>
                    <p className="metric-value">{metrics.services?.active || 0} / {metrics.services?.total || 0}</p>
                </div>

                <div className="metric-card">
                    <Cpu className="metric-icon" />
                    <h4>Response Time</h4>
                    <p className="metric-value">{metrics.response_time?.avg || "N/A"} ms</p>
                </div>
            </div>

            {alerts.length > 0 && (
                <div className="alerts-section">
                    <h3>Active Alerts ({alerts.length})</h3>
                    {alerts.map((alert) => (
                        <div key={alert.id || `${alert.message}-${alert.severity}`} className={`alert-item alert-${alert.severity}`}>
                            <AlertCircle size={16} />
                            <span>{alert.message}</span>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default SystemMonitor;
