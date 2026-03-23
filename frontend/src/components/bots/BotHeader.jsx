/**
 * Bot Header Component
 * Displays bot identity, status, and primary actions
 */
import { useState } from "react";

const statusColors = {
    active: "bg-emerald-500",
    inactive: "bg-slate-500",
    running: "bg-blue-500 animate-pulse",
    error: "bg-rose-500",
    preview: "bg-amber-500",
};

const statusLabels = {
    active: "Active",
    inactive: "Inactive",
    running: "Running",
    error: "Error",
    preview: "Preview",
};

export default function BotHeader({
    botInfo,
    onRefresh,
    onExecute,
    loading = false,
    isPreview = false,
}) {
    const [executing, setExecuting] = useState(false);

    const handleExecute = async () => {
        if (isPreview || executing) return;
        setExecuting(true);
        try {
            await onExecute?.();
        } finally {
            setExecuting(false);
        }
    };

    const status = isPreview ? "preview" : botInfo?.status || "inactive";

    return (
        <div className="rounded-2xl border border-slate-700/50 bg-gradient-to-br from-slate-900/95 via-slate-800/95 to-slate-900/95 p-6 backdrop-blur-xl shadow-2xl">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                {/* Bot Identity */}
                <div className="flex items-center gap-4">
                    {/* Status Indicator */}
                    <div className="relative">
                        <div
                            className={`h-12 w-12 rounded-xl ${statusColors[status]} flex items-center justify-center text-2xl shadow-lg`}
                        >
                            
                        </div>
                        <div
                            className={`absolute -bottom-1 -right-1 h-4 w-4 rounded-full border-2 border-slate-900 ${statusColors[status]}`}
                        />
                    </div>

                    {/* Bot Info */}
                    <div>
                        <h1 className="text-xl font-bold text-white">
                            {botInfo?.name || "AI Bot"}
                        </h1>
                        <div className="flex flex-wrap items-center gap-2 mt-1">
                            <span className="rounded-full bg-white/10 px-2 py-0.5 text-xs font-medium text-slate-300">
                                {botInfo?.type || "Bot"}
                            </span>
                            <span
                                className={`rounded-full px-2 py-0.5 text-xs font-semibold ${status === "active"
                                    ? "bg-emerald-500/20 text-emerald-300"
                                    : status === "preview"
                                        ? "bg-amber-500/20 text-amber-300"
                                        : "bg-slate-500/20 text-slate-300"
                                    }`}
                            >
                                {statusLabels[status]}
                            </span>
                            {botInfo?.version && (
                                <span className="text-xs text-slate-500">
                                    v{botInfo.version}
                                </span>
                            )}
                        </div>
                    </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2">
                    {/* Refresh Button */}
                    <button
                        onClick={onRefresh}
                        disabled={loading}
                        className="flex items-center gap-1.5 rounded-lg border border-slate-700/50 bg-slate-800/40 px-3 py-2 text-sm font-medium text-slate-300 transition hover:bg-slate-800/60 backdrop-blur disabled:opacity-50"
                    >
                        <span className={loading ? "animate-spin" : ""}></span>
                        Refresh
                    </button>

                    {/* Execute Button */}
                    <button
                        onClick={handleExecute}
                        disabled={isPreview || executing}
                        className={`flex items-center gap-1.5 rounded-lg px-4 py-2 text-sm font-semibold transition backdrop-blur ${isPreview
                            ? "bg-slate-700/50 text-slate-400 cursor-not-allowed"
                            : executing
                                ? "bg-blue-900/60 text-blue-200 cursor-wait"
                                : "bg-gradient-to-r from-blue-600/80 to-indigo-600/80 text-white shadow-lg shadow-blue-500/20 hover:shadow-blue-500/40"
                            }`}
                    >
                        <span>{executing ? "" : ""}</span>
                        {executing ? "Running..." : "Execute"}
                    </button>
                </div>
            </div>

            {/* Stats Row */}
            <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
                <StatBox
                    label="Efficiency"
                    value={botInfo?.efficiencyScore || ""}
                    icon=""
                />
                <StatBox
                    label="Last Run"
                    value={
                        botInfo?.lastExecuted
                            ? new Date(botInfo.lastExecuted).toLocaleTimeString()
                            : "Never"
                    }
                    icon=""
                />
                <StatBox label="Type" value={botInfo?.type || "Bot"} icon="" />
                <StatBox
                    label="Status"
                    value={statusLabels[status]}
                    icon={status === "active" ? "" : status === "preview" ? "" : ""}
                />
            </div>
        </div>
    );
}

function StatBox({ label, value, icon }) {
    return (
        <div className="rounded-xl border border-slate-700/30 bg-slate-800/40 p-3 backdrop-blur">
            <div className="flex items-center gap-2 text-slate-400">
                <span className="text-base">{icon}</span>
                <span className="text-xs font-medium">{label}</span>
            </div>
            <div className="mt-1 truncate text-sm font-semibold text-white">
                {value}
            </div>
        </div>
    );
}
