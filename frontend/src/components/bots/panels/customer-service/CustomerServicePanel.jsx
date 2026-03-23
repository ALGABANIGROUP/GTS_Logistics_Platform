// src/components/bots/panels/customer-service/CustomerServicePanel.jsx
import React, { useState, useEffect, useRef } from 'react';
import CustomerDashboard from './CustomerDashboard';
import ConversationManager from './ConversationManager';
import CallManager from './CallManager';
import MessageCenter from './MessageCenter';
import TicketSystem from './TicketSystem';
import LiveChat from './LiveChat';
import { customerServiceAPI, initWebSocket } from '../../../../services/customerService';
import './CustomerServicePanel.css';

const CustomerServicePanel = () => {
    const [activeTab, setActiveTab] = useState('dashboard');
    const [botConfig, setBotConfig] = useState(null);
    const [liveStats, setLiveStats] = useState({
        activeConversations: 0,
        pendingTickets: 0,
        avgResponseTime: '0m',
        satisfactionRate: '0%'
    });
    const [notifications, setNotifications] = useState([]);
    const wsRef = useRef(null);

    useEffect(() => {
        initializeBotConfig();
        initializeWebSocket();

        const interval = setInterval(updateLiveStats, 30000);

        return () => {
            clearInterval(interval);
            if (wsRef.current?.close) wsRef.current.close();
        };
    }, []);

    const initializeBotConfig = () => {
        const config = {
            name: "AI Customer Service Bot",
            description: "Intelligent customer support with messaging, calls, and AI automation",
            status: "active",
            version: "1.0.0",
            lastUpdated: new Date().toISOString().split('T')[0],

            tabs: [
                { id: 'dashboard', name: 'Dashboard', icon: '📊' },
                { id: 'livechat', name: 'Live Chat', icon: '💬' },
                { id: 'conversations', name: 'Conversations', icon: '💭' },
                { id: 'calls', name: 'Call Center', icon: '📞' },
                { id: 'messages', name: 'Message Center', icon: '📧' },
                { id: 'tickets', name: 'Tickets', icon: '🎫' }
            ]
        };

        setBotConfig(config);
    };

    const initializeWebSocket = async () => {
        try {
            wsRef.current = await initWebSocket({
                onMessage: handleWebSocketMessage,
                onOpen: () => console.log('Customer Service WebSocket connected'),
                onClose: () => console.log('Customer Service WebSocket disconnected'),
                onError: (error) => console.error('WebSocket error:', error)
            });
        } catch (error) {
            console.error('Failed to initialize WebSocket:', error);
        }
    };

    const handleWebSocketMessage = (data) => {
        switch (data.type) {
            case 'new_conversation':
                addNotification('New conversation started', '');
                updateLiveStats();
                break;
            case 'new_ticket':
                addNotification('New support ticket created', '');
                break;
            case 'call_started':
                addNotification('New call initiated', '');
                break;
            case 'ai_response':
                addNotification('AI generated response', '');
                break;
            default:
                break;
        }
    };

    const addNotification = (message, icon) => {
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

    const updateLiveStats = async () => {
        try {
            const stats = await customerServiceAPI.getLiveStats();
            setLiveStats(stats);
        } catch (error) {
            console.error('Failed to update live stats:', error);
        }
    };

    const renderTabContent = () => {
        const commonProps = {
            onNewNotification: addNotification,
            webSocket: wsRef.current
        };

        switch (activeTab) {
            case 'dashboard':
                return <CustomerDashboard stats={liveStats} notifications={notifications} {...commonProps} />;
            case 'livechat':
                return <LiveChat {...commonProps} />;
            case 'conversations':
                return <ConversationManager {...commonProps} />;
            case 'calls':
                return <CallManager {...commonProps} />;
            case 'messages':
                return <MessageCenter {...commonProps} />;
            case 'tickets':
                return <TicketSystem {...commonProps} />;
            default:
                return <CustomerDashboard stats={liveStats} notifications={notifications} {...commonProps} />;
        }
    };

    if (!botConfig) return <div className="loading-panel"> Loading Customer Service Bot...</div>;

    return (
        <div className="customer-service-panel">
            {/* Header */}
            <div className="panel-header">
                <div className="header-title">
                    <h1> {botConfig.name}</h1>
                    <span className="status-badge active">{botConfig.status}</span>
                </div>
                <div className="header-stats">
                    <div className="stat">
                        <span className="stat-icon"></span>
                        <span className="stat-value">{liveStats.activeConversations}</span>
                        <span className="stat-label">Active</span>
                    </div>
                    <div className="stat">
                        <span className="stat-icon"></span>
                        <span className="stat-value">{liveStats.pendingTickets}</span>
                        <span className="stat-label">Pending</span>
                    </div>
                    <div className="stat">
                        <span className="stat-icon"></span>
                        <span className="stat-value">{liveStats.avgResponseTime}</span>
                        <span className="stat-label">Avg Response</span>
                    </div>
                    <div className="stat">
                        <span className="stat-icon"></span>
                        <span className="stat-value">{liveStats.satisfactionRate}</span>
                        <span className="stat-label">Satisfaction</span>
                    </div>
                </div>
            </div>

            {/* Tab Navigation */}
            <div className="tab-navigation">
                {botConfig.tabs.map(tab => (
                    <button
                        key={tab.id}
                        className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
                        onClick={() => setActiveTab(tab.id)}
                    >
                        <span className="tab-icon">{tab.icon}</span>
                        <span className="tab-name">{tab.name}</span>
                    </button>
                ))}
            </div>

            {/* Notifications */}
            {notifications.length > 0 && (
                <div className="notifications-container">
                    {notifications.map(notif => (
                        <div key={notif.id} className="notification">
                            <span className="notif-icon">{notif.icon}</span>
                            <span className="notif-message">{notif.message}</span>
                            <span className="notif-time">{notif.time}</span>
                        </div>
                    ))}
                </div>
            )}

            {/* Tab Content */}
            <div className="tab-content">
                {renderTabContent()}
            </div>
        </div>
    );
};

export default CustomerServicePanel;
