// Operational Dashboard Component
import React, { useState, useEffect } from 'react';
import informationService from '../../../../services/informationService';
import './OperationalDashboard.css';

const OperationalDashboard = ({ onNewNotification, refreshKey }) => {
    const [loading, setLoading] = useState(true);
    const [dashboardData, setDashboardData] = useState(null);
    const [kpis, setKpis] = useState(null);
    const [alerts, setAlerts] = useState([]);
    const [selectedMetricType, setSelectedMetricType] = useState('all');
    const [timeRange, setTimeRange] = useState('today');

    useEffect(() => {
        loadDashboardData();
    }, [refreshKey, timeRange]);

    const loadDashboardData = async () => {
        setLoading(true);
        try {
            const [dashboard, kpisData, alertsData] = await Promise.all([
                informationService.getOperationalDashboard(),
                informationService.getKPIs(),
                informationService.getSystemAlerts(null, 10)
            ]);

            setDashboardData(dashboard);
            setKpis(kpisData);
            setAlerts(alertsData.alerts || []);
        } catch (error) {
            onNewNotification?.('Failed to load dashboard data', 'error');
        } finally {
            setLoading(false);
        }
    };

    const getSeverityColor = (severity) => {
        const colors = {
            critical: '#ef4444',
            high: '#f59e0b',
            medium: '#eab308',
            low: '#3b82f6'
        };
        return colors[severity] || '#64748b';
    };

    const formatInsightText = (insight) => {
        if (!insight) {
            return '';
        }

        if (typeof insight === 'string') {
            return insight;
        }

        if (typeof insight === 'object') {
            const { load, carrier, confidence } = insight;
            const parts = [];
            if (load) parts.push(load);
            if (carrier) parts.push(carrier);
            if (typeof confidence === 'number') {
                parts.push(`${confidence.toFixed(1)}% confidence`);
            }
            return parts.join(' · ') || JSON.stringify(insight);
        }

        return String(insight);
    };

    const getTrendIcon = (trend) => {
        switch (trend) {
            case 'up': return '';
            case 'down': return '';
            case 'stable': return '';
            default: return '';
        }
    };

    const getKPIStatus = (value, target) => {
        const percentage = (value / target) * 100;
        if (percentage >= 100) return 'excellent';
        if (percentage >= 90) return 'good';
        if (percentage >= 70) return 'warning';
        return 'poor';
    };

    if (loading) {
        return (
            <div className="loading-container">
                <div className="loading-spinner"></div>
                <p>Loading dashboard data...</p>
            </div>
        );
    }

    return (
        <div className="operational-dashboard">
            {/* Time Range Selector */}
            <div className="dashboard-controls">
                <div className="time-range-selector">
                    {['today', 'week', 'month', 'year'].map(range => (
                        <button
                            key={range}
                            className={`range-button ${timeRange === range ? 'active' : ''}`}
                            onClick={() => setTimeRange(range)}
                        >
                            {range.charAt(0).toUpperCase() + range.slice(1)}
                        </button>
                    ))}
                </div>
            </div>

            {/* Live Metrics */}
            <div className="metrics-section">
                <h2 className="section-title"> Live Metrics</h2>
                <div className="metrics-grid">
                    {/* Shipments Metrics */}
                    <div className="metric-card glass-card">
                        <div className="metric-header">
                            <span className="metric-icon"></span>
                            <h3>Shipments</h3>
                        </div>
                        <div className="metric-stats">
                            <div className="stat-item glass-card">
                                <span className="stat-label">Completed Today</span>
                                <span className="stat-value">
                                    {dashboardData?.metrics?.shipments?.completed_today || 0}
                                </span>
                            </div>
                            <div className="stat-item glass-card">
                                <span className="stat-label">Active</span>
                                <span className="stat-value">
                                    {dashboardData?.metrics?.shipments?.total_active || 0}
                                </span>
                            </div>
                            <div className="stat-item glass-card warning">
                                <span className="stat-label">Delayed</span>
                                <span className="stat-value">
                                    {dashboardData?.metrics?.shipments?.delayed_shipments || 0}
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Financial Metrics */}
                    <div className="metric-card glass-card">
                        <div className="metric-header">
                            <span className="metric-icon"></span>
                            <h3>Financial</h3>
                        </div>
                        <div className="metric-stats">
                            <div className="stat-item glass-card">
                                <span className="stat-label">Daily Revenue</span>
                                <span className="stat-value">
                                    ${(dashboardData?.metrics?.financial?.daily_revenue || 0).toLocaleString()}
                                </span>
                            </div>
                            <div className="stat-item glass-card">
                                <span className="stat-label">Monthly Revenue</span>
                                <span className="stat-value">
                                    ${(dashboardData?.metrics?.financial?.monthly_revenue || 0).toLocaleString()}
                                </span>
                            </div>
                            <div className="stat-item glass-card warning">
                                <span className="stat-label">Overdue</span>
                                <span className="stat-value">
                                    ${(dashboardData?.metrics?.financial?.overdue_amount || 0).toLocaleString()}
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Inventory Metrics */}
                    <div className="metric-card glass-card">
                        <div className="metric-header">
                            <span className="metric-icon"></span>
                            <h3>Inventory</h3>
                        </div>
                        <div className="metric-stats">
                            <div className="stat-item glass-card">
                                <span className="stat-label">Total Items</span>
                                <span className="stat-value">
                                    {dashboardData?.metrics?.inventory?.total_items || 0}
                                </span>
                            </div>
                            <div className="stat-item glass-card">
                                <span className="stat-label">Total Value</span>
                                <span className="stat-value">
                                    ${(dashboardData?.metrics?.inventory?.total_inventory_value || 0).toLocaleString()}
                                </span>
                            </div>
                            <div className="stat-item glass-card warning">
                                <span className="stat-label">Low Stock</span>
                                <span className="stat-value">
                                    {dashboardData?.metrics?.inventory?.low_stock_count || 0}
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Customer Metrics */}
                    <div className="metric-card glass-card">
                        <div className="metric-header">
                            <span className="metric-icon"></span>
                            <h3>Customers</h3>
                        </div>
                        <div className="metric-stats">
                            <div className="stat-item glass-card">
                                <span className="stat-label">Total Customers</span>
                                <span className="stat-value">
                                    {dashboardData?.metrics?.customers?.total_customers || 0}
                                </span>
                            </div>
                            <div className="stat-item glass-card">
                                <span className="stat-label">Active</span>
                                <span className="stat-value">
                                    {dashboardData?.metrics?.customers?.active_customers || 0}
                                </span>
                            </div>
                            <div className="stat-item glass-card success">
                                <span className="stat-label">New This Month</span>
                                <span className="stat-value">
                                    {dashboardData?.metrics?.customers?.new_customers_month || 0}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* KPIs Section */}
            {kpis && (
                <div className="kpis-section">
                    <h2 className="section-title"> Key Performance Indicators</h2>

                    {/* Operational KPIs */}
                    <div className="kpi-category">
                        <h3 className="category-title">Operational</h3>
                        <div className="kpi-grid">
                            {Object.entries(kpis.kpis?.operational || {}).map(([key, kpi]) => (
                                <div key={key} className={`kpi-card ${getKPIStatus(kpi.value, kpi.target)}`}>
                                    <div className="kpi-header">
                                        <span className="kpi-name">{key.replace(/_/g, ' ')}</span>
                                        <span className="kpi-trend">{getTrendIcon(kpi.trend)}</span>
                                    </div>
                                    <div className="kpi-values">
                                        <div className="kpi-current">
                                            <span className="kpi-value">{kpi.value}</span>
                                            <span className="kpi-unit">{kpi.unit}</span>
                                        </div>
                                        <div className="kpi-target">
                                            Target: {kpi.target}{kpi.unit}
                                        </div>
                                    </div>
                                    <div className="kpi-progress">
                                        <div
                                            className="kpi-progress-bar"
                                            style={{ width: `${Math.min((kpi.value / kpi.target) * 100, 100)}%` }}
                                        ></div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Financial KPIs */}
                    <div className="kpi-category">
                        <h3 className="category-title">Financial</h3>
                        <div className="kpi-grid">
                            {Object.entries(kpis.kpis?.financial || {}).map(([key, kpi]) => (
                                <div key={key} className={`kpi-card ${getKPIStatus(kpi.value, kpi.target)}`}>
                                    <div className="kpi-header">
                                        <span className="kpi-name">{key.replace(/_/g, ' ')}</span>
                                        <span className="kpi-trend">{getTrendIcon(kpi.trend)}</span>
                                    </div>
                                    <div className="kpi-values">
                                        <div className="kpi-current">
                                            <span className="kpi-value">{kpi.value}</span>
                                            <span className="kpi-unit">{kpi.unit}</span>
                                        </div>
                                        <div className="kpi-target">
                                            Target: {kpi.target}{kpi.unit}
                                        </div>
                                    </div>
                                    <div className="kpi-progress">
                                        <div
                                            className="kpi-progress-bar"
                                            style={{ width: `${Math.min((kpi.value / kpi.target) * 100, 100)}%` }}
                                        ></div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Customer KPIs */}
                    <div className="kpi-category">
                        <h3 className="category-title">Customer</h3>
                        <div className="kpi-grid">
                            {Object.entries(kpis.kpis?.customer || {}).map(([key, kpi]) => (
                                <div key={key} className={`kpi-card ${getKPIStatus(kpi.value, kpi.target)}`}>
                                    <div className="kpi-header">
                                        <span className="kpi-name">{key.replace(/_/g, ' ')}</span>
                                        <span className="kpi-trend">{getTrendIcon(kpi.trend)}</span>
                                    </div>
                                    <div className="kpi-values">
                                        <div className="kpi-current">
                                            <span className="kpi-value">{kpi.value}</span>
                                            <span className="kpi-unit">{kpi.unit}</span>
                                        </div>
                                        <div className="kpi-target">
                                            Target: {kpi.target}{kpi.unit}
                                        </div>
                                    </div>
                                    <div className="kpi-progress">
                                        <div
                                            className="kpi-progress-bar"
                                            style={{ width: `${Math.min((kpi.value / kpi.target) * 100, 100)}%` }}
                                        ></div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            {/* Active Alerts */}
            {alerts.length > 0 && (
                <div className="alerts-section">
                    <h2 className="section-title"> Active Alerts</h2>
                    <div className="alerts-list">
                        {alerts.map((alert) => (
                            <div
                                key={alert.id}
                                className="alert-item"
                                style={{ borderLeft: `4px solid ${getSeverityColor(alert.severity)}` }}
                            >
                                <div className="alert-header">
                                    <span className="alert-severity" style={{ color: getSeverityColor(alert.severity) }}>
                                        {alert.severity.toUpperCase()}
                                    </span>
                                    <span className="alert-time">{new Date(alert.timestamp).toLocaleString()}</span>
                                </div>
                                <div className="alert-title">{alert.title}</div>
                                <div className="alert-message">{alert.message}</div>
                                {alert.action_required && (
                                    <div className="alert-action">
                                        <span className="action-badge">Action Required</span>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Quick Insights */}
            {dashboardData?.insights && dashboardData.insights.length > 0 && (
                <div className="insights-section">
                    <h2 className="section-title"> Quick Insights</h2>
                    <div className="insights-list">
                        {dashboardData.insights.map((insight, index) => {
                            const insightText = formatInsightText(insight);
                            return (
                                <div key={index} className="insight-item">
                                    <span className="insight-icon"></span>
                                    <span className="insight-text">{insightText}</span>
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}
        </div>
    );
};

export default OperationalDashboard;
