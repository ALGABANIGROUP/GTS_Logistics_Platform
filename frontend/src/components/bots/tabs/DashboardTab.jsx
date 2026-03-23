/**
 * Dashboard Tab - Bot Overview & Metrics
 */
import { useState, useEffect } from "react";

export default function DashboardTab({
    botKey,
    botConfig = {},
    statusData,
    configData,
    onRefresh,
    isPreview = false,
}) {
    // Extract metrics from status/config
    const metrics = statusData?.status?.metrics || statusData?.metrics || {};
    const capabilities = configData?.capabilities || botConfig.capabilities || [];

    return (
        <div className="space-y-6">
            {/* Quick Stats */}
            <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
                <MetricCard
                    title="Tasks Today"
                    value={metrics.tasks_today || "0"}
                    trend="+12%"
                    trendUp={true}
                    icon=""
                />
                <MetricCard
                    title="Success Rate"
                    value={metrics.success_rate || "N/A"}
                    trend={metrics.success_trend || "stable"}
                    trendUp={true}
                    icon=""
                />
                <MetricCard
                    title="Avg Response"
                    value={metrics.avg_response || "< 1s"}
                    trend="-8%"
                    trendUp={true}
                    icon=""
                />
                <MetricCard
                    title="Active Tasks"
                    value={metrics.active_tasks || "0"}
                    icon=""
                />
            </div>

            {/* Main Content Grid */}
            <div className="grid gap-6 lg:grid-cols-3">
                {/* Status Panel */}
                <div className="rounded-xl border border-slate-700/50 bg-gradient-to-br from-slate-900/90 via-slate-800/90 to-slate-900/90 p-5 lg:col-span-2 backdrop-blur-xl">
                    <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold text-white">
                        <span></span> Bot Status
                    </h3>
                    <div className="space-y-3">
                        <StatusRow
                            label="Operational Status"
                            value={statusData?.status?.is_active !== false ? "Online" : "Offline"}
                            good={statusData?.status?.is_active !== false}
                        />
                        <StatusRow
                            label="Mode"
                            value={configData?.mode || botConfig.mode || "Standard"}
                        />
                        <StatusRow
                            label="Automation Level"
                            value={configData?.automation_level || "Semi-Auto"}
                        />
                        <StatusRow
                            label="Priority"
                            value={configData?.priority || "Normal"}
                        />
                        {isPreview && (
                            <StatusRow
                                label="Backend Status"
                                value="Not Activated"
                                good={false}
                            />
                        )}
                    </div>
                </div>

                {/* Capabilities */}
                <div className="rounded-xl border border-slate-700/50 bg-gradient-to-br from-slate-900/90 via-slate-800/90 to-slate-900/90 p-5 backdrop-blur-xl">
                    <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold text-white">
                        <span></span> Capabilities
                    </h3>
                    <div className="space-y-2">
                        {capabilities.length > 0 ? (
                            capabilities.map((cap, i) => (
                                <div
                                    key={i}
                                    className="flex items-center gap-2 rounded-lg border border-slate-700/30 bg-slate-800/40 px-3 py-2 text-xs text-slate-300 backdrop-blur"
                                >
                                    <span className="text-emerald-400"></span>
                                    {cap}
                                </div>
                            ))
                        ) : (
                            <div className="text-xs text-slate-500">
                                No capabilities defined
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Activity Timeline */}
            <div className="rounded-xl border border-slate-700/50 bg-gradient-to-br from-slate-900/90 via-slate-800/90 to-slate-900/90 p-5 backdrop-blur-xl">
                <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold text-white">
                    <span></span> Recent Activity
                </h3>
                <div className="space-y-3">
                    {statusData?.recent_activity?.length > 0 ? (
                        statusData.recent_activity.slice(0, 5).map((activity, i) => (
                            <ActivityRow key={i} activity={activity} />
                        ))
                    ) : (
                        <div className="rounded-lg border border-slate-700/30 bg-slate-800/40 p-4 text-center text-xs text-slate-500 backdrop-blur">
                            No recent activity recorded
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

function MetricCard({ title, value, trend, trendUp, icon }) {
    return (
        <div className="rounded-xl border border-slate-700/50 bg-gradient-to-br from-slate-900/80 via-slate-800/80 to-slate-900/80 p-4 backdrop-blur-xl shadow-lg">
            <div className="flex items-center justify-between">
                <span className="text-2xl">{icon}</span>
                {trend && (
                    <span
                        className={`text-xs font-medium ${trendUp ? "text-emerald-400" : "text-rose-400"
                            }`}
                    >
                        {trend}
                    </span>
                )}
            </div>
            <div className="mt-2 text-2xl font-bold text-white">{value}</div>
            <div className="text-xs text-slate-400">{title}</div>
        </div>
    );
}

function StatusRow({ label, value, good }) {
    return (
        <div className="flex items-center justify-between rounded-lg border border-slate-700/30 bg-slate-800/40 px-3 py-2 backdrop-blur">
            <span className="text-xs text-slate-400">{label}</span>
            <span
                className={`text-xs font-medium ${good === true
                    ? "text-emerald-400"
                    : good === false
                        ? "text-rose-400"
                        : "text-white"
                    }`}
            >
                {value}
            </span>
        </div>
    );
}

function ActivityRow({ activity }) {
    const icons = {
        success: "",
        error: "",
        warning: "",
        info: "",
    };

    return (
        <div className="flex items-start gap-3 rounded-lg border border-slate-700/30 bg-slate-800/40 p-3 backdrop-blur">
            <span className="text-base">{icons[activity.type] || ""}</span>
            <div className="flex-1">
                <p className="text-xs text-white">{activity.message || activity.action}</p>
                <p className="text-xs text-slate-500">
                    {activity.timestamp
                        ? new Date(activity.timestamp).toLocaleString()
                        : "Unknown time"}
                </p>
            </div>
        </div>
    );
}
