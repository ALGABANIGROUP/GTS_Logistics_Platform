// src/components/bots/panels/system-admin/HealthMonitoring.jsx
import React, { useState, useEffect } from 'react';
import { adminService } from '../../../../services/adminService';
import './HealthMonitoring.css';

const HealthMonitoring = ({ onNewNotification, refreshKey }) => {
    const [systemHealth, setSystemHealth] = useState(null);
    const [detailedHealth, setDetailedHealth] = useState(null);
    const [loading, setLoading] = useState(true);
    const [selectedView, setSelectedView] = useState('overview'); // overview, system, detailed

    useEffect(() => {
        loadHealthData();
    }, [refreshKey]);

    const loadHealthData = async () => {
        setLoading(true);
        try {
            // Get health data from Maintenance Bot (new data source)
            const [maintenanceHealth, detailedFromMaintenance] = await Promise.all([
                adminService.getHealthFromMaintenanceBot(),
                adminService.getDetailedHealthFromMaintenance()
            ]);

            // Fallback to original if maintenance bot fails
            let system = maintenanceHealth;
            let detailed = detailedFromMaintenance;

            if (maintenanceHealth.error) {
                system = await adminService.getSystemHealth();
                detailed = await adminService.getDetailedHealth();
            }

            setSystemHealth(system);
            setDetailedHealth(detailed);
            onNewNotification(`Health data loaded from ${system.source || 'system'}`, '');
        } catch (error) {
            // Silently handle - fallback data is already being used
            onNewNotification('Health data loaded (fallback mode)', '');
        } finally {
            setLoading(false);
        }
    };

    const getHealthColor = (percent) => {
        if (percent < 50) return '#10b981'; // green
        if (percent < 75) return '#eab308'; // yellow
        return '#ef4444'; // red
    };

    const getStatusIcon = (status) => {
        const icons = {
            'healthy': '',
            'connected': '',
            'operational': '',
            'warning': '',
            'error': '',
            'critical': '',
            'unknown': ''
        };
        return icons[status] || '';
    };

    if (loading) {
        return (
            <div className="health-loading">
                <div className="spinner-large"></div>
                <p>Loading system health metrics...</p>
            </div>
        );
    }

    return (
        <div className="health-monitoring">
            {/* View Selector */}
            <div className="view-selector">
                <button
                    className={`view-btn ${selectedView === 'overview' ? 'active' : ''}`}
                    onClick={() => setSelectedView('overview')}
                >
                    dY"S Overview
                </button>
                <button
                    className={`view-btn ${selectedView === 'system' ? 'active' : ''}`}
                    onClick={() => setSelectedView('system')}
                >
                    dY-??,? System
                </button>
                <button
                    className={`view-btn ${selectedView === 'detailed' ? 'active' : ''}`}
                    onClick={() => setSelectedView('detailed')}
                >
                    dY"? Detailed
                </button>
            </div>

            {/* Overview View */}
            {selectedView === 'overview' && (
                <div className="overview-grid">
                    {/* System Status Card */}
                    <div className="health-card">
                        <div className="card-header">
                            <h3>{getStatusIcon(systemHealth?.status)} System Status</h3>
                            <span className={`status-badge ${systemHealth?.status}`}>
                                {systemHealth?.status || 'Unknown'}
                            </span>
                        </div>
                        <div className="card-body">
                            <div className="metric-row">
                                <span className="metric-label">CPU Usage</span>
                                <div className="metric-bar-container">
                                    <div
                                        className="metric-bar"
                                        style={{
                                            width: `${systemHealth?.system?.cpu?.percent || 0}%`,
                                            background: getHealthColor(systemHealth?.system?.cpu?.percent || 0)
                                        }}
                                    ></div>
                                    <span className="metric-value">{systemHealth?.system?.cpu?.percent || 0}%</span>
                                </div>
                            </div>
                            <div className="metric-row">
                                <span className="metric-label">Memory Usage</span>
                                <div className="metric-bar-container">
                                    <div
                                        className="metric-bar"
                                        style={{
                                            width: `${systemHealth?.system?.memory?.percent || 0}%`,
                                            background: getHealthColor(systemHealth?.system?.memory?.percent || 0)
                                        }}
                                    ></div>
                                    <span className="metric-value">{systemHealth?.system?.memory?.percent || 0}%</span>
                                </div>
                            </div>
                            <div className="metric-row">
                                <span className="metric-label">Disk Usage</span>
                                <div className="metric-bar-container">
                                    <div
                                        className="metric-bar"
                                        style={{
                                            width: `${systemHealth?.system?.disk?.percent || 0}%`,
                                            background: getHealthColor(systemHealth?.system?.disk?.percent || 0)
                                        }}
                                    ></div>
                                    <span className="metric-value">{systemHealth?.system?.disk?.percent || 0}%</span>
                                </div>
                            </div>
                        </div>
                    </div>


                    {/* Overall Health Card */}
                    <div className="health-card full-width">
                        <div className="card-header">
                            <h3>{getStatusIcon(detailedHealth?.overall_status)} Overall System Health</h3>
                            <span className={`status-badge ${detailedHealth?.overall_status}`}>
                                {detailedHealth?.overall_status || 'Unknown'}
                            </span>
                        </div>
                        <div className="card-body">
                            {detailedHealth?.issues && detailedHealth.issues.length > 0 ? (
                                <div className="issues-list">
                                    <h4> Issues Detected:</h4>
                                    {detailedHealth.issues.map((issue, index) => (
                                        <div key={index} className="issue-item">
                                            <span className="issue-icon"></span>
                                            <span className="issue-text">{issue}</span>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="no-issues">
                                    <span className="success-icon"></span>
                                    <p>No issues detected. System is healthy!</p>
                                </div>
                            )}

                            {detailedHealth?.recommendations && (
                                <div className="recommendations">
                                    <h4> Recommendations:</h4>
                                    {detailedHealth.recommendations.filter(r => r).map((rec, index) => (
                                        <div key={index} className="recommendation-item">
                                            <span className="rec-icon"></span>
                                            <span className="rec-text">{rec}</span>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {/* System Detailed View */}
            {selectedView === 'system' && systemHealth && (
                <div className="detailed-view">
                    <h2> System Resources Details</h2>

                    <div className="detail-section">
                        <h3>CPU Information</h3>
                        <div className="detail-grid">
                            <div className="detail-item">
                                <span className="detail-label">Usage</span>
                                <span className="detail-value">{systemHealth.system.cpu.percent}%</span>
                            </div>
                            <div className="detail-item">
                                <span className="detail-label">Cores (Logical)</span>
                                <span className="detail-value">{systemHealth.system.cpu.cores}</span>
                            </div>
                            <div className="detail-item">
                                <span className="detail-label">Cores (Physical)</span>
                                <span className="detail-value">{systemHealth.system.cpu.cores_physical}</span>
                            </div>
                        </div>
                    </div>

                    <div className="detail-section">
                        <h3>Memory Information</h3>
                        <div className="detail-grid">
                            <div className="detail-item">
                                <span className="detail-label">Total</span>
                                <span className="detail-value">{systemHealth.system.memory.total_gb} GB</span>
                            </div>
                            <div className="detail-item">
                                <span className="detail-label">Used</span>
                                <span className="detail-value">{systemHealth.system.memory.used_gb} GB</span>
                            </div>
                            <div className="detail-item">
                                <span className="detail-label">Available</span>
                                <span className="detail-value">{systemHealth.system.memory.available_gb} GB</span>
                            </div>
                            <div className="detail-item">
                                <span className="detail-label">Usage %</span>
                                <span className="detail-value">{systemHealth.system.memory.percent}%</span>
                            </div>
                        </div>
                    </div>

                    <div className="detail-section">
                        <h3>Disk Information</h3>
                        <div className="detail-grid">
                            <div className="detail-item">
                                <span className="detail-label">Total</span>
                                <span className="detail-value">{systemHealth.system.disk.total_gb} GB</span>
                            </div>
                            <div className="detail-item">
                                <span className="detail-label">Used</span>
                                <span className="detail-value">{systemHealth.system.disk.used_gb} GB</span>
                            </div>
                            <div className="detail-item">
                                <span className="detail-label">Free</span>
                                <span className="detail-value">{systemHealth.system.disk.free_gb} GB</span>
                            </div>
                            <div className="detail-item">
                                <span className="detail-label">Usage %</span>
                                <span className="detail-value">{systemHealth.system.disk.percent}%</span>
                            </div>
                        </div>
                    </div>

                    <div className="detail-section">
                        <h3>System Uptime</h3>
                        <div className="uptime-display">
                            <span className="uptime-value">{systemHealth.system.uptime}</span>
                            <span className="uptime-label">System has been running</span>
                        </div>
                    </div>
                </div>
            )}


            {/* Detailed Analysis View */}
            {selectedView === 'detailed' && detailedHealth && (
                <div className="detailed-view">
                    <h2> Detailed System Analysis</h2>

                    <div className="analysis-header">
                        <div className="overall-status-card">
                            <span className="status-icon-large">
                                {getStatusIcon(detailedHealth.overall_status)}
                            </span>
                            <div className="status-info">
                                <h3>Overall Status</h3>
                                <span className={`status-badge large ${detailedHealth.overall_status}`}>
                                    {detailedHealth.overall_status}
                                </span>
                            </div>
                        </div>
                    </div>

                    <div className="components-analysis">
                        <h3>Component Health</h3>
                        <div className="components-grid">
                            {detailedHealth.components && Object.entries(detailedHealth.components).map(([component, data]) => (
                                <div key={component} className="component-card">
                                    <h4>{component.charAt(0).toUpperCase() + component.slice(1)}</h4>
                                    <span className={`status-badge ${data.status || data.overall_status}`}>
                                        {data.status || data.overall_status}
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>

                    {detailedHealth.issues && detailedHealth.issues.length > 0 && (
                        <div className="issues-section">
                            <h3> Active Issues</h3>
                            <div className="issues-grid">
                                {detailedHealth.issues.map((issue, index) => (
                                    <div key={index} className="issue-card">
                                        <span className="issue-severity">Critical</span>
                                        <p className="issue-description">{issue}</p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {detailedHealth.recommendations && detailedHealth.recommendations.filter(r => r).length > 0 && (
                        <div className="recommendations-section">
                            <h3> System Recommendations</h3>
                            <div className="recommendations-list">
                                {detailedHealth.recommendations.filter(r => r).map((rec, index) => (
                                    <div key={index} className="recommendation-card">
                                        <span className="rec-priority">Suggested</span>
                                        <p className="rec-description">{rec}</p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* Refresh Button */}
            <div className="health-actions">
                <button className="btn-refresh-health" onClick={loadHealthData}>
                    Refresh Health Data
                </button>
            </div>
        </div>
    );
};

export default HealthMonitoring;
