import { useCallback, useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import axiosClient from '../api/axiosClient';
import { REGISTRATION_CONTACT, REGISTRATION_DISABLED_FLAG } from '../config/registration';
import { useAuth } from '../contexts/AuthContext';
import { formatTierLabel, normalizeTier } from '../utils/tierUtils';
import './AIBotsPanel.css';

/**
 * AI Bots Panel with Subscription-based Access Control
 * 
 * Displays available bots based on:
 * - Subscription type (free, starter, growth, professional, enterprise)
 * - User role (shipper, carrier, broker, admin, super_admin)
 * - System type (tms, loadboard)
 */

const ROUTE_BY_ID = {
    general_manager: '/ai-bots/general-manager',
    payment_bot: '/ai-bots/payment',
    finance_bot: '/ai-bots/finance',
    bot_finance: '/ai-bots/finance',
    finance: '/ai-bots/finance',
    operations_manager_bot: '/ai-bots/operations',
    ai_dispatcher: '/ai-bots/aid-dispatcher',
    freight_broker: '/ai-bots/freight_broker',
    ai_freight_broker: '/ai-bots/freight_broker',
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
    security_manager: '/ai-bots/security_manager',
    system_manager_bot: '/ai-bots/system-admin',
    maintenance_dev_cto: '/ai-bots/maintenance-dashboard',
    partner_manager: '/ai-bots/partner-management',
    marketing_manager: '/admin/ai/marketing-bot',
    trainer_bot: '/ai-bots/control?bot=trainer_bot',
};

const BOT_ID_ALIASES = {
    bot_finance: 'finance_bot',
    finance: 'finance_bot',
    payment: 'payment_bot',
    payment_gateway: 'payment_bot',
    ai_freight_broker: 'freight_broker',
    freightbroker: 'freight_broker',
    freight_broker_bot: 'freight_broker',
    operations_manager: 'operations_manager_bot',
    safety_manager: 'safety_manager_bot',
    security_manager: 'security_manager_bot',
    system_manager: 'system_manager_bot',
    trainer: 'trainer_bot',
    training_bot: 'trainer_bot',
};

const normalizeBots = (list = []) => {
    const safeList = Array.isArray(list) ? list : [];
    return safeList.map((bot) => {
        const rawId = String(bot?.id || '').trim();
        const normalizedId = BOT_ID_ALIASES[rawId] || rawId;

        return {
            ...bot,
            id: normalizedId,
            status: bot.status || 'active',
        };
    });
};

const maintenanceBot = {
    id: 'maintenance_dev',
    name: 'AI Dev Maintenance Bot (CTO)',
    description: 'Monitors platform health, auto-repair workflows, and CTO maintenance actions.',
    color: '#64748B',
    icon: 'CTO',
    category: 'Maintenance',
    status: 'active',
};

const REQUIRED_PANEL_BOTS = [
    {
        id: 'finance_bot',
        name: 'AI Finance Bot',
        description: 'Financial analysis, revenue tracking, expense management, and invoice processing.',
        color: '#16A34A',
        icon: 'FIN',
        category: 'Finance',
        status: 'active',
    },
    {
        id: 'payment_bot',
        name: 'Payment Gateway Dashboard',
        description: 'Secure payment processing, invoice management, transaction tracking, and finance bot integration.',
        color: '#2563EB',
        icon: 'PAY',
        category: 'Finance',
        status: 'active',
    },
    {
        id: 'marketing_manager',
        name: 'AI Marketing Manager',
        description: 'Campaign orchestration, lead nurturing, and marketing performance insights.',
        color: '#EC4899',
        icon: 'MKT',
        category: 'Marketing',
        status: 'active',
    },
    {
        id: 'partner_manager',
        name: 'AI Partner Manager',
        description: 'Partner operations, alliance workflows, and partner performance management.',
        color: '#8B5CF6',
        icon: 'PRT',
        category: 'Management',
        status: 'active',
    },
    {
        id: 'maintenance_dev',
        name: 'AI Dev Maintenance Bot (CTO)',
        description: 'Monitors platform health, auto-repair workflows, and CTO maintenance actions.',
        color: '#64748B',
        icon: 'CTO',
        category: 'Maintenance',
        status: 'active',
    },
    {
        id: 'security_manager_bot',
        name: 'AI Security Manager',
        description: 'Security monitoring, threat detection, and access control governance.',
        color: '#0EA5E9',
        icon: 'SEC',
        category: 'Security',
        status: 'active',
    },
    {
        id: 'trainer_bot',
        name: 'AI Trainer Bot',
        description: 'Training and simulation orchestration for bot readiness before production rollout.',
        color: '#14B8A6',
        icon: 'TRN',
        category: 'Training',
        status: 'active',
    },
];

const getFallbackBots = () => [
    {
        id: 'customer_service',
        name: 'AI Customer Service',
        description: 'Automated customer support and notifications',
        color: '#06B6D4',
        icon: 'CS',
        category: 'Basic',
        status: 'active',
    },
    {
        id: 'documents_manager',
        name: 'AI Documents Manager',
        description: 'Document archiving and file management',
        color: '#F59E0B',
        icon: 'DM',
        category: 'Basic',
        status: 'active',
    },
];

const deriveIcon = (icon, name = '') => {
    if (icon && icon !== 'AI') return icon;
    const parts = name.split(/\s+/).filter(Boolean);
    if (parts.length === 0) return 'AI';
    const initials = parts.map((part) => part[0].toUpperCase()).join('');
    return initials.slice(0, 3);
};

const AIBotsPanelEnhanced = () => {
    const [bots, setBots] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [subscriptionInfo, setSubscriptionInfo] = useState(null);
    const [selectedCategory, setSelectedCategory] = useState('All');
    const [services, setServices] = useState([]);

    const { user, role, plan, system } = useAuth();

    const userInfo = useMemo(() => {
        const normalizePlan = (value) => {
            if (!value) return null;
            if (typeof value === 'string') return value;
            return value.key || value.id || value.code || null;
        };

        const normalizeSystem = (value) => {
            if (!value) return null;
            if (typeof value === 'string') return value;
            return value.type || value.key || value.id || null;
        };

        const rawPlan = normalizePlan(plan) || user?.subscription_tier || user?.subscription || null;
        const rawSystem = normalizeSystem(system) || user?.system_type || user?.system || null;
        const rawRole = role || user?.role || 'shipper';
        const isAdmin = ['admin', 'super_admin'].includes(String(rawRole).toLowerCase());
        const normalizedPlan = normalizeTier(rawPlan);

        return {
            subscription: isAdmin ? 'enterprise' : (normalizedPlan || 'free'),
            role: isAdmin ? 'super_admin' : rawRole,
            system: rawSystem || 'tms',
            isAdmin,
        };
    }, [plan, system, role, user]);

    const withMaintenanceBot = useCallback(
        (list = []) => {
            const safeList = Array.isArray(list) ? list : [];
            if (!userInfo.isAdmin) return safeList;
            if (safeList.some((bot) => bot.id === maintenanceBot.id)) {
                return safeList;
            }
            return [...safeList, maintenanceBot];
        },
        [userInfo.isAdmin]
    );

    const withRequiredPanelBots = useCallback(
        (list = []) => {
            const safeList = Array.isArray(list) ? list : [];

            const aliasById = {
                finance: 'finance_bot',
                bot_finance: 'finance_bot',
                security_manager: 'security_manager_bot',
                maintenance_dev_cto: 'maintenance_dev',
                partner_management: 'partner_manager',
                ai_partner_manager: 'partner_manager',
                ai_marketing_manager: 'marketing_manager',
            };

            const existing = new Set(
                safeList
                    .map((bot) => String(bot?.id || '').trim())
                    .filter(Boolean)
                    .map((id) => aliasById[id] || id)
            );

            const merged = [...safeList];
            for (const requiredBot of REQUIRED_PANEL_BOTS) {
                if (!existing.has(requiredBot.id)) {
                    merged.push(requiredBot);
                }
            }

            return merged;
        },
        []
    );

    useEffect(() => {
        const fetchBots = async () => {
            try {
                setLoading(true);
                setError(null);

                try {
                    const userResponse = await axiosClient.get('/api/v1/ai/bots/current-user/available', {
                        params: { language: 'en' },
                    });

                    if (userResponse?.data) {
                        setBots(withRequiredPanelBots(withMaintenanceBot(normalizeBots(userResponse.data.bots || []))));
                        setServices(userResponse.data.services || []);
                        setSubscriptionInfo({
                            name_en: formatTierLabel(userResponse.data.subscription_tier),
                            total_bots: userResponse.data.total_count,
                        });
                        return;
                    }
                } catch (userErr) {
                    console.warn('User bots endpoint failed, using manual parameters:', userErr);
                }

                const response = await axiosClient.get('/api/v1/ai/bots/available', {
                    params: { language: 'en' },
                });

                if (response?.data) {
                    setBots(withRequiredPanelBots(withMaintenanceBot(normalizeBots(response.data.bots || []))));
                    setServices(response.data.services || []);

                    try {
                        const subResponse = await axiosClient.get('/api/v1/ai/bots/subscription-summary');
                        if (subResponse?.data) {
                            const normalizedName = subResponse?.data?.name_en || subResponse?.data?.name || subResponse?.data?.tier;
                            setSubscriptionInfo({
                                ...subResponse.data,
                                name_en: formatTierLabel(normalizedName),
                            });
                        } else {
                            setSubscriptionInfo(null);
                        }
                    } catch (subErr) {
                        console.warn('Unable to fetch subscription info:', subErr);
                        setSubscriptionInfo(null);
                    }
                } else {
                    setBots(withRequiredPanelBots(withMaintenanceBot(normalizeBots(getFallbackBots()))));
                    setServices([]);
                    setSubscriptionInfo(null);
                }
            } catch (err) {
                console.error('Error fetching bots:', err);
                setError('Failed to load available bots');
                setBots(withRequiredPanelBots(withMaintenanceBot(normalizeBots(getFallbackBots()))));
                setServices([]);
                setSubscriptionInfo(null);
            } finally {
                setLoading(false);
            }
        };

        fetchBots();
    }, [
        userInfo.subscription,
        userInfo.role,
        userInfo.system,
        userInfo.isAdmin,
        withMaintenanceBot,
        withRequiredPanelBots,
    ]);

    // Categorize bots
    const categories = useMemo(() => {
        const cats = new Set(['All']);
        bots.forEach((bot) => {
            if (bot.category) cats.add(bot.category);
        });
        return Array.from(cats);
    }, [bots]);

    // Filter bots
    const filteredBots = useMemo(() => {
        let filtered = bots;

        // Filter by category
        if (selectedCategory !== 'All') {
            filtered = filtered.filter((bot) => bot.category === selectedCategory);
        }

        // Filter by search
        if (searchTerm) {
            filtered = filtered.filter((bot) =>
                bot.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                bot.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                String(bot.id || '').toLowerCase().includes(searchTerm.toLowerCase())
            );
        }

        return filtered;
    }, [bots, selectedCategory, searchTerm]);

    const visibleTotal = subscriptionInfo?.total_bots
        ? Math.max(Number(subscriptionInfo.total_bots) || 0, bots.length)
        : bots.length;

    if (loading) {
        return (
            <div className="ai-bots-panel">
                <div className="loading-state">
                    <div className="spinner"></div>
                    <p>Loading available AI Bots...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="ai-bots-panel">
            {/* Header */}
            <header className="panel-header">
                <div className="header-content">
                    <h1>AI Bots Dashboard</h1>
                    <p className="subtitle">
                        {subscriptionInfo ? (
                            <>
                                Plan: <strong>{subscriptionInfo.name_en || subscriptionInfo.name}</strong> |
                                Available Bots: <strong>{bots.length}</strong> of {visibleTotal}
                            </>
                        ) : (
                            'Intelligent assistants for operations and strategy'
                        )}
                    </p>
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
                        <span className="stat-value">{filteredBots.length}</span>
                        <span className="stat-label">Active Bots</span>
                    </div>
                </div>
            </header>

            {/* Categories Filter */}
            {categories.length > 2 && (
                <div className="categories-filter">
                    {categories.map((cat) => (
                        <button
                            key={cat}
                            className={`category-btn ${selectedCategory === cat ? 'active' : ''}`}
                            onClick={() => setSelectedCategory(cat)}
                        >
                            {cat}
                        </button>
                    ))}
                </div>
            )}

            {/* Error State */}
            {error && (
                <div className="error-banner">
                    <span>âš ï¸</span>
                    <p>{error}</p>
                </div>
            )}

            {/* Main Content */}
            <main className="panel-main">
                {filteredBots.length === 0 ? (
                    <div className="empty-state">
                        <div className="empty-icon">ðŸ¤–</div>
                        <h3>No Bots Available</h3>
                        <p>
                            {searchTerm
                                ? 'No bots found matching your search'
                                : 'No bots available for your current internal policy scope'}
                        </p>
                    </div>
                ) : (
                    <div className="bots-grid">
                        {filteredBots.map((bot, index) => (
                            <Link
                                to={ROUTE_BY_ID[bot.id] || `/ai-bots/${bot.id}`}
                                key={bot.id || bot.botKey || `bot-${bot.name}-${index}`}
                                className="bot-card-link"
                            >
                                <div className="bot-card" style={{ '--bot-color': bot.color }}>
                                    <div className="bot-card-header">
                                        <div className="bot-icon" style={{ background: bot.color }}>
                                            {deriveIcon(bot.icon, bot.name)}
                                        </div>
                                        <div className="bot-info">
                                            <h3>{bot.name}</h3>
                                            <span className="category-badge">{bot.category}</span>
                                        </div>
                                    </div>

                                    <p className="bot-description">{bot.description}</p>

                                    <div className="bot-card-footer">
                                        <span className={`status-badge ${bot.status}`}>
                                            {bot.status === 'active' ? 'Active' : 'Inactive'}
                                        </span>
                                        {bot.tier_required && (
                                            <span className="tier-badge" title={`Requires: ${formatTierLabel(bot.tier_required)}`}>
                                                {formatTierLabel(bot.tier_required)}
                                            </span>
                                        )}
                                    </div>
                                </div>
                            </Link>
                        ))}
                    </div>
                )}

                {services.length > 0 && (
                    <section className="system-services">
                        <h2 className="services-title">System Services</h2>
                        <p className="services-subtitle">
                            These services run in the background based on your subscription.
                        </p>
                        <div className="services-grid">
                            {services.map((service, idx) => (
                                <div key={service.id || `service-${service.name}-${idx}`} className="service-card">
                                    <div className="service-icon" style={{ background: service.color }}>
                                        {deriveIcon(service.icon, service.name)}
                                    </div>
                                    <div className="service-info">
                                        <h3>{service.name}</h3>
                                        <p>{service.description}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </section>
                )}
            </main>

            {/* Upgrade / Admin Prompt */}
            {userInfo.isAdmin ? (
                <div className="upgrade-prompt">
                    <div className="upgrade-content">
                        <h3>Access Governance</h3>
                        <p>Manage bot access policies and role assignments through internal admin controls.</p>
                        <Link to="/admin" className="upgrade-btn">
                            Open Admin Controls
                        </Link>
                    </div>
                </div>
            ) : (
                userInfo.subscription !== 'enterprise' && (
                    <div className="upgrade-prompt">
                        <div className="upgrade-content">
                            <h3>Need More Access?</h3>
                            <p>
                                {REGISTRATION_DISABLED_FLAG
                                    ? `Platform runs in internal-only mode. Contact admin: ${REGISTRATION_CONTACT}`
                                    : 'Contact your administrator to request additional bot access.'}
                            </p>
                        </div>
                    </div>
                )
            )}
        </div>
    );
};

export default AIBotsPanelEnhanced;
