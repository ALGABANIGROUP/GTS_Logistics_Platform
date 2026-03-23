import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axiosClient from '../api/axiosClient';
import { REGISTRATION_DISABLED_FLAG, REGISTRATION_CONTACT } from '../config/registration';
import { formatTierLabel, normalizeTier, UNIFIED_TIERS } from '../utils/tierUtils';
import './BotFeatures.css';

/**
 * Bot Features Page
 * Displays all available bots grouped by subscription tier and system type
 * Shows which bots are available for current user's subscription
 */

const TIER_COLORS = {
    free: '#10B981',
    starter: '#06B6D4',
    growth: '#0EA5E9',
    professional: '#7C3AED',
    enterprise: '#4F46E5',
};

const TIER_ORDER = {
    free: 0,
    starter: 1,
    growth: 2,
    professional: 3,
    enterprise: 4,
};

const BotFeatures = () => {
    const { user } = useAuth();
    const [allBots, setAllBots] = useState({});
    const [userBots, setUserBots] = useState([]);
    const [userServices, setUserServices] = useState([]);
    const [loading, setLoading] = useState(true);
    const [userSubscription, setUserSubscription] = useState(null);
    const [selectedTier, setSelectedTier] = useState('all');
    const [selectedSystem, setSelectedSystem] = useState('all');

    useEffect(() => {
        fetchBotsData();
    }, []);

    const fetchBotsData = async () => {
        try {
            setLoading(true);
            let currentUserPayload = null;

            // Fetch current user's available bots
            try {
                const userResponse = await axiosClient.get('/api/v1/ai/bots/current-user/available', {
                    params: { language: 'en' },
                });
                currentUserPayload = userResponse?.data || null;

                if (userResponse.data) {
                    setUserBots(userResponse.data.bots || []);
                    setUserServices(userResponse.data.services || []);
                    setUserSubscription({
                        tier: normalizeTier(userResponse.data.subscription_tier),
                        role: userResponse.data.user_role,
                        system: userResponse.data.system_type,
                        count: userResponse.data.total_count,
                    });
                }
            } catch (err) {
                console.warn('Could not fetch user bots:', err);
                setUserSubscription({
                    tier: 'free',
                    role: 'shipper',
                    system: 'loadboard',
                    count: 0,
                });
                setUserServices([]);
            }

            // Fetch all bots for all tiers to show feature comparison
            // In internal-only mode we only render effective user access from backend.
            if (REGISTRATION_DISABLED_FLAG) {
                const tier = normalizeTier(currentUserPayload?.subscription_tier || 'free');
                const merged = [
                    ...(currentUserPayload?.bots || []),
                    ...(currentUserPayload?.services || []),
                ];
                const unique = merged.filter(
                    (bot, index, self) => self.findIndex((b) => b.id === bot.id) === index
                );
                setAllBots({ [tier]: unique });
                return;
            }

            const tierFetches = ['demo', 'basic', 'tms_pro', 'unified', 'enterprise'];
            const systemTypes = ['tms', 'loadboard'];
            const roles = ['shipper', 'carrier', 'broker'];

            const allBotsData = {
                free: [],
                starter: [],
                growth: [],
                professional: [],
                enterprise: [],
            };

            for (const tier of tierFetches) {
                for (const system of systemTypes) {
                    for (const role of roles) {
                        try {
                            const response = await axiosClient.get('/api/v1/ai/bots/available', {
                                params: {
                                    subscription_tier: tier,
                                    user_role: role,
                                    system_type: system,
                                    language: 'en',
                                },
                            });

                            if (response.data && response.data.bots) {
                                const unifiedTier = normalizeTier(tier);
                                allBotsData[unifiedTier] = [
                                    ...allBotsData[unifiedTier],
                                    ...response.data.bots.filter(
                                        (bot) => !allBotsData[unifiedTier].find((b) => b.id === bot.id)
                                    ),
                                ];
                            }
                        } catch (err) {
                            console.warn(`Failed to fetch bots for ${tier}/${system}/${role}`);
                        }
                    }
                }
            }

            setAllBots(allBotsData);
        } catch (err) {
            console.error('Error fetching bots data:', err);
        } finally {
            setLoading(false);
        }
    };

    const getUserTierLevel = () => {
        return userSubscription ? TIER_ORDER[userSubscription.tier] || 0 : 0;
    };

    const getTierLevel = (tier) => {
        return TIER_ORDER[tier] || 0;
    };

    const isAvailable = (botTier) => {
        return getUserTierLevel() >= getTierLevel(botTier);
    };

    const getFilteredBots = () => {
        let filtered = Object.entries(allBots).flatMap(([tier, bots]) =>
            bots.map((bot) => ({ ...bot, tier }))
        );

        if (selectedTier !== 'all') {
            filtered = filtered.filter((bot) => TIER_ORDER[bot.tier] <= getTierLevel(selectedTier));
        }

        return filtered.filter((bot, index, self) => self.findIndex((b) => b.id === bot.id) === index);
    };

    const getCategoryColor = (category) => {
        const colors = {
            Basic: '#06B6D4',
            Advanced: '#0EA5E9',
            Professional: '#7C3AED',
            Enterprise: '#4F46E5',
        };
        return colors[category] || '#64748B';
    };

    if (loading) {
        return (
            <div className="bot-features">
                <div className="loading-state">
                    <div className="spinner"></div>
                    <p>Loading bot features...</p>
                </div>
            </div>
        );
    }

    const filteredBots = getFilteredBots();

    return (
        <div className="bot-features">
            {/* Header */}
            <header className="features-header">
                <h1>🤖 AI Bots Features</h1>
                <p>Explore all available bots based on your subscription plan</p>

                {userSubscription && (
                    <div className="user-subscription-banner">
                        <div className="subscription-info">
                            <span className="label">Your Plan:</span>
                            <span className="tier" style={{ color: TIER_COLORS[userSubscription.tier] }}>
                                {formatTierLabel(userSubscription.tier)}
                            </span>
                            <span className="role">Role: {userSubscription.role}</span>
                            <span className="bots-count">Available Bots: {userSubscription.count}</span>
                        </div>
                    </div>
                )}
            </header>

            {/* Filters */}
            <div className="features-filters">
                <div className="filter-group">
                    <label>Filter by Tier:</label>
                    <select
                        value={selectedTier}
                        onChange={(e) => setSelectedTier(e.target.value)}
                        className="filter-select"
                    >
                        <option value="all">All Available</option>
                        <option value="starter">Starter & Above</option>
                        <option value="growth">Growth & Above</option>
                        <option value="professional">Professional & Above</option>
                        <option value="enterprise">Enterprise</option>
                    </select>
                </div>
            </div>

            {/* Bots Grid */}
            <div className="bots-grid">
                {filteredBots.length === 0 ? (
                    <div className="no-bots">
                        <p>No bots match your filter criteria</p>
                    </div>
                ) : (
                    filteredBots.map((bot) => {
                        const botInUser = userBots.find((ub) => ub.id === bot.id);
                        const available = isAvailable(bot.tier);

                        return (
                            <div
                                key={bot.id}
                                className={`bot-card ${available ? 'available' : 'locked'} ${botInUser ? 'active' : ''}`}
                            >
                                {/* Lock indicator */}
                                {!available && <div className="lock-badge">🔒 Locked</div>}
                                {botInUser && <div className="active-badge">✓ Active</div>}

                                {/* Icon & Name */}
                                <div className="bot-header">
                                    <div className="bot-icon" style={{ backgroundColor: bot.color }}>
                                        {bot.icon || '🤖'}
                                    </div>
                                    <h3>{bot.name}</h3>
                                </div>

                                {/* Category */}
                                <div
                                    className="bot-category"
                                    style={{ backgroundColor: getCategoryColor(bot.category) + '20' }}
                                >
                                    {bot.category}
                                </div>

                                {/* Description */}
                                <p className="bot-description">{bot.description}</p>

                                {/* Tier Info */}
                                <div className="bot-tier-info">
                                    <span className="required-tier">Requires: {formatTierLabel(bot.tier_required)}</span>
                                    {available ? (
                                        <span className="status-available">✓ Available</span>
                                    ) : (
                                        <span className="status-locked">
                                            {REGISTRATION_DISABLED_FLAG ? 'Access Managed Internally' : 'Upgrade Required'}
                                        </span>
                                    )}
                                </div>

                                {/* Action Button */}
                                <button
                                    className={`bot-action-btn ${available ? 'access' : 'upgrade'}`}
                                    disabled={!available}
                                >
                                    {available ? (
                                        <>
                                            {botInUser ? '✓ Access Now' : 'Start Using'}
                                        </>
                                    ) : (
                                        REGISTRATION_DISABLED_FLAG ? 'Contact Admin' : 'Upgrade Plan'
                                    )}
                                </button>
                            </div>
                        );
                    })
                )}
            </div>

            {REGISTRATION_DISABLED_FLAG && (
                <section className="features-services">
                    <p style={{ marginTop: 12 }}>
                        Internal-only mode is active. Access requests are handled by admin: {REGISTRATION_CONTACT}
                    </p>
                </section>
            )}

            {userServices.length > 0 && (
                <section className="features-services">
                    <h2>🧩 System Services</h2>
                    <p>These services run in the background based on your plan.</p>
                    <div className="services-grid">
                        {userServices.map((service) => (
                            <div key={service.id} className="service-card">
                                <div className="service-icon" style={{ backgroundColor: service.color }}>
                                    {service.icon || '⚙️'}
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

            {/* Feature Comparison */}
            {!REGISTRATION_DISABLED_FLAG && <section className="features-comparison">
                <h2>📊 Subscription Plans Comparison</h2>

                <div className="comparison-table">
                    <div className="comparison-header">
                        <div className="column-title">Feature</div>
                        <div className="column-tier">Free</div>
                        <div className="column-tier">Starter</div>
                        <div className="column-tier">Growth</div>
                        <div className="column-tier">Professional</div>
                        <div className="column-tier">Enterprise</div>
                    </div>

                    {['customer_service', 'documents_manager', 'ai_dispatcher', 'operations_manager_bot', 'safety_manager_bot', 'mapleload_bot', 'general_manager'].map(
                        (botId, idx) => (
                            <div key={idx} className="comparison-row">
                                <div className="feature-name">
                                    {botId
                                        .replace(/_/g, ' ')
                                        .replace(/\b\w/g, (char) => char.toUpperCase())}
                                </div>
                                {UNIFIED_TIERS.map((tier) => (
                                    <div
                                        key={tier}
                                        className="comparison-cell"
                                        style={{
                                            backgroundColor: allBots[tier]?.some((b) => b.id === botId)
                                                ? getCategoryColor(allBots[tier].find((b) => b.id === botId)?.category) + '20'
                                                : '#f1f5f9',
                                        }}
                                    >
                                        {allBots[tier]?.some((b) => b.id === botId) ? '✓' : '—'}
                                    </div>
                                ))}
                            </div>
                        )
                    )}
                </div>
            </section>}

            {/* Upgrade CTA */}
            {!REGISTRATION_DISABLED_FLAG && userSubscription && TIER_ORDER[userSubscription.tier] < 4 && (
                <section className="upgrade-cta">
                    <h2>Ready for More?</h2>
                    <p>
                        Upgrade to {userSubscription.tier === 'free' ? 'Starter' : 'the next'} plan to unlock
                        powerful AI features
                    </p>
                    <button className="upgrade-btn">View Plans</button>
                </section>
            )}

            {REGISTRATION_DISABLED_FLAG && (
                <section className="upgrade-cta">
                    <h2>Access Requests</h2>
                    <p>Internal-only mode is active. Request additional bot access via admin: {REGISTRATION_CONTACT}</p>
                </section>
            )}
        </div>
    );
};

export default BotFeatures;
