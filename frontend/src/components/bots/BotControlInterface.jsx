/**
 * Advanced Bot Control Interface - Main Component
 * Comprehensive control system for all AI bots
 */
import { useState, useEffect, useCallback } from "react";
import axiosClient from "../../api/axiosClient";
import BotHeader from "./BotHeader";
import BotTabs from "./BotTabs";
import DashboardTab from "./tabs/DashboardTab";
import ExecuteTab from "./tabs/ExecuteTab";
import ScheduleTab from "./tabs/ScheduleTab";
import AnalyticsTab from "./tabs/AnalyticsTab";
import ConfigTab from "./tabs/ConfigTab";
import LogsTab from "./tabs/LogsTab";
import StatusBar from "./StatusBar";

const getErrorMessage = (error, fallback) => {
    return (
        error?.normalized?.detail ||
        error?.response?.data?.detail ||
        error?.response?.data?.error ||
        error?.message ||
        fallback
    );
};

export default function BotControlInterface({
    botKey,
    botConfig = {},
    mode = "active",
}) {
    const [activeTab, setActiveTab] = useState("dashboard");
    const [loading, setLoading] = useState(true);
    const [botData, setBotData] = useState(null);
    const [statusData, setStatusData] = useState(null);
    const [configData, setConfigData] = useState(null);
    const [executionHistory, setExecutionHistory] = useState([]);
    const [error, setError] = useState(null);
    const [lastRefresh, setLastRefresh] = useState(null);

    const isPreview = mode === "preview";

    // Load bot status
    const loadStatus = useCallback(async () => {
        if (isPreview || !botKey) return;
        try {
            const res = await axiosClient.get(
                `/api/v1/ai/bots/available/${encodeURIComponent(botKey)}/status`
            );
            setStatusData(res?.data || null);
        } catch (err) {
            console.warn("Status load failed:", err);
        }
    }, [botKey, isPreview]);

    // Load bot config
    const loadConfig = useCallback(async () => {
        if (isPreview || !botKey) return;
        try {
            const res = await axiosClient.get(
                `/api/v1/ai/bots/available/${encodeURIComponent(botKey)}/config`
            );
            setConfigData(res?.data?.config || res?.data || null);
        } catch (err) {
            console.warn("Config load failed:", err);
        }
    }, [botKey, isPreview]);

    // Load execution history from BOS
    const loadHistory = useCallback(async () => {
        if (isPreview) return;
        try {
            const res = await axiosClient.get("/api/v1/bots/history", {
                params: { limit: 20 },
            });
            const runs = res?.data?.runs || [];
            // Filter by bot if needed
            const filtered = botKey
                ? runs.filter((r) => r.bot_name === botKey)
                : runs;
            setExecutionHistory(filtered.slice(0, 10));
        } catch (err) {
            console.warn("History load failed:", err);
        }
    }, [botKey, isPreview]);

    // Refresh all data
    const refreshAll = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            await Promise.all([loadStatus(), loadConfig(), loadHistory()]);
            setLastRefresh(new Date());
        } catch (err) {
            setError(getErrorMessage(err, "Failed to load bot data"));
        } finally {
            setLoading(false);
        }
    }, [loadStatus, loadConfig, loadHistory]);

    useEffect(() => {
        refreshAll();
    }, [refreshAll]);

    // Execute bot
    const executeBot = async (payload = {}) => {
        if (isPreview || !botKey) return { ok: false, error: "Preview mode" };
        try {
            const res = await axiosClient.post(
                `/api/v1/ai/bots/available/${encodeURIComponent(botKey)}/run`,
                {
                    message: payload.message || "run",
                    context: payload.context || {},
                    meta: { source: "bot_control_ui", ...payload.meta },
                }
            );
            await loadHistory();
            return { ok: true, data: res?.data };
        } catch (err) {
            return { ok: false, error: getErrorMessage(err, "Execution failed") };
        }
    };

    // Build bot info from status/config
    const botInfo = {
        name: botConfig.displayName || configData?.display_name || botKey,
        type: botConfig.type || configData?.mode || "AI Bot",
        status: statusData?.status?.is_active !== false ? "active" : "inactive",
        lastExecuted: executionHistory[0]?.started_at || null,
        efficiencyScore: statusData?.status?.efficiency || "N/A",
        version: configData?.version || "1.0.0",
    };

    const tabs = [
        { id: "dashboard", name: "Dashboard", icon: "" },
        { id: "execute", name: "Execute", icon: "" },
        { id: "schedule", name: "Schedule", icon: "" },
        { id: "analytics", name: "Analytics", icon: "" },
        { id: "config", name: "Config", icon: "" },
        { id: "logs", name: "Logs", icon: "" },
    ];

    const renderTabContent = () => {
        switch (activeTab) {
            case "dashboard":
                return (
                    <DashboardTab
                        botKey={botKey}
                        botConfig={botConfig}
                        statusData={statusData}
                        configData={configData}
                        onRefresh={refreshAll}
                        isPreview={isPreview}
                    />
                );
            case "execute":
                return (
                    <ExecuteTab
                        botKey={botKey}
                        botConfig={botConfig}
                        onExecute={executeBot}
                        isPreview={isPreview}
                    />
                );
            case "schedule":
                return (
                    <ScheduleTab
                        botKey={botKey}
                        botConfig={botConfig}
                        isPreview={isPreview}
                    />
                );
            case "analytics":
                return (
                    <AnalyticsTab
                        botKey={botKey}
                        executionHistory={executionHistory}
                        isPreview={isPreview}
                    />
                );
            case "config":
                return (
                    <ConfigTab
                        botKey={botKey}
                        configData={configData}
                        onRefresh={loadConfig}
                        isPreview={isPreview}
                    />
                );
            case "logs":
                return (
                    <LogsTab
                        botKey={botKey}
                        executionHistory={executionHistory}
                        onRefresh={loadHistory}
                        isPreview={isPreview}
                    />
                );
            default:
                return null;
        }
    };

    return (
        <div className="space-y-4">
            {/* Preview Mode Banner */}
            {isPreview && (
                <div className="rounded-xl border border-amber-700/50 bg-gradient-to-br from-amber-900/40 via-amber-800/30 to-amber-900/40 px-4 py-3 backdrop-blur-xl">
                    <div className="flex items-center gap-2">
                        <span className="text-amber-400"></span>
                        <span className="text-sm font-semibold text-amber-100">
                            Intelligence Mode
                        </span>
                    </div>
                    <p className="mt-1 text-xs text-amber-100/80">
                        Backend execution is not active. You can view metrics and configuration but cannot execute tasks.
                    </p>
                </div>
            )}

            {/* Bot Header */}
            <BotHeader
                botInfo={botInfo}
                onRefresh={refreshAll}
                onExecute={() => executeBot({ message: "run" })}
                loading={loading}
                isPreview={isPreview}
            />

            {/* Main Content */}
            <div className="rounded-2xl border border-slate-700/50 bg-gradient-to-br from-slate-900/95 via-slate-800/95 to-slate-900/95 backdrop-blur-xl shadow-2xl">
                {/* Tabs */}
                <BotTabs
                    tabs={tabs}
                    activeTab={activeTab}
                    onTabChange={setActiveTab}
                />

                {/* Tab Content */}
                <div className="p-6">
                    {loading ? (
                        <div className="flex items-center justify-center py-12">
                            <div className="text-sm text-slate-400">Loading bot data...</div>
                        </div>
                    ) : error ? (
                        <div className="rounded-lg border border-rose-700/50 bg-gradient-to-br from-rose-900/30 via-rose-800/20 to-rose-900/30 p-4 text-center backdrop-blur">
                            <p className="text-sm text-rose-200">{error}</p>
                            <button
                                onClick={refreshAll}
                                className="mt-3 rounded-lg border border-rose-700/40 bg-rose-900/40 px-4 py-2 text-xs font-semibold text-rose-100 hover:bg-rose-900/60 backdrop-blur"
                            >
                                Retry
                            </button>
                        </div>
                    ) : (
                        renderTabContent()
                    )}
                </div>
            </div>

            {/* Status Bar */}
            <StatusBar
                botKey={botKey}
                status={botInfo.status}
                lastExecution={executionHistory[0]}
                lastRefresh={lastRefresh}
                isPreview={isPreview}
            />
        </div>
    );
}
