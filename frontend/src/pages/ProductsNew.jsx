import React, { useState, useEffect } from 'react';
import './ProductsPage.css';

const driftAt = (wave, tick) => wave[tick % wave.length];

const Products = () => {
    const [flatbed, setFlatbed] = useState(12653);
    const [van, setVan] = useState(9027);
    const [reefer, setReefer] = useState(5730);
    const [heavyHaul, setHeavyHaul] = useState(3565);
    const [movedToday, setMovedToday] = useState(2402);
    const [tick, setTick] = useState(0);

    useEffect(() => {
        // Update data every 8 seconds using deterministic drift
        const interval = setInterval(() => {
            setTick(prevTick => {
                const nextTick = prevTick + 1;
                setFlatbed(prev => Math.max(8800, prev + driftAt([31, -20, 14, -8, 23, -11, 6], nextTick)));
                setVan(prev => Math.max(6200, prev + driftAt([28, -16, 19, -7, 12, -10, 9], nextTick)));
                setReefer(prev => Math.max(3400, prev + driftAt([17, -9, 12, -6, 15, -7, 5], nextTick)));
                setHeavyHaul(prev => Math.max(2100, prev + driftAt([11, -5, 8, -4, 9, -3, 6], nextTick)));
                setMovedToday(prev => prev + driftAt([19, 14, 21, 16, 24, 13, 18], nextTick));
                return nextTick;
            });
        }, 8000);

        return () => clearInterval(interval);
    }, []);

    const formatNumber = (num) => {
        return num.toLocaleString('en-US');
    };

    const handleStartTrial = () => {
        // Navigate to signup/registration
        window.location.href = '/signup';
    };

    const handleContactSales = () => {
        // Navigate to contact sales
        window.location.href = '/contact';
    };

    return (
        <div className="products-page">
            {/* Hero Section */}
            <div className="products-hero">
                <div className="hero-content">
                    <h1>GTS Logistics Platform</h1>
                    <p>Complete transportation management solution for modern logistics</p>
                    <div className="hero-buttons">
                        <button className="btn-primary-large" onClick={handleStartTrial}>
                            Start Free Trial
                        </button>
                        <button className="btn-secondary-large" onClick={handleContactSales}>
                            Contact Sales
                        </button>
                    </div>
                </div>
            </div>

            {/* FreightPulse Live Dashboard */}
            <div className="freight-dashboard-section">
                <div className="container">
                    <div className="dashboard-header">
                        <h2>
                            FreightPulse <span className="live-badge">LIVE BOARD</span>
                        </h2>
                        <p>Real-time freight marketplace · Load availability & integrations</p>
                    </div>

                    {/* Stats Grid */}
                    <div className="stats-grid">
                        <div className="stat-card">
                            <div className="stat-title">
                                <i className="fas fa-truck-ramp-box"></i> FLATBED LOADS
                            </div>
                            <div className="stat-number">{formatNumber(flatbed)}</div>
                            <div className="stat-sub">available nationally</div>
                        </div>

                        <div className="stat-card">
                            <div className="stat-title">
                                <i className="fas fa-boxes"></i> VAN LOADS
                            </div>
                            <div className="stat-number">{formatNumber(van)}</div>
                            <div className="stat-sub">dry van / box truck</div>
                        </div>

                        <div className="stat-card">
                            <div className="stat-title">
                                <i className="fas fa-temperature-low"></i> REEFER LOADS
                            </div>
                            <div className="stat-number">{formatNumber(reefer)}</div>
                            <div className="stat-sub">temp-controlled</div>
                        </div>

                        <div className="stat-card">
                            <div className="stat-title">
                                <i className="fas fa-truck-moving"></i> HEAVY HAUL LOADS
                            </div>
                            <div className="stat-number">{formatNumber(heavyHaul)}</div>
                            <div className="stat-sub">oversize / specialized</div>
                        </div>

                        <div className="stat-card highlight-card">
                            <div className="stat-title">
                                <i className="fas fa-check-double"></i> LOADS MOVED TODAY
                            </div>
                            <div className="stat-number">{formatNumber(movedToday)}</div>
                            <div className="stat-sub">updated in real-time</div>
                        </div>
                    </div>

                    {/* Integration Partners */}
                    <div className="integration-section">
                        <h3 className="integration-title">
                            <i className="fas fa-handshake"></i> Integration Partners
                        </h3>
                        <div className="integration-grid">
                            <div className="integration-card">
                                <i className="fab fa-quickbooks"></i>
                                <h4>QuickBooks</h4>
                                <span className="integration-badge connected">Connected</span>
                            </div>

                            <div className="integration-card">
                                <i className="fab fa-salesforce"></i>
                                <h4>Salesforce</h4>
                                <span className="integration-badge connected">CRM Sync</span>
                            </div>

                            <div className="integration-card">
                                <i className="fab fa-google"></i>
                                <h4>Google Maps</h4>
                                <span className="integration-badge connected">Geolocation</span>
                            </div>

                            <div className="integration-card pending-activation">
                                <i className="fas fa-credit-card"></i>
                                <h4>SUDAPAY</h4>
                                <span className="integration-badge">Activation Pending</span>
                            </div>

                            <div className="integration-card">
                                <i className="fas fa-shield-alt"></i>
                                <h4>FMCSA</h4>
                                <span className="integration-badge connected">Safety & Compliance</span>
                            </div>

                            <div className="integration-card not-integrated">
                                <i className="fab fa-stripe"></i>
                                <h4>Stripe</h4>
                                <span className="integration-badge">Not integrated</span>
                            </div>
                        </div>
                    </div>

                    <div className="dashboard-footer">
                        <i className="fas fa-charging-station"></i> Data refreshes automatically every 8 seconds
                    </div>
                </div>
            </div>

            {/* Product Features Section */}
            <div className="products-features">
                <div className="container">
                    <h2>Platform Features</h2>
                    <div className="features-grid">
                        <div className="feature-card">
                            <i className="fas fa-chart-line"></i>
                            <h3>Real-time Analytics</h3>
                            <p>Track your fleet performance with live dashboards and custom reports</p>
                        </div>
                        <div className="feature-card">
                            <i className="fas fa-route"></i>
                            <h3>Route Optimization</h3>
                            <p>AI-powered routing to reduce fuel costs and delivery times</p>
                        </div>
                        <div className="feature-card">
                            <i className="fas fa-file-invoice-dollar"></i>
                            <h3>Automated Billing</h3>
                            <p>Streamline invoicing and payment collection with integrated systems</p>
                        </div>
                        <div className="feature-card">
                            <i className="fas fa-shield-alt"></i>
                            <h3>Compliance Management</h3>
                            <p>Stay compliant with FMCSA regulations and automated documentation</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Products;