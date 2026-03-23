// frontend/src/GoogleMapFeatures.js
import React, { useEffect, useRef } from "react";

/**
 * GoogleMapFeatures component
 * Renders a map and displays shipment locations with markers and optional route lines
 * @param {Object[]} shipments - List of shipments with lat/lng
 * @param {boolean} drawRoutes - Whether to draw polyline between pickup and dropoff
 */
const GoogleMapFeatures = ({ shipments = [], drawRoutes = true }) => {
  const mapRef = useRef(null);
  const mapInstance = useRef(null);

  useEffect(() => {
    if (!window.google || !window.google.maps) {
      console.error("❌ Google Maps API not loaded");
      return;
    }

    const map = new window.google.maps.Map(mapRef.current, {
      center: { lat: 39.5, lng: -98.35 }, // Default center of USA
      zoom: 4,
    });

    mapInstance.current = map;

    // Add shipment markers
    shipments.forEach((shipment) => {
      const { pickup_location, dropoff_location } = shipment;

      if (pickup_location && dropoff_location) {
        const pickup = new window.google.maps.LatLng(pickup_location.lat, pickup_location.lng);
        const dropoff = new window.google.maps.LatLng(dropoff_location.lat, dropoff_location.lng);

        new window.google.maps.Marker({
          position: pickup,
          map,
          label: "P",
          title: `Pickup: ${shipment.pickup_location_text}`,
        });

        new window.google.maps.Marker({
          position: dropoff,
          map,
          label: "D",
          title: `Dropoff: ${shipment.dropoff_location_text}`,
        });

        // Draw line between pickup and dropoff
        if (drawRoutes) {
          new window.google.maps.Polyline({
            path: [pickup, dropoff],
            geodesic: true,
            strokeColor: "#1e88e5",
            strokeOpacity: 0.8,
            strokeWeight: 3,
            map,
          });
        }
      }
    });
  }, [shipments, drawRoutes]);

  return <div ref={mapRef} className="w-full h-[600px] rounded shadow" />;
};

export default GoogleMapFeatures;
// Note: Ensure to load the Google Maps JavaScript API in your HTML or index.js file
// Example: <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyAsXLhtkKaS0SxmAyAbLz3bgxK2DOC5QAQ"></script>