// src/components/bots/panels/documents-manager/DocumentsDashboard.jsx
import React, { useState, useEffect } from 'react';
import './DocumentsDashboard.css';
import documentsService from '../../../../services/documentsService';

const DocumentsDashboard = ({ stats }) => {
    const [timeRange, setTimeRange] = useState('today');
    const [documents, setDocuments] = useState([]);
    const [processingQueue, setProcessingQueue] = useState([]);
    const [recentActivities, setRecentActivities] = useState([]);
    const [loading, setLoading] = useState(false);

    const documentTypes = [
        { id: 'bill_of_lading', name: 'Bill of Lading', icon: '', count: 0, color: '#3b82f6' },
        { id: 'commercial_invoice', name: 'Commercial Invoice', icon: '', count: 0, color: '#10b981' },
        { id: 'packing_list', name: 'Packing List', icon: '', count: 0, color: '#f59e0b' },
        { id: 'certificate_of_origin', name: 'Certificate of Origin', icon: '', count: 0, color: '#8b5cf6' },
        { id: 'insurance_certificate', name: 'Insurance Certificate', icon: '', count: 0, color: '#ef4444' },
        { id: 'customs_declaration', name: 'Customs Declaration', icon: '', count: 0, color: '#06b6d4' }
    ];

    useEffect(() => {
        loadDashboardData();
    }, [timeRange]);

    const loadDashboardData = async () => {
        setLoading(true);
        try {
            const data = await documentsService.getDashboard(timeRange);
            setDocuments(data.documents || []);
            setRecentActivities(data.activities || []);
            setProcessingQueue(data.processingQueue || []);
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
        } finally {
            setLoading(false);
        }
    };

    const quickActions = [
        { id: 'upload', label: 'Upload Documents', icon: '', color: '#3b82f6' },
        { id: 'process', label: 'Process Queue', icon: '', color: '#10b981' },
        { id: 'export', label: 'Export Reports', icon: '', color: '#f59e0b' },
        { id: 'scan', label: 'Scan for Compliance', icon: '', color: '#8b5cf6' }
    ];

    const handleQuickAction = async (actionId) => {
        setLoading(true);
        try {
            await documentsService.triggerQuickAction(actionId);
            await loadDashboardData();
        } catch (error) {
            console.error('Quick action failed:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="documents-dashboard">
            <div className="dashboard-header">
                <h2>Documents Dashboard</h2>
                <div className="dashboard-controls">
                    <select value={timeRange} onChange={(e) => setTimeRange(e.target.value)}>
                        <option value="today">Today</option>
                        <option value="week">This Week</option>
                        <option value="month">This Month</option>
                        <option value="quarter">This Quarter</option>
                    </select>
                    <button className="refresh-btn" onClick={loadDashboardData}>
                         Refresh
                    </button>
                </div>
            </div>

            <div className="quick-actions-grid">
                {quickActions.map((action) => (
                    <button
                        key={action.id}
                        className="quick-action-btn"
                        style={{ background: action.color }}
                        onClick={() => handleQuickAction(action.id)}
                    >
                        <span className="action-icon">{action.icon}</span>
                        <span className="action-label">{action.label}</span>
                    </button>
                ))}
            </div>

            <div className="stats-cards">
                <div className="stat-card">
                    <div className="stat-header">
                        <span className="stat-icon"></span>
                        <span className="stat-label">Total Documents</span>
                    </div>
                    <div className="stat-value">{stats.total}</div>
                    <div className="stat-trend">+0 this week</div>
                </div>

                <div className="stat-card">
                    <div className="stat-header">
                        <span className="stat-icon"></span>
                        <span className="stat-label">Processed</span>
                    </div>
                    <div className="stat-value">{stats.processed}</div>
                    <div className="stat-trend">100% completion</div>
                </div>

                <div className="stat-card">
                    <div className="stat-header">
                        <span className="stat-icon"></span>
                        <span className="stat-label">Storage Used</span>
                    </div>
                    <div className="stat-value">{stats.storage}</div>
                    <div className="stat-trend">0% of limit</div>
                </div>

                <div className="stat-card">
                    <div className="stat-header">
                        <span className="stat-icon"></span>
                        <span className="stat-label">Compliance Rate</span>
                    </div>
                    <div className="stat-value">100%</div>
                    <div className="stat-trend">All documents compliant</div>
                </div>
            </div>

            <div className="section-card">
                <h3>Document Types</h3>
                <div className="document-types-grid">
                    {documentTypes.map((type) => (
                        <div key={type.id} className="doc-type-card">
                            <div className="doc-type-header">
                                <span className="doc-icon">{type.icon}</span>
                                <span className="doc-name">{type.name}</span>
                            </div>
                            <div className="doc-count">{type.count} documents</div>
                            <div className="doc-progress">
                                <div className="progress-bar">
                                    <div
                                        className="progress-fill"
                                        style={{
                                            width: '0%',
                                            backgroundColor: type.color
                                        }}
                                    ></div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            <div className="section-card">
                <h3>Recent Documents</h3>
                <div className="recent-documents">
                    <table>
                        <thead>
                            <tr>
                                <th>Document Name</th>
                                <th>Type</th>
                                <th>Status</th>
                                <th>Uploaded</th>
                                <th>Size</th>
                                <th>Shipment</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {documents.map((doc) => (
                                <tr key={doc.id}>
                                    <td>
                                        <div className="doc-name-cell">
                                            <span className="doc-icon">
                                                {documentTypes.find(t => t.id === doc.type)?.icon || ''}
                                            </span>
                                            <span className="doc-name">{doc.name}</span>
                                        </div>
                                    </td>
                                    <td>
                                        <span className={`doc-type ${doc.type}`}>
                                            {documentTypes.find(t => t.id === doc.type)?.name || doc.type}
                                        </span>
                                    </td>
                                    <td>
                                        <span className={`status-badge ${doc.status}`}>
                                            {doc.status}
                                        </span>
                                    </td>
                                    <td>{doc.uploaded}</td>
                                    <td>{doc.size}</td>
                                    <td>
                                        {doc.shipment ? (
                                            <span className="shipment-link">{doc.shipment}</span>
                                        ) : (
                                            ''
                                        )}
                                    </td>
                                    <td>
                                        <div className="doc-actions">
                                            <button className="action-btn" title="View">
                                                
                                            </button>
                                            <button className="action-btn" title="Download">
                                                
                                            </button>
                                            <button className="action-btn" title="Process">
                                                
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            <div className="section-card">
                <h3>Processing Queue</h3>
                <div className="processing-queue">
                    {processingQueue.length === 0 ? (
                        <div className="empty-queue">
                            <span className="empty-icon"></span>
                            <p>No documents in processing queue</p>
                        </div>
                    ) : (
                        processingQueue.map((item) => (
                            <div key={item.id} className="queue-item">
                                <div className="queue-doc">
                                    <span className="doc-icon"></span>
                                    <span className="doc-name">{item.document}</span>
                                </div>
                                <div className="queue-progress">
                                    <div className="progress-bar">
                                        <div
                                            className="progress-fill"
                                            style={{ width: `${item.progress}%` }}
                                        >
                                            <span className="progress-text">{item.progress}%</span>
                                        </div>
                                    </div>
                                </div>
                                <button className="queue-action"> Process</button>
                            </div>
                        ))
                    )}
                </div>
            </div>

            <div className="section-card">
                <h3>Recent Activity</h3>
                <div className="activity-feed">
                    {recentActivities.map((activity) => (
                        <div key={activity.id} className="activity-item">
                            <div className="activity-icon">{activity.icon}</div>
                            <div className="activity-content">
                                <div className="activity-text">
                                    <strong>{activity.user}</strong> {activity.action} <em>{activity.document}</em>
                                </div>
                                <div className="activity-time">{activity.time}</div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default DocumentsDashboard;
