// frontend/src/pages/ai-bots/CarriersDashboard.jsx

import React, { useState, useEffect } from 'react';
import { FaTruck, FaStar, FaChartLine, FaFileContract } from 'react-icons/fa';
import { getCarrierStats, getRecentCarriers } from '../../services/carriersApi';

const CarriersDashboard = () => {
    const [stats, setStats] = useState({
        totalCarriers: 0,
        activeCarriers: 0,
        avgRating: 0,
        totalContracts: 0
    });
    const [recentCarriers, setRecentCarriers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchDashboardData = async () => {
        try {
            setLoading(true);
            setError(null);

            // Fetch stats and recent carriers in parallel
            const [statsResponse, recentResponse] = await Promise.all([
                getCarrierStats(),
                getRecentCarriers(5)
            ]);

            setStats({
                totalCarriers: statsResponse.total_carriers || 0,
                activeCarriers: statsResponse.active_carriers || 0,
                avgRating: statsResponse.avg_rating || 0,
                totalContracts: statsResponse.total_contracts || 0
            });

            setRecentCarriers(recentResponse.items || []);
        } catch (err) {
            console.error('Error fetching dashboard data:', err);
            setError('Failed to load dashboard data. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchDashboardData();
    }, []);

    if (loading) {
        return (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
                <div className="loading">Loading dashboard...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', flexDirection: 'column' }}>
                <div style={{ color: '#ef4444', fontSize: '16px', marginBottom: '16px' }}>{error}</div>
                <button
                    onClick={fetchDashboardData}
                    style={{
                        padding: '10px 20px',
                        background: '#3b82f6',
                        border: 'none',
                        borderRadius: '8px',
                        color: 'white',
                        cursor: 'pointer'
                    }}
                >
                    Try Again
                </button>
            </div>
        );
    }

    return (
        <div style={{ padding: '24px' }}>
            {/* Header */}
            <div style={{ marginBottom: '32px' }}>
                <h1 style={{ color: 'white', fontSize: '28px', marginBottom: '8px' }}>Carriers Dashboard</h1>
                <p style={{ color: '#94a3b8' }}>Manage your carrier network and partnerships</p>
            </div>

            {/* Stats Cards */}
            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(4, 1fr)',
                gap: '20px',
                marginBottom: '32px'
            }}>
                <div style={{ background: '#1e293b', borderRadius: '16px', padding: '20px', border: '1px solid #334155' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                        <FaTruck style={{ fontSize: '28px', color: '#10b981' }} />
                        <span style={{ fontSize: '28px', fontWeight: 'bold', color: 'white' }}>{stats.totalCarriers}</span>
                    </div>
                    <div style={{ color: '#94a3b8', fontSize: '14px' }}>Total Carriers</div>
                    <div style={{ fontSize: '12px', color: '#10b981', marginTop: '8px' }}>
                        +{stats.activeCarriers} active
                    </div>
                </div>

                <div style={{ background: '#1e293b', borderRadius: '16px', padding: '20px', border: '1px solid #334155' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                        <FaStar style={{ fontSize: '28px', color: '#fbbf24' }} />
                        <span style={{ fontSize: '28px', fontWeight: 'bold', color: 'white' }}>{stats.avgRating}</span>
                    </div>
                    <div style={{ color: '#94a3b8', fontSize: '14px' }}>Average Rating</div>
                    <div style={{ fontSize: '12px', color: '#10b981', marginTop: '8px' }}>
                        ★★★★★
                    </div>
                </div>

                <div style={{ background: '#1e293b', borderRadius: '16px', padding: '20px', border: '1px solid #334155' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                        <FaFileContract style={{ fontSize: '28px', color: '#3b82f6' }} />
                        <span style={{ fontSize: '28px', fontWeight: 'bold', color: 'white' }}>{stats.totalContracts}</span>
                    </div>
                    <div style={{ color: '#94a3b8', fontSize: '14px' }}>Active Contracts</div>
                    <div style={{ fontSize: '12px', color: '#10b981', marginTop: '8px' }}>
                        +5 this month
                    </div>
                </div>

                <div style={{ background: '#1e293b', borderRadius: '16px', padding: '20px', border: '1px solid #334155' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                        <FaChartLine style={{ fontSize: '28px', color: '#f97316' }} />
                        <span style={{ fontSize: '28px', fontWeight: 'bold', color: 'white' }}>+18%</span>
                    </div>
                    <div style={{ color: '#94a3b8', fontSize: '14px' }}>Growth Rate</div>
                    <div style={{ fontSize: '12px', color: '#10b981', marginTop: '8px' }}>
                        vs last quarter
                    </div>
                </div>
            </div>

            {/* Recent Carriers */}
            <div style={{ background: '#1e293b', borderRadius: '16px', border: '1px solid #334155', overflow: 'hidden' }}>
                <div style={{ padding: '20px', borderBottom: '1px solid #334155' }}>
                    <h3 style={{ color: 'white', margin: 0 }}>Recent Carriers</h3>
                </div>
                <div style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                        <thead>
                            <tr style={{ borderBottom: '1px solid #334155', color: '#94a3b8' }}>
                                <th style={{ padding: '16px', textAlign: 'right' }}>Carrier Name</th>
                                <th style={{ padding: '16px', textAlign: 'right' }}>Rating</th>
                                <th style={{ padding: '16px', textAlign: 'right' }}>Fleet Size</th>
                                <th style={{ padding: '16px', textAlign: 'right' }}>Status</th>
                                <th style={{ padding: '16px', textAlign: 'right' }}>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {recentCarriers.map(carrier => (
                                <tr key={carrier.id} style={{ borderBottom: '1px solid #334155' }}>
                                    <td style={{ padding: '16px', color: 'white' }}>{carrier.name}</td>
                                    <td style={{ padding: '16px', color: '#fbbf24' }}>
                                        {carrier.rating ? '★'.repeat(Math.floor(carrier.rating)) + '☆'.repeat(5 - Math.floor(carrier.rating)) + ` ${carrier.rating}` : 'N/A'}
                                    </td>
                                    <td style={{ padding: '16px', color: '#94a3b8' }}>
                                        {carrier.fleet_size ? `${carrier.fleet_size} trucks` : 'N/A'}
                                    </td>
                                    <td style={{ padding: '16px' }}>
                                        <span style={{
                                            padding: '4px 12px',
                                            borderRadius: '20px',
                                            fontSize: '12px',
                                            background: carrier.is_active ? '#10b98120' : '#ef444420',
                                            color: carrier.is_active ? '#10b981' : '#ef4444'
                                        }}>
                                            {carrier.is_active ? 'Active' : 'Inactive'}
                                        </span>
                                    </td>
                                    <td style={{ padding: '16px' }}>
                                        <button style={{
                                            padding: '6px 12px',
                                            background: '#3b82f6',
                                            border: 'none',
                                            borderRadius: '6px',
                                            color: 'white',
                                            cursor: 'pointer',
                                            fontSize: '12px'
                                        }}>
                                            View Details
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            <style>{`
        .loading {
          color: #94a3b8;
          font-size: 16px;
        }
        .loading::after {
          content: '';
          display: inline-block;
          width: 20px;
          height: 20px;
          border: 2px solid #3b82f6;
          border-top-color: transparent;
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin-right: 8px;
        }
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
        </div>
    );
};

export default CarriersDashboard;