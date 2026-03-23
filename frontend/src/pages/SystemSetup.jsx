import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import axiosClient from '../api/axiosClient';
import { getPlans, getPolicyContext } from '../services/billingApi';
import { formatTierLabel, normalizeTier } from '../utils/tierUtils';
import './SystemSetup.css';

/**
 * System Setup Page
 * User selects: System Type, Subscription Plan, and Role
 */
export default function SystemSetup() {
    const navigate = useNavigate();
    const { updateUser } = useAuth();
    const [step, setStep] = useState(1);
    const [selectedSystem, setSelectedSystem] = useState(null);
    const [selectedPlan, setSelectedPlan] = useState(null);
    const [selectedRole, setSelectedRole] = useState(null);
    const [loading, setLoading] = useState(false);
    const [loadingPlans, setLoadingPlans] = useState(true);
    const [error, setError] = useState('');
    const [plans, setPlans] = useState([]);
    const [planCurrency, setPlanCurrency] = useState('USD');

    const systems = [
        {
            id: 'tms',
            name: 'TMS System',
            title: 'Transportation Management System',
            description: 'Complete fleet management, dispatch, and operations control',
            icon: '🚛',
            features: ['Fleet Management', 'Dispatch Control', 'Route Optimization', 'Driver Management'],
        },
        {
            id: 'loadboard',
            name: 'LoadBoard',
            title: 'Load Board Platform',
            description: 'Connect shippers and carriers, find loads and trucks',
            icon: '📦',
            features: ['Load Posting', 'Carrier Search', 'Real-time Matching', 'Rate Management'],
        },
    ];

    useEffect(() => {
        let active = true;

        const loadPricing = async () => {
            setLoadingPlans(true);
            try {
                const context = await getPolicyContext();
                const region = context?.country || context?.region || 'GLOBAL';
                const response = await getPlans(region);
                if (!active) return;

                const normalized = (response?.plans || []).map((plan) => {
                    const unifiedTier = normalizeTier(plan?.code);
                    const code = unifiedTier.toUpperCase();
                    const loadboardEnabled = Boolean(plan?.entitlements?.['module.loadboard']);
                    const vehicles = plan?.limits?.vehicles;
                    const users = plan?.limits?.users;
                    const limits = [
                        vehicles === -1 ? 'Unlimited vehicles' : `${vehicles ?? 0} vehicles`,
                        users === -1 ? 'Unlimited users' : `${users ?? 0} users`,
                    ];

                    return {
                        id: unifiedTier,
                        code,
                        name: plan?.name || formatTierLabel(unifiedTier),
                        price: `${plan?.price_amount ?? 0} ${plan?.currency || 'USD'}/month`,
                        system: loadboardEnabled ? 'both' : 'tms',
                        bots: 0,
                        features: [
                            ...(plan?.highlights || []),
                            ...limits,
                        ],
                        color: code === 'FREE'
                            ? '#10B981'
                            : code === 'STARTER'
                                ? '#3B82F6'
                                : code === 'GROWTH'
                                    ? '#6366F1'
                                    : code === 'PROFESSIONAL'
                                        ? '#8B5CF6'
                                        : '#EF4444',
                    };
                });

                setPlans(normalized);
                setPlanCurrency(response?.plans?.[0]?.currency || 'USD');
            } catch {
                if (!active) return;
                setPlans([]);
            } finally {
                if (active) setLoadingPlans(false);
            }
        };

        loadPricing();
        return () => {
            active = false;
        };
    }, []);

    const roles = [
        {
            id: 'shipper',
            name: 'Shipper',
            description: 'Post and manage shipments, track deliveries',
            icon: '📤',
            systems: ['tms', 'loadboard'],
        },
        {
            id: 'carrier',
            name: 'Carrier',
            description: 'Manage fleet, find loads, optimize routes',
            icon: '🚚',
            systems: ['tms', 'loadboard'],
        },
        {
            id: 'broker',
            name: 'Broker',
            description: 'Connect shippers and carriers, manage operations',
            icon: '🤝',
            systems: ['tms', 'loadboard'],
        },
    ];

    const handleSystemSelect = (system) => {
        setSelectedSystem(system);
        setStep(2);
    };

    const handlePlanSelect = (plan) => {
        setSelectedPlan(plan);
        setStep(3);
    };

    const handleRoleSelect = (role) => {
        setSelectedRole(role);
    };

    const handleComplete = async () => {
        if (!selectedSystem || !selectedPlan || !selectedRole) {
            setError('Please complete all selections');
            return;
        }

        setLoading(true);
        setError('');

        try {
            const response = await axiosClient.post('/api/v1/user/setup', {
                system_type: selectedSystem.id,
                subscription_tier: selectedPlan.id,
                role: selectedRole.id,
            });

            if (response.data) {
                // Update user context
                if (updateUser) {
                    updateUser(response.data.user);
                }
                // Navigate to dashboard
                navigate('/dashboard');
            }
        } catch (err) {
            console.error('Setup error:', err);
            setError(err.response?.data?.detail || 'Failed to complete setup');
        } finally {
            setLoading(false);
        }
    };

    const filteredPlans = plans.filter(
        (plan) => plan.system === 'both' || plan.system === selectedSystem?.id
    );

    const filteredRoles = roles.filter((role) => role.systems.includes(selectedSystem?.id));

    return (
        <div className="system-setup">
            <div className="setup-container">
                {/* Header */}
                <header className="setup-header">
                    <h1>🚀 Setup Your Account</h1>
                    <p>Choose your system, plan, and role to get started</p>
                    <div className="step-indicator">
                        <div className={`step ${step >= 1 ? 'active' : ''}`}>1. System</div>
                        <div className={`step ${step >= 2 ? 'active' : ''}`}>2. Plan</div>
                        <div className={`step ${step >= 3 ? 'active' : ''}`}>3. Role</div>
                    </div>
                </header>

                {error && (
                    <div className="error-banner">
                        <span>⚠️</span>
                        <p>{error}</p>
                    </div>
                )}

                {/* Step 1: System Selection */}
                {step === 1 && (
                    <div className="selection-step">
                        <h2>Select Your System</h2>
                        <div className="cards-grid">
                            {systems.map((system) => (
                                <div
                                    key={system.id}
                                    className="selection-card"
                                    onClick={() => handleSystemSelect(system)}
                                >
                                    <div className="card-icon">{system.icon}</div>
                                    <h3>{system.title}</h3>
                                    <p className="card-description">{system.description}</p>
                                    <ul className="card-features">
                                        {system.features.map((feature, idx) => (
                                            <li key={idx}>✓ {feature}</li>
                                        ))}
                                    </ul>
                                    <button className="select-btn">Select {system.name}</button>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Step 2: Plan Selection */}
                {step === 2 && (
                    <div className="selection-step">
                        <button className="back-btn" onClick={() => setStep(1)}>
                            ← Back
                        </button>
                        <h2>Choose Your Subscription Plan</h2>
                        <p className="card-description" style={{ marginBottom: 16 }}>
                            Pricing is synced with the main billing catalog ({planCurrency}).
                        </p>
                        {loadingPlans ? (
                            <p className="card-description">Loading plans...</p>
                        ) : null}
                        {!loadingPlans && filteredPlans.length === 0 ? (
                            <p className="card-description">No plans available for this system.</p>
                        ) : null}
                        <div className="cards-grid">
                            {filteredPlans.map((plan) => (
                                <div
                                    key={plan.id}
                                    className={`selection-card plan-card ${selectedPlan?.id === plan.id ? 'selected' : ''
                                        }`}
                                    style={{ '--plan-color': plan.color }}
                                    onClick={() => handlePlanSelect(plan)}
                                >
                                    <div className="plan-header">
                                        <h3>{plan.name}</h3>
                                        <div className="plan-price">{plan.price}</div>
                                    </div>
                                    <div className="plan-bots">Bot bundles and extra services are available as add-ons.</div>
                                    <ul className="card-features">
                                        {plan.features.map((feature, idx) => (
                                            <li key={idx}>✓ {feature}</li>
                                        ))}
                                    </ul>
                                    <button className="select-btn">Select Plan</button>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Step 3: Role Selection */}
                {step === 3 && (
                    <div className="selection-step">
                        <button className="back-btn" onClick={() => setStep(2)}>
                            ← Back
                        </button>
                        <h2>Select Your Role</h2>
                        <div className="cards-grid">
                            {filteredRoles.map((role) => (
                                <div
                                    key={role.id}
                                    className={`selection-card role-card ${selectedRole?.id === role.id ? 'selected' : ''
                                        }`}
                                    onClick={() => handleRoleSelect(role)}
                                >
                                    <div className="card-icon">{role.icon}</div>
                                    <h3>{role.name}</h3>
                                    <p className="card-description">{role.description}</p>
                                    <button className="select-btn">Select Role</button>
                                </div>
                            ))}
                        </div>

                        {selectedRole && (
                            <div className="complete-section">
                                <div className="selection-summary">
                                    <h3>Your Selection:</h3>
                                    <div className="summary-items">
                                        <div className="summary-item">
                                            <span className="label">System:</span>
                                            <span className="value">{selectedSystem.name}</span>
                                        </div>
                                        <div className="summary-item">
                                            <span className="label">Plan:</span>
                                            <span className="value">{selectedPlan.name}</span>
                                        </div>
                                        <div className="summary-item">
                                            <span className="label">Role:</span>
                                            <span className="value">{selectedRole.name}</span>
                                        </div>
                                    </div>
                                </div>
                                <button
                                    className="complete-btn"
                                    onClick={handleComplete}
                                    disabled={loading}
                                >
                                    {loading ? 'Setting up...' : 'Complete Setup 🚀'}
                                </button>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
