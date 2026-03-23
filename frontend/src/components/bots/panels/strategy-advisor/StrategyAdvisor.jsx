import React, { useEffect, useState } from 'react';
import {
    StrategyDashboard,
    MarketAnalysis,
    CompetitorIntel,
    RecommendationsPanel,
    ConsultationPanel
} from './index';
import strategyService from '../../../../services/strategyService';
import './StrategyAdvisor.css';

const TABS = [
    { key: 'dashboard', label: 'Dashboard' },
    { key: 'market', label: 'Market Analysis' },
    { key: 'competitors', label: 'Competitor Intel' },
    { key: 'recommendations', label: 'Recommendations' },
    { key: 'consult', label: 'Consultation' }
];

const StrategyAdvisor = () => {
    const [activeTab, setActiveTab] = useState('dashboard');
    const [dashboardData, setDashboardData] = useState(null);
    const [loadingDashboard, setLoadingDashboard] = useState(true);
    const [error, setError] = useState(null);
    const [refreshKey, setRefreshKey] = useState(0);
    const [notifications, setNotifications] = useState([]);

    useEffect(() => {
        loadDashboard();
        const interval = setInterval(() => {
            loadDashboard();
        }, 60000);
        return () => clearInterval(interval);
    }, [refreshKey]);

    const loadDashboard = async () => {
        try {
            setLoadingDashboard(true);
            const data = await strategyService.getDashboard();
            setDashboardData(data);
            setError(null);
        } catch (err) {
            setError('Failed to load dashboard');
        } finally {
            setLoadingDashboard(false);
        }
    };

    const handleRefresh = () => setRefreshKey((prev) => prev + 1);

    const pushNotification = (message, type = 'info') => {
        const id = Date.now();
        setNotifications((prev) => [...prev, { id, message, type }]);
        setTimeout(() => {
            setNotifications((prev) => prev.filter((n) => n.id !== id));
        }, 5000);
    };

    const renderTab = () => {
        switch (activeTab) {
            case 'dashboard':
                return (
                    <StrategyDashboard
                        data={dashboardData}
                        loading={loadingDashboard}
                        onRefresh={handleRefresh}
                    />
                );
            case 'market':
                return <MarketAnalysis pushNotification={pushNotification} />;
            case 'competitors':
                return <CompetitorIntel pushNotification={pushNotification} />;
            case 'recommendations':
                return <RecommendationsPanel pushNotification={pushNotification} />;
            case 'consult':
                return <ConsultationPanel pushNotification={pushNotification} />;
            default:
                return null;
        }
    };

    return (
        <div className="strategy-advisor-panel">
            <header className="strategy-header">
                <div className="header-left">
                    <div className="bot-badge">AI</div>
                    <div>
                        <p className="eyebrow">AI Strategy Advisor</p>
                        <h1>Strategic Intelligence for Gabani Transport Solutions (GTS)</h1>
                        <p className="subtitle">Market analysis, competitive intelligence, and actionable recommendations.</p>
                    </div>
                </div>
                <div className="header-actions">
                    <button className="secondary" onClick={handleRefresh}>Refresh</button>
                    <span className={`status-pill ${dashboardData?.status === 'active' ? 'ok' : 'warn'}`}>
                        {dashboardData?.status === 'active' ? 'Active' : 'Idle'}
                    </span>
                </div>
            </header>

            <div className="tab-bar">
                {TABS.map((tab) => (
                    <button
                        key={tab.key}
                        className={tab.key === activeTab ? 'tab active' : 'tab'}
                        onClick={() => setActiveTab(tab.key)}
                    >
                        {tab.label}
                    </button>
                ))}
            </div>

            <div className="tab-content">
                {renderTab()}
            </div>

            {notifications.length > 0 && (
                <div className="toast-container">
                    {notifications.map((n) => (
                        <div key={n.id} className={`toast ${n.type}`}>
                            {n.message}
                        </div>
                    ))}
                </div>
            )}

            {error && <div className="error-banner">{error}</div>}
        </div>
    );
};

export default StrategyAdvisor;
