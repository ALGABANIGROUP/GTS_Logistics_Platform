// frontend/src/pages/ai-bots/ShippersWorkspaceLayout.jsx

import React from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { FaTachometerAlt, FaUsers, FaBox, FaFileInvoice, FaSignOutAlt } from 'react-icons/fa';

const ShippersWorkspaceLayout = () => {
    const navigate = useNavigate();

    const handleSignOut = () => {
        localStorage.removeItem('token');
        navigate('/login');
    };

    return (
        <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: '#0f172a' }}>
            {/* Sidebar */}
            <div style={{
                width: '280px',
                background: 'linear-gradient(180deg, #0f172a 0%, #1e293b 100%)',
                color: 'white',
                display: 'flex',
                flexDirection: 'column',
                borderRight: '1px solid #334155',
                position: 'fixed',
                height: '100vh',
                overflowY: 'auto'
            }}>
                {/* Logo */}
                <div style={{ padding: '24px', borderBottom: '1px solid #334155', textAlign: 'center' }}>
                    <div style={{ fontSize: '32px', marginBottom: '8px' }}>📦</div>
                    <h2 style={{ margin: 0, color: '#f59e0b', fontSize: '20px' }}>AI Shippers</h2>
                    <p style={{ fontSize: '11px', color: '#64748b', margin: '4px 0 0' }}>
                        Shipper Management Platform
                    </p>
                </div>

                {/* Navigation */}
                <nav style={{ flex: 1, padding: '20px 16px' }}>
                    <NavLink to="/ai-bots/shippers/dashboard" className={({ isActive }) =>
                        `nav-link ${isActive ? 'active' : ''}`
                    }>
                        <FaTachometerAlt style={{ marginLeft: '12px', fontSize: '16px' }} />
                        Dashboard
                    </NavLink>

                    <NavLink to="/ai-bots/shippers/list" className={({ isActive }) =>
                        `nav-link ${isActive ? 'active' : ''}`
                    }>
                        <FaUsers style={{ marginLeft: '12px', fontSize: '16px' }} />
                        Shippers List
                    </NavLink>

                    <NavLink to="/ai-bots/shippers/shipments" className={({ isActive }) =>
                        `nav-link ${isActive ? 'active' : ''}`
                    }>
                        <FaBox style={{ marginLeft: '12px', fontSize: '16px' }} />
                        Shipments
                    </NavLink>

                    <NavLink to="/ai-bots/shippers/invoices" className={({ isActive }) =>
                        `nav-link ${isActive ? 'active' : ''}`
                    }>
                        <FaFileInvoice style={{ marginLeft: '12px', fontSize: '16px' }} />
                        Invoices
                    </NavLink>
                </nav>

                {/* Footer */}
                <div style={{ padding: '20px', borderTop: '1px solid #334155' }}>
                    <button
                        onClick={handleSignOut}
                        style={{
                            width: '100%',
                            padding: '10px',
                            background: 'transparent',
                            border: '1px solid #334155',
                            borderRadius: '8px',
                            color: '#94a3b8',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: '8px',
                            fontSize: '14px',
                            transition: 'all 0.2s'
                        }}
                        onMouseEnter={(e) => {
                            e.target.style.background = '#334155';
                            e.target.style.color = 'white';
                        }}
                        onMouseLeave={(e) => {
                            e.target.style.background = 'transparent';
                            e.target.style.color = '#94a3b8';
                        }}
                    >
                        <FaSignOutAlt /> Sign Out
                    </button>
                    <div style={{ fontSize: '11px', color: '#475569', textAlign: 'center', marginTop: '12px' }}>
                        AI Shippers v1.0
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div style={{ marginRight: '280px', flex: 1, minHeight: '100vh' }}>
                <Outlet />
            </div>

            <style>{`
        .nav-link {
          display: flex;
          align-items: center;
          padding: 12px 16px;
          margin: 4px 0;
          color: #94a3b8;
          text-decoration: none;
          border-radius: 10px;
          transition: all 0.2s;
          font-size: 14px;
          gap: 12px;
        }
        .nav-link:hover {
          background: #334155;
          color: white;
        }
        .nav-link.active {
          background: #f59e0b;
          color: white;
        }
      `}</style>
        </div>
    );
};

export default ShippersWorkspaceLayout;