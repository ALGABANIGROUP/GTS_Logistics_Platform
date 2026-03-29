import React, { useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './AIBotsPanel.css';

const botList = [
    {
        id: 'general_manager',
        name: 'AI General Manager',
        description: 'Executive oversight and strategic reporting.',
        color: '#4F46E5',
        status: 'active'
    },
    {
        id: 'operations_manager_bot',
        name: 'AI Operations Manager',
        description: 'Coordinates daily operations and workflow orchestration between bots.',
        color: '#2563EB',
        status: 'active'
    },
    {
        id: 'ai_dispatcher',
        name: 'AI Dispatcher',
        description: 'Real-time dispatch management and task distribution.',
        color: '#0EA5E9',
        status: 'active'
    },
    {
        id: 'information_coordinator',
        name: 'AI Information Coordinator',
        description: 'Routes intelligence and connects data to operations.',
        color: '#6366F1',
        status: 'active'
    },
    {
        id: 'intelligence_bot',
        name: 'AI Intelligence Bot',
        description: 'Strategic analysis, executive insights, and reporting.',
        color: '#7C3AED',
        status: 'active'
    },
    {
        id: 'documents_manager',
        name: 'AI Documents Manager',
        description: 'Document archiving, compliance workflows, and file control.',
        color: '#F59E0B',
        status: 'active'
    },
    {
        id: 'customer_service',
        name: 'AI Customer Service',
        description: 'Automated customer support, notifications, and feedback analysis.',
        color: '#06B6D4',
        status: 'active'
    },
    {
        id: 'legal_bot',
        name: 'AI Legal Consultant',
        description: 'Reviews legal documents and ensures compliance.',
        color: '#64748B',
        status: 'active'
    },
    {
        id: 'maintenance_dev',
        name: 'AI Maintenance Dev',
        description: 'Monitors bot health, fixes bugs, and suggests system upgrades.',
        color: '#64748B',
        status: 'active'
    },
    {
        id: 'mapleload_bot',
        name: 'AI MapleLoad Canada',
        description: 'Canadian logistics intelligence and cross-border coordination.',
        color: '#F97316',
        status: 'active'
    },
    {
        id: 'safety_manager_bot',
        name: 'AI Safety Manager',
        description: 'Monitors safety data, incident reporting, and compliance checks.',
        color: '#F97316',
        status: 'active'
    },
    {
        id: 'sales_bot',
        name: 'AI Sales Bot',
        description: 'CRM insights, lead management, and revenue analysis.',
        color: '#10B981',
        status: 'active'
    },
    {
        id: 'security_manager_bot',
        name: 'AI Security Manager',
        description: 'Security monitoring, threat detection, and compliance auditing.',
        color: '#EF4444',
        status: 'active'
    },
    {
        id: 'system_manager_bot',
        name: 'AI System Manager',
        description: 'System performance, infrastructure health, and optimization.',
        color: '#475569',
        status: 'active'
    },
    {
        id: 'trainer_bot',
        name: 'AI Trainer Bot',
        description: 'Training and simulation orchestration for bot readiness before production rollout.',
        color: '#14B8A6',
        status: 'active'
    }
];

const deriveIcon = (name = '') => {
    const parts = name.split(/\s+/).filter(Boolean);
    if (parts.length === 0) return 'AI';
    const initials = parts.map((part) => part[0].toUpperCase()).join('');
    return initials.slice(0, 3);
};

const ROUTE_BY_ID = {
    general_manager: '/ai-bots/general-manager',
    operations_manager_bot: '/ai-bots/operations',
    ai_dispatcher: '/ai-bots/aid-dispatcher',
    information_coordinator: '/ai-bots/information',
    intelligence_bot: '/ai-bots/control?bot=intelligence_bot',
    documents_manager: '/ai-bots/documents',
    customer_service: '/ai-bots/customer-service',
    legal_bot: '/ai-bots/legal',
    maintenance_dev: '/ai-bots/maintenance-dashboard',
    mapleload_bot: '/ai-bots/mapleload-canada',
    safety_manager_bot: '/ai-bots/safety_manager',
    sales_bot: '/ai-bots/sales',
    security_manager_bot: '/ai-bots/security_manager',
    system_manager_bot: '/ai-bots/system-admin',
    trainer_bot: '/ai-bots/control?bot=trainer_bot',
};

const CONTROL_ROUTE_BY_ID = {
    general_manager: '/ai-bots/general-manager',
    operations_manager_bot: '/ai-bots/operations-manager',
    ai_dispatcher: '/ai-bots/aid-dispatcher',
    information_coordinator: '/ai-bots/information',
    intelligence_bot: '/ai-bots/control?bot=intelligence_bot',
    documents_manager: '/ai-bots/documents',
    customer_service: '/ai-bots/customer-service',
    legal_bot: '/ai-bots/legal',
    maintenance_dev: '/ai-bots/maintenance-dashboard',
    mapleload_bot: '/ai-bots/mapleload-canada',
    safety_manager_bot: '/ai-bots/safety_manager',
    sales_bot: '/ai-bots/sales',
    security_manager_bot: '/ai-bots/security_manager',
    system_manager_bot: '/ai-bots/system-admin',
    trainer_bot: '/ai-bots/control?bot=trainer_bot',
};

const AIBotsPanel = () => {
    const navigate = useNavigate();
    const [searchTerm, setSearchTerm] = useState('');
    const bots = useMemo(() => botList, []);

    const filteredBots = useMemo(
        () =>
            bots.filter((bot) =>
                bot.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                bot.description.toLowerCase().includes(searchTerm.toLowerCase())
            ),
        [searchTerm, bots]
    );

    const buildQuickRunRoute = (botId) => {
        const baseRoute = ROUTE_BY_ID[botId] || `/ai-bots/${botId}`;
        return `${baseRoute}${baseRoute.includes('?') ? '&' : '?'}quick=1`;
    };

    const handleCardAction = (event, path) => {
        event.preventDefault();
        event.stopPropagation();
        navigate(path);
    };

    return (
        <div className="ai-bots-panel">
            {/* Header */}
            <header className="panel-header">
                <div className="header-content">
                    <h1>AI Bots Panel</h1>
                    <p className="subtitle">Run operational and strategic assistants</p>
                </div>

                <div className="header-actions">
                    <div className="search-container">
                        <input
                            type="text"
                            placeholder="Search bots..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="search-input"
                        />
                        <span className="search-icon">Search</span>
                    </div>

                    <div className="stats-badge">
                        <span className="stat-value">{bots.length}</span>
                        <span className="stat-label">Active Bots</span>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="panel-main">
                <div className="bots-grid">
                    {filteredBots.map((bot) => (
                        <Link
                            to={ROUTE_BY_ID[bot.id] || `/ai-bots/${bot.id}`}
                            key={bot.id}
                            className="bot-card-link"
                        >
                            <div className="bot-card" style={{ '--bot-color': bot.color }}>
                                <div className="bot-card-header">
                                    <div className="bot-icon" style={{ color: bot.color }}>
                                        {deriveIcon(bot.name)}
                                    </div>
                                    <div className="bot-info">
                                        <h3>{bot.name}</h3>
                                        <span className={`status-badge ${bot.status}`}>
                                            {bot.status === 'active' ? 'Active' : 'Inactive'}
                                        </span>
                                    </div>
                                </div>

                                <p className="bot-description">{bot.description}</p>

                                <div className="bot-card-footer">
                                    <button
                                        type="button"
                                        className="control-btn"
                                        onClick={(event) =>
                                            handleCardAction(
                                                event,
                                                CONTROL_ROUTE_BY_ID[bot.id] || ROUTE_BY_ID[bot.id] || `/ai-bots/${bot.id}`
                                            )
                                        }
                                    >
                                        Control Panel
                                    </button>
                                    <button
                                        type="button"
                                        className="quick-run"
                                        onClick={(event) => handleCardAction(event, buildQuickRunRoute(bot.id))}
                                    >
                                        Quick Run
                                    </button>
                                </div>
                            </div>
                        </Link>
                    ))}
                </div>
            </main>
        </div>
    );
};

export default AIBotsPanel;
