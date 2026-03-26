import React, { useEffect, useMemo, useRef, useState } from "react";
import {
  Circle,
  LayersControl,
  MapContainer,
  Marker,
  Polyline,
  Popup,
  TileLayer,
  useMap,
} from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";
import axiosClient from "../api/axiosClient";
import { getShipmentLiveData } from "../api/shipmentMapApi";
import { WS_BASE_URL } from "../config/env";
import { appendTokenToWsUrl, isSocketUnauthorized, notifySocketUnauthorized } from "../utils/wsHelpers";

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({ iconRetinaUrl: markerIcon2x, iconUrl: markerIcon, shadowUrl: markerShadow });

const ITEM_URL = (id) => `/api/v1/shipments/${id}`;
const CITY_COORDINATES = {
  dubai: [25.2048, 55.2708], abu_dhabi: [24.4539, 54.3773], riyadh: [24.7136, 46.6753],
  chicago: [41.8781, -87.6298], atlanta: [33.749, -84.388], dallas: [32.7767, -96.797],
  phoenix: [33.4484, -112.074], new_york: [40.7128, -74.006], boston: [42.3601, -71.0589],
  los_angeles: [34.0522, -118.2437], san_francisco: [37.7749, -122.4194], houston: [29.7604, -95.3698],
  philadelphia: [39.9526, -75.1652], toronto: [43.6532, -79.3832], montreal: [45.5017, -73.5673],
  vancouver: [49.2827, -123.1207], calgary: [51.0447, -114.0719], edmonton: [53.5461, -113.4938],
  winnipeg: [49.8951, -97.1384], kingston: [44.2312, -76.486],
};

function buildWsUrl(path = "/live") {
  const base = String(WS_BASE_URL || "").replace(/\/+$/, "");
  const suffix = path.startsWith("/") ? path : `/${path}`;
  return `${base}${suffix}`;
}
const buildAuthWsUrl = (path = "/live") => appendTokenToWsUrl(buildWsUrl(path));
const normalizeList = (input) =>
  Array.isArray(input) ? input : input?.items || input?.shipments || input?.data || [];

function firstNumber(...values) {
  for (const value of values) {
    const num = Number(value);
    if (Number.isFinite(num) && num !== 0) return num;
  }
}

function normalizeCityKey(value = "") {
  return String(value).trim().toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "")
    .replace(/,\s*[a-z]{2}$/i, "").replace(/,\s*[a-z.\s]+$/i, "").replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "");
}

function lookupCoordsFromText(...values) {
  for (const value of values) {
    if (!value) continue;
    const text = String(value);
    const variants = text.split(/[-,/]/).map((part) => normalizeCityKey(part)).filter(Boolean);
    for (const variant of variants) if (CITY_COORDINATES[variant]) return CITY_COORDINATES[variant];
    const normalized = normalizeCityKey(text);
    if (CITY_COORDINATES[normalized]) return CITY_COORDINATES[normalized];
  }
  return null;
}

const normalizeStatus = (status) => String(status || "").trim().toLowerCase().replace(/\s+/g, "_");
function statusColor(status) {
  const normalized = normalizeStatus(status);
  if (normalized.startsWith("deliver")) return "#22c55e";
  if (normalized.includes("delay")) return "#ef4444";
  if (["in_transit", "on_trip", "on_the_way"].includes(normalized)) return "#38bdf8";
  if (["available", "active"].includes(normalized)) return "#34d399";
  return "#f59e0b";
}

function formatDateTime(value) {
  if (!value) return "N/A";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? String(value) : date.toLocaleString();
}

function formatEtaCountdown(value, nowTs) {
  if (!value) return "N/A";
  const eta = new Date(value);
  if (Number.isNaN(eta.getTime())) return "N/A";
  const diffMs = eta.getTime() - nowTs;
  if (diffMs <= 0) return "Arrived / overdue";
  const totalMinutes = Math.floor(diffMs / 60000);
  const days = Math.floor(totalMinutes / 1440);
  const hours = Math.floor((totalMinutes % 1440) / 60);
  const minutes = totalMinutes % 60;
  if (days > 0) return `${days}d ${hours}h ${minutes}m`;
  if (hours > 0) return `${hours}h ${minutes}m`;
  return `${minutes}m`;
}

function makeBadgeIcon(text, background) {
  return L.divIcon({
    className: "",
    html: `<div style="width:34px;height:34px;border-radius:999px;background:${background};border:2px solid rgba(255,255,255,0.2);display:flex;align-items:center;justify-content:center;color:#fff;font-weight:800;font-size:12px;box-shadow:0 6px 20px rgba(0,0,0,0.35)">${text}</div>`,
    iconSize: [34, 34],
    iconAnchor: [17, 17],
    popupAnchor: [0, -14],
  });
}

const driverAvailableIcon = makeBadgeIcon("D", "#10b981");
const driverBusyIcon = makeBadgeIcon("D", "#f59e0b");
const companyIcon = makeBadgeIcon("C", "#6366f1");
const tenantIcon = makeBadgeIcon("T", "#8b5cf6");
const brokerIcon = makeBadgeIcon("B", "#ec4899");
const carrierIcon = makeBadgeIcon("C", "#22c55e");
const truckIcon = makeBadgeIcon("T", "#0ea5e9");
const startIcon = makeBadgeIcon("S", "#22c55e");
const endIcon = makeBadgeIcon("E", "#ef4444");

