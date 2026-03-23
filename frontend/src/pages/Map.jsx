import React, { useMemo } from "react";
import { useLocation, useSearchParams } from "react-router-dom";
import UnifiedShipmentMap from "../components/UnifiedShipmentMap";

const MARKET_ROUTES_STORAGE_KEY = "freight_broker_market_routes";

const CITY_COORDINATES = {
  toronto: [43.6532, -79.3832],
  montreal: [45.5017, -73.5673],
  vancouver: [49.2827, -123.1207],
  calgary: [51.0447, -114.0719],
  edmonton: [53.5461, -113.4938],
  winnipeg: [49.8951, -97.1384],
  halifax: [44.6488, -63.5752],
  windsor: [42.3149, -83.0364],
  kamloops: [50.6745, -120.3273],
  thunder_bay: [48.3809, -89.2477],
  sept_iles: [50.2001, -66.3821],
};

const normalizeCityKey = (value = "") =>
  String(value)
    .trim()
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/,\s*[a-z.\s]+$/i, "")
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "");

const splitRoute = (routeName = "") => {
  const parts = String(routeName)
    .split(/\s*-\s*/)
    .map((part) => part.trim())
    .filter(Boolean);

  if (parts.length >= 2) {
    return { origin: parts[0], destination: parts[1] };
  }

  return { origin: "", destination: "" };
};

const readStoredRoutes = () => {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.sessionStorage.getItem(MARKET_ROUTES_STORAGE_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
};

const toMarketRoute = (route, index) => {
  const routeName = route?.route || route?.name || "";
  const parsed = splitRoute(routeName);
  const origin = route?.origin || parsed.origin;
  const destination = route?.destination || parsed.destination;
  const originCoords = CITY_COORDINATES[normalizeCityKey(origin)];
  const destinationCoords = CITY_COORDINATES[normalizeCityKey(destination)];

  if (!originCoords || !destinationCoords) return null;

  return {
    id: route?.id || `${routeName || "route"}-${index}`,
    route: routeName,
    name: routeName,
    origin,
    destination,
    originLabel: origin,
    destinationLabel: destination,
    originCoords,
    destinationCoords,
  };
};

const Map = () => {
  const [params] = useSearchParams();
  const location = useLocation();
  const shipmentId = Number(params.get("shipment_id") || 0) || undefined;

  const marketRoutes = useMemo(() => {
    const stateRoutes = Array.isArray(location.state?.marketRoutes)
      ? location.state.marketRoutes
      : [];
    const sourceRoutes = stateRoutes.length > 0 ? stateRoutes : readStoredRoutes();

    return sourceRoutes
      .map((route, index) => toMarketRoute(route, index))
      .filter(Boolean);
  }, [location.state]);

  return (
    <div className="p-6">
      <h2 className="mb-4 text-xl font-bold">
        {shipmentId ? `Shipment #${shipmentId} Map View` : "Logistics Map View"}
      </h2>
      <div className="w-full h-[600px] rounded-xl overflow-hidden shadow">
        <UnifiedShipmentMap
          filterShipmentId={shipmentId}
          marketRoutes={marketRoutes}
          enableLive
        />
      </div>
    </div>
  );
};

export default Map;
