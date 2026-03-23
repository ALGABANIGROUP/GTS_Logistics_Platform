import React, { useEffect, useMemo, useState } from 'react';
import { getPlans, getPolicyContext } from '../../services/billingApi';
import { formatTierLabel, normalizeTier } from '../../utils/tierUtils';
import './PlanSelector.css';

/**
 * Plan Selector Component - Choose TMS Subscription Plan
 * Uses the same billing catalog as the pricing page
 */
export default function PlanSelector({ onPlanSelected, currentPlan = null }) {
    const [selectedPlan, setSelectedPlan] = useState(currentPlan || 'professional');
    const [billingCycle, setBillingCycle] = useState('monthly');
    const [plans, setPlans] = useState([]);
    const [loadingPlans, setLoadingPlans] = useState(true);

    useEffect(() => {
        let active = true;

        const loadPlans = async () => {
            setLoadingPlans(true);
            try {
                const context = await getPolicyContext();
                const region = context?.country || context?.region || 'GLOBAL';
                const response = await getPlans(region);
                if (!active) return;

                const normalized = (response?.plans || []).map((plan) => {
                    const tier = normalizeTier(plan?.code);
                    return {
                        id: tier,
                        name: plan?.name || formatTierLabel(tier),
                        icon: tier === 'free' ? '🟢' : tier === 'starter' ? '🚀' : tier === 'growth' ? '📈' : tier === 'professional' ? '⭐' : '👑',
                        description: plan?.description || '',
                        priceMonthly: Number(plan?.price_amount || 0),
                        priceAnnual: Number(plan?.price_amount || 0) * 12,
                        maxUsers: plan?.limits?.users ?? 0,
                        maxDrivers: plan?.limits?.vehicles ?? 0,
                        maxShipments: -1,
                        bots: [],
                        features: plan?.highlights || [],
                        popular: tier === 'growth',
                    };
                });

                setPlans(normalized);
                if (normalized.length && !normalized.some((p) => p.id === selectedPlan)) {
                    setSelectedPlan(normalized[0].id);
                }
            } catch {
                if (!active) return;
                setPlans([]);
            } finally {
                if (active) setLoadingPlans(false);
            }
        };

        loadPlans();
        return () => {
            active = false;
        };
    }, []);

    const permissionLevels = {
        'view_only': { label: 'View Only', icon: '👁️', color: '#6c757d' },
        'quick_run': { label: 'Quick Run', icon: '⚡', color: '#17a2b8' },
        'control_panel': { label: 'Full Control', icon: '🎮', color: '#28a745' },
        'configure': { label: 'Configure', icon: '⚙️', color: '#ffc107' }
    };

    const handleSelectPlan = (planId) => {
        setSelectedPlan(planId);
        const plan = plans.find((p) => p.id === planId);
        if (!plan) return;
        if (onPlanSelected) {
            onPlanSelected({
                plan_id: planId,
                billing_cycle: billingCycle,
                price: billingCycle === 'monthly' ? plan.priceMonthly : plan.priceAnnual
            });
        }
    };

    const formatPrice = (plan) => {
        const price = billingCycle === 'monthly' ? plan.priceMonthly : plan.priceAnnual;
        const perMonth = billingCycle === 'annual' ? ` ($${Math.round(price / 12)}/mo)` : '';
        return `$${price}/${billingCycle === 'monthly' ? 'month' : 'year'}${perMonth}`;
    };

    const formatLimit = (value) => {
        return value === -1 ? 'Unlimited' : value;
    };

    const showPermissionGuide = useMemo(() => plans.some((plan) => (plan.bots || []).length > 0), [plans]);

    return (
        <div className="plan-selector-container">
            <div className="plan-selector-header">
                <h1>Choose Your TMS Plan</h1>
                <p className="subtitle">Plans are synced with the main billing catalog.</p>

                <div className="billing-toggle">
                    <button
                        className={billingCycle === 'monthly' ? 'active' : ''}
                        onClick={() => setBillingCycle('monthly')}
                    >
                        Monthly
                    </button>
                    <button
                        className={billingCycle === 'annual' ? 'active' : ''}
                        onClick={() => setBillingCycle('annual')}
                    >
                        Annual <span className="save-badge">x12 billing</span>
                    </button>
                </div>
            </div>

            <div className="plans-grid">
                {loadingPlans ? <p>Loading plans...</p> : null}
                {!loadingPlans && plans.length === 0 ? <p>No plans available right now.</p> : null}
                {plans.map(plan => (
                    <div
                        key={plan.id}
                        className={`plan-card ${plan.popular ? 'popular' : ''} ${selectedPlan === plan.id ? 'selected' : ''}`}
                        onClick={() => handleSelectPlan(plan.id)}
                    >
                        {plan.popular && (
                            <div className="popular-badge">Most Popular</div>
                        )}

                        <div className="plan-header">
                            <div className="plan-icon">{plan.icon}</div>
                            <h2 className="plan-name">{plan.name}</h2>
                            <p className="plan-description">{plan.description}</p>
                        </div>

                        <div className="plan-pricing">
                            <div className="price">{formatPrice(plan)}</div>
                        </div>

                        <div className="plan-limits">
                            <div className="limit-item">
                                <span className="limit-icon">👥</span>
                                <span>{formatLimit(plan.maxUsers)} Users</span>
                            </div>
                            <div className="limit-item">
                                <span className="limit-icon">🚗</span>
                                <span>{formatLimit(plan.maxDrivers)} Drivers</span>
                            </div>
                            <div className="limit-item">
                                <span className="limit-icon">📦</span>
                                <span>{formatLimit(plan.maxShipments)} Shipments/mo</span>
                            </div>
                        </div>

                        <div className="plan-bots">
                            <h4>AI Bots Included:</h4>
                            {(plan.bots || []).length > 0 ? (
                                <ul className="bots-list">
                                    {plan.bots.map(bot => (
                                        <li key={bot.key} className="bot-item">
                                            <span className="bot-icon">{bot.icon}</span>
                                            <span className="bot-name">{bot.name}</span>
                                            <span
                                                className="permission-badge"
                                                style={{ background: permissionLevels[bot.level].color }}
                                            >
                                                {permissionLevels[bot.level].icon} {permissionLevels[bot.level].label}
                                            </span>
                                        </li>
                                    ))}
                                </ul>
                            ) : (
                                <p className="card-description">Bot bundles are available as add-ons from Billing.</p>
                            )}
                        </div>

                        <div className="plan-features">
                            <h4>Features:</h4>
                            <ul>
                                {plan.features.map((feature, index) => (
                                    <li key={index}>
                                        <span className="check-icon">✓</span>
                                        {feature}
                                    </li>
                                ))}
                            </ul>
                        </div>

                        <button className={`select-button ${selectedPlan === plan.id ? 'selected' : ''}`}>
                            {selectedPlan === plan.id ? '✓ Selected' : 'Select Plan'}
                        </button>
                    </div>
                ))}
            </div>

            {showPermissionGuide ? (
                <div className="permissions-guide">
                    <h3>Understanding Bot Permission Levels</h3>
                    <div className="permissions-grid">
                        {Object.entries(permissionLevels).map(([key, level]) => (
                            <div key={key} className="permission-card">
                                <div className="permission-icon" style={{ color: level.color }}>
                                    {level.icon}
                                </div>
                                <h4>{level.label}</h4>
                                <p>{getPermissionDescription(key)}</p>
                            </div>
                        ))}
                    </div>
                </div>
            ) : null}

            <div className="faq-section">
                <h3>Frequently Asked Questions</h3>
                <div className="faq-grid">
                    <div className="faq-item">
                        <h4>Can I upgrade later?</h4>
                        <p>Yes. You can change your subscription tier later from billing settings.</p>
                    </div>
                    <div className="faq-item">
                        <h4>What happens if I exceed my limits?</h4>
                        <p>You can add extra vehicles or users from the add-ons catalog, or upgrade your tier.</p>
                    </div>
                    <div className="faq-item">
                        <h4>Are bots included in all plans?</h4>
                        <p>Core plan features are included by tier. Bot packages are available as separate add-ons.</p>
                    </div>
                    <div className="faq-item">
                        <h4>Is there a free tier?</h4>
                        <p>Yes. The Free plan is available in the unified pricing model with limited usage caps.</p>
                    </div>
                </div>
            </div>
        </div>
    );
}

function getPermissionDescription(level) {
    const descriptions = {
        'view_only': 'View dashboards and reports only. No execution capabilities.',
        'quick_run': 'Execute pre-defined templates and quick actions. Perfect for routine tasks.',
        'control_panel': 'Full control of bot operations, custom workflows, and manual execution.',
        'configure': 'Complete access including API integrations, webhooks, and automation rules.'
    };
    return descriptions[level] || '';
}
