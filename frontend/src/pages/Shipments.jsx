// frontend/src/pages/Shipments.jsx
import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useRefreshSubscription } from "../contexts/UiActionsContext.jsx";
import axiosClient from "../api/axiosClient";
import { WS_BASE_URL } from "../config/env";
import { appendTokenToWsUrl, isSocketUnauthorized, notifySocketUnauthorized } from "../utils/wsHelpers";
import { useAuth } from "../contexts/AuthContext.jsx";
import { useCurrencyStore } from "../stores/useCurrencyStore";

// -----------------------------
// Config / helpers
// -----------------------------
function buildWsUrl(path = "/live") {
  const base = String(WS_BASE_URL || "").replace(/\/+$/, "");
  const suffix = path.startsWith("/") ? path : `/${path}`;
  return `${base}${suffix}`;
}

function buildAuthWsUrl(path = "/live", overrideToken) {
  return appendTokenToWsUrl(buildWsUrl(path), overrideToken);
}

function normalizeList(input) {
  // Accepts: array, or {data:[...]} or any similar simple shape
  if (Array.isArray(input)) return input;
  if (input && Array.isArray(input.data)) return input.data;
  return [];
}

function upsertById(list, item) {
  const idx = list.findIndex((x) => String(x.id) === String(item.id));
  if (idx === -1) return [item, ...list];
  const merged = { ...list[idx], ...item };
  const next = list.slice();
  next[idx] = merged;
  return next;
}

