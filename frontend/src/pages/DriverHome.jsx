import React, { useEffect, useMemo, useRef, useState } from "react";
import {
  getDriverShipments,
  postDriverCheckpoint,
  postDriverLocation,
} from "../services/driverApi";

const CHECKPOINTS = [
  { key: "arrived_pickup", label: "Arrived Pickup" },
  { key: "loaded", label: "Loaded" },
  { key: "departed_pickup", label: "Departed / In Transit" },
  { key: "arrived_dropoff", label: "Arrived Dropoff" },
  { key: "delivered", label: "Delivered" },
];

const DriverHome = () => {
  const [shipments, setShipments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [tracking, setTracking] = useState(false);
  const watchRef = useRef<number | null>(null);

  const fetchShipments = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await getDriverShipments();
      setShipments(data || []);
    } catch (err) {
      setError("Unable to load shipments.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchShipments();
  }, []);

  const handleCheckpoint = async (shipmentId, type) => {
    try {
      await postDriverCheckpoint(shipmentId, { type });
      await fetchShipments();
    } catch (err) {
      setError("Failed to update checkpoint.");
    }
  };

  const handleStartTracking = () => {
    if (!("geolocation" in navigator)) {
      setError("Geolocation is unavailable.");
      return;
    }

    if (tracking) {
      if (watchRef.current !== null) {
        navigator.geolocation.clearWatch(watchRef.current);
      }
      setTracking(false);
      return;
    }

    const id = navigator.geolocation.watchPosition(
      async (position) => {
        try {
          await postDriverLocation({
            shipment_id: shipments[0]?.id,
            lat: position.coords.latitude,
            lng: position.coords.longitude,
            accuracy: position.coords.accuracy,
            speed: position.coords.speed,
            heading: position.coords.heading,
          });
        } catch {
          // ignore
        }
      },
      () => {
        setError("Unable to fetch location.");
      },
      { enableHighAccuracy: true, maximumAge: 15000, timeout: 10000 }
    );
    watchRef.current = id;
    setTracking(true);
  };

  useEffect(() => {
    return () => {
      if (watchRef.current !== null) {
        navigator.geolocation.clearWatch(watchRef.current);
      }
    };
  }, []);

  const renderShipments = useMemo(() => {
    return shipments.map((shipment) => (
      <div key={shipment.id} className="border border-gray-200 rounded-lg p-4 space-y-3 bg-white shadow-sm">
        <div className="flex justify-between text-sm">
          <span className="font-semibold">#{shipment.id}</span>
          <span className="text-gray-500">{shipment.status}</span>
        </div>
        <p className="text-xs text-gray-600">
          {shipment.pickup_location} → {shipment.dropoff_location}
        </p>
        <div className="grid grid-cols-2 gap-2">
          {CHECKPOINTS.map((checkpoint) => (
            <button
              key={checkpoint.key}
              onClick={() => handleCheckpoint(shipment.id, checkpoint.key)}
              className="px-2 py-1 rounded bg-blue-600 text-white text-xs font-semibold"
            >
              {checkpoint.label}
            </button>
          ))}
        </div>
        {shipment.last_location ? (
          <p className="text-xs text-gray-500">
            Last seen {new Date(shipment.last_location.recorded_at).toLocaleTimeString()}
          </p>
        ) : null}
      </div>
    ));
  }, [shipments]);

  return (
    <div className="p-6 space-y-6">
      <header className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold">Driver Console</h1>
          <p className="text-sm text-gray-500">Update checkpoints and share your location.</p>
        </div>
        <button
          onClick={handleStartTracking}
          className={`px-4 py-2 text-sm rounded ${
            tracking ? "bg-red-600 text-white" : "bg-emerald-600 text-white"
          }`}
        >
          {tracking ? "Stop Tracking" : "Start Tracking"}
        </button>
      </header>

      {error && <div className="text-sm text-red-600">{error}</div>}

      {loading ? (
        <p className="text-sm text-gray-500">Loading your assignments...</p>
      ) : shipments.length === 0 ? (
        <p className="text-sm text-gray-400">No shipments assigned right now.</p>
      ) : (
        <div className="space-y-4">{renderShipments}</div>
      )}
    </div>
  );
};

export default DriverHome;
