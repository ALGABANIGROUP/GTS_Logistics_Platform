// src/components/bots/panels/customer-service/CustomerDashboard.jsx
import React, { useState, useEffect } from 'react';
import { customerServiceAPI } from '../../../../services/customerService';
import { metaDataService } from '../../../../services/metaDataService';
import './CustomerDashboard.css';

const CustomerDashboard = ({ stats, notifications, onNewNotification }) => {
    // Dynamic meta data
    const [trailerTypes, setTrailerTypes] = useState([]);
    const [locations, setLocations] = useState([]);

    useEffect(() => {
        metaDataService.getTrailerTypes().then(setTrailerTypes);
        metaDataService.getLocations().then(setLocations);
    }, []);
    const [timeRange, setTimeRange] = useState('today');
    const [recentActivity, setRecentActivity] = useState([]);
    const [topAgents, setTopAgents] = useState([]);
    const [conversationMetrics, setConversationMetrics] = useState({
        total: 0,
        resolved: 0,
        escalated: 0,
        avgDuration: '0m'
    });
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        loadDashboardData();
    }, [timeRange]);

    const loadDashboardData = async () => {
        setLoading(true);
        try {
            const [activity, agents, metrics] = await Promise.all([
                customerServiceAPI.getRecentActivity(timeRange),
                customerServiceAPI.getTopAgents(),
                customerServiceAPI.getConversationMetrics(timeRange)
            ]);

            setRecentActivity(activity);
            setTopAgents(agents);
            setConversationMetrics(metrics);
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
        } finally {
            setLoading(false);
        }
    };

    const quickActions = [
        {
            id: 'new_conversation',
            label: 'Start Conversation',
            icon: '',
            color: '#3b82f6',
            action: () => onNewNotification('New conversation started', '')
        },
        {
            id: 'new_ticket',
            label: 'Create Ticket',
            icon: '',
            color: '#10b981',
            action: () => onNewNotification('New support ticket created', '')
        },
        {
            id: 'send_broadcast',
            label: 'Send Broadcast',
            icon: '',
            color: '#f59e0b',
            action: () => onNewNotification('Broadcast message sent', '')
        },
        {
            id: 'make_call',
            label: 'Make Call',
            icon: '',
            color: '#8b5cf6',
            action: () => onNewNotification('Call initiated', '')
        }
    ];

    return (
        <div className="customer-dashboard">
            {/* Header */}
            <div className="dashboard-header">
                <h2>Dashboard Overview</h2>
                <div className="dashboard-controls">
                    <select
                        value={timeRange}
                        onChange={(e) => setTimeRange(e.target.value)}
                        className="time-range-select"
                    >
                        <option value="today">Today</option>
                        <option value="week">This Week</option>
                        <option value="month">This Month</option>
                        <option value="quarter">This Quarter</option>
                    </select>
                    <button
                        className="refresh-btn"
                        onClick={loadDashboardData}
                        disabled={loading}
                    >
                        {loading ? ' Loading...' : ' Refresh'}
                    </button>
                </div>
            </div>

            {/* Quick Actions */}
            <div className="quick-actions-grid">
                {quickActions.map((action) => (
                    <button
                        key={action.id}
                        className="quick-action-btn"
                        style={{
                            background: `linear-gradient(135deg, ${action.color}80 0%, ${action.color}40 100%)`,
                            borderColor: action.color
                        }}
                        onClick={action.action}
                    >
                        <span className="action-icon">{action.icon}</span>
                        <span className="action-label">{action.label}</span>
                    </button>
                ))}
            </div>

            {/* Live Stats */}
            <div className="stats-cards">
                <div className="stat-card">
                    <div className="stat-header">
                        <span className="stat-icon"></span>
                        <span className="stat-label">Active Conversations</span>
                    </div>
                    <div className="stat-value">{stats.activeConversations}</div>
                    <div className="stat-trend"> +5 this hour</div>
                </div>

                <div className="stat-card">
                    <div className="stat-header">
                        <span className="stat-icon"></span>
                        <span className="stat-label">Pending Tickets</span>
                    </div>
                    <div className="stat-value">{stats.pendingTickets}</div>
                    <div className="stat-trend"> -2 since yesterday</div>
                </div>

                <div className="stat-card">
                    <div className="stat-header">
                        <span className="stat-icon"></span>
                        <span className="stat-label">Avg Response Time</span>
                    </div>
                    <div className="stat-value">{stats.avgResponseTime}</div>
                    <div className="stat-trend"> -15% faster</div>
                </div>

                <div className="stat-card">
                    <div className="stat-header">
                        <span className="stat-icon"></span>
                        <span className="stat-label">Satisfaction Rate</span>
                    </div>
                    <div className="stat-value">{stats.satisfactionRate}</div>
                    <div className="stat-trend"> +3.2% improvement</div>
                </div>
            </div>

            {/* Content Grid */}
            <div className="dashboard-grid">
                {/* Quick Reference: Trailer Types & Locations */}
                <div className="section-card meta-card">
                    <h3>Trailer Types</h3>
                    <div className="meta-list">
                        {trailerTypes.length > 0 ? (
                            trailerTypes.map((type, idx) => (
                                <span key={idx} className="meta-item">{type}</span>
                            ))
                        ) : (
                            <span className="empty-state">No trailer types available</span>
                        )}
                    </div>
                    <h3>Canada/USA Cities and Provinces</h3>
                    <div className="meta-list">
                        {locations.length > 0 ? (
                            locations.slice(0, 10).map((loc, idx) => (
                                <span key={idx} className="meta-item">{loc}</span>
                            ))
                        ) : (
                            <span className="empty-state">No locations available</span>
                        )}
                        {locations.length > 10 && <span className="meta-item">... and more</span>}
                    </div>
                </div>

                {/* Recent Activity */}
                <div className="section-card activity-card">
                    <h3> Recent Activity</h3>
                    <div className="activity-feed">
                        {recentActivity.length > 0 ? (
                            recentActivity.map((activity) => (
                                <div key={activity.id} className="activity-item">
                                    <div className="activity-icon">{activity.icon || ''}</div>
                                    <div className="activity-content">
                                        <div className="activity-text">
                                            <strong>{activity.user || 'System'}</strong> {activity.action} <em>{activity.target}</em>
                                        </div>
                                        <div className="activity-time">{activity.time || 'now'}</div>
                                    </div>
                                </div>
                            ))
                        ) : (
                            <div className="empty-state">No recent activity</div>
                        )}
                    </div>
                </div>

                {/* Conversation Metrics */}
                <div className="section-card metrics-card">
                    <h3> Conversation Metrics</h3>
                    <div className="metrics-grid">
                        <div className="metric-item">
                            <span className="metric-label">Total</span>
                            <span className="metric-value">{conversationMetrics.total}</span>
                        </div>
                        <div className="metric-item">
                            <span className="metric-label">Resolved</span>
                            <span className="metric-value success">{conversationMetrics.resolved}</span>
                        </div>
                        <div className="metric-item">
                            <span className="metric-label">Escalated</span>
                            <span className="metric-value warning">{conversationMetrics.escalated}</span>
                        </div>
                        <div className="metric-item">
                            <span className="metric-label">Avg Duration</span>
                            <span className="metric-value">{conversationMetrics.avgDuration}</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Top Agents */}
            <div className="section-card">
                <h3> Top Performing Agents</h3>
                <div className="agents-list">
                    {topAgents.length > 0 ? (
                        topAgents.map((agent) => (
                            <div key={agent.id} className="agent-card">
                                <div className="agent-info">
                                    <div className="agent-avatar">{agent.avatar || agent.name?.charAt(0)}</div>
                                    <div className="agent-details">
                                        <div className="agent-name">{agent.name}</div>
                                        <div className="agent-role">{agent.role || 'Agent'}</div>
                                    </div>
                                </div>
                                <div className="agent-stats">
                                    <div className="stat">
                                        <span className="stat-label">Resolved</span>
                                        <span className="stat-value">{agent.resolved || 0}</span>
                                    </div>
                                    <div className="stat">
                                        <span className="stat-label">Rating</span>
                                        <span className="stat-value">{agent.rating || '0'}</span>
                                    </div>
                                </div>
                            </div>
                        ))
                    ) : (
                        <div className="empty-state">No agents data available</div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default CustomerDashboard;
