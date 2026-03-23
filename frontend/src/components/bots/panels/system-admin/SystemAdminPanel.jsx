// src/components/bots/panels/system-admin/SystemAdminPanel.jsx
import React, { useState, useEffect } from 'react';
import HealthMonitoring from './HealthMonitoring';
import UserManagement from './UserManagement';
import DataManagement from './DataManagement';
import SecurityAudit from './SecurityAudit';
import PlatformExpenses from '../finance-bot/PlatformExpenses';
import PlatformFeatures from './PlatformFeatures';
import { adminService } from '../../../../services/adminService';
import './SystemAdminPanel.css';

const SystemAdminPanel = () => {
    const [activeTab, setActiveTab] = useState('health');
    const [botConfig, setBotConfig] = useState(null);
    const [dashboardStats, setDashboardStats] = useState({
        systemStatus: 'loading',
        activeUsers: 0,
        dbSizeLabel: 'N/A',
        cpuUsageLabel: 'N/A'
    });
    const [notifications, setNotifications] = useState([]);
    const [refreshKey, setRefreshKey] = useState(0);

    useEffect(() => {
        initializeBotConfig();
        loadDashboardStats();

        const interval = setInterval(() => {
            loadDashboardStats();
        }, 30000); // Refresh every 30 seconds

        return () => clearInterval(interval);
    }, []);

    const initializeBotConfig = () => {
        const config = {
            name: "System Admin Bot",
            description: "Comprehensive administration system - full management, monitoring, and control",
            status: "active",
            version: "1.0.0",
            lastUpdated: new Date().toISOString().split('T')[0],
            tabs: [
                { id: 'health', name: 'Health Monitoring', icon: '', description: 'System health monitoring' },
                { id: 'users', name: 'User Management', icon: '', description: 'User administration' },
                { id: 'data', name: 'Data Management', icon: '', description: 'Data operations' },
                { id: 'security', name: 'Security & Audit', icon: '', description: 'Security and audit logs' },
                { id: 'expenses', name: 'Platform Expenses', icon: '', description: 'Platform expenses and invoices' },
                { id: 'features', name: 'Platform Features', icon: '', description: 'Platform features and plan comparison' }
            ]
        };

        setBotConfig(config);
    };

    const loadDashboardStats = async () => {
        try {
            const [dashboardData, systemHealth, usersStats, databaseHealth] = await Promise.all([
                adminService.getDashboardStats(),
                adminService.getSystemHealth(),
                adminService.getUsersStatistics(),
                adminService.getDatabaseHealth()
            ]);

            const activeUsersCount = usersStats?.summary?.active_users ?? 0;
            const dbSizeValue = databaseHealth?.database?.size_gb;
            const cpuValue = systemHealth?.system?.cpu?.percent;

            const dbSizeLabel = Number.isFinite(dbSizeValue) ? `${dbSizeValue} GB` : 'N/A';
            const cpuUsageLabel = Number.isFinite(cpuValue) ? `${cpuValue}%` : 'N/A';

            setDashboardStats({
                systemStatus: dashboardData?.status || 'unknown',
                activeUsers: activeUsersCount,
                dbSizeLabel,
                cpuUsageLabel
            });
        } catch (error) {
            // Silently handle - fallback data is already being used
        }
    };

    const addNotification = (message, icon = '') => {
        const notification = {
            id: Date.now(),
            message,
            icon,
            time: new Date().toLocaleTimeString(),
            read: false
        };

        setNotifications(prev => [notification, ...prev.slice(0, 9)]);

        setTimeout(() => {
            setNotifications(prev => prev.filter(n => n.id !== notification.id));
        }, 5000);
    };

    const handleRefresh = () => {
        setRefreshKey(prev => prev + 1);
        loadDashboardStats();
        addNotification('Dashboard refreshed', '');
    };

    const renderTabContent = () => {
        const commonProps = {
            onNewNotification: addNotification,
            refreshKey: refreshKey
        };

        switch (activeTab) {
            case 'health':
                return <HealthMonitoring {...commonProps} />;
            case 'users':
                return <UserManagement {...commonProps} />;
            case 'data':
                return <DataManagement {...commonProps} />;
            case 'security':
                return <SecurityAudit {...commonProps} />;
            case 'expenses':
                return <PlatformExpenses />;
            case 'features':
                return <PlatformFeatures />;
            default:
                return <HealthMonitoring {...commonProps} />;
        }
    };

    if (!botConfig) return <div className="loading-panel"> Loading System Admin Bot...</div>;

    return (
        <div className="system-admin-panel">
            {/* Header */}
            <div className="admin-panel-header">
                <div className="header-title">
                    <h1> {botConfig.name}</h1>
                    <span className={`status-badge ${dashboardStats.systemStatus}`}>
                        {dashboardStats.systemStatus}
                    </span>
                </div>
                <div className="header-stats">
                    <div className="stat-card">
                        <span className="stat-icon"></span>
                        <div className="stat-content">
                            <span className="stat-value">{dashboardStats.activeUsers}</span>
                            <span className="stat-label">Active Users</span>
                        </div>
                    </div>
                    <div className="stat-card">
                        <span className="stat-icon"></span>
                        <div className="stat-content">
                            <span className="stat-value">{dashboardStats.dbSizeLabel}</span>
                            <span className="stat-label">Database</span>
                        </div>
                    </div>
                    <div className="stat-card">
                        <span className="stat-icon"></span>
                        <div className="stat-content">
                            <span className="stat-value">{dashboardStats.cpuUsageLabel}</span>
                            <span className="stat-label">CPU Usage</span>
                        </div>
                    </div>
                    <button
                        className="btn-refresh-dashboard"
                        onClick={handleRefresh}
                        title="Refresh Dashboard"
                    >
                        Refresh
                    </button>
                </div>
            </div>

            {/* Tab Navigation */}
            <div className="admin-tab-navigation">
                {botConfig.tabs.map(tab => (
                    <button
                        key={tab.id}
                        className={`admin-tab-btn ${activeTab === tab.id ? 'active' : ''}`}
                        onClick={() => setActiveTab(tab.id)}
                        title={tab.description}
                    >
                        <span className="tab-icon">{tab.icon}</span>
                        <div className="tab-content">
                            <span className="tab-name">{tab.name}</span>
                            <span className="tab-description">{tab.description}</span>
                        </div>
                    </button>
                ))}
            </div>

            {/* Notifications */}
            {notifications.length > 0 && (
                <div className="admin-notifications">
                    {notifications.slice(0, 3).map(notif => (
                        <div key={notif.id} className="notification-item">
                            <span className="notif-icon">{notif.icon}</span>
                            <span className="notif-message">{notif.message}</span>
                            <span className="notif-time">{notif.time}</span>
                        </div>
                    ))}
                </div>
            )}

            {/* Tab Content */}
            <div className="admin-tab-content">
                {renderTabContent()}
            </div>

            {/* Footer Info */}
            <div className="admin-panel-footer">
                <div className="footer-info">
                    <span>Version: {botConfig.version}</span>
                    <span>Last Updated: {botConfig.lastUpdated}</span>
                    <span>Status: {botConfig.status.toUpperCase()}</span>
                </div>
            </div>
        </div>
    );
};

export default SystemAdminPanel;
