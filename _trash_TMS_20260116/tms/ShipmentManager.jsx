
import React from "react";
import ShipmentCard from "../../components/tms/ShipmentCard.jsx";
import Timeline from "../../components/tms/Timeline.jsx";
import AISuggestions from "../../components/tms/AISuggestions.jsx";
import LiveMap from "../../components/tms/LiveMap.jsx";

// Temporary fake data
const mockShipments = [
    {
        id: 1,
        status: "active",
        origin: "Riyadh",
        destination: "Jeddah",
        driver: "Sami Al-Otaibi",
        events: [
            { title: "Created", timestamp: "2026-01-10 09:00", description: "The shipment has been created." },
            { title: "Loaded", timestamp: "2026-01-10 10:30", description: "The goods have been loaded." },
        ],
        suggestions: ["Expediting delivery due to an urgent request.", "Checking the driver's condition before setting off."],
        locations: [{ lat: 24.7136, lng: 46.6753 }],
    },
];

export default function ShipmentManager() {
    return (
        <div className="shipment-manager-page">
            <h2>Shipment Management</h2>
            {mockShipments.map((shipment) => (
                <div key={shipment.id} style={{ marginBottom: 32 }}>
                    <ShipmentCard shipment={shipment} />
                    <LiveMap locations={shipment.locations} />
                    <Timeline events={shipment.events} />
                    <AISuggestions suggestions={shipment.suggestions} />
                </div>
            ))}
        </div>
    );
}
