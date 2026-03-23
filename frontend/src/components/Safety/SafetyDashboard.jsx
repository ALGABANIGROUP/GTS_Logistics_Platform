// Safety Dashboard - Comprehensive Safety Management UI
// frontend/src/components/Safety/SafetyDashboard.jsx

import React, { useState, useEffect } from 'react';
import {
    LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
    XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import axios from 'axios';
import './SafetyDashboard.css';

const SafetyDashboard = () => {
    const [safetyData, setSafetyData] = useState(null);
    const [incidents, setIncidents] = useState([]);
    const [alerts, setAlerts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedPeriod, setSelectedPeriod] = useState('daily');
    const [metrics, setMetrics] = useState(null);

    useEffect(() => {
        fetchSafetyData();
        setupWebSocket();

        const interval = setInterval(fetchSafetyData, 300000);

        return () => clearInterval(interval);
    }, [selectedPeriod]);

    const fetchSafetyData = async () => {
        try {
            const [dashboardRes, incidentsRes, metricsRes] = await Promise.all([
                axios.get(`/api/v1/safety/reports/${selectedPeriod}`),
                axios.get('/api/v1/safety/incidents?limit=10'),
                axios.get('/api/v1/safety/metrics')
            ]);

            setSafetyData(dashboardRes.data.data);
            setIncidents(incidentsRes.data.incidents);
            setMetrics(metricsRes.data.metrics);
            setLoading(false);
        } catch (error) {
            console.error('Error fetching safety data:', error);
            setLoading(false);
        }
    };

    const setupWebSocket = () => {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const ws = new WebSocket(`${protocol}//${window.location.host}/api/v1/safety/ws/alerts`);

            ws.onopen = () => {
                ws.send(JSON.stringify({
                    type: 'subscribe',
                    channels: ['alerts', 'incidents', 'metrics']
                }));
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);

                if (data.type === 'safety_alert') {
                    showAlertNotification(data.data);
                    setAlerts(prev => [data.data, ...prev].slice(0, 10));
                }
            };

            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
        } catch (error) {
            console.error('Error setting up WebSocket:', error);
        }
    };

    const showAlertNotification = (alert) => {
        if (Notification.permission === 'granted') {
            new Notification(`Safety Alert: ${alert.priority}`, {
                body: alert.message,
                icon: '/safety-icon.png'
            });
        }
    };

    if (loading) {
        return (
            <div className="loading-container">
                <div className="spinner"></div>
                <p>Loading safety data...</p>
            </div>
        );
    }

    const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

    return (
        <div className="safety-dashboard">
            {/* Header */}
            <div className="dashboard-header">
                <h1>Safety Manager</h1>
                <div className="period-selector">
                    <button
                        className={selectedPeriod === 'daily' ? 'active' : ''}
                        onClick={() => setSelectedPeriod('daily')}
                    >
                        Daily
                    </button>
                    <button
                        className={selectedPeriod === 'weekly' ? 'active' : ''}
                        onClick={() => setSelectedPeriod('weekly')}
                    >
                        Weekly
                    </button>
                    <button
                        className={selectedPeriod === 'monthly' ? 'active' : ''}
                        onClick={() => setSelectedPeriod('monthly')}
                    >
                        Monthly
                    </button>
                </div>
            </div>

            {/* Key Metrics */}
            <div className="stats-grid">
                <div className="stat-card safety-score">
                    <h3>Safety Score</h3>
                    <div className="score-value">
                        {safetyData?.summary?.safety_score || 92}/100
                    </div>
                    <div className={`trend ${safetyData?.summary?.trend || 'stable'}`}>
                        {safetyData?.summary?.trend === 'improving' ? '↗ Improving' :
                            safetyData?.summary?.trend === 'deteriorating' ? '↘ Declining' : '➡ Stable'}
                    </div>
                </div>

                <div className="stat-card incidents">
                    <h3>Incidents</h3>
                    <div className="incident-count">
                        {metrics?.incidents?.total || 0}
                    </div>
                    <div className="incident-breakdown">
                        <span>Severe: {metrics?.incidents?.severe || 0}</span>
                        <span>Moderate: {metrics?.incidents?.moderate || 0}</span>
                    </div>
                </div>

                <div className="stat-card risky-drivers">
                    <h3>High-Risk Drivers</h3>
                    <div className="driver-count">
                        {metrics?.drivers?.high_risk || 0}
                    </div>
                    <p className="driver-total">of {metrics?.drivers?.total || 0} drivers</p>
                </div>

                <div className="stat-card alerts">
                    <h3>Active Alerts</h3>
                    <div className="alert-count">
                        {alerts.length}
                    </div>
                    <p className="alert-status">Last 24 hours</p>
                </div>

                <div className="stat-card vehicles">
                    <h3>Vehicle Status</h3>
                    <div className="vehicle-status">
                        <span className="safe">{metrics?.vehicles?.safe || 0} Safe</span>
                        <span className="unsafe">{metrics?.vehicles?.needs_maintenance || 0} Need Service</span>
                    </div>
                </div>

                <div className="stat-card compliance">
                    <h3>Compliance Score</h3>
                    <div className="compliance-value">
                        {metrics?.compliance_score || 95}%
                    </div>
                    <p>Target: 100%</p>
                </div>
            </div>

            {/* Charts Section */}
            <div className="charts-section">
                <div className="chart-container">
                    <h4>Safety Trend</h4>
                    <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={safetyData?.trend_data || []}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="date" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Line type="monotone" dataKey="safety_score" stroke="#8884d8" name="Safety Score" />
                            <Line type="monotone" dataKey="incidents" stroke="#82ca9d" name="Incidents" />
                        </LineChart>
                    </ResponsiveContainer>
                </div>

                <div className="chart-container">
                    <h4>Incident Distribution</h4>
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={safetyData?.incident_data || []}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="type" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Bar dataKey="count" fill="#8884d8" name="Count" />
                        </BarChart>
                    </ResponsiveContainer>
                </div>

                <div className="chart-container">
                    <h4>Risk Distribution</h4>
                    <ResponsiveContainer width="100%" height={300}>
                        <PieChart>
                            <Pie
                                data={[
                                    { name: 'Low Risk', value: 60 },
                                    { name: 'Medium Risk', value: 25 },
                                    { name: 'High Risk', value: 10 },
                                    { name: 'Critical', value: 5 }
                                ]}
                                cx="50%"
                                cy="50%"
                                labelLine={false}
                                label={(entry) => `${entry.name}: ${entry.value}%`}
                                outerRadius={80}
                                fill="#8884d8"
                                dataKey="value"
                            >
                                {[0, 1, 2, 3].map((index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </Pie>
                            <Tooltip />
                        </PieChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Recent Incidents */}
            <div className="incidents-section">
                <h4>Recent Incidents</h4>
                <div className="incidents-list">
                    {incidents.slice(0, 5).map((incident, index) => (
                        <div key={index} className={`incident-item severity-${incident.severity || 'moderate'}`}>
                            <div className="incident-header">
                                <span className="incident-type">{incident.incident_type || 'Unknown'}</span>
                                <span className="incident-time">
                                    {new Date(incident.incident_date).toLocaleDateString()}
                                </span>
                            </div>
                            <div className="incident-description">
                                {incident.description || 'No description provided'}
                            </div>
                            <div className="incident-details">
                                <span>Severity: {incident.severity || 'N/A'}</span>
                                <span>Status: {incident.investigation_status || 'Pending'}</span>
                            </div>
                        </div>
                    ))}
                    {incidents.length === 0 && (
                        <p className="no-data">No incidents in this period</p>
                    )}
                </div>
            </div>

            {/* Active Alerts */}
            <div className="alerts-section">
                <h4>Active Alerts</h4>
                <div className="alerts-list">
                    {alerts.slice(0, 5).map((alert, index) => (
                        <div key={index} className={`alert-item priority-${alert.priority || 'medium'}`}>
                            <div className="alert-header">
                                <span className="alert-priority">{(alert.priority || 'Medium').toUpperCase()}</span>
                                <span className="alert-time">
                                    {new Date(alert.timestamp).toLocaleTimeString()}
                                </span>
                            </div>
                            <div className="alert-message">{alert.message}</div>
                            <div className="alert-actions">
                                <button className="btn-view">View Details</button>
                                <button className="btn-acknowledge">Acknowledge</button>
                            </div>
                        </div>
                    ))}
                    {alerts.length === 0 && (
                        <p className="no-data">No active alerts</p>
                    )}
                </div>
            </div>

            {/* Recommendations */}
            <div className="recommendations-section">
                <h4>Safety Recommendations</h4>
                <div className="recommendations-list">
                    {safetyData?.recommendations?.map((rec, index) => (
                        <div key={index} className={`recommendation-item priority-${rec.priority || 'medium'}`}>
                            <div className="recommendation-title">
                                <span className="rec-icon">💡</span>
                                {rec.action || 'Action'}
                            </div>
                            <div className="recommendation-details">
                                <p>{rec.message}</p>
                                <div className="rec-meta">
                                    <span>Priority: {rec.priority}</span>
                                    <span>Deadline: {rec.deadline}</span>
                                </div>
                            </div>
                        </div>
                    ))}
                    {!safetyData?.recommendations || safetyData.recommendations.length === 0 && (
                        <p className="no-data">No recommendations at this time</p>
                    )}
                </div>
            </div>

            {/* Action Items */}
            <div className="action-items-section">
                <h4>Pending Actions</h4>
                <div className="action-items-list">
                    <div className="action-item">
                        <input type="checkbox" id="action1" />
                        <label htmlFor="action1">Review vehicle inspection reports</label>
                        <span className="deadline">Due: 2026-02-10</span>
                    </div>
                    <div className="action-item">
                        <input type="checkbox" id="action2" />
                        <label htmlFor="action2">Conduct safety training session</label>
                        <span className="deadline">Due: 2026-02-15</span>
                    </div>
                    <div className="action-item">
                        <input type="checkbox" id="action3" />
                        <label htmlFor="action3">Complete incident investigation</label>
                        <span className="deadline">Due: 2026-02-08</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SafetyDashboard;