const getShipmentLabel = (shipment) => shipment?.reference || shipment?.shipment_number || shipment?.reference_number || shipment?.id || "N/A";
const getPickupLabel = (shipment) => shipment?.pickup_location || shipment?.origin_address || shipment?.origin?.address || shipment?.origin?.city || shipment?.origin_city || "Origin";
const getDropoffLabel = (shipment) => shipment?.dropoff_location || shipment?.destination_address || shipment?.destination?.address || shipment?.destination?.city || shipment?.destination_city || "Destination";

function getPickupCoords(shipment) {
  const lat = firstNumber(shipment?.latitude, shipment?.origin_latitude, shipment?.origin?.lat, shipment?.origin?.latitude, shipment?.pickup_lat, shipment?.pickup?.lat);
  const lng = firstNumber(shipment?.longitude, shipment?.origin_longitude, shipment?.origin?.lng, shipment?.origin?.longitude, shipment?.pickup_lng, shipment?.pickup?.lng);
  return lat && lng ? [lat, lng] : lookupCoordsFromText(shipment?.pickup_location, shipment?.origin_address, shipment?.origin_city, shipment?.origin?.city) || [24.7136, 46.6753];
}

function getDropoffCoords(shipment) {
  const lat = firstNumber(shipment?.dropoff_lat, shipment?.destination_latitude, shipment?.destination?.lat, shipment?.destination?.latitude, shipment?.dropoff?.lat);
  const lng = firstNumber(shipment?.dropoff_lng, shipment?.destination_longitude, shipment?.destination?.lng, shipment?.destination?.longitude, shipment?.dropoff?.lng);
  return lat && lng ? [lat, lng] : lookupCoordsFromText(shipment?.dropoff_location, shipment?.destination_address, shipment?.destination_city, shipment?.destination?.city) || [24.7743, 46.7386];
}

function getCurrentCoords(shipment) {
  const lat = firstNumber(shipment?.current_latitude, shipment?.current_location?.lat, shipment?.current_location?.latitude, shipment?.currentLocation?.[0]);
  const lng = firstNumber(shipment?.current_longitude, shipment?.current_location?.lng, shipment?.current_location?.longitude, shipment?.currentLocation?.[1]);
  return lat && lng ? [lat, lng] : null;
}

function buildShipmentRoute(shipment) {
  if (Array.isArray(shipment?.route) && shipment.route.length > 1) {
    return shipment.route.map((point) => Array.isArray(point) ? point : [point.lat, point.lng]);
  }
  return [getPickupCoords(shipment), getDropoffCoords(shipment)];
}

function buildFallbackLiveData(shipment, drivers = [], companies = [], vehicles = []) {
  if (!shipment) return null;
  const driver = drivers.find((item) => String(item.id) === String(shipment.driver_id));
  const vehicle = vehicles.find((item) => String(item.id) === String(shipment.vehicle_id || shipment.truck_id));
  const company = companies.find((item) => String(item.id) === String(shipment.company_id));
  return {
    shipment: {
      id: shipment.id,
      reference: getShipmentLabel(shipment),
      status: shipment.status,
      origin: { city: shipment.origin?.city || shipment.origin_city, address: getPickupLabel(shipment), lat: getPickupCoords(shipment)[0], lng: getPickupCoords(shipment)[1], country: shipment.origin?.country },
      destination: { city: shipment.destination?.city || shipment.destination_city, address: getDropoffLabel(shipment), lat: getDropoffCoords(shipment)[0], lng: getDropoffCoords(shipment)[1], country: shipment.destination?.country },
      current_location: { lat: getCurrentCoords(shipment)?.[0], lng: getCurrentCoords(shipment)?.[1], updated_at: shipment.current_location?.updated_at || shipment.updated_at || shipment.pickup_date || shipment.created_at, description: shipment.current_location?.description || shipment.current_location_description || company?.name || "Live GPS point" },
      eta: shipment.eta || shipment.delivery_scheduled || shipment.delivery_deadline,
      cargo: shipment.cargo || { type: shipment.shipment_type || shipment.trailer_type, weight: shipment.weight_kg || shipment.weight, dimensions: shipment.dimensions_meter || shipment.length, description: shipment.goods_description || shipment.description },
      progress: { percentage: shipment.progress?.percentage ?? (typeof shipment.progress === "number" ? shipment.progress * 100 : shipment.progress_percentage) },
      company,
    },
    driver: driver ? { id: driver.id, name: driver.name || driver.full_name || driver.email, phone: driver.phone || driver.phone_number || "N/A", rating: driver.rating ?? null, status: driver.status, experience: driver.experience, completed_trips: driver.completed_trips } : { id: shipment.driver_id, name: shipment.driver_name || shipment.driver || "Unassigned", phone: shipment.driver_phone || shipment.phone || "N/A", rating: null },
    vehicle: vehicle ? { id: vehicle.id, plate: vehicle.plate, type: vehicle.type, speed: shipment.current_location?.speed || shipment.speed || null, truck_number: vehicle.model || vehicle.plate, status: vehicle.status } : { id: shipment.vehicle_id || shipment.truck_id, plate: shipment.license_plate || null, type: shipment.trailer_type || shipment.shipment_type, speed: shipment.current_location?.speed || shipment.speed || null, truck_number: shipment.truck_number || shipment.truck || shipment.truck_id || "N/A", status: shipment.vehicle_status || null },
  };
}

