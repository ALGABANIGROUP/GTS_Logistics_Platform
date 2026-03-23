// frontend/src/pages/ai-bots/CarriersList.jsx

import React, { useState, useEffect } from 'react';
import { FaSearch, FaPlus, FaEdit, FaTrash, FaEye } from 'react-icons/fa';
import { listCarriers, deleteCarrier } from '../../services/carriersApi';

const CarriersList = () => {
    const [carriers, setCarriers] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchCarriers = async () => {
        try {
            setLoading(true);
            setError(null);
            const response = await listCarriers();
            setCarriers(response.items || []);
        } catch (err) {
            console.error('Error fetching carriers:', err);
            setError('Failed to load carriers. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchCarriers();
    }, []);

    const handleDeleteCarrier = async (carrierId) => {
        if (!window.confirm('Are you sure you want to delete this carrier?')) {
            return;
        }

        try {
            await deleteCarrier(carrierId);
            // Refresh the list after deletion
            await fetchCarriers();
        } catch (err) {
            console.error('Error deleting carrier:', err);
            alert('Failed to delete carrier. Please try again.');
        }
    };

    const filteredCarriers = carriers.filter(carrier =>
        carrier.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        carrier.contact_person?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        carrier.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        carrier.phone?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    if (loading) {
        return (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
                <div className="loading">Loading carriers...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', flexDirection: 'column' }}>
                <div style={{ color: '#ef4444', fontSize: '16px', marginBottom: '16px' }}>{error}</div>
                <button
                    onClick={fetchCarriers}
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
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                <div>
                    <h1 style={{ color: 'white', fontSize: '28px', marginBottom: '4px' }}>Carriers List</h1>
                    <p style={{ color: '#94a3b8' }}>Manage all your transportation partners</p>
                </div>
                <button style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    padding: '10px 20px',
                    background: '#10b981',
                    border: 'none',
                    borderRadius: '8px',
                    color: 'white',
                    cursor: 'pointer',
                    fontWeight: '500',
                    fontSize: '14px'
                }}>
                    <FaPlus /> Add Carrier
                </button>
            </div>

            {/* Search Bar */}
            <div style={{ marginBottom: '24px' }}>
                <div style={{ position: 'relative', maxWidth: '400px' }}>
                    <FaSearch style={{ position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)', color: '#64748b' }} />
                    <input
                        type="text"
                        placeholder="Search carriers by name, contact, or email..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        style={{
                            width: '100%',
                            padding: '12px 40px 12px 16px',
                            background: '#1e293b',
                            border: '1px solid #334155',
                            borderRadius: '8px',
                            color: 'white',
                            fontSize: '14px'
                        }}
                    />
                </div>
            </div>

            {/* Carriers Table */}
            <div style={{ background: '#1e293b', borderRadius: '16px', border: '1px solid #334155', overflow: 'hidden' }}>
                <div style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                        <thead>
                            <tr style={{ borderBottom: '1px solid #334155', background: '#0f172a' }}>
                                <th style={{ padding: '16px', textAlign: 'right', color: '#94a3b8', fontWeight: '500' }}>Carrier Name</th>
                                <th style={{ padding: '16px', textAlign: 'right', color: '#94a3b8', fontWeight: '500' }}>Contact Person</th>
                                <th style={{ padding: '16px', textAlign: 'right', color: '#94a3b8', fontWeight: '500' }}>Phone</th>
                                <th style={{ padding: '16px', textAlign: 'right', color: '#94a3b8', fontWeight: '500' }}>Email</th>
                                <th style={{ padding: '16px', textAlign: 'right', color: '#94a3b8', fontWeight: '500' }}>Rating</th>
                                <th style={{ padding: '16px', textAlign: 'right', color: '#94a3b8', fontWeight: '500' }}>Status</th>
                                <th style={{ padding: '16px', textAlign: 'right', color: '#94a3b8', fontWeight: '500' }}>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredCarriers.map(carrier => (
                                <tr key={carrier.id} style={{ borderBottom: '1px solid #334155' }}>
                                    <td style={{ padding: '16px', color: 'white', fontWeight: '500' }}>{carrier.name}</td>
                                    <td style={{ padding: '16px', color: '#cbd5e1' }}>{carrier.contact_person}</td>
                                    <td style={{ padding: '16px', color: '#94a3b8' }}>{carrier.phone}</td>
                                    <td style={{ padding: '16px', color: '#94a3b8' }}>{carrier.email}</td>
                                    <td style={{ padding: '16px', color: '#fbbf24' }}>
                                        {carrier.rating ? `${carrier.rating} ★` : 'N/A'}
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
                                        <div style={{ display: 'flex', gap: '8px' }}>
                                            <button style={{ padding: '6px', background: '#3b82f6', border: 'none', borderRadius: '6px', color: 'white', cursor: 'pointer' }}>
                                                <FaEye size={12} />
                                            </button>
                                            <button style={{ padding: '6px', background: '#f59e0b', border: 'none', borderRadius: '6px', color: 'white', cursor: 'pointer' }}>
                                                <FaEdit size={12} />
                                            </button>
                                            <button
                                                onClick={() => handleDeleteCarrier(carrier.id)}
                                                style={{ padding: '6px', background: '#ef4444', border: 'none', borderRadius: '6px', color: 'white', cursor: 'pointer' }}
                                            >
                                                <FaTrash size={12} />
                                            </button>
                                        </div>
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

export default CarriersList;