// src/components/bots/panels/documents-manager/SecurityPanel.jsx
import React, { useState } from 'react';
import './SecurityPanel.css';

const SecurityPanel = () => {
    const [activeSection, setActiveSection] = useState('encryption');
    const [accessRules, setAccessRules] = useState([
        { id: 1, role: 'Admin', permissions: 'Full Access', status: 'active' },
        { id: 2, role: 'Manager', permissions: 'Read/Write', status: 'active' },
        { id: 3, role: 'User', permissions: 'Read Only', status: 'active' }
    ]);
    const [auditLogs, setAuditLogs] = useState([
        { id: 1, action: 'Document Accessed', user: 'admin@gts.com', timestamp: '2024-01-15 14:30:45', status: 'success' },
        { id: 2, action: 'File Uploaded', user: 'manager@gts.com', timestamp: '2024-01-15 13:15:22', status: 'success' },
        { id: 3, action: 'Unauthorized Access', user: 'unknown', timestamp: '2024-01-15 12:45:10', status: 'blocked' }
    ]);

    const complianceTemplates = [
        { id: 1, name: 'GDPR Compliance', coverage: 95, status: 'compliant' },
        { id: 2, name: 'HIPAA', coverage: 88, status: 'compliant' },
        { id: 3, name: 'SOC 2 Type II', coverage: 92, status: 'compliant' },
        { id: 4, name: 'ISO 27001', coverage: 89, status: 'compliant' }
    ];

    const encryptionSettings = [
        { id: 1, type: 'At-Rest Encryption', algorithm: 'AES-256', status: 'enabled' },
        { id: 2, type: 'In-Transit Encryption', algorithm: 'TLS 1.3', status: 'enabled' },
        { id: 3, type: 'End-to-End Encryption', algorithm: 'E2EE', status: 'enabled' }
    ];

    const securityEvents = [
        { severity: 'high', description: 'Multiple failed login attempts', count: 3, timestamp: '2024-01-15 15:30' },
        { severity: 'medium', description: 'Unusual document access pattern', count: 1, timestamp: '2024-01-15 14:45' },
        { severity: 'low', description: 'API rate limit approached', count: 1, timestamp: '2024-01-15 14:30' }
    ];

    return (
        <div className="security-panel">
            <div className="panel-header">
                <h2> Advanced Security & Compliance</h2>
                <p>Encryption, access control, and compliance management</p>
            </div>

            {/* Security Tabs */}
            <div className="security-tabs">
                <button
                    className={`tab-btn ${activeSection === 'encryption' ? 'active' : ''}`}
                    onClick={() => setActiveSection('encryption')}
                >
                     Encryption
                </button>
                <button
                    className={`tab-btn ${activeSection === 'access' ? 'active' : ''}`}
                    onClick={() => setActiveSection('access')}
                >
                     Access Control
                </button>
                <button
                    className={`tab-btn ${activeSection === 'compliance' ? 'active' : ''}`}
                    onClick={() => setActiveSection('compliance')}
                >
                     Compliance
                </button>
                <button
                    className={`tab-btn ${activeSection === 'audit' ? 'active' : ''}`}
                    onClick={() => setActiveSection('audit')}
                >
                     Audit Logs
                </button>
            </div>

            {/* Encryption Section */}
            {activeSection === 'encryption' && (
                <div className="security-section">
                    <h3> Data Encryption</h3>

                    <div className="encryption-cards">
                        {encryptionSettings.map(setting => (
                            <div key={setting.id} className="encryption-card">
                                <div className="encryption-header">
                                    <div className="encryption-type">{setting.type}</div>
                                    <span className={`status-badge ${setting.status}`}>
                                        {setting.status === 'enabled' ? '' : ''} {setting.status}
                                    </span>
                                </div>
                                <div className="encryption-algorithm">Algorithm: {setting.algorithm}</div>
                                <div className="encryption-actions">
                                    <button className="action-btn"> Configure</button>
                                    <button className="action-btn"> Rotate Keys</button>
                                </div>
                            </div>
                        ))}
                    </div>

                    <div className="encryption-config">
                        <h4>Encryption Configuration</h4>
                        <div className="config-grid">
                            <div className="config-item">
                                <label>Master Key Rotation (days)</label>
                                <input type="number" value="90" />
                            </div>
                            <div className="config-item">
                                <label>Key Escrow</label>
                                <select>
                                    <option>Enabled</option>
                                    <option>Disabled</option>
                                </select>
                            </div>
                            <div className="config-item">
                                <label>Perfect Forward Secrecy</label>
                                <select>
                                    <option>Enabled</option>
                                    <option>Disabled</option>
                                </select>
                            </div>
                            <div className="config-item">
                                <label>Hardware Security Module</label>
                                <select>
                                    <option>Connected</option>
                                    <option>Disconnected</option>
                                </select>
                            </div>
                        </div>
                        <button className="save-btn"> Save Configuration</button>
                    </div>
                </div>
            )}

            {/* Access Control Section */}
            {activeSection === 'access' && (
                <div className="security-section">
                    <h3> Access Control & Permissions</h3>

                    <div className="access-table">
                        <table>
                            <thead>
                                <tr>
                                    <th>Role</th>
                                    <th>Permissions</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {accessRules.map(rule => (
                                    <tr key={rule.id}>
                                        <td>{rule.role}</td>
                                        <td>{rule.permissions}</td>
                                        <td><span className="status-badge active"> {rule.status}</span></td>
                                        <td>
                                            <button className="action-btn small">Edit</button>
                                            <button className="action-btn small">Details</button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                    <div className="access-control-settings">
                        <h4>Access Control Settings</h4>
                        <div className="settings-list">
                            <div className="setting-item">
                                <label className="checkbox-label">
                                    <input type="checkbox" defaultChecked />
                                    <span>Multi-Factor Authentication (MFA)</span>
                                </label>
                            </div>
                            <div className="setting-item">
                                <label className="checkbox-label">
                                    <input type="checkbox" defaultChecked />
                                    <span>IP Whitelisting</span>
                                </label>
                            </div>
                            <div className="setting-item">
                                <label className="checkbox-label">
                                    <input type="checkbox" defaultChecked />
                                    <span>Session Timeout (minutes)</span>
                                </label>
                                <input type="number" value="30" className="inline-input" />
                            </div>
                            <div className="setting-item">
                                <label className="checkbox-label">
                                    <input type="checkbox" defaultChecked />
                                    <span>Role-Based Access Control (RBAC)</span>
                                </label>
                            </div>
                            <div className="setting-item">
                                <label className="checkbox-label">
                                    <input type="checkbox" defaultChecked />
                                    <span>Attribute-Based Access Control (ABAC)</span>
                                </label>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Compliance Section */}
            {activeSection === 'compliance' && (
                <div className="security-section">
                    <h3> Compliance Management</h3>

                    <div className="compliance-templates">
                        <h4>Compliance Standards</h4>
                        <div className="templates-grid">
                            {complianceTemplates.map(template => (
                                <div key={template.id} className={`template-card compliance-${template.status}`}>
                                    <div className="template-name">{template.name}</div>
                                    <div className="coverage-bar">
                                        <div className="bar-fill" style={{ width: `${template.coverage}%` }}>
                                            {template.coverage}%
                                        </div>
                                    </div>
                                    <div className="compliance-status">
                                        {template.status === 'compliant' ? '' : ''} {template.status}
                                    </div>
                                    <div className="template-actions">
                                        <button className="action-btn"> View</button>
                                        <button className="action-btn"> Export</button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="compliance-checklist">
                        <h4>Compliance Checklist</h4>
                        <div className="checklist-items">
                            <div className="checklist-item">
                                <input type="checkbox" defaultChecked />
                                <span>Data minimization principles implemented</span>
                            </div>
                            <div className="checklist-item">
                                <input type="checkbox" defaultChecked />
                                <span>Data retention policies defined</span>
                            </div>
                            <div className="checklist-item">
                                <input type="checkbox" defaultChecked />
                                <span>Privacy by design implemented</span>
                            </div>
                            <div className="checklist-item">
                                <input type="checkbox" defaultChecked />
                                <span>Third-party risk assessments completed</span>
                            </div>
                            <div className="checklist-item">
                                <input type="checkbox" defaultChecked />
                                <span>Incident response plan documented</span>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Audit Logs Section */}
            {activeSection === 'audit' && (
                <div className="security-section">
                    <h3> Audit Logs</h3>

                    <div className="security-events">
                        <h4> Security Events</h4>
                        <div className="events-list">
                            {securityEvents.map((event, idx) => (
                                <div key={idx} className={`event-card severity-${event.severity}`}>
                                    <div className="event-icon">
                                        {event.severity === 'high' ? '' : event.severity === 'medium' ? '' : ''}
                                    </div>
                                    <div className="event-content">
                                        <div className="event-description">{event.description}</div>
                                        <div className="event-meta">
                                            <span>{event.count} incident(s)</span>
                                            <span>{event.timestamp}</span>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="audit-logs-table">
                        <h4>Audit Trail</h4>
                        <table>
                            <thead>
                                <tr>
                                    <th>Action</th>
                                    <th>User</th>
                                    <th>Timestamp</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {auditLogs.map(log => (
                                    <tr key={log.id}>
                                        <td>{log.action}</td>
                                        <td>{log.user}</td>
                                        <td>{log.timestamp}</td>
                                        <td>
                                            <span className={`status-badge ${log.status}`}>
                                                {log.status === 'success' ? '' : ''} {log.status}
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                    <div className="audit-export">
                        <button className="export-btn"> Export Audit Report</button>
                        <button className="export-btn"> Email Report</button>
                        <button className="export-btn"> Share Link</button>
                    </div>
                </div>
            )}

            {/* Security Status Overview */}
            <div className="security-overview">
                <h3> Security Status Overview</h3>
                <div className="status-cards">
                    <div className="status-card">
                        <div className="status-icon"></div>
                        <div className="status-info">
                            <div className="status-label">Encryption</div>
                            <div className="status-value">100% Enabled</div>
                        </div>
                    </div>
                    <div className="status-card">
                        <div className="status-icon"></div>
                        <div className="status-info">
                            <div className="status-label">Access Control</div>
                            <div className="status-value">3 Roles Active</div>
                        </div>
                    </div>
                    <div className="status-card">
                        <div className="status-icon"></div>
                        <div className="status-info">
                            <div className="status-label">Compliance</div>
                            <div className="status-value">4/4 Standards</div>
                        </div>
                    </div>
                    <div className="status-card">
                        <div className="status-icon"></div>
                        <div className="status-info">
                            <div className="status-label">Audit Trail</div>
                            <div className="status-value">{auditLogs.length} Records</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SecurityPanel;
