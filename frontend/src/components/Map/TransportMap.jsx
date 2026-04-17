import React, { useEffect, useState, useCallback } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, Circle, LayersControl } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';
import './TransportMap.css';

// Fix Leaflet icon issue in React
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: markerIcon2x,
    iconUrl: markerIcon,
    shadowUrl: markerShadow,
});

// Custom icons for transportation
const truckIcon = new L.Icon({
    iconUrl: 'https://cdn-icons-png.flaticon.com/512/684/684908.png',
    iconSize: [40, 40],
    iconAnchor: [20, 40],
    popupAnchor: [0, -40]
});

const shipmentIcon = new L.Icon({
    iconUrl: 'https://cdn-icons-png.flaticon.com/512/3481/3481072.png',
    iconSize: [35, 35],
    iconAnchor: [17, 35],
    popupAnchor: [0, -35]
});

const warehouseIcon = new L.Icon({
    iconUrl: 'https://cdn-icons-png.flaticon.com/512/2910/2910769.png',
    iconSize: [40, 40],
    iconAnchor: [20, 40],
    popupAnchor: [0, -40]
});

const TransportMap = ({ shipments = [], trucks = [] }) => {
    const [center, setCenter] = useState([39.8283, -98.5795]); // USA center
    const [zoom, setZoom] = useState(4);
    const [selectedTruck, setSelectedTruck] = useState(null);
    const [selectedShipment, setSelectedShipment] = useState(null);

    // Default seed data for previews
    const defaultShipments = [
        {
            id: 1,
            name: 'Medical Supplies - Hospital Chain',
            status: 'in_transit',
            from: [40.7128, -74.0060], // NYC
            to: [34.0522, -118.2437], // LA
            currentLocation: [35.5353, -97.4867], // Oklahoma City
            driver: 'John Smith',
            estimatedArrival: '2025-02-08T16:00:00',
            weight: '500 kg',
            value: '$25,000',
            progress: 65
        },
        {
            id: 2,
            name: 'Electronic Components - Factory',
            status: 'in_transit',
            from: [41.8781, -87.6298], // Chicago
            to: [33.7490, -84.3880], // Atlanta
            currentLocation: [35.0895, -85.2779], // Nashville
            driver: 'Maria Garcia',
            estimatedArrival: '2025-02-07T12:00:00',
            weight: '300 kg',
            value: '$45,000',
            progress: 45
        },
        {
            id: 3,
            name: 'Chemical Containers - Distribution',
            status: 'in_transit',
            from: [47.6062, -122.3321], // Seattle
            to: [37.3382, -121.8863], // San Jose
            currentLocation: [44.0521, -123.0351], // Portland
            driver: 'Robert Johnson',
            estimatedArrival: '2025-02-09T14:00:00',
            weight: '800 kg',
            value: '$35,000',
            progress: 30
        }
    ];

    const defaultTrucks = [
        {
            id: 1,
            license: 'TX-4821',
            status: 'moving',
            currentLocation: [35.5353, -97.4867],
            driver: 'John Smith',
            speed: 65,
            heading: 45,
            lastUpdate: new Date().toISOString(),
            shipmentId: 1
        },
        {
            id: 2,
            license: 'GA-7293',
            status: 'moving',
            currentLocation: [35.0895, -85.2779],
            driver: 'Maria Garcia',
            speed: 72,
            heading: 120,
            lastUpdate: new Date().toISOString(),
            shipmentId: 2
        },
        {
            id: 3,
            license: 'CA-5612',
            status: 'moving',
            currentLocation: [44.0521, -123.0351],
            driver: 'Robert Johnson',
            speed: 58,
            heading: 180,
            lastUpdate: new Date().toISOString(),
            shipmentId: 3
        }
    ];

    const displayShipments = shipments.length > 0 ? shipments : defaultShipments;
    const displayTrucks = trucks.length > 0 ? trucks : defaultTrucks;

    // Handle location change
    const handleLocationChange = useCallback((lat, lng) => {
        setCenter([lat, lng]);
        setZoom(10);
    }, []);

    const getStatusColor = (status) => {
        switch (status) {
            case 'delivered': return 'green';
            case 'in_transit': return 'blue';
            case 'pending': return 'orange';
            case 'delayed': return 'red';
            default: return 'gray';
        }
    };

    const getStatusLabel = (status) => {
        const labels = {
            'in_transit': 'In Transit',
            'delivered': 'Delivered',
            'pending': 'Pending',
            'delayed': 'Delayed'
        };
        return labels[status] || status;
    };

    return (
        <div className="transport-map-container">
            <div className="map-controls">
                <div className="control-group">
                    <button onClick={() => setZoom(zoom + 1)} title="Zoom In">+</button>
                    <button onClick={() => setZoom(zoom - 1)} title="Zoom Out">−</button>
                </div>
                <div className="control-group">
                    <select onChange={(e) => {
                        const coords = JSON.parse(e.target.value);
                        handleLocationChange(coords[0], coords[1]);
                    }}>
                        <option value="[39.8283, -98.5795]">USA Center</option>
                        <option value="[40.7128, -74.0060]">New York</option>
                        <option value="[34.0522, -118.2437]">Los Angeles</option>
                        <option value="[41.8781, -87.6298]">Chicago</option>
                        <option value="[34.0522, -118.2437]">Houston</option>
                    </select>
                </div>
            </div>

            <MapContainer
                center={center}
                zoom={zoom}
                style={{ height: '600px', width: '100%', borderRadius: '8px' }}
            >
                <LayersControl position="topright">
                    <LayersControl.BaseLayer checked name="OpenStreetMap">
                        <TileLayer
                            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        />
                    </LayersControl.BaseLayer>

                    <LayersControl.BaseLayer name="Satellite">
                        <TileLayer
                            url="http://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}"
                            attribution="Google Maps"
                        />
                    </LayersControl.BaseLayer>

                    {/* Trucks Layer */}
                    <LayersControl.Overlay name="Trucks" checked>
                        {displayTrucks.map(truck => (
                            <Marker
                                key={truck.id}
                                position={truck.currentLocation}
                                icon={truckIcon}
                                eventHandlers={{
                                    click: () => {
                                        setSelectedTruck(truck);
                                        handleLocationChange(truck.currentLocation[0], truck.currentLocation[1]);
                                    }
                                }}
                            >
                                <Popup>
                                    <div className="truck-popup">
                                        <h4>Truck {truck.license}</h4>
                                        <p><strong>Driver:</strong> {truck.driver}</p>
                                        <p><strong>Status:</strong> {truck.status}</p>
                                        <p><strong>Speed:</strong> {truck.speed} mph</p>
                                        <p><strong>Heading:</strong> {truck.heading}°</p>
                                    </div>
                                </Popup>
                            </Marker>
                        ))}
                    </LayersControl.Overlay>

                    {/* Shipments Layer */}
                    <LayersControl.Overlay name="Shipments" checked>
                        {displayShipments.map(shipment => (
                            <React.Fragment key={shipment.id}>
                                {/* Origin Marker */}
                                <Marker
                                    position={shipment.from}
                                    icon={warehouseIcon}
                                    eventHandlers={{
                                        click: () => {
                                            setSelectedShipment(shipment);
                                            handleLocationChange(shipment.from[0], shipment.from[1]);
                                        }
                                    }}
                                >
                                    <Popup>
                                        <div className="shipment-popup">
                                            <h4>Origin</h4>
                                            <p><strong>Shipment:</strong> {shipment.name}</p>
                                            <p><strong>Status:</strong> {getStatusLabel(shipment.status)}</p>
                                        </div>
                                    </Popup>
                                </Marker>

                                {/* Destination Marker */}
                                <Marker
                                    position={shipment.to}
                                    icon={warehouseIcon}
                                >
                                    <Popup>
                                        <div className="shipment-popup">
                                            <h4>Destination</h4>
                                            <p><strong>Shipment:</strong> {shipment.name}</p>
                                        </div>
                                    </Popup>
                                </Marker>

                                {/* Route Line */}
                                <Polyline
                                    positions={[shipment.from, shipment.currentLocation || shipment.to]}
                                    color={getStatusColor(shipment.status)}
                                    weight={3}
                                    opacity={0.7}
                                />

                                {/* Current Location Circle */}
                                <Circle
                                    center={shipment.currentLocation || shipment.to}
                                    radius={5000}
                                    color={getStatusColor(shipment.status)}
                                    fill
                                    fillColor={getStatusColor(shipment.status)}
                                    fillOpacity={0.3}
                                >
                                    <Popup>
                                        <div className="shipment-popup">
                                            <h4>Current Location</h4>
                                            <p><strong>Shipment:</strong> {shipment.name}</p>
                                            <p><strong>Progress:</strong> {shipment.progress || 0}%</p>
                                            <p><strong>ETA:</strong> {new Date(shipment.estimatedArrival).toLocaleDateString()}</p>
                                        </div>
                                    </Popup>
                                </Circle>
                            </React.Fragment>
                        ))}
                    </LayersControl.Overlay>
                </LayersControl>
            </MapContainer>

            {/* Sidebar Information */}
            <div className="map-sidebar">
                <h3>Transport Tracking Dashboard</h3>

                <div className="stats">
                    <div className="stat-item">
                        <span className="stat-label">Active Trucks</span>
                        <span className="stat-value">{displayTrucks.length}</span>
                    </div>
                    <div className="stat-item">
                        <span className="stat-label">In Transit</span>
                        <span className="stat-value">{displayShipments.filter(s => s.status === 'in_transit').length}</span>
                    </div>
                    <div className="stat-item">
                        <span className="stat-label">Delivered</span>
                        <span className="stat-value">{displayShipments.filter(s => s.status === 'delivered').length}</span>
                    </div>
                </div>

                {selectedTruck && (
                    <div className="selected-item">
                        <h4>Selected Truck</h4>
                        <p><strong>License:</strong> {selectedTruck.license}</p>
                        <p><strong>Driver:</strong> {selectedTruck.driver}</p>
                        <p><strong>Status:</strong> <span className="status-badge">{selectedTruck.status}</span></p>
                        <p><strong>Speed:</strong> {selectedTruck.speed} mph</p>
                        <button onClick={() => setSelectedTruck(null)}>Clear</button>
                    </div>
                )}

                {selectedShipment && (
                    <div className="selected-item">
                        <h4>Selected Shipment</h4>
                        <p><strong>Name:</strong> {selectedShipment.name}</p>
                        <p><strong>Status:</strong> <span className="status-badge">{getStatusLabel(selectedShipment.status)}</span></p>
                        <p><strong>Progress:</strong> {selectedShipment.progress || 0}%</p>
                        <p><strong>Value:</strong> {selectedShipment.value}</p>
                        <p><strong>ETA:</strong> {new Date(selectedShipment.estimatedArrival).toLocaleString()}</p>
                        <button onClick={() => setSelectedShipment(null)}>Clear</button>
                    </div>
                )}

                <div className="legend">
                    <h4>Status Colors</h4>
                    <div className="legend-item"><span className="legend-color" style={{ backgroundColor: 'blue' }}></span> In Transit</div>
                    <div className="legend-item"><span className="legend-color" style={{ backgroundColor: 'green' }}></span> Delivered</div>
                    <div className="legend-item"><span className="legend-color" style={{ backgroundColor: 'orange' }}></span> Pending</div>
                    <div className="legend-item"><span className="legend-color" style={{ backgroundColor: 'red' }}></span> Delayed</div>
                </div>
            </div>
        </div>
    );
};

export default TransportMap;
