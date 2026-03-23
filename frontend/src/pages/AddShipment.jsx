// frontend/src/pages/AddShipment.jsx
import React, { useState } from "react";
import axiosClient from "../api/axiosClient";
import { useCurrencyStore } from "../stores/useCurrencyStore";

export default function AddShipment() {
  const { currency, currencySymbol } = useCurrencyStore();
  const [form, setForm] = useState({
    pickup_location: "",
    dropoff_location: "",
    status: "Pending",
    rate: "",
    description: "",
  });
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState("");

  const onChange = (e) => setForm((p) => ({ ...p, [e.target.name]: e.target.value }));

  const geocodeIfPossible = async (address) => {
    const key = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;
    if (!key || !address) return null;
    try {
      const url = `https://maps.googleapis.com/maps/api/geocode/json?address=${encodeURIComponent(address)}&key=${key}`;
      const res = await fetch(url);
      const data = await res.json();
      return data?.results?.[0]?.geometry?.location || null;
    } catch {
      return null;
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setMessage("");

    try {
      // Optional geocoding (pickup + dropoff)
      const pickupCoords = await geocodeIfPossible(form.pickup_location);
      const dropoffCoords = await geocodeIfPossible(form.dropoff_location);

      const payload = {
        pickup_location: form.pickup_location,
        dropoff_location: form.dropoff_location,
        status: form.status || "Pending",
        rate: form.rate ? Number(form.rate) : undefined,
        description: form.description || undefined,
        latitude: pickupCoords?.lat ?? undefined,
        longitude: pickupCoords?.lng ?? undefined,
        dropoff_lat: dropoffCoords?.lat ?? undefined,
        dropoff_lng: dropoffCoords?.lng ?? undefined,
      };

      const res = await axiosClient.post("/api/v1/shipments/shipments/", payload);
      const data = res?.data || {};

      if (res?.status >= 200 && res?.status < 300) {
        setMessage("✅ Shipment added successfully!");
        setForm({
          pickup_location: "",
          dropoff_location: "",
          status: "Pending",
          rate: "",
          description: "",
        });
      } else {
        setMessage(`❌ Failed: ${data?.detail || "Unknown error"}`);
      }
    } catch (error) {
      console.error(error);
      setMessage("❌ Error submitting the form");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="p-6 max-w-xl mx-auto">
      <h2 className="text-xl font-bold mb-4">Add Shipment</h2>
      <form onSubmit={handleSubmit} className="space-y-3">
        <input
          className="border rounded p-2 w-full"
          name="pickup_location"
          placeholder="Pickup Location"
          value={form.pickup_location}
          onChange={onChange}
          required
        />
        <input
          className="border rounded p-2 w-full"
          name="dropoff_location"
          placeholder="Dropoff Location"
          value={form.dropoff_location}
          onChange={onChange}
          required
        />
        <input
          className="border rounded p-2 w-full"
          name="rate"
          placeholder={`Rate (${currencySymbol} ${currency})`}
          value={form.rate}
          onChange={onChange}
        />
        <textarea
          className="border rounded p-2 w-full"
          name="description"
          placeholder="Notes/Description"
          value={form.description}
          onChange={onChange}
        />
        <button
          disabled={submitting}
          className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-60"
          type="submit"
        >
          {submitting ? "Submitting..." : "Add Shipment"}
        </button>
      </form>
      {message && <p className="mt-3 text-sm">{message}</p>}
    </div>
  );
}