function normalizeDriverEntity(driver) {
  if (!driver) return driver;
  return {
    ...driver,
    current_location: driver.current_location || driver.location || null,
    status: driver.status || driver.driver_status || "unknown",
    completed_trips: driver.completed_trips ?? driver.stats?.completed_trips ?? null,
  };
}

function normalizeCompanyEntity(company) {
  if (!company) return company;
  return {
    ...company,
    headquarters: company.headquarters || company.location || null,
    fleet_size: company.fleet_size ?? company.stats?.vehicles ?? company.stats?.fleet_size ?? null,
    phone: company.phone || company.contact?.phone || null,
  };
}

function StatRow({ label, value }) {
  return <div style={{ display: "flex", justifyContent: "space-between", gap: 12, fontSize: 12 }}><span style={{ color: "#94a3b8" }}>{label}</span><strong style={{ color: "#e2e8f0" }}>{value ?? "N/A"}</strong></div>;
}

function SectionCard({ title, children }) {
  return <div style={{ background: "#111827", border: "1px solid rgba(148,163,184,0.16)", borderRadius: 14, padding: 14 }}><div style={{ color: "#f8fafc", fontSize: 14, fontWeight: 700, marginBottom: 10 }}>{title}</div><div style={{ display: "grid", gap: 8 }}>{children}</div></div>;
}

function FitMapToEntities({ shipments, marketRoutes, drivers, companies, tenants, brokers, carriers }) {
  const map = useMap();
  useEffect(() => {
    const points = [];
    shipments.forEach((shipment) => {
      points.push(getPickupCoords(shipment), getDropoffCoords(shipment));
      const current = getCurrentCoords(shipment);
      if (current) points.push(current);
    });
    drivers.forEach((driver) => driver?.current_location?.lat && driver?.current_location?.lng && points.push([driver.current_location.lat, driver.current_location.lng]));
    companies.forEach((company) => company?.headquarters?.lat && company?.headquarters?.lng && points.push([company.headquarters.lat, company.headquarters.lng]));
    tenants.forEach((tenant) => tenant?.location?.lat && tenant?.location?.lng && points.push([tenant.location.lat, tenant.location.lng]));
    brokers.forEach((broker) => broker?.location?.lat && broker?.location?.lng && points.push([broker.location.lat, broker.location.lng]));
    carriers.forEach((carrier) => carrier?.location?.lat && carrier?.location?.lng && points.push([carrier.location.lat, carrier.location.lng]));
    marketRoutes.forEach((route) => {
      if (route?.originCoords) points.push(route.originCoords);
      if (route?.destinationCoords) points.push(route.destinationCoords);
    });
    const validPoints = points.filter((point) => Array.isArray(point) && Number.isFinite(point[0]) && Number.isFinite(point[1]));
    if (validPoints.length === 0) return;
    if (validPoints.length === 1) return map.setView(validPoints[0], 7);
    map.fitBounds(validPoints, { padding: [40, 40] });
  }, [map, shipments, marketRoutes, drivers, companies, tenants, brokers, carriers]);
  return null;
}

