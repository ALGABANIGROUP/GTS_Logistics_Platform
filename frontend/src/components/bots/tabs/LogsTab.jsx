/**
 * Logs Tab - Bot Execution Logs & Activity History
 */
import { useState, useEffect, useCallback } from "react";
import axiosClient from "../../../api/axiosClient";

const LOG_LEVELS = {
    info: { color: "text-blue-400", bg: "bg-blue-500/20", icon: "" },
    success: { color: "text-emerald-400", bg: "bg-emerald-500/20", icon: "" },
    warning: { color: "text-amber-400", bg: "bg-amber-500/20", icon: "" },
    error: { color: "text-rose-400", bg: "bg-rose-500/20", icon: "" },
    debug: { color: "text-slate-400", bg: "bg-slate-500/20", icon: "" },
};

export default function LogsTab({
    botKey,
    executionHistory = [],
    onRefresh,
    isPreview = false,
}) {
    const [logs, setLogs] = useState([]);
    const [selectedRun, setSelectedRun] = useState(null);
    const [filter, setFilter] = useState("all");
    const [loading, setLoading] = useState(false);
    const [autoRefresh, setAutoRefresh] = useState(false);

    // Convert execution history to log format
    useEffect(() => {
        const logsFromHistory = executionHistory.map((run, i) => ({
            id: run.id || `run-${i}`,
            timestamp: run.started_at || run.created_at || new Date().toISOString(),
            level: run.status === "success" ? "success" : run.status === "failed" ? "error" : "info",
            message: `Bot execution ${run.status || "completed"}`,
            details: {
                trigger: run.trigger || "manual",
                duration: run.duration_ms ? `${run.duration_ms}ms` : "",
                result: run.result || null,
                error: run.error || null,
            },
        }));
        setLogs(logsFromHistory);
    }, [executionHistory]);

    // Auto-refresh functionality
    useEffect(() => {
        if (!autoRefresh || isPreview) return;
        const interval = setInterval(() => {
            onRefresh?.();
        }, 5000);
        return () => clearInterval(interval);
    }, [autoRefresh, onRefresh, isPreview]);

    const filteredLogs = logs.filter((log) => {
        if (filter === "all") return true;
        return log.level === filter;
    });

    const handleViewDetails = (log) => {
        setSelectedRun(selectedRun?.id === log.id ? null : log);
    };

    const handleClearLogs = () => {
        // Note: This would need a backend endpoint to actually clear logs
        setLogs([]);
    };

    const handleExportLogs = () => {
        const exportData = JSON.stringify(logs, null, 2);
        const blob = new Blob([exportData], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${botKey || "bot"}-logs-${new Date().toISOString().split("T")[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
    };

    return (
        <div className="space-y-4">
            {/* Toolbar */}
            <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                    {/* Filter Dropdown */}
                    <select
                        value={filter}
                        onChange={(e) => setFilter(e.target.value)}
                        className="rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-white focus:border-blue-500 focus:outline-none"
                    >
                        <option value="all">All Levels</option>
                        <option value="success">Success</option>
                        <option value="error">Errors</option>
                        <option value="warning">Warnings</option>
                        <option value="info">Info</option>
                    </select>

                    {/* Auto-refresh Toggle */}
                    <button
                        onClick={() => setAutoRefresh(!autoRefresh)}
                        disabled={isPreview}
                        className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium transition ${autoRefresh
                                ? "bg-blue-500/20 text-blue-300"
                                : "bg-white/5 text-slate-400 hover:bg-white/10"
                            } ${isPreview ? "cursor-not-allowed opacity-50" : ""}`}
                    >
                        <span className={autoRefresh ? "animate-spin" : ""}></span>
                        {autoRefresh ? "Auto-refresh ON" : "Auto-refresh"}
                    </button>
                </div>

                <div className="flex items-center gap-2">
                    <button
                        onClick={onRefresh}
                        disabled={loading || isPreview}
                        className="rounded-lg bg-white/5 px-3 py-1.5 text-xs font-medium text-slate-300 transition hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                        Refresh
                    </button>
                    <button
                        onClick={handleExportLogs}
                        disabled={logs.length === 0}
                        className="rounded-lg bg-white/5 px-3 py-1.5 text-xs font-medium text-slate-300 transition hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                         Export
                    </button>
                </div>
            </div>

            {/* Log Stats */}
            <div className="grid grid-cols-4 gap-2">
                {Object.entries({
                    all: logs.length,
                    success: logs.filter((l) => l.level === "success").length,
                    error: logs.filter((l) => l.level === "error").length,
                    warning: logs.filter((l) => l.level === "warning").length,
                }).map(([key, count]) => (
                    <button
                        key={key}
                        onClick={() => setFilter(key)}
                        className={`rounded-lg p-2 text-center transition ${filter === key
                                ? "bg-white/10 ring-1 ring-white/20"
                                : "bg-white/5 hover:bg-white/10"
                            }`}
                    >
                        <div className="text-lg font-bold text-white">{count}</div>
                        <div className="text-xs capitalize text-slate-400">{key}</div>
                    </button>
                ))}
            </div>

            {/* Logs List */}
            <div className="rounded-xl border border-white/10 bg-white/5">
                {filteredLogs.length > 0 ? (
                    <div className="divide-y divide-white/5">
                        {filteredLogs.map((log) => {
                            const levelConfig = LOG_LEVELS[log.level] || LOG_LEVELS.info;
                            const isExpanded = selectedRun?.id === log.id;

                            return (
                                <div key={log.id} className="p-3">
                                    <button
                                        onClick={() => handleViewDetails(log)}
                                        className="flex w-full items-start gap-3 text-left"
                                    >
                                        {/* Level Icon */}
                                        <span
                                            className={`mt-0.5 flex h-6 w-6 items-center justify-center rounded-full text-xs ${levelConfig.bg}`}
                                        >
                                            {levelConfig.icon}
                                        </span>

                                        {/* Content */}
                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-center gap-2">
                                                <span className={`text-sm font-medium ${levelConfig.color}`}>
                                                    {log.message}
                                                </span>
                                                {log.details?.trigger && (
                                                    <span className="rounded-full bg-white/10 px-2 py-0.5 text-xs text-slate-400">
                                                        {log.details.trigger}
                                                    </span>
                                                )}
                                            </div>
                                            <div className="mt-0.5 flex items-center gap-3 text-xs text-slate-500">
                                                <span>
                                                    {new Date(log.timestamp).toLocaleString()}
                                                </span>
                                                {log.details?.duration && (
                                                    <span>Duration: {log.details.duration}</span>
                                                )}
                                            </div>
                                        </div>

                                        {/* Expand Icon */}
                                        <span className="text-slate-500">
                                            {isExpanded ? "" : ""}
                                        </span>
                                    </button>

                                    {/* Expanded Details */}
                                    {isExpanded && log.details && (
                                        <div className="mt-3 ml-9 rounded-lg bg-slate-900/50 p-3">
                                            <pre className="text-xs text-slate-400 overflow-x-auto">
                                                {JSON.stringify(log.details, null, 2)}
                                            </pre>
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                ) : (
                    <div className="p-12 text-center">
                        <div className="text-3xl"></div>
                        <p className="mt-2 text-sm text-slate-400">No logs to display</p>
                        {!isPreview && (
                            <button
                                onClick={onRefresh}
                                className="mt-4 rounded-lg bg-white/10 px-4 py-2 text-xs font-medium text-slate-300 transition hover:bg-white/20"
                            >
                                Refresh Logs
                            </button>
                        )}
                    </div>
                )}
            </div>

            {/* Log Stream (scaffold for WebSocket) */}
            {!isPreview && autoRefresh && (
                <div className="rounded-lg border border-blue-500/30 bg-blue-500/10 p-3 text-center text-xs text-blue-200">
                     Live updates enabled - refreshing every 5 seconds
                </div>
            )}
        </div>
    );
}
