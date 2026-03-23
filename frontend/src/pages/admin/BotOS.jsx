import React, { useState, useEffect, useCallback, useRef } from "react";
import axiosClient from "../../api/axiosClient";
import { AlertCircle, Play, Pause, RefreshCw, Send } from "lucide-react";

const BotOSPage = () => {
    const [bots, setBots] = useState([]);
    const [history, setHistory] = useState([]);
    const [stats, setStats] = useState(null);
    const [command, setCommand] = useState("");
    const [loading, setLoading] = useState(false);
    const [wsConnected, setWsConnected] = useState(false);
    const [feedback, setFeedback] = useState(null);
    const wsRef = useRef(null);
    const subscriptionsRef = useRef(new Set());

    // Use central axiosClient which resolves baseURL from VITE_API_BASE_URL or defaults

    const connectWS = useCallback(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) return;

        const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
        const ws = new WebSocket(`${protocol}//${window.location.host}/api/v1/ws/live`);

        ws.onopen = () => {
            setWsConnected(true);
            ws.send(JSON.stringify({ type: "subscribe", channel: "bots.*" }));
            ws.send(JSON.stringify({ type: "subscribe", channel: "commands.*" }));
            subscriptionsRef.current.add("bots.*");
            subscriptionsRef.current.add("commands.*");
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.channel === "bots.run.completed") {
                    refreshBots();
                    refreshHistory();
                } else if (data.channel === "commands.executed") {
                    refreshHistory();
                }
            } catch (e) {
                console.error("WS message parse error:", e);
            }
        };

        ws.onclose = () => {
            setWsConnected(false);
            setTimeout(connectWS, 3000);
        };

        ws.onerror = (error) => {
            console.error("WS error:", error);
            setWsConnected(false);
        };

        wsRef.current = ws;
    }, []);

    const refreshBots = useCallback(async () => {
        try {
            const res = await axiosClient.get("/api/v1/bots");
            setBots(res.data.bots || []);
        } catch (error) {
            console.error("Failed to fetch bots:", error);
        }
    }, []);

    const refreshHistory = useCallback(async () => {
        try {
            const res = await axiosClient.get("/api/v1/bots/history?limit=20");
            setHistory(res.data.runs || []);
        } catch (error) {
            console.error("Failed to fetch history:", error);
        }
    }, []);

    const refreshStats = useCallback(async () => {
        try {
            const res = await axiosClient.get("/api/v1/bots/stats");
            setStats(res.data);
        } catch (error) {
            console.error("Failed to fetch stats:", error);
        }
    }, []);

    useEffect(() => {
        refreshBots();
        refreshHistory();
        refreshStats();
        connectWS();

        return () => {
            if (wsRef.current?.readyState === WebSocket.OPEN) {
                wsRef.current.close();
            }
        };
    }, [refreshBots, refreshHistory, refreshStats, connectWS]);

    const handleCommandSubmit = async (e) => {
        e.preventDefault();
        if (!command.trim()) return;

        setLoading(true);
        try {
            const res = await axiosClient.post(`/api/v1/bots/commands/human`, {
                command: command.trim(),
            });
            setCommand("");
            await refreshHistory();
            setFeedback({
                type: res.data.ok ? "success" : "error",
                message: res.data.ok ? "Command executed successfully." : `Command failed: ${res.data.error}`,
            });
        } catch (error) {
            const detail = error.response?.data?.detail;
            setFeedback({
                type: "error",
                message: `Error: ${typeof detail === "object" ? JSON.stringify(detail) : detail || error.message}`,
            });
        } finally {
            setLoading(false);
        }
    };

    const formatDateTime = (value) => {
        if (!value) return '---';
        const date = new Date(value);
        if (Number.isNaN(date.getTime())) return '---';
        return date.toLocaleString('en-US', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: true,
        });
    };

    const resolveRunFields = (run) => {
        if (!run || typeof run !== 'object') {
            return {
                id: '---',
                botName: '---',
                taskType: '---',
                status: 'unknown',
                startedAt: null,
                finishedAt: null,
                error: null,
            };
        }

        return {
            id: run.id ?? run.run_id ?? run.uuid ?? '---',
            botName: run.bot_name ?? run.bot ?? run.bot_id ?? run.name ?? '---',
            taskType: run.task_type ?? run.task ?? run.action ?? run.command ?? '---',
            status: run.status ?? run.state ?? 'unknown',
            startedAt: run.started_at ?? run.startedAt ?? run.created_at ?? run.createdAt ?? null,
            finishedAt: run.finished_at ?? run.finishedAt ?? run.ended_at ?? run.endedAt ?? null,
            error: run.error ?? run.error_message ?? run.detail ?? null,
        };
    };

    const handleBotAction = async (botName, action) => {
        setLoading(true);
        try {
            const resolvedAction = action === "run" ? "restart" : action;
            await axiosClient.post(`/api/v1/bots/${botName}/${resolvedAction}`, {});
            await refreshBots();
            setFeedback({
                type: "success",
                message: `${resolvedAction} command sent to ${botName}.`,
            });
        } catch (error) {
            setFeedback({
                type: "error",
                message: `Error: ${error.response?.data?.detail || error.message}`,
            });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="glass-page p-6 max-w-7xl mx-auto space-y-6">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
                <div>
                    <h1 className="text-2xl md:text-3xl font-bold">Bot Operating System</h1>
                    <p className="text-xs md:text-sm text-slate-400 mt-1">Monitor and control bot orchestration, automation tasks, and execution history.</p>
                </div>
                <div className="flex gap-2 items-center">
                    <div className={`w-3 h-3 rounded-full ${wsConnected ? "bg-emerald-500" : "bg-rose-500"}`} />
                    <span className="text-xs md:text-sm text-slate-400">{wsConnected ? "WS Connected" : "WS Disconnected"}</span>
                    <button
                        onClick={() => {
                            refreshBots();
                            refreshHistory();
                            refreshStats();
                        }}
                        className="p-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition"
                    >
                        <RefreshCw size={18} />
                    </button>
                </div>
            </div>

            {feedback && (
                <div
                    className={`rounded-lg border px-4 py-3 text-sm flex items-start justify-between gap-3 ${
                        feedback.type === "success"
                            ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-200"
                            : "border-rose-500/30 bg-rose-500/10 text-rose-200"
                    }`}
                >
                    <span>{feedback.message}</span>
                    <button
                        type="button"
                        onClick={() => setFeedback(null)}
                        className="text-current/80 hover:text-current"
                    >
                        Dismiss
                    </button>
                </div>
            )}

            {stats && (
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="glass-card p-4 rounded-lg">
                        <p className="text-xs text-slate-400">Total Runs</p>
                        <p className="text-2xl font-bold text-slate-200 mt-1">{stats.total_runs || 0}</p>
                    </div>
                    <div className="glass-card p-4 rounded-lg">
                        <p className="text-xs text-slate-400">Completed</p>
                        <p className="text-2xl font-bold text-emerald-400 mt-1">{stats.by_status?.completed || 0}</p>
                    </div>
                    <div className="glass-card p-4 rounded-lg">
                        <p className="text-xs text-slate-400">Failed</p>
                        <p className="text-2xl font-bold text-rose-400 mt-1">{stats.by_status?.failed || 0}</p>
                    </div>
                    <div className="glass-card p-4 rounded-lg">
                        <p className="text-xs text-slate-400">Human Commands</p>
                        <p className="text-2xl font-bold text-blue-400 mt-1">{stats.human_commands || 0}</p>
                    </div>
                </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2">
                    <div className="glass-card rounded-lg p-6">
                        <h2 className="text-xl font-bold mb-4">Registered Bots</h2>
                        <div className="space-y-2 max-h-96 overflow-y-auto">
                            {bots.length === 0 ? (
                                <p className="text-slate-500 text-sm">No bots registered</p>
                            ) : (
                                bots.map((bot) => (
                                    <div key={bot.bot_name} className="flex justify-between items-center p-3 bg-slate-700/30 rounded border border-slate-600">
                                        <div className="flex-1">
                                            <p className="font-semibold text-slate-200">{bot.bot_name}</p>
                                            <p className="text-xs text-slate-400">
                                                Level: {bot.automation_level} | Status: {bot.status} | Enabled: {bot.enabled ? "Yes" : "No"}
                                            </p>
                                            {bot.last_run && (
                                                <p className="text-xs text-slate-500">
                                                    Last run: {bot.last_run.status} at {formatDateTime(bot.last_run.started_at)}
                                                </p>
                                            )}
                                        </div>
                                        <div className="flex gap-2">
                                            <button
                                                onClick={() => handleBotAction(bot.bot_name, "pause")}
                                                disabled={loading}
                                                className="p-2 bg-amber-600 hover:bg-amber-700 text-white rounded transition disabled:opacity-50"
                                            >
                                                <Pause size={16} />
                                            </button>
                                            <button
                                                onClick={() => handleBotAction(bot.bot_name, "resume")}
                                                disabled={loading}
                                                className="p-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded transition disabled:opacity-50"
                                            >
                                                <Play size={16} />
                                            </button>
                                            <button
                                                onClick={() => handleBotAction(bot.bot_name, "run")}
                                                disabled={loading}
                                                className="p-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition disabled:opacity-50"
                                            >
                                                <RefreshCw size={16} />
                                            </button>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                </div>

                <div>
                    <div className="glass-card rounded-lg p-6">
                        <h2 className="text-xl font-bold mb-4">Send Command</h2>
                        <form onSubmit={handleCommandSubmit} className="space-y-4">
                            <textarea
                                value={command}
                                onChange={(e) => setCommand(e.target.value)}
                                placeholder='e.g., "run finance_bot" or {"bot":"finance_bot","task":"daily"}'
                                className="w-full p-3 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                                rows={8}
                            />
                            <button
                                type="submit"
                                disabled={loading || !command.trim()}
                                className="w-full bg-blue-600 hover:bg-blue-700 text-white p-2 rounded transition disabled:opacity-50 flex items-center justify-center gap-2"
                            >
                                <Send size={16} /> Submit Command
                            </button>
                        </form>
                    </div>
                </div>
            </div>

            <div className="glass-card rounded-lg p-6">
                <h2 className="text-xl font-bold mb-4 flex items-center justify-between">
                    <span>Recent Execution History</span>
                    <button
                        onClick={refreshHistory}
                        className="text-sm bg-slate-700 hover:bg-slate-600 px-3 py-1 rounded flex items-center gap-2 transition-colors"
                        title="Refresh"
                    >
                        <RefreshCw size={14} /> Refresh
                    </button>
                </h2>
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead>
                            <tr className="border-b border-slate-600">
                                <th className="text-left py-2 px-3 text-slate-300 font-semibold text-xs">ID</th>
                                <th className="text-left py-2 px-3 text-slate-300 font-semibold text-xs">Bot</th>
                                <th className="text-left py-2 px-3 text-slate-300 font-semibold text-xs">Task</th>
                                <th className="text-left py-2 px-3 text-slate-300 font-semibold text-xs">Status</th>
                                <th className="text-left py-2 px-3 text-slate-300 font-semibold text-xs">Started At</th>
                                <th className="text-left py-2 px-3 text-slate-300 font-semibold text-xs">Duration</th>
                                <th className="text-left py-2 px-3 text-slate-300 font-semibold text-xs">Error</th>
                            </tr>
                        </thead>
                        <tbody>
                            {history.length === 0 ? (
                                <tr>
                                    <td colSpan="7" className="text-center py-4 text-slate-500 text-sm">
                                        No runs yet
                                    </td>
                                </tr>
                            ) : (
                                history.map((run) => {
                                    const normalized = resolveRunFields(run);
                                    const startDate = normalized.startedAt ? new Date(normalized.startedAt) : null;
                                    const endDate = normalized.finishedAt ? new Date(normalized.finishedAt) : null;
                                    const duration = startDate && endDate
                                        ? Math.round((endDate - startDate) / 1000) // seconds
                                        : null;

                                    return (
                                        <tr key={run.id} className="border-b border-slate-700 hover:bg-slate-700/30 text-xs">
                                            <td className="py-2 px-3 text-slate-300">{normalized.id}</td>
                                            <td className="py-2 px-3 text-slate-300">{normalized.botName}</td>
                                            <td className="py-2 px-3 text-slate-300">{normalized.taskType}</td>
                                            <td className="py-2 px-3">
                                                <span
                                                    className={`px-2 py-0.5 rounded text-xs font-semibold ${normalized.status === "completed"
                                                        ? "bg-emerald-500/30 text-emerald-200"
                                                        : normalized.status === "failed"
                                                            ? "bg-rose-500/30 text-rose-200"
                                                            : normalized.status === "running"
                                                                ? "bg-blue-500/30 text-blue-200"
                                                                : "bg-amber-500/30 text-amber-200"
                                                        }`}
                                                >
                                                    {normalized.status}
                                                </span>
                                            </td>
                                            <td className="py-2 px-3 text-slate-400 text-xs">
                                                {formatDateTime(normalized.startedAt)}
                                            </td>
                                            <td className="py-2 px-3 text-slate-400 text-xs">
                                                {duration !== null
                                                    ? duration < 60
                                                        ? `${duration}s`
                                                        : `${Math.floor(duration / 60)}m ${duration % 60}s`
                                                    : normalized.status === "running"
                                                        ? "In progress..."
                                                        : '---'
                                                }
                                            </td>
                                            <td className="py-2 px-3 text-rose-400 text-xs">
                                                {normalized.error && (
                                                    <div className="flex items-center gap-1 cursor-help" title={normalized.error}>
                                                        <AlertCircle size={14} />
                                                        <span>{String(normalized.error).substring(0, 20)}...</span>
                                                    </div>
                                                )}
                                            </td>
                                        </tr>
                                    );
                                })
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default BotOSPage;
