
import React from "react";

// Fake data for drivers
const mockDrivers = [
    { id: 1, name: "Sami Al-Otaibi", status: "available" },
    { id: 2, name: "Muhammad Al-Ghamdi", status: "On assignment" },
];

export default function DriverManagement() {
    return (
        <div className="driver-management-page">
            <h2>Driver Management</h2>
            <ul>
                {mockDrivers.map((driver) => (
                    <li key={driver.id} style={{ marginBottom: 12, padding: 8, background: "#f5f5f5", borderRadius: 8 }}>
                        <strong>{driver.name}</strong> - <span style={{ color: driver.status === "available" ? "green" : "orange" }}>{driver.status}</span>
                    </li>
                ))}
            </ul>
        </div>
    );
}
