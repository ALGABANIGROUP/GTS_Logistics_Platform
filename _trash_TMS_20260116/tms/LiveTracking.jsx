
import React from "react";
import LiveMap from "../../components/tms/LiveMap.jsx";

export default function LiveTracking() {
    // Fake data for truck locations
    const truckLocations = [
        { lat: 24.7136, lng: 46.6753, name: "Truck 1" },
        { lat: 21.3891, lng: 39.8579, name: "Truck 2" },
    ];

    return (
        <div className="live-tracking-page">
            <h2>Live Truck Tracking</h2>
            <LiveMap locations={truckLocations} />
            <ul>
                {truckLocations.map((loc, idx) => (
                    <li key={idx}>{loc.name}: ({loc.lat}, {loc.lng})</li>
                ))}
            </ul>
        </div>
    );
}
