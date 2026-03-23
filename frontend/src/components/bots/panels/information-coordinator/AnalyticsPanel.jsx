// Analytics Panel Component
import React, { useState, useEffect } from 'react';
import informationService from '../../../../services/informationService';
import './OperationalDashboard.css';

const AnalyticsPanel = ({ onNewNotification, refreshKey }) => {
    const [loading, setLoading] = useState(false);
    const [analyticsType, setAnalyticsType] = useState('shipments');
    const [dateRange, setDateRange] = useState({
        start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        end: new Date().toISOString().split('T')[0]
    });
    const [analyticsData, setAnalyticsData] = useState(null);

    useEffect(() => {
        loadAnalytics();
    }, [analyticsType, refreshKey]);

    const loadAnalytics = async () => {
        setLoading(true);
        try {
            let data;
            switch (analyticsType) {
                case 'shipments':
                    data = await informationService.getShipmentsAnalytics(dateRange.start, dateRange.end);
                    break;
                case 'financial':
                    data = await informationService.getFinancialAnalytics(dateRange.start, dateRange.end);
                    break;
                case 'inventory':
                    data = await informationService.getInventoryAnalytics();
                    break;
                case 'customers':
                    data = await informationService.getCustomerAnalytics(dateRange.start, dateRange.end);
                    break;
                default:
                    data = null;
            }
            setAnalyticsData(data);
        } catch (error) {
            onNewNotification?.('Failed to load analytics', 'error');
        } finally {
            setLoading(false);
        }
    };

    const handleDateChange = (e) => {
        setDateRange(prev => ({ ...prev, [e.target.name]: e.target.value }));
    };

    const applyDateFilter = () => {
        loadAnalytics();
    };

    return (
        <div className="analytics-panel">
            {/* Analytics Controls */}
            <div className="analytics-controls">
                <div className="analytics-type-selector">
                    {['shipments', 'financial', 'inventory', 'customers'].map(type => (
                        <button
                            key={type}
                            className={`type-button ${analyticsType === type ? 'active' : ''}`}
                            onClick={() => setAnalyticsType(type)}
                        >
                            {type.charAt(0).toUpperCase() + type.slice(1)}
                        </button>
                    ))}
                </div>
                <div className="date-range-picker">
                    <input
                        type="date"
                        name="start"
                        value={dateRange.start}
                        onChange={handleDateChange}
                        className="date-input"
                    />
                    <span>to</span>
                    <input
                        type="date"
                        name="end"
                        value={dateRange.end}
                        onChange={handleDateChange}
                        className="date-input"
                    />
                    <button onClick={applyDateFilter} className="apply-button">
                        Apply
                    </button>
                </div>
            </div>

            {/* Analytics Content */}
            {loading ? (
                <div className="loading-container">
                    <div className="loading-spinner"></div>
                    <p>Loading analytics...</p>
                </div>
            ) : analyticsData ? (
                <div className="analytics-content">
                    <div className="analytics-info">
                        <h3> {analyticsType.charAt(0).toUpperCase() + analyticsType.slice(1)} Analytics</h3>
                        <p className="analytics-description">
                            Comprehensive analysis from {dateRange.start} to {dateRange.end}
                        </p>
                    </div>

                    <div className="analytics-results">
                        <pre className="analytics-json">
                            {JSON.stringify(analyticsData, null, 2)}
                        </pre>

                        <div className="analytics-note">
                            <span className="note-icon"></span>
                            <p>Backend analytics integration required for detailed visualizations and insights.</p>
                        </div>
                    </div>
                </div>
            ) : (
                <div className="empty-state">
                    <span className="empty-icon"></span>
                    <p>No analytics data available</p>
                </div>
            )}
        </div>
    );
};

export default AnalyticsPanel;
