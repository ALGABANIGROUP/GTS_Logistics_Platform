// frontend/src/pages/Operations.jsx
import React, { useEffect, useRef, useState } from "react";
import UnifiedShipmentMap from "../components/UnifiedShipmentMap";
import axiosClient from "../api/axiosClient";
import { WS_BASE_URL } from "../config/env";
import { appendTokenToWsUrl, isSocketUnauthorized, notifySocketUnauthorized } from "../utils/wsHelpers";

// ---- Config ----
function buildWsUrl(path = "/live") {
  const base = String(WS_BASE_URL || "").replace(/\/+$/, "");
  const suffix = path.startsWith("/") ? path : `/${path}`;
  return `${base}${suffix}`;
}

function buildAuthWsUrl(path = "/live") {
  return appendTokenToWsUrl(buildWsUrl(path));
}

function normalizeList(input) {
  if (Array.isArray(input)) return input;
  if (input && Array.isArray(input.data)) return input.data;
  return [];
}

export default function Operations() {
  const [counts, setCounts] = useState({ total: 0, today: 0, in_transit: 0, delayed: 0, delivered: 0 });
  const [recent, setRecent] = useState([]); // last few events (ids)
  const [live, setLive] = useState(true);
  const [loading, setLoading] = useState(true);

  const wsRef = useRef(null);
  const hbRef = useRef(null);
  const reconnectRef = useRef(1000);
  const refreshTimer = useRef(null);

  const computeCounts = (list) => {
    const now = new Date();
    const isToday = (d) => {
      if (!d) return false;
      const t = new Date(d);
      return (
        t.getFullYear() === now.getFullYear() &&
        t.getMonth() === now.getMonth() &&
        t.getDate() === now.getDate()
      );
    };

    const total = list.length;
    const delivered = list.filter((s) => String(s.status || "").toLowerCase().startsWith("deliver")).length;
    const delayed = list.filter((s) => String(s.status || "").toLowerCase().startsWith("delay")).length;
    const in_transit =
      list.filter((s) => {
        const st = String(s.status || "").toLowerCase();
        return st === "on_the_way" || st === "in_transit" || st === "in-transit";
      }).length;
    const today = list.filter((s) => isToday(s.created_at || s.updated_at || s.pickup_date)).length;

    return { total, today, in_transit, delayed, delivered };
  };

  const fetchCounts = async () => {
    try {
      const res = await axiosClient.get("/shipments", { params: { limit: 200 } });
      const payload = res?.data?.shipments ?? res?.data;
      const list = normalizeList(payload);
      setCounts(computeCounts(list));
    } catch (e) {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  const scheduleRefresh = (ms = 600) => {
    if (refreshTimer.current) return;
    refreshTimer.current = setTimeout(() => {
      refreshTimer.current = null;
      fetchCounts();
    }, ms);
  };

  const connectWS = () => {
    try {
      const url = buildAuthWsUrl("/live");
      if (!url) {
        console.warn("Skipping Operations WebSocket (no auth token).");
        setLive(false);
        return;
      }
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        setLive(true);
        reconnectRef.current = 1000;
        ws.send(JSON.stringify({ type: "subscribe", channel: "events.load.created" }));
        ws.send(JSON.stringify({ type: "subscribe", channel: "events.ops.shipment_imported" }));
        if (hbRef.current) clearInterval(hbRef.current);
        hbRef.current = setInterval(() => {
          try { ws.send(JSON.stringify({ type: "ping" })); } catch { }
        }, 25_000);
      };

      ws.onmessage = (evt) => {
        let msg = null;
        try { msg = JSON.parse(evt.data); } catch { return; }
        if (!msg || (!msg.channel && msg.type !== "pong")) return;
        const p = msg.payload || {};
        const id = p.shipment_id || p.id;
        if (id) {
          setRecent((prev) => {
            const next = [{ id, ts: new Date().toISOString(), type: msg.channel }, ...prev];
            return next.slice(0, 10);
          });
        }
        // any shipment event → recompute counts shortly (debounced)
        scheduleRefresh(500);
      };

      ws.onclose = (event) => {
        setLive(false);
        if (hbRef.current) { clearInterval(hbRef.current); hbRef.current = null; }
        if (isSocketUnauthorized(event)) {
          notifySocketUnauthorized(event);
          return;
        }
        const delay = Math.min(reconnectRef.current, 15_000);
        setTimeout(connectWS, delay);
        reconnectRef.current = Math.round(reconnectRef.current * 1.7);
      };

      ws.onerror = () => {
        try { ws.close(); } catch { }
      };
    } catch {
      setLive(false);
      const delay = Math.min(reconnectRef.current, 15_000);
      setTimeout(connectWS, delay);
      reconnectRef.current = Math.round(reconnectRef.current * 1.7);
    }
  };

  useEffect(() => {
    fetchCounts();
    const intv = setInterval(fetchCounts, 20_000);
    connectWS();
    return () => {
      clearInterval(intv);
      if (refreshTimer.current) { clearTimeout(refreshTimer.current); refreshTimer.current = null; }
      if (hbRef.current) { clearInterval(hbRef.current); hbRef.current = null; }
      if (wsRef.current) { try { wsRef.current.close(); } catch { } }
    };
  }, []);

  return (
    <div className="p-6 space-y-6 glass-page">
      <div className="flex items-center justify-between glass-panel rounded-2xl p-4 border border-white/10 shadow-lg">
        <h1 className="text-xl font-bold text-slate-50 flex items-center gap-2">🚦 Operations</h1>
        <div className="glass-status-badge text-xs">
          {live ? "Live" : "Offline"}
        </div>
      </div>

      {/* Status tiles */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Tile title="Today" value={counts.today} loading={loading} />
        <Tile title="In Transit" value={counts.in_transit} loading={loading} />
        <Tile title="Delayed" value={counts.delayed} loading={loading} />
        <Tile title="Delivered" value={counts.delivered} loading={loading} />
      </div>

      {/* Recent events */}
      <div className="glass-panel rounded-2xl p-4 border border-white/10 shadow-lg">
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-semibold text-slate-50">Recent Events</h2>
          <button
            className="glass-btn-secondary glass-btn-sm"
            onClick={() => fetchCounts()}
          >
            Refresh
          </button>
        </div>
        {recent.length === 0 ? (
          <div className="text-sm text-slate-300">No events yet.</div>
        ) : (
          <ul className="text-sm space-y-2">
            {recent.map((e, i) => (
              <li key={i} className="glass-panel rounded-lg border border-white/10 p-2">
                <span className="font-mono text-xs text-slate-400">{e.ts}</span>{" "}
                — <strong className="text-slate-100">#{e.id}</strong> via <em className="text-slate-200">{e.type}</em>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Live map (compact) */}
      <div className="h-[420px] rounded-xl overflow-hidden border border-white/10 glass-panel shadow-xl">
        <UnifiedShipmentMap enableLive />
      </div>
    </div>
  );
}

function Tile({ title, value, loading }) {
  return (
    <div className="glass-panel rounded-2xl p-4 border border-white/10 shadow-md">
      <div className="text-sm text-slate-300">{title}</div>
      <div className="text-2xl font-bold text-slate-50">{loading ? "…" : value}</div>
    </div>
  );
}
