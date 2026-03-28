import React, { useEffect, useRef, useState } from 'react';

const FreightPulseDashboard = () => {
    const [flatbed, setFlatbed] = useState(12450);
    const [van, setVan] = useState(8932);
    const [reefer, setReefer] = useState(5678);
    const [heavyHaul, setHeavyHaul] = useState(3421);
    const [movedToday, setMovedToday] = useState(2156);
    const tickRef = useRef(0);

    const formatNumber = (num) => num.toLocaleString('en-US');

    const updateUI = () => {
        // State is already updated
    };

    const nextDrift = (wave, fallback = 0) => {
        const idx = tickRef.current % wave.length;
        return wave[idx] ?? fallback;
    };

    const refreshLoadData = () => {
        setFlatbed(prev => Math.max(8800, prev + nextDrift([31, -20, 14, -8, 23, -11, 6])));
        setVan(prev => Math.max(6200, prev + nextDrift([28, -16, 19, -7, 12, -10, 9])));
        setReefer(prev => Math.max(3400, prev + nextDrift([17, -9, 12, -6, 15, -7, 5])));
        setHeavyHaul(prev => Math.max(2100, prev + nextDrift([11, -5, 8, -4, 9, -3, 6])));
        setMovedToday(prev => prev + nextDrift([19, 14, 21, 16, 24, 13, 18], 16));
    };

    const enhancedRefresh = () => {
        tickRef.current += 1;
        refreshLoadData();
        if (tickRef.current % 5 === 0) {
            setMovedToday(prev => prev + nextDrift([25, 38, 31, 44], 30));
            const liftTarget = tickRef.current % 4;
            if (liftTarget === 0) setFlatbed(prev => Math.floor(prev * 1.008) + 12);
            if (liftTarget === 1) setVan(prev => Math.floor(prev * 1.006) + 18);
            if (liftTarget === 2) setReefer(prev => Math.floor(prev * 1.009) + 9);
            if (liftTarget === 3) setHeavyHaul(prev => Math.floor(prev * 1.007) + 7);
        }
    };

    useEffect(() => {
        const intervalId = setInterval(enhancedRefresh, 8000);
        return () => clearInterval(intervalId);
    }, []);

    return (
        <div className="dashboard-container" style={{ maxWidth: '1400px', margin: '0 auto', fontFamily: "'Inter', sans-serif", background: '#f4f7fc', color: '#1a2c3e', padding: '2rem 1.5rem' }}>
            <div className="header" style={{ marginBottom: '2rem' }}>
                <h1 style={{ fontSize: '1.9rem', fontWeight: 700, background: 'linear-gradient(135deg, #0b2b3b, #1b4f6e)', WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent', letterSpacing: '-0.3px' }}>
                    FreightPulse <span style={{ fontSize: '1rem', background: '#eef2f8', padding: '4px 12px', borderRadius: '40px', fontWeight: 500, color: '#2c7da0' }}>LIVE BOARD</span>
                </h1>
                <p style={{ color: '#4a627a', fontWeight: 500, marginTop: '0.3rem', fontSize: '0.9rem' }}>Real-time freight marketplace · Load availability & integrations</p>
            </div>

            <div className="stats-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.3rem', marginBottom: '2.5rem' }}>
                <div className="stat-card" style={{ background: 'white', borderRadius: '28px', padding: '1.4rem 1.2rem', boxShadow: '0 8px 20px rgba(0, 0, 0, 0.02), 0 2px 6px rgba(0, 0, 0, 0.05)', transition: 'transform 0.2s ease, box-shadow 0.2s ease', border: '1px solid rgba(0, 0, 0, 0.03)' }}>
                    <div className="stat-title" style={{ fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: 600, color: '#5b7a9a', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <i className="fas fa-truck-ramp-box" style={{ fontSize: '1.1rem', width: '24px', color: '#2c7da0' }}></i> Flatbed loads
                    </div>
                    <div className="stat-number" style={{ fontSize: '2.5rem', fontWeight: 800, color: '#0a2f44', lineHeight: 1.2, letterSpacing: '-0.5px' }}>{formatNumber(flatbed)}</div>
                    <div className="stat-sub" style={{ fontSize: '0.75rem', color: '#6b8aae', marginTop: '0.4rem', fontWeight: 500 }}>available nationally</div>
                </div>

                <div className="stat-card" style={{ background: 'white', borderRadius: '28px', padding: '1.4rem 1.2rem', boxShadow: '0 8px 20px rgba(0, 0, 0, 0.02), 0 2px 6px rgba(0, 0, 0, 0.05)', transition: 'transform 0.2s ease, box-shadow 0.2s ease', border: '1px solid rgba(0, 0, 0, 0.03)' }}>
                    <div className="stat-title" style={{ fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: 600, color: '#5b7a9a', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <i className="fas fa-boxes" style={{ fontSize: '1.1rem', width: '24px', color: '#2c7da0' }}></i> Van loads
                    </div>
                    <div className="stat-number" style={{ fontSize: '2.5rem', fontWeight: 800, color: '#0a2f44', lineHeight: 1.2, letterSpacing: '-0.5px' }}>{formatNumber(van)}</div>
                    <div className="stat-sub" style={{ fontSize: '0.75rem', color: '#6b8aae', marginTop: '0.4rem', fontWeight: 500 }}>dry van / box truck</div>
                </div>

                <div className="stat-card" style={{ background: 'white', borderRadius: '28px', padding: '1.4rem 1.2rem', boxShadow: '0 8px 20px rgba(0, 0, 0, 0.02), 0 2px 6px rgba(0, 0, 0, 0.05)', transition: 'transform 0.2s ease, box-shadow 0.2s ease', border: '1px solid rgba(0, 0, 0, 0.03)' }}>
                    <div className="stat-title" style={{ fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: 600, color: '#5b7a9a', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <i className="fas fa-temperature-low" style={{ fontSize: '1.1rem', width: '24px', color: '#2c7da0' }}></i> Reefer loads
                    </div>
                    <div className="stat-number" style={{ fontSize: '2.5rem', fontWeight: 800, color: '#0a2f44', lineHeight: 1.2, letterSpacing: '-0.5px' }}>{formatNumber(reefer)}</div>
                    <div className="stat-sub" style={{ fontSize: '0.75rem', color: '#6b8aae', marginTop: '0.4rem', fontWeight: 500 }}>temp-controlled</div>
                </div>

                <div className="stat-card" style={{ background: 'white', borderRadius: '28px', padding: '1.4rem 1.2rem', boxShadow: '0 8px 20px rgba(0, 0, 0, 0.02), 0 2px 6px rgba(0, 0, 0, 0.05)', transition: 'transform 0.2s ease, box-shadow 0.2s ease', border: '1px solid rgba(0, 0, 0, 0.03)' }}>
                    <div className="stat-title" style={{ fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: 600, color: '#5b7a9a', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <i className="fas fa-truck-moving" style={{ fontSize: '1.1rem', width: '24px', color: '#2c7da0' }}></i> Heavy Haul loads
                    </div>
                    <div className="stat-number" style={{ fontSize: '2.5rem', fontWeight: 800, color: '#0a2f44', lineHeight: 1.2, letterSpacing: '-0.5px' }}>{formatNumber(heavyHaul)}</div>
                    <div className="stat-sub" style={{ fontSize: '0.75rem', color: '#6b8aae', marginTop: '0.4rem', fontWeight: 500 }}>oversize / specialized</div>
                </div>

                <div className="stat-card highlight-card" style={{ background: 'linear-gradient(125deg, #1f5e7e, #0d3f58)', color: 'white', borderRadius: '28px', padding: '1.4rem 1.2rem', boxShadow: '0 8px 20px rgba(0, 0, 0, 0.02), 0 2px 6px rgba(0, 0, 0, 0.05)', transition: 'transform 0.2s ease, box-shadow 0.2s ease', border: '1px solid rgba(0, 0, 0, 0.03)' }}>
                    <div className="stat-title" style={{ fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: 600, color: '#c9e9ff', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <i className="fas fa-check-double" style={{ fontSize: '1.1rem', width: '24px', color: '#c9e9ff' }}></i> Loads moved today
                    </div>
                    <div className="stat-number" style={{ fontSize: '2.5rem', fontWeight: 800, color: 'white', lineHeight: 1.2, letterSpacing: '-0.5px' }}>{formatNumber(movedToday)}</div>
                    <div className="stat-sub" style={{ fontSize: '0.75rem', color: '#c9e9ff', marginTop: '0.4rem', fontWeight: 500 }}>updated in real-time <i className="fas fa-sync-alt fa-fw" style={{ fontSize: '10px' }}></i></div>
                </div>
            </div>

            <div className="section-title" style={{ fontSize: '1.5rem', fontWeight: 600, margin: '2rem 0 1.2rem 0', display: 'flex', alignItems: 'center', gap: '12px', borderLeft: '5px solid #2c7da0', paddingLeft: '1rem' }}>
                <i className="fas fa-handshake"></i> Integration Partners
            </div>
            <div className="integration-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1.3rem', marginBottom: '2rem' }}>
                <div className="integration-card" style={{ background: 'white', borderRadius: '24px', padding: '1.2rem 0.8rem', textAlign: 'center', transition: 'all 0.2s', boxShadow: '0 2px 8px rgba(0, 0, 0, 0.03)', border: '1px solid #eef2f8' }}>
                    <i className="fab fa-quickbooks" style={{ fontSize: '2.6rem', marginBottom: '0.6rem', color: '#1f5e7e' }}></i>
                    <h3 style={{ fontSize: '1.2rem', fontWeight: 600, margin: '0.5rem 0 0.2rem' }}>QuickBooks</h3>
                    <div className="integration-badge" style={{ fontSize: '0.7rem', background: '#eef3fc', display: 'inline-block', padding: '0.2rem 0.8rem', borderRadius: '30px', color: '#1f5e7e', fontWeight: 500, marginTop: '6px' }}><i className="fas fa-link"></i> Connected</div>
                </div>

                <div className="integration-card" style={{ background: 'white', borderRadius: '24px', padding: '1.2rem 0.8rem', textAlign: 'center', transition: 'all 0.2s', boxShadow: '0 2px 8px rgba(0, 0, 0, 0.03)', border: '1px solid #eef2f8' }}>
                    <i className="fab fa-salesforce" style={{ fontSize: '2.6rem', marginBottom: '0.6rem', color: '#1f5e7e' }}></i>
                    <h3 style={{ fontSize: '1.2rem', fontWeight: 600, margin: '0.5rem 0 0.2rem' }}>Salesforce</h3>
                    <div className="integration-badge" style={{ fontSize: '0.7rem', background: '#eef3fc', display: 'inline-block', padding: '0.2rem 0.8rem', borderRadius: '30px', color: '#1f5e7e', fontWeight: 500, marginTop: '6px' }}><i className="fas fa-chart-line"></i> CRM Sync</div>
                </div>

                <div className="integration-card" style={{ background: 'white', borderRadius: '24px', padding: '1.2rem 0.8rem', textAlign: 'center', transition: 'all 0.2s', boxShadow: '0 2px 8px rgba(0, 0, 0, 0.03)', border: '1px solid #eef2f8' }}>
                    <i className="fab fa-google" style={{ fontSize: '2.6rem', marginBottom: '0.6rem', color: '#1f5e7e' }}></i>
                    <h3 style={{ fontSize: '1.2rem', fontWeight: 600, margin: '0.5rem 0 0.2rem' }}>Google Maps</h3>
                    <div className="integration-badge" style={{ fontSize: '0.7rem', background: '#eef3fc', display: 'inline-block', padding: '0.2rem 0.8rem', borderRadius: '30px', color: '#1f5e7e', fontWeight: 500, marginTop: '6px' }}><i className="fas fa-map-marker-alt"></i> Geolocation</div>
                </div>

                <div className="integration-card" style={{ background: 'white', borderRadius: '24px', padding: '1.2rem 0.8rem', textAlign: 'center', transition: 'all 0.2s', boxShadow: '0 2px 8px rgba(0, 0, 0, 0.03)', border: '1px solid #eef2f8' }}>
                    <i className="fab fa-stripe" style={{ fontSize: '2.6rem', marginBottom: '0.6rem', color: '#635bff' }}></i>
                    <h3 style={{ fontSize: '1.2rem', fontWeight: 600, margin: '0.5rem 0 0.2rem' }}>Stripe</h3>
                    <div className="integration-badge" style={{ fontSize: '0.7rem', background: '#eef3fc', display: 'inline-block', padding: '0.2rem 0.8rem', borderRadius: '30px', color: '#1f5e7e', fontWeight: 500, marginTop: '6px' }}><i className="fas fa-check-circle"></i> Primary Gateway</div>
                </div>

                <div className="integration-card" style={{ background: 'white', borderRadius: '24px', padding: '1.2rem 0.8rem', textAlign: 'center', transition: 'all 0.2s', boxShadow: '0 2px 8px rgba(0, 0, 0, 0.03)', border: '1px solid #eef2f8' }}>
                    <i className="fas fa-shield-alt" style={{ fontSize: '2.6rem', marginBottom: '0.6rem', color: '#1f5e7e' }}></i>
                    <h3 style={{ fontSize: '1.2rem', fontWeight: 600, margin: '0.5rem 0 0.2rem' }}>FMCSA</h3>
                    <div className="integration-badge" style={{ fontSize: '0.7rem', background: '#eef3fc', display: 'inline-block', padding: '0.2rem 0.8rem', borderRadius: '30px', color: '#1f5e7e', fontWeight: 500, marginTop: '6px' }}><i className="fas fa-id-card"></i> Safety & Compliance</div>
                </div>

            </div>
            <div className="footer-note" style={{ fontSize: '0.75rem', textAlign: 'center', marginTop: '3rem', color: '#6c8db0', borderTop: '1px solid #dce5ef', paddingTop: '1.5rem' }}>
                <i className="fas fa-charging-station"></i> Data refreshes automatically every 8 seconds • Simulated live freight market fluctuations
            </div>
        </div>
    );
};

export default FreightPulseDashboard;
