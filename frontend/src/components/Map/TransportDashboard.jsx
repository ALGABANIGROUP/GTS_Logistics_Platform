import React, { useState, useEffect } from 'react';
import TransportMap from './TransportMap';
import './TransportDashboard.css';

const TransportDashboard = () => {
    const [shipments, setShipments] = useState([]);
    const [trucks, setTrucks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all');
    const [stats, setStats] = useState({
        total_shipments: 0,
        in_transit: 0,
        delivered: 0,
        pending: 0,
        active_trucks: 0,
        avg_speed: 0
    });

    useEffect(() => {
        fetchTransportData();
        const interval = setInterval(fetchTransportData, 30000);
        return () => clearInterval(interval);
    }, [filter]);

    const fetchTransportData = async () => {
        try {
            // Try to fetch from API
            const [shipmentsRes, trucksRes] = await Promise.all([
                fetch('http://localhost:8000/api/v1/transport/shipments'),
                fetch('http://localhost:8000/api/v1/transport/trucks')
            ]);

            if (shipmentsRes.ok && trucksRes.ok) {
                const shipmentsData = await shipmentsRes.json();
                const trucksData = await trucksRes.json();
                setShipments(shipmentsData);
                setTrucks(trucksData);
            } else {
                setShipments(getMockShipments());
                setTrucks(getMockTrucks());
            }
            setLoading(false);
        } catch (error) {
            console.warn('Using mock data:', error);
            setShipments(getMockShipments());
            setTrucks(getMockTrucks());
            setLoading(false);
        }
    };

    const getMockShipments = () => [
        {
            id: 1,
            name: 'Medical Supplies - Hospital Chain',
            status: 'in_transit',
            from: [40.7128, -74.0060],
            to: [34.0522, -118.2437],
            currentLocation: [35.5353, -97.4867],
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
            from: [41.8781, -87.6298],
            to: [33.7490, -84.3880],
            currentLocation: [35.0895, -85.2779],
            driver: 'Maria Garcia',
            estimatedArrival: '2025-02-07T12:00:00',
            weight: '300 kg',
            value: '$45,000',
            progress: 45
        },
        {
            id: 3,
            name: 'Chemical Containers - Distribution',
            status: 'pending',
            from: [47.6062, -122.3321],
            to: [37.3382, -121.8863],
            currentLocation: [47.6062, -122.3321],
            driver: 'Robert Johnson',
            estimatedArrival: '2025-02-09T14:00:00',
            weight: '800 kg',
            value: '$35,000',
            progress: 0
        },
        {
            id: 4,
            name: 'Automotive Parts - Dealer',
            status: 'delivered',
            from: [32.7157, -117.1611],
            to: [37.3382, -121.8863],
            currentLocation: [37.3382, -121.8863],
            driver: 'James Wilson',
            estimatedArrival: '2025-02-05T10:00:00',
            weight: '1200 kg',
            value: '$65,000',
            progress: 100
        }
    ];

    const getMockTrucks = () => [
        {
            id: 1,
            license: 'TX-4821',
            status: 'moving',
            currentLocation: [35.5353, -97.4867],
            driver: 'John Smith',
            speed: 65,
            heading: 45,
            shipmentId: 1,
            lastUpdate: new Date().toISOString()
        },
        {
            id: 2,
            license: 'GA-7293',
            status: 'moving',
            currentLocation: [35.0895, -85.2779],
            driver: 'Maria Garcia',
            speed: 72,
            heading: 120,
            shipmentId: 2,
            lastUpdate: new Date().toISOString()
        },
        {
            id: 3,
            license: 'CA-5612',
            status: 'stopped',
            currentLocation: [47.6062, -122.3321],
            driver: 'Robert Johnson',
            speed: 0,
            heading: 180,
            shipmentId: 3,
            lastUpdate: new Date().toISOString()
        }
    ];

    useEffect(() => {
        const displayShipments = shipments.length > 0 ? shipments : getMockShipments();
        const displayTrucks = trucks.length > 0 ? trucks : getMockTrucks();

        const filteredShipments = filter === 'all' ? displayShipments : displayShipments.filter(s => s.status === filter);

        const newStats = {
            total_shipments: displayShipments.length,
            in_transit: displayShipments.filter(s => s.status === 'in_transit').length,
            delivered: displayShipments.filter(s => s.status === 'delivered').length,
            pending: displayShipments.filter(s => s.status === 'pending').length,
            active_trucks: displayTrucks.filter(t => t.status === 'moving').length,
            avg_speed: displayTrucks.length > 0
                ? Math.round(displayTrucks.reduce((sum, t) => sum + t.speed, 0) / displayTrucks.length)
                : 0
        };

        setStats(newStats);
    }, [shipments, trucks, filter]);

    if (loading) {
        return (
            <div className="transport-dashboard loading">
                <div className="loader">
                    <div className="spinner"></div>
                    <p>Loading transport data...</p>
                </div>
            </div>
        );
    }

    const displayShipments = shipments.length > 0 ? shipments : getMockShipments();
    const filteredShipments = filter === 'all' ? displayShipments : displayShipments.filter(s => s.status === filter);

    return (
        <div className="transport-dashboard">
            <div className="dashboard-header">
                <h1>Transport Tracking System</h1>
                <p className="subtitle">Real-time vehicle and shipment tracking</p>
            </div>

            <div className="dashboard-stats">
                <StatCard
                    title="Total Shipments"
                    value={stats.total_shipments}
                    icon="📦"
                    color="#3498db"
                />
                <StatCard
                    title="In Transit"
                    value={stats.in_transit}
                    icon="🚚"
                    color="#f39c12"
                />
                <StatCard
                    title="Delivered"
                    value={stats.delivered}
                    icon="✓"
                    color="#27ae60"
                />
                <StatCard
                    title="Active Trucks"
                    value={stats.active_trucks}
                    icon="🚛"
                    color="#e74c3c"
                />
                <StatCard
                    title="Avg Speed"
                    value={`${stats.avg_speed} mph`}
                    icon="⚡"
                    color="#9b59b6"
                />
                <StatCard
                    title="Pending"
                    value={stats.pending}
                    icon="⏳"
                    color="#95a5a6"
                />
            </div>

            <div className="dashboard-content">
                <div className="map-section">
                    <TransportMap shipments={displayShipments} trucks={trucks} />
                </div>

                <div className="sidebar-section">
                    <div className="filters-panel">
                        <h3>Filters</h3>
                        <div className="filter-buttons">
                            <button
                                className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
                                onClick={() => setFilter('all')}
                            >
                                All Shipments
                            </button>
                            <button
                                className={`filter-btn ${filter === 'in_transit' ? 'active' : ''}`}
                                onClick={() => setFilter('in_transit')}
                            >
                                In Transit
                            </button>
                            <button
                                className={`filter-btn ${filter === 'delivered' ? 'active' : ''}`}
                                onClick={() => setFilter('delivered')}
                            >
                                Delivered
                            </button>
                            <button
                                className={`filter-btn ${filter === 'pending' ? 'active' : ''}`}
                                onClick={() => setFilter('pending')}
                            >
                                Pending
                            </button>
                        </div>
                    </div>

                    <div className="shipments-list-panel">
                        <h3>Recent Shipments ({filteredShipments.length})</h3>
                        <div className="shipments-list">
                            {filteredShipments.slice(0, 5).map(shipment => (
                                <ShipmentCard key={shipment.id} shipment={shipment} />
                            ))}
                            {filteredShipments.length === 0 && (
                                <p className="empty-message">No shipments found</p>
                            )}
                        </div>
                    </div>

                    <div className="active-routes">
                        <h3>Active Routes</h3>
                        <div className="routes-list">
                            {displayShipments.filter(s => s.status === 'in_transit').slice(0, 3).map(shipment => (
                                <RouteCard key={shipment.id} shipment={shipment} />
                            ))}
                            {displayShipments.filter(s => s.status === 'in_transit').length === 0 && (
                                <p className="empty-message">No active routes</p>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

const StatCard = ({ title, value, icon, color }) => (
    <div className="stat-card" style={{ borderLeftColor: color }}>
        <div className="stat-icon">{icon}</div>
        <div className="stat-content">
            <div className="stat-title">{title}</div>
            <div className="stat-value" style={{ color }}>{value}</div>
        </div>
    </div>
);

const ShipmentCard = ({ shipment }) => {
    const getStatusColor = (status) => {
        switch (status) {
            case 'delivered': return '#27ae60';
            case 'in_transit': return '#f39c12';
            case 'pending': return '#95a5a6';
            case 'delayed': return '#e74c3c';
            default: return '#3498db';
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
        <div className="shipment-card">
            <div className="shipment-header">
                <h4>{shipment.name}</h4>
                <span className="status-badge" style={{ backgroundColor: getStatusColor(shipment.status) }}>
                    {getStatusLabel(shipment.status)}
                </span>
            </div>
            <div className="shipment-details">
                <p><strong>Driver:</strong> {shipment.driver}</p>
                <p><strong>Weight:</strong> {shipment.weight}</p>
                <p><strong>Value:</strong> {shipment.value}</p>
                {shipment.progress > 0 && (
                    <div className="progress-bar">
                        <div className="progress-fill" style={{ width: `${shipment.progress}%` }}></div>
                        <span className="progress-text">{shipment.progress}%</span>
                    </div>
                )}
            </div>
        </div>
    );
};

const RouteCard = ({ shipment }) => {
    return (
        <div className="route-card">
            <div className="route-header">
                <div className="route-title">{shipment.name}</div>
                <div className="route-status">In Transit</div>
            </div>
            <div className="route-info">
                <div className="route-point">
                    <span className="point-label">From:</span>
                    <span className="point-value">New York</span>
                </div>
                <div className="route-arrow">→</div>
                <div className="route-point">
                    <span className="point-label">To:</span>
                    <span className="point-value">Los Angeles</span>
                </div>
            </div>
            <div className="route-driver">{shipment.driver}</div>
        </div>
    );
};

export default TransportDashboard;