function ShipmentSidebar(props) {
  const {
    shipments, drivers, companies, tenants, brokers, carriers, selectedShipmentId, selectedLiveData,
    selectedDriver, selectedCompany, selectedTenant, selectedBroker, selectedCarrier,
    loadingLive, liveError, onSelectShipment, onSelectDriver, onSelectCompany,
    onSelectTenant, onSelectBroker, onSelectCarrier, marketRoutes, nowTs,
  } = props;
  const shipment = selectedLiveData?.shipment;
  const driver = selectedDriver || selectedLiveData?.driver;
  const company = selectedCompany || selectedLiveData?.shipment?.company;
  const vehicle = selectedLiveData?.vehicle;
  return (
    <aside style={{ width: 360, maxWidth: "100%", height: "100%", background: "#0b1220", border: "1px solid rgba(148,163,184,0.18)", borderRadius: 18, padding: 16, display: "flex", flexDirection: "column", gap: 12, color: "#e2e8f0", overflow: "hidden" }}>
      <div><div style={{ fontSize: 18, fontWeight: 800 }}>Unified Shipment Map</div><div style={{ marginTop: 4, fontSize: 12, color: "#94a3b8" }}>Shipments, drivers, and companies across US, Canada, and Gulf routes</div></div>
      <SectionCard title="Overview">
        <StatRow label="Total Shipments" value={shipments.length} />
        <StatRow label="Drivers" value={drivers.length} />
        <StatRow label="Tenants" value={tenants.length} />
        <StatRow label="Brokers" value={brokers.length} />
        <StatRow label="Carriers" value={carriers.length} />
        <StatRow label="Market Routes" value={marketRoutes.length} />
      </SectionCard>
      <div style={{ display: "grid", gap: 12, overflow: "auto", paddingRight: 2 }}>
        <SectionCard title="Selected Shipment">
          {!shipment ? <div style={{ fontSize: 12, color: "#94a3b8" }}>Select a shipment marker or shipment item.</div> : <>
            <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}><strong style={{ fontSize: 15 }}>{shipment.reference || shipment.id}</strong><span style={{ background: `${statusColor(shipment.status)}22`, color: statusColor(shipment.status), border: `1px solid ${statusColor(shipment.status)}55`, borderRadius: 999, padding: "3px 10px", fontSize: 11, fontWeight: 700 }}>{shipment.status || "unknown"}</span></div>
            <StatRow label="From" value={shipment.origin?.city || shipment.origin?.address} />
            <StatRow label="To" value={shipment.destination?.city || shipment.destination?.address} />
            <StatRow label="ETA" value={formatDateTime(shipment.eta)} />
            <StatRow label="ETA Remaining" value={formatEtaCountdown(shipment.eta, nowTs)} />
            <StatRow label="Cargo" value={shipment.cargo?.type || shipment.cargo?.description} />
            <StatRow label="Weight" value={shipment.cargo?.weight ? `${shipment.cargo.weight}` : "N/A"} />
            <StatRow label="Progress" value={shipment.progress?.percentage != null ? `${Math.round(Number(shipment.progress.percentage))}%` : "N/A"} />
          </>}
        </SectionCard>
        <SectionCard title="Driver">
          <StatRow label="Name" value={driver?.name || driver?.full_name || "Unassigned"} />
          <StatRow label="Phone" value={driver?.phone || driver?.phone_number || "N/A"} />
          <StatRow label="Status" value={driver?.status || "N/A"} />
          <StatRow label="Trips" value={driver?.completed_trips ?? "N/A"} />
          <StatRow label="Rating" value={driver?.rating ?? "N/A"} />
        </SectionCard>
        <SectionCard title="Vehicle">
          <StatRow label="Truck" value={vehicle?.truck_number || vehicle?.plate || "N/A"} />
          <StatRow label="Plate" value={vehicle?.plate || "N/A"} />
          <StatRow label="Type" value={vehicle?.type || "N/A"} />
          <StatRow label="Speed" value={vehicle?.speed != null ? `${Math.round(Number(vehicle.speed))} km/h` : "N/A"} />
          <StatRow label="Status" value={vehicle?.status || "N/A"} />
        </SectionCard>
        <SectionCard title="Company">
          <StatRow label="Name" value={company?.name || "N/A"} />
          <StatRow label="Fleet" value={company?.fleet_size ?? company?.stats?.vehicles ?? "N/A"} />
          <StatRow label="Phone" value={company?.phone || company?.contact?.phone || "N/A"} />
          <StatRow label="Website" value={company?.website || company?.contact?.website || "N/A"} />
          <StatRow label="Rating" value={company?.rating ?? "N/A"} />
        </SectionCard>
        <SectionCard title="Selected Tenant">
          <StatRow label="Name" value={selectedTenant?.name || "N/A"} />
          <StatRow label="City" value={selectedTenant?.location?.city || "N/A"} />
          <StatRow label="Phone" value={selectedTenant?.contact?.phone || "N/A"} />
          <StatRow label="Active Shipments" value={selectedTenant?.stats?.active_shipments ?? "N/A"} />
        </SectionCard>
        <SectionCard title="Selected Broker">
          <StatRow label="Name" value={selectedBroker?.name || "N/A"} />
          <StatRow label="City" value={selectedBroker?.location?.city || "N/A"} />
          <StatRow label="Phone" value={selectedBroker?.contact?.phone || "N/A"} />
          <StatRow label="Active Loads" value={selectedBroker?.stats?.active_loads ?? "N/A"} />
        </SectionCard>
        <SectionCard title="Selected Carrier">
          <StatRow label="Name" value={selectedCarrier?.name || "N/A"} />
          <StatRow label="City" value={selectedCarrier?.location?.city || "N/A"} />
          <StatRow label="Phone" value={selectedCarrier?.contact?.phone || "N/A"} />
          <StatRow label="Fleet" value={selectedCarrier?.stats?.fleet_size ?? "N/A"} />
        </SectionCard>
        <SectionCard title="Shipments">
          {shipments.map((item) => {
            const selected = String(item.id) === String(selectedShipmentId);
            return <button key={item.id} type="button" onClick={() => onSelectShipment(item.id)} style={{ textAlign: "left", background: selected ? "rgba(56,189,248,0.12)" : "#0f172a", border: selected ? "1px solid rgba(56,189,248,0.45)" : "1px solid rgba(148,163,184,0.14)", borderRadius: 12, padding: 10, color: "#e2e8f0", cursor: "pointer" }}>
              <div style={{ display: "flex", justifyContent: "space-between", gap: 10 }}><strong style={{ fontSize: 13 }}>{getShipmentLabel(item)}</strong><span style={{ color: statusColor(item.status), fontSize: 11, fontWeight: 700 }}>{item.status || "unknown"}</span></div>
              <div style={{ marginTop: 6, fontSize: 12, color: "#94a3b8" }}>{getPickupLabel(item)} to {getDropoffLabel(item)}</div>
            </button>;
          })}
        </SectionCard>
        <SectionCard title="Available Drivers">
          {drivers.filter((item) => normalizeStatus(item.status) === "available").map((item) => (
            <button key={item.id} type="button" onClick={() => onSelectDriver(item.id)} style={{ textAlign: "left", background: "#0f172a", border: "1px solid rgba(148,163,184,0.14)", borderRadius: 12, padding: 10, color: "#e2e8f0", cursor: "pointer" }}>
              <div style={{ fontSize: 13, fontWeight: 700 }}>{item.name || item.full_name || item.email}</div>
              <div style={{ marginTop: 4, fontSize: 12, color: "#94a3b8" }}>{item.current_location?.city || "Unknown"}{item.current_location?.state ? `, ${item.current_location.state}` : ""}</div>
            </button>
          ))}
        </SectionCard>
        <SectionCard title="Companies">
          {companies.map((item) => (
            <button key={item.id} type="button" onClick={() => onSelectCompany(item.id)} style={{ textAlign: "left", background: "#0f172a", border: "1px solid rgba(148,163,184,0.14)", borderRadius: 12, padding: 10, color: "#e2e8f0", cursor: "pointer" }}>
              <div style={{ fontSize: 13, fontWeight: 700 }}>{item.name}</div>
              <div style={{ marginTop: 4, fontSize: 12, color: "#94a3b8" }}>{item.headquarters?.city || item.location?.city || "Unknown"}{item.headquarters?.state || item.location?.state ? `, ${item.headquarters?.state || item.location?.state}` : ""}</div>
            </button>
          ))}
        </SectionCard>
        <SectionCard title="Tenants">
          {tenants.map((item) => (
            <button key={item.id} type="button" onClick={() => onSelectTenant(item.id)} style={{ textAlign: "left", background: "#0f172a", border: "1px solid rgba(148,163,184,0.14)", borderRadius: 12, padding: 10, color: "#e2e8f0", cursor: "pointer" }}>
              <div style={{ fontSize: 13, fontWeight: 700 }}>{item.name}</div>
              <div style={{ marginTop: 4, fontSize: 12, color: "#94a3b8" }}>{item.location?.city || "Unknown"}{item.location?.state ? `, ${item.location.state}` : ""}</div>
            </button>
          ))}
        </SectionCard>
        <SectionCard title="Brokers">
          {brokers.map((item) => (
            <button key={item.id} type="button" onClick={() => onSelectBroker(item.id)} style={{ textAlign: "left", background: "#0f172a", border: "1px solid rgba(148,163,184,0.14)", borderRadius: 12, padding: 10, color: "#e2e8f0", cursor: "pointer" }}>
              <div style={{ fontSize: 13, fontWeight: 700 }}>{item.name}</div>
              <div style={{ marginTop: 4, fontSize: 12, color: "#94a3b8" }}>{item.location?.city || "Unknown"}{item.location?.state ? `, ${item.location.state}` : ""}</div>
            </button>
          ))}
        </SectionCard>
        <SectionCard title="Carriers">
          {carriers.map((item) => (
            <button key={item.id} type="button" onClick={() => onSelectCarrier(item.id)} style={{ textAlign: "left", background: "#0f172a", border: "1px solid rgba(148,163,184,0.14)", borderRadius: 12, padding: 10, color: "#e2e8f0", cursor: "pointer" }}>
              <div style={{ fontSize: 13, fontWeight: 700 }}>{item.name}</div>
              <div style={{ marginTop: 4, fontSize: 12, color: "#94a3b8" }}>{item.location?.city || "Unknown"}{item.location?.state ? `, ${item.location.state}` : ""}</div>
            </button>
          ))}
        </SectionCard>
        {loadingLive ? <div style={{ fontSize: 12, color: "#93c5fd" }}>Loading live shipment details...</div> : null}
        {liveError ? <div style={{ fontSize: 12, color: "#fca5a5" }}>{liveError}</div> : null}
      </div>
    </aside>
  );
}

