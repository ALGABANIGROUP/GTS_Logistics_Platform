// Unified Freight Broker Control Panel
// Integrates Transport Tracking, Safety Management, and Dispatch
// frontend/src/pages/FreightBrokerPanel.jsx

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import TransportMap from '../components/Map/TransportMap';
import TransportDashboard from '../components/Map/TransportDashboard';
import SafetyDashboard from '../components/Safety/SafetyDashboard';
import './FreightBrokerPanel.css';

const FreightBrokerPanel = () => {
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState('transport');
    const [botsStatus, setBotsStatus] = useState({
        freightBroker: 'active',
        safetyManager: 'active',
        operationsManager: 'pending',
        finance: 'idle'
    });
    const [realTimeAlerts, setRealTimeAlerts] = useState([]);
    const [wsConnected, setWsConnected] = useState(false);
    const [systemHealth, setSystemHealth] = useState({
        transport: 'healthy',
        safety: 'healthy',
        dispatch: 'healthy'
    });

    // Setup WebSocket connections
    useEffect(() => {
        setupWebSocketConnections();
        checkBotsHealth();
        const healthInterval = setInterval(checkBotsHealth, 60000);

        return () => {
            clearInterval(healthInterval);
        };
    }, []);

    const setupWebSocketConnections = () => {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const host = window.location.host;

            // Connect to Transport WebSocket
            const transportWs = new WebSocket(`${protocol}//${host}/api/v1/transport/ws/tracking`);
            transportWs.onopen = () => {
                console.log('Transport WebSocket connected');
                setWsConnected(true);
                transportWs.send(JSON.stringify({
                    type: 'subscribe',
                    channels: ['trucks', 'shipments', 'routes']
                }));
            };

            transportWs.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.type === 'alert') {
                    addAlert(data.data, 'transport');
                }
            };

            // Connect to Safety WebSocket
            const safetyWs = new WebSocket(`${protocol}//${host}/api/v1/safety/ws/alerts`);
            safetyWs.onopen = () => {
                console.log('Safety WebSocket connected');
                safetyWs.send(JSON.stringify({
                    type: 'subscribe',
                    channels: ['alerts', 'incidents', 'metrics']
                }));
            };

            safetyWs.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.type === 'safety_alert' || data.type === 'incident') {
                    addAlert(data.data, 'safety');
                }
            };

            transportWs.onerror = (error) => {
                console.error('Transport WebSocket error:', error);
                setSystemHealth(prev => ({ ...prev, transport: 'disconnected' }));
            };

            safetyWs.onerror = (error) => {
                console.error('Safety WebSocket error:', error);
                setSystemHealth(prev => ({ ...prev, safety: 'disconnected' }));
            };
        } catch (error) {
            console.error('Error setting up WebSocket connections:', error);
        }
    };

    const addAlert = (alert, source) => {
        const newAlert = {
            id: Date.now(),
            source,
            timestamp: new Date(),
            ...alert
        };
        setRealTimeAlerts(prev => [newAlert, ...prev].slice(0, 50));
    };

    const checkBotsHealth = async () => {
        try {
            const botsToCheck = ['freight_broker', 'safety_manager', 'operations_manager', 'finance'];
            const health = await Promise.all(
                botsToCheck.map(bot =>
                    fetch(`/api/v1/ai/bots/${bot}/status`)
                        .then(res => res.ok ? res.json() : { status: 'error' })
                        .catch(() => ({ status: 'disconnected' }))
                )
            );

            const botStatusMap = {
                freight_broker: health[0]?.status === 'active' ? 'active' : 'inactive',
                safety_manager: health[1]?.status === 'active' ? 'active' : 'inactive',
                operations_manager: health[2]?.status === 'active' ? 'active' : 'inactive',
                finance: health[3]?.status === 'active' ? 'active' : 'inactive'
            };

            setBotsStatus(botStatusMap);
        } catch (error) {
            console.error('Error checking bots health:', error);
        }
    };

    const handleBotAction = async (botName, action) => {
        try {
            const response = await fetch(`/api/v1/ai/bots/${botName}/${action}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ timestamp: new Date().toISOString() })
            });

            if (response.ok) {
                const data = await response.json();
                console.log(`${botName} ${action}:`, data);
                addAlert({
                    message: `${botName} ${action} executed successfully`,
                    priority: 'info'
                }, 'system');
            }
        } catch (error) {
            console.error(`Error executing ${action} on ${botName}:`, error);
        }
    };

    const clearAlerts = () => {
        setRealTimeAlerts([]);
    };

    return (
        <div className="freight-broker-panel">
            {/* Header */}
            <div className="fbp-header">
                <div className="fbp-title-section">
                    <h1>🚚 Freight Broker Control Panel</h1>
                    <p className="subtitle">Unified Transport Management & Safety Operations Dashboard</p>
                </div>

                {/* System Health Indicators */}
                <div className="system-health-indicators">
                    <div className={`health-indicator ${systemHealth.transport}`}>
                        <span className="indicator-dot"></span>
                        Transport
                    </div>
                    <div className={`health-indicator ${systemHealth.safety}`}>
                        <span className="indicator-dot"></span>
                        Safety
                    </div>
                    <div className={`health-indicator ${systemHealth.dispatch}`}>
                        <span className="indicator-dot"></span>
                        Dispatch
                    </div>
                    <div className="ws-status">
                        <span className={`ws-dot ${wsConnected ? 'connected' : 'disconnected'}`}></span>
                        {wsConnected ? 'Live' : 'Offline'}
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="fbp-main">
                {/* Left Sidebar - Tabs */}
                <div className="fbp-sidebar">
                    <div className="fbp-tabs">
                        <button
                            className={`fbp-tab ${activeTab === 'transport' ? 'active' : ''}`}
                            onClick={() => setActiveTab('transport')}
                        >
                            <span className="tab-icon">🗺️</span>
                            Transport
                        </button>
                        <button
                            className={`fbp-tab ${activeTab === 'safety' ? 'active' : ''}`}
                            onClick={() => setActiveTab('safety')}
                        >
                            <span className="tab-icon">🛡️</span>
                            Safety
                        </button>
                        <button
                            className={`fbp-tab ${activeTab === 'dispatch' ? 'active' : ''}`}
                            onClick={() => setActiveTab('dispatch')}
                        >
                            <span className="tab-icon">📋</span>
                            Dispatch
                        </button>
                        <button
                            className={`fbp-tab ${activeTab === 'bots' ? 'active' : ''}`}
                            onClick={() => setActiveTab('bots')}
                        >
                            <span className="tab-icon">🤖</span>
                            Bots
                        </button>
                    </div>

                    {/* Real-time Alerts Feed */}
                    <div className="fbp-alerts-feed">
                        <div className="alerts-header">
                            <h3>Live Alerts ({realTimeAlerts.length})</h3>
                            {realTimeAlerts.length > 0 && (
                                <button className="clear-alerts-btn" onClick={clearAlerts}>Clear</button>
                            )}
                        </div>
                        <div className="alerts-list">
                            {realTimeAlerts.slice(0, 8).map(alert => (
                                <div key={alert.id} className={`alert-item alert-${alert.source}`}>
                                    <div className="alert-time">
                                        {alert.timestamp.toLocaleTimeString()}
                                    </div>
                                    <div className="alert-message">
                                        {alert.message || `${alert.source} alert`}
                                    </div>
                                    <div className="alert-priority">
                                        {alert.priority && `[${alert.priority.toUpperCase()}]`}
                                    </div>
                                </div>
                            ))}
                            {realTimeAlerts.length === 0 && (
                                <p className="no-alerts">No alerts at this time</p>
                            )}
                        </div>
                    </div>
                </div>

                {/* Main Content Area */}
                <div className="fbp-content">
                    <div className="fbp-hero">
                        <div className="hero-text">
                            <h2>📦 Freight Broker Bot</h2>
                            <p>Canadian Logistics Command Center</p>
                        </div>
                        <div className="hero-meta">
                            <span className="hero-pill">Daily Free Views: 1/4</span>
                            <button className="hero-btn" onClick={() => navigate('/ai-bots/freight_broker/control')}>Bot Settings</button>
                        </div>
                    </div>

                    {/* Transport Tab */}
                    {activeTab === 'transport' && (
                        <div className="fbp-tab-content transport-content">
                            <div className="transport-grid">
                                {/* Map Section */}
                                <div className="transport-map-container">
                                    <TransportMap />
                                </div>

                                {/* Dashboard Section */}
                                <div className="transport-dashboard-container">
                                    <TransportDashboard />
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Safety Tab */}
                    {activeTab === 'safety' && (
                        <div className="fbp-tab-content safety-content">
                            <SafetyDashboard />
                        </div>
                    )}

                    {/* Dispatch Tab */}
                    {activeTab === 'dispatch' && (
                        <div className="fbp-tab-content dispatch-content">
                            <DispatchBoard />
                        </div>
                    )}

                    {/* Bots Control Tab */}
                    {activeTab === 'bots' && (
                        <div className="fbp-tab-content bots-content">
                            <BotsControlPanel
                                botsStatus={botsStatus}
                                onBotAction={handleBotAction}
                            />
                        </div>
                    )}
                </div>
            </div>

            {/* Footer - Quick Stats */}
            <div className="fbp-footer">
                <div className="quick-stats">
                    <div className="quick-stat">
                        <span className="stat-label">Active Bots</span>
                        <span className="stat-value">
                            {Object.values(botsStatus).filter(s => s === 'active').length}/4
                        </span>
                    </div>
                    <div className="quick-stat">
                        <span className="stat-label">System Time</span>
                        <span className="stat-value" id="system-time">
                            {new Date().toLocaleTimeString()}
                        </span>
                    </div>
                    <div className="quick-stat">
                        <span className="stat-label">Alerts</span>
                        <span className="stat-value">{realTimeAlerts.length}</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

// Dispatch Board Component
const DispatchBoard = () => {
    const [shipments, setShipments] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchDispatchData();
    }, []);

    const fetchDispatchData = async () => {
        try {
            const response = await fetch('/api/v1/transport/shipments');
            if (response.ok) {
                const data = await response.json();
                setShipments(data);
            }
            setLoading(false);
        } catch (error) {
            console.error('Error fetching dispatch data:', error);
            setLoading(false);
        }
    };

    const STATUSES = ['unassigned', 'assigned', 'in_transit', 'delivered', 'cancelled'];

    if (loading) {
        return <div className="dispatch-loading">Loading dispatch board...</div>;
    }

    return (
        <div className="dispatch-board">
            <h2>Dispatch Board - Kanban View</h2>
            <div className="dispatch-columns">
                {STATUSES.map(status => (
                    <div key={status} className="dispatch-column">
                        <h3 className={`column-title status-${status}`}>
                            {status.replace(/_/g, ' ').toUpperCase()}
                        </h3>
                        <div className="column-cards">
                            {shipments
                                .filter(s => s.status === status || (status === 'unassigned' && !s.assigned_driver))
                                .map(shipment => (
                                    <div key={shipment.id} className="dispatch-card">
                                        <div className="card-title">{shipment.name}</div>
                                        <div className="card-details">
                                            <p>From: {shipment.from}</p>
                                            <p>To: {shipment.to}</p>
                                            <p>Driver: {shipment.driver || 'Unassigned'}</p>
                                        </div>
                                    </div>
                                ))}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

// Bots Control Panel Component
const BotsControlPanel = ({ botsStatus, onBotAction }) => {
    const BOTS = [
        {
            name: 'freight_broker',
            displayName: 'Freight Broker Bot',
            icon: '🚚',
            description: 'Main coordinator for all freight operations',
            actions: ['run', 'pause', 'status']
        },
        {
            name: 'safety_manager',
            displayName: 'Safety Manager Bot',
            icon: '🛡️',
            description: 'Safety monitoring and incident management',
            actions: ['run', 'pause', 'status', 'health_check']
        },
        {
            name: 'operations_manager',
            displayName: 'Operations Manager Bot',
            icon: '⚙️',
            description: 'Operations coordination and scheduling',
            actions: ['run', 'pause', 'status']
        },
        {
            name: 'finance',
            displayName: 'Finance Bot',
            icon: '💰',
            description: 'Financial tracking and billing',
            actions: ['run', 'pause', 'status', 'generate_report']
        }
    ];

    return (
        <div className="bots-control-panel">
            <h2>AI Bots Control Center</h2>
            <div className="bots-grid">
                {BOTS.map(bot => (
                    <div key={bot.name} className={`bot-card bot-${botsStatus[bot.name]}`}>
                        <div className="bot-header">
                            <span className="bot-icon">{bot.icon}</span>
                            <div className="bot-info">
                                <h3>{bot.displayName}</h3>
                                <p className="bot-status">
                                    Status: <span className={`status-${botsStatus[bot.name]}`}>
                                        {botsStatus[bot.name]?.toUpperCase()}
                                    </span>
                                </p>
                            </div>
                        </div>
                        <p className="bot-description">{bot.description}</p>
                        <div className="bot-actions">
                            {bot.actions.map(action => (
                                <button
                                    key={action}
                                    className="action-btn"
                                    onClick={() => onBotAction(bot.name, action)}
                                >
                                    {action.charAt(0).toUpperCase() + action.slice(1).replace(/_/g, ' ')}
                                </button>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default FreightBrokerPanel;
