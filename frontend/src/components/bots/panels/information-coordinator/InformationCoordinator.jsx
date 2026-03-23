// Information Coordinator Bot - Main Panel
import React, { useState, useEffect } from 'react';
import OperationalDashboard from './OperationalDashboard';
import AnalyticsPanel from './AnalyticsPanel';
import ReportsManager from './ReportsManager';
import PredictionsView from './PredictionsView';
import informationService from '../../../../services/informationService';
import './InformationCoordinator.css';

const InformationCoordinator = () => {
    const [activeTab, setActiveTab] = useState('dashboard');
    const [botStatus, setBotStatus] = useState({
        status: 'loading',
        lastSync: null,
        tasksActive: 0
    });
    const [overviewStats, setOverviewStats] = useState({
        shipmentsToday: 0,
        revenueToday: 0,
        activeAlerts: 0,
        syncStatus: 'unknown'
    });
    const [notifications, setNotifications] = useState([]);
    const [refreshKey, setRefreshKey] = useState(0);

    useEffect(() => {
        loadBotStatus();
        loadOverviewStats();

        const interval = setInterval(() => {
            loadOverviewStats();
        }, 60000); // Refresh every minute

        return () => clearInterval(interval);
    }, []);

    const loadBotStatus = async () => {
        const status = await informationService.getCoordinatorStatus();
        setBotStatus({
            status: status.status || 'unknown',
            lastSync: status.last_sync,
            tasksActive: status.tasks_active || 0
        });
    };

    const loadOverviewStats = async () => {
        try {
            const [dashboard, alerts] = await Promise.all([
                informationService.getOperationalDashboard(),
                informationService.getSystemAlerts(null, 10)
            ]);

            setOverviewStats({
                shipmentsToday: dashboard.metrics?.shipments?.completed_today || 0,
                revenueToday: dashboard.metrics?.financial?.daily_revenue || 0,
                activeAlerts: alerts.unresolved || 0,
                syncStatus: dashboard.status || 'unknown'
            });
        } catch (error) {
            console.error('Failed to load overview stats:', error);
        }
    };

    const addNotification = (message, type = 'info') => {
        const notification = {
            id: Date.now(),
            message,
            type,
            time: new Date().toLocaleTimeString(),
            read: false
        };

        setNotifications(prev => [notification, ...prev.slice(0, 9)]);

        setTimeout(() => {
            setNotifications(prev => prev.filter(n => n.id !== notification.id));
        }, 5000);
    };

    const handleRefresh = async () => {
        setRefreshKey(prev => prev + 1);
        await loadBotStatus();
        await loadOverviewStats();
        addNotification('Data refreshed successfully', 'success');
    };

    const handleSync = async () => {
        addNotification('Starting data synchronization...', 'info');
        const result = await informationService.syncAllDataSources();

        if (result.status === 'completed') {
            addNotification('All data sources synchronized', 'success');
            await loadOverviewStats();
        } else {
            addNotification('Synchronization failed', 'error');
        }
    };

    const tabs = [
        { id: 'dashboard', name: 'Dashboard', icon: '', description: 'Operational overview and metrics' },
        { id: 'analytics', name: 'Analytics', icon: '', description: 'Data analysis and insights' },
        { id: 'predictions', name: 'Predictions', icon: '', description: 'AI-powered forecasts' },
        { id: 'reports', name: 'Reports', icon: '', description: 'Generate and manage reports' }
    ];

    const getStatusColor = (status) => {
        switch (status) {
            case 'running': return 'status-active';
            case 'stopped': return 'status-inactive';
            case 'error': return 'status-error';
            default: return 'status-unknown';
        }
    };

    const renderTabContent = () => {
        const commonProps = {
            onNewNotification: addNotification,
            refreshKey: refreshKey
        };

        switch (activeTab) {
            case 'dashboard':
                return <OperationalDashboard {...commonProps} />;
            case 'analytics':
                return <AnalyticsPanel {...commonProps} />;
            case 'predictions':
                return <PredictionsView {...commonProps} />;
            case 'reports':
                return <ReportsManager {...commonProps} />;
            default:
                return <OperationalDashboard {...commonProps} />;
        }
    };

    return (

        <div className="information-coordinator-panel">
            {/* Header */}
            <div className="coordinator-header">
                <div className="header-left">
                    <div className="bot-icon"></div>
                    <div className="bot-info">
                        <h1 className="bot-title">Information Coordinator</h1>
                        <p className="bot-description">
                            AI-powered data integration, analysis, and insights
                        </p>
                    </div>
                    <span className={`bot-status-badge ${getStatusColor(botStatus.status)}`}>
                        {botStatus.status}
                    </span>
                </div>
                <div className="header-right">
                    <button onClick={handleSync} className="sync-button">
                        Sync Data
                    </button>
                    <button onClick={handleRefresh} className="refresh-button">
                        Refresh
                    </button>
                </div>
            </div>

            {/* Overview Stats */}
            <div className="overview-stats">
                <div className="stat-card glass-card">
                    <div className="stat-icon"></div>
                    <div className="stat-content">
                        <div className="stat-value">{overviewStats.shipmentsToday}</div>
                        <div className="stat-label">Shipments Today</div>
                    </div>
                </div>
                <div className="stat-card glass-card">
                    <div className="stat-icon"></div>
                    <div className="stat-content">
                        <div className="stat-value">${overviewStats.revenueToday.toLocaleString()}</div>
                        <div className="stat-label">Revenue Today</div>
                    </div>
                </div>
                <div className="stat-card glass-card">
                    <div className="stat-icon"></div>
                    <div className="stat-content">
                        <div className="stat-value">{overviewStats.activeAlerts}</div>
                        <div className="stat-label">Active Alerts</div>
                    </div>
                </div>
                <div className="stat-card glass-card">
                    <div className="stat-icon"></div>
                    <div className="stat-content">
                        <div className="stat-value">{overviewStats.syncStatus}</div>
                        <div className="stat-label">Sync Status</div>
                    </div>
                </div>
            </div>

            {/* Tab Navigation */}
            <div className="coordinator-tabs">
                {tabs.map(tab => (
                    <button
                        key={tab.id}
                        className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
                        onClick={() => setActiveTab(tab.id)}
                    >
                        <span className="tab-icon">{tab.icon}</span>
                        <div className="tab-text">
                            <div className="tab-name">{tab.name}</div>
                            <div className="tab-description">{tab.description}</div>
                        </div>
                    </button>
                ))}
            </div>

            {/* Tab Content */}
            <div className="coordinator-content">
                {renderTabContent()}
            </div>

            {/* Notifications */}
            {notifications.length > 0 && (
                <div className="notifications-container">
                    {notifications.map(notification => (
                        <div key={notification.id} className={`notification notification-${notification.type}`}>
                            <span className="notification-icon">
                                {notification.type === 'success' ? '' :
                                    notification.type === 'error' ? '' : ''}
                            </span>
                            <span className="notification-message">{notification.message}</span>
                            <span className="notification-time">{notification.time}</span>
                        </div>
                    ))}
                </div>
            )}

            {/* Footer */}
            <div className="coordinator-footer">
                <div className="footer-left">
                    <span>Information Coordinator v2.0.0</span>
                    {botStatus.lastSync && (
                        <span className="last-sync">
                            Last sync: {new Date(botStatus.lastSync).toLocaleString()}
                        </span>
                    )}
                </div>
                <div className="footer-right">
                    <span>Active Tasks: {botStatus.tasksActive}</span>
                    <a href="/admin" className="footer-link">Admin Panel</a>
                </div>
            </div>
        </div>
    );
};

export default InformationCoordinator;
