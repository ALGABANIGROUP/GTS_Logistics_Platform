import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const SystemHealthWidget = () => {
    const navigate = useNavigate();
    const [systemHealth, setSystemHealth] = useState({
        status: "unknown",
        errorCount: 0,
        lastCheck: null,
        loading: false,
        error: null,
        metrics: {
            apiLatency: null,
            databaseUsage: null,
            cacheHitRate: null,
            messageQueueBacklog: null,
        },
    });

    const fetchMetrics = async () => {
        const metricsRes = await axios.get("/api/v1/system/metrics", {
            timeout: 5000,
        });
        return {
            apiLatency: metricsRes.data.api_latency_ms ?? null,
            databaseUsage: metricsRes.data.database_usage_percent ?? null,
            cacheHitRate: metricsRes.data.cache_hit_rate_percent ?? null,
            messageQueueBacklog: metricsRes.data.message_queue_backlog ?? null,
        };
    };

    const performHealthCheck = async () => {
        setSystemHealth((prev) => ({ ...prev, loading: true, error: null }));

        const checks = [
            { name: "Database", endpoint: "/api/v1/health/db" },
            { name: "API", endpoint: "/healthz" },
            { name: "System", endpoint: "/api/v1/system/health" },
            { name: "Cache", endpoint: "/api/v1/health/redis" },
        ];

        let errorCount = 0;
        let successCount = 0;

        for (const check of checks) {
            try {
                const response = await axios.get(check.endpoint, {
                    timeout: 5000,
                });
                if (response.status === 200) {
                    successCount++;
                } else {
                    errorCount++;
                }
            } catch (err) {
                errorCount++;
            }
        }

        const status =
            errorCount === 0 ? "healthy" : errorCount <= 1 ? "warning" : "critical";

        try {
            const metrics = await fetchMetrics();
            setSystemHealth({
                status,
                errorCount,
                lastCheck: new Date().toLocaleTimeString(),
                loading: false,
                error: null,
                metrics,
            });
        } catch (err) {
            console.error("Failed to fetch metrics:", err);
            setSystemHealth({
                status,
                errorCount,
                lastCheck: new Date().toLocaleTimeString(),
                loading: false,
                error: err?.response?.data?.detail || err?.message || "Failed to fetch health data",
                metrics: {
                    apiLatency: null,
                    databaseUsage: null,
                    cacheHitRate: null,
                    messageQueueBacklog: null,
                },
            });
        }
    };

    // Auto-check on mount
    useEffect(() => {
        performHealthCheck();
        // Check every 30 seconds
        const interval = setInterval(performHealthCheck, 30 * 1000);
        return () => clearInterval(interval);
    }, []);

    const statusColors = {
        healthy: {
            bg: "bg-emerald-500/10",
            border: "border-emerald-500/30",
            text: "text-emerald-300",
            icon: "✅",
            label: "Healthy",
        },
        warning: {
            bg: "bg-amber-500/10",
            border: "border-amber-500/30",
            text: "text-amber-300",
            icon: "⚠️",
            label: "Warning",
        },
        critical: {
            bg: "bg-rose-500/10",
            border: "border-rose-500/30",
            text: "text-rose-300",
            icon: "🚨",
            label: "Critical",
        },
        unknown: {
            bg: "bg-slate-500/10",
            border: "border-slate-500/30",
            text: "text-slate-300",
            icon: "❓",
            label: "Checking...",
        },
    };

    const currentStatus = statusColors[systemHealth.status];

    if (systemHealth.error && !systemHealth.loading && systemHealth.metrics.apiLatency == null) {
        return (
            <div className="rounded-2xl glass-15 p-5 shadow-xl shadow-black/35 border border-rose-500/30 bg-rose-500/10">
                <div className="text-2xl text-rose-300 mb-2">⚠️</div>
                <h2 className="text-sm font-semibold text-slate-50">Health Data Unavailable</h2>
                <p className="text-xs text-rose-200 mt-2">{String(systemHealth.error)}</p>
                <button
                    onClick={performHealthCheck}
                    className="mt-4 px-3 py-2 rounded-lg text-xs font-semibold border bg-slate-500/20 text-slate-200 border-slate-500/30 hover:bg-slate-500/30"
                >
                    Retry
                </button>
            </div>
        );
    }

    return (
        <div
            className={`rounded-2xl glass-15 p-5 shadow-xl shadow-black/35 border ${currentStatus.border} ${currentStatus.bg}`}
        >
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                    <div className={`text-2xl ${currentStatus.text}`}>
                        {currentStatus.icon}
                    </div>
                    <div>
                        <h2 className="text-sm font-semibold text-slate-50">
                            System Health Monitor
                        </h2>
                        <p className={`text-xs ${currentStatus.text}`}>
                            {currentStatus.label}
                        </p>
                    </div>
                </div>
                <button
                    onClick={performHealthCheck}
                    disabled={systemHealth.loading}
                    className={`px-3 py-1 rounded-lg text-xs font-semibold border transition-all ${systemHealth.loading
                            ? "bg-slate-500/20 text-slate-300 border-slate-500/30 cursor-not-allowed"
                            : "bg-slate-500/20 text-slate-200 border-slate-500/30 hover:bg-slate-500/30"
                        }`}
                >
                    {systemHealth.loading ? "Checking..." : "Check Now"}
                </button>
            </div>

            {/* Status Indicators */}
            <div className="grid grid-cols-2 gap-3 mb-4">
                <div className="backdrop-blur-sm bg-white/5 rounded-lg p-3 border border-white/10">
                    <p className="text-xs text-gray-400">Errors Detected</p>
                    <p className={`text-2xl font-bold mt-1 ${systemHealth.errorCount === 0
                            ? "text-emerald-300"
                            : systemHealth.errorCount <= 1
                                ? "text-amber-300"
                                : "text-rose-300"
                        }`}>
                        {systemHealth.errorCount}
                    </p>
                </div>

                <div className="backdrop-blur-sm bg-white/5 rounded-lg p-3 border border-white/10">
                    <p className="text-xs text-gray-400">Last Check</p>
                    <p className="text-sm text-slate-200 mt-1">
                        {systemHealth.lastCheck || "Never"}
                    </p>
                </div>
            </div>

            {/* Real-time System Metrics */}
            <div className="bg-white/5 rounded-lg mb-4 border border-white/10">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 p-3">
                    <div>
                        <p className="text-xs text-gray-400">API Gateway</p>
                        <p className="text-lg font-bold text-blue-300 mt-1">
                            {systemHealth.metrics.apiLatency != null ? `${systemHealth.metrics.apiLatency}ms` : "N/A"}
                        </p>
                        <p className="text-xs text-gray-500">Latency</p>
                    </div>

                    <div>
                        <p className="text-xs text-gray-400">Database</p>
                        <p className={`text-lg font-bold mt-1 ${
                            systemHealth.metrics.databaseUsage > 80
                                ? "text-rose-300"
                                : systemHealth.metrics.databaseUsage > 60
                                ? "text-amber-300"
                                : "text-emerald-300"
                        }`}>
                            {systemHealth.metrics.databaseUsage != null ? `${systemHealth.metrics.databaseUsage}%` : "N/A"}
                        </p>
                        <p className="text-xs text-gray-500">Usage</p>
                    </div>

                    <div>
                        <p className="text-xs text-gray-400">Cache</p>
                        <p className={`text-lg font-bold mt-1 ${
                            systemHealth.metrics.cacheHitRate > 80
                                ? "text-emerald-300"
                                : systemHealth.metrics.cacheHitRate > 60
                                ? "text-amber-300"
                                : "text-rose-300"
                        }`}>
                            {systemHealth.metrics.cacheHitRate != null ? `${systemHealth.metrics.cacheHitRate}%` : "N/A"}
                        </p>
                        <p className="text-xs text-gray-500">Hit Rate</p>
                    </div>

                    <div>
                        <p className="text-xs text-gray-400">Message Queue</p>
                        <p className={`text-lg font-bold mt-1 ${
                            systemHealth.metrics.messageQueueBacklog > 100
                                ? "text-rose-300"
                                : systemHealth.metrics.messageQueueBacklog > 50
                                ? "text-amber-300"
                                : "text-emerald-300"
                        }`}>
                            {systemHealth.metrics.messageQueueBacklog != null ? systemHealth.metrics.messageQueueBacklog : "N/A"}
                        </p>
                        <p className="text-xs text-gray-500">Backlog</p>
                    </div>
                </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-2">
                <button
                    onClick={() => navigate("/ai-bots/maintenance-dashboard")}
                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg text-xs font-semibold transition-all"
                >
                    🔧 Repair Issues
                </button>
                <button
                    onClick={performHealthCheck}
                    className="flex-1 border border-white/20 text-gray-300 hover:bg-white/10 py-2 rounded-lg text-xs font-semibold transition-all"
                >
                    🔄 Refresh
                </button>
            </div>

            {systemHealth.errorCount > 0 && (
                <div className={`mt-3 p-3 rounded-lg ${currentStatus.bg} border ${currentStatus.border}`}>
                    <p className={`text-xs ${currentStatus.text}`}>
                        {systemHealth.errorCount} issue{systemHealth.errorCount > 1 ? "s" : ""} detected.{" "}
                        <button
                            onClick={() => navigate("/ai-bots/maintenance-dashboard")}
                            className="underline font-semibold hover:no-underline"
                        >
                            Click to fix
                        </button>
                    </p>
                </div>
            )}
        </div>
    );
};

export default SystemHealthWidget;
