// src/components/bots/panels/documents-manager/IntegrationsPanel.jsx
import React, { useState } from 'react';
import './IntegrationsPanel.css';

const IntegrationsPanel = () => {
    const [activeTab, setActiveTab] = useState('customs');
    const [integrations, setIntegrations] = useState([
        { id: 1, name: 'US Customs (ACE)', status: 'connected', lastSync: '2024-01-15 10:30', apiStatus: 'healthy' },
        { id: 2, name: 'EU Customs (ICS)', status: 'connected', lastSync: '2024-01-15 10:15', apiStatus: 'healthy' },
        { id: 3, name: 'Canadian Border (CBP)', status: 'connecting', lastSync: '2024-01-15 10:00', apiStatus: 'processing' }
    ]);
    const [carriers, setCarriers] = useState([
        { id: 1, name: 'DHL', status: 'active', trackingDocs: 245, lastUpdate: '2024-01-15 11:20' },
        { id: 2, name: 'FedEx', status: 'active', trackingDocs: 187, lastUpdate: '2024-01-15 10:45' },
        { id: 3, name: 'Maersk', status: 'inactive', trackingDocs: 0, lastUpdate: '2024-01-14 15:30' }
    ]);
    const [erpConnections, setErpConnections] = useState([
        { id: 1, name: 'SAP', status: 'synced', lastSync: '2024-01-15 06:00', records: 15847, errors: 0 },
        { id: 2, name: 'Oracle ERP', status: 'synced', lastSync: '2024-01-15 05:30', records: 8945, errors: 2 },
        { id: 3, name: 'NetSuite', status: 'pending', lastSync: '2024-01-14 22:00', records: 0, errors: 5 }
    ]);
    const [blockchainStatus, setBlockchainStatus] = useState('connected');

    const customsIntegrations = [
        {
            name: 'US Customs (ACE)',
            description: 'Automated Commercial Environment integration',
            features: ['Real-time submission', 'Status tracking', 'Duty calculation'],
            credentials: 'Configured'
        },
        {
            name: 'EU Customs (ICS)',
            description: 'Import Control System',
            features: ['Entry processing', 'Risk assessment', 'Compliance check'],
            credentials: 'Configured'
        },
        {
            name: 'Canadian Border (CBP)',
            description: 'Canada Border Services Agency',
            features: ['B3/B4 filing', 'Tariff lookup', 'Document submission'],
            credentials: 'Pending'
        }
    ];

    const carrierIntegrations = [
        {
            name: 'DHL',
            trackingApi: 'DHL Express API',
            status: 'Active',
            documentsLinked: 245,
            features: ['Tracking', 'Shipping labels', 'Proof of delivery']
        },
        {
            name: 'FedEx',
            trackingApi: 'FedEx Web Services',
            status: 'Active',
            documentsLinked: 187,
            features: ['Real-time tracking', 'Rate shopping', 'Label generation']
        },
        {
            name: 'Maersk',
            trackingApi: 'Maersk Seatrade',
            status: 'Inactive',
            documentsLinked: 0,
            features: ['Vessel tracking', 'Container status', 'Port updates']
        }
    ];

    const erpIntegrations = [
        {
            name: 'SAP',
            modules: ['MM', 'FI', 'LE'],
            syncFrequency: 'Real-time',
            dataFlow: 'Bidirectional'
        },
        {
            name: 'Oracle ERP',
            modules: ['AP', 'AR', 'GL'],
            syncFrequency: 'Hourly',
            dataFlow: 'Bidirectional'
        },
        {
            name: 'NetSuite',
            modules: ['Procurement', 'Fulfillment', 'Accounting'],
            syncFrequency: 'Daily',
            dataFlow: 'Unidirectional'
        }
    ];

    return (
        <div className="integrations-panel">
            <div className="panel-header">
                <h2> External Integrations</h2>
                <p>Connect with customs, carriers, ERP systems, and blockchain networks</p>
            </div>

            {/* Integration Tabs */}
            <div className="integration-tabs">
                <button
                    className={`tab-btn ${activeTab === 'customs' ? 'active' : ''}`}
                    onClick={() => setActiveTab('customs')}
                >
                     Customs Agencies
                </button>
                <button
                    className={`tab-btn ${activeTab === 'carriers' ? 'active' : ''}`}
                    onClick={() => setActiveTab('carriers')}
                >
                     Carriers
                </button>
                <button
                    className={`tab-btn ${activeTab === 'erp' ? 'active' : ''}`}
                    onClick={() => setActiveTab('erp')}
                >
                     ERP Systems
                </button>
                <button
                    className={`tab-btn ${activeTab === 'blockchain' ? 'active' : ''}`}
                    onClick={() => setActiveTab('blockchain')}
                >
                     Blockchain
                </button>
            </div>

            {/* Customs Integration */}
            {activeTab === 'customs' && (
                <div className="customs-integration">
                    <h3> Customs Agency Integration</h3>
                    <div className="integration-status-cards">
                        {integrations.map(integration => (
                            <div key={integration.id} className={`status-card ${integration.status}`}>
                                <div className="status-header">
                                    <div className="status-name">{integration.name}</div>
                                    <span className={`status-badge ${integration.status}`}>{integration.status}</span>
                                </div>
                                <div className="status-details">
                                    <div className="detail">
                                        <span className="label">Last Sync:</span>
                                        <span className="value">{integration.lastSync}</span>
                                    </div>
                                    <div className="detail">
                                        <span className="label">API Status:</span>
                                        <span className={`api-status ${integration.apiStatus}`}>
                                            {integration.apiStatus === 'healthy' ? '' : ''} {integration.apiStatus}
                                        </span>
                                    </div>
                                </div>
                                <div className="status-actions">
                                    <button className="action-btn"> Configure</button>
                                    <button className="action-btn"> Sync Now</button>
                                    <button className="action-btn"> Logs</button>
                                </div>
                            </div>
                        ))}
                    </div>

                    <div className="customs-details">
                        <h4> Available Customs Integration</h4>
                        {customsIntegrations.map((custom, idx) => (
                            <div key={idx} className="detail-card">
                                <div className="detail-title">{custom.name}</div>
                                <div className="detail-description">{custom.description}</div>
                                <div className="features-list">
                                    {custom.features.map((feature, fidx) => (
                                        <span key={fidx} className="feature-tag"> {feature}</span>
                                    ))}
                                </div>
                                <div className="credentials-status">
                                    Credentials: <span className={`cred-${custom.credentials.toLowerCase()}`}>{custom.credentials}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Carriers Integration */}
            {activeTab === 'carriers' && (
                <div className="carriers-integration">
                    <h3> Carrier Integration</h3>
                    <div className="carriers-table">
                        <table>
                            <thead>
                                <tr>
                                    <th>Carrier</th>
                                    <th>Status</th>
                                    <th>Linked Documents</th>
                                    <th>Last Update</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {carriers.map(carrier => (
                                    <tr key={carrier.id} className={`carrier-row ${carrier.status}`}>
                                        <td>
                                            <span className="carrier-icon"></span>
                                            {carrier.name}
                                        </td>
                                        <td>
                                            <span className={`status-badge ${carrier.status}`}>
                                                {carrier.status === 'active' ? '' : ''} {carrier.status}
                                            </span>
                                        </td>
                                        <td>{carrier.trackingDocs}</td>
                                        <td>{carrier.lastUpdate}</td>
                                        <td>
                                            <button className="action-btn small"></button>
                                            <button className="action-btn small"></button>
                                            <button className="action-btn small"></button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                    <div className="carriers-details">
                        <h4> Carrier API Connections</h4>
                        {carrierIntegrations.map((carrier, idx) => (
                            <div key={idx} className="carrier-detail-card">
                                <div className="card-header">{carrier.name}</div>
                                <div className="card-info">
                                    <div className="info-row">
                                        <span className="label">API:</span>
                                        <span className="value">{carrier.trackingApi}</span>
                                    </div>
                                    <div className="info-row">
                                        <span className="label">Status:</span>
                                        <span className="value">{carrier.status}</span>
                                    </div>
                                    <div className="info-row">
                                        <span className="label">Documents Linked:</span>
                                        <span className="value">{carrier.documentsLinked}</span>
                                    </div>
                                </div>
                                <div className="features-list">
                                    {carrier.features.map((feature, fidx) => (
                                        <span key={fidx} className="feature-tag"> {feature}</span>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* ERP Integration */}
            {activeTab === 'erp' && (
                <div className="erp-integration">
                    <h3> ERP System Integration</h3>
                    <div className="erp-status-cards">
                        {erpConnections.map(erp => (
                            <div key={erp.id} className={`erp-card ${erp.status}`}>
                                <div className="erp-header">{erp.name}</div>
                                <div className="erp-status">
                                    <span className={`sync-status ${erp.status}`}>
                                        {erp.status === 'synced' ? '' : ''} {erp.status}
                                    </span>
                                </div>
                                <div className="erp-stats">
                                    <div className="stat">
                                        <span className="stat-label">Records:</span>
                                        <span className="stat-value">{erp.records}</span>
                                    </div>
                                    <div className="stat">
                                        <span className="stat-label">Errors:</span>
                                        <span className="stat-value">{erp.errors}</span>
                                    </div>
                                    <div className="stat">
                                        <span className="stat-label">Last Sync:</span>
                                        <span className="stat-value">{erp.lastSync}</span>
                                    </div>
                                </div>
                                <button className="sync-btn"> Sync Now</button>
                            </div>
                        ))}
                    </div>

                    <div className="erp-modules">
                        <h4> ERP Modules & Configuration</h4>
                        {erpIntegrations.map((erp, idx) => (
                            <div key={idx} className="module-card">
                                <div className="module-name">{erp.name}</div>
                                <div className="module-config">
                                    <div className="config-item">
                                        <span className="config-label">Modules:</span>
                                        <div className="module-list">
                                            {erp.modules.map((mod, midx) => (
                                                <span key={midx} className="module-tag">{mod}</span>
                                            ))}
                                        </div>
                                    </div>
                                    <div className="config-item">
                                        <span className="config-label">Sync Frequency:</span>
                                        <span className="config-value">{erp.syncFrequency}</span>
                                    </div>
                                    <div className="config-item">
                                        <span className="config-label">Data Flow:</span>
                                        <span className="config-value">{erp.dataFlow}</span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Blockchain Integration */}
            {activeTab === 'blockchain' && (
                <div className="blockchain-integration">
                    <h3> Blockchain Integration</h3>
                    <div className="blockchain-status-card">
                        <div className="status-icon">
                            {blockchainStatus === 'connected' ? '' : ''}
                        </div>
                        <div className="status-info">
                            <div className="status-title">Blockchain Network Status</div>
                            <div className="status-description">
                                {blockchainStatus === 'connected'
                                    ? 'Connected to Ethereum & Hyperledger networks'
                                    : 'Connection pending...'}
                            </div>
                        </div>
                    </div>

                    <div className="blockchain-networks">
                        <h4> Blockchain Networks</h4>
                        <div className="networks-grid">
                            <div className="network-card">
                                <div className="network-name">Ethereum Mainnet</div>
                                <div className="network-status"> Connected</div>
                                <div className="network-info">
                                    <div>Smart Contracts: 3</div>
                                    <div>Transactions: 1,245</div>
                                    <div>Gas Used: 45.2 ETH</div>
                                </div>
                                <button className="network-btn"> View Contracts</button>
                            </div>
                            <div className="network-card">
                                <div className="network-name">Hyperledger Fabric</div>
                                <div className="network-status"> Connected</div>
                                <div className="network-info">
                                    <div>Organizations: 5</div>
                                    <div>Chaincode: 8</div>
                                    <div>Ledger Records: 8,945</div>
                                </div>
                                <button className="network-btn"> View Chaincode</button>
                            </div>
                            <div className="network-card">
                                <div className="network-name">Polygon (L2)</div>
                                <div className="network-status"> Connecting</div>
                                <div className="network-info">
                                    <div>Smart Contracts: 1</div>
                                    <div>Transactions: 342</div>
                                    <div>Gas Used: 12.5 MATIC</div>
                                </div>
                                <button className="network-btn"> Configure</button>
                            </div>
                        </div>
                    </div>

                    <div className="blockchain-features">
                        <h4> Blockchain Features</h4>
                        <div className="features-list">
                            <div className="feature-item">
                                <span className="feature-icon"></span>
                                <div className="feature-content">
                                    <div className="feature-title">Smart Document Hashing</div>
                                    <div className="feature-desc">Immutable document fingerprints on blockchain</div>
                                </div>
                            </div>
                            <div className="feature-item">
                                <span className="feature-icon"></span>
                                <div className="feature-content">
                                    <div className="feature-title">Supply Chain Tracking</div>
                                    <div className="feature-desc">Real-time tracking from origin to destination</div>
                                </div>
                            </div>
                            <div className="feature-item">
                                <span className="feature-icon"></span>
                                <div className="feature-content">
                                    <div className="feature-title">Smart Contracts</div>
                                    <div className="feature-desc">Automated execution upon document milestone</div>
                                </div>
                            </div>
                            <div className="feature-item">
                                <span className="feature-icon"></span>
                                <div className="feature-content">
                                    <div className="feature-title">Tokenization</div>
                                    <div className="feature-desc">Document-backed digital assets roadmap</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Global Integration Settings */}
            <div className="integration-settings">
                <h3> Global Integration Settings</h3>
                <div className="settings-grid">
                    <div className="setting">
                        <label>Sync Interval</label>
                        <select>
                            <option>Real-time</option>
                            <option>Every 5 minutes</option>
                            <option>Every 15 minutes</option>
                            <option>Hourly</option>
                        </select>
                    </div>
                    <div className="setting">
                        <label>Error Notification</label>
                        <select>
                            <option>Immediate</option>
                            <option>On-demand</option>
                            <option>Daily Summary</option>
                        </select>
                    </div>
                    <div className="setting">
                        <label>Data Retention</label>
                        <select>
                            <option>1 Month</option>
                            <option>3 Months</option>
                            <option>6 Months</option>
                            <option>1 Year</option>
                        </select>
                    </div>
                    <div className="setting">
                        <label>API Rate Limiting</label>
                        <input type="text" placeholder="requests/minute" />
                    </div>
                </div>
            </div>
        </div>
    );
};

export default IntegrationsPanel;
