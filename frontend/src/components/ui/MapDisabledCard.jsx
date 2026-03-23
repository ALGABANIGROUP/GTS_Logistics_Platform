import React from "react";
import { MapPin, AlertTriangle, Settings, Eye } from "lucide-react";

export default function MapDisabledCard({
    title = "Live Map",
    reason = "Map service is disabled until the provider/API key is configured.",
    status = "disabled",
    onConfigure,
    onGoToShipments
}) {
    return (
        <div className="map-disabled-card glass-card">
            <div className="map-disabled-header">
                <MapPin size={24} className="map-icon" />
                <h3>{title}</h3>
            </div>
            <div className="map-disabled-body">
                <AlertTriangle size={48} className="warning-icon" />
                <p>{reason}</p>
                <p className="map-disabled-note">
                    This feature will be available after configuring the map provider in settings.
                </p>
            </div>
            <div className="map-disabled-footer">
                <button
                    className="glass-button small"
                    onClick={onConfigure}
                >
                    <Settings size={16} />
                    Configure Map
                </button>
                <button
                    className="glass-button small secondary"
                    onClick={onGoToShipments}
                >
                    <Eye size={16} />
                    View Shipments
                </button>
            </div>
        </div>
    );
}