const UnifiedShipmentMap = ({ filterShipmentId, onTotalChange, setSummary, marketRoutes = [], enableLive = true }) => {
  const [shipments, setShipments] = useState([]);
  const [drivers, setDrivers] = useState([]);
  const [companies, setCompanies] = useState([]);
  const [tenants, setTenants] = useState([]);
  const [brokers, setBrokers] = useState([]);
  const [carriers, setCarriers] = useState([]);
  const [vehicles, setVehicles] = useState([]);
  const [selectedShipmentId, setSelectedShipmentId] = useState(filterShipmentId || null);
  const [selectedDriverId, setSelectedDriverId] = useState(null);
  const [selectedCompanyId, setSelectedCompanyId] = useState(null);
  const [selectedTenantId, setSelectedTenantId] = useState(null);
  const [selectedBrokerId, setSelectedBrokerId] = useState(null);
  const [selectedCarrierId, setSelectedCarrierId] = useState(null);
  const [selectedShipmentLive, setSelectedShipmentLive] = useState(null);
  const [loadingLive, setLoadingLive] = useState(false);
  const [liveError, setLiveError] = useState("");
  const [mapError, setMapError] = useState("");
  const [nowTs, setNowTs] = useState(() => Date.now());
  const wsRef = useRef(null);
  const hbRef = useRef(null);
  const reconnectRef = useRef(1000);

  const selectedDriver = useMemo(() => drivers.find((item) => String(item.id) === String(selectedDriverId)) || null, [drivers, selectedDriverId]);
  const selectedCompany = useMemo(() => companies.find((item) => String(item.id) === String(selectedCompanyId)) || null, [companies, selectedCompanyId]);
  const selectedTenant = useMemo(() => tenants.find((item) => String(item.id) === String(selectedTenantId)) || null, [tenants, selectedTenantId]);
  const selectedBroker = useMemo(() => brokers.find((item) => String(item.id) === String(selectedBrokerId)) || null, [brokers, selectedBrokerId]);
  const selectedCarrier = useMemo(() => carriers.find((item) => String(item.id) === String(selectedCarrierId)) || null, [carriers, selectedCarrierId]);

  const fetchMapData = async () => {
    setMapError("");
    try {
      const res = await axiosClient.get("/api/v1/unified/shipments", {
        params: { limit: filterShipmentId ? 500 : 100 },
      });
      const mapData = res?.data?.data || {};
      let realShipments = normalizeList(mapData.shipments || []);
      if (filterShipmentId) {
        const one = realShipments.find((x) => Number(x.id) === Number(filterShipmentId));
        if (!one) {
          const itemRes = await axiosClient.get(ITEM_URL(filterShipmentId)).catch(() => null);
          const single = itemRes?.data?.data || itemRes?.data || null;
          realShipments = single?.id ? [single] : [];
        } else {
          realShipments = [one];
        }
      }
      setShipments(realShipments);
      setDrivers((mapData.drivers || []).map(normalizeDriverEntity));
      setCompanies((mapData.companies || mapData.tenants || []).map(normalizeCompanyEntity));
      setTenants(mapData.tenants || []);
      setBrokers(mapData.brokers || []);
      setCarriers(mapData.carriers || []);
      setVehicles(mapData.vehicles || []);
      setSelectedShipmentId((current) => {
        if (filterShipmentId) return filterShipmentId;
        if (current && realShipments.some((item) => String(item.id) === String(current))) return current;
        return realShipments[0]?.id ?? null;
      });
      onTotalChange?.(realShipments.length);
      setSummary?.({
        on_the_way: realShipments.filter((item) => ["on_the_way", "in_transit"].includes(normalizeStatus(item.status))).length,
        delayed: realShipments.filter((item) => normalizeStatus(item.status).includes("delay")).length,
        delivered: realShipments.filter((item) => normalizeStatus(item.status).startsWith("deliver")).length,
      });
    } catch (err) {
      console.error("Failed to fetch map data:", err);
      const detail = err?.response?.data?.detail;
      setMapError(typeof detail === "string" ? detail : err?.message || "Unable to load shipment data.");
      setShipments([]);
      setDrivers([]);
      setCompanies([]);
      setTenants([]);
      setBrokers([]);
      setCarriers([]);
      setVehicles([]);
    }
  };

  const fetchLiveData = async (shipmentId) => {
    if (!shipmentId) return setSelectedShipmentLive(null);
    const selectedShipment = shipments.find((item) => String(item.id) === String(shipmentId));
    const fallback = buildFallbackLiveData(selectedShipment, drivers, companies, vehicles);
    setSelectedShipmentLive(fallback);
    setLoadingLive(true);
    setLiveError("");
    try {
      if (Number(shipmentId) >= 4000) return setSelectedShipmentLive(fallback);
      const liveData = await getShipmentLiveData(shipmentId);
      setSelectedShipmentLive({
        ...(fallback || {}),
        ...(liveData || {}),
        shipment: { ...(fallback?.shipment || {}), ...(liveData?.shipment || {}) },
        driver: { ...(fallback?.driver || {}), ...(liveData?.driver || {}) },
        vehicle: { ...(fallback?.vehicle || {}), ...(liveData?.vehicle || {}) },
      });
    } catch (error) {
      console.error("Failed to fetch live shipment data:", error);
      setSelectedShipmentLive(fallback);
      setLiveError(error?.message || "Unable to load live shipment details.");
    } finally {
      setLoadingLive(false);
    }
  };

  const connectWS = () => {
    if (!enableLive) return;
    try {
      const url = buildAuthWsUrl("/live");
      if (!url) return;
      const ws = new WebSocket(url);
      wsRef.current = ws;
      ws.onopen = () => {
        reconnectRef.current = 1000;
        ws.send(JSON.stringify({ type: "subscribe", channel: "events.load.created" }));
        ws.send(JSON.stringify({ type: "subscribe", channel: "events.ops.shipment_imported" }));
        if (hbRef.current) clearInterval(hbRef.current);
        hbRef.current = setInterval(() => {
          try { ws.send(JSON.stringify({ type: "ping" })); } catch {}
        }, 25000);
      };
      ws.onmessage = async (evt) => {
        let msg = null;
        try { msg = JSON.parse(evt.data); } catch { return; }
        const id = msg?.payload?.shipment_id || msg?.payload?.id;
        if (!id || (filterShipmentId && Number(id) !== Number(filterShipmentId))) return;
        await fetchMapData();
        if (String(selectedShipmentId) === String(id)) fetchLiveData(id);
      };
      ws.onclose = (event) => {
        if (hbRef.current) clearInterval(hbRef.current);
        if (isSocketUnauthorized(event)) return notifySocketUnauthorized(event);
        const delay = Math.min(reconnectRef.current, 15000);
        setTimeout(connectWS, delay);
        reconnectRef.current = Math.round(reconnectRef.current * 1.7);
      };
      ws.onerror = () => { try { ws.close(); } catch {} };
    } catch {
      const delay = Math.min(reconnectRef.current, 15000);
      setTimeout(connectWS, delay);
      reconnectRef.current = Math.round(reconnectRef.current * 1.7);
    }
  };

  useEffect(() => {
    fetchMapData();
    const refreshId = setInterval(fetchMapData, 30000);
    const tickerId = setInterval(() => setNowTs(Date.now()), 30000);
    connectWS();
    return () => {
      clearInterval(refreshId);
      clearInterval(tickerId);
      if (hbRef.current) clearInterval(hbRef.current);
      try { wsRef.current?.close(); } catch {}
    };
  }, [filterShipmentId, enableLive]);

  useEffect(() => { fetchLiveData(selectedShipmentId); }, [selectedShipmentId, shipments, drivers, companies, vehicles]);

  const handleSelectShipment = (shipmentId) => {
    setSelectedShipmentId(shipmentId);
    setSelectedDriverId(null);
    setSelectedCompanyId(null);
    setSelectedTenantId(null);
    setSelectedBrokerId(null);
    setSelectedCarrierId(null);
  };
  const handleSelectDriver = (driverId) => {
    setSelectedDriverId(driverId);
    setSelectedTenantId(null);
    setSelectedBrokerId(null);
    setSelectedCarrierId(null);
    const assignedShipment = shipments.find((item) => String(item.driver_id) === String(driverId));
    if (assignedShipment) setSelectedShipmentId(assignedShipment.id);
  };
  const handleSelectCompany = (companyId) => {
    setSelectedCompanyId(companyId);
    setSelectedTenantId(null);
    setSelectedBrokerId(null);
    setSelectedCarrierId(null);
    const companyShipment = shipments.find((item) => String(item.company_id) === String(companyId));
    if (companyShipment) setSelectedShipmentId(companyShipment.id);
  };
  const handleSelectTenant = (tenantId) => {
    setSelectedTenantId(tenantId);
    setSelectedDriverId(null);
    setSelectedCompanyId(null);
    setSelectedBrokerId(null);
    setSelectedCarrierId(null);
  };
  const handleSelectBroker = (brokerId) => {
    setSelectedBrokerId(brokerId);
    setSelectedDriverId(null);
    setSelectedCompanyId(null);
    setSelectedTenantId(null);
    setSelectedCarrierId(null);
  };
  const handleSelectCarrier = (carrierId) => {
    setSelectedCarrierId(carrierId);
    setSelectedDriverId(null);
    setSelectedCompanyId(null);
    setSelectedTenantId(null);
    setSelectedBrokerId(null);
  };

  if (mapError) {
    return (
      <div style={{ width: "100%", minHeight: 420, display: "grid", placeItems: "center", borderRadius: 18, border: "1px solid rgba(248,113,113,0.25)", background: "rgba(15,23,42,0.92)", color: "#e2e8f0", padding: 24, textAlign: "center" }}>
        <div style={{ maxWidth: 420 }}>
          <div style={{ fontSize: 28, marginBottom: 10 }}>⚠️</div>
          <div style={{ fontSize: 20, fontWeight: 800, marginBottom: 8 }}>Unable to Load Shipment Data</div>
          <div style={{ fontSize: 14, color: "#cbd5e1", marginBottom: 16 }}>{mapError}</div>
          <button type="button" onClick={fetchMapData} style={{ background: "#2563eb", color: "#fff", border: "none", borderRadius: 10, padding: "10px 16px", fontWeight: 700, cursor: "pointer" }}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", gap: 16, width: "100%", height: "600px", flexWrap: "wrap" }}>
      <div style={{ position: "relative", flex: "1 1 680px", minWidth: 0, height: "100%", borderRadius: 18, overflow: "hidden", border: "1px solid rgba(148,163,184,0.18)" }}>
        <div style={{ position: "absolute", top: 10, left: 10, zIndex: 1000, backgroundColor: "rgba(15,23,42,0.92)", padding: "10px 14px", borderRadius: 12, border: "1px solid rgba(148,163,184,0.18)", fontSize: 12, color: "#cbd5e1" }}>
          <div style={{ fontWeight: 700, color: "#f8fafc" }}>Unified North America + Gulf Map</div>
          <div style={{ marginTop: 2 }}>Shipments, tenants, brokers, carriers, and drivers are active.</div>
        </div>
        <MapContainer center={[39.8283, -98.5795]} zoom={4} style={{ width: "100%", height: "100%" }}>
          <FitMapToEntities shipments={shipments} marketRoutes={marketRoutes} drivers={drivers} companies={companies} tenants={tenants} brokers={brokers} carriers={carriers} />
          <LayersControl position="topright">
            <LayersControl.BaseLayer checked name="OpenStreetMap"><TileLayer attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" maxZoom={19} /></LayersControl.BaseLayer>
            <LayersControl.BaseLayer name="Satellite"><TileLayer url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}" attribution="Tiles &copy; Esri" /></LayersControl.BaseLayer>
            <LayersControl.Overlay checked name="Tenants">
              <>
                {tenants.map((tenant) => tenant?.location?.lat && tenant?.location?.lng ? <Marker key={`tenant-${tenant.id}`} position={[tenant.location.lat, tenant.location.lng]} icon={tenantIcon} eventHandlers={{ click: () => handleSelectTenant(tenant.id) }}><Popup><strong>{tenant.name}</strong><div>{tenant.location.city || "Unknown"}{tenant.location.state ? `, ${tenant.location.state}` : ""}</div><div>{tenant.contact?.phone || "N/A"}</div><div>Active shipments: {tenant.stats?.active_shipments ?? "N/A"}</div></Popup></Marker> : null)}
              </>
            </LayersControl.Overlay>
            <LayersControl.Overlay checked name="Brokers">
              <>
                {brokers.map((broker) => broker?.location?.lat && broker?.location?.lng ? <Marker key={`broker-${broker.id}`} position={[broker.location.lat, broker.location.lng]} icon={brokerIcon} eventHandlers={{ click: () => handleSelectBroker(broker.id) }}><Popup><strong>{broker.name}</strong><div>{broker.location.city || "Unknown"}{broker.location.state ? `, ${broker.location.state}` : ""}</div><div>{broker.contact?.phone || "N/A"}</div><div>Active loads: {broker.stats?.active_loads ?? "N/A"}</div></Popup></Marker> : null)}
              </>
            </LayersControl.Overlay>
            <LayersControl.Overlay checked name="Carriers">
              <>
                {carriers.map((carrier) => carrier?.location?.lat && carrier?.location?.lng ? <Marker key={`carrier-${carrier.id}`} position={[carrier.location.lat, carrier.location.lng]} icon={carrierIcon} eventHandlers={{ click: () => handleSelectCarrier(carrier.id) }}><Popup><strong>{carrier.name}</strong><div>{carrier.location.city || "Unknown"}{carrier.location.state ? `, ${carrier.location.state}` : ""}</div><div>{carrier.contact?.phone || "N/A"}</div><div>Fleet: {carrier.stats?.fleet_size ?? "N/A"}</div></Popup></Marker> : null)}
              </>
            </LayersControl.Overlay>
            <LayersControl.Overlay checked name="Shipments">
              <>
                {shipments.map((shipment) => {
                  const pickup = getPickupCoords(shipment);
                  const dropoff = getDropoffCoords(shipment);
                  const current = getCurrentCoords(shipment);
                  const route = buildShipmentRoute(shipment);
                  return <React.Fragment key={`shipment-${shipment.id}`}>
                    <Marker position={pickup} icon={startIcon} eventHandlers={{ click: () => handleSelectShipment(shipment.id) }}><Popup><strong>Pickup</strong><div>{getPickupLabel(shipment)}</div><div>Shipment: {getShipmentLabel(shipment)}</div></Popup></Marker>
                    <Marker position={dropoff} icon={endIcon} eventHandlers={{ click: () => handleSelectShipment(shipment.id) }}><Popup><strong>Destination</strong><div>{getDropoffLabel(shipment)}</div><div>Status: {shipment.status || "unknown"}</div></Popup></Marker>
                    {current ? <Marker position={current} icon={truckIcon} eventHandlers={{ click: () => handleSelectShipment(shipment.id) }}><Popup><strong>Truck Position</strong><div>{shipment.current_location?.description || "Live position"}</div><div>Shipment: {getShipmentLabel(shipment)}</div></Popup></Marker> : null}
                    <Polyline positions={route} pathOptions={{ color: statusColor(shipment.status), weight: String(selectedShipmentId) === String(shipment.id) ? 5 : 3, opacity: 0.85 }} eventHandlers={{ click: () => handleSelectShipment(shipment.id) }} />
                  </React.Fragment>;
                })}
              </>
            </LayersControl.Overlay>
            <LayersControl.Overlay checked name="Drivers">
              <>
                {drivers.map((driver) => driver?.current_location?.lat && driver?.current_location?.lng ? <Marker key={`driver-${driver.id}`} position={[driver.current_location.lat, driver.current_location.lng]} icon={normalizeStatus(driver.status) === "available" ? driverAvailableIcon : driverBusyIcon} eventHandlers={{ click: () => handleSelectDriver(driver.id) }}><Popup><strong>{driver.name || driver.full_name || driver.email}</strong><div>{driver.current_location.city}, {driver.current_location.state}</div><div>Status: {driver.status || "unknown"}</div><div>Trips: {driver.completed_trips ?? "N/A"}</div></Popup></Marker> : null)}
              </>
            </LayersControl.Overlay>
            <LayersControl.Overlay checked name="Companies">
              <>
                {companies.map((company) => company?.headquarters?.lat && company?.headquarters?.lng ? <Marker key={`company-${company.id}`} position={[company.headquarters.lat, company.headquarters.lng]} icon={companyIcon} eventHandlers={{ click: () => handleSelectCompany(company.id) }}><Popup><strong>{company.name}</strong><div>{company.headquarters.city || "Unknown"}{company.headquarters.state ? `, ${company.headquarters.state}` : ""}</div><div>Fleet: {company.fleet_size ?? "N/A"}</div><div>Phone: {company.phone || "N/A"}</div></Popup></Marker> : null)}
              </>
            </LayersControl.Overlay>
            {marketRoutes.length > 0 ? <LayersControl.Overlay checked name="Market Routes"><>{marketRoutes.map((route, index) => route?.originCoords && route?.destinationCoords ? <React.Fragment key={`market-route-${route.id || index}`}><Polyline positions={[route.originCoords, route.destinationCoords]} color="#8B5CF6" weight={4} opacity={0.85} /><Circle center={route.originCoords} radius={12000} pathOptions={{ color: "#8B5CF6", fillColor: "#8B5CF6", fillOpacity: 0.15 }} /></React.Fragment> : null)}</></LayersControl.Overlay> : null}
          </LayersControl>
        </MapContainer>
      </div>
      <ShipmentSidebar shipments={shipments} drivers={drivers} companies={companies} tenants={tenants} brokers={brokers} carriers={carriers} selectedShipmentId={selectedShipmentId} selectedLiveData={selectedShipmentLive} selectedDriver={selectedDriver} selectedCompany={selectedCompany} selectedTenant={selectedTenant} selectedBroker={selectedBroker} selectedCarrier={selectedCarrier} loadingLive={loadingLive} liveError={liveError} onSelectShipment={handleSelectShipment} onSelectDriver={handleSelectDriver} onSelectCompany={handleSelectCompany} onSelectTenant={handleSelectTenant} onSelectBroker={handleSelectBroker} onSelectCarrier={handleSelectCarrier} marketRoutes={marketRoutes} nowTs={nowTs} />
    </div>
  );
};

export default UnifiedShipmentMap;