// -----------------------------
// Component
// -----------------------------
const Shipments = () => {
  const [shipments, setShipments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("All");
  const [live, setLive] = useState(true); // WS live status

  const reconnectRef = useRef(1000); // backoff ms
  const hbRef = useRef(null);
  const wsRef = useRef(null);

  // NEW refs to prevent dev StrictMode loops + reconnect storms
  const reconnectTimerRef = useRef(null);
  const shouldReconnectRef = useRef(true);
  const closingRef = useRef(false);
  const mountedRef = useRef(false);

  const { token } = useAuth();
  const tokenRef = useRef(token);
  const { currencySymbol, formatCurrency } = useCurrencyStore();
  const connectingRef = useRef(false);
  const navigate = useNavigate();

  useEffect(() => {
    tokenRef.current = token;
  }, [token]);

  // ---------- API ----------
  const fetchShipments = useCallback(async () => {
    setLoading(true);
    try {
      const res = await axiosClient.get("/shipments/", { params: { limit: 50 } });
      const payload = res?.data?.shipments ?? res?.data;
      setShipments(normalizeList(payload));
    } catch (error) {
      console.error("Error fetching shipments:", error);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchShipmentById = useCallback(async (id) => {
    try {
      const res = await axiosClient.get(`/shipments/${id}`);
      const data = res?.data;
      return data && data.data ? data.data : data;
    } catch {
      return null;
    }
  }, []);

  // ---------- WS ----------
  const connectWS = useCallback(
    (authToken) => {
      const effectiveToken = authToken || tokenRef.current;

      // Don't connect if unmounted or reconnect disabled
      if (!mountedRef.current || !shouldReconnectRef.current) return;

      if (!effectiveToken) {
        setLive(false);
        return;
      }
      if (connectingRef.current) return;

      connectingRef.current = true;

      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
        reconnectTimerRef.current = null;
      }

      try {
        const url = buildAuthWsUrl("/live", effectiveToken);
        if (!url) {
          console.warn("Skipping shipments WebSocket (no url).");
          setLive(false);
          connectingRef.current = false;
          return;
        }

        if (wsRef.current) {
          const sameUrl = wsRef.current.url === url;
          const state = wsRef.current.readyState;

          if (sameUrl && (state === WebSocket.OPEN || state === WebSocket.CONNECTING)) {
            connectingRef.current = false;
            return;
          }

          try {
            closingRef.current = true;
            wsRef.current.close(1000, "reconnect");
          } catch { }
          wsRef.current = null;
        }

        const ws = new WebSocket(url);
        wsRef.current = ws;
        closingRef.current = false;

        ws.onopen = () => {
          if (!mountedRef.current) return;

          setLive(true);
          reconnectRef.current = 1000; // reset backoff
          connectingRef.current = false;

          console.log("WS open");

          try {
            ws.send(JSON.stringify({ type: "subscribe", channel: "events.load.created" }));
            ws.send(JSON.stringify({ type: "subscribe", channel: "events.ops.shipment_imported" }));
          } catch { }

          if (hbRef.current) clearInterval(hbRef.current);
          hbRef.current = setInterval(() => {
            try {
              if (ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ type: "ping" }));
              }
            } catch { }
          }, 25000);
        };

        ws.onmessage = async (evt) => {
          let msg = null;
          try {
            msg = JSON.parse(evt.data);
          } catch {
            return;
          }
          if (!msg || (!msg.channel && msg.type !== "pong")) return;

          if (msg.channel === "events.load.created") {
            const p = msg.payload || {};
            const id = p.shipment_id || p.id;
            if (!id) return;

            const candidate = {
              id,
              pickup_location: p.pickup_location || "Unknown",
              dropoff_location: p.dropoff_location || "Unknown",
              status: p.status || "Imported",
            };
            setShipments((prev) => upsertById(prev, candidate));
          }

          if (msg.channel === "events.ops.shipment_imported") {
            const p = msg.payload || {};
            const id = p.shipment_id || p.id;
            if (!id) return;

            const full = await fetchShipmentById(id);
            const candidate =
              full || {
                id,
                pickup_location: "Unknown",
                dropoff_location: "Unknown",
                status: "Imported",
              };

            setShipments((prev) => upsertById(prev, candidate));
          }
        };

        ws.onclose = (event) => {
          if (!mountedRef.current) return;

          setLive(false);
          connectingRef.current = false;

          console.log("WS closed", {
            code: event.code,
            reason: event.reason,
            wasClean: event.wasClean,
            closingRef: closingRef.current,
          });

          // Unauthorized => clear and redirect
          if (isSocketUnauthorized(event)) {
            notifySocketUnauthorized(event);
            return;
          }

          const wasIntentional = closingRef.current;
          closingRef.current = false;

          // cleanup heartbeat
          if (hbRef.current) {
            clearInterval(hbRef.current);
            hbRef.current = null;
          }

          // IMPORTANT: if closed intentionally OR reconnect disabled => do nothing
          if (wasIntentional || !shouldReconnectRef.current) return;

          // Backoff reconnect
          const delay = Math.min(reconnectRef.current, 15000);
          reconnectTimerRef.current = setTimeout(() => connectWS(), delay);
          reconnectRef.current = Math.round(reconnectRef.current * 1.7);
        };

        ws.onerror = (err) => {
          // Don't force-close here; it can cause "closed before established" noise in dev
          console.log("WS error", err);
        };
      } catch (e) {
        setLive(false);
        connectingRef.current = false;

        if (!mountedRef.current || !shouldReconnectRef.current) return;

        const delay = Math.min(reconnectRef.current, 15000);
        reconnectTimerRef.current = setTimeout(() => connectWS(), delay);
        reconnectRef.current = Math.round(reconnectRef.current * 1.7);
      }
    },
    [fetchShipmentById]
  );

  useEffect(() => {
    mountedRef.current = true;
    shouldReconnectRef.current = true;

    fetchShipments();
    const interval = setInterval(fetchShipments, 20000); // light refresh

    if (token) {
      reconnectRef.current = 1000;
      connectWS(token);
    } else {
      setLive(false);
    }

    return () => {
      mountedRef.current = false;
      shouldReconnectRef.current = false;

      clearInterval(interval);

      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
        reconnectTimerRef.current = null;
      }

      if (hbRef.current) {
        clearInterval(hbRef.current);
        hbRef.current = null;
      }

      if (wsRef.current) {
        try {
          closingRef.current = true; // prevent reconnect inside onclose
          wsRef.current.close(1000, "unmount");
        } catch { }
        wsRef.current = null;
      }

      connectingRef.current = false;
    };
  }, [connectWS, fetchShipments, token]);

  useRefreshSubscription(() => {
    fetchShipments();
  });

  // ---------- UI helpers ----------
  const handleFilterChange = (e) => setStatusFilter(e.target.value);

  const handleViewDetails = (id) => navigate(`/map?shipment_id=${id}`);

  const filteredShipments = useMemo(() => {
    if (statusFilter === "All") return shipments;
    return shipments.filter(
      (s) => String(s.status || "").toLowerCase() === String(statusFilter).toLowerCase()
    );
  }, [shipments, statusFilter]);

  const getRowColor = (status) => {
    switch (status) {
      case "on_the_way":
        return "bg-blue-100";
      case "Pending":
        return "bg-gray-100";
      case "Imported":
        return "bg-green-100";
      default:
        return "";
    }
  };

  // ---------- Render ----------
  return (
    <div className="glass-page p-6">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-xl font-bold text-blue-700">📦 Shipments</h1>
        <span className={`text-sm ${live ? "text-green-600" : "text-red-600"}`}>
          {live ? "Live" : "Offline"}
        </span>
      </div>

      <div className="mb-4 flex items-center gap-2">
        <label className="font-semibold">Filter by Status:</label>
        <select className="border px-2 py-1 rounded" value={statusFilter} onChange={handleFilterChange}>
          <option value="All">All</option>
          <option value="on_the_way">On the Way</option>
          <option value="Pending">Pending</option>
          <option value="Imported">Imported</option>
        </select>
      </div>

      {loading ? (
        <p className="text-gray-500">Loading shipments...</p>
      ) : filteredShipments.length === 0 ? (
        <p className="text-gray-400 italic">No shipments found for selected status.</p>
      ) : (
        <table className="w-full border border-gray-300 text-sm">
          <thead>
            <tr className="bg-gray-200 text-left">
              <th className="border p-2">ID</th>
              <th className="border p-2">Pickup</th>
              <th className="border p-2">Dropoff</th>
              <th className="border p-2">Status</th>
              <th className="border p-2">Action</th>
            </tr>
          </thead>
          <tbody>
            {filteredShipments.map((s) => (
              <tr key={s.id} className={getRowColor(s.status)}>
                <td className="border p-2">{s.id}</td>
                <td className="border p-2">{s.pickup_location || "—"}</td>
                <td className="border p-2">{s.dropoff_location || "—"}</td>
                <td className="border p-2">{s.status || "—"}</td>
                <td className="border p-2">
                  <button className="text-blue-600 hover:underline" onClick={() => handleViewDetails(s.id)}>
                    View Details
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default Shipments;
