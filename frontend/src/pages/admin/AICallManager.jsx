import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import axiosClient from "../../api/axiosClient";
import { API_BASE_URL } from "../../config/env";

function buildCallsWsUrl() {
  try {
    if (API_BASE_URL) {
      const u = new URL(API_BASE_URL);
      const proto = u.protocol === "https:" ? "wss" : "ws";
      return `${proto}://${u.host}/api/v1/ws/live`;
    }
  } catch {
    // ignore
  }
  if (typeof window !== "undefined" && window.location?.host) {
    const proto = window.location.protocol === "https:" ? "wss" : "ws";
    return `${proto}://${window.location.host}/api/v1/ws/live`;
  }
  return "ws://127.0.0.1:8000/api/v1/ws/live";
}

function normalizeCallPayload(msg) {
  const payload = msg.payload || msg;
  return {
    callId: payload.call_id || payload.id || payload.callId || "",
    direction: payload.direction || "",
    customer: payload.customer_name || payload.customer || payload.from || payload.to || "Unknown",
    event: payload.event || payload.status || msg.channel || "",
    summary: payload.summary || payload.reason || payload.message || payload.last_event || "",
    timestamp: payload.ts || payload.timestamp || new Date().toISOString(),
  };
}

export default function AICallManager() {
  const [logs, setLogs] = useState([]);
  const [recent, setRecent] = useState([]);
  const [connected, setConnected] = useState(false);
  const [status, setStatus] = useState("Waiting for updates...");
  const [recentStatus, setRecentStatus] = useState("");
  const wsUrl = useMemo(buildCallsWsUrl, []);
  const wsRef = useRef(null);
  const retryRef = useRef(0);
  const retryTimerRef = useRef(null);

  const fetchRecent = useCallback(async () => {
    try {
      const res = await axiosClient.get("/api/v1/ai-calls/recent?limit=50");
      setRecent(Array.isArray(res.data) ? res.data : []);
      setRecentStatus("");
    } catch (err) {
      if (err?.response?.status === 404) {
        setRecent([]);
        setRecentStatus("Recent call storage endpoint is not mounted in this environment.");
        return;
      }
      console.error("Failed to load recent calls", err);
      setRecentStatus("Failed to load recent calls.");
    }
  }, []);

  useEffect(() => {
    let isMounted = true;

    const scheduleReconnect = () => {
      if (!isMounted) return;
      const attempt = Math.min(retryRef.current + 1, 6);
      retryRef.current = attempt;
      const delayMs = Math.min(3000 * attempt, 15000);
      if (retryTimerRef.current) clearTimeout(retryTimerRef.current);
      retryTimerRef.current = setTimeout(connect, delayMs);
    };

    const connect = () => {
      try {
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;
        ws.onopen = () => {
          if (!isMounted) return;
          setConnected(true);
          setStatus("Connected. Streaming AI call events...");
          retryRef.current = 0;
          ws.send(JSON.stringify({ type: "subscribe", channel: "ai.calls.*" }));
          ws.send(JSON.stringify({ type: "subscribe", channel: "quo.*" }));
        };
        ws.onmessage = (event) => {
          try {
            const parsed = JSON.parse(event.data);
            const log = normalizeCallPayload(parsed);
            setLogs((prev) => [log, ...prev].slice(0, 200));
            setStatus(`New event: ${log.event || "update"} | ${log.customer}`);
          } catch {
            // ignore malformed payloads
          }
        };
        ws.onclose = () => {
          if (!isMounted) return;
          setConnected(false);
          setStatus("Disconnected. Reconnecting...");
          scheduleReconnect();
        };
        ws.onerror = () => {
          setConnected(false);
        };
      } catch {
        scheduleReconnect();
      }
    };

    connect();
    fetchRecent();

    return () => {
      isMounted = false;
      if (retryTimerRef.current) clearTimeout(retryTimerRef.current);
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.close();
      }
    };
  }, [fetchRecent, wsUrl]);

  return (
    <div className="min-h-screen bg-slate-950/60 backdrop-blur-sm">
      <div className="mx-auto max-w-6xl p-6">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-xl font-semibold text-white/90 sm:text-2xl">AI Call Manager</h2>
          <div className="flex items-center gap-3">
            <span
              className={`inline-flex items-center rounded border px-2 py-1 text-xs font-medium ${
                connected
                  ? "border-emerald-500/30 bg-emerald-500/20 text-emerald-300"
                  : "border-rose-500/30 bg-rose-500/20 text-rose-300"
              }`}
            >
              <span
                className={`mr-1 inline-block h-2 w-2 rounded-full ${
                  connected ? "bg-emerald-400" : "bg-rose-400"
                }`}
              />
              {connected ? "Connected" : "Disconnected"}
            </span>
            <button
              onClick={() => setLogs([])}
              className="rounded border border-white/10 px-3 py-1.5 text-white/80 transition hover:bg-white/5 hover:text-white"
            >
              Clear
            </button>
          </div>
        </div>

        <p className="mb-4 text-sm text-white/70">{status}</p>

        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-3">
            <div className="font-semibold text-white/80">Live Events</div>
            {logs.length === 0 && <div className="text-sm text-white/60">No events yet.</div>}
            {logs.map((log, index) => (
              <div key={`${log.callId}-${index}`} className="rounded-lg border border-white/10 bg-white/5 p-4 text-white/90">
                <div className="mb-1 flex flex-wrap items-center justify-between gap-2">
                  <div className="font-medium">{log.customer}</div>
                  <div className="text-xs text-white/60">{new Date(log.timestamp).toLocaleString()}</div>
                </div>
                <div className="text-sm">
                  <span className="text-white/60">Event:</span> {log.event || "(unknown)"}
                </div>
                {log.summary && (
                  <div className="text-sm">
                    <span className="text-white/60">Summary:</span> {log.summary}
                  </div>
                )}
                {log.callId && <div className="text-xs text-white/50">Call ID: {log.callId}</div>}
              </div>
            ))}
          </div>

          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="font-semibold text-white/80">Recent Calls</div>
              <button
                onClick={fetchRecent}
                className="rounded border border-white/10 px-2 py-1 text-xs text-white/70 hover:bg-white/5"
              >
                Refresh
              </button>
            </div>
            {recent.length === 0 && <div className="text-sm text-white/60">{recentStatus || "No recent calls stored."}</div>}
            {recent.map((call) => (
              <div key={call.call_id} className="rounded-lg border border-white/10 bg-white/5 p-4 text-white/90">
                <div className="mb-1 flex items-center justify-between text-sm">
                  <span className="font-medium">{call.call_id}</span>
                  <span className="text-white/60">{new Date(call.updated_at || call.created_at).toLocaleString()}</span>
                </div>
                <div className="mb-1 text-xs text-white/70">
                  {call.direction?.toUpperCase()} | {call.status}
                </div>
                <div className="mb-1 text-xs text-white/70">
                  From: {call.from_number || "?"} | To: {call.to_number || "?"}
                </div>
                {call.bot_name && <div className="text-xs text-emerald-300">Bot: {call.bot_name}</div>}
                {call.purpose && <div className="text-xs text-white/70">Purpose: {call.purpose}</div>}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
