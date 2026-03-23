/**
 * Status Bar Component
 * Bottom status bar showing real-time bot information
 */
export default function StatusBar({
    botKey,
    status,
    lastExecution,
    lastRefresh,
    isPreview = false,
}) {
    const formatTime = (date) => {
        if (!date) return "";
        const d = typeof date === "string" ? new Date(date) : date;
        return d.toLocaleString();
    };

    return (
        <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-700/50 bg-gradient-to-r from-slate-900/80 via-slate-800/80 to-slate-900/80 px-4 py-3 text-xs text-slate-400 backdrop-blur-xl shadow-lg">
            <div className="flex items-center gap-4">
                {/* Connection Status */}
                <div className="flex items-center gap-1.5">
                    <div
                        className={`h-2 w-2 rounded-full ${isPreview
                            ? "bg-amber-500"
                            : status === "active"
                                ? "bg-emerald-500"
                                : "bg-slate-500"
                            }`}
                    />
                    <span>{isPreview ? "Preview Mode" : status === "active" ? "Connected" : "Offline"}</span>
                </div>

                {/* Bot ID */}
                <div className="hidden sm:flex items-center gap-1">
                    <span className="text-slate-500">Bot:</span>
                    <span className="font-mono text-slate-300">{botKey || ""}</span>
                </div>
            </div>

            <div className="flex items-center gap-4">
                {/* Last Execution */}
                {lastExecution && (
                    <div className="flex items-center gap-1">
                        <span className="text-slate-500">Last run:</span>
                        <span className="text-slate-300">
                            {formatTime(lastExecution.started_at)}
                        </span>
                        <span
                            className={`ml-1 ${lastExecution.status === "success"
                                ? "text-emerald-400"
                                : lastExecution.status === "failed"
                                    ? "text-rose-400"
                                    : "text-slate-400"
                                }`}
                        >
                            ({lastExecution.status || "unknown"})
                        </span>
                    </div>
                )}

                {/* Last Refresh */}
                <div className="flex items-center gap-1">
                    <span className="text-slate-500">Refreshed:</span>
                    <span className="text-slate-300">
                        {lastRefresh ? formatTime(lastRefresh) : ""}
                    </span>
                </div>
            </div>
        </div>
    );
}
