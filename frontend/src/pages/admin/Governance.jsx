import { useEffect, useMemo, useRef, useState, useCallback } from "react";
import governanceClient from "../../api/governanceClient";

function StatusBadge({ status }) {
    const color = useMemo(() => {
        const s = (status || "").toLowerCase();
        if (s === "active") return "bg-green-100 text-green-800";
        if (s === "approved") return "bg-blue-100 text-blue-800";
        if (s === "under_review") return "bg-yellow-100 text-yellow-800";
        return "bg-gray-100 text-gray-800";
    }, [status]);
    return (
        <span className={`px-2 py-1 rounded text-xs font-medium ${color}`}>{status || "unknown"}</span>
    );
}

export default function Governance() {
    const [loading, setLoading] = useState(false);
    const [bots, setBots] = useState([]);
    const [error, setError] = useState("");
    const [envByBot, setEnvByBot] = useState({});
    const [noteByBot, setNoteByBot] = useState({});
    const [wsConnected, setWsConnected] = useState(false);
    const wsRef = useRef(null);

    const load = async () => {
        setLoading(true);
        setError("");
        try {
            const data = await governanceClient.listBots();
            setBots(data?.bots || []);
        } catch (e) {
            setError(e?.normalized?.detail || e?.message || "Failed to load bots");
        } finally {
            setLoading(false);
        }
    };

    const connectWS = useCallback(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) return;
        const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
        const ws = new WebSocket(`${protocol}//${window.location.host}/api/v1/ws/live`);
        ws.onopen = () => {
            setWsConnected(true);
            try {
                ws.send(JSON.stringify({ type: "subscribe", channel: "governance.*" }));
            } catch { }
        };
        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if ((data?.channel || "").startsWith("governance.")) {
                    load();
                }
            } catch {
                // ignore
            }
        };
        ws.onclose = () => {
            setWsConnected(false);
            setTimeout(connectWS, 3000);
        };
        ws.onerror = () => setWsConnected(false);
        wsRef.current = ws;
    }, []);

    useEffect(() => {
        load();
        connectWS();
        return () => {
            if (wsRef.current?.readyState === WebSocket.OPEN) wsRef.current.close();
        };
    }, [connectWS]);

    const onApprove = async (botId) => {
        try {
            await governanceClient.approveBot(botId, { comments: noteByBot[botId] });
            await load();
        } catch (e) {
            setError(e?.normalized?.detail || e?.message || "Approve failed");
        }
    };

    const onActivate = async (botId) => {
        const env = envByBot[botId] || "staging";
        try {
            await governanceClient.activateBot(botId, env);
            await load();
        } catch (e) {
            setError(e?.normalized?.detail || e?.message || "Activate failed");
        }
    };

    return (
        <div className="p-6">
            <div className="flex items-center justify-between mb-4">
                <h1 className="text-xl font-semibold">Bot Governance</h1>
                <button
                    onClick={load}
                    className="px-3 py-1.5 rounded bg-gray-800 text-white hover:bg-gray-900"
                    disabled={loading}
                >
                    Refresh
                </button>
            </div>

            <div className="mb-3 text-xs text-gray-500">WS: {wsConnected ? "connected" : "disconnected"}</div>

            {error && (
                <div className="mb-4 p-3 rounded bg-red-50 text-red-700 border border-red-200">{error}</div>
            )}

            <div className="overflow-x-auto border border-gray-200 rounded">
                <table className="min-w-full text-sm">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-3 py-2 text-left">Bot ID</th>
                            <th className="px-3 py-2 text-left">Name</th>
                            <th className="px-3 py-2 text-left">Status</th>
                            <th className="px-3 py-2 text-left">Approvals</th>
                            <th className="px-3 py-2 text-left">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {bots.map((b) => (
                            <tr key={b.bot_id} className="border-t">
                                <td className="px-3 py-2 font-mono">{b.bot_id}</td>
                                <td className="px-3 py-2">{b.name || "-"}</td>
                                <td className="px-3 py-2"><StatusBadge status={b.status} /></td>
                                <td className="px-3 py-2">{b.approvals}</td>
                                <td className="px-3 py-2">
                                    <div className="flex items-center gap-2">
                                        <input
                                            placeholder="approval note"
                                            className="px-2 py-1 border rounded"
                                            value={noteByBot[b.bot_id] || ""}
                                            onChange={(e) => setNoteByBot((s) => ({ ...s, [b.bot_id]: e.target.value }))}
                                        />
                                        <button
                                            className="px-2 py-1 rounded bg-blue-600 text-white hover:bg-blue-700"
                                            onClick={() => onApprove(b.bot_id)}
                                        >
                                            Approve
                                        </button>

                                        <select
                                            className="px-2 py-1 border rounded"
                                            value={envByBot[b.bot_id] || "staging"}
                                            onChange={(e) => setEnvByBot((s) => ({ ...s, [b.bot_id]: e.target.value }))}
                                        >
                                            <option value="development">development</option>
                                            <option value="staging">staging</option>
                                            <option value="production">production</option>
                                        </select>
                                        <button
                                            className="px-2 py-1 rounded bg-green-600 text-white hover:bg-green-700"
                                            onClick={() => onActivate(b.bot_id)}
                                        >
                                            Activate
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        ))}
                        {!loading && bots.length === 0 && (
                            <tr><td className="px-3 py-6 text-gray-500" colSpan={5}>No bots found</td></tr>
                        )}
                        {loading && (
                            <tr><td className="px-3 py-6 text-gray-500" colSpan={5}>Loading...</td></tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
