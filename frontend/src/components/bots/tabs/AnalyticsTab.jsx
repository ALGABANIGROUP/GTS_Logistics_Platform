/**
 * Analytics Tab - Bot Performance Analytics & Insights
 */
import { useMemo } from "react";

export default function AnalyticsTab({
    botKey,
    executionHistory = [],
    isPreview = false,
}) {
    // Calculate analytics from execution history
    const analytics = useMemo(() => {
        if (!executionHistory.length) {
            return {
                totalRuns: 0,
                successRate: 0,
                avgDuration: 0,
                successCount: 0,
                failedCount: 0,
                recentTrend: "stable",
            };
        }

        const successCount = executionHistory.filter(
            (r) => r.status === "success"
        ).length;
        const failedCount = executionHistory.filter(
            (r) => r.status === "failed"
        ).length;
        const totalRuns = executionHistory.length;
        const successRate =
            totalRuns > 0 ? Math.round((successCount / totalRuns) * 100) : 0;

        // Calculate average duration
        const durations = executionHistory
            .filter((r) => r.duration_ms)
            .map((r) => r.duration_ms);
        const avgDuration =
            durations.length > 0
                ? Math.round(durations.reduce((a, b) => a + b, 0) / durations.length)
                : 0;

        // Determine trend (simplified)
        const recentSuccess = executionHistory
            .slice(0, 3)
            .filter((r) => r.status === "success").length;
        const recentTrend = recentSuccess >= 2 ? "up" : recentSuccess === 0 ? "down" : "stable";

        return {
            totalRuns,
            successRate,
            avgDuration,
            successCount,
            failedCount,
            recentTrend,
        };
    }, [executionHistory]);

    // Group executions by day for chart
    const dailyStats = useMemo(() => {
        const days = {};
        executionHistory.forEach((run) => {
            if (!run.started_at) return;
            const date = new Date(run.started_at).toLocaleDateString();
            if (!days[date]) {
                days[date] = { success: 0, failed: 0, total: 0 };
            }
            days[date].total++;
            if (run.status === "success") days[date].success++;
            if (run.status === "failed") days[date].failed++;
        });
        return Object.entries(days)
            .slice(0, 7)
            .reverse()
            .map(([date, stats]) => ({ date, ...stats }));
    }, [executionHistory]);

    return (
        <div className="space-y-6">
            {/* Stats Overview */}
            <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
                <StatCard
                    label="Total Runs"
                    value={analytics.totalRuns}
                    icon=""
                    color="blue"
                />
                <StatCard
                    label="Success Rate"
                    value={`${analytics.successRate}%`}
                    icon=""
                    color={analytics.successRate >= 80 ? "green" : analytics.successRate >= 50 ? "yellow" : "red"}
                />
                <StatCard
                    label="Avg Duration"
                    value={`${analytics.avgDuration}ms`}
                    icon=""
                    color="purple"
                />
                <StatCard
                    label="Trend"
                    value={analytics.recentTrend === "up" ? " Improving" : analytics.recentTrend === "down" ? " Declining" : " Stable"}
                    icon=""
                    color={analytics.recentTrend === "up" ? "green" : analytics.recentTrend === "down" ? "red" : "slate"}
                />
            </div>

            {/* Performance Chart (Simplified) */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-4">
                <h3 className="mb-4 text-sm font-semibold text-white">
                     Daily Performance
                </h3>
                {dailyStats.length > 0 ? (
                    <div className="space-y-3">
                        {dailyStats.map((day) => (
                            <div key={day.date} className="flex items-center gap-3">
                                <span className="w-20 text-xs text-slate-400">{day.date}</span>
                                <div className="flex-1">
                                    <div className="flex h-6 overflow-hidden rounded-full bg-slate-800">
                                        {day.success > 0 && (
                                            <div
                                                className="bg-emerald-500"
                                                style={{
                                                    width: `${(day.success / day.total) * 100}%`,
                                                }}
                                            />
                                        )}
                                        {day.failed > 0 && (
                                            <div
                                                className="bg-rose-500"
                                                style={{
                                                    width: `${(day.failed / day.total) * 100}%`,
                                                }}
                                            />
                                        )}
                                    </div>
                                </div>
                                <span className="w-16 text-right text-xs text-slate-400">
                                    {day.success}/{day.total}
                                </span>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="rounded-lg bg-white/5 p-8 text-center text-sm text-slate-500">
                        No execution data available
                    </div>
                )}
            </div>

            {/* Success/Failure Breakdown */}
            <div className="grid gap-4 lg:grid-cols-2">
                <div className="rounded-xl border border-white/10 bg-white/5 p-4">
                    <h3 className="mb-3 text-sm font-semibold text-white">
                         Successful Runs
                    </h3>
                    <div className="text-3xl font-bold text-emerald-400">
                        {analytics.successCount}
                    </div>
                    <div className="mt-1 text-xs text-slate-400">
                        {analytics.totalRuns > 0
                            ? `${Math.round((analytics.successCount / analytics.totalRuns) * 100)}% of total`
                            : "No data"}
                    </div>
                </div>
                <div className="rounded-xl border border-white/10 bg-white/5 p-4">
                    <h3 className="mb-3 text-sm font-semibold text-white">
                         Failed Runs
                    </h3>
                    <div className="text-3xl font-bold text-rose-400">
                        {analytics.failedCount}
                    </div>
                    <div className="mt-1 text-xs text-slate-400">
                        {analytics.totalRuns > 0
                            ? `${Math.round((analytics.failedCount / analytics.totalRuns) * 100)}% of total`
                            : "No data"}
                    </div>
                </div>
            </div>

            {/* Recent Executions Table */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-4">
                <h3 className="mb-3 text-sm font-semibold text-white">
                     Recent Executions
                </h3>
                {executionHistory.length > 0 ? (
                    <div className="overflow-x-auto">
                        <table className="w-full text-xs">
                            <thead>
                                <tr className="border-b border-white/10 text-left text-slate-400">
                                    <th className="pb-2 pr-4">Time</th>
                                    <th className="pb-2 pr-4">Status</th>
                                    <th className="pb-2 pr-4">Duration</th>
                                    <th className="pb-2">Trigger</th>
                                </tr>
                            </thead>
                            <tbody>
                                {executionHistory.slice(0, 10).map((run, i) => (
                                    <tr
                                        key={run.id || i}
                                        className="border-b border-white/5 text-slate-300"
                                    >
                                        <td className="py-2 pr-4">
                                            {run.started_at
                                                ? new Date(run.started_at).toLocaleString()
                                                : ""}
                                        </td>
                                        <td className="py-2 pr-4">
                                            <span
                                                className={`rounded-full px-2 py-0.5 text-xs ${run.status === "success"
                                                        ? "bg-emerald-500/20 text-emerald-300"
                                                        : run.status === "failed"
                                                            ? "bg-rose-500/20 text-rose-300"
                                                            : "bg-slate-500/20 text-slate-300"
                                                    }`}
                                            >
                                                {run.status || "unknown"}
                                            </span>
                                        </td>
                                        <td className="py-2 pr-4">{run.duration_ms || ""}ms</td>
                                        <td className="py-2">{run.trigger || "manual"}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                ) : (
                    <div className="text-center text-sm text-slate-500">
                        No execution history available
                    </div>
                )}
            </div>
        </div>
    );
}

function StatCard({ label, value, icon, color = "blue" }) {
    const colorClasses = {
        blue: "from-blue-500/20 to-blue-600/10 border-blue-500/30",
        green: "from-emerald-500/20 to-emerald-600/10 border-emerald-500/30",
        red: "from-rose-500/20 to-rose-600/10 border-rose-500/30",
        yellow: "from-amber-500/20 to-amber-600/10 border-amber-500/30",
        purple: "from-purple-500/20 to-purple-600/10 border-purple-500/30",
        slate: "from-slate-500/20 to-slate-600/10 border-slate-500/30",
    };

    return (
        <div
            className={`rounded-xl border bg-gradient-to-br p-4 ${colorClasses[color]}`}
        >
            <div className="flex items-center gap-2 text-slate-400">
                <span className="text-lg">{icon}</span>
                <span className="text-xs font-medium">{label}</span>
            </div>
            <div className="mt-2 text-xl font-bold text-white">{value}</div>
        </div>
    );
}
