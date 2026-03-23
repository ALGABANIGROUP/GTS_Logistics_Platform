import React, { useState, useEffect } from 'react';
import axiosClient from '../../api/axiosClient';
import { formatTierLabel, normalizeTier } from '../../utils/tierUtils';
import './TMSRequestsPanel.css';

/**
 * TMS Requests Management Panel - Admin Only
 * Allows admins to approve/reject TMS access requests
 */
export default function TMSRequestsPanel() {
    const [requests, setRequests] = useState([]);
    const [filter, setFilter] = useState('pending');
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState({ pending: 0, approved: 0, rejected: 0, total: 0 });
    const [selectedRequest, setSelectedRequest] = useState(null);
    const [showDetailsModal, setShowDetailsModal] = useState(false);
    const [actionLoading, setActionLoading] = useState(false);

    useEffect(() => {
        fetchRequests();
        fetchStats();
    }, [filter]);

    const fetchRequests = async () => {
        try {
            setLoading(true);
            const response = await axiosClient.get(`/api/v1/admin/tms-requests/list`, {
                params: {
                    status_filter: filter === 'all' ? null : filter,
                    limit: 100
                }
            });

            if (response.data.success) {
                setRequests(response.data.requests);
            }
        } catch (error) {
            console.error('Error fetching TMS requests:', error);
        } finally {
            setLoading(false);
        }
    };

    const fetchStats = async () => {
        try {
            const response = await axiosClient.get('/api/v1/admin/tms-requests/stats');
            if (response.data.success) {
                setStats(response.data.stats);
            }
        } catch (error) {
            console.error('Error fetching stats:', error);
        }
    };

    const approveRequest = async (requestId) => {
        if (!window.confirm('Are you sure you want to approve this TMS access request?')) {
            return;
        }

        try {
            setActionLoading(true);
            const response = await axiosClient.post(
                `/api/v1/admin/tms-requests/${requestId}/approve`,
                { notes: 'Approved by admin' }
            );

            if (response.data.success) {
                alert('✅ TMS access granted successfully! User will receive an email.');
                fetchRequests();
                fetchStats();
            }
        } catch (error) {
            console.error('Error approving request:', error);
            alert('Failed to approve request: ' + (error.response?.data?.detail || error.message));
        } finally {
            setActionLoading(false);
        }
    };

    const rejectRequest = async (requestId) => {
        const reason = prompt('Enter rejection reason:');
        if (!reason) return;

        try {
            setActionLoading(true);
            const response = await axiosClient.post(
                `/api/v1/admin/tms-requests/${requestId}/reject`,
                { rejection_reason: reason }
            );

            if (response.data.success) {
                alert('❌ Request rejected. User will receive an email.');
                fetchRequests();
                fetchStats();
            }
        } catch (error) {
            console.error('Error rejecting request:', error);
            alert('Failed to reject request: ' + (error.response?.data?.detail || error.message));
        } finally {
            setActionLoading(false);
        }
    };

    const viewDetails = (request) => {
        setSelectedRequest(request);
        setShowDetailsModal(true);
    };

    const getCountryFlag = (countryCode) => {
        const flags = {
            'US': '🇺🇸',
            'CA': '🇨🇦',
            'MX': '🇲🇽',
            'UK': '🇬🇧',
            'FR': '🇫🇷',
            'DE': '🇩🇪',
            'CN': '🇨🇳',
            'IN': '🇮🇳',
            'BR': '🇧🇷'
        };
        return flags[countryCode] || '🌍';
    };

    const getPlanBadgeClass = (plan) => {
        const normalizedPlan = normalizeTier(plan, 'starter');
        const classes = {
            'free': 'badge-free',
            'starter': 'badge-starter',
            'growth': 'badge-growth',
            'professional': 'badge-professional',
            'enterprise': 'badge-enterprise'
        };
        return classes[normalizedPlan] || 'badge-default';
    };

    return (
        <div className="tms-requests-panel">
            <div className="panel-header">
                <h2>🚛 TMS Access Requests Management</h2>
                <p className="subtitle">Review and approve/reject TMS registration requests</p>
            </div>

            {/* Statistics Cards */}
            <div className="stats-grid">
                <div className="stat-card pending">
                    <div className="stat-number">{stats.pending}</div>
                    <div className="stat-label">Pending Review</div>
                </div>
                <div className="stat-card approved">
                    <div className="stat-number">{stats.approved}</div>
                    <div className="stat-label">Approved</div>
                </div>
                <div className="stat-card rejected">
                    <div className="stat-number">{stats.rejected}</div>
                    <div className="stat-label">Rejected</div>
                </div>
                <div className="stat-card total">
                    <div className="stat-number">{stats.total}</div>
                    <div className="stat-label">Total Requests</div>
                </div>
            </div>

            {/* Filter Tabs */}
            <div className="filter-tabs">
                <button
                    className={filter === 'pending' ? 'tab-active' : ''}
                    onClick={() => setFilter('pending')}
                >
                    Pending ({stats.pending})
                </button>
                <button
                    className={filter === 'approved' ? 'tab-active' : ''}
                    onClick={() => setFilter('approved')}
                >
                    Approved ({stats.approved})
                </button>
                <button
                    className={filter === 'rejected' ? 'tab-active' : ''}
                    onClick={() => setFilter('rejected')}
                >
                    Rejected ({stats.rejected})
                </button>
                <button
                    className={filter === 'all' ? 'tab-active' : ''}
                    onClick={() => setFilter('all')}
                >
                    All ({stats.total})
                </button>
            </div>

            {/* Requests Table */}
            {loading ? (
                <div className="loading-state">
                    <div className="spinner"></div>
                    <p>Loading requests...</p>
                </div>
            ) : requests.length === 0 ? (
                <div className="empty-state">
                    <div className="empty-icon">📭</div>
                    <h3>No requests found</h3>
                    <p>There are no {filter !== 'all' ? filter : ''} TMS requests at the moment.</p>
                </div>
            ) : (
                <div className="table-container">
                    <table className="requests-table">
                        <thead>
                            <tr>
                                <th>Company</th>
                                <th>Contact</th>
                                <th>Email</th>
                                <th>Industry</th>
                                <th>Location</th>
                                <th>Plan</th>
                                <th>Requested</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {requests.map(request => (
                                <tr key={request.id} className={`row-status-${request.status}`}>
                                    <td className="company-cell">
                                        <strong>{request.company_name}</strong>
                                    </td>
                                    <td>{request.contact_name}</td>
                                    <td>
                                        <a href={`mailto:${request.contact_email}`}>
                                            {request.contact_email}
                                        </a>
                                    </td>
                                    <td>
                                        <span className="badge badge-industry">
                                            {request.industry_type || 'N/A'}
                                        </span>
                                    </td>
                                    <td>
                                        <span className="location">
                                            {getCountryFlag(request.country_code)} {request.country_code}
                                            {request.state_province && `, ${request.state_province}`}
                                        </span>
                                    </td>
                                    <td>
                                        <span className={`badge ${getPlanBadgeClass(request.requested_plan)}`}>
                                            {formatTierLabel(request.requested_plan)}
                                        </span>
                                    </td>
                                    <td>
                                        {new Date(request.created_at).toLocaleDateString()}
                                        <br />
                                        <small>{new Date(request.created_at).toLocaleTimeString()}</small>
                                    </td>
                                    <td>
                                        <span className={`status-badge status-${request.status}`}>
                                            {request.status}
                                        </span>
                                    </td>
                                    <td className="actions-cell">
                                        {request.status === 'pending' && (
                                            <>
                                                <button
                                                    className="btn-approve"
                                                    onClick={() => approveRequest(request.id)}
                                                    disabled={actionLoading}
                                                >
                                                    ✅ Approve
                                                </button>
                                                <button
                                                    className="btn-reject"
                                                    onClick={() => rejectRequest(request.id)}
                                                    disabled={actionLoading}
                                                >
                                                    ❌ Reject
                                                </button>
                                            </>
                                        )}
                                        {request.status === 'approved' && (
                                            <span className="badge badge-success">✅ Granted</span>
                                        )}
                                        {request.status === 'rejected' && (
                                            <span className="badge badge-danger">❌ Denied</span>
                                        )}
                                        <button
                                            className="btn-details"
                                            onClick={() => viewDetails(request)}
                                        >
                                            🔍 Details
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {/* Details Modal */}
            {showDetailsModal && selectedRequest && (
                <div className="modal-overlay" onClick={() => setShowDetailsModal(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h3>Request Details</h3>
                            <button
                                className="modal-close"
                                onClick={() => setShowDetailsModal(false)}
                            >
                                ✕
                            </button>
                        </div>
                        <div className="modal-body">
                            <div className="detail-grid">
                                <div className="detail-item">
                                    <label>Company Name:</label>
                                    <div>{selectedRequest.company_name}</div>
                                </div>
                                <div className="detail-item">
                                    <label>Contact Person:</label>
                                    <div>{selectedRequest.contact_name}</div>
                                </div>
                                <div className="detail-item">
                                    <label>Email:</label>
                                    <div>{selectedRequest.contact_email}</div>
                                </div>
                                <div className="detail-item">
                                    <label>Phone:</label>
                                    <div>{selectedRequest.contact_phone || 'N/A'}</div>
                                </div>
                                <div className="detail-item">
                                    <label>Website:</label>
                                    <div>{selectedRequest.company_website || 'N/A'}</div>
                                </div>
                                <div className="detail-item">
                                    <label>Industry Type:</label>
                                    <div>{selectedRequest.industry_type || 'N/A'}</div>
                                </div>
                                <div className="detail-item">
                                    <label>Location:</label>
                                    <div>
                                        {getCountryFlag(selectedRequest.country_code)} {selectedRequest.country_code}
                                        {selectedRequest.state_province && `, ${selectedRequest.state_province}`}
                                        {selectedRequest.city && `, ${selectedRequest.city}`}
                                    </div>
                                </div>
                                <div className="detail-item">
                                    <label>Requested Plan:</label>
                                    <div>
                                        <span className={`badge ${getPlanBadgeClass(selectedRequest.requested_plan)}`}>
                                            {formatTierLabel(selectedRequest.requested_plan)}
                                        </span>
                                    </div>
                                </div>
                                <div className="detail-item">
                                    <label>Status:</label>
                                    <div>
                                        <span className={`status-badge status-${selectedRequest.status}`}>
                                            {selectedRequest.status}
                                        </span>
                                    </div>
                                </div>
                                <div className="detail-item">
                                    <label>Submitted:</label>
                                    <div>{new Date(selectedRequest.created_at).toLocaleString()}</div>
                                </div>
                                {selectedRequest.reviewed_at && (
                                    <div className="detail-item">
                                        <label>Reviewed:</label>
                                        <div>{new Date(selectedRequest.reviewed_at).toLocaleString()}</div>
                                    </div>
                                )}
                                {selectedRequest.rejection_reason && (
                                    <div className="detail-item full-width">
                                        <label>Rejection Reason:</label>
                                        <div className="rejection-reason">{selectedRequest.rejection_reason}</div>
                                    </div>
                                )}
                                {selectedRequest.notes && (
                                    <div className="detail-item full-width">
                                        <label>Notes:</label>
                                        <div>{selectedRequest.notes}</div>
                                    </div>
                                )}
                            </div>
                        </div>
                        <div className="modal-footer">
                            <button
                                className="btn-secondary"
                                onClick={() => setShowDetailsModal(false)}
                            >
                                Close
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
