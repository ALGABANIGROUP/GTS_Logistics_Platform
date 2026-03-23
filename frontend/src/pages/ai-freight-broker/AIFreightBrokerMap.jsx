import React from "react";
import MapDisabledCard from "../../components/ui/MapDisabledCard";

export default function AIFreightBrokerMap() {
    return (
        <div className="ai-freight-broker-map">
            <div className="page-header">
                <h1>Freight Map</h1>
                <p>Track shipments and routes on the interactive map</p>
            </div>

            <div className="map-content">
                <MapDisabledCard />
            </div>
        </div>
    );
}