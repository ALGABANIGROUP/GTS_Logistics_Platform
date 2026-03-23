import React, { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { MapContainer, Marker, Polyline, Popup, TileLayer } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import RequireAuth from "../../components/RequireAuth.jsx";
import fleetSafetyApi from "../../services/fleetSafetyApi";

delete L.Icon.Default.prototype._getIconUrl;

const saudiCenter = [24.7136, 46.6753];

const makeIcon = (label, background) =>
  L.divIcon({
    className: "",
    html: `<div style="width:34px;height:34px;border-radius:999px;background:${background};color:#fff;display:flex;align-items:center;justify-content:center;border:2px solid rgba(255,255,255,0.9);box-shadow:0 10px 24px rgba(15,23,42,0.35);font-size:16px;font-weight:700">${label}</div>`,
    iconSize: [34, 34],
    iconAnchor: [17, 17],
    popupAnchor: [0, -14],
  });

const vehicleIcons = {
  available: makeIcon("V", "#10b981"),
  occupied: makeIcon("V", "#f59e0b"),
  maintenance: makeIcon("V", "#ef4444"),
  broken: makeIcon("V", "#64748b"),
  inactive: makeIcon("V", "#475569"),
};

const driverIcons = {
  available: makeIcon("D", "#22c55e"),
  busy: makeIcon("D", "#fb923c"),
  rest: makeIcon("D", "#38bdf8"),
  leave: makeIcon("D", "#a855f7"),
  offline: makeIcon("D", "#64748b"),
  inactive: makeIcon("D", "#475569"),
};

const statusClass = {
  available: "border-emerald-400/30 bg-emerald-500/10 text-emerald-200",
  occupied: "border-amber-400/30 bg-amber-500/10 text-amber-200",
  maintenance: "border-rose-400/30 bg-rose-500/10 text-rose-200",
  broken: "border-slate-400/30 bg-slate-500/10 text-slate-200",
  busy: "border-amber-400/30 bg-amber-500/10 text-amber-200",
  rest: "border-sky-400/30 bg-sky-500/10 text-sky-200",
  leave: "border-fuchsia-400/30 bg-fuchsia-500/10 text-fuchsia-200",
  offline: "border-slate-400/30 bg-slate-500/10 text-slate-200",
  high: "border-rose-400/30 bg-rose-500/10 text-rose-100",
  medium: "border-amber-400/30 bg-amber-500/10 text-amber-100",
  low: "border-emerald-400/30 bg-emerald-500/10 text-emerald-100",
  critical: "border-red-500/30 bg-red-600/10 text-red-100",
};

const wsBase = () => {
  const envBase = import.meta.env.VITE_API_BASE_URL;
  if (envBase) {
    try {
      const url = new URL(envBase);
      url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
      url.pathname = "/api/v1/fleet/live/ws";
      url.search = "";
      url.hash = "";
      return url.toString();
    } catch {
      return null;
    }
  }
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${protocol}//${window.location.host}/api/v1/fleet/live/ws`;
};

function FleetLiveMapContent() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [vehicles, setVehicles] = useState([]);
  const [drivers, setDrivers] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [stats, setStats] = useState({});
  const [selected, setSelected] = useState(null);
  const [selectedTrack, setSelectedTrack] = useState([]);
  const [lastSync, setLastSync] = useState(null);

  const mapEntities = useMemo(() => {
    const markers = [];
    vehicles.forEach((vehicle) => {
      if (vehicle.lat !== null && vehicle.lng !== null) {
        markers.push({ kind: "vehicle", id: vehicle.id });
      }
    });
    drivers.forEach((driver) => {
      if (driver.lat !== null && driver.lng !== null) {
        markers.push({ kind: "driver", id: driver.id });
      }
    });
    return markers;
  }, [vehicles, drivers]);

  const loadData = async () => {
    try {
      const response = await fleetSafetyApi.getLiveMapData();
      setVehicles(response.data?.vehicles || []);
      setDrivers(response.data?.drivers || []);
      setAlerts(response.data?.alerts || []);
      setStats(response.data?.stats || {});
      setLastSync(response.data?.timestamp || new Date().toISOString());
      setError("");
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to load fleet live map.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = window.setInterval(loadData, 30000);
    return () => window.clearInterval(interval);
  }, []);

  useEffect(() => {
    const url = wsBase();
    if (!url) return undefined;
    let active = true;
    let socket;
    try {
      socket = new WebSocket(url);
      socket.onmessage = (event) => {
        if (!active) return;
        try {
          const message = JSON.parse(event.data);
          if (message.type !== "location_update") return;
          if (message.entity_type === "vehicle") {
            setVehicles((prev) => prev.map((item) => (item.id === message.data.id ? { ...item, ...message.data } : item)));
            setLastSync(message.timestamp);
          } else if (message.entity_type === "driver") {
            setDrivers((prev) => prev.map((item) => (item.id === message.data.id ? { ...item, ...message.data } : item)));
            setLastSync(message.timestamp);
          } else if (message.entity_type === "alert") {
            setAlerts((prev) => [message.data, ...prev].slice(0, 10));
          }
        } catch {
          // Ignore malformed websocket payloads.
        }
      };
    } catch {
      return undefined;
    }
    return () => {
      active = false;
      try {
        socket?.close();
      } catch {
        // Ignore close failures.
      }
    };
  }, []);

  const handleVehicleSelect = async (vehicle) => {
    setSelected({ kind: "vehicle", item: vehicle });
    try {
      const response = await fleetSafetyApi.getVehicleTrack(vehicle.id, 24);
      setSelectedTrack(response.data?.track || []);
    } catch {
      setSelectedTrack([]);
    }
  };

  const handleDriverSelect = async (driver) => {
    setSelected({ kind: "driver", item: driver });
    try {
      const response = await fleetSafetyApi.getDriverTrack(driver.id, 24);
      setSelectedTrack(response.data?.track || []);
    } catch {
      setSelectedTrack([]);
    }
  };

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(56,189,248,0.14),_rgba(2,6,23,0.98)_42%)] p-4 md:p-6">
      <div className="mx-auto flex max-w-[1800px] flex-col gap-6">
        <div className="overflow-hidden rounded-[32px] border border-sky-400/10 bg-white/[0.03] p-6 shadow-[0_24px_80px_rgba(2,6,23,0.45)]">
          <div className="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
            <div className="max-w-3xl">
              <div className="mb-3 inline-flex rounded-full border border-sky-400/20 bg-sky-400/10 px-3 py-1 text-xs uppercase tracking-[0.28em] text-sky-200">Fleet Live Tracking</div>
              <h1 className="text-3xl font-semibold tracking-tight text-white md:text-4xl">Fleet Live Map Integration</h1>
              <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-300">
                Monitor live vehicle and driver positions, inspect active tracks, review safety alerts, and jump back into fleet control without leaving the map.
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <Link to="/ai-bots/freight_broker/vehicles" className="rounded-2xl border border-white/15 bg-white/5 px-4 py-3 text-sm font-semibold text-white hover:bg-white/10">
                Back to Fleet Workspace
              </Link>
              <Link to="/ai-bots/freight_broker" className="rounded-2xl border border-sky-400/20 bg-sky-500/10 px-4 py-3 text-sm font-semibold text-sky-100 hover:bg-sky-500/20">
                Freight Broker Dashboard
              </Link>
              <button onClick={loadData} className="rounded-2xl bg-white px-4 py-3 text-sm font-semibold text-slate-950 hover:bg-slate-100">
                Refresh Live Data
              </button>
            </div>
          </div>
        </div>

        {error ? <div className="rounded-2xl border border-rose-400/30 bg-rose-500/10 p-4 text-sm text-rose-100">{error}</div> : null}

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
          {[
            ["Active Vehicles", stats.active_vehicles || 0, "Reporting live coordinates"],
            ["Available Drivers", stats.available_drivers || 0, "Ready for assignment"],
            ["Busy Drivers", stats.busy_drivers || 0, "Currently allocated"],
            ["Maintenance Units", stats.maintenance_vehicles || 0, "Held off the road"],
            ["Open Alerts", stats.alerts_open || 0, lastSync ? `Last sync ${new Date(lastSync).toLocaleTimeString("en-US")}` : "Waiting for first sync"],
          ].map(([title, value, meta]) => (
            <div key={title} className="rounded-[28px] border border-white/10 bg-white/[0.04] p-5 shadow-[0_18px_45px_rgba(15,23,42,0.22)]">
              <div className="text-xs uppercase tracking-[0.24em] text-slate-400">{title}</div>
              <div className="mt-3 text-3xl font-semibold text-white">{value}</div>
              <div className="mt-2 text-sm text-slate-400">{meta}</div>
            </div>
          ))}
        </div>

        <div className="grid gap-6 xl:grid-cols-[360px_minmax(0,1fr)_340px]">
          <div className="space-y-6">
            <div className="rounded-[30px] border border-white/10 bg-white/[0.03] p-5">
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-semibold text-white">Vehicles</h2>
                  <p className="text-sm text-slate-400">Live fleet units with location or assignment context.</p>
                </div>
                <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-300">{vehicles.length}</span>
              </div>
              <div className="max-h-[340px] space-y-3 overflow-y-auto pr-1">
                {vehicles.map((vehicle) => (
                  <button
                    key={vehicle.id}
                    type="button"
                    onClick={() => handleVehicleSelect(vehicle)}
                    className={`w-full rounded-2xl border p-4 text-left transition ${
                      selected?.kind === "vehicle" && selected?.item?.id === vehicle.id
                        ? "border-sky-400/40 bg-sky-500/10"
                        : "border-white/10 bg-slate-950/40 hover:bg-white/[0.04]"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <div className="font-medium text-white">{vehicle.plate_number}</div>
                        <div className="text-xs text-slate-400">{vehicle.vehicle_code} · {vehicle.type}</div>
                      </div>
                      <span className={`inline-flex rounded-full border px-3 py-1 text-[11px] font-medium ${statusClass[vehicle.vehicle_status] || statusClass.available}`}>
                        {vehicle.vehicle_status}
                      </span>
                    </div>
                    <div className="mt-3 flex items-center justify-between text-xs text-slate-400">
                      <span>{vehicle.driver_name || "No driver assigned"}</span>
                      <span>{vehicle.speed ? `${Math.round(Number(vehicle.speed))} km/h` : "No telemetry"}</span>
                    </div>
                  </button>
                ))}
                {!vehicles.length ? <div className="rounded-2xl border border-dashed border-white/10 bg-slate-950/30 p-4 text-sm text-slate-400">No fleet vehicles available yet.</div> : null}
              </div>
            </div>

            <div className="rounded-[30px] border border-white/10 bg-white/[0.03] p-5">
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-semibold text-white">Drivers</h2>
                  <p className="text-sm text-slate-400">Driver readiness, status, and live position feed.</p>
                </div>
                <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-300">{drivers.length}</span>
              </div>
              <div className="max-h-[340px] space-y-3 overflow-y-auto pr-1">
                {drivers.map((driver) => (
                  <button
                    key={driver.id}
                    type="button"
                    onClick={() => handleDriverSelect(driver)}
                    className={`w-full rounded-2xl border p-4 text-left transition ${
                      selected?.kind === "driver" && selected?.item?.id === driver.id
                        ? "border-sky-400/40 bg-sky-500/10"
                        : "border-white/10 bg-slate-950/40 hover:bg-white/[0.04]"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <div className="font-medium text-white">{driver.driver_name}</div>
                        <div className="text-xs text-slate-400">{driver.driver_code}</div>
                      </div>
                      <span className={`inline-flex rounded-full border px-3 py-1 text-[11px] font-medium ${statusClass[driver.driver_status] || statusClass.offline}`}>
                        {driver.driver_status}
                      </span>
                    </div>
                    <div className="mt-3 flex items-center justify-between text-xs text-slate-400">
                      <span>{driver.plate_number || "No active vehicle"}</span>
                      <span>{driver.speed ? `${Math.round(Number(driver.speed))} km/h` : "No telemetry"}</span>
                    </div>
                  </button>
                ))}
                {!drivers.length ? <div className="rounded-2xl border border-dashed border-white/10 bg-slate-950/30 p-4 text-sm text-slate-400">No fleet drivers available yet.</div> : null}
              </div>
            </div>
          </div>

          <div className="overflow-hidden rounded-[32px] border border-white/10 bg-slate-950/60 shadow-[0_24px_80px_rgba(2,6,23,0.35)]">
            {loading ? (
              <div className="flex h-[860px] items-center justify-center text-sm text-slate-300">Loading live fleet map...</div>
            ) : (
              <MapContainer center={saudiCenter} zoom={6} scrollWheelZoom className="h-[860px] w-full">
                <TileLayer
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                {vehicles.filter((item) => item.lat !== null && item.lng !== null).map((vehicle) => (
                  <Marker
                    key={`vehicle-${vehicle.id}`}
                    position={[Number(vehicle.lat), Number(vehicle.lng)]}
                    icon={vehicleIcons[vehicle.vehicle_status] || vehicleIcons.available}
                    eventHandlers={{ click: () => handleVehicleSelect(vehicle) }}
                  >
                    <Popup>
                      <div className="min-w-[220px] space-y-1">
                        <div className="font-semibold">{vehicle.plate_number}</div>
                        <div>Vehicle: {vehicle.vehicle_code}</div>
                        <div>Status: {vehicle.vehicle_status}</div>
                        <div>Driver: {vehicle.driver_name || "Unassigned"}</div>
                        <div>Speed: {vehicle.speed ? `${Math.round(Number(vehicle.speed))} km/h` : "N/A"}</div>
                      </div>
                    </Popup>
                  </Marker>
                ))}
                {drivers.filter((item) => item.lat !== null && item.lng !== null).map((driver) => (
                  <Marker
                    key={`driver-${driver.id}`}
                    position={[Number(driver.lat), Number(driver.lng)]}
                    icon={driverIcons[driver.driver_status] || driverIcons.offline}
                    eventHandlers={{ click: () => handleDriverSelect(driver) }}
                  >
                    <Popup>
                      <div className="min-w-[220px] space-y-1">
                        <div className="font-semibold">{driver.driver_name}</div>
                        <div>Driver code: {driver.driver_code}</div>
                        <div>Status: {driver.driver_status}</div>
                        <div>Vehicle: {driver.plate_number || "Unassigned"}</div>
                        <div>Speed: {driver.speed ? `${Math.round(Number(driver.speed))} km/h` : "N/A"}</div>
                      </div>
                    </Popup>
                  </Marker>
                ))}
                {selectedTrack.length > 1 ? (
                  <Polyline
                    positions={selectedTrack.map((point) => [Number(point.lat), Number(point.lng)])}
                    pathOptions={{ color: "#38bdf8", weight: 4, opacity: 0.8 }}
                  />
                ) : null}
              </MapContainer>
            )}
          </div>

          <div className="space-y-6">
            <div className="rounded-[30px] border border-white/10 bg-white/[0.03] p-5">
              <h2 className="text-lg font-semibold text-white">Selected Entity</h2>
              <p className="mt-1 text-sm text-slate-400">Click a marker or pick a row to inspect details and recent movement.</p>
              {selected ? (
                <div className="mt-4 space-y-4">
                  <div className="rounded-2xl border border-white/10 bg-slate-950/40 p-4">
                    <div className="text-xs uppercase tracking-[0.2em] text-slate-500">{selected.kind === "vehicle" ? "Vehicle" : "Driver"}</div>
                    <div className="mt-2 text-lg font-semibold text-white">
                      {selected.kind === "vehicle" ? selected.item.plate_number : selected.item.driver_name}
                    </div>
                    <div className="mt-2 text-sm text-slate-300">
                      {selected.kind === "vehicle"
                        ? `${selected.item.vehicle_code} · ${selected.item.type}`
                        : `${selected.item.driver_code} · ${selected.item.plate_number || "No vehicle assigned"}`}
                    </div>
                    <div className="mt-3 flex flex-wrap gap-2">
                      <span className={`inline-flex rounded-full border px-3 py-1 text-xs font-medium ${statusClass[selected.kind === "vehicle" ? selected.item.vehicle_status : selected.item.driver_status] || statusClass.offline}`}>
                        {selected.kind === "vehicle" ? selected.item.vehicle_status : selected.item.driver_status}
                      </span>
                      <span className="inline-flex rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-medium text-slate-300">
                        {selected.item.speed ? `${Math.round(Number(selected.item.speed))} km/h` : "No speed data"}
                      </span>
                    </div>
                  </div>
                  <div className="rounded-2xl border border-white/10 bg-slate-950/40 p-4">
                    <div className="text-xs uppercase tracking-[0.2em] text-slate-500">Track Points</div>
                    <div className="mt-2 text-3xl font-semibold text-white">{selectedTrack.length}</div>
                    <div className="mt-2 text-sm text-slate-400">Last 24-hour route history plotted on the map.</div>
                  </div>
                  <div className="flex gap-3">
                    <Link to="/ai-bots/freight_broker/vehicles" className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm font-semibold text-white hover:bg-white/10">
                      Open Fleet Workspace
                    </Link>
                    <Link to="/ai-bots/freight_broker/map" className="rounded-2xl border border-sky-400/20 bg-sky-500/10 px-4 py-3 text-sm font-semibold text-sky-100 hover:bg-sky-500/20">
                      Freight Broker Map
                    </Link>
                  </div>
                </div>
              ) : (
                <div className="mt-4 rounded-2xl border border-dashed border-white/10 bg-slate-950/30 p-4 text-sm text-slate-400">No entity selected yet.</div>
              )}
            </div>

            <div className="rounded-[30px] border border-white/10 bg-white/[0.03] p-5">
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-semibold text-white">Live Alerts</h2>
                  <p className="text-sm text-slate-400">Speeding and operational signals from live telemetry.</p>
                </div>
                <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-300">{alerts.length}</span>
              </div>
              <div className="space-y-3">
                {alerts.map((alert) => (
                  <div key={alert.id} className="rounded-2xl border border-white/10 bg-slate-950/40 p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <div className="font-medium text-white">{alert.message || alert.alert_type}</div>
                        <div className="mt-1 text-xs text-slate-400">{new Date(alert.created_at).toLocaleString("en-US")}</div>
                      </div>
                      <span className={`inline-flex rounded-full border px-3 py-1 text-[11px] font-medium ${statusClass[alert.severity] || statusClass.medium}`}>
                        {alert.severity}
                      </span>
                    </div>
                  </div>
                ))}
                {!alerts.length ? <div className="rounded-2xl border border-dashed border-white/10 bg-slate-950/30 p-4 text-sm text-slate-400">No open live alerts.</div> : null}
              </div>
            </div>

            <div className="rounded-[30px] border border-white/10 bg-white/[0.03] p-5">
              <h2 className="text-lg font-semibold text-white">Coverage</h2>
              <div className="mt-4 space-y-3">
                {[
                  ["Map entities with coordinates", mapEntities.length],
                  ["Vehicles with telemetry", vehicles.filter((item) => item.lat !== null).length],
                  ["Drivers with telemetry", drivers.filter((item) => item.lat !== null).length],
                ].map(([label, value]) => (
                  <div key={label} className="flex items-center justify-between rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-3">
                    <span className="text-sm text-slate-300">{label}</span>
                    <span className="text-sm font-semibold text-white">{value}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function FleetLiveMap() {
  return (
    <RequireAuth roles={["admin", "owner", "super_admin"]}>
      <FleetLiveMapContent />
    </RequireAuth>
  );
}
