// src/components/UnifiedBotsDashboard.tsx
import React, { useState, useMemo, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { unifiedBots, getBotStats, Bot, BotStatus, BotCategory, getBotHierarchy } from '../../data/botsData';
import './UnifiedBotsDashboard.css';

const UnifiedBotsDashboard: React.FC = () => {
    const navigate = useNavigate();
    const [selectedCategory, setSelectedCategory] = useState<BotCategory | 'all'>('all');
    const [selectedStatus, setSelectedStatus] = useState<BotStatus | 'all'>('all');
    const [searchTerm, setSearchTerm] = useState('');
    const [viewMode, setViewMode] = useState<'grid' | 'list' | 'table'>('grid');
    const [showHierarchy, setShowHierarchy] = useState(false);
    const [selectedBot, setSelectedBot] = useState<Bot | null>(null);

    const stats = useMemo(() => getBotStats(unifiedBots), []);
    const hierarchy = useMemo(() => getBotHierarchy(), []);

    const filteredBots = useMemo(() => {
        return unifiedBots.filter(bot => {
            // Filter by category
            if (selectedCategory !== 'all' && bot.category !== selectedCategory) {
                return false;
            }

            // Filter by status
            if (selectedStatus !== 'all' && bot.status !== selectedStatus) {
                return false;
            }

            // Filter by search term
            if (searchTerm) {
                const term = searchTerm.toLowerCase();
                const matches =
                    bot.name.toLowerCase().includes(term) ||
                    bot.displayName.toLowerCase().includes(term) ||
                    bot.description.toLowerCase().includes(term) ||
                    (bot.email && bot.email.toLowerCase().includes(term)) ||
                    (bot.secondaryEmail && bot.secondaryEmail.toLowerCase().includes(term));

                if (!matches) return false;
            }

            return true;
        });
    }, [selectedCategory, selectedStatus, searchTerm]);

    const getStatusColor = (status: BotStatus) => {
        switch (status) {
            case 'active': return '#10b981';
            case 'intelligence_mode': return '#f59e0b';
            case 'paused': return '#6b7280';
            case 'stopped': return '#ef4444';
            default: return '#6b7280';
        }
    };

    const getHealthColor = (health: Bot['health']) => {
        switch (health) {
            case 'excellent': return '#10b981';
            case 'good': return '#22c55e';
            case 'warning': return '#f59e0b';
            case 'critical': return '#ef4444';
            default: return '#6b7280';
        }
    };

    const sendTestEmail = (bot: Bot) => {
        if (!bot.email) {
            alert(`No email configured for ${bot.displayName}.`);
            return;
        }

        const subject = encodeURIComponent(`Bot Test Email - ${bot.displayName}`);
        const body = encodeURIComponent(
            `Hello,

This is a test email for ${bot.name}.

Sent at: ${new Date().toLocaleString('en-US')}
Bot Name: ${bot.displayName}
Bot Key: ${bot.key}
Status: ${getStatusText(bot.status)}

Regards,
GTS Bot Ops
`
        );

        window.open(`mailto:${bot.email}?subject=${subject}&body=${body}`, '_blank');
    };

    const viewBotDetails = (bot: Bot) => {
        setSelectedBot(bot);
    };

    const closeBotDetails = () => {
        setSelectedBot(null);
    };

    const runBot = (bot: Bot) => {
        navigate(`/ai-bots/control?bot=${encodeURIComponent(bot.key)}`);
    };

    const getCategoryIcon = (category: BotCategory) => {
        switch (category) {
            case 'management': return 'MGT';
            case 'operations': return 'OPS';
            case 'finance': return 'FIN';
            case 'services': return 'SVC';
            case 'intelligence': return 'INT';
            case 'marketing': return 'MKT';
            case 'maintenance': return 'MNT';
            case 'safety': return 'SAF';
            case 'security': return 'SEC';
            case 'sales': return 'SAL';
            case 'training': return 'TRN';
            default: return 'BOT';
        }
    };

    const getStatusText = (status: BotStatus) => {
        switch (status) {
            case 'active': return 'Active';
            case 'intelligence_mode': return 'Intelligence Mode';
            case 'paused': return 'Paused';
            case 'stopped': return 'Stopped';
            default: return 'Unknown';
        }
    };

    const getAutomationText = (level: Bot['automationLevel']) => {
        switch (level) {
            case 'full': return 'Full';
            case 'semi': return 'Semi';
            case 'manual': return 'Manual';
            default: return 'Unknown';
        }
    };

    const getHealthText = (health: Bot['health']) => {
        switch (health) {
            case 'excellent': return 'Excellent';
            case 'good': return 'Good';
            case 'warning': return 'Warning';
            case 'critical': return 'Critical';
            default: return 'Unknown';
        }
    };

    const exportBotsData = () => {
        const data = {
            exportedAt: new Date().toISOString(),
            totalBots: filteredBots.length,
            bots: filteredBots
        };

        const dataStr = JSON.stringify(data, null, 2);
        const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);

        const exportFileDefaultName = `bots-export-${new Date().toISOString().slice(0, 10)}.json`;

        const linkElement = document.createElement('a');
        linkElement.setAttribute('href', dataUri);
        linkElement.setAttribute('download', exportFileDefaultName);
        linkElement.click();
    };

    return (
        <div className="unified-bots-dashboard">
            <h1 className="dashboard-title">Unified AI Bots Dashboard</h1>
            <div className="dashboard-controls">
                <label htmlFor="category-select" className="select-label">Category:</label>
                <select id="category-select" title="Select category" value={selectedCategory} onChange={e => setSelectedCategory(e.target.value as BotCategory | 'all')}>
                    <option value="all">All Categories</option>
                    <option value="management">Management</option>
                    <option value="operations">Operations</option>
                    <option value="finance">Finance</option>
                    <option value="services">Services</option>
                    <option value="intelligence">Intelligence</option>
                    <option value="marketing">Marketing</option>
                    <option value="maintenance">Maintenance</option>
                    <option value="safety">Safety</option>
                    <option value="security">Security</option>
                    <option value="sales">Sales</option>
                    <option value="training">Training</option>
                </select>

                <label htmlFor="status-select" className="select-label">Status:</label>
                <select id="status-select" title="Select status" value={selectedStatus} onChange={e => setSelectedStatus(e.target.value as BotStatus | 'all')}>
                    <option value="all">All Statuses</option>
                    <option value="active">Active</option>
                    <option value="intelligence_mode">Intelligence Mode</option>
                    <option value="paused">Paused</option>
                    <option value="stopped">Stopped</option>
                </select>

                <input
                    type="text"
                    placeholder="Search bots..."
                    value={searchTerm}
                    onChange={e => setSearchTerm(e.target.value)}
                />
                <button className="export-btn" onClick={exportBotsData}>Export Data</button>
            </div>

            <div className="bots-grid">
                {filteredBots.length === 0 ? (
                    <div className="no-bots">No bots match your filters.</div>
                ) : (
                    filteredBots.map(bot => (
                        <div className="bot-card" key={bot.id}>
                            <div className="bot-header">
                                <span className="bot-category-icon">{getCategoryIcon(bot.category)}</span>
                                <span className="bot-title">{bot.displayName}</span>
                            </div>
                            <div className="bot-meta">
                                <span className={`bot-status status-${bot.status}`}>{getStatusText(bot.status)}</span>
                                <span className={`bot-health health-${bot.health}`}>{getHealthText(bot.health)}</span>
                                <span className="bot-automation">{getAutomationText(bot.automationLevel)}</span>
                            </div>
                            <div className="bot-description">{bot.description}</div>
                            <div className="bot-actions">
                                <button title="Control Panel" className="action-btn control-panel" onClick={() => viewBotDetails(bot)}>
                                    <span role="img" aria-label="Control Panel">CP</span> Control Panel
                                </button>
                                <button title="Quick Run" className="action-btn quick-run" onClick={() => runBot(bot)}>
                                    <span role="img" aria-label="Quick Run">RUN</span> Quick Run
                                </button>
                                <button title="Details" className="action-btn details" onClick={() => viewBotDetails(bot)}>
                                    <span role="img" aria-label="Details">INFO</span> Details
                                </button>
                                {bot.email && (
                                    <button title="Send Email" className="action-btn email" onClick={() => sendTestEmail(bot)}>
                                        <span role="img" aria-label="Send Email">MAIL</span> Email
                                    </button>
                                )}
                            </div>

                        </div>
                    ))
                )}
            </div>

            {selectedBot && (
                <div className="bot-details-modal" onClick={closeBotDetails}>
                    <div className="bot-details-content" onClick={e => e.stopPropagation()}>
                        <h2>{selectedBot.displayName}</h2>
                        <p>{selectedBot.description}</p>
                        <div>Status: <span className={`bot-status status-${selectedBot.status}`}>{getStatusText(selectedBot.status)}</span></div>
                        <div>Health: <span className={`bot-health health-${selectedBot.health}`}>{getHealthText(selectedBot.health)}</span></div>
                        <div>Automation: {getAutomationText(selectedBot.automationLevel)}</div>
                        {selectedBot.email && <div>Email: {selectedBot.email}</div>}
                        <button onClick={closeBotDetails}>Close</button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default UnifiedBotsDashboard;
