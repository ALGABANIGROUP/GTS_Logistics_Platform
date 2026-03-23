// src/components/bots/panels/dev-maintenance/DevMaintenancePanel.jsx
import React, { useState, useEffect } from 'react';
import DevMaintenanceLiveChat from './DevMaintenanceLiveChat';
import DevMaintenanceControlPanel from '../../DevMaintenanceControlPanel';
import './DevMaintenancePanel.css';

const DevMaintenancePanel = () => {
    const [activeTab, setActiveTab] = useState('dashboard');
    const [botConfig, setBotConfig] = useState(null);
    const [liveStats, setLiveStats] = useState({
        systemUptime: '99.97%',
        activeIssues: 0,
        pendingDeployments: 2,
        avgResponseTime: '142ms'
    });

    useEffect(() => {
        initializeBotConfig();
    }, []);

    const initializeBotConfig = () => {
        const config = {
            name: "AI Development & Maintenance Bot",
            description: "Technical support, bug tracking, and system monitoring",
            status: "active",
            version: "2.4.1",
            lastUpdated: new Date().toISOString().split('T')[0],

            tabs: [
                { id: 'dashboard', name: 'Control Panel', icon: '🎛️' },
                { id: 'livechat', name: 'Live Support', icon: '💬' },
                { id: 'monitoring', name: 'System Monitor', icon: '📊' },
                { id: 'bugs', name: 'Bug Tracker', icon: '🐛' },
                { id: 'deployments', name: 'Deployments', icon: '🚀' },
                { id: 'security', name: 'Security', icon: '🔒' }
            ]
        };

        setBotConfig(config);
    };

    const renderTabContent = () => {
        switch (activeTab) {
            case 'dashboard':
                return <DevMaintenanceControlPanel mode="active" />;
            case 'livechat':
                return <DevMaintenanceLiveChat />;
            case 'monitoring':
                return <SystemMonitoringView />;
            case 'bugs':
                return <BugTrackerView />;
            case 'deployments':
                return <DeploymentsView />;
            case 'security':
                return <SecurityView />;
            default:
                return <DevMaintenanceControlPanel mode="active" />;
        }
    };

    if (!botConfig) return <div className="loading-panel">Loading Dev & Maintenance Bot...</div>;

    return (
        <div className="dev-maintenance-panel" style={{ background: '#0f172a', minHeight: '100vh' }}>
            {/* Header */}
            <div style={{
                background: 'rgba(15, 23, 42, 0.8)',
                backdropFilter: 'blur(20px)',
                borderBottom: '1px solid rgba(148, 163, 184, 0.2)',
                padding: '16px 24px'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                        <div style={{
                            width: '48px',
                            height: '48px',
                            background: 'linear-gradient(135deg, #8b5cf6 0%, #3b82f6 100%)',
                            borderRadius: '12px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontSize: '24px'
                        }}>
                            🔧
                        </div>
                        <div>
                            <h1 style={{ color: 'white', fontSize: '20px', fontWeight: 'bold', margin: '0 0 4px 0' }}>
                                {botConfig.name}
                            </h1>
                            <p style={{ color: '#94a3b8', fontSize: '14px', margin: 0 }}>
                                {botConfig.description}
                            </p>
                        </div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                        <div style={{
                            background: 'rgba(34, 197, 94, 0.2)',
                            border: '1px solid rgba(34, 197, 94, 0.4)',
                            borderRadius: '8px',
                            padding: '6px 12px',
                            color: '#22c55e',
                            fontSize: '14px',
                            fontWeight: '600'
                        }}>
                            {botConfig.status.toUpperCase()}
                        </div>
                        <div style={{ color: '#94a3b8', fontSize: '14px' }}>
                            v{botConfig.version}
                        </div>
                    </div>
                </div>

                {/* Stats Bar */}
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                    gap: '16px',
                    marginTop: '16px'
                }}>
                    {[
                        { icon: '⚡', label: 'Uptime', value: liveStats.systemUptime },
                        { icon: '🐛', label: 'Active Issues', value: liveStats.activeIssues },
                        { icon: '🚀', label: 'Pending', value: liveStats.pendingDeployments },
                        { icon: '📊', label: 'Response', value: liveStats.avgResponseTime }
                    ].map((stat, i) => (
                        <div key={i} style={{
                            background: 'rgba(30, 41, 59, 0.4)',
                            border: '1px solid rgba(148, 163, 184, 0.2)',
                            borderRadius: '8px',
                            padding: '12px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '12px'
                        }}>
                            <span style={{ fontSize: '24px' }}>{stat.icon}</span>
                            <div>
                                <div style={{ color: 'white', fontSize: '18px', fontWeight: 'bold' }}>
                                    {stat.value}
                                </div>
                                <div style={{ color: '#94a3b8', fontSize: '12px' }}>
                                    {stat.label}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Tab Navigation */}
            <div style={{
                background: 'rgba(15, 23, 42, 0.6)',
                borderBottom: '1px solid rgba(148, 163, 184, 0.2)',
                padding: '0 24px',
                display: 'flex',
                gap: '8px',
                overflowX: 'auto'
            }}>
                {botConfig.tabs.map(tab => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        style={{
                            background: activeTab === tab.id
                                ? 'linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(59, 130, 246, 0.2) 100%)'
                                : 'transparent',
                            border: 'none',
                            borderBottom: activeTab === tab.id ? '2px solid #8b5cf6' : '2px solid transparent',
                            color: activeTab === tab.id ? 'white' : '#94a3b8',
                            padding: '16px 24px',
                            cursor: 'pointer',
                            fontSize: '14px',
                            fontWeight: '600',
                            transition: 'all 0.2s',
                            whiteSpace: 'nowrap',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px'
                        }}
                    >
                        <span>{tab.icon}</span>
                        <span>{tab.name}</span>
                    </button>
                ))}
            </div>

            {/* Tab Content */}
            <div>
                {renderTabContent()}
            </div>
        </div>
    );
};

// Placeholder components for other tabs
const SystemMonitoringView = () => (
    <div style={{ padding: '24px', color: 'white' }}>
        <h2>System Monitoring</h2>
        <p>Real-time system metrics and performance monitoring coming soon...</p>
    </div>
);

const BugTrackerView = () => (
    <div style={{ padding: '24px', color: 'white' }}>
        <h2>Bug Tracker</h2>
        <p>Comprehensive bug tracking and issue management coming soon...</p>
    </div>
);

const DeploymentsView = () => (
    <div style={{ padding: '24px', color: 'white' }}>
        <h2>Deployment Pipeline</h2>
        <p>CI/CD pipeline management and deployment tracking coming soon...</p>
    </div>
);

const SecurityView = () => (
    <div style={{ padding: '24px', color: 'white' }}>
        <h2>Security Dashboard</h2>
        <p>Security monitoring and threat detection coming soon...</p>
    </div>
);

export default DevMaintenancePanel;
